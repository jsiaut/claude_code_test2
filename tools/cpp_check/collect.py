#!/usr/bin/env python3
"""Remarque sur C++ (docs/CPP.md, section 2) : preuves tirées du code, des chaînes et de leur documentation livrée.
Sorties : results/cpp_check/{versions,gcc_manual,simd,p2795,reflection,k4,k9_harness,k8_q1,clang_loops}.txt.
Les binaires comparés pour Cascade Lake sont recompilés avec -march=cascadelake dans un répertoire temporaire
(identiques à l'octet à ceux de la campagne pour C par clang et C++ par g++, ce que le script vérifie)."""
import collections, filecmp, glob, os, re, subprocess, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "results", "cpp_check")
PROBES = os.path.join(ROOT, "tools", "cpp_check", "probes")
GXX, GCC, CLANGXX, CLANG = "/opt/gcc-16/bin/g++-16", "/opt/gcc-16/bin/gcc-16", "clang++-23", "clang-23"
REG = re.compile(r"%[a-z0-9]+")


def sh(cmd, **kw):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True, **kw)
    return (p.stdout + p.stderr).strip()


def save(name, lines):
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, name), "w").write("\n".join(lines) + "\n")


def disasm(path):
    txt = subprocess.run(["objdump", "-d", "--no-show-raw-insn", "-C", path], capture_output=True, text=True).stdout
    fs, cur = collections.OrderedDict(), None
    for line in txt.splitlines():
        m = re.match(r"^([0-9a-f]+) <(.*)>:$", line)
        if m:
            cur = m.group(2)
            fs[cur] = []
            continue
        m = re.match(r"^\s+([0-9a-f]+):\s+(\S+)\s*(.*)$", line)
        if m and cur:
            fs[cur].append((int(m.group(1), 16), m.group(2), m.group(3)))
    return fs


def fn(fs, name):
    for k, v in fs.items():
        if k.split("(")[0].split(".")[0] == name:
            return v
    return []


def loops(ins):
    out = []
    for a, mn, ops in ins:
        if mn.startswith("j"):
            t = re.match(r"([0-9a-f]+)", ops)
            if t and int(t.group(1), 16) < a:
                s = int(t.group(1), 16)
                out.append([x for x in ins if s <= x[0] <= a])
    return out


def norm(body):
    names, out = {}, []
    for _a, mn, ops in body:
        if mn.startswith("j"):
            out.append("j")
            continue
        ops = re.sub(r"#.*", "", ops).strip()
        ops = re.sub(r"-?0x[0-9a-f]+\(%rip\)", "CONST(%rip)", ops)
        ops = re.sub(r"(?<![0-9a-fx])0x0\(", "(", ops)
        ops = REG.sub(lambda m: names.setdefault(m.group(0), f"R{len(names)}"), ops)
        out.append(mn + " " + ops)
    return tuple(out)


def main_vloop(ins):
    """Boucle chaude : parmi les boucles les plus internes (qui n'en contiennent pas d'autre), celle qui fait le plus
    d'additions vectorielles."""
    ls = loops(ins)
    spans = [(l[0][0], l[-1][0]) for l in ls]
    inner = [l for l, (s, e) in zip(ls, spans) if not any(s <= s2 and e2 <= e and (s2, e2) != (s, e) for s2, e2 in spans)]
    inner = [l for l in inner if sum(1 for x in l if x[1].startswith("v")) >= 4]
    # densité d'instructions vectorielles : la boucle chaude vectorisée, pas une boucle de reste scalaire
    return max(inner, key=lambda l: sum(1 for x in l if x[1].startswith("v")) / len(l)) if inner else []


def main():
    tmp = tempfile.mkdtemp(prefix="cpp_check_")
    # versions et dialecte par défaut
    save("versions.txt", [
        "# Chaînes", sh(f"{GXX} --version | head -1"), sh(f"{CLANGXX} --version | head -1"),
        "# __cplusplus sans -std (dialecte par défaut)",
        "g++-16 : " + sh(f"{GXX} -dM -E -x c++ /dev/null | grep -w __cplusplus"),
        "clang++-23 : " + sh(f"{CLANGXX} -dM -E -x c++ /dev/null | grep -w __cplusplus"),
        "# bibliothèque C++ chargée à l'exécution par le binaire C++ de la campagne",
        sh(f"ldd {ROOT}/bench/cpp/ms | grep libstdc"),
        "# options de construction du banc", sh(f"tail -1 {ROOT}/bench/cpp/build.sh"), sh(f"tail -1 {ROOT}/bench/c/build.sh"),
        sh(f"tail -1 {ROOT}/bench/c_gcc/build.sh")])
    # manuel livré de GCC 16.2
    info = sh("zcat -f /opt/gcc-16/share/info/gcc.info* 2>/dev/null")
    keep = []
    for pat in (r"‘c\+\+23’\n.*?(?=\n\n)", r"‘c\+\+2c’\n.*?(?=\n\n)", r"‘gnu\+\+20’\n.*?(?=\n\n)", r"‘-freflection’\n.*?(?=\n\n)",
                r"The default is ‘uninitialized’ except for C\+\+26.*?(?=\n\n)"):
        m = re.search(pat, info, re.S)
        keep.append(m.group(0) if m else f"(introuvable : {pat})")
    save("gcc_manual.txt", ["# Extraits du manuel livré avec GCC 16.2 (/opt/gcc-16/share/info/gcc.info)", ""] + keep)
    # std::simd : garde de libstdc++, clang++ sur le banc
    vh = open("/opt/gcc-16/include/c++/16.2.0/bits/version.h").read()
    m = re.search(r"#if !defined\(__cpp_lib_simd\).*?#endif /\* !defined\(__cpp_lib_simd\) \*/", vh, re.S)
    clang_err = sh(f"cd {tmp} && {CLANGXX} -std=c++26 -O3 -march=cascadelake -pthread --gcc-toolchain=/opt/gcc-16 "
                   f"-o ms_clang {ROOT}/bench/cpp/ms.cpp 2>&1 | grep -m3 error")
    save("simd.txt", ["# libstdc++ 16 : condition de std::simd (bits/version.h) ; __cpp_lib_simd n'est pas défini",
                      m.group(0) if m else "(introuvable)", "",
                      "# clang++ 23 sur bench/cpp/ms.cpp avec la libstdc++ de GCC 16 (trois premières erreurs)", clang_err, "",
                      "# libc++ 23 (installée) : en-tête <simd> de C++26 ? en-têtes de std::experimental (TS Parallelism v2)",
                      sh("ls -d /usr/lib/llvm-23/include/c++/v1 /usr/lib/llvm-23/lib/libc++.so 2>&1"),
                      sh("ls /usr/lib/llvm-23/include/c++/v1/simd 2>&1"),
                      "experimental/ : " + sh("ls /usr/lib/llvm-23/include/c++/v1/experimental | tr '\\n' ' '")])
    # P2795
    p = os.path.join(PROBES, "p2795.cpp")
    lines = ["# Sonde p2795.cpp : tableau local non initialisé ; rangements d'un registre mis à zéro (vpxor) sur la pile"]
    for label, cmd in (("g++-16 -std=c++23", f"{GXX} -std=c++23"), ("g++-16 -std=c++26", f"{GXX} -std=c++26"),
                       ("g++-16 -std=c++26 -ftrivial-auto-var-init=uninitialized", f"{GXX} -std=c++26 -ftrivial-auto-var-init=uninitialized"),
                       ("clang++-23 -std=c++26", f"{CLANGXX} -std=c++26")):
        asm = [l.strip() for l in sh(f"{cmd} -O3 -march=cascadelake -S -o - {p}").splitlines()]
        zero = 0
        for i, l in enumerate(asm):  # registre mis à zéro puis rangé sur la pile dans les 8 instructions suivantes
            m = re.match(r"vpxor\s+%xmm(\d+), %xmm\1, %xmm\1", l)
            if m:
                zero += sum(1 for x in asm[i + 1:i + 9] if re.match(rf"vmovdq[ua]\s+%[xy]mm{m.group(1)}, -?\d*\(%rsp\)", x))
        lines.append(f"{label} : rangements à zéro sur la pile {zero}")
    camp = os.path.join(tmp, "cpp_cl")
    noinit = os.path.join(tmp, "cpp_cl_noinit")
    sh(f"{GXX} -std=c++26 -O3 -march=cascadelake -pthread -Wno-interference-size -o {camp} {ROOT}/bench/cpp/ms.cpp")
    sh(f"{GXX} -std=c++26 -ftrivial-auto-var-init=uninitialized -O3 -march=cascadelake -pthread -Wno-interference-size -o {noinit} "
       f"{ROOT}/bench/cpp/ms.cpp")
    lines.append(f"binaire C++ recompilé pour Cascade Lake identique à celui de la campagne : {filecmp.cmp(camp, ROOT + '/bench/cpp/ms', shallow=False)}")
    a, b = disasm(camp), disasm(noinit)

    def body(ins):
        return [mn + " " + re.sub(r"#.*", "", re.sub(r"-?0x[0-9a-f]+\(%rip\)", "RIP", re.sub(r"[0-9a-f]{5,} <[^>]*>", "ADDR", ops)))
                for _x, mn, ops in ins]
    kern = [k for k in a if re.match(r"(k\d|q\d)_", k)]
    changed = [k.split("(")[0] for k in kern if k in b and body(a[k]) != body(b[k])]
    harness = sorted({k.split("(")[0] for k in a if k in b and body(a[k]) != body(b[k]) and not re.match(r"(k\d|q\d)_", k)})
    lines += [f"noyaux (k*_ et q*_) comparés avec et sans -ftrivial-auto-var-init=uninitialized : {len(kern)} ; modifiés : {changed or 'aucun'}",
              f"autres fonctions modifiées (harnais, constructeurs) : {', '.join(harness[:14])}"]
    save("p2795.txt", lines)
    # réflexion
    r = os.path.join(PROBES, "refl.cpp")
    save("reflection.txt", ["# Sonde refl.cpp (P2996 : nombre de membres d'une structure à la compilation)",
                            "g++-16 -std=c++26 -freflection : " + sh(f"{GXX} -std=c++26 -freflection -o {tmp}/r {r} && {tmp}/r; echo code $?"),
                            "g++-16 -std=c++26 : " + sh(f"{GXX} -std=c++26 -o {tmp}/r2 {r} 2>&1 | grep -m1 error"),
                            "clang++-23 -std=c++26 -freflection : " + sh(f"{CLANGXX} -std=c++26 -freflection -o {tmp}/r3 {r} 2>&1 | grep -m1 error"),
                            "", "# Sonde refl_syntax.cpp (l'opérateur ^^ seul, sans en-tête)",
                            "g++-16 -std=c++26 -freflection : " + sh(f"{GXX} -std=c++26 -freflection -c -o {tmp}/s1.o {PROBES}/refl_syntax.cpp 2>&1 && echo compilé"),
                            "clang++-23 -std=c++26 -freflection : " + sh(f"{CLANGXX} -std=c++26 -freflection -c -o {tmp}/s2.o {PROBES}/refl_syntax.cpp 2>&1 | grep -m2 -E 'warning|error' | tr '\\n' ' '")])
    # K4 : C et C++ sous GCC (Cascade Lake), C par clang, C++ par clang++
    cg = os.path.join(tmp, "c_gcc_cl")
    cc = os.path.join(tmp, "c_clang_cl")
    sh(f"{GCC} -std=c23 -O3 -march=cascadelake -pthread -o {cg} {ROOT}/bench/c/ms.c")
    sh(f"{CLANG} -std=c23 -O3 -march=cascadelake -pthread -o {cc} {ROOT}/bench/c/ms.c")
    k4o = os.path.join(tmp, "k4_clang.o")
    sh(f"{CLANGXX} -std=c++26 -O3 -march=cascadelake --gcc-toolchain=/opt/gcc-16 -c -o {k4o} {PROBES}/k4.cpp")
    A, G, C, X = disasm(camp), disasm(cg), disasm(cc), disasm(k4o)
    lines = ["# K4 : boucle vectorielle principale (sauts arrière) ; instructions par itération et mnémoniques",
             f"C par clang recompilé pour Cascade Lake identique au binaire de la campagne : {filecmp.cmp(cc, ROOT + '/bench/c/ms', shallow=False)}"]
    for f in ("k4_natural", "k4_branchless"):
        la, lg, lc, lx = (main_vloop(fn(d, f)) for d in (A, G, C, X))
        lines.append(f"{f} : C++ g++ {len(la)} instr., C gcc {len(lg)} instr., mêmes instructions (multiensemble) : "
                     f"{collections.Counter(x[1] for x in la) == collections.Counter(x[1] for x in lg)} ; "
                     f"C clang {len(lc)} instr. ; C++ clang++ (sonde k4.cpp) {len(lx)} instr.")
        lines.append(f"   C clang : {sorted(set(x[1] for x in lc))} ; C++ clang++ : {sorted(set(x[1] for x in lx))}")
        lines.append(f"   C++ g++ : {sorted(set(x[1] for x in la))}")
    save("k4.txt", lines)
    # K9 : allocation des grilles du chemin tuned et mt, dans la boucle des répétitions ou avant, par implémentation.
    # Table explicite : (source, en-tête de la fonction, boucle des répétitions, allocation des grilles du chemin tuned/mt) ;
    # la sortie donne les numéros de ligne trouvés, pour relecture.
    K9SRC = [
        ("c", "bench/c/ms.c", r"static void run_k9\(", r"for \(int r = -warmup_count\(\)", r"aligned_alloc\(64, n \* 8\)"),
        ("cpp", "bench/cpp/ms.cpp", r"static void run_k9\(", r"for \(int r = -warmup_count\(\)", r"avec<double> a\(\(size_t\)M9 \* M9\)"),
        ("zig", "bench/zig/ms.zig", r"fn runK9\(", r"while \(r < reps\)", r"gpa\.alignedAlloc\(f64"),
        ("odin", "bench/odin/ms.odin", r"run_k9 :: proc", r"for r := -WARMUP", r"mem\.make_aligned\(\[\]f64, M9 \* M9, 64\)"),
        ("c3", "bench/c3/ms.c3", r"fn void run_k9\(", r"for \(int r = -g_warmup", r"alloc::malloc_aligned\(mem, M9 \* M9 \* 8, 64\)"),
        ("rust", "bench/rust/ms.rs", r"let init: Vec<f64> =", r"for r in -warmup\(\)\.\.reps", r"let mut a = init\.clone\(\);"),
        ("nim", "bench/nim/ms.nim", r"proc runK9\(", r"for r in -WARMUP \.\.< reps:", r"aligned_alloc\(64, csize_t\(M9 \* M9 \* 8\)\)"),
        ("d", "bench/d/ms.d", r"void runK9\(", r"foreach \(r; -WARMUP \.\. reps\)", r"aligned_alloc\(64, M9 \* M9 \* 8\)"),
        ("chapel", "bench/chapel/ms.chpl", r"proc runK9\(", r"for r in -warm\.\.<reps", r"var a, b: \[0\.\.<M9, 0\.\.<M9\] real;"),
        ("ada", "bench/ada/ms.adb", r"procedure Run_K9", r"for R in -Warm \.\. Reps - 1 loop", r"A : Grid_Acc := new Grid"),
        ("fortran", "bench/fortran/ms.f90", r"subroutine run_k9\(", r"do r = -warm, reps - 1", r"allocate \(ba\(NN \+ 8\), bb\(NN \+ 8\)\)"),
        ("julia", "bench/julia/ms.jl", r"function run_k9\(", r"for r in -WARMUP:reps-1", r"a = \[k9_init\(i, j\) for i in 0:M9-1, j in 0:M9-1\]"),
        ("csharp", "bench/csharp/Program.cs", r"static void RunK9\(", r"for \(int r = -Warmup; r < reps; r\+\+\)", r"NativeMemory\.AlignedAlloc\(M9 \* M9 \* 8, 64\)"),
        ("mojo", "bench/mojo/ms.mojo", r"def run_k9\(", r"for r in range\(-warmup, reps\):", r"unsafe_alloc\[Float64\]\(M9 \* M9, alignment=64\)"),
        ("go", "bench/go/ms.go", r"func runK9\(", r"for r := -warmup\(\); r < reps; r\+\+", r"a, b := make\(\[\]float64, M9\*M9\)"),
        ("java", "bench/java/Ms.java", r"static void runK9\(", r"for \(int r = -warmup\(\); r < reps; r\+\+\)", r"double\[\] a = new double\[M9 \* M9\]"),
    ]
    lines = ["# K9 : grilles du chemin tuned et mt allouées à chaque répétition (dans la boucle) ou une fois (avant), d'après le",
             "# source du banc (numéros de ligne : en-tête de la fonction, boucle des répétitions, allocation) ;",
             "# défauts de page par processus : results/cpp_check/data_facts.txt"]
    for l, path, fpat, lpat, apat in K9SRC:
        src = open(os.path.join(ROOT, path)).read().splitlines()
        f0 = next(i for i, x in enumerate(src) if re.search(fpat, x))
        lo = next(i for i in range(f0, len(src)) if re.search(lpat, src[i]))
        al = next(i for i in range(f0, len(src)) if re.search(apat, src[i]))
        lines.append(f"{l:8s}: {'à chaque répétition' if al > lo else 'une fois'} ({path} : fonction {f0 + 1}, "
                     f"boucle {lo + 1}, allocation {al + 1})")
    save("k9_harness.txt", lines)
    # K8 et Q1
    cpp = open(os.path.join(ROOT, "bench", "cpp", "ms.cpp")).read()
    csrc = open(os.path.join(ROOT, "bench", "c", "ms.c")).read()
    q1c = fn(A, "q1_tuned")
    q1g = fn(C, "q1_tuned")
    save("k8_q1.txt", ["# K8 tuned : signature de la construction de l'arène",
                       "C   : " + re.search(r"static int32_t a8_build\([^)]*\)", csrc).group(0),
                       "C++ : " + re.search(r"static int32_t a8_build\([^)]*\)", cpp).group(0),
                       "# Q1 tuned : produits 64 bits (vpmullq) et 32x32->64 (vpmuldq) dans le binaire de la campagne",
                       f"C++ g++ : vpmullq {sum(1 for x in q1c if x[1] == 'vpmullq')}, vpmuldq {sum(1 for x in q1c if x[1] == 'vpmuldq')}",
                       f"C clang : vpmullq {sum(1 for x in q1g if x[1] == 'vpmullq')}, vpmuldq {sum(1 for x in q1g if x[1] == 'vpmuldq')}"])
    # copies de la remarque : boucles de C++ par clang++ (cpp_clang) contre C par clang (c_ref), même hôte
    if os.path.exists(os.path.join(ROOT, "bench", "cpp_clang", "ms")) and os.path.exists(os.path.join(ROOT, "bench", "c_ref", "ms")):
        P, Q = disasm(os.path.join(ROOT, "bench", "cpp_clang", "ms")), disasm(os.path.join(ROOT, "bench", "c_ref", "ms"))
        lines = ["# Boucle principale de C par clang (c_ref) retrouvée à l'identique dans C++ par clang++ (cpp_clang) ?"]
        for f1, f2 in (("k1_aos", "k1_aos"), ("k1_soa", "k1_soa"), ("k2_chase", "k2_chase"), ("k4_natural", "k4_natural"),
                       ("k4_branchless", "k4_branchless"), ("k5_natural", "k5_natural"), ("k5_tuned", "k5_tuned"),
                       ("q6_tuned_k", "q6_tuned"), ("q1_tuned", "q1_tuned"), ("k9_rows", "k9_rows")):
            lb = [l for l in loops(fn(Q, f2))]
            la = [l for l in loops(fn(P, f1))]
            if not lb or not la:
                lines.append(f"{f1} : boucles introuvables")
                continue
            mb = max(lb, key=lambda l: (sum(1 for x in l if x[1].startswith("v")), len(l)))
            lines.append(f"{f1} : {'identique' if any(norm(l) == norm(mb) for l in la) else 'différente'} "
                         f"(C {len(mb)} instr. ; C++ {len(max(la, key=lambda l: (sum(1 for x in l if x[1].startswith('v')), len(l))))} instr.)")
        save("clang_loops.txt", lines)
    print("preuves écrites dans results/cpp_check/")


if __name__ == "__main__":
    main()
