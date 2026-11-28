#!/usr/bin/env python3
"""Valide une implémentation contre les résultats de référence (olap/expected).

Usage : check.py <commande de l'implémentation> <jeu : small|full> [fils...] [--queries t1,c4,...]
  ex. : check.py olap/c/olap_p small 1 4

La commande est lancée comme « <commande> <requête> <fils> <répétitions> <répertoire des données> --print » ; son
résultat canonique doit être celui de olap/expected/<jeu>/<requête>.txt, et l'empreinte de chaque ligne RESULT celle de
ce texte (FNV-1a 64 bits). Répertoires des données : variable OLAP_DATA (/opt/olap/data par défaut)."""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.environ.get("OLAP_DATA", "/opt/olap/data")
DIRS = {"small": {"t": "sf01", "c": "hits_small"}, "full": {"t": "sf10", "c": "hits20"}}
QUERIES = ["t1", "t6", "t9", "t18", "c4", "c12", "c16", "c20", "c33", "c36"]


def fnv1a(b):
    h = 0xCBF29CE484222325
    for x in b:
        h = ((h ^ x) * 0x100000001B3) & 0xFFFFFFFFFFFFFFFF
    return h


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    cmd, scale, threads = args[0].split(), args[1], [int(x) for x in args[2:]] or [1]
    queries = QUERIES
    for a in sys.argv[1:]:
        if a.startswith("--queries="):
            queries = a.split("=", 1)[1].split(",")
    reps = int(os.environ.get("OLAP_REPS", "2"))
    bad = 0
    for q in queries:
        want = open(os.path.join(HERE, "..", "expected", scale, q + ".txt"), "rb").read()
        for nt in threads:
            r = subprocess.run(cmd + [q, str(nt), str(reps), os.path.join(DATA, DIRS[scale][q[0]]), "--print"], capture_output=True)
            lines = r.stdout.split(b"\n")
            res = [l for l in lines if l.startswith(b"RESULT;")]
            body = b"\n".join(l for l in lines if not l.startswith(b"RESULT;"))
            sums = {l.split(b";")[6].decode() for l in res}
            times = [float(l.split(b";")[5]) for l in res]
            ok = r.returncode == 0 and len(res) == reps and body == want and sums == {f"{fnv1a(want):016x}"}
            bad += not ok
            print(f"{q:4s} {nt} fil(s) : {'juste' if ok else 'FAUX'} ; {min(times) if times else float('nan'):.4f} s"
                  + ("" if ok else f" ; code {r.returncode} ; {r.stderr.decode(errors='replace')[-300:]}"), flush=True)
            if not ok and body != want:
                a, b = body.split(b"\n"), want.split(b"\n")
                for i, (x, y) in enumerate(zip(a, b)):
                    if x != y:
                        print(f"     ligne {i + 1} : rendu {x[:120]!r}\n               attendu {y[:120]!r}")
                        break
                else:
                    print(f"     {len(a) - 1} lignes rendues, {len(b) - 1} attendues")
    print("tout est juste" if not bad else f"{bad} résultats faux")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
