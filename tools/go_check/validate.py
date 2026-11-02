#!/usr/bin/env python3
"""Validation des copies de la remarque sur Go (docs/GO.md) : un processus par cellule Go de la campagne (sauf
go_nopre, binaire de go_ref), deux répétitions (une pour les noyaux longs), sommes de contrôle vérifiées par le pilote
contre results/expected.json. Sorties : .work/go/<copie>.jsonl (hors dépôt)."""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from measure_go import jobs, driver  # noqa: E402

OUT_DIR = os.path.join(ROOT, ".work", "go")
COPIES = ("go_ref", "go_fix", "go_noexp", "go_exp")
LONG = {"k7", "k3", "k8"}


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for impl in COPIES:
        for ext in (".jsonl", ".log"):
            if os.path.exists(os.path.join(OUT_DIR, impl + ext)):
                os.remove(os.path.join(OUT_DIR, impl + ext))
    todo = [(i, k, v, p) for i, k, v, p, _, _ in jobs() if i in COPIES]
    for impl, k, v, p in todo:
        driver(impl, k, v, p, 1 if k in LONG or k == "k2" else 2, 1, out_dir=OUT_DIR, tag="go_valid")
    seen, bad = set(), 0
    for impl in COPIES:
        for line in open(os.path.join(OUT_DIR, f"{impl}.jsonl")):
            r = json.loads(line)
            reps = r.get("reps", [])
            ok = bool(reps) and r.get("returncode") == 0 and all(x["ok"] is True for x in reps)
            bad += not ok
            seen.add((r["lang"], r["kernel"], r["variant"], r["param"]))
            if not ok or r["variant"] not in ("natural", "tuned", "mt", "natural_sorted", "natural_unsorted",
                                               "branchless_unsorted", "natural_shuffled", "aos", "soa", "sw_padded",
                                               "sw_packed", "rmw_padded", "rmw_packed"):
                print(f"{r['lang']:9s} {r['kernel']:3s} {r['variant']:12s} {r['param']:10s} {'ok' if ok else 'ÉCHEC'} "
                      f"rc={r.get('returncode')} {[round(1e3 * x['sec'], 1) for x in reps]} ms "
                      f"{reps[0]['chk'] if reps else r.get('stderr', '')[-300:]}")
    missing = [c for c in todo if c not in seen]
    print(f"cellules : {len(seen)}, échecs : {bad}, manquantes : {missing}")


if __name__ == "__main__":
    main()
