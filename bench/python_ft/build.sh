#!/bin/sh
# CPython 3.15.2 free-threaded (python3.15t, sans GIL) — même source que bench/python
python3.15t -m py_compile "$(dirname "$0")/../python/ms.py"
