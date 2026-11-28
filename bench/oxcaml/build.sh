#!/bin/sh
# OxCaml 5.4.0-ox7 (ocamlopt -O3, optimiseur flambda2) ; bibliothèques livrées avec le compilateur : unix,
# runtime_events, stdlib_stable, stdlib_upstream_compatible. Deux binaires (docs/V6_1.md, 3 et 4) :
# * ms, de ms.ml : la source d'OCaml, inchangée à l'octet près (son en-tête dit encore « OCaml 5.5.2 »). C'est elle
#   que le témoin de la mesure d'OxCaml compile par OCaml 5.5.2 ; le code naturel en vient ;
# * ms_ox, de ox.ml : les formes propres à OxCaml (types non boxés, vecteurs, préchargement, région locale).
# run aiguille chaque variante vers son binaire.
set -e
cd "$(dirname "$0")"
# MS_MODE=unc : mode R1', sans vérifications (-unsafe) ; sans MS_MODE, la commande publiée.
case "${MS_MODE:-}" in
  "") MODE="" ;;
  unc) MODE=-unsafe ;;
  *) echo "MS_MODE=$MS_MODE : mode inconnu pour ce langage" >&2; exit 2 ;;
esac
O=/opt/oxcaml/bin/ocamlopt
# Tailles de la construction : les noms MS_* des sources sont remplacés à la compilation (préprocesseur -pp, qui
# garde les lignes) par les valeurs des variables MS_* ; sans elles, par le texte publié (« 1 lsl 22 »…).
v() { if [ -n "$1" ]; then echo "$1"; else echo "$2"; fi; }
K7LOG=$(v "${MS_K7_LOG2:+$((MS_K7_LOG2 + 1))}" 21)
K8NODES=$(v "${MS_K8_REQ:+$(((2 << MS_K8_REQ) - 1))}" 2047)
cat > sizes.sed <<EOT
# Écrit par build.sh (v4, point 2 : docs/V4_SIZES.md) : tailles de la construction ; sans variable MS_*, le texte
# publié.
s/\\bMS_N1\\b/$(v "$MS_N1" "1 lsl 22")/g
s/\\bMS_INNER5\\b/$(v "$MS_INNER5" "1 lsl 16")/g
s/\\bMS_N6\\b/$(v "$MS_N6" "1 lsl 24")/g
s/\\bMS_K7_LOG\\b/$K7LOG/g
s/\\bMS_K8_NODES\\b/$K8NODES/g
s/\\bMS_K8_LONG\\b/$(v "$MS_K8_LONG" 20)/g
s/\\bMS_K8_REQ\\b/$(v "$MS_K8_REQ" 10)/g
s/\\bMS_M9\\b/$(v "$MS_M9" 2048)/g
EOT
# OxCaml signale Domain.spawn par deux alertes (il conseille son module Multicore) : les variantes à quatre fils
# l'emploient comme sous OCaml ; les alertes sont tues, sans effet sur le code produit.
QUIET="-alert -do_not_spawn_domains-unsafe_multidomain"
$O -O3 $MODE $QUIET -pp "sed -f sizes.sed" -I +unix -I +runtime_events unix.cmxa runtime_events.cmxa ms.ml -o ms
# Primitives de ox.ml : le compilateur remplace chaque appel par des instructions ([@@builtin]) et aucune n'est jamais
# appelée, mais l'éditeur de liens demande leurs symboles ; --defsym les lui donne, sans code C.
DEFS=$(grep -o '"caml_[a-z0-9_]*"' ox.ml | tr -d '"' | grep -v unreachable | sort -u |
  sed 's/^/-ccopt -Wl,--defsym,/; s/$/=0/' | tr '\n' ' ')
$O -O3 $MODE $QUIET -pp "sed -f sizes.sed" -I +unix -I +runtime_events -I +stdlib_stable \
  -I +stdlib_upstream_compatible unix.cmxa runtime_events.cmxa stdlib_stable.cmxa stdlib_upstream_compatible.cmxa \
  $DEFS ox.ml -o ms_ox
