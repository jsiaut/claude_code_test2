#!/bin/sh
# Première sonde de Lua (deux cas, reprise par audit/ : run.sh).
/opt/lua55/bin/lua "$(dirname "$0")/probe.lua"
