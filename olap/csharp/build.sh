#!/bin/sh
# v7 : le banc OLAP en C# (.NET 10), niveau portable (olap_p) et niveau spécialisé (olap_s : constante SPECIAL,
# intrinsèques AVX-512). olap_p et olap_s sont des lanceurs de l'assemblage de chaque niveau.
set -e
cd "$(dirname "$0")"
DOTNET=/opt/dotnet/dotnet
$DOTNET build -c Release -o bin/p --nologo -v q -p:IntermediateOutputPath=obj/p/ 2>&1 | grep -E "error|warn" | grep -v "0 Warn" | head -40 || true
$DOTNET build -c Release -o bin/s --nologo -v q -p:IntermediateOutputPath=obj/s/ -p:DefineConstants=SPECIAL 2>&1 |
  grep -E "error|warn" | grep -v "0 Warn" | head -40 || true
test -f bin/p/olap.dll && test -f bin/s/olap.dll
printf '#!/bin/sh\nexec %s %s/bin/p/olap.dll "$@"\n' "$DOTNET" "$PWD" > olap_p
printf '#!/bin/sh\nexec %s %s/bin/s/olap.dll "$@"\n' "$DOTNET" "$PWD" > olap_s
chmod +x olap_p olap_s
