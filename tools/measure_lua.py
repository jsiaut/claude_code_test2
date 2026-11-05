#!/usr/bin/env python3
"""Mesures de la remarque sur Lua (plan : docs/LUA.md, section 3.4), machine 23 (Cascade Lake, du même modèle que l'hôte
des données principales, results/hw/machine23).

Cellules (sortie results/raw_lua/<implémentation>.jsonl, étiquette « lua ») :
* lua_ref (le code publié, PUC-Lua 5.5.1) : K3 (quatre variantes), K4 (trois variantes), Q6 tuned et `mt`, K8 naturel
  (bases des corrections), Q6 naturel (contrôle), K9 tuned et `mt`, K7 tuned, K8 tuned, K1 soa, K2 tuned à 16 Kio,
  256 Kio et 8 Mio (bases des sensibilités) ;
* lua_fix (corrections publiées) : K3, K4, Q6 tuned et `mt`, K8 naturel, et Q6 naturel (code inchangé : contrôle) ;
* lua_exp (sensibilités) : K6 tuned_n et mt_n, K9 tuned_s et mt_s, K7 tuned_p, K8 tuned_it, K1 soa_h, K2 tuned_s ;
* luajit_ref et luajit_fix (sensibilité S-LuaJIT) : K8 naturel des deux, K3 conforme de luajit_fix ;
* python_ref et python_k8n : K8 naturel (conséquence pour Python) ;
* c (binaire de la campagne) : K3 sw_padded et rmw_padded, K4 natural_unsorted et branchless_unsorted, témoin du même
  hôte pour le pont.
7 passes ; dans chaque passe, toutes les cellules dans un ordre tiré au hasard (graine fixe). Répétitions de
results/calib.json (variante d'origine pour les variantes nouvelles ; K3 de luajit_fix, interprété, avec celles de K3
de Lua) ; échauffements de la campagne (3 pour LuaJIT, 1 sinon) ; règle de vol du pilote. Usage : measure_lua.py [--dry]"""
import json, os, random, subprocess, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "raw_lua")
PASSES = 7
SEED = 20261105 + 1000

K3 = [("k3", "rmw_packed", ""), ("k3", "rmw_padded", ""), ("k3", "sw_packed", ""), ("k3", "sw_padded", "")]
K4 = [("k4", "natural_unsorted", ""), ("k4", "natural_sorted", ""), ("k4", "branchless_unsorted", "")]
Q6 = [("k6", "tuned", "q6"), ("k6", "mt", "q6")]
Q6N, K8N = ("k6", "natural", "q6"), ("k8", "natural", "")
K2S = ["16384", "262144", "8388608"]
CELLS = {
    "lua_ref": K3 + K4 + Q6 + [Q6N, K8N, ("k9", "tuned", ""), ("k9", "mt", ""), ("k7", "tuned", ""), ("k8", "tuned", ""),
                               ("k1", "soa", "energy")] + [("k2", "tuned", s) for s in K2S],
    "lua_fix": K3 + K4 + Q6 + [Q6N, K8N],
    "lua_exp": [("k6", "tuned_n", "q6"), ("k6", "mt_n", "q6"), ("k9", "tuned_s", ""), ("k9", "mt_s", ""),
                ("k7", "tuned_p", ""), ("k8", "tuned_it", ""), ("k1", "soa_h", "energy")] + [("k2", "tuned_s", s) for s in K2S],
    "luajit_ref": [K8N],
    "luajit_fix": K3 + [K8N],
    "python_ref": [K8N],
    "python_k8n": [K8N],
    "c": [("k3", "sw_padded", ""), ("k3", "rmw_padded", ""), ("k4", "natural_unsorted", ""), ("k4", "branchless_unsorted", "")],
}
CALIB_VARIANT = {"tuned_n": "tuned", "mt_n": "mt", "tuned_s": "tuned", "mt_s": "mt", "tuned_p": "tuned",
                 "tuned_it": "tuned", "soa_h": "soa"}


def calib_base(impl, k):
    if impl == "luajit_fix" and k == "k3":
        return "lua"  # K3 interprété : répétitions de K3 de Lua (celles de LuaJIT valaient pour 0,04 s)
    if impl.startswith("luajit"):
        return "luajit"
    if impl.startswith("lua"):
        return "lua"
    if impl.startswith("python"):
        return "python"
    return impl


def warmup(impl, k):
    return 3 if impl.startswith("luajit") else 1


def jobs():
    calib = json.load(open(os.path.join(ROOT, "results", "calib.json")))
    out = []
    for impl, keys in CELLS.items():
        for k, v, p in keys:
            reps = calib[f"{calib_base(impl, k)}|{k}|{CALIB_VARIANT.get(v, v)}|{p}"]["reps"]
            out.append((impl, k, v, p, reps, warmup(impl, k)))
    return out


def driver(impl, k, v, p, reps, w, out_dir=OUT, tag="lua"):
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
    n = len(js) * PASSES
    if "--dry" in sys.argv:
        print(f"{len(js)} cellules, {PASSES} passes : {n} processus")
        return
    log = open(os.path.join(ROOT, "results", "campaign.log"), "a")
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"remarque Lua : début, {len(js)} cellules, {n} processus\n")
    log.flush()
    for pas in range(PASSES):
        order = list(js)
        random.Random(SEED + pas).shuffle(order)
        for impl, k, v, p, reps, w in order:
            driver(impl, k, v, p, reps, w)
        log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + f"remarque Lua : passe {pas + 1}/{PASSES} terminée\n")
        log.flush()
        print(f"passe {pas + 1}/{PASSES}", flush=True)
    log.write(time.strftime("%Y-%m-%dT%H:%M:%S ") + "remarque Lua : fin\n")


if __name__ == "__main__":
    main()
