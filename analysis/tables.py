#!/usr/bin/env python3
"""Tableaux Markdown des résultats bruts par noyau (médianes et coefficient de variation)."""
import json, os, statistics, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import final_data, point, RANKED, ANNEX  # noqa: E402

ORDER = RANKED + list(ANNEX)
COLS = {
    "K1 (ms)": [("k1", "natural", "energy"), ("k1", "natural_shuffled", "energy"), ("k1", "aos", "energy"), ("k1", "soa", "energy")],
    "K3 (ms)": [("k3", "rmw_packed", ""), ("k3", "rmw_padded", ""), ("k3", "sw_packed", ""), ("k3", "sw_padded", "")],
    "K4 (ms)": [("k4", "natural_unsorted", ""), ("k4", "natural_sorted", ""), ("k4", "branchless_unsorted", "")],
    "K5 (ms)": [("k5", "natural", ""), ("k5", "tuned", "")],
    "K6 (ms)": [("k6", "natural", "q6"), ("k6", "tuned", "q6"), ("k6", "mt", "q6"), ("k6", "natural", "q1"), ("k6", "tuned", "q1"), ("k6", "mt", "q1")],
    "K7 (ms)": [("k7", "natural", ""), ("k7", "tuned", "")],
    "K8 (ms)": [("k8", "natural", ""), ("k8", "tuned", ""), ("k8", "tuned_alloc", "")],
    "K9 (ms)": [("k9", "natural", ""), ("k9", "tuned", ""), ("k9", "mt", "")],
    "K10 (ms)": [("k10", "natural", ""), ("k10", "tuned", "")],
    "K2 (ns/saut)": [("k2", "tuned", s) for s in ["16384", "65536", "262144", "524288", "2097152", "8388608", "16777216",
                                                   "33554432", "67108864", "268435456"]],
}
LABEL = lambda k: (k[1] + (" " + k[2] if k[2] and k[0] != "k2" else "") if k[0] != "k2" else
                   {"16384": "16K", "65536": "64K", "262144": "256K", "524288": "512K", "2097152": "2M", "8388608": "8M",
                    "16777216": "16M", "33554432": "32M", "67108864": "64M", "268435456": "256M"}[k[2]])


def cv(procs):
    xs = [statistics.median(p) for p in procs]
    return statistics.pstdev(xs) / statistics.mean(xs) if len(xs) > 1 else 0.0


def main():
    data, lat, rss, invalid, *_ = final_data()
    for title, keys in COLS.items():
        print(f"\n### {title}\n")
        print("| Langage | " + " | ".join(LABEL(k) for k in keys) + " |")
        print("|---|" + "---|" * len(keys))
        for l in ORDER:
            if l not in data:
                continue
            cells = []
            for k in keys:
                procs = data[l].get(k)
                if not procs:
                    cells.append("—")
                    continue
                t = point(procs)
                v = t / 4.2e6 * 1e9 if k[0] == "k2" else t * 1e3
                c = cv(procs)
                cells.append(f"{v:.3g}" + ("*" if c > 0.05 else ""))
            print(f"| {l} | " + " | ".join(cells) + " |")
    print("\n\\* coefficient de variation inter-processus > 5 %")
    print("\n### K8 natural : latences par requête (µs, médianes des répétitions)\n")
    print("| Langage | p50 | p90 | p99 | p99.9 | max | p99.9/p50 |")
    print("|---|---|---|---|---|---|---|")
    for l in ORDER:
        L = lat.get(l, {}).get(("k8", "natural", ""))
        if not L:
            continue
        m = [statistics.median([x[i] for x in L]) / 1e3 for i in range(5)]
        print(f"| {l} | " + " | ".join(f"{x:.3g}" for x in m) + f" | {m[3] / m[0]:.1f} |")


if __name__ == "__main__":
    main()
