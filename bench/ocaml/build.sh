#!/bin/sh
# OCaml 5.5.2 + flambda (-O3) ; bibliothèques unix et bigarray de la distribution
set -e
cd "$(dirname "$0")"
/opt/ocaml/bin/ocamlfind ocamlopt -version >/dev/null 2>&1 || true
/opt/ocaml/bin/ocamlopt -O3 -I +unix unix.cmxa ms.ml -o ms
