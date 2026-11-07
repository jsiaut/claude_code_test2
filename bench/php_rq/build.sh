#!/bin/sh
# Copie de la remarque sur PHP : vérification syntaxique (même binaire que bench/php).
set -e
cd "$(dirname "$0")"
/opt/php85/bin/php -l ms.php > /dev/null
