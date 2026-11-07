#!/bin/sh
# Remarque sur PHP : PHP 8.3.36 (/opt/php83, tools/php_remark/build.sh) ; le banc publié, vérification syntaxique.
set -e
cd "$(dirname "$0")"
/opt/php83/bin/php -l ../php/ms.php > /dev/null
