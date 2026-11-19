#!/bin/sh
# Audit de la grille, Python 3.15.2 (CPython, construction par défaut avec GIL) : programme exécuté (audit.py), forme
# refusée, et recherches d'absence dans la bibliothèque standard livrée (sources .py de /usr/lib/python3.15, sans les
# tests, et noms publics des modules écrits en C : tools/grid_audit/listings/python_cmods.py).
cd "$(dirname "$0")" && mkdir -p bin
python3.15 audit.py > bin/audit.out 2> bin/audit.err
printf 'asm("pause")\n' > bin/e2.py
python3.15 bin/e2.py > bin/e2.txt 2>&1
(cd ../../.. && python3 tools/grid_audit/search.py python A6 B2 B3 C1 C2 C4 D2 D3 D5 E2 E3 E4 E5 E7 F2) > bin/search.out
python3 - <<'PY'
import re
rd = lambda f: open("bin/" + f).read()
out = rd("audit.out").splitlines()
fact = {l.split(";")[1]: l.split(";", 2)[2] for l in out if l.startswith("FACT;")}
srch = {l.split(";")[1]: l.split(";") for l in rd("search.out").splitlines() if l.startswith("SEARCH;")}
e2 = re.search(r"NameError: [^\n]*", rd("e2.txt"))
def rech(c, exam=""):
    s = srch[c]; pl = "s" if int(s[2]) > 1 else ""
    return f"[recherche] motif {c} dans la bibliothèque standard de Python 3.15.2 (sources .py livrées et modules en C, introspection) : {s[2]} déclaration{pl}{exam} ({s[5]})"
L = {}
L["A1"] = ("0.5", f"[exécutée] {fact['A1']}")
L["A2"] = ("0.5", f"[exécutée] {fact['A2']}")
L["A3"] = ("0.5", f"[exécutée] {fact['A3']}")
L["A4"] = ("0.5", f"[exécutée] {fact['A4']}")
L["A5"] = ("0.5", f"[exécutée] {fact['A5']}")
L["A6"] = ("0", rech("A6") + " ; aucun conteneur SoA (NumPy est tiers)")
L["A7"] = ("0.5", f"[exécutée] {fact['A7']}")
L["A8"] = ("0.5", f"[exécutée] {fact['A8']}")
L["B1"] = ("1", f"[exécutée] {fact['B1']}")
L["B2"] = ("0", rech("B2") + " ; aucun allocateur à choisir ni arène (PyMem_SetAllocator n'existe que dans l'API C)")
L["B3"] = ("0", f"[échec] {fact['B3']} ; " + rech("B3"))
L["B4"] = ("0", f"[échec] {fact['B4']}")
L["B5"] = ("0.5", f"[exécutée] {fact['B5']}")
L["C1"] = ("0", rech("C1") + " ; aucun type vectoriel")
L["C2"] = ("0", rech("C2", " : CALL_INTRINSIC_1 et _2 (opcodes du bytecode, dis et _opcode), TUPLE2 de pickle (b'\\x86'), faux positifs") + " ; aucune intrinsèque")
L["C4"] = ("0", f"[échec] {fact['C4']} ; " + rech("C4"))
L["C5"] = ("0.5", f"[exécutée] {fact['C5']}")
L["D1"] = ("0.5", f"[exécutée] {fact['D1']}")
L["D2"] = ("0", rech("D2", " : acquire et release des verrous (threading, _thread, multiprocessing), horloges monotonic, uname().release, faux positifs") + " ; aucun atomique")
L["D3"] = ("0", rech("D3") + " ; aucune aide de ligne de cache")
L["D4"] = ("1", f"[exécutée] {fact['D4']} ; ½ en v1")
L["D5"] = ("0", rech("D5", " : signal.pause (attente d'un signal), faux positif") + " ; ni pause ni barrière")
L["E1"] = ("0", f"[échec] {fact['E1']}")
L["E2"] = ("0", f"[échec] asm(\"pause\") : {e2.group(0) if e2 else '?'} ; " + rech("E2"))
L["E3"] = ("0", rech("E3", " : importlib.metadata.FastPath (chemins de recherche), faux positif") + " ; aucune indication de branchement")
L["E4"] = ("0", rech("E4") + " ; aucun préchargement")
L["E5"] = ("0", rech("E5", " : stat.SF_RESTRICTED et zipfile restrict_rglob, faux positifs") + " ; ni restrict ni règle de non-aliasing")
L["E6"] = ("0.5", f"[exécutée] {fact['E6']}")
L["E7"] = ("0", rech("E7", " : _opcode.ENABLE_SPECIALIZATION et get_specialization_stats (spécialisation du bytecode par l'interpréteur), faux positifs") + " ; ni génériques monomorphisés ni calcul à la compilation")
L["F1"] = ("0.5", f"[exécutée] {fact['F1']}")
L["F2"] = ("0", rech("F2", " : locale.setlocale, setLocale (SAX), SRE_FLAG_LOCALE, interleave (_ast_unparse), faux positifs") + " ; aucune construction de localité ni de distribution")
L["F3"] = ("0.5", f"[exécutée] {fact['F3']}")
L["F4"] = ("1", f"[exécutée] {fact['F4']}")
order = ["A1","A2","A3","A4","A5","A6","A7","A8","B1","B2","B3","B4","B5","C1","C2","C4","C5","D1","D2","D3","D4","D5","E1","E2","E3","E4","E5","E6","E7","F1","F2","F3","F4"]
for c in order: print(f"CAP;{c};{L[c][0]};{L[c][1]}")
PY
