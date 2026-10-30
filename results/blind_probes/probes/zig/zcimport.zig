const c = @cImport({ @cInclude("immintrin.h"); }); export fn f() void { _ = c; }
