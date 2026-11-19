# Audit de la grille (docs/V4_PLAN.md 2.1) : sonde exécutée de Julia 1.13 (julia -t 4 -O3), cas positifs et code produit
# (@code_native, @code_llvm). run.sh y ajoute les recherches d'absence et la contre-épreuve de D4.
using InteractiveUtils, Distributed, SharedArrays
p(x...) = println(x...)
nat(f, types) = sprint(io -> code_native(io, f, types; syntax=:att, debuginfo=:none))
ll(f, types) = sprint(io -> code_llvm(io, f, types; debuginfo=:none))
cnt(s, re) = count(_ -> true, eachmatch(re, s))

struct Part; x::Float32; y::Float32; z::Float32; m::UInt8; end
struct Inl; n::UInt32; a::NTuple{16,Float32}; end

# A1
v = [Part(1, 2, 3, 4) for _ in 1:8]
GC.@preserve v begin
  stride = UInt(pointer(v, 2)) - UInt(pointer(v, 1))
  raw = unsafe_load(Ptr{NTuple{4,UInt8}}(pointer(v)))
end
p("CAP;A1;1;[exécutée] Vector{Part} (isbits) : pas de ", stride, " o = sizeof(Part) ", sizeof(Part), " ; les 4 premiers octets du tampon sont le Float32 x en ligne : ", join(string.(raw, base=16, pad=2), " "))
# A4 (½ : alignement par l'implémentation, pas d'attribut)
a = Vector{Float32}(undef, 1000)
p("FACT;A4;Vector{Float32}(undef, 1000) à ", UInt(pointer(a)) % 64, " mod 64 (alignement choisi par l'allocateur de tableaux)")
# A7, A8
p("CAP;A7;1;[exécutée] struct (n::UInt32, a::NTuple{16,Float32}) : ", sizeof(Inl), " o, fieldoffset(Inl, 2) = ", fieldoffset(Inl, 2), " (tuple en ligne)")
p("CAP;A8;1;[exécutée] UInt8/Int16/Float16/Float32 : ", sizeof(UInt8), "/", sizeof(Int16), "/", sizeof(Float16), "/", sizeof(Float32), " o ; Vector{UInt8}(undef, 1000) : ", sizeof(Vector{UInt8}(undef, 1000)), " o de données")
# B1 (0 : ramasse-miettes imposé)
n0 = Base.gc_num().pause
for i in 1:200; x = Vector{UInt8}(undef, 1 << 20); x[1] = 1; end
GC.gc(false)
p("CAP;B1;0;[exécutée] tout tableau et tout objet mutable passent par le ramasse-miettes : ", Base.gc_num().pause - n0, " collectes pendant 200 allocations de 1 Mio (Base.gc_num) ; GC.enable(false) suspend la collecte sans rendre la mémoire : aucune libération explicite")
# B3, B4
mkt(x) = (x, 2x, 3x)
mkp(x) = Part(x, x, x, 0x01)
mka(x) = [x, 2x, 3x]
function per_call(f, x, out)
  for i in eachindex(out); @inbounds out[i] = f(x); end    # échauffement
  n0 = Base.gc_num()
  for i in eachindex(out); @inbounds out[i] = f(x); end
  d = Base.GC_Diff(Base.gc_num(), n0)
  round(Int, d.allocd / length(out))
end
b3 = (per_call(mkt, 1.0f0, Vector{NTuple{3,Float32}}(undef, 1000)), per_call(mkp, 1.0f0, Vector{Part}(undef, 1000)),
      per_call(mka, 1.0f0, Vector{Vector{Float32}}(undef, 1000)))
p("CAP;B3;0.5;[exécutée] octets alloués par appel (Base.gc_num, résultats conservés) : tuple ", b3[1], " o, struct isbits ", b3[2], " o (pile ou registres) ; petit tableau [x, 2x, 3x] ", b3[3], " o (tas) : pas de tableau sur la pile")
function clo_esc(k)
  f = () -> k    # fermeture rendue, variable non réaffectée
  f
end
function boxed_esc(k)
  f = () -> k
  k = k + 1      # variable capturée puis réaffectée : Core.Box
  f
end
unstable(c) = c ? 1 : 1.0
sumu(n) = (s = 0; for i in 1:n; s += unstable(isodd(i)); end; s)
anysum(v) = (s = 0; for x in v; s += x; end; s)
va_any = Any[i for i in 1:1000]
b4 = (per_call(clo_esc, 1, Vector{Any}(undef, 1000)), per_call(boxed_esc, 1, Vector{Any}(undef, 1000)),
      per_call(anysum, va_any, Vector{Any}(undef, 100)), per_call(sumu, 1000, Vector{Float64}(undef, 100)))
p("CAP;B4;0.5;[exécutée] octets alloués par appel (Base.gc_num) : fermeture rendue ", b4[1], " o, la même sur une variable réaffectée (Core.Box) ", b4[2], " o ; somme sur un Vector{Any} de 1000 entiers ", b4[3], " o (boîtes) ; instabilité réduite à une petite union (Int ou Float64) : ", b4[4], " o : allocations implicites selon les types")
# B5
buf = zeros(UInt32, 8)
GC.@preserve buf begin
  q = pointer(buf)
  unsafe_store!(q, 42, 4)
  unsafe_store!(Ptr{UInt32}(UInt(q) + 16), 7)
end
p("CAP;B5;1;[exécutée] Ptr{UInt32} : unsafe_store!(q, 42, 4) -> buf[4] = ", buf[4], " ; écriture par décalage d'octets -> buf[5] = ", buf[5])
# C1 (½ : VecElement + llvmcall)
const V8 = NTuple{8,VecElement{Float32}}
vadd(a::V8, b::V8) = Base.llvmcall("%r = fadd <8 x float> %0, %1\nret <8 x float> %r", V8, Tuple{V8,V8}, a, b)
va = ntuple(i -> VecElement(Float32(i)), 8)
r = vadd(va, va)
p("CAP;C1;0.5;[exécutée] NTuple{8,VecElement{Float32}} + llvmcall : (a + a)[8] = ", r[8].value, ", ", cnt(nat(vadd, (V8, V8)), r"vaddps\s+%ymm"), " vaddps ymm ; aucun type vectoriel avec opérateurs dans Base (SIMD.jl est tiers)")
# C2 (llvmcall vers une intrinsèque)
const V16 = NTuple{16,VecElement{Int32}}
tern(a::V16, b::V16, c::V16) = Base.llvmcall(("""
  declare <16 x i32> @llvm.x86.avx512.pternlog.d.512(<16 x i32>, <16 x i32>, <16 x i32>, i32)
  define <16 x i32> @entry(<16 x i32> %0, <16 x i32> %1, <16 x i32> %2) #0 {
    %r = call <16 x i32> @llvm.x86.avx512.pternlog.d.512(<16 x i32> %0, <16 x i32> %1, <16 x i32> %2, i32 150)
    ret <16 x i32> %r
  }
  attributes #0 = { alwaysinline }""", "entry"), V16, Tuple{V16,V16,V16}, a, b, c)
k = Int32(length(ARGS) + 1)
t = tern(ntuple(_ -> VecElement(Int32(12) * k), 16), ntuple(_ -> VecElement(Int32(10) * k), 16), ntuple(_ -> VecElement(k), 16))
p("CAP;C2;1;[exécutée] Base.llvmcall vers llvm.x86.avx512.pternlog.d.512 : 12 ^ 10 ^ 1 = ", t[1].value, ", ", cnt(nat(tern, (V16, V16, V16)), r"vpternlogd"), " vpternlogd ; ½ en v1")
# C4
sum_plain(x) = (s = 0f0; for v in x; s += v; end; s)
sum_fast(x) = (s = 0f0; @fastmath for v in x; s += v; end; s)
sum_simd(x) = (s = 0f0; @simd for i in eachindex(x); @inbounds s += x[i]; end; s)
nf = nat(sum_fast, (Vector{Float32},)); ns = nat(sum_simd, (Vector{Float32},)); np = nat(sum_plain, (Vector{Float32},))
p("CAP;C4;1;[exécutée] @fastmath et @simd, par expression ou par boucle : vaddps ymm/zmm = ", cnt(nf, r"vaddps\s+%[yz]mm"), " (@fastmath), ", cnt(ns, r"vaddps\s+%[yz]mm"), " (@simd), ", cnt(np, r"vaddps\s+%[yz]mm"), " sans ($(cnt(np, r"vaddss")) vaddss)")
# C5, D1
ids = zeros(Int32, 4000)
Threads.@threads for i in 1:4000; ids[i] = ccall(:gettid, Int32, ()); end
r5 = Threads.@spawn sum(1:10)
p("CAP;C5;1;[exécutée] Threads.@threads sur ", length(unique(ids)), " fils distincts (gettid, julia -t ", Threads.nthreads(), ")")
tids = zeros(Int32, 4); parts = zeros(Int, 4)
@sync for t in 1:4
  Threads.@spawn begin
    s = 0; for i in (t-1)*1000:t*1000-1; s += i; end
    parts[t] = s; tids[t] = ccall(:gettid, Int32, ())
  end
end
p("CAP;D1;1;[exécutée] Threads.@spawn : 4 tâches sur ", length(unique(tids)), " fils (gettid), somme ", sum(parts), " (attendu 7998000) ; ", fetch(r5))
# D2
mutable struct AF; @atomic x::Int; end
st_rel(a::AF) = (@atomic :release a.x = 1; nothing)
st_seq(a::AF) = (@atomic :sequentially_consistent a.x = 1; nothing)
add_mon(a::AF) = (@atomic :monotonic a.x += 1)
st_rel(AF(0)); st_seq(AF(0)); add_mon(AF(0))
p("CAP;D2;1;[exécutée] @atomic à ordre explicite, code produit : :release = ", cnt(nat(st_rel, (AF,)), r"\bmovq\s+\$1,"), " mov et ", cnt(nat(st_rel, (AF,)), r"xchg|mfence"), " xchg ; :sequentially_consistent = ", cnt(nat(st_seq, (AF,)), r"xchg"), " xchg ; @atomic :monotonic a.x += 1 = ", cnt(nat(add_mon, (AF,)), r"lock"), " instruction lock")
# D5 (atomic_fence + pause par llvmcall)
spin() = (Threads.atomic_fence(); Base.llvmcall(("""
  declare void @llvm.x86.sse2.pause()
  define void @entry() #0 {
    call void @llvm.x86.sse2.pause()
    ret void
  }
  attributes #0 = { alwaysinline }""", "entry"), Cvoid, Tuple{}))
spin()
p("CAP;D5;1;[exécutée] Threads.atomic_fence et llvm.x86.sse2.pause par llvmcall : ", cnt(nat(spin, ()), r"\bpause\b"), " pause et ", cnt(nat(spin, ()), r"mfence|lock\s+or"), " barrière ; ½ en v1 (pause hors de l'API publique)")
# E1, E2, E4
p("CAP;E1;1;[exécutée] @code_native : ", length(split(nat(sum_simd, (Vector{Float32},)), '\n')), " lignes d'assembleur pour sum_simd ; @code_llvm pour l'IR")
asmadd(x::Int64) = Base.llvmcall("%r = call i64 asm \"leaq 1(\$1), \$0\", \"=r,r\"(i64 %0)\nret i64 %r", Int64, Tuple{Int64}, x)
p("CAP;E2;1;[exécutée] llvmcall portant de l'assembleur en ligne (asm de l'IR de LLVM) : leaq 1(x) avec x = 41 -> ", asmadd(41), " ; ½ en v1")
pf(x::Ptr{Float32}) = Base.llvmcall(("""
  declare void @llvm.prefetch.p0(ptr, i32, i32, i32)
  define void @entry(ptr %0) #0 {
    call void @llvm.prefetch.p0(ptr %0, i32 0, i32 3, i32 1)
    ret void
  }
  attributes #0 = { alwaysinline }""", "entry"), Cvoid, Tuple{Ptr{Float32}}, x)
GC.@preserve a pf(pointer(a))
p("CAP;E4;1;[exécutée] llvmcall vers llvm.prefetch : ", cnt(nat(pf, (Ptr{Float32},)), r"prefetcht0"), " prefetcht0 ; ½ en v1")
# E5 (½ : Base.Experimental.@aliasscope, expérimental et partiel)
function copy_as!(dst, src)
  Base.Experimental.@aliasscope for i in eachindex(dst, src)
    @inbounds dst[i] = Base.Experimental.Const(src)[i]
  end
end
function copy_plain!(dst, src)
  for i in eachindex(dst, src); @inbounds dst[i] = src[i]; end
end
function axpy_as!(y, x)
  Base.Experimental.@aliasscope for i in eachindex(y, x)
    @inbounds y[i] = y[i] + 2f0 * Base.Experimental.Const(x)[i]
  end
end
llr(f) = sprint(io -> code_llvm(io, f, (Vector{Float32}, Vector{Float32}); debuginfo=:none, raw=true))
mc(f) = cnt(llr(f), r"vector\.memcheck")
p("CAP;E5;0.5;[exécutée] Base.Experimental.@aliasscope et Const (module Experimental) : contrôles de recouvrement (vector.memcheck) dans l'IR de la copie : ", mc(copy_as!), " avec, ", mc(copy_plain!), " sans ; mais ", mc(axpy_as!), " pour y[i] = y[i] + 2Const(x)[i] : effet partiel, sous un module expérimental")
# E6
idx(x, i) = x[i]
idxu(x, i) = @inbounds x[i]
idx([1f0], 1); idxu([1f0], 1)
p("CAP;E6;1;[exécutée] x[i] : ", cnt(nat(idx, (Vector{Float32}, Int)), r"throw_boundserror"), " appel à throw_boundserror ; @inbounds x[i] : ", cnt(nat(idxu, (Vector{Float32}, Int)), r"throw_boundserror"), " (local, par expression ; --check-bounds=no en global)")
# E7
@generated function fibg(::Val{N}) where N
  a, b = 0, 1
  for _ in 1:N; a, b = b, a + b; end
  return :($a)
end
fib60() = fibg(Val(60))
gsum(x, y) = x + y
p("CAP;E7;1;[exécutée] @generated : fibg(Val(60)) = ", fib60(), ", calculé à la compilation (", cnt(nat(fib60, ()), r"1548008755920"), " constante immédiate dans le code natif) ; spécialisation par types : gsum(Float32) = ", gsum(1.5f0, 2.5f0), ", gsum(Float64) = ", gsum(1.5, 2.25))
# F1
nrow = 3 + length(ARGS)
M = zeros(Float32, nrow, 4)
p("CAP;F1;1;[exécutée] Matrix{Float32}(", nrow, ", 4) de taille connue à l'exécution : M[2,1] - M[1,1] = ", UInt(pointer(M, 2)) - UInt(pointer(M, 1)), " o, M[1,2] - M[", nrow, ",1] = ", UInt(pointer(M, nrow + 1)) - UInt(pointer(M, nrow)), " o (contigu, par colonnes)")
# F2 (½ : Distributed, SharedArrays : des processus)
addprocs(2)
@everywhere using SharedArrays
S = SharedArray{Int}(10)
@sync @distributed for i in 1:10; S[i] = myid(); end
p("CAP;F2;0.5;[exécutée] Distributed (addprocs(2)) et SharedArray : propriétaires des éléments ", unique(S), " ; processus et mémoire partagée par mmap, sans construction NUMA ni distribution par nœud")
# F3
p("CAP;F3;1;[exécutée] typemax(UInt32) + 1 = ", typemax(UInt32) + UInt32(1), ", typemax(Int32) + Int32(1) = ", typemax(Int32) + Int32(1), ", 0xfa + 0x0a = ", 0xfa + 0x0a, " (arithmétique entière modulaire)")
