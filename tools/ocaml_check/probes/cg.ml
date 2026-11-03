let[@inline never] mx (a : int) b = if a > b then a else b
let[@inline never] sel (x : int) = if x >= 128 then x else 0
let[@inline never] pc x = Int.popcount x
let () = Printf.printf "%d %d %d\n" (mx (Sys.opaque_identity 3) 4) (sel (Sys.opaque_identity 200)) (pc (Sys.opaque_identity 255))
