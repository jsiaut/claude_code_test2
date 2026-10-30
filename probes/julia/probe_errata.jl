# Sonde des errata de la remarque sur Julia (docs/JULIA.md) : B2, D3, D5 (règle v2), E3.
using InteractiveUtils
p = Ptr{Int64}(Libc.malloc(8 * 1000)); a = unsafe_wrap(Array, p, 1000; own=false); a .= 1:1000
println("CAP;B2;0.5;Libc.malloc + unsafe_wrap (publics) : arène à la main, somme = ", sum(a)); Libc.free(p)
T = Base.Threads.PaddedSpinLock
println("CAP;D3;0.5;Threads.PaddedSpinLock public = ", Base.ispublic(Base.Threads, :PaddedSpinLock), ", sizeof = ", sizeof(T), " (propre aux verrous)")
pause() = ccall("llvm.x86.sse2.pause", llvmcall, Cvoid, ())
c = sprint(io -> code_native(io, pause, (); syntax=:att, debuginfo=:none))
println("CAP;D5;0.5;Threads.atomic_fence ; pause par ccall llvmcall : ", occursin(r"\bpause\b", c), " (règle v2 : 1)")
@inline expect(x::Bool) = Base.llvmcall(("declare i1 @llvm.expect.i1(i1, i1)\ndefine i8 @entry(i8 %0) #0 {\n%2 = trunc i8 %0 to i1\n%3 = call i1 @llvm.expect.i1(i1 %2, i1 true)\n%4 = zext i1 %3 to i8\nret i8 %4\n}\nattributes #0 = { alwaysinline }", "entry"), Bool, Tuple{Bool}, x)
f(x) = expect(x > 0) ? x + 1 : x - 1
ir = sprint(io -> code_llvm(io, f, (Int,); debuginfo=:none))
println("CAP;E3;0;llvm.expect par llvmcall : poids de branchement dans l'IR optimisé = ", occursin("branch_weights", ir))
