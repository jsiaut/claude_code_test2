export fn sum_opt(p: [*]const f32, n: usize) f32 {
    @setFloatMode(.optimized);
    var s: f32 = 0;
    for (p[0..n]) |x| s += x;
    return s;
}
export fn sum_plain(p: [*]const f32, n: usize) f32 {
    var s: f32 = 0;
    for (p[0..n]) |x| s += x;
    return s;
}
