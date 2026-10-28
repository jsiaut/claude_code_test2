#!/usr/bin/env python3
"""Empreinte K1 (pilier D2a), mesurée après le redémarrage de la VM (docs/METHODOLOGY.md, journal).

Méthode en deux points dans le processus (tools/patch_footprint_mem.py) : la variante `footprint`
émet META;mem;<kind>;<M(P1)>;<M(P2)> et META;rss;<RSS(P1)>;<RSS(P2)>, où P1 = tampon brut chargé et
P2 = collection naturelle construite (tampon toujours vivant). kind = live (octets vivants comptés par
le runtime ou l'allocateur après un GC complet) ou rss (RSS courant).
octets/particule = (M(P2) - M(P1)) / 4 194 304, médiane de 3 processus. Les octets ne dépendent pas
de la vitesse de la machine. Entrée : results/raw_post/*.jsonl (tag post_fp2).
Sorties : results/footprint.json ({langage: octets/particule}) et results/footprint_detail.json.
"""
import glob, json, os, statistics

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
N1 = 4194304
# Collections de valeurs contiguës : la taille d'un élément est fixée par le langage (64 o, imprimée
# par les sondes, capacité A1) et 11 implémentations mesurent 64,00 à 64,03 o. Deux mesures sont
# faussées par l'allocateur, mécanisme vérifié (strace, getOccupiedMem) : on retient alors la taille
# de structure, et la mesure brute reste dans results/footprint_detail.json.
STRUCTURAL = {
    "nim": (64.0, "l'allocateur de Nim arrondit la demande de 256 Mio à sa classe de taille (264 Mio, "
                  "8 Mio jamais touchés) : getOccupiedMem compte 66 o, la mémoire physique est de 64 o"),
    "mojo": (64.0, "l'allocateur du runtime Mojo (réservations de 1 Gio, libération par madvise) réutilise "
                   "environ 24 Mo du tampon de chargement libéré pour la liste : le RSS ne voit que 58 o"),
}


def main():
    per = {}
    for f in glob.glob(os.path.join(ROOT, "results", "raw_post", "*.jsonl")):
        for line in open(f):
            r = json.loads(line)
            if r["kernel"] != "fp" or r.get("tag") != "post_fp2" or r.get("returncode") != 0 or "mem" not in r["meta"]:
                continue
            kind, p1, p2 = r["meta"]["mem"].split(";")
            q1, q2 = r["meta"].get("rss", "0;0").split(";")
            per.setdefault(r["lang"], []).append((kind, (int(p2) - int(p1)) / N1, (int(q2) - int(q1)) / N1, int(q1)))
    bpp, detail = {}, {}
    print(f"{'langage':14s} {'mesure':6s} {'o/particule':>12s} {'écart':>7s} {'RSS (contrôle)':>15s}  processus")
    for lang, xs in sorted(per.items(), key=lambda kv: statistics.median(x[1] for x in kv[1])):
        if len(xs) < 3:
            print(f"{lang}: {len(xs)} processus seulement")
        b = statistics.median(x[1] for x in xs)
        rss = statistics.median(x[2] for x in xs)
        spread = max(x[1] for x in xs) - min(x[1] for x in xs)
        measured = b
        if lang in STRUCTURAL:
            b = STRUCTURAL[lang][0]
        bpp[lang] = round(b, 2)
        detail[lang] = {"kind": xs[0][0], "bytes_per_particle": round(b, 2), "measured": round(measured, 2),
                        "note": STRUCTURAL.get(lang, (None, ""))[1], "per_process": [round(x[1], 3) for x in xs],
                        "rss_bytes_per_particle": round(rss, 2), "rss_p1_mib": round(statistics.median(x[3] for x in xs) / 2 ** 20, 1),
                        "D2a": round(min(1.0, 64.0 / b), 3) if b > 0 else None}
        print(f"{lang:14s} {xs[0][0]:6s} {b:12.2f} {spread:7.2f} {rss:15.2f}  {len(xs)}"
              + (f"  (mesure brute {measured:.2f} : {STRUCTURAL[lang][1]})" if lang in STRUCTURAL else ""))
    json.dump(bpp, open(os.path.join(ROOT, "results", "footprint.json"), "w"), indent=1, sort_keys=True)
    json.dump(detail, open(os.path.join(ROOT, "results", "footprint_detail.json"), "w"), indent=1, sort_keys=True)


if __name__ == "__main__":
    main()
