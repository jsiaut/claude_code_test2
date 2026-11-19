#!/bin/sh
# Audit de la grille, Lua 5.5.1 (interpréteur de référence du banc) : programme exécuté (audit.lua), bytecode listé
# par luac -l, forme refusée, et recherches d'absence dans la bibliothèque standard (noms de _G et des tables de
# bibliothèque : tools/grid_audit/listings/lua_api.lua).
cd "$(dirname "$0")" && mkdir -p bin
L=/opt/lua55/bin
$L/lua audit.lua > bin/audit.out 2> bin/audit.err
$L/luac -l -p audit.lua > bin/luac.txt 2>&1
printf 'asm("pause")\n' > bin/e2.lua
$L/lua bin/e2.lua > bin/e2.txt 2>&1
(cd ../../.. && python3 tools/grid_audit/search.py lua A2 A3 A4 A6 A7 B2 B5 C1 C2 C4 C5 D1 D2 D3 D4 D5 E1 E2 E3 E4 E5 E6 E7 F1 F2 F4) > bin/search.out
N=$($L/lua ../../../tools/grid_audit/listings/lua_api.lua | wc -l)
python3 - "$N" <<'PY'
import re, sys
n = sys.argv[1]
rd = lambda f: open("bin/" + f).read()
out = rd("audit.out").splitlines()
fact = {l.split(";")[1]: l.split(";", 2)[2] for l in out if l.startswith("FACT;")}
notes = [l for l in out if l.startswith("NOTE;")]
srch = {l.split(";")[1]: l.split(";") for l in rd("search.out").splitlines() if l.startswith("SEARCH;")}
lc = rd("luac.txt")
ops = len(re.findall(r"^\s+\d+\s+\[\d+\]\s+[A-Z]+", lc, re.M))
e2 = re.search(r"attempt to call a nil value[^\n]*", rd("e2.txt"))
def rech(c, exam=""):
    s = srch[c]; pl = "s" if int(s[2]) > 1 else ""
    return f"[recherche] motif {c} dans la bibliothèque standard de Lua 5.5.1 ({n} noms de _G, des tables de bibliothèque et des méthodes ; introspection) : {s[2]} nom{pl} ({s[5]})"
L = {}
L["A1"] = ("0", f"[échec] {fact['A1']}")
L["A2"] = ("0", rech("A2") + " ; aucun contrôle de la disposition")
L["A3"] = ("0", rech("A3") + " ; ni compactage ni champ de bits hors des chaînes immuables de string.pack (NOTE)")
L["A4"] = ("0", rech("A4") + " ; aucun contrôle de l'alignement")
L["A5"] = ("0.5", f"[exécutée] {fact['A5']}")
L["A6"] = ("0", rech("A6") + " ; aucun conteneur SoA")
L["A7"] = ("0", f"[échec] {fact['A7']} ; " + rech("A7"))
L["A8"] = ("0", f"[échec] {fact['A8']}")
L["B1"] = ("0", f"[échec] {fact['B1']}")
L["B2"] = ("0", rech("B2") + " ; aucun allocateur à choisir (lua_Alloc n'existe que dans l'API C)")
L["B3"] = ("0.5", f"[exécutée] {fact['B3']} ; tables toujours sur le tas")
L["B4"] = ("0.5", f"[exécutée] {fact['B4']}")
L["B5"] = ("0", rech("B5") + " ; ni pointeur ni accès mémoire brut")
L["C1"] = ("0", rech("C1") + " ; aucun type vectoriel")
L["C2"] = ("0", rech("C2") + " ; aucune intrinsèque")
L["C4"] = ("0", f"[échec] {fact['C4']} ; " + rech("C4"))
L["C5"] = ("0", rech("C5") + " ; aucune construction parallèle")
L["D1"] = ("0", f"[échec] {fact['D1']} ; " + rech("D1"))
L["D2"] = ("0", rech("D2") + " ; aucun atomique")
L["D3"] = ("0", rech("D3") + " ; aucune aide de ligne de cache")
L["D4"] = ("0", rech("D4") + " ; aucune affinité")
L["D5"] = ("0", rech("D5") + " ; ni pause ni barrière")
L["E1"] = ("0", f"[échec] interpréteur : luac -l ne liste que le bytecode ({ops} instructions de la machine virtuelle pour audit.lua), aucun code machine ; " + rech("E1"))
L["E2"] = ("0", f"[échec] asm(\"pause\") : {e2.group(0) if e2 else '?'} ; " + rech("E2"))
L["E3"] = ("0", rech("E3") + " ; aucune indication de branchement")
L["E4"] = ("0", rech("E4") + " ; aucun préchargement")
L["E5"] = ("0", rech("E5") + " ; ni restrict ni règle de non-aliasing")
L["E6"] = ("0", f"[échec] {fact['E6']} ; " + rech("E6"))
L["E7"] = ("0", rech("E7") + " ; ni génériques ni calcul à la compilation")
L["F1"] = ("0", f"[échec] {fact['F1']} ; " + rech("F1"))
L["F2"] = ("0", rech("F2") + " ; aucune construction de localité ni de distribution")
L["F3"] = ("0.5", f"[exécutée] {fact['F3']}")
L["F4"] = ("0", rech("F4") + " ; pas de projection de fichier (io lit par copie)")
order = ["A1","A2","A3","A4","A5","A6","A7","A8","B1","B2","B3","B4","B5","C1","C2","C4","C5","D1","D2","D3","D4","D5","E1","E2","E3","E4","E5","E6","E7","F1","F2","F3","F4"]
for c in order: print(f"CAP;{c};{L[c][0]};{L[c][1]}")
for l in notes: print(l)
PY
