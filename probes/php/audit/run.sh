#!/bin/sh
# Audit de la grille, PHP 8.5 (réglages du banc : OPcache, JIT tracing) : compléments exécutés (audit.php), formes
# canoniques refusées, et recherches d'absence dans l'API publique introspectée (fonctions, classes et méthodes,
# constantes, directives ini et extensions de la construction : tools/grid_audit/listings/php_api.php).
# Imprime des lignes FACT et SEARCHTXT, reprises par probes/php/run.sh.
cd "$(dirname "$0")/../../.." && mkdir -p probes/php/audit/bin
B=probes/php/audit/bin
PHP="/opt/php85/bin/php -d memory_limit=-1 -d opcache.enable_cli=1 -d opcache.jit=tracing -d opcache.file_update_protection=0"
V="PHP $(/opt/php85/bin/php -r 'echo PHP_VERSION;')"
$PHP probes/php/audit/audit.php
# formes canoniques : assembleur en ligne, générique, appel de fonction dans une expression constante
err() { $PHP "$1" 2>&1 | grep -m1 -E 'error' | sed -e 's/^PHP //' -e 's/  */ /g' -e 's/ in [^ ]*\.php.*$//'; }
printf '<?php\nasm("pause");\n' > $B/e2.php
printf '<?php\nfunction id<T>(T $x): T { return $x; }\n' > $B/e7a.php
printf '<?php\nconst N = strlen("abc");\necho N;\n' > $B/e7b.php
echo "FACT;E2;asm(\"pause\") : $(err $B/e2.php)"
echo "FACT;E7;function id<T>(T \$x): T : $(err $B/e7a.php) ; const N = strlen(\"abc\") : $(err $B/e7b.php)"
N=$($PHP tools/grid_audit/listings/php_api.php | wc -l)
S=$(python3 tools/grid_audit/search.py php A6 B2 B3 C1 C2 C4 C5 D2 D3 D5 E2 E3 E4 E5 E7 F2 F4)
# noms trouvés (déclarations publiques), pour l'examen
names() { sed -n '/^## Déclarations publiques/,/^## Mentions/p' "results/grid_audit/search/php_$1.txt" \
  | grep '^<introspection>' | awk '{print $2" "$3}' | paste -sd, - | sed 's/,/, /g'; }
seen() { case "$1" in
  A6) echo " : $(names A6) (type d'enregistrement DNS), faux positif" ;;
  D2) echo " : $(names D2) (version ; sémaphores System V, des verrous), faux positifs" ;;
  D3) echo " : $(names D3) (cache des chemins de fichiers), faux positifs" ;;
  E4) echo " : $(names E4) (lignes lues d'avance par un pilote de base de données), faux positifs" ;;
  E5) echo " : $(names E5) (constante de pathconf ; directive d'OPcache), faux positifs" ;;
  *) [ -n "$(names "$1")" ] && echo " : $(names "$1") (non examinés)" ;;
esac; }
echo "$S" | while IFS=';' read k c pub men fil out; do
  [ "$pub" -gt 1 ] && s=s || s=
  echo "SEARCHTXT;$c;[recherche] motif $c dans l'API publique de $V ($N noms : fonctions, classes et méthodes, constantes, directives ini, extensions ; introspection) : $pub nom$s$(seen "$c") ($out)"
done
