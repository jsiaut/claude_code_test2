#!/usr/bin/env python3
"""v4, campagne finale (docs/V4_FINAL.md, 11, écart 1) : contrôle d'exactitude « par construction » des formes de K4
(règle C2, 2 : exacte pour toutes les données admises, pas seulement pour les fichiers du banc).

Données extrêmes : 2^28 octets (la grande taille), tous à 255 : chaque octet compte, et chaque accumulateur reçoit le
plus qu'il puisse recevoir. Somme attendue : 2^28 x 255. Chaque cellule de K4 de la campagne (constructions pub, cv,
chk, unc ; jeu de tailles « large ») est exécutée une fois, une répétition, sans échauffement, sur ces données placées
dans le répertoire de données de la grande taille (/dev/shm/ms_k4_large, que lisent aussi les constructions qui fixent
ce répertoire à la compilation : Mojo), effacé ensuite pour que la campagne refasse les vraies données.
Sortie : results/final/k4_extreme.txt. À lancer machine au repos, hors de la campagne."""
import importlib.util, os, shutil, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
_spec = importlib.util.spec_from_file_location("camp", os.path.join(HERE, "campaign.py"))
C = importlib.util.module_from_spec(_spec)
sys.argv = sys.argv[:1]
_spec.loader.exec_module(C)

N = 1 << 28
EXPECT = str(N * 255)
D = C.S.data_dir("k4", "large")
OUT = os.path.join(ROOT, "results", "final", "k4_extreme.txt")


def main():
    if os.path.exists(os.path.join(D, ".complete")):
        raise SystemExit(f"{D} contient les vraies données d'un groupe en cours : contrôle refusé")
    shutil.rmtree(D, ignore_errors=True)
    os.makedirs(D)
    with open(os.path.join(D, "k4_bytes.u8"), "wb") as f:
        chunk = b"\xff" * (1 << 24)
        for _ in range(N >> 24):
            f.write(chunk)
    lines, bad = [], 0
    try:
        for lang in C.LANGS:
            for cons in C.FB.constructions(lang):
                for v, q in C.cells(lang, cons, "k4"):
                    d = C.runner_dir(lang, cons, "k4", "large")
                    env = dict(os.environ, MS_DATA=D, WARMUP="0")
                    for k in list(env):
                        if k.startswith("MS_") and k != "MS_DATA":
                            env.pop(k)
                    r = subprocess.run([os.path.join(d, "run"), "k4", v, "1"], cwd=d, env=env, capture_output=True,
                                       text=True, timeout=3600)
                    got = [x.split(";")[6] for x in r.stdout.splitlines() if x.startswith("RESULT;")]
                    ok = r.returncode == 0 and got and all(g.strip() == EXPECT for g in got)
                    bad += not ok
                    lines.append(f"{lang:8} {cons:7} {v:20} {'juste' if ok else 'FAUX'} {got[:1]} code {r.returncode}")
                    print(lines[-1], flush=True)
    finally:
        shutil.rmtree(D, ignore_errors=True)
    with open(OUT, "w") as g:
        g.write(f"# K4, 2^28 octets à 255 (somme attendue {EXPECT}), {time.strftime('%Y-%m-%d %H:%M')} UTC, machine "
                f"{C.FB.machine()} ; {len(lines)} cellules, {bad} fausses\n")
        g.write("\n".join(lines) + "\n")
    print(f"{len(lines)} cellules, {bad} fausses -> {OUT}")


if __name__ == "__main__":
    main()
