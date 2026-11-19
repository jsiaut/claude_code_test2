const std = @import("std");
pub fn main(init: std.process.Init) void { const n = init.minimal.args.vector.len + 3; var m: [n][3]f32 = undefined; m[0][0] = 1; std.debug.print("{d}\n", .{m[0][0]}); }
