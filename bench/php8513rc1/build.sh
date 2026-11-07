#!/bin/sh
# Remarque sur PHP : PHP 8.5.13RC1 (/opt/php8513rc1, tools/php_remark/build.sh) ; le banc publié, vérification syntaxique.
set -e
cd "$(dirname "$0")"
/opt/php8513rc1/bin/php -l ../php/ms.php > /dev/null
