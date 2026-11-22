#!/usr/bin/env python3
"""v4, point 6 : analyse de la piste ouverte (docs/V4_OPEN.md, section 7, fixée avant les mesures ; écart 7 de la
section 10).

Base : « Convergent, avec R4 » du point 4 (analysis/converge_v4.py : données de la machine 33, même graine, 20 000
variantes, mêmes poids), refait ici à l'identique (contrôle, comme au point 5).
Report (7) : une forme op_* mesurée sur la machine 34 (results/open/raw, tools/open/campaign.py) entre dans l'ensemble
« meilleur de » de sa cellule (results/open/forms.json), avec les temps (estimation centrale et tirages) de la forme
d'accès de la cellule dans les données du point 4, multipliés par r : la médiane sur les trois passes du rapport
(médiane de la forme op_*) / (médiane de la forme d'accès dans la construction op). Écart 7 : si le témoin
w = médiane sur les passes de (forme d'accès dans op) / (forme d'accès dans cv) s'écarte de 1 de plus de 0,10, le
dénominateur est la forme d'accès dans cv ; les deux r sont rapportés. K3 : temps relevés à b3 (R4). La frontière de
chaque cellule est recalculée.
Grille ouverte : la note ouverte de chaque case comblée (results/open/grid_open.json) remplace la note de la règle
quand elle est plus haute ; son bruit de jugement (même probabilité, même tirage qu'une note publiée) est tiré par le
générateur de la variante après les autres cases, pour que leurs tirages ne changent pas.
Calculs : 1. Ouverte (plafond et grille ouverts) ; 2. Plafond ouvert seul ; 3. Grille ouverte seule ;
4. Bibliothèques nommées (formes et cases des seules bibliothèques nommées par le dossier, 3.3 c) ; 5. Cases comblées à
½ (sensibilité de 1 : chaque case comblée vaut ½) ; 6. Report par le témoin C (sensibilité de 1 : r rapporté à la forme
de C de la cellule sur les deux hôtes au lieu de la forme d'accès du langage) ; 7. Coût d'accès (information : lignes
des formes op_* par l'outil et les règles de lecture du point 5, results/open/counts_op.json, rapportées à celles du
code naturel, à côté de la forme d'accès standard).
Pour chaque calcul : scores, rangs espérés, rang plausible (90 %), étages indicatifs, langages qui bougent de plus de
deux places par rapport à « Convergent, avec R4 » ; par cellule, la forme retenue et son rapport à la forme d'accès ;
par langage, les cases changées. Sorties : results/open/analysis.json, results/report_open.md."""
import glob, json, math, os, re, sys
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools", "cost"))
import analyze_v2 as v2  # noqa: E402
import analyze_v3 as v3  # noqa: E402
import confrontation as cf  # noqa: E402
import converge_v4 as cv  # noqa: E402
import sizes_v4 as S  # noqa: E402
from analyze_v2 import RANKED, NAMES  # noqa: E402
import needed as ND  # noqa: E402

OPEN = os.path.join(ROOT, "results", "open")
RAW = os.path.join(OPEN, "raw")
FORMS = os.path.join(OPEN, "forms.json")
GRID = os.path.join(OPEN, "grid_open.json")
COUNTS_OP = os.path.join(OPEN, "counts_op.json")
COUNTS = os.path.join(ROOT, "results", "cost", "counts.json")
OUT = os.path.join(OPEN, "analysis.json")
REPORT = os.path.join(ROOT, "results", "report_open.md")
R4 = "Convergent, avec R4"
CALCS = ["Ouverte", "Plafond ouvert seul", "Grille ouverte seule", "Bibliothèques nommées", "Cases comblées à ½",
         "Report par le témoin C"]
WITNESS_TOL = 0.10  # écart 7


def tkey(s):
    f = s.split("|")
    return (f[0], f[1], f[2])


# ------------------------------------------------------------------ mesures de la machine 34
def load_open():
    """{(construction, langage, clé): {passe: médiane}} des processus valides, et les processus écartés."""
    med, failures, models = defaultdict(dict), [], defaultdict(int)
    for f in sorted(glob.glob(os.path.join(RAW, "*.jsonl"))):
        for line in open(f):
            r = json.loads(line)
            models[r.get("cpu_model", "?")] += 1
            key = "|".join((r["kernel"], r["variant"], r["param"]))
            ok = (not r.get("failed_calibration") and r.get("returncode") == 0 and not r.get("oom")
                  and not r.get("timeout") and r.get("n", 0) > 0 and r.get("oks") == ["True"])
            if not ok:
                fc = r.get("failed_calibration") or {}
                failures.append({"lang": r["lang"], "build": r["build"], "key": key, "pass": r.get("pass"),
                                 "returncode": r.get("returncode", fc.get("returncode")), "oks": r.get("oks"),
                                 "oom": bool(r.get("oom") or fc.get("oom")),
                                 "stderr": (r.get("stderr") or fc.get("stderr") or "")[-300:]})
                continue
            med[(r["build"], r["lang"], key)][r["pass"]] = r["median"]
    return med, failures, dict(models)


def pass_ratios(num, den):
    """Médiane sur les passes communes du rapport num / den (None sans passe commune)."""
    ps = sorted(set(num) & set(den))
    return float(np.median([num[p] / den[p] for p in ps])) if ps else None, len(ps)


def transfers(forms, med):
    """Par forme : r (plan), r par la construction cv, témoin w, r retenu (écart 7), et le rapport au témoin C par
    passe (calcul 6)."""
    out = []
    for f in forms["forms"]:
        l, key, acc, cell = f["lang"], f["key"], f["access"], f["cell"]
        op = med.get(("op", l, key), {})
        a_op = med.get(("op", l, acc), {})
        a_cv = med.get(("cv", l, acc), {})
        cw = forms["c_witness"][cell]
        c34 = med.get((cw["build"], "c", cw["key"]), {})
        r_op, n_op = pass_ratios(op, a_op)
        r_cv, n_cv = pass_ratios(op, a_cv)
        w, n_w = pass_ratios(a_op, a_cv)
        rc, n_c = pass_ratios(op, c34)
        use_cv = w is not None and abs(w - 1) > WITNESS_TOL
        r = r_cv if use_cv else r_op
        out.append(dict(f, r_op=r_op, r_cv=r_cv, w=w, denominator="cv" if use_cv else "op", r=r, r_c34=rc,
                        passes={"op": sorted(op), "access_op": sorted(a_op), "access_cv": sorted(a_cv),
                                "c": sorted(c34)}, n=[n_op, n_cv, n_w, n_c]))
    return out


# ------------------------------------------------------------------ plafond ouvert : patch des temps simulés
def op_patch(tr, langs, b3, mode):
    """Ajoute les clés des formes op_* : colonne du langage = temps de la forme d'accès × r (mode « r ») ou × le
    rapport tiré du témoin C (mode « c ») ; K3 relevé à b3."""
    def patch(A):
        for x in tr:
            if not usable(x, mode):
                continue
            j = A.idx[x["lang"]]
            acc, key = tkey(x["access"]), tkey(x["key"])
            if mode == "r":
                factor = x["r"]
            else:  # t_op(33) = (t_op / t_C)(34) × t_C(33) ; rapporté à la forme d'accès du langage (33)
                ck = tkey(x["c_key"])
                tc33 = A.t[("mean", ck)][0, A.idx["c"]]
                ta33 = A.t[("mean", acc)][0, j]
                factor = x["r_c34"] * tc33 / ta33
            for est in ("mean", "min"):
                src = A.t[(est, acc)]
                arr = A.t.get((est, key))
                if arr is None:
                    arr = np.full_like(src, np.nan)
                arr[:, j] = src[:, j] * factor
                if x["cell"] == "K3":
                    arr[:, j] = np.maximum(arr[:, j], b3)
                A.t[(est, key)] = arr
    return patch


def usable(x, mode):
    return x["r"] is not None and (mode != "c" or x["r_c34"] is not None)


def e_meas_open(ceil_of, tr, mode="r"):
    """E de « Convergent » (E_V2 et les formes admises du point 4), chaque clé op_* ajoutée au groupe de sa cellule."""
    e = cv.e_meas_with(ceil_of)
    for x in tr:
        if not usable(x, mode):
            continue
        k, gi = ND.CELLS[x["cell"]]
        key = tkey(x["key"])
        if key not in e[k][gi]:
            e[k][gi] = e[k][gi] + [key]
    return e


# ------------------------------------------------------------------ grille ouverte
def grid_values(grid, which):
    """{(langage, capacité): note} des cases comblées dont la note monte (which : ouverte, nommees, demi)."""
    out = {}
    for l, caps in grid.items():
        for cap, x in caps.items():
            if which == "demi":
                if x["ouverte"] > x["publiee"]:
                    out[(l, cap)] = max(x["publiee"], 0.5)
            elif x[which] > x["publiee"]:
                out[(l, cap)] = x[which]
    return out


def c_cells_open(orig, values):
    base = {}

    def c_cells(rule, c3_, rng=None, noise=0.0):
        cells = orig(rule, c3_, rng=rng, noise=noise)
        if rule not in base:
            base[rule] = orig(rule, c3_)
        for (l, cap) in sorted(values):
            if l not in cells or cap not in cells[l]:
                continue
            v = max(base[rule][l][cap], values[(l, cap)])
            if v == base[rule][l][cap]:
                continue  # la note de la règle reste, avec son tirage
            if rng is not None and rng.random() < noise:  # même bruit qu'une note publiée, tiré après les autres
                v = 0.5 if v in (0, 1) else (0.0 if rng.random() < 0.5 else 1.0)
            cells[l][cap] = v
        return cells
    return c_cells


# ------------------------------------------------------------------ un calcul
def run(env, tr=None, grid=None, mode="r"):
    data, bypass, lat, fc, langs, footprint, c3, eb, b3, keys = env
    d = {l: dict(data["pub"].get(l, {})) for l in langs}
    lt = {l: dict(lat["pub"].get(l, {})) for l in langs}
    filled = S.fill_missing(d, langs, keys)
    add, ceil_of, missing = cv.additions(data, fc, langs)
    e_meas = e_meas_open(ceil_of, tr or [], mode)
    patches = [cv.fill_patch(d, langs, add)]
    if tr:
        patches.append(op_patch(tr, langs, b3, mode))
    patches.append(cv.r4_patch(b3))
    saved_eb, saved_ref, saved_cc = v3.EBOUND, cf.references, cf.c_cells
    v3.EBOUND = dict(eb)
    v3.EBOUND[("k3", 0)] = b3

    def references(A, est):
        ref = saved_ref(A, est)
        ref["tstar"][("k3", 0)] = b3
        return ref
    cf.references = references
    if grid:
        cf.c_cells = c_cells_open(saved_cc, grid)
    try:
        s = cf.scenario(d, lt, langs, footprint, c3, "main", e_meas=e_meas,
                        patch=lambda A: [p(A) for p in patches])
        cells = {}
        A = s["A"]
        for x in (tr or []):  # temps centraux (estimation « mean ») de la forme d'accès et de la forme op_*
            j = A.idx[x["lang"]]
            ta = float(A.t[("mean", tkey(x["access"]))][0, j])
            to = A.t.get(("mean", tkey(x["key"])))
            cells.setdefault(x["lang"], {}).setdefault(x["cell"], {"access": x["access"], "t_access": ta,
                                                                    "forms": {}})
            if to is not None and not math.isnan(float(to[0, j])):
                cells[x["lang"]][x["cell"]]["forms"][x["key"]] = float(to[0, j])
    finally:
        v3.EBOUND, cf.references, cf.c_cells = saved_eb, saved_ref, saved_cc
    out = S.summarize(s, langs)
    out["missing"] = missing
    out["filled"] = [list(map(str, x)) for x in filled]
    for l, row in cells.items():
        for c, x in row.items():
            best = min([(x["t_access"], x["access"])] + [(t, k) for k, t in x["forms"].items()])
            x["retained"], x["ratio"] = best[1], best[0] / x["t_access"]
    out["cells"] = cells
    return out


# ------------------------------------------------------------------ calcul 7
def access_cost(forms):
    """Lignes de code des formes op_* (results/open/counts_op.json : outil et règles de lecture du point 5), de la
    forme d'accès et de la référence naturelle de la cellule (results/cost/counts.json)."""
    if not os.path.exists(COUNTS_OP):
        return None
    cop = json.load(open(COUNTS_OP))
    cnt = json.load(open(COUNTS))
    out = []
    for f in forms["forms"]:
        l, c = f["lang"], f["cell"]
        nat = ND.k3_ref(f["access"]) if c == "K3" else ND.NATURAL[c]
        N = cnt[l]["forms"].get(nat, {}).get("L")
        La = cnt[l]["forms"].get(f["access"], {}).get("L")
        Lo = cop.get(l, {}).get("forms", {}).get(f["key"], {}).get("L")
        out.append({"lang": l, "cell": c, "form": f["key"], "lib": f["lib"], "L_op": Lo, "L_access": La,
                    "N": N, "nat": nat,
                    "s_op": max(0.0, 1 - N / Lo) if Lo and N else None,
                    "s_access": max(0.0, 1 - N / La) if La and N else None})
    return out


def b3_open():
    vals = {}
    for which in ("start", "end"):
        p = os.path.join(OPEN, f"k3_ref_{which}.txt")
        if not os.path.exists(p):
            continue
        runs, cur = [], []
        for line in open(p):
            m = re.match(r"décalage\s+(\d+) octets :\s+([\d.]+) ms", line)
            if m:
                cur.append(float(m.group(2)))
            elif line.startswith("---") and cur:
                runs.append(cur)
                cur = []
        if cur:
            runs.append(cur)
        vals[which] = [float(np.median(r)) for r in runs]
    return vals


# ------------------------------------------------------------------ principal
def main():
    v2.ADDED.clear()
    data, bypass, lat, failures4, steal4, models4 = cv.load()
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

    forms = json.load(open(FORMS))
    grid = json.load(open(GRID))
    med, failures, models = load_open()
    tr = transfers(forms, med)
    for x in tr:
        x["c_key"] = forms["c_witness"][x["cell"]]["key"]
    named = [x for x in tr if x["named"]]
    g_open, g_named, g_half = grid_values(grid, "ouverte"), grid_values(grid, "nommees"), grid_values(grid, "demi")

    base = run(env)
    prev = json.load(open(cv.OUT))["results"][R4]
    control = {"same_order": prev["order"] == base["order"],
               "max_exp_diff": max(abs(prev["exp"][l] - base["exp"][l]) for l in langs),
               "max_ms0_diff": max(abs(prev["ms0"][l] - base["ms0"][l]) for l in langs)}
    res = {R4: base,
           "Ouverte": run(env, tr, g_open),
           "Plafond ouvert seul": run(env, tr, None),
           "Grille ouverte seule": run(env, None, g_open),
           "Bibliothèques nommées": run(env, named, g_named),
           "Cases comblées à ½": run(env, tr, g_half),
           "Report par le témoin C": run(env, tr, g_open, mode="c")}
    moved = {c: S.moved(base["order"], res[c]["order"], langs) for c in CALCS}
    changed = {l: {cap: [x["publiee"], x["ouverte"], x["nommees"]] for cap, x in caps.items()}
               for l, caps in grid.items()}  # toutes les cases comblées, montées ou non
    out = {"control": control, "results": res, "moved_vs_R4": moved, "transfers": tr, "grid_changed": changed,
           "grid_values": {"ouverte": {f"{l}|{c}": v for (l, c), v in g_open.items()},
                           "nommees": {f"{l}|{c}": v for (l, c), v in g_named.items()},
                           "demi": {f"{l}|{c}": v for (l, c), v in g_half.items()}},
           "access_cost": access_cost(forms), "b3_point4": b3, "b3_machine34_ms": b3_open(),
           "failures": failures, "cpu_models": models}
    json.dump(out, open(OUT, "w"), indent=1, ensure_ascii=False, default=float)
    report(out)


# ------------------------------------------------------------------ rapport
def fr(x, d=2):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "–"
    return f"{x:.{d}f}".replace(".", ",")


def short(key):
    k, v, p = key.split("|")
    return f"{v}{' ' + p if p else ''}"


def report(o):
    R = o["results"]
    base = R[R4]
    L = ["# v4, point 6 : la piste ouverte — résultats", "",
         "*Plan : `docs/V4_OPEN.md` (sections 5 à 7, écarts de la section 10). Généré par `analysis/open_v4.py` à "
         "partir de `results/open/raw` (machine 34), du relevé `results/open/forms.json`, de la grille ouverte "
         "`results/open/grid_open.json` et des données du point 4 (machine 33). Le classement de tête du README ne "
         "change pas (section 8).*", ""]
    c = o["control"]
    L += [f"Contrôle : « {R4} » refait par l'outil : même ordre que le point 4 = {c['same_order']} ; écart maximal "
          f"des rangs espérés {c['max_exp_diff']:.2g}, des scores au centre {c['max_ms0_diff']:.2g}.", ""]
    L += ["## Classements", "", "| Langage | " + " | ".join([R4] + CALCS) + " |", "|---|" + "---|" * (len(CALCS) + 1)]
    for l in base["order"]:
        cells = []
        for name in [R4] + CALCS:
            r = R[name]
            p = r["order"].index(l) + 1
            mark = "" if name == R4 or abs(p - base["order"].index(l) - 1) <= 2 else " **"
            cells.append(f"{p}{mark} ({fr(r['exp'][l])} ; {fr(r['ms0'][l], 1)})")
        L.append(f"| {NAMES[l]} | " + " | ".join(cells) + " |")
    L += ["", f"Chaque case : place (rang espéré ; score au centre) ; ** : plus de deux places d'écart avec « {R4} ». "
          f"Ordre des lignes : « {R4} ».", "", "## Rangs plausibles (90 %)", "",
          "| Langage | " + " | ".join([R4] + CALCS) + " |", "|---|" + "---|" * (len(CALCS) + 1)]
    for l in base["order"]:
        L.append(f"| {NAMES[l]} | " + " | ".join(f"{R[n]['rank90'][l][0]}–{R[n]['rank90'][l][1]}"
                                                 for n in [R4] + CALCS) + " |")
    L += ["", f"## Langages qui bougent de plus de deux places par rapport à « {R4} »", ""]
    for name in CALCS:
        mv = o["moved_vs_R4"][name]
        L.append(f"* {name} : " + (", ".join(f"{NAMES[l]} {a}e → {b}e" for l, (a, b) in
                                            sorted(mv.items(), key=lambda x: x[1][1])) or "aucun"))
    L += ["", "## Étages indicatifs (paires ordonnées dans au moins 95 % des variantes)", ""]
    for name in [R4] + CALCS:
        L.append(f"* {name} : " + " | ".join(", ".join(NAMES[l] for l in t) for t in R[name]["tiers"]))
    L += ["", "## Report des formes op_* (machine 34 → données du point 4)", "",
          "r : médiane sur les passes du rapport (forme op_*) / (forme d'accès) ; w : témoin de construction (forme "
          "d'accès dans op / dans cv) ; dénominateur cv si |w − 1| > 0,10 (écart 7) ; r par C : (forme op_*) / "
          "(forme de C de la cellule), sur la machine 34.", "",
          "| Langage | Cellule | Forme | Bibliothèque | Forme d'accès | r (op) | r (cv) | w | r retenu | r par C | "
          "passes |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for x in sorted(o["transfers"], key=lambda x: (base["order"].index(x["lang"]), ND.CELLS[x["cell"]], x["key"])):
        L.append(f"| {NAMES[x['lang']]} | {x['cell']} | {short(x['key'])} | {x['lib']}{' (nommée)' if x['named'] else ''}"
                 f" | {short(x['access'])} | {fr(x['r_op'])} | {fr(x['r_cv'])} | {fr(x['w'])} | {fr(x['r'])}"
                 f" ({x['denominator']}) | {fr(x['r_c34'])} | {x['n'][0]} |")
    L += ["", "## Forme retenue par cellule (« Ouverte », estimation centrale)", "",
          "Chaque case : forme retenue et rapport de son temps à celui de la forme d'accès du point 4 (1,00 : la forme "
          "d'accès reste).", "", "| Langage | Cellule | Forme d'accès | Forme retenue | Rapport |", "|---|---|---|---|---|"]
    cells = R["Ouverte"]["cells"]
    for l in base["order"]:
        for cell, x in sorted(cells.get(l, {}).items(), key=lambda kv: ND.CELLS[kv[0]]):
            L.append(f"| {NAMES[l]} | {cell} | {short(x['access'])} | {short(x['retained'])} | {fr(x['ratio'])} |")
    L += ["", "## Grille ouverte : cases comblées", "",
          "Chaque case : capacité, note publiée → note ouverte (note des seules bibliothèques nommées) ; une case dont "
          "la note ne monte pas (bibliothèque limitée) garde sa note publiée.", ""]
    for l in base["order"]:
        ch = o["grid_changed"].get(l)
        if ch:
            L.append(f"* {NAMES[l]} : " + ", ".join(f"{cap} {fr(v[0], 1)} → {fr(v[1], 1)} ({fr(v[2], 1)})"
                                                     for cap, v in sorted(ch.items())))
    ac = o["access_cost"]
    L += ["", "## Calcul 7 (information) : coût d'accès des formes op_*", ""]
    if ac is None:
        L.append("Comptage des formes op_* absent (`results/open/counts_op.json`).")
    else:
        L += ["L : lignes de code de la forme (outil et règles de lecture du point 5) ; N : la référence naturelle de "
              "la cellule ; s = max(0 ; 1 − N / L).", "",
              "| Langage | Cellule | Forme | L | s | Forme d'accès : L | s |", "|---|---|---|---|---|---|---|"]
        for x in sorted(ac, key=lambda x: (base["order"].index(x["lang"]), ND.CELLS[x["cell"]], x["form"])):
            L.append(f"| {NAMES[x['lang']]} | {x['cell']} | {short(x['form'])} | {x['L_op'] or '–'} | {fr(x['s_op'])}"
                     f" | {x['L_access'] or '–'} | {fr(x['s_access'])} |")
    b = o["b3_machine34_ms"]
    L += ["", f"b3 du point 4 (machine 33) : {fr(1e3 * o['b3_point4'])} ms ; machine 34 : "
          + (" ; ".join(f"{w} " + ", ".join(fr(v) for v in vs) for w, vs in b.items()) if b else "–") + " ms.", "",
          "Processeur des enregistrements : " + " ; ".join(f"{m} ({n})" for m, n in o["cpu_models"].items())
          + f". Processus écartés : {len(o['failures'])}."]
    for f in o["failures"]:
        L.append(f"* {NAMES.get(f['lang'], f['lang'])} {f['build']} {f['key']} passe {f['pass']} : code "
                 f"{f['returncode']}, contrôles {f['oks']}{', hors mémoire' if f['oom'] else ''}")
    open(REPORT, "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
