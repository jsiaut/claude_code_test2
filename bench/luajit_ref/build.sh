#!/bin/sh
# LuaJIT 2.1 (branche v2.1, compilé depuis les sources officielles) : compilation en bytecode pour vérifier la syntaxe
/opt/luajit/bin/luajit -b "$(dirname "$0")/ms.lua" /dev/null
