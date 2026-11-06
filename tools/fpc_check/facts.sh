#!/bin/sh
# Faits relevés en écrivant le banc FreePascal (docs/FPC.md, 2.4) : chaîne, code produit, RTL et essais chronométrés
# sur la machine courante. Sortie : results/fpc_check/facts.txt
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
SRC=$ROOT/tools/fpc_check/src
W=$(mktemp -d)
FPC="/opt/fpc/bin/fpc -n @/opt/fpc/etc/fpc.cfg -O3 -CpCOREAVX2 -OpCOREAVX2 -CfAVX2"
U=/opt/fpc/lib/fpc/3.2.2/units/x86_64-linux
# corps d'une fonction de l'assembleur de FPC (-al), sans commentaires ni étiquettes de CFI
body() { awk -v f="$2" 'index($0, f) == 1 && /:$/ {p = 1} p && !/^[[:space:]]*#/ && !/^\.Lc/ && !/cfi/ {print} p && /^\.Le/ {exit}' "$1"; }
mkdir -p "$ROOT/results/fpc_check"
{
echo "== 1. chaîne"
/opt/fpc/bin/fpc -iW; echo "cible : $(/opt/fpc/bin/fpc -iTP)-$(/opt/fpc/bin/fpc -iTO) ; processeurs : $(/opt/fpc/bin/fpc -ic | tr '\n' ' ') ; FPU : $(/opt/fpc/bin/fpc -if | tr '\n' ' ')"
echo "fpc.cfg livré, mode release :"; grep -A3 '^#IFDEF RELEASE' /opt/fpc/etc/fpc.cfg
echo "options -O : $(/opt/fpc/bin/fpc -h 2>&1 | grep -E '^ +-O[1234] ' | tr -s ' ' | tr '\n' ';')"
echo "-O3 / -O4 : disposition d'un record et d'une classe {Byte; Int64; Byte; LongInt} (taille, décalages) et réduction"
for O in -O3 -O4; do mkdir -p $W/o$O; /opt/fpc/bin/fpc -n @/opt/fpc/etc/fpc.cfg $O -B -FU$W/o$O -FE$W/o$O $SRC/o4_layout.pas > /dev/null 2>&1; \
  $FPC $O -al -FU$W/o$O $SRC/dot.pas > /dev/null 2>&1; \
  echo "$O : $($W/o$O/o4_layout | tr '\n' ' ') ; produit scalaire : $(grep -c vfmadd $W/o$O/dot.s) vfmadd, $(grep -c vaddss $W/o$O/dot.s) vaddss"; done
echo "== 2. -Sv ne change rien sans expression vectorielle (source du banc, -dSCALAR, avec et sans -Sv)"
mkdir -p $W/a $W/b
$FPC -dSCALAR -B -FU$W/a -FE$W/a -oms $ROOT/bench/fpc/ms.pas > /dev/null 2>&1
$FPC -dSCALAR -Sv -B -FU$W/b -FE$W/b -oms $ROOT/bench/fpc/ms.pas > /dev/null 2>&1
echo "sans -Sv $(sha256sum $W/a/ms | cut -c1-16) ; avec -Sv $(sha256sum $W/b/ms | cut -c1-16)"
echo "== 3. code produit du banc (bench/fpc, -al)"
mkdir -p $W/s && cp $ROOT/bench/fpc/ms.pas $ROOT/bench/fpc/msvec.pas $W/s/ && (cd $W/s && $FPC -Sv -al -B -oms ms.pas > /dev/null 2>&1)
echo "-- K5 naturel (accumulateur sur la pile ; High(a) appelle fpc_dynarray_high) :"; body $W/s/ms.s 'P$MS_$$_K5NATURAL' | grep -E 'call|ss'
echo "-- K5 tuned scalaire (copie fpc_scal) : $(body $W/s/ms.s 'P$MS_$$_K5TUNED$' | grep -c vfmadd231ss) vfmadd231ss, $(body $W/s/ms.s 'P$MS_$$_K5TUNED$' | grep -c vmovaps) vmovaps"
echo "-- K5 tuned -Sv (msvec) : $(body $W/s/msvec.s 'MSVEC_$$_K5TUNEDV' | grep -cE '^\s+mulps') mulps, $(body $W/s/msvec.s 'MSVEC_$$_K5TUNEDV' | grep -cE '^\s+addps') addps (encodage SSE classique), $(body $W/s/msvec.s 'MSVEC_$$_K5TUNEDV' | grep -cE 'vmov(a|u)ps\s+%xmm[0-9]+,[0-9]*\(%rsp\)') rangements des accumulateurs sur la pile"
echo "-- K3 (RMW puis écriture simple) :"; body $W/s/ms.s 'P$MS_$$_K3WORKER' | grep -E 'call|addq\s+\$1,\('
echo "-- K4 naturel (un branchement par octet) :"; body $W/s/ms.s 'P$MS_$$_K4NATURAL' | grep -E 'cmpb|jnae|addq'
echo "-- K9 tuned (boucle intérieure) :"; body $W/s/ms.s 'P$MS_$$_K9ROWS' | grep -cE 'vaddsd|vmulsd' | sed 's/^/instructions flottantes : /'
echo "-- K10 tuned, attente du producteur :"; body $W/s/ms.s 'P$MS_$$_SQPROD' | sed -n '/Lj.*:/,/je/p' | head -8
echo "== 4. RTL (system.o)"
objdump -d --no-show-raw-insn $U/rtl/system.o 2>/dev/null | grep -A3 -E '<SYSTEM_\$\$_(READBARRIER|WRITEBARRIER|READWRITEBARRIER)>:' | grep -E '>:|fence|ret'
objdump -d --no-show-raw-insn $U/rtl/system.o 2>/dev/null | grep -A6 '<SYSTEM_\$\$_INTERLOCKEDINCREMENT64\$INT64\$\$INT64>:' | head -6
echo "== 5. essais chronométrés (machine courante)"
mkdir -p $W/t
for p in q1_forms dict_lookup dict_k7; do
  $FPC -B -FU$W/t -FE$W/t $SRC/$p.pas > $W/t/$p.log 2>&1 || { echo "compilation de $p : échec"; tail -3 $W/t/$p.log; }
  echo "-- $p"; $W/t/$p | tail -6
done
for p in k5k9_forms k1soa_forms; do
  $FPC -Sv -B -FU$W/t -FE$W/t $SRC/$p.pas > $W/t/$p.log 2>&1 || { echo "compilation de $p : échec"; tail -3 $W/t/$p.log; }
  echo "-- $p (-Sv)"; $W/t/$p | tail -10
done
} > "$ROOT/results/fpc_check/facts.txt" 2>&1
rm -rf "$W"
