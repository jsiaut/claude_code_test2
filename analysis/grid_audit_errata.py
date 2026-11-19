#!/usr/bin/env python3
"""Audit de la grille (v4, point 1 ; plan : docs/V4_PLAN.md, 2.3) : errata appliqués ensemble et sensibilité des cases
discutables.

Sur les données du classement publié (analyse globale de la v3 rejouée, mêmes tirages) :
* Avant : matrice publiée avant l'audit ; contrôle : reproduit P-E de results/php_check.json (le publié) ;
* Après : errata de l'audit (docs/GRID_AUDIT.md, section 4) ;
* une variante par case discutable (docs/GRID_AUDIT.md, section 3), appliquée à Après avec l'autre note possible, puis
  toutes ensemble.
La matrice est corrigée en mémoire (les règles v1 et v2 la lisent ; aucune de ces cases n'a de note propre à la v2).
Option --published : la matrice du dépôt porte déjà les errata ; Avant les retire alors en mémoire.
Sorties : results/grid_audit/errata.json, results/grid_audit/report_errata.md."""
import copy, json, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_v2 as v2  # noqa: E402
import audit3 as a3  # noqa: E402
import capabilities  # noqa: E402
from analyze_v2 import RANKED, ANNEX, ROOT, NAMES  # noqa: E402

# (langage, case) : (note de la matrice avant l'audit, note établie par la sonde)
ERRATA = {("haskell", "A3"): (0, 0.5)}

DISCUTABLE = [
    ("Rust D4 et F4 à ½ (crate libc du sysroot, rustc_private)", {("rust", "D4"): 0.5, ("rust", "F4"): 0.5}),
    ("Zig C2 à 1 (extern fn au nom d'une intrinsèque de LLVM)", {("zig", "C2"): 1}),
    ("F2 à ½ par appel système brut (Odin, C, C++, Go, Zig, FreePascal)",
     {(l, "F2"): 0.5 for l in ("odin", "c", "cpp", "go", "zig", "fpc")}),
    ("Nim E3 à 0 (clang, compilateur C du banc)", {("nim", "E3"): 0}),
    ("C B2 à 1 (obstack de la glibc)", {("c", "B2"): 1}),
    ("C et C++ F2 à ½ (trait d'allocateur OpenMP)", {("c", "F2"): 0.5, ("cpp", "F2"): 0.5}),
    ("B1 à ½ (C#, Java, Go, Lua : ramasse-miettes qu'on peut arrêter)",
     {(l, "B1"): 0.5 for l in ("csharp", "java", "go", "lua")}),
    ("Java E6 à ½ (sun.misc.Unsafe)", {("java", "E6"): 0.5}),
    ("Java F2 à ½ (-XX:+UseNUMA)", {("java", "F2"): 0.5}),
]


def set_notes(patch):
    for (l, c), v in patch.items():
        old = capabilities.MATRIX[l][c]
        capabilities.MATRIX[l][c] = (v, old[1]) if isinstance(old, tuple) else (v, "")


def summary(z):
    return {"ms0": z["ms0"], "exp21": z["exp21"], "order21": z["order21"], "rank90": z["rank90"],
            "tiers": [len(t) for t in z["tiers"]], "tiers_members": z["tiers"]}


def main():
    published = "--published" in sys.argv
    data, lat, *_ = v2.dataset_main(transfers=True)
    v2.align_lat(data, lat)
    c3 = json.load(open(os.path.join(ROOT, "results", "vectorization.json")))
    footprint = json.load(open(os.path.join(ROOT, "results", "footprint.json")))
    langs = [l for l in RANKED + list(ANNEX) if l in data]
    saved = copy.deepcopy(capabilities.MATRIX)
    out = {"errata": {f"{l} {c}": list(v) for (l, c), v in ERRATA.items()}, "scenarios": {}}
    t0 = time.time()
    set_notes({k: v[0] for k, v in ERRATA.items()})
    av = out["scenarios"]["Avant"] = summary(a3.run(data, lat, langs, footprint, c3))
    ref = json.load(open(os.path.join(ROOT, "results", "php_check.json")))["scenarios"]["P-E"]
    out["check_avant"] = max(max(abs(av["ms0"][l] - ref["ms0"][l]), abs(av["exp21"][l] - ref["exp21"][l])) for l in RANKED)
    print(f"Avant ({time.time() - t0:.0f} s) : écart maximal à P-E = {out['check_avant']:.2e}", flush=True)
    set_notes({k: v[1] for k, v in ERRATA.items()})
    ap = out["scenarios"]["Après"] = summary(a3.run(data, lat, langs, footprint, c3))
    if published:
        s3 = json.load(open(os.path.join(ROOT, "results", "summary_v3.json")))["results"]
        out["check_apres"] = max(abs(ap["ms0"][l] - s3[l]["MS"]) for l in RANKED)
        print(f"Après : écart maximal au score publié (summary_v3) = {out['check_apres']:.2e}", flush=True)
    print(f"Après ({time.time() - t0:.0f} s) : " + ", ".join(
        f"{NAMES[l]} {av['ms0'][l]:.2f} → {ap['ms0'][l]:.2f}" for l in RANKED if abs(ap['ms0'][l] - av['ms0'][l]) > 1e-9),
        flush=True)
    after = copy.deepcopy(capabilities.MATRIX)
    out["variantes"] = {}
    alln = {}
    for name, patch in DISCUTABLE:
        capabilities.MATRIX.clear(); capabilities.MATRIX.update(copy.deepcopy(after))
        set_notes(patch)
        alln.update(patch)
        z = summary(a3.run(data, lat, langs, footprint, c3))
        out["variantes"][name] = {"cases": [f"{l} {c}" for (l, c) in patch], "notes": list(patch.values()), **z}
        moved = [l for l in RANKED if abs(z["ms0"][l] - ap["ms0"][l]) > 1e-9]
        print(f"{name} ({time.time() - t0:.0f} s) : " + ", ".join(
            f"{NAMES[l]} {ap['ms0'][l]:.2f} → {z['ms0'][l]:.2f} ({ap['order21'].index(l) + 1}e → {z['order21'].index(l) + 1}e)"
            for l in moved), flush=True)
    capabilities.MATRIX.clear(); capabilities.MATRIX.update(copy.deepcopy(after))
    set_notes(alln)
    z = summary(a3.run(data, lat, langs, footprint, c3))
    out["variantes"]["Toutes ensemble"] = {"cases": [f"{l} {c}" for (l, c) in alln], "notes": list(alln.values()), **z}
    print(f"Toutes ensemble ({time.time() - t0:.0f} s) : ordre " + ", ".join(NAMES[l] for l in z["order21"]), flush=True)
    capabilities.MATRIX.clear(); capabilities.MATRIX.update(saved)
    os.makedirs(os.path.join(ROOT, "results", "grid_audit"), exist_ok=True)
    json.dump(out, open(os.path.join(ROOT, "results", "grid_audit", "errata.json"), "w"), indent=1, default=float)
    report(out)


def report(o):
    av, ap = o["scenarios"]["Avant"], o["scenarios"]["Après"]
    L = ["# Audit de la grille : errata et sensibilité des cases discutables", "",
         "Produit par `analysis/grid_audit_errata.py` (docs/V4_PLAN.md 2.3 ; docs/GRID_AUDIT.md, sections 3 et 4). "
         "Analyse globale de la v3 rejouée sur les données du classement publié, mêmes tirages.", "",
         f"Contrôle : le scénario Avant reproduit P-E de `results/php_check.json` (écart maximal {o['check_avant']:.1e}).", "",
         "## Avant et après les errata", "",
         "| Langage | Score avant | Score après | Écart | Place avant | Place après | Rang espéré avant | après |",
         "|---|---|---|---|---|---|---|---|"]
    for l in ap["order21"]:
        L.append(f"| {NAMES[l]} | {av['ms0'][l]:.2f} | {ap['ms0'][l]:.2f} | {ap['ms0'][l] - av['ms0'][l]:+.2f} | "
                 f"{av['order21'].index(l) + 1} | {ap['order21'].index(l) + 1} | {av['exp21'][l]:.2f} | {ap['exp21'][l]:.2f} |")
    L += ["", f"Étages : avant {av['tiers']}, après {ap['tiers']}.", "",
          "## Cases discutables : l'autre note, une à la fois (sur Après)", "",
          "| Variante | Langages touchés : score (place) | Étages |", "|---|---|---|"]
    for name, z in o["variantes"].items():
        moved = [l for l in RANKED if abs(z["ms0"][l] - ap["ms0"][l]) > 1e-9]
        txt = " ; ".join(f"{NAMES[l]} {ap['ms0'][l]:.2f} → {z['ms0'][l]:.2f} ({ap['order21'].index(l) + 1}e → "
                         f"{z['order21'].index(l) + 1}e)" for l in moved)
        others = [l for l in RANKED if l not in moved and z["order21"].index(l) != ap["order21"].index(l)]
        if others:
            txt += " ; places déplacées : " + ", ".join(f"{NAMES[l]} {ap['order21'].index(l) + 1}e → "
                                                        f"{z['order21'].index(l) + 1}e" for l in others)
        L.append(f"| {name} | {txt} | {z['tiers']} |")
    open(os.path.join(ROOT, "results", "grid_audit", "report_errata.md"), "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
