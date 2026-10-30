// Sonde Zig 0.17.
const std = @import("std");
const S = extern struct { a: u8, b: u32, c: f64 };
const P = packed struct { x: u3, y: u5, z: u8 };
const L = struct { v: i32 align(64) };
const U = extern union { f: f32, u: u32 };
pub fn main() !void {
    std.debug.print("CAP;A2;1;@offsetOf(S, \"c\")={d}\n", .{@offsetOf(S, "c")});
    std.debug.print("CAP;A3;1;packed struct u3/u5/u8 : @bitSizeOf={d}\n", .{@bitSizeOf(P)});
    std.debug.print("CAP;A4;1;align(64) : @alignOf(L)={d}\n", .{@alignOf(L)});
    const u = U{ .f = 1.0 };
    std.debug.print("CAP;A5;1;extern union 0x{x} @bitCast 0x{x}\n", .{ u.u, @as(u32, @bitCast(@as(f32, 1.0))) });
    var acc: f32 = 0;
    {
        @setFloatMode(.optimized);
        for (0..64) |i| acc += @floatFromInt(i);
    }
    std.debug.print("CAP;C4;1;@setFloatMode(.optimized) par portée : {d}\n", .{acc});
    var x: u32 = 1;
    if (x == 1) {
        @branchHint(.likely);
        x += 1;
    }
    std.debug.print("CAP;E3;1;@branchHint(.likely) : {d}\n", .{x});
    const arr: [64]u8 = @splat(0);
    @prefetch(&arr, .{ .rw = .read, .locality = 3, .cache = .data });
    std.debug.print("CAP;E4;1;@prefetch\n", .{});
    std.debug.print("CAP;D3;1;std.atomic.cache_line={d}\n", .{std.atomic.cache_line});
    std.atomic.spinLoopHint();
    std.debug.print("CAP;D5;0.5;spinLoopHint ; pas de @fence\n", .{});
    const fd = try std.posix.openat(std.posix.AT.FDCWD, "/opt/msdata/k5_a.f32", .{}, 0);
    const m = try std.posix.mmap(null, 8192, .{ .READ = true }, .{ .TYPE = .PRIVATE }, fd, 0);
    const fl = std.mem.bytesAsSlice(f32, m);
    // F4 est notée par probe_f4.zig (std.Io.File.MemoryMap, portable) depuis la correction du 30/10 (docs/ZIG.md)
    std.debug.print("INFO;F4;std.posix.mmap (liaison POSIX) + bytesAsSlice : {d}\n", .{fl[0]});
}
