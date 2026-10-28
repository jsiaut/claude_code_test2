#!/bin/sh
# .NET SDK 10.0.403 / runtime 10.0.14 (RyuJIT, PGO dynamique)
set -e
cd "$(dirname "$0")"
export DOTNET_CLI_TELEMETRY_OPTOUT=1 DOTNET_NOLOGO=1
/opt/dotnet/dotnet build -c Release -o bin/rel --nologo -v q 2>&1 | grep -E "error|Warn|warn" | grep -v "0 Warn" | head -20 || true
