// Contre-épreuve C2 : nom d'intrinsèque LLVM déclaré comme fonction externe (aucun mécanisme documenté par Zig).
const std = @import("std");
extern fn @"llvm.x86.avx512.pternlog.d.512"(a: @Vector(16, i32), b: @Vector(16, i32), c: @Vector(16, i32), imm: i32) @Vector(16, i32);
pub fn main(init: std.process.Init) void {
    const k: i32 = @intCast(init.minimal.args.vector.len); // 1 à l'exécution, inconnu à la compilation
    const a: @Vector(16, i32) = @splat(12 * k);
    const b: @Vector(16, i32) = @splat(10 * k);
    const c: @Vector(16, i32) = @splat(k);
    const r = @"llvm.x86.avx512.pternlog.d.512"(a, b, c, 0x96);
    std.debug.print("{d}\n", .{r[0]});
}
