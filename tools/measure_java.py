#!/usr/bin/env python3
"""Mesures de la remarque sur Java (plan : docs/JAVA.md, section 3.4), machine 17 (Emerald Rapids, results/hw/machine17).

Cellules (sortie results/raw_java/<implémentation>.jsonl, étiquette « java ») :
* java_ref (copie exacte de bench/java) et java_fix (correction : K5 tuned et K1 soa sur des copies hors tas alignées
  sur 64 octets) : K5 tuned, K1 soa (clés corrigées) ; K5 naturel, K1 naturel, K6 tuned Q6 (témoins, code inchangé) ;
* java_exp (sensibilités, tools/java_check/make_copies.py) : chaque forme nouvelle et la variante d'origine qu'elle
  remplace, dans la même copie ;
* c (binaire de la campagne) : témoin du même hôte pour la règle du pont (analysis/transfer_check.py).
7 processus par cellule, en 7 passes ; dans chaque passe, toutes les cellules dans un ordre tiré au hasard (graine
fixe). Répétitions de results/calib.json (clé de la variante d'origine) ; échauffements des données publiées (Java : 10
pour K5, 3 sinon ; C : 2 pour K5, 1 sinon) ; règle de vol du pilote (processus refait au-delà de 2 % de la capacité des
4 vCPU, deux fois au plus). Usage : measure_java.py [--dry]"""
import json, os, random, subprocess, sys, time

ROOT = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(ROOT)
OUT = os.path.join(ROOT, "results", "raw_java")
PASSES = 7
SEED = 20261102 + 300
K5T, K5N = ("k5", "tuned", ""), ("k5", "natural", "")
K1S, K1N = ("k1", "soa", "energy"), ("k1", "natural", "energy")
Q6T, Q6M, Q1T, Q1M = ("k6", "tuned", "q6"), ("k6", "mt", "q6"), ("k6", "tuned", "q1"), ("k6", "mt", "q1")
FIXED = [K5T, K1S]
WITNESS = [K5N, K1N, Q6T]
EXP = [Q1T, ("k6", "tuned_1p", "q1"), Q1M, ("k6", "mt_1p", "q1"), ("k6", "mt_pool", "q1"), ("k6", "mt_pool_1p", "q1"),
       Q6M, ("k6", "mt_pool", "q6"),
       ("k9", "tuned", ""), ("k9", "tuned_vec", ""), ("k9", "mt", ""), ("k9", "mt_pool", ""), ("k9", "mt_pool_vec", ""),
       ("k7", "natural", ""), ("k7", "natural_iso", ""), ("k7", "tuned", ""), ("k7", "tuned_iso", ""),
       ("k7", "tuned_batch", ""),
       ("k8", "tuned", ""), ("k8", "tuned_it", "")]
C_BRIDGE = [K5T, K1S, Q1T, Q1M, Q6M, ("k7", "natural", ""), ("k7", "tuned", ""), ("k8", "tuned", ""), ("k9", "tuned", ""),
            ("k9", "mt", "")]
CELLS = {"java_ref": FIXED + WITNESS, "java_fix": FIXED + WITNESS, "java_exp": EXP, "c": C_BRIDGE}
# variantes propres aux copies : répétitions de la variante d'origine
CALIB_VARIANT = {"tuned_1p": "tuned", "mt_1p": "mt", "mt_pool": "mt", "mt_pool_1p": "mt", "tuned_vec": "tuned",
                 "mt_pool_vec": "mt", "natural_iso": "natural", "tuned_iso": "tuned", "tuned_batch": "tuned",
                 "tuned_it": "tuned"}


def warmup(impl, k):
    if impl.startswith("java"):
        return 10 if k == "k5" else 3
    return 2 if k == "k5" else 1


def jobs():
    calib = json.load(open(os.path.join(ROOT, "results", "calib.json")))
    out = []
    for impl, keys in CELLS.items():
        base = "java" if impl.startswith("java") else impl
        for k, v, p in keys:
            reps = calib[f"{base}|{k}|{CALIB_VARIANT.get(v, v)}|{p}"]["reps"]
            out.append((impl, k, v, p, reps, warmup(impl, k)))
    return out


def driver(impl, k, v, p, reps, w, out_dir=OUT, tag="java"):
    args = [sys.executable, os.path.join(ROOT, "tools", "driver.py"), impl, "--kernels", k, "--variants", v,
            "--procs", "1", "--reps", str(reps), "--warmup", str(w), "--tag", tag,
            "--out", os.path.join(out_dir, f"{impl}.jsonl")]
    if p:
        args += ["--params", p]
    with open(os.path.join(out_dir, f"{impl}.log"), "a") as lf:
        subprocess.run(args, stdout=lf, stderr=subprocess.STDOUT, cwd=ROOT, timeout=3600)


def main():
    os.makedirs(OUT, exist_ok=True)
    js = jobs()
    if "--dry" in sys.argv:
        print(f"{len(js)} cellules x {PASSES} passes = {len(js) * PASSES} processus")
        return
    log = open(os.path.join(ROOT, "results", "campaign.log"), "a")
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"remarque Java : début, {len(js)} cellules, {PASSES} passes\n")
    log.flush()
    for pas in range(PASSES):
        order = list(js)
        random.Random(SEED + pas).shuffle(order)
        for impl, k, v, p, reps, w in order:
            driver(impl, k, v, p, reps, w)
        log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"remarque Java : passe {pas + 1}/{PASSES} terminée\n")
        log.flush()
        print(f"passe {pas + 1}/{PASSES}", flush=True)
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + "remarque Java : fin\n")


if __name__ == "__main__":
    main()
