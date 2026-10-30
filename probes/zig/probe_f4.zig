// Sonde Zig 0.17 (ajoutée le 30/10 après la remarque sur Zig, docs/ZIG.md) : F4 par std.Io.File.MemoryMap, l'interface
// portable de la bibliothèque standard (depuis 0.16), au lieu de std.posix.mmap. Vérifie que la projection est réelle :
// le fichier apparaît dans /proc/self/maps à l'adresse de la mémoire rendue, sans copie.
const std = @import("std");
const Io = std.Io;
pub fn main(init: std.process.Init) !void {
    const io = init.io;
    const path = "/opt/msdata/k5_a.f32";
    const f = try Io.Dir.cwd().openFile(io, path, .{});
    defer f.close(io);
    var mm = try Io.File.MemoryMap.create(io, f, .{ .len = 8192, .protection = .{ .read = true, .write = false } });
    defer mm.destroy(io);
    const fl = std.mem.bytesAsSlice(f32, mm.memory);
    // lecture en flux : readFileAlloc se fie à la taille annoncée, nulle sous /proc (docs/FINDINGS.md)
    const mf = try Io.Dir.cwd().openFile(io, "/proc/self/maps", .{});
    defer mf.close(io);
    var rbuf: [4096]u8 = undefined;
    var fr = mf.readerStreaming(io, &rbuf);
    const maps = try fr.interface.allocRemaining(init.gpa, .unlimited);
    var buf: [32]u8 = undefined;
    const addr = try std.fmt.bufPrint(&buf, "{x}-", .{@intFromPtr(mm.memory.ptr)});
    var mapped = false;
    var it = std.mem.splitScalar(u8, maps, '\n');
    while (it.next()) |line| {
        if (std.mem.startsWith(u8, line, addr) and std.mem.endsWith(u8, line, path)) mapped = true;
    }
    std.debug.print("CAP;F4;1;std.Io.File.MemoryMap + bytesAsSlice : {d}, projection dans /proc/self/maps : {}\n", .{ fl[0], mapped });
}
