#!/usr/bin/env python3
"""Noms de l'interface publique des unités livrées avec FreePascal 3.2.2 (RTL et paquets rtl-* et fcl-*), extraits par
ppudump -Fj -VA (interface entière) : un nom par ligne, « Unité.nom ». Sert à tools/grid_audit/search.py (introspection)."""
import glob, json, os, subprocess
U = "/opt/fpc/lib/fpc/3.2.2/units/x86_64-linux"
seen = set()
for d in sorted(glob.glob(os.path.join(U, "rtl*")) + glob.glob(os.path.join(U, "fcl-*"))):
    for ppu in sorted(glob.glob(os.path.join(d, "*.ppu"))):
        out = subprocess.run(["/opt/fpc/bin/ppudump", "-Fj", "-VA", ppu], capture_output=True, text=True).stdout
        try:
            js = json.loads(out)
        except Exception:
            continue
        units = js if isinstance(js, list) else [js]
        for u in units:
            name = u.get("Name", os.path.basename(ppu)[:-4])
            def walk(o):
                if isinstance(o, dict):
                    if "Name" in o and o.get("Type") not in (None, "unit"):
                        s = f"{name}.{o['Name']} ({o.get('Type', '')})"
                        if s not in seen:
                            seen.add(s); print(s)
                    for v in o.values(): walk(v)
                elif isinstance(o, list):
                    for v in o: walk(v)
            walk(u.get("Interface", u))
