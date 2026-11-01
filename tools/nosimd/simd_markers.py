#!/usr/bin/env python3
"""Sensibilité « sans SIMD explicite » (docs/NOSIMD.md, section 2) : fonctions de chaque implémentation qui contiennent
des marqueurs de SIMD explicite (types vectoriels ou intrinsèques), puis les lignes trouvées dans les fonctions dont le
classement demande une lecture (faux positifs : types uint8/int8, alias déclarés entre deux fonctions, pause, prefetch).
Lecture seule ; sortie sur la sortie standard (results/nosimd/markers.txt)."""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MARK = re.compile(
    r"_mm[0-9]*_|__m512|__m256|__m128|@Vector|#simd|\bsimd\.|std::simd|stdx::|ss::vec|core\.simd|"
    r"\b(?:float|double|int|long|short|ubyte|byte|uint|ulong)(?:4|8|16)\b(?!_)|"
    r"M512|vector_type|__builtin_ia32|SIMD\[|Vector512|Vector256|Vector128|Vector<|FloatVector|IntVector|LongVector|"
    r"DoubleVector|ByteVector|archsimd|VecElement|llvmcall|\[<[0-9]+>\]|Avx512|Avx2\.|Avx\.|Sse\d*\.|Bmi2\.|"
    r"X16#|X8#|X4#|X32#|X64#|extern proc|importc|ldc\.gccbuiltins|ldc\.simd|Popcnt\.|pext|gccbuiltin")
FUNC = {
    "c": r"^(?:__attribute__\S*\s+)*(?:static\s+)?(?:inline\s+)?[\w\s\*]+?\b(\w+)\s*\([^;]*$",
    "cpp": r"^(?:\[\[[^\]]*\]\]\s*)?(?:static\s+)?(?:inline\s+)?[\w:<>,\s\*&]+?\b(\w+)\s*\([^;]*$",
    "zig": r"^\s*(?:pub\s+)?(?:noinline\s+|inline\s+)?fn\s+(\w+)", "odin": r"^\s*(\w+)\s*::\s*(?:#force_\w+\s+)?proc",
    "c3": r"^\s*(?:fn|macro)\s+[\w\[\]<>*]+\s+(\w+)\s*\(", "rust": r"^\s*(?:pub\s+)?(?:unsafe\s+)?fn\s+(\w+)",
    "nim": r"^\s*(?:proc|func|template|iterator)\s+(\w+)",
    "d": r"^\s*(?:pragma\([^)]*\)\s*)?(?:static\s+)?(?:@\w+\s+)*[\w\[\]!().*]+\s+(\w+)\s*\([^;]*\)\s*(?:@\w+\s*|nothrow\s*|pure\s*)*\{?\s*$",
    "ada": r"^\s*(?:procedure|function)\s+(\w+)", "mojo": r"^\s*(?:fn|def)\s+(\w+)",
    "csharp": r"^\s*(?:\[[^\]]*\]\s*)?(?:(?:static|unsafe|public|private|internal)\s+)+[\w<>\[\],\s\*]+?\s(\w+)\s*\(",
    "java": r"^\s*(?:(?:static|public|private|final)\s+)+[\w<>\[\],\s]+?\s(\w+)\s*\(", "go": r"^func\s+(?:\([^)]*\)\s*)?(\w+)",
    "julia": r"^\s*(?:@\w+\s+)*function\s+(\w+)", "chapel": r"^\s*(?:inline\s+|export\s+)?proc\s+(\w+)",
    "fortran": r"^\s*(?:(?:pure|elemental|recursive)\s+)*(?:subroutine|(?:[\w()=*]+\s+)?function)\s+(\w+)",
    "haskell": r"^(\w+)\s*::", "js": r"^\s*function\s+(\w+)", "python": r"^\s*def\s+(\w+)", "ocaml": r"^let\s+(?:rec\s+)?(?:\[@[^\]]*\]\s*)?(\w+)",
    "lua": r"^\s*(?:local\s+)?function\s+(\w+)",
}
FILES = {"c": ["bench/c/ms.c"], "cpp": ["bench/cpp/ms.cpp"], "zig": ["bench/zig/ms.zig"], "odin": ["bench/odin/ms.odin"],
         "c3": ["bench/c3/ms.c3"], "rust": ["bench/rust/ms.rs"], "nim": ["bench/nim/ms.nim"], "d": ["bench/d/ms.d"],
         "d_fix": ["bench/d_fix/ms.d"], "ada": ["bench/ada/ms.adb"], "mojo": ["bench/mojo/ms.mojo"],
         "csharp": ["bench/csharp/Program.cs"], "java": ["bench/java/Ms.java"], "go": ["bench/go/ms.go"],
         "julia": ["bench/julia/ms.jl"], "chapel": ["bench/chapel/ms.chpl"], "fortran": ["bench/fortran/ms.f90", "bench/fortran/tuned.f90"],
         "haskell": ["bench/haskell/Ms.hs"], "js": ["bench/js/ms.js"], "python": ["bench/python/ms.py"], "ocaml": ["bench/ocaml/ms.ml"],
         "lua": ["bench/lua/ms.lua"]}
READ = {"c": ["sq_prod", "sq_cons"], "cpp": ["(global)", "q1_natural", "cons", "prod"], "rust": ["run_k7"],
        "nim": ["secs", "prefetchw", "cpuRelax", "k4Natural", "k4Branchless", "runK4", "runK5", "q6Tuned", "runK6"],
        "d": ["(global)"], "ada": ["Pause", "V", "K5_Tuned"], "mojo": ["k1_aos", "run_k5", "q6_natural", "ld8", "run_k6"],
        "csharp": ["RunK7", "Ld8", "Ld32"], "java": ["bench"], "go": ["(global)", "runK5"],
        "fortran": ["load_i8", "k4_natural", "k4_branchless", "run_k4", "run_k5", "q6_tuned", "q1_tuned"]}


def scan(impl):
    lang = impl.split("_")[0]
    for f in FILES[impl]:
        cur = "(global)"
        for n, line in enumerate(open(os.path.join(ROOT, f), encoding="utf-8", errors="replace"), 1):
            m = re.match(FUNC[lang], line)
            if m and m.group(1) not in ("if", "for", "while", "switch", "return", "else"):
                cur = m.group(1)
            if MARK.search(line) and not line.strip().startswith(("//", "--", "#", "!")):
                yield f, n, cur, line.strip()


def main():
    print("# Fonctions contenant des marqueurs de SIMD explicite (nombre de lignes)")
    for impl in FILES:
        hits = {}
        for _f, _n, cur, _line in scan(impl):
            hits[cur] = hits.get(cur, 0) + 1
        print(f"{impl}: " + (", ".join(f"{k}({v})" for k, v in hits.items()) or "aucune"))
    print("\n# Lignes lues à la main (faux positifs et cas limites)")
    for impl, funcs in READ.items():
        for f, n, cur, line in scan(impl):
            if cur in funcs:
                print(f"{impl} {f}:{n} [{cur}] {line[:160]}")


if __name__ == "__main__":
    sys.exit(main())
