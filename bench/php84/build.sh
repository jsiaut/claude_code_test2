#!/bin/sh
# Remarque sur PHP : PHP 8.4.27 (/opt/php84, tools/php_remark/build.sh) ; le banc publié, vérification syntaxique.
set -e
cd "$(dirname "$0")"
/opt/php84/bin/php -l ../php/ms.php > /dev/null
