#!/usr/bin/env python3
"""Tableaux Markdown du rapport (README, sections 4 à 6), générés à partir des sorties de l'analyse pour
éviter toute recopie manuelle : results/summary.json, results/summary_noisy_old.json,
results/footprint_detail.json, results/vectorization.json, results/raw (rusage).
Sortie : results/report_tables.md."""
import glob, json, os, statistics, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from analyze import final_data, RANKED, ANNEX, E_MEASURES  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAMES = {"c": "C", "cpp": "C++", "csharp": "C#", "java": "Java", "zig": "Zig", "odin": "Odin", "julia": "Julia", "ada": "Ada",
         "fortran": "Fortran", "js": "JavaScript", "python": "Python", "haskell": "Haskell", "c3": "C3", "d": "D", "rust": "Rust",
         "chapel": "Chapel", "nim": "Nim", "mojo": "Mojo", "go": "Go", "ocaml": "OCaml", "lua": "Lua", "c_gcc": "C (gcc)",
         "fortran_flang": "Fortran (flang)", "luajit": "LuaJIT", "js_bun": "JavaScript (Bun)", "python_ft": "Python sans GIL"}
F = lambda x, d=1: "—" if x is None else f"{x:.{d}f}".replace(".", ",")


def load(name):
    p = os.path.join(ROOT, "results", name)
    return json.load(open(p)) if os.path.exists(p) else {}


def ranking(s):
    res = s["results"]
    return sorted([l for l in RANKED if res.get(l, {}).get("MS") is not None], key=lambda l: -res[l]["MS"])


def main():
    s, old = load("summary.json"), load("summary_noisy_old.json")
    res = s["results"]
    order = ranking(s)
    out = []
    # 1. classement
    out += ["### Classement", "",
            "| Rang | Langage | MS | C (rang) | E [IC 95 %] (rang) | D [IC 95 %] (rang) | Rang, poids tirés au hasard [5-95 %] "
            "| Rang, cellules 0,5 tirées [5-95 %] | Rang, un noyau retiré [min-max] |",
            "|---|---|---|---|---|---|---|---|---|"]
    for i, l in enumerate(order):
        r = res[l]
        out.append(f"| {i + 1} | {NAMES[l]} | **{F(r['MS'])}** | {F(r['C'])} ({r['rank_C']}) | {F(r['E'])} [{F(r['E_ci'][0])}–{F(r['E_ci'][1])}] "
                   f"({r['rank_E']}) | {F(r['D'])} [{F(r['D_ci'][0])}–{F(r['D_ci'][1])}] ({r['rank_D']}) | {r['rank_median']} "
                   f"[{r['rank_90'][0]}–{r['rank_90'][1]}] | [{r['rank_halves_90'][0]}–{r['rank_halves_90'][1]}] | "
                   f"[{r['rank_drop_kernel'][0]}–{r['rank_drop_kernel'][1]}] |")
    # 2. E par noyau
    ks = list(E_MEASURES)
    out += ["", "### Pilier E par noyau (t\\*/t, 1 = meilleur langage classé ; moyenne géométrique des sous-mesures)", "",
            "| Langage | " + " | ".join(k.upper() for k in ks) + " | E |", "|---|" + "---|" * (len(ks) + 1)]
    for l in order + [a for a in ANNEX if res.get(a, {}).get("E") is not None]:
        ek = res[l].get("E_kernels", {})
        out.append(f"| {NAMES[l]} | " + " | ".join(F(ek.get(k), 2) for k in ks) + f" | {F(res[l].get('E'))} |")
    # 3. D
    out += ["", "### Pilier D (défaut et transparence)", "",
            "| Langage | D1 code naturel | D2 coût de structure | D3 prévisibilité K8 | D4 hiérarchie visible K2 | D |", "|---|---|---|---|---|---|"]
    for l in order:
        dp = res[l]["D_parts"]
        out.append(f"| {NAMES[l]} | {F(dp['D1'], 2)} | {F(dp['D2'], 2)} | {F(dp['D3'], 2)} | {F(dp['D4'], 2)} | {F(res[l]['D'])} |")
    # 4. empreinte
    fp = load("footprint_detail.json")
    out += ["", "### Empreinte de la collection naturelle K1 (octets par particule de 64 o utiles)", "",
            "| Langage | Octets/particule | Mesure | RSS (contrôle) | D2a = min(1, 64/x) |", "|---|---|---|---|---|"]
    for l, d in sorted(fp.items(), key=lambda kv: (kv[1]["bytes_per_particle"], kv[0])):
        kind = "octets vivants (runtime)" if d["kind"] == "live" else "RSS"
        note = f" (mesure brute {F(d['measured'], 1)})" if d.get("note") else ""
        out.append(f"| {NAMES.get(l, l)} | {F(d['bytes_per_particle'], 1)}{note} | {kind} | {F(d['rss_bytes_per_particle'], 1)} | {F(d['D2a'], 2)} |")
    # 5. vectorisation
    vec = load("vectorization.json")
    out += ["", "### Vectorisation automatique mesurée (C3) : boucle chaude de K4 et K9 `natural`", "",
            "| Langage | K4 (somme conditionnelle d'octets) | K9 (stencil f64) | C3 |", "|---|---|---|---|"]
    for l in RANKED + [a for a in ANNEX if a in vec]:
        cells = []
        for k in ("k4", "k9"):
            p = os.path.join(ROOT, "results", "vectorization", f"{l}_{k}.txt")
            if not os.path.exists(p):
                cells.append("—")
                continue
            first = open(p).readline()
            share = first.split("%")[0]
            v = "'vectorized': True" in first
            w = first.split("'width': '")[1].split("'")[0] if "'width': '" in first else "-"
            cells.append(f"{'vectorisée (' + w + ')' if v else 'scalaire'}, {share.replace('.', ',')} % des échantillons")
        out.append(f"| {NAMES[l]} | {cells[0]} | {cells[1]} | {F(vec.get(l), 1)} |")
    # 6. travail caché du runtime
    rows = {}
    single = {("k1", "natural"), ("k4", "natural_unsorted"), ("k5", "natural"), ("k5", "tuned"), ("k7", "natural"),
              ("k8", "natural"), ("k9", "natural"), ("k6", "natural"), ("k1", "soa")}
    for f in glob.glob(os.path.join(ROOT, "results", "raw", "*.jsonl")):
        for line in open(f):
            r = json.loads(line)
            if (r["kernel"], r["variant"]) in single and r.get("returncode") == 0 and r["wall"] > 0:
                rows.setdefault(r["lang"], []).append((r["utime"] + r["stime"]) / r["wall"])
    out += ["", "### Travail caché du runtime : (CPU utilisateur + système) / temps mural, noyaux mono-thread", "",
            "| Langage | Médiane | Maximum |", "|---|---|---|"]
    for l, v in sorted(rows.items(), key=lambda kv: statistics.median(kv[1])):
        out.append(f"| {NAMES.get(l, l)} | {F(statistics.median(v), 2)} | {F(max(v), 2)} |")
    # 7. K8 latences
    data, lat, *_ = final_data()
    out += ["", "### K8 natural : latence par requête (µs ; médiane des répétitions)", "",
            "| Langage | p50 | p99 | p99,9 | max | p99,9 / p50 |", "|---|---|---|---|---|---|"]
    tab = []
    for l in RANKED + list(ANNEX):
        L = lat.get(l, {}).get(("k8", "natural", ""))
        if L:
            m = [statistics.median([x[i] for x in L]) / 1e3 for i in range(5)]
            tab.append((m[3] / m[0], l, m))
    for ratio, l, m in sorted(tab):
        out.append(f"| {NAMES[l]} | {F(m[0], 2)} | {F(m[2], 2)} | {F(m[3], 2)} | {F(m[4], 1)} | {F(ratio, 1)} |")
    # 8. sensibilité aux données remesurées
    if old:
        oo = ranking(old)
        out += ["", "### Sensibilité : K5 et K10 `tuned` d'avant le redémarrage (2-3 processus) au lieu de la remesure (9 processus)", "",
                "| Langage | Rang (remesure) | MS | Rang (données d'avant) | MS |", "|---|---|---|---|---|"]
        for i, l in enumerate(order):
            out.append(f"| {NAMES[l]} | {i + 1} | {F(res[l]['MS'])} | {oo.index(l) + 1} | {F(old['results'][l]['MS'])} |")
    open(os.path.join(ROOT, "results", "report_tables.md"), "w").write("\n".join(out) + "\n")
    print("results/report_tables.md écrit")


if __name__ == "__main__":
    main()
