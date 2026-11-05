#!/bin/sh
# Sonde Swift : probe.swift (cas positifs, exécutés) + cas négatifs vérifiés sur le code produit.
cd "$(dirname "$0")" && mkdir -p bin
SC=/opt/swift/usr/bin/swiftc
$SC -swift-version 6 -O -target-cpu native -parse-as-library -o bin/probe probe.swift && bin/probe
$SC -swift-version 6 -O -target-cpu native -parse-as-library -emit-assembly -o bin/neg.s neg.swift
$SC -swift-version 6 -O -target-cpu native -parse-as-library -emit-ir -o bin/neg.ll neg.swift
echo "CAP;C2;0.5;import _Builtin_intrinsics.intel (module Clang non documenté) : $(grep -c vaddps bin/neg.s) vaddps pour _mm512_add_ps ; fonctions intégrées sans corps inutilisables (pause, préchargement) ; macros à immédiat refusées"
if $SC -O -o bin/pause pause.swift > bin/pause.log 2>&1; then echo "CAP;D5;1;_mm_pause liée"; else echo "NOTE;D5;_mm_pause importée mais non liée : $(grep -o "undefined reference to [^ ]*" bin/pause.log | head -1)"; fi
printf 'import Glibc\nvar s = cpu_set_t()\nprint(sched_setaffinity(0, MemoryLayout<cpu_set_t>.size, &s))\n' > bin/aff.swift
if $SC -o bin/aff bin/aff.swift > bin/aff.log 2>&1; then echo "NOTE;D4;sched_setaffinity disponible"; else echo "NOTE;D4;$(grep -o "cannot find 'sched_setaffinity' in scope" bin/aff.log | head -1) (module Glibc)"; fi
echo "CAP;E3;0.5;_slowPath/_fastPath (publics mais soulignés) : poids de branchement dans l'IR = $(grep -c branch_weights bin/neg.ll)"
echo "CAP;E4;0;_m_prefetchw importée mais supprimée : $(grep -c prefetch bin/neg.s) instruction de préchargement dans le code produit ; _mm_prefetch est une macro refusée"
echo "CAP;E5;0.5;exclusivité des inout (règle du langage, exploitée par l'optimiseur SIL) ; IR de two(_:_:) sans noalias : $(grep -E '^define.*3two' bin/neg.ll | grep -c noalias) ; pas de restrict pour les pointeurs"
if $SC -o bin/align align.swift > bin/align.log 2>&1; then echo "NOTE;A4;@_alignment(64) accepté : $(bin/align)"; else echo "NOTE;A4;$(grep -o "'@_alignment' cannot increase alignment above maximum alignment of [0-9]*" bin/align.log | head -1)"; fi
