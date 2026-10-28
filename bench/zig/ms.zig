// Implémentation Zig 0.17 (bibliothèque standard seule). Voir docs/SPEC.md.
const std = @import("std");
const Io = std.Io;
const Allocator = std.mem.Allocator;
const Atomic = std.atomic.Value;

// ------------------------------------------------------------------ harnais
var io: Io = undefined;
var gpa: Allocator = undefined;
var out: *Io.Writer = undefined;
var warmup: i32 = 1;
var data_dir: []const u8 = "/opt/msdata";

fn nowNs() i96 {
    return Io.Clock.awake.now(io).nanoseconds;
}
fn secs(t0: i96) f64 {
    return @as(f64, @floatFromInt(nowNs() - t0)) * 1e-9;
}
fn loadBytes(name: []const u8) []align(64) u8 {
    var pbuf: [512]u8 = undefined;
    const path = std.fmt.bufPrint(&pbuf, "{s}/{s}", .{ data_dir, name }) catch unreachable;
    const raw = Io.Dir.cwd().readFileAlloc(io, path, gpa, .unlimited) catch @panic("lecture");
    // copie dans un tampon aligné sur une ligne de cache
    const a = gpa.alignedAlloc(u8, .@"64", raw.len) catch @panic("alloc");
    @memcpy(a, raw);
    gpa.free(raw);
    return a;
}
fn load(comptime T: type, name: []const u8) []align(64) T {
    const b = loadBytes(name);
    return @alignCast(std.mem.bytesAsSlice(T, b));
}
fn result(k: []const u8, v: []const u8, p: []const u8, rep: i32, sec: f64, chk: []const u8) void {
    out.print("RESULT;{s};{s};{s};{d};{d:.9};{s}\n", .{ k, v, p, rep, sec, chk }) catch {};
    out.flush() catch {};
}
var chk_buf: [128]u8 = undefined;
fn fmt(comptime f: []const u8, args: anytype) []const u8 {
    return std.fmt.bufPrint(&chk_buf, f, args) catch unreachable;
}

// ------------------------------------------------------------------ K1
const N1 = 1 << 22;
const Particle = struct {
    x: f32, y: f32, z: f32, vx: f32, vy: f32, vz: f32, ax: f32, ay: f32, az: f32,
    mass: f32, charge: f32, radius: f32, temp: f32, pressure: f32, energy: f32, density: f32,
    // struct « auto » : Zig peut réordonner les champs, d'où une construction champ par champ
    fn from(f: *const [16]f32) Particle {
        return .{ .x = f[0], .y = f[1], .z = f[2], .vx = f[3], .vy = f[4], .vz = f[5], .ax = f[6], .ay = f[7], .az = f[8],
            .mass = f[9], .charge = f[10], .radius = f[11], .temp = f[12], .pressure = f[13], .energy = f[14], .density = f[15] };
    }
};
noinline fn k1Natural(ps: []const Particle) f64 {
    var e: f64 = 0;
    for (ps) |p| e += 0.5 * @as(f64, p.mass) * @as(f64, p.vx * p.vx + p.vy * p.vy + p.vz * p.vz);
    return e;
}
noinline fn k1AoS(ps: []const Particle) f64 {
    var acc: [8]f64 = @splat(0);
    var i: usize = 0;
    while (i < ps.len) : (i += 8) {
        inline for (0..8) |k| {
            const q = &ps[i + k];
            acc[k] += @as(f64, 0.5 * q.mass * (q.vx * q.vx + q.vy * q.vy + q.vz * q.vz));
        }
    }
    var e: f64 = 0;
    for (acc) |a| e += a;
    return e;
}
// SoA : std.MultiArrayList (SoA de la bibliothèque standard) + @Vector(16, f32)
noinline fn k1SoA(vx: []const f32, vy: []const f32, vz: []const f32, m: []const f32) f64 {
    const V = @Vector(16, f32);
    const D = @Vector(8, f64);
    var a0: D = @splat(0);
    var a1: D = @splat(0);
    const h: V = @splat(0.5);
    var i: usize = 0;
    while (i < vx.len) : (i += 16) {
        const x: V = vx[i..][0..16].*;
        const y: V = vy[i..][0..16].*;
        const z: V = vz[i..][0..16].*;
        const w: V = m[i..][0..16].*;
        const e = h * w * @mulAdd(V, z, z, @mulAdd(V, y, y, x * x));
        const ea: [16]f32 = e;
        const lo: @Vector(8, f32) = ea[0..8].*;
        const hi: @Vector(8, f32) = ea[8..16].*;
        a0 += @as(D, @floatCast(lo));
        a1 += @as(D, @floatCast(hi));
    }
    return @reduce(.Add, a0 + a1);
}
fn runK1(v: []const u8, reps: i32) void {
    if (std.mem.eql(u8, v, "footprint0")) return result("k1", v, "energy", 0, 0, "0");
    const raw = load(f32, "k1_particles.f32");
    var ps: std.ArrayList(Particle) = .empty;
    ps.ensureTotalCapacity(gpa, N1) catch @panic("oom");
    for (0..N1) |i| ps.appendAssumeCapacity(Particle.from(raw[16 * i ..][0..16]));
    gpa.free(std.mem.sliceAsBytes(raw));
    if (std.mem.eql(u8, v, "footprint")) return result("k1", v, "energy", 0, 0, fmt("{d:.6}", .{k1Natural(ps.items)}));
    if (std.mem.eql(u8, v, "soa")) {
        var soa: std.MultiArrayList(Particle) = .empty;
        soa.ensureTotalCapacity(gpa, N1) catch @panic("oom");
        for (ps.items) |p| soa.appendAssumeCapacity(p);
        ps.deinit(gpa);
        const s = soa.slice();
        var r: i32 = -warmup;
        while (r < reps) : (r += 1) {
            const t0 = nowNs();
            const e = k1SoA(s.items(.vx), s.items(.vy), s.items(.vz), s.items(.mass));
            const dt = secs(t0);
            if (r >= 0) result("k1", v, "energy", r, dt, fmt("{d:.6}", .{e}));
        }
        return;
    }
    if (std.mem.eql(u8, v, "natural_shuffled")) {
        const perm = load(u32, "k1_perm.u32");
        const s = gpa.alloc(Particle, N1) catch @panic("oom");
        for (perm, 0..) |j, i| s[i] = ps.items[j];
        ps.deinit(gpa);
        ps = .fromOwnedSlice(s);
    }
    const aos = std.mem.eql(u8, v, "aos");
    var r: i32 = -warmup;
    while (r < reps) : (r += 1) {
        const t0 = nowNs();
        const e = if (aos) k1AoS(ps.items) else k1Natural(ps.items);
        const dt = secs(t0);
        if (r >= 0) result("k1", v, "energy", r, dt, fmt("{d:.6}", .{e}));
    }
}

// ------------------------------------------------------------------ K2
noinline fn k2Chase(a: []const u32, h: usize) u32 {
    var i: u32 = 0;
    for (0..h) |_| i = a[i];
    return i;
}
fn runK2(v: []const u8, reps: i32, p: []const u8) void {
    const a = load(u32, fmt("k2_chase_{s}.u32", .{p}));
    var r: i32 = -warmup;
    while (r < reps) : (r += 1) {
        const t0 = nowNs();
        const i = k2Chase(a, 4200000);
        const dt = secs(t0);
        if (r >= 0) result("k2", v, p, r, dt, fmt("{d}", .{i}));
    }
}

// ------------------------------------------------------------------ K3
const ITER3 = 1 << 25;
const Padded = struct { v: Atomic(u64) align(std.atomic.cache_line) = .init(0) };
fn k3Worker(c: *Atomic(u64), rmw: bool) void {
    if (rmw) {
        for (0..ITER3) |_| _ = c.fetchAdd(1, .monotonic);
    } else {
        for (0..ITER3) |_| c.store(c.load(.monotonic) + 1, .monotonic);
    }
}
fn runK3(v: []const u8, reps: i32) void {
    const rmw = std.mem.startsWith(u8, v, "rmw");
    const padded = std.mem.endsWith(u8, v, "padded");
    out.print("META;k3_mechanism;{s}\nMETA;cache_line;{d}\n", .{ if (rmw) "fetchAdd(.monotonic) (lock xadd)" else "load/store(.monotonic) (mov)", std.atomic.cache_line }) catch {};
    var packed_c: [4]Atomic(u64) align(64) = .{ .init(0), .init(0), .init(0), .init(0) };
    var pad: [4]Padded = @splat(.{});
    var r: i32 = -warmup;
    while (r < reps) : (r += 1) {
        var ctr: [4]*Atomic(u64) = undefined;
        for (0..4) |t| {
            ctr[t] = if (padded) &pad[t].v else &packed_c[t];
            ctr[t].store(0, .monotonic);
        }
        const t0 = nowNs();
        var th: [4]std.Thread = undefined;
        for (0..4) |t| th[t] = std.Thread.spawn(.{}, k3Worker, .{ ctr[t], rmw }) catch @panic("spawn");
        for (th) |x| x.join();
        const dt = secs(t0);
        var s: u64 = 0;
        for (ctr) |c| s += c.load(.monotonic);
        if (r >= 0) result("k3", v, "4x2^25", r, dt, fmt("{d}", .{s}));
    }
}

// ------------------------------------------------------------------ K4
noinline fn k4Natural(v: []const u8) u64 {
    var s: u64 = 0;
    for (v) |x| {
        if (x >= 128) s += x;
    }
    return s;
}
noinline fn k4Branchless(v: []const u8) u64 {
    var s: u64 = 0;
    for (v) |x| s += @as(u64, x) * (x >> 7);
    return s;
}
fn runK4(v: []const u8, reps: i32) void {
    const d = load(u8, "k4_bytes.u8");
    if (std.mem.eql(u8, v, "natural_sorted")) std.mem.sort(u8, d, {}, std.sort.asc(u8));
    const bl = std.mem.eql(u8, v, "branchless_unsorted");
    var r: i32 = -warmup;
    while (r < reps) : (r += 1) {
        const t0 = nowNs();
        const s = if (bl) k4Branchless(d) else k4Natural(d);
        const dt = secs(t0);
        if (r >= 0) result("k4", v, "16M", r, dt, fmt("{d}", .{s}));
    }
}

// ------------------------------------------------------------------ K5
const INNER5 = 1 << 16;
noinline fn k5Natural(a: []const f32, b: []const f32) f32 {
    var s: f32 = 0;
    for (a, b) |x, y| s += x * y;
    return s;
}
noinline fn k5Tuned(a: []align(64) const f32, b: []align(64) const f32) f32 {
    const V = @Vector(16, f32);
    var s: [4]V = @splat(@splat(0));
    var i: usize = 0;
    while (i < a.len) : (i += 64) {
        inline for (0..4) |k| {
            const x: V = a[i + 16 * k ..][0..16].*;
            const y: V = b[i + 16 * k ..][0..16].*;
            s[k] = @mulAdd(V, x, y, s[k]);
        }
    }
    return @reduce(.Add, (s[0] + s[1]) + (s[2] + s[3]));
}
fn runK5(v: []const u8, reps: i32) void {
    const a = load(f32, "k5_a.f32");
    const b = load(f32, "k5_b.f32");
    const tuned = std.mem.eql(u8, v, "tuned");
    var r: i32 = -warmup;
    while (r < reps) : (r += 1) {
        var d: f32 = 0;
        const t0 = nowNs();
        for (0..INNER5) |_| {
            std.mem.doNotOptimizeAway(a.ptr);
            d = if (tuned) k5Tuned(a, b) else k5Natural(a, b);
        }
        const dt = secs(t0);
        if (r >= 0) result("k5", v, "2048x65536", r, dt, fmt("{d:.4}", .{d}));
    }
}

// ------------------------------------------------------------------ K6
const N6 = 1 << 24;
const Cols = struct { sd: []align(64) i32, pr: []align(64) i32, q: []align(64) u8, d: []align(64) u8, t: []align(64) u8, rf: []align(64) u8, ls: []align(64) u8 };
const Q1Acc = [6][5]i64;
noinline fn q6Natural(c: *const Cols, lo: usize, hi: usize) i64 {
    var s: i64 = 0;
    for (lo..hi) |i| {
        if (c.sd[i] >= 8766 and c.sd[i] < 9131 and c.d[i] >= 5 and c.d[i] <= 7 and c.q[i] < 24) s += @as(i64, c.pr[i]) * c.d[i];
    }
    return s;
}
// Q6 optimisé : @Vector(16, i32), prédicat en masques, @select, accumulation i64
noinline fn q6Tuned(c: *const Cols, lo: usize, hi: usize) i64 {
    const I = @Vector(16, i32);
    var acc: @Vector(16, i64) = @splat(0);
    var i = lo;
    while (i + 16 <= hi) : (i += 16) {
        const sd: I = c.sd[i..][0..16].*;
        const d: I = @as(@Vector(16, u8), c.d[i..][0..16].*);
        const q: I = @as(@Vector(16, u8), c.q[i..][0..16].*);
        const pr: I = c.pr[i..][0..16].*;
        const m = (sd >= @as(I, @splat(8766))) & (sd < @as(I, @splat(9131))) & (d >= @as(I, @splat(5))) & (d <= @as(I, @splat(7))) & (q < @as(I, @splat(24)));
        acc += @as(@Vector(16, i64), @select(i32, m, pr * d, @as(I, @splat(0))));
    }
    return @reduce(.Add, acc) + q6Natural(c, i, hi);
}
noinline fn q1Natural(c: *const Cols, lo: usize, hi: usize, acc: *Q1Acc) void {
    for (lo..hi) |i| {
        if (c.sd[i] <= 10471) {
            const g = c.rf[i] * 2 + c.ls[i];
            const p: i64 = c.pr[i];
            const dp = p * (100 - @as(i64, c.d[i]));
            acc[g][0] += 1;
            acc[g][1] += c.q[i];
            acc[g][2] += p;
            acc[g][3] += dp;
            acc[g][4] += dp * (100 + @as(i64, c.t[i]));
        }
    }
}
// Q1 optimisé : agrégation masquée par groupe en @Vector (même algorithme que la référence C)
noinline fn q1Tuned(c: *const Cols, lo: usize, hi: usize, acc: *Q1Acc) void {
    const I = @Vector(16, i32);
    const L = @Vector(16, i64);
    const z: I = @splat(0);
    var i = lo;
    while (i + 16 <= hi) {
        var aq: [6]I = @splat(z);
        var ap: [6]I = @splat(z);
        var adp: [6]I = @splat(z);
        var ach: [6]L = @splat(@splat(0));
        var cnt: [6]i64 = @splat(0);
        const end = if (i + 4096 <= hi) i + 4096 else hi - (hi - i) % 16;
        while (i < end) : (i += 16) {
            const sd: I = c.sd[i..][0..16].*;
            const pass = sd <= @as(I, @splat(10471));
            const vg = @as(I, @as(@Vector(16, u8), c.rf[i..][0..16].*)) * @as(I, @splat(2)) + @as(I, @as(@Vector(16, u8), c.ls[i..][0..16].*));
            const vq: I = @as(@Vector(16, u8), c.q[i..][0..16].*);
            const vd: I = @as(@Vector(16, u8), c.d[i..][0..16].*);
            const vt: I = @as(I, @as(@Vector(16, u8), c.t[i..][0..16].*)) + @as(I, @splat(100));
            const vp: I = c.pr[i..][0..16].*;
            const vdp = vp * (@as(I, @splat(100)) - vd);
            const ch = @as(L, vdp) * @as(L, vt);
            inline for (0..6) |g| {
                const m = pass & (vg == @as(I, @splat(g)));
                cnt[g] += @popCount(@as(u16, @bitCast(m)));
                aq[g] += @select(i32, m, vq, z);
                ap[g] += @select(i32, m, vp, z);
                adp[g] += @select(i32, m, vdp, z);
                ach[g] += @select(i64, m, ch, @as(L, @splat(0)));
            }
        }
        for (0..6) |g| {
            acc[g][0] += cnt[g];
            acc[g][1] += @reduce(.Add, aq[g]);
            acc[g][2] += @reduce(.Add, ap[g]);
            acc[g][3] += @reduce(.Add, @as(L, adp[g]));
            acc[g][4] += @reduce(.Add, ach[g]);
        }
    }
    if (i < hi) q1Natural(c, i, hi, acc);
}
fn fold(a: *const Q1Acc) i64 {
    var s: i64 = 0;
    for (a) |row| for (row) |x| {
        s += x;
    };
    return s;
}
fn k6Worker(c: *const Cols, lo: usize, hi: usize, q1: bool, res: *i64) void {
    if (q1) {
        var a = std.mem.zeroes(Q1Acc);
        q1Tuned(c, lo, hi, &a);
        res.* = fold(&a);
    } else res.* = q6Tuned(c, lo, hi);
}
fn runK6(v: []const u8, reps: i32, p: []const u8) void {
    const c = Cols{ .sd = load(i32, "k6_shipdate.i32"), .pr = load(i32, "k6_extendedprice.i32"), .q = load(u8, "k6_quantity.u8"), .d = load(u8, "k6_discount.u8"), .t = load(u8, "k6_tax.u8"), .rf = load(u8, "k6_returnflag.u8"), .ls = load(u8, "k6_linestatus.u8") };
    const q1 = std.mem.eql(u8, p, "q1");
    var r: i32 = -warmup;
    while (r < reps) : (r += 1) {
        const t0 = nowNs();
        var s: i64 = 0;
        if (std.mem.eql(u8, v, "mt")) {
            var part: [4]i64 = @splat(0);
            var th: [4]std.Thread = undefined;
            for (0..4) |t| th[t] = std.Thread.spawn(.{}, k6Worker, .{ &c, N6 / 4 * t, N6 / 4 * (t + 1), q1, &part[t] }) catch @panic("spawn");
            for (th) |x| x.join();
            for (part) |x| s += x;
        } else if (std.mem.eql(u8, v, "tuned")) {
            if (q1) {
                var a = std.mem.zeroes(Q1Acc);
                q1Tuned(&c, 0, N6, &a);
                s = fold(&a);
            } else s = q6Tuned(&c, 0, N6);
        } else {
            if (q1) {
                var a = std.mem.zeroes(Q1Acc);
                q1Natural(&c, 0, N6, &a);
                s = fold(&a);
            } else s = q6Natural(&c, 0, N6);
        }
        const dt = secs(t0);
        if (r >= 0) result("k6", v, p, r, dt, fmt("{d}", .{s}));
    }
}

// ------------------------------------------------------------------ K7
const Agg = struct { count: u32 = 0, sum: u64 = 0 };
const Slot = extern struct { key: u32, count: u32, sum: u64 };
fn runK7(v: []const u8, reps: i32) void {
    const keys = load(u32, "k7_keys.u32");
    const vals = load(u32, "k7_vals.u32");
    var r: i32 = -warmup;
    while (r < reps) : (r += 1) {
        var nk: u64 = 0;
        var ws: u64 = 0;
        var dt: f64 = 0;
        if (std.mem.eql(u8, v, "natural")) {
            const t0 = nowNs();
            var m = std.AutoHashMap(u32, Agg).init(gpa);
            for (keys, vals) |k, x| {
                const e = m.getOrPut(k) catch @panic("oom");
                if (!e.found_existing) e.value_ptr.* = .{};
                e.value_ptr.count += 1;
                e.value_ptr.sum += x;
            }
            dt = secs(t0);
            nk = m.count();
            var it = m.iterator();
            while (it.next()) |e| ws += e.value_ptr.sum * ((e.key_ptr.* & 1023) + 1);
            m.deinit();
        } else {
            const LOG = 21;
            const CAP = 1 << LOG;
            const t0 = nowNs();
            const tab = gpa.alignedAlloc(Slot, .@"64", CAP) catch @panic("oom");
            @memset(tab, .{ .key = 0, .count = 0, .sum = 0 });
            var i: usize = 0;
            while (i < keys.len) : (i += 16) {
                var h: [16]u32 = undefined;
                inline for (0..16) |b| {
                    h[b] = (keys[i + b] *% 0x9E3779B1) >> (32 - LOG);
                    @prefetch(&tab[h[b]], .{ .rw = .write, .locality = 3 });
                }
                inline for (0..16) |b| {
                    const k = keys[i + b];
                    var s = h[b];
                    while (tab[s].count != 0 and tab[s].key != k) s = (s + 1) & (CAP - 1);
                    tab[s].key = k;
                    tab[s].count += 1;
                    tab[s].sum += vals[i + b];
                }
            }
            dt = secs(t0);
            for (tab) |e| if (e.count != 0) {
                nk += 1;
                ws += e.sum * ((e.key & 1023) + 1);
            };
            gpa.free(tab);
        }
        if (r >= 0) result("k7", v, "16M/1M", r, dt, fmt("{d}:{d}", .{ nk, ws }));
    }
}

// ------------------------------------------------------------------ K8
const Node = struct { v: i64, l: ?*Node, r: ?*Node };
fn tBuild(a: Allocator, d: u32, c: *i64) *Node {
    const n = a.create(Node) catch @panic("oom");
    n.v = c.*;
    c.* += 1;
    n.l = if (d > 0) tBuild(a, d - 1, c) else null;
    n.r = if (d > 0) tBuild(a, d - 1, c) else null;
    return n;
}
fn tSum(n: ?*const Node) i64 {
    const x = n orelse return 0;
    return x.v + tSum(x.l) + tSum(x.r);
}
fn tFree(a: Allocator, n: ?*Node) void {
    const x = n orelse return;
    tFree(a, x.l);
    tFree(a, x.r);
    a.destroy(x);
}
const ANode = struct { v: i64, l: i32, r: i32 };
fn aBuild(a: *[2047]ANode, top: *i32, d: u32, c: *i64) i32 {
    const i = top.*;
    top.* += 1;
    a[@intCast(i)] = .{ .v = c.*, .l = -1, .r = -1 };
    c.* += 1;
    if (d > 0) {
        const l = aBuild(a, top, d - 1, c);
        const r = aBuild(a, top, d - 1, c);
        a[@intCast(i)].l = l;
        a[@intCast(i)].r = r;
    }
    return i;
}
fn aSum(a: *const [2047]ANode, i: i32) i64 {
    if (i < 0) return 0;
    const n = a[@intCast(i)];
    return n.v + aSum(a, n.l) + aSum(a, n.r);
}
fn runK8(v: []const u8, reps: i32) void {
    const Q = 16384;
    const tuned = std.mem.eql(u8, v, "tuned");
    const talloc = std.mem.eql(u8, v, "tuned_alloc");
    const nodes = gpa.create([2047]ANode) catch @panic("oom");
    var c0: i64 = 0;
    const keep = tBuild(gpa, 20, &c0);
    const lsum = tSum(keep);
    const lat = gpa.alloc(u64, Q) catch @panic("oom");
    var arena = std.heap.ArenaAllocator.init(gpa);
    var r: i32 = -warmup;
    while (r < reps) : (r += 1) {
        var total: i64 = 0;
        const t0 = nowNs();
        for (0..Q) |q| {
            const a = nowNs();
            var c: i64 = @intCast(q);
            var s: i64 = undefined;
            if (tuned) { // nœuds compacts indexés dans un tableau réutilisé (DOD)
                var top: i32 = 0;
                s = aSum(nodes, aBuild(nodes, &top, 10, &c));
            } else if (talloc) { // arène : libération en bloc, capacité conservée -> plus d'appel système
                s = tSum(tBuild(arena.allocator(), 10, &c));
                _ = arena.reset(.retain_capacity);
            } else {
                const t = tBuild(gpa, 10, &c);
                s = tSum(t);
                tFree(gpa, t);
            }
            total += s;
            lat[q] = @intCast(nowNs() - a);
        }
        const dt = secs(t0);
        if (r >= 0) {
            result("k8", v, "16384x2047", r, dt, fmt("{d}", .{total + lsum}));
            std.mem.sort(u64, lat, {}, std.sort.asc(u64));
            out.print("LAT;{s};{d};{d};{d};{d};{d}\n", .{ v, lat[Q / 2], lat[Q * 9 / 10], lat[Q * 99 / 100], lat[Q * 999 / 1000], lat[Q - 1] }) catch {};
            out.flush() catch {};
        }
    }
    tFree(gpa, keep);
}

// ------------------------------------------------------------------ K9
const M9 = 2048;
fn k9Init(i: usize, j: usize) f64 {
    return @as(f64, @floatFromInt((i * 31 + j * 17) % 1024)) / 1024.0;
}
// naturel : type tableau 2D de taille connue à la compilation (contigu)
noinline fn k9Natural(in: *const [M9][M9]f64, o: *[M9][M9]f64) void {
    for (1..M9 - 1) |i| {
        for (1..M9 - 1) |j| o[i][j] = 0.25 * (((in[i - 1][j] + in[i + 1][j]) + in[i][j - 1]) + in[i][j + 1]);
    }
}
noinline fn k9Rows(in: []const f64, o: []f64, r0: usize, r1: usize) void {
    const V = @Vector(8, f64);
    const q4: V = @splat(0.25);
    for (r0..r1) |i| {
        const up = in[(i - 1) * M9 ..];
        const mid = in[i * M9 ..];
        const dn = in[(i + 1) * M9 ..];
        const op = o[i * M9 ..];
        var j: usize = 1;
        while (j + 8 <= M9 - 1) : (j += 8) {
            const u: V = up[j..][0..8].*;
            const d: V = dn[j..][0..8].*;
            const l: V = mid[j - 1 ..][0..8].*;
            const rr: V = mid[j + 1 ..][0..8].*;
            op[j..][0..8].* = q4 * (((u + d) + l) + rr);
        }
        while (j < M9 - 1) : (j += 1) op[j] = 0.25 * (((up[j] + dn[j]) + mid[j - 1]) + mid[j + 1]);
    }
}
fn runK9(v: []const u8, reps: i32) void {
    var r: i32 = -warmup;
    while (r < reps) : (r += 1) {
        var s: f64 = 0;
        var dt: f64 = 0;
        if (std.mem.eql(u8, v, "natural")) {
            var a = gpa.create([M9][M9]f64) catch @panic("oom");
            var b = gpa.create([M9][M9]f64) catch @panic("oom");
            for (0..M9) |i| for (0..M9) |j| {
                a[i][j] = k9Init(i, j);
                b[i][j] = a[i][j];
            };
            const t0 = nowNs();
            for (0..4) |_| {
                k9Natural(a, b);
                std.mem.swap(*[M9][M9]f64, &a, &b);
            }
            dt = secs(t0);
            for (a) |row| for (row) |x| {
                s += x;
            };
            gpa.destroy(a);
            gpa.destroy(b);
        } else {
            var a = gpa.alignedAlloc(f64, .@"64", M9 * M9) catch @panic("oom");
            var b = gpa.alignedAlloc(f64, .@"64", M9 * M9) catch @panic("oom");
            for (0..M9 * M9) |k| {
                a[k] = k9Init(k / M9, k % M9);
                b[k] = a[k];
            }
            const t0 = nowNs();
            for (0..4) |_| {
                if (std.mem.eql(u8, v, "tuned")) k9Rows(a, b, 1, M9 - 1) else {
                    var th: [4]std.Thread = undefined;
                    for (0..4) |t| th[t] = std.Thread.spawn(.{}, k9Rows, .{ a, b, 1 + (M9 - 2) * t / 4, 1 + (M9 - 2) * (t + 1) / 4 }) catch @panic("spawn");
                    for (th) |x| x.join();
                }
                std.mem.swap([]align(64) f64, &a, &b);
            }
            dt = secs(t0);
            for (a) |x| s += x;
            gpa.free(a);
            gpa.free(b);
        }
        if (r >= 0) result("k9", v, "2048^2x4", r, dt, fmt("{e:.15}", .{s}));
    }
}

// ------------------------------------------------------------------ K10
const M10 = 1 << 22;
const CAP10 = 1 << 14;
const Spsc = struct {
    write_idx: Atomic(usize) align(std.atomic.cache_line) = .init(0),
    read_idx: Atomic(usize) align(std.atomic.cache_line) = .init(0),
    buf: [CAP10]u64 align(std.atomic.cache_line) = undefined,
};
fn spscProd(q: *Spsc) void {
    var w: usize = 0;
    var rc: usize = 0;
    var x: u64 = 1;
    while (x <= M10) : (x += 1) {
        while (w - rc == CAP10) {
            rc = q.read_idx.load(.acquire);
            if (w - rc == CAP10) std.atomic.spinLoopHint();
        }
        q.buf[w & (CAP10 - 1)] = x;
        w += 1;
        q.write_idx.store(w, .release);
    }
}
fn spscCons(q: *Spsc, res: *u64) void {
    var rd: usize = 0;
    var wc: usize = 0;
    var s: u64 = 0;
    for (0..M10) |_| {
        while (rd == wc) {
            wc = q.write_idx.load(.acquire);
            if (rd == wc) std.atomic.spinLoopHint();
        }
        s += q.buf[rd & (CAP10 - 1)];
        rd += 1;
        q.read_idx.store(rd, .release);
    }
    res.* = s;
}
fn ioqProd(q: *Io.Queue(u64)) void {
    var x: u64 = 1;
    while (x <= M10) : (x += 1) q.putOneUncancelable(io, x) catch @panic("queue");
}
fn ioqCons(q: *Io.Queue(u64), res: *u64) void {
    var s: u64 = 0;
    for (0..M10) |_| s += q.getOneUncancelable(io) catch @panic("queue");
    res.* = s;
}
fn runK10(v: []const u8, reps: i32) void {
    var r: i32 = -warmup;
    while (r < reps) : (r += 1) {
        var s: u64 = 0;
        const t0 = nowNs();
        if (std.mem.eql(u8, v, "natural")) { // std.Io.Queue : file bloquante de la bibliothèque standard
            const buf = gpa.alloc(u64, CAP10) catch @panic("oom");
            var q = Io.Queue(u64).init(buf);
            const c = std.Thread.spawn(.{}, ioqCons, .{ &q, &s }) catch @panic("spawn");
            const p = std.Thread.spawn(.{}, ioqProd, .{&q}) catch @panic("spawn");
            p.join();
            c.join();
            gpa.free(buf);
        } else {
            const q = gpa.create(Spsc) catch @panic("oom");
            q.* = .{};
            const c = std.Thread.spawn(.{}, spscCons, .{ q, &s }) catch @panic("spawn");
            const p = std.Thread.spawn(.{}, spscProd, .{q}) catch @panic("spawn");
            p.join();
            c.join();
            gpa.destroy(q);
        }
        const dt = secs(t0);
        if (r >= 0) result("k10", v, "2^22", r, dt, fmt("{d}", .{s}));
    }
}

pub fn main(init: std.process.Init) !void {
    io = init.io;
    gpa = std.heap.smp_allocator; // allocateur généraliste multi-thread de la bibliothèque standard
    var obuf: [4096]u8 = undefined;
    var ow = Io.File.stdout().writer(io, &obuf);
    out = &ow.interface;
    if (init.environ_map.get("WARMUP")) |w| warmup = std.fmt.parseInt(i32, w, 10) catch 1;
    if (init.environ_map.get("MS_DATA")) |d| data_dir = d;
    const args = try init.minimal.args.toSlice(init.arena.allocator());
    const k = args[1];
    const v = args[2];
    const reps = try std.fmt.parseInt(i32, args[3], 10);
    const p: []const u8 = if (args.len > 4) args[4] else "";
    if (std.mem.eql(u8, k, "k1")) runK1(v, reps)
    else if (std.mem.eql(u8, k, "k2")) runK2(v, reps, p)
    else if (std.mem.eql(u8, k, "k3")) runK3(v, reps)
    else if (std.mem.eql(u8, k, "k4")) runK4(v, reps)
    else if (std.mem.eql(u8, k, "k5")) runK5(v, reps)
    else if (std.mem.eql(u8, k, "k6")) runK6(v, reps, p)
    else if (std.mem.eql(u8, k, "k7")) runK7(v, reps)
    else if (std.mem.eql(u8, k, "k8")) runK8(v, reps)
    else if (std.mem.eql(u8, k, "k9")) runK9(v, reps)
    else if (std.mem.eql(u8, k, "k10")) runK10(v, reps);
}
