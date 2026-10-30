package main
import "core:fmt"
import "core:simd"
import x86 "core:simd/x86"
import "core:sync"
import "core:thread"
import "core:sys/linux"
import "base:intrinsics"
import "base:runtime"

foreign import llvm_intr "system:c"
@(default_calling_convention="none")
foreign llvm_intr {
	@(link_name="llvm.x86.avx512.conflict.d.512")
	vpconflictd512 :: proc(a: #simd[16]i32) -> #simd[16]i32 ---
	@(link_name="llvm.x86.avx512.psad.bw.512")
	vpsadbw512 :: proc(a, b: #simd[64]u8) -> #simd[8]u64 ---
}

@(enable_target_feature="avx512f,avx512cd,avx512bw,evex512")
dp :: proc "c" (a: #simd[16]i32, x, y: #simd[64]u8) -> (#simd[16]i32, #simd[8]u64) { return vpconflictd512(a), vpsadbw512(x, y) }

@(enable_target_feature="avx512f,evex512")
srl :: proc "c" (a, c: x86.__m512i) -> x86.__m512i { return x86._mm512_srlv_epi32(a, c) }

@(cold)
slow :: proc(x: int) -> int { return x * 3 }

flag: i32
data: int

main :: proc() {
	a := #simd[8]f32{1, 2, 3, 4, 5, 6, 7, 8}
	b := a * a + a
	fmt.println("simd ok", simd.extract(b, 7), simd.reduce_add_ordered(b))
	x := 5
	if intrinsics.expect(x > 0, true) { fmt.println("expect ok") } else { fmt.println(slow(x)) }
	arr: [128]int
	intrinsics.prefetch_read_data(&arr[64], 3)
	t := thread.create_and_start(proc() {
		for sync.atomic_load_explicit(&flag, .Relaxed) == 0 { intrinsics.cpu_relax() }
		sync.atomic_thread_fence(.Acquire)
		fmt.println("thread saw", data)
	})
	data = 42
	sync.atomic_thread_fence(.Release)
	sync.atomic_store_explicit(&flag, 1, .Relaxed)
	thread.join(t)
	mask: [16]u64
	mask[0] = 1
	_, err := linux.sched_setaffinity(0, size_of(mask), &mask)
	fmt.println("affinity err", err, "MAP_CACHE_LINE_SIZE", runtime.MAP_CACHE_LINE_SIZE)
	_ = dp; _ = srl
}
