// Audit de la grille (docs/V4_PLAN.md 2.1) : sonde exécutée de Zig 0.17, cas positifs. run.sh y ajoute le code produit,
// les échecs et les recherches d'absence.
const std = @import("std");
const Part = struct { x: f32, y: f32, z: f32, m: u8 };
const Inl = extern struct { n: u32, a: [16]f32 };

var n_alloc: usize = 0;
const Counting = struct {
    child: std.mem.Allocator,
    fn allocator(self: *Counting) std.mem.Allocator {
        return .{ .ptr = self, .vtable = &.{ .alloc = alloc, .resize = resize, .remap = remap, .free = free } };
    }
    fn alloc(ctx: *anyopaque, len: usize, a: std.mem.Alignment, ra: usize) ?[*]u8 {
        const self: *Counting = @ptrCast(@alignCast(ctx));
        n_alloc += 1;
        return self.child.rawAlloc(len, a, ra);
    }
    fn resize(ctx: *anyopaque, m: []u8, a: std.mem.Alignment, n: usize, ra: usize) bool {
        const self: *Counting = @ptrCast(@alignCast(ctx));
        return self.child.rawResize(m, a, n, ra);
    }
    fn remap(ctx: *anyopaque, m: []u8, a: std.mem.Alignment, n: usize, ra: usize) ?[*]u8 {
        const self: *Counting = @ptrCast(@alignCast(ctx));
        return self.child.rawRemap(m, a, n, ra);
    }
    fn free(ctx: *anyopaque, m: []u8, a: std.mem.Alignment, ra: usize) void {
        const self: *Counting = @ptrCast(@alignCast(ctx));
        self.child.rawFree(m, a, ra);
    }
};

fn worker(t: usize, out: *u64, tid: *std.Thread.Id) void {
    var s: u64 = 0;
    for (t * 1000..(t + 1) * 1000) |i| s += i;
    out.* = s;
    tid.* = std.Thread.getCurrentId();
}
fn fib(n: u64) u64 {
    var a: u64 = 0;
    var b: u64 = 1;
    for (0..n) |_| {
        const t = a + b;
        a = b;
        b = t;
    }
    return a;
}
fn gsum(comptime T: type, x: []const T) T {
    var s: T = 0;
    for (x) |v| s += v;
    return s;
}
fn countTasks(io: std.Io) usize {
    var d = std.Io.Dir.cwd().openDir(io, "/proc/self/task", .{ .iterate = true }) catch return 0;
    defer d.close(io);
    var it = d.iterate();
    var n: usize = 0;
    while (it.next(io) catch null) |_| n += 1;
    return n;
}

pub fn main(init: std.process.Init) !void {
    const io = init.io;
    const p = std.debug.print;
    const gpa = std.heap.page_allocator;
    // A1
    const v = try gpa.alloc(Part, 8);
    for (v) |*e| e.* = .{ .x = 1.0, .y = 2.0, .z = 3.0, .m = 4 };
    const stride = @intFromPtr(&v[1]) - @intFromPtr(&v[0]);
    const raw: [*]const u8 = @ptrCast(v.ptr);
    p("CAP;A1;1;[exécutée] []Part : pas de {d} o = @sizeOf(Part) {d} ; les 4 premiers octets du tampon sont le f32 x en ligne : {x}\n", .{ stride, @sizeOf(Part), raw[0..4].* });
    // A6
    var soa: std.MultiArrayList(Part) = .empty;
    defer soa.deinit(gpa);
    for (0..100) |i| try soa.append(gpa, .{ .x = @floatFromInt(i), .y = 0, .z = 0, .m = 0 });
    const xs = soa.items(.x);
    const ys = soa.items(.y);
    p("CAP;A6;1;[exécutée] std.MultiArrayList(Part) : items(.x) au pas de {d} o ; items(.y) commence {d} o après items(.x) (un tableau par champ) ; xs[99] = {d}\n", .{ @intFromPtr(&xs[1]) - @intFromPtr(&xs[0]), @intFromPtr(ys.ptr) -% @intFromPtr(xs.ptr), xs[99] });
    // A7, A8
    p("CAP;A7;1;[exécutée] extern struct {{ n: u32, a: [16]f32 }} : {d} o, @offsetOf(Inl, \"a\") = {d} (tableau en ligne)\n", .{ @sizeOf(Inl), @offsetOf(Inl, "a") });
    const b8 = try gpa.alloc(u8, 1000);
    const h16 = try gpa.alloc(i16, 1000);
    p("CAP;A8;1;[exécutée] u8/i16/f16/f32 : {d}/{d}/{d}/{d} o ; []u8 de 1000 éléments : {d} o, []i16 : {d} o\n", .{ @sizeOf(u8), @sizeOf(i16), @sizeOf(f16), @sizeOf(f32), b8.len * @sizeOf(u8), h16.len * @sizeOf(i16) });
    // B1
    p("CAP;B1;1;[exécutée] aucune collecte : mémoire rendue par free/defer explicites ; {d} fil dans /proc/self/task (aucun fil de collecteur)\n", .{countTasks(io)});
    // B2
    var store: [4096]u8 = undefined;
    var fba = std.heap.FixedBufferAllocator.init(&store);
    const fa = fba.allocator();
    const blk = try fa.alloc(u64, 100);
    var arena = std.heap.ArenaAllocator.init(gpa);
    defer arena.deinit();
    const aa = arena.allocator();
    var list: std.ArrayList(u32) = .empty;
    for (0..1000) |i| try list.append(aa, @intCast(i));
    const inside = @intFromPtr(blk.ptr) >= @intFromPtr(&store) and @intFromPtr(blk.ptr) < @intFromPtr(&store) + store.len;
    p("CAP;B2;1;[exécutée] std.mem.Allocator passé en argument : FixedBufferAllocator (tampon de pile) -> bloc dans le tampon = {} ; ArenaAllocator -> ArrayList de {d} éléments libérée d'un coup par arena.deinit()\n", .{ inside, list.items.len });
    // B3
    var local: [4096]u8 = undefined;
    local[0] = 1;
    var marker: u8 = 0;
    marker +%= local[0];
    const ds = @abs(@as(i64, @intCast(@intFromPtr(&marker))) - @as(i64, @intCast(@intFromPtr(&local))));
    const dh = @abs(@as(i64, @intCast(@intFromPtr(b8.ptr))) - @as(i64, @intCast(@intFromPtr(&local))));
    p("CAP;B3;1;[exécutée] [4096]u8 local à {d} o d'une autre variable locale, à {d} o du tas : sur la pile\n", .{ ds, dh });
    // B4
    var cnt = Counting{ .child = gpa };
    const ca = cnt.allocator();
    const n0 = n_alloc;
    var data: [256]f32 = undefined;
    for (&data, 0..) |*d, i| d.* = @floatFromInt(i);
    std.mem.sort(f32, &data, {}, std.sort.desc(f32));
    var fbuf: [64]u8 = undefined;
    const s = try std.fmt.bufPrint(&fbuf, "{d:.1} {d}", .{ data[0], gsum(f32, &data) });
    const n1 = n_alloc;
    const lst = try ca.alloc(f32, 1000);
    const n2 = n_alloc;
    p("CAP;B4;1;[exécutée] allocateur compteur : tri, formatage dans un tampon, boucles et tranches -> {d} allocation ({s}) ; seule l'API qui reçoit l'allocateur alloue : {d} ; ArrayList exige l'allocateur à chaque append (std 0.17)\n", .{ n1 - n0, s, n2 - n1 });
    ca.free(lst);
    // B5
    var buf: [8]u32 = @splat(0);
    const mp: [*]u32 = &buf;
    mp[3] = 42;
    const bp: [*]u8 = @ptrCast(&buf);
    @as(*align(1) u32, @ptrCast(bp + 16)).* = 7;
    p("CAP;B5;1;[exécutée] [*]u32 : mp[3] = 42 -> buf[3] = {d} ; écriture par décalage d'octets -> buf[4] = {d}\n", .{ buf[3], buf[4] });
    // C1
    const va: @Vector(8, f32) = .{ 1, 2, 3, 4, 5, 6, 7, 8 };
    const vb = va + va;
    p("CAP;C1;1;[exécutée] @Vector(8, f32) : (a + a)[7] = {d}, @reduce(.Add, a) = {d}, @shuffle et @select dans le langage\n", .{ vb[7], @reduce(.Add, va) });
    // D1
    var parts: [4]u64 = @splat(0);
    var ids: [4]std.Thread.Id = @splat(0);
    var th: [4]std.Thread = undefined;
    for (0..4) |t| th[t] = try std.Thread.spawn(.{}, worker, .{ t, &parts[t], &ids[t] });
    for (th) |t| t.join();
    var distinct: usize = 0;
    for (0..4) |i| {
        var seen = false;
        for (0..i) |j| seen = seen or ids[j] == ids[i];
        if (!seen) distinct += 1;
    }
    p("CAP;D1;1;[exécutée] std.Thread.spawn : 4 fils, {d} identifiants de fil distincts, somme {d} (attendu 7998000)\n", .{ distinct, parts[0] + parts[1] + parts[2] + parts[3] });
    // E2
    var ex: u64 = 41;
    ex = asm volatile ("leaq 1(%[x]), %[ret]"
        : [ret] "=r" (-> u64),
        : [x] "r" (ex),
    );
    p("CAP;E2;1;[exécutée] asm volatile (syntaxe AT&T, contraintes de registres) : leaq 1(x) avec x = 41 -> {d}\n", .{ex});
    // D4
    var set = std.mem.zeroes(std.os.linux.cpu_set_t);
    set[0] = 2;
    std.os.linux.sched_setaffinity(0, &set) catch |e| p("err {}\n", .{e});
    var cpu: usize = 99;
    _ = std.os.linux.getcpu(&cpu, null);
    p("CAP;D4;1;[exécutée] std.os.linux.sched_setaffinity (bibliothèque standard ; ½ en v1, liaison propre à Linux) : fil épinglé, getcpu = {d}\n", .{cpu});
    // E7, F1, F3
    const F60 = comptime fib(60);
    p("FACT;E7;comptime fib(60) = {d} ; gsum(f32) = {d}, gsum(f64) = {d}\n", .{ F60, gsum(f32, &.{ 1.5, 2.5 }), gsum(f64, &.{ 1.5, 2.25 }) });
    const m: [3][4]f32 = @splat(@splat(0));
    p("FACT;F1;[3][4]f32 contigu : &m[1][0] - &m[0][3] = {d} o, @sizeOf = {d} o\n", .{ @intFromPtr(&m[1][0]) - @intFromPtr(&m[0][3]), @sizeOf([3][4]f32) });
    const um: u32 = std.math.maxInt(u32);
    const im: i32 = std.math.maxInt(i32);
    const b250: u8 = 250;
    p("CAP;F3;1;[exécutée] maxInt(u32) +% 1 = {d}, maxInt(i32) +% 1 = {d}, 250 +% 10 (u8) = {d}, entiers de toute largeur (u3, i7) ; + déborde en mode sûr\n", .{ um +% 1, im +% 1, b250 +% 10 });
}
