#!/bin/sh
# Audit de la grille, OCaml 5.5.2 + flambda (réglages du banc : ocamlopt -O3, bibliothèques unix et bigarray) :
# programme exécuté (audit.ml), code machine lu dans l'assembleur (-S) et dans le binaire (objdump), formes refusées,
# et recherches d'absence dans les interfaces livrées (.mli de la bibliothèque standard, unix, str, threads,
# runtime_events ; sans compiler-libs). Sortie : lignes CAP et NOTE.
cd "$(dirname "$0")" && mkdir -p bin/fail
O=/opt/ocaml/bin/ocamlopt
(cd bin && cp ../audit.ml . && $O -O3 -S -I +unix -I +str unix.cmxa str.cmxa audit.ml -o audit > build.log 2>&1 && rm -f audit.ml)
(cd bin && cp ../audit.ml audit_u.ml && $O -O3 -S -unsafe -I +unix -I +str unix.cmxa str.cmxa audit_u.ml -o audit_u > build_u.log 2>&1)
bin/audit > bin/audit.out
objdump -d --no-show-raw-insn bin/audit | awk '/<caml_ml_domain_cpu_relax>:/{p=1} p&&/^$/{exit} p' > bin/relax.txt
w() { printf '%s\n' "$2" > bin/fail/$1.ml; $O -c -o bin/fail/$1.cmx bin/fail/$1.ml 2>&1 | grep -m1 -E '^Error' > bin/fail/$1.err; }
w E2 'let () = asm "pause"'
w C5 'let _ = Domainslib.Task.setup_pool ~num_domains:4 ()'
w C1 'let v : float32x4 = Obj.magic 0'
(cd ../../.. && python3 tools/grid_audit/search.py ocaml A2 A3 A4 A6 A7 B2 B3 C1 C2 C4 C5 D2 D4 D5 E2 E3 E4 E5 E7 F2) > bin/search.out
N=$(find /opt/ocaml/lib/ocaml -name '*.mli' | grep -vE '/compiler-libs/|/ocamldoc/|/caml/|/camlinternal' | wc -l)
python3 - "$N" <<'PY'
import re, sys
n = sys.argv[1]
rd = lambda f: open("bin/" + f).read()
out = rd("audit.out").splitlines()
fact = {l.split(";")[1]: l.split(";", 2)[2] for l in out if l.startswith("FACT;")}
srch = {l.split(";")[1]: l.split(";") for l in rd("search.out").splitlines() if l.startswith("SEARCH;")}
err = {k: rd(f"fail/{k}.err").strip() for k in ("E2", "C5", "C1")}
def fn(asm, name):
    m = re.search(r"^camlAudit(_u)?\." + name + r"_\d+:.*?\.cfi_endproc", asm, re.S | re.M)
    return m.group(0) if m else ""
S, SU = rd("audit.s"), rd("audit_u.s")
bound = lambda a: len(re.findall(r"caml_ml_array_bound_error", fn(a, "cg_idx")))
cmpb = lambda a: len(re.findall(r"cmpq\s+%rbx, %rsi", fn(a, "cg_idx")))
polys = re.findall(r"^camlAudit\.poly_sum_\d+:", S, re.M)
def rech(c, exam=""):
    s = srch[c]; pl = "s" if int(s[2]) > 1 else ""
    return f"[recherche] motif {c} dans les {n} interfaces livrées avec OCaml 5.5.2 (bibliothèque standard, unix, str, threads, runtime_events) : {s[2]} déclaration{pl}{exam} ({s[5]})"
L = {}
L["A1"] = ("0", f"[échec] {fact['A1']}")
L["A2"] = ("0", f"[échec] {fact['A2']} ; " + rech("A2"))
L["A3"] = ("0", f"[échec] {fact['A3']} ; " + rech("A3", " : signed_bitsize et unsigned_bitsize (Int, Int32, Int64, Nativeint), faux positifs"))
L["A4"] = ("0", rech("A4", " : Arg.align (mise en page de l'aide) et Obj.unaligned_tag, faux positifs") + " ; aucun contrôle de l'alignement")
L["A5"] = ("0.5", f"[exécutée] {fact['A5']}")
L["A6"] = ("0", rech("A6") + " ; aucun conteneur SoA")
L["A7"] = ("0", f"[échec] {fact['A7']} ; " + rech("A7"))
L["A8"] = ("0.5", f"[exécutée] {fact['A8']}")
L["B1"] = ("0", f"[échec] {fact['B1']}")
L["B2"] = ("0", rech("B2") + " ; ni arène ni allocateur à choisir")
L["B3"] = ("0", f"[échec] {fact['B3']} ; " + rech("B3"))
L["B4"] = ("0", f"[échec] {fact['B4']}")
L["B5"] = ("0.5", f"[exécutée] {fact['B5']}")
L["C1"] = ("0", f"[échec] type float32x4 : {err['C1']} ; " + rech("C1") + " ; aucun type vectoriel en OCaml 5.5")
L["C2"] = ("0", rech("C2") + " ; aucune intrinsèque")
L["C4"] = ("0", f"[échec] {fact['C4']} ; " + rech("C4"))
L["C5"] = ("0", f"[échec] Domainslib (bibliothèque tierce) : {err['C5']} ; " + rech("C5") + " ; Domain.spawn seulement (D1)")
L["D1"] = ("1", f"[exécutée] {fact['D1']}")
L["D2"] = ("0.5", f"[exécutée] {fact['D2']} ; " + rech("D2", " : Semaphore.acquire et release (verrous), Gc.finalise_release, et des lignes de documentation, faux positifs : aucun ordre relâché, acquire ou release"))
L["D3"] = ("1", f"[exécutée] {fact['D3']}")
L["D4"] = ("0", rech("D4") + " ; ni affinité de domaine ni de processus (Unix n'a pas sched_setaffinity)")
L["D5"] = ("0.5", f"[exécutée] {fact['D5'].split(' (')[0]} : {len(re.findall(r'pause', rd('relax.txt')))} pause dans caml_ml_domain_cpu_relax du runtime (objdump) ; " + rech("D5", " : Domain.cpu_relax (la capacité), Unix.pause et Runtime_events.pause (signaux, traces)") + " ; aucune barrière explicite : Atomic est séquentiellement cohérent")
L["E1"] = ("1", f"[exécutée] ocamlopt -S : {len(S.splitlines())} lignes d'assembleur pour audit.ml")
L["E2"] = ("0", f"[échec] asm \"pause\" : {err['E2']} ; " + rech("E2"))
L["E3"] = ("0", rech("E3", " : lignes de documentation de Hashtbl et MoreLabels (« less likely »), faux positifs") + " ; aucune indication de branchement")
L["E4"] = ("0", rech("E4") + " ; aucun préchargement")
L["E5"] = ("0", rech("E5") + " ; ni restrict ni règle de non-aliasing")
L["E6"] = ("1", f"[exécutée] {fact['E6']} ; code machine de cg_idx : {cmpb(S)} comparaison à la longueur et {bound(S)} appel à caml_ml_array_bound_error ; avec -unsafe (option globale) : {cmpb(SU)} et {bound(SU)}")
L["E7"] = ("0", f"[échec] pas de monomorphisation : {len(polys)} corps pour poly_sum dans l'assembleur, appelé sur des float avec allocation de boîtes (B4) ; " + rech("E7") + " ; ni calcul à la compilation")
L["F1"] = ("1", f"[exécutée] {fact['F1']}")
L["F2"] = ("0", rech("F2", " : Seq.interleave, faux positif") + " ; aucune construction de localité ni de distribution")
L["F3"] = ("0.5", f"[exécutée] {fact['F3']}")
L["F4"] = ("1", f"[exécutée] {fact['F4']}")
order = ["A1","A2","A3","A4","A5","A6","A7","A8","B1","B2","B3","B4","B5","C1","C2","C4","C5","D1","D2","D3","D4","D5","E1","E2","E3","E4","E5","E6","E7","F1","F2","F3","F4"]
for c in order: print(f"CAP;{c};{L[c][0]};{L[c][1]}")
PY
