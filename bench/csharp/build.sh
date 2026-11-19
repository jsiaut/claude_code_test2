#!/bin/sh
# .NET SDK 10.0.403 / runtime 10.0.14 (RyuJIT, PGO dynamique)
set -e
cd "$(dirname "$0")"
export DOTNET_CLI_TELEMETRY_OPTOUT=1 DOTNET_NOLOGO=1
# Tailles de la construction (v4, point 2 : docs/V4_SIZES.md) : variables MS_*, valeurs publiées par défaut
cat > Sizes.cs <<EOF
// Écrit par build.sh (v4, point 2 : docs/V4_SIZES.md) : tailles de la construction ; sans variable MS_*, les valeurs
// publiées.
static class Sizes
{
    public const int N1 = ${MS_N1:-4194304}, INNER5 = ${MS_INNER5:-65536}, N6 = ${MS_N6:-16777216};
    public const int K7_LOG2 = ${MS_K7_LOG2:-20}, K8_LONG = ${MS_K8_LONG:-20}, K8_REQ = ${MS_K8_REQ:-10}, M9 = ${MS_M9:-2048};
}
EOF
/opt/dotnet/dotnet build -c Release -o bin/rel --nologo -v q 2>&1 | grep -E "error|Warn|warn" | grep -v "0 Warn" | head -20 || true
