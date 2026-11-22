#!/usr/bin/env python3
"""v4, point 5 (docs/V4_COST.md, 3.2 à 3.5) : contrôle du relevé des régions et comptage.

Usage :
  count.py --check [langage…]   contrôle le relevé (tools/cost/regions.py) : empreinte de chaque fichier, bornes des
                                intervalles, chevauchements dans une forme, fonction d'entrée présente, formes requises
                                présentes (formes d'accès et candidates du calcul principal et de la sensibilité (d),
                                références naturelles : tools/cost/needed.py) ; n'affiche aucun compte.
  count.py                      comptage de tous les langages relevés : results/cost/counts.json,
                                results/cost/regions.md (régions de chaque forme), results/cost/matches.md (chaque
                                occurrence d'une construction recherchée, dans une région ou non, à examiner).
Par forme : lignes de code (L), lexèmes (T), lignes dans la portée d'une construction qui contourne une vérification
(U, part marginale), lignes propres à une architecture (X) ; par fichier : lignes propres à une architecture dans le
fichier entier (prévision de la compilation croisée, 3.5)."""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import lex  # noqa: E402
import patterns as P  # noqa: E402
from regions import LANGS  # noqa: E402

OUT = os.path.join(ROOT, "results", "cost")


def blob(path):
    return subprocess.run(["git", "hash-object", path], capture_output=True, text=True, check=True).stdout.strip()


def indent(s):
    return len(s) - len(s.lstrip(" \t"))


# ------------------------------------------------------------------ portées
def scope_brace(lang, lines, i, pos):
    """La ligne i et le bloc entre accolades ouvert à partir de la position pos (ou sur une ligne suivante)."""
    depth, started, out = 0, False, set()
    for j in range(i, len(lines)):
        s = lex.blank_strings(lang, lines[j])
        k0 = pos if j == i else 0
        out.add(j)
        for ch in s[k0:]:
            if ch == "{":
                depth += 1
                started = True
            elif ch == "}" and started:
                depth -= 1
                if depth == 0:
                    return out
        if not started and j > i + 3:
            return {i}      # pas d'accolade dans les trois lignes suivantes : la ligne seule
    return out


BLOCK_KW = re.compile(r"\b(for|while|begin|let|if)\b")


def scope_indent(lines, i, m_end):
    if not BLOCK_KW.search(lines[i][m_end:]):
        return {i}
    base, out = indent(lines[i]), {i}
    for j in range(i + 1, len(lines)):
        s = lines[j]
        if not s.strip():
            continue
        if indent(s) > base:
            out.add(j)
            continue
        if indent(s) == base and s.strip() == "end":
            out.add(j)
        break
    return out


def scope_pushpop(lines, i):
    out = {i}
    for j in range(i + 1, len(lines)):
        out.add(j)
        if re.search(r"\{\.\s*pop\s*\.\}", lines[j]):
            break
    return out


SUB = re.compile(r"^\s*(?:(?:not\s+)?overriding\s+)?(procedure|function)\s+(\w+)", re.I)
DECLARE = re.compile(r"^\s*declare\s*$", re.I)


def scope_unit(lines, i):
    """Ada : la région déclarative qui contient la ligne i : le bloc « declare » (de declare à son « end; ») ou le
    sous-programme (de son en-tête à son « end Nom; »), le plus proche des deux (en-tête moins indenté que la ligne).
    Correction du 22 novembre, à l'examen des occurrences (docs/V4_COST.md, 11) : un pragma placé dans un bloc declare
    ne s'applique qu'au bloc ; les en-têtes « overriding procedure » sont reconnus."""
    for h in range(i - 1, -1, -1):
        if not lines[h].strip() or indent(lines[h]) >= indent(lines[i]):
            continue
        if DECLARE.match(lines[h]):
            base = indent(lines[h])
            for j in range(i + 1, len(lines)):
                if re.match(r"^\s*end\s*;", lines[j]) and indent(lines[j]) == base:
                    return set(range(h, j + 1))
            break
        m = SUB.match(lines[h])
        if m:
            name, base = m.group(2), indent(lines[h])
            end = re.compile(r"^\s*end\s+" + re.escape(name) + r"\s*;", re.I)
            for j in range(i + 1, len(lines)):
                if end.match(lines[j]) and indent(lines[j]) == base:
                    return set(range(h, j + 1))
            break
    return {i}


def scope_ir(lines, i, m_end):
    """Julia : la ligne de llvmcall et la chaîne d'IR qu'elle reçoit (constante « const NOM = (\"\"\" … \"\"\", … ) »)."""
    out = {i}
    m = re.match(r"\s*\(\s*(\w+)\s*,", lines[i][m_end:])
    if not m:
        return out
    start = re.compile(r"^const\s+" + re.escape(m.group(1)) + r"\s*=")
    for h, s in enumerate(lines):
        if start.match(s):
            for j in range(h, len(lines)):
                out.add(j)
                if j > h and '"""' in lines[j]:
                    return out
    return out


# ------------------------------------------------------------------ fichiers
def analyse_file(lang, path):
    text = open(path, encoding="utf-8").read()
    lines = lex.strip(lang, text)
    code = {i for i, s in enumerate(lines) if lex.is_code(s)}
    unchecked, matches = set(), []
    for rx, kind in P.unchecked(lang):
        for i, s in enumerate(lines):
            for m in rx.finditer(s):
                if lang == "csharp" and kind == "brace" and re.search(r"\bclass\b", s):
                    matches.append(("U", i, m.group(0), "modificateur de classe : pas de portée"))
                    continue
                if kind == "line":
                    sc = {i}
                elif kind == "brace":
                    sc = scope_brace(lang, lines, i, m.start())
                elif kind == "indent":
                    sc = scope_indent(lines, i, m.end())
                elif kind == "pushpop":
                    sc = scope_pushpop(lines, i)
                elif kind == "ir":
                    sc = scope_ir(lines, i, m.end())
                else:
                    sc = scope_unit(lines, i)
                unchecked |= sc
                matches.append(("U", i, m.group(0), f"portée {kind} : lignes {min(sc) + 1} à {max(sc) + 1}"))
    archl = set()
    for rx in P.arch(lang):
        for i, s in enumerate(lines):
            for m in rx.finditer(s):
                if P.EMPTY_ASM.search(s):
                    matches.append(("X", i, m.group(0), "barrière à gabarit vide : pas propre à une architecture"))
                    continue
                archl.add(i)
                matches.append(("X", i, m.group(0), ""))
    toks = {i: len(lex.tokens(lang, lines[i])) for i in code}
    return {"lines": lines, "raw": text.split("\n"), "code": code, "unchecked": unchecked & code,
            "arch": archl & code, "tokens": toks, "matches": matches}


def form_lines(L, files, regs):
    out = {}
    for r in regs:
        for f, a, b in L["regions"][r]:
            out.setdefault(f, set()).update(range(a - 1, b))
    return out


# ------------------------------------------------------------------ contrôle
def check(langs):
    import needed as N
    need = N.needed()
    bad = 0
    for lang in langs:
        L = LANGS[lang]
        d = os.path.join(ROOT, L["dir"])
        errs = []
        sizes = {}
        for f, h in L["files"].items():
            p = os.path.join(d, f)
            if blob(p) != h:
                errs.append(f"{f} : empreinte {blob(p)} au lieu de {h}")
            sizes[f] = len(open(p, encoding="utf-8").read().split("\n"))
        for r, rng in L["regions"].items():
            for f, a, b in rng:
                if f not in sizes or not (1 <= a <= b <= sizes[f]):
                    errs.append(f"région {r} : intervalle {f}:{a}-{b} hors du fichier")
        for key, (entry, regs) in L["forms"].items():
            seen = {}
            for r in regs:
                if r not in L["regions"]:
                    errs.append(f"forme {key} : région {r} absente")
                    continue
                for f, a, b in L["regions"][r]:
                    for x in range(a, b + 1):
                        if (f, x) in seen:
                            errs.append(f"forme {key} : ligne {f}:{x} dans {seen[(f, x)]} et {r}")
                            break
                        seen[(f, x)] = r
            fl = form_lines(L, L["files"], [r for r in regs if r in L["regions"]])
            found = False
            for f, ls in fl.items():
                text = open(os.path.join(d, f), encoding="utf-8").read().split("\n")
                if any(re.search(r"(?<![\w$])" + re.escape(entry) + r"(?![\w])", text[x]) for x in ls if x < len(text)):
                    found = True
            if not found:
                errs.append(f"forme {key} : fonction d'entrée {entry} absente de ses régions")
        for key in sorted(need.get(lang, [])):
            if key not in L["forms"]:
                errs.append(f"forme requise {key} absente du relevé")
        print(f"{lang} : " + ("relevé conforme" if not errs else f"{len(errs)} erreur(s)"))
        for e in errs:
            print("   ", e)
        bad += len(errs)
    return bad


# ------------------------------------------------------------------ comptage
def count():
    res, reg_md, match_md = {}, ["# Régions des formes (v4, point 5)", "",
                                 "*Écrit par `tools/cost/count.py` à partir du relevé `tools/cost/regions.py` ; plan : "
                                 "`docs/V4_COST.md`, 3.2. Intervalles de lignes (bornes comprises) dans les copies "
                                 "`bench/<langage>_cv`.*", ""], \
        ["# Constructions trouvées (v4, point 5)", "",
         "*Écrit par `tools/cost/count.py`. U : contourne une vérification (3.4) ; X : propre à une architecture (3.5). "
         "Chaque occurrence est à examiner ; « hors région » : dans le fichier, dans aucune région relevée.*", ""]
    for lang, L in LANGS.items():
        d = os.path.join(ROOT, L["dir"])
        A = {f: analyse_file(lang, os.path.join(d, f)) for f in L["files"]}
        forms = {}
        inreg = set()
        reg_md += [f"## {lang}", ""]
        for key, (entry, regs) in sorted(L["forms"].items()):
            fl = form_lines(L, L["files"], regs)
            Lc = T = U = X = 0
            for f, ls in fl.items():
                a = A[f]
                c = ls & a["code"]
                Lc += len(c)
                T += sum(a["tokens"][i] for i in c)
                U += len(c & a["unchecked"])
                X += len(c & a["arch"])
                inreg |= {(f, i) for i in ls}
            forms[key] = {"entry": entry, "regions": regs, "L": Lc, "T": T, "U": U, "X": X}
            reg_md.append(f"* `{key}` (entrée `{entry}`) : " + " ; ".join(
                f"{r} " + ", ".join(f"{f}:{a}-{b}" for f, a, b in L["regions"][r]) for r in regs)
                + f" — L {Lc}, T {T}, U {U}, X {X}")
        reg_md.append("")
        files = {f: {"arch_lines": sorted(i + 1 for i in A[f]["arch"]), "code_lines": len(A[f]["code"])}
                 for f in L["files"]}
        res[lang] = {"forms": forms, "files": files, "no_check_mode": lang in P.NO_CHECK_MODE}
        match_md += [f"## {lang}", ""]
        for f in L["files"]:
            for kind, i, txt, note in sorted(A[f]["matches"], key=lambda x: (x[1], x[0])):
                where = "région" if (f, i) in inreg else "hors région"
                match_md.append(f"* {kind} {f}:{i + 1} `{txt}` ({where}{' ; ' + note if note else ''}) : "
                                f"`{A[f]['raw'][i].strip()[:110]}`")
        match_md.append("")
    os.makedirs(OUT, exist_ok=True)
    json.dump(res, open(os.path.join(OUT, "counts.json"), "w"), indent=1, ensure_ascii=False)
    open(os.path.join(OUT, "regions.md"), "w").write("\n".join(reg_md) + "\n")
    open(os.path.join(OUT, "matches.md"), "w").write("\n".join(match_md) + "\n")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        sys.exit(1 if check(sys.argv[2:] or list(LANGS)) else 0)
    count()
