// Code produit, lu par run.sh (zig build-obj -O ReleaseFast -mcpu native, et -O ReleaseSafe pour E6).
const std = @import("std");
export fn st_release(a: *u64) void { @atomicStore(u64, a, 1, .release); }
export fn st_seqcst(a: *u64) void { @atomicStore(u64, a, 1, .seq_cst); }
export fn add_relaxed(a: *u64) u64 { return @atomicRmw(u64, a, .Add, 1, .monotonic); }
export fn spin(f: *u64) void { while (@atomicLoad(u64, f, .acquire) == 0) std.atomic.spinLoopHint(); }
export fn axpy(noalias a: [*]f32, noalias b: [*]const f32, n: usize) void { for (0..n) |i| a[i] += 2.0 * b[i]; }
export fn idx_checked(a: [*]const f32, n: usize, i: usize) f32 { const s = a[0..n]; return s[i]; }
export fn idx_unchecked(a: [*]const f32, n: usize, i: usize) f32 { @setRuntimeSafety(false); const s = a[0..n]; return s[i]; }
extern fn ext(x: u64) void;
export fn hinted(x: u64) u64 { var r = x; if (x == 7) { @branchHint(.unlikely); ext(x); r = x * 5; } return r + 1; }
export fn hinted_cold(x: u64) u64 { var r = x; if (x == 10) { @branchHint(.cold); ext(x); r = x * 9; } return r + 4; }
export fn unhinted(x: u64) u64 { var r = x; if (x == 9) { ext(x); r = x * 7; } return r + 3; }
export fn pf(p: [*]const u8) void { @prefetch(p, .{ .rw = .read, .locality = 3, .cache = .data }); }
fn fib(n: u64) u64 { var a: u64 = 0; var b: u64 = 1; for (0..n) |_| { const t = a + b; a = b; b = t; } return a; }
export fn fib60() u64 { return comptime fib(60); }
noinline fn gsum(comptime T: type, x: []const T) T { var s: T = 0; for (x) |v| s += v; return s; }
export fn use_both(a: [*]const f32, b: [*]const f64, n: usize) f64 { return @as(f64, gsum(f32, a[0..n])) + gsum(f64, b[0..n]); }
export fn sum_plain(a: [*]const f32, n: usize) f32 { var s: f32 = 0; for (a[0..n]) |x| s += x; return s; }
export fn sum_opt(a: [*]const f32, n: usize) f32 { @setFloatMode(.optimized); var s: f32 = 0; for (a[0..n]) |x| s += x; return s; }
