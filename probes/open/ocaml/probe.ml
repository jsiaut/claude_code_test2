(* v4, point 6 (docs/V4_OPEN.md, 4) : sondes de la grille ouverte d'OCaml
   (C2 : ocaml_intrinsics_kernel v0.17.3 ; C5 : domainslib 0.5.2 ; D4 : processor 0.2). *)
module T = Domainslib.Task
module I = Ocaml_intrinsics_kernel

let[@inline never] popc x = I.Int.count_set_bits x
let[@inline never] csel c a b = I.Conditional.select_int c a b

external gettid : unit -> int = "probe_gettid"
external getcpu : unit -> int = "probe_getcpu"

let c2 () =
  let s = ref 0 in
  for i = 0 to 1_000_000 do s := !s + popc i done;
  let k = ref 0 in
  for i = 0 to 255 do k := !k + csel (i >= 128) i 0 done;
  Printf.printf "RESULT;C2;ocaml_intrinsics_kernel;Int.count_set_bits sur 0..10^6 = %d ; Conditional.select_int dans une somme conditionnelle de 0..255 (i >= 128) = %d (attendu 24512)\n" !s !k

let c5 () =
  let pool = T.setup_pool ~num_domains:3 () in
  let tids = Array.make 4 0 in
  let s = T.run pool (fun () ->
    T.parallel_for_reduce ~chunk_size:1 ~start:0 ~finish:3 ~body:(fun c ->
      tids.(c) <- gettid ();
      let acc = ref 0 in
      for k = c * 10_000_000 + 1 to (c + 1) * 10_000_000 do acc := !acc + k done;
      !acc) pool ( + ) 0) in
  T.teardown_pool pool;
  let distinct = List.length (List.sort_uniq compare (Array.to_list tids)) in
  Printf.printf "RESULT;C5;domainslib;Task.parallel_for_reduce sur 4 tranches (pool de 3 domaines + l'appelant) : somme = %d (attendu 800000020000000) ; tranches exécutées sur %d fils distincts\n" s distinct

let d4 () =
  let before = Processor.Affinity.get_ids () in
  let d = Domain.spawn (fun () ->
    Processor.Affinity.set_ids [2];
    let ids = Processor.Affinity.get_ids () in
    let cpus = List.sort_uniq compare (List.init 1000 (fun _ -> getcpu ())) in
    ids, cpus) in
  let ids, cpus = Domain.join d in
  Printf.printf "RESULT;D4;processor;Affinity.get_ids () avant = [%s] ; dans un domaine, set_ids [2] puis get_ids () = [%s], sched_getcpu sur 1000 lectures = [%s] ; Query.cpu_count = %d\n"
    (String.concat ";" (List.map string_of_int before)) (String.concat ";" (List.map string_of_int ids))
    (String.concat ";" (List.map string_of_int cpus)) Processor.Query.cpu_count

let () = c2 (); c5 (); d4 ()
