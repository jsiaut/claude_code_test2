(* Implémentation OCaml 5.5.2 + flambda (bibliothèque standard + unix). Voir docs/SPEC.md. *)
open Bigarray

(* ------------------------------------------------------------------ harnais *)
let data_dir = try Sys.getenv "MS_DATA" with Not_found -> "/opt/msdata"
let warmup = try int_of_string (Sys.getenv "WARMUP") with Not_found -> 1

(* projection mémoire du fichier (mmap) : tableau Bigarray sans copie *)
let map kind name =
  let fd = Unix.openfile (Filename.concat data_dir name) [ Unix.O_RDONLY ] 0 in
  let a = array1_of_genarray (Unix.map_file fd kind c_layout false [| -1 |]) in
  Unix.close fd;
  a

let result k v p rep sec chk = Printf.printf "RESULT;%s;%s;%s;%d;%.9f;%s\n%!" k v p rep sec chk
(* remarque sur OCaml (docs/OCAML.md) : horloge monotone à la nanoseconde de la distribution, depuis OCaml 5.4 *)
let now () = Int64.to_float (Runtime_events.Timestamp.to_int64 (Runtime_events.Timestamp.get_current ())) *. 1e-9

let bench k v p reps f =
  for r = -warmup to reps - 1 do
    let t0 = now () in
    let chk = f () in
    let dt = now () -. t0 in
    if r >= 0 then result k v p r dt chk
  done

(* ------------------------------------------------------------------ K1 *)
let n1 = MS_N1

(* enregistrement uniquement flottant : OCaml le stocke « à plat » (16 doubles), mais un
   tableau d'enregistrements reste un tableau de pointeurs *)
type particle = { x : float; y : float; z : float; vx : float; vy : float; vz : float; ax : float; ay : float; az : float;
                  mass : float; charge : float; radius : float; temp : float; pressure : float; energy : float; density : float }

let[@inline never] k1_natural (ps : particle array) =
  let e = ref 0.0 in
  Array.iter (fun p -> e := !e +. (0.5 *. p.mass *. ((p.vx *. p.vx) +. (p.vy *. p.vy) +. (p.vz *. p.vz)))) ps;
  !e

(* AoS manuel : Bigarray float32 entrelacé (pas de 16), 4 accumulateurs *)
let[@inline never] k1_aos (f : (float, float32_elt, c_layout) Array1.t) =
  let a0 = ref 0.0 and a1 = ref 0.0 and a2 = ref 0.0 and a3 = ref 0.0 in
  (* remarque sur OCaml (docs/OCAML.md) : x *. x, pas pow de la libm *)
  let e i = let x = Array1.unsafe_get f (i + 3) and y = Array1.unsafe_get f (i + 4) and z = Array1.unsafe_get f (i + 5) in
    0.5 *. Array1.unsafe_get f (i + 9) *. ((x *. x) +. (y *. y) +. (z *. z)) in
  let i = ref 0 in
  while !i < n1 * 16 do
    a0 := !a0 +. e !i; a1 := !a1 +. e (!i + 16); a2 := !a2 +. e (!i + 32); a3 := !a3 +. e (!i + 48);
    i := !i + 64
  done;
  !a0 +. !a1 +. !a2 +. !a3

(* SoA : colonnes Bigarray float32 (pas de SIMD dans OCaml : 4 accumulateurs) *)
type f32 = (float, float32_elt, c_layout) Array1.t

(* les accès Bigarray ne sont compilés en ligne que si kind et layout sont connus statiquement *)
let[@inline never] k1_soa (vx : f32) (vy : f32) (vz : f32) (m : f32) =
  let a0 = ref 0.0 and a1 = ref 0.0 and a2 = ref 0.0 and a3 = ref 0.0 in
  let e i =
    let x = Array1.unsafe_get vx i and y = Array1.unsafe_get vy i and z = Array1.unsafe_get vz i in
    0.5 *. Array1.unsafe_get m i *. ((x *. x) +. (y *. y) +. (z *. z))
  in
  let i = ref 0 in
  while !i < n1 do
    a0 := !a0 +. e !i; a1 := !a1 +. e (!i + 1); a2 := !a2 +. e (!i + 2); a3 := !a3 +. e (!i + 3);
    i := !i + 4
  done;
  !a0 +. !a1 +. !a2 +. !a3

(* Empreinte K1 (D2a) : octets vivants du tas après GC complet, et RSS courant (pages de 4 Kio) *)
let live_now () = Gc.full_major (); (Gc.stat ()).Gc.live_words * (Sys.word_size / 8)
let rss_now () =
  try
    let ic = open_in "/proc/self/statm" in
    let l = input_line ic in
    close_in ic;
    int_of_string (List.nth (String.split_on_char ' ' l) 1) * 4096
  with _ -> 0

let run_k1 v reps =
  if v = "footprint0" then result "k1" v "energy" 0 0. "0"
  else begin
    let raw = map float32 "k1_particles.f32" in
    let f6 x = Printf.sprintf "%.6f" x in
    match v with
    | "footprint_raw" -> (let s = ref 0. in for i = 0 to Bigarray.Array1.dim raw - 1 do s := !s +. raw.{i} done;
                          result "k1" v "energy" 0 0. (if !s = 0. then "0" else "0"))
    | "aos" -> bench "k1" v "energy" reps (fun () -> f6 (k1_aos raw))
    | "soa" ->
        let col k = let c = Array1.create float32 c_layout n1 in for i = 0 to n1 - 1 do Array1.unsafe_set c i (Array1.unsafe_get raw ((16 * i) + k)) done; c in
        let vx = col 3 and vy = col 4 and vz = col 5 and m = col 9 in
        bench "k1" v "energy" reps (fun () -> f6 (k1_soa vx vy vz m))
    | _ ->
        let g i k = Array1.get raw ((16 * i) + k) in
        let m1, r1 = if v = "footprint" then (live_now (), rss_now ()) else (0, 0) in (* P1 : tampon brut chargé *)
        let ps = Array.init n1 (fun i ->
          { x = g i 0; y = g i 1; z = g i 2; vx = g i 3; vy = g i 4; vz = g i 5; ax = g i 6; ay = g i 7; az = g i 8;
            mass = g i 9; charge = g i 10; radius = g i 11; temp = g i 12; pressure = g i 13; energy = g i 14; density = g i 15 }) in
        if v = "footprint" then begin
          let m2 = live_now () in (* P2 : collection construite, tampon brut encore vivant *)
          let r2 = rss_now () in
          Printf.printf "META;mem;live;%d;%d\nMETA;rss;%d;%d\nMETA;raw0;%g\n%!" m1 m2 r1 r2 (Array1.get raw 0);
          result "k1" v "energy" 0 0. (f6 (k1_natural ps))
        end
        else begin
          let ps =
            if v = "natural_shuffled" then begin
              let perm = map int32 "k1_perm.u32" in
              let s = Array.init n1 (fun j -> ps.(Int32.to_int (Array1.get perm j))) in
              Gc.compact (); s
            end else ps
          in
          bench "k1" v "energy" reps (fun () -> f6 (k1_natural ps))
        end
  end

(* ------------------------------------------------------------------ K2 *)
let[@inline never] k2_chase (a : (int32, int32_elt, c_layout) Array1.t) h =
  let i = ref 0 in
  for _ = 1 to h do i := Int32.to_int (Array1.unsafe_get a !i) done;
  !i

let run_k2 v reps p =
  let a = map int32 ("k2_chase_" ^ p ^ ".u32") in
  bench "k2" v p reps (fun () -> string_of_int (k2_chase a 4200000))

(* ------------------------------------------------------------------ K3 *)
let iter3 = 1 lsl 25

let run_k3 v reps =
  let rmw = String.sub v 0 3 = "rmw" and padded = Filename.check_suffix v "padded" in
  Printf.printf "META;k3_mechanism;%s\n" (if rmw then "Atomic.fetch_and_add (lock xadd)" else "Atomic.get + Atomic.set (set = xchg séquentiellement cohérent ; OCaml n'a pas d'ordre relaxed)");
  bench "k3" v "4x2^25" reps (fun () ->
    (* Atomic.make_contended place chaque atomique sur sa propre ligne de cache *)
    let ctr = Array.init 4 (fun _ -> if padded then Atomic.make_contended 0 else Atomic.make 0) in
    let work c () =
      if rmw then for _ = 1 to iter3 do ignore (Atomic.fetch_and_add c 1) done
      else for _ = 1 to iter3 do Atomic.set c (Atomic.get c + 1) done
    in
    let ds = Array.map (fun c -> Domain.spawn (work c)) ctr in
    Array.iter Domain.join ds;
    string_of_int (Array.fold_left (fun s c -> s + Atomic.get c) 0 ctr))

(* ------------------------------------------------------------------ K4 *)
let[@inline never] k4_natural (v : Bytes.t) =
  let s = ref 0 in
  for i = 0 to Bytes.length v - 1 do
    let x = Char.code (Bytes.unsafe_get v i) in
    if x >= 128 then s := !s + x
  done;
  !s

let[@inline never] k4_branchless (v : Bytes.t) =
  let s = ref 0 in
  for i = 0 to Bytes.length v - 1 do
    let x = Char.code (Bytes.unsafe_get v i) in
    s := !s + (x * (x lsr 7))
  done;
  !s

(* v4, point 3 (docs/V4_EQUAL.md, R3) : variante tuned. OCaml n'a pas de SIMD explicite : la meilleure forme trouvée,
   huit octets par mot de 64 bits (Bytes.get_int64_le, calcul en Int64 que flambda garde hors du tas) : masque des
   octets >= 128 par leur bit de poids fort, sommes par paires d'octets puis par multiplication (5 ms, contre 21 pour la
   forme sans branchement et 12 pour celle-ci déroulée par quatre). *)
let[@inline never] k4_tuned (v : Bytes.t) =
  let n = Bytes.length v in
  let ones = 0x0101010101010101L and lo = 0x00FF00FF00FF00FFL and mul = 0x0001000100010001L in
  let s = ref 0 in
  let i = ref 0 in
  while !i + 8 <= n do
    let w = Bytes.get_int64_le v !i in
    let m = Int64.logand (Int64.shift_right_logical w 7) ones in
    let y = Int64.logand w (Int64.mul m 0xFFL) in
    let p = Int64.add (Int64.logand y lo) (Int64.logand (Int64.shift_right_logical y 8) lo) in
    s := !s + Int64.to_int (Int64.shift_right_logical (Int64.mul p mul) 48);
    i := !i + 8
  done;
  while !i < n do
    let x = Char.code (Bytes.unsafe_get v !i) in
    if x >= 128 then s := !s + x;
    incr i
  done;
  !s

(* v4, point 4 (docs/V4_CONVERGE.md, 3.3, swar) : huit octets par mot de 64 bits (Bytes.get_int64_le), voies de 16
   bits en Int64 (le int de 63 bits ne tient pas quatre voies de 16 bits ; flambda garde les Int64 locaux hors du tas).
   Par mot w : m = (w lsr 7) land 0x0101…01 (le bit de poids fort de chaque octet), y = w land (m * 0xFF) (octets >= 128
   gardés, les autres à zéro), puis les octets de rang pair et impair ajoutés en quatre voies de 16 bits. Exactitude :
   par mot, chaque voie reçoit au plus 2 × 255 = 510 ; vidée toutes les 128 mots, elle reste sous 128 × 510 = 65 280
   < 2^16 ; au vidage, deux voies de 32 bits (au plus 2 × 65 280) ajoutées à la somme. La variante tuned du point 3
   vide ses voies à chaque mot, par une multiplication. *)
let[@inline never] k4_swar (v : Bytes.t) =
  let n = Bytes.length v in
  let nw = n / 8 in
  let s = ref 0 in
  let i = ref 0 in
  while !i < nw do
    let e = min (!i + 128) nw in
    let acc = ref 0L in
    while !i < e do
      let w = Bytes.get_int64_le v (8 * !i) in
      let y = Int64.logand w (Int64.mul (Int64.logand (Int64.shift_right_logical w 7) 0x0101010101010101L) 0xFFL) in
      acc := Int64.add !acc (Int64.add (Int64.logand y 0x00FF00FF00FF00FFL)
                                       (Int64.logand (Int64.shift_right_logical y 8) 0x00FF00FF00FF00FFL));
      incr i
    done;
    let a2 = Int64.add (Int64.logand !acc 0x0000FFFF0000FFFFL) (Int64.logand (Int64.shift_right_logical !acc 16) 0x0000FFFF0000FFFFL) in
    s := !s + Int64.to_int (Int64.logand a2 0xFFFFFFFFL) + Int64.to_int (Int64.shift_right_logical a2 32)
  done;
  for k = nw * 8 to n - 1 do
    let x = Char.code (Bytes.unsafe_get v k) in
    s := !s + (x land (- (x lsr 7)))
  done;
  !s

let run_k4 v reps =
  let ic = open_in_bin (Filename.concat data_dir "k4_bytes.u8") in
  let d = Bytes.create (in_channel_length ic) in
  really_input ic d 0 (Bytes.length d);
  close_in ic;
  if v = "natural_sorted" then begin
    let cnt = Array.make 256 0 in
    Bytes.iter (fun c -> cnt.(Char.code c) <- cnt.(Char.code c) + 1) d;
    let k = ref 0 in
    Array.iteri (fun b c -> for _ = 1 to c do Bytes.set d !k (Char.chr b); incr k done) cnt
  end;
  let f = if v = "tuned" then k4_tuned else if v = "swar" then k4_swar else if v = "branchless_unsorted" then k4_branchless else k4_natural in
  bench "k4" v "16M" reps (fun () -> string_of_int (f d))

(* ------------------------------------------------------------------ K5 *)
let inner5 = MS_INNER5

let[@inline never] k5_natural (a : (float, float32_elt, c_layout) Array1.t) (b : (float, float32_elt, c_layout) Array1.t) =
  let s = ref 0.0 in
  for i = 0 to Array1.dim a - 1 do s := !s +. (a.{i} *. b.{i}) done;
  !s

let[@inline never] k5_tuned (a : (float, float32_elt, c_layout) Array1.t) (b : (float, float32_elt, c_layout) Array1.t) =
  let s0 = ref 0.0 and s1 = ref 0.0 and s2 = ref 0.0 and s3 = ref 0.0 in
  let i = ref 0 in
  while !i < Array1.dim a do
    let g k = Array1.unsafe_get a (!i + k) *. Array1.unsafe_get b (!i + k) in
    s0 := !s0 +. g 0; s1 := !s1 +. g 1; s2 := !s2 +. g 2; s3 := !s3 +. g 3;
    i := !i + 4
  done;
  (!s0 +. !s1) +. (!s2 +. !s3)

let run_k5 v reps =
  let a = map float32 "k5_a.f32" and b = map float32 "k5_b.f32" in
  let r = ref a in
  let f = if v = "tuned" then k5_tuned else k5_natural in
  bench "k5" v "2048x65536" reps (fun () ->
    let d = ref 0.0 in
    for _ = 1 to inner5 do d := f (Sys.opaque_identity !r) b done;
    Printf.sprintf "%.4f" !d)

(* ------------------------------------------------------------------ réserve de domaines (v4, point 4) *)
(* docs/V4_CONVERGE.md, 3.3 (mt_pool) : quatre domaines de travail, le domaine principal compris. Les trois autres sont
   créés une fois par processus (Domain.spawn), avant l'échauffement ; à chaque appel, le domaine principal publie la
   tâche et les réveille (barrière faite d'un Mutex et d'une Condition, avec un compteur de génération : la bibliothèque
   standard n'a pas de barrière), traite le quart 0, puis attend leur fin à une seconde barrière. Entre deux appels, ils
   attendent, bloqués (Condition.wait) ; le Mutex ordonne aussi les accès mémoire entre les domaines. *)
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

type cols = { sd : (int32, int32_elt, c_layout) Array1.t; pr : (int32, int32_elt, c_layout) Array1.t;
              q : (int, int8_unsigned_elt, c_layout) Array1.t; d : (int, int8_unsigned_elt, c_layout) Array1.t;
              t : (int, int8_unsigned_elt, c_layout) Array1.t; rf : (int, int8_unsigned_elt, c_layout) Array1.t;
              ls : (int, int8_unsigned_elt, c_layout) Array1.t }

let[@inline never] q6_natural c lo hi =
  let s = ref 0 in
  for i = lo to hi - 1 do
    let sd = Int32.to_int c.sd.{i} in
    if sd >= 8766 && sd < 9131 && c.d.{i} >= 5 && c.d.{i} <= 7 && c.q.{i} < 24 then s := !s + (Int32.to_int c.pr.{i} * c.d.{i})
  done;
  !s

let[@inline never] q6_tuned c lo hi =
  let s = ref 0 in
  for i = lo to hi - 1 do
    let sd = Int32.to_int (Array1.unsafe_get c.sd i) and d = Array1.unsafe_get c.d i and q = Array1.unsafe_get c.q i in
    (* remarque sur OCaml (docs/OCAML.md) : chaque comparaison séparément ; && (court-circuit) gardait deux branchements *)
    let m = Bool.to_int (sd - 8766 >= 0) land Bool.to_int (sd - 8766 < 365) land Bool.to_int (d - 5 >= 0)
            land Bool.to_int (d - 5 <= 2) land Bool.to_int (q < 24) in
    s := !s + (Int32.to_int (Array1.unsafe_get c.pr i) * d * m)
  done;
  !s

let[@inline never] q1_natural c lo hi (acc : int array) =
  for i = lo to hi - 1 do
    if Int32.to_int c.sd.{i} <= 10471 then begin
      let g = ((c.rf.{i} * 2) + c.ls.{i}) * 5 and p = Int32.to_int c.pr.{i} in
      let dp = p * (100 - c.d.{i}) in
      acc.(g) <- acc.(g) + 1; acc.(g + 1) <- acc.(g + 1) + c.q.{i}; acc.(g + 2) <- acc.(g + 2) + p;
      acc.(g + 3) <- acc.(g + 3) + dp; acc.(g + 4) <- acc.(g + 4) + (dp * (100 + c.t.{i}))
    end
  done

(* Q1 optimisé : sans branchement, groupe 6 = rejet, accès non vérifiés *)
let[@inline never] q1_tuned c lo hi (acc : int array) =
  let a = Array.make 35 0 in
  for i = lo to hi - 1 do
    let rej = ((10471 - Int32.to_int (Array1.unsafe_get c.sd i)) lsr 62) land 1 in
    let g = ((((Array1.unsafe_get c.rf i * 2) + Array1.unsafe_get c.ls i) * (1 - rej)) + (6 * rej)) * 5 in
    let p = Int32.to_int (Array1.unsafe_get c.pr i) in
    let dp = p * (100 - Array1.unsafe_get c.d i) in
    Array.unsafe_set a g (Array.unsafe_get a g + 1);
    Array.unsafe_set a (g + 1) (Array.unsafe_get a (g + 1) + Array1.unsafe_get c.q i);
    Array.unsafe_set a (g + 2) (Array.unsafe_get a (g + 2) + p);
    Array.unsafe_set a (g + 3) (Array.unsafe_get a (g + 3) + dp);
    Array.unsafe_set a (g + 4) (Array.unsafe_get a (g + 4) + (dp * (100 + Array1.unsafe_get c.t i)))
  done;
  for k = 0 to 29 do acc.(k) <- acc.(k) + a.(k) done

(* v4, point 4 (3.3, Q6 tuned_s : forme de repli, OCaml n'ayant pas de vecteurs) : la forme de la remarque sur OCaml
   (bench/ocaml_exp, tuned_m ; docs/OCAML.md, 4.4 : × 0,86), recopiée : un masque tiré des bits de signe, une seule
   comparaison par ligne : x = (sd - 8766) lor (9130 - sd) lor (d - 5) lor (7 - d) lor (23 - q) est négatif si et
   seulement si l'une des bornes manque ; m = 1 - (bit de signe de x) ; s += prix × remise × m (int de 63 bits). *)
let[@inline never] q6_tuned_m c lo hi =
  let s = ref 0 in
  for i = lo to hi - 1 do
    let sd = Int32.to_int (Array1.unsafe_get c.sd i) and d = Array1.unsafe_get c.d i and q = Array1.unsafe_get c.q i in
    let x = (sd - 8766) lor (9130 - sd) lor (d - 5) lor (7 - d) lor (23 - q) in
    s := !s + (Int32.to_int (Array1.unsafe_get c.pr i) * d * (1 - ((x lsr 62) land 1)))
  done;
  !s

(* v4, point 4 (3.3, Q1 tuned_s) : une passe, les 30 accumulateurs en variables locales (références locales, gardées
   hors du tas) ; par ligne, pm = -1 si shipdate <= 10471 (décalage arithmétique du signe de shipdate - 10472), et pour
   chaque groupe k, mk = pm land (signe de (g lxor k) - 1), -1 si g = k ; additions masquées par land mk, sans
   branchement. Exactitude : les mêmes sommes que q1_tuned (entiers de 63 bits). *)
let[@inline never] q1_tuned_s c lo hi (acc : int array) =
  let n0 = ref 0 and q0 = ref 0 and p0 = ref 0 and e0 = ref 0 and c0 = ref 0 in
  let n1 = ref 0 and q1 = ref 0 and p1 = ref 0 and e1 = ref 0 and c1 = ref 0 in
  let n2 = ref 0 and q2 = ref 0 and p2 = ref 0 and e2 = ref 0 and c2 = ref 0 in
  let n3 = ref 0 and q3 = ref 0 and p3 = ref 0 and e3 = ref 0 and c3 = ref 0 in
  let n4 = ref 0 and q4 = ref 0 and p4 = ref 0 and e4 = ref 0 and c4 = ref 0 in
  let n5 = ref 0 and q5 = ref 0 and p5 = ref 0 and e5 = ref 0 and c5 = ref 0 in
  for i = lo to hi - 1 do
    let pm = (Int32.to_int (Array1.unsafe_get c.sd i) - 10472) asr 62 in
    let g = (Array1.unsafe_get c.rf i * 2) + Array1.unsafe_get c.ls i in
    let q = Array1.unsafe_get c.q i and p = Int32.to_int (Array1.unsafe_get c.pr i) in
    let dp = p * (100 - Array1.unsafe_get c.d i) in
    let ch = dp * (100 + Array1.unsafe_get c.t i) in
    let m = pm land ((g - 1) asr 62) in
    n0 := !n0 - m; q0 := !q0 + (q land m); p0 := !p0 + (p land m); e0 := !e0 + (dp land m); c0 := !c0 + (ch land m);
    let m = pm land (((g lxor 1) - 1) asr 62) in
    n1 := !n1 - m; q1 := !q1 + (q land m); p1 := !p1 + (p land m); e1 := !e1 + (dp land m); c1 := !c1 + (ch land m);
    let m = pm land (((g lxor 2) - 1) asr 62) in
    n2 := !n2 - m; q2 := !q2 + (q land m); p2 := !p2 + (p land m); e2 := !e2 + (dp land m); c2 := !c2 + (ch land m);
    let m = pm land (((g lxor 3) - 1) asr 62) in
    n3 := !n3 - m; q3 := !q3 + (q land m); p3 := !p3 + (p land m); e3 := !e3 + (dp land m); c3 := !c3 + (ch land m);
    let m = pm land (((g lxor 4) - 1) asr 62) in
    n4 := !n4 - m; q4 := !q4 + (q land m); p4 := !p4 + (p land m); e4 := !e4 + (dp land m); c4 := !c4 + (ch land m);
    let m = pm land (((g lxor 5) - 1) asr 62) in
    n5 := !n5 - m; q5 := !q5 + (q land m); p5 := !p5 + (p land m); e5 := !e5 + (dp land m); c5 := !c5 + (ch land m)
  done;
  let put k a b c' d' e' =
    acc.(k) <- acc.(k) + a; acc.(k + 1) <- acc.(k + 1) + b; acc.(k + 2) <- acc.(k + 2) + c';
    acc.(k + 3) <- acc.(k + 3) + d'; acc.(k + 4) <- acc.(k + 4) + e'
  in
  put 0 !n0 !q0 !p0 !e0 !c0; put 5 !n1 !q1 !p1 !e1 !c1; put 10 !n2 !q2 !p2 !e2 !c2;
  put 15 !n3 !q3 !p3 !e3 !c3; put 20 !n4 !q4 !p4 !e4 !c4; put 25 !n5 !q5 !p5 !e5 !c5

let run_k6 v reps p =
  let c = { sd = map int32 "k6_shipdate.i32"; pr = map int32 "k6_extendedprice.i32"; q = map int8_unsigned "k6_quantity.u8";
            d = map int8_unsigned "k6_discount.u8"; t = map int8_unsigned "k6_tax.u8"; rf = map int8_unsigned "k6_returnflag.u8";
            ls = map int8_unsigned "k6_linestatus.u8" } in
  let q1 = p = "q1" in
  let one f lo hi = if q1 then (let a = Array.make 30 0 in f c lo hi a; Array.fold_left ( + ) 0 a) else (if f == q1_natural then q6_natural c lo hi else q6_tuned c lo hi) in
  (* v4, point 4 : formes à un fil nouvelles (tuned_s de Q6 et de Q1), et réserve de domaines *)
  let one_s lo hi = if q1 then (let a = Array.make 30 0 in q1_tuned_s c lo hi a; Array.fold_left ( + ) 0 a) else q6_tuned_m c lo hi in
  let pl = v = "mt_pool" || v = "mt_pool_s" in
  if pl then pool_start ();
  bench "k6" v p reps (fun () ->
    string_of_int
      (match v with
       | "mt_pool" | "mt_pool_s" ->
           let part = Array.make 4 0 in
           pool_run (fun t ->
             let lo = n6 * t / 4 and hi = n6 * (t + 1) / 4 in
             part.(t) <- (if v = "mt_pool_s" then one_s lo hi else one q1_tuned lo hi));
           Array.fold_left ( + ) 0 part
       | "tuned_s" -> one_s 0 n6
       | "mt" ->
           let ds = Array.init 4 (fun k -> Domain.spawn (fun () -> one q1_tuned (n6 / 4 * k) (n6 / 4 * (k + 1)))) in
           Array.fold_left (fun s d -> s + Domain.join d) 0 ds
       | "tuned" -> one q1_tuned 0 n6
       | _ -> one q1_natural 0 n6));
  if pl then pool_stop ()

(* ------------------------------------------------------------------ K7 *)
type agg = { mutable count : int; mutable sum : int }

let run_k7 v reps =
  let keys = map int32 "k7_keys.u32" and vals = map int32 "k7_vals.u32" in
  let n = Array1.dim keys in
  let key i = Int32.to_int (Array1.unsafe_get keys i) land 0xFFFFFFFF in
  for r = -warmup to reps - 1 do
    let nk, ws, dt =
      if v = "natural" then begin
        let t0 = now () in
        let h = Hashtbl.create 16 in
        for i = 0 to n - 1 do
          let k = key i and x = Int32.to_int vals.{i} in
          match Hashtbl.find_opt h k with
          | Some e -> e.count <- e.count + 1; e.sum <- e.sum + x
          | None -> Hashtbl.add h k { count = 1; sum = x }
        done;
        let dt = now () -. t0 in
        (Hashtbl.length h, Hashtbl.fold (fun k e s -> s + (e.sum * ((k land 1023) + 1))) h 0, dt)
      end else if v = "tuned_oa" then begin
        (* v4, point 4 (3.3, K7 tuned_oa : forme de repli, OCaml n'ayant pas de préchargement) : la table de tuned_pf
           (cases de 16 octets) sans préchargement ni lots, la forme de la remarque sur OCaml (bench/ocaml_exp,
           tuned_p ; docs/OCAML.md, 4.4 : × 0,875), recopiée : clé (32 bits) et compteur (30 bits) dans un seul
           entier, somme dans le second : deux mots par case, au lieu des trois de la variante tuned publiée.
           Exactitude : le compteur tient en 30 bits tant que n < 2^30 (vérifié avant la zone chronométrée). *)
        let logc = MS_K7_LOG in
        let cap = 1 lsl logc and cmask = (1 lsl 30) - 1 in
        if n >= 1 lsl 30 then failwith "K7 tuned_oa : compteur de 30 bits";
        let t0 = now () in
        let tab = Array.make (2 * cap) 0 in
        for i = 0 to n - 1 do
          let k = key i in
          let s = ref (((k * 0x9E3779B1) land 0xFFFFFFFF) lsr (32 - logc)) in
          while (let p = Array.unsafe_get tab (2 * !s) in p land cmask <> 0 && p lsr 30 <> k) do s := (!s + 1) land (cap - 1) done;
          let b = 2 * !s in
          Array.unsafe_set tab b ((k lsl 30) lor ((Array.unsafe_get tab b land cmask) + 1));
          Array.unsafe_set tab (b + 1) (Array.unsafe_get tab (b + 1) + Int32.to_int (Array1.unsafe_get vals i))
        done;
        let dt = now () -. t0 in
        let nk = ref 0 and ws = ref 0 in
        for s = 0 to cap - 1 do
          let p = tab.(2 * s) in
          if p land cmask <> 0 then (incr nk; ws := !ws + (tab.((2 * s) + 1) * (((p lsr 30) land 1023) + 1)))
        done;
        (!nk, !ws, dt)
      end else begin
        let logc = MS_K7_LOG in
        let cap = 1 lsl logc in
        let t0 = now () in
        (* AoS manuel dans un int array : [clé; compteur; somme] par case *)
        let tab = Array.make (3 * cap) 0 in
        for i = 0 to n - 1 do
          let k = key i in
          let s = ref (((k * 0x9E3779B1) land 0xFFFFFFFF) lsr (32 - logc)) in
          while Array.unsafe_get tab ((3 * !s) + 1) <> 0 && Array.unsafe_get tab (3 * !s) <> k do s := (!s + 1) land (cap - 1) done;
          let b = 3 * !s in
          Array.unsafe_set tab b k;
          Array.unsafe_set tab (b + 1) (Array.unsafe_get tab (b + 1) + 1);
          Array.unsafe_set tab (b + 2) (Array.unsafe_get tab (b + 2) + Int32.to_int (Array1.unsafe_get vals i))
        done;
        let dt = now () -. t0 in
        let nk = ref 0 and ws = ref 0 in
        for s = 0 to cap - 1 do
          if tab.((3 * s) + 1) <> 0 then (incr nk; ws := !ws + (tab.((3 * s) + 2) * ((tab.(3 * s) land 1023) + 1)))
        done;
        (!nk, !ws, dt)
      end
    in
    if r >= 0 then result "k7" v "16M/1M" r dt (Printf.sprintf "%d:%d" nk ws)
  done

(* ------------------------------------------------------------------ K8 *)
type tree = Leaf | Node of int * tree * tree

let rec t_build d c = if d = 0 then (Node (!c, Leaf, Leaf) |> fun n -> incr c; n) else begin
    let v = !c in incr c;
    let l = t_build (d - 1) c in
    let r = t_build (d - 1) c in
    Node (v, l, r) end

let rec t_sum = function Leaf -> 0 | Node (v, l, r) -> v + t_sum l + t_sum r

(* arène : tableaux d'entiers réutilisés, nœuds indexés *)
let av = Array.make MS_K8_NODES 0 and al = Array.make MS_K8_NODES 0 and ar = Array.make MS_K8_NODES 0

let rec a_build top d c =
  let i = !top in
  incr top;
  Array.unsafe_set av i !c; incr c;
  if d = 0 then (Array.unsafe_set al i (-1); Array.unsafe_set ar i (-1))
  else begin
    let l = a_build top (d - 1) c in
    Array.unsafe_set al i l;
    Array.unsafe_set ar i (a_build top (d - 1) c)
  end;
  i

let rec a_sum i = if i < 0 then 0 else Array.unsafe_get av i + a_sum (Array.unsafe_get al i) + a_sum (Array.unsafe_get ar i)

(* v4, point 4 (3.3, K8 tuned_val) : la forme de la remarque sur OCaml (bench/ocaml_exp ; docs/OCAML.md, 4.4 : × 0,77),
   recopiée : la même arène, l'indice du nœud en ordre préfixe passé par valeur, la valeur du nœud vaut q + indice, la
   fonction rend l'indice libre suivant ; ni référence d'état ni compteur partagé. *)
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

(* v4, point 4 (3.3, K8 tuned_it) : la même arène, construction et somme itératives avec des piles explicites de 64
   entrées (tableaux alloués une fois) ; la construction descend à gauche en empilant le sous-arbre droit de chaque nœud
   interne, puis le reprend à la feuille suivante (même ordre préfixe, mêmes valeurs que a_build). La profondeur doit
   rester sous 63 (vérifié dans run_k8). *)
let stp = Array.make 64 0 and std = Array.make 64 0 and sts = Array.make 64 0

let a_build_it depth q =
  let sp = ref 0 and nxt = ref 0 and parent = ref (-1) and right = ref false and d = ref depth and fin = ref false in
  while not !fin do
    let i = !nxt in
    incr nxt;
    Array.unsafe_set av i (q + i);
    if !parent >= 0 then (if !right then Array.unsafe_set ar !parent i else Array.unsafe_set al !parent i);
    if !d > 0 then begin
      Array.unsafe_set stp !sp i;
      Array.unsafe_set std !sp (!d - 1);
      incr sp;
      parent := i;
      right := false;
      decr d
    end else begin
      Array.unsafe_set al i (-1);
      Array.unsafe_set ar i (-1);
      if !sp = 0 then fin := true
      else begin
        decr sp;
        parent := Array.unsafe_get stp !sp;
        d := Array.unsafe_get std !sp;
        right := true
      end
    end
  done

let a_sum_it root =
  let sp = ref 1 and s = ref 0 in
  Array.unsafe_set sts 0 root;
  while !sp > 0 do
    decr sp;
    let i = Array.unsafe_get sts !sp in
    s := !s + Array.unsafe_get av i;
    let l = Array.unsafe_get al i in
    if l >= 0 then begin
      Array.unsafe_set sts !sp (Array.unsafe_get ar i);
      Array.unsafe_set sts (!sp + 1) l;
      sp := !sp + 2
    end
  done;
  !s

let run_k8 v reps =
  let q = 16384 in
  let keep = t_build MS_K8_LONG (ref 0) in
  let lsum = t_sum keep in
  let lat = Array.make q 0.0 in
  (* remarque sur OCaml (docs/OCAML.md) : sommet et compteur de l'arène alloués une fois, remis à zéro à chaque requête *)
  let top = ref 0 and ca = ref 0 in
  if v = "tuned_it" && MS_K8_REQ >= 63 then failwith "K8 tuned_it : piles de 64 entrées, MS_K8_REQ doit rester sous 63";
  for r = -warmup to reps - 1 do
    let total = ref 0 in
    let t0 = now () in
    for qq = 0 to q - 1 do
      let a = now () in
      let s =
        if v = "tuned" then (top := 0; ca := qq; a_sum (a_build top MS_K8_REQ ca))
        else if v = "tuned_val" then (ignore (a_build_val 0 MS_K8_REQ qq); a_sum 0)
        else if v = "tuned_it" then (a_build_it MS_K8_REQ qq; a_sum_it 0)
        else t_sum (t_build MS_K8_REQ (ref qq)) in
      total := !total + s;
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

(* naturel : float array array (chaque ligne est un tableau de flottants « à plat ») *)
let[@inline never] k9_natural (a : float array array) (b : float array array) =
  for i = 1 to m9 - 2 do
    for j = 1 to m9 - 2 do b.(i).(j) <- 0.25 *. (((a.(i - 1).(j) +. a.(i + 1).(j)) +. a.(i).(j - 1)) +. a.(i).(j + 1)) done
  done

(* v4, point 3 (docs/V4_EQUAL.md, R2) : naturel en grille contiguë, float array (flottants à plat) indexé i * m9 + j,
   même boucle *)
let[@inline never] k9_natural_flat (a : float array) (b : float array) =
  for i = 1 to m9 - 2 do
    for j = 1 to m9 - 2 do
      b.((i * m9) + j) <- 0.25 *. (((a.(((i - 1) * m9) + j) +. a.(((i + 1) * m9) + j)) +. a.((i * m9) + j - 1)) +. a.((i * m9) + j + 1))
    done
  done

(* optimisé : Bigarray.Array1 float64 plat (contigu), accès non vérifiés *)
let[@inline never] k9_rows (a : (float, float64_elt, c_layout) Array1.t) (b : (float, float64_elt, c_layout) Array1.t) r0 r1 =
  for i = r0 to r1 - 1 do
    let up = (i - 1) * m9 and mid = i * m9 and dn = (i + 1) * m9 in
    for j = 1 to m9 - 2 do
      Array1.unsafe_set b (mid + j)
        (0.25 *. (((Array1.unsafe_get a (up + j) +. Array1.unsafe_get a (dn + j)) +. Array1.unsafe_get a (mid + j - 1)) +. Array1.unsafe_get a (mid + j + 1)))
    done
  done

let run_k9 v reps =
  (* harnais commun de K9 (docs/K9.md) : grilles allouées une fois par processus, réinitialisées hors chrono *)
  if v = "natural" then begin
    let a = Array.make_matrix m9 m9 0.0 and b = Array.make_matrix m9 m9 0.0 in
    for r = -warmup to reps - 1 do
      for i = 0 to m9 - 1 do
        for j = 0 to m9 - 1 do let x = k9_init i j in a.(i).(j) <- x; b.(i).(j) <- x done
      done;
      let t0 = now () in
      k9_natural a b; k9_natural b a; k9_natural a b; k9_natural b a;
      let dt = now () -. t0 in
      let s = Array.fold_left (Array.fold_left ( +. )) 0.0 a in
      if r >= 0 then result "k9" v "2048^2x4" r dt (Printf.sprintf "%.15e" s)
    done
  end else if v = "natural_flat" then begin
    (* v4, point 3 (docs/V4_EQUAL.md, R2) : K9 naturel contigu, au harnais commun de K9 *)
    let a = Array.make (m9 * m9) 0.0 and b = Array.make (m9 * m9) 0.0 in
    for r = -warmup to reps - 1 do
      for k = 0 to (m9 * m9) - 1 do let x = k9_init (k / m9) (k mod m9) in a.(k) <- x; b.(k) <- x done;
      let t0 = now () in
      k9_natural_flat a b; k9_natural_flat b a; k9_natural_flat a b; k9_natural_flat b a;
      let dt = now () -. t0 in
      let s = Array.fold_left ( +. ) 0.0 a in
      if r >= 0 then result "k9" v "2048^2x4" r dt (Printf.sprintf "%.15e" s)
    done
  end else begin
    let a = Array1.create float64 c_layout (m9 * m9) and b = Array1.create float64 c_layout (m9 * m9) in
    let pl = v = "mt_pool" in  (* v4, point 4 : réserve de domaines, chaque quart : k9_rows publiée *)
    if pl then pool_start ();
    let step x y =
      if v = "tuned" then k9_rows x y 1 (m9 - 1)
      else if pl then pool_run (fun t -> k9_rows x y (1 + ((m9 - 2) * t / 4)) (1 + ((m9 - 2) * (t + 1) / 4)))
      else Array.iter Domain.join (Array.init 4 (fun t -> Domain.spawn (fun () -> k9_rows x y (1 + ((m9 - 2) * t / 4)) (1 + ((m9 - 2) * (t + 1) / 4)))))
    in
    for r = -warmup to reps - 1 do
      for k = 0 to (m9 * m9) - 1 do let x = k9_init (k / m9) (k mod m9) in a.{k} <- x; b.{k} <- x done;
      let t0 = now () in
      step a b; step b a; step a b; step b a;
      let dt = now () -. t0 in
      let s = ref 0.0 in
      for k = 0 to (m9 * m9) - 1 do s := !s +. a.{k} done;
      if r >= 0 then result "k9" v "2048^2x4" r dt (Printf.sprintf "%.15e" !s)
    done;
    if pl then pool_stop ()
  end

(* ------------------------------------------------------------------ K10 *)
let m10 = 1 lsl 22
let cap10 = 1 lsl 14

let run_k10 v reps =
  bench "k10" v "2^22" reps (fun () ->
    if v = "natural" then begin
      (* tampon borné classique : Queue + Mutex + Condition (bibliothèque standard) *)
      let qu = Queue.create () and mu = Mutex.create () and not_empty = Condition.create () and not_full = Condition.create () in
      let prod = Domain.spawn (fun () ->
        for x = 1 to m10 do
          Mutex.lock mu;
          while Queue.length qu >= cap10 do Condition.wait not_full mu done;
          Queue.push x qu;
          Condition.signal not_empty;
          Mutex.unlock mu
        done) in
      let cons = Domain.spawn (fun () ->
        let s = ref 0 in
        for _ = 1 to m10 do
          Mutex.lock mu;
          while Queue.is_empty qu do Condition.wait not_empty mu done;
          s := !s + Queue.pop qu;
          Condition.signal not_full;
          Mutex.unlock mu
        done;
        !s) in
      Domain.join prod;
      string_of_int (Domain.join cons)
    end else begin
      let w_idx = Atomic.make_contended 0 and r_idx = Atomic.make_contended 0 in
      let buf = Array.make cap10 0 in
      let prod = Domain.spawn (fun () ->
        let w = ref 0 and rc = ref 0 in
        for x = 1 to m10 do
          while !w - !rc = cap10 do rc := Atomic.get r_idx; if !w - !rc = cap10 then Domain.cpu_relax () done;
          Array.unsafe_set buf (!w land (cap10 - 1)) x;
          incr w;
          Atomic.set w_idx !w
        done) in
      let cons = Domain.spawn (fun () ->
        let rd = ref 0 and wc = ref 0 and s = ref 0 in
        for _ = 1 to m10 do
          while !rd = !wc do wc := Atomic.get w_idx; if !rd = !wc then Domain.cpu_relax () done;
          s := !s + Array.unsafe_get buf (!rd land (cap10 - 1));
          incr rd;
          Atomic.set r_idx !rd
        done;
        !s) in
      Domain.join prod;
      string_of_int (Domain.join cons)
    end)

(* ------------------------------------------------------------------ v4, point 6 : piste ouverte *)
(* Formes de la piste ouverte (docs/V4_OPEN.md, 5.1 ; relevé : ocaml_intrinsics_kernel v0.17.3), placées en fin de
   fichier pour que les noms numérotés des fonctions du banc ne changent pas. Avec le compilateur classé (OCaml 5.5.2 et
   flambda, sans le greffon des intrinsèques), Conditional.select_int est un appel C noalloc au talon
   caml_csel_int_untagged (compilé -O2 -march=native, 5.2). *)
module CI = Ocaml_intrinsics_kernel.Conditional

(* K4 op_intrinsics : la somme conditionnelle octet par octet, la sélection par select_int (x >= 128) x 0. La forme
   tuned sélectionne par masques les octets d'un mot de 64 bits, ce que select_int, qui choisit entre deux int, ne
   remplace pas. *)
let[@inline never] k4_op (v : Bytes.t) =
  let s = ref 0 in
  for i = 0 to Bytes.length v - 1 do
    let x = Char.code (Bytes.unsafe_get v i) in
    s := !s + CI.select_int (x >= 128) x 0
  done;
  !s

let run_k4_op v reps =
  if v <> "op_intrinsics" then failwith ("variante inconnue " ^ v);
  let ic = open_in_bin (Filename.concat data_dir "k4_bytes.u8") in
  let d = Bytes.create (in_channel_length ic) in
  really_input ic d 0 (Bytes.length d);
  close_in ic;
  bench "k4" v "16M" reps (fun () -> string_of_int (k4_op d))

(* Q6 op_intrinsics : la forme tuned_s (q6_tuned_m : une comparaison par ligne, x négatif si et seulement si une borne
   manque), le filtre par select_int (x >= 0) (prix × remise) 0 au lieu du masque tiré du bit de signe. Q6 mt
   op_intrinsics_mt : la même fonction sur les quatre quarts, dans la réserve de domaines de mt_pool_s. *)
let[@inline never] q6_op c lo hi =
  let s = ref 0 in
  for i = lo to hi - 1 do
    let sd = Int32.to_int (Array1.unsafe_get c.sd i) and d = Array1.unsafe_get c.d i and q = Array1.unsafe_get c.q i in
    let x = (sd - 8766) lor (9130 - sd) lor (d - 5) lor (7 - d) lor (23 - q) in
    s := !s + CI.select_int (x >= 0) (Int32.to_int (Array1.unsafe_get c.pr i) * d) 0
  done;
  !s

let run_k6_op v reps p =
  if p <> "q6" || (v <> "op_intrinsics" && v <> "op_intrinsics_mt") then failwith ("variante inconnue " ^ v ^ " " ^ p);
  let c = { sd = map int32 "k6_shipdate.i32"; pr = map int32 "k6_extendedprice.i32"; q = map int8_unsigned "k6_quantity.u8";
            d = map int8_unsigned "k6_discount.u8"; t = map int8_unsigned "k6_tax.u8"; rf = map int8_unsigned "k6_returnflag.u8";
            ls = map int8_unsigned "k6_linestatus.u8" } in
  let mt = v = "op_intrinsics_mt" in
  if mt then pool_start ();
  bench "k6" v p reps (fun () ->
    string_of_int
      (if mt then begin
         let part = Array.make 4 0 in
         pool_run (fun t ->
           let lo = n6 * t / 4 and hi = n6 * (t + 1) / 4 in
           part.(t) <- q6_op c lo hi);
         Array.fold_left ( + ) 0 part
       end else q6_op c 0 n6));
  if mt then pool_stop ()

let () =
  let k = Sys.argv.(1) and v = Sys.argv.(2) and reps = int_of_string Sys.argv.(3) in
  let p = if Array.length Sys.argv > 4 then Sys.argv.(4) else "" in
  match k with
  | "k1" -> run_k1 v reps
  | "k2" -> run_k2 v reps p
  | "k3" -> run_k3 v reps
  | "k4" -> if String.starts_with ~prefix:"op_" v then run_k4_op v reps else run_k4 v reps
  | "k5" -> run_k5 v reps
  | "k6" -> if String.starts_with ~prefix:"op_" v then run_k6_op v reps p else run_k6 v reps p
  | "k7" -> run_k7 v reps
  | "k8" -> run_k8 v reps
  | "k9" -> run_k9 v reps
  | "k10" -> run_k10 v reps
  | _ -> ()
