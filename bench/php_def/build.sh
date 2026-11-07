#!/bin/sh
# même source que bench/php (vérification syntaxique : bench/php/build.sh)
set -e
exec "$(dirname "$0")/../php/build.sh"
