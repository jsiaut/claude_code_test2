# Implémentation Julia 1.13 (Base et bibliothèques standard seules). Voir docs/SPEC.md.
module MS

# ------------------------------------------------------------------ harnais
const DATA = get(ENV, "MS_DATA", "/opt/msdata")
const WARMUP = parse(Int, get(ENV, "WARMUP", "1"))
load(::Type{T}, name) where {T} = copy(reinterpret(T, read(joinpath(DATA, name))))  # tableaux Julia alignés sur 64 o
result(k, v, p, rep, sec, chk) = (println("RESULT;$k;$v;$p;$rep;", round(sec; digits=9), ";", chk); flush(stdout))
secs(t0) = (time_ns() - t0) * 1e-9
fmt6(x) = string(round(x; digits=6))
using Printf

# ------------------------------------------------------------------ K1
const N1 = 1 << 22
struct Particle  # immuable et « isbits » : stocké en ligne dans un Vector (AoS valeur)
    x::Float32; y::Float32; z::Float32; vx::Float32; vy::Float32; vz::Float32; ax::Float32; ay::Float32; az::Float32
    mass::Float32; charge::Float32; radius::Float32; temp::Float32; pressure::Float32; energy::Float32; density::Float32
end
@noinline function k1_natural(ps::Vector{Particle})
    e = 0.0
    for p in ps
        e += 0.5 * p.mass * (p.vx * p.vx + p.vy * p.vy + p.vz * p.vz)
    end
    e
end
@noinline function k1_aos(ps::Vector{Particle})
    e = 0.0
    @inbounds @simd for i in eachindex(ps)   # @simd autorise la réassociation -> vectorisation
        p = ps[i]
        e += Float64(0.5f0 * p.mass * (p.vx * p.vx + p.vy * p.vy + p.vz * p.vz))
    end
    e
end
@noinline function k1_soa(vx::Vector{Float32}, vy::Vector{Float32}, vz::Vector{Float32}, m::Vector{Float32})
    e = 0.0
    @inbounds @simd for i in eachindex(vx)
        e += Float64(0.5f0 * m[i] * muladd(vz[i], vz[i], muladd(vy[i], vy[i], vx[i] * vx[i])))
    end
    e
end
# Empreinte K1 (D2a) : octets vivants du tas après GC complet, et RSS courant (pages de 4 Kio)
live_now() = (GC.gc(true); Int(Base.gc_live_bytes()))
rss_now() = parse(Int, split(read("/proc/self/statm", String))[2]) * 4096
function run_k1(v, reps)
    v == "footprint0" && return result("k1", v, "energy", 0, 0, "0")
    raw = load(Float32, "k1_particles.f32")
    v == "footprint_raw" && return result("k1", v, "energy", 0, 0, "0")
    m1, r1 = v == "footprint" ? (live_now(), rss_now()) : (0, 0)  # P1 : tampon brut chargé
    ps = copy(reinterpret(Particle, raw))
    if v == "footprint"
        m2, r2 = live_now(), rss_now()  # P2 : collection construite, tampon brut encore vivant
        println("META;mem;live;$m1;$m2\nMETA;rss;$r1;$r2\nMETA;raw0;$(raw[1])")
        return result("k1", v, "energy", 0, 0, fmt6(k1_natural(ps)))
    end
    if v == "soa"
        cols = [raw[k:16:end] for k in 1:16]
        for r in -WARMUP:reps-1
            t0 = time_ns(); e = k1_soa(cols[4], cols[5], cols[6], cols[10]); dt = secs(t0)
            r >= 0 && result("k1", v, "energy", r, dt, fmt6(e))
        end
        return
    end
    if v == "natural_shuffled"
        perm = load(UInt32, "k1_perm.u32")
        ps = ps[perm .+ 1]
    end
    f = v == "aos" ? k1_aos : k1_natural
    for r in -WARMUP:reps-1
        t0 = time_ns(); e = f(ps); dt = secs(t0)
        r >= 0 && result("k1", v, "energy", r, dt, fmt6(e))
    end
end

# ------------------------------------------------------------------ K2
@noinline function k2_chase(a::Vector{UInt32}, h)
    i = UInt32(0)
    @inbounds for _ in 1:h
        i = a[i+1]
    end
    i
end
function run_k2(v, reps, p)
    a = load(UInt32, "k2_chase_$p.u32")
    for r in -WARMUP:reps-1
        t0 = time_ns(); i = k2_chase(a, 4200000); dt = secs(t0)
        r >= 0 && result("k2", v, p, r, dt, string(i))
    end
end

# ------------------------------------------------------------------ K3
const ITER3 = 1 << 25
function k3_worker(m::AtomicMemory{UInt64}, idx::Int, rmw::Bool)
    if rmw
        for _ in 1:ITER3
            @atomic :monotonic m[idx] += 1
        end
    else
        for _ in 1:ITER3
            x = @atomic :monotonic m[idx]
            @atomic :monotonic m[idx] = x + 1
        end
    end
end
function run_k3(v, reps)
    rmw = startswith(v, "rmw")
    stride = endswith(v, "padded") ? 16 : 1  # 128 o ou 8 o
    println("META;k3_mechanism;", rmw ? "@atomic :monotonic m[i] += 1 (lock xadd)" : "@atomic :monotonic lecture/écriture (mov)")
    m = AtomicMemory{UInt64}(undef, 128)
    for r in -WARMUP:reps-1
        for t in 0:3
            @atomic m[17+t*stride] = UInt64(0)
        end
        t0 = time_ns()
        tasks = [Threads.@spawn k3_worker(m, 17 + t * stride, rmw) for t in 0:3]
        foreach(wait, tasks)
        dt = secs(t0)
        s = sum(@atomic(m[17+t*stride]) for t in 0:3)
        r >= 0 && result("k3", v, "4x2^25", r, dt, string(s))
    end
end

# ------------------------------------------------------------------ K4
@noinline function k4_natural(v::Vector{UInt8})
    s = UInt64(0)
    for x in v
        if x >= 128
            s += x
        end
    end
    s
end
@noinline function k4_branchless(v::Vector{UInt8})
    s = UInt64(0)
    @inbounds @simd for i in eachindex(v)
        x = v[i]
        s += UInt64(x) * UInt64(x >> 7)
    end
    s
end
function run_k4(v, reps)
    d = load(UInt8, "k4_bytes.u8")
    v == "natural_sorted" && sort!(d)
    f = v == "branchless_unsorted" ? k4_branchless : k4_natural
    for r in -WARMUP:reps-1
        t0 = time_ns(); s = f(d); dt = secs(t0)
        r >= 0 && result("k4", v, "16M", r, dt, string(s))
    end
end

# ------------------------------------------------------------------ K5
const INNER5 = 1 << 16
@noinline function k5_natural(a::Vector{Float32}, b::Vector{Float32})
    s = 0.0f0
    for i in eachindex(a)
        s += a[i] * b[i]
    end
    s
end
@noinline function k5_tuned(a::Vector{Float32}, b::Vector{Float32})
    s = 0.0f0
    @inbounds @simd for i in eachindex(a)
        s = muladd(a[i], b[i], s)
    end
    s
end
const SINK = Ref{Vector{Float32}}()
function run_k5(v, reps)
    a = load(Float32, "k5_a.f32"); b = load(Float32, "k5_b.f32")
    f = v == "tuned" ? k5_tuned : k5_natural
    for r in -WARMUP:reps-1
        d = 0.0f0
        t0 = time_ns()
        for _ in 1:INNER5
            SINK[] = a                  # barrière : relu depuis un Ref global
            d = f(SINK[], b)
        end
        dt = secs(t0)
        r >= 0 && result("k5", v, "2048x65536", r, dt, @sprintf("%.4f", d))
    end
end

# ------------------------------------------------------------------ K6
const N6 = 1 << 24
struct Cols
    sd::Vector{Int32}; pr::Vector{Int32}; q::Vector{UInt8}; d::Vector{UInt8}; t::Vector{UInt8}; rf::Vector{UInt8}; ls::Vector{UInt8}
end
@noinline function q6_natural(c::Cols, lo, hi)
    s = Int64(0)
    for i in lo:hi
        if c.sd[i] >= 8766 && c.sd[i] < 9131 && c.d[i] >= 5 && c.d[i] <= 7 && c.q[i] < 24
            s += Int64(c.pr[i]) * c.d[i]
        end
    end
    s
end
@noinline function q6_tuned(c::Cols, lo, hi)
    sd, pr, q, d = c.sd, c.pr, c.q, c.d
    s = Int64(0)
    @inbounds @simd for i in lo:hi
        m = ((sd[i] - Int32(8766)) % UInt32 < UInt32(365)) & ((d[i] - 0x05) <= 0x02) & (q[i] < 0x18)
        s += ifelse(m, Int64(pr[i] * Int32(d[i])), Int64(0))
    end
    s
end
@noinline function q1_natural(c::Cols, lo, hi, acc::Matrix{Int64})
    for i in lo:hi
        if c.sd[i] <= 10471
            g = c.rf[i] * 2 + c.ls[i] + 1
            p = Int64(c.pr[i]); dp = p * (100 - c.d[i])
            acc[1, g] += 1; acc[2, g] += c.q[i]; acc[3, g] += p; acc[4, g] += dp; acc[5, g] += dp * (100 + c.t[i])
        end
    end
end
# Q1 optimisé : agrégation masquée par groupe sur blocs, @simd (vectorisé par LLVM)
@noinline function q1_tuned(c::Cols, lo, hi, acc::Matrix{Int64})
    sd, pr, q, d, t, rf, ls = c.sd, c.pr, c.q, c.d, c.t, c.rf, c.ls
    B = 4096
    @inbounds for b0 in lo:B:hi
        b1 = min(b0 + B - 1, hi)
        for g in Int32(0):Int32(5)
            cnt = Int32(0); sq = Int32(0); sp = Int32(0); sdp = Int32(0); sch = Int64(0)
            @simd for i in b0:b1
                m = (sd[i] <= Int32(10471)) & (Int32(rf[i]) * Int32(2) + Int32(ls[i]) == g)
                dp = pr[i] * (Int32(100) - Int32(d[i]))
                cnt += m
                sq += ifelse(m, Int32(q[i]), Int32(0))
                sp += ifelse(m, pr[i], Int32(0))
                sdp += ifelse(m, dp, Int32(0))
                sch += ifelse(m, Int64(dp) * (100 + Int64(t[i])), Int64(0))
            end
            acc[1, g+1] += cnt; acc[2, g+1] += sq; acc[3, g+1] += sp; acc[4, g+1] += sdp; acc[5, g+1] += sch
        end
    end
end
function run_k6(v, reps, p)
    c = Cols(load(Int32, "k6_shipdate.i32"), load(Int32, "k6_extendedprice.i32"), load(UInt8, "k6_quantity.u8"), load(UInt8, "k6_discount.u8"),
             load(UInt8, "k6_tax.u8"), load(UInt8, "k6_returnflag.u8"), load(UInt8, "k6_linestatus.u8"))
    q1 = p == "q1"
    for r in -WARMUP:reps-1
        t0 = time_ns()
        s = Int64(0)
        if v == "mt"
            tasks = map(0:3) do t
                lo, hi = N6 ÷ 4 * t + 1, N6 ÷ 4 * (t + 1)
                Threads.@spawn q1 ? (local acc = zeros(Int64, 5, 6); q1_tuned(c, lo, hi, acc); sum(acc)) : q6_tuned(c, lo, hi)
            end
            s = sum(fetch.(tasks))
        elseif q1
            a = zeros(Int64, 5, 6)
            (v == "tuned" ? q1_tuned : q1_natural)(c, 1, N6, a)
            s = sum(a)
        else
            s = v == "tuned" ? q6_tuned(c, 1, N6) : q6_natural(c, 1, N6)
        end
        dt = secs(t0)
        r >= 0 && result("k6", v, p, r, dt, string(s))
    end
end

# ------------------------------------------------------------------ K7
struct Slot
    key::UInt32; count::UInt32; sum::UInt64
end
function run_k7(v, reps)
    keys = load(UInt32, "k7_keys.u32"); vals = load(UInt32, "k7_vals.u32")
    for r in -WARMUP:reps-1
        nk = UInt64(0); ws = UInt64(0)
        if v == "natural"
            t0 = time_ns()
            m = Dict{UInt32,Tuple{UInt32,UInt64}}()
            for i in eachindex(keys)
                k = keys[i]
                c, s = get(m, k, (UInt32(0), UInt64(0)))
                m[k] = (c + 1, s + vals[i])
            end
            dt = secs(t0)
            nk = length(m)
            for (k, (_, s)) in m
                ws += s * ((k & 1023) + 1)
            end
        else
            LOG = 21; CAP = 1 << LOG
            t0 = time_ns()
            tab = fill(Slot(0, 0, 0), CAP)
            @inbounds for i in eachindex(keys)
                k = keys[i]
                s = ((k * 0x9E3779B1) >> (32 - LOG)) + 1
                while tab[s].count != 0 && tab[s].key != k
                    s = (s & (CAP - 1)) + 1
                end
                e = tab[s]
                tab[s] = Slot(k, e.count + 1, e.sum + vals[i])
            end
            dt = secs(t0)
            for e in tab
                if e.count != 0
                    nk += 1; ws += e.sum * ((e.key & 1023) + 1)
                end
            end
        end
        r >= 0 && result("k7", v, "16M/1M", r, dt, "$nk:$ws")
    end
end

# ------------------------------------------------------------------ K8
mutable struct Node
    v::Int64; l::Union{Node,Nothing}; r::Union{Node,Nothing}
end
function t_build(d, c::Base.RefValue{Int64})
    n = Node(c[], nothing, nothing); c[] += 1
    if d > 0
        n.l = t_build(d - 1, c); n.r = t_build(d - 1, c)
    end
    n
end
t_sum(n::Node) = n.v + (n.l === nothing ? 0 : t_sum(n.l)) + (n.r === nothing ? 0 : t_sum(n.r))
struct ANode
    v::Int64; l::Int32; r::Int32
end
function a_build(a::Vector{ANode}, top::Base.RefValue{Int32}, d, c::Base.RefValue{Int64})
    i = top[]; top[] += 1
    @inbounds a[i] = ANode(c[], -1, -1); c[] += 1
    if d > 0
        l = a_build(a, top, d - 1, c); r = a_build(a, top, d - 1, c)
        @inbounds a[i] = ANode(a[i].v, l, r)
    end
    i
end
a_sum(a::Vector{ANode}, i::Int32) = i < 0 ? 0 : (@inbounds n = a[i]; n.v + a_sum(a, n.l) + a_sum(a, n.r))
const KEEP = Ref{Node}()
function run_k8(v, reps)
    Q = 16384
    tuned = v == "tuned"
    KEEP[] = t_build(20, Ref(0)); lsum = t_sum(KEEP[])
    lat = zeros(Int64, Q)
    arena = Vector{ANode}(undef, 2047)
    for r in -WARMUP:reps-1
        total = 0
        t0 = time_ns()
        for q in 0:Q-1
            a = time_ns()
            c = Ref(Int64(q))
            if tuned
                top = Ref(Int32(1))
                s = a_sum(arena, a_build(arena, top, 10, c))
            else
                s = t_sum(t_build(10, c))
            end
            total += s
            lat[q+1] = time_ns() - a
        end
        dt = secs(t0)
        if r >= 0
            result("k8", v, "16384x2047", r, dt, string(total + lsum))
            sort!(lat)
            println("LAT;$v;$(lat[Q÷2+1]);$(lat[Q*9÷10+1]);$(lat[Q*99÷100+1]);$(lat[Q*999÷1000+1]);$(lat[Q])")
        end
    end
end

# ------------------------------------------------------------------ K9
const M9 = 2048
k9_init(i, j) = ((i * 31 + j * 17) % 1024) / 1024.0   # i = ligne, j = colonne (base 0)
# naturel : Matrix{Float64} (colonne-majeur) parcourue dans l'ordre mémoire, comme le recommande le manuel
@noinline function k9_natural(a::Matrix{Float64}, b::Matrix{Float64})
    for j in 2:M9-1, i in 2:M9-1
        b[i, j] = 0.25 * (((a[i-1, j] + a[i+1, j]) + a[i, j-1]) + a[i, j+1])
    end
end
@noinline function k9_cols(a::Matrix{Float64}, b::Matrix{Float64}, c0, c1)
    @inbounds for j in c0:c1
        @simd for i in 2:M9-1
            b[i, j] = 0.25 * (((a[i-1, j] + a[i+1, j]) + a[i, j-1]) + a[i, j+1])
        end
    end
end
function run_k9(v, reps)
    for r in -WARMUP:reps-1
        a = [k9_init(i, j) for i in 0:M9-1, j in 0:M9-1]
        b = copy(a)
        t0 = time_ns()
        for _ in 1:4
            if v == "natural"
                k9_natural(a, b)
            elseif v == "tuned"
                k9_cols(a, b, 2, M9 - 1)
            else
                tasks = [Threads.@spawn k9_cols(a, b, 2 + (M9 - 2) * t ÷ 4, 1 + (M9 - 2) * (t + 1) ÷ 4) for t in 0:3]
                foreach(wait, tasks)
            end
            a, b = b, a
        end
        dt = secs(t0)
        s = 0.0
        for x in a
            s += x
        end
        r >= 0 && result("k9", v, "2048^2x4", r, dt, @sprintf("%.15e", s))
    end
end

# ------------------------------------------------------------------ K10
const M10 = 1 << 22
const CAP10 = 1 << 14
function run_k10(v, reps)
    for r in -WARMUP:reps-1
        t0 = time_ns()
        if v == "natural"  # Channel{T} : canal borné de Base, producteur et consommateur sur des threads
            ch = Channel{UInt64}(CAP10)
            prod = Threads.@spawn begin
                for x in UInt64(1):UInt64(M10)
                    put!(ch, x)
                end
            end
            cons = Threads.@spawn begin
                s = UInt64(0)
                for _ in 1:M10
                    s += take!(ch)
                end
                s
            end
            wait(prod); s = fetch(cons)
        else
            ctl = AtomicMemory{Int}(undef, 64)  # écriture @17, lecture @49 : 256 o d'écart
            @atomic ctl[17] = 0; @atomic ctl[49] = 0
            buf = Vector{UInt64}(undef, CAP10)
            prod = Threads.@spawn begin
                w = 0; rc = 0
                for x in UInt64(1):UInt64(M10)
                    spins = 0
                    while w - rc == CAP10
                        rc = @atomic :acquire ctl[49]
                        # ordonnanceur coopératif : sans yield(), interblocage si les deux tâches
                        # partagent un thread (constaté)
                        (spins += 1) % 1024 == 0 && yield()
                    end
                    @inbounds buf[(w&(CAP10-1))+1] = x
                    w += 1
                    @atomic :release ctl[17] = w
                end
            end
            cons = Threads.@spawn begin
                rd = 0; wc = 0; s = UInt64(0)
                for _ in 1:M10
                    spins = 0
                    while rd == wc
                        wc = @atomic :acquire ctl[17]
                        (spins += 1) % 1024 == 0 && yield()
                    end
                    @inbounds s += buf[(rd&(CAP10-1))+1]
                    rd += 1
                    @atomic :release ctl[49] = rd
                end
                s
            end
            wait(prod); s = fetch(cons)
        end
        dt = secs(t0)
        r >= 0 && result("k10", v, "2^22", r, dt, string(s))
    end
end

function main(args)
    k, v, reps = args[1], args[2], parse(Int, args[3])
    p = length(args) > 3 ? args[4] : ""
    k == "k1" ? run_k1(v, reps) : k == "k2" ? run_k2(v, reps, p) : k == "k3" ? run_k3(v, reps) :
    k == "k4" ? run_k4(v, reps) : k == "k5" ? run_k5(v, reps) : k == "k6" ? run_k6(v, reps, p) :
    k == "k7" ? run_k7(v, reps) : k == "k8" ? run_k8(v, reps) : k == "k9" ? run_k9(v, reps) :
    k == "k10" ? run_k10(v, reps) : nothing
end
end # module

MS.main(ARGS)
