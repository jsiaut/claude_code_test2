using Mmap
struct S; a::UInt8; b::UInt32; c::Float64; end
println("CAP;A2;1;fieldoffset(S, 3)=", fieldoffset(S, 3))
println("CAP;A5;1;reinterpret(UInt32, 1f0)=0x", string(reinterpret(UInt32, 1f0), base=16))
a = Mmap.mmap(open("/opt/msdata/k5_a.f32"), Vector{Float32}, 2048)
println("CAP;F4;1;Mmap.mmap -> Vector{Float32} : ", a[1])
x = Threads.Atomic{Int}(0); Threads.atomic_add!(x, 1); Threads.atomic_fence()
println("CAP;D5;0.5;Threads.atomic_fence ; pas de pause publique")
