// Noyaux K4 et K9 naturels de bench/zig/ms.zig, corps de boucle inchangés, exportés pour un pilote C commun.
const M9 = 2048;
export fn k4_natural(p: [*]const u8, n: usize) u64 {
    const v = p[0..n];
    var s: u64 = 0;
    for (v) |x| {
        if (x >= 128) s += x;
    }
    return s;
}
export fn k4_branchless(p: [*]const u8, n: usize) u64 {
    const v = p[0..n];
    var s: u64 = 0;
    for (v) |x| s += @as(u64, x) * (x >> 7);
    return s;
}
export fn k9_natural(in: *const [M9][M9]f64, o: *[M9][M9]f64) void {
    for (1..M9 - 1) |i| {
        for (1..M9 - 1) |j| o[i][j] = 0.25 * (((in[i - 1][j] + in[i + 1][j]) + in[i][j - 1]) + in[i][j + 1]);
    }
}
