#!/bin/sh
cd "$(dirname "$0")" && /opt/dotnet/dotnet run -c Release --nologo -v q
