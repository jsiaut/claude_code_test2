#!/usr/bin/env python3
"""Tailles des langages sans construction (docs/METHOD.md, 3) : Julia, dont le source est exécuté tel quel.

Le source publié ne change pas. La copie d'un jeu de tailles (tools/final/build.py) remplace les seules constantes de
taille du source par celles du jeu : chaque entrée donne le texte publié exact, le texte de remplacement (gabarit de
str.format, champs ci-dessous) et le nombre d'occurrences attendu, vérifié à chaque copie. Le code exécuté à une autre
taille est donc le code publié, aux constantes de taille près, comme pour les langages compilés.

Champs des gabarits : N1, INNER5, N6, K7_LOG (K7_LOG2 + 1), K8_LONG, K8_REQ, K8_NODES ((2 << K8_REQ) - 1), M9."""

PATCHES = {
    "julia": ("ms.jl", [
        ("const N1 = 1 << 22\n", "const N1 = {N1}\n", 1),
        ("const INNER5 = 1 << 16\n", "const INNER5 = {INNER5}\n", 1),
        ("const N6 = 1 << 24\n", "const N6 = {N6}\n", 1),
        ("            LOG = 21; CAP = 1 << LOG\n", "            LOG = {K7_LOG}; CAP = 1 << LOG\n", 1),
        ("    KEEP[] = t_build(20, Ref(0));", "    KEEP[] = t_build({K8_LONG}, Ref(0));", 1),
        ("    arena = Vector{ANode}(undef, 2047)\n", "    arena = Vector{{ANode}}(undef, {K8_NODES})\n", 1),
        ("s = a_sum(arena, a_build(arena, top, 10, c))", "s = a_sum(arena, a_build(arena, top, {K8_REQ}, c))", 1),
        ("s = t_sum(t_build(10, c))", "s = t_sum(t_build({K8_REQ}, c))", 1),
        ("const M9 = 2048\n", "const M9 = {M9}\n", 1),
    ]),
}

# Formes du catalogue (docs/METHOD.md, 4) : elles ajoutent leurs propres constantes de taille à celles des variantes
# publiées.
EXTRA = {
    "julia": [("const K7_LOG = 21\n", "const K7_LOG = {K7_LOG}\n", 1),
              ("const K8_REQ = 10\n", "const K8_REQ = {K8_REQ}\n", 1)],
}
for _lang, _more in EXTRA.items():
    PATCHES[_lang] = (PATCHES[_lang][0], PATCHES[_lang][1] + _more)


def fields(params):
    """Champs des gabarits à partir des paramètres d'un jeu (tools/sizes/sizes.py, set_params)."""
    p = {k[3:]: int(v) for k, v in params.items()}  # MS_N1 -> N1
    p["K7_LOG"] = p["K7_LOG2"] + 1
    p["K8_NODES"] = (2 << p["K8_REQ"]) - 1
    return p


def apply(lang, text, params):
    """Remplace les constantes de taille du source publié ; vérifie le nombre d'occurrences de chaque motif."""
    f = fields(params)
    for old, new, count in PATCHES[lang][1]:
        n = text.count(old)
        if n != count:
            raise SystemExit(f"{lang} : motif {old!r} trouvé {n} fois, {count} attendu(s)")
        text = text.replace(old, new.format(**f))
    return text
