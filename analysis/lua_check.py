#!/usr/bin/env python3
"""Remarque sur Lua (plan : docs/LUA.md, section 3), poussé avant les mesures.

Rapports appariés sur la machine 23 (Cascade Lake, du même modèle que l'hôte des données principales ; results/raw_lua,
étiquette « lua »), reportés sur les données publiées de Lua (PUC-Lua 5.5.1) ; analyse globale de la v3 rejouée (mêmes
tirages) pour chaque scénario du plan (3.5) :
* Avant : le classement publié d'avant (B3 = 0, B4 = 0) ; doit reproduire results/python_check.json (P-E, avec le K8
  naturel de Python corrigé par la même règle, docs/PYTHON.md 4.8) à l'identique.
* L-code : K3 (quatre variantes), K4 (trois variantes), Q6 tuned et mt, K8 naturel (temps et latences)
  × r(lua_fix / lua_ref), par transfert ; grille d'avant.
* L-M : errata B3 = B4 = 1/2 seuls. L-E (classement publié) : les deux.
* L-E-P (information) : L-E, K3 et K4 reportés par la règle du pont de analysis/transfer_check.py et la règle de sens.
* Sensibilités (sur L-E, en min(1, r) par rapport à la base du même hôte : lua_fix pour Q6, lua_ref sinon) : S-Q6n
  (Q6 tuned et mt par tests imbriqués), S-K9s (K9 tuned et mt, voisins glissants), S-K7p (K7 tuned, une table tassée),
  S-K8it (arène itérative), S-K1h (K1 soa, 0,5 hors de la boucle), S-K2s (K2 aux indices décalés), S-mesures (toutes),
  S-cases (A8 = 1/2), S-tout.
* S-LuaJIT (information) : LuaJIT à la place de PUC-Lua, avec la grille de Lua (errata compris) : ses données publiées
  (annexe), K3 conforme = K3 corrigé de Lua × r(luajit_fix / lua_fix), K8 naturel à champs nommés
  × r(luajit_fix / luajit_ref) (temps et latences), son empreinte ; S-LuaJIT-FFI : la même, sa FFI notée comme ctypes
  (Python) et node:ffi (JavaScript), son -jdump comme le --print-opt-code de Node (cellules FFI_CELLS).
Information : Q6 naturel sous lua_fix / lua_ref (code inchangé : contrôle).
Les corrections publiées des autres langages (results/transfers.json : ratios, ratios_k9h, lat_ratios) sont appliquées
comme dans le calcul publié ; celles de Lua en sont retirées pour le calcul, puis les rapports de L-E y sont écrits
(« ratios » ; « lat_ratios » pour les latences de K8 naturel). Les rapports de la réplication (« replication_ratios »,
« replication_lat_ratios ») vont dans results/lua_check.json.
Sorties : results/lua_check.json, results/report_lua.md ; results/transfers.json (Lua).
Variables (essai) : LUA_RAW, LUA_TAG, LUA_OUT (sorties ailleurs, transferts non écrits)."""
import glob, json, os, sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import analyze_v2 as v2  # noqa: E402
import analyze_v3 as v3  # noqa: E402
import confrontation as cf  # noqa: E402
from analyze_v2 import RANKED, ANNEX, ROOT, NAMES, K8N  # noqa: E402
from fortran_check import ratio  # noqa: E402
from python_check import kk, gm, lat_ratio, LATCOLS, f  # noqa: E402

RAW = os.environ.get("LUA_RAW", os.path.join(ROOT, "results", "raw_lua"))
TAG = os.environ.get("LUA_TAG", "lua")
OUT = os.environ.get("LUA_OUT", os.path.join(ROOT, "results"))
LANG = "lua"
LIMIT = 0.25
K3 = [("k3", "rmw_packed", ""), ("k3", "rmw_padded", ""), ("k3", "sw_packed", ""), ("k3", "sw_padded", "")]
K4 = [("k4", "natural_unsorted", ""), ("k4", "natural_sorted", ""), ("k4", "branchless_unsorted", "")]
Q6T, Q6M, Q6N = ("k6", "tuned", "q6"), ("k6", "mt", "q6"), ("k6", "natural", "q6")
K9T, K9M, K7T, K8T, K1S = ("k9", "tuned", ""), ("k9", "mt", ""), ("k7", "tuned", ""), ("k8", "tuned", ""), ("k1", "soa", "energy")
K2S = ["16384", "262144", "8388608"]
CORR = K3 + K4 + [Q6T, Q6M, K8N]
CONTROLS = [Q6N]
BRIDGE = [("k3", "sw_padded", ""), ("k3", "rmw_padded", ""), ("k4", "natural_unsorted", ""), ("k4", "branchless_unsorted", "")]
SENS = {"q6_tuned_n": (Q6T, ("lua_exp", ("k6", "tuned_n", "q6")), ("lua_fix", Q6T)),
        "q6_mt_n": (Q6M, ("lua_exp", ("k6", "mt_n", "q6")), ("lua_fix", Q6M)),
        "k9_tuned_s": (K9T, ("lua_exp", ("k9", "tuned_s", "")), ("lua_ref", K9T)),
        "k9_mt_s": (K9M, ("lua_exp", ("k9", "mt_s", "")), ("lua_ref", K9M)),
        "k7_tuned_p": (K7T, ("lua_exp", ("k7", "tuned_p", "")), ("lua_ref", K7T)),
        "k8_tuned_it": (K8T, ("lua_exp", ("k8", "tuned_it", "")), ("lua_ref", K8T)),
        "k1_soa_h": (K1S, ("lua_exp", ("k1", "soa_h", "energy")), ("lua_ref", K1S))}
for _s in K2S:
    SENS[f"k2_tuned_s_{_s}"] = (("k2", "tuned", _s), ("lua_exp", ("k2", "tuned_s", _s)), ("lua_ref", ("k2", "tuned", _s)))
PLAN = {"S-Q6n": ["q6_tuned_n", "q6_mt_n"], "S-K9s": ["k9_tuned_s", "k9_mt_s"], "S-K7p": ["k7_tuned_p"],
        "S-K8it": ["k8_tuned_it"], "S-K1h": ["k1_soa_h"], "S-K2s": [f"k2_tuned_s_{s}" for s in K2S],
        "S-mesures": list(SENS)}
ERRATA = {"B3": 0.5, "B4": 0.5}
BEFORE = {"B3": 0, "B4": 0}
CASES = {"A8": 0.5}
# S-LuaJIT-FFI : FFI de LuaJIT notée comme ctypes (Python : A1, A2, A3, A4, A7, B5, E6 à 1/2 ; A8 à 1/2 comme array) et
# node:ffi (JavaScript), -jdump comme --print-opt-code (E1 = 1)
FFI_CELLS = {"A1": 0.5, "A2": 0.5, "A3": 0.5, "A4": 0.5, "A7": 0.5, "A8": 0.5, "B5": 0.5, "E6": 0.5, "E1": 1}


def load_raw():
    d, lat, bad = defaultdict(dict), defaultdict(dict), []
    for fn in sorted(glob.glob(os.path.join(RAW, "*.jsonl"))):
        for line in open(fn):
            r = json.loads(line)
            if r.get("tag") != TAG:
                continue
            key = (r["kernel"], r["variant"], r["param"])
            reps = r.get("reps", [])
            if not reps or r.get("returncode") not in (0, None) or any(x["ok"] is not True for x in reps):
                bad.append((r["lang"], key, r.get("returncode")))
                continue
            d[r["lang"]].setdefault(key, []).append([x["sec"] for x in reps])
            if r["kernel"] == "k8" and r.get("lat"):
                lat[r["lang"]].setdefault(key, []).append(r["lat"])
    return d, lat, bad


def scaled(data, factors):
    d = {l: {k: [list(p) for p in v] for k, v in dd.items()} for l, dd in data.items()}
    for key, r in factors.items():
        d[LANG][key] = [[t * r for t in p] for p in data[LANG][key]]
    return d


def summary(s):
    i = RANKED.index(LANG)
    order = sorted(RANKED, key=lambda l: (s["exp21"][l], -s["ms0"][l]))
    pos = order.index(LANG)
    nb = {}
    if pos > 0:
        nb["devant"] = (order[pos - 1], float(s["prec"][i, RANKED.index(order[pos - 1])]))
    if pos < len(order) - 1:
        nb["derrière"] = (order[pos + 1], float(s["prec"][i, RANKED.index(order[pos + 1])]))
    return {"order21": order, "exp21": s["exp21"], "rank90": s["rank90"], "first": s["first"],
            "ms0": {l: s["ms0"][l] for l in RANKED}, "E": {l: s["E"][l] for l in RANKED},
            "D": {l: s["D"][l] for l in RANKED}, "C": {l: s["C"][l] for l in RANKED},
            "Ek": s["Ek"][LANG], "pos": pos + 1, "neighbours": nb,
            "prec_l": {l: float(s["prec"][i, RANKED.index(l)]) for l in RANKED if l != LANG},
            "prec_next": {a: float(s["prec"][RANKED.index(a), RANKED.index(b)]) for a, b in zip(order, order[1:])}}


def run(data, lat, langs, footprint, c3, cells=None):
    """Scénario avec des cases de Lua remplacées le temps du calcul."""
    saved = {}
    try:
        for cap, val in (cells or {}).items():
            saved[cap] = v2.MATRIX[LANG][cap]
            v2.MATRIX[LANG][cap] = (val, saved[cap][1])
        return summary(cf.scenario(data, lat, langs, footprint, c3, "main"))
    finally:
        for cap, v in saved.items():
            v2.MATRIX[LANG][cap] = v


def published_data():
    """Données du calcul publié, sans les corrections de Lua : transferts des autres langages, K9 de la machine 16 (et
    les corrections de K9 des autres langages), latences de la machine 11 (et les corrections de latence des autres)."""
    data, lat, *_ = v2.dataset_main(transfers=False, k9h=None)
    tr = json.load(open(os.path.join(ROOT, "results", "transfers.json")))
    for lang, keys in tr["ratios"].items():
        if lang != LANG:
            for k, r in keys.items():
                key = tuple(k.split("|"))
                data[lang][key] = [[t * r for t in p] for p in data[lang][key]]
    for lang, r in tr.get("lat_ratios", {}).items():
        if lang != LANG and K8N in lat.get(lang, {}):
            lat[lang][K8N] = v2.scale_lat(lat[lang][K8N], r)
    v2.apply_k9h(data, "common", skip=(LANG,))
    v2.align_lat(data, lat)
    return data, lat, tr


def with_lat(lat, r):
    out = {l: dict(v) for l, v in lat.items()}
    out[LANG][K8N] = v2.scale_lat(lat[LANG][K8N], r)
    return out


def main():
    m = v2.MATRIX[LANG]
    assert {c: m[c][0] for c in ERRATA} == ERRATA, "errata B3, B4 absents de analysis/capabilities.py"
    data, lat, tr = published_data()
    c3 = json.load(open(os.path.join(ROOT, "results", "vectorization.json")))
    footprint = json.load(open(os.path.join(ROOT, "results", "footprint.json")))
    langs = [l for l in RANKED + list(ANNEX) if l in data]
    raw, rawlat, bad = load_raw()
    rng = np.random.default_rng(v3.SEED + 1000)
    times = {impl: {kk(k): 1e3 * gm(p) for k, p in dd.items()} for impl, dd in raw.items()}
    r_fix = {k: ratio(raw["lua_fix"][k], raw["lua_ref"][k], rng) for k in CORR + CONTROLS}
    r_sens = {n: ratio(raw[nc][nk], raw[bc][bk], rng) for n, (_, (nc, nk), (bc, bk)) in SENS.items()}
    l_fix = lat_ratio(rawlat["lua_fix"][K8N], rawlat["lua_ref"][K8N], rng)
    r_jk3 = {k: ratio(raw["luajit_fix"][k], raw["lua_fix"][k], rng) for k in K3}
    r_jk8 = ratio(raw["luajit_fix"][K8N], raw["luajit_ref"][K8N], rng)
    l_jk8 = lat_ratio(rawlat["luajit_fix"][K8N], rawlat["luajit_ref"][K8N], rng)
    r_py8 = ratio(raw["python_k8n"][K8N], raw["python_ref"][K8N], rng)  # information (appliqué par python_check)
    transfer = {}

    def bridged(label, key, r, new_procs):
        """Pont par le C du même hôte au-delà de 25 % d'écart, et règle de sens (information, scénario L-E-P)."""
        t_main = gm(data[LANG][key])
        trf = t_main * r
        if key not in raw.get("c", {}):
            return r
        br = gm(data["c"][key]) * gm(new_procs) / gm(raw["c"][key])
        gap = trf / br - 1
        use = abs(gap) > LIMIT
        fct = (br if use else trf) / t_main
        used = min(1.0, fct) if r < 1 else max(1.0, fct)
        transfer[label] = {"key": kk(key), "main_ms": 1e3 * t_main, "transfer_ms": 1e3 * trf, "bridge_ms": 1e3 * br,
                           "gap": gap, "bridge_used": use, "ratio": r, "factor": fct, "factor_used": used,
                           "c_main_ms": 1e3 * gm(data["c"][key]), "c_here_ms": 1e3 * gm(raw["c"][key])}
        return used

    fix_t = {k: r_fix[k]["ratio"] for k in CORR}
    fix_b = dict(fix_t)
    for k in BRIDGE:
        fix_b[k] = bridged(f"pont {kk(k)}", k, r_fix[k]["ratio"], raw["lua_fix"][k])
    sens_t = {n: fix_t.get(key, 1.0) * min(1.0, r_sens[n]["ratio"]) for n, (key, _, _) in SENS.items()}
    lat_fix = l_fix["ratio"]

    def with_sens(names):
        fct = dict(fix_t)
        for n in names:
            fct[SENS[n][0]] = sens_t[n]
        return fct

    lat_e = with_lat(lat, lat_fix)
    plans = {"Avant": (data, lat, BEFORE), "L-code": (scaled(data, fix_t), lat_e, BEFORE), "L-M": (data, lat, None),
             "L-E": (scaled(data, fix_t), lat_e, None), "L-E-P": (scaled(data, fix_b), lat_e, None)}
    for name, names in PLAN.items():
        plans[name] = (scaled(data, with_sens(names)), lat_e, None)
    plans["S-cases"] = (scaled(data, fix_t), lat_e, CASES)
    plans["S-tout"] = (scaled(data, with_sens(PLAN["S-mesures"])), lat_e, CASES)
    # LuaJIT à la place de PUC-Lua (information)
    dj = {l: v for l, v in data.items()}
    dj[LANG] = {k: [list(p) for p in v] for k, v in data["luajit"].items()}
    for k in K3:
        dj[LANG][k] = [[t * fix_t[k] * r_jk3[k]["ratio"] for t in p] for p in data[LANG][k]]
    dj[LANG][K8N] = [[t * r_jk8["ratio"] for t in p] for p in data["luajit"][K8N]]
    lj = {l: dict(v) for l, v in lat.items()}
    lj[LANG] = dict(lat["luajit"])
    lj[LANG][K8N] = v2.scale_lat(lat["luajit"][K8N], l_jk8["ratio"])
    fj = dict(footprint)
    fj[LANG] = footprint["luajit"]
    out = {"bad": bad, "times_ms": times, "r_fix": {kk(k): r for k, r in r_fix.items()}, "r_sens": r_sens,
           "lat_fix": l_fix, "transfer": transfer, "published_ratios": {kk(k): v for k, v in fix_t.items()},
           "bridge_ratios": {kk(k): v for k, v in fix_b.items()}, "sens_factors": sens_t,
           "luajit": {"r_k3": {kk(k): r for k, r in r_jk3.items()}, "r_k8": r_jk8, "lat_k8": l_jk8},
           "python_k8": r_py8, "replication_ratios": {"|".join(k): v for k, v in fix_t.items()},
           "replication_lat_ratios": lat_fix, "scenarios": {}}
    for name, (d, lt, cells) in plans.items():
        z = out["scenarios"][name] = run(d, lt, langs, footprint, c3, cells)
        print(f"{name} : Lua {z['ms0'][LANG]:.2f} points, C {z['C'][LANG]:.1f}, E {z['E'][LANG]:.2f}, "
              f"D {z['D'][LANG]:.1f}, rang espéré {z['exp21'][LANG]:.2f} ({z['pos']}e), rang 90 % {z['rank90'][LANG]}",
              flush=True)
    for name, cells in (("S-LuaJIT", None), ("S-LuaJIT-FFI", FFI_CELLS)):
        z = out["scenarios"][name] = run(dj, lj, langs, fj, c3, cells)
        print(f"{name} : LuaJIT {z['ms0'][LANG]:.2f} points, C {z['C'][LANG]:.1f}, E {z['E'][LANG]:.2f}, "
              f"D {z['D'][LANG]:.1f}, rang espéré {z['exp21'][LANG]:.2f} ({z['pos']}e), rang 90 % {z['rank90'][LANG]}",
              flush=True)
    ref = json.load(open(os.path.join(ROOT, "results", "python_check.json")))["scenarios"]["P-E"]
    av = out["scenarios"]["Avant"]
    out["check_before"] = max(max(abs(av["ms0"][l] - ref["ms0"][l]), abs(av["exp21"][l] - ref["exp21"][l])) for l in RANKED)
    print(f"Contrôle : écart maximal du scénario Avant au publié d'avant = {out['check_before']:.2e}")
    json.dump(out, open(os.path.join(OUT, "lua_check.json"), "w"), indent=1, default=float)
    report(out)
    if OUT != os.path.join(ROOT, "results"):
        return
    # classement publié (3.2) : rapports de L-E inscrits dans les corrections transférées
    tr["ratios"][LANG] = {"|".join(k): v for k, v in fix_t.items()}
    tr.setdefault("lat_ratios", {})[LANG] = lat_fix
    note = " ; Lua : docs/LUA.md (3.2), results/raw_lua, machine 23, results/lua_check.json (K8 naturel : lat_ratios)"
    if note not in tr["source"]:
        tr["source"] += note
    json.dump(tr, open(os.path.join(ROOT, "results", "transfers.json"), "w"), indent=1)


def report(o):
    L = ["# Remarque sur Lua : rapports appariés et scénarios\n",
         "Plan : `docs/LUA.md`. Mesures : `results/raw_lua/` (machine 23, Cascade Lake, 7 processus par cellule). Code :",
         "`analysis/lua_check.py`. Processus rejetés : " + (str(len(o["bad"])) if o["bad"] else "aucun") + ".",
         f"Contrôle : le scénario Avant reproduit le classement publié d'avant (écart maximal {o['check_before']:.1e}).\n",
         "## Rapports appariés (même hôte) : lua_fix / lua_ref\n",
         "Clés corrigées (reportées) en gras ; Q6 naturel, au code identique dans les deux copies, sert de contrôle.\n",
         "| Clé | Ancien (ms) | Nouveau (ms) | Rapport | IC 95 % |", "|---|---|---|---|---|"]
    corr = {kk(k) for k in CORR}
    for k, r in o["r_fix"].items():
        b = "**" if k in corr else ""
        L.append(f"| {b}{k}{b} | {f(r['old_ms'], 1)} | {f(r['new_ms'], 1)} | {b}{f(r['ratio'], 3)}{b} | "
                 f"{f(r['ci'][0], 3)}–{f(r['ci'][1], 3)} |")
    x = o["lat_fix"]
    L += ["", "## Latences de K8 naturel (médianes de toutes les répétitions, µs) : lua_fix / lua_ref\n",
          "| | " + " | ".join(LATCOLS) + " |", "|---|" + "---|" * len(LATCOLS),
          "| positionnel (lua_ref) | " + " | ".join(f(v, 0) for v in x["old_us"]) + " |",
          "| champs nommés (lua_fix) | " + " | ".join(f(v, 0) for v in x["new_us"]) + " |",
          "| rapport [IC 95 %] | " + " | ".join(f"{f(r, 3)} [{f(a, 2)}–{f(b, 2)}]"
                                              for r, a, b in zip(x["ratio"], x["ci_lo"], x["ci_hi"])) + " |"]
    L += ["", "## Sensibilités (forme nouvelle / base, même hôte)\n",
          "| Sensibilité | Clé | Base | Base (ms) | Forme nouvelle (ms) | Rapport | IC 95 % |", "|---|---|---|---|---|---|---|"]
    for n, r in o["r_sens"].items():
        L.append(f"| {n} | {kk(SENS[n][0])} | {SENS[n][2][0]} | {f(r['old_ms'], 1)} | {f(r['new_ms'], 1)} | "
                 f"{f(r['ratio'], 3)} | {f(r['ci'][0], 3)}–{f(r['ci'][1], 3)} |")
    j = o["luajit"]
    L += ["", "## LuaJIT (S-LuaJIT, information)\n",
          "| Rapport | Clé | Base (ms) | Nouveau (ms) | Rapport | IC 95 % |", "|---|---|---|---|---|---|"]
    for k, r in j["r_k3"].items():
        L.append(f"| K3 conforme : luajit_fix / lua_fix | {k} | {f(r['old_ms'], 1)} | {f(r['new_ms'], 1)} | "
                 f"{f(r['ratio'], 3)} | {f(r['ci'][0], 3)}–{f(r['ci'][1], 3)} |")
    r = j["r_k8"]
    L.append(f"| champs nommés : luajit_fix / luajit_ref | k8:natural | {f(r['old_ms'], 1)} | {f(r['new_ms'], 1)} | "
             f"{f(r['ratio'], 3)} | {f(r['ci'][0], 3)}–{f(r['ci'][1], 3)} |")
    r = o["python_k8"]
    L += ["", "## Python, K8 naturel sans `__slots__` (python_k8n / python_ref ; appliqué par analysis/python_check.py)\n",
          f"{f(r['old_ms'], 1)} → {f(r['new_ms'], 1)} ms, rapport {f(r['ratio'], 3)} [{f(r['ci'][0], 3)}–{f(r['ci'][1], 3)}].\n"]
    L += ["## Pont par le C de clang (information : scénario L-E-P ; le classement publié reporte par transfert)\n",
          "| Rapport | Clé | Lua publié | Transfert | Pont | Écart | Retenu | Facteur appliqué |",
          "|---|---|---|---|---|---|---|---|"]
    for lab, b in o["transfer"].items():
        L.append(f"| {lab} | {b['key']} | {f(b['main_ms'], 1)} ms | {f(b['transfer_ms'], 1)} ms | {f(b['bridge_ms'], 1)} ms | "
                 f"{f(100 * b['gap'], 1)} % | {'pont' if b['bridge_used'] else 'transfert'} | {f(b['factor_used'], 3)} |")
    L += ["", "## Scénarios (analyse globale de la v3 rejouée, 20 000 variantes)\n",
          "| Scénario | Score de Lua | C | E | D | Rang espéré | Place | Rang 90 % | Voisins |",
          "|---|---|---|---|---|---|---|---|---|"]
    for name, z in o["scenarios"].items():
        nbs = "; ".join(f"{w} {NAMES.get(l, l)} {f(100 * p, 0)} %" for w, (l, p) in z["neighbours"].items())
        L.append(f"| {name} | {f(z['ms0'][LANG])} | {f(z['C'][LANG])} | {f(z['E'][LANG], 2)} | {f(z['D'][LANG])} | "
                 f"{f(z['exp21'][LANG], 2)} | {z['pos']} | {z['rank90'][LANG][0]}–{z['rank90'][LANG][1]} | {nbs} |")
    L.append("\nDans S-LuaJIT et S-LuaJIT-FFI, la ligne « Lua » porte LuaJIT.\n")
    for name, z in o["scenarios"].items():
        top = ", ".join(f"{i + 1}. {NAMES.get(l, l)} ({f(z['exp21'][l], 2)}, {f(z['ms0'][l])})"
                        for i, l in enumerate(z["order21"][15:21], start=15))
        L.append(f"**{name}** : {top}.\n")
    L.append("## Rapports reportés sur la réplication (machine 3)\n")
    L.append(", ".join(f"{k.replace('|', ':').rstrip(':')} {f(r, 3)}" for k, r in sorted(o["replication_ratios"].items()))
             + " ; latences de K8 naturel : " + ", ".join(f(r, 3) for r in o["replication_lat_ratios"]) + ".")
    open(os.path.join(OUT, "report_lua.md"), "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
