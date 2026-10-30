export fn isum(p: [*]const i32, n: usize) i32 {
    var s: i32 = 0;
    for (p[0..n]) |x| s +%= x;
    return s;
}
export fn fsum_opt2(p: [*]const f32, n: usize) f32 {
    @setFloatMode(.optimized);
    var s: f32 = 0;
    var i: usize = 0;
    while (i < n) : (i += 1) s += p[i];
    return s;
}
export fn fmul_opt(p: [*]f32, n: usize) void {
    for (p[0..n]) |*x| x.* = x.* * 2.0;
}
