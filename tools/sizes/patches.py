#!/usr/bin/env python3
"""v4, point 2 (docs/V4_SIZES.md) : tailles des langages interprétés ou à JIT sans construction.

Leurs sources publiées ne changent pas. La copie d'un jeu de tailles (tools/sizes/build.py) remplace les seules
constantes de taille du source par celles du jeu : chaque entrée donne le texte publié exact, le texte de remplacement
(gabarit Python, champs ci-dessous) et le nombre d'occurrences attendu, vérifié à chaque copie. Le code exécuté à une
autre taille est donc le code publié, aux constantes de taille près, comme pour les langages compilés.

Champs des gabarits : N1, INNER5, N6, N6_4 (N6 / 4), K7_LOG (K7_LOG2 + 1), K8_LONG, K8_REQ, K8_NODES ((2 << K8_REQ) - 1),
M9."""

PATCHES = {
    "python": ("ms.py", [
        ("N1 = 1 << 22\n", "N1 = {N1}\n", 1),
        ("INNER5 = 1 << 16\n", "INNER5 = {INNER5}\n", 1),
        ("N6 = 1 << 24\n", "N6 = {N6}\n", 1),
        ("AV, AL, AR = [0] * 2047, [-1] * 2047, [-1] * 2047\n",
         "AV, AL, AR = [0] * {K8_NODES}, [-1] * {K8_NODES}, [-1] * {K8_NODES}\n", 1),
        ("    keep = t_build(20)\n", "    keep = t_build({K8_LONG})\n", 1),
        ("s = a_sum(a_build(10, 0)[0])", "s = a_sum(a_build({K8_REQ}, 0)[0])", 1),
        ("s = t_sum(t_build(10))", "s = t_sum(t_build({K8_REQ}))", 1),
        ("M9 = 2048\n", "M9 = {M9}\n", 1),
    ]),
    "lua": ("ms.lua", [
        ("local N1 = 1 << 22\n", "local N1 = {N1}\n", 1),
        ("local INNER5 = 1 << 16\n", "local INNER5 = {INNER5}\n", 1),
        ("local N6 = 1 << 24\n", "local N6 = {N6}\n", 1),
        ("  local keep = t_build(20)\n", "  local keep = t_build({K8_LONG})\n", 1),
        ("s = a_sum(a_build(10)) else s = t_sum(t_build(10))", "s = a_sum(a_build({K8_REQ})) else s = t_sum(t_build({K8_REQ}))", 1),
        ("local M9 = 2048\n", "local M9 = {M9}\n", 1),
    ]),
    "php": ("ms.php", [
        ("const N1 = 1 << 22;\n", "const N1 = {N1};\n", 1),
        ("const INNER5 = 1 << 16;\n", "const INNER5 = {INNER5};\n", 1),
        ("const N6 = 1 << 24;\n", "const N6 = {N6};\n", 1),
        ("            $cap = 1 << 21;\n", "            $cap = 1 << {K7_LOG};\n", 1),
        ("    $keep = t_build(20);\n", "    $keep = t_build({K8_LONG});\n", 1),
        ("array_fill(0, 2047, ", "array_fill(0, {K8_NODES}, ", 3),
        ("a_build(10, $q, ", "a_build({K8_REQ}, $q, ", 1),
        ("$s = t_sum(t_build(10));", "$s = t_sum(t_build({K8_REQ}));", 1),
        ("const M9 = 2048;\n", "const M9 = {M9};\n", 1),
    ]),
    "bqn": ("ms.bqn", [
        ("n1 ← 4194304\n", "n1 ← {N1}\n", 1),
        ("⍟65536 0‿a}", "⍟{INNER5} 0‿a}}", 2),
        ("n6 ← 16777216\n", "n6 ← {N6}\n", 1),
        ("Chunks ← {<˘ 4‿4194304 ⥊ 𝕩}", "Chunks ← {{<˘ 4‿{N6_4} ⥊ 𝕩}}", 1),
        ("  val ← c + ↕2047\n", "  val ← c + ↕{K8_NODES}\n", 1),
        ("}⍟10 ⟨⟨0⟩, 2047, 2047⥊¯1, 2047⥊¯1⟩", "}}⍟{K8_REQ} ⟨⟨0⟩, {K8_NODES}, {K8_NODES}⥊¯1, {K8_NODES}⥊¯1⟩", 1),
        ("  long‿· ← Build 20‿0\n", "  long‿· ← Build {K8_LONG}‿0\n", 1),
        ("{TSum ⊑ Build 10‿𝕩}", "{{TSum ⊑ Build {K8_REQ}‿𝕩}}", 1),
        ("{NSum ⊑ NBuild 10‿𝕩}", "{{NSum ⊑ NBuild {K8_REQ}‿𝕩}}", 1),
        ("m9 ← 2048\n", "m9 ← {M9}\n", 1),
    ]),
    "js": ("ms.js", [
        ("const N1 = 1 << 22;\n", "const N1 = {N1};\n", 1),
        ("const INNER5 = 1 << 16;\n", "const INNER5 = {INNER5};\n", 1),
        ("const N6 = 1 << 24;\n", "const N6 = {N6};\n", 1),
        ("      const LOG = 21, CAP = 1 << LOG;\n", "      const LOG = {K7_LOG}, CAP = 1 << LOG;\n", 1),
        ("const av = new Float64Array(2047), al = new Int32Array(2047), ar = new Int32Array(2047);",
         "const av = new Float64Array({K8_NODES}), al = new Int32Array({K8_NODES}), ar = new Int32Array({K8_NODES});", 1),
        ("const keep = tBuild(20);", "const keep = tBuild({K8_LONG});", 1),
        ("s = aSum(aBuild(10)); } else s = tSum(tBuild(10));", "s = aSum(aBuild({K8_REQ})); }} else s = tSum(tBuild({K8_REQ}));", 1),
        ("const M9 = 2048;\n", "const M9 = {M9};\n", 1),
    ]),
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


def fields(params):
    """Champs des gabarits à partir des paramètres d'un jeu (tools/sizes/sizes.py, set_params)."""
    p = {k[3:]: int(v) for k, v in params.items()}  # MS_N1 -> N1
    p["N6_4"] = p["N6"] // 4
    p["K7_LOG"] = p["K7_LOG2"] + 1
    p["K8_NODES"] = (2 << p["K8_REQ"]) - 1
    # v4, point 4 : décalage du compte dans la table tassée de Lua (rq_pack) : la somme d'une clé (au plus N7 × 999)
    # doit tenir sous ce bit ; 35 à la taille publiée
    p["K7_SUMBITS"] = max(35, (p["N7"] * 999).bit_length()) if "N7" in p else 35
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


# v4, point 4 (docs/V4_CONVERGE.md, 3.2, 5) : copies bench/<langage>_cv des langages sans construction. Les motifs du
# source publié s'y trouvent aux mêmes comptes ; les formes nouvelles y ajoutent leurs propres constantes de taille.
CV_EXTRA = {
    "python": [("tab = k7_tuned_oa(keys, vals, 21)", "tab = k7_tuned_oa(keys, vals, {K7_LOG})", 1),
               ('tval, tit, d8 = v == "tuned_val", v == "tuned_it", 10', 'tval, tit, d8 = v == "tuned_val", v == "tuned_it", {K8_REQ}', 1)],
    "lua": [("local tab = k7_tuned_oa(keys, vals, n, 21)", "local tab = k7_tuned_oa(keys, vals, n, {K7_LOG})", 1),
            ("if tval then a_build_val(1, 10, q)", "if tval then a_build_val(1, {K8_REQ}, q)", 1),
            ("s = a_sum_it(a_build_it(10))", "s = a_sum_it(a_build_it({K8_REQ}))", 1),
            ("local ONE = 1 << 35", "local ONE = 1 << {K7_SUMBITS}", 1)],
    "php": [("            $log = 21;\n", "            $log = {K7_LOG};\n", 1),
            ("a_build_val(0, 10, $q, $av, $al, $ar);", "a_build_val(0, {K8_REQ}, $q, $av, $al, $ar);", 1)],
    "bqn": [("  d8 ← 10 ⋄ n8 ← 2047\n", "  d8 ← {K8_REQ} ⋄ n8 ← {K8_NODES}\n", 1)],
    "js": [("  const D8 = 10;\n", "  const D8 = {K8_REQ};\n", 1)],
    "julia": [("const K7_LOG = 21\n", "const K7_LOG = {K7_LOG}\n", 1),
              ("const K8_REQ = 10\n", "const K8_REQ = {K8_REQ}\n", 1)],
}
CV_PATCHES = {lang: (PATCHES[lang][0], PATCHES[lang][1] + CV_EXTRA[lang]) for lang in CV_EXTRA}


def apply_cv(lang, text, params):
    """Comme apply, pour la copie bench/<langage>_cv (point 4)."""
    f = fields(params)
    for old, new, count in CV_PATCHES[lang][1]:
        n = text.count(old)
        if n != count:
            raise SystemExit(f"{lang} (_cv) : motif {old!r} trouvé {n} fois, {count} attendu(s)")
        text = text.replace(old, new.format(**f))
    return text
