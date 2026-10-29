#!/bin/sh
# Le JIT de .NET vectorise-t-il des boucles simples ? Son propre désassemblage, en optimisation complète.
cd "$(dirname "$0")" && /opt/dotnet/dotnet build -c Release --nologo -v q >/dev/null && \
DOTNET_TieredCompilation=0 DOTNET_JitDisasm="SumInt AddF CondSum" DOTNET_JitStdOutFile=disasm.txt \
  /opt/dotnet/dotnet bin/Release/net10.0/jitvec.dll >/dev/null && cat disasm.txt
