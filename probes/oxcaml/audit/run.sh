#!/bin/sh
# Audit de la grille, OxCaml 5.4.0-ox7 (réglages du banc : ocamlopt -O3 ; bibliothèques livrées avec le compilateur) :
# programme exécuté (audit.ml), code machine lu dans l'assembleur (-S) de fonctions compilées une à une, formes
# refusées, essais à part (indices de bloc, Multicore, attribut cold) et recherches d'absence dans les interfaces
# livrées (.mli de la bibliothèque standard, unix, str, threads, runtime_events, dynlink, stdlib_stable,
# stdlib_upstream_compatible, stdlib_alpha, stdlib_beta ; sans compiler-libs). Règle de la grille pour OxCaml
# (docs/V6_1.md, 4.5) : entière si la capacité s'écrit avec ce que le compilateur livre, extensions « stable »
# comprises ; moitié si elle demande une extension « beta » ou « alpha », ou des primitives [@@builtin] déclarées à
# la main. Sortie : lignes CAP.
cd "$(dirname "$0")" && rm -rf bin && mkdir -p bin/fail bin/asm bin/try bin/cold bin/plain
O=/opt/oxcaml/bin/ocamlopt
INC="-I +unix -I +str -I +stdlib_stable -I +stdlib_upstream_compatible"
LIBS="unix.cmxa str.cmxa stdlib_stable.cmxa stdlib_upstream_compatible.cmxa"
QUIET="-alert -do_not_spawn_domains-unsafe_multidomain"
# un symbole par primitive déclarée : l'unité y fait référence, aucune fonction C n'est appelée (bench/oxcaml/build.sh)
defs() { grep -o '"caml_[a-z0-9_]*"' "$1" | tr -d '"' | grep -v unreachable | sort -u | sed 's/^/-ccopt -Wl,--defsym,/; s/$/=0/' | tr '\n' ' '; }
(cd bin && cp ../audit.ml . && $O -O3 $QUIET $INC $LIBS $(defs audit.ml) audit.ml -o audit > build.log 2>&1; rm -f audit.ml)
# le même programme sous -extension-universe stable : toutes les extensions qu'il emploie sont de maturité « stable »
(cd bin && cp ../audit.ml audit_st.ml && $O -O3 -extension-universe stable $QUIET $INC -c audit_st.ml > build_st.log 2>&1; echo $? > stable.rc)
bin/audit > bin/audit.out
# code machine : une fonction par fichier, assembleur entier gardé
s() { printf '%s\n' "$2" > bin/asm/$1.ml; (cd bin/asm && $O -O3 $3 $INC -S -c $1.ml > $1.log 2>&1); }
s e6 'let cg_idx (a : float array) i = a.(i)'
s e6u 'let cg_idx (a : float array) i = a.(i)' -unsafe
s e6l 'let cg_idx (a : float array) i = Array.unsafe_get a i'
s e4 'external prefetch_r : '"'"'a -> (int[@untagged]) -> unit = "" "caml_prefetch_read_high_val_offset_untagged" [@@noalloc] [@@builtin]
let pf (a : int array) i = prefetch_r a (8 * i)'
s d5 'external pause : unit -> unit = "" "caml_pause_hint" [@@noalloc] [@@builtin]
let spin (a : int Atomic.t) = while Atomic.get a = 0 do pause () done'
s c2 'external fma : float32x8# -> float32x8# -> float32x8# -> float32x8# = "caml_vec256_unreachable" "caml_fma_float32x8_mul_add" [@@noalloc] [@@builtin]
external sad : int8x32# -> int8x32# -> int64x4# = "caml_vec256_unreachable" "caml_avx2_int8x32_sad_unsigned" [@@noalloc] [@@builtin]
external popcnt : (int64[@unboxed]) -> (int[@untagged]) = "" "caml_int64_popcnt_unboxed_to_untagged" [@@noalloc] [@@builtin]
let f a b c = fma a b c
let g a b = sad a b
let h a = popcnt a'
s e7 'let[@inline never] poly_sum (add : '"'"'a -> '"'"'a -> '"'"'a) (z : '"'"'a) (a : '"'"'a array) = Array.fold_left add z a
let fl = poly_sum ( +. ) 0. [| 1.; 2. |]
let it = poly_sum ( + ) 0 [| 1; 2 |]'
# attribut [@cold] : la même fonction, l'appelée marquée [@cold] ou [@inline never], avec et sans -cfg-block-layout
cold() { printf 'let[%s] slow x = prerr_int x; x\nlet hot (a : int array) =\n  let s = ref 0 in\n  for i = 0 to Array.length a - 1 do\n    let v = Array.unsafe_get a i in\n    if v < 0 then s := !s + slow v else s := !s + v\n  done;\n  !s\n' "$2" > bin/$1/e3.ml; (cd bin/$1 && $O -O3 -S -c e3.ml -o e3.cmx > e3.log 2>&1; cp e3.s e3_default.s 2>/dev/null; $O -O3 -cfg-block-layout -S -c e3.ml -o e3.cmx > e3_layout.log 2>&1; cp e3.s e3_layout.s 2>/dev/null); }
cold cold '@cold'
cold plain '@inline never'
# formes refusées : première ligne d'erreur
w() { printf '%s\n' "$2" > bin/fail/$1.ml; $O $3 $INC -c -o bin/fail/$1.cmx bin/fail/$1.ml 2>&1 | grep -m1 -E '^(Error|Alert|>> Fatal error)' > bin/fail/$1.err; }
w E2 'let () = asm "pause"'
w C5 'let _ = Parallel.fork_join2'
w C1a 'let add (a : float32x8#) (b : float32x8#) = Float32x8.add a b'
w C1b 'let add (a : float32x8#) (b : float32x8#) : float32x8# = a +. b'
w C2 'external add16 : float32x16# -> float32x16# -> float32x16# = "caml_vec512_unreachable" "caml_avx512_float32x16_add" [@@noalloc] [@@builtin]
let f a b = add16 a b'
w B3 'let escape x = let t = stack_ (x, x) in t'
w B4 'let[@zero_alloc] pair x = (x, x)' -O3
w E5a 'type t = { mutable a : int }
let use (x : t @ unique) = x.a
let twice (x : t @ unique) = use x + use x'
w E5b 'type r = { x : string; y : string }
let update (r : r @ unique) = overwrite_ r with { x = "foo" }' '-extension-universe alpha'
w E7 'let id : ('"'"'a : any). '"'"'a -> '"'"'a = fun x -> x'
# essais à part : compilés, liés et exécutés ; un échec de compilation laisse sa première ligne d'erreur
t() { printf '%s\n' "$2" > bin/try/$1.ml; (cd bin/try && $O -O3 $QUIET $INC $3 $LIBS $4 $1.ml -o $1 > $1.log 2>&1 && ./$1 > $1.out 2>&1; grep -m1 -E '^Error' $1.log > $1.err; $O -O3 -extension-universe stable $QUIET $INC $3 -c $1.ml -o $1_st.cmx > $1_st.log 2>&1; echo $? > $1_st.rc); }
t a2 'open Stdlib_stable
type order = { w : float#; s : string; y : int64_u; z : int }
let () =
  let o = { w = #1.5; s = "s"; y = #42L; z = 7 } in
  let i : (order, int64_u) idx_imm = (.y) in
  Printf.printf "Idx_imm.get o (.y) = %Ld" (Stdlib_upstream_compatible.Int64_u.to_int64 (Idx_imm.get o i))'
t d1 'let () =
  let dom : int Atomic.t = Atomic.make (-1) in
  (match Multicore.spawn_on ~domain:1 (fun () -> Atomic.set dom (Multicore.current_domain ())) () with
   | Spawned -> ()
   | Failed (_, e, _) -> raise e);
  while Atomic.get dom < 0 do Domain.cpu_relax () done;
  Printf.printf "Multicore.spawn_on ~domain:1 (bibliothèque threads livrée) : fil exécuté sur le domaine %d, Multicore.max_domains = %d" (Atomic.get dom) (Multicore.max_domains ())' '-I +threads' threads.cmxa
(cd ../../.. && python3 tools/grid_audit/search.py oxcaml A2 A3 A4 A6 A7 B2 B3 C1 C2 C4 C5 D2 D4 D5 E2 E3 E4 E5 E7 F2) > bin/search.out
N=$(find /opt/oxcaml/lib/ocaml -name '*.mli' | grep -vE '/compiler-libs/|/ocamldoc/|/caml/|/camlinternal' | wc -l)
python3 - "$N" <<'PY'
import os, re, sys
n = sys.argv[1]
rd = lambda f: open("bin/" + f).read() if os.path.exists("bin/" + f) else ""
out = rd("audit.out").splitlines()
fact = {l.split(";")[1]: l.split(";", 2)[2] for l in out if l.startswith("FACT;")}
srch = {l.split(";")[1]: l.split(";") for l in rd("search.out").splitlines() if l.startswith("SEARCH;")}
err = lambda k: rd(f"fail/{k}.err").strip() or "(aucune erreur)"
asm = lambda k: rd(f"asm/{k}.s")
cnt = lambda k, pat: len(re.findall(pat, asm(k)))
ins = lambda k, name: cnt(k, r"(?m)^\s+" + name)  # instructions dont le mnémonique commence par name
tried = lambda k: rd(f"try/{k}.out").strip() or ("refusé : " + (rd(f"try/{k}.err").strip() or "?"))
stable = lambda k: "accepté" if rd(f"try/{k}_st.rc").strip() == "0" else "refusé"
def code(s):
    """Section de code d'un assembleur (entre __code_begin et __code_end), sans les directives de débogage."""
    m = re.search(r"__code_begin:(.*?)^\w+__code_end:", s, re.S | re.M)
    return [l for l in (m.group(1) if m else "?" + s).splitlines() if not re.match(r"\s*\.(file|loc|cfi)", l)]
def rech(c, exam=""):
    s = srch[c]; pl = "s" if int(s[2]) > 1 else ""
    return f"[recherche] motif {c} dans les {n} interfaces livrées avec OxCaml 5.4.0-ox7 (bibliothèque standard, unix, str, threads, runtime_events, dynlink, stdlib_stable, stdlib_upstream_compatible) : {s[2]} déclaration{pl}{exam} ({s[5]})"
st = "le programme entier compile sous -extension-universe stable" if rd("stable.rc").strip() == "0" else "LE PROGRAMME NE COMPILE PAS SOUS -extension-universe stable"
cold_same = {k: code(rd(f"cold/e3_{k}.s")) == code(rd(f"plain/e3_{k}.s")) for k in ("default", "layout")}
cold_n = len(code(rd("cold/e3_default.s")))
L = {}
L["A1"] = ("1", f"[exécutée] {fact['A1']} ; {st}")
L["A2"] = ("0.5", f"[exécutée] {fact['A2']} ; décalage typé d'un champ par un indice de bloc : {tried('a2')} ({stable('a2')} sous -extension-universe stable) ; " + rech("A2"))
L["A3"] = ("0", f"[échec] {fact['A3']} ; " + rech("A3"))
L["A4"] = ("0", rech("A4", " : Arg.align (mise en page de l'aide) et Obj.unaligned_tag, faux positifs") + " ; aucun contrôle de l'alignement")
L["A5"] = ("0.5", f"[exécutée] {fact['A5']}")
L["A6"] = ("0", rech("A6") + " ; aucun conteneur SoA")
L["A7"] = ("0.5", f"[exécutée] {fact['A7']} ; " + rech("A7"))
L["A8"] = ("1", f"[exécutée] {fact['A8']} ; dans un enregistrement, un mot par champ (A1, A3)")
L["B1"] = ("0", f"[échec] {fact['B1']}")
L["B2"] = ("0.5", f"[exécutée] {fact['B2']} ; " + rech("B2"))
L["B3"] = ("1", f"[exécutée] {fact['B3']} ; une valeur stack_ qui s'échappe est refusée : {err('B3')} ; " + rech("B3"))
L["B4"] = ("0.5", f"[exécutée] {fact['B4']} ; vérifié par le compilateur fonction par fonction : let[@zero_alloc] pair x = (x, x) est refusée : {err('B4')}")
L["B5"] = ("0.5", f"[exécutée] {fact['B5']}")
L["C1"] = ("0.5", f"[exécutée] {fact['C1']} ; aucune opération dans le langage ni dans les bibliothèques livrées : a +. b sur float32x8# : {err('C1b')} float ; Float32x8.add : {err('C1a')} ; " + rech("C1"))
L["C2"] = ("0.5", f"[exécutée] primitives [@@builtin] déclarées à la main, code machine : {ins('c2', 'vfmadd')} vfmadd (FMA), {ins('c2', 'vpsadbw')} vpsadbw (AVX2), {ins('c2', 'popcnt')} popcnt ; ni type ni primitive de 512 bits : {err('C2')} ; " + rech("C2"))
L["C4"] = ("0", f"[échec] {fact['C4']} ; " + rech("C4"))
L["C5"] = ("0", f"[échec] Parallel (paquet opam, non livré) : {err('C5')} ; " + rech("C5") + " ; Multicore.spawn et Domain.spawn seulement (D1)")
L["D1"] = ("1", f"[exécutée] {fact['D1']} ; {tried('d1')}")
L["D2"] = ("0.5", f"[exécutée] {fact['D2']} ; " + rech("D2", " : Domain.Tick.acquire et release (minuterie), Semaphore.acquire et release (verrous), Gc.finalise_release, Sys.ocaml_release, et des lignes de documentation, faux positifs : aucun ordre relâché, acquire ou release"))
L["D3"] = ("1", f"[exécutée] {fact['D3']}")
L["D4"] = ("0", rech("D4") + " ; ni affinité de domaine ni de processus (Multicore.spawn_on désigne un domaine, pas un processeur)")
L["D5"] = ("0.5", f"[exécutée] {fact['D5']} ; primitive caml_pause_hint déclarée à la main : {ins('d5', 'pause')} pause dans le code machine ; " + rech("D5", " : Domain.cpu_relax (la capacité), Unix.pause et Runtime_events.pause (signaux, traces)") + " ; aucune barrière explicite : Atomic est séquentiellement cohérent")
L["E1"] = ("1", f"[exécutée] ocamlopt -S : {len(asm('e6').splitlines())} lignes d'assembleur pour une fonction d'une ligne")
L["E2"] = ("0", f"[échec] asm \"pause\" : {err('E2')} ; " + rech("E2"))
L["E3"] = ("0", f"[échec] [@cold] sur la fonction appelée dans la branche rare : le code machine du module ({cold_n} lignes) est {'le même' if cold_same['default'] else 'DIFFÉRENT'} qu'avec [@inline never], et {'le même' if cold_same['layout'] else 'DIFFÉRENT'} avec l'option -cfg-block-layout : l'attribut ne déplace pas la branche rare ; " + rech("E3", " : lignes de documentation de Hashtbl et MoreLabels (« less likely »), faux positifs") + " ; aucune indication de branchement")
L["E4"] = ("0.5", f"[exécutée] primitive caml_prefetch_read_high_val_offset_untagged déclarée à la main : {ins('e4', 'prefetch')} prefetch dans le code machine ; " + rech("E4") + " ; aucune interface livrée")
L["E5"] = ("0", f"[échec] le mode unique est une règle de typage (second usage refusé : {err('E5a')}) sans effet sur le code produit : overwrite_ sous -extension-universe alpha : {err('E5b')} ; " + rech("E5"))
L["E6"] = ("1", f"[exécutée] {fact['E6']} ; code machine de a.(i) : {ins('e6', 'jae')} comparaison à la longueur suivie d'un saut (jae) vers la levée d'Invalid_argument ; Array.unsafe_get : {ins('e6l', 'jae')} ; avec -unsafe (option globale) : {ins('e6u', 'jae')}")
L["E7"] = ("0", f"[échec] pas de monomorphisation : {cnt('e7', r'(?m)^caml[A-Za-z0-9_.]*poly_sum[A-Za-z0-9_.]*_code:')} corps pour poly_sum, appelée sur des float et sur des int ; une fonction ne peut pas être polymorphe en disposition : {err('E7')} ; " + rech("E7") + " ; ni calcul à la compilation (ppx_template est un paquet tiers)")
L["F1"] = ("1", f"[exécutée] {fact['F1']}")
L["F2"] = ("0", rech("F2", " : Seq.interleave, faux positif") + " ; aucune construction de localité ni de distribution")
L["F3"] = ("0.5", f"[exécutée] {fact['F3']}")
L["F4"] = ("1", f"[exécutée] {fact['F4']}")
order = ["A1","A2","A3","A4","A5","A6","A7","A8","B1","B2","B3","B4","B5","C1","C2","C4","C5","D1","D2","D3","D4","D5","E1","E2","E3","E4","E5","E6","E7","F1","F2","F3","F4"]
for c in order: print(f"CAP;{c};{L[c][0]};{L[c][1]}")
PY
