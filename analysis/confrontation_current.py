#!/usr/bin/env python3
"""Confrontation et notation à l'aveugle rejouées dans l'état actuel du classement (errata de la matrice et corrections
du banc d'Ada à C#), avec la copie standard de Chapel corrigée le 31/10 (meilleure forme standard par clé, comme
analysis/chapel_check.py). Les sorties datées du 30 octobre (results/confrontation.json, report_confrontation.md,
blind_compare.json, report_blind.md) ne changent pas. Sorties : results/confrontation_current.json,
results/report_confrontation_current.md, results/blind_compare_current.json, results/report_blind_current.md."""
import os, sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_v3 as v3  # noqa: E402
import blind_compare  # noqa: E402
import chapel_check as cc  # noqa: E402
import confrontation as cf  # noqa: E402


def chapel_fix(ratios):
    """Copie standard de Chapel : pour K5 tuned et K1 aos/soa, la meilleure des deux formes standard (docs/CHAPEL.md, 4.3)."""
    raw, _bad = cc.load_raw()
    rng = np.random.default_rng(v3.SEED + 80)  # mêmes tirages, dans le même ordre, que chapel_check
    _ = {k: cc.ratio(raw["chapel_exp"][k], raw["chapel_ref"][k], rng) for k in cc.CHANGED + cc.CONTROLS}
    std = {k: cc.ratio(raw["chapel_std2"][k], raw["chapel_ref"][k], rng) for k in cc.STD_KEYS}
    out = dict(ratios)
    for k in cc.STD_KEYS:
        old = out.get(("chapel", k))
        if old is None or std[k]["ratio"] < old["ratio"]:
            out[("chapel", k)] = {**std[k], "erratum": "31/10, docs/CHAPEL.md"}
    return out


if __name__ == "__main__":
    cf.main(suffix="_current", fix_ratios=chapel_fix)
    blind_compare.main(suffix="_current")
