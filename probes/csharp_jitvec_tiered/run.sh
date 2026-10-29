#!/bin/sh
# Code machine de chaque niveau du JIT de .NET, compilation par niveaux et PGO dynamique actives (réglages par défaut).
cd "$(dirname "$0")" && /opt/dotnet/dotnet build -c Release --nologo -v q >/dev/null && \
DOTNET_JitDisasm="SumInt AddF CondSum" DOTNET_JitStdOutFile=disasm.txt \
  /opt/dotnet/dotnet bin/Release/net10.0/jitvec.dll >/dev/null && cat disasm.txt
