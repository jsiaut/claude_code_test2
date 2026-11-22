"""v4, point 5 (docs/V4_COST.md, 3.3) : règles lexicales des 25 langages, pour compter les lignes de code et les
lexèmes d'une région.

Pour chaque langage : marques de commentaire de ligne, commentaires de bloc (imbriqués ou non), délimiteurs de chaînes
(avec ou sans échappement, sur une ou plusieurs lignes), littéraux de caractère, et préfixes qui ressemblent à un
commentaire mais sont du code (directives OpenMP de Fortran `!$`, pragmas de GHC `{-#`, directives de FreePascal `{$`).
Une chaîne de documentation seule dans son instruction (Python, Mojo : chaîne triple en début de ligne ; Julia : chaîne
triple seule sur sa ligne avant une définition) compte comme commentaire.

`strip(lang, text)` rend les lignes du fichier, commentaires remplacés par des blancs, chaînes conservées (les
constructions recherchées peuvent être dans une chaîne : nom d'intrinsèque d'un `pragma Import` d'Ada) ; `blank_strings`
rend la même ligne, chaînes remplacées par des blancs (pour apparier les accolades) ; `tokens(lang, line)` découpe une
ligne déjà sans commentaires en lexèmes."""
import re

# lang -> règles. line : marques de commentaire de ligne ; block : (ouvrant, fermant, imbriqué) ; strings :
# (délimiteur, échappement '\\' ou None, plusieurs lignes) ; char : regex d'un littéral de caractère (ou None) ;
# keep : préfixes qui ne sont pas des commentaires ; doc : règle des chaînes de documentation.
C_STR = [('"', "\\", False)]
C_CHAR = r"'(?:\\.|[^'\\])'"
RULES = {
    "c": {"line": ["//"], "block": [("/*", "*/", False)], "strings": C_STR, "char": C_CHAR},
    "cpp": {"line": ["//"], "block": [("/*", "*/", False)], "strings": C_STR, "char": C_CHAR},
    "c3": {"line": ["//"], "block": [("/*", "*/", True)], "strings": C_STR + [("`", None, True)], "char": C_CHAR},
    "zig": {"line": ["//"], "block": [], "strings": C_STR, "char": C_CHAR},
    "odin": {"line": ["//"], "block": [("/*", "*/", True)], "strings": C_STR + [("`", None, True)], "char": C_CHAR},
    "rust": {"line": ["//"], "block": [("/*", "*/", True)], "strings": [('"', "\\", True)],
             "char": r"'(?:\\.|\\u\{[0-9a-fA-F]+\}|[^'\\])'"},
    "d": {"line": ["//"], "block": [("/*", "*/", False), ("/+", "+/", True)],
          "strings": [('"', "\\", True), ("`", None, True)], "char": C_CHAR},
    "swift": {"line": ["//"], "block": [("/*", "*/", True)], "strings": [('"""', "\\", True), ('"', "\\", False)],
              "char": None},
    "go": {"line": ["//"], "block": [("/*", "*/", False)], "strings": C_STR + [("`", None, True)], "char": C_CHAR,
           "keep": ["//go:"]},
    "csharp": {"line": ["//"], "block": [("/*", "*/", False)], "strings": [('"""', None, True), ('"', "\\", False)],
               "char": C_CHAR},
    "java": {"line": ["//"], "block": [("/*", "*/", False)], "strings": [('"""', "\\", True), ('"', "\\", False)],
             "char": C_CHAR},
    "js": {"line": ["//"], "block": [("/*", "*/", False)],
           "strings": [('"', "\\", False), ("'", "\\", False), ("`", "\\", True)], "char": None},
    "chapel": {"line": ["//"], "block": [("/*", "*/", True)], "strings": [('"', "\\", False), ("'", "\\", False)],
               "char": None},
    "php": {"line": ["//", "#"], "block": [("/*", "*/", False)], "strings": [('"', "\\", True), ("'", "\\", True)],
            "char": None, "keep": ["#["]},
    "mojo": {"line": ["#"], "block": [], "strings": [('"""', "\\", True), ('"', "\\", False), ("'", "\\", False)],
             "char": None, "doc": "py"},
    "python": {"line": ["#"], "block": [],
               "strings": [('"""', "\\", True), ("'''", "\\", True), ('"', "\\", False), ("'", "\\", False)],
               "char": None, "doc": "py"},
    "nim": {"line": ["#"], "block": [("#[", "]#", True), ("##[", "]##", True)],
            "strings": [('"""', None, True), ('"', "\\", False)], "char": C_CHAR},
    "julia": {"line": ["#"], "block": [("#=", "=#", True)], "strings": [('"""', "\\", True), ('"', "\\", False)],
              "char": r"'(?:\\.|[^'\\])'", "doc": "jl"},
    "lua": {"line": ["--"], "block": [("--[[", "]]", False), ("--[==[", "]==]", False)],
            "strings": [("[[", None, True), ('"', "\\", False), ("'", "\\", False)], "char": None},
    "haskell": {"line": ["--"], "block": [("{-", "-}", True)], "strings": [('"', "\\", False)],
                "char": r"(?<![\w'])'(?:\\.|[^'\\])'", "keep": ["{-#"]},
    "ocaml": {"line": [], "block": [("(*", "*)", True)], "strings": [('"', "\\", True)],
              "char": r"(?<![\w'])'(?:\\.|[^'\\])'"},
    "ada": {"line": ["--"], "block": [], "strings": [('"', None, False)], "char": r"(?<![\w)])'.'"},
    "fortran": {"line": ["!"], "block": [], "strings": [('"', None, False), ("'", None, False)], "char": None,
                "keep": ["!$"]},
    "fpc": {"line": ["//"], "block": [("{", "}", False), ("(*", "*)", False)], "strings": [("'", None, False)],
            "char": None, "keep": ["{$"]},
    "bqn": {"line": ["#"], "block": [], "strings": [('"', None, True)], "char": r"'.'"},
}
# Un « -- » de Haskell n'ouvre un commentaire que s'il n'est pas suivi d'un symbole (opérateur comme --> ou |--).
HS_SYM = set("!#$%&*+./<=>?@\\^|-~:")


def _starts(s, i, tok):
    return s.startswith(tok, i)


def strip(lang, text):
    """Lignes du texte, commentaires remplacés par des blancs (même longueur), chaînes conservées. Une chaîne triple
    qui ouvre une instruction (rien avant elle sur sa ligne, et la ligne de code précédente ne se termine pas par un
    signe qui appelle une suite) est une chaîne de documentation : elle est traitée comme un commentaire."""
    R = RULES[lang]
    out, i, n = [], 0, len(text)
    buf = []
    depth, block = 0, None          # commentaire de bloc en cours
    instr = None                    # chaîne en cours : (fermant, échappement, plusieurs lignes)
    doc = None                      # chaîne de documentation en cours : son fermant
    keep = R.get("keep", [])
    char_re = re.compile(R["char"]) if R.get("char") else None
    prev_last = ""                  # dernier caractère de la dernière ligne de code
    while i < n:
        c = text[i]
        if c == "\n":
            line = "".join(buf)
            out.append(line)
            if line.strip():
                prev_last = line.rstrip()[-1]
            buf = []
            i += 1
            if instr and not instr[2]:
                instr = None        # chaîne d'une ligne non fermée : on s'arrête à la fin de la ligne
            continue
        if doc is not None:
            if _starts(text, i, doc):
                buf.append(" " * len(doc))
                i += len(doc)
                doc = None
                continue
            buf.append(" ")
            i += 1
            continue
        if block is not None:
            op, cl, nested = block
            if nested and _starts(text, i, op):
                depth += 1
                buf.append(" " * len(op))
                i += len(op)
                continue
            if _starts(text, i, cl):
                depth -= 1
                buf.append(" " * len(cl))
                i += len(cl)
                if depth == 0:
                    block = None
                continue
            buf.append(" ")
            i += 1
            continue
        if instr is not None:
            cl, esc, _ = instr
            if esc and c == esc and i + 1 < n and text[i + 1] != "\n":
                buf.append(text[i:i + 2])
                i += 2
                continue
            if _starts(text, i, cl):
                buf.append(cl)
                i += len(cl)
                instr = None
                continue
            buf.append(c)
            i += 1
            continue
        # code
        if any(_starts(text, i, k) for k in keep):
            k = next(k for k in keep if _starts(text, i, k))
            buf.append(k)
            i += len(k)
            continue
        opened = False
        for op, cl, nested in sorted(R["block"], key=lambda x: -len(x[0])):
            if _starts(text, i, op):
                block, depth = (op, cl, nested), 1
                buf.append(" " * len(op))
                i += len(op)
                opened = True
                break
        if opened:
            continue
        lc = next((m for m in R["line"] if _starts(text, i, m)), None)
        if lc is not None and lang == "haskell" and i + 2 < n and text[i + 2] in HS_SYM - {"-"}:
            lc = None
        if lc is not None and lang == "haskell":
            j = i
            while j > 0 and text[j - 1] in HS_SYM:
                j -= 1
            if j < i:
                lc = None       # « -- » au milieu d'un opérateur
        if lc is not None:
            j = text.find("\n", i)
            j = n if j < 0 else j
            buf.append(" " * (j - i))
            i = j
            continue
        if char_re is not None:
            m = char_re.match(text, i)
            if m:
                buf.append(m.group(0))
                i = m.end()
                continue
        if R.get("doc"):
            q = next((d for d in ('"""', "'''") if _starts(text, i, d)), None)
            if q and not "".join(buf).strip() and (prev_last == "" or prev_last not in "=([{,+\\") and \
                    not (lang == "julia" and q == "'''"):
                doc = q
                buf.append(" " * len(q))
                i += len(q)
                continue
        for d, esc, multi in sorted(R["strings"], key=lambda x: -len(x[0])):
            if _starts(text, i, d):
                cl = "]]" if d == "[[" else d
                instr = (cl, esc, multi)
                buf.append(d)
                i += len(d)
                break
        else:
            buf.append(c)
            i += 1
    out.append("".join(buf))
    return out


def is_code(line):
    return bool(line.strip())


def blank_strings(lang, line):
    """La ligne (déjà sans commentaires), contenu des chaînes et des caractères remplacé par des blancs."""
    R = RULES[lang]
    out, i, n = [], 0, len(line)
    char_re = re.compile(R["char"]) if R.get("char") else None
    while i < n:
        if char_re is not None:
            m = char_re.match(line, i)
            if m:
                out.append(" " * len(m.group(0)))
                i = m.end()
                continue
        for d, esc, _ in sorted(R["strings"], key=lambda x: -len(x[0])):
            if line.startswith(d, i):
                cl = "]]" if d == "[[" else d
                j = i + len(d)
                while j < n and not line.startswith(cl, j):
                    j += 2 if esc and line[j] == esc else 1
                j = min(n, j + len(cl))
                out.append(" " * (j - i))
                i = j
                break
        else:
            out.append(line[i])
            i += 1
    return "".join(out)


NUM = r"\d[\w.]*(?:[eEpP][+-]\d+)?"
IDENT = r"[^\W\d]\w*['!?]*"
BRACKETS = "()[]{}"


def tokens(lang, line):
    """Lexèmes d'une ligne sans commentaires : chaînes et caractères (un lexème chacun), nombres, identifiants,
    crochets (un lexème chacun), suites d'autres signes ASCII (un lexème), et chaque autre caractère (glyphes de BQN)."""
    R = RULES[lang]
    toks, i, n = [], 0, len(line)
    char_re = re.compile(R["char"]) if R.get("char") else None
    num_re, id_re = re.compile(NUM), re.compile(IDENT)
    while i < n:
        c = line[i]
        if c.isspace():
            i += 1
            continue
        if char_re is not None:
            m = char_re.match(line, i)
            if m:
                toks.append(m.group(0))
                i = m.end()
                continue
        hit = False
        for d, esc, _ in sorted(R["strings"], key=lambda x: -len(x[0])):
            if line.startswith(d, i):
                cl = "]]" if d == "[[" else d
                j = i + len(d)
                while j < n and not line.startswith(cl, j):
                    j += 2 if esc and line[j] == esc else 1
                j = min(n, j + len(cl))
                toks.append(line[i:j])
                i, hit = j, True
                break
        if hit:
            continue
        m = num_re.match(line, i)
        if m:
            toks.append(m.group(0))
            i = m.end()
            continue
        m = id_re.match(line, i)
        if m and (c.isalpha() or c == "_"):
            toks.append(m.group(0))
            i = m.end()
            continue
        if c in BRACKETS or ord(c) > 127:
            toks.append(c)
            i += 1
            continue
        j = i
        while j < n and not line[j].isspace() and not line[j].isalnum() and line[j] not in BRACKETS \
                and line[j] != "_" and ord(line[j]) < 128 and not any(line.startswith(d, j) for d, _, _ in R["strings"]):
            j += 1
        if j == i:
            j = i + 1
        toks.append(line[i:j])
        i = j
    return toks
