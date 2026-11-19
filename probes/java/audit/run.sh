#!/bin/sh
# Audit de la grille, Java (OpenJDK 27.0.1, réglages du banc : C2, G1, --add-modules jdk.incubator.vector) : programme
# exécuté (Audit.java), contre-épreuves (Epsilon, @Contended, hsdis), formes refusées par javac, et recherches d'absence
# dans l'API exportée des modules système (tools/grid_audit/listings/JavaApi.java). Sortie : lignes CAP et NOTE.
cd "$(dirname "$0")" && mkdir -p bin && unset JAVA_TOOL_OPTIONS
J=/opt/jdk27/bin
JV="$J/java -Dstdout.encoding=UTF-8 --add-modules jdk.incubator.vector"
$J/javac --release 27 --add-modules jdk.incubator.vector -d bin Audit.java > bin/javac.log 2>&1
$JV -XX:CompileCommand=quiet -XX:CompileCommand=dontinline,Audit::makeNI -cp bin Audit > bin/audit.out 2> bin/audit.err
# B1 : Epsilon, 200 Mio puis 300 Mio dans un tas de 256 Mio
EPS="$JV -XX:+UnlockExperimentalVMOptions -XX:+UseEpsilonGC -Xmx256m -cp bin Audit eps"
$EPS 200 > bin/eps1.out 2>&1; $EPS 300 > bin/eps2.out 2>&1; echo "rc=$?" >> bin/eps2.out
$J/java -XX:+UseEpsilonGC -version > bin/eps0.out 2>&1
# D3 : @Contended, avec et sans -XX:-RestrictContended
$J/javac --add-exports java.base/jdk.internal.vm.annotation=ALL-UNNAMED -d bin Contended.java > bin/cont.log 2>&1
$J/java -XX:-RestrictContended -cp bin Contended > bin/cont1.out 2>/dev/null
$J/java -cp bin Contended > bin/cont2.out 2>/dev/null
# E1 : -XX:+PrintAssembly sans hsdis, -XX:+PrintCompilation
$JV -XX:+UnlockDiagnosticVMOptions -XX:+PrintAssembly -XX:CompileCommand=quiet -XX:CompileCommand=compileonly,Audit::make -Xcomp -cp bin Audit eps 1 > bin/pa.out 2>&1
$JV -XX:+PrintCompilation -cp bin Audit eps 1 > bin/pc.out 2>&1
# F2 : -XX:+UseNUMA sur cet hôte
$J/java -XX:+UseNUMA -XX:+PrintFlagsFinal -version 2>/dev/null | grep -E ' UseNUMA ' > bin/numa.out
# formes refusées
printf 'class E2 { void f() { asm("pause"); } }\n' > bin/E2.java
printf 'class A3 { int x : 3; }\n' > bin/A3.java
printf 'value class A1 { int x; }\n' > bin/A1.java
printf 'import java.util.*;\nclass E7a { List<int> l; }\n' > bin/E7a.java
printf 'class E7b { static int f(int n) { return n; } static final int N = f(10);\n int g(int k) { switch (k) { case N: return 1; } return 0; } }\n' > bin/E7b.java
for f in E2 A3 A1 E7a E7b; do $J/javac -d bin/fail bin/$f.java 2>&1 | grep -m1 'error:' | sed 's/^.*error: /error: /' > bin/$f.err; done
(cd ../../.. && python3 tools/grid_audit/search.py java A6 B2 B3 C2 C4 D3 D4 E2 E3 E4 E5 E7 F2) > bin/search.out
N=$(cd ../../.. && sh -c "$(python3 -c "import json;print(json.load(open('tools/grid_audit/patterns.json'))['langs']['java']['listing'])")" | wc -l)
python3 - "$N" <<'PY'
import re, sys
n = sys.argv[1]
rd = lambda f: open("bin/" + f).read()
out = rd("audit.out").splitlines()
fact = {l.split(";")[1]: l.split(";", 2)[2] for l in out if l.startswith("FACT;")}
notes = [l for l in out if l.startswith("NOTE;")]
srch = {l.split(";")[1]: l.split(";") for l in rd("search.out").splitlines() if l.startswith("SEARCH;")}
err = {k: rd(k + ".err").strip() for k in ("E2", "A3", "A1", "E7a", "E7b")}
inc = "WARNING: Using incubator modules: jdk.incubator.vector" in rd("audit.err")
def rech(c, exam=""):
    s = srch[c]; pl = "s" if int(s[2]) > 1 else ""
    return (f"[recherche] motif {c} dans l'API exportée d'OpenJDK 27.0.1 (paquets exportés des modules système, "
            f"{n} noms : classes et membres publics ou protégés) : {s[2]} nom{pl}{exam} ({s[5]})")
e1 = rd("eps1.out").strip().split(";"); e2 = rd("eps2.out")
oom = "Terminating due to java.lang.OutOfMemoryError" in e2 or "OutOfMemoryError" in e2
eps0 = re.search(r"Error: (VM option 'UseEpsilonGC' is experimental[^\n]*)", rd("eps0.out"))
c1, c2 = rd("cont1.out").strip(), rd("cont2.out").strip()
pa = rd("pa.out"); hs = re.search(r"Loading hsdis library failed, undisassembled code is shown in MachCode section", pa)
pc = len([l for l in rd("pc.out").splitlines() if re.match(r"^\s*\d+\s+\d+\s", l)])
numa = " ".join(rd("numa.out").split())
L = {}
L["A1"] = ("0.5", f"[exécutée] {fact['A1']} ; [échec] value class (JEP 401, absente du JDK 27) : {err['A1']}")
L["A2"] = ("0.5", f"[exécutée] {fact['A2']}")
L["A3"] = ("0.5", f"[exécutée] {fact['A3']} ; [échec] champ de bits int x : 3 : {err['A3']}")
L["A4"] = ("0.5", f"[exécutée] {fact['A4']}")
L["A5"] = ("0.5", f"[exécutée] {fact['A5']}")
L["A6"] = ("0", rech("A6") + " ; aucun conteneur SoA")
L["A7"] = ("0.5", f"[exécutée] {fact['A7']}")
L["A8"] = ("1", f"[exécutée] {fact['A8']}")
L["B1"] = ("0", f"[échec] {fact['B1']}")
notes.append(f"NOTE;B1;-XX:+UnlockExperimentalVMOptions -XX:+UseEpsilonGC -Xmx256m (collecteur expérimental{' : ' + eps0.group(1) if eps0 else ''}) : {e1[1]} Mio alloués sans référence, {e1[2]} collecte, {e1[3]} Mio occupés ; 300 Mio : {'OutOfMemoryError, la JVM s’arrête' if oom else 'pas d’erreur'} (rien n'est rendu sans ramasse-miettes)")
L["B2"] = ("0.5", f"[exécutée] {fact['B2']} ; " + rech("B2", " : Arena, SegmentAllocator, slicingAllocator et prefixAllocator (FFM, segments seulement), Region et AbstractRegionPainter (Swing), MemoryPoolMXBean (supervision), XMLEventAllocator (StAX) : aucun allocateur d'objets"))
L["B3"] = ("0", f"[échec] {fact['B3']} ; " + rech("B3"))
L["B4"] = ("0", f"[échec] {fact['B4']}")
L["B5"] = ("0.5", f"[exécutée] {fact['B5']}")
L["C1"] = ("0.5", f"[exécutée] {fact['C1']}, en incubation ({'avertissement « WARNING: Using incubator modules: jdk.incubator.vector » au lancement' if inc else 'sans avertissement'})")
L["C2"] = ("0", rech("C2", " : ConstantInstruction.ofIntrinsic et IntrinsicConstantInstruction (instructions constantes du bytecode, API java.lang.classfile), faux positifs") + " ; aucune intrinsèque propre à x86")
L["C4"] = ("0.5", f"[exécutée] {fact['C4']} ; réduction sans ordre de la Vector API, en incubation ; " + rech("C4", " : VectorOperators.Associative et Operator.isAssociative (Vector API), la même capacité"))
L["C5"] = ("1", f"[exécutée] {fact['C5']}")
L["D1"] = ("1", f"[exécutée] {fact['D1']}")
L["D2"] = ("1", f"[exécutée] {fact['D2']}")
L["D3"] = ("0.5", f"[exécutée] @jdk.internal.vm.annotation.Contended sur deux champs long voisins (javac --add-exports java.base/jdk.internal.vm.annotation=ALL-UNNAMED) : écart {c1} o avec -XX:-RestrictContended, {c2} o sans (annotation ignorée pour les classes de l'application) ; annotation interne ; " + rech("D3", " : MonitorContended* (JDI), hasContended (AbstractQueuedSynchronizer), SessionCacheSize (SSL), caches de Swing, faux positifs"))
L["D4"] = ("0", rech("D4") + " ; ni affinité de fil ni de processus")
L["D5"] = ("1", f"[exécutée] {fact['D5']}")
L["E1"] = ("0.5", f"[exécutée] -XX:+PrintCompilation : {pc} méthodes compilées listées ; [échec] -XX:+PrintAssembly : « {hs.group(0) if hs else 'hsdis chargé'} » (la bibliothèque hsdis n'est pas livrée avec le JDK : code machine en octets bruts seulement)")
L["E2"] = ("0", f"[échec] asm(\"pause\") : {err['E2']} ; " + rech("E2"))
L["E3"] = ("0", rech("E3") + " ; aucune indication de branchement")
L["E4"] = ("0", rech("E4") + " ; aucun préchargement (Unsafe.prefetch* retirées au JDK 9)")
L["E5"] = ("0", f"[échec] {fact['E5']} ; " + rech("E5", " : importedKeyRestrict, NO_USAGE_RESTRICTIONS, DERIVATION_RESTRICTION, canUnrestrictedlyRedefineClasses, faux positifs") + " ; ni restrict ni règle de non-aliasing")
L["E6"] = ("0", f"[échec] {fact['E6']}")
L["E7"] = ("0", f"[échec] génériques effacés, List<int> : {err['E7a']} ; pas d'évaluation à la compilation, case N avec N = f(10) : {err['E7b']} ; " + rech("E7"))
L["F1"] = ("0.5", f"[exécutée] {fact['F1']}")
L["F2"] = ("0", rech("F2", " : Locale (texte) et PixelInterleavedSampleModel (images), faux positifs") + " ; aucune construction de localité ni de distribution")
notes.append(f"NOTE;F2;-XX:+UseNUMA (allocation NUMA du collecteur, option globale de la JVM) : {numa} : coupée par l'ergonomie sur cet hôte à un seul nœud ; HotSpot passe par libnuma (dlopen), tierce")
L["F3"] = ("0.5", f"[exécutée] {fact['F3']}")
L["F4"] = ("1", f"[exécutée] {fact['F4']}")
order = ["A1","A2","A3","A4","A5","A6","A7","A8","B1","B2","B3","B4","B5","C1","C2","C4","C5","D1","D2","D3","D4","D5","E1","E2","E3","E4","E5","E6","E7","F1","F2","F3","F4"]
for c in order: print(f"CAP;{c};{L[c][0]};{L[c][1]}")
for l in notes: print(l)
PY
