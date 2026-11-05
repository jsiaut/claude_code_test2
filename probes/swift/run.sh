#!/bin/sh
# Sonde Swift : probe.swift (cas positifs, exécutés) + cas négatifs vérifiés sur le code produit.
cd "$(dirname "$0")" && mkdir -p bin
SC=/opt/swift/usr/bin/swiftc
$SC -swift-version 6 -O -target-cpu native -parse-as-library -o bin/probe probe.swift && bin/probe
$SC -swift-version 6 -O -target-cpu native -parse-as-library -emit-assembly -o bin/neg.s neg.swift
$SC -swift-version 6 -O -target-cpu native -parse-as-library -emit-ir -o bin/neg.ll neg.swift
echo "CAP;C2;0.5;import _Builtin_intrinsics.intel (module Clang non documenté) : $(grep -c vaddps bin/neg.s) vaddps pour _mm512_add_ps ; fonctions intégrées sans corps inutilisables (pause, préchargement) ; macros à immédiat refusées"
if $SC -O -o bin/pause pause.swift > bin/pause.log 2>&1; then echo "CAP;D5;1;_mm_pause liée"; else echo "NOTE;D5;_mm_pause importée mais non liée : $(grep -o "undefined reference to [^ ]*" bin/pause.log | head -1)"; fi
# D4 (erratum du 5/11, remarque sur Swift) : sched_setaffinity est derrière _GNU_SOURCE dans le module Glibc, comme en C
printf 'import Glibc\nvar s = cpu_set_t()\nwithUnsafeMutableBytes(of: &s) { b in for i in 0..<b.count { b[i] = 0 }; b[0] = 2 }\nlet r = sched_setaffinity(0, MemoryLayout<cpu_set_t>.size, &s)\nprint(r, sched_getcpu())\n' > bin/aff.swift
$SC -o bin/aff_plain bin/aff.swift > bin/aff_plain.log 2>&1
if $SC -Xcc -D_GNU_SOURCE -o bin/aff bin/aff.swift > bin/aff.log 2>&1 && [ "$(bin/aff)" = "0 1" ]; then echo "CAP;D4;0.5;sched_setaffinity du module Glibc livré avec swiftc -Xcc -D_GNU_SOURCE : fil épinglé sur le CPU 1, sched_getcpu() = 1 (sans l'option : $(grep -o "cannot find 'sched_setaffinity' in scope" bin/aff_plain.log | head -1))"; else echo "CAP;D4;0;sched_setaffinity introuvable ou sans effet"; fi
echo "CAP;E3;0.5;_slowPath/_fastPath (publics mais soulignés) : poids de branchement dans l'IR = $(grep -c branch_weights bin/neg.ll)"
# E4 (erratum du 5/11, remarque sur Swift) : l'intrinsèque de LLVM par l'attribut souligné @_silgen_name
printf '@_silgen_name("llvm.prefetch.p0")\nfunc pf(_ p: UnsafeRawPointer, _ rw: Int32, _ loc: Int32, _ c: Int32)\n@_silgen_name("llvm.x86.sse2.pause")\nfunc relax()\n@inline(never) public func touch(_ p: UnsafeMutablePointer<UInt64>, _ n: Int) -> UInt64 { var s: UInt64 = 0; for i in 0..<n { pf(UnsafeRawPointer(p + i + 64), 1, 3, 1); s &+= p[i] }; return s }\n@inline(never) public func spin(_ f: UnsafeMutablePointer<Int>) { while f.pointee == 0 { relax() } }\n' > bin/silgen.swift
$SC -O -target-cpu native -parse-as-library -module-name silgen -emit-assembly -o bin/silgen.s bin/silgen.swift
echo "CAP;E4;0.5;@_silgen_name(\"llvm.prefetch.p0\"), attribut souligné : $(grep -c prefetchw bin/silgen.s) prefetchw dans le code produit ; _m_prefetchw importée [readnone] et supprimée ($(grep -c prefetch bin/neg.s) instruction) ; _mm_prefetch est une macro refusée"
echo "NOTE;D5;@_silgen_name(\"llvm.x86.sse2.pause\") : $(grep -c -w pause bin/silgen.s) pause dans le code produit (attribut souligné)"
echo "CAP;E5;0.5;exclusivité des inout (règle du langage, exploitée par l'optimiseur SIL) ; IR de two(_:_:) sans noalias : $(grep -E '^define.*3two' bin/neg.ll | grep -c noalias) ; pas de restrict pour les pointeurs"
if $SC -o bin/align align.swift > bin/align.log 2>&1; then echo "NOTE;A4;@_alignment(64) accepté : $(bin/align)"; else echo "NOTE;A4;$(grep -o "'@_alignment' cannot increase alignment above maximum alignment of [0-9]*" bin/align.log | head -1)"; fi
