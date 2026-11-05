#!/bin/sh
# Faits de l'ajout de Swift (docs/SWIFT.md, section 2) : chaîne, mode release de SwiftPM, génération de code.
# Sortie : results/swift_check/facts.txt
cd "$(dirname "$0")"
OUT=../../results/swift_check/facts.txt
W=$(mktemp -d)
SC=/opt/swift/usr/bin/swiftc
{
echo "== chaîne"
$SC --version 2>&1 | head -1
/opt/swift/usr/bin/clang --version | head -1
echo "archive : $(sha256sum /opt/dl/swift/swift-6.4.2-RELEASE-ubuntu24.04.tar.gz | cut -c1-64) $(stat -c %s /opt/dl/swift/swift-6.4.2-RELEASE-ubuntu24.04.tar.gz) octets"
python3 -c "import json; r=[x for x in json.load(open('/opt/dl/swift/releases.json')) if x.get('name') in ('6.4.1','6.4.2')]; print('releases.json (swift.org) :', [(x['name'], x['date']) for x in r])"
echo "== mode release de SwiftPM (paquet créé par swift package init)"
mkdir -p $W/pkg && cd $W/pkg && PATH=/opt/swift/usr/bin:$PATH swift package init --type executable --name Hello > /dev/null 2>&1
head -1 Package.swift
PATH=/opt/swift/usr/bin:$PATH swift build -c release -v 2>&1 | grep -o -E "(-O|-whole-module-optimization|-swift-version [0-9]+|-enforce-exclusivity=[a-z]+) " | sort | uniq -c
cd - > /dev/null
echo "== génération de code (-O -target-cpu native)"
$SC -swift-version 6 -O -target-cpu native -parse-as-library -module-name codegen -emit-assembly -o $W/cg.s codegen.swift
for f in convLib convLanes cmpScalar cmpVector sumLib sumTree k4; do
  body=$(awk "/^\\\$s7codegen[0-9]*${f}/,/\\.Lfunc_end/" $W/cg.s)
  echo "$f : $(echo "$body" | grep -c -E '^\s+[a-z]') instructions, appels $(echo "$body" | grep -c -E 'call|jmp\s+\(')," \
       "branchements $(echo "$body" | grep -c -E '^\s+j(e|ne|ns|ae|b|l|g|a)\s')," \
       "$(echo "$body" | grep -o -E 'vpmovzxbd|vpcmpeqd|vpcmpneqd|vaddss|vaddps|ud2' | sort | uniq -c | tr '\n' ' ')"
done
} > $OUT 2>&1
rm -rf $W
cat $OUT
