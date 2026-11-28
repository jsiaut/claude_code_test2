(* Formes propres à OxCaml 5.4.0-ox7 (docs/V6_1.md, 4) : celles qu'OCaml ne pouvait pas écrire. La source commune avec
   OCaml est ms.ml, inchangée ; ce fichier-ci n'est compilé que par OxCaml. Bibliothèques livrées avec le compilateur
   seulement (stdlib, unix, runtime_events, stdlib_stable, stdlib_upstream_compatible). Les opérations sur les vecteurs
   et le préchargement sont des fonctions externes que le compilateur remplace par des instructions ([@@builtin]) ;
   build.sh donne leurs symboles à l'éditeur de liens (--defsym) : aucune n'est jamais appelée. *)
open Bigarray
module F32 = Stdlib_stable.Float32_u
module FU = Stdlib_upstream_compatible.Float_u

(* ------------------------------------------------------------------ harnais (celui de ms.ml) *)
let data_dir = try Sys.getenv "MS_DATA" with Not_found -> "/opt/msdata"
let warmup = try int_of_string (Sys.getenv "WARMUP") with Not_found -> 1

let map kind name =
  let fd = Unix.openfile (Filename.concat data_dir name) [ Unix.O_RDONLY ] 0 in
  let a = array1_of_genarray (Unix.map_file fd kind c_layout false [| -1 |]) in
  Unix.close fd;
  a

let result k v p rep sec chk = Printf.printf "RESULT;%s;%s;%s;%d;%.9f;%s\n%!" k v p rep sec chk
let now () = Int64.to_float (Runtime_events.Timestamp.to_int64 (Runtime_events.Timestamp.get_current ())) *. 1e-9

let bench k v p reps f =
  for r = -warmup to reps - 1 do
    let t0 = now () in
    let chk = f () in
    let dt = now () -. t0 in
    if r >= 0 then result k v p r dt chk
  done

(* ------------------------------------------------------------------ primitives *)
(* fichier projeté vu comme une suite d'octets : chargements de vecteurs non alignés, indices en octets *)
type bigstring = (char, int8_unsigned_elt, c_layout) Array1.t
let map_bytes name : bigstring = map char name

type f32x8 = float32x8#
type f32x4 = float32x4#
type f64x4 = float64x4#
type f64x2 = float64x2#
type i8x32 = int8x32#
type i8x16 = int8x16#
type i32x8 = int32x8#
type i32x4 = int32x4#
type i64x4 = int64x4#
type i64x2 = int64x2#

(* tableaux d'éléments non boxés *)
external[@layout_poly] aget : ('a : any mod separable). 'a array -> int -> 'a = "%array_unsafe_get"
external[@layout_poly] aset : ('a : any mod separable). 'a array -> int -> 'a -> unit = "%array_unsafe_set"
external[@layout_poly] amake : ('a : any mod separable). int -> 'a -> 'a array = "%makearray_dynamic"

(* chargements et écritures de vecteurs, sans vérification de bornes *)
external bs_f32x8 : bigstring -> int -> f32x8 = "%caml_bigstring_getu256u#"
external bs_i32x8 : bigstring -> int -> i32x8 = "%caml_bigstring_getu256u#"
external bs_i8x16 : bigstring -> int -> i8x16 = "%caml_bigstring_getu128u#"
external bytes_i8x32 : bytes -> int -> i8x32 = "%caml_bytes_getu256u#"
external f32a_x8 : float32_u array -> int -> f32x8 = "%caml_unboxed_float32_array_get256u#"
external fa_x4 : float# array -> int -> f64x4 = "%caml_unboxed_float_array_get256u#"
external fa_set_x4 : float# array -> int -> f64x4 -> unit = "%caml_unboxed_float_array_set256u#"

(* f32 *)
external f32x8_const : (float32[@unboxed]) -> f32x8 = "caml_vec256_unreachable" "caml_float32x8_const1" [@@noalloc] [@@builtin]
external f32x8_add : f32x8 -> f32x8 -> f32x8 = "caml_vec256_unreachable" "caml_avx_float32x8_add" [@@noalloc] [@@builtin]
external f32x8_mul : f32x8 -> f32x8 -> f32x8 = "caml_vec256_unreachable" "caml_avx_float32x8_mul" [@@noalloc] [@@builtin]
external f32x8_fma : f32x8 -> f32x8 -> f32x8 -> f32x8 = "caml_vec256_unreachable" "caml_fma_float32x8_mul_add" [@@noalloc] [@@builtin]
external f32x8_lo : f32x8 -> f32x4 = "caml_vec256_unreachable" "caml_vec256_low_to_vec128" [@@noalloc] [@@builtin]
external f32x8_hi : (int[@untagged]) -> f32x8 -> f32x4 = "caml_vec256_unreachable" "caml_avx_vec256_extract_128" [@@noalloc] [@@builtin]
external f32x4_add : f32x4 -> f32x4 -> f32x4 = "caml_vec128_unreachable" "caml_sse_float32x4_add" [@@noalloc] [@@builtin]
external f32x4_hadd : f32x4 -> f32x4 -> f32x4 = "caml_vec128_unreachable" "caml_sse3_float32x4_hadd" [@@noalloc] [@@builtin]
external f32x4_low : f32x4 -> (float32[@unboxed]) = "caml_vec128_unreachable" "caml_float32x4_low_to_float32" [@@noalloc] [@@builtin]
external f64x4_of_f32x4 : f32x4 -> f64x4 = "caml_vec256_unreachable" "caml_avx_cvt_float32x4_float64x4" [@@noalloc] [@@builtin]
(* f64 *)
external f64x4_const : (float[@unboxed]) -> f64x4 = "caml_vec256_unreachable" "caml_float64x4_const1" [@@noalloc] [@@builtin]
external f64x4_add : f64x4 -> f64x4 -> f64x4 = "caml_vec256_unreachable" "caml_avx_float64x4_add" [@@noalloc] [@@builtin]
external f64x4_mul : f64x4 -> f64x4 -> f64x4 = "caml_vec256_unreachable" "caml_avx_float64x4_mul" [@@noalloc] [@@builtin]
external f64x4_lo : f64x4 -> f64x2 = "caml_vec256_unreachable" "caml_vec256_low_to_vec128" [@@noalloc] [@@builtin]
external f64x4_hi : (int[@untagged]) -> f64x4 -> f64x2 = "caml_vec256_unreachable" "caml_avx_vec256_extract_128" [@@noalloc] [@@builtin]
external f64x2_add : f64x2 -> f64x2 -> f64x2 = "caml_vec128_unreachable" "caml_sse2_float64x2_add" [@@noalloc] [@@builtin]
external f64x2_hadd : f64x2 -> f64x2 -> f64x2 = "caml_vec128_unreachable" "caml_sse3_float64x2_hadd" [@@noalloc] [@@builtin]
external f64x2_low : f64x2 -> (float[@unboxed]) = "caml_vec128_unreachable" "caml_float64x2_low_to_float" [@@noalloc] [@@builtin]
(* entiers *)
external i8x32_const : int8# -> i8x32 = "caml_vec256_unreachable" "caml_int8x32_const1" [@@noalloc] [@@builtin]
external i8x32_cmpgt : i8x32 -> i8x32 -> i8x32 = "caml_vec256_unreachable" "caml_avx2_int8x32_cmpgt" [@@noalloc] [@@builtin]
external i8x32_and : i8x32 -> i8x32 -> i8x32 = "caml_vec256_unreachable" "caml_avx_vec256_and" [@@noalloc] [@@builtin]
external i8x32_sad : i8x32 -> i8x32 -> i64x4 = "caml_vec256_unreachable" "caml_avx2_int8x32_sad_unsigned" [@@noalloc] [@@builtin]
external i32x8_const : (int32[@unboxed]) -> i32x8 = "caml_vec256_unreachable" "caml_int32x8_const1" [@@noalloc] [@@builtin]
external i32x8_add : i32x8 -> i32x8 -> i32x8 = "caml_vec256_unreachable" "caml_avx2_int32x8_add" [@@noalloc] [@@builtin]
external i32x8_sub : i32x8 -> i32x8 -> i32x8 = "caml_vec256_unreachable" "caml_avx2_int32x8_sub" [@@noalloc] [@@builtin]
external i32x8_mul : i32x8 -> i32x8 -> i32x8 = "caml_vec256_unreachable" "caml_avx2_int32x8_mul_low" [@@noalloc] [@@builtin]
external i32x8_mul_even : i32x8 -> i32x8 -> i64x4 = "caml_vec256_unreachable" "caml_avx2_int32x8_mul_even" [@@noalloc] [@@builtin]
external i32x8_cmpgt : i32x8 -> i32x8 -> i32x8 = "caml_vec256_unreachable" "caml_avx2_int32x8_cmpgt" [@@noalloc] [@@builtin]
external i32x8_cmpeq : i32x8 -> i32x8 -> i32x8 = "caml_vec256_unreachable" "caml_avx2_int32x8_cmpeq" [@@noalloc] [@@builtin]
external i32x8_and : i32x8 -> i32x8 -> i32x8 = "caml_vec256_unreachable" "caml_avx_vec256_and" [@@noalloc] [@@builtin]
external i32x8_slli : (int[@untagged]) -> i32x8 -> i32x8 = "caml_vec256_unreachable" "caml_avx2_int32x8_slli" [@@noalloc] [@@builtin]
external i32x8_dup_even : i32x8 -> i32x8 = "caml_vec256_unreachable" "caml_avx_vec256_dup_even_32" [@@noalloc] [@@builtin]
external i32x8_dup_odd : i32x8 -> i32x8 = "caml_vec256_unreachable" "caml_avx_vec256_dup_odd_32" [@@noalloc] [@@builtin]
external i32x8_lo : i32x8 -> i32x4 = "caml_vec256_unreachable" "caml_vec256_low_to_vec128" [@@noalloc] [@@builtin]
external i32x8_hi : (int[@untagged]) -> i32x8 -> i32x4 = "caml_vec256_unreachable" "caml_avx_vec256_extract_128" [@@noalloc] [@@builtin]
external i32x8_of_i8x16 : i8x16 -> i32x8 = "caml_vec256_unreachable" "caml_avx2_cvtzx_int8x16_int32x8" [@@noalloc] [@@builtin]
external i8x16_high : i8x16 -> i8x16 -> i8x16 = "caml_vec128_unreachable" "caml_sse_vec128_high_64_to_low_64" [@@noalloc] [@@builtin]
external i64x4_of_i32x4 : i32x4 -> i64x4 = "caml_vec256_unreachable" "caml_avx2_cvtsx_int32x4_int64x4" [@@noalloc] [@@builtin]
external i64x4_of_i32x8 : i32x8 -> i64x4 = "caml_vec256_unreachable" "caml_vec256_cast" [@@noalloc] [@@builtin]
external i32x8_of_i64x4 : i64x4 -> i32x8 = "caml_vec256_unreachable" "caml_vec256_cast" [@@noalloc] [@@builtin]
external i64x4_const : (int64[@unboxed]) -> i64x4 = "caml_vec256_unreachable" "caml_int64x4_const1" [@@noalloc] [@@builtin]
external i64x4_add : i64x4 -> i64x4 -> i64x4 = "caml_vec256_unreachable" "caml_avx2_int64x4_add" [@@noalloc] [@@builtin]
external i64x4_and : i64x4 -> i64x4 -> i64x4 = "caml_vec256_unreachable" "caml_avx_vec256_and" [@@noalloc] [@@builtin]
external i64x4_srli : (int[@untagged]) -> i64x4 -> i64x4 = "caml_vec256_unreachable" "caml_avx2_int64x4_srli" [@@noalloc] [@@builtin]
external i64x4_lo : i64x4 -> i64x2 = "caml_vec256_unreachable" "caml_vec256_low_to_vec128" [@@noalloc] [@@builtin]
external i64x4_hi : (int[@untagged]) -> i64x4 -> i64x2 = "caml_vec256_unreachable" "caml_avx_vec256_extract_128" [@@noalloc] [@@builtin]
external i64x2_add : i64x2 -> i64x2 -> i64x2 = "caml_vec128_unreachable" "caml_sse2_int64x2_add" [@@noalloc] [@@builtin]
external i64x2_high : i64x2 -> i64x2 -> i64x2 = "caml_vec128_unreachable" "caml_sse_vec128_high_64_to_low_64" [@@noalloc] [@@builtin]
external i64x2_low : i64x2 -> (int64[@unboxed]) = "caml_vec128_unreachable" "caml_int64x2_low_to_int64" [@@noalloc] [@@builtin]
(* préchargement en écriture de l'octet de rang donné dans un bloc *)
external prefetch_w : 'a -> (int[@untagged]) -> unit = "" "caml_prefetch_write_high_val_offset_untagged" [@@noalloc] [@@builtin]

(* sommes des voies *)
let[@inline always] hsum_f64x4 (v : f64x4) = let q = f64x2_add (f64x4_lo v) (f64x4_hi 1 v) in f64x2_low (f64x2_hadd q q)
let[@inline always] hsum_i64x4 (v : i64x4) =
  let q = i64x2_add (i64x4_lo v) (i64x4_hi 1 v) in
  Int64.to_int (i64x2_low (i64x2_add q (i64x2_high q q)))
let[@inline always] hsum_i32x8 (v : i32x8) = hsum_i64x4 (i64x4_add (i64x4_of_i32x4 (i32x8_lo v)) (i64x4_of_i32x4 (i32x8_hi 1 v)))

(* ------------------------------------------------------------------ K1 *)
let n1 = MS_N1

(* aos : enregistrements non boxés, rangés en ligne dans le tableau. Chaque champ float32_u y occupe un mot de 64 bits
   (128 octets par particule) : la disposition des blocs d'OxCaml ne compacte pas encore les champs de 32 bits. *)
type particle = #{ x : float32_u; y : float32_u; z : float32_u; vx : float32_u; vy : float32_u; vz : float32_u;
                   ax : float32_u; ay : float32_u; az : float32_u; mass : float32_u; charge : float32_u;
                   radius : float32_u; temp : float32_u; pressure : float32_u; energy : float32_u; density : float32_u }

(* calcul en f32, huit accumulateurs f64 (la forme de C) *)
let[@inline never] k1_aos (ps : particle array) =
  let[@inline always] e i =
    let p = aget ps i in
    F32.to_float (F32.mul (F32.mul #0.5s p.#mass)
                    (F32.add (F32.add (F32.mul p.#vx p.#vx) (F32.mul p.#vy p.#vy)) (F32.mul p.#vz p.#vz))) in
  let mutable a0 = #0.0 in let mutable a1 = #0.0 in let mutable a2 = #0.0 in let mutable a3 = #0.0 in
  let mutable a4 = #0.0 in let mutable a5 = #0.0 in let mutable a6 = #0.0 in let mutable a7 = #0.0 in
  let mutable i = 0 in
  while i < n1 do
    a0 <- FU.add a0 (e i); a1 <- FU.add a1 (e (i + 1)); a2 <- FU.add a2 (e (i + 2)); a3 <- FU.add a3 (e (i + 3));
    a4 <- FU.add a4 (e (i + 4)); a5 <- FU.add a5 (e (i + 5)); a6 <- FU.add a6 (e (i + 6)); a7 <- FU.add a7 (e (i + 7));
    i <- i + 8
  done;
  FU.to_float (FU.add (FU.add (FU.add a0 a1) (FU.add a2 a3)) (FU.add (FU.add a4 a5) (FU.add a6 a7)))

(* soa : colonnes float32_u array (4 octets par élément), vecteurs de 8 f32, énergie en f32 avec FMA, élargie en f64
   pour l'accumulation (quatre accumulateurs de 4 f64, 16 particules par tour : la forme de C en deux fois moins large) *)
let[@inline never] k1_soa (vx : float32_u array) (vy : float32_u array) (vz : float32_u array) (m : float32_u array) =
  let h = f32x8_const 0.5s in
  let mutable a0 = f64x4_const 0.0 in let mutable a1 = f64x4_const 0.0 in
  let mutable a2 = f64x4_const 0.0 in let mutable a3 = f64x4_const 0.0 in
  let[@inline always] e j =
    let x = f32a_x8 vx j and y = f32a_x8 vy j and z = f32a_x8 vz j in
    f32x8_mul (f32x8_mul h (f32a_x8 m j)) (f32x8_fma z z (f32x8_fma y y (f32x8_mul x x))) in
  let mutable i = 0 in
  while i < n1 do
    let e0 = e i and e1 = e (i + 8) in
    a0 <- f64x4_add a0 (f64x4_of_f32x4 (f32x8_lo e0)); a1 <- f64x4_add a1 (f64x4_of_f32x4 (f32x8_hi 1 e0));
    a2 <- f64x4_add a2 (f64x4_of_f32x4 (f32x8_lo e1)); a3 <- f64x4_add a3 (f64x4_of_f32x4 (f32x8_hi 1 e1));
    i <- i + 16
  done;
  hsum_f64x4 (f64x4_add (f64x4_add a0 a1) (f64x4_add a2 a3))

let run_k1 v reps =
  let raw = map float32 "k1_particles.f32" in
  let f6 x = Printf.sprintf "%.6f" x in
  let g i k = F32.of_float (FU.of_float (Array1.unsafe_get raw ((16 * i) + k))) in
  if v = "aos" then begin
    Printf.printf "META;aos_repr;tableau d'enregistrements non boxés, 16 champs float32_u de 8 octets (128 octets par particule)\n";
    let z = #0.0s in
    let ps = amake n1 #{ x = z; y = z; z; vx = z; vy = z; vz = z; ax = z; ay = z; az = z; mass = z; charge = z;
                         radius = z; temp = z; pressure = z; energy = z; density = z } in
    for i = 0 to n1 - 1 do
      aset ps i #{ x = g i 0; y = g i 1; z = g i 2; vx = g i 3; vy = g i 4; vz = g i 5; ax = g i 6; ay = g i 7;
                   az = g i 8; mass = g i 9; charge = g i 10; radius = g i 11; temp = g i 12; pressure = g i 13;
                   energy = g i 14; density = g i 15 }
    done;
    bench "k1" v "energy" reps (fun () -> f6 (k1_aos ps))
  end else begin
    let col k = let c = amake n1 #0.0s in for i = 0 to n1 - 1 do aset c i (g i k) done; c in
    let vx = col 3 and vy = col 4 and vz = col 5 and m = col 9 in
    bench "k1" v "energy" reps (fun () -> f6 (k1_soa vx vy vz m))
  end

(* ------------------------------------------------------------------ K4 *)
(* tuned (docs/METHOD.md, 4 : SIMD explicite) : 32 octets par tour. Un octet >= 128 est négatif en entier signé :
   0 > x donne le masque, les octets hors masque sont mis à zéro, vpsadbw additionne chaque groupe de 8 octets en un
   entier de 64 bits (au plus 8 × 255 par tour : l'accumulateur de 64 bits tient pour toute taille). *)
let[@inline never] k4_tuned (v : Bytes.t) =
  let n = Bytes.length v in
  let zero = i8x32_const #0s in
  let mutable acc = i64x4_const 0L in
  let mutable i = 0 in
  while i + 32 <= n do
    let x = bytes_i8x32 v i in
    acc <- i64x4_add acc (i8x32_sad (i8x32_and x (i8x32_cmpgt zero x)) zero);
    i <- i + 32
  done;
  let mutable s = hsum_i64x4 acc in
  while i < n do
    let x = Char.code (Bytes.unsafe_get v i) in
    if x >= 128 then s <- s + x;
    i <- i + 1
  done;
  s

let run_k4 v reps =
  let ic = open_in_bin (Filename.concat data_dir "k4_bytes.u8") in
  let d = Bytes.create (in_channel_length ic) in
  really_input ic d 0 (Bytes.length d);
  close_in ic;
  bench "k4" v "16M" reps (fun () -> string_of_int (k4_tuned d))

(* ------------------------------------------------------------------ K5 *)
let inner5 = MS_INNER5

(* tuned_v (docs/METHOD.md, 4) : 64 éléments par tour, en huit vecteurs de 8 f32 (pas de vecteurs de 16 f32 dans cette
   version), huit accumulateurs, FMA ; réduction dans les registres. Les tailles de K5 sont des multiples de 64. *)
let[@inline never] k5_tuned_v (a : bigstring) (b : bigstring) =
  let n = Array1.dim a in
  let mutable s0 = f32x8_const 0.0s in let mutable s1 = f32x8_const 0.0s in
  let mutable s2 = f32x8_const 0.0s in let mutable s3 = f32x8_const 0.0s in
  let mutable s4 = f32x8_const 0.0s in let mutable s5 = f32x8_const 0.0s in
  let mutable s6 = f32x8_const 0.0s in let mutable s7 = f32x8_const 0.0s in
  let mutable i = 0 in
  while i < n do
    s0 <- f32x8_fma (bs_f32x8 a i) (bs_f32x8 b i) s0;
    s1 <- f32x8_fma (bs_f32x8 a (i + 32)) (bs_f32x8 b (i + 32)) s1;
    s2 <- f32x8_fma (bs_f32x8 a (i + 64)) (bs_f32x8 b (i + 64)) s2;
    s3 <- f32x8_fma (bs_f32x8 a (i + 96)) (bs_f32x8 b (i + 96)) s3;
    s4 <- f32x8_fma (bs_f32x8 a (i + 128)) (bs_f32x8 b (i + 128)) s4;
    s5 <- f32x8_fma (bs_f32x8 a (i + 160)) (bs_f32x8 b (i + 160)) s5;
    s6 <- f32x8_fma (bs_f32x8 a (i + 192)) (bs_f32x8 b (i + 192)) s6;
    s7 <- f32x8_fma (bs_f32x8 a (i + 224)) (bs_f32x8 b (i + 224)) s7;
    i <- i + 256
  done;
  let s = f32x8_add (f32x8_add (f32x8_add s0 s1) (f32x8_add s2 s3)) (f32x8_add (f32x8_add s4 s5) (f32x8_add s6 s7)) in
  let q = f32x4_add (f32x8_lo s) (f32x8_hi 1 s) in
  let q = f32x4_hadd q q in
  f32x4_low (f32x4_hadd q q)

let run_k5 v reps =
  let a = map_bytes "k5_a.f32" and b = map_bytes "k5_b.f32" in
  let r = ref a in
  bench "k5" v "2048x65536" reps (fun () ->
    let d = ref 0.0s in
    for _ = 1 to inner5 do d := k5_tuned_v (Sys.opaque_identity !r) b done;
    Printf.sprintf "%.4f" (Stdlib_stable.Float32.to_float !d))

(* ------------------------------------------------------------------ réserve de domaines (celle de ms.ml) *)
type barrier = { bm : Mutex.t; bc : Condition.t; mutable bcount : int; mutable bgen : int; bn : int }

let barrier n = { bm = Mutex.create (); bc = Condition.create (); bcount = 0; bgen = 0; bn = n }

let barrier_wait b =
  Mutex.lock b.bm;
  let g = b.bgen in
  b.bcount <- b.bcount + 1;
  if b.bcount = b.bn then begin
    b.bcount <- 0;
    b.bgen <- b.bgen + 1;
    Condition.broadcast b.bc
  end else
    while b.bgen = g do Condition.wait b.bc b.bm done;
  Mutex.unlock b.bm

type pool = { pgo : barrier; pfin : barrier; mutable pjob : int -> unit; mutable pquit : bool; mutable pdoms : unit Domain.t list }

let pool = { pgo = barrier 4; pfin = barrier 4; pjob = (fun _ -> ()); pquit = false; pdoms = [] }

let pool_start () =
  pool.pquit <- false;
  pool.pdoms <- List.init 3 (fun t ->
    Domain.spawn (fun () ->
      let rec loop () =
        barrier_wait pool.pgo;
        if not pool.pquit then begin
          pool.pjob (t + 1);
          barrier_wait pool.pfin;
          loop ()
        end
      in
      loop ()))

let pool_run job =
  pool.pjob <- job;
  barrier_wait pool.pgo;
  job 0;
  barrier_wait pool.pfin

let pool_stop () =
  pool.pquit <- true;
  barrier_wait pool.pgo;
  List.iter Domain.join pool.pdoms

(* ------------------------------------------------------------------ K6 *)
let n6 = MS_N6

(* colonnes : les fichiers projetés, vus comme des suites d'octets (i32 : 4 octets par ligne ; u8 : 1) *)
type cols = { sd : bigstring; pr : bigstring; q : bigstring; d : bigstring; t : bigstring; rf : bigstring; ls : bigstring }
external bs_i32 : bigstring -> int -> int32 = "%caml_bigstring_get32u"
let[@inline always] i32 (c : bigstring) i = Int32.to_int (bs_i32 c (4 * i))
let[@inline always] u8 (c : bigstring) i = Char.code (Array1.unsafe_get c i)

(* reste éventuel (moins de 16 lignes) : les boucles naturelles *)
let q6_rest c lo hi =
  let s = ref 0 in
  for i = lo to hi - 1 do
    let sd = i32 c.sd i and d = u8 c.d i in
    if sd >= 8766 && sd < 9131 && d >= 5 && d <= 7 && u8 c.q i < 24 then s := !s + (i32 c.pr i * d)
  done;
  !s

let q1_rest c lo hi (acc : int array) =
  for i = lo to hi - 1 do
    if i32 c.sd i <= 10471 then begin
      let g = ((u8 c.rf i * 2) + u8 c.ls i) * 5 and p = i32 c.pr i in
      let dp = p * (100 - u8 c.d i) in
      acc.(g) <- acc.(g) + 1; acc.(g + 1) <- acc.(g + 1) + u8 c.q i; acc.(g + 2) <- acc.(g + 2) + p;
      acc.(g + 3) <- acc.(g + 3) + dp; acc.(g + 4) <- acc.(g + 4) + (dp * (100 + u8 c.t i))
    end
  done

(* les 8 octets de poids fort d'un vecteur de 16, élargis en 8 i32 *)
let[@inline always] hi8 (v : i8x16) = i32x8_of_i8x16 (i8x16_high v v)

(* Q6 tuned_v (docs/METHOD.md, 4) : blocs de 16 lignes, en deux vecteurs de 8 i32 (pas de vecteurs de 16 i32 dans
   cette version) : colonnes d'octets élargies en i32, prédicat par comparaisons (masques de voies), produit prix ×
   remise en i32, voies hors prédicat mises à zéro. Exactitude pour toute donnée de la spécification (docs/SPEC.md,
   K6) : prix <= 50 000 et remise <= 10, donc produit <= 500 000 ; les accumulateurs i32 sont vidés tous les 2048
   lignes au plus (128 tours : une voie reçoit au plus 128 × 500 000 < 2^31) dans une somme de 63 bits. *)
let[@inline never] q6_tuned_v c lo hi =
  let k8765 = i32x8_const 8765l in let k9131 = i32x8_const 9131l in let k4 = i32x8_const 4l in
  let k8 = i32x8_const 8l in let k24 = i32x8_const 24l in
  let[@inline always] term sd pr d q =
    let m = i32x8_and (i32x8_and (i32x8_cmpgt sd k8765) (i32x8_cmpgt k9131 sd))
              (i32x8_and (i32x8_and (i32x8_cmpgt d k4) (i32x8_cmpgt k8 d)) (i32x8_cmpgt k24 q)) in
    i32x8_and m (i32x8_mul pr d) in
  let mutable total = 0 in
  let mutable i = lo in
  while i + 16 <= hi do
    let stop = min (i + 2048) (hi - ((hi - i) land 15)) in
    let mutable a0 = i32x8_const 0l in
    let mutable a1 = i32x8_const 0l in
    while i < stop do
      let db = bs_i8x16 c.d i and qb = bs_i8x16 c.q i in
      a0 <- i32x8_add a0 (term (bs_i32x8 c.sd (4 * i)) (bs_i32x8 c.pr (4 * i)) (i32x8_of_i8x16 db) (i32x8_of_i8x16 qb));
      a1 <- i32x8_add a1 (term (bs_i32x8 c.sd ((4 * i) + 32)) (bs_i32x8 c.pr ((4 * i) + 32)) (hi8 db) (hi8 qb));
      i <- i + 16
    done;
    total <- total + hsum_i32x8 a0 + hsum_i32x8 a1
  done;
  total + q6_rest c i hi

(* Q1 tuned_v (docs/METHOD.md, 4 ; la forme de C en deux fois moins large) : 16 lignes par tour en deux vecteurs de
   8 i32, additions masquées par groupe (six groupes). Compte, quantité, prix et prix remisé en voies de 32 bits,
   vidées tous les 2048 lignes au plus (256 additions par voie ; prix remisé <= 50 000 × 100 = 5 000 000, donc au plus
   1,28e9 < 2^31) ; produits de la colonne charge en 64 bits (vpmuldq sur les lignes paires, puis impaires), ajoutés à
   des voies de 64 bits. Les accumulateurs sont des tableaux de vecteurs, un par groupe. *)
type q1acc = { cnt : i32x8 array; aq : i32x8 array; ap : i32x8 array; adp : i32x8 array; ace : i64x4 array; aco : i64x4 array }

let q1acc () =
  let z = i32x8_const 0l and z64 = i64x4_const 0L in
  { cnt = amake 6 z; aq = amake 6 z; ap = amake 6 z; adp = amake 6 z; ace = amake 6 z64; aco = amake 6 z64 }

let[@inline never] q1_tuned_v c lo hi (acc : int array) =
  let a = q1acc () in
  let k10472 = i32x8_const 10472l in let k100 = i32x8_const 100l in
  let z = i32x8_const 0l in let z64 = i64x4_const 0L in
  let[@inline always] row8 sd pr q d t rf ls =
    let pass = i32x8_cmpgt k10472 sd in
    let vg = i32x8_add (i32x8_slli 1 rf) ls in
    let dp = i32x8_mul pr (i32x8_sub k100 d) in
    let t100 = i32x8_add t k100 in
    let che = i32x8_mul_even dp t100 in
    let cho = i32x8_mul_even (i32x8_of_i64x4 (i64x4_srli 32 (i64x4_of_i32x8 dp))) (i32x8_of_i64x4 (i64x4_srli 32 (i64x4_of_i32x8 t100))) in
    let[@inline always] grp g kg =
      let m = i32x8_and pass (i32x8_cmpeq vg kg) in
      aset a.cnt g (i32x8_sub (aget a.cnt g) m);
      aset a.aq g (i32x8_add (aget a.aq g) (i32x8_and m q));
      aset a.ap g (i32x8_add (aget a.ap g) (i32x8_and m pr));
      aset a.adp g (i32x8_add (aget a.adp g) (i32x8_and m dp));
      aset a.ace g (i64x4_add (aget a.ace g) (i64x4_and (i64x4_of_i32x8 (i32x8_dup_even m)) che));
      aset a.aco g (i64x4_add (aget a.aco g) (i64x4_and (i64x4_of_i32x8 (i32x8_dup_odd m)) cho)) in
    grp 0 z; grp 1 (i32x8_const 1l); grp 2 (i32x8_const 2l); grp 3 (i32x8_const 3l); grp 4 (i32x8_const 4l);
    grp 5 (i32x8_const 5l) in
  let mutable i = lo in
  while i + 16 <= hi do
    let stop = min (i + 2048) (hi - ((hi - i) land 15)) in
    while i < stop do
      let qb = bs_i8x16 c.q i and db = bs_i8x16 c.d i and tb = bs_i8x16 c.t i and rb = bs_i8x16 c.rf i
      and lb = bs_i8x16 c.ls i in
      row8 (bs_i32x8 c.sd (4 * i)) (bs_i32x8 c.pr (4 * i)) (i32x8_of_i8x16 qb) (i32x8_of_i8x16 db) (i32x8_of_i8x16 tb)
        (i32x8_of_i8x16 rb) (i32x8_of_i8x16 lb);
      row8 (bs_i32x8 c.sd ((4 * i) + 32)) (bs_i32x8 c.pr ((4 * i) + 32)) (hi8 qb) (hi8 db) (hi8 tb) (hi8 rb) (hi8 lb);
      i <- i + 16
    done;
    for g = 0 to 5 do
      acc.(5 * g) <- acc.(5 * g) + hsum_i32x8 (aget a.cnt g);
      acc.((5 * g) + 1) <- acc.((5 * g) + 1) + hsum_i32x8 (aget a.aq g);
      acc.((5 * g) + 2) <- acc.((5 * g) + 2) + hsum_i32x8 (aget a.ap g);
      acc.((5 * g) + 3) <- acc.((5 * g) + 3) + hsum_i32x8 (aget a.adp g);
      acc.((5 * g) + 4) <- acc.((5 * g) + 4) + hsum_i64x4 (aget a.ace g) + hsum_i64x4 (aget a.aco g);
      aset a.cnt g z; aset a.aq g z; aset a.ap g z; aset a.adp g z; aset a.ace g z64; aset a.aco g z64
    done
  done;
  q1_rest c i hi acc

let run_k6 v reps p =
  let c = { sd = map_bytes "k6_shipdate.i32"; pr = map_bytes "k6_extendedprice.i32"; q = map_bytes "k6_quantity.u8";
            d = map_bytes "k6_discount.u8"; t = map_bytes "k6_tax.u8"; rf = map_bytes "k6_returnflag.u8";
            ls = map_bytes "k6_linestatus.u8" } in
  let q1 = p = "q1" in
  let one lo hi = if q1 then (let a = Array.make 30 0 in q1_tuned_v c lo hi a; Array.fold_left ( + ) 0 a) else q6_tuned_v c lo hi in
  let pl = v = "mt_pool_v" in
  if pl then pool_start ();
  bench "k6" v p reps (fun () ->
    string_of_int
      (if pl then begin
         let part = Array.make 4 0 in
         pool_run (fun t -> part.(t) <- one (n6 * t / 4) (n6 * (t + 1) / 4));
         Array.fold_left ( + ) 0 part
       end else one 0 n6));
  if pl then pool_stop ()

(* ------------------------------------------------------------------ K7 *)
(* tuned_pf (docs/METHOD.md, 4) : la table de tuned_oa (ms.ml : cases de 16 octets, clé et compteur de 30 bits dans un
   mot, somme dans l'autre, hachage de Fibonacci, sondage linéaire), par lots de 16 clés dont les cases sont
   préchargées en écriture avant d'être traitées. Exactitude : le compteur tient en 30 bits tant que n < 2^30 (vérifié
   avant la zone chronométrée). *)
let run_k7 v reps =
  let keys = map int32 "k7_keys.u32" and vals = map int32 "k7_vals.u32" in
  let n = Array1.dim keys in
  let key i = Int32.to_int (Array1.unsafe_get keys i) land 0xFFFFFFFF in
  let logc = MS_K7_LOG in
  let cap = 1 lsl logc and cmask = (1 lsl 30) - 1 in
  if n >= 1 lsl 30 then failwith "K7 tuned_pf : compteur de 30 bits";
  let hs = Array.make 16 0 in
  for r = -warmup to reps - 1 do
    let t0 = now () in
    let tab = Array.make (2 * cap) 0 in
    let put k s0 x =
      let s = ref s0 in
      while (let p = Array.unsafe_get tab (2 * !s) in p land cmask <> 0 && p lsr 30 <> k) do s := (!s + 1) land (cap - 1) done;
      let b = 2 * !s in
      Array.unsafe_set tab b ((k lsl 30) lor ((Array.unsafe_get tab b land cmask) + 1));
      Array.unsafe_set tab (b + 1) (Array.unsafe_get tab (b + 1) + x) in
    let slot k = ((k * 0x9E3779B1) land 0xFFFFFFFF) lsr (32 - logc) in
    let i = ref 0 in
    while !i + 16 <= n do
      for b = 0 to 15 do
        let s = slot (key (!i + b)) in
        Array.unsafe_set hs b s;
        prefetch_w tab (16 * s)
      done;
      for b = 0 to 15 do put (key (!i + b)) (Array.unsafe_get hs b) (Int32.to_int (Array1.unsafe_get vals (!i + b))) done;
      i := !i + 16
    done;
    while !i < n do
      let k = key !i in
      put k (slot k) (Int32.to_int (Array1.unsafe_get vals !i));
      incr i
    done;
    let dt = now () -. t0 in
    let nk = ref 0 and ws = ref 0 in
    for s = 0 to cap - 1 do
      let p = tab.(2 * s) in
      if p land cmask <> 0 then (incr nk; ws := !ws + (tab.((2 * s) + 1) * (((p lsr 30) land 1023) + 1)))
    done;
    if r >= 0 then result "k7" v "16M/1M" r dt (Printf.sprintf "%d:%d" !nk !ws)
  done

(* ------------------------------------------------------------------ K8 *)
type tree = Leaf | Node of int * tree * tree

(* arbre de longue durée : sur le tas, comme dans ms.ml *)
let rec t_build d c = if d = 0 then (Node (!c, Leaf, Leaf) |> fun n -> incr c; n) else begin
    let v = !c in incr c;
    let l = t_build (d - 1) c in
    let r = t_build (d - 1) c in
    Node (v, l, r) end

let rec t_sum = function Leaf -> 0 | Node (v, l, r) -> v + t_sum l + t_sum r

(* tuned_alloc : les nœuds de la variante naturelle (même type, mêmes valeurs, même ordre préfixe), alloués dans la
   région locale de la requête : exclave_ place chaque nœud dans la région de l'appelant, donc tous dans celle de
   request ; la région est libérée en bloc à son retour, sans ramasse-miettes. *)
let rec l_build d (c : int ref @ local) : tree @ local =
  let v = !c in
  incr c;
  if d = 0 then exclave_ Node (v, Leaf, Leaf)
  else exclave_ (
    let l = l_build (d - 1) c in
    let r = l_build (d - 1) c in
    Node (v, l, r))

let rec l_sum (t : tree @ local) = match t with Leaf -> 0 | Node (v, l, r) -> v + l_sum l + l_sum r

let[@inline never] request qq = let c = stack_ (ref qq) in l_sum (l_build MS_K8_REQ c) [@nontail]

let run_k8 v reps =
  let q = 16384 in
  let keep = t_build MS_K8_LONG (ref 0) in
  let lsum = t_sum keep in
  let lat = Array.make q 0.0 in
  for r = -warmup to reps - 1 do
    let total = ref 0 in
    let t0 = now () in
    for qq = 0 to q - 1 do
      let a = now () in
      total := !total + request qq;
      lat.(qq) <- (now () -. a) *. 1e9
    done;
    let dt = now () -. t0 in
    if r >= 0 then begin
      result "k8" v "16384x2047" r dt (string_of_int (!total + lsum));
      Array.sort compare lat;
      Printf.printf "LAT;%s;%.0f;%.0f;%.0f;%.0f;%.0f\n%!" v lat.(q / 2) lat.(q * 9 / 10) lat.(q * 99 / 100) lat.(q * 999 / 1000) lat.(q - 1)
    end
  done;
  ignore (Sys.opaque_identity keep)

(* ------------------------------------------------------------------ K9 *)
let m9 = MS_M9
let k9_init i j = float_of_int (((i * 31) + (j * 17)) mod 1024) /. 1024.0

(* tuned_v (docs/METHOD.md, 4) : par ligne, 8 f64 par tour en deux vecteurs de 4 (pas de vecteurs de 8 f64 dans cette
   version) : haut, bas, gauche et droite chargés en vecteurs, même ordre des additions que la spécification, résultat
   écrit en vecteur, reste scalaire. Grilles : float# array (flottants à plat, dans le tas : chargements non alignés) ;
   la boucle part de j = 1, comme la forme de C. *)
let[@inline never] k9_rows_v (a : float# array) (b : float# array) r0 r1 =
  let q = f64x4_const 0.25 in
  let[@inline always] cell k = f64x4_mul q (f64x4_add (f64x4_add (f64x4_add (fa_x4 a (k - m9)) (fa_x4 a (k + m9))) (fa_x4 a (k - 1))) (fa_x4 a (k + 1))) in
  for i = r0 to r1 - 1 do
    let mid = i * m9 in
    let mutable j = 1 in
    while j + 8 <= m9 - 1 do
      fa_set_x4 b (mid + j) (cell (mid + j));
      fa_set_x4 b (mid + j + 4) (cell (mid + j + 4));
      j <- j + 8
    done;
    while j < m9 - 1 do
      let k = mid + j in
      aset b k (FU.mul #0.25 (FU.add (FU.add (FU.add (aget a (k - m9)) (aget a (k + m9))) (aget a (k - 1))) (aget a (k + 1))));
      j <- j + 1
    done
  done

let run_k9 v reps =
  let a = amake (m9 * m9) #0.0 and b = amake (m9 * m9) #0.0 in
  let pl = v = "mt_pool_v" in
  if pl then pool_start ();
  let step x y =
    if pl then pool_run (fun t -> k9_rows_v x y (1 + ((m9 - 2) * t / 4)) (1 + ((m9 - 2) * (t + 1) / 4)))
    else k9_rows_v x y 1 (m9 - 1) in
  for r = -warmup to reps - 1 do
    for k = 0 to (m9 * m9) - 1 do let x = FU.of_float (k9_init (k / m9) (k mod m9)) in aset a k x; aset b k x done;
    let t0 = now () in
    step a b; step b a; step a b; step b a;
    let dt = now () -. t0 in
    let s = ref 0.0 in
    for k = 0 to (m9 * m9) - 1 do s := !s +. FU.to_float (aget a k) done;
    if r >= 0 then result "k9" v "2048^2x4" r dt (Printf.sprintf "%.15e" !s)
  done;
  if pl then pool_stop ()

let () =
  let k = Sys.argv.(1) and v = Sys.argv.(2) and reps = int_of_string Sys.argv.(3) in
  let p = if Array.length Sys.argv > 4 then Sys.argv.(4) else "" in
  match k, v with
  | "k1", ("aos" | "soa") -> run_k1 v reps
  | "k4", "tuned" -> run_k4 v reps
  | "k5", "tuned_v" -> run_k5 v reps
  | "k6", ("tuned_v" | "mt_pool_v") -> run_k6 v reps p
  | "k7", "tuned_pf" -> run_k7 v reps
  | "k8", "tuned_alloc" -> run_k8 v reps
  | "k9", ("tuned_v" | "mt_pool_v") -> run_k9 v reps
  | _ -> prerr_endline ("ox : variante inconnue " ^ k ^ " " ^ v); exit 2
