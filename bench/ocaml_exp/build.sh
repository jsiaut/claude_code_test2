#!/bin/sh
# OCaml 5.5.2 + flambda (-O3) ; bibliothèques unix, bigarray et runtime_events de la distribution (horloge monotone,
# remarque sur OCaml, docs/OCAML.md)
set -e
cd "$(dirname "$0")"
/opt/ocaml/bin/ocamlopt -O3 -I +unix -I +runtime_events unix.cmxa runtime_events.cmxa ms.ml -o ms
