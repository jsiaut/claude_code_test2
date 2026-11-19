#!/bin/sh
# Noms publics des modules Swift livrés sans .swiftinterface (Foundation, FoundationEssentials, Dispatch), extraits par
# swift-symbolgraph-extract de la chaîne : un nom par ligne, « Module : chemin.du.symbole ». Sert à tools/grid_audit/search.py.
D=$(mktemp -d)
for m in Foundation FoundationEssentials Dispatch; do
  mkdir -p $D/$m && /opt/swift/usr/bin/swift-symbolgraph-extract -module-name $m -target x86_64-unknown-linux-gnu -output-dir $D/$m > /dev/null 2>&1
done
python3 - "$D" <<'PY'
import json, glob, os, sys
seen = set()
for f in sorted(glob.glob(os.path.join(sys.argv[1], "*", "*.symbols.json"))):
    d = json.load(open(f))
    mod = d["module"]["name"]
    for s in d.get("symbols", []):
        name = mod + " : " + ".".join(s.get("pathComponents", []))
        if name not in seen:
            seen.add(name); print(name)
PY
rm -rf "$D"
