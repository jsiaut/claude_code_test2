#!/bin/bash
# Remarque sur Swift (docs/SWIFT.md, section 5) : vérification des faits sur la chaîne installée (Swift 6.4.2), sans
# page web. Sortie : results/swift_check/facts2.txt. Le test de l'arbre UniqueBox sans deinit plafonne la mémoire.
cd "$(dirname "$0")" && R=$(cd ../.. && pwd) && W=$(mktemp -d) && cp src/*.swift "$W"/ && cd "$W"
SC=/opt/swift/usr/bin/swiftc
echo "# Faits de la remarque sur Swift ($(date '+%F %T'), $(grep -m1 'model name' /proc/cpuinfo | cut -d: -f2 | xargs), modèle $(grep -m1 '^model\s' /proc/cpuinfo | cut -d: -f2 | xargs))"
echo "## D4 : affinité par le module Glibc"
echo "sans option : $($SC -O -parse-as-library -o aff_plain aff.swift 2>&1 | grep -o "cannot find '[a-z_]*' in scope" | sort -u | tr '\n' ';')"
$SC -O -parse-as-library -Xcc -D_GNU_SOURCE -o aff aff.swift && echo "avec -Xcc -D_GNU_SOURCE : $(./aff | tr '\n' ' ')"
echo "swiftc --help : $($SC --help | grep -E '^  -Xcc ' | xargs)"
echo "## E4 et D5 : préchargement et pause"
echo "prfchwintrin.h livré : $(grep -h -E '^void _m_prefetchw?\(' /opt/swift/usr/lib/clang/*/include/prfchwintrin.h | tr '\n' ' ')(déclarations sans corps)"
$SC -Onone -parse-as-library -module-name pf -emit-silgen pf.swift -o pf.silgen
echo "import en SIL : $(grep -o -E '^sil \[readnone\] \[asmname "_m_prefetchw?"\]' pf.silgen | tr '\n' ' ')"
$SC -O -parse-as-library -module-name pf -emit-sil pf.swift -o pf.sil
$SC -O -target-cpu native -parse-as-library -module-name pf -emit-assembly pf.swift -o pf.s
echo "appels restant dans le SIL -O : $(grep -c '_m_prefetch' pf.sil) ; instructions prefetch dans le code : $(grep -c prefetch pf.s)"
$SC -O -target-cpu native -parse-as-library -module-name pf2 -emit-assembly pf2.swift -o pf2.s
echo "@_silgen_name(\"llvm.prefetch.p0\") : $(grep -c prefetchw pf2.s) prefetchw ; @_silgen_name(\"llvm.x86.sse2.pause\") : $(grep -c -w pause pf2.s) pause"
echo "@_silgen_name dans les interfaces livrées : $(grep -c '@_silgen_name' /opt/swift/usr/lib/swift/linux/Swift.swiftmodule/x86_64-unknown-linux-gnu.swiftinterface) fois (Swift), dont vers une intrinsèque LLVM : $(grep -c '@_silgen_name("llvm\.' /opt/swift/usr/lib/swift/linux/Swift.swiftmodule/x86_64-unknown-linux-gnu.swiftinterface)"
echo "## E5 : noalias dans l'IR"
$SC -O -parse-as-library -module-name na -emit-ir na.swift -o na.ll
grep -E "^define .*(inoutInt|inoutArr|inoutBig|inoutPtr|rawPtrs)" na.ll | sed -E 's/^define protected swiftcc void @"\$s2na[0-9]+([a-zA-Z]+)[^"]*"/\1/; s/ #[0-9]+ \{$//; s/captures\(none\) //g'
echo "## E7 : spécialisation et calcul à la compilation"
$SC -O -parse-as-library -module-name spec -emit-sil spec.swift -o spec.sil && echo "@specialized(where T == Int/Double) et @inline(always) sans option : $(grep -c -E '^sil .*sum' spec.sil) fonctions sum dans le SIL, dont $(grep -c -E '^// specialized sum' spec.sil) spécialisées"
echo "@const sans option : $($SC -O -parse-as-library -module-name cst -emit-sil cst.swift -o /dev/null 2>&1 | grep -m1 -o "'const' attribute is only valid when experimental feature [A-Za-z]* is enabled")"
echo "## Types de la 6.4 dans Swift.swiftinterface"
for t in "struct UniqueBox" "struct UniqueArray" "struct Ref<" "struct MutableRef" "protocol Iterable"; do echo "$t : $(grep -c "public $t" /opt/swift/usr/lib/swift/linux/Swift.swiftmodule/x86_64-unknown-linux-gnu.swiftinterface)"; done
echo "## Alignement"
$SC -O al.swift -o al && echo "MemoryLayout alignment SIMD16<Float>, SIMD8<Double>, SIMD64<UInt8> ; taille SIMD16<Float> : $(./al)"
echo "@_alignment(64) : $(printf '@_alignment(64) struct Al { var v: Int32 = 0 }\nprint(MemoryLayout<Al>.alignment)\n' > a64.swift; $SC a64.swift -o a64 2>&1 | grep -m1 -o "'@_alignment' cannot increase alignment above maximum alignment of [0-9]*")"
echo "## K4 naturel : += vérifié contre &+= (cible cascadelake)"
for mode in -O -Ounchecked; do $SC $mode -target-cpu cascadelake -parse-as-library -module-name k4 -emit-assembly k4.swift -o k4$mode.s; done
python3 - <<'PY'
import re
for mode in ("-O", "-Ounchecked"):
    lines = open(f"k4{mode}.s").read().split("\n")
    labels = [(i, l) for i, l in enumerate(lines) if re.match(r"^\$s.*:", l)]
    for f in ("Checked", "Wrapping"):
        start = next(i for i, l in labels if f in l)
        end = next(i for i in range(start, len(lines)) if "End function" in lines[i])
        body = [l for l in lines[start:end] if l.startswith("\t") and not l.startswith("\t.")]
        c = lambda p: sum(1 for l in body if re.search(p, l))
        print(f"{mode} k4{f} : {len(body)} instructions, {c(r'%[yz]mm')} vectorielles (vpaddq {c('vpaddq')}), cmov {c('cmov')}, ud2 {c('ud2')}")
PY
echo "## K8 : comptage de références dans le binaire mesuré (bench/swift_exp/ms)"
for s in '$s2ms4tSumys5Int64VAA4NodeCSgF' '$s2ms4fSumys5Int64VAA5FNodeCSgF'; do b=$(objdump -d --no-show-raw-insn "$R/bench/swift_exp/ms" --disassemble="$s"); echo "$s : retain $(echo "$b" | grep -c swift_retain), release $(echo "$b" | grep -c swift_release)"; done
echo "swift_beginAccess importé par bench/swift/ms : $(nm -D "$R/bench/swift/ms" | grep -c beginAccess)"
echo "## K5 naturel : FMA scalaire (binaires publiés)"
echo "C k5_natural : $(objdump -d --no-show-raw-insn "$R/bench/c/ms" --disassemble=k5_natural | grep -c vfmadd) vfmadd ; Swift k5Natural : $(objdump -d --no-show-raw-insn "$R/bench/swift/ms" --disassemble='$s2ms9k5NaturalySfSaySfG_ACtF' | grep -c vfmadd) vfmadd, $(objdump -d --no-show-raw-insn "$R/bench/swift/ms" --disassemble='$s2ms9k5NaturalySfSaySfG_ACtF' | grep -c vaddss) vaddss"
echo "## Arbre UniqueBox (K8) : avec et sans deinit {} vide (mémoire plafonnée à 6 Go)"
sed 's/DEINIT/deinit {}/' ub.swift > ub_d.swift; sed 's/DEINIT//' ub.swift > ub_p.swift
t0=$(date +%s.%N); $SC -O -target-cpu native -parse-as-library -module-name ub ub_d.swift -o ub_d > ub_d.log 2>&1; t1=$(date +%s.%N)
echo "avec deinit {} : retour $? ; $(python3 -c "print(round($t1-$t0,1))") s ; exécution : $(./ub_d)"
t0=$(date +%s.%N); (ulimit -v 6000000; $SC -O -target-cpu native -parse-as-library -module-name ub ub_p.swift -o ub_p > ub_p.log 2>&1); rc=$?; t1=$(date +%s.%N)
echo "sans deinit : retour $rc ; $(python3 -c "print(round($t1-$t0,1))") s ; $(grep -m1 -o 'LLVM ERROR: out of memory' ub_p.log) ; $(grep -m1 -o 'While running pass #[0-9]* SILFunctionTransform "[A-Za-z]*"' ub_p.log)"
echo "## Provenance des binaires (machine 24)"
echo "bench/c/ms (publié, Cascade Lake) $(sha256sum "$R/bench/c/ms" | cut -c1-16) ; bench/c_er/ms (natif ici) $(sha256sum "$R/bench/c_er/ms" | cut -c1-16) ; machine 3 : $(grep -o 'ca4eeb97[0-9a-f]\{8\}' "$R/results/hw/machine3/binaries.txt" | head -1)"
rm -rf "$W"
