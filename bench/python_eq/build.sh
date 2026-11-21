#!/bin/sh
# CPython 3.15.2 (deadsnakes, build par défaut avec GIL) : vérification syntaxique seulement
python3.15 -m py_compile "$(dirname "$0")/ms.py"
