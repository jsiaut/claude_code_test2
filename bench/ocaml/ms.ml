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
let now () = Unix.gettimeofday ()

let bench k v p reps f =
  for r = -warmup to reps - 1 do
    let t0 = now () in
    let chk = f () in
    let dt = now () -. t0 in
    if r >= 0 then result k v p r dt chk
  done

(* ------------------------------------------------------------------ K1 *)
let n1 = 1 lsl 22

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
  let e i = 0.5 *. Array1.unsafe_get f (i + 9) *. ((Array1.unsafe_get f (i + 3) ** 2.) +. (Array1.unsafe_get f (i + 4) ** 2.) +. (Array1.unsafe_get f (i + 5) ** 2.)) in
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
  let f = if v = "branchless_unsorted" then k4_branchless else k4_natural in
  bench "k4" v "16M" reps (fun () -> string_of_int (f d))

(* ------------------------------------------------------------------ K5 *)
let inner5 = 1 lsl 16

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

(* ------------------------------------------------------------------ K6 *)
let n6 = 1 lsl 24

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
    let m = Bool.to_int (sd - 8766 >= 0 && sd - 8766 < 365) land Bool.to_int (d - 5 >= 0 && d - 5 <= 2) land Bool.to_int (q < 24) in
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

let run_k6 v reps p =
  let c = { sd = map int32 "k6_shipdate.i32"; pr = map int32 "k6_extendedprice.i32"; q = map int8_unsigned "k6_quantity.u8";
            d = map int8_unsigned "k6_discount.u8"; t = map int8_unsigned "k6_tax.u8"; rf = map int8_unsigned "k6_returnflag.u8";
            ls = map int8_unsigned "k6_linestatus.u8" } in
  let q1 = p = "q1" in
  let one f lo hi = if q1 then (let a = Array.make 30 0 in f c lo hi a; Array.fold_left ( + ) 0 a) else (if f == q1_natural then q6_natural c lo hi else q6_tuned c lo hi) in
  bench "k6" v p reps (fun () ->
    string_of_int
      (match v with
       | "mt" ->
           let ds = Array.init 4 (fun k -> Domain.spawn (fun () -> one q1_tuned (n6 / 4 * k) (n6 / 4 * (k + 1)))) in
           Array.fold_left (fun s d -> s + Domain.join d) 0 ds
       | "tuned" -> one q1_tuned 0 n6
       | _ -> one q1_natural 0 n6))

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
      end else begin
        let logc = 21 in
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
let av = Array.make 2047 0 and al = Array.make 2047 0 and ar = Array.make 2047 0

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

let run_k8 v reps =
  let q = 16384 in
  let keep = t_build 20 (ref 0) in
  let lsum = t_sum keep in
  let lat = Array.make q 0.0 in
  for r = -warmup to reps - 1 do
    let total = ref 0 in
    let t0 = now () in
    for qq = 0 to q - 1 do
      let a = now () in
      let c = ref qq in
      let s = if v = "tuned" then a_sum (a_build (ref 0) 10 c) else t_sum (t_build 10 c) in
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
let m9 = 2048
let k9_init i j = float_of_int (((i * 31) + (j * 17)) mod 1024) /. 1024.0

(* naturel : float array array (chaque ligne est un tableau de flottants « à plat ») *)
let[@inline never] k9_natural (a : float array array) (b : float array array) =
  for i = 1 to m9 - 2 do
    for j = 1 to m9 - 2 do b.(i).(j) <- 0.25 *. (((a.(i - 1).(j) +. a.(i + 1).(j)) +. a.(i).(j - 1)) +. a.(i).(j + 1)) done
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
  for r = -warmup to reps - 1 do
    let s, dt =
      if v = "natural" then begin
        let a = Array.init m9 (fun i -> Array.init m9 (fun j -> k9_init i j)) in
        let b = Array.map Array.copy a in
        let t0 = now () in
        k9_natural a b; k9_natural b a; k9_natural a b; k9_natural b a;
        let dt = now () -. t0 in
        (Array.fold_left (Array.fold_left ( +. )) 0.0 a, dt)
      end else begin
        let mk () = let g = Array1.create float64 c_layout (m9 * m9) in for k = 0 to (m9 * m9) - 1 do g.{k} <- k9_init (k / m9) (k mod m9) done; g in
        let a = mk () and b = mk () in
        let step x y =
          if v = "tuned" then k9_rows x y 1 (m9 - 1)
          else Array.iter Domain.join (Array.init 4 (fun t -> Domain.spawn (fun () -> k9_rows x y (1 + ((m9 - 2) * t / 4)) (1 + ((m9 - 2) * (t + 1) / 4)))))
        in
        let t0 = now () in
        step a b; step b a; step a b; step b a;
        let dt = now () -. t0 in
        let s = ref 0.0 in
        for k = 0 to (m9 * m9) - 1 do s := !s +. a.{k} done;
        (!s, dt)
      end
    in
    if r >= 0 then result "k9" v "2048^2x4" r dt (Printf.sprintf "%.15e" s)
  done

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

let () =
  let k = Sys.argv.(1) and v = Sys.argv.(2) and reps = int_of_string Sys.argv.(3) in
  let p = if Array.length Sys.argv > 4 then Sys.argv.(4) else "" in
  match k with
  | "k1" -> run_k1 v reps
  | "k2" -> run_k2 v reps p
  | "k3" -> run_k3 v reps
  | "k4" -> run_k4 v reps
  | "k5" -> run_k5 v reps
  | "k6" -> run_k6 v reps p
  | "k7" -> run_k7 v reps
  | "k8" -> run_k8 v reps
  | "k9" -> run_k9 v reps
  | "k10" -> run_k10 v reps
  | _ -> ()
