package probe

import "core:fmt"
import "base:intrinsics"

S :: struct { a: u8, b: u32, c: f64 }
P :: struct #packed { a: u8, b: u32 }
BF :: bit_field u16 { x: u8 | 3, y: u8 | 5 }
U :: struct #raw_union { f: f32, u: u32 }

main :: proc() {
	fmt.printf("CAP;A2;1;offset_of(S, c)=%d\n", offset_of(S, c))
	fmt.printf("CAP;A3;1;#packed size_of(P)=%d ; bit_field size_of(BF)=%d\n", size_of(P), size_of(BF))
	u := U{f = 1.0}
	fmt.printf("CAP;A5;1;#raw_union 0x%x transmute 0x%x\n", u.u, transmute(u32)f32(1.0))
	x := 1
	if intrinsics.expect(x == 1, true) do x += 1
	fmt.printf("CAP;E3;1;intrinsics.expect : %d\n", x)
	arr: [64]u8
	intrinsics.prefetch_read_data(&arr, 3)
	intrinsics.cpu_relax()
	fmt.printf("CAP;E4;1;prefetch_read_data ; D5 cpu_relax\n")
}
