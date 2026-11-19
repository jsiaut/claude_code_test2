#!/usr/bin/env python3
"""v4, point 2 : remet en file des cellules écartées à tort par l'outil de campagne (docs/V4_SIZES.md, 7.1).

Déplace leurs enregistrements de results/sizes/work/raw vers results/sizes/discarded (gardés tels quels, avec le
motif et la date) et retire leur étalonnage de results/sizes/work/calib.json (gardé dans le même fichier), pour que
tools/sizes/campaign.py les mesure de nouveau, étalonnage compris, à toutes les passes. Refuse de tourner pendant que
le pilote tourne (il écrit dans les mêmes fichiers).

Usage : requeue.py LANGAGE CONSTRUCTION NOYAU TAILLE VARIANTE PARAM[,PARAM...] MOTIF
Exemple : requeue.py php new k6 large mt q1,q6 "sentinelle de mémoire : somme des VmRSS (7.1)"
"""
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WORK = os.path.join(ROOT, "results", "sizes", "work")
OUT = os.path.join(ROOT, "results", "sizes", "discarded")


def main():
    if len(sys.argv) != 8:
        sys.exit(__doc__)
    lang, build, kernel, size, variant, params, reason = sys.argv[1:8]
    params = params.split(",")
    if subprocess.run(["pgrep", "-f", "tools/sizes/campaign.py"], capture_output=True).returncode == 0:
        sys.exit("le pilote tourne : attendre la fin de la campagne")
    stamp = time.strftime("%Y-%m-%dT%H:%M:%S")
    raw = os.path.join(WORK, "raw", f"{lang}.jsonl")
    keep, moved = [], []
    for line in open(raw):
        r = json.loads(line)
        if (r["lang"], r["build"], r["kernel"], r["size"], r["variant"]) == (lang, build, kernel, size, variant) \
                and r["param"] in params:
            moved.append(r)
        else:
            keep.append(line)
    cpath = os.path.join(WORK, "calib.json")
    calib = json.load(open(cpath))
    gone = {}
    for q in params:
        key = f"{lang}|{build}|{kernel}|{size}|{variant}|{q}"
        if key in calib:
            gone[key] = calib.pop(key)
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, f"{lang}.jsonl"), "a") as f:
        for r in moved:
            f.write(json.dumps({"discarded": stamp, "reason": reason, "record": r}) + "\n")
        for k, c in gone.items():
            f.write(json.dumps({"discarded": stamp, "reason": reason, "calibration": {k: c}}) + "\n")
    with open(raw + ".tmp", "w") as f:
        f.writelines(keep)
    os.replace(raw + ".tmp", raw)
    with open(cpath + ".tmp", "w") as f:
        json.dump(calib, f, indent=0, sort_keys=True)
    os.replace(cpath + ".tmp", cpath)
    print(f"{len(moved)} enregistrements et {len(gone)} étalonnages écartés vers {os.path.relpath(OUT, ROOT)} ; "
          f"à remesurer : campaign.py --langs {lang} --groups {kernel}:{size}")


if __name__ == "__main__":
    main()
