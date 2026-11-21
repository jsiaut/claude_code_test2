// Sonde de mode (v4, point 3 : docs/V4_EQUAL.md, 4) : « 1d » : tranche allouée, « 2d » : *[4][M]f64 (comme k9Natural).
const std = @import("std");
const M = 64;
pub fn main(init: std.process.Init) !void {
    const gpa = std.heap.smp_allocator;
    const args = try init.minimal.args.toSlice(init.arena.allocator());
    const n = try std.fmt.parseInt(usize, args[2], 10);
    if (args[1][0] == '1') {
        const a = try gpa.alloc(f64, n);
        @memset(a, 1.0);
        std.debug.print("{d}\n", .{a[n]});
    } else {
        const g = try gpa.create([4][M]f64);
        for (g) |*r| @memset(r, 1.0);
        std.debug.print("{d}\n", .{g[1][n]});
    }
}
