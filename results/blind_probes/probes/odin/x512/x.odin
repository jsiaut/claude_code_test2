package x512
import x86 "core:simd/x86"
foreign import llvm_intr "system:c"
@(default_calling_convention="none")
foreign llvm_intr {
	@(link_name="llvm.x86.avx512.conflict.d.512")
	vpconflictd512 :: proc(a: #simd[16]i32) -> #simd[16]i32 ---
}
@(export, enable_target_feature="avx512f,avx512cd,evex512")
conflict :: proc "c" (a: ^#simd[16]i32, r: ^#simd[16]i32) { r^ = vpconflictd512(a^) }
@(export, enable_target_feature="avx512f,evex512")
srl :: proc "c" (a, c: ^x86.__m512i, r: ^x86.__m512i) { r^ = x86._mm512_srlv_epi32(a^, c^) }
