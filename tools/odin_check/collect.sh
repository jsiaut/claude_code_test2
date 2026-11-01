#!/bin/sh
# Remarque sur Odin (docs/ODIN.md, section 2) : preuves des vérifications, depuis les sources d'Odin dev-2026-10
# (/opt/src/odin, commit 84bc3fc), des sondes et des binaires du banc. Sorties : results/odin_check/*.txt.
# Lecture et compilation seulement, rien n'est mesuré.
set -u
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
SRC=/opt/src/odin
ODIN=$SRC/odin
OUT=$ROOT/results/odin_check
P=$ROOT/tools/odin_check/probes
T=$(mktemp -d)
mkdir -p "$OUT"
cd "$SRC" || exit 1

{ $ODIN version; git -C "$SRC" describe --tags; git -C "$SRC" log --oneline -1; } > "$OUT/versions.txt" 2>&1

{ echo "# results/blind_notation.json : notes du juge à l'aveugle pour Odin C2 (règle A = ma règle v2)"
  python3 -c "
import json
for x in json.load(open('$ROOT/results/blind_notation.json'))['cells']:
    if x['lang'] == 'odin' and x['item'] == 'C2': print(json.dumps(x, ensure_ascii=False))"
  echo; echo "# Liaisons actives vers des intrinsèques de LLVM (foreign + @(link_name=\"llvm.…\")) dans core et base"
  python3 -c "
import re, glob
tot = {}
for f in glob.glob('core/**/*.odin', recursive=True) + glob.glob('base/**/*.odin', recursive=True):
    s = open(f, encoding='utf-8', errors='replace').read()
    s = re.sub(r'/\*.*?\*/', '', s, flags=re.S); s = '\n'.join(l.split('//')[0] for l in s.split('\n'))
    n = len(re.findall(r'link_name\s*=\s*\"llvm\.', s))
    if n: tot[f] = n
print('total', sum(tot.values()), '; core:simd/x86', sum(v for k, v in tot.items() if 'simd/x86' in k),
      '; core:sys/llvm', sum(v for k, v in tot.items() if 'sys/llvm' in k), '; core:simd/arm', sum(v for k, v in tot.items() if 'simd/arm' in k))"
  echo; echo "# #const pour les opérandes immédiats (core:simd/x86)"; grep -rn "#const" core/simd/x86/*.odin | head -3
  echo; echo "# Sonde c2.odin : vpconflictd et vpternlogd (intrinsèques absentes de core:simd/x86)"
  $ODIN build "$P/c2/c2.odin" -file -o:speed -microarch:native -out:$T/c2 >/dev/null 2>&1 && $T/c2
  echo "vpconflictd : $(objdump -d --no-show-raw-insn $T/c2 | grep -c vpconflictd) ; vpternlogd : $(objdump -d --no-show-raw-insn $T/c2 | grep -c vpternlogd)"
  echo; echo "# analysis/capabilities_v2.py : précédents en règle v2"; grep -n '("julia", "C2")\|("mojo", "C2")' "$ROOT/analysis/capabilities_v2.py"
} > "$OUT/c2.txt" 2>&1

{ echo "# src/types.cpp : indices de bit de OdinFastMathFlag"; grep -n -A3 "enum OdinFastMathFlag" src/types.cpp
  echo; echo "# src/llvm_backend_opt.cpp : les indices sont testés comme des masques (Allow_Reassoc = 0 n'est jamais posé)"; sed -n 61,64p src/llvm_backend_opt.cpp
  echo; echo "# odin build -help : aucune option globale de mathématiques rapides"; $ODIN build -help 2>&1 | grep -i -c "fast" | sed 's/^/occurrences de « fast » : /'
} > "$OUT/fast_math.txt" 2>&1

{ echo "# src/build_settings.cpp : niveaux d'optimisation"; sed -n '/^enum OptimizationLevel/,/^};/p' src/build_settings.cpp
  echo; echo "# src/llvm_backend_passes.cpp : pipeline de LLVM par niveau"; grep -n "case 2:\|case 3:\|default<O2>\|default<O3>" src/llvm_backend_passes.cpp | head -6
  echo; echo "# -o:aggressive n'a pas d'autre effet"; grep -rn "OptimizationLevel_Aggressive" src/*.cpp
} > "$OUT/optlevels.txt" 2>&1

{ echo "# base/runtime/heap_allocator.odin : sur-allocation pour l'alignement"; grep -n "space := \|a := max\|heap_alloc(space" base/runtime/heap_allocator.odin
  echo; echo "# base/runtime/heap_allocator_unix.odin : calloc par défaut"; sed -n '/^_heap_alloc ::/,/^}/p' base/runtime/heap_allocator_unix.odin
  echo; echo "# Sonde usable.c : bloc occupé par 24 et 39 octets"; cc -O2 -o $T/usable "$P/alloc/usable.c" && $T/usable
  echo; echo "# K8 naturel (binaire de la campagne) : t_build -> mem_alloc_bytes -> appel indirect -> heap_allocator_proc -> calloc"
  objdump -d --no-show-raw-insn "$ROOT/bench/odin/ms" | awk '$2=="<ms::t_build>:"{p=1;next} p&&/^$/{exit} p{print}' | grep call
  objdump -d --no-show-raw-insn "$ROOT/bench/odin/ms" | awk '$2=="<runtime::mem_alloc_bytes>:"{p=1;next} p&&/^$/{exit} p{print}' | grep -E "call" | head -2
} > "$OUT/allocator.txt" 2>&1

{ echo "# core/time/time_linux.odin et core/sys/linux/sys.odin : lecture d'horloge par appel système brut (sans vDSO)"
  grep -n -A2 "^_tick_now" core/time/time_linux.odin; grep -n -A3 "^clock_gettime ::" core/sys/linux/sys.odin
} > "$OUT/clock.txt" 2>&1

{ echo "# Les 14 noyaux que le banc C déclare noinline"
  python3 -c "
import re
print(' '.join(re.findall(r'noinline\)\)\s+static\s+[\w ]+?\b(\w+)\s*\(', open('$ROOT/bench/c/ms.c').read())))"
  K="k1_natural k1_aos k1_soa k2_chase k4_natural k4_branchless k5_natural k5_tuned q6_natural q6_tuned q1_natural q1_tuned k9_natural k9_rows"
  for b in odin odin_fix; do f="$ROOT/bench/$b/ms"; [ -f "$f" ] || continue
    s=$(nm "$f" | grep ' t ms::' | awk '{print $3}' | sed 's/ms:://; s/\$.*//' | sort -u)
    abs=""; for k in $K; do echo "$s" | grep -q -x "$k" || abs="$abs $k"; done
    echo "bench/$b/ms : noyaux absents (inlinés)$abs"; done
  echo; echo "# Seule annotation du banc de la campagne"; grep -n "optimization_mode\|force_no_inline" "$ROOT/bench/odin/ms.odin"
} > "$OUT/inlining.txt" 2>&1

{ echo "# Q1 tuned : comptage de chaque groupe"; grep -n "cnt\[g\] +=" "$ROOT/bench/odin/ms.odin"
  for spec in "c:__builtin_popcount" "zig:@popCount" "rust:count_ones" "cpp:reduce_count" "csharp:PopCount" "c3:select\(m, \(int\[<16>\]\)1" "mojo:reduce_add\(\)\)" "d_fix:cnt\[g\] -= m"; do l=${spec%%:*}; pat=${spec#*:}
    f=$(ls "$ROOT"/bench/$l/ms.* "$ROOT"/bench/$l/Program.cs 2>/dev/null | grep -v "\.o$" | head -1); echo "$l : $(grep -n -m1 -E "$pat" "$f" | sed 's/^ *//' | tr -s ' \t' ' ' | cut -c1-110)"; done
  echo; echo "# Binaires de la campagne : popcnt et permutations dans Q1 tuned"
  for spec in "odin:ms::q1_tuned" "c:q1_tuned" "zig:ms.q1Tuned" "c3:ms.q1_tuned"; do l=${spec%%:*}; s=${spec#*:}
    body=$(objdump -d --no-show-raw-insn "$ROOT/bench/$l/ms" | awk -v s="<$s>:" '$2==s{p=1;next} p&&/^$/{exit} p{print}')
    echo "$l : $(echo "$body" | wc -l) instructions, popcnt $(echo "$body" | grep -c popcnt), permutations $(echo "$body" | grep -c -E 'vpshuf|vperm|vpunpck|vextract|vpalignr|vshuf|valign')"; done
  echo; echo "# core:simd : extract_msbs et card existent dans dev-2026-10"; grep -n "^extract_msbs ::" core/simd/simd.odin; grep -n "^card :: proc" base/runtime/core_builtin.odin
} > "$OUT/q1.txt" 2>&1
rm -rf "$T"
ls "$OUT"
