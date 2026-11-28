(* Audit de la grille, OxCaml 5.4.0-ox7 (réglages du banc : ocamlopt -O3 ; bibliothèques livrées avec le compilateur :
   unix, str, stdlib_stable, stdlib_upstream_compatible) : chaque case est exercée sous sa forme la plus forte et
   imprime un fait observable (docs/V6_1.md, 4.5). Lignes FACT, reprises par run.sh avec le code machine, les formes
   refusées et les recherches. Les primitives [@@builtin] sont déclarées ici à la main : leur interface documentée est
   un paquet tiers (ocaml_simd, ocaml_intrinsics), que le compilateur ne livre pas. *)

module FU = Stdlib_upstream_compatible.Float_u
module I64 = Stdlib_upstream_compatible.Int64_u
module I32 = Stdlib_upstream_compatible.Int32_u
module NU = Stdlib_upstream_compatible.Nativeint_u
module F32 = Stdlib_stable.Float32_u
module I8 = Stdlib_stable.Int8_u

let fact c ev = Printf.printf "FACT;%s;%s\n%!" c ev
let words () = Gc.minor_words ()

external[@layout_poly] aget : ('a : any mod separable). 'a array -> int -> 'a = "%array_safe_get"
external[@layout_poly] aset : ('a : any mod separable). 'a array -> int -> 'a -> unit = "%array_safe_set"
external[@layout_poly] esize : ('a : any mod separable). 'a array -> int = "%array_element_size_in_bytes"
external[@layout_poly] amake : ('a : any mod separable). int -> 'a -> 'a array = "%makearray_dynamic"

(* Primitives reconnues par le compilateur : aucune fonction C, leurs symboles sont donnés à l'édition de liens. *)
external f32x8_const : (float32[@unboxed]) -> float32x8# = "caml_vec256_unreachable" "caml_float32x8_const1"
[@@noalloc] [@@builtin]
external f32x8_fma : float32x8# -> float32x8# -> float32x8# -> float32x8#
  = "caml_vec256_unreachable" "caml_fma_float32x8_mul_add" [@@noalloc] [@@builtin]
external f32x8_lo : float32x8# -> float32x4# = "caml_vec256_unreachable" "caml_vec256_low_to_vec128"
[@@noalloc] [@@builtin]
external f32x4_low : float32x4# -> (float32[@unboxed]) = "caml_vec128_unreachable" "caml_float32x4_low_to_float32"
[@@noalloc] [@@builtin]
external ptr_load_i32 : nativeint_u -> int32_u = "" "caml_native_pointer_load_unboxed_int32"
[@@noalloc] [@@builtin] [@@warning "-187"]
external ptr_store_i32 : nativeint_u -> int32_u -> unit = "" "caml_native_pointer_store_unboxed_int32"
[@@noalloc] [@@builtin] [@@warning "-187"]

type p4 = { x : float; y : float; z : float; vx : float }                      (* boxé : un bloc par élément *)
type u4 = #{ ux : float#; uy : float#; uz : float#; uvx : float# }             (* non boxé : en ligne *)
type u16 = #{ a0 : float32_u; a1 : float32_u; a2 : float32_u; a3 : float32_u; a4 : float32_u; a5 : float32_u;
              a6 : float32_u; a7 : float32_u; a8 : float32_u; a9 : float32_u; a10 : float32_u; a11 : float32_u;
              a12 : float32_u; a13 : float32_u; a14 : float32_u; a15 : float32_u }
type mixed = { c : char; i : int32_u; d : float# }                             (* bloc mixte : int32 en ligne *)
type order = { w : float#; s : string; y : int64_u; z : int }                  (* valeurs d'abord : s, z, w, y *)
type pk = { b : bool; n : int }
type b2 = #{ b0 : int8#; b1 : int8# }
type with_arr = { f : float array; k : int }
type f16 = #{ v0 : float#; v1 : float#; v2 : float#; v3 : float#; v4 : float#; v5 : float#; v6 : float#; v7 : float#;
              v8 : float#; v9 : float#; v10 : float#; v11 : float#; v12 : float#; v13 : float#; v14 : float#;
              v15 : float# }
type with_inline = { v : f16; k2 : int }                                        (* 16 flottants en ligne dans le bloc *)
type tree = Leaf | Node of int * tree * tree

let[@inline never] pair i = (i, i + 1)
let[@inline never] pair_stack i = let t = stack_ (i, i + 1) in let a, b = t in a + b
let[@inline never] pair_region i : (int * int) @ local = exclave_ (i, i + 1)
let[@inline never] pair_caller i = let a, b = pair_region i in a + b
let[@inline never] fadd (a : float) (b : float) = a +. b
let[@inline never] fadd_u (a : float#) (b : float#) = FU.add a b
let[@inline never] poly_sum (add : 'a -> 'a -> 'a) (z : 'a) (a : 'a array) = Array.fold_left add z a
let[@inline never] mono_sum (a : float array) =
  let s = ref 0. in
  for i = 0 to Array.length a - 1 do s := !s +. a.(i) done;
  !s
let[@inline never] i32add a b = Int32.add a b
let[@inline never] i32add_u (a : int32_u) (b : int32_u) = I32.add a b

let rec pairwise (a : float array) lo hi =
  if hi - lo <= 8 then (let s = ref 0. in for i = lo to hi - 1 do s := !s +. a.(i) done; !s)
  else let m = (lo + hi) / 2 in pairwise a lo m +. pairwise a m hi

(* B2 : arbre bâti dans la région de l'appelant (exclave_), libéré en bloc au retour de request_region *)
let rec t_build d c = let v = !c in incr c; if d = 0 then Node (v, Leaf, Leaf) else
    let l = t_build (d - 1) c in let r = t_build (d - 1) c in Node (v, l, r)
let rec t_sum = function Leaf -> 0 | Node (v, l, r) -> v + t_sum l + t_sum r
let rec l_build d (c : int ref @ local) : tree @ local =
  let v = !c in
  incr c;
  if d = 0 then exclave_ Node (v, Leaf, Leaf)
  else exclave_ (let l = l_build (d - 1) c in let r = l_build (d - 1) c in Node (v, l, r))
let rec l_sum (t : tree @ local) = match t with Leaf -> 0 | Node (v, l, r) -> v + l_sum l + l_sum r
let[@inline never] request_heap q = t_sum (t_build 9 (ref q))
let[@inline never] request_region q = let c = stack_ (ref q) in l_sum (l_build 9 c) [@nontail]

let () =
  (* ---------- A *)
  let n = 1000 in
  let boxed = Array.init n (fun i -> { x = float i; y = 0.; z = 0.; vx = 0. }) in
  let flat : u4 array = amake n #{ ux = #1.0; uy = #2.0; uz = #3.0; uvx = #4.0 } in
  aset flat 7 #{ ux = #5.0; uy = #6.0; uz = #7.0; uvx = #8.0 };
  let q = aget flat 7 in
  let c16 : u16 array =
    amake n #{ a0 = #0.s; a1 = #1.s; a2 = #2.s; a3 = #3.s; a4 = #4.s; a5 = #5.s; a6 = #6.s; a7 = #7.s; a8 = #8.s;
               a9 = #9.s; a10 = #10.s; a11 = #11.s; a12 = #12.s; a13 = #13.s; a14 = #14.s; a15 = #15.s } in
  fact "A1" (Printf.sprintf "tableau de %d enregistrements non boxés #{4 float#} : %d octets par élément dans un seul bloc de %d mots (en ligne : ni pointeur ni en-tête par élément), flat.(7).#uy = %g ; le même enregistrement boxé : %d mots atteignables (%d par élément) ; 16 champs float32_u : %d octets par élément (un mot par champ)"
    n (esize flat) (Obj.size (Obj.repr flat)) (FU.to_float q.#uy) (Obj.reachable_words (Obj.repr boxed))
    (Obj.reachable_words (Obj.repr boxed) / n) (esize c16));
  let m = { c = 'a'; i = #7l; d = #1.5 } in
  let o = { w = #1.5; s = "s"; y = #42L; z = 7 } in
  let r = Obj.repr o in
  fact "A2" (Printf.sprintf "{char; int32_u; float#} : %d mots dans un seul bloc (%d atteignables : l'int32 est en ligne, sur un mot entier) ; {w : float#; s : string; y : int64_u; z : int} : bloc mixte, les %d valeurs d'abord (s, z) puis w et y : mot 1 = %nd (z = 7, étiqueté), mot 3 = %nd (y) : un mot par champ, ordre fixé par le compilateur, aucune disposition C"
    (Obj.size (Obj.repr m)) (Obj.reachable_words (Obj.repr m))
    (Obj.Uniform_or_mixed.mixed_scannable_prefix_len_exn (Obj.Uniform_or_mixed.of_block r))
    (Obj.raw_field r 1) (Obj.raw_field r 3));
  let p = { b = true; n = 3 } in
  let pk2 : b2 array = amake 4 #{ b0 = I8.of_int 1; b1 = I8.of_int 2 } in
  fact "A3" (Printf.sprintf "{bool; int} : %d mots (%d octets) ; tableau de #{int8#; int8#} : %d octets par élément : aucun compactage ni champ de bits"
    (Obj.size (Obj.repr p)) (8 * Obj.size (Obj.repr p)) (esize pk2));
  let bb = Bytes.create 4 in
  Bytes.set_int32_le bb 0 (Int32.bits_of_float 1.0);
  fact "A5" (Printf.sprintf "Int32.bits_of_float 1.0 = 0x%08lx ; Float32_u.to_bits #1.0s = 0x%08lx (sans boîte) ; octets relus par Bytes.get_uint8 : %d %d %d %d (copie, pas d'union)"
    (Int32.bits_of_float 1.0) (I32.to_int32 (F32.to_bits #1.0s)) (Bytes.get_uint8 bb 0) (Bytes.get_uint8 bb 1)
    (Bytes.get_uint8 bb 2) (Bytes.get_uint8 bb 3));
  let wa = { f = Array.make 16 0.; k = 2 } in
  let wi = { v = #{ v0 = #0.; v1 = #1.; v2 = #2.; v3 = #3.; v4 = #4.; v5 = #5.; v6 = #6.; v7 = #7.; v8 = #8.;
                    v9 = #9.; v10 = #10.; v11 = #11.; v12 = #12.; v13 = #13.; v14 = #14.; v15 = #15. }; k2 = 2 } in
  fact "A7" (Printf.sprintf "{float array; int} : %d mots dans le bloc, le tableau de 16 float est un bloc séparé (%d mots atteignables) ; {#{16 float#}; int} : %d mots dans un seul bloc (%d atteignables), wi.v.#v11 = %g : 16 flottants en ligne, lus par nom de champ, sans indexation"
    (Obj.size (Obj.repr wa)) (Obj.reachable_words (Obj.repr wa)) (Obj.size (Obj.repr wi))
    (Obj.reachable_words (Obj.repr wi)) (FU.to_float wi.v.#v11));
  let f32s : float32_u array = amake n #1.5s in
  let i8s : int8# array = amake n (I8.of_int 3) in
  let x32 = F32.add (aget f32s 3) #0.25s in
  fact "A8" (Printf.sprintf "float32_u array : %d octets par élément (bloc de %d mots pour %d éléments) ; int8# array : %d octet ; calcul en float32 sans boîte : 1.5 + 0.25 = %g ; Bigarray : int16 %d octets"
    (esize f32s) (Obj.size (Obj.repr f32s)) n (esize i8s) (FU.to_float (F32.to_float x32))
    (Bigarray.kind_size_in_bytes Bigarray.int16_signed));
  (* ---------- B *)
  let g0 = (Gc.quick_stat ()).Gc.minor_collections in
  let sink = ref [||] in
  for _ = 1 to 1024 * 1024 do sink := Array.make 127 0 done;
  let g1 = (Gc.quick_stat ()).Gc.minor_collections in
  fact "B1" (Printf.sprintf "1 Gio de tableaux de 1 Kio sans référence : %d collectes mineures déclenchées par le runtime, sans appel du programme (ramasse-miettes traçant, ni arrêt ni réglage qui le supprime)" (g1 - g0));
  let tot = ref 0 in
  let h0 = words () in
  for q = 0 to 999 do tot := !tot + request_heap q done;
  let h1 = words () in
  for q = 0 to 999 do tot := !tot + request_region q done;
  let h2 = words () in
  ignore (Sys.opaque_identity !tot);
  fact "B2" (Printf.sprintf "arbre de 1023 nœuds bâti dans la région locale de l'appelant (exclave_) et libéré en bloc à son retour : %.0f mots alloués sur le tas par arbre ; le même arbre sur le tas : %.0f mots ; une seule région, liée à la pile d'appels : ni allocateur à choisir ni arène durable"
    ((h2 -. h1) /. 1000.) ((h1 -. h0) /. 1000.));
  let w0 = words () in
  let acc = ref 0 in
  for i = 1 to 100000 do let (a, b) = pair i in acc := !acc + a + b done;
  let w1 = words () in
  for i = 1 to 100000 do acc := !acc + pair_stack i done;
  let w2 = words () in
  for i = 1 to 100000 do acc := !acc + pair_caller i done;
  let w3 = words () in
  ignore (Sys.opaque_identity !acc);
  fact "B3" (Printf.sprintf "n-uplet rendu par une fonction non incorporée : %.0f mots alloués sur le tas par appel ; alloué par stack_ : %.0f ; alloué par l'appelée dans la région de l'appelant (exclave_) : %.0f"
    ((w1 -. w0) /. 100000.) ((w2 -. w1) /. 100000.) ((w3 -. w2) /. 100000.));
  let fs = Array.init 100000 float in
  let w4 = words () in
  let s1 = ref 0. in
  for i = 0 to 99999 do s1 := fadd !s1 fs.(i) done;
  let w5 = words () in
  let s2 = poly_sum ( +. ) 0. fs in
  let w6 = words () in
  let mutable s3 = #0. in
  for i = 0 to 99999 do s3 <- fadd_u s3 (FU.of_float fs.(i)) done;
  let w7 = words () in
  ignore (Sys.opaque_identity (!s1 +. s2 +. FU.to_float s3 +. mono_sum fs));
  fact "B4" (Printf.sprintf "allocations implicites : float rendu par une fonction non incorporée %.0f mots par appel (boîte) ; somme polymorphe (Array.fold_left) %.0f mots par élément ; la même fonction sur float# : %.0f"
    ((w5 -. w4) /. 100000.) ((w6 -. w5) /. 100000.) ((w7 -. w6) /. 100000.));
  let ba = Bigarray.Array1.create Bigarray.int32 Bigarray.c_layout 8 in
  Bigarray.Array1.fill ba 0l;
  let view = Bigarray.Array1.sub ba 3 5 in
  Bigarray.Array1.set view 0 42l;
  let addr = NU.of_nativeint (Obj.raw_field (Obj.repr ba) 1) in
  ptr_store_i32 (NU.add addr #20n) #77l;
  fact "B5" (Printf.sprintf "Bigarray hors tas : Array1.sub ba 3 5 (vue décalée, sans copie) puis view.{0} <- 42 → ba.{3} = %ld ; adresse des données (Obj.raw_field), plus 20 octets, écrite par caml_native_pointer_store_unboxed_int32 et relue : %ld, ba.{5} = %ld (primitive déclarée à la main ; aucune allocation brute livrée)"
    (Bigarray.Array1.get ba 3) (I32.to_int32 (ptr_load_i32 (NU.add addr #20n))) (Bigarray.Array1.get ba 5));
  (* ---------- C *)
  let v = f32x8_fma (f32x8_const 2.0s) (f32x8_const 3.0s) (f32x8_const 1.0s) in
  let low = Stdlib_stable.Float32.to_float (f32x4_low (f32x8_lo v)) in
  fact "C1" (Printf.sprintf "float32x8# (type du langage, 256 bits, non boxé) : 2 × 3 + 1 = %g dans chaque voie, par la primitive caml_fma_float32x8_mul_add déclarée à la main" low);
  let rs = Random.State.make [| 42 |] in
  let big = Array.init 1048576 (fun _ -> Random.State.float rs 1.0 -. 0.5) in
  let sq = mono_sum big and pw = pairwise big 0 (Array.length big) in
  fact "C4" (Printf.sprintf "un million de float : boucle compilée %.17g, somme par paires écrite à la main %.17g (écart %.3g) : l'ordre est gardé, aucune option de réassociation" sq pw (Float.abs (pw -. sq)));
  (* ---------- D *)
  let cnt = Atomic.make 0 in
  let ds = List.init 4 (fun _ -> Domain.spawn (fun () -> for _ = 1 to 1000 do Atomic.incr cnt done)) in
  List.iter Domain.join ds;
  fact "D1" (Printf.sprintf "Domain.spawn : 4 domaines (fils système), %d incréments (Domain.recommended_domain_count = %d)" (Atomic.get cnt) (Domain.recommended_domain_count ()));
  let a = Atomic.make 5 in
  let ok = Atomic.compare_and_set a 5 8 in
  let old = Atomic.fetch_and_add a 3 in
  fact "D2" (Printf.sprintf "Atomic : compare_and_set 5 → 8 : %b, fetch_and_add 3 → %d puis %d (séquentiellement cohérents)" ok old (Atomic.get a));
  let ac = Atomic.make_contended 0 and an = Atomic.make 0 in
  fact "D3" (Printf.sprintf "Atomic.make_contended : bloc de %d mots, %d octets avec l'en-tête (une ligne de cache) ; Atomic.make : %d mot (bourrage contre le faux partage)"
    (Obj.size (Obj.repr ac)) (8 * (1 + Obj.size (Obj.repr ac))) (Obj.size (Obj.repr an)));
  for _ = 1 to 10 do Domain.cpu_relax () done;
  fact "D5" "Domain.cpu_relax exécuté";
  (* ---------- E *)
  let four = [| 1.; 2.; 3.; 4. |] in
  let msg = try ignore (four.(4 + Array.length Sys.argv - 1)); "rien" with Invalid_argument s -> s in
  fact "E6" (Printf.sprintf "four.(4) : Invalid_argument « %s » ; Array.unsafe_get four 2 = %.0f (local)" msg (Array.unsafe_get four (2 + Array.length Sys.argv - 1)));
  (* ---------- F *)
  let g = Bigarray.Array2.init Bigarray.float64 Bigarray.c_layout 3 4 (fun i j -> float (i * 4 + j)) in
  let flat1 = Bigarray.reshape_1 (Bigarray.genarray_of_array2 g) 12 in
  fact "F1" (Printf.sprintf "Bigarray.Array2 c_layout 3×4 (dimensions à l'exécution) : g.{2,3} = %.0f, élément 11 du bloc à plat = %.0f (reshape_1, sans copie) ; fortran_layout aussi" (Bigarray.Array2.get g 2 3) (Bigarray.Array1.get flat1 11));
  let w8 = words () in
  let x = ref 0l in
  for i = 1 to 1000 do x := i32add !x (Int32.of_int i) done;
  let w9 = words () in
  let mutable xu = #0l in
  for i = 1 to 1000 do xu <- i32add_u xu (I32.of_int i) done;
  let w10 = words () in
  fact "F3" (Printf.sprintf "Int32.add Int32.max_int 1l = %ld (enveloppe) ; Int32.unsigned_to_int (-1l) = %s ; une addition Int32 non incorporée alloue %.0f mots par tour (boîtes), la même sur int32_u %.0f (somme %ld) ; int8# : 127 + 1 = %d ; opérations unsigned_* sur des types signés, pas de type non signé"
    (Int32.add Int32.max_int 1l) (match Int32.unsigned_to_int (-1l) with Some v -> string_of_int v | None -> "None")
    ((w9 -. w8) /. 1000.) ((w10 -. w9) /. 1000.) (I32.to_int32 xu) (I8.to_int (I8.add (I8.of_int 127) (I8.of_int 1))));
  let fd = Unix.openfile "/opt/msdata/k5_a.f32" [ Unix.O_RDONLY ] 0 in
  let mp = Bigarray.array1_of_genarray (Unix.map_file fd Bigarray.float32 Bigarray.c_layout false [| 2048 |]) in
  let maps = In_channel.with_open_text "/proc/self/maps" In_channel.input_all in
  let has = try ignore (Str.search_forward (Str.regexp_string "/opt/msdata/k5_a.f32") maps 0); true with Not_found -> false in
  fact "F4" (Printf.sprintf "Unix.map_file → Bigarray float32 : k5_a.f32 projeté (%b, /proc/self/maps), premier float %.7g, dernier %.8g" has (Bigarray.Array1.get mp 0) (Bigarray.Array1.get mp 2047));
  ignore (Sys.opaque_identity !sink)
