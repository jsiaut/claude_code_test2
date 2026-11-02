#!/usr/bin/env python3
"""Validation des copies de la remarque sur Java (docs/JAVA.md) : un processus par cellule de la campagne, deux
répétitions (une pour K7 naturel), sommes de contrôle vérifiées par le pilote contre results/expected.json.
Sorties : .work/java/<copie>.jsonl (hors dépôt)."""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from measure_java import jobs, driver  # noqa: E402

OUT_DIR = os.path.join(ROOT, ".work", "java")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for impl in ("java_ref", "java_fix", "java_exp"):
        for ext in (".jsonl", ".log"):
            if os.path.exists(os.path.join(OUT_DIR, impl + ext)):
                os.remove(os.path.join(OUT_DIR, impl + ext))
    todo = [(i, k, v, p) for i, k, v, p, _, _ in jobs() if i != "c"]
    for impl, k, v, p in todo:
        reps = 1 if (k, v) in (("k7", "natural"), ("k7", "natural_iso")) else 2
        driver(impl, k, v, p, reps, 1, out_dir=OUT_DIR, tag="java_valid")
    seen, bad = set(), 0
    for impl in ("java_ref", "java_fix", "java_exp"):
        path = os.path.join(OUT_DIR, f"{impl}.jsonl")
        for line in open(path):
            r = json.loads(line)
            reps = r.get("reps", [])
            ok = bool(reps) and r.get("returncode") == 0 and all(x["ok"] is True for x in reps)
            bad += not ok
            seen.add((r["lang"], r["kernel"], r["variant"], r["param"]))
            print(f"{r['lang']:9s} {r['kernel']:3s} {r['variant']:12s} {r['param']:6s} {'ok' if ok else 'ÉCHEC'} "
                  f"rc={r.get('returncode')} {[round(1e3 * x['sec'], 1) for x in reps]} ms "
                  f"{reps[0]['chk'] if reps else r.get('stderr', '')[-300:]}")
    missing = [c for c in todo if c not in seen]
    print(f"cellules : {len(seen)}, échecs : {bad}, manquantes : {missing}")


if __name__ == "__main__":
    main()
