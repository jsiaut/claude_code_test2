#!/usr/bin/env python3
"""Le classement : calcul complet, de results/final/raw à results/report_final.md (v5.4).

Méthode : docs/METHOD.md ; plans fixés avant les calculs : docs/V4_FINAL.md, section 8 (campagne finale de la v4),
docs/V4_1.md (corrections A1 à A4 de l'analyse), docs/V5.md (campagne rejouée : corrections A5 et A6, C par gcc,
réplication), docs/V5_1.md (A7 et A8 : mode du code naturel tiré au sort), docs/V5_2.md (Zig par sa version de
développement) et docs/V5_4.md (Go mesuré hors de l'expérience simd). Ce module est autonome : il lit les mesures de
la campagne (results/final/raw, tools/final/campaign.py), les remesures de Zig (results/zig_dev/raw) et de Go
(results/go_std/raw), b3 (results/final/b3.jsonl), les bornes physiques
des machines qui ont mesuré (results/hw/machine<N>), le relevé des formes (results/converge/forms.json), l'empreinte
de K1 (results/footprint.json) et la grille de contrôle (analysis/capabilities.py, analysis/capabilities_v2.py ; la
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
  manquante : absente de son ensemble, signalée ;
* A5 : l'effet commun d'un groupe (noyau, taille) dans une passe, écart de vitesse de la machine d'une passe à
  l'autre, est retiré des logarithmes des temps avant de calculer les résidus du rééchantillonnage ; les estimations
  ponctuelles ne changent pas ;
* A6 : la borne physique des mesures à quatre fils vient de la sonde corrigée (stream.txt ou stream4.txt de la
  machine ; pour une machine qui n'en a pas, médiane des relevés corrigés des machines de la campagne, à défaut des
  machines du même modèle, à défaut de toutes) ;
* A7, A8 : dans chaque variante, le mode du code naturel est tiré parmi trois, à probabilité 1/3 : R1, le mode publié
  de chaque chaîne (les données du calcul « Sans R1 ») ou R1' (celles de « R1' au lieu de R1 ») ; le tirage vient d'un
  générateur à part, les autres tirages ne changent pas ; au centre, le code naturel reste sous R1. Sans A8 : tirage
  entre les deux premiers modes, à probabilité 1/2 (le classement publié le 26 novembre à 15 h).
* Zig (docs/V5_2.md) : par exception, ses cellules sont celles de sa version de développement. Elle est mesurée hors
  campagne, à côté d'un témoin (la version de la campagne, remesurée dans les mêmes groupes) ; chaque processus de Zig
  de la campagne est multiplié par le rapport de sa cellule, moyenne géométrique des rapports appariés (même passe,
  même copie) du temps sous la version de développement au temps du témoin ; ce rapport est rééchantillonné avec les
  mesures. Les latences de K8 naturel restent celles de la campagne (docs/V5_2.md, 8 : leurs rapports ne se
  distinguent pas du bruit). « Zig 0.17 » : le même calcul avec les cellules de la campagne ; FINAL_ZIG17=1 : sans
  l'exception.
* Go (docs/V5_4.md) : la campagne a mesuré tout son banc dans un binaire compilé avec GOEXPERIMENT=simd, où la
  préemption asynchrone de Go 1.27 fausse les boucles qui mêlent SSE et VEX. Quinze cellules de K1 en sont faussées
  d'un facteur 40 ou plus (K1 naturel et naturel permuté dans ses deux modes, K1 AoS, aux trois tailles). Go est
  remesuré hors campagne dans sa configuration corrigée (ces variantes dans un binaire standard), à côté de C. Chaque
  cellule faussée abandonne ses temps de la campagne : elle prend les processus d'une cellule de C dans la campagne
  (K1 naturel, ou K1 naturel permuté), multipliés par le rapport apparié (même passe) du temps de Go au temps de cette
  cellule de C ; ce rapport est rééchantillonné avec les mesures. Les autres cellules de Go ne changent pas, K7
  naturel à la grande taille compris, que le même artefact ralentit plus faiblement (docs/V5_4.md, 9). « Go de la
  campagne » : le même calcul sans cette correction ; « Go, toutes les cellules » : les autres cellules ramenées
  elles aussi, par le binaire de la campagne pris pour témoin ; FINAL_GOSIMD=1 : sans la correction. « Campagne telle
  que mesurée » : ni l'exception de Zig ni la correction de Go.
Sensibilités (CALCS) : Base, trois tailles ; sans les tailles, sans R1, sans R2, sans C1, sans R4 ; R1' au lieu de R1 ;
une taille à la fois ; sélection indépendante ; D3 et D4 sur trois processus ; sur les seules mesures ; sans une
correction à la fois (Sans A1 à Sans A8) ; « Méthode du 23 novembre », sans aucune et classée au rang moyen ; « C par
gcc », quand la campagne porte les constructions de C par gcc ; « Zig 0.17 », quand Zig est remesuré par sa version
de développement ; « Go de la campagne », quand Go est remesuré. Les tirages des variantes viennent du même générateur,
avancé de la même façon pour tous les calculs : ils sont identiques d'un calcul à l'autre. Réplication : la campagne
précédente, telle qu'elle était publiée et recalculée par cette méthode (comparisons.json de la campagne), comparée
à la campagne telle que mesurée. Effet de
machine : les cellules mesurées sur plusieurs machines de la campagne, rapportées à la première.

Lectures du classement (docs/V5_3.md), sans effet sur les scores : « ce qui décide de l'ordre », la part de la variance
du score au centre que porte chaque pilier, chaque noyau et chaque part de D, dans quatre groupes de langages
(importance) ; « tri des écarts », chaque cellule du code naturel rapportée à la médiane de quinze pairs, les couples
signalés et la cause que le registre TRI_CAUSES donne à chacun (triage).

Sorties : results/final/analysis.json, results/report_final.md. Variables : BOOT (2000 rééchantillonnages), UA (20 000
variantes), FINAL_DIR (répertoire d'une autre campagne), FINAL_RAW (autres données), FINAL_OUT (autre répertoire de
sortie), FINAL_ZIG17 (sans l'exception de Zig), FINAL_GOSIMD (sans la correction de Go). « --extract <fichier> <note> »
et « --extract-same <fichier> <note> » :
extraits du calcul déjà écrit, pour la réplication d'une campagne suivante (classement publié ; recalcul par la méthode
de la suivante). Contrôle : tools/check.sh."""
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
DRAW_SEED = SEED + 4300  # A7, A8 : tirage du mode du code naturel de chaque variante, générateur à part
FIN = os.path.join(ROOT, os.environ.get("FINAL_DIR", os.path.join("results", "final")))  # répertoire de la campagne
RAW = os.environ.get("FINAL_RAW", os.path.join(FIN, "raw"))
B3F = os.path.join(os.path.dirname(RAW), "b3.jsonl")
FORMS = os.path.join(ROOT, "results", "converge", "forms.json")
OUTD = os.environ.get("FINAL_OUT", FIN)
OUT = os.path.join(OUTD, "analysis.json")
REPORT = os.path.join(OUTD, "report_final.md") if "FINAL_OUT" in os.environ else os.path.join(ROOT, "results",
                                                                                               "report_final.md")
FINAL = "Final"
OLD = "Méthode du 23 novembre"  # sans aucune correction (A1 à A8), classée au rang moyen
A_OFF = {"Sans A1": "a1", "Sans A2": "a2", "Sans A3": "a3", "Sans A4": "a4", "Sans A5": "a5", "Sans A6": "a6",
         "Sans A7": "a7", "Sans A8": "a8"}
CALCS = [FINAL, "Base, trois tailles", "Sans les tailles (taille publiée seule)", "Sans R1", "Sans R2", "Sans C1",
         "Sans R4", "R1' au lieu de R1", "Taille petite", "Taille grande", "Sélection indépendante",
         "D3 et D4 sur trois processus", "Sur les seules mesures"] + list(A_OFF) + [OLD]
MT_MEASURES = {("k6", 2), ("k6", 3), ("k9", 1)}  # mesures à quatre fils : Q6 mt, Q1 mt, K9 mt (A4)
GCC_CALC = "C par gcc"  # « Final » où les cellules de C viennent de ses constructions par gcc (docs/V5.md, S2)
GCC_VIEW = {"c": {"gcc": "pub", "gcc_cv": "cv", "gcc_chk": "chk"}}
# calculs dont le mode du code naturel est fixé, sans tirage (A7) : pas de R1, mode publié partout, R1' partout
NO_DRAW = ("Base, trois tailles", "Sans R1", "R1' au lieu de R1")
DRAW_MODES = ("R1", "mode publié", "R1'")  # modes du tirage, dans l'ordre du générateur ; sans A8 : les deux premiers
# Zig par sa version de développement (docs/V5_2.md) : remesure à côté de la campagne, avec son témoin
DEV_LANG = "zig"
DEV_DIR = os.path.join(os.path.dirname(FIN), "zig_dev")
DEV_VIEW = {"dev": "pub", "dev_cv": "cv", "dev_chk": "chk"}  # étiquette de la remesure -> étiquette de la campagne
DEV_SEED = SEED + 4600  # rééchantillonnage du rapport au témoin : un générateur par cellule
ZIG17 = "Zig 0.17"  # « Final » avec les cellules de Zig de la campagne, mesurées par sa version stable
ZIGV = "Zig 0.18, K4 et K9 seuls"  # « Final » où seules les cellules de K4 et de K9 de Zig sont ramenées par le témoin
ZIGL = "Zig 0.18, latences du plan"  # « Final » où les latences de K8 naturel de Zig sont ramenées elles aussi
# Go hors de l'expérience simd (docs/V5_4.md) : remesure à côté de la campagne, avec le binaire de la campagne pour
# témoin et le C pour pont des cellules que la préemption asynchrone faussait
GO_LANG = "go"
GO_DIR = os.path.join(os.path.dirname(FIN), "go_std")
GO_VIEW = {"wit": "pub", "wit_cv": "cv", "wit_unc": "unc", "wit_cv_unc": "cv_unc"}  # témoin -> étiquette de la campagne
GO_SEED = SEED + 4700  # rééchantillonnage du rapport au pont (ou au témoin) : un générateur par cellule
GO_BRIDGE = ("c", "pub")  # pont : langage et étiquette de ses cellules
GO_FIXED = {K1N: K1N, K1S: K1S, ("k1", "aos", "energy"): K1N}  # cellule faussée de Go -> cellule du pont
GOC = "Go de la campagne"  # « Final » sans la correction de Go : le classement de la v5.2 et de la v5.3
GOALL = "Go, toutes les cellules"  # « Final » où les autres cellules de Go sont ramenées par leur propre témoin
MEAS = "Campagne telle que mesurée"  # ni exception de Zig ni correction de Go : le classement du 26 novembre à 17 h


def corrections(calc):
    """Corrections appliquées dans un calcul. v4.1 (docs/V4_1.md, 3) : A1 (grille en règle v2 dans toutes les
    variantes), A2 (b3 : le plus lent des 16 décalages), A3 (code naturel rapporté au meilleur code naturel), A4
    (mesures à quatre fils sans la petite taille). v5 (docs/V5.md, 8) : A5 (effet commun d'un groupe d'une passe
    retiré des résidus), A6 (borne à quatre fils : relevé de la sonde corrigée). v5.1 (docs/V5_1.md, 3 et 9) : A7 (mode
    du code naturel tiré au sort dans chaque variante), A8 (tirage entre trois modes, R1, mode publié et R1' ; sans A8,
    entre les deux premiers ; sans A7, pas de tirage : R1)."""
    names = ("a1", "a2", "a3", "a4", "a5", "a6", "a7", "a8")
    if calc == OLD:
        return dict.fromkeys(names, False)
    return {a: A_OFF.get(calc) != a for a in names}


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
class Proc(list):
    """Un processus retenu : [médiane de ses répétitions]. Attributs : ps (passe), cp (copie), machine, boot
    (démarrage), b (effet commun de son groupe dans sa passe, en logarithme : A5, block_effects), dev (cellule de Zig
    ou de Go ramenée à la campagne : graine et rapports appariés au témoin ou au pont, apply_dev et apply_go)."""
    ps, cp, machine, boot, b, dev = None, 0, None, None, 0.0, None

    def like(self, value):
        """Un processus de mêmes attributs et d'une autre valeur."""
        q = Proc([value])
        q.__dict__.update(self.__dict__)
        return q


class Data:
    """Mesures de la campagne : data[(construction, taille)][langage][clé] = [processus (Proc)] ; latences de K8
    naturel (lat) ; blocks : effet commun de chaque groupe (noyau, taille) dans chaque passe (A5)."""

    def __init__(self):
        self.data = defaultdict(lambda: defaultdict(dict))
        self.lat = defaultdict(lambda: defaultdict(dict))
        self.failures, self.skipped, self.steal = [], [], []
        self.models, self.machines = defaultdict(lambda: defaultdict(int)), defaultdict(set)
        self.gcc = 0  # enregistrements des étiquettes gcc laissés de côté
        self.gcc_models = defaultdict(int)  # leur processeur
        self.blocks = {}

    def procs(self, cons, size, lang, key):
        return self.data.get((cons, size), {}).get(lang, {}).get(key)


def load(view=None):
    """Un processus est retenu s'il a fini sans erreur, sans dépassement de mémoire ni de durée, et si toutes ses
    sommes de contrôle sont justes ; il est représenté par la médiane de ses répétitions. Les étiquettes gcc (C par gcc)
    sont à part : sans view, elles sont ignorées ; avec view = {langage: {étiquette lue: étiquette remplacée}}, leurs
    enregistrements prennent la place de ceux de l'étiquette remplacée (GCC_VIEW)."""
    F = Data()
    for f in sorted(glob.glob(os.path.join(RAW, "*.jsonl"))):
        for line in open(f):
            r = json.loads(line)
            swap = (view or {}).get(r["lang"], {})
            if r["construction"] in swap:
                r["construction"] = swap[r["construction"]]
            elif r["construction"] in swap.values() or r["construction"].startswith("gcc"):
                if r["construction"].startswith("gcc"):
                    F.gcc += 1
                    F.gcc_models[r.get("cpu_model", "?")] += 1
                continue
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
            q = Proc([r["median"]])
            q.ps, q.cp, q.machine, q.boot = r["pass"], r.get("copy", 0), r.get("machine"), r.get("boot_id")
            F.data[tag][r["lang"]].setdefault(key, []).append(q)
            if key == K8N:
                F.lat[tag][r["lang"]].setdefault(key, []).append((r.get("copy", 0), r.get("lat", [])))
    F.blocks = block_effects(F.data)
    return F


def dev_ratios():
    """Remesure de Zig par sa version de développement (docs/V5_2.md, 3 et 4), si la campagne en a une. Pour chaque
    cellule (étiquette, taille, clé) : les logarithmes des rapports appariés (même passe, même copie) du temps sous la
    version de développement au temps du témoin, et la moyenne géométrique du témoin sur ces paires. Latences de K8
    naturel : rapport des médianes de chaque colonne, toutes répétitions confondues. Un processus compte s'il est
    retenu au sens de load. Sans remesure, ou sous FINAL_ZIG17 : None."""
    raw = os.path.join(DEV_DIR, "raw", DEV_LANG + ".jsonl")
    if os.environ.get("FINAL_ZIG17") or not os.path.exists(raw):
        return None
    t, lat = defaultdict(lambda: ({}, {})), defaultdict(lambda: ([], []))
    machines, invalid, n = set(), [], [0, 0]
    for line in open(raw):
        r = json.loads(line)
        side = int(r["construction"] in DEV_VIEW)  # 0 : témoin, 1 : version de développement
        key = (r["kernel"], r["variant"], r["param"])
        cell = (DEV_VIEW.get(r["construction"], r["construction"]), r["size"], key)
        ok = (not r.get("skipped") and r.get("returncode") == 0 and not r.get("oom") and not r.get("timeout")
              and r.get("n", 0) > 0 and r.get("oks") == ["True"])
        if not ok:
            invalid.append([r["construction"], r["size"], "|".join(key), r.get("pass")])
            continue
        n[side] += 1
        machines.add(r.get("machine"))
        t[cell][side][(r["pass"], r.get("copy", 0))] = r["median"]
        if key == K8N:
            lat[cell[:2]][side].extend(r.get("lat", []))
    logs, witness = {}, {}
    for cell, (w, d) in t.items():
        pairs = sorted(set(w) & set(d))
        if pairs:
            logs[cell] = np.array([math.log(d[k] / w[k]) for k in pairs])
            witness[cell] = math.exp(float(np.mean([math.log(w[k]) for k in pairs])))
    latr = {tag: np.median(np.asarray(d, float), axis=0) / np.median(np.asarray(w, float), axis=0)
            for tag, (w, d) in lat.items() if w and d}
    return {"logs": logs, "witness": witness, "lat": latr, "machines": sorted(m for m in machines if m is not None),
            "invalid": invalid, "processes": n}


def apply_dev(F, dev, only=None, lat=False):
    """Cellules de Zig ramenées aux conditions de la campagne (docs/V5_2.md, 4) : chaque processus de la campagne est
    multiplié par le rapport de sa cellule (moyenne géométrique de ses rapports appariés) et garde ces rapports, que
    dev_noise rééchantillonne. Une cellule sans rapport est retirée : elle est absente pour Zig. Renvoie les cellules
    retirées. only : noyaux auxquels le transport est limité (les autres cellules restent celles de la campagne).
    lat : chaque colonne des latences de K8 naturel est multipliée par son rapport, comme le prévoyait le plan ; par
    défaut, elles restent celles de la campagne (docs/V5_2.md, 8)."""
    absent = []
    for (cons, size), dl in F.data.items():
        keys = dl.get(DEV_LANG, {})
        for key in sorted(keys):
            if only is not None and key[0] not in only:
                continue
            logs = dev["logs"].get((cons, size, key))
            if logs is None:
                del keys[key]
                absent.append([cons, size, "|".join(key)])
                continue
            rho, seed = math.exp(float(logs.mean())), [DEV_SEED, zlib.crc32("|".join((cons, size) + key).encode())]
            keys[key] = [q.like(q[0] * rho) for q in keys[key]]
            for q in keys[key]:
                q.dev = (seed, logs)
    for tag, dl in F.lat.items():
        lp = dl.get(DEV_LANG, {})
        if K8N in lp and lat:
            if tag in dev["lat"] and (tag[0], tag[1], K8N) in dev["logs"]:
                lp[K8N] = [(c, (np.asarray(rows, float) * dev["lat"][tag]).tolist() if len(rows) else rows)
                           for c, rows in lp[K8N]]
            else:
                del lp[K8N]
    return absent


def dev_noise(procs, nb):
    """Facteurs, pour les nb rééchantillonnages, du rapport au témoin d'une cellule de Zig ramenée à la campagne
    (docs/V5_2.md, 4) : ses rapports appariés sont tirés avec remise par un générateur propre à la cellule, et leur
    moyenne est rapportée à celle de l'estimation ponctuelle. 1 pour toute autre cellule."""
    dev = getattr(procs[0], "dev", None)
    if dev is None:
        return 1.0
    seed, logs = dev
    pick = np.random.default_rng(seed).integers(0, len(logs), size=(nb, len(logs)))
    return np.exp(logs[pick].mean(axis=1) - logs.mean())


def dev_summary(dev, F17):
    """Remesure de Zig, pour le rapport : version, machines, processus retenus, et pour chaque cellule son rapport au
    témoin, ses paires, l'écart type de leurs logarithmes et le rapport du témoin à ses temps de la campagne."""
    ver, p = "?", os.path.join(DEV_DIR, "toolchains.txt")
    if os.path.exists(p):
        for line in open(p):
            if line.startswith(DEV_LANG + "-dev"):
                ver = line.split(None, 1)[1].strip()
    cells = {}
    for (cons, size, key), logs in sorted(dev["logs"].items()):
        camp = F17.procs(cons, size, DEV_LANG, key)
        cells["|".join((cons, size) + key)] = {
            "rho": math.exp(float(logs.mean())), "pairs": len(logs),
            "sd": float(logs.std(ddof=1)) if len(logs) > 1 else 0.0,
            "witness_vs_campaign": dev["witness"][(cons, size, key)] / gm(camp) if camp else None}
    w = [c["witness_vs_campaign"] for c in cells.values() if c["witness_vs_campaign"]]
    return {"version": ver, "machines": dev["machines"], "processes": dev["processes"], "invalid": dev["invalid"],
            "absent": dev["absent"], "cells": cells,
            "lat": {"|".join(tag): [float(x) for x in v] for tag, v in sorted(dev["lat"].items())},
            "witness_vs_campaign": {"median": float(np.median(w)), "min": float(min(w)), "max": float(max(w)),
                                    "within_10pct": float(np.mean([abs(math.log(x)) <= math.log(1.10) for x in w]))}}


def go_ratios():
    """Remesure de Go hors de l'expérience simd (docs/V5_4.md, 3), si la campagne en a une. Trois côtés, mesurés dans
    les mêmes groupes : Go dans sa nouvelle configuration (étiquettes de la campagne), son témoin, le binaire de la
    campagne (étiquettes de GO_VIEW), et le pont, C (GO_BRIDGE), pour les cellules faussées (GO_FIXED). Pour chaque
    cellule (étiquette, taille, clé) de Go : logs, les logarithmes des rapports appariés (même passe, même copie) de
    la nouvelle configuration au témoin ; pour chaque cellule faussée : fixed, ceux de la nouvelle configuration à la
    cellule du pont. Un processus compte s'il est retenu au sens de load. Sans remesure, ou sous FINAL_GOSIMD : None."""
    raw = os.path.join(GO_DIR, "raw")
    if os.environ.get("FINAL_GOSIMD") or not os.path.exists(os.path.join(raw, GO_LANG + ".jsonl")):
        return None
    t, c = defaultdict(lambda: ({}, {})), defaultdict(dict)
    machines, invalid, n = set(), [], [0, 0, 0]  # processus retenus : témoin, nouvelle configuration, pont
    for lang in (GO_LANG, GO_BRIDGE[0]):
        path = os.path.join(raw, lang + ".jsonl")
        for line in (open(path) if os.path.exists(path) else ()):
            r = json.loads(line)
            key = (r["kernel"], r["variant"], r["param"])
            if lang != GO_LANG and (r["construction"] != GO_BRIDGE[1] or key not in GO_FIXED.values()):
                continue
            ok = (not r.get("skipped") and r.get("returncode") == 0 and not r.get("oom") and not r.get("timeout")
                  and r.get("n", 0) > 0 and r.get("oks") == ["True"])
            if not ok:
                invalid.append([lang, r["construction"], r["size"], "|".join(key), r.get("pass")])
                continue
            machines.add(r.get("machine"))
            pc = (r["pass"], r.get("copy", 0))
            if lang != GO_LANG:
                n[2] += 1
                c[(r["size"], key)][pc] = r["median"]
            else:
                side = int(r["construction"] not in GO_VIEW)  # 0 : témoin, 1 : nouvelle configuration
                n[side] += 1
                t[(GO_VIEW.get(r["construction"], r["construction"]), r["size"], key)][side][pc] = r["median"]
    logs, witness, fixed = {}, {}, {}
    for cell, (w, d) in t.items():
        pairs = sorted(set(w) & set(d))
        if pairs:
            logs[cell] = np.array([math.log(d[k] / w[k]) for k in pairs])
            witness[cell] = math.exp(float(np.mean([math.log(w[k]) for k in pairs])))
        b = c.get((cell[1], GO_FIXED.get(cell[2])), {})
        pairs = sorted(set(b) & set(d))
        if pairs:
            fixed[cell] = np.array([math.log(d[k] / b[k]) for k in pairs])
    return {"logs": logs, "witness": witness, "fixed": fixed, "machines": sorted(m for m in machines if m is not None),
            "invalid": invalid, "processes": n}


def apply_go(F, go, Fm, all_cells=False):
    """Cellules de Go corrigées (docs/V5_4.md, 3.3). Une cellule faussée (GO_FIXED) abandonne ses temps de la
    campagne : elle prend les processus de la cellule du pont dans la campagne telle que mesurée (Fm), chacun
    multiplié par le rapport de la cellule au pont (moyenne géométrique de ses rapports appariés), et garde ces
    rapports, que dev_noise rééchantillonne. all_cells : chaque autre cellule de Go est en plus ramenée par son propre
    témoin, comme celles de Zig. Renvoie les cellules faussées restées sans rapport : elles gardent leurs temps de la
    campagne."""
    absent = []
    for (cons, size), dl in F.data.items():
        keys = dl.get(GO_LANG, {})
        for key in sorted(keys):
            cell = (cons, size, key)
            if key in GO_FIXED:
                logs, base = go["fixed"].get(cell), Fm.procs(GO_BRIDGE[1], size, GO_BRIDGE[0], GO_FIXED[key])
                if logs is None or not base:
                    absent.append([cons, size, "|".join(key)])
                    continue
            elif all_cells and cell in go["logs"]:
                logs, base = go["logs"][cell], keys[key]
            else:
                continue
            rho, seed = math.exp(float(logs.mean())), [GO_SEED, zlib.crc32("|".join((cons, size) + key).encode())]
            keys[key] = [q.like(q[0] * rho) for q in base]
            for q in keys[key]:
                q.dev = (seed, logs)
    return absent


def go_summary(go, Fm, F):
    """Remesure de Go, pour le rapport : machines, processus retenus ; pour chaque cellule faussée, son rapport au
    pont, ses paires, l'écart type de leurs logarithmes, son temps de la campagne et son temps corrigé, et l'artefact,
    rapport apparié du témoin à la nouvelle configuration (moyenne géométrique et plus petit des rapports) ; pour
    chaque autre cellule, son rapport au témoin ; pour toutes, le rapport du témoin à ses temps de la campagne. Fm :
    la campagne telle que mesurée ; F : avec la correction."""
    sd = lambda x: float(x.std(ddof=1)) if len(x) > 1 else 0.0  # noqa: E731
    fixed, cells = {}, {}
    for (cons, size, key), logs in sorted(go["fixed"].items()):
        camp, new = Fm.procs(cons, size, GO_LANG, key), F.procs(cons, size, GO_LANG, key)
        own = go["logs"].get((cons, size, key))
        fixed["|".join((cons, size) + key)] = {
            "rho": math.exp(float(logs.mean())), "pairs": len(logs), "sd": sd(logs),
            "campaign": gm(camp) if camp else None, "corrected": gm(new) if new else None,
            "artifact": None if own is None else math.exp(-float(own.mean())),
            "artifact_min": None if own is None else math.exp(-float(own.max())),
            "witness_vs_campaign": go["witness"][(cons, size, key)] / gm(camp) if camp and own is not None else None}
    for (cons, size, key), logs in sorted(go["logs"].items()):
        if key in GO_FIXED:
            continue
        camp = Fm.procs(cons, size, GO_LANG, key)
        cells["|".join((cons, size) + key)] = {
            "rho": math.exp(float(logs.mean())), "pairs": len(logs), "sd": sd(logs),
            "witness_vs_campaign": go["witness"][(cons, size, key)] / gm(camp) if camp else None}
    rho = [x["rho"] for x in cells.values()]
    w = [x["witness_vs_campaign"] for x in cells.values() if x["witness_vs_campaign"]]
    stat = lambda v: {"median": float(np.median(v)), "min": float(min(v)), "max": float(max(v)),  # noqa: E731
                      "within_10pct": float(np.mean([abs(math.log(x)) <= math.log(1.10) for x in v]))} if v else None
    return {"machines": go["machines"], "processes": go["processes"], "invalid": go["invalid"], "absent": go["absent"],
            "fixed": fixed, "cells": cells, "rho": stat(rho), "witness_vs_campaign": stat(w),
            "outside": sorted(k for k, x in cells.items() if not 0.8 <= x["rho"] <= 1.25)}


def block_effects(data):
    """A5 (docs/V5.md, 8) : effet commun de chaque groupe (noyau, taille) dans chaque passe, inscrit dans ses processus
    (attribut b) et renvoyé : {(noyau, taille): {passe: effet}}. Un groupe d'une passe est mesuré en entier sur une
    machine : l'effet est la médiane, sur les cellules du groupe mesurées dans toutes ses passes, de l'écart entre la
    moyenne des logarithmes des temps de la cellule dans la passe et la moyenne de ses moyennes par passe."""
    cells = defaultdict(list)  # (noyau, taille) -> une ligne par cellule : {passe: moyenne des logarithmes}
    for (cons, size), dl in data.items():
        for l, keys in dl.items():
            for key, procs in keys.items():
                by = defaultdict(list)
                for q in procs:
                    by[q.ps].append(math.log(q[0]))
                cells[(key[0], size)].append({ps: float(np.mean(v)) for ps, v in by.items()})
    out = {}
    for g, rows in cells.items():
        passes = sorted({ps for row in rows for ps in row})
        full = [row for row in rows if len(row) == len(passes)]
        out[g] = {ps: float(np.median([row[ps] - np.mean([row[x] for x in passes]) for row in full])) if full else 0.0
                  for ps in passes}
    for (cons, size), dl in data.items():
        for l, keys in dl.items():
            for key, procs in keys.items():
                for q in procs:
                    q.b = out[(key[0], size)][q.ps]
    return out


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
                out[tag][l][key] = [q.like(q[0] * b3ref / b3g[(q.ps, q.boot)]) for q in procs]
    block_effects(out)  # A5 : l'effet commun qui reste une fois les temps ramenés à b3
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
                d[l][key] = [p.like(p[0]) for p in d[slow][key]]
                filled.append((l, key, slow))
    return filled


# ------------------------------------------------------------------ bornes physiques des machines
def hw_numbers(path):
    """Caractérisation d'une machine (tools/sizes/hwchar.sh, tools/hwprobe.c) : bande passante en lecture sur 1 thread
    selon la taille (bw), STREAM triad sur 4 threads, pic FMA et fréquence. STREAM sur 4 threads (A6) : stream4 est le
    relevé de la sonde corrigée (lignes « relevés par les fils » de stream.txt ou de stream4.txt), None s'il n'y en a
    pas ; stream4_0 est le relevé d'origine (à défaut, le corrigé) ; model : famille/modèle/révision du processeur."""
    bw = []
    for line in open(os.path.join(path, "bw.txt")):
        m = re.match(r"bw:\s+(\d+) KiB\s+([\d.]+) GB/s", line)
        if m:
            bw.append((int(m.group(1)) * 1024, float(m.group(2)) * 1e9))
    s4, s40 = [], []
    for f in ("stream.txt", "stream4.txt"):
        fp = os.path.join(path, f)
        for line in open(fp) if os.path.exists(fp) else []:
            m = re.search(r"stream: T=(\d)\s+(\w+)\s+([\d.]+) GB/s", line)
            if m and m.group(1) == "4" and m.group(2) == "triad":  # triad : la figure de mérite de STREAM
                (s4 if "par les fils" in line else s40).append(float(m.group(3)) * 1e9)
    peak = []
    for line in open(os.path.join(path, "peak.txt")):
        m = re.search(r"([\d.]+) GFLOP/s", line)
        if m:
            peak.append(float(m.group(1)) * 1e9)
    freq = [float(m.group(1)) * 1e9 for line in open(os.path.join(path, "freq.txt"))
            for m in [re.search(r"freq: ([\d.]+) GHz", line)] if m]
    cpu, lp = {}, os.path.join(path, "lscpu.txt")
    for line in open(lp) if os.path.exists(lp) else []:
        m = re.match(r"(CPU family|Model|Stepping):\s+(\d+)", line)
        if m:
            cpu[m.group(1)] = m.group(2)
    return {"bw": sorted(bw), "stream4": max(s4) if s4 else None, "stream4_0": max(s40 or s4), "peak": max(peak),
            "freq": max(freq), "model": "/".join(cpu.get(k, "?") for k in ("CPU family", "Model", "Stepping"))}


def machines_hw(F, a6=True):
    """Bornes physiques : médiane, quantité par quantité, des caractérisations des machines qui ont mesuré. STREAM sur
    4 threads (A6) : médiane des relevés de la sonde corrigée, sur les machines de la campagne qui en ont un ; à défaut
    sur les autres machines de results/hw du même modèle de processeur, puis sur toutes ; sans A6, médiane des relevés
    d'origine."""
    ms = sorted({m for v in F.machines.values() for m in v if m is not None}, key=lambda x: int(x))
    hws = [hw_numbers(os.path.join(ROOT, "results", "hw", f"machine{m}")) for m in ms]
    if not hws:
        raise SystemExit("aucune machine dans les enregistrements")
    sizes = sorted(set.intersection(*[{s for s, _ in h["bw"]} for h in hws]))
    bw = [(s, float(np.median([dict(h["bw"])[s] for h in hws]))) for s in sizes]
    if a6:
        s4 = [h["stream4"] for h in hws if h["stream4"]]
        if not s4:
            others = [hw_numbers(p) for p in sorted(glob.glob(os.path.join(ROOT, "results", "hw", "machine*")))]
            others = [h for h in others if h["stream4"]]
            models = {h["model"] for h in hws}
            s4 = [h["stream4"] for h in others if h["model"] in models] or [h["stream4"] for h in others]
        if not s4:
            raise SystemExit("aucun relevé corrigé de STREAM à 4 fils dans results/hw (stream4.txt)")
    else:
        s4 = [h["stream4_0"] for h in hws]
    hw = {"bw": bw, "stream4": float(np.median(s4))}
    for q in ("peak", "freq"):
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


def build_pools(data, langs, keys, a5=True):
    """Réservoirs de résidus par (noyau, classe), fusionnés avec le noyau s'ils ont moins de 20 résidus. a5 : résidus
    des logarithmes diminués de l'effet commun du groupe de chaque processus dans sa passe (block_effects)."""
    pools, kpool = defaultdict(list), defaultdict(list)
    for l in langs:
        for key in sorted(keys):  # ordre fixe : l'ordre d'un ensemble change d'un processus à l'autre
            procs = data.get(l, {}).get(key)
            if not procs or len(procs) < 2:
                continue
            y = proc_logs(procs)
            if a5:
                y = y - np.array([p.b for p in procs])
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
                    f = dev_noise(procs, nb)
                    mean[1:, j], mn[1:, j] = f * np.exp(draws.mean(axis=1)), f * np.exp(draws.min(axis=1))
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


def position(F, p, calc, k3n, natural=None):
    """(d, lt, src, missing) d'une position : la base (construction pub), K3 de R4, puis les substitutions du calcul.
    src[l][clé] = (construction, taille, clé source), pour la sélection indépendante. natural : un autre mode du
    tirage (A7, A8) que celui du calcul ; « pub » : le code naturel reste dans le mode publié de chaque chaîne, comme
    dans « Sans R1 » ; « unc » : il passe en mode R1', comme dans « R1' au lieu de R1 »."""
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
                    procs = [q for q in procs if q.cp == 0]
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
            procs = [q for q in procs if q.cp == 0]
        d[l][tk] = procs
        src[l][tk] = (cons, size, sk)
        if tk == K8N:
            lp = F.lat.get((cons, size), {}).get(l, {}).get(K8N)
            if lp:
                lt[l][K8N] = [x for c, x in lp if not three or c == 0]
            else:
                missing.append([l, cons, "latences de K8", size])

    mode = None if calc in ("Base, trois tailles", "Sans R1") else ("unc" if calc == "R1' au lieu de R1" else "chk")
    if natural is not None:
        mode = {"pub": None, "unc": "unc"}[natural]
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


def new_cells_patch(d, add, allkeys, p, base_seed, a5):
    """Tableaux simulés des clés nouvelles d'une position : estimation ponctuelle, et tirages dans les réservoirs du
    noyau (bâtis sur la base de la position), un générateur par clé, langage et position ; NaN où la forme manque."""
    def patch(A):
        pools = build_pools(d, LANGS, sorted(needed_keys()), a5)
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
                    f = dev_noise(procs, A.nb)
                    mean[1:, j], mn[1:, j] = f * np.exp(draws.mean(axis=1)), f * np.exp(draws.min(axis=1))
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
                    p0 = [q[0] for q in F.procs(b, size, l, key) or [] if q.ps == 0]
                    if not p0:
                        continue
                    t0 = math.exp(float(np.mean(np.log(p0))))
                    if best is None or t0 < best[0]:
                        best = (t0, b, size, key)
                if best is None:
                    continue
                _, b, size, key = best
                later = [q for q in F.procs(b, size, l, key) if q.ps in (1, 2)]
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
          a1=True, a3=True, a4=True, a5=True, alt=()):
    """Un calcul. host : données qui avancent le générateur principal (les mêmes pour tous les calculs) ; pos_dl : [(d,
    lt)] des trois positions ; wmode : « three » (poids des tailles égaux au centre, tirés dans les variantes) ou une
    position (0, 1, 2) de poids 1 ; b3 : R4 (référence de K3) ; measures_only : poids de la grille à 0 ; a1, a3, a4,
    a5 : corrections (corrections()). Les tirages de la règle de la grille (a1) et de la référence du code naturel (a3)
    sont faits puis ignorés, pour que tous les calculs gardent les mêmes tirages. alt (A7, A8) : [(pos_dl, patches)]
    du même calcul avec le code naturel dans les autres modes du tirage (mode publié, puis R1') ; chaque variante
    prend alors l'un des jeux de tableaux, tiré par un générateur à part (DRAW_SEED), et le centre garde le premier
    (R1)."""
    rng = np.random.default_rng(SEED)
    keys = sorted(needed_keys())
    Arrays3(host[0], host[1], LANGS, B, rng, build_pools(host[0], LANGS, keys))  # avance rng de la même façon
    ebs = [dict(e) for e in ebs]

    def arrays(pos_dl, patches):
        As, refs = [], []
        for p, (d, lt) in enumerate(pos_dl):
            A = Arrays3(d, lt, LANGS, B, np.random.default_rng(SEED + 4100 + p), build_pools(d, LANGS, keys, a5))
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
        return As, refs

    As, refs = arrays(pos_dl, patches)
    worlds = [(As, refs)] + [arrays(*a) for a in alt]  # jeux de tableaux : celui du calcul, puis ceux des autres modes
    draw = np.random.default_rng(DRAW_SEED)
    if len(worlds) == 2:  # sans A8 : pile ou face, tel que publié le 26 novembre à 15 h
        pick = (draw.random(U) < 0.5).astype(int)
    else:
        pick = draw.integers(0, len(worlds), U)
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
        Aw, rw = worlds[int(pick[u])]
        S_u = scores(Aw, b, cfg, C, footprint, rw, ebs, wsz(wS), wE=wE, wD=wD, wP=wP, mt_nosmall=a4)
        r_ = ranks_of(S_u["MS"][rk])
        ms_sum += S_u["MS"]
        prec += r_[:, None] < r_[None, :]
        first[int(np.argmin(r_))] += 1
        ranks[u] = r_
    prec /= U
    idx = As[1].idx
    exp21 = {a: 1 + sum(prec[RANKED.index(b_), RANKED.index(a)] for b_ in RANKED if b_ != a) for a in RANKED}
    return {"mode_share": [float((pick == i).mean()) for i in range(len(worlds))] if alt else None,
            "exp21": exp21, "ms0": {l: float(S0["MS"][idx[l]]) for l in LANGS}, "prec": prec,
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
    if s.get("mode_share") is not None:  # A7, A8 : part des variantes dans chaque mode du code naturel (DRAW_MODES)
        out["mode_share"] = s["mode_share"]
    return out


def run_calc(calc, F, fc, footprint, c3, ebs, b3, host, keys):
    cor = corrections(calc)
    b3ref, k3n = b3["max" if cor["a2"] else "median"][:2]
    r4 = calc not in ("Base, trois tailles", "Sans R4")

    def world(natural=None):
        """Données du calcul pour un mode du code naturel : le sien (None) ou un autre mode du tirage (« pub » : mode
        publié ; « unc » : R1') : positions, cellules remplies, manquantes, mesures du plafond, tableaux à ajouter,
        sélection."""
        pos = [position(F, p, calc, k3n, natural) for p in range(3)]
        filled, missing = {}, []
        for p, (d, lt, src, miss) in enumerate(pos):
            filled[POS_NAMES[p]] = fill_missing(d, LANGS, keys)
            missing += miss
        e_meas, patches, chosen = None, [[], [], []], None
        if calc == "Sélection indépendante":
            e_meas, adds, sel, chosen = selection(F, fc, pos)
            for p in range(3):
                patches[p].append(new_cells_patch(pos[p][0], adds[p], sel, p, SEL_SEED, cor["a5"]))
        elif calc not in ("Base, trois tailles", "Sans C1"):
            adds, allc = [], {}
            for p in range(3):
                add, ceil_of, miss = additions(F, fc, p, pos[p][0])
                adds.append(add)
                allc.update(ceil_of)
                missing += miss
            e_meas = e_meas_with(allc)
            for p in range(3):
                patches[p].append(new_cells_patch(pos[p][0], adds[p], allc, p, NEW_SEED, cor["a5"]))
        if r4:
            for p in range(3):
                patches[p].append(r4_patch(b3ref))
        return pos, filled, missing, e_meas, patches, chosen

    pos, filled, missing, e_meas, patches, chosen = world()
    alt = []
    if cor["a7"] and calc not in NO_DRAW:  # A7, A8 : le même calcul, code naturel dans les autres modes du tirage
        for natural in ("pub", "unc") if cor["a8"] else ("pub",):
            pos0, filled0, missing0, e_meas0, patches0, _ = world(natural)
            if e_meas0 != e_meas or any([x[:2] for x in filled0[k]] != [x[:2] for x in filled[k]] for k in filled):
                raise SystemExit(f"{calc} : les modes du code naturel n'ont pas les mêmes cellules")
            missing += [m for m in missing0 if m not in missing]
            alt.append(([(d, lt) for d, lt, src, miss in pos0], patches0))
    wmode = {"Sans les tailles (taille publiée seule)": 1, "Taille petite": 0, "Taille grande": 2}.get(calc, "three")
    s = three(host, [(d, lt) for d, lt, src, miss in pos], footprint, c3, ebs, e_meas=e_meas, patches=patches,
              wmode=wmode, b3=b3ref if r4 else None, measures_only=(calc == "Sur les seules mesures"),
              a1=cor["a1"], a3=cor["a3"], a4=cor["a4"], a5=cor["a5"], alt=alt)
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
    """Écart entre la passe la plus lente et la plus rapide de chaque cellule (moyennes géométriques par passe) : brut,
    puis une fois retiré l'effet commun de chaque groupe dans chaque passe (A5)."""
    raw, net = [], []
    for (cons, size), dl in F.data.items():
        for l, keys in dl.items():
            for key, procs in keys.items():
                by, byn = defaultdict(list), defaultdict(list)
                for q in procs:
                    by[q.ps].append(q[0])
                    byn[q.ps].append(q[0] * math.exp(-q.b))
                by, byn = ({ps: np.log(v) for ps, v in d.items()} for d in (by, byn))
                if len(by) == 3:
                    for acc, d in ((raw, by), (net, byn)):
                        g = [math.exp(float(np.mean(v))) for v in d.values()]
                        acc.append(max(g) / min(g))
    raw, net = np.array(raw), np.array(net)
    return {"cells": int(len(raw)), "median": float(np.median(raw)) if len(raw) else None,
            "over_20pct": int((raw > 1.2).sum()), "net_median": float(np.median(net)) if len(net) else None,
            "net_over_20pct": int((net > 1.2).sum())}


def machine_effect(F):
    """Effet de machine dans la campagne (docs/V5.md, 8) : pour chaque cellule mesurée sur la première machine et sur
    une machine suivante, rapport de la médiane de ses processus sur cette machine à la médiane de ses processus sur la
    première. Par machine : nombre de cellules, médiane des rapports (ensemble et par noyau), part des cellules à moins
    de 5 % de la médiane d'ensemble. None si la campagne n'a qu'une machine."""
    cells = [(key[0], procs) for dl in F.data.values() for keys in dl.values() for key, procs in keys.items()]
    ms = sorted({q.machine for k, procs in cells for q in procs if q.machine is not None}, key=int)
    if len(ms) < 2:
        return None
    out = {}
    for m in ms[1:]:
        by = defaultdict(list)
        for k, procs in cells:
            a = [q[0] for q in procs if q.machine == ms[0]]
            b = [q[0] for q in procs if q.machine == m]
            if a and b:
                by[k].append(float(np.median(b) / np.median(a)))
        ratios = [r for v in by.values() for r in v]
        if ratios:
            med = float(np.median(ratios))
            out[m] = {"cells": len(ratios), "median": med,
                      "within_5pct": float(np.mean([abs(math.log(r / med)) <= math.log(1.05) for r in ratios])),
                      "by_kernel": {k: float(np.median(v)) for k, v in sorted(by.items())}}
    return {"first": ms[0], "machines": out}


def cell_estimates(F):
    """Estimation ponctuelle de chaque cellule mesurée : moyenne géométrique des médianes de ses processus."""
    return {"|".join((l, cons, size) + key): gm(procs) for (cons, size), dl in F.data.items()
            for l, keys in dl.items() for key, procs in keys.items()}


def extract(path, note, key="previous"):
    """Extrait d'une campagne, gardé pour que la suivante s'y compare (replication) : classement et scores du calcul
    « Final » déjà écrit (OUT). Complète le fichier comparisons.json de la campagne suivante. Clé « previous » : le
    classement tel qu'il était publié, avec les estimations par cellule relues dans les mesures ; clé
    « previous_same_method » : la même campagne recalculée par la méthode de la suivante (docs/V5.md, 8, écart 7)."""
    f = json.load(open(OUT))["results"][FINAL]
    prev = {k: f[k] for k in ("order", "ms_mean", "ms0", "exp", "first", "E", "D", "C")}
    comp = json.load(open(path)) if os.path.exists(path) else {}
    if key == "previous":
        prev["cells"] = cell_estimates(load())
        comp["note"] = note
    else:
        prev["note"] = note
    comp[key] = prev
    json.dump(comp, open(path, "w"), indent=1, ensure_ascii=False)


def replication(F, prev, fin, same=None):
    """Cette campagne contre la précédente (prev : extract) : places et scores de « Final », langages à plus de deux
    places, et rapport des temps cellule par cellule (cette campagne sur la précédente, cellules mesurées dans les
    deux) : médiane d'ensemble, médiane par langage, part des cellules à moins de 10 % de la médiane d'ensemble. Avec
    same (la campagne précédente recalculée par la méthode de celle-ci) : la comparaison à méthode égale, et ce que
    le changement de méthode déplace dans la campagne précédente."""
    now = cell_estimates(F)
    ratios = {k: now[k] / t for k, t in prev["cells"].items() if k in now}
    med = float(np.median(list(ratios.values())))
    by = defaultdict(list)
    for k, r in ratios.items():
        by[k.split("|")[0]].append(r)
    keep = ("order", "ms_mean", "exp", "first", "E", "D")
    out = {"moved": moved(prev["order"], fin["order"], LANGS), "cells": len(ratios), "median": med,
           "within_10pct": float(np.mean([abs(math.log(r / med)) <= math.log(1.10) for r in ratios.values()])),
           "by_lang": {l: float(np.median(v)) for l, v in sorted(by.items())},
           "previous": {k: prev[k] for k in keep}}
    if same:
        out["same_method"] = {"moved": moved(same["order"], fin["order"], LANGS),
                              "method_moved": moved(prev["order"], same["order"], LANGS),
                              "previous": {k: same[k] for k in keep}}
    return out


# ------------------------------------------------------------------ lectures du classement (docs/V5_3.md)
# Groupes de tête de « ce qui décide de l'ordre » : rang plausible commençant à n ou mieux.
HEADS = (("première moitié possible", 12), ("podium possible", 3))
# Pairs du tri des écarts : les langages dont la chaîne produit son code machine par LLVM (C par clang, Zig, Odin, Rust,
# Nim par clang, C3, D par LDC, Julia, Chapel, Mojo, Swift, Haskell par ghc -fllvm) ou par GCC (C++, Ada, Fortran).
PEERS = ("c", "cpp", "zig", "odin", "rust", "nim", "c3", "d", "ada", "julia", "fortran", "chapel", "mojo", "swift",
         "haskell")
TRI_MODES = (("R1", None), ("mode publié", "pub"), ("R1'", "unc"))  # mode du tirage -> argument natural de position()
TRI_FACTOR = 2.0  # rapport, arrondi au dixième, à partir duquel une cellule est signalée
TRI_STATUS = ("établie", "attribuée", "à corriger", "à examiner")  # du mieux fondé au moins fondé
# Registre des causes : statut, cause, contrôle qui la montre, couples « langage mesure sens modes » qu'elle couvre
# (modes : *, ou parmi R1, pub, R1' séparés par des virgules). Un couple signalé sans cause est « à examiner ».
TRI_CAUSES = [
    {"status": "établie",
     "cause": "clang fusionne par défaut la multiplication et l'addition du produit scalaire en une FMA "
              "(`-ffp-contract=on`), qui allonge la chaîne de dépendance de la somme",
     "control": "le même source compilé par gcc prend 0,45 à 0,51 fois le temps de clang (campagne, « C par gcc ») ; "
                "code machine (`docs/V5_3.md`, 8)",
     "cells": ["c K5 lent *"]},
    {"status": "attribuée",
     "cause": "même facteur deux que le produit scalaire de C : fusion en FMA probable (Chapel `--fast`, Mojo, "
              "`ghc -mfma`)",
     "control": "aucun contrôle propre ; `docs/HASKELL.md` de l'archive (2) donne à Haskell le temps de C sur K5",
     "cells": ["chapel K5 lent pub,R1'", "mojo K5 lent *", "haskell K5 lent *"]},
    {"status": "établie",
     "cause": "GCC vectorise la somme conditionnelle d'octets moins bien que LLVM",
     "control": "le même source C compilé par gcc prend 3,9, 3,6 et 2,5 fois le temps de clang aux trois tailles "
                "(campagne, « C par gcc »)",
     "cells": ["cpp K4 lent *", "ada K4 lent *", "fortran K4 lent *"]},
    {"status": "établie",
     "cause": "vérifications que R1 ajoute au mode publié (débordement des entiers de `-O safe` pour Zig, `--checks` "
              "pour Chapel, `-D_GLIBCXX_ASSERTIONS` pour C++, `-Cr -Co` pour FreePascal) : elles empêchent la "
              "vectorisation",
     "control": "l'écart disparaît en mode publié ; `docs/V5_1.md`, 2 (Zig) et 9.1 (Chapel)",
     "cells": ["zig K4 lent R1", "chapel K5 lent R1", "chapel Q6 lent R1", "chapel Q1 lent R1", "chapel K9 lent R1",
               "cpp K9 lent R1", "fpc K9 lent R1"]},
    {"status": "établie",
     "cause": "vérifications du mode publié qu'une option retire : contrôle de falsification des conteneurs d'Ada sur "
              "K7, bornes d'Ada, de Swift et de Mojo sur leurs tableaux, bornes de Go sur les colonnes de Q6",
     "control": "l'écart disparaît en R1' ; `docs/V5_1.md`, 9.1 (Ada) ; `docs/SWIFT.md` (2.4) et `docs/MOJO.md` (2) de "
                "l'archive ; Go : Q6 naturel prend 2,1 à 2,6 fois son temps sans elles (campagne, `-gcflags=-B`)",
     "cells": ["ada K7 lent R1,pub", "ada K9 lent R1,pub", "swift K9 lent R1,pub", "mojo Q1 lent R1,pub",
               "mojo K9 lent R1,pub", "go Q6 lent R1,pub"]},
    {"status": "établie",
     "cause": "somme conditionnelle que les pairs vectorisent et que la chaîne laisse scalaire : pas de vectoriseur de "
              "boucles dans les passes de Mojo ; un branchement par octet en Swift, avec le piège de débordement de "
              "`-O` ; pas de vectoriseur automatique pour cette boucle en Go, C#, Java, Haskell, OCaml, JavaScript, "
              "Lua et Python",
     "control": "`docs/MOJO.md` (2), `docs/SWIFT.md` (2.4) et `docs/GO.md` (2) de l'archive",
     "cells": ["mojo K4 lent *", "swift K4 lent *", "haskell K4 lent *", "go K4 lent *", "csharp K4 lent *",
               "java K4 lent *", "ocaml K4 lent *", "js K4 lent *", "lua K4 lent *", "python K4 lent *"]},
    {"status": "attribuée",
     "cause": "boucle que les pairs vectorisent et que la chaîne laisse scalaire, sans relecture qui le consigne : "
              "somme conditionnelle de FreePascal et de PHP ; stencil de C#, Go, JavaScript, PHP, Python, Lua et BQN ; "
              "stencil de Mojo une fois ses vérifications retirées",
     "control": "aucun contrôle propre",
     "cells": ["fpc K4 lent *", "php K4 lent *", "csharp K9 lent *", "go K9 lent *", "js K9 lent *", "php K9 lent *",
               "python K9 lent *", "lua K9 lent *", "bqn K9 lent *", "mojo K9 lent R1'"]},
    {"status": "attribuée",
     "cause": "stencil de Nim sur une `seq` : vérifications de bornes de `-d:release`, et boucle que clang ne "
              "vectorise pas même sans elles (Nim lui passe `-fno-strict-aliasing`)",
     "control": "`docs/NIM.md` de l'archive (2), établi pour la forme imbriquée, non refait pour la forme contiguë",
     "cells": ["nim K9 lent *"]},
    {"status": "établie",
     "cause": "ramasse-miettes de D : chaque nœud de K8 est un `new` de classe",
     "control": "`docs/DLANG.md` de l'archive (2)",
     "cells": ["d K8 lent *"]},
    {"status": "attribuée",
     "cause": "coût d'allocation du type par défaut : comptage de références de la classe de Swift, nœuds de Haskell "
              "confiés au ramasse-miettes",
     "control": "aucun contrôle propre ; `docs/SWIFT.md` de l'archive (2.4, point 9) chiffre une part du coût de "
                "Swift",
     "cells": ["swift K8 lent pub", "haskell K8 lent pub,R1'"]},
    {"status": "établie",
     "cause": "types par défaut de Haskell : liste chaînée pour K1, `Data.IntMap` pour K7 faute de table de hachage "
              "livrée, tableau immuable `UArray` pour K9",
     "control": "`docs/NATURAL.md` ; `docs/HASKELL.md` de l'archive (1 et 2)",
     "cells": ["haskell K1 lent *", "haskell K7 lent *", "haskell K9 lent *"]},
    {"status": "attribuée",
     "cause": "types par défaut du langage : enregistrements en références de JavaScript, PHP et Lua et matrice de "
              "doubles de BQN pour K1 ; `TDictionary` de FreePascal (deux recherches par ligne) et `Hashtbl` d'OCaml "
              "pour K7 ; idiomes de tableaux de BQN pour Q1 et K8 ; produit scalaire de FreePascal",
     "control": "`docs/NATURAL.md` décrit ces types ; leur part dans l'écart n'a pas de contrôle propre",
     "cells": ["js K1 lent *", "php K1 lent *", "lua K1 lent *", "bqn K1 lent *", "fpc K7 lent pub,R1'",
               "ocaml K7 lent pub,R1'", "bqn Q1 lent *", "bqn K8 lent *", "fpc K5 lent pub"]},
    {"status": "établie",
     "cause": "ni C ni Fortran n'ont de table de hachage en bibliothèque standard : leur code naturel est le chaînage "
              "des manuels, écrit pour le noyau, au nombre de seaux fixé d'avance sur le nombre de clés et haché par "
              "un modulo ; les tables de bibliothèque des pairs grandissent et hachent plus fort. Avantage que la "
              "règle du code naturel accepte",
     "control": "`docs/NATURAL.md` (K7, cas discutables) ; sources de `bench/c` et de `bench/fortran`",
     "cells": ["c K7 rapide *", "fortran K7 rapide *"]},
    {"status": "attribuée",
     "cause": "allocation par un ramasse-miettes générationnel : un nœud de K8 coûte un déplacement de pointeur, "
              "contre une allocation et une libération chez les pairs",
     "control": "aucun contrôle propre",
     "cells": ["java K8 rapide *", "ocaml K8 rapide *"]},
    {"status": "établie",
     "cause": "sans vérification de bornes, LLVM vectorise la boucle naturelle de Q6 d'Odin ; celle des autres pairs "
              "reste scalaire",
     "control": "campagne, taille publiée : Odin 48,7 ms avec les bornes, 18,4 ms sans, 13,6 ms pour sa forme SIMD ; "
                "C 40,9 ms",
     "cells": ["odin Q6 rapide R1'"]},
    {"status": "attribuée",
     "cause": "primitives de tableaux de CBQN, vectorisées",
     "control": "aucun contrôle propre ; `docs/BQN.md` de l'archive",
     "cells": ["bqn Q6 rapide *"]},
]


def importance(r):
    """Ce qui décide de l'ordre (docs/V5_3.md, 2) : pour quatre groupes de langages emboîtés, part de la variance du
    score au centre que porte chaque composante. Piliers et parts de D : cov(apport, score) / var(score), le score au
    centre étant linéaire en ses piliers et D en ses parts ; noyaux : la part du plafond, répartie au prorata de
    cov(ln E_k / n, ln E) / var(ln E). r : résumé du calcul « Final »."""
    kernels = list(E_V2)
    weights = dict(WEIGHTS, **{k: WEIGHTS["E"] / len(kernels) for k in kernels},
                   **{q: WEIGHTS["D"] * w for q, w in DW.items()})
    groups = [(f"les {len(r['order'])} langages", list(r["order"])), ("premier étage", list(r["tiers"][0]))]
    groups += [(name, [l for l in r["order"] if r["rank90"][l][0] <= n]) for name, n in HEADS]
    cov = lambda x, y: float(np.mean((x - x.mean()) * (y - y.mean())))  # noqa: E731
    out = {"weights": weights, "groups": []}
    for name, g in groups:
        C, E, D, S = (np.array([r[key][l] for l in g]) for key in ("C", "E", "D", "ms0"))
        ek = {k: np.array([r["Ek"][l][k] for l in g]) for k in kernels}
        dq = {q: np.array([r["Dparts"][l][q] for l in g]) for q in DW}
        lnE = np.log(E)
        if not (np.allclose(S, WEIGHTS["C"] * C + WEIGHTS["E"] * E + WEIGHTS["D"] * D, atol=1e-9)
                and np.allclose(D, 100 * sum(w * dq[q] for q, w in DW.items()), atol=1e-9)
                and np.allclose(lnE, math.log(100) + np.mean([np.log(ek[k]) for k in kernels], axis=0), atol=1e-9)):
            raise SystemExit("importance : le score au centre n'est pas celui que ses composantes recomposent")
        v, ve = cov(S, S), cov(lnE, lnE)
        if len(g) < 3 or v == 0 or ve == 0:
            continue
        sh = {x: cov(WEIGHTS[x] * y, S) / v for x, y in (("C", C), ("E", E), ("D", D))}
        sh.update({k: sh["E"] * cov(np.log(ek[k]) / len(kernels), lnE) / ve for k in kernels})
        sh.update({q: cov(WEIGHTS["D"] * 100 * w * dq[q], S) / v for q, w in DW.items()})
        sums = (sh["C"] + sh["E"] + sh["D"] - 1, sum(sh[k] for k in kernels) - sh["E"],
                sum(sh[q] for q in DW) - sh["D"])
        if max(abs(x) for x in sums) > 1e-9:
            raise SystemExit("importance : les parts ne somment pas")
        out["groups"].append({"name": name, "langs": g, "sd": math.sqrt(v), "shares": sh})
    return out


def triage(F):
    """Tri des écarts du code naturel (docs/V5_3.md, 3). Cellules : les mesures de D1, aux trois tailles, dans les
    trois modes du tirage, estimations ponctuelles du score. Rapport d'une cellule : son temps sur la médiane des temps
    des pairs (PEERS). Niveau d'un langage hors pairs, à une taille et dans un mode : médiane de ses rapports, au moins
    1 ; d'un pair : 1. Lente : rapport / niveau d'au moins TRI_FACTOR ; rapide : médiane des pairs / temps d'au moins
    TRI_FACTOR ; les deux arrondis au dixième. Un couple (langage, mesure) est signalé dans un mode s'il l'est à une
    taille au moins ; chaque mode signalé est rattaché à une cause du registre (TRI_CAUSES), sinon « à examiner »."""
    names = [{("k6", 0): "Q6", ("k6", 1): "Q1"}.get((k, i), k.upper()) for k, lst in D1_V2.items() for i, ks in lst]
    keysets = [ks for lst in D1_V2.values() for i, ks in lst]
    modes = [m for m, nat in TRI_MODES]
    ratio, level = {}, {}
    for mode, nat in TRI_MODES:
        for p in range(3):
            d = position(F, p, FINAL, {}, nat)[0]
            for m, ks in zip(names, keysets):
                t = {l: min(gm(d[l][key]) for key in ks if d[l].get(key)) for l in LANGS
                     if any(d.get(l, {}).get(key) for key in ks)}
                ref = float(np.median([t[l] for l in PEERS if l in t]))
                ratio.update({(mode, p, m, l): x / ref for l, x in t.items()})
            for l in LANGS:
                rs = [ratio[(mode, p, m, l)] for m in names if (mode, p, m, l) in ratio]
                level[(mode, p, l)] = 1.0 if l in PEERS or not rs else max(1.0, float(np.median(rs)))
    short = {"R1": "R1", "mode publié": "pub", "R1'": "R1'"}
    covered = {}  # (langage, mesure, sens, mode) -> rang de la cause
    for n, c in enumerate(TRI_CAUSES):
        for cell in c["cells"]:
            l, m, sense, ms = cell.split()
            for mode in modes:
                if ms == "*" or short[mode] in ms.split(","):
                    covered.setdefault((l, m, sense, mode), n)
    rows, used = [], set()
    for l in LANGS:
        for m in names:
            for sense in ("lent", "rapide"):
                vals, sizes = {}, {}
                for mode in modes:
                    ps = [p for p in range(3) if (mode, p, m, l) in ratio]
                    if not ps:
                        continue
                    if sense == "lent":
                        xs = [ratio[(mode, p, m, l)] / level[(mode, p, l)] for p in ps]
                        vals[mode], hit = max(xs), [round(x, 1) >= TRI_FACTOR for x in xs]
                    else:
                        xs = [ratio[(mode, p, m, l)] for p in ps]
                        vals[mode], hit = min(xs), [round(1 / x, 1) >= TRI_FACTOR for x in xs]
                    if any(hit):
                        sizes[mode] = [POS_NAMES[p] for p, h in zip(ps, hit) if h]
                if not sizes:
                    continue
                cause = {mode: covered.get((l, m, sense, mode)) for mode in sizes}
                used.update((l, m, sense, mode) for mode in sizes)
                st = [TRI_STATUS[-1] if n is None else TRI_CAUSES[n]["status"] for n in cause.values()]
                lv = [level[(mode, p, l)] for mode in modes for p in range(3)]
                rows.append({"lang": l, "measure": m, "sense": sense, "ratio": vals, "sizes": sizes, "cause": cause,
                             "status": max(st, key=TRI_STATUS.index), "level": [min(lv), max(lv)]})
    seen = {k[:3] for k in used}
    stale = sorted({" ".join(k[:3]) for k in covered if k[:3] not in seen})  # entrées du registre sans couple signalé
    return {"peers": list(PEERS), "factor": TRI_FACTOR,
            "causes": [{k: c[k] for k in ("status", "cause", "control")} for c in TRI_CAUSES], "rows": rows,
            "counts": {s: sum(r["status"] == s for r in rows) for s in TRI_STATUS},
            "unexplained": [f"{r['lang']} {r['measure']} {r['sense']} {mode}" for r in rows
                            for mode, n in r["cause"].items() if n is None], "stale": stale}


def main():
    if len(sys.argv) == 4 and sys.argv[1] in ("--extract", "--extract-same"):  # <option> <fichier> <note>
        return extract(sys.argv[2], sys.argv[3], "previous" if sys.argv[1] == "--extract" else "previous_same_method")
    Fm = F = load()  # Fm : la campagne telle que mesurée
    c3 = json.load(open(os.path.join(ROOT, "results", "vectorization.json")))
    footprint = json.load(open(os.path.join(ROOT, "results", "footprint.json")))
    dev, go, c3_17 = dev_ratios(), go_ratios(), c3

    def data(zig=True, golang=True, view=None, **kw):
        """Mesures d'un calcul : la campagne, avec ou sans chacune de ses remesures (Zig ramené par son témoin : docs/
        V5_2.md ; cellules faussées de Go rebâties par le pont : docs/V5_4.md). kw : only et lat pour Zig (apply_dev),
        all_cells pour Go (apply_go)."""
        Fx, absent = load(view), {}
        if zig and dev:
            absent[DEV_LANG] = apply_dev(Fx, dev, **{k: v for k, v in kw.items() if k in ("only", "lat")})
        if golang and go:
            absent[GO_LANG] = apply_go(Fx, go, Fm, **{k: v for k, v in kw.items() if k == "all_cells"})
        return Fx, absent

    if dev or go:
        F, absent = data()
        for x, lang in ((dev, DEV_LANG), (go, GO_LANG)):
            if x:
                x["absent"] = absent[lang]
    if dev:
        c3 = dict(c3, **{DEV_LANG: c3[DEV_LANG + "_master"]})  # règle v1 : vectorisation mesurée sous cette version
    hw, machines = machines_hw(F)
    ebs = [ebounds(hw, p) for p in range(3)]
    hw0 = machines_hw(F, a6=False)[0]  # sans A6 : relevé d'origine de STREAM à 4 fils
    ebs0 = [ebounds(hw0, p) for p in range(3)]
    b3 = {}  # statistique de b3 -> (b3 de référence, temps de K3 ramenés à ce b3, b3 des groupes)
    for stat in ("max", "median"):
        ref, groups, b3recs = b3_values(stat)
        b3[stat] = (ref, k3_normalized(F, ref, groups), groups)
    fc = forms_cells(LANGS)
    keys = campaign_keys({k: v for k, v in F.data.items() if k[0] == "pub"})
    Fh = Fm  # avance du générateur principal : la base de la campagne, taille publiée

    def b3_of(Fx):
        return {stat: (ref, k3_normalized(Fx, ref, groups), groups) for stat, (ref, _, groups) in b3.items()}

    def more(calc, Fx, c3x):
        calcs.append(calc)
        res[calc] = run_calc(calc, Fx, fc, footprint, c3x, ebs, b3_of(Fx), host, keys)

    hd = position(Fh, 1, "Base, trois tailles", {})[0]
    host = (copy.deepcopy(hd), position(Fh, 1, "Base, trois tailles", {})[1])
    fill_missing(host[0], LANGS, keys)
    calcs = list(CALCS)
    res = {c: run_calc(c, F, fc, footprint, c3, ebs if corrections(c)["a6"] else ebs0, b3, host, keys)
           for c in calcs}
    if F.gcc:  # C par gcc : mêmes tirages, les cellules de C prises dans ses constructions par gcc
        Fg = data(view=GCC_VIEW)[0]
        more(GCC_CALC, Fg, c3)
        gcc = {"records": F.gcc, "cpu_models": dict(F.gcc_models),
               "failures": [x for x in Fg.failures if x["lang"] in GCC_VIEW],
               "skipped": [x for x in Fg.skipped if x["lang"] in GCC_VIEW],
               "steal_over_5pct": [x for x in Fg.steal if x[0] in GCC_VIEW]}
    if dev:  # mêmes tirages
        more(ZIG17, data(zig=False)[0], c3_17)  # les cellules de Zig de la campagne
        more(ZIGV, data(only=("k4", "k9"))[0], c3)  # transport limité aux noyaux dont le code machine change
        more(ZIGL, data(lat=True)[0], c3)  # le calcul du plan : latences de K8 naturel ramenées elles aussi
    if go:
        more(GOC, data(golang=False)[0], c3)  # les cellules de Go de la campagne : le classement de la v5.3
        more(GOALL, data(all_cells=True)[0], c3)  # les autres cellules de Go ramenées par leur témoin
    if dev and go:
        more(MEAS, Fm, c3_17)  # ni l'une ni l'autre : le classement du 26 novembre à 17 h
    asm = MEAS if dev and go else (ZIG17 if dev else (GOC if go else FINAL))  # la campagne telle que mesurée
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
           "stream4_original": hw0["stream4"],
           "block_effects": {f"{k}|{s}": v for (k, s), v in sorted(F.blocks.items())},
           "machine_effect": machine_effect(F),
           "retained": retained(F, fc), "spread": spread(F), "failures": F.failures, "skipped": F.skipped,
           "steal_over_5pct": F.steal, "cpu_models": {m: dict(ps) for m, ps in F.models.items()},
           "importance": importance(res[FINAL]), "triage": triage(F)}
    if F.gcc:
        out["gcc"] = gcc
    if dev:
        out["zig_dev"] = dev_summary(dev, Fm)
    if go:
        out["go_std"] = go_summary(go, Fm, F)
    # comparaisons : la méthode du 23 novembre (calcul OLD) et, si comparisons.json la porte, la campagne précédente
    out["moved_vs_old"] = moved(res[OLD]["order"], fin, LANGS)
    cp = os.path.join(FIN, "comparisons.json")
    comp = json.load(open(cp)) if os.path.exists(cp) else {}
    if "previous" in comp:  # à configurations égales : la campagne telle que mesurée, sans ses remesures
        out["replication"] = replication(Fh, comp["previous"], res[asm], comp.get("previous_same_method"))
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
    zd = o.get("zig_dev")  # Zig par sa version de développement : astérisque
    gs = o.get("go_std")  # Go hors de l'expérience simd
    asm = MEAS if zd and gs else (ZIG17 if zd else (GOC if gs else None))  # la campagne telle que mesurée : réplication
    star = lambda l: NAMES[l] + ("*" if zd and l == DEV_LANG else "")
    L = ["# v5.4 : le classement — résultats", "",
         "*Plans : `docs/V4_FINAL.md` (section 8), `docs/V4_1.md` (corrections A1 à A4 de l'analyse), `docs/V5.md` "
         "(campagne rejouée, corrections A5 et A6), `docs/V5_1.md` (A7 et A8 : mode du code naturel tiré au sort) et "
         "`docs/V5_2.md` (Zig par sa version de développement), fixés "
         "avant les mesures ou avant leur analyse ; `docs/V5_3.md` (ce qui décide de l'ordre, tri des écarts) ; "
         "`docs/V5_4.md` (Go mesuré hors de l'expérience simd). Généré par "
         "`analysis/final_v4.py` à partir de `results/final/raw`, de `results/final/b3.jsonl` et du relevé des formes "
         "(`results/converge/forms.json`).*", "",
         f"Machines : {', '.join(o['machines'])} ; b3 de référence (le plus lent des 16 décalages, A2) : "
         f"{1e3 * o['b3_ref']:.2f} ms ; b3 des groupes de K3 : "
         + ", ".join(f"passe {k.split('|')[0]} {1e3 * v:.2f} ms" for k, v in sorted(o["b3_groups"].items()))
         + f" ; avec la médiane des 16 décalages (méthode du 23 novembre) : {1e3 * o['b3_median_ref']:.2f} ms.", "",
         "## Classement « Final »", "",
         "| Rang | Langage | Score | Score au centre | Rang espéré | Rang plausible | Devance le suivant | Plafond | "
         "Code par défaut | Contrôle |", "|---|---|---|---|---|---|---|---|---|---|"]
    for i, l in enumerate(f["order"]):
        ahead = f["ahead_next"].get(l)
        L.append(f"| {i + 1} | {star(l)} | {f['ms_mean'][l]:.1f} | {f['ms0'][l]:.1f} | {f['exp'][l]:.2f} | "
                 f"{f['rank90'][l][0]}–{f['rank90'][l][1]} | {'—' if ahead is None else f'{100 * ahead:.0f} %'} | "
                 f"{f['E'][l]:.1f} | {f['D'][l]:.1f} | {f['C'][l]:.1f} |")
    L += ["", "Score : moyenne du score sur les variantes de l'analyse ; il fixe l'ordre. Score au centre, plafond, "
          "code par défaut et contrôle : poids et choix principaux, estimation ponctuelle. Rang espéré : rang moyen sur "
          "les variantes.", ""]
    if zd:
        z17 = R[ZIG17]
        L += [f"\\* Zig est mesuré, par exception, par sa version de développement {zd['version']} (`docs/V5_2.md`) : "
              "ses temps sont ceux de la campagne, multipliés cellule par cellule par le rapport mesuré à côté d'un "
              f"témoin ; ses latences de K8 naturel restent celles de la campagne. Avec sa version stable, celle de la "
              f"campagne (« Zig 0.17 ») : {nth(place(z17, DEV_LANG))}, score {z17['ms_mean'][DEV_LANG]:.1f}.", ""]
    if gs:
        g0 = R[GOC]
        L += [f"Go est mesuré hors de l'expérience `simd` de sa chaîne (`docs/V5_4.md`) : ses {len(gs['fixed'])} "
              "cellules de K1 que la campagne faussait sont rebâties par un pont par le C ; ses autres cellules sont "
              f"celles de la campagne. Avec ses cellules de la campagne (« {GOC} ») : {nth(place(g0, GO_LANG))}, "
              f"score {g0['ms_mean'][GO_LANG]:.1f}.", ""]
    if f.get("mode_share") is not None:
        L += ["Mode du code naturel, tiré dans chaque variante (A7, A8) : "
              + ", ".join(f"{m} dans {100 * x:.1f} % des variantes" for m, x in zip(DRAW_MODES, f["mode_share"]))
              + " ; au centre, R1.", ""]
    L += [
          "Étages (paires ordonnées dans au moins 95 % des variantes) : "
          + " | ".join(", ".join(NAMES[l] for l in t) for t in f["tiers"]), "",
          "## Tous les calculs", ""]
    rp = o.get("replication")  # campagne précédente : dernière colonne, et ligne des rangs qui bougent
    L += ["| Langage | " + " | ".join(calcs) + (" | Campagne précédente |" if rp else " |"),
          "|---|" + "---|" * (len(calcs) + bool(rp))]
    for l in f["order"]:
        cells = []
        for c in calcs:
            p = place(R[c], l)
            mark = "" if c == FINAL or abs(p - place(f, l)) <= 2 else " **"
            cells.append(f"{p}{mark}")
        if rp:
            cells.append(str(rp["previous"]["order"].index(l) + 1))
        L.append(f"| {NAMES[l]} | " + " | ".join(cells) + " |")
    L += ["", "Chaque case : place dans le calcul ; ** : plus de deux places d'écart avec « Final ». Ordre des lignes : "
          "« Final ». « Sans A1 » à « Sans A8 » : « Final » sans une de ses corrections ; « Méthode du 23 novembre » : "
          "sans aucune et classée au rang moyen" + (" ; « Zig 0.17 » : « Final » avec les cellules de Zig de la "
                                                    "campagne ; « Zig 0.18, K4 et K9 seuls » : le rapport au témoin "
                                                    "appliqué à ces deux noyaux seulement ; « Zig 0.18, latences du "
                                                    "plan » : les latences de K8 naturel de Zig multipliées elles "
                                                    "aussi par leur rapport" if zd else "")
          + (f" ; « {GOC} » : « Final » avec les cellules de Go de la campagne ; « {GOALL} » : les autres cellules de "
             "Go ramenées elles aussi par leur témoin" if gs else "")
          + (f" ; « {MEAS} » : ni l'exception de Zig ni la correction de Go" if zd and gs else "")
          + (" ; « Campagne précédente » : son classement publié." if rp else "."), "",
          "## Rangs qui bougent de plus de deux places par rapport à « Final »", ""]
    for c in calcs[1:]:
        mv = o["moved_more_than_2"][c]
        L.append(f"* {c} : " + (", ".join(f"{NAMES[l]} {nth(b)} (Final {nth(a)})" for l, (a, b) in
                                         sorted(mv.items(), key=lambda x: x[1][0])) or "aucun"))
    versus = [("la méthode du 23 novembre", o["moved_vs_old"])]
    sm = rp.get("same_method") if rp else None  # la campagne précédente recalculée par la méthode de celle-ci
    if rp:
        versus.append(("la campagne précédente, classement publié", rp["moved"]))
    if sm:
        versus.append(("la campagne précédente recalculée par la méthode de celle-ci", sm["moved"]))
    for i, (name, mv) in enumerate(versus):  # contre la campagne précédente : à compilateurs égaux (« Zig 0.17 »)
        who = f"« {asm} »" if asm and i else "Final"
        L.append(f"* {who} contre {name} : " + (", ".join(f"{NAMES[l]} {nth(a)} → {nth(b)}" for l, (a, b) in
                                                          sorted(mv.items(), key=lambda x: x[1][1])) or "aucun"))
    if sm:
        L.append("* Campagne précédente, du classement publié à son recalcul : "
                 + (", ".join(f"{NAMES[l]} {nth(a)} → {nth(b)}" for l, (a, b) in
                              sorted(sm["method_moved"].items(), key=lambda x: x[1][1])) or "aucun"))
    if GCC_CALC in R:
        g, ks = R[GCC_CALC], list(E_V2)
        L += ["", "## C par gcc", "",
              "« C par gcc » : « Final » où toutes les cellules de C viennent de ses constructions par gcc ; la grille "
              "et les autres langages ne changent pas.", "",
              "| C compilé par | Place | Score | Premier | Devance C++ | Plafond | Code naturel | "
              + " | ".join(k.upper() for k in ks) + " |", "|---|" + "---|" * (6 + len(ks))]
        for name, r in (("clang (« Final »)", f), ("gcc", g)):
            L.append(f"| {name} | {place(r, 'c')} | {r['ms_mean']['c']:.1f} | {100 * r['first']['c']:.1f} % | "
                     f"{100 * r['prec_full']['c']['cpp']:.1f} % | {r['E']['c']:.1f} | {100 * r['Dparts']['c']['D1']:.1f} | "
                     + " | ".join(f"{100 * r['Ek']['c'][k]:.0f}" for k in ks) + " |")
    if rp:
        pv, f0 = rp["previous"], f
        f = R[asm] if asm else f  # la campagne telle qu'elle a été mesurée, comme la précédente
        L += ["", "## Réplication : cette campagne et la précédente", ""]
        if asm:
            L += [("Les deux campagnes sont comparées à compilateurs égaux" if asm == ZIG17 else
                   "Les deux campagnes sont comparées à configurations égales")
                  + f" : pour celle-ci, le calcul « {asm} ».", ""]
        L += [f"Cellules mesurées dans les deux campagnes : {rp['cells']}. Rapport des temps (cette campagne sur la "
              f"précédente, estimations ponctuelles) : médiane {rp['median']:.3f} ; {100 * rp['within_10pct']:.0f} % des "
              "cellules à moins de 10 % de cette médiane.", "",
              "| Langage | Place | Précédente, recalculée | Précédente, publiée | Score | Précédent, recalculé | "
              "Précédent, publié | Plafond | Plafond précédent | Rapport médian des temps |",
              "|---|" + "---|" * 9]
        ps = sm["previous"] if sm else None
        for i, l in enumerate(f["order"]):
            rec = (ps["order"].index(l) + 1, f"{ps['ms_mean'][l]:.1f}") if ps else ("–",) * 2
            L.append(f"| {NAMES[l]} | {i + 1} | {rec[0]} | {pv['order'].index(l) + 1} | {f['ms_mean'][l]:.1f} | "
                     f"{rec[1]} | {pv['ms_mean'][l]:.1f} | {f['E'][l]:.1f} | {pv['E'][l]:.1f} | "
                     f"{rp['by_lang'][l]:.3f} |")
        L += ["", "« Publiée » : le classement de la campagne précédente tel qu'il était publié ; « recalculée » : la "
              "même campagne recalculée par la méthode de celle-ci (comparaison à méthode égale). Le plafond, donné au "
              "centre, est le même dans les deux."]
        f = f0
    if zd:
        wc, kinds = zd["witness_vs_campaign"], {}
        for name, c in zd["cells"].items():
            cons, size, k, v, q = name.split("|")
            row = kinds.setdefault((k, cons, v, q), ["–"] * 3)
            row[POS[k].index(size) if k in POS else 1] = f"{c['rho']:.2f} ({c['pairs']})"
        L += ["", "## Zig par sa version de développement", "",
              f"Version {zd['version']}, mesurée hors campagne sur la machine {', '.join(zd['machines'])} avec son "
              f"témoin, la version de la campagne remesurée dans les mêmes groupes : {zd['processes'][1]} et "
              f"{zd['processes'][0]} processus retenus, {len(zd['invalid'])} écartés, {len(zd['absent'])} cellules "
              "sans rapport. Chaque case : rapport du temps sous la version de développement au temps du témoin "
              "(moyenne géométrique des rapports appariés, et nombre de paires) ; les processus de Zig de la campagne "
              "sont multipliés par ce rapport.", "",
              "| Noyau | Étiquette | Variante | " + " | ".join(POS_NAMES) + " |", "|---|---|---|---|---|---|"]
        for (k, cons, v, q), row in sorted(kinds.items()):
            L.append(f"| {k.upper()} | {cons} | {v}{' ' + q if q else ''} | " + " | ".join(row) + " |")
        L += ["", f"Le témoin contre ses temps de la campagne : rapport médian {wc['median']:.2f}, de {wc['min']:.2f} "
              f"à {wc['max']:.2f} ; {100 * wc['within_10pct']:.0f} % des cellules à moins de 10 %. Le transport annule "
              "cet écart. Latences de K8 naturel (p50, p90, p99, p99,9, maximum), rapport des médianes, appliqué dans "
              "le seul calcul « Zig 0.18, latences du plan » : "
              + " ; ".join(f"{name.replace('|', ', ')} : " + ", ".join(f"{x:.2f}" for x in v)
                           for name, v in zd["lat"].items()) + "."]
    if gs:
        fx, ct, n = {}, {}, gs["processes"]
        ms = lambda t: (f"{1e3 * t:,.0f}".replace(",", " ") if t >= 0.1 else  # noqa: E731
                        f"{1e3 * t:.1f}" if t >= 0.01 else f"{1e3 * t:.3g}")
        for name, c in gs["fixed"].items():
            cons, size, k, v, q = name.split("|")
            rows, j = fx.setdefault((cons, v), [["–"] * 3 for _ in range(4)]), POS[k].index(size)
            rows[0][j] = f"{c['rho']:.2f} ({c['pairs']})"
            if c["artifact"] is not None:
                rows[1][j] = f"{c['artifact']:.0f} ({c['artifact_min']:.0f})"
            if c["witness_vs_campaign"]:
                rows[2][j] = f"{c['witness_vs_campaign']:.2f}"
            if c["campaign"] and c["corrected"]:
                rows[3][j] = f"{ms(c['campaign'])} → {ms(c['corrected'])}"
        for name, c in gs["cells"].items():
            cons, size, k, v, q = name.split("|")
            ct.setdefault((k, cons, v, q), ["–"] * 3)[POS[k].index(size) if k in POS else 1] = (
                f"{c['rho']:.2f} ({c['pairs']})")
        rs, wc = gs["rho"], gs["witness_vs_campaign"]
        L += ["", "## Go hors de l'expérience simd", "",
              f"Go est remesuré hors campagne sur la machine {', '.join(gs['machines'])} (`docs/V5_4.md`), dans les "
              "mêmes groupes : sa nouvelle configuration (les variantes sans SIMD explicite dans un binaire compilé "
              "sans `GOEXPERIMENT=simd`), son témoin (le binaire de la campagne) et, pour K1, le pont (C) ; "
              f"{n[1]}, {n[0]} et {n[2]} processus retenus, {len(gs['invalid'])} écartés, {len(gs['absent'])} "
              "cellules faussées sans rapport.", "",
              "Cellules faussées, rebâties par le pont. Rapport au pont : temps de Go dans le binaire standard sur "
              "temps de la cellule de C, moyenne géométrique des rapports appariés (nombre de paires) ; la cellule "
              "prend les processus de C dans la campagne, multipliés par ce rapport. Artefact : rapport du témoin à la "
              "nouvelle configuration, moyenne géométrique (plus petit rapport apparié). Témoin sur campagne : temps "
              "du témoin dans la remesure sur temps de la cellule dans la campagne. Temps : celui de la campagne, puis "
              "le temps corrigé, en millisecondes.", "",
              "| Étiquette | Variante | Grandeur | " + " | ".join(POS_NAMES) + " |", "|---|---|---|---|---|---|"]
        for (cons, v), rows in sorted(fx.items()):
            for label, row in zip(("rapport au pont", "artefact", "témoin sur campagne", "temps (ms)"), rows):
                L.append(f"| {cons} | {v} | {label} | " + " | ".join(row) + " |")
        if rs:
            L += ["", f"Autres cellules, rapport de la nouvelle configuration au témoin (contrôle ; appliqué dans le "
                  f"seul calcul « {GOALL} ») : {len(gs['cells'])} cellules, médiane {rs['median']:.2f}, de "
                  f"{rs['min']:.2f} à {rs['max']:.2f} ; {100 * rs['within_10pct']:.0f} % à moins de 10 % de 1 ; hors "
                  "de 0,8 à 1,25 : " + (", ".join(x.replace("|", " ").strip() for x in gs["outside"])
                                         + " (instruites : `docs/V5_4.md`, 9)" if gs["outside"] else "aucune")
                  + f". Le témoin contre ses temps de la campagne : rapport médian {wc['median']:.2f}, de "
                  f"{wc['min']:.2f} à {wc['max']:.2f}.", "",
                  "| Noyau | Étiquette | Variante | " + " | ".join(POS_NAMES) + " |", "|---|---|---|---|---|---|"]
            for (k, cons, v, q), row in sorted(ct.items()):
                L.append(f"| {k.upper()} | {cons} | {v}{' ' + q if q else ''} | " + " | ".join(row) + " |")
    nat = [(n, R[c]) for n, c in (("mode publié", "Sans R1"), ("R1'", "R1' au lieu de R1")) if c in R]
    L += ["", "## Plafond par noyau et parts du code par défaut (« Final », au centre)", "",
          "| Langage | " + " | ".join(k.upper() for k in E_V2) + " | D1 | D2 | D3 | D4 |"
          + "".join(f" D1, {n} |" for n, r in nat), "|---|" + "---|" * (len(E_V2) + 4 + len(nat))]
    for l in f["order"]:
        L.append(f"| {NAMES[l]} | " + " | ".join(f"{100 * f['Ek'][l][k]:.0f}" for k in E_V2) + " | "
                 + " | ".join(f"{100 * f['Dparts'][l][q]:.0f}" for q in ("D1", "D2", "D3", "D4")) + " |"
                 + "".join(f" {100 * r['Dparts'][l]['D1']:.0f} |" for n, r in nat))
    if nat:
        L += ["", "D1 : code naturel sous R1 (le centre) ; « D1, mode publié » : dans le mode publié de chaque chaîne "
              "(centre de « Sans R1 ») ; « D1, R1' » : sans les vérifications qu'une option retire (centre de « R1' au "
              "lieu de R1 »). Les variantes de « Final » tirent l'un des trois (A7, A8)."]
    imp, tr = o.get("importance"), o.get("triage")
    if imp and imp["groups"]:  # ce qui décide de l'ordre (docs/V5_3.md, 2)
        gs, w = imp["groups"], imp["weights"]
        L += ["", "## Ce qui décide de l'ordre (« Final », au centre)", "",
              "Part de la variance du score au centre que porte chaque composante, parmi les langages d'un groupe "
              "(`docs/V5_3.md`, 2) : covariance de son apport au score avec le score, divisée par la variance du "
              "score. "
              "Les trois piliers somment à 100 % ; les noyaux se partagent la part du plafond, D1 à D4 celle du code "
              "par défaut. Une part négative : la composante joue, dans ce groupe, contre l'ordre du score. Le poids "
              "affiché est celui de la composante dans le score.", "",
              "| Composante | Poids affiché | " + " | ".join(f"{g['name']} ({len(g['langs'])})" for g in gs) + " |",
              "|---|---|" + "---|" * len(gs)]
        comps = ([("Contrôle (grille)", "C", 0), ("Plafond", "E", 0)] + [(k.upper(), k, 1) for k in E_V2]
                 + [("Code par défaut", "D", 0), ("D1, code naturel", "D1", 1), ("D2, coût de structure", "D2", 1),
                    ("D3, queues de latence", "D3", 1), ("D4, hiérarchie mémoire", "D4", 1)])
        for name, key, dec in comps:  # piliers en gras, sans décimale ; leurs composantes à une décimale
            b = "" if dec else "**"
            L.append(f"| {b}{name}{b} | {100 * w[key]:.{2 if key in ('D2', 'D3') else dec}f} % | "
                     + " | ".join(f"{b}{round(100 * g['shares'][key], dec) + 0.0:.{dec}f} %{b}" for g in gs) + " |")
        L += ["", "Écart-type du score au centre dans chaque groupe : "
              + ", ".join(f"{g['sd']:.1f} ({g['name']})" for g in gs) + ". "
              + " ".join(f"{g['name'].capitalize()} : {', '.join(star(l) for l in g['langs'])}." for g in gs[1:])
              + " « Première moitié possible » et « podium possible » : rang plausible commençant à "
              + " et à ".join(str(n) for name, n in HEADS) + " ou mieux."]
    if tr:  # tri des écarts du code naturel (docs/V5_3.md, 3)
        rows = sorted(tr["rows"], key=lambda x: (f["order"].index(x["lang"]), x["sense"]))
        modes = [m for m, nat in TRI_MODES]
        cn = lambda x: ", ".join(dict.fromkeys("?" if n is None else str(n + 1) for n in x["cause"].values()))  # noqa
        L += ["", "## Tri des écarts du code naturel", "",
              f"Règle (`docs/V5_3.md`, 3) : pour chaque mesure du code naturel, à chaque taille et dans chaque mode du "
              f"tirage, le temps d'un langage est rapporté à la médiane des temps de {len(tr['peers'])} pairs, les "
              "langages dont la chaîne produit son code machine par LLVM ou par GCC ("
              + ", ".join(NAMES[l] for l in f["order"] if l in tr["peers"]) + "). Pour les autres langages, ce rapport "
              "est divisé par leur niveau : la médiane de leurs rapports à cette taille et dans ce mode, au moins 1. "
              f"Une cellule est lente à partir de {tr['factor']:.1f} (arrondi au dixième), rapide quand elle est au "
              f"moins {tr['factor']:.1f} fois plus rapide que la médiane des pairs ; un couple (langage, mesure) est "
              "signalé dans un mode s'il l'est à une taille au moins. Chaque couple signalé est rattaché à une cause : "
              "« établie » (un contrôle nommé la montre), « attribuée » (cause probable, sans contrôle propre), « à "
              "corriger » (cellule faussée par l'étude, correction à planifier) ou « à examiner » (aucune cause).", "",
              f"{len(rows)} couples signalés : "
              + ", ".join(f"{n} dont la cause est {s}" if s in TRI_STATUS[:2] else f"{n} {s}"
                          for s, n in tr["counts"].items()) + "."]
        if tr["causes"]:
            L += ["", "| n° | Statut | Cause | Contrôle | Couples |", "|---|---|---|---|---|"]
            for n, c in enumerate(tr["causes"]):
                cells = []
                for x in rows:
                    ms = [m for m in modes if x["cause"].get(m, -1) == n]
                    if ms:
                        cells.append(f"{star(x['lang'])} {x['measure']}"
                                     + ("" if len(ms) == len(x["cause"]) else f" ({', '.join(ms)})"))
                L.append(f"| {n + 1} | {c['status']} | {c['cause']} | {c['control']} | {', '.join(cells) or '–'} |")
        L += ["", "| Langage | Mesure | Sens | " + " | ".join(m.capitalize() for m in modes)
              + " | Niveau | Cause | Statut |",
              "|---|---|---|" + "---|" * (len(modes) + 3)]
        for x in rows:
            vals = []
            for m in modes:
                v = x["ratio"].get(m)
                s = "–" if v is None else (f"{v:.1f}" if x["sense"] == "lent" else f"{v:.2f}")
                vals.append(f"**{s}**" if m in x["sizes"] else s)
            lv = "1" if x["lang"] in tr["peers"] else f"{x['level'][0]:.1f} à {x['level'][1]:.1f}"
            L.append(f"| {star(x['lang'])} | {x['measure']} | {x['sense']} | " + " | ".join(vals)
                     + f" | {lv} | {cn(x)} | {x['status']} |")
        L += ["", "Chaque case : le rapport le plus extrême des trois tailles (lent : rapport au niveau du langage, le "
              "plus grand ; rapide : rapport à la médiane des pairs, le plus petit), en gras dans les modes où le "
              "couple est signalé. Niveau : 1 pour un pair ; pour les autres, étendue sur les tailles et les modes."]
        if tr["stale"]:
            L += ["", "Entrées du registre sans couple signalé : " + ", ".join(tr["stale"]) + "."]
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
    L += ["", "## Campagne", ""]
    if sp["median"]:
        L += [f"Écart entre la passe la plus lente et la plus rapide d'une cellule : médiane "
              f"{100 * (sp['median'] - 1):.1f} % ; {sp['over_20pct']} cellules sur {sp['cells']} au-delà de 20 %. Une "
              f"fois retiré l'effet commun de chaque groupe dans chaque passe (A5) : médiane "
              f"{100 * (sp['net_median'] - 1):.1f} % ; {sp['net_over_20pct']} cellules au-delà de 20 %.", ""]
    be = sorted((abs(v), k, ps) for k, d in o["block_effects"].items() for ps, v in d.items())
    if be:
        a, k, ps = be[-1]
        L += [f"Effet commun d'un groupe dans une passe (A5) : médiane des valeurs absolues "
              f"{100 * (math.exp(float(np.median([x[0] for x in be]))) - 1):.1f} % ; le plus fort : "
              f"{100 * (math.exp(a) - 1):.1f} % ({k.replace('|', ' ')}, passe {ps}).", ""]
    L += [f"Borne à quatre fils (STREAM triad sur 4 fils) : {o['hw']['stream4'] / 1e9:.1f} Go/s avec la sonde corrigée "
          f"(A6) ; relevé d'origine : {o['stream4_original'] / 1e9:.1f} Go/s.", "",
          "Machine de chaque groupe et de chaque passe :", ""]
    gm_ = defaultdict(list)
    for k, v in o["group_machines"].items():
        gm_["/".join(v)].append(k.replace("|", " "))
    for m, gl in gm_.items():
        L.append(f"* machine {m} : {len(gl)} groupes")
    me = o.get("machine_effect")
    if me:
        ks = sorted({k for x in me["machines"].values() for k in x["by_kernel"]})
        L += ["", f"Effet de machine : rapport des temps d'une cellule sur une machine à ses temps sur la machine "
              f"{me['first']} (médianes de ses processus), pour les cellules mesurées sur les deux.", "",
              "| Machine | Cellules | Rapport médian | À moins de 5 % de ce rapport | "
              + " | ".join(k.upper() for k in ks) + " |", "|---|" + "---|" * (3 + len(ks))]
        for m, x in me["machines"].items():
            L.append(f"| {m} | {x['cells']} | {x['median']:.3f} | {100 * x['within_5pct']:.0f} % | "
                     + " | ".join(f"{x['by_kernel'][k]:.3f}" if k in x["by_kernel"] else "–" for k in ks) + " |")
    else:
        L += ["", "Effet de machine : sans objet, une seule machine a mesuré la campagne."]
    L += ["", "## Cellules", ""]
    same = defaultdict(list)  # texte -> calculs qui le partagent
    for c in calcs:
        r = R[c]
        nf = sum(len(v) for v in r["filled"].values())
        if r["missing"] or nf:
            same["formes ou cellules substituées manquantes : "
                 + (", ".join(f"{NAMES.get(x[0], x[0])} {x[1]} {x[2]} ({x[3]})" for x in r["missing"]) or "aucune")
                 + " ; cellules de la base remplies (temps le plus lent des autres langages) : "
                 + (", ".join(f"{NAMES.get(x[0], x[0])} {x[1]} ({t})" for t, v in r["filled"].items() for x in v)
                    or "aucune")].append(c)
    for text, cs in same.items():
        L.append(f"* {'Tous les calculs' if len(cs) == len(calcs) else ', '.join(cs)} : {text}")
    cm, gc = o["cpu_models"], o.get("gcc")
    L += ["", "Processeur des enregistrements : " + " ; ".join(
        f"{m} ({sum(ps.values())} enregistrements)" for m, ps in cm.items())
          + (" ; C par gcc : " + " ; ".join(f"{m} ({n} enregistrements)" for m, n in gc["cpu_models"].items())
             if gc else "")
          + (" — **plusieurs modèles**" if len(set(cm) | set(gc["cpu_models"] if gc else ())) > 1 else "") + "."]
    for name, x in [("", o)] + ([("C par gcc : ", gc)] if gc else []):
        sk = defaultdict(set)
        for y in x["skipped"]:
            sk[(y["lang"], y["construction"], y["size"], " ".join(y["key"]))].add(y["status"])
        L += ["", f"{name}{'processus' if name else 'Processus'} écartés : {len(x['failures'])} ; cellules non "
              f"exécutées (étalonnage hors mémoire ou hors durée) : {len(sk)} ; vol de temps > 5 % après reprise : "
              f"{len(x['steal_over_5pct'])}."]
        for y in x["failures"]:
            L.append(f"* {NAMES.get(y['lang'], y['lang'])} {y['construction']} {y['size']} {' '.join(y['key'])} passe "
                     f"{y['pass']} : code {y['returncode']}, contrôles {y['oks']}{', hors mémoire' if y['oom'] else ''}"
                     f"{', durée' if y['timeout'] else ''}")
        for (l, c, s_, k), st in sorted(sk.items()):
            L.append(f"* non exécutée : {NAMES.get(l, l)} {c} {s_} {k} ({', '.join(sorted(st))})")
    open(REPORT, "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
