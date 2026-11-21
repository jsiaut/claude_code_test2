(* Sonde de mode (v4, point 3 : docs/V4_EQUAL.md, 4) : « 1d » : float array, « 2d » : float array array (K9 naturel). *)
let () =
  let n = int_of_string Sys.argv.(2) in
  if Sys.argv.(1) = "1d" then begin
    let a = Array.make n 1.0 in
    Printf.printf "%g\n" a.(n)
  end else begin
    let g = Array.init 4 (fun _ -> Array.make n 1.0) in
    Printf.printf "%g\n" g.(1).(n)
  end
