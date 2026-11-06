#!/bin/sh
# Faits relevés pour la remarque sur FreePascal (docs/FPC.md, 5.2) : trois chaînes officielles (3.2.2 publiée,
# 3.2.4-rc2, instantané de la branche main), code produit, RTL et essais chronométrés sur la machine courante.
# Sortie : results/fpc_remark/facts.txt
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
SRC=$ROOT/tools/fpc_remark/src
W=$(mktemp -d)
C322="/opt/fpc/lib/fpc/3.2.2/ppcx64 -n @/opt/fpc/etc/fpc.cfg"
C324="/opt/fpc-324rc2/lib/fpc/3.2.4/ppcx64 -n @/opt/fpc-324rc2/etc/fpc.cfg"
CMAIN="/opt/fpc-main/lib/fpc/3.3.1/ppcx64 -n @/opt/fpc-main/etc/fpc.cfg"
OPT="-O3 -CpCOREAVX2 -OpCOREAVX2 -CfAVX2 -Xs-"
# compile $3 avec la chaîne $2 dans $W/$1 ; affiche les erreurs ; renvoie 0 si le binaire existe
cc() { d=$W/$1; mkdir -p $d; c=$2; f=$3; shift 3; $c $OPT "$@" -B -FU$d -FE$d $SRC/$f.pas > $d/$f.log 2>&1; \
  grep -E 'Error|Fatal' $d/$f.log | grep -v 'Compilation aborted' | head -3; [ -x $d/$f ]; }
# instructions d'une fonction (symbole dont le nom contient $3) du binaire $1/$2
dis() { s=$(nm $W/$1/$2 | grep -i -F "$3" | awk '{print $3}' | head -1); \
  objdump -d --no-show-raw-insn --disassemble="$s" $W/$1/$2 | grep -E '^\s+[0-9a-f]+:' | sed 's/^\s*[0-9a-f]*:\s*/    /'; }
mkdir -p "$ROOT/results/fpc_remark"
{
echo "== 1. chaînes"
for c in "$C322" "$C324" "$CMAIN"; do set -- $c; echo "$1 : $($1 -iVDW)"; done
echo "-- processeurs (-ic), FPU (-if), optimisations (-io)"
for c in "$C322" "$C324" "$CMAIN"; do set -- $c; echo "$($1 -iV) : CPU $($1 -ic | tr '\n' ' ')"; echo "    FPU $($1 -if | tr '\n' ' ')"; echo "    OPT $($1 -io | tr '\n' ' ')"; done
echo "== 2. TThread.SpinWait (unité classes de la RTL)"
for L in /opt/fpc/lib/fpc/3.2.2 /opt/fpc-324rc2/lib/fpc/3.2.4 /opt/fpc-main/lib/fpc/3.3.1; do O=$L/units/x86_64-linux/rtl/classes.o; \
  echo "-- $L"; objdump -d --no-show-raw-insn --disassemble='CLASSES$_$TTHREAD_$__$$_SPINWAIT$LONGWORD' $O | grep -E '^\s+[0-9a-f]+:' | sed 's/^\s*[0-9a-f]*:\s*/    /'; done
echo "== 3. assembleur en ligne AVX-512 (zmm)"
for n in 322:C322 324:C324 main:CMAIN; do v=${n%%:*}; eval c=\$${n##*:}; echo "-- $v"; cc $v "$c" asm512 && { $W/$v/asm512; objdump -d --no-show-raw-insn $W/$v/asm512 | grep -m2 zmm | sed 's/^\s*[0-9a-f]*:\s*/    /'; }; done
echo "== 4. alignement d'un type (« end align 64 »)"
for n in 322:C322 324:C324 main:CMAIN; do v=${n%%:*}; eval c=\$${n##*:}; echo "-- $v"; cc $v "$c" align64 && $W/$v/align64; done
echo "-- main, pile et New (align2.pas, -O3 puis -O-) :"
cc main "$CMAIN" align2 && $W/main/align2
mkdir -p $W/main0 && $CMAIN -O- -B -FU$W/main0 -FE$W/main0 $SRC/align2.pas > /dev/null 2>&1 && $W/main0/align2
echo "== 5. atomiques et lecture volatile (main)"
cc main "$CMAIN" atom && { $W/main/atom; for f in 'ATOM_$$_INCX' 'ATOM_$$_CASY' 'ATOM_$$_READF'; do echo "-- $f"; dis main atom "$f"; done; \
  echo "-- fpc_atomic_inc_64"; dis main atom 'fpc_atomic_inc_64'; }
echo "-- procédures Atomic* de l'unité system (main), paramètre d'ordre mémoire :"
/opt/fpc-main/bin/ppudump /opt/fpc-main/lib/fpc/3.3.1/units/x86_64-linux/rtl/system.ppu 2>/dev/null | grep -E '^(Procedure|Function) symbol .*[Aa]tomic' | awk '{print $3}' | sort -u | tr '\n' ' '; echo
echo "-- affinité (system, main) : $(/opt/fpc-main/bin/ppudump /opt/fpc-main/lib/fpc/3.3.1/units/x86_64-linux/rtl/system.ppu 2>/dev/null | grep -i -E '^(Procedure|Function) symbol .*affinity' | awk '{print $3}' | tr '\n' ' ')"
echo "== 6. intrinsèques x86 (main) : unité intrinsics, pause, Prefetch, Likely"
for u in system intrinsics; do /opt/fpc-main/bin/ppudump /opt/fpc-main/lib/fpc/3.3.1/units/x86_64-linux/rtl/$u.ppu > $W/$u.dump 2>/dev/null; \
  echo "$u : $(grep -c 'Constant symbol fpc_in_x86_' $W/$u.dump) constantes fpc_in_x86_* ; procédures x86 déclarées : $(grep -E '^Procedure symbol fpc_x86_' $W/$u.dump | awk '{print $3}' | tr '\n' ' ')"; done
echo "dont SSE/SSE2/MMX (après fpc_in_x86_pause) : $(grep 'Constant symbol fpc_in_x86_' $W/system.dump | sed -n '/fpc_in_x86_movss$/,$p' | wc -l)"
cc main "$CMAIN" hints && for f in 'HINTS_$$_SPIN' 'HINTS_$$_PF$POINTER'; do echo "-- $f"; dis main hints "$f"; done
for n in 322:C322 324:C324; do v=${n%%:*}; eval c=\$${n##*:}; cc $v "$c" pf322 && { echo "-- Prefetch, $v"; dis $v pf322 'PF322_$$_PF$POINTER'; }; done
for n in 322:C322 main:CMAIN; do v=${n%%:*}; eval c=\$${n##*:}; echo "-- Likely, $v :"; cc $v "$c" brhint && echo "    connu"; done
echo "== 7. TParallel.For (System.Threading, paquet vcl-compat)"
for L in /opt/fpc/lib/fpc/3.2.2 /opt/fpc-324rc2/lib/fpc/3.2.4 /opt/fpc-main/lib/fpc/3.3.1; do echo "$L : $(ls $L/units/x86_64-linux/vcl-compat/ 2>/dev/null | grep -c -i 'system.threading.ppu') system.threading.ppu"; done
cc main "$CMAIN" par && $W/main/par
echo "== 8. traitement vectoriel -Sv (main)"
echo "-- source de bench/fpc (array[0..3] of Single) :"; mkdir -p $W/sv && $CMAIN $OPT -Sv -B -FU$W/sv -FE$W/sv -oms $ROOT/bench/fpc/ms.pas 2>&1 | grep -E 'Error' | head -2
for fpu in SSE64 AVX2; do for d in "" "-dM256"; do echo "-- __m128$d, -Cf$fpu :"; mkdir -p $W/v$fpu$d; \
  $CMAIN -O3 -CpCOREAVX2 -Cf$fpu -Sv $d -B -FU$W/v$fpu$d -FE$W/v$fpu$d $SRC/vec.pas > $W/v$fpu$d/log 2>&1; \
  grep -E 'Error' $W/v$fpu$d/log | head -1; [ -x $W/v$fpu$d/vec ] && $W/v$fpu$d/vec; done; done
echo "== 9. cible FPU X86-64-V4 (main) : code flottant d'un produit scalaire"
for fpu in AVX2 AVX512F X86-64-V4; do mkdir -p $W/x$fpu; $CMAIN -O3 -CpCOREAVX2 -Cf$fpu -Xs- -B -FU$W/x$fpu -FE$W/x$fpu $SRC/x87.pas > /dev/null 2>&1; \
  s=$(nm $W/x$fpu/x87 | grep -i 'X87_$$_DOT' | awk '{print $3}'); \
  echo "-Cf$fpu : résultat $($W/x$fpu/x87) ; x87 : $(objdump -d --no-show-raw-insn --disassemble="$s" $W/x$fpu/x87 | grep -cE '\sf(ld|st|add|mul|stp)')  ; AVX : $(objdump -d --no-show-raw-insn --disassemble="$s" $W/x$fpu/x87 | grep -cE '\sv(add|mul)ss')"; done
echo "== 10. K5 naturel : borne High(a) ou Length(a) - 1 (bench/fpc_rq/ms.pas)"
for n in 322:C322: 322len:C322:-dLEN main:CMAIN:-dM128; do v=$(echo $n | cut -d: -f1); eval c=\$$(echo $n | cut -d: -f2); d=$(echo $n | cut -d: -f3); \
  mkdir -p $W/k5$v; $c $OPT -Sv $d -B -FU$W/k5$v -FE$W/k5$v -oms $ROOT/bench/fpc_rq/ms.pas > /dev/null 2>&1; \
  s=$(nm $W/k5$v/ms.o | grep -i 'K5NATURAL' | awk '{print $3}'); \
  echo "-- $v : $(objdump -d --no-show-raw-insn --disassemble="$s" $W/k5$v/ms.o | grep -cE '\scall') appel(s) ; accumulateur : $(objdump -d --no-show-raw-insn --disassemble="$s" $W/k5$v/ms.o | grep -E 'vaddss' | sed 's/^\s*[0-9a-f]*:\s*//')"; done
echo "== 11. essais chronométrés (machine courante)"
echo "-- K4 sans branchement, formes du masque (meilleure de 5 répétitions, 16 Mio)"
for n in 322:C322 main:CMAIN; do v=${n%%:*}; eval c=\$${n##*:}; echo "$v :"; cc $v "$c" k4forms && $W/$v/k4forms; done
echo "-- TDictionary<LongWord, TAgg> : recherche (tools/fpc_check/src/dict_lookup.pas)"
for n in 322:C322 324:C324 main:CMAIN; do v=${n%%:*}; eval c=\$${n##*:}; mkdir -p $W/d$v; \
  $c $OPT -B -FU$W/d$v -FE$W/d$v $ROOT/tools/fpc_check/src/dict_lookup.pas > /dev/null 2>&1; echo "$v :"; $W/d$v/dict_lookup | tail -4; done
} > "$ROOT/results/fpc_remark/facts.txt" 2>&1
rm -rf "$W"
echo "écrit : results/fpc_remark/facts.txt"
