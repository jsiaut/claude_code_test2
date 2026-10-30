const std = @import("std");
const linux = std.os.linux;

var flag = std.atomic.Value(u32).init(0);
var data: u32 = 0;

fn consumer() void {
    while (flag.load(.monotonic) == 0) std.atomic.spinLoopHint();
    std.debug.print("thread saw {d}\n", .{@atomicLoad(u32, &data, .acquire)});
}

fn slow(x: i32) i32 {
    @branchHint(.cold);
    return x * 3;
}

fn vaddzmm(a: @Vector(16, f32), b: @Vector(16, f32)) @Vector(16, f32) {
    return asm ("vaddps %[b], %[a], %[ret]"
        : [ret] "=v" (-> @Vector(16, f32)),
        : [a] "v" (a),
          [b] "v" (b),
    );
}

pub fn main() !void {
    const a: @Vector(8, f32) = .{ 1, 2, 3, 4, 5, 6, 7, 8 };
    const b = a * a + a;
    std.debug.print("@Vector ok {d} reduce={d}\n", .{ b[7], @reduce(.Add, b) });
    var arr: [128]i32 = undefined;
    @prefetch(&arr[64], .{ .rw = .read, .locality = 3, .cache = .data });
    const x: i32 = 5;
    if (x > 0) {
        @branchHint(.likely);
        std.debug.print("branchHint ok\n", .{});
    } else std.debug.print("{d}\n", .{slow(x)});
    const t = try std.Thread.spawn(.{}, consumer, .{});
    @atomicStore(u32, &data, 42, .release);
    flag.store(1, .release);
    t.join();
    std.debug.print("cache_line={d} cpus={d}\n", .{ std.atomic.cache_line, try std.Thread.getCpuCount() });
    var set: linux.cpu_set_t = std.mem.zeroes(linux.cpu_set_t);
    set[0] = 1;
    linux.sched_setaffinity(0, &set) catch |e| std.debug.print("aff err {}\n", .{e});
    std.debug.print("sched_setaffinity ok\n", .{});
    if (std.Target.x86.featureSetHas(@import("builtin").cpu.features, .avx512f)) {
        const z: @Vector(16, f32) = @splat(1.5);
        std.debug.print("asm zmm {d}\n", .{vaddzmm(z, z)[0]});
    }
}
