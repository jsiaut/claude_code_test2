(* Audit de la grille, OCaml 5.5.2 + flambda (réglages du banc : ocamlopt -O3, bibliothèques unix et bigarray) :
   chaque case est exercée sous sa forme la plus forte et imprime un fait observable (docs/V4_PLAN.md 2.1). Lignes
   FACT (reprises par run.sh avec le code machine, les formes refusées et les recherches) et NOTE. *)

let fact c ev = Printf.printf "FACT;%s;%s\n%!" c ev
let words () = Gc.minor_words ()

type p4 = { x : float; y : float; z : float; vx : float }          (* enregistrement de flottants : à plat *)
type mixed = { c : char; i : int32; d : float }                    (* champs mêlés : un mot chacun, int32 boxé *)
type pk = { b : bool; n : int }
type with_arr = { f : float array; k : int }

let[@inline never] pair i = (i, i + 1)
let[@inline] pair_inl i = (i, i + 1)
let[@inline never] fadd (a : float) (b : float) = a +. b
let[@inline never] poly_sum (add : 'a -> 'a -> 'a) (z : 'a) (a : 'a array) = Array.fold_left add z a
let[@inline never] mono_sum (a : float array) = let s = ref 0. in for i = 0 to Array.length a - 1 do s := !s +. a.(i) done; !s
let[@inline never] cg_idx (a : float array) i = a.(i)
let[@inline never] cg_idx_unsafe (a : float array) i = Array.unsafe_get a i
let[@inline never] i32add a b = Int32.add a b

let rec pairwise (a : float array) lo hi =
  if hi - lo <= 8 then (let s = ref 0. in for i = lo to hi - 1 do s := !s +. a.(i) done; !s)
  else let m = (lo + hi) / 2 in pairwise a lo m +. pairwise a m hi

let () =
  (* ---------- A *)
  let n = 1000 in
  let arr = Array.init n (fun i -> { x = float i; y = 0.; z = 0.; vx = 0. }) in
  let fa = Float.Array.make n 0. in
  fact "A1" (Printf.sprintf "Array de %d enregistrements {4 float} : %d mots atteignables (%d par élément : un pointeur et un bloc séparé) ; Float.Array de %d float : %d mots (à plat, flottants seulement)"
    n (Obj.reachable_words (Obj.repr arr)) (Obj.reachable_words (Obj.repr arr) / n) n (Obj.reachable_words (Obj.repr fa)));
  let m = { c = 'a'; i = 7l; d = 1.5 } in
  fact "A2" (Printf.sprintf "{char; int32; float} : %d mots dans le bloc, int32 rangé à part (%d mots atteignables en tout) : un mot par champ, ni ordre ni taille contrôlables"
    (Obj.size (Obj.repr m)) (Obj.reachable_words (Obj.repr m)));
  let p = { b = true; n = 3 } in
  fact "A3" (Printf.sprintf "{bool; int} : %d mots (%d octets) : aucun compactage ni champ de bits" (Obj.size (Obj.repr p)) (8 * Obj.size (Obj.repr p)));
  let bb = Bytes.create 4 in
  Bytes.set_int32_le bb 0 (Int32.bits_of_float 1.0);
  fact "A5" (Printf.sprintf "Int32.bits_of_float 1.0 = 0x%08lx ; Int64.bits_of_float 1.0 = 0x%016Lx ; octets relus par Bytes.get_uint8 : %d %d %d %d (copie, pas d'union)"
    (Int32.bits_of_float 1.0) (Int64.bits_of_float 1.0) (Bytes.get_uint8 bb 0) (Bytes.get_uint8 bb 1) (Bytes.get_uint8 bb 2) (Bytes.get_uint8 bb 3));
  let w = { f = Array.make 16 0.; k = 2 } in
  fact "A7" (Printf.sprintf "{float array; int} : %d mots dans le bloc, le tableau de 16 float est un bloc séparé (%d mots atteignables)"
    (Obj.size (Obj.repr w)) (Obj.reachable_words (Obj.repr w)));
  fact "A8" (Printf.sprintf "Bigarray : int8 %d octet, int16 %d, float32 %d (stockage) ; les valeurs lues sont des int de 63 bits ou des float de 64 bits"
    (Bigarray.kind_size_in_bytes Bigarray.int8_signed) (Bigarray.kind_size_in_bytes Bigarray.int16_signed) (Bigarray.kind_size_in_bytes Bigarray.float32));
  (* ---------- B *)
  let g0 = (Gc.quick_stat ()).Gc.minor_collections in
  let sink = ref [||] in
  for _ = 1 to 1024 * 1024 do sink := Array.make 127 0 done;
  let g1 = (Gc.quick_stat ()).Gc.minor_collections in
  fact "B1" (Printf.sprintf "1 Gio de tableaux de 1 Kio sans référence : %d collectes mineures déclenchées par le runtime, sans appel du programme (ramasse-miettes traçant, ni arrêt ni réglage qui le supprime)" (g1 - g0));
  let w0 = words () in
  let acc = ref 0 in
  for i = 1 to 100000 do let (a, b) = pair i in acc := !acc + a + b done;
  let w1 = words () in
  for i = 1 to 100000 do let (a, b) = pair_inl i in acc := !acc + a + b done;
  let w2 = words () in
  ignore (Sys.opaque_identity !acc);
  fact "B3" (Printf.sprintf "n-uplet rendu par une fonction [@inline never] : %.0f mots alloués par appel ; incorporée [@inline] : %.0f (flambda le supprime localement, sans garantie du langage)"
    ((w1 -. w0) /. 100000.) ((w2 -. w1) /. 100000.));
  let fs = Array.init 100000 float in
  let w3 = words () in
  let s1 = ref 0. in
  for i = 0 to 99999 do s1 := fadd !s1 fs.(i) done;
  let w4 = words () in
  let s2 = poly_sum ( +. ) 0. fs in
  let w5 = words () in
  let s3 = mono_sum fs in
  let w6 = words () in
  ignore (Sys.opaque_identity (!s1 +. s2 +. s3));
  fact "B4" (Printf.sprintf "allocations implicites : float rendu par une fonction non incorporée %.0f mots par appel (boîte) ; somme polymorphe (Array.fold_left) %.0f mots par élément ; boucle monomorphe %.0f"
    ((w4 -. w3) /. 100000.) ((w5 -. w4) /. 100000.) ((w6 -. w5) /. 100000.));
  let ba = Bigarray.Array1.create Bigarray.int32 Bigarray.c_layout 8 in
  Bigarray.Array1.fill ba 0l;
  let view = Bigarray.Array1.sub ba 3 5 in
  Bigarray.Array1.set view 0 42l;
  fact "B5" (Printf.sprintf "Bigarray hors tas : Array1.sub ba 3 5 (vue décalée, sans copie) puis view.{0} <- 42 → ba.{3} = %ld ; pas de pointeur ni d'arithmétique libre" (Bigarray.Array1.get ba 3));
  (* ---------- C *)
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
  fact "D5" "Domain.cpu_relax exécuté (instruction pause dans le runtime, lue par run.sh) ; aucune barrière explicite : Atomic est séquentiellement cohérent";
  (* ---------- E *)
  let four = [| 1.; 2.; 3.; 4. |] in
  let msg = try ignore (cg_idx four (4 + Array.length Sys.argv - 1)); "rien" with Invalid_argument s -> s in
  fact "E6" (Printf.sprintf "four.(4) : Invalid_argument « %s » ; Array.unsafe_get four 2 = %.0f (local)" msg (cg_idx_unsafe four 2));
  (* ---------- F *)
  let g = Bigarray.Array2.init Bigarray.float64 Bigarray.c_layout 3 4 (fun i j -> float (i * 4 + j)) in
  let flat = Bigarray.reshape_1 (Bigarray.genarray_of_array2 g) 12 in
  fact "F1" (Printf.sprintf "Bigarray.Array2 c_layout 3×4 (dimensions à l'exécution) : g.{2,3} = %.0f, élément 11 du bloc à plat = %.0f (reshape_1, sans copie) ; fortran_layout aussi" (Bigarray.Array2.get g 2 3) (Bigarray.Array1.get flat 11));
  let w7 = words () in
  let x = ref 0l in
  for i = 1 to 1000 do x := i32add !x (Int32.of_int i) done;
  let w8 = words () in
  fact "F3" (Printf.sprintf "Int32.add Int32.max_int 1l = %ld (enveloppe) ; Int32.unsigned_to_int (-1l) = %s ; une addition Int32 non incorporée alloue %.0f mots par tour (boîtes) ; pas de type non signé"
    (Int32.add Int32.max_int 1l) (match Int32.unsigned_to_int (-1l) with Some v -> string_of_int v | None -> "None") ((w8 -. w7) /. 1000.));
  let fd = Unix.openfile "/opt/msdata/k5_a.f32" [ Unix.O_RDONLY ] 0 in
  let mp = Bigarray.array1_of_genarray (Unix.map_file fd Bigarray.float32 Bigarray.c_layout false [| 2048 |]) in
  let maps = In_channel.with_open_text "/proc/self/maps" In_channel.input_all in
  let has = try ignore (Str.search_forward (Str.regexp_string "/opt/msdata/k5_a.f32") maps 0); true with Not_found -> false in
  fact "F4" (Printf.sprintf "Unix.map_file → Bigarray float32 : k5_a.f32 projeté (%b, /proc/self/maps), premier float %.7g, dernier %.8g" has (Bigarray.Array1.get mp 0) (Bigarray.Array1.get mp 2047));
  ignore (Sys.opaque_identity !sink)
