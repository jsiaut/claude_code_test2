extern fn @"llvm.x86.avx512.conflict.d.512"(a: @Vector(16, i32)) @Vector(16, i32);
export fn f(a: *const @Vector(16, i32), r: *@Vector(16, i32)) void { r.* = @"llvm.x86.avx512.conflict.d.512"(a.*); }
