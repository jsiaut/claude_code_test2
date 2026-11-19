#!/bin/sh
# Audit de la grille, JavaScript (Node 26.12.1, V8 ; réglages du banc : --expose-gc --max-old-space-size=8192) :
# programme exécuté (audit.js), code machine de TurboFan (--print-opt-code), forme refusée, et recherches d'absence
# dans l'API de la construction (objet global et modules intégrés : tools/grid_audit/listings/node_api.js).
cd "$(dirname "$0")" && mkdir -p bin
N=/opt/node26/bin/node
$N --expose-gc --max-old-space-size=8192 audit.js > bin/audit.out 2> bin/audit.err
printf 'function hot(a){let s=0;for(let i=0;i<a.length;i++)s+=a[i];return s}\nconst a=new Float64Array(1000).fill(1);let t=0;for(let r=0;r<20000;r++)t+=hot(a);console.log(t)\n' > bin/hot.js
$N --print-opt-code --code-comments bin/hot.js > bin/optcode.txt 2>&1
printf 'asm("pause");\n' > bin/e2.js
$N bin/e2.js > bin/e2.txt 2>&1
(cd ../../.. && python3 tools/grid_audit/search.py js A2 A3 A6 A7 B2 B3 C1 C2 C4 C5 D2 D3 D4 E2 E3 E4 E5 E7 F2 F4) > bin/search.out
CNT=$(cd ../../.. && $N tools/grid_audit/listings/node_api.js 2>/dev/null | wc -l)
python3 - "$CNT" <<'PY'
import re, sys
n = sys.argv[1]
rd = lambda f: open("bin/" + f).read()
out = rd("audit.out").splitlines()
fact = {l.split(";")[1]: l.split(";", 2)[2] for l in out if l.startswith("FACT;")}
notes = [l for l in out if l.startswith("NOTE;")]
srch = {l.split(";")[1]: l.split(";") for l in rd("search.out").splitlines() if l.startswith("SEARCH;")}
oc = rd("optcode.txt")
blocks = oc.count("--- Optimized code ---")
hot = re.search(r"name = hot.*?--- End code ---", oc, re.S)
hotlines = len([l for l in hot.group(0).splitlines() if re.match(r"^0x[0-9a-f]+\s", l)]) if hot else 0
e2 = re.search(r"ReferenceError: [^\n]*", rd("e2.txt"))
warn = "ExperimentalWarning: FFI is an experimental feature" in rd("audit.out") + rd("audit.err")
def rech(c, exam=""):
    s = srch[c]; pl = "s" if int(s[2]) > 1 else ""
    return f"[recherche] motif {c} dans l'API de Node 26.12.1 (objet global, modules intégrés et leurs classes, {n} noms ; introspection) : {s[2]} nom{pl}{exam} ({s[5]})"
exp = " ; node:ffi expérimental (« ExperimentalWarning: FFI is an experimental feature »)" if warn else ""
L = {}
L["A1"] = ("0", f"[échec] {fact['A1']}")
L["A2"] = ("0", rech("A2") + " ; aucun contrôle de la disposition des objets")
L["A3"] = ("0", rech("A3", " : http2.getPackedSettings et getUnpackedSettings (réglages HTTP/2), faux positifs") + " ; ni compactage ni champ de bits")
L["A4"] = ("0.5", f"[exécutée] {fact['A4']}{exp}")
L["A5"] = ("0.5", f"[exécutée] {fact['A5']}")
L["A6"] = ("0", rech("A6") + " ; aucun conteneur SoA")
L["A7"] = ("0", f"[échec] {fact['A7']} ; " + rech("A7"))
L["A8"] = ("0.5", f"[exécutée] {fact['A8']}")
L["B1"] = ("0", f"[échec] {fact['B1']}")
L["B2"] = ("0", rech("B2", " : Intl.Locale.prototype.region et StatementSync.setAllowBareNamedParameters (« arena » dans « BareNamed »), faux positifs") + " ; ni arène ni allocateur à choisir")
L["B3"] = ("0", f"[échec] {fact['B3']} ; " + rech("B3"))
L["B4"] = ("0", f"[échec] {fact['B4']}")
L["B5"] = ("0.5", f"[exécutée] {fact['B5']}")
L["C1"] = ("0", f"[échec] {fact['C1']} ; " + rech("C1", " : process.versions.simdjson et simdutf, variables de configuration de la construction (bibliothèques internes de Node), faux positifs"))
L["C2"] = ("0", rech("C2") + " ; aucune intrinsèque")
L["C4"] = ("0", f"[échec] {fact['C4']} ; " + rech("C4"))
L["C5"] = ("0", rech("C5", " : os.availableParallelism (nombre de processeurs), faux positif") + " ; ni boucle parallèle ni réserve de tâches (Worker à écrire soi-même, D1)")
L["D1"] = ("0.5", f"[exécutée] {fact['D1']}")
L["D2"] = ("0.5", f"[exécutée] {fact['D2']} ; " + rech("D2", " : releaseLock (flux), os.release, process.release, kLenientHeaderValueRelaxed, releaseBuffer, faux positifs : aucun ordre relâché, acquire ou release"))
L["D3"] = ("0", rech("D3") + " ; aucune aide de ligne de cache")
L["D4"] = ("0", rech("D4") + " ; aucune affinité dans l'API")
L["D5"] = ("0.5", f"[exécutée] {fact['D5']}")
L["E1"] = ("1", f"[exécutée] node --print-opt-code : {blocks} fonctions optimisées par TurboFan listées, {hotlines} instructions pour hot() (binaire officiel)")
L["E2"] = ("0", f"[échec] asm(\"pause\") : {e2.group(0) if e2 else '?'} ; " + rech("E2"))
L["E3"] = ("0", rech("E3") + " ; aucune indication de branchement")
L["E4"] = ("0", rech("E4") + " ; aucun préchargement")
L["E5"] = ("0", rech("E5") + " ; ni restrict ni règle de non-aliasing")
L["E6"] = ("0.5", f"[exécutée] {fact['E6']}")
L["E7"] = ("0", rech("E7") + " ; ni génériques monomorphisés ni calcul à la compilation")
L["F1"] = ("0", f"[échec] {fact['F1']}")
L["F2"] = ("0", rech("F2", " : Intl.Locale et ses membres (langue et région), faux positifs") + " ; aucune construction de localité ni de distribution")
L["F3"] = ("0.5", f"[exécutée] {fact['F3']}")
L["F4"] = ("0", rech("F4") + " ; pas de projection de fichier dans l'API (mmap seulement par node:ffi vers la libc, NOTE)")
order = ["A1","A2","A3","A4","A5","A6","A7","A8","B1","B2","B3","B4","B5","C1","C2","C4","C5","D1","D2","D3","D4","D5","E1","E2","E3","E4","E5","E6","E7","F1","F2","F3","F4"]
for c in order: print(f"CAP;{c};{L[c][0]};{L[c][1]}")
for l in notes:
    if not l.startswith("NOTE;FFI"): print(l)
PY
