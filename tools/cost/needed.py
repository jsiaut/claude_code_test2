"""v4, point 5 (docs/V4_COST.md, 3.1) : formes requises par langage et par cellule du plafond, d'après la campagne du
point 4 (results/converge/raw, relevé results/converge/forms.json).

Pour chaque langage et chaque cellule : les formes admises (variantes publiées de la cellule dans E_V2, formes écrites
ou présentes du relevé du point 4), leur temps (moyenne géométrique des médianes de processus, construction pub pour
les variantes publiées et les formes présentes, cv pour les formes écrites), la plus rapide (forme d'accès du calcul
principal : celle que retient « Convergent » au point 4 pour ses dix cellules ; pour K1 et K3, la plus rapide des
formes publiées), les candidates à 10 % ou moins de la plus rapide (sensibilité (d)), et la référence naturelle de la
cellule (K3 : la variante packed du schéma de chaque forme candidate)."""
import glob, json, math, os, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "analysis"))
from analyze_v2 import E_V2, RANKED  # noqa: E402

CELLS = {"K1": ("k1", 0), "K3": ("k3", 0), "K4": ("k4", 0), "K5": ("k5", 0), "Q6": ("k6", 0), "Q1": ("k6", 1),
         "Q6 mt": ("k6", 2), "Q1 mt": ("k6", 3), "K7": ("k7", 0), "K8": ("k8", 0), "K9": ("k9", 0), "K9 mt": ("k9", 1)}
NATURAL = {"K1": "k1|natural|energy", "K4": "k4|natural_unsorted|", "K5": "k5|natural|", "Q6": "k6|natural|q6",
           "Q1": "k6|natural|q1", "Q6 mt": "k6|natural|q6", "Q1 mt": "k6|natural|q1", "K7": "k7|natural|",
           "K8": "k8|natural|", "K9": "k9|natural|", "K9 mt": "k9|natural|"}
NEAR = 0.10


def k(t):
    return "|".join(t)


def k3_ref(key):
    """K3 : la variante packed du même schéma (sw_padded -> sw_packed, rmw_padded -> rmw_packed)."""
    return key.replace("_padded", "_packed")


def times():
    procs = defaultdict(list)
    for f in glob.glob(os.path.join(ROOT, "results", "converge", "raw", "*.jsonl")):
        for line in open(f):
            r = json.loads(line)
            if r["build"] == "old" or r.get("oks") != ["True"] or r.get("returncode") != 0:
                continue
            procs[(r["lang"], r["build"], k((r["kernel"], r["variant"], r["param"])))].append(r["median"])
    return {x: math.exp(sum(math.log(v) for v in vs) / len(vs)) for x, vs in procs.items()}


def cells():
    """{langage: {cellule: {"forms": [(clé, construction, temps)], "best": clé, "near": [clés], "natural": [clés]}}}"""
    T = times()
    fc = json.load(open(os.path.join(ROOT, "results", "converge", "forms.json")))["langs"]
    out = {}
    for l in RANKED:
        row = {}
        for c, (kern, gi) in CELLS.items():
            cand = [(k(key), "pub") for key in E_V2[kern][gi]]
            for form, x in sorted(fc.get(l, {}).items()):
                if x["status"] in ("écrite", "présente") and x["ceiling"] == c:
                    for cell in x["cells"]:
                        b = "cv" if x["status"] == "écrite" else "pub"
                        if (k(cell), b) not in cand:
                            cand.append((k(cell), b))
            forms = [(key, b, T[(l, b, key)]) for key, b in cand if (l, b, key) in T]
            if not forms:
                continue
            best = min(forms, key=lambda x: x[2])
            near = sorted({key for key, b, t in forms if t <= (1 + NEAR) * best[2]})
            nat = sorted({k3_ref(x) for x in near} | {k3_ref(best[0])}) if c == "K3" else [NATURAL[c]]
            row[c] = {"forms": forms, "best": best[0], "near": near, "natural": nat}
        out[l] = row
    return out


def needed():
    """{langage: ensemble des clés à relever}."""
    out = {}
    for l, row in cells().items():
        s = set()
        for c, x in row.items():
            s |= {x["best"]} | set(x["near"]) | set(x["natural"])
        out[l] = s
    return out


if __name__ == "__main__":
    for l, s in needed().items():
        print(l, len(s), " ".join(sorted(s)))
