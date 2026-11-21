#!/bin/sh
# OCaml 5.5.2 + flambda (-O3) ; bibliothèques unix et bigarray de la distribution
set -e
cd "$(dirname "$0")"
# v4, point 3 (docs/V4_EQUAL.md, 3.1). MS_MODE=unc : mode R1', sans vérifications (-unsafe) ; sans MS_MODE, la
# commande publiée.
case "${MS_MODE:-}" in
  "") MODE="" ;;
  unc) MODE=-unsafe ;;
  *) echo "MS_MODE=$MS_MODE : mode inconnu pour ce langage" >&2; exit 2 ;;
esac
/opt/ocaml/bin/ocamlfind ocamlopt -version >/dev/null 2>&1 || true
# Tailles de la construction (v4, point 2 : docs/V4_SIZES.md) : les noms MS_* du source sont remplacés à la
# compilation (préprocesseur -pp, qui garde les lignes) par les valeurs des variables MS_* ; sans elles, par le texte
# publié lui-même (« 1 lsl 22 »…), pour que le binaire publié ne change pas (les noms de symboles d'OCaml numérotent
# les expressions).
v() { if [ -n "$1" ]; then echo "$1"; else echo "$2"; fi; }
K7LOG=$(v "${MS_K7_LOG2:+$((MS_K7_LOG2 + 1))}" 21)
K8NODES=$(v "${MS_K8_REQ:+$(((2 << MS_K8_REQ) - 1))}" 2047)
cat > sizes.sed <<EOF
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
EOF
/opt/ocaml/bin/ocamlopt -O3 $MODE -pp "sed -f sizes.sed" -I +unix unix.cmxa ms.ml -o ms
