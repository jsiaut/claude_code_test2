// Code produit, lu par run.sh (-build-mode:asm et -build-mode:llvm-ir, -o:speed, -microarch:native).
package codegen

import "base:intrinsics"

@(export) st_release :: proc "c" (a: ^u64) { intrinsics.atomic_store_explicit(a, 1, .Release) }
@(export) st_seqcst :: proc "c" (a: ^u64) { intrinsics.atomic_store_explicit(a, 1, .Seq_Cst) }
@(export) add_relaxed :: proc "c" (a: ^u64) -> u64 { return intrinsics.atomic_add_explicit(a, 1, .Relaxed) }
@(export) spin :: proc "c" (f: ^u64) { for intrinsics.atomic_load_explicit(f, .Acquire) == 0 do intrinsics.cpu_relax(); intrinsics.atomic_thread_fence(.Seq_Cst) }
@(export) axpy :: proc "c" (#no_alias a: [^]f32, #no_alias b: [^]f32, n: int) { for i in 0 ..< n do a[i] += 2 * b[i] }
@(export) idx_checked :: proc "c" (a: [^]f32, n: int, i: int) -> f32 { context = {}; s := a[:n]; return s[i] }
@(export) idx_unchecked :: proc "c" (a: [^]f32, n: int, i: int) -> f32 #no_bounds_check { s := a[:n]; return s[i] }
foreign { ext :: proc "c" (x: u64) --- }
@(export) hinted :: proc "c" (x: u64) -> u64 { r := x; if intrinsics.expect(x == 7, false) { ext(x); r = x * 5 }; return r + 1 }
@(export) unhinted :: proc "c" (x: u64) -> u64 { r := x; if x == 9 { ext(x); r = x * 7 }; return r + 3 }
@(export) pf :: proc "c" (p: rawptr) { intrinsics.prefetch_read_data(p, 3) }
@(export) sum_plain :: proc "c" (a: [^]f32, n: int) -> f32 { s: f32; for i in 0 ..< n do s += a[i]; return s }
@(export, fast_math = {.Allow_Reassoc}) sum_fast :: proc "c" (a: [^]f32, n: int) -> f32 { s: f32; for i in 0 ..< n do s += a[i]; return s }
gsum :: #force_no_inline proc(x: []$T) -> T { s: T; for v in x do s += v; return s }
@(export) use_both :: proc "c" (a: [^]f32, b: [^]f64, n: int) -> f64 { context = {}; return f64(gsum(a[:n])) + gsum(b[:n]) }
@(default_calling_convention = "none")
foreign _ { @(link_name = "llvm.x86.avx512.pternlog.d.512") pternlog :: proc(a, b, c: #simd[16]i32, #const imm: i32) -> #simd[16]i32 --- }
@(export) tern :: proc "c" (a, b, c: ^#simd[16]i32) -> #simd[16]i32 { return pternlog(a^, b^, c^, 0x96) }
@(export, fast_math = {.Allow_Reassoc, .No_NaNs, .No_Infs, .No_Signed_Zeros, .Allow_Reciprocal, .Allow_Contract, .Approx_Func}) sum_allfast :: proc "c" (a: [^]f32, n: int) -> f32 { s: f32; for i in 0 ..< n do s += a[i]; return s }
