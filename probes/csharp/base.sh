#!/bin/sh
# Première sonde de C# (quatre cas, reprise par audit/ : run.sh).
cd "$(dirname "$0")" && /opt/dotnet/dotnet run -c Release --nologo -v q
