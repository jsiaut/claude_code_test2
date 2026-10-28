let () =
  let a = Atomic.make_contended 0 in
  Atomic.incr a; Domain.cpu_relax ();
  Printf.printf "CAP;D3;1;Atomic.make_contended ; D5 Domain.cpu_relax : %d\n" (Atomic.get a);
  Printf.printf "CAP;A5;0.5;Int32.bits_of_float 1.0 = 0x%lx\n" (Int32.bits_of_float 1.0);
  let m = Bigarray.Array2.create Bigarray.float64 Bigarray.c_layout 4 4 in
  m.{1, 2} <- 3.0;
  Printf.printf "CAP;F1;1;Bigarray.Array2 c_layout : %g\n" m.{1, 2};
  let fd = Unix.openfile "/opt/msdata/k5_a.f32" [Unix.O_RDONLY] 0 in
  let v = Bigarray.array1_of_genarray (Unix.map_file fd Bigarray.float32 Bigarray.c_layout false [| -1 |]) in
  Printf.printf "CAP;F4;1;Unix.map_file -> Bigarray float32 : %g\n" v.{0}
