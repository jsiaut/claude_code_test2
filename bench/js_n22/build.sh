#!/bin/sh
# Node.js 22.22.0 (V8 12.4) : rien à compiler
/opt/node22/bin/node --check "$(dirname "$0")/../js_ref/ms.js"
