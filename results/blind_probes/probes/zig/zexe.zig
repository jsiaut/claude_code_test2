const std = @import("std");
noinline fn sum_opt(v: []const f32) f32 {
    @setFloatMode(.optimized);
    var s: f32 = 0;
    for (v) |x| s += x;
    return s;
}
noinline fn isum(v: []const i32) i32 {
    var s: i32 = 0;
    for (v) |x| s +%= x;
    return s;
}
pub fn main() void {
    var a: [4096]f32 = undefined;
    var b: [4096]i32 = undefined;
    for (&a, &b, 0..) |*x, *y, i| { x.* = @floatFromInt(i); y.* = @intCast(i); }
    std.mem.doNotOptimizeAway(&a);
    std.mem.doNotOptimizeAway(&b);
    std.debug.print("{d} {d}\n", .{ sum_opt(&a), isum(&b) });
}
