#!/bin/sh
# Lua 5.5.1 (PUC-Rio, compilé avec gcc -O2 comme le Makefile officiel) : vérification syntaxique
/opt/lua55/bin/luac -p "$(dirname "$0")/ms.lua"
