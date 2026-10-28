use CTypes;
record S { var a: uint(8); var b: uint(32); var c: real; }
writeln("CAP;A2;1;c_offsetof(S, \"c\")=", c_offsetof(S, "c"));
var p = allocate(real(32), 64, alignment=64);
writeln("CAP;A4;0.5;allocate(alignment=64) -> adresse mod 64 = ", (p: c_uintptr) % 64);
writeln("CAP;A5;0.5;(1.0: real(32)).transmute(uint(32)) = ", (1.0: real(32)).transmute(uint(32)));
atomicFence();
writeln("CAP;D5;0.5;atomicFence");
deallocate(p);
