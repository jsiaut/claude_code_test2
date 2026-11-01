#!/bin/sh
# Remarque sur C3 (docs/C3.md, section 2) : preuves des vérifications, depuis les sources de C3 0.8.5_1 (/opt/src/c3c,
# commit d1b1e44), des sondes de compilation et des binaires du banc. Sorties : results/c3_check/*.txt.
# Lecture et compilation seulement, rien n'est mesuré.
set -u
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
SRC=/opt/src/c3c
C3=$SRC/build/c3c
OUT=$ROOT/results/c3_check
P=$ROOT/tools/c3_check/probes
T=$(mktemp -d)
mkdir -p "$OUT"
cd "$SRC" || exit 1

{ $C3 --version; echo; git -C "$SRC" log --oneline -1; } > "$OUT/versions.txt" 2>&1

{ echo "# c3c --help"; $C3 --help 2>&1 | grep -E -- "-O[0-5] |--optlevel|--fp-math"
  echo; echo "# src/build/builder.c : réglages de -O3, -O4 et -O5"; sed -n '/case OPT_SETTING_O3:/,/case OPT_SETTING_O5:/p' src/build/builder.c
  echo; echo "# src/compiler/llvm_codegen.c : niveau d'optimisation -> pipeline de LLVM"; sed -n '/case OPTIMIZATION_LESS:/,/LLVM_O3;/p' src/compiler/llvm_codegen.c | head -12
  echo; echo "# src/build/builder.c : une option explicite l'emporte sur le réglage de -O"; grep -n "COPY_IF_DEFAULT(target->optlevel\|COPY_IF_DEFAULT(target->feature.fp_math" src/build/builder.c
} > "$OUT/options.txt" 2>&1

{ echo "# Sonde fpmath.c3 (C4) : mode strict (-O3) puis --fp-math=relaxed"
  $C3 compile "$P/fpmath.c3" -O3 --x86cpu=native -o $T/fs --emit-llvm --llvm-out $T/fs_ll >/dev/null 2>&1
  echo "## strict : réductions et additions flottantes avec drapeaux"; grep -h -o -E "call [a-z ]*float @llvm.vector.reduce.fadd[^(]*\([^)]*\)|fadd (reassoc|fast)[a-z ]*" $T/fs_ll/*.ll | sort | uniq -c
  $C3 compile "$P/fpmath.c3" -O3 --x86cpu=native --fp-math=relaxed -o $T/fr --emit-llvm --llvm-out $T/fr_ll >/dev/null 2>&1
  echo "## --fp-math=relaxed"; grep -h -o -E "call (reassoc |arcp |contract |nsz |fast )*float @llvm.vector.reduce.fadd[^(]*|fadd (reassoc|arcp|contract|fast)[a-z ]* <?[0-9 x]*float>?" $T/fr_ll/*.ll | sort | uniq -c
  echo; echo "# Attributs du compilateur (aucun contrôle local des mathématiques flottantes)"; grep -o '"@[a-z_]*"' src/compiler/symtab.c | tr '\n' ' '; echo
} > "$OUT/fpmath.txt" 2>&1

{ echo "# K5 tuned de C3 (bench/c3/ms, binaire de la campagne) : réduction finale"
  objdump -d --no-show-raw-insn "$ROOT/bench/c3/ms" | awk '/<ms.k5_tuned>:$/{p=1} p{print} p&&/ret/{exit}' | tail -34
  echo; echo "# Réduction finale de K5 tuned dans les autres implémentations (binaires du banc) : nombre de vaddss (chaîne ordonnée ~16, arbre 1)"
  for l in c cpp zig c3 d nim mojo go; do b=$ROOT/bench/$l/ms; s=$(nm "$b" 2>/dev/null | grep -i -E "k5.?tuned" | grep -i " t " | head -1 | awk '{print $3}'); [ -z "$s" ] && continue
    body=$(objdump -d --no-show-raw-insn "$b" | awk -v s="<$s>:" '$2==s{p=1;next} p&&/^$/{exit} p{print}')
    echo "$l : vaddss=$(echo "$body" | grep -c vaddss) vaddps=$(echo "$body" | grep -c vaddps)"; done
} > "$OUT/k5_reduction.txt" 2>&1

{ echo "# src/compiler/llvm_codegen.c, l. 1240-1248 : noalias posé à l'indice 1, quel que soit le paramètre"; sed -n '1240,1248p' src/compiler/llvm_codegen.c
  echo; echo "# Sonde noalias.c3 : signatures dans l'IR (-O3)"
  $C3 compile "$P/noalias.c3" -O3 --x86cpu=native -o $T/na --emit-llvm --llvm-out $T/na_ll >/dev/null 2>&1
  grep -h "^define.*\(first\|second\|slice_arg\)" $T/na_ll/*.ll | sed 's/ #0.*//'
  echo; echo "# Tests et bibliothèque standard qui utilisent @noalias"; grep -rln "@noalias" test lib | wc -l
  echo; echo "# releasenotes.md"; grep -n "@noalias" releasenotes.md; awk 'NR<=2010 && /^## /{h=$0} NR==2010{print "(ligne 2010 dans : " h ")"}' releasenotes.md
} > "$OUT/noalias.txt" 2>&1

{ echo "# src/compiler/asm_target.c : mnémoniques x86 reconnues (init_asm_x86)"
  awk '/static void init_asm_x86/,/^}/' src/compiler/asm_target.c | grep -o -E 'reg_instr[a-z_]*\(target, "[a-z0-9]+' | awk -F'"' '{print $2}' | sort -u > $T/mn.txt
  echo "nombre : $(wc -l < $T/mn.txt)"; tr '\n' ' ' < $T/mn.txt | fold -w 118; echo
  echo; echo "# Sondes (compilation -O3)"
  for f in asm_scalar asm_vaddps asm_vecload asm_fma asm_pause asm_mfence asm_string; do
    r=$($C3 compile "$P/$f.c3" -O3 --x86cpu=native -o $T/$f 2>&1 | grep -i -E "error" | sed 's/.*error: //' | head -1)
    echo "$f : ${r:-compile}"; done
  $C3 compile "$P/asm_string.c3" -O3 -o $T/as --emit-llvm --llvm-out $T/as_ll >/dev/null 2>&1
  echo "asm(\"...\") dans l'IR : $(grep -h -o 'asm sideeffect "[^"]*", "[^"]*"' $T/as_ll/*.ll | head -1)"
} > "$OUT/asm.txt" 2>&1

{ echo "# Sonde unchecked.c3"; $C3 compile "$P/unchecked.c3" -O3 -o $T/u 2>&1 | grep -i error | sed 's/.*error: //'
} > "$OUT/unchecked.txt" 2>&1

{ echo "# lib/std/io/file_mmap.c3 et lib/std/core/os/mem_vm.c3"; head -2 lib/std/io/file_mmap.c3; grep -n "fn FileMmap? mmap_open\|fn FileMmap? mmap_file" lib/std/io/file_mmap.c3
  grep -n "fn void\*? mmap_file" lib/std/core/os/mem_vm.c3
  echo; echo "# releasenotes.md"; grep -n "FileMmap\|vm::mmap_file" releasenotes.md; awk 'NR<=1142 && /^## /{h=$0} NR==1142{print "(ligne 1142 dans : " h ")"}' releasenotes.md
  echo; echo "# Sonde mmap.c3 sur /opt/msdata/k1_perm.u32, puis le premier mot lu par Python"
  $C3 compile "$P/mmap.c3" -O3 --x86cpu=native -o $T/mm >/dev/null 2>&1 && $T/mm /opt/msdata/k1_perm.u32
  python3 -c "import struct;print('python : premier mot %x' % struct.unpack('<I', open('/opt/msdata/k1_perm.u32','rb').read(4))[0])"
} > "$OUT/mmap.txt" 2>&1

{ echo "# Appels système et cache : @syscall, constantes SYS_*, sysconf"; grep -n "macro uptr @syscall" lib/std/core/builtin.c3
  grep -rn "const SYS_" lib/std/libc | head; echo "SYS_SCHED_SETAFFINITY : $(grep -rc 'SYS_SCHED_SETAFFINITY' lib/std | awk -F: '{s+=$2} END {print s}') occurrence(s)"
  echo "sched_setaffinity : $(grep -rc 'sched_setaffinity' lib/std | awk -F: '{s+=$2} END {print s}') occurrence(s)"
  grep -rn "fn CLong sysconf" lib/std; echo "_SC_LEVEL1_DCACHE_LINESIZE : $(grep -rc '_SC_LEVEL1_DCACHE' lib/std | awk -F: '{s+=$2} END {print s}') occurrence(s)"
} > "$OUT/syscall_sysconf.txt" 2>&1

{ echo "# Builtins \$\$ utilisés par la bibliothèque standard (opérations génériques de LLVM, aucune propre à x86)"
  grep -rhoE '\$\$[a-z_0-9]+' lib/std | sort -u | tr '\n' ' ' | fold -w 118; echo
  echo; echo "# Sonde c2_llvm.c3 : intrinsèques de LLVM par extern @cname (non documenté)"
  $C3 compile "$P/c2_llvm.c3" -O3 --x86cpu=native -o $T/c2 --emit-asm --asm-out $T/c2s 2>&1 | grep -o "undefined reference to \`[^']*'" | sort -u
  echo "instructions émises : $(grep -h -o -E '^\s+(pause|pext[a-z]*)' $T/c2s/*.s | sort | uniq -c | tr '\n' ' ')"
} > "$OUT/c2.txt" 2>&1

{ echo "# Génériques (releasenotes.md, sections 0.7.9 et 0.8.0)"; grep -n "Generics using ad-hoc\|Module-based generics\|Removed deprecated .module foo" releasenotes.md
  echo; echo "# Slice2d"; grep -n "struct Slice2d" lib/std/core/slice2d.c3
} > "$OUT/generics_slice2d.txt" 2>&1

{ echo "# lib/std/threads/os/thread_posix.c3 : NativeThread.create attend le démarrage du fils (Linux)"
  awk '/fn void\? NativeThread.create/,/^}/' lib/std/threads/os/thread_posix.c3; awk '/fn void\* callback/,/^}/' lib/std/threads/os/thread_posix.c3
} > "$OUT/threads.txt" 2>&1

{ echo "# TBAA dans l'IR du banc (C3 -O3) et de la référence C (clang -O3)"
  $C3 compile "$ROOT/bench/c3/ms.c3" -O3 --x86cpu=native -o $T/ms --emit-llvm --llvm-out $T/ms_ll >/dev/null 2>&1
  echo "C3 : $(cat $T/ms_ll/*.ll | grep -c '!tbaa') métadonnées !tbaa"
  clang -O3 -march=native -S -emit-llvm "$ROOT/bench/c/ms.c" -o $T/c.ll 2>/dev/null; echo "C : $(grep -c '!tbaa' $T/c.ll) métadonnées !tbaa"
  echo; echo "# Q1 naturel de C3 (binaire de la campagne) : les pointeurs des colonnes sont relus dans la boucle"
  objdump -d --no-show-raw-insn "$ROOT/bench/c3/ms" | awk '/<ms.q1_natural>:$/{p=1} p{print} p&&/^$/{exit}'
} > "$OUT/tbaa_q1.txt" 2>&1

{ echo "# lib/std/core/alloc.c3 : alloc::new sans valeur initiale -> calloc par l'interface Allocator"; sed -n '/^macro new(Allocator allocator/,/^}/p' lib/std/core/alloc.c3
  echo; echo "# K8 naturel de C3 (binaire de la campagne) : appels de t_build"; objdump -d --no-show-raw-insn "$ROOT/bench/c3/ms" | awk '/<ms.t_build>:$/{p=1} p{print} p&&/^$/{exit}' | grep call
  echo; echo "# src/compiler/llvm_codegen_expr.c : .dyn_search, recherche linéaire dans la table de méthodes, sans cache"; grep -n "dyn_search\|next_parent\|missing_function" src/compiler/llvm_codegen_expr.c | head -8
  echo; echo "# lib/std/collections/hashmap.c3 : table chaînée, une Entry allouée par insertion"; sed -n '/^struct Entry/,/^}/p' lib/std/collections/hashmap.c3; grep -n "Entry\* entry = alloc::new" lib/std/collections/hashmap.c3
} > "$OUT/k8_k7.txt" 2>&1
rm -rf "$T"
ls "$OUT"
