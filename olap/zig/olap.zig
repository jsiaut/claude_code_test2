// v7 (docs/V7.md ; olap/SPEC.md) : le banc OLAP en Zig. Même architecture que la référence (olap/c/olap.c), écrite
// avec les moyens du langage : routines par largeur et tables calculées à la compilation (comptime), pointeurs
// bruts sur de la mémoire prise au système, fils persistants. Le fichier racine (olap_p.zig ou olap_s.zig) fixe le
// niveau : la constante `special` choisit, à la compilation, les primitives portables ou spécialisées.
//
// Usage : olap <requête> <fils> <répétitions> <répertoire des données> [--print]
const std = @import("std");
const linux = std.os.linux;
const Io = std.Io;
const special: bool = @import("root").special;

const PBITS = 10; // bits de partition
const VEC = 2048; // lignes d'un vecteur
const CHUNK = 16384; // octets utiles d'un morceau de tampon de partition
const BLOCK = 65536; // lignes d'un bloc : un morceau
const NPART = 1 << PBITS; // partitions des grandes tables
const MAXT = 64; // fils au plus
const ARENA_BLOCK: usize = 32 << 20; // octets d'un bloc d'arène
const HUGE_PAGE: usize = 1 << 21; // octets d'une page large
const K1: u64 = 0x9E3779B97F4A7C15;
const K2: u64 = 0xC2B2AE3D27D4EB4F;

var io: Io = undefined;

fn die(msg: []const u8) noreturn {
    std.debug.print("olap : {s}\n", .{msg});
    std.process.exit(2);
}

// ------------------------------------------------------------------------------------------------ mémoire, arènes
/// Toute la mémoire du programme (colonnes chargées, arènes, vecteurs de travail) vient du système par zones alignées
/// sur 2 Mio et signalées comme pages larges.
fn hugeAlloc(size: usize) [*]align(64) u8 {
    const n = (size + HUGE_PAGE - 1) & ~(HUGE_PAGE - 1);
    const r = linux.mmap(null, n + HUGE_PAGE, .{ .READ = true, .WRITE = true }, .{ .TYPE = .PRIVATE, .ANONYMOUS = true }, -1, 0);
    if (linux.errno(r) != .SUCCESS) die("mémoire");
    const p = (r + HUGE_PAGE - 1) & ~(HUGE_PAGE - 1);
    _ = linux.madvise(@ptrFromInt(p), n, linux.MADV.HUGEPAGE);
    return @ptrFromInt(p);
}

/// Une arène par fil : allocation par déplacement d'un pointeur, remise à zéro à chaque exécution ; la mémoire est
/// gardée d'une répétition à l'autre.
const ArenaBlock = extern struct { next: ?*ArenaBlock, cap: usize, used: usize, pad: [40]u8 }; // 64 octets
const Arena = struct {
    first: ?*ArenaBlock = null,
    cur: ?*ArenaBlock = null,

    fn alloc(a: *Arena, size: usize) [*]align(64) u8 {
        const n = (size + 63) & ~@as(usize, 63);
        while (true) {
            if (a.cur) |b| {
                if (b.used + n <= b.cap) {
                    const p: [*]align(64) u8 = @ptrFromInt(@intFromPtr(b) + 64 + b.used);
                    b.used += n;
                    return p;
                }
                if (b.next) |nx| {
                    if (nx.cap >= n) {
                        a.cur = nx;
                        nx.used = 0;
                        continue;
                    }
                }
            }
            const cap = @max(n, ARENA_BLOCK - 64);
            const nb: *ArenaBlock = @ptrCast(hugeAlloc(64 + cap));
            nb.cap = cap;
            nb.used = 0;
            if (a.cur) |b| {
                nb.next = b.next;
                b.next = nb;
            } else {
                nb.next = null;
                a.first = nb;
            }
            a.cur = nb;
        }
    }
    fn array(a: *Arena, comptime T: type, n: usize) [*]T {
        return @ptrCast(@alignCast(a.alloc(n * @sizeOf(T))));
    }
    fn reset(a: *Arena) void {
        a.cur = a.first;
        if (a.cur) |b| b.used = 0;
    }
};

// ------------------------------------------------------------------------------------------------ fils persistants
/// Les fils sont créés une fois et attendent, bloqués, entre deux phases.
const Pool = struct {
    n: usize = 1,
    mu: Io.Mutex = .init,
    work: Io.Condition = .init,
    done: Io.Condition = .init,
    func: *const fn (*anyopaque, usize) void = undefined,
    ctx: *anyopaque = undefined,
    gen: u64 = 0,
    pending: usize = 0,

    fn worker(p: *Pool, tid: usize) void {
        var seen: u64 = 0;
        while (true) {
            p.mu.lockUncancelable(io);
            while (p.gen == seen) p.work.waitUncancelable(io, &p.mu);
            seen = p.gen;
            const f = p.func;
            const c = p.ctx;
            p.mu.unlock(io);
            f(c, tid);
            p.mu.lockUncancelable(io);
            p.pending -= 1;
            if (p.pending == 0) p.done.broadcast(io);
            p.mu.unlock(io);
        }
    }
    fn start(p: *Pool, n: usize) void {
        p.n = n;
        for (1..n) |tid| {
            const th = std.Thread.spawn(.{}, worker, .{ p, tid }) catch die("fil");
            th.detach();
        }
    }
    /// Exécute q.f(tid) sur tous les fils (le fil principal est le fil 0) et attend la fin de tous.
    fn run(p: *Pool, q: anytype, comptime f: fn (@TypeOf(q), usize) void) void {
        const Q = @TypeOf(q);
        const call = struct {
            fn call(c: *anyopaque, tid: usize) void {
                f(@as(Q, @ptrCast(@alignCast(c))), tid);
            }
        }.call;
        if (p.n > 1) {
            p.mu.lockUncancelable(io);
            p.func = call;
            p.ctx = @ptrCast(q);
            p.pending = p.n - 1;
            p.gen += 1;
            p.work.broadcast(io);
            p.mu.unlock(io);
        }
        f(q, 0);
        if (p.n > 1) {
            p.mu.lockUncancelable(io);
            while (p.pending != 0) p.done.waitUncancelable(io, &p.mu);
            p.mu.unlock(io);
        }
    }
};
var pool: Pool = .{};

/// Compteur de morceaux partagé : la seule opération atomique.
const Counter = struct {
    next: std.atomic.Value(u64) = .init(0),
    n: u64 = 0,
    fn set(c: *Counter, n: u64) void {
        c.next.store(0, .monotonic);
        c.n = n;
    }
    inline fn take(c: *Counter) ?usize {
        const i = c.next.fetchAdd(1, .monotonic);
        return if (i < c.n) i else null;
    }
};

// ------------------------------------------------------------------------------------------------ colonnes
const Entry = extern struct { min: i64, max: i64, data_off: u64, aux_off: u64, width: u32, count: u32 };
const Col = struct {
    nrows: u64 = 0,
    nblocks: u64 = 0,
    aux_count: u64 = 0,
    dir: [*]const Entry = undefined,
    data: [*]const u64 = undefined,
    aux: [*]const u8 = undefined,

    fn words(c: *const Col, b: usize) [*]const u64 {
        return c.data + c.dir[b].data_off / 8;
    }
    /// Entrée d'un dictionnaire : ses octets suivent la table des positions.
    fn dict(c: *const Col, code: usize) []const u8 {
        const pos: [*]align(1) const u32 = @ptrCast(c.aux);
        return (c.aux + 4 * (c.aux_count + 1))[pos[code]..pos[code + 1]];
    }
};
var data_dir: []const u8 = "";

fn colOpen(table: []const u8, name: []const u8) Col {
    var buf: [4096]u8 = undefined;
    const text = std.fmt.bufPrint(buf[0..4095], "{s}/{s}/{s}.msc", .{ data_dir, table, name }) catch die("chemin");
    buf[text.len] = 0;
    const path: [*:0]const u8 = @ptrCast(text.ptr);
    const fd_r = linux.open(path, .{ .ACCMODE = .RDONLY }, 0);
    if (linux.errno(fd_r) != .SUCCESS) die(text);
    const fd: linux.fd_t = @intCast(fd_r);
    const size: usize = @intCast(linux.lseek(fd, 0, linux.SEEK.END));
    const base = hugeAlloc(size + 64); // la colonne est lue en entier, en pages larges, avec 64 octets nuls de marge
    var off: usize = 0;
    while (off < size) {
        const r = linux.pread(fd, base + off, size - off, @intCast(off));
        if (linux.errno(r) != .SUCCESS or r == 0) die("lecture");
        off += r;
    }
    _ = linux.close(fd);
    if (!std.mem.eql(u8, base[0..4], "MSC1")) die("format");
    const h32: [*]const u32 = @ptrCast(base + 4);
    const h64: [*]const u64 = @ptrCast(base + 16);
    if (h32[2] != BLOCK) die("taille de bloc");
    return .{
        .nrows = h64[0],
        .nblocks = h64[1],
        .dir = @ptrCast(@alignCast(base + h64[2])),
        .data = @ptrCast(@alignCast(base + h64[3])),
        .aux = base + h64[4],
        .aux_count = h64[5],
    };
}

// ------------------------------------------------------------------------------------------------ décodage
// Une routine par largeur, engendrée à la compilation : un groupe de 64 valeurs occupe W mots ; les positions sont
// des constantes. Niveau portable, deux formes : quand W divise 64, chaque valeur tient dans un mot ; sinon, deux
// mots voisins sont toujours combinés, sans test, et les 64 affectations sont déroulées (inline for). Niveau
// spécialisé : seize valeurs à la fois (largeur de 25 bits au plus) ; une permutation d'octets, calculée à la
// compilation pour chaque largeur, amène dans chaque voie de 32 bits les 4 octets où commence sa valeur, un décalage
// par voie la cale, un masque la borne ; au-delà de 25 bits, huit valeurs à la fois dans des voies de 64 bits.
const UnpackFn = *const fn (noalias in: [*]const u64, noalias out: [*]i32, n: usize, base: u32) void;

fn unpackPortable(comptime w: comptime_int) UnpackFn {
    return &struct {
        fn f(noalias in0: [*]const u64, noalias out0: [*]i32, n: usize, base: u32) void {
            var in = in0;
            var out = out0;
            const mask: u64 = (1 << w) - 1;
            var g: usize = 0;
            while (g < n) : (g += 64) {
                if (64 % w == 0) {
                    for (0..64) |j| {
                        const bit = j * w;
                        out[j] = @bitCast(@as(u32, @truncate((in[bit >> 6] >> @intCast(bit & 63)) & mask)) +% base);
                    }
                } else {
                    inline for (0..64) |j| {
                        const idx = (j * w) >> 6;
                        const sh = (j * w) & 63;
                        const v = (in[idx] >> sh) | ((in[idx + 1] << 1) << (63 - sh));
                        out[j] = @bitCast(@as(u32, @truncate(v & mask)) +% base);
                    }
                }
                in += w;
                out += 64;
            }
        }
    }.f;
}

fn unpackSpecial(comptime w: comptime_int) UnpackFn {
    return &struct {
        fn f(noalias in0: [*]const u64, noalias out: [*]i32, n: usize, base: u32) void {
            var p: [*]const u8 = @ptrCast(in0);
            var i: usize = 0;
            if (w <= 25) {
                const idx: @Vector(64, i32) = comptime blk: {
                    var t: [64]i32 = undefined;
                    for (0..16) |j| for (0..4) |k| {
                        t[4 * j + k] = ((j * w) >> 3) + k;
                    };
                    break :blk t;
                };
                const sh: @Vector(16, u5) = comptime blk: {
                    var t: [16]u5 = undefined;
                    for (0..16) |j| t[j] = (j * w) & 7;
                    break :blk t;
                };
                const mask: @Vector(16, u32) = @splat((1 << w) - 1);
                const vb: @Vector(16, u32) = @splat(base);
                while (i < n) : (i += 16) {
                    const bytes: @Vector(64, u8) = p[0..64].*;
                    const x: @Vector(16, u32) = @bitCast(@shuffle(u8, bytes, undefined, idx));
                    out[i..][0..16].* = @bitCast(((x >> sh) & mask) +% vb);
                    p += 2 * w;
                }
            } else {
                const idx: @Vector(64, i32) = comptime blk: {
                    var t: [64]i32 = undefined;
                    for (0..8) |j| for (0..8) |k| {
                        t[8 * j + k] = ((j * w) >> 3) + k;
                    };
                    break :blk t;
                };
                const sh: @Vector(8, u6) = comptime blk: {
                    var t: [8]u6 = undefined;
                    for (0..8) |j| t[j] = (j * w) & 7;
                    break :blk t;
                };
                const mask: @Vector(8, u64) = @splat((1 << w) - 1);
                const vb: @Vector(8, u32) = @splat(base);
                while (i < n) : (i += 8) {
                    const bytes: @Vector(64, u8) = p[0..64].*;
                    const x: @Vector(8, u64) = @bitCast(@shuffle(u8, bytes, undefined, idx));
                    const v: @Vector(8, u32) = @truncate((x >> sh) & mask);
                    out[i..][0..8].* = @bitCast(v +% vb);
                    p += w;
                }
            }
        }
    }.f;
}
const unpack_fn: [33]?UnpackFn = blk: {
    var t: [33]?UnpackFn = @splat(null);
    for (1..33) |w| t[w] = if (special) unpackSpecial(w) else unpackPortable(w);
    break :blk t;
};

/// Décode n valeurs du bloc b à partir de la ligne start (multiple de 64) ; écrit des groupes entiers (de 64 valeurs
/// au niveau portable, de 16 au niveau spécialisé).
fn unpack(c: *const Col, b: usize, start: usize, n: usize, out: [*]i32) void {
    const e = &c.dir[b];
    if (e.width == 0) {
        @memset(out[0..n], @truncate(e.min));
        return;
    }
    unpack_fn[e.width].?(c.words(b) + start / 64 * e.width, out, n, @bitCast(@as(i32, @truncate(e.min))));
}
/// Décode les valeurs du bloc b aux positions pos (lignes dans le bloc), dans l'ordre : out[i] est celle de pos[i].
fn unpackSel(c: *const Col, b: usize, pos: []const i32, out: [*]i32) void {
    const e = &c.dir[b];
    const in = c.words(b);
    const w: u64 = e.width;
    const base: u32 = @bitCast(@as(i32, @truncate(e.min)));
    if (w == 0) {
        @memset(out[0..pos.len], @bitCast(base));
        return;
    }
    const mask = (@as(u64, 1) << @intCast(w)) - 1;
    for (pos, 0..) |p, i| {
        const bit = @as(u64, @intCast(p)) * w;
        const idx = bit >> 6;
        const sh: u6 = @intCast(bit & 63);
        const v = (in[idx] >> sh) | ((in[idx + 1] << 1) << (63 - sh));
        out[i] = @bitCast(@as(u32, @truncate(v & mask)) +% base);
    }
}

// ------------------------------------------------------------------------------------------------ hachage
inline fn load64(p: [*]const u8) u64 {
    return @as(*align(1) const u64, @ptrCast(p)).*;
}
inline fn hash64(k: u64) u64 {
    const x = k *% K1;
    return x ^ (x >> 32);
}
/// Octets : deux voies de mots de 64 bits ; le dernier mot, incomplet, est masqué (8 octets lisibles après la fin).
inline fn hashBytes(ptr: [*]const u8, len: usize) u64 {
    var p = ptr;
    var n = len;
    var h1 = K1 ^ @as(u64, n);
    var h2 = K2;
    while (n >= 16) : (n -= 16) {
        h1 = (std.math.rotl(u64, h1, 5) ^ load64(p)) *% K1;
        h2 = (std.math.rotl(u64, h2, 5) ^ load64(p + 8)) *% K2;
        p += 16;
    }
    if (n >= 8) {
        h1 = (std.math.rotl(u64, h1, 5) ^ load64(p)) *% K1;
        p += 8;
        n -= 8;
    }
    if (n != 0) h2 = (std.math.rotl(u64, h2, 5) ^ (load64(p) & ((@as(u64, 1) << @intCast(8 * n)) - 1))) *% K2;
    var h = (h1 ^ std.math.rotl(u64, h2, 32)) *% K1;
    h ^= h >> 32;
    return if (h != 0) h else 1; // 0 marque une case vide
}
inline fn partOf(h: u64) usize {
    return @intCast(h >> (64 - PBITS));
}

// ------------------------------------------------------------------------------------------------ table de hachage
// Adressage ouvert, sondage linéaire, capacité en puissance de deux, clé et valeur dans la même case ; doublement
// quand la table est à moitié pleine. Clés entières positives ou nulles ; -1 marque une case vide.
fn pow2For(n: u64) u64 { // capacité pour n clés : au moins le double, 16 au moins
    var cap: u64 = 16;
    while (cap < 2 * n) cap *= 2;
    return cap;
}
/// Capacité de départ d'une table d'agrégation qui recevra n tuples ; elle double ensuite à la demande.
fn pow2Start(n: u64) u64 {
    return pow2For(n / 8);
}

const Cell = extern struct { key: i64, val: i64 };
const Map = struct {
    cells: [*]Cell = undefined,
    mask: u64 = 0,
    count: u64 = 0,
    arena: *Arena = undefined,

    fn init(a: *Arena, cap: u64) Map {
        const cells = a.array(Cell, cap);
        @memset(std.mem.sliceAsBytes(cells[0..cap]), 0xFF);
        return .{ .cells = cells, .mask = cap - 1, .count = 0, .arena = a };
    }
    /// Case de la clé, dont h est le hash64 ; null si elle manque.
    inline fn findH(m: *const Map, key: i64, h: u64) ?*Cell {
        var i = h & m.mask;
        while (true) : (i = (i + 1) & m.mask) {
            const c = &m.cells[i];
            if (c.key == key) return c;
            if (c.key == -1) return null;
        }
    }
    inline fn find(m: *const Map, key: i64) ?*Cell {
        return m.findH(key, hash64(@bitCast(key)));
    }
    fn grow(m: *Map) void {
        const old = m.*;
        m.* = init(old.arena, 2 * (old.mask + 1));
        for (old.cells[0 .. old.mask + 1]) |c| {
            if (c.key != -1) {
                var i = hash64(@bitCast(c.key)) & m.mask;
                while (m.cells[i].key != -1) i = (i + 1) & m.mask;
                m.cells[i] = c;
            }
        }
        m.count = old.count;
    }
    /// Rend la case de la clé, créée avec la valeur 0 si elle manquait (fresh le dit).
    inline fn upsertFresh(m: *Map, key: i64, fresh: *bool) *Cell {
        if ((m.count + 1) * 2 > m.mask + 1) m.grow();
        var i = hash64(@bitCast(key)) & m.mask;
        while (true) : (i = (i + 1) & m.mask) {
            const c = &m.cells[i];
            if (c.key == key) {
                fresh.* = false;
                return c;
            }
            if (c.key == -1) {
                c.* = .{ .key = key, .val = 0 };
                m.count += 1;
                fresh.* = true;
                return c;
            }
        }
    }
    inline fn upsert(m: *Map, key: i64) *Cell {
        var fresh: bool = undefined;
        return m.upsertFresh(key, &fresh);
    }
    fn all(m: *const Map) []Cell {
        return m.cells[0 .. m.mask + 1];
    }
};

/// Filtre de Bloom par blocs, devant les sondes de semi-jointure : 16 bits par clé, deux bits dans un même mot de
/// 64 bits. Un refus est sûr ; une acceptation se confirme dans la table.
const Bloom = struct {
    bits: [*]u64 = undefined,
    mask: u64 = 0,

    fn init(a: *Arena, nkeys: u64) Bloom {
        var words: u64 = 64;
        while (words * 4 < nkeys) words *= 2;
        const bits = a.array(u64, words);
        @memset(bits[0..words], 0);
        return .{ .bits = bits, .mask = words - 1 };
    }
    inline fn two(h: u64) u64 {
        return (@as(u64, 1) << @intCast(h & 63)) | (@as(u64, 1) << @intCast((h >> 6) & 63));
    }
    fn add(f: *Bloom, h: u64) void {
        f.bits[(h >> 12) & f.mask] |= two(h);
    }
    inline fn has(f: *const Bloom, h: u64) bool {
        const m = two(h);
        return f.bits[(h >> 12) & f.mask] & m == m;
    }
};

/// Même table pour des clés faites d'un entier et d'une chaîne : la case garde le hachage, l'entier, la position et
/// la longueur de la chaîne, et un compte. Hachage nul : case vide.
const SCell = extern struct { hash: u64, ikey: i64, pos: u64, len: u32, count: u32 };
const SMap = struct {
    cells: [*]SCell,
    mask: u64,
    n: u64,
    arena: *Arena,
    bytes: [*]const u8,

    fn init(a: *Arena, cap: u64, bytes: [*]const u8) SMap {
        const cells = a.array(SCell, cap);
        @memset(std.mem.sliceAsBytes(cells[0..cap]), 0);
        return .{ .cells = cells, .mask = cap - 1, .n = 0, .arena = a, .bytes = bytes };
    }
    fn grow(m: *SMap) void {
        const old = m.*;
        m.* = init(old.arena, 2 * (old.mask + 1), old.bytes);
        for (old.cells[0 .. old.mask + 1]) |c| {
            if (c.hash != 0) {
                var i = c.hash & m.mask;
                while (m.cells[i].hash != 0) i = (i + 1) & m.mask;
                m.cells[i] = c;
            }
        }
        m.n = old.n;
    }
    inline fn add(m: *SMap, hash: u64, ikey: i64, pos: u64, len: u32) void {
        if ((m.n + 1) * 2 > m.mask + 1) m.grow();
        var i = hash & m.mask;
        while (true) : (i = (i + 1) & m.mask) {
            const c = &m.cells[i];
            if (c.hash == hash and c.ikey == ikey and c.len == len and
                std.mem.eql(u8, (m.bytes + c.pos)[0..len], (m.bytes + pos)[0..len]))
            {
                c.count += 1;
                return;
            }
            if (c.hash == 0) {
                c.* = .{ .hash = hash, .ikey = ikey, .pos = pos, .len = len, .count = 1 };
                m.n += 1;
                return;
            }
        }
    }
};

// ------------------------------------------------------------------------------------------------ deux niveaux
const Agg1 = extern struct { qty: i64 = 0, base: i64 = 0, disc_price: i64 = 0, charge: i64 = 0, disc: i64 = 0, count: i64 = 0, pad: [2]i64 = .{ 0, 0 } };
const AHEAD = 16; // tuples d'avance pour le préchargement (niveau spécialisé)

/// Précharge une ligne de cache : au niveau spécialisé seulement.
inline fn prefetch(p: anytype) void {
    if (special) @prefetch(p, .{});
}

/// Compression : écrit en dst, à la suite, les voies de v que retient le masque (vpcompressd, en assembleur : le
/// langage n'a pas d'opération pour cela).
inline fn compressStore(dst: [*]i32, mask: u16, v: @Vector(16, i32)) void {
    asm volatile ("vpcompressd %[v], (%[d]) {%k1}"
        :
        : [v] "v" (v),
          [d] "r" (dst),
          [k] "{k1}" (mask),
        : .{ .memory = true });
}

/// Sélection. Positions (base + i) des valeurs v[i] comprises entre lo et hi, bornes comprises. Niveau portable : sans
/// branchement. Niveau spécialisé : 16 comparaisons d'un coup, puis compression des positions retenues.
fn selBetween(v: [*]const i32, n: usize, lo: i32, hi: i32, base: usize, pos: [*]i32) usize {
    var k: usize = 0;
    if (!special) {
        for (0..n) |i| {
            pos[k] = @intCast(base + i);
            k += @intFromBool(v[i] >= lo and v[i] <= hi);
        }
        return k;
    }
    const iota: @Vector(16, i32) = .{ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15 };
    var i: usize = 0;
    while (i < n) : (i += 16) {
        const m = between16(v + i, n - i, lo, hi);
        compressStore(pos + k, m, iota + @as(@Vector(16, i32), @splat(@intCast(base + i))));
        k += @popCount(m);
    }
    return k;
}
/// Masque des valeurs de v[0..16] comprises entre lo et hi, limité aux `left` valeurs qui restent. Les vecteurs de
/// travail ont 16 cases de marge : chaque pas lit 16 voies entières.
inline fn between16(v: [*]const i32, left: usize, lo: i32, hi: i32) u16 {
    const V = @Vector(16, i32);
    const x: V = v[0..16].*;
    const ge: u16 = @bitCast(x >= @as(V, @splat(lo)));
    const le: u16 = @bitCast(x <= @as(V, @splat(hi)));
    return ge & le & (if (left >= 16) @as(u16, 0xFFFF) else (@as(u16, 1) << @intCast(left)) - 1);
}
/// Parmi n entrées (position, charge) : garde celles dont la valeur v[i] est entre lo et hi.
fn keepBetween(v: [*]const i32, pos_in: [*]const i32, pay_in: [*]const i32, n: usize, lo: i32, hi: i32, pos_out: [*]i32, pay_out: [*]i32) usize {
    var k: usize = 0;
    if (!special) {
        for (0..n) |i| {
            pos_out[k] = pos_in[i];
            pay_out[k] = pay_in[i];
            k += @intFromBool(v[i] >= lo and v[i] <= hi);
        }
        return k;
    }
    var i: usize = 0;
    while (i < n) : (i += 16) {
        const m = between16(v + i, n - i, lo, hi);
        compressStore(pos_out + k, m, pos_in[i..][0..16].*);
        compressStore(pay_out + k, m, pay_in[i..][0..16].*);
        k += @popCount(m);
    }
    return k;
}

/// Agrégation de T1 : un vecteur de n lignes dans le tableau des six groupes ; ship non nul : seules comptent les
/// lignes dont la date ne dépasse pas cut. Niveau spécialisé : huit lignes à la fois, un masque et cinq additions
/// masquées par groupe.
fn t1Aggregate(agg: *[6]Agg1, grp: [*]const i32, qty: [*]const i32, ext: [*]const i32, disc: [*]const i32, dp: [*]const i64, ch: [*]const i64, ship: ?[*]const i32, cut: i32, n: usize, sel: [*]i32) void {
    if (!special) {
        if (ship) |s| {
            const k = selBetween(s, n, std.math.minInt(i32), cut, 0, sel);
            for (sel[0..k]) |j| {
                const i: usize = @intCast(j);
                t1Add(&agg[@intCast(grp[i])], qty[i], ext[i], dp[i], ch[i], disc[i]);
            }
        } else {
            for (0..n) |i| t1Add(&agg[@intCast(grp[i])], qty[i], ext[i], dp[i], ch[i], disc[i]);
        }
        return;
    }
    const L = @Vector(8, i64);
    const I = @Vector(8, i32);
    const zero: L = @splat(0);
    var acc: [6][5]L = @splat(@splat(zero));
    var cnt: [6]u64 = @splat(0);
    var i: usize = 0;
    while (i < n) : (i += 8) {
        var live: u8 = if (n - i >= 8) 0xFF else (@as(u8, 1) << @intCast(n - i)) - 1;
        if (ship) |s| live &= @bitCast(@as(I, s[i..][0..8].*) <= @as(I, @splat(cut)));
        const g8: I = grp[i..][0..8].*;
        const q: L = @as(I, qty[i..][0..8].*);
        const e: L = @as(I, ext[i..][0..8].*);
        const d: L = @as(I, disc[i..][0..8].*);
        const x: L = dp[i..][0..8].*;
        const y: L = ch[i..][0..8].*;
        inline for (0..6) |g| {
            const mb: u8 = @as(u8, @bitCast(g8 == @as(I, @splat(g)))) & live;
            const m: @Vector(8, bool) = @bitCast(mb);
            acc[g][0] += @select(i64, m, q, zero);
            acc[g][1] += @select(i64, m, e, zero);
            acc[g][2] += @select(i64, m, x, zero);
            acc[g][3] += @select(i64, m, y, zero);
            acc[g][4] += @select(i64, m, d, zero);
            cnt[g] += @popCount(mb);
        }
    }
    for (0..6) |g| {
        agg[g].qty += @reduce(.Add, acc[g][0]);
        agg[g].base += @reduce(.Add, acc[g][1]);
        agg[g].disc_price += @reduce(.Add, acc[g][2]);
        agg[g].charge += @reduce(.Add, acc[g][3]);
        agg[g].disc += @reduce(.Add, acc[g][4]);
        agg[g].count += @intCast(cnt[g]);
    }
}
inline fn t1Add(g: *Agg1, qty: i32, ext: i32, dp: i64, ch: i64, disc: i32) void {
    g.qty += qty;
    g.base += ext;
    g.disc_price += dp;
    g.charge += ch;
    g.disc += disc;
    g.count += 1;
}

// ------------------------------------------------------------------------------------------------ partitions
// Tampons d'un fil : pour chaque partition, une liste de morceaux de CHUNK octets pris dans son arène. Niveau
// spécialisé : chaque partition a de plus un tampon de 64 octets ; plein, il part d'un trait dans le morceau par une
// écriture non temporelle (vmovntdq, en assembleur : le langage n'a pas d'opération pour cela). La taille d'un tuple
// divise 64.
const PChunk = extern struct { next: ?*PChunk, used: u32, pad: u32, fill: [48]u8 }; // 64 octets, puis les tuples
const Parts = struct {
    cur: [NPART][*]u8 = undefined,
    end: [NPART][*]u8 = undefined,
    head: [NPART]?*PChunk = @splat(null),
    tail: [NPART]?*PChunk = @splat(null),
    fill: [NPART]u8 = @splat(0),
    tsize: usize = 0,
    arena: *Arena = undefined,
    wc: ?[*]align(64) [64]u8 = null,

    fn init(p: *Parts, a: *Arena, tsize: usize) void {
        if (special and p.wc == null) p.wc = @ptrCast(hugeAlloc(NPART * 64));
        const nowhere: [*]u8 = @ptrFromInt(64);
        @memset(&p.cur, nowhere);
        @memset(&p.end, nowhere);
        @memset(&p.head, null);
        @memset(&p.tail, null);
        @memset(&p.fill, 0);
        p.tsize = tsize;
        p.arena = a;
    }
    fn used(p: *const Parts, k: usize, t: *PChunk) u32 {
        return @intCast(@intFromPtr(p.cur[k]) - @intFromPtr(t) - 64);
    }
    noinline fn chunk(p: *Parts, k: usize) [*]u8 {
        const c: *PChunk = @ptrCast(p.arena.alloc(64 + CHUNK));
        c.next = null;
        c.used = 0;
        if (p.tail[k]) |t| {
            t.used = p.used(k, t);
            t.next = c;
        } else p.head[k] = c;
        p.tail[k] = c;
        p.cur[k] = @as([*]u8, @ptrCast(c)) + 64;
        p.end[k] = p.cur[k] + CHUNK / p.tsize * p.tsize;
        return p.cur[k];
    }
    /// Place du prochain tuple (de type T) de la partition k.
    inline fn push(p: *Parts, comptime T: type, k: usize) *align(1) T {
        if (special) {
            var f: usize = p.fill[k];
            const w: [*]u8 = @ptrCast(&p.wc.?[k]);
            if (f == 64) { // tampon plein : il est vidé avant de resservir
                if (p.cur[k] == p.end[k]) _ = p.chunk(k);
                streamStore(p.cur[k], @ptrCast(@alignCast(w)));
                p.cur[k] += 64;
                f = 0;
            }
            p.fill[k] = @intCast(f + @sizeOf(T));
            return @ptrCast(w + f);
        }
        var t = p.cur[k];
        if (t == p.end[k]) t = p.chunk(k);
        p.cur[k] = t + @sizeOf(T);
        return @ptrCast(t);
    }
    fn close(p: *Parts) void {
        for (0..NPART) |k| {
            if (special and p.fill[k] != 0) {
                if (p.cur[k] == p.end[k]) _ = p.chunk(k);
                const f: usize = p.fill[k];
                @memcpy(p.cur[k][0..f], @as([*]const u8, @ptrCast(&p.wc.?[k]))[0..f]);
                p.cur[k] += f;
                p.fill[k] = 0;
            }
            if (p.tail[k]) |t| t.used = p.used(k, t);
        }
        if (special) asm volatile ("sfence" ::: .{ .memory = true });
    }
};
/// Écriture non temporelle de 64 octets alignés.
inline fn streamStore(dst: [*]u8, src: *align(64) const [64]u8) void {
    const v: @Vector(64, u8) = src.*;
    asm volatile ("vmovntdq %[v], (%[d])"
        :
        : [v] "v" (v),
          [d] "r" (dst),
        : .{ .memory = true });
}
fn partsCount(ps: []const Parts, k: usize) u64 {
    var n: u64 = 0;
    for (ps) |*p| {
        var c = p.head[k];
        while (c) |x| : (c = x.next) n += x.used / p.tsize;
    }
    return n;
}
/// Tuples (de type T) d'un morceau.
inline fn tuples(comptime T: type, c: *const PChunk) []align(1) const T {
    const first: [*]align(1) const T = @ptrCast(@as([*]const u8, @ptrCast(c)) + 64);
    return first[0 .. c.used / @sizeOf(T)];
}

// ------------------------------------------------------------------------------------------------ état des fils
/// Vecteurs de travail d'un fil. Ceux de 32 bits ont 16 cases de marge pour les pas entiers du niveau spécialisé.
const Scratch = struct {
    a: [VEC + 16]i32,
    b: [VEC + 16]i32,
    c: [VEC + 16]i32,
    d: [VEC + 16]i32,
    e: [VEC + 16]i32,
    f: [VEC + 16]i32,
    g: [VEC + 16]i32,
    sel: [VEC + 16]i32,
    sel2: [VEC + 16]i32,
    pos: [VEC + 16]i32,
    x: [VEC]i64,
    y: [VEC]i64,
    h: [VEC]u64,
    len: [BLOCK + 16]i32,
    rows: [BLOCK + 16]i32,
};
var NT: usize = 1;
var arena: [MAXT]Arena = @splat(.{});
var scratch: [MAXT]*Scratch = undefined;
var parts: []Parts = undefined;
var parts2: []Parts = undefined;

/// Liste d'entiers de 64 bits dans une arène.
const List = struct {
    v: [*]i64 = undefined,
    n: usize = 0,
    cap: usize = 0,
    a: *Arena = undefined,

    fn init(a: *Arena) List {
        return .{ .a = a };
    }
    fn push(l: *List, x: i64) void {
        if (l.n == l.cap) {
            const cap = if (l.cap != 0) 2 * l.cap else 1024;
            const v = l.a.array(i64, cap);
            if (l.n != 0) @memcpy(v[0..l.n], l.v[0..l.n]);
            l.v = v;
            l.cap = cap;
        }
        l.v[l.n] = x;
        l.n += 1;
    }
    fn items(l: *const List) []const i64 {
        return l.v[0..l.n];
    }
};

// ------------------------------------------------------------------------------------------------ résultat
var res: []u8 = &.{};
var res_len: usize = 0;

fn emit(s: []const u8) void {
    if (res_len + s.len > res.len) {
        const bigger = hugeAlloc(2 * (res_len + s.len) + 4096)[0 .. 2 * (res_len + s.len) + 4096];
        @memcpy(bigger[0..res_len], res[0..res_len]);
        res = bigger;
    }
    @memcpy(res[res_len..][0..s.len], s);
    res_len += s.len;
}
fn emitInt(v: anytype) void {
    var buf: [24]u8 = undefined;
    emit(std.fmt.bufPrint(&buf, "{d}", .{v}) catch unreachable);
}
fn fnv1a(s: []const u8) u64 {
    var h: u64 = 0xCBF29CE484222325;
    for (s) |c| h = (h ^ c) *% 0x100000001B3;
    return h;
}

// ------------------------------------------------------------------------------------------------ dates
fn daysFromCivil(year: i32, m: i32, d: i32) i32 { // jours depuis le 1er janvier 1970
    const y = if (m <= 2) year - 1 else year;
    const era = @divFloor(y, 400);
    const yoe = y - era * 400;
    const doy = @divTrunc(153 * (m + @as(i32, if (m > 2) -3 else 9)) + 2, 5) + d - 1;
    const doe = yoe * 365 + @divTrunc(yoe, 4) - @divTrunc(yoe, 100) + doy;
    return era * 146097 + doe - 719468;
}
/// Premier jour de chaque année à partir de 1970 : table calculée à la compilation.
const year_start: [200]i32 = blk: {
    var t: [200]i32 = undefined;
    for (0..200) |y| t[y] = daysFromCivil(1970 + y, 1, 1);
    break :blk t;
};
fn yearOf(days: i32) i64 {
    var y: usize = @intCast(@divTrunc(days, 366));
    while (year_start[y + 1] <= days) y += 1;
    return 1970 + @as(i64, @intCast(y));
}

// ------------------------------------------------------------------------------------------------ sous-chaînes
// Lignes d'un bloc de chaînes qui contiennent l'aiguille (2 octets au moins) : les octets du bloc sont parcourus
// d'un trait, par mots de 8 octets ; un mot est candidat si, à une même position, il porte le premier octet de
// l'aiguille et le mot décalé de sa longueur moins un porte le dernier. Une occurrence compte si elle tient dans
// une ligne, et une ligne compte une fois. Niveau spécialisé : 64 positions d'un coup, un bit candidat par position.
const ONES: u64 = 0x0101010101010101;
const HIGHS: u64 = 0x8080808080808080;
inline fn zeroBytes(x: u64) u64 { // bit de poids fort de chaque octet nul de x, exactement
    return ~(((x & ~HIGHS) +% ~HIGHS) | x) & HIGHS;
}
inline fn searchCandidates(p: [*]const u8, m: usize, c0: u8, c1: u8) u64 {
    const V = @Vector(64, u8);
    const a: V = p[0..64].*;
    const b: V = (p + m - 1)[0..64].*;
    return @as(u64, @bitCast(a == @as(V, @splat(c0)))) & @as(u64, @bitCast(b == @as(V, @splat(c1))));
}
fn searchBlock(buf: [*]const u8, nbytes: usize, len: [*]const i32, needle: []const u8, rows: [*]i32) usize {
    const m = needle.len;
    var r: usize = 0;
    var k: usize = 0;
    var row_end: usize = if (nbytes != 0) @intCast(len[0]) else 0;
    const c0 = needle[0];
    const c1 = needle[m - 1];
    const first = ONES * c0;
    const last = ONES * c1;
    const stop = if (nbytes >= m) nbytes - m + 1 else 0; // positions de départ possibles : [0, stop)
    var i: usize = 0;
    while (i < stop) {
        var cand: u64 = 0;
        var step: usize = 8;
        var shift: u6 = 3; // un bit candidat par octet du mot : rang du bit / 8
        if (special) {
            while (i + 64 + m - 1 <= nbytes) : (i += 64) {
                cand = searchCandidates(buf + i, m, c0, c1);
                if (cand != 0) break;
            }
            if (cand != 0) {
                step = 64;
                shift = 0;
            }
        }
        if (cand == 0) {
            // boucle serrée sur les mots sans candidate
            while (i + 8 <= stop) : (i += 8) {
                cand = zeroBytes((load64(buf + i) ^ first) | (load64(buf + i + m - 1) ^ last));
                if (cand != 0) break;
            }
            if (cand == 0) { // fin du bloc : moins de 8 positions, octet par octet
                var j = i;
                while (j < stop) : (j += 1) {
                    if (buf[j] == c0 and buf[j + m - 1] == c1) cand |= @as(u64, 0x80) << @intCast(8 * (j - i));
                }
            }
        }
        var next = i + step;
        while (cand != 0) : (cand &= cand - 1) {
            const at = i + (@as(usize, @ctz(cand)) >> shift);
            if (!std.mem.eql(u8, (buf + at + 1)[0 .. m - 2], needle[1 .. m - 1])) continue;
            while (row_end <= at) {
                r += 1;
                row_end += @intCast(len[r]);
            }
            if (at + m <= row_end) { // la suite de la ligne est sautée
                rows[k] = @intCast(r);
                k += 1;
                next = row_end;
                break;
            }
        }
        i = next;
    }
    return k;
}
/// Longueurs d'un bloc de chaînes (dans len) ; rend le nombre de ses octets.
fn blockLengths(c: *const Col, b: usize, len: [*]i32) usize {
    const n = c.dir[b].count;
    unpack(c, b, 0, n, len);
    var total: usize = 0;
    for (len[0..n]) |l| total += @intCast(l);
    return total;
}

// ------------------------------------------------------------------------------------------------ dix premiers
const Top = struct { count: u32, len: u32, ikey: i64, pos: u64 };
const Top10 = struct {
    t: [10]Top = undefined,
    n: usize = 0,

    /// Ordre : compte décroissant, entier croissant, chaîne croissante.
    fn before(a: Top, b: Top, bytes: [*]const u8) bool {
        if (a.count != b.count) return a.count > b.count;
        if (a.ikey != b.ikey) return a.ikey < b.ikey;
        return std.mem.order(u8, (bytes + a.pos)[0..a.len], (bytes + b.pos)[0..b.len]) == .lt;
    }
    fn add(t: *Top10, x: Top, bytes: [*]const u8) void {
        if (t.n == 10 and !before(x, t.t[9], bytes)) return;
        var i: usize = 9;
        if (t.n < 10) {
            i = t.n;
            t.n += 1;
        }
        while (i > 0 and before(x, t.t[i - 1], bytes)) : (i -= 1) t.t[i] = t.t[i - 1];
        t.t[i] = x;
    }
};

/// Vecteurs d'un bloc de `count` lignes : début et longueur du vecteur suivant.
const Vectors = struct {
    count: usize,
    st: usize = 0,
    fn next(v: *Vectors) ?struct { usize, usize } {
        if (v.st >= v.count) return null;
        const st = v.st;
        v.st += VEC;
        return .{ st, @min(v.count - st, VEC) };
    }
};

// ================================================================================================ T1 (TPC-H Q1)
const T1 = struct {
    ship: Col,
    rf: Col,
    ls: Col,
    qty: Col,
    ext: Col,
    disc: Col,
    tax: Col,
    ctr: Counter = .{},
    cut: i32,
    agg: [MAXT][6]Agg1 = undefined,

    fn open() T1 {
        return .{
            .ship = colOpen("lineitem", "l_shipdate"),
            .rf = colOpen("lineitem", "l_returnflag"),
            .ls = colOpen("lineitem", "l_linestatus"),
            .qty = colOpen("lineitem", "l_quantity"),
            .ext = colOpen("lineitem", "l_extendedprice"),
            .disc = colOpen("lineitem", "l_discount"),
            .tax = colOpen("lineitem", "l_tax"),
            .cut = daysFromCivil(1998, 9, 2),
        };
    }
    fn task(q: *T1, tid: usize) void {
        const s = scratch[tid];
        var agg: [6]Agg1 = @splat(.{});
        while (q.ctr.take()) |b| {
            const e = &q.ship.dir[b];
            if (e.min > q.cut) continue; // bloc exclu par sa carte de zones
            const all = e.max <= q.cut; // bloc retenu en entier : le filtre n'est pas évalué
            var vs: Vectors = .{ .count = e.count };
            while (vs.next()) |v| {
                const st, const n = v;
                unpack(&q.rf, b, st, n, &s.a);
                unpack(&q.ls, b, st, n, &s.b);
                unpack(&q.qty, b, st, n, &s.c);
                unpack(&q.ext, b, st, n, &s.d);
                unpack(&q.disc, b, st, n, &s.e);
                unpack(&q.tax, b, st, n, &s.f);
                for (s.x[0..n], s.d[0..n], s.e[0..n]) |*x, d, disc| x.* = @as(i64, d) * (100 - disc);
                for (s.y[0..n], s.x[0..n], s.f[0..n]) |*y, x, tax| y.* = x * (100 + tax);
                for (s.g[0..n], s.a[0..n], s.b[0..n]) |*g, rf, ls| g.* = rf * 2 + ls;
                var ship: ?[*]const i32 = null;
                if (!all) {
                    unpack(&q.ship, b, st, n, &s.pos);
                    ship = &s.pos;
                }
                t1Aggregate(&agg, &s.g, &s.c, &s.d, &s.e, &s.x, &s.y, ship, q.cut, n, &s.sel);
            }
        }
        q.agg[tid] = agg;
    }
    fn run(q: *T1) void {
        q.ctr.set(q.ship.nblocks);
        pool.run(q, task);
        for (0..6) |g| {
            var a: Agg1 = .{};
            for (q.agg[0..NT]) |*t| {
                const x = &t[g];
                a.qty += x.qty;
                a.base += x.base;
                a.disc_price += x.disc_price;
                a.charge += x.charge;
                a.disc += x.disc;
                a.count += x.count;
            }
            if (a.count == 0) continue;
            emit(q.rf.dict(g / 2));
            emit("|");
            emit(q.ls.dict(g % 2));
            inline for (.{ a.qty, a.base, a.disc_price, a.charge, a.disc, a.count }) |v| {
                emit("|");
                emitInt(v);
            }
            emit("\n");
        }
    }
};

// ================================================================================================ T6 (TPC-H Q6)
const T6 = struct {
    ship: Col,
    disc: Col,
    qty: Col,
    ext: Col,
    ctr: Counter = .{},
    lo: i32,
    hi: i32,
    sum: [MAXT][8]i64 = undefined,

    fn open() T6 {
        return .{
            .ship = colOpen("lineitem", "l_shipdate"),
            .disc = colOpen("lineitem", "l_discount"),
            .qty = colOpen("lineitem", "l_quantity"),
            .ext = colOpen("lineitem", "l_extendedprice"),
            .lo = daysFromCivil(1994, 1, 1),
            .hi = daysFromCivil(1995, 1, 1),
        };
    }
    fn task(q: *T6, tid: usize) void {
        const s = scratch[tid];
        var sum: i64 = 0;
        while (q.ctr.take()) |b| {
            const e = &q.ship.dir[b];
            if (e.max < q.lo or e.min >= q.hi) continue;
            var vs: Vectors = .{ .count = e.count };
            while (vs.next()) |v| {
                const st, const n = v;
                unpack(&q.ship, b, st, n, &s.a);
                const k = selBetween(&s.a, n, q.lo, q.hi - 1, st, &s.pos);
                if (k == 0) continue;
                unpackSel(&q.disc, b, s.pos[0..k], &s.b);
                const k2 = keepBetween(&s.b, &s.pos, &s.b, k, 5, 7, &s.sel, &s.c);
                if (k2 == 0) continue;
                unpackSel(&q.qty, b, s.sel[0..k2], &s.d);
                const k3 = keepBetween(&s.d, &s.sel, &s.c, k2, std.math.minInt(i32), 2399, &s.sel2, &s.e);
                if (k3 == 0) continue;
                unpackSel(&q.ext, b, s.sel2[0..k3], &s.f);
                for (s.f[0..k3], s.e[0..k3]) |price, disc| sum += @as(i64, price) * disc;
            }
        }
        q.sum[tid][0] = sum;
    }
    fn run(q: *T6) void {
        q.ctr.set(q.ship.nblocks);
        pool.run(q, task);
        var sum: i64 = 0;
        for (q.sum[0..NT]) |t| sum += t[0];
        emitInt(sum);
        emit("\n");
    }
};

// ================================================================================================ T9 (TPC-H Q9)
// 1. part : noms qui contiennent « green » -> ensemble de pièces (table et filtre de Bloom) ;
// 2. partsupp : lignes de ces pièces -> (pièce, fournisseur) -> coût ; 3. supplier -> nation ;
// 4. lineitem : lignes de ces pièces, montant et nation, réparties par commande ;
// 5. orders : (commande, date) réparties de même ; 6. par partition : table des lignes de lineitem, sondée par les
//    commandes ; agrégat par nation et année.
const T9Tuple = extern struct { okey: i32, nation: i32, amount: i64 };
const T9Order = extern struct { okey: i32, date: i32 };

/// Positions (dans le bloc) et clés des lignes d'un vecteur dont la clé est dans l'ensemble (filtre, puis table).
fn semi(set: *const Map, filter: *const Bloom, key: []const i32, st: usize, pos: [*]i32, out: [*]i32) usize {
    var k: usize = 0;
    for (key, 0..) |x, i| {
        const h = hash64(@bitCast(@as(i64, x)));
        if (filter.has(h) and set.findH(x, h) != null) {
            pos[k] = @intCast(st + i);
            out[k] = x;
            k += 1;
        }
    }
    return k;
}

const T9 = struct {
    p_partkey: Col,
    p_name: Col,
    ps_partkey: Col,
    ps_suppkey: Col,
    ps_cost: Col,
    s_suppkey: Col,
    s_nationkey: Col,
    n_nationkey: Col,
    n_name: Col,
    l_partkey: Col,
    l_suppkey: Col,
    l_orderkey: Col,
    l_qty: Col,
    l_ext: Col,
    l_disc: Col,
    o_orderkey: Col,
    o_orderdate: Col,
    ctr: Counter = .{},
    l1: [MAXT]List = undefined, // listes des fils
    l2: [MAXT]List = undefined,
    part: Map = .{},
    ps: Map = .{},
    supp: Map = .{},
    agg: [MAXT]Map = undefined,
    fpart: Bloom = .{},

    fn open() T9 {
        return .{
            .p_partkey = colOpen("part", "p_partkey"),
            .p_name = colOpen("part", "p_name"),
            .ps_partkey = colOpen("partsupp", "ps_partkey"),
            .ps_suppkey = colOpen("partsupp", "ps_suppkey"),
            .ps_cost = colOpen("partsupp", "ps_supplycost"),
            .s_suppkey = colOpen("supplier", "s_suppkey"),
            .s_nationkey = colOpen("supplier", "s_nationkey"),
            .n_nationkey = colOpen("nation", "n_nationkey"),
            .n_name = colOpen("nation", "n_name"),
            .l_partkey = colOpen("lineitem", "l_partkey"),
            .l_suppkey = colOpen("lineitem", "l_suppkey"),
            .l_orderkey = colOpen("lineitem", "l_orderkey"),
            .l_qty = colOpen("lineitem", "l_quantity"),
            .l_ext = colOpen("lineitem", "l_extendedprice"),
            .l_disc = colOpen("lineitem", "l_discount"),
            .o_orderkey = colOpen("orders", "o_orderkey"),
            .o_orderdate = colOpen("orders", "o_orderdate"),
        };
    }
    fn partTask(q: *T9, tid: usize) void {
        const s = scratch[tid];
        var l = List.init(&arena[tid]);
        while (q.ctr.take()) |b| {
            const nbytes = blockLengths(&q.p_name, b, &s.len);
            const k = searchBlock(q.p_name.aux + q.p_name.dir[b].aux_off, nbytes, &s.len, "green", &s.rows);
            var i: usize = 0;
            while (i < k) : (i += VEC) {
                const n = @min(k - i, VEC);
                unpackSel(&q.p_partkey, b, s.rows[i..][0..n], &s.a);
                for (s.a[0..n]) |key| l.push(key);
            }
        }
        q.l1[tid] = l;
    }
    fn psTask(q: *T9, tid: usize) void {
        const s = scratch[tid];
        var l1 = List.init(&arena[tid]);
        var l2 = List.init(&arena[tid]);
        while (q.ctr.take()) |b| {
            var vs: Vectors = .{ .count = q.ps_partkey.dir[b].count };
            while (vs.next()) |v| {
                const st, const n = v;
                unpack(&q.ps_partkey, b, st, n, &s.a);
                const k = semi(&q.part, &q.fpart, s.a[0..n], st, &s.pos, &s.b);
                if (k == 0) continue;
                unpackSel(&q.ps_suppkey, b, s.pos[0..k], &s.c);
                unpackSel(&q.ps_cost, b, s.pos[0..k], &s.d);
                for (0..k) |i| {
                    l1.push((@as(i64, s.b[i]) << 32) | s.c[i]);
                    l2.push(s.d[i]);
                }
            }
        }
        q.l1[tid] = l1;
        q.l2[tid] = l2;
    }
    fn lineTask(q: *T9, tid: usize) void {
        const s = scratch[tid];
        const p = &parts[tid];
        p.init(&arena[tid], @sizeOf(T9Tuple));
        while (q.ctr.take()) |b| {
            var vs: Vectors = .{ .count = q.l_partkey.dir[b].count };
            while (vs.next()) |v| {
                const st, const n = v;
                unpack(&q.l_partkey, b, st, n, &s.a);
                const k = semi(&q.part, &q.fpart, s.a[0..n], st, &s.pos, &s.b);
                if (k == 0) continue;
                unpackSel(&q.l_suppkey, b, s.pos[0..k], &s.c);
                unpackSel(&q.l_orderkey, b, s.pos[0..k], &s.d);
                unpackSel(&q.l_qty, b, s.pos[0..k], &s.e);
                unpackSel(&q.l_ext, b, s.pos[0..k], &s.f);
                unpackSel(&q.l_disc, b, s.pos[0..k], &s.g);
                if (special) { // les cases des deux tables sont préchargées pour tout le vecteur
                    for (0..k) |i| {
                        prefetch(&q.ps.cells[hash64(@bitCast((@as(i64, s.b[i]) << 32) | s.c[i])) & q.ps.mask]);
                        prefetch(&q.supp.cells[hash64(@bitCast(@as(i64, s.c[i]))) & q.supp.mask]);
                    }
                }
                for (0..k) |i| {
                    const cost = q.ps.find((@as(i64, s.b[i]) << 32) | s.c[i]).?.val;
                    const nation = q.supp.find(s.c[i]).?.val;
                    p.push(T9Tuple, partOf(hash64(@bitCast(@as(i64, s.d[i]))))).* = .{
                        .okey = s.d[i],
                        .nation = @intCast(nation),
                        .amount = @as(i64, s.f[i]) * (100 - s.g[i]) - cost * s.e[i],
                    };
                }
            }
        }
        p.close();
    }
    fn ordersTask(q: *T9, tid: usize) void {
        const s = scratch[tid];
        const p = &parts2[tid];
        p.init(&arena[tid], @sizeOf(T9Order));
        while (q.ctr.take()) |b| {
            var vs: Vectors = .{ .count = q.o_orderkey.dir[b].count };
            while (vs.next()) |v| {
                const st, const n = v;
                unpack(&q.o_orderkey, b, st, n, &s.a);
                unpack(&q.o_orderdate, b, st, n, &s.b);
                for (s.h[0..n], s.a[0..n]) |*h, key| h.* = hash64(@bitCast(@as(i64, key)));
                for (0..n) |i| p.push(T9Order, partOf(s.h[i])).* = .{ .okey = s.a[i], .date = s.b[i] };
            }
        }
        p.close();
    }
    fn joinTask(q: *T9, tid: usize) void {
        const a = &arena[tid];
        var agg = Map.init(a, 1024);
        while (q.ctr.take()) |k| {
            const n = partsCount(parts, k);
            if (n == 0) continue;
            const tu = a.array(T9Tuple, n);
            const next = a.array(i32, n);
            var m = Map.init(a, pow2For(n)); // commande -> rang de son dernier tuple ; next chaîne les tuples d'une même commande
            var i: usize = 0;
            for (parts) |*p| {
                var c = p.head[k];
                while (c) |x| : (c = x.next) {
                    for (tuples(T9Tuple, x)) |t| {
                        var fresh: bool = undefined;
                        const cell = m.upsertFresh(t.okey, &fresh);
                        tu[i] = t;
                        next[i] = if (fresh) -1 else @intCast(cell.val);
                        cell.val = @intCast(i);
                        i += 1;
                    }
                }
            }
            for (parts2) |*p| {
                var c = p.head[k];
                while (c) |x| : (c = x.next) {
                    const os = tuples(T9Order, x);
                    for (os, 0..) |o, oi| {
                        if (special and oi + AHEAD < os.len) prefetch(&m.cells[hash64(@bitCast(@as(i64, os[oi + AHEAD].okey))) & m.mask]);
                        const cell = m.find(o.okey) orelse continue;
                        const year = yearOf(o.date);
                        var j: i32 = @intCast(cell.val);
                        while (j >= 0) : (j = next[@intCast(j)]) {
                            const t = &tu[@intCast(j)];
                            agg.upsert((@as(i64, t.nation) << 16) | year).val += t.amount;
                        }
                    }
                }
            }
        }
        q.agg[tid] = agg;
    }
    const Row = struct { name: []const u8, year: i64, sum: i64 };
    fn rowBefore(_: void, a: Row, b: Row) bool {
        return switch (std.mem.order(u8, a.name, b.name)) {
            .lt => true,
            .gt => false,
            .eq => a.year > b.year,
        };
    }
    fn run(q: *T9) void {
        const a0 = &arena[0];
        const s = scratch[0];
        q.ctr.set(q.p_name.nblocks);
        pool.run(q, partTask);
        var n: usize = 0;
        for (q.l1[0..NT]) |*l| n += l.n;
        q.part = Map.init(a0, pow2For(n));
        q.fpart = Bloom.init(a0, n);
        for (q.l1[0..NT]) |*l| {
            for (l.items()) |key| {
                _ = q.part.upsert(key);
                q.fpart.add(hash64(@bitCast(key)));
            }
        }
        q.ctr.set(q.ps_partkey.nblocks);
        pool.run(q, psTask);
        n = 0;
        for (q.l1[0..NT]) |*l| n += l.n;
        q.ps = Map.init(a0, pow2For(n));
        for (q.l1[0..NT], q.l2[0..NT]) |*l1, *l2| {
            for (l1.items(), l2.items()) |key, cost| q.ps.upsert(key).val = cost;
        }
        q.supp = Map.init(a0, pow2For(q.s_suppkey.nrows));
        for (0..q.s_suppkey.nblocks) |b| {
            var vs: Vectors = .{ .count = q.s_suppkey.dir[b].count };
            while (vs.next()) |v| {
                const st, const m = v;
                unpack(&q.s_suppkey, b, st, m, &s.a);
                unpack(&q.s_nationkey, b, st, m, &s.b);
                for (s.a[0..m], s.b[0..m]) |key, nation| q.supp.upsert(key).val = nation;
            }
        }
        q.ctr.set(q.l_partkey.nblocks);
        pool.run(q, lineTask);
        q.ctr.set(q.o_orderkey.nblocks);
        pool.run(q, ordersTask);
        q.ctr.set(NPART);
        pool.run(q, joinTask);
        // fusion ; nation -> nom ; tri par nom puis année décroissante
        var total = Map.init(a0, 1024);
        for (q.agg[0..NT]) |*agg| {
            for (agg.all()) |c| {
                if (c.key != -1) total.upsert(c.key).val += c.val;
            }
        }
        var nat = Map.init(a0, 64);
        const nn: usize = q.n_nationkey.nrows;
        unpack(&q.n_nationkey, 0, 0, nn, &s.a);
        unpack(&q.n_name, 0, 0, nn, &s.b);
        for (s.a[0..nn], s.b[0..nn]) |key, name| nat.upsert(key).val = name;
        const rows = a0.array(Row, total.count + 1);
        var nr: usize = 0;
        for (total.all()) |c| {
            if (c.key != -1) {
                rows[nr] = .{ .name = q.n_name.dict(@intCast(nat.find(c.key >> 16).?.val)), .year = c.key & 0xFFFF, .sum = c.val };
                nr += 1;
            }
        }
        std.mem.sortUnstable(Row, rows[0..nr], {}, rowBefore);
        for (rows[0..nr]) |r| {
            emit(r.name);
            emit("|");
            emitInt(r.year);
            emit("|");
            emitInt(r.sum);
            emit("\n");
        }
    }
};

// ================================================================================================ T18 (TPC-H Q18)
const KQ = extern struct { key: i32, qty: i32 };

const T18 = struct {
    l_orderkey: Col,
    l_qty: Col,
    o_orderkey: Col,
    o_custkey: Col,
    o_orderdate: Col,
    o_totalprice: Col,
    c_custkey: Col,
    c_name: Col,
    ctr: Counter = .{},
    l: [4][MAXT]List = undefined,
    big: Map = .{},
    cust: Map = .{},
    sums: [MAXT]Map = undefined,
    fbig: Bloom = .{},
    fcust: Bloom = .{},

    fn open() T18 {
        return .{
            .l_orderkey = colOpen("lineitem", "l_orderkey"),
            .l_qty = colOpen("lineitem", "l_quantity"),
            .o_orderkey = colOpen("orders", "o_orderkey"),
            .o_custkey = colOpen("orders", "o_custkey"),
            .o_orderdate = colOpen("orders", "o_orderdate"),
            .o_totalprice = colOpen("orders", "o_totalprice"),
            .c_custkey = colOpen("customer", "c_custkey"),
            .c_name = colOpen("customer", "c_name"),
        };
    }
    fn scatterTask(q: *T18, tid: usize) void { // lineitem réparti par commande
        const s = scratch[tid];
        const p = &parts[tid];
        p.init(&arena[tid], @sizeOf(KQ));
        while (q.ctr.take()) |b| {
            var vs: Vectors = .{ .count = q.l_orderkey.dir[b].count };
            while (vs.next()) |v| {
                const st, const n = v;
                unpack(&q.l_orderkey, b, st, n, &s.a);
                unpack(&q.l_qty, b, st, n, &s.b);
                for (s.h[0..n], s.a[0..n]) |*h, key| h.* = hash64(@bitCast(@as(i64, key)));
                for (0..n) |i| p.push(KQ, partOf(s.h[i])).* = .{ .key = s.a[i], .qty = s.b[i] };
            }
        }
        p.close();
    }
    fn aggTask(q: *T18, tid: usize) void { // une partition : somme par commande ; garde celles de plus de 300 unités
        const a = &arena[tid];
        var l = List.init(a);
        while (q.ctr.take()) |k| {
            var m = Map.init(a, pow2Start(partsCount(parts, k)));
            for (parts) |*p| {
                var c = p.head[k];
                while (c) |x| : (c = x.next) {
                    const ts = tuples(KQ, x);
                    for (ts, 0..) |t, i| {
                        if (special and i + AHEAD < ts.len) prefetch(&m.cells[hash64(@bitCast(@as(i64, ts[i + AHEAD].key))) & m.mask]);
                        m.upsert(t.key).val += t.qty;
                    }
                }
            }
            for (m.all()) |c| {
                if (c.key != -1 and c.val > 30000) l.push(c.key);
            }
        }
        q.l[0][tid] = l;
    }
    fn ordersTask(q: *T18, tid: usize) void { // commandes retenues : client, date, prix
        const s = scratch[tid];
        var l: [4]List = @splat(List.init(&arena[tid]));
        while (q.ctr.take()) |b| {
            var vs: Vectors = .{ .count = q.o_orderkey.dir[b].count };
            while (vs.next()) |v| {
                const st, const n = v;
                unpack(&q.o_orderkey, b, st, n, &s.a);
                const k = semi(&q.big, &q.fbig, s.a[0..n], st, &s.pos, &s.b);
                if (k == 0) continue;
                unpackSel(&q.o_custkey, b, s.pos[0..k], &s.c);
                unpackSel(&q.o_orderdate, b, s.pos[0..k], &s.d);
                unpackSel(&q.o_totalprice, b, s.pos[0..k], &s.e);
                for (0..k) |i| {
                    l[0].push(s.b[i]);
                    l[1].push(s.c[i]);
                    l[2].push(s.d[i]);
                    l[3].push(s.e[i]);
                }
            }
        }
        for (0..4) |j| q.l[j][tid] = l[j];
    }
    fn custTask(q: *T18, tid: usize) void { // clients de ces commandes : position et longueur de leur nom
        const s = scratch[tid];
        var l: [3]List = @splat(List.init(&arena[tid]));
        while (q.ctr.take()) |b| {
            var pos: u64 = q.c_name.dir[b].aux_off;
            var vs: Vectors = .{ .count = q.c_custkey.dir[b].count };
            while (vs.next()) |v| {
                const st, const n = v;
                unpack(&q.c_custkey, b, st, n, &s.a);
                unpack(&q.c_name, b, st, n, &s.b);
                for (s.a[0..n], s.b[0..n]) |key, len| {
                    const h = hash64(@bitCast(@as(i64, key)));
                    if (q.fcust.has(h) and q.cust.findH(key, h) != null) {
                        l[0].push(key);
                        l[1].push(@intCast(pos));
                        l[2].push(len);
                    }
                    pos += @intCast(len);
                }
            }
        }
        for (0..3) |j| q.l[j][tid] = l[j];
    }
    fn sumTask(q: *T18, tid: usize) void { // lineitem des commandes retenues : somme des quantités
        const s = scratch[tid];
        var m = Map.init(&arena[tid], 1024);
        while (q.ctr.take()) |b| {
            var vs: Vectors = .{ .count = q.l_orderkey.dir[b].count };
            while (vs.next()) |v| {
                const st, const n = v;
                unpack(&q.l_orderkey, b, st, n, &s.a);
                const k = semi(&q.big, &q.fbig, s.a[0..n], st, &s.pos, &s.b);
                if (k == 0) continue;
                unpackSel(&q.l_qty, b, s.pos[0..k], &s.c);
                for (s.b[0..k], s.c[0..k]) |key, qty| m.upsert(key).val += qty;
            }
        }
        q.sums[tid] = m;
    }
    const Row = struct { okey: i64, cust: i64, date: i64, price: i64, sum: i64 = 0, name: []const u8 = "" };
    fn rowBefore(_: void, a: Row, b: Row) bool { // prix décroissant, date, commande
        if (a.price != b.price) return a.price > b.price;
        if (a.date != b.date) return a.date < b.date;
        return a.okey < b.okey;
    }
    fn run(q: *T18) void {
        const a0 = &arena[0];
        // 1. et 2. agrégation de lineitem par commande ; 3. commandes de plus de 300 unités
        q.ctr.set(q.l_orderkey.nblocks);
        pool.run(q, scatterTask);
        q.ctr.set(NPART);
        pool.run(q, aggTask);
        var n: usize = 0;
        for (q.l[0][0..NT]) |*l| n += l.n;
        q.big = Map.init(a0, pow2For(n));
        q.fbig = Bloom.init(a0, n);
        for (q.l[0][0..NT]) |*l| {
            for (l.items()) |key| {
                _ = q.big.upsert(key);
                q.fbig.add(hash64(@bitCast(key)));
            }
        }
        // 4. leurs lignes dans orders
        q.ctr.set(q.o_orderkey.nblocks);
        pool.run(q, ordersTask);
        const rows = a0.array(Row, n + 1);
        var nr: usize = 0;
        q.cust = Map.init(a0, pow2For(n));
        q.fcust = Bloom.init(a0, n);
        for (0..NT) |t| {
            for (q.l[0][t].items(), q.l[1][t].items(), q.l[2][t].items(), q.l[3][t].items()) |okey, c, date, price| {
                rows[nr] = .{ .okey = okey, .cust = c, .date = date, .price = price };
                nr += 1;
                _ = q.cust.upsert(c);
                q.fcust.add(hash64(@bitCast(c)));
            }
        }
        // 5. leurs clients ; 6. leurs lignes dans lineitem
        q.ctr.set(q.c_custkey.nblocks);
        pool.run(q, custTask);
        var name = Map.init(a0, pow2For(n)); // client -> rang dans les listes
        const names = a0.array([]const u8, n + 1);
        var nn: usize = 0;
        for (0..NT) |t| {
            for (q.l[0][t].items(), q.l[1][t].items(), q.l[2][t].items()) |c, pos, len| {
                name.upsert(c).val = @intCast(nn);
                names[nn] = (q.c_name.aux + @as(usize, @intCast(pos)))[0..@intCast(len)];
                nn += 1;
            }
        }
        q.ctr.set(q.l_orderkey.nblocks);
        pool.run(q, sumTask);
        for (rows[0..nr]) |*r| {
            for (q.sums[0..NT]) |*m| {
                if (m.find(r.okey)) |c| r.sum += c.val;
            }
            r.name = names[@intCast(name.find(r.cust).?.val)];
        }
        std.mem.sortUnstable(Row, rows[0..nr], {}, rowBefore);
        for (rows[0..@min(nr, 100)]) |r| {
            emit(r.name);
            inline for (.{ r.cust, r.okey, r.date, r.price, r.sum }) |v| {
                emit("|");
                emitInt(v);
            }
            emit("\n");
        }
    }
};

// ================================================================================================ C4
const C4 = struct {
    uid: Col,
    ctr: Counter = .{},
    count: [MAXT][8]u64 = undefined,
    minus1: [MAXT][8]u64 = undefined,

    fn open() C4 {
        return .{ .uid = colOpen("hits", "UserID") };
    }
    fn scatterTask(q: *C4, tid: usize) void {
        const s = scratch[tid];
        const p = &parts[tid];
        p.init(&arena[tid], 8);
        while (q.ctr.take()) |b| {
            const all: [*]const i64 = @ptrCast(q.uid.words(b)); // 64 bits : valeurs telles quelles
            var vs: Vectors = .{ .count = q.uid.dir[b].count };
            while (vs.next()) |vec| {
                const st, const n = vec;
                const v = all[st..][0..n];
                for (s.h[0..n], v) |*h, x| h.* = hash64(@bitCast(x));
                for (s.h[0..n], v) |h, x| p.push(i64, partOf(h)).* = x;
            }
        }
        p.close();
    }
    fn countTask(q: *C4, tid: usize) void {
        var count: u64 = 0;
        var minus1: u64 = 0;
        while (q.ctr.take()) |k| {
            var m = Map.init(&arena[tid], pow2Start(partsCount(parts, k)));
            for (parts) |*p| {
                var c = p.head[k];
                while (c) |x| : (c = x.next) {
                    const ts = tuples(i64, x);
                    for (ts, 0..) |t, i| {
                        if (special and i + AHEAD < ts.len) prefetch(&m.cells[hash64(@bitCast(ts[i + AHEAD])) & m.mask]);
                        if (t == -1) {
                            minus1 = 1; // la valeur qui marque les cases vides est comptée à part
                        } else _ = m.upsert(t);
                    }
                }
            }
            count += m.count;
        }
        q.count[tid][0] = count;
        q.minus1[tid][0] = minus1;
    }
    fn run(q: *C4) void {
        q.ctr.set(q.uid.nblocks);
        pool.run(q, scatterTask);
        q.ctr.set(NPART);
        pool.run(q, countTask);
        var count: u64 = 0;
        var minus1: u64 = 0;
        for (0..NT) |t| {
            count += q.count[t][0];
            minus1 |= q.minus1[t][0];
        }
        emitInt(count + minus1);
        emit("\n");
    }
};

// ================================================================================================ agrégations par chaîne
// C12, C16, C33, C36 : les lignes retenues sont hachées, réparties, puis agrégées partition par partition ; chaque
// fil garde ses dix premiers groupes.
const STuple = extern struct { hash: u64, ikey: i64, pos: u64, len: u32, pad: u32 = 0 };

const CS = struct {
    mode: u32, // 12, 16, 33, 36
    str: Col,
    uid: Col = .{},
    counter: Col = .{},
    date: Col = .{},
    dch: Col = .{},
    refresh: Col = .{},
    ctr: Counter = .{},
    lo: i32,
    hi: i32,
    top: [MAXT]Top10 = undefined,

    fn open(mode: u32) CS {
        var q: CS = .{
            .mode = mode,
            .str = colOpen("hits", if (mode == 12 or mode == 16) "SearchPhrase" else "URL"),
            .lo = daysFromCivil(2013, 7, 1),
            .hi = daysFromCivil(2013, 7, 31),
        };
        if (mode == 16) q.uid = colOpen("hits", "UserID");
        if (mode == 36) {
            q.counter = colOpen("hits", "CounterID");
            q.date = colOpen("hits", "EventDate");
            q.dch = colOpen("hits", "DontCountHits");
            q.refresh = colOpen("hits", "IsRefresh");
        }
        return q;
    }
    fn scatterTask(q: *CS, tid: usize) void {
        const s = scratch[tid];
        const p = &parts[tid];
        p.init(&arena[tid], @sizeOf(STuple));
        const bytes = q.str.aux;
        while (q.ctr.take()) |b| {
            if (q.mode == 36) { // cartes de zones : compteur et date
                const ec = &q.counter.dir[b];
                const ed = &q.date.dir[b];
                if (ec.min > 62 or ec.max < 62 or ed.max < q.lo or ed.min > q.hi) continue;
            }
            const uid: ?[*]const i64 = if (q.mode == 16) @ptrCast(q.uid.words(b)) else null;
            var pos: u64 = q.str.dir[b].aux_off;
            var vs: Vectors = .{ .count = q.str.dir[b].count };
            while (vs.next()) |v| {
                const st, const n = v;
                unpack(&q.str, b, st, n, &s.a); // longueurs
                for (s.x[0..n], s.a[0..n]) |*x, len| {
                    x.* = @intCast(pos);
                    pos += @intCast(len);
                }
                var k: usize = 0;
                if (q.mode == 36) {
                    unpack(&q.counter, b, st, n, &s.b);
                    const k1 = selBetween(&s.b, n, 62, 62, st, &s.pos);
                    if (k1 == 0) continue;
                    unpackSel(&q.date, b, s.pos[0..k1], &s.c);
                    unpackSel(&q.dch, b, s.pos[0..k1], &s.d);
                    unpackSel(&q.refresh, b, s.pos[0..k1], &s.e);
                    for (0..k1) |i| {
                        const j = @as(usize, @intCast(s.pos[i])) - st;
                        s.sel[k] = @intCast(j);
                        k += @intFromBool(s.c[i] >= q.lo and s.c[i] <= q.hi and s.d[i] == 0 and s.e[i] == 0 and s.a[j] > 0);
                    }
                } else if (q.mode == 12) {
                    k = selBetween(&s.a, n, 1, std.math.maxInt(i32), 0, &s.sel);
                } else {
                    for (s.sel[0..n], 0..) |*x, i| x.* = @intCast(i);
                    k = n;
                }
                for (s.h[0..k], s.sel[0..k]) |*h, j| {
                    const i: usize = @intCast(j);
                    h.* = hashBytes(bytes + @as(usize, @intCast(s.x[i])), @intCast(s.a[i]));
                }
                if (uid) |u| {
                    for (s.h[0..k], s.sel[0..k]) |*h, j| {
                        const x = hash64(h.* ^ (@as(u64, @bitCast(u[st + @as(usize, @intCast(j))])) *% K2));
                        h.* = if (x != 0) x else 1;
                    }
                }
                for (s.h[0..k], s.sel[0..k]) |h, j| {
                    const i: usize = @intCast(j);
                    p.push(STuple, partOf(h)).* = .{
                        .hash = h,
                        .ikey = if (uid) |u| u[st + i] else 0,
                        .pos = @intCast(s.x[i]),
                        .len = @intCast(s.a[i]),
                    };
                }
            }
        }
        p.close();
    }
    fn aggTask(q: *CS, tid: usize) void {
        var top: Top10 = .{};
        const bytes = q.str.aux;
        while (q.ctr.take()) |k| {
            var m = SMap.init(&arena[tid], pow2Start(partsCount(parts, k)), bytes);
            for (parts) |*p| {
                var c = p.head[k];
                while (c) |x| : (c = x.next) {
                    const ts = tuples(STuple, x);
                    for (ts, 0..) |t, i| {
                        if (special and i + AHEAD < ts.len) {
                            // à AHEAD tuples : la case et les octets du tuple ; à mi-distance : les octets de la case
                            const far = ts[i + AHEAD];
                            prefetch(&m.cells[far.hash & m.mask]);
                            prefetch(bytes + far.pos);
                            const near = ts[i + AHEAD / 2];
                            const cell = &m.cells[near.hash & m.mask];
                            if (cell.hash == near.hash) prefetch(bytes + cell.pos);
                        }
                        m.add(t.hash, t.ikey, t.pos, t.len);
                    }
                }
            }
            for (m.cells[0 .. m.mask + 1]) |c| {
                if (c.hash != 0) top.add(.{ .count = c.count, .len = c.len, .ikey = c.ikey, .pos = c.pos }, bytes);
            }
        }
        q.top[tid] = top;
    }
    fn run(q: *CS) void {
        q.ctr.set(q.str.nblocks);
        pool.run(q, scatterTask);
        q.ctr.set(NPART);
        pool.run(q, aggTask);
        var all: Top10 = .{};
        for (q.top[0..NT]) |*t| {
            for (t.t[0..t.n]) |x| all.add(x, q.str.aux);
        }
        for (all.t[0..all.n]) |t| {
            if (q.mode == 16) {
                emitInt(t.ikey);
                emit("|");
            }
            emit((q.str.aux + t.pos)[0..t.len]);
            emit("|");
            emitInt(t.count);
            emit("\n");
        }
    }
};

// ================================================================================================ C20
const C20 = struct {
    url: Col,
    ctr: Counter = .{},
    count: [MAXT][8]u64 = undefined,

    fn open() C20 {
        return .{ .url = colOpen("hits", "URL") };
    }
    fn task(q: *C20, tid: usize) void {
        const s = scratch[tid];
        var count: u64 = 0;
        while (q.ctr.take()) |b| {
            const nbytes = blockLengths(&q.url, b, &s.len);
            count += searchBlock(q.url.aux + q.url.dir[b].aux_off, nbytes, &s.len, "google", &s.rows);
        }
        q.count[tid][0] = count;
    }
    fn run(q: *C20) void {
        q.ctr.set(q.url.nblocks);
        pool.run(q, task);
        var count: u64 = 0;
        for (0..NT) |t| count += q.count[t][0];
        emitInt(count);
        emit("\n");
    }
};

// ================================================================================================ principal
fn perform(comptime Q: type, q: *Q, name: []const u8, reps: usize, print: bool, out: *Io.Writer) void {
    pool.start(NT);
    for (0..reps) |r| {
        for (arena[0..NT]) |*a| a.reset();
        res_len = 0;
        const t0 = Io.Clock.awake.now(io).nanoseconds;
        q.run();
        const dt = @as(f64, @floatFromInt(Io.Clock.awake.now(io).nanoseconds - t0)) * 1e-9;
        out.print("RESULT;{s};{s};{d};{d};{d:.6};{x:0>16}\n", .{ name, if (special) "s" else "p", NT, r, dt, fnv1a(res[0..res_len]) }) catch {};
        if (print and r == reps - 1) out.writeAll(res[0..res_len]) catch {};
        out.flush() catch {};
    }
}
fn alloc(comptime T: type) *T {
    return @ptrCast(@alignCast(hugeAlloc(@sizeOf(T))));
}

pub fn main(init: std.process.Init) !void {
    io = init.io;
    var obuf: [4096]u8 = undefined;
    var ow = Io.File.stdout().writer(io, &obuf);
    const out = &ow.interface;
    const args = try init.minimal.args.toSlice(init.arena.allocator());
    if (args.len < 5) die("usage : olap <requête> <fils> <répétitions> <répertoire des données> [--print]");
    const name = args[1];
    NT = std.fmt.parseInt(usize, args[2], 10) catch 0;
    const reps = std.fmt.parseInt(usize, args[3], 10) catch 0;
    data_dir = args[4];
    const print = args.len > 5 and std.mem.eql(u8, args[5], "--print");
    if (NT < 1 or NT > MAXT) die("nombre de fils");
    for (0..NT) |t| scratch[t] = alloc(Scratch);
    parts = @as([*]Parts, @ptrCast(@alignCast(hugeAlloc(NT * @sizeOf(Parts)))))[0..NT];
    parts2 = @as([*]Parts, @ptrCast(@alignCast(hugeAlloc(NT * @sizeOf(Parts)))))[0..NT];
    for (parts, parts2) |*a, *b| {
        a.wc = null;
        b.wc = null;
    }
    const eq = std.mem.eql;
    if (eq(u8, name, "t1")) {
        const q = alloc(T1);
        q.* = T1.open();
        perform(T1, q, name, reps, print, out);
    } else if (eq(u8, name, "t6")) {
        const q = alloc(T6);
        q.* = T6.open();
        perform(T6, q, name, reps, print, out);
    } else if (eq(u8, name, "t9")) {
        const q = alloc(T9);
        q.* = T9.open();
        perform(T9, q, name, reps, print, out);
    } else if (eq(u8, name, "t18")) {
        const q = alloc(T18);
        q.* = T18.open();
        perform(T18, q, name, reps, print, out);
    } else if (eq(u8, name, "c4")) {
        const q = alloc(C4);
        q.* = C4.open();
        perform(C4, q, name, reps, print, out);
    } else if (eq(u8, name, "c12") or eq(u8, name, "c16") or eq(u8, name, "c33") or eq(u8, name, "c36")) {
        const q = alloc(CS);
        q.* = CS.open(std.fmt.parseInt(u32, name[1..], 10) catch 0);
        perform(CS, q, name, reps, print, out);
    } else if (eq(u8, name, "c20")) {
        const q = alloc(C20);
        q.* = C20.open();
        perform(C20, q, name, reps, print, out);
    } else die("requête inconnue");
}
