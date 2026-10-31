#!/bin/sh
# Remarque sur C# (docs/CSHARP.md, section 2) : preuves des vérifications faites avant le plan.
# Écrit results/csharp_check/*.txt. Prérequis : /opt/dotnet (SDK 10.0.403), /opt/dotnet11 (SDK 11.0.100-rc.3),
# /opt/go127, un clone partiel de dotnet/runtime dans $RUNTIME (défaut /home/user/dotnet/runtime) avec les
# références pr127032 et pr127853 (git fetch origin refs/pull/<n>/head:pr<n>).
set -e
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
OUT=$ROOT/results/csharp_check
W=$ROOT/.work/cs/collect
RUNTIME=${RUNTIME:-/home/user/dotnet/runtime}
mkdir -p "$OUT" "$W"
export DOTNET_CLI_TELEMETRY_OPTOUT=1 DOTNET_NOLOGO=1 MS_DATA=/opt/msdata
DLL=$ROOT/bench/csharp/bin/rel/ms.dll
EXP=$ROOT/bench/csharp_exp/bin/rel/ms.dll

# 1. Versions installées
{ echo "== .NET 10"; /opt/dotnet/dotnet --list-sdks; /opt/dotnet/dotnet --list-runtimes
  echo "== .NET 11"; /opt/dotnet11/dotnet --list-sdks; /opt/dotnet11/dotnet --list-runtimes; } > "$OUT/versions.txt"

# 2. K4 : code de K4Branchless et K4Natural selon le protocole et la version
listing() { # $1 fichier JitStdOutFile, $2 méthode : extrait chaque listing de la méthode (en-tête + boucle)
  awk -v m="$2" '/^; Assembly listing for method/{p=index($0, m)>0} p' "$1"; }
{ for spec in "P0:3:1" "W120:120:1" "FullOpts:3:0"; do
    name=${spec%%:*}; rest=${spec#*:}; w=${rest%%:*}; tc=${rest#*:}
    echo "==== .NET 10, $name (WARMUP=$w, TieredCompilation=$tc), K4Branchless"
    WARMUP=$w DOTNET_TieredCompilation=$tc DOTNET_JitStdOutFile=$W/k4.txt DOTNET_JitDisasm=K4Branchless \
      /opt/dotnet/dotnet "$DLL" k4 branchless_unsorted 3 > /dev/null
    listing "$W/k4.txt" "K4Branchless"
  done
  echo "==== .NET 10, FullOpts, K4Natural"
  WARMUP=1 DOTNET_TieredCompilation=0 DOTNET_JitStdOutFile=$W/k4n.txt DOTNET_JitDisasm=K4Natural \
    /opt/dotnet/dotnet "$DLL" k4 natural_unsorted 1 > /dev/null
  listing "$W/k4n.txt" "K4Natural"
  for mv in K4Branchless:branchless_unsorted K4Natural:natural_unsorted; do
    m=${mv%%:*}; v=${mv#*:}
    echo "==== .NET 11 RC3, FullOpts, $m"
    rm -f "$W/k4_11.txt"
    WARMUP=1 DOTNET_TieredCompilation=0 DOTNET_ROLL_FORWARD=Major DOTNET_ROLL_FORWARD_TO_PRERELEASE=1 \
      DOTNET_JitStdOutFile=$W/k4_11.txt DOTNET_JitDisasm=$m /opt/dotnet11/dotnet "$DLL" k4 "$v" 1 > /dev/null
    listing "$W/k4_11.txt" "$m"
  done; } > "$OUT/k4_disasm.txt"

# 3. Niveaux de compilation des méthodes chaudes : protocole des données principales (3) et 120 échauffements
{ echo "==== WARMUP=3"; python3 "$ROOT/tools/csharp_check/tier_diag.py" 3 "$W"
  echo "==== WARMUP=120"; python3 "$ROOT/tools/csharp_check/tier_diag.py" 120 "$W"; } > "$OUT/tiers.txt"

# 4. Q1 tuned : forme en variables locales (csharp_exp) compilée par OSR (repli en MinOpts) et en FullOpts
{ echo "==== csharp_exp, protocole P0 : en-têtes des listings de Q1Tuned"
  WARMUP=3 DOTNET_JitStdOutFile=$W/q1.txt DOTNET_JitDisasm=Q1Tuned /opt/dotnet/dotnet "$EXP" k6 tuned 3 q1 > /dev/null
  grep -E "^; (Assembly listing|Tier|OSR|optimized|compiling with|Total bytes)" "$W/q1.txt"
  echo "==== csharp_exp, FullOpts"
  WARMUP=1 DOTNET_TieredCompilation=0 DOTNET_JitStdOutFile=$W/q1f.txt DOTNET_JitDisasm=Q1Tuned \
    /opt/dotnet/dotnet "$EXP" k6 tuned 1 q1 > /dev/null
  grep -E "^; (Assembly listing|Tier|optimized|compiling with|Total bytes)" "$W/q1f.txt"
  echo "==== binaire de la campagne, protocole P0 : niveau de Q1Tuned"
  WARMUP=3 DOTNET_JitStdOutFile=$W/q1c.txt DOTNET_JitDisasmSummary=1 /opt/dotnet/dotnet "$DLL" k6 tuned 3 q1 > /dev/null
  grep Q1Tuned "$W/q1c.txt"; } > "$OUT/q1_tiers.txt"

# 5. AVX-512 : réglage par défaut des Cascade Lake (largeur préférée 256 bits) simulé par DOTNET_PreferredVectorBitWidth
( cd "$ROOT/tools/csharp_check/avx512" && /opt/dotnet/dotnet build -c Release -o "$W/avx512" --nologo -v q > /dev/null )
{ for wv in "" 256; do
    echo "==== DOTNET_PreferredVectorBitWidth=${wv:-(défaut)}"
    env ${wv:+DOTNET_PreferredVectorBitWidth=$wv} /opt/dotnet/dotnet "$W/avx512/probe.dll"
    env ${wv:+DOTNET_PreferredVectorBitWidth=$wv} WARMUP=1 DOTNET_TieredCompilation=0 DOTNET_JitStdOutFile=$W/soa.txt \
      DOTNET_JitDisasm=K1SoA /opt/dotnet/dotnet "$DLL" k1 soa 1 > /dev/null
    echo "K1SoA : $(grep -c zmm "$W/soa.txt") lignes avec zmm ; $(grep -m1 vfmadd "$W/soa.txt" | sed 's/^ *//')"
  done
  echo "==== codeman.cpp (dotnet/runtime, $(git -C "$RUNTIME" rev-parse --short HEAD 2>/dev/null))"
  grep -n -A42 "Some architectures can experience frequency throttling" "$RUNTIME/src/coreclr/vm/codeman.cpp"; } > "$OUT/avx512.txt"

# 6. Unions de C# 15 (SDK .NET 11 RC3)
( cd "$ROOT/tools/csharp_check/union15" && /opt/dotnet11/dotnet build -c Release -o "$W/union15" --nologo -v q > /dev/null )
/opt/dotnet11/dotnet "$W/union15/u.dll" > "$OUT/union15.txt"

# 7. Génériques : C# (struct spécialisé, classe partagée) et Go (une copie par forme GC, appel par dictionnaire)
( cd "$ROOT/tools/csharp_check/generics_cs" && /opt/dotnet/dotnet build -c Release -o "$W/gen" --nologo -v q > /dev/null )
{ echo "==== C# : G.Apply<T> où T : IAdder (FullOpts)"
  DOTNET_TieredCompilation=0 DOTNET_JitStdOutFile=$W/apply.txt DOTNET_JitDisasm=Apply /opt/dotnet/dotnet "$W/gen/csgen.dll" > /dev/null
  grep -E "Assembly listing|^\s+(lea|call|mov|add|jmp)" "$W/apply.txt"
  echo "==== Go 1.27 : symboles et appels de main.Apply / main.Sum"
  cd "$ROOT/tools/csharp_check/generics_go" && GOFLAGS=-mod=mod /opt/go127/bin/go build -gcflags=-S -o /dev/null . 2>&1 \
    | grep -E "^main\.(Sum|Apply)\[[^ ]*\] STEXT|^main\.(Sum|Apply)\[go\.shape[^]]*\] STEXT|CALL\s+SI" ; } > "$OUT/generics.txt"

# 8. Sources du JIT (dotnet/runtime) : garde-fou de l'if-conversion, PR 127032, PR 127853, phases du JIT
{ echo "==== main : $(git -C "$RUNTIME" log -1 --format='%H %cd')"
  grep -n -B2 -A10 "Don't optimise the block if it is inside a loop" "$RUNTIME/src/coreclr/jit/ifconversion.cpp"
  echo "==== recherche d'un vectoriseur de boucles dans src/coreclr/jit (main) :"
  grep -rli "autovectoriz\|auto-vectoriz\|auto vectoriz" "$RUNTIME/src/coreclr/jit/" || echo "(aucun fichier)"
  echo "==== refs/pull/127032/head : propres commits de la PR"
  git -C "$RUNTIME" log --format='%h %ad %an : %s' --date=short pr127032 | head -3
  git -C "$RUNTIME" diff 337094ae 09c488b7 -- src/coreclr/jit/ifconversion.cpp | sed -n '1,60p'
  echo "==== refs/pull/127853/head : derniers commits"
  git -C "$RUNTIME" log --format='%h %ad %an : %s' --date=short pr127853 | head -6; } > "$OUT/jit_sources.txt"
echo "preuves écrites dans $OUT"
