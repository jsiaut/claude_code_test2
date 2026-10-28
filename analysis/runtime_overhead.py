#!/usr/bin/env python3
"""Analyse descriptive (hors score) : travail caché du runtime.

Pour les noyaux mono-thread, le rapport (temps CPU utilisateur + système) / temps mural du processus
mesure le travail fait en parallèle par le runtime (compilation JIT, GC concurrent, threads
auxiliaires). Un langage « transparent » est proche de 1. On relève aussi le pic RSS et les défauts
de page mineurs par processus (rusage du pilote).
"""
import glob, json, os, statistics

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SINGLE = {("k1", "natural"), ("k4", "natural_unsorted"), ("k5", "natural"), ("k5", "tuned"), ("k7", "natural"),
          ("k8", "natural"), ("k9", "natural"), ("k6", "natural"), ("k1", "soa")}


def main():
    rows = {}
    for f in glob.glob(os.path.join(ROOT, "results", "raw", "*.jsonl")):
        for line in open(f):
            r = json.loads(line)
            if (r["kernel"], r["variant"]) not in SINGLE or r.get("returncode") != 0 or r["wall"] <= 0:
                continue
            d = rows.setdefault(r["lang"], {"cpu_ratio": [], "rss_mb": [], "minflt": []})
            d["cpu_ratio"].append((r["utime"] + r["stime"]) / r["wall"])
            d["rss_mb"].append(r["maxrss_kb"] / 1024)
            d["minflt"].append(r["minflt"])
    print("| Langage | (CPU utilisateur + système) / mural, noyaux mono-thread (médiane) | max | pic RSS médian (Mo) |")
    print("|---|---|---|---|")
    for l, d in sorted(rows.items(), key=lambda kv: statistics.median(kv[1]["cpu_ratio"])):
        print(f"| {l} | {statistics.median(d['cpu_ratio']):.2f} | {max(d['cpu_ratio']):.2f} | {statistics.median(d['rss_mb']):.0f} |")


if __name__ == "__main__":
    main()
