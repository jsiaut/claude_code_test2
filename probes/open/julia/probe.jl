# v4, point 6 (docs/V4_OPEN.md, 4) : sondes de la grille ouverte de Julia
# (B2 : Bumper ; C1 : VectorizationBase ; D4 : ThreadPinningCore ; F2 : NUMA).
using Bumper, VectorizationBase, ThreadPinningCore, NUMA, InteractiveUtils

# B2 : tableaux alloués par @alloc dans @no_escape, sur le tampon par défaut
function b2()
    buf = default_buffer()
    addrs = UInt[]
    s = 0.0
    @no_escape buf begin
        a = @alloc(Float64, 1000)
        b = @alloc(Float64, 1000)
        a .= 1.0; b .= 2.0
        s = sum(a) + sum(b)
        push!(addrs, UInt(pointer(a)), UInt(pointer(b)))
    end
    @no_escape buf begin
        c = @alloc(Float64, 1000)
        push!(addrs, UInt(pointer(c)))
    end
    allocs = @allocated @no_escape buf begin
        d = @alloc(Float64, 1000); d .= 3.0; sum(d)
    end
    println("RESULT;B2;Bumper;@no_escape + @alloc(Float64, 1000) deux fois : écart entre les tampons = $(Int(addrs[2] - addrs[1])) octets, somme = $s ; après la sortie du bloc, le tableau suivant reprend l'adresse du premier = $(addrs[3] == addrs[1]) ; octets alloués sur le tas du GC par un bloc = $allocs")
end

# C1 : Vec de VectorizationBase
function dot_vb(a::Vector{Float32}, b::Vector{Float32})
    pa = stridedpointer(a); pb = stridedpointer(b)
    acc = Vec(ntuple(_ -> 0.0f0, Val(16))...)
    GC.@preserve a b begin
        @inbounds for i in 0:16:length(a)-1
            va = vload(pa, (MM{16}(i + 1),))
            vb = vload(pb, (MM{16}(i + 1),))
            acc = muladd(va, vb, acc)
        end
    end
    VectorizationBase.vsum(acc)
end
function c1()
    a = Float32[i % 7 for i in 0:4095]
    b = Float32[i % 5 for i in 0:4095]
    d = dot_vb(a, b)
    io = IOBuffer()
    code_native(io, dot_vb, (Vector{Float32}, Vector{Float32}); debuginfo=:none)
    asm = String(take!(io))
    nfma = count(l -> occursin(r"vfmadd\d*ps", l) && occursin("zmm", l), split(asm, '\n'))
    println("RESULT;C1;VectorizationBase;Vec{16,Float32} (stridedpointer, vload avec MM{16}, muladd, vsum) : produit scalaire de 4096 = $d (somme scalaire $(sum(a .* b))) ; code natif de dot_vb : $nfma vfmadd…ps sur zmm ; pick_vector_width(Float32) = $(VectorizationBase.pick_vector_width(Float32))")
end

# D4 : ThreadPinningCore
function d4()
    t = Threads.nthreads()
    res = fetch(Threads.@spawn begin
        pinthread(2)
        cpus = Set(getcpuid() for _ in 1:1000)
        (ispinned(), cpus)
    end)
    println("RESULT;D4;ThreadPinningCore;$t fils ; pinthread(2) dans une tâche : ispinned = $(res[1]), getcpuid sur 1000 lectures = $(sort(collect(res[2])))")
end

# F2 : NUMA (libnuma)
function f2()
    avail = numa_available()
    nn = nnumanodes()
    v = Vector{Float64}(numanode(1), 1 << 19)
    v .= 1.0
    node = which_numa_node(v)
    println("RESULT;F2;NUMA;numa_available = $avail, $nn nœud(s) ; Vector{Float64}(numanode(1), 2^19) (nœuds numérotés à partir de 1) : pages sur le nœud $node (which_numa_node) ; current_numa_node = $(current_numa_node())")
end

b2(); c1(); d4(); f2()
