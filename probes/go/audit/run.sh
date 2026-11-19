#!/bin/sh
# Audit de la grille, Go 1.27.3 (réglages du banc : GOAMD64=v4 ; GOEXPERIMENT=simd pour les paquets simd) : programme
# exécuté (main/) dont le code machine des fonctions cg* est lu par go tool objdump, paquets expérimentaux arena et
# simd construits avec et sans GOEXPERIMENT, assembleur de Go (asm/), formes refusées par le compilateur, et
# recherches d'absence dans la liste de l'API publique livrée (api/go1*.txt). Sortie : lignes CAP et NOTE.
cd "$(dirname "$0")" && mkdir -p bin/fail
export GOTOOLCHAIN=local GOFLAGS=-mod=mod
G=/opt/go127/bin/go
(cd main && GOAMD64=v4 $G build -o ../bin/audit . && GOAMD64=v4 $G build -gcflags=-m -o /dev/null . 2> ../bin/escape.txt)
bin/audit > bin/audit.out
$G tool objdump -s 'main\.cg' bin/audit > bin/objdump.txt
(cd main && GOAMD64=v4 $G build -gcflags=-B -o ../bin/audit_B .) && $G tool objdump -s 'main\.cgIdx$' bin/audit_B > bin/objdump_B.txt
(cd arenas && $G build -o ../bin/arenas . > ../bin/arenas_off.txt 2>&1; GOEXPERIMENT=arenas $G build -o ../bin/arenas .) && bin/arenas > bin/arenas.out
(cd simd && GOAMD64=v4 $G build -o ../bin/simd . > ../bin/simd_off.txt 2>&1; GOAMD64=v4 GOEXPERIMENT=simd $G build -o ../bin/simd .) && bin/simd > bin/simd.out
$G tool objdump -s 'main\.cg' bin/simd > bin/objdump_simd.txt
(cd asm && $G build -o ../bin/asm .) && bin/asm > bin/asm.out
# formes refusées (un fichier chacune)
w() { printf 'package main\n\n%s\n\nfunc main() {}\n' "$2" > bin/fail/$1.go; $G build -o /dev/null bin/fail/$1.go 2>&1 | grep -m1 -E '[0-9]+:[0-9]+: ' | sed -E 's/^.*\.go:[0-9]+:[0-9]+: //' > bin/fail/$1.err; }
w A3 'type P struct { B uint32 : 3 }'
w A5 'type U union { f float32; u uint32 }'
w E2 'func f() { asm("pause") }'
w E7 'func f(n int) int { return n }
const N = f(10)'
w F1 'func g(n int) { var a [n][4]float64; _ = a }'
w D3 'import "internal/cpu"
var _ cpu.CacheLinePad'
w E4 'import "internal/runtime/sys"
func f(p uintptr) { sys.Prefetch(p) }'
w D5 'import "runtime"
func f() { runtime.procyield(10) }'
(cd ../../.. && python3 tools/grid_audit/search.py go A3 A6 C2 C4 C5 D3 D5 E2 E3 E4 E5 F2) > bin/search.out
python3 - <<'PY'
import re
rd = lambda f: open("bin/" + f).read()
out = rd("audit.out").splitlines()
fact = {l.split(";")[1]: l.split(";", 2)[2] for l in out if l.startswith("FACT;")}
notes = [l for l in out if l.startswith("NOTE;")]
srch = {l.split(";")[1]: l.split(";") for l in rd("search.out").splitlines() if l.startswith("SEARCH;")}
err = {k: rd(f"fail/{k}.err").strip() for k in ("A3", "A5", "E2", "E7", "F1", "D3", "E4", "D5")}
def funcs(txt):
    d, cur = {}, None
    for l in txt.splitlines():
        if l.startswith("TEXT "):
            cur = l.split()[1].split("(SB)")[0]; d[cur] = []
        elif cur: d[cur].append(l)
    return d
F = funcs(rd("objdump.txt")); FS = funcs(rd("objdump_simd.txt"))
def cnt(d, name, pat): return sum(1 for l in d.get(name, []) if re.search(pat, l))
def rech(c, exam=""):
    s = srch[c]; pl = "s" if int(s[2]) > 1 else ""
    return f"[recherche] motif {c} dans l'API publique de Go 1.27.3 (api/go1*.txt livrés avec la chaîne) : {s[2]} déclaration{pl}{exam} ({s[5]})"
ar = rd("arenas.out").split(); sm = rd("simd.out").split()
aoff = re.search(r"build constraints exclude all Go files in \S+", rd("arenas_off.txt"))
soff = re.search(r"build constraints exclude all Go files in \S+", rd("simd_off.txt"))
esc = rd("escape.txt")
L = {}
L["A1"] = ("1", f"[exécutée] {fact['A1']}")
L["A2"] = ("1", f"[exécutée] {fact['A2']}")
L["A3"] = ("0", f"[échec] {fact['A3']} ; champ de bits B uint32 : 3 : {err['A3']} ; " + rech("A3", " : attributs DWARF (AttrBitOffset, AttrBitSize, TagPackedType…, paquet debug/dwarf) et CurveParams.BitSize, faux positifs"))
L["A4"] = ("0.5", f"[exécutée] {fact['A4']}")
L["A5"] = ("0.5", f"[exécutée] {fact['A5']} ; [échec] union : {err['A5']}")
L["A6"] = ("0", rech("A6", " : DNS_TYPE_SOA (syscall pour Windows), faux positif") + " ; aucun conteneur SoA")
L["A7"] = ("1", f"[exécutée] {fact['A7']}")
L["A8"] = ("1", f"[exécutée] {fact['A8']}")
L["B1"] = ("0", f"[échec] {fact['B1']}")
L["B2"] = ("0.5", f"[exécutée] paquet arena avec GOEXPERIMENT=arenas : arena.New deux fois → objets à {ar[0]} o l'un de l'autre, MakeSlice de {ar[1]} float64, Free libère tout d'un coup ; sans l'expérience : « {aoff.group(0) if aoff else '?'} »")
L["B3"] = ("0.5", f"[exécutée] {fact['B3']} : « {'moved to heap: p' if 'moved to heap: p' in esc else '?'} » pour escape3, rien pour local3 ; aucune construction pour l'imposer")
L["B4"] = ("0.5", f"[exécutée] {fact['B4']}")
L["B5"] = ("1", f"[exécutée] {fact['B5']}")
p512 = cnt(FS, "main.cgPortable@simd512", r"VFMADD\w+PS .*Z\d")
L["C1"] = ("0.5", f"[exécutée] paquet simd portable (GOEXPERIMENT=simd) : simd.VectorBitSize() = {sm[0]}, LoadFloat32s(a).MulAdd(b, c) = {sm[1]} ; versions produites pour chaque largeur ({', '.join(k.split('@')[1] for k in FS if k.startswith('main.cgPortable@'))}), {p512} VFMADD sur Z dans simd512 ; sans l'expérience : « {soff.group(0) if soff else '?'} »")
L["C2"] = ("0.5", f"[exécutée] simd/archsimd (GOEXPERIMENT=simd) : LoadFloat32x16(a).Add(b) = {sm[2]}, {cnt(FS, 'main.cgArch', r'VADDPS .*Z')} VADDPS sur Z dans le code machine ; expérimental")
L["C4"] = ("0", f"[échec] {fact['C4']} ; code machine de cgSumF : {cnt(F, 'main.cgSumF', r'ADDSD')} ADDSD scalaire, {cnt(F, 'main.cgSumF', r'VADDPD|ADDPD')} addition vectorielle ; la spécification interdit la réassociation ; " + rech("C4", " : IMAGE_COMDAT_SELECT_ASSOCIATIVE (debug/pe), faux positif"))
L["C5"] = ("0", rech("C5", " : B.RunParallel, B.SetParallelism, T.Parallel (exécution parallèle des tests et des bancs d'essai du paquet testing), pas une construction de données parallèles") + " ; ni boucle parallèle ni réserve de tâches (goroutines à répartir soi-même, D1)")
L["D1"] = ("1", f"[exécutée] {fact['D1']}")
L["D2"] = ("0.5", f"[exécutée] {fact['D2']} ; code machine : Store {cnt(F, 'main.cgStore', r'XCHGL')} XCHGL (séquentiellement cohérent), Load {cnt(F, 'main.cgLoad', r'MOVL')} MOVL, Add {cnt(F, 'main.cgAdd', r'LOCK')} LOCK XADDQ")
L["D3"] = ("0", f"[échec] internal/cpu.CacheLinePad : {err['D3']} ; " + rech("D3") + " ; aucune constante ni type de bourrage exportés")
L["D4"] = ("1", f"[exécutée] {fact['D4']} ; ½ en v1")
L["D5"] = ("0", f"[échec] runtime.procyield (PAUSE, interne) : {err['D5']} ; " + rech("D5", " : syscall.Pause (appel système pause(2)) et GCStats.Pause (durées du ramasse-miettes), faux positifs") + " ; ni pause ni barrière explicite")
L["E1"] = ("1", f"[exécutée] go tool objdump : {len(F)} fonctions cg* désassemblées ; aussi go build -gcflags=-S")
L["E2"] = ("0.5", f"[exécutée] assembleur de Go dans un fichier .s à part (asm/add_amd64.s, TEXT ·addOne) : addOne(41) = {rd('asm.out').strip()} ; [échec] assembleur en ligne asm(\"pause\") : {err['E2']} ; " + rech("E2"))
L["E3"] = ("0", rech("E3") + " ; aucune indication de branchement (l'optimisation guidée par profil, default.pgo, n'en est pas une)")
L["E4"] = ("0", f"[échec] internal/runtime/sys.Prefetch : {err['E4']} ; " + rech("E4") + " ; aucun préchargement exporté")
L["E5"] = ("0", f"[échec] {fact['E5']} ; " + rech("E5", " : TagRestrictType (DWARF), SO_RESTRICT* (Darwin), TokenHasRestrictions et TokenRestrictedSids (Windows), faux positifs") + " ; ni restrict ni règle de non-aliasing")
L["E6"] = ("1", f"[exécutée] {fact['E6']} ; code machine : cgIdx {cnt(F, 'main.cgIdx', r'CMPQ')} CMPQ + {cnt(F, 'main.cgIdx', r'panicBounds')} appel à runtime.panicBounds, cgIdxUnsafe {cnt(F, 'main.cgIdxUnsafe', r'panicBounds')} (contrôle local) ; -gcflags=-B (global) : cgIdx {cnt(funcs(rd('objdump_B.txt')), 'main.cgIdx', r'panicBounds')} appel")
shapes = [k for k in F if k.startswith("main.cgSum[") or k.startswith("main.cgCount[")]
L["E7"] = ("0.5", f"[exécutée] {fact['E7']} ; code machine : {len(shapes)} corps, un par forme GC ({', '.join(k[5:] for k in shapes)}) : *A et *B partagent un corps à dictionnaire ; [échec] const N = f(10) : {err['E7']}")
L["F1"] = ("0.5", f"[exécutée] {fact['F1']} ; [échec] var a [n][4]float64 : {err['F1']}")
L["F2"] = ("0", rech("F2", " : SYS_MBIND, SYS_SET_MEMPOLICY, SYS_GET_MEMPOLICY et SYS_NUMA_* (numéros d'appels système bruts, section 3 de docs/GRID_AUDIT.md), PT_GNU_MBIND_* et STB_* (debug/elf), NumAttrs (log/slog), IFT_INTERLEAVE (BSD), faux positifs") + " ; aucune construction de localité ni de distribution")
L["F3"] = ("1", f"[exécutée] {fact['F3']}")
L["F4"] = ("1", f"[exécutée] {fact['F4']} ; ½ en v1")
order = ["A1","A2","A3","A4","A5","A6","A7","A8","B1","B2","B3","B4","B5","C1","C2","C4","C5","D1","D2","D3","D4","D5","E1","E2","E3","E4","E5","E6","E7","F1","F2","F3","F4"]
for c in order: print(f"CAP;{c};{L[c][0]};{L[c][1]}")
for l in notes: print(l)
PY
