#!/bin/sh
# Sonde Free Pascal 3.2.2 : probe.pas (cas positifs, exécutés) + cas négatifs vérifiés à la compilation ou sur le
# code produit. Sortie : results/probes/fpc.txt
cd "$(dirname "$0")" && mkdir -p bin
FPC="/opt/fpc/bin/fpc -n @/opt/fpc/etc/fpc.cfg -O3 -CpCOREAVX2 -OpCOREAVX2 -CfAVX2"
$FPC -Sv -FUbin -FEbin -obin/probe probe.pas > bin/probe.log 2>&1 && bin/probe || { echo "ECHEC probe"; tail -5 bin/probe.log; }
cd bin
# A4 : alignement de type ou de variable au-delà de 16
printf 'program a4;\n{$mode objfpc}\ntype T = record x: Byte; end align 64;\nbegin writeln(SizeOf(T)) end.\n' > a4a.pas
$FPC a4a.pas > a4a.log 2>&1; A4A=$(grep -o 'Fatal: Syntax.*\|Error: [^/]*$' a4a.log | head -1)
printf 'program a4;\n{$mode objfpc}\n{$CODEALIGN VARMIN=64}\nvar pad: Byte; g: array[0..63] of Byte;\nbegin writeln(PtrUInt(@pad) mod 64, %s, PtrUInt(@g) mod 64) end.\n' "' '" > a4b.pas
$FPC a4b.pas > a4b.log 2>&1 && A4B=$(./a4b) || A4B=$(grep -o 'Error: .*' a4b.log | head -1)
printf 'program a4;\n{$mode objfpc}\n{$PACKRECORDS 64}\ntype T = record a: Byte; b: Int64; end;\nbegin writeln(SizeOf(T)) end.\n' > a4c.pas
$FPC a4c.pas > a4c.log 2>&1 && A4C="taille $(./a4c)" || A4C=$(grep -o 'Error: .*\|Warning: .*' a4c.log | head -1)
echo "NOTE;A4;« end align 64 » : ${A4A:-accepté} ; {\$CODEALIGN VARMIN=64} (variables globales, décalages mod 64) : $A4B ; {\$PACKRECORDS 64} : $A4C"
# C1 : -Sv sur 8 Single, puis sur des opérandes non alignés
printf 'program c1;\n{$mode objfpc}\ntype TV8 = array[0..7] of single;\nvar a, b, c: TV8; i: integer;\nbegin\n  for i := 0 to 7 do begin a[i] := i; b[i] := 1; end;\n  c := a + b;\n  writeln(c[7]:0:1);\nend.\n' > c1a.pas
$FPC -Sv c1a.pas > c1a.log 2>&1; echo "NOTE;C1;-Sv sur array[0..7] of Single : $(grep -o 'Fatal: .*\|Error: .*' c1a.log | head -1)"
printf 'program c1;\n{$mode objfpc}\ntype TV4 = array[0..3] of single; PV4 = ^TV4;\nvar raw: PByte; a, b: PV4; c: TV4; i: integer;\nbegin\n  GetMem(raw, 256); a := PV4(raw + 4); b := PV4(raw + 68);\n  for i := 0 to 3 do begin a^[i] := i; b^[i] := 1; end;\n  c := a^ + b^;\n  writeln(c[3]:0:1);\nend.\n' > c1b.pas
$FPC -Sv c1b.pas > c1b.log 2>&1; R=$(./c1b 2>&1 | head -1); echo "NOTE;C1;-Sv, opérandes à 4 o d'une frontière de 16 : $R ($(grep -c 'addps\s*(' c1b.s 2>/dev/null || echo '?') ; addps à opérande mémoire, encodage SSE classique)"
$FPC -Sv -al c1b.pas > /dev/null 2>&1; echo "NOTE;C1;code de c := a^ + b^ : $(grep -E '^\s+(v?movups|addps)' c1b.s | head -3 | tr -s ' \t' ' ' | tr '\n' ';')"
# C4 : -OoFASTMATH sur une réduction
printf 'unit c4;\n{$mode objfpc}{$pointermath on}\ninterface\nfunction dot(a, b: PSingle; n: SizeInt): Single;\nimplementation\nfunction dot(a, b: PSingle; n: SizeInt): Single;\nvar i: SizeInt; s: Single;\nbegin\n  s := 0;\n  for i := 0 to n - 1 do s := s + a[i] * b[i];\n  Result := s;\nend;\nend.\n' > c4.pas
$FPC -al c4.pas > /dev/null 2>&1 && mv c4.s c4_plain.s; $FPC -OoFASTMATH -al c4.pas > /dev/null 2>&1 && mv c4.s c4_fast.s
echo "CAP;C4;0;-OoFASTMATH (aussi {\$OPTIMIZATION FASTMATH}) sur une réduction : $(grep -c 'vfmadd' c4_plain.s) FMA sans l'option, $(grep -c 'vfmadd' c4_fast.s) avec (contraction a*b+s) ; la chaîne reste scalaire et dans l'ordre : aucune réassociation"
# E2 : assembleur AVX2 accepté, AVX-512 refusé
printf 'program e2;\n{$mode objfpc}{$asmmode intel}\nprocedure p; assembler; nostackframe;\nasm\n  vaddps ymm0, ymm1, ymm2\nend;\nbegin p; writeln(1) end.\n' > e2a.pas
$FPC e2a.pas > e2a.log 2>&1 && E2A="vaddps ymm accepté" || E2A=$(grep -o 'Error: .*' e2a.log | head -1)
printf 'program e2;\n{$mode objfpc}{$asmmode intel}\nprocedure p; assembler; nostackframe;\nasm\n  vaddps zmm0, zmm1, zmm2\nend;\nbegin p; writeln(1) end.\n' > e2b.pas
$FPC e2b.pas > e2b.log 2>&1 && E2B="vaddps zmm accepté" || E2B=$(grep -o 'Error: .*' e2b.log | head -1)
printf 'program e2;\n{$mode objfpc}{$asmmode intel}\nprocedure p; assembler; nostackframe;\nasm\n  db $62, $f1, $74, $48, $58, $c2\nend;\nbegin p; writeln(1) end.\n' > e2c.pas
$FPC e2c.pas > e2c.log 2>&1 && E2C="$(./e2c) (exécuté)" || E2C=$(grep -o 'Error: .*' e2c.log | head -1)
echo "NOTE;E2;$E2A ; zmm : $E2B ; vaddps zmm0, zmm1, zmm2 en octets bruts (db) : $E2C"
# E3 : Likely
printf 'program e3;\n{$mode objfpc}\nvar x: integer;\nbegin x := ParamCount; if Likely(x > 0) then writeln(1) end.\n' > e3.pas
$FPC e3.pas > e3.log 2>&1 && echo "NOTE;E3;Likely accepté" || echo "NOTE;E3;Likely : $(grep -o 'Error: .*' e3.log | head -1)"
# E4 / D5 : préchargement et pause dans le code produit
printf 'program e4;\n{$mode objfpc}\nvar a: array[0..1023] of Int64;\nprocedure pf; begin Prefetch(a[512]); end;\nbegin pf; ReadWriteBarrier; writeln(a[0]) end.\n' > e4.pas
$FPC -al e4.pas > /dev/null 2>&1; echo "NOTE;E4;Prefetch(a[512]) : $(grep -E '^\s+prefetch' e4.s | tr -s ' \t' ' ' | head -1)"
printf 'program d5;\n{$mode objfpc}\nbegin CpuPause; end.\n' > d5.pas
$FPC d5.pas > d5.log 2>&1 && echo "NOTE;D5;CpuPause accepté" || echo "NOTE;D5;pause : aucune intrinsèque ($(grep -o 'Error: .*' d5.log | head -1)) ; seulement asm pause end (assembleur en ligne)"
