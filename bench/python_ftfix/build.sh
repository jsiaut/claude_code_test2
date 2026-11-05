#!/bin/sh
# CPython 3.15.2 sans GIL : vérification syntaxique seulement
python3.15t -m py_compile "$(dirname "$0")/ms.py"
