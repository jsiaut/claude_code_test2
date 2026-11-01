#!/usr/bin/env python3
"""Remarque sur Odin (docs/ODIN.md, 4.2) : l'isolement des noyaux change-t-il leur code machine ?

Désassemble bench/odin_ref/ms (binaire du banc, noyaux inlinés) et bench/odin_fix/ms (noyaux en #force_no_inline), puis
cherche, pour chaque boucle (saut arrière) des noyaux isolés, la même boucle dans le binaire du banc :
mêmes mnémoniques et mêmes opérandes, registres renommés dans l'ordre d'apparition (allocation de registres ignorée),
adresses de saut et des constantes (relatives à rip) ignorées. Donne aussi l'adresse de chaque boucle modulo 64 (placement) et, pour K4, dont les deux
formes compilent en la même boucle, les temps des deux formes dans les données principales et sur l'hôte. Refait la comparaison sur les deux sources compilés pour Cascade Lake
(cible des données principales). Sortie : results/odin_check/codegen.txt."""
import collections, filecmp, json, math, os, re, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KERNELS = ["k1_natural", "k1_aos", "k1_soa", "k2_chase", "k4_natural", "k4_branchless", "k5_natural", "k5_tuned",
           "q6_natural", "q6_tuned", "q1_natural", "q1_tuned", "k9_natural", "k9_rows"]
REG = re.compile(r"%[a-z0-9]+")
ODIN = "/opt/src/odin/odin"


def disasm(path):
    txt = subprocess.run(["objdump", "-d", "--no-show-raw-insn", "-C", path], capture_output=True, text=True,
                         check=True).stdout
    funcs, cur = collections.OrderedDict(), None
    for line in txt.splitlines():
        m = re.match(r"^([0-9a-f]+) <(.*)>:$", line)
        if m:
            cur = m.group(2)
            funcs[cur] = []
            continue
        m = re.match(r"^\s+([0-9a-f]+):\s+(\S+)\s*(.*)$", line)
        if m and cur:
            funcs[cur].append((int(m.group(1), 16), m.group(2), m.group(3)))
    return funcs


def loops(ins):
    out = []
    for a, mn, ops in ins:
        if mn.startswith("j"):  # saut arrière, conditionnel ou non (boucle à sortie au milieu)
            t = re.match(r"([0-9a-f]+)", ops)
            if t and int(t.group(1), 16) < a:
                ta = int(t.group(1), 16)
                out.append((ta, [x for x in ins if ta <= x[0] <= a]))
    return out


def norm(body):
    names, out = {}, []
    for _a, mn, ops in body:
        if mn.startswith("j"):
            out.append("j")  # sens du saut (jl/jb) ignoré
            continue
        ops = re.sub(r"#.*", "", ops).strip()
        ops = re.sub(r"-?0x[0-9a-f]+\(%rip\)", "CONST(%rip)", ops)  # constantes : adresse propre au binaire
        ops = re.sub(r"(?<![0-9a-fx])0x0\(", "(", ops)  # déplacement nul explicite (base r13)
        ops = REG.sub(lambda m: names.setdefault(m.group(0), f"R{len(names)}"), ops)
        out.append(mn + " " + ops)
    return tuple(out)


def compare(ref, fix, L):
    seen = collections.defaultdict(list)
    for f, ins in ref.items():
        for ta, body in loops(ins):
            seen[norm(body)].append((f, ta))
    L.append("noyau : boucles du noyau isolé (taille, adresse mod 64) -> même boucle dans le binaire à noyaux inlinés ?")
    for k in KERNELS:
        ins = fix.get(f"ms::{k}")
        if not ins:
            L.append(f"{k} : absent de la copie corrigée")
            continue
        parts = []
        for ta, body in sorted(loops(ins), key=lambda x: -len(x[1]))[:3]:
            hit = seen.get(norm(body))
            where = f"oui, {hit[0][0]} (mod 64 = {hit[0][1] % 64})" if hit else "non"
            parts.append(f"{len(body)} instr. (mod 64 = {ta % 64}) -> {where}")
        L.append(f"{k} : " + " | ".join(parts))


def main():
    ref_bin = os.path.join(ROOT, "bench", "odin_ref", "ms")
    fix_bin = os.path.join(ROOT, "bench", "odin_fix", "ms")
    L = ["# Code machine des noyaux d'Odin : binaire du banc (noyaux inlinés) contre noyaux isolés (#force_no_inline)",
         f"bench/odin_ref/ms identique à l'octet à bench/odin/ms (binaire du banc, compilé le 29/10 sur la machine 3) : "
         f"{filecmp.cmp(ref_bin, os.path.join(ROOT, 'bench', 'odin', 'ms'), shallow=False)} ; les données principales "
         "viennent d'une compilation du même source sur Cascade Lake (results/hw/machine3/binaries.txt, « avant »)", "",
         "## Binaires mesurés (-microarch:native sur Emerald Rapids) : bench/odin_ref/ms contre bench/odin_fix/ms"]
    fix = disasm(fix_bin)
    compare(disasm(ref_bin), fix, L)
    # même comparaison pour la cible des données principales : les deux sources compilés pour Cascade Lake
    with tempfile.TemporaryDirectory() as tmp:
        outs = {}
        for name, src in (("ref", os.path.join(ROOT, "bench", "odin", "ms.odin")),
                          ("fix", os.path.join(ROOT, "bench", "odin_fix", "ms.odin"))):
            outs[name] = os.path.join(tmp, f"ms_{name}")
            subprocess.run([ODIN, "build", src, "-file", "-o:speed", "-microarch:cascadelake", f"-out:{outs[name]}"],
                           check=True, capture_output=True)
        L += ["", "## Mêmes sources compilés pour Cascade Lake (-microarch:cascadelake), cible des données principales"]
        compare(disasm(outs["ref"]), disasm(outs["fix"]), L)
    # K4 : les deux formes donnent la même boucle ; temps des deux formes, même binaire
    sys.path.insert(0, os.path.join(ROOT, "analysis"))
    import analyze_v2 as v2  # noqa: E402
    from analyze_v3 import proc_logs  # noqa: E402
    data, *_ = v2.dataset_main(transfers=False)
    gm = lambda p: 1e3 * math.exp(proc_logs(p).mean())  # noqa: E731
    raw = collections.defaultdict(lambda: collections.defaultdict(list))
    for impl in ("odin_ref", "odin_fix"):
        for line in open(os.path.join(ROOT, "results", "raw_odin", f"{impl}.jsonl")):
            r = json.loads(line)
            raw[impl][(r["kernel"], r["variant"], r["param"])].append([x["sec"] for x in r["reps"]])
    kn, kb = ("k4", "natural_unsorted", ""), ("k4", "branchless_unsorted", "")
    same = norm(loops(fix["ms::k4_natural"])[0][1]) == norm(loops(fix["ms::k4_branchless"])[0][1])
    L += ["", f"K4 naturel et sans branchement : même boucle dans odin_fix : {same} (même chose dans le binaire du banc)",
          f"K4, données principales (Cascade Lake, binaire de la campagne) : naturel {gm(data['odin'][kn]):.2f} ms, "
          f"sans branchement {gm(data['odin'][kb]):.2f} ms",
          f"K4, hôte (machine 14), odin_ref : naturel {gm(raw['odin_ref'][kn]):.2f} ms, sans branchement "
          f"{gm(raw['odin_ref'][kb]):.2f} ms ; odin_fix : naturel {gm(raw['odin_fix'][kn]):.2f} ms, sans branchement "
          f"{gm(raw['odin_fix'][kb]):.2f} ms"]
    out = os.path.join(ROOT, "results", "odin_check", "codegen.txt")
    open(out, "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
