#!/usr/bin/env python3
"""Boucle chaude d'un programme profilé par tools/sampler.c, puis classification de son code machine.

Pour l'IP la plus fréquente d'un fichier ELF (ou d'une région JIT copiée), on désassemble une fenêtre
autour d'elle et on cherche la plus petite boucle (saut arrière) qui la contient. La boucle est dite
« vectorisée » si elle contient des instructions SIMD empaquetées (registres ymm/zmm, ou xmm avec
un mnémonique empaqueté).

Usage : hotloop.py prefixe   (lit prefixe.ips et éventuellement prefixe.jit)
"""
import os, re, subprocess, sys

PACKED = re.compile(r"\bv?p(add|sub|mul|cmp|and|or|xor|max|min|blend|shuf|movzx|movsx|maddw|sad|test|sll|srl|sra|ermd|ermq|unpck|alignr|broadcast|gather)"
                    r"|\bv?(add|sub|mul|div|max|min|sqrt|fmadd\d*|fmsub\d*|fnmadd\d*|cmp|blendv?|and|or|xor|cvt\w*|perm\w*|shuf|unpck\w*|broadcast\w*|gather\w*|mov[au]|movdq[au])p[sd]\b"
                    r"|\bvmovdq[au](8|16|32|64)?\b|\bvpcompress|\bvpexpand|\bkmov|\bvextract|\bvinsert")
SCALAR_ONLY = re.compile(r"\b(v?(add|sub|mul|div|fmadd\d*)s[sd])\b")
# cible imprimée « 7f12… <sym> » (fichier ELF) ou « 0x7f12… » (octets bruts) : le préfixe 0x est facultatif
JUMP = re.compile(r"^\s*([0-9a-f]+):\s+(j[a-z]+)\s+(?:0x)?([0-9a-f]+)")
INSN = re.compile(r"^\s*([0-9a-f]+):\s+(\S.*)$")


def segments(path):
    """Segments LOAD : (offset, vaddr, filesz)."""
    out = subprocess.run(["readelf", "-lW", path], capture_output=True, text=True).stdout
    segs = []
    for line in out.splitlines():
        f = line.split()
        if f and f[0] == "LOAD":
            segs.append((int(f[1], 16), int(f[2], 16), int(f[4], 16)))
    return segs


def off2vaddr(path, off):
    for o, v, sz in segments(path):
        if o <= off < o + sz:
            return off - o + v
    return off


def disasm_file(path, vaddr, before=1536, after=512):
    out = subprocess.run(["objdump", "-d", "--no-show-raw-insn", "-M", "intel", f"--start-address={max(0, vaddr - before)}",
                          f"--stop-address={vaddr + after}", path], capture_output=True, text=True).stdout
    return out


def disasm_bytes(hexstr, base):
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".bin", delete=False) as t:
        t.write(bytes.fromhex(hexstr))
        name = t.name
    return subprocess.run(["objdump", "-D", "-b", "binary", "-m", "i386:x86-64", "-M", "intel", "--no-show-raw-insn",
                           f"--adjust-vma={base}", name], capture_output=True, text=True).stdout


def loop_around(text, ip):
    """Instructions de la plus petite boucle [cible, saut] contenant ip."""
    insns, best = [], None
    for line in text.splitlines():
        m = INSN.match(line)
        if m:
            insns.append((int(m.group(1), 16), m.group(2)))
        j = JUMP.match(line)
        if j:
            src, dst = int(j.group(1), 16), int(j.group(3), 16)
            if dst <= ip <= src and (best is None or src - dst < best[1] - best[0]):
                best = (dst, src)
    if not best:
        return [i for i in insns if abs(i[0] - ip) < 64], None
    return [i for i in insns if best[0] <= i[0] <= best[1]], best


ZEROING = re.compile(r"\b(v?xorp[sd]|v?pxor[dq]?)\s+([xyz]mm\d+),\s*\2(,\s*\2)?\s*$")
ARITH = re.compile(r"\bv?p(add|sub|mul|cmp|max|min|blend|movzx|movsx|maddw|sad|sll|srl|sra|test)"
                   r"|\bv?(add|sub|mul|div|max|min|fmadd\d*|fmsub\d*|fnmadd\d*|cmp|blendv?|cvt\w*)p[sd]\b")


def classify(body):
    vec = [t for _, t in body if PACKED.search(t) and ("ymm" in t or "zmm" in t or "xmm" in t) and not ZEROING.search(t)
           and ARITH.search(t)]
    wide = [t for t in vec if "ymm" in t or "zmm" in t]
    scal = [t for _, t in body if SCALAR_ONLY.search(t)]
    return {"n": len(body), "packed": len(vec), "wide": len(wide), "scalar_fp": len(scal),
            "vectorized": len(vec) >= 2, "width": "zmm" if any("zmm" in t for t in vec) else "ymm" if wide else "xmm" if vec else "-"}


def parse_ips(prefix):
    """Lignes « n pct ip chemin décalage » ; le chemin peut contenir des espaces (« /memfd:x (deleted) »)."""
    rows = []
    for l in open(prefix + ".ips"):
        if l.startswith("#"):
            continue
        f = l.split()
        rows.append((int(f[0]), float(f[1].rstrip("%")), int(f[2], 16), " ".join(f[3:-1]), int(f[-1], 16)))
    return rows


def is_jit(path):
    return path in ("", "?") or path.startswith("//anon") or path.startswith("/memfd:") or not path.startswith("/")


def main(prefix, cover=0.9, maxips=80):
    """Regroupe les échantillons par boucle (la plus petite boucle qui contient chaque IP chaude), jusqu'à
    couvrir 90 % des échantillons, puis classe la boucle qui en reçoit le plus. La première ligne imprimée
    résume cette boucle ; suivent les trois boucles les plus chaudes, pour vérification."""
    rows = parse_ips(prefix)
    jit = {}
    try:
        cur = None
        for l in open(prefix + ".jit"):
            if l.startswith("REGION"):
                cur = int(l.split()[1], 16)
            elif cur is not None:
                jit[cur] = l.strip()
    except FileNotFoundError:
        pass
    total = sum(r[0] for r in rows) or 1
    loops, acc = {}, 0
    for n, pct, ip, path, off in rows[:maxips]:
        if acc >= cover * total:
            break
        acc += n
        if not is_jit(path):
            va = off2vaddr(path, off)
            body, span = loop_around(disasm_file(path, va), va)
            if not span:
                # objdump affiche comme données le code placé sous un symbole de type objet (tables d'info
                # de GHC, code dans .text) : on désassemble alors les octets bruts du fichier
                with open(path, "rb") as fh:
                    fh.seek(max(0, off - 1536))
                    raw = fh.read(2048)
                body, span = loop_around(disasm_bytes(raw.hex(), va - min(off, 1536)), va)
            key, where = (path, span or va), f"{os.path.basename(path)}+0x{va:x}"
        else:
            base = next((b for b in jit if b <= ip < b + len(jit[b]) // 2), None)
            if base is None:
                key, body, span, where = ("JIT sans copie", ip), [], None, f"JIT 0x{ip:x} (code non copié)"
            else:
                body, span = loop_around(disasm_bytes(jit[base], base), ip)
                key, where = ("JIT", span or ip), f"JIT 0x{ip:x}"
        e = loops.setdefault(key, {"n": 0, "body": body, "span": span, "where": where})
        e["n"] += n
    ranked = sorted(loops.values(), key=lambda e: -e["n"])
    # boucle du programme : code JIT ou exécutable principal (compilé, ou interpréteur), et non une
    # bibliothèque partagée du runtime (libc, libjvm, libjulia, OpenBLAS…) qui tourne à côté du noyau
    own = [e for e in ranked if ".so" not in e["where"].split("+")[0]]
    if own and own[0] is not ranked[0]:
        ranked.remove(own[0])
        ranked.insert(0, own[0])
    for i, e in enumerate(ranked[:3]):
        c = classify(e["body"])
        span = "0x%x-0x%x" % e["span"] if e["span"] else "?"
        print(f"{100 * e['n'] / total:.1f}% des échantillons : {e['where']} boucle={span} {c}")
        if i == 0:
            for a, t in e["body"][:60]:
                print(f"    {a:x}: {t}")
    return total


if __name__ == "__main__":
    main(sys.argv[1])
