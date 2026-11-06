#!/usr/bin/env python3
"""Mesures de l'ajout de BQN (plan : docs/BQN.md, section 3.4), machine 26 (Emerald Rapids, du même modèle que les
machines 3, 11 et 16 dont viennent K5, les latences de K8 et K9 publiés ; results/hw/machine26).

Cellules (sortie results/raw_bqn/<implémentation>.jsonl, étiquette « bqn ») :
* bqn (bench/bqn : CBQN pour la cible Cascade Lake, clés de la machine 1, K9 et latences de K8) : les 29 cellules du
  score (K1 : 4 ; K2 tuned à 16 Kio, 256 Kio et 8 Mio ; K3 : 4 ; K4 : 3 ; K5 : 2 ; K6 : 6 ; K7 : 2 ; K8 : 2 ; K9 : 3),
  plus les variantes de sensibilité K1 natural_ns et natural_ns_shuffled, K7 natural_arr, K8 natural_ns ;
* bqn_er (bench/bqn_er : construction native de la machine 26, pour K5 et la réplication) : les 29 cellules du score ;
* bqn_o3 (sensibilité B-o3, construction par défaut de CBQN) : les 9 cellules naturelles du score (K1 natural et
  natural_shuffled, K4 natural_unsorted, K5 natural, K6 natural q6 et q1, K7 natural, K8 natural, K9 natural) ;
* c (binaire publié, Cascade Lake : témoin des clés de la machine 1, de K9 et des latences de K8) et c_er
  (construction native Emerald Rapids, identique au binaire de la machine 3 : témoin de K5 et de la réplication) : les
  29 cellules du score ;
* c_gcc_cl (second témoin, binaire des données publiées de c_gcc) : les 24 cellules des clés de la machine 1 (K1, K2,
  K3, K4, K6, K7, K8).
Répétitions : celles de results/calib.json (« c|… ») pour c, c_er et c_gcc_cl ; pour bqn, la règle du pilote
(tools/driver.py : 3 s divisées par le temps d'une répétition, entre 3 et 10 ; 2 au-delà de 5 s), appliquée au temps
d'une répétition de calibration mesuré au début avec l'échauffement de la campagne (écrit dans results/calib.json sous
« bqn|… ») ; bqn_er et bqn_o3 prennent les répétitions de la cellule de bqn. Échauffement : 3 pour bqn, bqn_er et
bqn_o3 (JIT de CBQN), 1 pour le C. 7 passes ; dans chaque passe, toutes les cellules dans un ordre tiré au hasard
(graine fixe) ; règle de vol du pilote. À la fin : empreinte de K1 (3 processus, étiquette post_fp2,
results/raw_post/bqn.jsonl), puis C3 (tools/c3_measure.py bqn).
Usage : measure_bqn.py [--dry]"""
import json, os, random, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "raw_bqn")
PASSES = 7
SEED = 20261106 + 2600

K2S = ["16384", "262144", "8388608"]
M1 = ([("k1", v, "energy") for v in ("natural", "aos", "soa", "natural_shuffled")]
      + [("k2", "tuned", s) for s in K2S]
      + [("k3", v, "") for v in ("rmw_packed", "rmw_padded", "sw_packed", "sw_padded")]
      + [("k4", v, "") for v in ("natural_unsorted", "natural_sorted", "branchless_unsorted")]
      + [("k6", v, q) for v in ("natural", "tuned", "mt") for q in ("q6", "q1")]
      + [("k7", v, "") for v in ("natural", "tuned")]
      + [("k8", v, "") for v in ("natural", "tuned")])
SCORE = M1 + [("k5", v, "") for v in ("natural", "tuned")] + [("k9", v, "") for v in ("natural", "tuned", "mt")]
EXTRA = [("k1", "natural_ns", "energy"), ("k1", "natural_ns_shuffled", "energy"), ("k7", "natural_arr", ""),
         ("k8", "natural_ns", "")]
NATURAL = [("k1", "natural", "energy"), ("k1", "natural_shuffled", "energy"), ("k4", "natural_unsorted", ""),
           ("k5", "natural", ""), ("k6", "natural", "q6"), ("k6", "natural", "q1"), ("k7", "natural", ""),
           ("k8", "natural", ""), ("k9", "natural", "")]
CELLS = {
    "bqn": SCORE + EXTRA,
    "bqn_er": SCORE,
    "bqn_o3": NATURAL,
    "c": SCORE,
    "c_er": SCORE,
    "c_gcc_cl": M1,
}
WITNESS = {"c", "c_er", "c_gcc_cl"}
WARM = 3  # échauffement des trois exécutions de BQN (JIT de CBQN : une fonction est compilée après deux appels)


def rule(t):
    """Règle de calibration de tools/driver.py."""
    reps = max(3, min(10, int(3.0 / max(t, 1e-6))))
    return 2 if t > 5.0 else reps


def calibrate():
    """Une répétition de chaque cellule de bqn (échauffement de la campagne), répétitions écrites dans
    results/calib.json."""
    path = os.path.join(ROOT, "results", "calib.json")
    calib = json.load(open(path))
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import driver
    for k, v, p in SCORE + EXTRA:
        key = f"bqn|{k}|{v}|{p}"
        if key in calib:
            continue
        rec = driver.run_one("bqn", k, v, p, 1, WARM, 3600)
        t = rec["reps"][0]["sec"] if rec.get("reps") else 10.0
        calib[key] = {"reps": rule(t), "procs": PASSES, "t_cal": t}
        print(f"calibration {key} t={t:.4f} reps={calib[key]['reps']}", flush=True)
        with open(path + ".tmp", "w") as cf:
            json.dump(calib, cf, indent=0, sort_keys=True)
        os.replace(path + ".tmp", path)
    return calib


def jobs(calib):
    out = []
    for impl, keys in CELLS.items():
        base = "c" if impl in WITNESS else "bqn"
        for k, v, p in keys:
            reps = calib[f"{base}|{k}|{v}|{p}"]["reps"]
            out.append((impl, k, v, p, reps, 1 if impl in WITNESS else WARM))
    return out


def driver(impl, k, v, p, reps, w, out_dir=OUT, tag="bqn"):
    args = [sys.executable, os.path.join(ROOT, "tools", "driver.py"), impl, "--kernels", k, "--variants", v,
            "--procs", "1", "--reps", str(reps), "--warmup", str(w), "--tag", tag,
            "--out", os.path.join(out_dir, f"{impl}.jsonl")]
    if p:
        args += ["--params", p]
    with open(os.path.join(out_dir, f"{impl}.log"), "a") as lf:
        subprocess.run(args, stdout=lf, stderr=subprocess.STDOUT, cwd=ROOT, timeout=3600)


def main():
    os.makedirs(OUT, exist_ok=True)
    if "--dry" in sys.argv:
        n = sum(len(v) for v in CELLS.values())
        print(f"{n} cellules, {PASSES} passes : {n * PASSES} processus")
        return
    log = open(os.path.join(ROOT, "results", "campaign.log"), "a")
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + "ajout de BQN : calibration\n")
    log.flush()
    calib = calibrate()
    js = jobs(calib)
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"ajout de BQN : début, {len(js)} cellules, {len(js) * PASSES} processus\n")
    log.flush()
    for pas in range(PASSES):
        order = list(js)
        random.Random(SEED + pas).shuffle(order)
        for impl, k, v, p, reps, w in order:
            driver(impl, k, v, p, reps, w)
        log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"ajout de BQN : passe {pas + 1}/{PASSES} terminée\n")
        log.flush()
        print(f"passe {pas + 1}/{PASSES}", flush=True)
    # empreinte de K1 (D2a, méthode en deux points de analysis/footprint.py)
    post = os.path.join(ROOT, "results", "raw_post")
    for _ in range(3):
        driver("bqn", "fp", "footprint", "energy", 1, 1, out_dir=post, tag="post_fp2")
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + "ajout de BQN : empreinte terminée, C3\n")
    log.flush()
    with open(os.path.join(OUT, "c3.log"), "w") as lf:
        subprocess.run([sys.executable, os.path.join(ROOT, "tools", "c3_measure.py"), "bqn"], stdout=lf,
                       stderr=subprocess.STDOUT, cwd=ROOT, timeout=3600)
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + "ajout de BQN : fin\n")


if __name__ == "__main__":
    main()
