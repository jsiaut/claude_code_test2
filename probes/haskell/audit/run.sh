#!/bin/sh
# Audit de la grille, Haskell (GHC 9.14.1, réglages du banc : -O2 -fllvm -mavx512f -mfma -mbmi2 -fno-full-laziness
# -threaded) : programme exécuté (Audit.hs, Layout.hsc passé par hsc2hs, Comptime.hs pour Template Haskell) avec
# +RTS -N4 -qa -T -s, code machine lu dans l'assembleur gardé (-keep-s-files), formes refusées, option --numa du RTS,
# et recherches d'absence dans l'API des bibliothèques livrées (tools/grid_audit/listings/haskell_api.sh).
cd "$(dirname "$0")" && mkdir -p bin/s bin/fail
G=/opt/ghc/bin
FL="-O2 -fllvm -mavx512f -mfma -mbmi2 -fno-full-laziness -threaded -rtsopts"
$G/hsc2hs Layout.hsc -o bin/Layout.hs && rm -f Layout_hsc.c Layout_hsc.h
$G/ghc $FL -keep-s-files -outputdir bin -o bin/audit Audit.hs bin/Layout.hs Comptime.hs > bin/build.log 2>&1
mv -f Audit.s Comptime.s bin/s/ 2>/dev/null; mv -f bin/Layout.s bin/s/ 2>/dev/null
bin/audit +RTS -N4 -qa -T -s -RTS > bin/audit.out 2> bin/rts.txt
$G/ghc -O2 -S -outputdir bin/fail -o bin/fail/Comptime.s Comptime.hs > /dev/null 2>&1
printf 'main :: IO ()\nmain = print 1\n' > bin/fail/N.hs
$G/ghc -threaded -rtsopts -outputdir bin/fail -o bin/fail/n bin/fail/N.hs > /dev/null 2>&1
bin/fail/n +RTS --numa -RTS > bin/fail/numa.txt 2>&1
w() { printf '%s\n' "$2" > bin/fail/$1.hs; $G/ghc -fno-code bin/fail/$1.hs 2>&1 | grep -A2 -m1 'error' | tail -n +2 | head -1 | sed -E 's/^ *//; s/[•*] //' > bin/fail/$1.err; }
w E2 'main :: IO ()
main = asm "pause"'
w C5 'import Control.Parallel.Strategies
main :: IO ()
main = return ()'
(cd ../../.. && python3 tools/grid_audit/search.py haskell A3 A6 C2 C4 D2 D3 D5 E2 E3 E5 F2 F4) > bin/search.out
N=$(cd ../../.. && sh tools/grid_audit/listings/haskell_api.sh | wc -l)
python3 - "$N" <<'PY'
import re, sys
n = sys.argv[1]
rd = lambda f: open("bin/" + f).read()
out = rd("audit.out").splitlines()
fact = {l.split(";")[1]: l.split(";", 2)[2] for l in out if l.startswith("FACT;")}
notes = [l for l in out if l.startswith("NOTE;")]
srch = {l.split(";")[1]: l.split(";") for l in rd("search.out").splitlines() if l.startswith("SEARCH;")}
err = {k: rd(f"fail/{k}.err").strip() for k in ("E2", "C5")}
asm = rd("s/Audit.s")
def body(name):
    m = re.search(r"^" + re.escape(name) + r"\$def:.*?(?=^Main_\w+\$def:)", asm, re.S | re.M)   # avec ses continuations locales
    return m.group(0) if m else ""
vec = sum(len(re.findall(r"vfmadd\w+ps\s.*zmm", body(f))) for f in ("Main_zdwcgVec_info", "Main_cgVec1_info", "Main_cgVec_info"))
pre = body("Main_zdwcgPrefetch_info")
sp = re.search(r"SPARKS: (\d+) \((\d+) converted", rd("rts.txt"))
numa = rd("fail/numa.txt").strip().splitlines()[0] if rd("fail/numa.txt").strip() else "?"
ncg = len(rd("fail/Comptime.s").splitlines()) if __import__("os").path.exists("bin/fail/Comptime.s") else 0
def rech(c, exam=""):
    s = srch[c]; pl = "s" if int(s[2]) > 1 else ""
    return (f"[recherche] motif {c} dans l'API des bibliothèques livrées avec GHC 9.14.1 (« :browse » de GHCi sur 833 modules "
            f"exposés de base, ghc-prim, ghc-internal, ghc-experimental, array, containers, bytestring, text, stm, unix…, {n} lignes) : "
            f"{s[2]} ligne{pl}{exam} ({s[5]})")
L = {}
L["A1"] = ("0.5", f"[exécutée] {fact['A1']}")
L["A2"] = ("0.5", f"[exécutée] {fact['A2']}")
L["A3"] = ("0.5", f"[exécutée] {fact['A3']} : le mécanisme que la matrice compte pour A2 (Storable, ½) donne aussi la disposition compactée, sans champ de bits")
L["A4"] = ("0.5", f"[exécutée] {fact['A4']}")
L["A5"] = ("0.5", f"[exécutée] {fact['A5']}")
L["A6"] = ("0", rech("A6") + " ; aucun conteneur SoA")
L["A7"] = ("0.5", f"[exécutée] {fact['A7']}")
L["A8"] = ("1", f"[exécutée] {fact['A8']}")
L["B1"] = ("0", f"[échec] {fact['B1']}")
L["B2"] = ("0.5", f"[exécutée] {fact['B2']}")
L["B3"] = ("0.5", f"[exécutée] {fact['B3']}")
L["B4"] = ("0", f"[échec] {fact['B4']}")
L["B5"] = ("1", f"[exécutée] {fact['B5']}")
L["C1"] = ("0.5", f"[exécutée] {fact['C1']} ; code machine (LLVM) : {vec} vfmadd…ps sur zmm dans cgVec")
L["C2"] = ("0", rech("C2") + " ; aucune intrinsèque propre à x86 (primops portables seulement)")
L["C4"] = ("0", f"[échec] {fact['C4']} ; " + rech("C4", " : LeftAssociative, RightAssociative, NotAssociative (associativité des opérateurs, Template Haskell et GHC.Generics), faux positifs"))
L["C5"] = ("0.5", f"[exécutée] {fact['C5'].split(' ; ')[0]} : {sp.group(1) if sp else '?'} étincelles, {sp.group(2) if sp else '?'} converties en calculs parallèles (+RTS -N4 -s) ; [échec] Control.Parallel.Strategies (paquet parallel, non livré) : {err['C5']}")
L["D1"] = ("1", f"[exécutée] {fact['D1']}")
L["D2"] = ("0.5", f"[exécutée] {fact['D2']} ; " + rech("D2", " : mapKeysMonotonic, getMonotonicTime, RelaxedPolyRec et RelaxedLayout (extensions), acquireSem et releaseSem (semaphore-compat), release (descripteurs, uname), faux positifs : aucun ordre relâché, acquire ou release"))
L["D3"] = ("0", rech("D3") + " ; aucune aide de ligne de cache")
L["D4"] = ("0.5", f"[exécutée] {fact['D4']}")
L["D5"] = ("0", rech("D5") + " ; ni pause ni barrière (yield rend la main à l'ordonnanceur de GHC)")
L["E1"] = ("1", f"[exécutée] ghc -S (générateur natif) : {ncg} lignes pour Comptime.hs ; -keep-s-files (LLVM) : {len(asm.splitlines())} lignes pour Audit.hs")
L["E2"] = ("0", f"[échec] asm \"pause\" : {err['E2']} ; " + rech("E2"))
L["E3"] = ("0", rech("E3", " : Text.Read.Lex.expect (analyse lexicale), faux positif") + " ; aucune indication de branchement")
L["E4"] = ("1", f"[exécutée] {fact['E4']} : {len(re.findall(r'prefetcht0', pre))} prefetcht0 et {len(re.findall(r'prefetchnta', pre))} prefetchnta dans le code machine (LLVM)")
L["E5"] = ("0", rech("E5", " : restrictKeys (containers), SetOwnerAndGroupIsRestricted (unix), MonomorphismRestriction (extension), faux positifs") + " ; ni restrict ni règle de non-aliasing")
L["E6"] = ("1", f"[exécutée] {fact['E6']}")
L["E7"] = ("0.5", f"[exécutée] {fact['E7']}")
L["F1"] = ("1", f"[exécutée] {fact['F1']}")
L["F2"] = ("0", f"[échec] +RTS --numa : « {numa} » ; " + rech("F2", " : numa et numaMask (champs de GHC.RTS.Flags, option --numa du RTS, absente de cette construction), TimeLocale, unsafeInterleaveIO/ST, faux positifs") + " ; aucune construction de localité dans le langage")
L["F3"] = ("1", f"[exécutée] {fact['F3']}")
L["F4"] = ("0", rech("F4", " : primMap* (constructeurs de bytestring), faux positifs") + " ; pas de projection de fichier dans les bibliothèques livrées (ni base ni unix)")
order = ["A1","A2","A3","A4","A5","A6","A7","A8","B1","B2","B3","B4","B5","C1","C2","C4","C5","D1","D2","D3","D4","D5","E1","E2","E3","E4","E5","E6","E7","F1","F2","F3","F4"]
for c in order: print(f"CAP;{c};{L[c][0]};{L[c][1]}")
for l in notes: print(l)
PY
