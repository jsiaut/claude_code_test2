#!/bin/sh
# Audit de la grille, C# (.NET 10.0.14, SDK 10.0.403, réglages du banc) : programme exécuté (Audit.cs) dont le code
# machine des méthodes Cg* est listé par DOTNET_JitDisasm, formes refusées par le compilateur (csc de Roslyn), et
# recherches d'absence dans l'API publique du paquet de référence Microsoft.NETCore.App.Ref
# (tools/grid_audit/listings/dotnet_api). Sortie : lignes CAP et NOTE, une par case.
cd "$(dirname "$0")" && mkdir -p bin
D=/opt/dotnet/dotnet
REF=/opt/dotnet/packs/Microsoft.NETCore.App.Ref/10.0.14/ref/net10.0
CSC="$D /opt/dotnet/sdk/10.0.403/Roslyn/bincore/csc.dll -nologo -t:library -unsafe -r:$REF/System.Runtime.dll"
$D build -c Release --nologo -v q -o bin/out > bin/build.log 2>&1
DOTNET_JitDisasm='Cg*' DOTNET_JitStdOutFile=bin/jit.txt $D bin/out/audit.dll > bin/audit.out
printf 'class X { static void Main() { asm("pause"); } }\n' > bin/e2.cs
printf 'struct B { int x : 3; }\n' > bin/a3.cs
printf 'class Y { const int N = F(10); static int F(int n) => n; }\n' > bin/e7.cs
for f in e2 a3 e7; do $CSC -out:bin/$f.dll bin/$f.cs 2>&1 | grep -m1 -o 'error CS[0-9]*: .*' > bin/$f.err; done
(cd ../../.. && python3 tools/grid_audit/search.py csharp A6 B2 C4 D3 E2 E3 E5 F2) > bin/search.out
N=$(cd ../../.. && sh -c "$(python3 -c "import json;print(json.load(open('tools/grid_audit/patterns.json'))['langs']['csharp']['listing'])")" | wc -l)
V=$($D --list-runtimes | grep NETCore.App | cut -d' ' -f2)
python3 - bin/audit.out bin/jit.txt bin/search.out "$N" "$V" <<'PY'
import re, sys
out = [l.rstrip("\n") for l in open(sys.argv[1])]
jit = open(sys.argv[2]).read()
srch = {l.split(";")[1]: l.rstrip("\n").split(";") for l in open(sys.argv[3]) if l.startswith("SEARCH;")}
n, ver = sys.argv[4], sys.argv[5]
err = {k: open(f"bin/{k}.err").read().strip() for k in ("e2", "a3", "e7")}
meth = {}
for part in jit.split("; Assembly listing for method ")[1:]:
    name = part.split("(")[0].split(":")[1]
    meth[name] = "\n".join(l for l in part.splitlines() if l.startswith("       "))
def cnt(m, pat): return len(re.findall(pat, meth.get(m, ""), re.M))
def rech(c, exam=""):
    s = srch[c]
    pl = "s" if int(s[2]) > 1 else ""
    return (f"[recherche] motif {c} dans l'API publique de .NET {ver} (paquet de référence Microsoft.NETCore.App.Ref, "
            f"{n} noms : types et membres publics) : {s[2]} nom{pl}{exam} ({s[5]})")
fact = {l.split(";")[1]: l.split(";", 2)[2] for l in out if l.startswith("FACT;")}
lines = {l.split(";")[1]: l for l in out if l.startswith("CAP;")}
notes = [l for l in out if l.startswith("NOTE;")]
L = lambda c, v, ev: lines.__setitem__(c, f"CAP;{c};{v};{ev}")
L("A3", "0.5", f"[exécutée] {fact['A3']} ; [échec] champ de bits int x : 3 : {err['a3']}")
L("A6", "0", rech("A6") + " ; aucun conteneur SoA")
L("B1", "0", f"[échec] {fact['B1']}")
L("B2", "0.5", f"[exécutée] {fact['B2']} ; " + rech("B2", " : RegionInfo, ExceptionRegion (métadonnées IL), NoGCRegion et les régions critiques du GC, MemoryPool<T> (tampons, comme ArrayPool), ThrowOnUnmappableCharEnable : aucune interface d'allocateur d'objets"))
L("C1", "1", f"[exécutée] {fact['C1']} ; code machine : CgFma {cnt('CgFma', r'vfmadd\w+ +ymm')} vfmadd sur ymm, CgVec512 {cnt('CgVec512', r'^ +v\w+ +zmm')} instructions sur zmm")
L("C2", "1", f"[exécutée] {fact['C2']} ; code machine de CgAvx512 : {cnt('CgAvx512', r'vaddps +zmm')} vaddps zmm")
L("C4", "0", f"[échec] {fact['C4']} ; a*b + a sur Vector512 reste vmulps + vaddps ({cnt('CgVec512', r'vfmadd')} FMA : pas de contraction) ; " + rech("C4"))
L("D2", "1", f"[exécutée] {fact['D2']} ; code machine : CgInc {cnt('CgInc', r'^ +lock')} lock + xadd, CgCas {cnt('CgCas', r'cmpxchg')} lock cmpxchg, Volatile.Write {cnt('CgVolWrite', r'^ +mov ')} mov simple ({cnt('CgVolWrite', r'lock')} lock), Volatile.Read {cnt('CgVolRead', r'^ +mov ')} mov")
L("D3", "0", rech("D3", " : Regex.CacheSize (cache des expressions rationnelles), faux positif") + " ; aucune constante ni type de bourrage")
L("D4", "0.5", f"[exécutée] {fact['D4']}")
L("D5", "1", f"[exécutée] {fact['D5']} ; code machine : CgPause {cnt('CgPause', r'^ +pause')} pause, CgBarrier {cnt('CgBarrier', r'^ +lock')} lock or")
L("E1", "1", f"[exécutée] DOTNET_JitDisasm : {len(meth)} méthodes Cg* listées ({len(jit.splitlines())} lignes), compilées en FullOpts (variables d'environnement du runtime livré, sans reconstruire)")
L("E2", "0", f"[échec] asm(\"pause\") : {err['e2']} ; " + rech("E2"))
L("E3", "0", rech("E3", " : HttpRequestHeader.Expect, HttpRequestHeaders.Expect, HttpWebRequest.Expect (en-tête HTTP Expect), faux positifs") + " ; aucune indication de branchement")
L("E4", "1", f"[exécutée] {fact['E4']} : {cnt('CgPrefetch', r'prefetcht0')} prefetcht0 dans le code machine (aussi Prefetch1, Prefetch2, PrefetchNonTemporal)")
L("E5", "0", f"[échec] {fact['E5']} ; " + rech("E5", " : Restriction(s), Unrestricted, FRESTRICTED… (restrictions XSD, COM, sécurité, liaison dynamique), faux positifs") + " ; ni restrict ni règle de non-aliasing")
L("E6", "1", f"[exécutée] {fact['E6']} ; code machine : CgIdx {cnt('CgIdx', r'RNGCHKFAIL')} appel à CORINFO_HELP_RNGCHKFAIL, CgIdxUnsafe {cnt('CgIdxUnsafe', r'RNGCHKFAIL')} (contrôle local par expression)")
spec = [m for m in meth if m.startswith("CgSum[")]
shared = [m for m in meth if m.startswith("CgCount[")]
L("E7", "0.5", f"[exécutée] {fact['E7']} ; code machine : {len(spec)} corps spécialisés pour les types valeur ({', '.join(spec)}), {len(shared)} corps partagé pour les références ({', '.join(shared)}) ; [échec] const int N = F(10) : {err['e7']}")
L("F2", "0", rech("F2", " : XmlEnumAttribute, SoapEnumAttribute, ScopelessEnumAttribute, InvalidEnumArgumentException (« numa » dans « EnumA… »), DataSet.Locale et DataTable.Locale, BindingFlags.OptionalParamBinding (« mbind »), faux positifs") + " ; aucune construction NUMA ni de distribution")
order = ["A1","A2","A3","A4","A5","A6","A7","A8","B1","B2","B3","B4","B5","C1","C2","C4","C5","D1","D2","D3","D4","D5","E1","E2","E3","E4","E5","E6","E7","F1","F2","F3","F4"]
for c in order: print(lines[c])
for l in notes: print(l)
PY
