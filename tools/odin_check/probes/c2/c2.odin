// Sonde C2 (remarque sur Odin) : intrinsèques x86 de LLVM importées par foreign _ et @(link_name), dont une à
// opérande immédiat (#const). Aucune n'est fournie par core:simd/x86.
package main

import "core:fmt"
import "core:simd"

@(default_calling_convention="none")
foreign _ {
	@(link_name="llvm.x86.avx512.conflict.d.512")
	conflict_d :: proc(a: #simd[16]i32) -> #simd[16]i32 ---
	@(link_name="llvm.x86.avx512.pternlog.d.512")
	ternlog_d :: proc(a, b, c: #simd[16]i32, #const imm: i32) -> #simd[16]i32 ---
}

main :: proc() {
	v := #simd[16]i32{1, 2, 2, 3, 4, 4, 4, 5, 6, 7, 8, 8, 9, 10, 11, 11}
	r := conflict_d(v)
	t := ternlog_d(v, r, v, 0x96)
	fmt.println(simd.to_array(r))
	fmt.println(simd.to_array(t))
}
