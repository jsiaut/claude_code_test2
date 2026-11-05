#!/usr/bin/env python3
"""Mesures de la remarque sur Swift (plan : docs/SWIFT.md, section 5.3), machine 24 (Emerald Rapids, du même modèle que
les machines 3, 11 et 16 dont viennent K5, les latences de K8 et K9 publiés, results/hw/machine24).

Cellules (sortie results/raw_swift_er/<implémentation>.jsonl, étiquette « swift_er ») :
* swift_er et c_er (constructions natives Emerald Rapids, comme les binaires recompilés sur la machine 3) : les 29
  cellules du score (K1 : 4 ; K2 tuned à 16 Kio, 256 Kio et 8 Mio ; K3 : 4 ; K4 : 3 ; K5 : 2 ; K6 : 6 ; K7 : 2 ; K8 : 2 ;
  K9 : 3), sans K10 (hors score) ;
* swift et c (binaires publiés, Cascade Lake, comme ceux des machines 11 et 16) : K9 natural, tuned et mt, K8 natural
  (latences), Q1 tuned (information) ;
* swift_ub (copie de sensibilité, cible cascadelake) : K4 natural_unsorted et natural_w_unsorted, K8 natural et
  natural_ub.
Répétitions : celles de results/calib.json (« c|… » pour c et c_er, « swift|… » pour swift, swift_er et swift_ub ;
natural_w_unsorted prend celles de natural_unsorted, natural_ub celles de natural). Échauffement : 1. 7 passes ; dans
chaque passe, toutes les cellules dans un ordre tiré au hasard (graine fixe) ; règle de vol du pilote.
Usage : measure_swift_er.py [--dry]"""
import json, os, random, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "raw_swift_er")
PASSES = 7
SEED = 20261105 + 2400

K2S = ["16384", "262144", "8388608"]
SCORE = ([("k1", v, "energy") for v in ("natural", "aos", "soa", "natural_shuffled")]
         + [("k2", "tuned", s) for s in K2S]
         + [("k3", v, "") for v in ("rmw_packed", "rmw_padded", "sw_packed", "sw_padded")]
         + [("k4", v, "") for v in ("natural_unsorted", "natural_sorted", "branchless_unsorted")]
         + [("k5", v, "") for v in ("natural", "tuned")]
         + [("k6", v, q) for v in ("natural", "tuned", "mt") for q in ("q6", "q1")]
         + [("k7", v, "") for v in ("natural", "tuned")]
         + [("k8", v, "") for v in ("natural", "tuned")]
         + [("k9", v, "") for v in ("natural", "tuned", "mt")])
PUBLISHED = [("k9", "natural", ""), ("k9", "tuned", ""), ("k9", "mt", ""), ("k8", "natural", ""), ("k6", "tuned", "q1")]
CELLS = {
    "swift_er": SCORE,
    "c_er": SCORE,
    "swift": PUBLISHED,
    "c": PUBLISHED,
    "swift_ub": [("k4", "natural_unsorted", ""), ("k4", "natural_w_unsorted", ""), ("k8", "natural", ""),
                 ("k8", "natural_ub", "")],
}
CALIB_VARIANT = {"natural_w_unsorted": "natural_unsorted", "natural_ub": "natural"}


def jobs(calib):
    out = []
    for impl, keys in CELLS.items():
        base = "c" if impl in ("c", "c_er") else "swift"
        for k, v, p in keys:
            reps = calib[f"{base}|{k}|{CALIB_VARIANT.get(v, v)}|{p}"]["reps"]
            out.append((impl, k, v, p, reps, 1))
    return out


def driver(impl, k, v, p, reps, w, out_dir=OUT, tag="swift_er"):
    args = [sys.executable, os.path.join(ROOT, "tools", "driver.py"), impl, "--kernels", k, "--variants", v,
            "--procs", "1", "--reps", str(reps), "--warmup", str(w), "--tag", tag,
            "--out", os.path.join(out_dir, f"{impl}.jsonl")]
    if p:
        args += ["--params", p]
    with open(os.path.join(out_dir, f"{impl}.log"), "a") as lf:
        subprocess.run(args, stdout=lf, stderr=subprocess.STDOUT, cwd=ROOT, timeout=3600)


def main():
    calib = json.load(open(os.path.join(ROOT, "results", "calib.json")))
    js = jobs(calib)
    if "--dry" in sys.argv:
        est = sum(calib[f"{'c' if i in ('c', 'c_er') else 'swift'}|{k}|{CALIB_VARIANT.get(v, v)}|{p}"].get("t_cal", 0.5)
                  * (r + w) for i, k, v, p, r, w in js)
        print(f"{len(js)} cellules, {PASSES} passes : {len(js) * PASSES} processus ; temps mesuré estimé "
              f"{est * PASSES / 60:.0f} min (hors lancement)")
        return
    os.makedirs(OUT, exist_ok=True)
    log = open(os.path.join(ROOT, "results", "campaign.log"), "a")
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"remarque sur Swift : début, {len(js)} cellules, "
              f"{len(js) * PASSES} processus\n")
    log.flush()
    for pas in range(PASSES):
        order = list(js)
        random.Random(SEED + pas).shuffle(order)
        for impl, k, v, p, reps, w in order:
            driver(impl, k, v, p, reps, w)
        log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"remarque sur Swift : passe {pas + 1}/{PASSES} terminée\n")
        log.flush()
        print(f"passe {pas + 1}/{PASSES}", flush=True)
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + "remarque sur Swift : fin\n")


if __name__ == "__main__":
    main()
