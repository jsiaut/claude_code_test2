#!/usr/bin/env python3
"""Remarque sur C (docs/C.md, section 2) : sondes et faits de compilation. Sorties : results/c_check/*.txt.

* iso.txt     : C23 strict (-std=c23 -pedantic-errors) sous clang 23 et gcc 16 : [[likely]], __GCC_DESTRUCTIVE_SIZE,
                _mm_prefetch / _mm_pause / AVX-512 depuis <immintrin.h> ;
* reassoc.txt : #pragma clang fp reassociate(on), effet local (additions vectorielles de deux sommes, l'une sous le
                pragma) ;
* k9_code.txt : k9_rows de C par gcc 16 et de C++ par g++ 16, compilés pour Cascade Lake (cible des données
                principales) : même boucle ? (si oui, l'écart de K9 tuned et mt entre C++ et C par gcc dans les données
                principales tient au harnais : allocation des grilles et lancement des fils) ;
* k8_code.txt : a8_build du banc C sous clang 23 (Emerald Rapids) : accès mémoire à *top et *counter."""
import collections, os, re, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "results", "c_check")
PROBES = os.path.join(ROOT, "tools", "c_check", "probes")
GCC, GXX, CLANG = "/opt/gcc-16/bin/gcc-16", "/opt/gcc-16/bin/g++-16", "clang-23"
sys.path.insert(0, os.path.join(ROOT, "tools", "cpp_check"))
from collect import disasm, fn, loops, norm  # noqa: E402


def sh(cmd):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return (p.stdout + p.stderr).strip(), p.returncode


def save(name, lines):
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, name), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


def main():
    tmp = tempfile.mkdtemp(prefix="c_check_")
    L = ["# C23 strict (-std=c23 -pedantic-errors), clang 23 et gcc 16"]
    for cc in (CLANG, GCC):
        name = os.path.basename(cc)
        out, rc = sh(f"{cc} -std=c23 -pedantic-errors -c -o {tmp}/l.o {PROBES}/likely.c")
        first = next((l for l in out.splitlines() if "error" in l or "warning" in l), "(aucun diagnostic)")
        L.append(f"{name} [[likely]] : code {rc} ; {first.split('likely.c:')[-1].strip()}")
        out, rc = sh(f"{cc} -std=c23 -pedantic-errors -o {tmp}/d {PROBES}/destructive.c && {tmp}/d")
        L.append(f"{name} constante de ligne de cache : {out}")
        out, rc = sh(f"{cc} -std=c23 -pedantic-errors -O2 -march=native -o {tmp}/i {PROBES}/intrin.c && {tmp}/i; echo code $?")
        L.append(f"{name} <immintrin.h> en C23 strict (_mm_prefetch, _mm_pause, _mm512_*) : {out.splitlines()[-1]}")
    save("iso.txt", L)
    # pragma de réassociation : additions vectorielles par fonction
    asm, _ = sh(f"{CLANG} -std=c23 -O3 -march=native -S -o - {PROBES}/reassoc.c")
    cur, cnt = None, collections.Counter()
    for line in asm.splitlines():
        m = re.match(r"^(sum_\w+):", line)
        if m:
            cur = m.group(1)
            continue
        if cur and re.match(r"\s+vaddp[sd]\s", line):
            cnt[cur] += 1
        if cur and re.match(r"\s+vaddss\s", line):
            cnt[cur + " (scalaire)"] += 1
    save("reassoc.txt", ["# #pragma clang fp reassociate(on) : additions par fonction (clang 23 -O3 -march=native)",
                         *(f"{k} : {v}" for k, v in sorted(cnt.items()))])
    # K9 : k9_rows de C (gcc) et de C++ (g++) pour Cascade Lake
    cg, cp = os.path.join(tmp, "c_gcc_cl"), os.path.join(tmp, "cpp_cl")
    sh(f"{GCC} -std=c23 -O3 -march=cascadelake -pthread -o {cg} {ROOT}/bench/c/ms.c")
    sh(f"{GXX} -std=c++26 -O3 -march=cascadelake -pthread -Wno-interference-size -o {cp} {ROOT}/bench/cpp/ms.cpp")
    A, B = disasm(cg), disasm(cp)
    la, lb = loops(fn(A, "k9_rows")), loops(fn(B, "k9_rows"))
    same = sorted(norm(x) for x in la) == sorted(norm(x) for x in lb)
    L = ["# k9_rows, compilé pour Cascade Lake : C par gcc 16 (options de c_gcc) et C++ par g++ 16 (options du banc)",
         f"boucles de k9_rows : C {len(la)} ({', '.join(str(len(x)) for x in la)} instructions) ; C++ {len(lb)} "
         f"({', '.join(str(len(x)) for x in lb)} instructions) ; mêmes boucles au renommage des registres près : {same}",
         f"C++ pour Cascade Lake identique au binaire de la campagne : "
         f"{sh(f'cmp -s {cp} {ROOT}/bench/cpp/ms && echo oui || echo non')[0]}"]
    save("k9_code.txt", L)
    # K8 : a8_build du banc C sous clang 23, accès mémoire
    cr = os.path.join(tmp, "c_ref")
    sh(f"{CLANG} -std=c23 -O3 -march=native -pthread -o {cr} {ROOT}/bench/c/ms.c")
    ins = fn(disasm(cr), "a8_build")
    mem = [f"{mn} {ops}" for _a, mn, ops in ins if "(" in ops and not mn.startswith(("call", "j", "lea", "nop", "push", "pop"))]
    save("k8_code.txt", ["# a8_build du banc C (clang 23 -O3, Emerald Rapids) : instructions qui touchent la mémoire",
                         f"{len(ins)} instructions, dont {len(mem)} accès mémoire (hors pile d'appel) :", *mem])


if __name__ == "__main__":
    main()
