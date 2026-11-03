#!/usr/bin/env python3
"""Copies de la remarque sur OCaml (plan : docs/OCAML.md, section 3.3), produites par remplacements de texte contrôlés
(chaque texte remplacé doit apparaître exactement une fois ; le reste du fichier est identique à l'octet).

* bench/ocaml_ref : copie exacte de bench/ocaml_k9h (le code publié : bench/ocaml, harnais commun de K9).
* bench/ocaml_fix : correction publiée, quatre corrections :
  (a) Q6 tuned (et `mt`, qui l'appelle) : prédicat sans branchement, comme dans les autres implémentations ; le code
      publié combinait les bornes par `&&`, évalué en court-circuit, et gardait deux branchements par ligne ;
  (b) K1 aos : `x *. x` au lieu de `x ** 2.`, qui appelle `pow` de la bibliothèque C trois fois par particule ;
  (c) K8 tuned : les deux références de l'arène (sommet, compteur) allouées une fois et remises à zéro à chaque
      requête, comme les variables de pile du C, au lieu de deux allocations par requête (la spécification exige
      « aucune allocation en régime permanent ») ;
  (d) horloge : `Runtime_events.Timestamp.get_current` (monotone, à la nanoseconde, livrée avec OCaml depuis 5.4),
      comme le demande la spécification (« l'horloge monotone de plus haute résolution du langage »), au lieu de
      `Unix.gettimeofday` (murale, à la microseconde).
* bench/ocaml_exp : ocaml_fix et des variantes nouvelles (sensibilités) : K6 `tuned_m` et `mt_m` (Q6, masque tiré des
  bits de signe), K8 `tuned_val` (arène par valeur, comme la copie c_k8val de C), K7 `tuned_p` (clé et compteur dans un
  seul entier : deux mots par case), K9 `tuned_fa` et `mt_fa` (`floatarray` au lieu d'un `Bigarray`), K5 `tuned_8`
  (huit accumulateurs, comme JavaScript).
Usage : make_copies.py (puis build.sh de ocaml_ref, ocaml_fix et ocaml_exp)."""
import os, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NOTE = "(* remarque sur OCaml (docs/OCAML.md) : "


def sub(text, old, new):
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"texte trouvé {n} fois (1 attendu) :\n{old[:300]}")
    return text.replace(old, new)


FIX = [
    # (d) horloge monotone
    ("let now () = Unix.gettimeofday ()\n",
     NOTE + "horloge monotone à la nanoseconde de la distribution, depuis OCaml 5.4 *)\n"
     "let now () = Int64.to_float (Runtime_events.Timestamp.to_int64 (Runtime_events.Timestamp.get_current ())) *. 1e-9\n"),
    # (b) K1 aos : pas de pow
    ("  let e i = 0.5 *. Array1.unsafe_get f (i + 9) *. ((Array1.unsafe_get f (i + 3) ** 2.) +. (Array1.unsafe_get f (i + 4) ** 2.) +. (Array1.unsafe_get f (i + 5) ** 2.)) in\n",
     "  " + NOTE + "x *. x, pas pow de la libm *)\n"
     "  let e i = let x = Array1.unsafe_get f (i + 3) and y = Array1.unsafe_get f (i + 4) and z = Array1.unsafe_get f (i + 5) in\n"
     "    0.5 *. Array1.unsafe_get f (i + 9) *. ((x *. x) +. (y *. y) +. (z *. z)) in\n"),
    # (a) Q6 tuned sans branchement
    ("    let m = Bool.to_int (sd - 8766 >= 0 && sd - 8766 < 365) land Bool.to_int (d - 5 >= 0 && d - 5 <= 2) land Bool.to_int (q < 24) in\n",
     "    " + NOTE + "chaque comparaison séparément ; && (court-circuit) gardait deux branchements *)\n"
     "    let m = Bool.to_int (sd - 8766 >= 0) land Bool.to_int (sd - 8766 < 365) land Bool.to_int (d - 5 >= 0)\n"
     "            land Bool.to_int (d - 5 <= 2) land Bool.to_int (q < 24) in\n"),
    # (c) K8 tuned : références allouées une fois
    ("  let lat = Array.make q 0.0 in\n  for r = -warmup to reps - 1 do\n",
     "  let lat = Array.make q 0.0 in\n"
     "  " + NOTE + "sommet et compteur de l'arène alloués une fois, remis à zéro à chaque requête *)\n"
     "  let top = ref 0 and ca = ref 0 in\n"
     "  for r = -warmup to reps - 1 do\n"),
    ("      let c = ref qq in\n      let s = if v = \"tuned\" then a_sum (a_build (ref 0) 10 c) else t_sum (t_build 10 c) in\n",
     "      let s = if v = \"tuned\" then (top := 0; ca := qq; a_sum (a_build top 10 ca)) else t_sum (t_build 10 (ref qq)) in\n"),
]


def fix(text):
    for a, b in FIX:
        text = sub(text, a, b)
    return text


DEF_Q6 = """(* Q6, masque tiré des bits de signe : une seule comparaison par ligne (sensibilité, docs/OCAML.md) *)
let[@inline never] q6_tuned_m c lo hi =
  let s = ref 0 in
  for i = lo to hi - 1 do
    let sd = Int32.to_int (Array1.unsafe_get c.sd i) and d = Array1.unsafe_get c.d i and q = Array1.unsafe_get c.q i in
    let x = (sd - 8766) lor (9130 - sd) lor (d - 5) lor (7 - d) lor (23 - q) in
    s := !s + (Int32.to_int (Array1.unsafe_get c.pr i) * d * (1 - ((x lsr 62) land 1)))
  done;
  !s

"""

DEF_K8 = """(* K8, arène par valeur (copie c_k8val de C ; sensibilité, docs/OCAML.md) : l'indice du nœud en ordre préfixe est
   passé par valeur, la valeur du nœud vaut q + indice, la fonction rend l'indice libre suivant *)
let rec a_build_val i d q =
  Array.unsafe_set av i (q + i);
  if d = 0 then (Array.unsafe_set al i (-1); Array.unsafe_set ar i (-1); i + 1)
  else begin
    let l = i + 1 in
    let r = a_build_val l (d - 1) q in
    Array.unsafe_set al i l;
    Array.unsafe_set ar i r;
    a_build_val r (d - 1) q
  end

"""

DEF_K5 = """(* K5, huit accumulateurs (sensibilité, docs/OCAML.md) *)
let[@inline never] k5_tuned8 (a : (float, float32_elt, c_layout) Array1.t) (b : (float, float32_elt, c_layout) Array1.t) =
  let s0 = ref 0.0 and s1 = ref 0.0 and s2 = ref 0.0 and s3 = ref 0.0 and s4 = ref 0.0 and s5 = ref 0.0 and s6 = ref 0.0
  and s7 = ref 0.0 in
  let i = ref 0 in
  while !i < Array1.dim a do
    let g k = Array1.unsafe_get a (!i + k) *. Array1.unsafe_get b (!i + k) in
    s0 := !s0 +. g 0; s1 := !s1 +. g 1; s2 := !s2 +. g 2; s3 := !s3 +. g 3;
    s4 := !s4 +. g 4; s5 := !s5 +. g 5; s6 := !s6 +. g 6; s7 := !s7 +. g 7;
    i := !i + 8
  done;
  ((!s0 +. !s1) +. (!s2 +. !s3)) +. ((!s4 +. !s5) +. (!s6 +. !s7))

"""

DEF_K9 = """(* K9, floatarray (tableau de flottants à plat de la bibliothèque standard) au lieu d'un Bigarray (sensibilité,
   docs/OCAML.md) *)
let[@inline never] k9_rows_fa (a : floatarray) (b : floatarray) r0 r1 =
  for i = r0 to r1 - 1 do
    let up = (i - 1) * m9 and mid = i * m9 and dn = (i + 1) * m9 in
    for j = 1 to m9 - 2 do
      Float.Array.unsafe_set b (mid + j)
        (0.25 *. (((Float.Array.unsafe_get a (up + j) +. Float.Array.unsafe_get a (dn + j)) +. Float.Array.unsafe_get a (mid + j - 1)) +. Float.Array.unsafe_get a (mid + j + 1)))
    done
  done

"""

EXP = [
    # chaque définition nouvelle juste avant la fonction run_kN qui l'utilise
    ("let run_k5 v reps =\n", DEF_K5 + "let run_k5 v reps =\n"),
    ("let run_k6 v reps p =\n", DEF_Q6 + "let run_k6 v reps p =\n"),
    ("let run_k8 v reps =\n", DEF_K8 + "let run_k8 v reps =\n"),
    ("let run_k9 v reps =\n", DEF_K9 + "let run_k9 v reps =\n"),
    # K5 tuned_8
    ("  let f = if v = \"tuned\" then k5_tuned else k5_natural in\n  bench \"k5\"",
     "  let f = if v = \"tuned\" then k5_tuned else if v = \"tuned_8\" then k5_tuned8 else k5_natural in\n  bench \"k5\""),
    # K6 tuned_m et mt_m (Q6)
    ("       | \"tuned\" -> one q1_tuned 0 n6\n",
     "       | \"tuned\" -> one q1_tuned 0 n6\n"
     "       | \"tuned_m\" -> q6_tuned_m c 0 n6\n"
     "       | \"mt_m\" ->\n"
     "           let ds = Array.init 4 (fun k -> Domain.spawn (fun () -> q6_tuned_m c (n6 / 4 * k) (n6 / 4 * (k + 1)))) in\n"
     "           Array.fold_left (fun s d -> s + Domain.join d) 0 ds\n"),
    # K7 tuned_p : run_k7 reconnaît la variante (branche « tuned » d'origine pour les autres)
    ("      end else begin\n        let logc = 21 in\n",
     "      end else if v = \"tuned_p\" then begin\n"
     "        (* clé (32 bits) et compteur (30 bits) dans un seul entier : deux mots par case *)\n"
     "        let logc = 21 in\n"
     "        let cap = 1 lsl logc and cmask = (1 lsl 30) - 1 in\n"
     "        let t0 = now () in\n"
     "        let tab = Array.make (2 * cap) 0 in\n"
     "        for i = 0 to n - 1 do\n"
     "          let k = key i in\n"
     "          let s = ref (((k * 0x9E3779B1) land 0xFFFFFFFF) lsr (32 - logc)) in\n"
     "          while (let p = Array.unsafe_get tab (2 * !s) in p land cmask <> 0 && p lsr 30 <> k) do s := (!s + 1) land (cap - 1) done;\n"
     "          let b = 2 * !s in\n"
     "          Array.unsafe_set tab b ((k lsl 30) lor ((Array.unsafe_get tab b land cmask) + 1));\n"
     "          Array.unsafe_set tab (b + 1) (Array.unsafe_get tab (b + 1) + Int32.to_int (Array1.unsafe_get vals i))\n"
     "        done;\n"
     "        let dt = now () -. t0 in\n"
     "        let nk = ref 0 and ws = ref 0 in\n"
     "        for s = 0 to cap - 1 do\n"
     "          let p = tab.(2 * s) in\n"
     "          if p land cmask <> 0 then (incr nk; ws := !ws + (tab.((2 * s) + 1) * (((p lsr 30) land 1023) + 1)))\n"
     "        done;\n"
     "        (!nk, !ws, dt)\n"
     "      end else begin\n        let logc = 21 in\n"),
    # K8 tuned_val
    ("      let s = if v = \"tuned\" then (top := 0; ca := qq; a_sum (a_build top 10 ca)) else t_sum (t_build 10 (ref qq)) in\n",
     "      let s = if v = \"tuned\" then (top := 0; ca := qq; a_sum (a_build top 10 ca))\n"
     "        else if v = \"tuned_val\" then (ignore (a_build_val 0 10 qq); a_sum 0)\n"
     "        else t_sum (t_build 10 (ref qq)) in\n"),
    # K9 tuned_fa et mt_fa : branche floatarray avant la branche Bigarray
    ("  end else begin\n    let a = Array1.create float64 c_layout (m9 * m9) and b = Array1.create float64 c_layout (m9 * m9) in\n",
     "  end else if v = \"tuned_fa\" || v = \"mt_fa\" then begin\n"
     "    let a = Float.Array.create (m9 * m9) and b = Float.Array.create (m9 * m9) in\n"
     "    let step x y =\n"
     "      if v = \"tuned_fa\" then k9_rows_fa x y 1 (m9 - 1)\n"
     "      else Array.iter Domain.join (Array.init 4 (fun t -> Domain.spawn (fun () -> k9_rows_fa x y (1 + ((m9 - 2) * t / 4)) (1 + ((m9 - 2) * (t + 1) / 4)))))\n"
     "    in\n"
     "    for r = -warmup to reps - 1 do\n"
     "      for k = 0 to (m9 * m9) - 1 do let x = k9_init (k / m9) (k mod m9) in Float.Array.set a k x; Float.Array.set b k x done;\n"
     "      let t0 = now () in\n"
     "      step a b; step b a; step a b; step b a;\n"
     "      let dt = now () -. t0 in\n"
     "      let s = ref 0.0 in\n"
     "      for k = 0 to (m9 * m9) - 1 do s := !s +. Float.Array.get a k done;\n"
     "      if r >= 0 then result \"k9\" v \"2048^2x4\" r dt (Printf.sprintf \"%.15e\" !s)\n"
     "    done\n"
     "  end else begin\n    let a = Array1.create float64 c_layout (m9 * m9) and b = Array1.create float64 c_layout (m9 * m9) in\n"),
]


def exp(text):
    text = fix(text)
    for a, b in EXP:
        text = sub(text, a, b)
    return text


BUILD = """#!/bin/sh
# OCaml 5.5.2 + flambda (-O3) ; bibliothèques unix, bigarray et runtime_events de la distribution (horloge monotone,
# remarque sur OCaml, docs/OCAML.md)
set -e
cd "$(dirname "$0")"
/opt/ocaml/bin/ocamlopt -O3 -I +unix -I +runtime_events unix.cmxa runtime_events.cmxa ms.ml -o ms
"""


def copy(dst, text, build):
    d = os.path.join(ROOT, "bench", dst)
    if os.path.exists(d):
        shutil.rmtree(d)
    os.makedirs(d)
    open(os.path.join(d, "ms.ml"), "w", encoding="utf-8").write(text)
    shutil.copy2(os.path.join(ROOT, "bench", "ocaml_k9h", "run"), os.path.join(d, "run"))
    if build is None:
        shutil.copy2(os.path.join(ROOT, "bench", "ocaml_k9h", "build.sh"), os.path.join(d, "build.sh"))
    else:
        open(os.path.join(d, "build.sh"), "w").write(build)
        os.chmod(os.path.join(d, "build.sh"), 0o755)
    print(f"{dst} écrit")


def main():
    src = open(os.path.join(ROOT, "bench", "ocaml_k9h", "ms.ml"), encoding="utf-8").read()
    copy("ocaml_ref", src, None)
    copy("ocaml_fix", fix(src), BUILD)
    copy("ocaml_exp", exp(src), BUILD)
    open(os.path.join(ROOT, "bench", "ocaml_exp", "extra_variants"), "w").write(
        "k6 tuned_m q6\nk6 mt_m q6\nk8 tuned_val\nk7 tuned_p\nk9 tuned_fa\nk9 mt_fa\nk5 tuned_8\n")


if __name__ == "__main__":
    main()
