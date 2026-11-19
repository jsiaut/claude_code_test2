#!/usr/bin/env python3
"""v4, point 2 : sommes de contrôle de référence de chaque taille, calculées par l'implémentation C, construite à
chaque taille (tools/sizes/build.py ; toutes ses variantes, qui doivent concorder entre elles) -> results/sizes/expected.json (clés « noyau:taille[:param] »).
Usage : expected.py [k1,k4,...] (par défaut tous les noyaux) ; les données des grandes tailles sont créées puis
effacées noyau par noyau."""
import json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sizes as S  # noqa: E402

PLAN = {"k1": [("natural", "energy"), ("aos", "energy"), ("soa", "energy"), ("natural_shuffled", "energy")],
        "k4": [("natural_unsorted", ""), ("natural_sorted", ""), ("branchless_unsorted", "")],
        "k5": [("natural", ""), ("tuned", "")],
        "k6": [(v, q) for v in ("natural", "tuned", "mt") for q in ("q6", "q1")],
        "k7": [("natural", ""), ("tuned", "")], "k8": [("natural", ""), ("tuned", "")],
        "k9": [("natural", ""), ("tuned", ""), ("mt", "")]}
TOL = {"k1": 1e-6, "k5": 1e-3, "k9": 1e-9}


def run_c(kernel, size, variant, param):
    import build as B
    name = S.set_of(kernel, size)
    run = os.path.join(S.ROOT, "bench", "c", "run") if name is None else os.path.join(B.ensure_build("c", name), "run")
    env = S.environ(kernel, size)
    for k in S.PUBLISHED:  # la taille est dans la construction du C, pas dans l'environnement
        env.pop(k, None)
    env["WARMUP"] = "0"
    out = subprocess.run([run, kernel, variant, "1"] + ([param] if param else []),
                         capture_output=True, text=True, env=env).stdout
    return [l for l in out.splitlines() if l.startswith("RESULT;")][-1].split(";")[6]


def main():
    kernels = sys.argv[1].split(",") if len(sys.argv) > 1 else list(PLAN)
    path = os.path.join(S.ROOT, "results", "sizes", "expected.json")
    exp = json.load(open(path)) if os.path.exists(path) else {}
    os.makedirs(os.path.dirname(path), exist_ok=True)
    for k in kernels:
        for size in S.ORDER[k]:
            S.ensure_data(k, size)
            for param in sorted({p for _, p in PLAN[k]}):
                vals = {v: run_c(k, size, v, p) for v, p in PLAN[k] if p == param}
                ref = vals[PLAN[k][0][0]] if param == PLAN[k][0][1] else next(iter(vals.values()))
                for v, c in vals.items():
                    if k in TOL:
                        assert abs(float(c) - float(ref)) <= TOL[k] * abs(float(ref)), (k, size, v, c, ref)
                    else:
                        assert c == ref, (k, size, v, c, ref)
                key = f"{k}:{size}" + (f":{param}" if k == "k6" else "")
                exp[key] = ref
                print(key, ref, flush=True)
            if size != "pub":
                S.drop_data(k, size)
        json.dump(exp, open(path, "w"), indent=1, sort_keys=True)


if __name__ == "__main__":
    main()
