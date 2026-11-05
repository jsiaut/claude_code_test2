#!/usr/bin/env python3
"""Validation des copies de la remarque sur Python (docs/PYTHON.md) : un processus par cellule Python de la
campagne, deux répétitions (une pour K2, K3, K7 et K8), sommes de contrôle vérifiées par le pilote contre
results/expected.json. Sorties : .work/py/valid/<copie>.jsonl (hors dépôt)."""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from measure_python import jobs, driver  # noqa: E402

OUT_DIR = os.path.join(ROOT, ".work", "py", "valid")
COPIES = ("python_ref", "python_fix", "python_exp", "python_ftfix")
LONG = {"k2", "k3", "k7", "k8"}


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for impl in COPIES:
        for ext in (".jsonl", ".log"):
            if os.path.exists(os.path.join(OUT_DIR, impl + ext)):
                os.remove(os.path.join(OUT_DIR, impl + ext))
    todo = [(i, k, v, p) for i, k, v, p, _, _ in jobs() if i in COPIES]
    for impl, k, v, p in todo:
        driver(impl, k, v, p, 1 if k in LONG else 2, 1, out_dir=OUT_DIR, tag="python_valid")
    seen, bad = set(), 0
    for impl in COPIES:
        for line in open(os.path.join(OUT_DIR, f"{impl}.jsonl")):
            r = json.loads(line)
            reps = r.get("reps", [])
            ok = bool(reps) and r.get("returncode") == 0 and all(x["ok"] is True for x in reps)
            bad += not ok
            seen.add((r["lang"], r["kernel"], r["variant"], r["param"]))
            print(f"{r['lang']:12s} {r['kernel']:3s} {r['variant']:20s} {r['param']:10s} {'ok' if ok else 'ÉCHEC'} "
                  f"rc={r.get('returncode')} {[round(1e3 * x['sec'], 2) for x in reps]} ms wall {r.get('wall', 0):.1f} s "
                  f"{reps[0]['chk'] if reps else r.get('stderr', '')[-300:]}")
    missing = [c for c in todo if c not in seen]
    print(f"cellules : {len(seen)}, échecs : {bad}, manquantes : {missing}")


if __name__ == "__main__":
    main()
