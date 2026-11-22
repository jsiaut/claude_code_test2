#!/usr/bin/env python3
"""v4, point 5 : le coût d'accès au plafond (docs/V4_COST.md, sections 3 à 5, fixées avant le comptage ; règles de
lecture et écarts datés : sections 8 et 10).

Entrées : results/cost/counts.json (tools/cost/count.py : lignes de code L, lexèmes T, lignes sans vérification U et
lignes propres à une architecture X de chaque forme relevée), tools/cost/needed.py (formes d'accès, candidates à 10 %,
références naturelles, d'après la campagne du point 4), la campagne du point 4 (results/converge/raw : temps des
cellules du plafond, b3 ; analysis/converge_v4.py) et results/cost/compile.txt (compilations croisées, s'il existe).

Par cellule (3.1 à 3.5) : forme d'accès (la plus rapide ; K1 et K3 : la plus rapide des formes publiées), référence
naturelle, s = max(0 ; 1 − N/L), part sans vérification absolue (1 dans les langages sans vérification dans leur mode
publié) et marginale, p = 1 si la forme porte une ligne propre à une architecture. Cellule atteinte (section 4) :
rapport frontière / langage ≥ 0,9 (estimation ponctuelle de la forme retenue au point 4, comme son tableau d'écarts ;
frontière : le plus rapide des 25 langages ; K3 : min(1 ; b3 / t), « avec R4 »). Indice d'accès : moyenne sur les 12
cellules de 1 − (s + u + p) / 3 pour les cellules atteintes, 0 pour les autres.
Calculs (section 5) :
1. descriptif par langage et par cellule ; compilations croisées et prévision statique ;
2. agrégats par langage ;
3. corrélations de rang (Spearman) entre les quantités de 2 et les catégories C et E de la grille (règle v2), le
   pilier contrôle et le plafond (« Convergent, avec R4 », au centre) ;
4. scénario « Accès » : le calcul « Convergent, avec R4 » du point 4 (analysis/converge_v4.py, même graine, mêmes
   tirages), chaque capacité des catégories C et E valant l'indice d'accès du langage, sans bruit de jugement ;
5. sensibilités : (a) part marginale ; (b) sans part sans vérification ; (c) seuil 0,8 ; (d) forme d'accès la plus
   courte à 10 % ou moins (cellule atteinte : comme au calcul principal) ; (e) grille entière remplacée par l'indice ;
   (f) lexèmes au lieu des lignes (3.3).
Le calcul « Convergent, avec R4 » est refait ici et comparé à results/converge/analysis.json (contrôle).
Sorties : results/cost/cost.json, results/report_cost.md. Variables : BOOT (2000), UA (20000). Option --report :
relit results/cost/compile.txt et régénère le rapport sans refaire les calculs."""
import json, math, os, statistics, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools", "cost"))
import analyze_v2 as v2  # noqa: E402
import confrontation as cf  # noqa: E402
import converge_v4 as cv  # noqa: E402
import sizes_v4 as S  # noqa: E402
from analyze_v2 import RANKED, NAMES, CATEGORIES  # noqa: E402
from analyze_v3 import E_V2  # noqa: E402
import needed as ND  # noqa: E402
import lex  # noqa: E402

COUNTS = os.path.join(ROOT, "results", "cost", "counts.json")
COMPILE = os.path.join(ROOT, "results", "cost", "compile.txt")
OUT = os.path.join(ROOT, "results", "cost", "cost.json")
REPORT = os.path.join(ROOT, "results", "report_cost.md")
CELLS = list(ND.CELLS)
THRESH, THRESH_C = 0.9, 0.8
R4 = "Convergent, avec R4"
SENS = {"a": "part marginale", "b": "sans part sans vérification", "c": "seuil 0,8",
        "d": "forme la plus courte à 10 %", "e": "grille entière remplacée", "f": "lexèmes"}
QUANT = {"gm_LN": "L/N (moyenne géométrique)", "added": "lignes ajoutées", "u_abs": "part sans vérification (absolue)",
         "u_marg": "part sans vérification (marginale)", "arch": "part propre à une architecture",
         "nonport": "cellules non portables", "A": "indice d'accès"}


def gmean(xs):
    xs = [x for x in xs if x > 0]
    return math.exp(sum(math.log(x) for x in xs) / len(xs)) if xs else float("nan")


# ------------------------------------------------------------------ cellules atteintes
def ratios(data, fc, langs, b3):
    """{langage: {cellule: rapport frontière / langage}} et les temps (estimation ponctuelle)."""
    ret = cv.retained(data, fc, langs)
    t = {l: {} for l in langs}
    for l in langs:
        for c in CELLS:
            if c in ("K1", "K3"):
                k, gi = ND.CELLS[c]
                ts = [cv.gm(data["pub"][l][key]) for key in E_V2[k][gi] if data["pub"].get(l, {}).get(key)]
                if ts:
                    t[l][c] = min(ts)
            elif c in ret.get(l, {}):
                t[l][c] = ret[l][c]["retained"]
    out = {l: {} for l in langs}
    for c in CELLS:
        have = [l for l in langs if c in t[l]]
        front = min(t[l][c] for l in have) if have else None
        for l in langs:
            if c not in t[l]:
                out[l][c] = 0.0
            elif c == "K3":
                out[l][c] = min(1.0, b3 / t[l][c])
            else:
                out[l][c] = front / t[l][c]
    return out, t


# ------------------------------------------------------------------ quantités
def access_forms(cells, cnt, shortest=False):
    """{langage: {cellule: (forme d'accès, référence naturelle)}}."""
    out = {}
    for l, row in cells.items():
        out[l] = {}
        for c, x in row.items():
            if shortest:
                times = {}
                for k, b, tm in x["forms"]:
                    times[k] = min(tm, times.get(k, tm))
                key = min(x["near"], key=lambda k: (cnt[l]["forms"][k]["L"], times.get(k, float("inf"))))
            else:
                key = x["best"]
            out[l][c] = (key, ND.k3_ref(key) if c == "K3" else ND.NATURAL[c])
    return out


def cell_q(cnt, lang, key, nat, measure="L"):
    F = cnt[lang]["forms"]
    a, n = F[key], F[nat]
    L, N = a[measure], n[measure]
    um = a["U"] / a["L"] if a["L"] else 0.0
    return {"form": key, "nat": nat, "L": a["L"], "N": n["L"], "T": a["T"], "NT": n["T"], "added": a["L"] - n["L"],
            "s": max(0.0, 1.0 - N / L) if L > 0 else 0.0, "u_abs": 1.0 if cnt[lang]["no_check_mode"] else um,
            "u_marg": um, "U": a["U"], "X": a["X"], "p": 1 if a["X"] > 0 else 0}


def access_index(q, ratio, langs, thresh=THRESH, u="u_abs", with_u=True):
    A = {}
    for l in langs:
        tot = 0.0
        for c in CELLS:
            if c not in q[l] or ratio[l][c] < thresh:
                continue
            x = q[l][c]
            cost = (x["s"] + x[u] + x["p"]) / 3 if with_u else (x["s"] + x["p"]) / 2
            tot += 1 - cost
        A[l] = tot / len(CELLS)
    return A


def aggregates(q, A, ratio, langs):
    out = {}
    for l in langs:
        cs = [q[l][c] for c in CELLS if c in q[l]]
        sl = sum(x["L"] for x in cs)
        out[l] = {"gm_LN": gmean([x["L"] / x["N"] for x in cs if x["N"] > 0]),
                  "added": sum(x["added"] for x in cs),
                  "u_abs": sum(x["u_abs"] * x["L"] for x in cs) / sl if sl else 0.0,
                  "u_marg": sum(x["U"] for x in cs) / sl if sl else 0.0,
                  "arch": sum(x["X"] for x in cs) / sl if sl else 0.0,
                  "nonport": sum(x["p"] for x in cs),
                  "reached": sum(1 for c in CELLS if ratio[l][c] >= THRESH),
                  "A": A[l]}
    return out


# ------------------------------------------------------------------ corrélations
def avg_ranks(v):
    order = sorted(range(len(v)), key=lambda i: v[i])
    r, i = [0.0] * len(v), 0
    while i < len(v):
        j = i
        while j + 1 < len(v) and v[order[j + 1]] == v[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def spearman(x, y):
    rx, ry = avg_ranks(x), avg_ranks(y)
    mx, my = statistics.fmean(rx), statistics.fmean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return num / den if den else float("nan")


def grid_scores(c3, langs):
    cells = v2.c_cells("v2", c3)
    catw0 = {cat: w for cat, (w, _) in CATEGORIES.items()}
    ctrl = v2.c_score(cells, catw0)
    out = {}
    for l in langs:
        row = {"control": ctrl[l]}
        for cat in ("C", "E"):
            caps = [c for c in CATEGORIES[cat][1] if c in cells[l]]
            row[cat] = 100 * statistics.fmean(cells[l][c] for c in caps)
        out[l] = row
    return out


# ------------------------------------------------------------------ scénarios
def run_scenario(env, A=None, whole=False):
    """« Convergent, avec R4 » du point 4 ; avec A, chaque capacité des catégories C et E (toutes si whole) vaut
    l'indice d'accès du langage. Les tirages de bruit des autres capacités ne changent pas (même générateur, même
    ordre : la fonction d'origine est appelée telle quelle, puis ses valeurs sont remplacées)."""
    data, bypass, lat, fc, langs, footprint, c3, eb, b3, keys = env
    orig = cf.c_cells
    if A is not None:
        def c_cells_access(rule, c3_, rng=None, noise=0.0):
            cells = orig(rule, c3_, rng=rng, noise=noise)
            for l, cs in cells.items():
                for cap in cs:
                    if whole or cap[0] in ("C", "E"):
                        cs[cap] = A[l]
            return cells
        cf.c_cells = c_cells_access
    try:
        return cv.run_calc(R4, data, bypass, lat, fc, langs, footprint, c3, eb, b3, keys)
    finally:
        cf.c_cells = orig


# ------------------------------------------------------------------ compilation
def read_compile(cnt):
    if not os.path.exists(COMPILE):
        return None
    rows = []
    for line in open(COMPILE, encoding="utf-8"):
        if line.startswith("#") or not line.strip():
            continue
        f = (line.rstrip("\n").split("\t") + [""] * 4)[:4]
        rows.append({"lang": f[0], "target": f[1], "result": f[2], "detail": f[3]})
    by = {}
    for r in rows:
        by.setdefault(r["lang"], {})[r["target"]] = r
    out = {}
    for l, tg in by.items():
        arch = any(v["arch_lines"] for v in cnt[l]["files"].values())
        ctrl = tg.get("x86_64", {}).get("result")
        row = {"control": ctrl, "predicted_off_x86": "refus" if arch else "compile", "targets": tg}
        if ctrl == "compile":
            row["agree"] = {t: (tg[t]["result"] == row["predicted_off_x86"]) for t in ("aarch64", "riscv64") if t in tg}
        out[l] = row
    return out


def julia_generator(cnt, q):
    """Q1 tuned_v de Julia : part de lignes ajoutées avec le générateur de l'IR à la place de l'IR (section 8)."""
    src = open(os.path.join(ROOT, "bench", "julia_cv", "ms.jl"), encoding="utf-8").read()
    jl = lex.strip("julia", src)
    ir = sum(1 for i in range(444, 765) if lex.is_code(jl[i]))  # Q1_IR, lignes 445 à 765
    gtext = open(os.path.join(ROOT, "tools", "converge", "gen_julia_ir.py"), encoding="utf-8").read()
    gen = sum(1 for s in lex.strip("python", gtext) if lex.is_code(s))
    out = {"ir_lines": ir, "generator_lines": gen}
    for c in ("Q1", "Q1 mt"):
        x = q["julia"].get(c)
        if x and "q1" in x["form"] and "tuned_v" in x["form"]:
            L2 = x["L"] - ir + gen
            out[c] = {"form": x["form"], "L": x["L"], "N": x["N"], "s": x["s"], "L_generator": L2,
                      "s_generator": max(0.0, 1 - x["N"] / L2)}
    return out


# ------------------------------------------------------------------ principal
def main():
    v2.ADDED.clear()
    data, bypass, lat, failures, steal, models = cv.load()
    c3 = json.load(open(os.path.join(ROOT, "results", "vectorization.json")))
    footprint = json.load(open(os.path.join(ROOT, "results", "footprint.json")))
    hw = cv.hw_numbers()
    eb = S.ebounds(hw, 1)
    eb[("k5", 0)] = S.ebounds(hw, 0)[("k5", 0)]
    b3, _ = cv.b3_value()
    langs = list(RANKED)
    fc = cv.forms_cells(langs)
    keys = S.campaign_keys({"pub": data["pub"]})
    env = (data, bypass, lat, fc, langs, footprint, c3, eb, b3, keys)

    cnt = json.load(open(COUNTS))
    cells = ND.cells()
    ratio, tcell = ratios(data, fc, langs, b3)
    acc, acc_d = access_forms(cells, cnt), access_forms(cells, cnt, shortest=True)

    def quantities(af, measure="L"):
        return {l: {c: cell_q(cnt, l, *af[l][c], measure=measure) for c in af[l]} for l in langs}

    q, qd, qt = quantities(acc), quantities(acc_d), quantities(acc, "T")
    A = access_index(q, ratio, langs)
    idx = {"a": access_index(q, ratio, langs, u="u_marg"), "b": access_index(q, ratio, langs, with_u=False),
           "c": access_index(q, ratio, langs, thresh=THRESH_C), "d": access_index(qd, ratio, langs), "e": A,
           "f": access_index(qt, ratio, langs)}
    agg = aggregates(q, A, ratio, langs)

    base = run_scenario(env)
    prev = json.load(open(cv.OUT))["results"][R4]
    control = {"same_order": prev["order"] == base["order"],
               "max_exp_diff": max(abs(prev["exp"][l] - base["exp"][l]) for l in langs),
               "max_ms0_diff": max(abs(prev["ms0"][l] - base["ms0"][l]) for l in langs)}
    grid = grid_scores(c3, langs)
    targets = {"C": {l: grid[l]["C"] for l in langs}, "E": {l: grid[l]["E"] for l in langs},
               "control": {l: grid[l]["control"] for l in langs}, "ceiling": {l: base["E"][l] for l in langs}}
    corr = {k: {t: spearman([agg[l][k] for l in langs], [targets[t][l] for l in langs]) for t in targets}
            for k in QUANT}
    access = run_scenario(env, A)
    sens = {k: run_scenario(env, idx[k], whole=(k == "e")) for k in SENS}
    moved = {"Accès": S.moved(base["order"], access["order"], langs)}
    moved.update({k: S.moved(base["order"], sens[k]["order"], langs) for k in SENS})
    moved_vs_access = {k: S.moved(access["order"], sens[k]["order"], langs) for k in SENS}

    out = {"cells": CELLS, "threshold": THRESH, "b3": b3, "ratio": ratio, "time": tcell,
           "access": {l: {c: list(acc[l][c]) for c in acc[l]} for l in langs},
           "shortest": {l: {c: list(acc_d[l][c]) for c in acc_d[l]} for l in langs},
           "q": q, "q_shortest": qd, "q_tokens": qt, "index": A, "index_sens": idx, "aggregates": agg,
           "grid": grid, "corr": corr, "control": control,
           "results": {R4: base, "Accès": access, **{f"({k})": sens[k] for k in SENS}},
           "moved_vs_R4": moved, "moved_vs_access": moved_vs_access,
           "compile": read_compile(cnt), "julia_generator": julia_generator(cnt, q),
           "published": json.load(open(cv.OUT))["published"]}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, "w"), indent=1, ensure_ascii=False, default=float)
    report(out)


# ------------------------------------------------------------------ rapport
def fr(x, d=2):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "–"
    return f"{x:.{d}f}".replace(".", ",").replace("-", "−")


def short(key):
    k, v, p = key.split("|")
    return v + (f" {p}" if p and p != "energy" else "")


def report(o):
    langs = list(RANKED)
    R = o["results"]
    L = ["# v4, point 5 : le coût d'accès au plafond — résultats", "",
         "*Plan : `docs/V4_COST.md` (sections 3 à 5, fixées avant le comptage ; règles de lecture et écarts datés : "
         "sections 8 et 10). Généré par `analysis/cost_v4.py` à partir de `results/cost/counts.json` "
         "(`tools/cost/count.py`, relevé `tools/cost/regions.py`), de la campagne du point 4 (machine 33) et de "
         "`results/cost/compile.txt`. Le classement de tête du README ne change pas au point 5.*", "",
         f"Contrôle : le calcul « {R4} » refait ici est identique à celui du point 4 "
         f"(même ordre : {'oui' if o['control']['same_order'] else 'non'} ; écart maximal des rangs espérés "
         f"{o['control']['max_exp_diff']:.2e}, des scores au centre {o['control']['max_ms0_diff']:.2e}).", "",
         "## Calcul 2 : par langage", "",
         "L/N : moyenne géométrique sur les 12 cellules du rapport des lignes de la forme d'accès à celles du code "
         "naturel ; parts pondérées par les lignes ; atteintes : cellules à 0,9 ou plus de la frontière.", "",
         "| Langage | L/N | Lignes ajoutées | Sans vérif. (abs.) | Sans vérif. (marg.) | Archi. | Non portables "
         "| Atteintes | Indice d'accès |", "|---|---|---|---|---|---|---|---|---|"]
    for l in sorted(langs, key=lambda l: -o["aggregates"][l]["A"]):
        a = o["aggregates"][l]
        L.append(f"| {NAMES[l]} | {fr(a['gm_LN'])} | {a['added']} | {fr(a['u_abs'])} | {fr(a['u_marg'])} | "
                 f"{fr(a['arch'])} | {a['nonport']} | {a['reached']} | {fr(a['A'], 3)} |")
    L += ["", "## Calcul 3 : corrélations de rang (Spearman, 25 langages)", "",
          "| Quantité | Catégorie C | Catégorie E | Pilier contrôle | Plafond (avec R4) |", "|---|---|---|---|---|"]
    for k, name in QUANT.items():
        c = o["corr"][k]
        L.append(f"| {name} | {fr(c['C'])} | {fr(c['E'])} | {fr(c['control'])} | {fr(c['ceiling'])} |")
    L += ["", "## Calculs 4 et 5 : scénario « Accès » et sensibilités (à côté du classement)", "",
          f"Places ; « {R4} » : le calcul du point 4 ; « Accès » : chaque capacité des catégories C et E vaut "
          "l'indice d'accès ; (a) à (f) : sensibilités (section 5 du plan ; (f) : 3.3).", "",
          "| Langage | Publié | " + R4 + " | Accès | " + " | ".join(f"({k})" for k in SENS) + " | Indice |",
          "|---|---|---|---|" + "---|" * len(SENS) + "---|"]
    pub = o["published"]["order"]
    for l in R["Accès"]["order"]:
        L.append(f"| {NAMES[l]} | {pub.index(l) + 1} | {R[R4]['order'].index(l) + 1} | "
                 f"{R['Accès']['order'].index(l) + 1} | "
                 + " | ".join(str(R[f'({k})']['order'].index(l) + 1) for k in SENS) + f" | {fr(o['index'][l], 3)} |")
    L += ["", "Rangs espérés, rang plausible (90 %), score au centre :", "",
          f"| Langage | {R4} : rang espéré | plausible | score | Accès : rang espéré | plausible | score |",
          "|---|---|---|---|---|---|---|"]
    for l in R["Accès"]["order"]:
        b, a = R[R4], R["Accès"]
        L.append(f"| {NAMES[l]} | {fr(b['exp'][l])} | {b['rank90'][l][0]}–{b['rank90'][l][1]} | {fr(b['ms0'][l], 1)} | "
                 f"{fr(a['exp'][l])} | {a['rank90'][l][0]}–{a['rank90'][l][1]} | {fr(a['ms0'][l], 1)} |")
    L += ["", "Plus de deux places par rapport à « " + R4 + " » :", ""]
    for name, mv in o["moved_vs_R4"].items():
        lab = name if name == "Accès" else f"({name}) {SENS[name]}"
        L.append(f"* {lab} : " + (", ".join(f"{NAMES[l]} {a} → {b}" for l, (a, b) in sorted(mv.items(),
                                                                                         key=lambda x: x[1][1]))
                                  or "aucun"))
    L += ["", "Sensibilités, plus de deux places par rapport à « Accès » :", ""]
    for k, mv in o["moved_vs_access"].items():
        L.append(f"* ({k}) {SENS[k]} : " + (", ".join(f"{NAMES[l]} {a} → {b}" for l, (a, b) in
                                                     sorted(mv.items(), key=lambda x: x[1][1])) or "aucun"))
    L += ["", "Étages indicatifs (règle v3 sans sa condition de réplication) :", ""]
    for name in (R4, "Accès"):
        L.append(f"* {name} : " + " | ".join(", ".join(NAMES[l] for l in t) for t in R[name]["tiers"]))
    comp = o.get("compile")
    L += ["", "## Compilation pour aarch64 et riscv64 (3.5)", ""]
    if comp is None:
        L.append("*Pas de `results/cost/compile.txt`.*")
    else:
        L += ["Prévision : le fichier compile hors x86 si et seulement si l'examen statique n'y trouve aucune ligne "
              "propre à une architecture. Une cible n'est interprétée que si la compilation de contrôle (x86_64, "
              "même outil) passe.", "",
              "| Langage | Contrôle x86_64 | aarch64 | riscv64 | Prévision | Accord |", "|---|---|---|---|---|---|"]
        for l in langs:
            if l not in comp:
                continue
            r = comp[l]
            tg = r["targets"]
            agree = r.get("agree")
            L.append(f"| {NAMES[l]} | {r['control']} | {tg.get('aarch64', {}).get('result', '–')} | "
                     f"{tg.get('riscv64', {}).get('result', '–')} | {r['predicted_off_x86']} | "
                     + ("–" if agree is None else ", ".join(f"{t} {'oui' if v else 'NON'}" for t, v in agree.items()))
                     + " |")
        L += ["", "Premières erreurs :", ""]
        for l in langs:
            for t, x in sorted(comp.get(l, {}).get("targets", {}).items()):
                if x["result"] != "compile" and x["detail"]:
                    L.append(f"* {NAMES[l]}, {t} : `{x['detail'][:150]}`")
    jg = o["julia_generator"]
    L += ["", "## Julia, Q1 `tuned_v` : IR écrit par un générateur (section 8)", "",
          f"IR dans la source : {jg['ir_lines']} lignes de code ; générateur (`tools/converge/gen_julia_ir.py`) : "
          f"{jg['generator_lines']}."]
    for c in ("Q1", "Q1 mt"):
        if c in jg:
            x = jg[c]
            L.append(f"* {c} (`{short(x['form'])}`) : L = {x['L']}, N = {x['N']}, s = {fr(x['s'])} ; avec le "
                     f"générateur à la place de l'IR, L = {x['L_generator']}, s = {fr(x['s_generator'])}.")
    L += ["", "## Calcul 1 : par langage et par cellule", "",
          "Forme d'accès (calcul principal), L et N (lignes de code de la forme et de la référence naturelle), "
          "s, parts sans vérification (absolue ; marginale), lignes propres à une architecture (X), rapport "
          "frontière / langage (« atteinte » à 0,9 ou plus).", ""]
    for l in langs:
        L += [f"### {NAMES[l]}", "", "| Cellule | Forme d'accès | L | N | L − N | s | Sans vérif. | X | Rapport |",
              "|---|---|---|---|---|---|---|---|---|"]
        for c in CELLS:
            x = o["q"][l].get(c)
            if not x:
                L.append(f"| {c} | – | | | | | | | {fr(o['ratio'][l][c])} |")
                continue
            L.append(f"| {c} | `{short(x['form'])}` | {x['L']} | {x['N']} | {x['added']} | {fr(x['s'])} | "
                     f"{fr(x['u_abs'])} ; {fr(x['u_marg'])} | {x['X']} | {fr(o['ratio'][l][c])} |")
        L.append("")
    open(REPORT, "w", encoding="utf-8").write("\n".join(L) + "\n")


def report_only():
    """--report : relit results/cost/compile.txt et régénère le rapport à partir de results/cost/cost.json."""
    o = json.load(open(OUT))
    o["compile"] = read_compile(json.load(open(COUNTS)))
    json.dump(o, open(OUT, "w"), indent=1, ensure_ascii=False, default=float)
    report(o)


if __name__ == "__main__":
    report_only() if "--report" in sys.argv[1:] else main()
