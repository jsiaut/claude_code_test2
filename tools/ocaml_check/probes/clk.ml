let now_tod () = Unix.gettimeofday ()
let now_re () = Int64.to_float (Runtime_events.Timestamp.to_int64 (Runtime_events.Timestamp.get_current ())) *. 1e-9
let lat = Array.make 1_000_000 0.0
let bench name now =
  let w0 = Gc.minor_words () in
  let t0 = now () in
  for i = 0 to 999_999 do let a = now () in lat.(i) <- (now () -. a) *. 1e9 done;
  let dt = now () -. t0 in
  let w1 = Gc.minor_words () in
  Array.sort compare lat;
  Printf.printf "%s : %.1f ns par paire, %.2f mots alloués par paire, médiane de l'écart %.0f ns\n%!" name (dt *. 1e9 /. 1e6) ((w1 -. w0) /. 1e6) lat.(500_000)
let () = bench "gettimeofday" now_tod; bench "Runtime_events" now_re; bench "gettimeofday" now_tod; bench "Runtime_events" now_re
