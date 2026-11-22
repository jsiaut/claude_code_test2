#!/bin/sh
# CPython 3.15.2 de /opt/open/python (piste ouverte, docs/V4_OPEN.md) : vérification syntaxique seulement
/opt/open/python/bin/python -m py_compile "$(dirname "$0")/ms.py"
