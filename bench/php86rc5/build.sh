#!/bin/sh
# Remarque sur PHP : PHP 8.6.0RC5 (/opt/php86rc5, tools/php_remark/build.sh) ; le banc publié, vérification syntaxique.
set -e
cd "$(dirname "$0")"
/opt/php86rc5/bin/php -l ../php/ms.php > /dev/null
