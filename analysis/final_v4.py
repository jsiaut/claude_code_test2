#!/usr/bin/env python3
"""Le classement : calcul complet, de results/final/raw à results/report_final.md (v4.1).

Méthode : docs/METHOD.md ; plans fixés avant les calculs : docs/V4_FINAL.md, section 8 (campagne finale), et
docs/V4_1.md (corrections A1 à A4 de l'analyse). Ce module est autonome : il lit les mesures de la campagne
(results/final/raw, tools/final/campaign.py), b3 (results/final/b3.jsonl), les bornes physiques des machines qui ont
mesuré (results/hw/machine<N>), le relevé des formes (results/converge/forms.json), l'empreinte de K1
(results/footprint.json) et la grille de contrôle (analysis/capabilities.py, analysis/capabilities_v2.py ; la
vectorisation mesurée de results/vectorization.json ne sert qu'à la règle v1, dans les calculs sans A1).

Score d'un langage (sur 100) : 0,35 x contrôle (C) + 0,40 x plafond (E) + 0,25 x code par défaut (D).
* Plafond : moyenne géométrique sur huit noyaux (K1, K3 à K9) du rapport de la référence au meilleur temps du langage ;
  la référence est le meilleur des 25 langages (ou, dans une variante sur deux, la borne physique de la machine). Sept
  noyaux comptent à trois tailles (positions petite, publiée, grande ; pour K5 : 2^11, 2^15, 2^21) : chaque cellule est
  calculée à chaque position avec ses propres références, puis moyennée en logarithme avec les poids des tailles ; les
  mesures à quatre fils ne comptent qu'aux positions publiée et grande (A4).
* Code par défaut : D1 (code naturel rapporté au meilleur code naturel, A3), D2 (empreinte et désordre de K1), D3
  (queues de latence de K8 naturel), D4 (chaîne de pointeurs de K2), pondérés 0,5 / 0,15 / 0,15 / 0,2.
* Contrôle : grille de 34 capacités notées 0, 1/2 ou 1, en règle v2 (A1).
Ordre publié : celui du score moyen sur 20 000 variantes qui tirent la configuration (estimateur, normalisations,
agrégation), le rééchantillonnage des mesures, les poids (piliers, noyaux, parts de D, catégories de la grille, tailles)
et un bruit de jugement sur chaque case de la grille. Jusqu'au 24 novembre, l'ordre était celui du rang moyen sur ces
variantes : le calcul « Méthode du 23 novembre » le garde.

Calcul « Final » (docs/V4_FINAL.md, 8 ; docs/V4_1.md, 3) :
* plafond : à chaque taille, chaque cellule prend la meilleure forme admise (C1 : variantes publiées et formes du
  relevé, écrites pour le catalogue ou déjà publiées), la variante naturelle y entrant dans son mode R1 (huit
  langages) et, pour K9, sous sa forme contiguë (R2, treize langages ; mode R1 pour C++ et D) ;
* K3 (R4, A2) : b3 est le plus lent des 16 décalages de la boucle de référence ; chaque processus de K3 est ramené au
  b3 de référence (moyenne de toutes les mesures de b3) par le rapport t x b3 / b3 de son groupe (moyenne des mesures
  faites juste avant et juste après le groupe de K3 de sa passe) ; les temps sont relevés à b3 au moins et la référence
  de K3 vaut b3 : la cellule vaut min(1, b3 / t) ;
* code par défaut : D1 et D2 (part de K1) à trois tailles avec R1 et R2 ; D3 (latences de K8 naturel, sept processus)
  à trois tailles ; D4 (K2, sept processus) à sa taille ; empreinte de K1 et grille inchangées ;
* chaque cellule nouvelle (forme absente de la base) est tirée par son propre générateur (graine fixée par la clé, le
  langage et la position), dans les réservoirs de résidus de son noyau bâtis sur la base de la position ;
* cellule manquante de la base : temps admissible le plus lent des autres langages (variantes communes) ; forme
  manquante : absente de son ensemble, signalée.
Sensibilités (CALCS) : Base, trois tailles ; sans les tailles, sans R1, sans R2, sans C1, sans R4 ; R1' au lieu de R1 ;
une taille à la fois ; sélection indépendante ; D3 et D4 sur trois processus ; sur les seules mesures ; sans une
correction de la v4.1 à la fois (Sans A1 à Sans A4) ; « Méthode du 23 novembre », sans aucune, qui redonne le classement
publié le 23 novembre. Les tirages des variantes viennent du même générateur, avancé de la même façon pour tous les
calculs : ils sont identiques d'un calcul à l'autre. Comparaison : le classement de la v3
(results/final/comparisons.json).

Sorties : results/final/analysis.json, results/report_final.md. Variables : BOOT (2000 rééchantillonnages), UA (20 000
variantes), FINAL_RAW (autres données), FINAL_OUT (autre répertoire de sortie). Contrôle : tools/check.sh."""
import copy, glob, importlib.util, json, math, os, re, sys, zlib
from collections import defaultdict

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from capabilities import MATRIX, CATEGORIES, M  # noqa: E402
from capabilities_v2 import V2_OVERRIDES, V2_DROP  # noqa: E402

_spec = importlib.util.spec_from_file_location("fbuild", os.path.join(ROOT, "tools", "final", "build.py"))
FB = importlib.util.module_from_spec(_spec)  # langages de chaque mode (R1, R1') : une seule liste, celle du pilote
_spec.loader.exec_module(FB)

# ------------------------------------------------------------------ protocole
# Ordre fixe des langages : les tirages en dépendent (les quatre derniers ont été ajoutés en cours d'étude).
RANKED = ["c", "cpp", "csharp", "java", "zig", "odin", "julia", "ada", "fortran", "js", "python", "haskell",
          "c3", "d", "rust", "chapel", "nim", "mojo", "go", "ocaml", "lua", "swift", "fpc", "bqn", "php"]
LANGS = list(RANKED)
NAMES = {"c": "C", "cpp": "C++", "csharp": "C#", "java": "Java", "zig": "Zig", "odin": "Odin", "julia": "Julia",
         "ada": "Ada", "fortran": "Fortran", "js": "JavaScript", "python": "Python", "haskell": "Haskell", "c3": "C3",
         "d": "D", "rust": "Rust", "chapel": "Chapel", "nim": "Nim", "mojo": "Mojo", "go": "Go", "ocaml": "OCaml",
         "lua": "Lua", "swift": "Swift", "fpc": "FreePascal", "bqn": "BQN", "php": "PHP"}
# Plafond : par noyau, ses mesures ; chaque mesure est la liste des clés (noyau, variante, paramètre) admissibles,
# dont le langage prend la plus rapide. Les formes du relevé s'y ajoutent (e_meas_with).
E_V2 = {
    "k1": [[("k1", "aos", "energy"), ("k1", "soa", "energy")]],
    "k3": [[("k3", "sw_padded", ""), ("k3", "rmw_padded", "")]],
    "k4": [[("k4", "natural_unsorted", ""), ("k4", "branchless_unsorted", "")]],
    "k5": [[("k5", "natural", ""), ("k5", "tuned", "")]],
    "k6": [[("k6", "natural", "q6"), ("k6", "tuned", "q6")], [("k6", "natural", "q1"), ("k6", "tuned", "q1")],
           [("k6", "mt", "q6")], [("k6", "mt", "q1")]],
    "k7": [[("k7", "natural", ""), ("k7", "tuned", "")]],
    "k8": [[("k8", "natural", ""), ("k8", "tuned", ""), ("k8", "tuned_alloc", "")]],
    "k9": [[("k9", "natural", ""), ("k9", "tuned", "")], [("k9", "mt", "")]],
}
# Code naturel (D1) : par noyau, (indice de la mesure du plafond qui sert de référence, clés naturelles).
D1_V2 = {
    "k1": [(0, [("k1", "natural", "energy")])], "k4": [(0, [("k4", "natural_unsorted", "")])],
    "k5": [(0, [("k5", "natural", "")])], "k6": [(0, [("k6", "natural", "q6")]), (1, [("k6", "natural", "q1")])],
    "k7": [(0, [("k7", "natural", "")])], "k8": [(0, [("k8", "natural", "")])], "k9": [(0, [("k9", "natural", "")])],
}
K2_SIZES = ["16384", "262144", "8388608"]
K1N, K1S = ("k1", "natural", "energy"), ("k1", "natural_shuffled", "energy")
K8N = ("k8", "natural", "")
NAT_KEYS = [K1N, K1S, ("k4", "natural_unsorted", ""), ("k5", "natural", ""), ("k6", "natural", "q6"),
            ("k6", "natural", "q1"), ("k7", "natural", ""), K8N, ("k9", "natural", "")]
K9N, K9F = ("k9", "natural", ""), ("k9", "natural_flat", "")
K3K = [("k3", "sw_padded", ""), ("k3", "rmw_padded", "")]
# cellule du plafond du relevé des formes -> (noyau, rang de la mesure dans E_V2)
CEIL = {"K4": ("k4", 0), "K5": ("k5", 0), "Q6": ("k6", 0), "Q1": ("k6", 1), "Q6 mt": ("k6", 2), "Q1 mt": ("k6", 3),
        "K7": ("k7", 0), "K8": ("k8", 0), "K9": ("k9", 0), "K9 mt": ("k9", 1)}
# noyaux à trois tailles ; taille de chaque noyau aux positions petite, publiée, grande (tools/sizes/sizes.py)
SIZED = ["k1", "k4", "k5", "k6", "k7", "k8", "k9"]
POS = {k: ["small", "pub", "large"] for k in SIZED}
POS["k5"] = ["pub", "l2", "l3"]
POS_NAMES = ["petite", "publiée", "grande"]
PARAMS = {"k1": {"small": 1 << 14, "pub": 1 << 22, "large": 1 << 24},
          "k4": {"small": 1 << 20, "pub": 1 << 24, "large": 1 << 28},
          "k5": {"pub": (2048, 1 << 16), "l2": (1 << 15, 1 << 12), "l3": (1 << 21, 1 << 6)},
          "k6": {"small": 1 << 16, "pub": 1 << 24, "large": 1 << 26},
          "k9": {"small": 1 << 8, "pub": 1 << 11, "large": 1 << 13}}
WEIGHTS = {"C": 0.35, "E": 0.40, "D": 0.25}
DW = {"D1": 0.5, "D2": 0.15, "D3": 0.15, "D4": 0.2}
# configuration du centre ; dans les variantes, chaque choix est tiré parmi les deux de OPTS
MAIN = {"est": "mean", "enorm": "frontier", "d3": "abs", "d4": "best", "d1ref": "tstar", "agg": "arith", "crule": "v2"}
OPTS = {"est": ["mean", "min"], "enorm": ["frontier", "bounds"], "d3": ["abs", "rel"], "d4": ["best", "c"],
        "d1ref": ["tstar", "best_natural"], "agg": ["arith", "geo"], "crule": ["v2", "v1"]}
JIT = {"java", "csharp", "js", "julia", "bqn", "php"}  # classes d'implémentation des réservoirs de résidus
INTERP = {"python", "lua"}

B = int(os.environ.get("BOOT", "2000"))
U = int(os.environ.get("UA", "20000"))
SEED = 20261029 + 3
NEW_SEED = SEED + 4500  # générateurs des cellules nouvelles (complétés par la clé, le langage et la position)
SEL_SEED = SEED + 4501  # générateurs des cellules de la sélection indépendante
FIN = os.path.join(ROOT, "results", "final")
RAW = os.environ.get("FINAL_RAW", os.path.join(FIN, "raw"))
B3F = os.path.join(os.path.dirname(RAW), "b3.jsonl")
FORMS = os.path.join(ROOT, "results", "converge", "forms.json")
OUTD = os.environ.get("FINAL_OUT", FIN)
OUT = os.path.join(OUTD, "analysis.json")
REPORT = os.path.join(OUTD, "report_final.md") if "FINAL_OUT" in os.environ else os.path.join(ROOT, "results",
                                                                                               "report_final.md")
FINAL = "Final"
OLD = "Méthode du 23 novembre"  # sans A1 à A4 : doit redonner le classement publié le 23 novembre
A_OFF = {"Sans A1": "a1", "Sans A2": "a2", "Sans A3": "a3", "Sans A4": "a4"}
CALCS = [FINAL, "Base, trois tailles", "Sans les tailles (taille publiée seule)", "Sans R1", "Sans R2", "Sans C1",
         "Sans R4", "R1' au lieu de R1", "Taille petite", "Taille grande", "Sélection indépendante",
         "D3 et D4 sur trois processus", "Sur les seules mesures"] + list(A_OFF) + [OLD]
MT_MEASURES = {("k6", 2), ("k6", 3), ("k9", 1)}  # mesures à quatre fils : Q6 mt, Q1 mt, K9 mt (A4)


def corrections(calc):
    """Corrections de la v4.1 (docs/V4_1.md, 3) appliquées dans un calcul : A1 (grille en règle v2 dans toutes les
    variantes), A2 (b3 : le plus lent des 16 décalages), A3 (code naturel rapporté au meilleur code naturel), A4
    (mesures à quatre fils sans la petite taille)."""
    if calc == OLD:
        return {"a1": False, "a2": False, "a3": False, "a4": False}
    return {a: A_OFF.get(calc) != a for a in ("a1", "a2", "a3", "a4")}


def klass(l):
    return "interp" if l in INTERP else ("jit" if l in JIT else "aot")


def needed_keys(e_meas=E_V2, d1_meas=D1_V2):
    """Cellules du score : celles du plafond et du code naturel, K1 naturel (dans l'ordre et mélangé) et K2."""
    keys = set()
    for ms in e_meas.values():
        for ks in ms:
            keys.update(ks)
    for lst in d1_meas.values():
        for _, ks in lst:
            keys.update(ks)
    keys.update([K1N, K1S] + [("k2", "tuned", s) for s in K2_SIZES])
    return keys


# ------------------------------------------------------------------ grille de contrôle (pilier C)
def c_cells(rule, c3, rng=None, noise=0.0):
    """Valeurs des cases par langage : {langage: {capacité: valeur}} (C3 retirée en règle v2). Avec rng, chaque case
    jugée change de note avec la probabilité noise (bruit de jugement)."""
    out = {}
    for l in RANKED:
        cells = {}
        for cat, (_, caps) in CATEGORIES.items():
            for cap in caps:
                if rule == "v2" and cap in V2_DROP:
                    continue
                v = MATRIX[l][cap]
                if v == M:
                    cells[cap] = c3.get(l, 0)  # mesurée : pas de bruit de jugement
                    continue
                v = V2_OVERRIDES[(l, cap)][0] if rule == "v2" and (l, cap) in V2_OVERRIDES else v[0]
                if rng is not None and rng.random() < noise:
                    v = 0.5 if v in (0, 1) else (0.0 if rng.random() < 0.5 else 1.0)
                cells[cap] = v
        out[l] = cells
    return out


def c_score(cells, catw):
    res = {}
    for l, cs in cells.items():
        tot = 0.0
        for cat, (_, caps) in CATEGORIES.items():
            vals = [cs[c] for c in caps if c in cs]
            tot += catw[cat] * sum(vals) / len(vals)
        res[l] = 100 * tot
    return res


def c_vector(cdict, langs):
    return np.array([cdict[l] for l in langs])


# ------------------------------------------------------------------ données de la campagne
class Data:
    """Mesures de la campagne : data[(construction, taille)][langage][clé] = [[médiane d'un processus]] ; pour chaque
    processus aussi sa passe et sa copie (bypass), et les latences de K8 naturel (lat)."""

    def __init__(self):
        self.data = defaultdict(lambda: defaultdict(dict))
        self.bypass = defaultdict(lambda: defaultdict(dict))
        self.lat = defaultdict(lambda: defaultdict(dict))
        self.k3 = defaultdict(lambda: defaultdict(dict))  # (construction, taille) -> langage -> clé -> [(passe, boot)]
        self.failures, self.skipped, self.steal = [], [], []
        self.models, self.machines = defaultdict(lambda: defaultdict(int)), defaultdict(set)

    def procs(self, cons, size, lang, key):
        return self.data.get((cons, size), {}).get(lang, {}).get(key)


def load():
    """Un processus est retenu s'il a fini sans erreur, sans dépassement de mémoire ni de durée, et si toutes ses
    sommes de contrôle sont justes ; il est représenté par la médiane de ses répétitions."""
    F = Data()
    for f in sorted(glob.glob(os.path.join(RAW, "*.jsonl"))):
        for line in open(f):
            r = json.loads(line)
            key = (r["kernel"], r["variant"], r["param"])
            tag = (r["construction"], r["size"])
            F.models[r.get("cpu_model", "?")][r.get("pass")] += 1
            F.machines[(r["pass"], r["kernel"], r["size"])].add(r.get("machine"))
            if r.get("skipped"):
                F.skipped.append({"lang": r["lang"], "construction": r["construction"], "size": r["size"],
                                  "key": key, "pass": r["pass"], "status": r["skipped"]})
                continue
            ok = (r.get("returncode") == 0 and not r.get("oom") and not r.get("timeout") and r.get("n", 0) > 0
                  and r.get("oks") == ["True"])
            if not ok:
                F.failures.append({"lang": r["lang"], "construction": r["construction"], "size": r["size"], "key": key,
                                   "pass": r["pass"], "oom": bool(r.get("oom")), "timeout": bool(r.get("timeout")),
                                   "returncode": r.get("returncode"), "oks": r.get("oks"),
                                   "stderr": (r.get("stderr") or "")[-300:]})
                continue
            if r.get("steal_frac", 0) > 0.05:
                F.steal.append((r["lang"], r["construction"], r["size"], key, r["steal_frac"]))
            m = r["median"]
            F.data[tag][r["lang"]].setdefault(key, []).append([m])
            F.bypass[tag][r["lang"]].setdefault(key, []).append((r["pass"], m, r.get("copy", 0)))
            if key[0] == "k3":
                F.k3[tag][r["lang"]].setdefault(key, []).append((r["pass"], r.get("boot_id")))
            if key == K8N:
                F.lat[tag][r["lang"]].setdefault(key, []).append((r.get("copy", 0), r.get("lat", [])))
    return F


def b3_values(stat):
    """b3 de référence (s) et b3 de chaque groupe de K3, par (passe, démarrage) : moyenne des mesures avant et après.
    Une mesure est la moyenne de deux exécutions de la boucle de référence ; stat : « max », le plus lent de ses 16
    décalages (A2), ou « median », leur médiane (méthode du 23 novembre, valeur enregistrée par le pilote)."""
    recs = [json.loads(l) for l in open(B3F)] if os.path.exists(B3F) else []
    if not recs:
        return None, {}, []

    def value(r):
        if stat == "median":
            return r["b3_ms"]
        runs = [[float(x) for x in re.findall(r":\s+([0-9.]+) ms", out)] for out in r["outputs"]]
        assert all(len(x) == 16 for x in runs), r["label"]
        return float(np.mean([max(x) for x in runs]))

    ref = 1e-3 * float(np.mean([value(r) for r in recs]))
    groups = defaultdict(list)
    for r in recs:
        if r.get("pass") is not None and "groupe K3" in r["label"]:
            groups[(r["pass"], r["boot_id"])].append(value(r))
    return ref, {k: 1e-3 * float(np.mean(v)) for k, v in groups.items()}, recs


def k3_normalized(F, b3ref, b3g):
    """Temps de K3 ramenés au b3 de référence : t x b3 / b3 du groupe (R4, b3 par groupe : docs/V4_FINAL.md, 6)."""
    out = defaultdict(lambda: defaultdict(dict))
    for tag, dl in F.data.items():
        if tag[1] != "pub":
            continue
        for l, keys in dl.items():
            for key, procs in keys.items():
                if key[0] != "k3":
                    continue
                tags = F.k3[tag][l][key]
                out[tag][l][key] = [[p[0] * b3ref / b3g[(ps, boot)]] for p, (ps, boot) in zip(procs, tags)]
    return out


def forms_cells(langs):
    """{langage: [(construction, clé, cellule du plafond, forme, remarque)]} des formes écrites ou présentes du relevé
    (results/converge/forms.json, tools/converge/inventory.py)."""
    js = json.load(open(FORMS))["langs"]
    out = {}
    for l in langs:
        rows = []
        for form, x in sorted(js.get(l, {}).items()):
            if x["status"] not in ("écrite", "présente"):
                continue
            for c in x["cells"]:
                key = tuple(c)
                rows.append(("cv" if x["status"] == "écrite" else "pub", key, x["ceiling"], form, bool(x["remarque"])))
        out[l] = rows
    return out


def campaign_keys(data):
    keys = set()
    for dl in data.values():
        for keys_l in dl.values():
            keys.update(keys_l)
    return keys


def fill_missing(d, langs, keys):
    """Une cellule manquante (hors mémoire, durée) prend le temps admissible le plus lent des autres langages. Seules
    les variantes communes à tous les langages (tools/driver.py, PLAN) sont concernées : une variante propre à un
    langage n'existe pas pour les autres, qui ne la reçoivent pas. Et seules les cellules du score (needed_keys)."""
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    from driver import PLAN
    common = {(k, v, q) for k, lst in PLAN.items() for v, q in lst} & needed_keys()
    filled = []
    for key in sorted(k for k in keys if k in common):
        have = [l for l in langs if d.get(l, {}).get(key)]
        if not have or len(have) == len(langs):
            continue
        slow = max(have, key=lambda l: np.mean(np.log([np.median(p) for p in d[l][key]])))
        for l in langs:
            if not d.get(l, {}).get(key):
                d[l][key] = [list(p) for p in d[slow][key]]
                filled.append((l, key, slow))
    return filled


# ------------------------------------------------------------------ bornes physiques des machines
def hw_numbers(path):
    """Caractérisation d'une machine (tools/sizes/hwchar.sh, tools/hwprobe.c) : bande passante en lecture sur 1 thread
    selon la taille (bw), STREAM triad sur 4 threads, pic FMA et fréquence."""
    bw = []
    for line in open(os.path.join(path, "bw.txt")):
        m = re.match(r"bw:\s+(\d+) KiB\s+([\d.]+) GB/s", line)
        if m:
            bw.append((int(m.group(1)) * 1024, float(m.group(2)) * 1e9))
    stream4 = []
    for line in open(os.path.join(path, "stream.txt")):
        m = re.search(r"stream: T=(\d)\s+(\w+)\s+([\d.]+) GB/s", line)
        if m and m.group(1) == "4" and m.group(2) == "triad":  # triad : la figure de mérite de STREAM
            stream4.append(float(m.group(3)) * 1e9)
    peak = []
    for line in open(os.path.join(path, "peak.txt")):
        m = re.search(r"([\d.]+) GFLOP/s", line)
        if m:
            peak.append(float(m.group(1)) * 1e9)
    freq = [float(m.group(1)) * 1e9 for line in open(os.path.join(path, "freq.txt"))
            for m in [re.search(r"freq: ([\d.]+) GHz", line)] if m]
    return {"bw": sorted(bw), "stream4": max(stream4), "peak": max(peak), "freq": max(freq)}


def machines_hw(F):
    """Bornes physiques : médiane, quantité par quantité, des caractérisations des machines qui ont mesuré."""
    ms = sorted({m for v in F.machines.values() for m in v if m is not None}, key=lambda x: int(x))
    hws = [hw_numbers(os.path.join(ROOT, "results", "hw", f"machine{m}")) for m in ms]
    if not hws:
        raise SystemExit("aucune machine dans les enregistrements")
    sizes = sorted(set.intersection(*[{s for s, _ in h["bw"]} for h in hws]))
    bw = [(s, float(np.median([dict(h["bw"])[s] for h in hws]))) for s in sizes]
    hw = {"bw": bw}
    for q in ("stream4", "peak", "freq"):
        hw[q] = float(np.median([h[q] for h in hws]))
    return hw, ms


def bw1(hw, size):
    """Bande passante sur 1 thread du plus petit volume mesuré qui contient size (le plus grand volume au-delà)."""
    for s, b in hw["bw"]:
        if s >= size:
            return b
    return hw["bw"][-1][1]


def bw4(hw, size):
    """Sur 4 threads : 4 fois la bande passante d'un quart du volume tant que ce quart tient dans le L2 d'un cœur
    (2 Mio), STREAM sur 4 threads au-delà."""
    return 4 * bw1(hw, size / 4) if size / 4 <= 2 << 20 else hw["stream4"]


def ebounds(hw, pos):
    """Bornes physiques des mesures du plafond, à la taille de la position : octets à déplacer sur la bande passante
    du niveau de mémoire où ils tiennent, opérations sur le débit crête, incréments sur la fréquence."""
    n1, n4 = PARAMS["k1"][POS["k1"][pos]], PARAMS["k4"][POS["k4"][pos]]
    n5, inner5 = PARAMS["k5"][POS["k5"][pos]]
    n6, m9 = PARAMS["k6"][POS["k6"][pos]], PARAMS["k9"][POS["k9"][pos]]
    g9 = 2 * 8 * m9 * m9
    return {
        ("k1", 0): 16 * n1 / bw1(hw, 16 * n1),
        ("k3", 0): 2 ** 25 * 5 / hw["freq"],
        ("k4", 0): n4 / bw1(hw, n4),
        # K5 : calcul seul dans le L1 (2 x 2 x n x INNER / pic) ; au-delà, aussi la bande passante
        ("k5", 0): max(4 * n5 * inner5 / hw["peak"], 0 if 8 * n5 <= 48 << 10 else 8 * n5 * inner5 / bw1(hw, 8 * n5)),
        ("k6", 0): 10 * n6 / bw1(hw, 10 * n6), ("k6", 1): 13 * n6 / bw1(hw, 13 * n6),
        ("k6", 2): 10 * n6 / bw4(hw, 10 * n6), ("k6", 3): 13 * n6 / bw4(hw, 13 * n6),
        ("k9", 0): 4 * g9 / bw1(hw, g9), ("k9", 1): 4 * g9 / bw4(hw, g9),
    }


# ------------------------------------------------------------------ estimations et rééchantillonnage
def proc_logs(procs):
    return np.log(np.array([np.median(p) for p in procs], float))


def build_pools(data, langs, keys):
    """Réservoirs de résidus par (noyau, classe), fusionnés avec le noyau s'ils ont moins de 20 résidus."""
    pools, kpool = defaultdict(list), defaultdict(list)
    for l in langs:
        for key in sorted(keys):  # ordre fixe : l'ordre d'un ensemble change d'un processus à l'autre
            procs = data.get(l, {}).get(key)
            if not procs or len(procs) < 2:
                continue
            y = proc_logs(procs)
            P = len(y)
            r = (y - y.mean()) * math.sqrt(P / (P - 1))
            pools[(key[0], klass(l))].extend(r.tolist())
            kpool[key[0]].extend(r.tolist())
    out = {}
    for k in kpool:
        for c in ("aot", "jit", "interp"):
            pl = pools.get((k, c), [])
            out[(k, c)] = np.array(pl if len(pl) >= 20 else kpool[k], float)
    return out


def lat_rows(lprocs, nb, rng):
    """D3 : médianes, sur toutes les répétitions, de p50, p99,9 et max (ligne 0) ; rééchantillonnage des processus puis
    des répétitions (lignes 1..nb). Renvoie un tableau (nb + 1, 3)."""
    arrs = [np.asarray(p, float) for p in lprocs if len(p)]
    out = np.empty((nb + 1, 3))
    allr = np.vstack(arrs)
    out[0] = np.median(allr[:, [0, 3, 4]], axis=0)
    for b in range(1, nb + 1):
        pick = rng.integers(0, len(arrs), size=len(arrs))
        rows = np.vstack([arrs[j][rng.integers(0, len(arrs[j]), size=len(arrs[j]))] for j in pick])
        out[b] = np.median(rows[:, [0, 3, 4]], axis=0)
    return out


class Arrays3:
    """Temps simulés par cellule : ligne 0 = estimation ponctuelle, lignes 1..nb = tirages à résidus regroupés.
    Deux estimateurs : 'mean' (moyenne des logarithmes des médianes de processus) et 'min' (minimum des médianes)."""

    def __init__(self, data, lat, langs, nb, rng, pools, e_meas=E_V2, d1_meas=D1_V2):
        self.langs, self.nb, self.e_meas, self.d1_meas = langs, nb, e_meas, d1_meas
        self.idx = {l: i for i, l in enumerate(langs)}
        self.ranked = np.array([self.idx[l] for l in RANKED if l in self.idx])
        self.t = {}
        for key in sorted(needed_keys(e_meas, d1_meas)):
            mean = np.full((nb + 1, len(langs)), np.nan)
            mn = np.full((nb + 1, len(langs)), np.nan)
            for l in langs:
                procs = data.get(l, {}).get(key)
                if not procs:
                    continue
                y = proc_logs(procs)
                j = self.idx[l]
                mean[0, j], mn[0, j] = math.exp(y.mean()), math.exp(y.min())
                if nb:
                    pool = pools[(key[0], klass(l))]
                    draws = y.mean() + pool[rng.integers(0, len(pool), size=(nb, len(y)))]
                    mean[1:, j], mn[1:, j] = np.exp(draws.mean(axis=1)), np.exp(draws.min(axis=1))
            self.t[("mean", key)], self.t[("min", key)] = mean, mn
        self.lat = np.full((nb + 1, len(langs), 3), np.nan)
        for l in langs:
            lp = lat.get(l, {}).get(K8N)
            if lp and any(len(p) for p in lp):
                self.lat[:, self.idx[l], :] = lat_rows(lp, nb, rng)

    def dt(self, est, key, r):
        return self.t[(est, key)][r]

    def best(self, est, keys, r):
        """Meilleur temps parmi les clés admissibles (NaN si aucune)."""
        arr = np.vstack([self.t[(est, k)][r] for k in keys])
        with np.errstate(all="ignore"):
            out = np.nanmin(np.where(np.isnan(arr), np.inf, arr), axis=0)
        out[np.isinf(out)] = np.nan
        return out


def references(A, est):
    """Références fixes, calculées sur la ligne 0 (estimations ponctuelles) : frontière de chaque mesure du plafond
    (tstar) et du code naturel (nat), K2 (meilleur langage, et C), latences de K8 (absolues, relatives à p50)."""
    rk = A.ranked
    ref = {"tstar": {}, "nat": {}, "k2_best": {}, "k2_c": {}}
    with np.errstate(all="ignore"):
        for k, ms in A.e_meas.items():
            for i, ks in enumerate(ms):
                ref["tstar"][(k, i)] = float(np.nanmin(A.best(est, ks, 0)[rk]))
        for k, lst in A.d1_meas.items():
            for i, ks in lst:
                ref["nat"][(k, i)] = float(np.nanmin(A.best(est, ks, 0)[rk]))
        for s in K2_SIZES:
            t = A.dt(est, ("k2", "tuned", s), 0)
            ref["k2_best"][s] = float(np.nanmin(t[rk]))
            ref["k2_c"][s] = float(t[A.idx["c"]])
        p50, p999, mx = A.lat[0, :, 0], A.lat[0, :, 1], A.lat[0, :, 2]
        ref["d3_abs"] = (float(np.nanmin(p999[rk])), float(np.nanmin(mx[rk])))
        ref["d3_rel"] = (float(np.nanmin((p999 / p50)[rk])), float(np.nanmin((mx / p50)[rk])))
    return ref


# ------------------------------------------------------------------ score
def scores(As, r, cfg, C, footprint, refs, ebs, wS, wE=None, wD=None, wP=None, mt_nosmall=False):
    """Piliers et score de tous les langages pour la ligne r des tableaux (0 : estimation ponctuelle) et la
    configuration cfg. Chaque cellule de E, de D1, de D2 (part de K1) et de D3 est calculée à chaque position avec ses
    propres références puis moyennée en logarithme avec les poids wS ; K3 et D4 (une seule taille) sont pris à la
    position publiée. mt_nosmall (A4) : les mesures à quatre fils ne comptent qu'aux positions publiée et grande, leurs
    poids ramenés à une somme de 1, sauf si la petite taille compte seule."""
    est = cfg["est"]
    A1 = As[1]
    kernels = list(A1.e_meas)
    wE = wE or {k: 1 / len(kernels) for k in kernels}
    wD, wP = wD or DW, wP or WEIGHTS
    pos_of = lambda k: range(3) if k in SIZED else [1]  # noqa: E731
    wpos = lambda k, p: wS[p] if k in SIZED else 1.0  # noqa: E731
    n = len(A1.langs)
    lnE, ek = np.zeros(n), {}
    with np.errstate(all="ignore"):
        for k, ms in A1.e_meas.items():
            lr = []
            for i, ks in enumerate(ms):
                cell = np.zeros(n)
                nosmall = mt_nosmall and (k, i) in MT_MEASURES and wS[1] + wS[2] > 0
                for p in pos_of(k):
                    if nosmall and p == 0:
                        continue
                    t = As[p].best(est, ks, r)
                    if cfg["enorm"] == "bounds" and (k, i) in ebs[p]:
                        v = np.log(np.minimum(1.0, ebs[p][(k, i)] / t))
                    else:
                        v = np.log(refs[p][est]["tstar"][(k, i)] / t)
                    cell = cell + (wS[p] / (wS[1] + wS[2]) if nosmall else wpos(k, p)) * v
                lr.append(cell)
            ek[k] = np.mean(lr, axis=0)
            lnE += wE[k] * ek[k]
        E = 100 * np.exp(lnE)
        d1k = []
        for k, lst in A1.d1_meas.items():
            lr = []
            for i, ks in lst:
                cell = np.zeros(n)
                for p in pos_of(k):
                    ref = refs[p][est]
                    t = As[p].best(est, ks, r)
                    cell = cell + wpos(k, p) * np.log((ref["tstar"][(k, i)] if cfg["d1ref"] == "tstar" else ref["nat"][(k, i)]) / t)
                lr.append(cell)
            d1k.append(np.mean(lr, axis=0))
        D1 = np.exp(np.mean(d1k, axis=0))
        a = np.array([min(1.0, 64.0 / footprint[l]) if footprint.get(l) else np.nan for l in A1.langs])
        lbb = sum(wS[p] * np.log(np.minimum(1.0, As[p].dt(est, K1N, r) / As[p].dt(est, K1S, r))) for p in range(3))
        bb = np.exp(lbb)
        D2 = np.where(np.isnan(a), bb, np.sqrt(a * bb))
        l3 = np.zeros(n)
        for p in range(3):
            ref = refs[p][est]
            p50, p999, mx = As[p].lat[r, :, 0], As[p].lat[r, :, 1], As[p].lat[r, :, 2]
            if cfg["d3"] == "abs":
                d3 = np.sqrt((ref["d3_abs"][0] / p999) * (ref["d3_abs"][1] / mx))
            else:
                d3 = np.sqrt((ref["d3_rel"][0] / (p999 / p50)) * (ref["d3_rel"][1] / (mx / p50)))
            l3 = l3 + wS[p] * np.log(d3)
        D3 = np.exp(l3)
        l4 = []
        ref1 = refs[1][est]
        for s in K2_SIZES:
            t = A1.dt(est, ("k2", "tuned", s), r)
            refv = ref1["k2_best"][s] if cfg["d4"] == "best" else ref1["k2_c"][s]
            l4.append(np.log(np.minimum(1.0, refv / t)))
        D4 = np.exp(np.mean(l4, axis=0))
        D = 100 * (wD["D1"] * D1 + wD["D2"] * D2 + wD["D3"] * D3 + wD["D4"] * D4)
        if cfg["agg"] == "arith":
            MS = wP["C"] * C + wP["E"] * E + wP["D"] * D
        else:
            MS = np.exp(wP["C"] * np.log(C) + wP["E"] * np.log(E) + wP["D"] * np.log(D))
    return {"E": E, "D": D, "MS": MS, "D1": D1, "D2": D2, "D3": D3, "D4": D4, "Ek": {k: np.exp(v) for k, v in ek.items()}}


def ranks_of(ms_ranked):
    """Rang (1 = meilleur) de chaque langage classé ; NaN en dernier."""
    order = np.argsort(-np.nan_to_num(ms_ranked, nan=-1e9), kind="stable")
    rk = np.empty(len(ms_ranked), int)
    rk[order] = np.arange(1, len(ms_ranked) + 1)
    return rk


def dirichlet(rng, alpha):
    g = rng.gamma(np.asarray(alpha, float))
    return g / g.sum()


def tiers(order, prec, idx, level=0.95):
    """Étages : frontière entre i et i + 1 si toutes les paires de part et d'autre sont ordonnées dans au moins level
    des variantes."""
    cuts = [i for i in range(1, len(order))
            if all(prec[idx[a], idx[b]] >= level for a in order[:i] for b in order[i:])]
    bounds = [0] + cuts + [len(order)]
    return [order[bounds[j]:bounds[j + 1]] for j in range(len(bounds) - 1)]


def moved(a, b, langs):
    """Langages dont la place change de plus de deux entre deux ordres : {langage: (place dans a, place dans b)}."""
    return {l: (a.index(l) + 1, b.index(l) + 1) for l in langs if abs(a.index(l) - b.index(l)) > 2}


# ------------------------------------------------------------------ données d'une position et d'un calcul
def size_of(key, p):
    k = key[0]
    return POS[k][p] if k in SIZED else "pub"


def position(F, p, calc, k3n):
    """(d, lt, src, missing) d'une position : la base (construction pub), K3 de R4, puis les substitutions du calcul.
    src[l][clé] = (construction, taille, clé source), pour la sélection indépendante."""
    d, lt, src, missing = defaultdict(dict), defaultdict(dict), defaultdict(dict), []
    three = calc == "D3 et D4 sur trois processus"
    for (cons, size), dl in F.data.items():
        if cons != "pub":
            continue
        for l, keys in dl.items():
            for key, procs in keys.items():
                if size_of(key, p) != size:
                    continue
                if three and (key[0] == "k2" or key == K8N):
                    procs = [[m] for ps, m, c in F.bypass[(cons, size)][l][key] if c == 0]
                d[l][key] = procs
                src[l][key] = (cons, size, key)
    for l in LANGS:
        lp = F.lat.get(("pub", POS["k8"][p]), {}).get(l, {}).get(K8N)
        if lp:
            lt[l][K8N] = [x for c, x in lp if not three or c == 0]
    r4 = calc not in ("Base, trois tailles", "Sans R4")
    if r4:
        for l, keys in k3n.get(("pub", "pub"), {}).items():
            for key, procs in keys.items():
                d[l][key] = procs

    def sub(l, cons, tk, sk):
        size = size_of(tk, p)
        procs = F.procs(cons, size, l, sk)
        if not procs:
            missing.append([l, cons, "|".join(sk), size])
            return
        if three and tk == K8N:
            procs = [[m] for ps, m, c in F.bypass[(cons, size)][l][sk] if c == 0]
        d[l][tk] = procs
        src[l][tk] = (cons, size, sk)
        if tk == K8N:
            lp = F.lat.get((cons, size), {}).get(l, {}).get(K8N)
            if lp:
                lt[l][K8N] = [x for c, x in lp if not three or c == 0]
            else:
                missing.append([l, cons, "latences de K8", size])

    mode = None if calc in ("Base, trois tailles", "Sans R1") else ("unc" if calc == "R1' au lieu de R1" else "chk")
    if mode:
        for l in (FB.CHK if mode == "chk" else FB.UNC):
            for k in NAT_KEYS:
                sub(l, mode, k, k)
    if calc not in ("Base, trois tailles", "Sans R2"):
        for l in nested():
            cons = "cv"
            if mode == "chk" and l in FB.CV_CHK:
                cons = "cv_chk"
            elif mode == "unc" and l in FB.CV_UNC:
                cons = "cv_unc"
            sub(l, cons, K9N, K9F)
    return d, lt, src, missing


_NESTED = None


def nested():
    """Les 13 langages à grille imbriquée : ceux dont cv_variants déclare K9 natural_flat (R2)."""
    global _NESTED
    if _NESTED is None:
        _NESTED = []
        for l in LANGS:
            p = os.path.join(ROOT, "bench", l, "cv_variants")
            if os.path.exists(p) and any(line.split()[:2] == ["k9", "natural_flat"] for line in open(p)):
                _NESTED.append(l)
    return _NESTED


def additions(F, fc, p, d):
    """Cellules nouvelles d'une position (C1) : {clé: {langage: processus}}, leur cellule du plafond, les manquantes."""
    add, ceil_of, missing = defaultdict(dict), {}, []
    for l in LANGS:
        for build, key, ceil, form, rq in fc.get(l, []):
            size = size_of(key, p)
            if build == "pub" and key in d.get(l, {}):
                continue  # forme présente : déjà dans la base
            procs = F.procs("cv", size, l, key) or F.procs(build, size, l, key)
            ceil_of[key] = ceil
            if not procs:
                missing.append([l, build, "|".join(key), size])
                continue
            add[key][l] = procs
    return add, ceil_of, missing


def e_meas_with(keys_ceil):
    """E_V2 (même ordre des noyaux et des mesures : les poids tirés ne changent pas), chaque clé nouvelle ajoutée à la
    mesure de sa cellule du plafond."""
    e = copy.deepcopy(E_V2)
    for key in sorted(keys_ceil):
        k, gi = CEIL[keys_ceil[key]]
        if key not in e[k][gi]:
            e[k][gi] = e[k][gi] + [key]
    return e


def seed_of(base, key, lang, p):
    return [base, zlib.crc32("|".join(key).encode()), zlib.crc32(lang.encode()), p]


def new_cells_patch(d, add, allkeys, p, base_seed):
    """Tableaux simulés des clés nouvelles d'une position : estimation ponctuelle, et tirages dans les réservoirs du
    noyau (bâtis sur la base de la position), un générateur par clé, langage et position ; NaN où la forme manque."""
    def patch(A):
        pools = build_pools(d, LANGS, sorted(needed_keys()))
        for key in sorted(allkeys):
            mean = np.full((A.nb + 1, len(LANGS)), np.nan)
            mn = np.full((A.nb + 1, len(LANGS)), np.nan)
            for l, procs in add.get(key, {}).items():
                y = proc_logs(procs)
                j = A.idx[l]
                mean[0, j], mn[0, j] = math.exp(y.mean()), math.exp(y.min())
                if A.nb:
                    g = np.random.default_rng(seed_of(base_seed, key, l, p))
                    pool = pools[(key[0], klass(l))]
                    draws = y.mean() + pool[g.integers(0, len(pool), size=(A.nb, len(y)))]
                    mean[1:, j], mn[1:, j] = np.exp(draws.mean(axis=1)), np.exp(draws.min(axis=1))
            A.t[("mean", key)], A.t[("min", key)] = mean, mn
    return patch


def r4_patch(b3):
    def patch(A):
        for est in ("mean", "min"):
            for k in K3K:
                A.t[(est, k)] = np.maximum(A.t[(est, k)], b3)
    return patch


def selection(F, fc, pos):
    """Sélection indépendante : pour chaque langage, cellule du plafond et position, la forme la plus rapide sur la
    passe 0 seule (moyenne géométrique des médianes de processus), estimée sur les passes 1 et 2 seules ; clé à part."""
    sel_keys = {ceil: (k, "sel " + ceil, "") for ceil, (k, gi) in CEIL.items()}
    adds, chosen = [], {}
    for p, (d, lt, src, _) in enumerate(pos):
        add = defaultdict(dict)
        for l in LANGS:
            cand = defaultdict(list)
            for ceil, (k, gi) in CEIL.items():
                for key in E_V2[k][gi]:
                    if key in src.get(l, {}):
                        cand[ceil].append(src[l][key])
            for build, key, ceil, form, rq in fc.get(l, []):
                size = size_of(key, p)
                b = "cv" if F.procs("cv", size, l, key) else build
                if (b, size, key) not in cand[ceil]:
                    cand[ceil].append((b, size, key))
            for ceil, lst in cand.items():
                best = None
                for b, size, key in lst:
                    rows = F.bypass.get((b, size), {}).get(l, {}).get(key, [])
                    p0 = [m for ps, m, c in rows if ps == 0]
                    if not p0:
                        continue
                    t0 = math.exp(float(np.mean(np.log(p0))))
                    if best is None or t0 < best[0]:
                        best = (t0, b, size, key)
                if best is None:
                    continue
                _, b, size, key = best
                later = [[m] for ps, m, c in F.bypass[(b, size)][l][key] if ps in (1, 2)]
                if later:
                    add[sel_keys[ceil]][l] = later
                    chosen[f"{l}|{ceil}|{POS_NAMES[p]}"] = [b, size, "|".join(key)]
        adds.append(add)
    e = copy.deepcopy(E_V2)
    for ceil, (k, gi) in CEIL.items():
        e[k][gi] = [sel_keys[ceil]]
    return e, adds, list(sel_keys.values()), chosen


# ------------------------------------------------------------------ moteur : un calcul, ses 20 000 variantes
def three(host, pos_dl, footprint, c3, ebs, e_meas=None, patches=None, wmode="three", b3=None, measures_only=False,
          a1=True, a3=True, a4=True):
    """Un calcul. host : données qui avancent le générateur principal (les mêmes pour tous les calculs) ; pos_dl : [(d,
    lt)] des trois positions ; wmode : « three » (poids des tailles égaux au centre, tirés dans les variantes) ou une
    position (0, 1, 2) de poids 1 ; b3 : R4 (référence de K3) ; measures_only : poids de la grille à 0 ; a1, a3, a4 :
    corrections de la v4.1. Les tirages de la règle de la grille (a1) et de la référence du code naturel (a3) sont
    faits puis ignorés, pour que tous les calculs gardent les mêmes tirages."""
    rng = np.random.default_rng(SEED)
    keys = sorted(needed_keys())
    Arrays3(host[0], host[1], LANGS, B, rng, build_pools(host[0], LANGS, keys))  # avance rng de la même façon
    As, refs, ebs = [], [], [dict(e) for e in ebs]
    for p, (d, lt) in enumerate(pos_dl):
        A = Arrays3(d, lt, LANGS, B, np.random.default_rng(SEED + 4100 + p), build_pools(d, LANGS, keys))
        if e_meas is not None:
            A.e_meas = e_meas
        for patch in (patches or [[], [], []])[p]:
            patch(A)
        As.append(A)
        rf = {e: references(A, e) for e in ("mean", "min")}
        if b3 is not None:
            for e in rf:
                rf[e]["tstar"][("k3", 0)] = b3
            ebs[p][("k3", 0)] = b3
        refs.append(rf)
    catw0 = {cat: w for cat, (w, _) in CATEGORIES.items()}
    C0 = c_vector(c_score(c_cells("v2", c3), catw0), LANGS)

    def wmap(w):
        if not measures_only:
            return {"C": w[0], "E": w[1], "D": w[2]}
        return {"C": 0.0, "E": w[1] / (w[1] + w[2]), "D": w[2] / (w[1] + w[2])}

    def wsz(srng_w):
        if wmode == "three":
            return srng_w
        w = np.zeros(3)
        w[wmode] = 1.0
        return w

    w0 = np.full(3, 1 / 3)
    main = dict(MAIN, d1ref="best_natural") if a3 else MAIN
    S0 = scores(As, 0, main, C0, footprint, refs, ebs, wsz(w0), wP=wmap(np.array([0.35, 0.40, 0.25])), mt_nosmall=a4)
    kernels, cat_names = list(As[1].e_meas), list(CATEGORIES)
    rk = As[1].ranked
    NR = len(RANKED)
    prec, first, ranks = np.zeros((NR, NR)), np.zeros(NR), np.empty((U, NR), np.int16)
    ms_sum = np.zeros(len(LANGS))
    srng = np.random.default_rng(SEED + 4200)  # poids des tailles : générateur à part
    for u in range(U):
        cfg = {k: v[int(rng.integers(len(v)))] for k, v in OPTS.items()}
        if a1:
            cfg["crule"] = "v2"
        if a3:
            cfg["d1ref"] = "best_natural"
        b = int(rng.integers(1, B + 1))
        wp = dirichlet(rng, 20 * np.array([0.35, 0.40, 0.25])) if rng.random() < 0.5 else dirichlet(rng, [1, 1, 1])
        wP = wmap(wp)
        wE = dict(zip(kernels, dirichlet(rng, 20 * np.full(len(kernels), 1 / len(kernels)))))
        wD = dict(zip(("D1", "D2", "D3", "D4"), dirichlet(rng, 20 * np.array([DW[k] for k in ("D1", "D2", "D3", "D4")]))))
        catw = dict(zip(cat_names, dirichlet(rng, 20 * np.array([catw0[c] for c in cat_names]))))
        prng = np.random.default_rng(int(rng.integers(2 ** 63)))
        C = c_vector(c_score(c_cells(cfg["crule"], c3, rng=prng, noise=0.10), catw), LANGS)
        wS = dirichlet(srng, 20 * w0) if srng.random() < 0.5 else dirichlet(srng, [1, 1, 1])
        S_u = scores(As, b, cfg, C, footprint, refs, ebs, wsz(wS), wE=wE, wD=wD, wP=wP, mt_nosmall=a4)
        r_ = ranks_of(S_u["MS"][rk])
        ms_sum += S_u["MS"]
        prec += r_[:, None] < r_[None, :]
        first[int(np.argmin(r_))] += 1
        ranks[u] = r_
    prec /= U
    idx = As[1].idx
    exp21 = {a: 1 + sum(prec[RANKED.index(b_), RANKED.index(a)] for b_ in RANKED if b_ != a) for a in RANKED}
    return {"exp21": exp21, "ms0": {l: float(S0["MS"][idx[l]]) for l in LANGS}, "prec": prec,
            "ms_mean": {l: float(ms_sum[idx[l]] / U) for l in LANGS},
            "first": {RANKED[j]: float(first[j] / U) for j in range(NR)},
            "rank90": {RANKED[j]: [int(np.quantile(ranks[:, j], 0.05)), int(np.quantile(ranks[:, j], 0.95))]
                       for j in range(NR)},
            "E": {l: float(S0["E"][idx[l]]) for l in LANGS}, "D": {l: float(S0["D"][idx[l]]) for l in LANGS},
            "C": {l: float(C0[idx[l]]) for l in LANGS},
            "Ek": {l: {k: float(S0["Ek"][k][idx[l]]) for k in S0["Ek"]} for l in LANGS},
            "Dparts": {l: {q: float(S0[q][idx[l]]) for q in ("D1", "D2", "D3", "D4")} for l in LANGS},
            "tstar": [{f"{k}#{i}": v for (k, i), v in rf["mean"]["tstar"].items()} for rf in refs]}


def summarize(s, by_rank=False):
    """Résumé d'un calcul : ordre (score moyen sur les variantes, puis rang moyen ; by_rank : rang moyen, puis score au
    centre, la règle du 23 novembre), rangs, scores, piliers, étages, plafond par noyau et parts du code par défaut au
    centre, part des variantes où chaque langage devance le suivant, préséances."""
    langs = LANGS
    if by_rank:
        order = sorted(langs, key=lambda l: (s["exp21"][l], -s["ms0"][l]))
    else:
        order = sorted(langs, key=lambda l: (-s["ms_mean"][l], s["exp21"][l]))
    idx = {l: i for i, l in enumerate(RANKED)}
    prec = s["prec"]
    out = {"order": order, "exp": {l: s["exp21"][l] for l in langs}, "rank90": {l: s["rank90"][l] for l in langs},
           "first": {l: s["first"][l] for l in langs}, "ms0": {l: s["ms0"][l] for l in langs},
           "ms_mean": {l: s["ms_mean"][l] for l in langs},
           "E": {l: s["E"][l] for l in langs}, "D": {l: s["D"][l] for l in langs}, "C": {l: s["C"][l] for l in langs},
           "tiers": tiers(order, prec, idx), "Ek": {l: s["Ek"][l] for l in langs}}
    out["Dparts"] = s["Dparts"]
    out["ahead_next"] = {a: float(prec[RANKED.index(a), RANKED.index(b)]) for a, b in zip(order, order[1:])}
    out["prec_full"] = {a: {b: float(prec[RANKED.index(a), RANKED.index(b)]) for b in order} for a in order}
    out["tstar"] = s["tstar"]
    return out


def run_calc(calc, F, fc, footprint, c3, ebs, b3, host, keys):
    cor = corrections(calc)
    b3ref, k3n = b3["max" if cor["a2"] else "median"][:2]
    pos = [position(F, p, calc, k3n) for p in range(3)]
    filled, missing = {}, []
    for p, (d, lt, src, miss) in enumerate(pos):
        filled[POS_NAMES[p]] = fill_missing(d, LANGS, keys)
        missing += miss
    e_meas, patches, chosen = None, [[], [], []], None
    if calc == "Sélection indépendante":
        e_meas, adds, sel, chosen = selection(F, fc, pos)
        for p in range(3):
            patches[p].append(new_cells_patch(pos[p][0], adds[p], sel, p, SEL_SEED))
    elif calc not in ("Base, trois tailles", "Sans C1"):
        adds, allc = [], {}
        for p in range(3):
            add, ceil_of, miss = additions(F, fc, p, pos[p][0])
            adds.append(add)
            allc.update(ceil_of)
            missing += miss
        e_meas = e_meas_with(allc)
        for p in range(3):
            patches[p].append(new_cells_patch(pos[p][0], adds[p], allc, p, NEW_SEED))
    r4 = calc not in ("Base, trois tailles", "Sans R4")
    if r4:
        for p in range(3):
            patches[p].append(r4_patch(b3ref))
    wmode = {"Sans les tailles (taille publiée seule)": 1, "Taille petite": 0, "Taille grande": 2}.get(calc, "three")
    s = three(host, [(d, lt) for d, lt, src, miss in pos], footprint, c3, ebs, e_meas=e_meas, patches=patches,
              wmode=wmode, b3=b3ref if r4 else None, measures_only=(calc == "Sur les seules mesures"),
              a1=cor["a1"], a3=cor["a3"], a4=cor["a4"])
    out = summarize(s, by_rank=(calc == OLD))
    out["missing"] = missing
    out["filled"] = {k: [[x[0], " ".join(x[1]).strip(), x[2]] for x in v] for k, v in filled.items()}
    if chosen is not None:
        out["chosen"] = chosen
    return out


# ------------------------------------------------------------------ descriptif
def gm(procs):
    return math.exp(float(np.mean(np.log([float(np.median(p)) for p in procs]))))


def retained(F, fc):
    """« Final » : pour chaque langage, cellule du plafond et taille, la forme la plus rapide (estimation ponctuelle),
    la meilleure forme publiée (mêmes substitutions R1 et R2 que « Final ») et leur rapport."""
    out = defaultdict(dict)
    for p in range(3):
        d, lt, src, _ = position(F, p, FINAL, {})
        for l in LANGS:
            for ceil, (k, gi) in CEIL.items():
                pub = [(gm(d[l][key]), key) for key in E_V2[k][gi] if d.get(l, {}).get(key)]
                new = []
                for build, key, c, form, rq in fc.get(l, []):
                    if c != ceil:
                        continue
                    procs = F.procs("cv", size_of(key, p), l, key) or F.procs(build, size_of(key, p), l, key)
                    if procs:
                        new.append((gm(procs), key, form))
                if not pub and not new:
                    continue
                bp = min(pub) if pub else None
                best = min([(t, key, "publiée") for t, key in pub] + new, key=lambda x: x[0])
                out[l][f"{ceil}|{POS_NAMES[p]}"] = {
                    "best_published": bp[0] if bp else None, "retained": best[0], "retained_key": "|".join(best[1]),
                    "retained_form": best[2], "ratio": best[0] / bp[0] if bp else None}
    return out


def spread(F):
    """Écart entre la passe la plus lente et la plus rapide de chaque cellule (moyennes géométriques par passe)."""
    out = []
    for (cons, size), dl in F.bypass.items():
        for l, keys in dl.items():
            for key, rows in keys.items():
                by = defaultdict(list)
                for ps, m, c in rows:
                    by[ps].append(m)
                if len(by) == 3:
                    g = [math.exp(float(np.mean(np.log(v)))) for v in by.values()]
                    out.append(max(g) / min(g))
    out = np.array(out)
    return {"cells": int(len(out)), "median": float(np.median(out)) if len(out) else None,
            "over_20pct": int((out > 1.2).sum())}


def main():
    F = load()
    c3 = json.load(open(os.path.join(ROOT, "results", "vectorization.json")))
    footprint = json.load(open(os.path.join(ROOT, "results", "footprint.json")))
    hw, machines = machines_hw(F)
    ebs = [ebounds(hw, p) for p in range(3)]
    b3 = {}  # statistique de b3 -> (b3 de référence, temps de K3 ramenés à ce b3, b3 des groupes)
    for stat in ("max", "median"):
        ref, groups, b3recs = b3_values(stat)
        b3[stat] = (ref, k3_normalized(F, ref, groups), groups)
    fc = forms_cells(LANGS)
    keys = campaign_keys({k: v for k, v in F.data.items() if k[0] == "pub"})
    hd = position(F, 1, "Base, trois tailles", {})[0]  # avance du générateur principal : la base, taille publiée
    host = (copy.deepcopy(hd), position(F, 1, "Base, trois tailles", {})[1])
    fill_missing(host[0], LANGS, keys)
    calcs = CALCS
    res = {c: run_calc(c, F, fc, footprint, c3, ebs, b3, host, keys) for c in calcs}
    fin = res[FINAL]["order"]
    moved_ = {c: moved(fin, res[c]["order"], LANGS) for c in calcs[1:]}
    out = {"results": res, "moved_more_than_2": moved_, "b3_ref": b3["max"][0],
           "b3_groups": {f"{p}|{boot}": v for (p, boot), v in b3["max"][2].items()},
           "b3_median_ref": b3["median"][0],
           "b3_median_groups": {f"{p}|{boot}": v for (p, boot), v in b3["median"][2].items()},
           "b3_records": [{k: v for k, v in r.items() if k != "outputs"} for r in b3recs],
           "machines": machines, "group_machines": {f"{p}|{k}|{s}": sorted(m for m in v if m is not None)
                                                    for (p, k, s), v in sorted(F.machines.items())},
           "bounds": [{f"{k}#{i}": v for (k, i), v in e.items()} for e in ebs], "hw": hw,
           "retained": retained(F, fc), "spread": spread(F), "failures": F.failures, "skipped": F.skipped,
           "steal_over_5pct": F.steal, "cpu_models": {m: dict(ps) for m, ps in F.models.items()}}
    # comparaisons : la méthode du 23 novembre (calcul OLD) et le classement de la v3 (tête du README jusqu'au 23)
    out["v3"] = json.load(open(os.path.join(FIN, "comparisons.json")))["v3"]
    out["moved_vs_old"] = moved(res[OLD]["order"], fin, LANGS)
    out["moved_vs_v3"] = moved(out["v3"]["order"], fin, LANGS)
    os.makedirs(OUTD, exist_ok=True)
    json.dump(out, open(OUT, "w"), indent=1, default=float)
    report(out, calcs)


# ------------------------------------------------------------------ rapport
def place(r, l):
    return r["order"].index(l) + 1


def nth(n):
    return "1er" if n == 1 else f"{n}e"


def report(o, calcs):
    R = o["results"]
    f = R[FINAL]
    L = ["# v4.1, campagne finale : le classement — résultats", "",
         "*Plans : `docs/V4_FINAL.md` (section 8, fixée avant les mesures) et `docs/V4_1.md` (corrections A1 à A4 de "
         "l'analyse, 24 novembre). Généré par `analysis/final_v4.py` à partir de `results/final/raw`, de "
         "`results/final/b3.jsonl` et du relevé des formes (`results/converge/forms.json`).*", "",
         f"Machines : {', '.join(o['machines'])} ; b3 de référence (le plus lent des 16 décalages, A2) : "
         f"{1e3 * o['b3_ref']:.2f} ms ; b3 des groupes de K3 : "
         + ", ".join(f"passe {k.split('|')[0]} {1e3 * v:.2f} ms" for k, v in sorted(o["b3_groups"].items()))
         + f" ; avec la médiane des 16 décalages (méthode du 23 novembre) : {1e3 * o['b3_median_ref']:.2f} ms.", "",
         "## Classement « Final »", "",
         "| Rang | Langage | Score | Score au centre | Rang espéré | Rang plausible | Devance le suivant | Plafond | "
         "Code par défaut | Contrôle |", "|---|---|---|---|---|---|---|---|---|---|"]
    for i, l in enumerate(f["order"]):
        ahead = f["ahead_next"].get(l)
        L.append(f"| {i + 1} | {NAMES[l]} | {f['ms_mean'][l]:.1f} | {f['ms0'][l]:.1f} | {f['exp'][l]:.2f} | "
                 f"{f['rank90'][l][0]}–{f['rank90'][l][1]} | {'—' if ahead is None else f'{100 * ahead:.0f} %'} | "
                 f"{f['E'][l]:.1f} | {f['D'][l]:.1f} | {f['C'][l]:.1f} |")
    L += ["", "Score : moyenne du score sur les variantes de l'analyse ; il fixe l'ordre. Score au centre, plafond, "
          "code par défaut et contrôle : poids et choix principaux, estimation ponctuelle. Rang espéré : rang moyen sur "
          "les variantes.", "",
          "Étages (paires ordonnées dans au moins 95 % des variantes) : "
          + " | ".join(", ".join(NAMES[l] for l in t) for t in f["tiers"]), "",
          "## Tous les calculs", "", "| Langage | " + " | ".join(calcs) + " | v3 |",
          "|---|" + "---|" * (len(calcs) + 1)]
    for l in f["order"]:
        cells = []
        for c in calcs:
            p = place(R[c], l)
            mark = "" if c == FINAL or abs(p - place(f, l)) <= 2 else " **"
            cells.append(f"{p}{mark}")
        cells.append(str(o["v3"]["order"].index(l) + 1))
        L.append(f"| {NAMES[l]} | " + " | ".join(cells) + " |")
    L += ["", "Chaque case : place dans le calcul ; ** : plus de deux places d'écart avec « Final ». Ordre des lignes : "
          "« Final ». « Sans A1 » à « Sans A4 » : « Final » sans une correction de la v4.1 ; « Méthode du 23 novembre » : "
          "sans aucune et classée au rang moyen, le classement publié le 23 novembre ; v3 : le classement publié "
          "jusqu'au 23 novembre.", "",
          "## Rangs qui bougent de plus de deux places par rapport à « Final »", ""]
    for c in calcs[1:]:
        mv = o["moved_more_than_2"][c]
        L.append(f"* {c} : " + (", ".join(f"{NAMES[l]} {nth(b)} (Final {nth(a)})" for l, (a, b) in
                                         sorted(mv.items(), key=lambda x: x[1][0])) or "aucun"))
    for name, mv in (("la méthode du 23 novembre", o["moved_vs_old"]), ("le classement de la v3", o["moved_vs_v3"])):
        L.append(f"* Final contre {name} : " + (", ".join(f"{NAMES[l]} {nth(a)} → {nth(b)}" for l, (a, b) in
                                                          sorted(mv.items(), key=lambda x: x[1][1])) or "aucun"))
    L += ["", "## Plafond par noyau et parts du code par défaut (« Final », au centre)", "",
          "| Langage | " + " | ".join(k.upper() for k in E_V2) + " | D1 | D2 | D3 | D4 |",
          "|---|" + "---|" * (len(E_V2) + 4)]
    for l in f["order"]:
        L.append(f"| {NAMES[l]} | " + " | ".join(f"{100 * f['Ek'][l][k]:.0f}" for k in E_V2) + " | "
                 + " | ".join(f"{100 * f['Dparts'][l][q]:.0f}" for q in ("D1", "D2", "D3", "D4")) + " |")
    L += ["", "## Forme retenue par « Final », cellule par cellule et taille par taille (estimation ponctuelle)", "",
          "Chaque case : forme retenue aux tailles petite / publiée / grande (« pub » : une variante publiée) ; rapport "
          "de son temps à la meilleure forme publiée, à la taille publiée.", "",
          "| Langage | " + " | ".join(CEIL) + " |", "|---|" + "---|" * len(CEIL)]
    for l in f["order"]:
        row = []
        for ceil in CEIL:
            xs = [o["retained"].get(l, {}).get(f"{ceil}|{n}") for n in POS_NAMES]
            if not any(xs):
                row.append("–")
                continue
            names = "/".join((x["retained_form"].replace("publiée", "pub") if x else "–") for x in xs)
            r = xs[1]["ratio"] if xs[1] and xs[1]["ratio"] else None
            row.append(names + (f" {r:.2f}" if r else ""))
        L.append(f"| {NAMES[l]} | " + " | ".join(row) + " |")
    sp = o["spread"]
    L += ["", "## Campagne", "", f"Écart entre la passe la plus lente et la plus rapide d'une cellule : médiane "
          f"{100 * (sp['median'] - 1):.1f} % ; {sp['over_20pct']} cellules sur {sp['cells']} au-delà de 20 %."
          if sp["median"] else "", "", "Machine de chaque groupe et de chaque passe :", ""]
    gm_ = defaultdict(list)
    for k, v in o["group_machines"].items():
        gm_["/".join(v)].append(k.replace("|", " "))
    for m, gl in gm_.items():
        L.append(f"* machine {m} : {len(gl)} groupes")
    L += ["", "## Cellules", ""]
    for c in calcs:
        r = R[c]
        nf = sum(len(v) for v in r["filled"].values())
        if r["missing"] or nf:
            L.append(f"* {c} : formes ou cellules substituées manquantes : "
                     + (", ".join(f"{NAMES.get(x[0], x[0])} {x[1]} {x[2]} ({x[3]})" for x in r["missing"]) or "aucune")
                     + " ; cellules de la base remplies (temps le plus lent des autres langages) : "
                     + (", ".join(f"{NAMES.get(x[0], x[0])} {x[1]} ({t})" for t, v in r["filled"].items() for x in v)
                        or "aucune"))
    cm = o["cpu_models"]
    L += ["", "Processeur des enregistrements : " + " ; ".join(
        f"{m} ({sum(ps.values())} enregistrements)" for m, ps in cm.items())
          + (" — **plusieurs modèles**" if len(cm) > 1 else "") + ".", "",
          f"Processus écartés : {len(o['failures'])} ; cellules non exécutées (étalonnage hors mémoire ou hors durée) : "
          f"{len(o['skipped'])} ; vol de temps > 5 % après reprise : {len(o['steal_over_5pct'])}."]
    for x in o["failures"]:
        L.append(f"* {NAMES.get(x['lang'], x['lang'])} {x['construction']} {x['size']} {' '.join(x['key'])} passe "
                 f"{x['pass']} : code {x['returncode']}, contrôles {x['oks']}{', hors mémoire' if x['oom'] else ''}"
                 f"{', durée' if x['timeout'] else ''}")
    sk = defaultdict(set)
    for x in o["skipped"]:
        sk[(x["lang"], x["construction"], x["size"], " ".join(x["key"]))].add(x["status"])
    for (l, c, s, k), st in sorted(sk.items()):
        L.append(f"* non exécutée : {NAMES.get(l, l)} {c} {s} {k} ({', '.join(sorted(st))})")
    open(REPORT, "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
