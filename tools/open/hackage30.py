#!/usr/bin/env python3
"""v4, point 6 (docs/V4_OPEN.md, 3.1 et écart 4) : contrôle du classement de Haskell par la statistique prévue au plan,
les téléchargements des 30 derniers jours, lus sur la page de chaque paquet de Hackage (« N in the last 30 days ») ;
le relevé (tools/open/registry.py) avait classé par la page « top » de Hackage. Écrit
results/open/registry/haskell_30d.json : pour chaque case, les candidates avec les deux statistiques et les deux rangs."""
import json
import os
import re
import time
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REG = os.path.join(ROOT, "results", "open", "registry", "haskell.json")
OUT = os.path.join(ROOT, "results", "open", "registry", "haskell_30d.json")


def downloads_30d(name):
    url = f"https://hackage.haskell.org/package/{name}"
    for k in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "open-track-survey"})
            t = urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace")
            m = re.search(r"([\d,]+)\s+in the last 30 days", t)
            tot = re.search(r"([\d,]+)\s+total", t)
            return (int(m.group(1).replace(",", "")) if m else None,
                    int(tot.group(1).replace(",", "")) if tot else None)
        except Exception as e:  # reprise
            err = e
            time.sleep(2 * (k + 1))
    raise RuntimeError(f"{name}: {err}")


def main():
    reg = json.load(open(REG, encoding="utf-8"))
    seen, out = {}, {"source": "pages des paquets de Hackage, « N in the last 30 days »",
                     "date": time.strftime("%Y-%m-%d %H:%M"), "cases": {}}
    for case, v in reg["cases"].items():
        rows = []
        for i, c in enumerate(v["candidates"]):
            n = c["name"]
            if n not in seen:
                seen[n] = downloads_30d(n)
                time.sleep(0.3)
            d30, tot = seen[n]
            rows.append({"name": n, "rang_top": i + 1, "stat_top": c.get("stat"), "30j": d30, "total": tot})
        order = sorted(rows, key=lambda r: (-(r["30j"] or -1), r["rang_top"]))
        for k, r in enumerate(order):
            r["rang_30j"] = k + 1
        out["cases"][case] = order
        print(case, [(r["name"], r["30j"]) for r in order[:10]])
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("écrit :", OUT)


if __name__ == "__main__":
    main()
