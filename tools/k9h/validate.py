#!/usr/bin/env python3
"""Validation des copies au harnais commun de K9 (docs/K9.md) : un processus par cellule, deux répétitions, sommes de
contrôle vérifiées par le pilote contre results/expected.json. Sortie : .work/k9h/valid.jsonl (hors dépôt)."""
import json, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from measure_k9h import cells, JIT, base_lang  # noqa: E402

OUT = os.path.join(ROOT, ".work", "k9h", "valid.jsonl")


def main():
    if os.path.exists(OUT):
        os.remove(OUT)
    todo = [(i, v) for i, v in cells() if i.endswith("_k9h")]
    for impl, v in todo:
        args = [sys.executable, os.path.join(ROOT, "tools", "driver.py"), impl, "--kernels", "k9", "--variants", v,
                "--procs", "1", "--reps", "2", "--warmup", "3" if base_lang(impl) in JIT else "1", "--tag", "k9h_valid",
                "--out", OUT]
        subprocess.run(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, cwd=ROOT, timeout=1800)
    seen = set()
    for line in open(OUT):
        r = json.loads(line)
        reps = r.get("reps", [])
        ok = bool(reps) and r.get("returncode") == 0 and all(x["ok"] is True for x in reps)
        seen.add((r["lang"], r["variant"]))
        print(f"{r['lang']:20s} {r['variant']:8s} {'ok' if ok else 'ÉCHEC'} rc={r.get('returncode')} "
              f"{[round(1e3 * x['sec'], 1) for x in reps]} ms {reps[0]['chk'] if reps else r.get('stderr', '')[-300:]}")
    missing = [c for c in todo if c not in seen]
    print("manquantes :", missing)


if __name__ == "__main__":
    main()
