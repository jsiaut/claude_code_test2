#!/bin/sh
cd "$(dirname "$0")" && mkdir -p bin && /opt/ocaml/bin/ocamlfind ocamlopt -package unix -linkpkg probe.ml -o bin/probe 2>/dev/null || /opt/ocaml/bin/ocamlopt -I +unix unix.cmxa probe.ml -o bin/probe && bin/probe
