// Coût d'un lancement de 4 tâches par Io.Group.concurrent puis await (pool d'Io.Threaded), 200 fois.
const std = @import("std");
fn work(x: *u64) void {
    x.* +%= 1;
}
pub fn main(init: std.process.Init) !void {
    const io = init.io;
    var best: f64 = 1e9;
    var tot: f64 = 0;
    var cnt: [4]u64 = @splat(0);
    for (0..200) |rep| {
        const t0 = std.Io.Clock.awake.now(io).nanoseconds;
        var g: std.Io.Group = .init;
        for (0..4) |t| try g.concurrent(io, work, .{&cnt[t]});
        try g.await(io);
        const dt = @as(f64, @floatFromInt(std.Io.Clock.awake.now(io).nanoseconds - t0)) / 4.0 / 1000.0;
        if (rep >= 10) {
            best = @min(best, dt);
            tot += dt;
        }
    }
    var buf: [256]u8 = undefined;
    const s = try std.fmt.bufPrint(&buf, "par tâche : min {d:.1} us, moyenne {d:.1} us ({d})\n", .{ best, tot / 190.0, cnt[0] });
    try std.Io.File.stdout().writeStreamingAll(io, s);
}
