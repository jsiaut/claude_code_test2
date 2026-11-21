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
# v4, point 3 (docs/V4_EQUAL.md, R3) : variante tuned, SIMD explicite (llvmcall, la seule voie de Base : VecElement et
# IR de LLVM ; SIMD.jl est un paquet tiers) : par bloc de 64 octets, comparaison non signée >= 128, octets hors masque
# à zéro, élargis en 64 voies de 16 bits et réduits (au plus 64 x 255 = 16 320).
const K4_IR = ("""
    declare i16 @llvm.vector.reduce.add.v64i16(<64 x i16>)
    define i16 @entry(ptr %0) #0 {
    top:
      %v = load <64 x i8>, ptr %0, align 1
      %m = icmp uge <64 x i8> %v, <$(join(fill("i8 -128", 64), ", "))>
      %z = select <64 x i1> %m, <64 x i8> %v, <64 x i8> zeroinitializer
      %w = zext <64 x i8> %z to <64 x i16>
      %s = call i16 @llvm.vector.reduce.add.v64i16(<64 x i16> %w)
      ret i16 %s
    }
    attributes #0 = { alwaysinline }
    """, "entry")
@inline k4_block(p::Ptr{UInt8}) = Base.llvmcall(K4_IR, UInt16, Tuple{Ptr{UInt8}}, p)
@noinline function k4_tuned(v::Vector{UInt8})
    n = length(v)
    s = UInt64(0)
    i = 1
    GC.@preserve v begin
        p = pointer(v)
        while i + 63 <= n
            s += k4_block(p + (i - 1))
            i += 64
        end
    end
    while i <= n
        @inbounds x = v[i]
        x >= 0x80 && (s += x)
        i += 1
    end
    s
end
# v4, point 4 (docs/V4_CONVERGE.md, 3.3, K4 swar) : octets traités par mots de 64 bits (unsafe_load sur le tampon du
# Vector, aligné). Le bit de poids fort de chaque octet, ramené au bit 0 de l'octet et multiplié par 0xFF, donne un
# masque d'octet qui garde les octets >= 128 ; les octets gardés sont sommés par paires dans quatre voies de 16 bits.
# Exactitude pour toute donnée : une voie reçoit au plus 2 × 255 = 510 par mot, donc au plus 128 × 510 = 65 280 < 2^16
# en 128 mots ; les voies sont vidées dans la somme toutes les 128 mots (et à la fin). Aucun branchement sur les données.
@noinline function k4_swar(v::Vector{UInt8})
    ones = 0x0101010101010101; lo = 0x00ff00ff00ff00ff
    n = length(v)
    s = UInt64(0)
    i = 0
    GC.@preserve v begin
        p = Ptr{UInt64}(pointer(v))
        while i + 8 <= n
            e = i + 128 * 8 <= n ? i + 128 * 8 : n - (n - i) % 8
            acc = UInt64(0)
            while i < e
                w = unsafe_load(p, (i >> 3) + 1)
                y = w & (((w >> 7) & ones) * 0xff)
                acc += (y & lo) + ((y >> 8) & lo)
                i += 8
            end
            acc = (acc & 0x0000ffff0000ffff) + ((acc >> 16) & 0x0000ffff0000ffff)  # deux voies de 32 bits
            s += (acc & 0xffffffff) + (acc >> 32)
        end
    end
    @inbounds while i < n
        x = v[i+1]
        s += UInt64(x) * UInt64(x >> 7)
        i += 1
    end
    s
end
function run_k4(v, reps)
    d = load(UInt8, "k4_bytes.u8")
    v == "natural_sorted" && sort!(d)
    f = v == "tuned" ? k4_tuned : v == "swar" ? k4_swar : v == "branchless_unsorted" ? k4_branchless : k4_natural
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
# v4, point 4 (docs/V4_CONVERGE.md, 3.3, K5 tuned_v ; forme de la frontière, C++ et C) : vecteurs explicites par
# llvmcall (la seule voie de Base, comme K4 tuned) : 16 f32, quatre accumulateurs indépendants, 64 éléments par tour,
# llvm.fmuladd (contraction permise), réduction horizontale une fois par appel. La longueur est un multiple de 64.
const K5_IR = ("""
    declare <16 x float> @llvm.fmuladd.v16f32(<16 x float>, <16 x float>, <16 x float>)
    declare float @llvm.vector.reduce.fadd.v16f32(float, <16 x float>)
    define float @entry(ptr %a, ptr %b, i64 %n) #0 {
    top:
      br label %loop
    loop:
      %i = phi i64 [ 0, %top ], [ %in, %loop ]
      %s0 = phi <16 x float> [ zeroinitializer, %top ], [ %t0, %loop ]
      %s1 = phi <16 x float> [ zeroinitializer, %top ], [ %t1, %loop ]
      %s2 = phi <16 x float> [ zeroinitializer, %top ], [ %t2, %loop ]
      %s3 = phi <16 x float> [ zeroinitializer, %top ], [ %t3, %loop ]
      %o0 = add i64 %i, 0
      %pa0 = getelementptr inbounds float, ptr %a, i64 %o0
      %pb0 = getelementptr inbounds float, ptr %b, i64 %o0
      %va0 = load <16 x float>, ptr %pa0, align 4
      %vb0 = load <16 x float>, ptr %pb0, align 4
      %t0 = call <16 x float> @llvm.fmuladd.v16f32(<16 x float> %va0, <16 x float> %vb0, <16 x float> %s0)
      %o1 = add i64 %i, 16
      %pa1 = getelementptr inbounds float, ptr %a, i64 %o1
      %pb1 = getelementptr inbounds float, ptr %b, i64 %o1
      %va1 = load <16 x float>, ptr %pa1, align 4
      %vb1 = load <16 x float>, ptr %pb1, align 4
      %t1 = call <16 x float> @llvm.fmuladd.v16f32(<16 x float> %va1, <16 x float> %vb1, <16 x float> %s1)
      %o2 = add i64 %i, 32
      %pa2 = getelementptr inbounds float, ptr %a, i64 %o2
      %pb2 = getelementptr inbounds float, ptr %b, i64 %o2
      %va2 = load <16 x float>, ptr %pa2, align 4
      %vb2 = load <16 x float>, ptr %pb2, align 4
      %t2 = call <16 x float> @llvm.fmuladd.v16f32(<16 x float> %va2, <16 x float> %vb2, <16 x float> %s2)
      %o3 = add i64 %i, 48
      %pa3 = getelementptr inbounds float, ptr %a, i64 %o3
      %pb3 = getelementptr inbounds float, ptr %b, i64 %o3
      %va3 = load <16 x float>, ptr %pa3, align 4
      %vb3 = load <16 x float>, ptr %pb3, align 4
      %t3 = call <16 x float> @llvm.fmuladd.v16f32(<16 x float> %va3, <16 x float> %vb3, <16 x float> %s3)
      %in = add i64 %i, 64
      %c = icmp slt i64 %in, %n
      br i1 %c, label %loop, label %done
    done:
      %u01 = fadd <16 x float> %t0, %t1
      %u23 = fadd <16 x float> %t2, %t3
      %u = fadd <16 x float> %u01, %u23
      %r = call reassoc float @llvm.vector.reduce.fadd.v16f32(float -0.0, <16 x float> %u)
      ret float %r
    }
    attributes #0 = { alwaysinline }
    """, "entry")
@noinline function k5_tuned_v(a::Vector{Float32}, b::Vector{Float32})
    GC.@preserve a b Base.llvmcall(K5_IR, Float32, Tuple{Ptr{Float32}, Ptr{Float32}, Int64}, pointer(a), pointer(b), length(a))
end
const SINK = Ref{Vector{Float32}}()
function run_k5(v, reps)
    a = load(Float32, "k5_a.f32"); b = load(Float32, "k5_b.f32")
    f = v == "tuned" ? k5_tuned : v == "tuned_v" ? k5_tuned_v : k5_natural
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
# v4, point 4 (docs/V4_CONVERGE.md, 3.3, K6 Q1 tuned_s ; forme de bench/julia_exp, remarque sur Julia, × 0,53),
# recopiée pour le calcul 4 bien que tuned_v soit écrite : une seule passe par bloc, accumulateurs des six groupes
# déroulés par Base.Cartesian.@nexprs, sélection par masques.
using Base.Cartesian: @nexprs
@noinline function q1_tuned_s(c::Cols, lo, hi, acc::Matrix{Int64})
    sd, pr, q, d, t, rf, ls = c.sd, c.pr, c.q, c.d, c.t, c.rf, c.ls
    B = 4096
    @inbounds for b0 in lo:B:hi
        b1 = min(b0 + B - 1, hi)
        @nexprs 6 g -> (cnt_g = Int32(0); sq_g = Int32(0); sp_g = Int32(0); sdp_g = Int32(0); sch_g = Int64(0))
        @simd for i in b0:b1
            pass = sd[i] <= Int32(10471)
            grp = Int32(rf[i]) * Int32(2) + Int32(ls[i])
            qi = Int32(q[i]); pi_ = pr[i]
            dp = pi_ * (Int32(100) - Int32(d[i]))
            ch = Int64(dp) * (100 + Int64(t[i]))
            @nexprs 6 g -> begin
                m_g = pass & (grp == Int32(g - 1))
                cnt_g += m_g
                sq_g += ifelse(m_g, qi, Int32(0))
                sp_g += ifelse(m_g, pi_, Int32(0))
                sdp_g += ifelse(m_g, dp, Int32(0))
                sch_g += ifelse(m_g, ch, Int64(0))
            end
        end
        @nexprs 6 g -> (acc[1, g] += cnt_g; acc[2, g] += sq_g; acc[3, g] += sp_g; acc[4, g] += sdp_g; acc[5, g] += sch_g)
    end
end
# v4, point 4 (docs/V4_CONVERGE.md, 3.3, K6 Q6 tuned_v ; forme de la frontière, Zig) : par llvmcall, blocs de 16
# lignes : colonnes élargies en i32, prédicat par comparaisons, produit prix × remise en i32, sélection, accumulation
# en <16 x i64>. Exactitude pour toute donnée (docs/SPEC.md, K6) : produit <= 50 000 × 10 = 500 000 < 2^31 ; une voie
# de 64 bits reçoit au plus N6 / 16 produits. La variante tuned publiée est scalaire (@simd, vectorisée par LLVM).
const Q6_IR = ("""
    declare i64 @llvm.vector.reduce.add.v16i64(<16 x i64>)
    define i64 @entry(ptr %sd, ptr %pr, ptr %d, ptr %q, i64 %nb) #0 {
    top:
      %z = icmp eq i64 %nb, 0
      br i1 %z, label %none, label %loop
    loop:
      %k = phi i64 [ 0, %top ], [ %kn, %loop ]
      %acc = phi <16 x i64> [ zeroinitializer, %top ], [ %accn, %loop ]
      %off = shl i64 %k, 4
      %psd = getelementptr inbounds i32, ptr %sd, i64 %off
      %ppr = getelementptr inbounds i32, ptr %pr, i64 %off
      %pd = getelementptr inbounds i8, ptr %d, i64 %off
      %pq = getelementptr inbounds i8, ptr %q, i64 %off
      %vsd = load <16 x i32>, ptr %psd, align 4
      %vpr = load <16 x i32>, ptr %ppr, align 4
      %vd8 = load <16 x i8>, ptr %pd, align 1
      %vq8 = load <16 x i8>, ptr %pq, align 1
      %vd = zext <16 x i8> %vd8 to <16 x i32>
      %vq = zext <16 x i8> %vq8 to <16 x i32>
      %m1 = icmp sge <16 x i32> %vsd, <i32 8766, i32 8766, i32 8766, i32 8766, i32 8766, i32 8766, i32 8766, i32 8766, i32 8766, i32 8766, i32 8766, i32 8766, i32 8766, i32 8766, i32 8766, i32 8766>
      %m2 = icmp slt <16 x i32> %vsd, <i32 9131, i32 9131, i32 9131, i32 9131, i32 9131, i32 9131, i32 9131, i32 9131, i32 9131, i32 9131, i32 9131, i32 9131, i32 9131, i32 9131, i32 9131, i32 9131>
      %m3 = icmp sge <16 x i32> %vd, <i32 5, i32 5, i32 5, i32 5, i32 5, i32 5, i32 5, i32 5, i32 5, i32 5, i32 5, i32 5, i32 5, i32 5, i32 5, i32 5>
      %m4 = icmp sle <16 x i32> %vd, <i32 7, i32 7, i32 7, i32 7, i32 7, i32 7, i32 7, i32 7, i32 7, i32 7, i32 7, i32 7, i32 7, i32 7, i32 7, i32 7>
      %m5 = icmp slt <16 x i32> %vq, <i32 24, i32 24, i32 24, i32 24, i32 24, i32 24, i32 24, i32 24, i32 24, i32 24, i32 24, i32 24, i32 24, i32 24, i32 24, i32 24>
      %ma = and <16 x i1> %m1, %m2
      %mb = and <16 x i1> %ma, %m3
      %mc = and <16 x i1> %mb, %m4
      %m = and <16 x i1> %mc, %m5
      %p = mul <16 x i32> %vpr, %vd
      %ps = select <16 x i1> %m, <16 x i32> %p, <16 x i32> zeroinitializer
      %p64 = sext <16 x i32> %ps to <16 x i64>
      %accn = add <16 x i64> %acc, %p64
      %kn = add i64 %k, 1
      %c = icmp ult i64 %kn, %nb
      br i1 %c, label %loop, label %done
    done:
      %r = call i64 @llvm.vector.reduce.add.v16i64(<16 x i64> %accn)
      ret i64 %r
    none:
      ret i64 0
    }
    attributes #0 = { alwaysinline }
    """, "entry")
@noinline function q6_tuned_v(c::Cols, lo, hi)
    sd, pr, q, d = c.sd, c.pr, c.q, c.d
    nb = (hi - lo + 1) ÷ 16
    s = GC.@preserve sd pr q d Base.llvmcall(Q6_IR, Int64, Tuple{Ptr{Int32}, Ptr{Int32}, Ptr{UInt8}, Ptr{UInt8}, Int64},
                                             pointer(sd, lo), pointer(pr, lo), pointer(d, lo), pointer(q, lo), nb)
    i = lo + 16 * nb
    i <= hi && (s += q6_natural(c, i, hi))  # reste (< 16 lignes)
    s
end
# v4, point 4 (docs/V4_CONVERGE.md, 3.3, K6 Q1 tuned_v) : l'algorithme de la référence C par llvmcall (IR écrit par
# tools/converge/gen_julia_ir.py) : 16 lignes par tour, masque de passage, groupe 2 × rf + ls, par groupe un masque,
# compte par population du masque (llvm.ctpop), additions masquées en voies de 32 bits vidées toutes les 4 096 lignes
# (au plus 256 lignes par voie : 256 × 5 000 000 < 2^31 ; sommes des voies faites en 64 bits), charge en 64 bits.
const Q1_IR = ("""
    declare i16 @llvm.ctpop.i16(i16)
    declare i64 @llvm.vector.reduce.add.v16i64(<16 x i64>)
    define void @entry(ptr %sd, ptr %pr, ptr %q, ptr %d, ptr %t, ptr %rf, ptr %ls, ptr %out, i64 %nb) #0 {
    top:
      br label %loop
    loop:
      %k = phi i64 [ 0, %top ], [ %kn, %loop ]
      %cnt0 = phi i64 [ 0, %top ], [ %cntn0, %loop ]
      %aq0 = phi <16 x i32> [ zeroinitializer, %top ], [ %aqn0, %loop ]
      %ap0 = phi <16 x i32> [ zeroinitializer, %top ], [ %apn0, %loop ]
      %adp0 = phi <16 x i32> [ zeroinitializer, %top ], [ %adpn0, %loop ]
      %ach0 = phi <16 x i64> [ zeroinitializer, %top ], [ %achn0, %loop ]
      %cnt1 = phi i64 [ 0, %top ], [ %cntn1, %loop ]
      %aq1 = phi <16 x i32> [ zeroinitializer, %top ], [ %aqn1, %loop ]
      %ap1 = phi <16 x i32> [ zeroinitializer, %top ], [ %apn1, %loop ]
      %adp1 = phi <16 x i32> [ zeroinitializer, %top ], [ %adpn1, %loop ]
      %ach1 = phi <16 x i64> [ zeroinitializer, %top ], [ %achn1, %loop ]
      %cnt2 = phi i64 [ 0, %top ], [ %cntn2, %loop ]
      %aq2 = phi <16 x i32> [ zeroinitializer, %top ], [ %aqn2, %loop ]
      %ap2 = phi <16 x i32> [ zeroinitializer, %top ], [ %apn2, %loop ]
      %adp2 = phi <16 x i32> [ zeroinitializer, %top ], [ %adpn2, %loop ]
      %ach2 = phi <16 x i64> [ zeroinitializer, %top ], [ %achn2, %loop ]
      %cnt3 = phi i64 [ 0, %top ], [ %cntn3, %loop ]
      %aq3 = phi <16 x i32> [ zeroinitializer, %top ], [ %aqn3, %loop ]
      %ap3 = phi <16 x i32> [ zeroinitializer, %top ], [ %apn3, %loop ]
      %adp3 = phi <16 x i32> [ zeroinitializer, %top ], [ %adpn3, %loop ]
      %ach3 = phi <16 x i64> [ zeroinitializer, %top ], [ %achn3, %loop ]
      %cnt4 = phi i64 [ 0, %top ], [ %cntn4, %loop ]
      %aq4 = phi <16 x i32> [ zeroinitializer, %top ], [ %aqn4, %loop ]
      %ap4 = phi <16 x i32> [ zeroinitializer, %top ], [ %apn4, %loop ]
      %adp4 = phi <16 x i32> [ zeroinitializer, %top ], [ %adpn4, %loop ]
      %ach4 = phi <16 x i64> [ zeroinitializer, %top ], [ %achn4, %loop ]
      %cnt5 = phi i64 [ 0, %top ], [ %cntn5, %loop ]
      %aq5 = phi <16 x i32> [ zeroinitializer, %top ], [ %aqn5, %loop ]
      %ap5 = phi <16 x i32> [ zeroinitializer, %top ], [ %apn5, %loop ]
      %adp5 = phi <16 x i32> [ zeroinitializer, %top ], [ %adpn5, %loop ]
      %ach5 = phi <16 x i64> [ zeroinitializer, %top ], [ %achn5, %loop ]
      %off = shl i64 %k, 4
      %psd = getelementptr inbounds i32, ptr %sd, i64 %off
      %vsd = load <16 x i32>, ptr %psd, align 4
      %ppr = getelementptr inbounds i32, ptr %pr, i64 %off
      %vpr = load <16 x i32>, ptr %ppr, align 4
      %pq = getelementptr inbounds i8, ptr %q, i64 %off
      %bq = load <16 x i8>, ptr %pq, align 1
      %vq = zext <16 x i8> %bq to <16 x i32>
      %pd = getelementptr inbounds i8, ptr %d, i64 %off
      %bd = load <16 x i8>, ptr %pd, align 1
      %vd = zext <16 x i8> %bd to <16 x i32>
      %pt = getelementptr inbounds i8, ptr %t, i64 %off
      %bt = load <16 x i8>, ptr %pt, align 1
      %vt = zext <16 x i8> %bt to <16 x i32>
      %prf = getelementptr inbounds i8, ptr %rf, i64 %off
      %brf = load <16 x i8>, ptr %prf, align 1
      %vrf = zext <16 x i8> %brf to <16 x i32>
      %pls = getelementptr inbounds i8, ptr %ls, i64 %off
      %bls = load <16 x i8>, ptr %pls, align 1
      %vls = zext <16 x i8> %bls to <16 x i32>
      %pass = icmp sle <16 x i32> %vsd, <i32 10471, i32 10471, i32 10471, i32 10471, i32 10471, i32 10471, i32 10471, i32 10471, i32 10471, i32 10471, i32 10471, i32 10471, i32 10471, i32 10471, i32 10471, i32 10471>
      %rf2 = shl <16 x i32> %vrf, <i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1>
      %vg = add <16 x i32> %rf2, %vls
      %c100d = sub <16 x i32> <i32 100, i32 100, i32 100, i32 100, i32 100, i32 100, i32 100, i32 100, i32 100, i32 100, i32 100, i32 100, i32 100, i32 100, i32 100, i32 100>, %vd
      %vdp = mul <16 x i32> %vpr, %c100d
      %vt100 = add <16 x i32> %vt, <i32 100, i32 100, i32 100, i32 100, i32 100, i32 100, i32 100, i32 100, i32 100, i32 100, i32 100, i32 100, i32 100, i32 100, i32 100, i32 100>
      %dp64 = sext <16 x i32> %vdp to <16 x i64>
      %t64 = zext <16 x i32> %vt100 to <16 x i64>
      %ch = mul <16 x i64> %dp64, %t64
      %eq0 = icmp eq <16 x i32> %vg, <i32 0, i32 0, i32 0, i32 0, i32 0, i32 0, i32 0, i32 0, i32 0, i32 0, i32 0, i32 0, i32 0, i32 0, i32 0, i32 0>
      %m0 = and <16 x i1> %pass, %eq0
      %bits0 = bitcast <16 x i1> %m0 to i16
      %pc0 = call i16 @llvm.ctpop.i16(i16 %bits0)
      %pc640 = zext i16 %pc0 to i64
      %cntn0 = add i64 %cnt0, %pc640
      %sq0 = select <16 x i1> %m0, <16 x i32> %vq, <16 x i32> zeroinitializer
      %aqn0 = add <16 x i32> %aq0, %sq0
      %sp0 = select <16 x i1> %m0, <16 x i32> %vpr, <16 x i32> zeroinitializer
      %apn0 = add <16 x i32> %ap0, %sp0
      %sdp0 = select <16 x i1> %m0, <16 x i32> %vdp, <16 x i32> zeroinitializer
      %adpn0 = add <16 x i32> %adp0, %sdp0
      %sch0 = select <16 x i1> %m0, <16 x i64> %ch, <16 x i64> zeroinitializer
      %achn0 = add <16 x i64> %ach0, %sch0
      %eq1 = icmp eq <16 x i32> %vg, <i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1, i32 1>
      %m1 = and <16 x i1> %pass, %eq1
      %bits1 = bitcast <16 x i1> %m1 to i16
      %pc1 = call i16 @llvm.ctpop.i16(i16 %bits1)
      %pc641 = zext i16 %pc1 to i64
      %cntn1 = add i64 %cnt1, %pc641
      %sq1 = select <16 x i1> %m1, <16 x i32> %vq, <16 x i32> zeroinitializer
      %aqn1 = add <16 x i32> %aq1, %sq1
      %sp1 = select <16 x i1> %m1, <16 x i32> %vpr, <16 x i32> zeroinitializer
      %apn1 = add <16 x i32> %ap1, %sp1
      %sdp1 = select <16 x i1> %m1, <16 x i32> %vdp, <16 x i32> zeroinitializer
      %adpn1 = add <16 x i32> %adp1, %sdp1
      %sch1 = select <16 x i1> %m1, <16 x i64> %ch, <16 x i64> zeroinitializer
      %achn1 = add <16 x i64> %ach1, %sch1
      %eq2 = icmp eq <16 x i32> %vg, <i32 2, i32 2, i32 2, i32 2, i32 2, i32 2, i32 2, i32 2, i32 2, i32 2, i32 2, i32 2, i32 2, i32 2, i32 2, i32 2>
      %m2 = and <16 x i1> %pass, %eq2
      %bits2 = bitcast <16 x i1> %m2 to i16
      %pc2 = call i16 @llvm.ctpop.i16(i16 %bits2)
      %pc642 = zext i16 %pc2 to i64
      %cntn2 = add i64 %cnt2, %pc642
      %sq2 = select <16 x i1> %m2, <16 x i32> %vq, <16 x i32> zeroinitializer
      %aqn2 = add <16 x i32> %aq2, %sq2
      %sp2 = select <16 x i1> %m2, <16 x i32> %vpr, <16 x i32> zeroinitializer
      %apn2 = add <16 x i32> %ap2, %sp2
      %sdp2 = select <16 x i1> %m2, <16 x i32> %vdp, <16 x i32> zeroinitializer
      %adpn2 = add <16 x i32> %adp2, %sdp2
      %sch2 = select <16 x i1> %m2, <16 x i64> %ch, <16 x i64> zeroinitializer
      %achn2 = add <16 x i64> %ach2, %sch2
      %eq3 = icmp eq <16 x i32> %vg, <i32 3, i32 3, i32 3, i32 3, i32 3, i32 3, i32 3, i32 3, i32 3, i32 3, i32 3, i32 3, i32 3, i32 3, i32 3, i32 3>
      %m3 = and <16 x i1> %pass, %eq3
      %bits3 = bitcast <16 x i1> %m3 to i16
      %pc3 = call i16 @llvm.ctpop.i16(i16 %bits3)
      %pc643 = zext i16 %pc3 to i64
      %cntn3 = add i64 %cnt3, %pc643
      %sq3 = select <16 x i1> %m3, <16 x i32> %vq, <16 x i32> zeroinitializer
      %aqn3 = add <16 x i32> %aq3, %sq3
      %sp3 = select <16 x i1> %m3, <16 x i32> %vpr, <16 x i32> zeroinitializer
      %apn3 = add <16 x i32> %ap3, %sp3
      %sdp3 = select <16 x i1> %m3, <16 x i32> %vdp, <16 x i32> zeroinitializer
      %adpn3 = add <16 x i32> %adp3, %sdp3
      %sch3 = select <16 x i1> %m3, <16 x i64> %ch, <16 x i64> zeroinitializer
      %achn3 = add <16 x i64> %ach3, %sch3
      %eq4 = icmp eq <16 x i32> %vg, <i32 4, i32 4, i32 4, i32 4, i32 4, i32 4, i32 4, i32 4, i32 4, i32 4, i32 4, i32 4, i32 4, i32 4, i32 4, i32 4>
      %m4 = and <16 x i1> %pass, %eq4
      %bits4 = bitcast <16 x i1> %m4 to i16
      %pc4 = call i16 @llvm.ctpop.i16(i16 %bits4)
      %pc644 = zext i16 %pc4 to i64
      %cntn4 = add i64 %cnt4, %pc644
      %sq4 = select <16 x i1> %m4, <16 x i32> %vq, <16 x i32> zeroinitializer
      %aqn4 = add <16 x i32> %aq4, %sq4
      %sp4 = select <16 x i1> %m4, <16 x i32> %vpr, <16 x i32> zeroinitializer
      %apn4 = add <16 x i32> %ap4, %sp4
      %sdp4 = select <16 x i1> %m4, <16 x i32> %vdp, <16 x i32> zeroinitializer
      %adpn4 = add <16 x i32> %adp4, %sdp4
      %sch4 = select <16 x i1> %m4, <16 x i64> %ch, <16 x i64> zeroinitializer
      %achn4 = add <16 x i64> %ach4, %sch4
      %eq5 = icmp eq <16 x i32> %vg, <i32 5, i32 5, i32 5, i32 5, i32 5, i32 5, i32 5, i32 5, i32 5, i32 5, i32 5, i32 5, i32 5, i32 5, i32 5, i32 5>
      %m5 = and <16 x i1> %pass, %eq5
      %bits5 = bitcast <16 x i1> %m5 to i16
      %pc5 = call i16 @llvm.ctpop.i16(i16 %bits5)
      %pc645 = zext i16 %pc5 to i64
      %cntn5 = add i64 %cnt5, %pc645
      %sq5 = select <16 x i1> %m5, <16 x i32> %vq, <16 x i32> zeroinitializer
      %aqn5 = add <16 x i32> %aq5, %sq5
      %sp5 = select <16 x i1> %m5, <16 x i32> %vpr, <16 x i32> zeroinitializer
      %apn5 = add <16 x i32> %ap5, %sp5
      %sdp5 = select <16 x i1> %m5, <16 x i32> %vdp, <16 x i32> zeroinitializer
      %adpn5 = add <16 x i32> %adp5, %sdp5
      %sch5 = select <16 x i1> %m5, <16 x i64> %ch, <16 x i64> zeroinitializer
      %achn5 = add <16 x i64> %ach5, %sch5
      %kn = add i64 %k, 1
      %c = icmp ult i64 %kn, %nb
      br i1 %c, label %loop, label %done
    done:
      %waqn0 = sext <16 x i32> %aqn0 to <16 x i64>
      %raqn0 = call i64 @llvm.vector.reduce.add.v16i64(<16 x i64> %waqn0)
      %wapn0 = sext <16 x i32> %apn0 to <16 x i64>
      %rapn0 = call i64 @llvm.vector.reduce.add.v16i64(<16 x i64> %wapn0)
      %wadpn0 = sext <16 x i32> %adpn0 to <16 x i64>
      %radpn0 = call i64 @llvm.vector.reduce.add.v16i64(<16 x i64> %wadpn0)
      %rach0 = call i64 @llvm.vector.reduce.add.v16i64(<16 x i64> %achn0)
      %po0_0 = getelementptr inbounds i64, ptr %out, i64 0
      %o0_0 = load i64, ptr %po0_0, align 8
      %on0_0 = add i64 %o0_0, %cntn0
      store i64 %on0_0, ptr %po0_0, align 8
      %po0_1 = getelementptr inbounds i64, ptr %out, i64 1
      %o0_1 = load i64, ptr %po0_1, align 8
      %on0_1 = add i64 %o0_1, %raqn0
      store i64 %on0_1, ptr %po0_1, align 8
      %po0_2 = getelementptr inbounds i64, ptr %out, i64 2
      %o0_2 = load i64, ptr %po0_2, align 8
      %on0_2 = add i64 %o0_2, %rapn0
      store i64 %on0_2, ptr %po0_2, align 8
      %po0_3 = getelementptr inbounds i64, ptr %out, i64 3
      %o0_3 = load i64, ptr %po0_3, align 8
      %on0_3 = add i64 %o0_3, %radpn0
      store i64 %on0_3, ptr %po0_3, align 8
      %po0_4 = getelementptr inbounds i64, ptr %out, i64 4
      %o0_4 = load i64, ptr %po0_4, align 8
      %on0_4 = add i64 %o0_4, %rach0
      store i64 %on0_4, ptr %po0_4, align 8
      %waqn1 = sext <16 x i32> %aqn1 to <16 x i64>
      %raqn1 = call i64 @llvm.vector.reduce.add.v16i64(<16 x i64> %waqn1)
      %wapn1 = sext <16 x i32> %apn1 to <16 x i64>
      %rapn1 = call i64 @llvm.vector.reduce.add.v16i64(<16 x i64> %wapn1)
      %wadpn1 = sext <16 x i32> %adpn1 to <16 x i64>
      %radpn1 = call i64 @llvm.vector.reduce.add.v16i64(<16 x i64> %wadpn1)
      %rach1 = call i64 @llvm.vector.reduce.add.v16i64(<16 x i64> %achn1)
      %po1_0 = getelementptr inbounds i64, ptr %out, i64 5
      %o1_0 = load i64, ptr %po1_0, align 8
      %on1_0 = add i64 %o1_0, %cntn1
      store i64 %on1_0, ptr %po1_0, align 8
      %po1_1 = getelementptr inbounds i64, ptr %out, i64 6
      %o1_1 = load i64, ptr %po1_1, align 8
      %on1_1 = add i64 %o1_1, %raqn1
      store i64 %on1_1, ptr %po1_1, align 8
      %po1_2 = getelementptr inbounds i64, ptr %out, i64 7
      %o1_2 = load i64, ptr %po1_2, align 8
      %on1_2 = add i64 %o1_2, %rapn1
      store i64 %on1_2, ptr %po1_2, align 8
      %po1_3 = getelementptr inbounds i64, ptr %out, i64 8
      %o1_3 = load i64, ptr %po1_3, align 8
      %on1_3 = add i64 %o1_3, %radpn1
      store i64 %on1_3, ptr %po1_3, align 8
      %po1_4 = getelementptr inbounds i64, ptr %out, i64 9
      %o1_4 = load i64, ptr %po1_4, align 8
      %on1_4 = add i64 %o1_4, %rach1
      store i64 %on1_4, ptr %po1_4, align 8
      %waqn2 = sext <16 x i32> %aqn2 to <16 x i64>
      %raqn2 = call i64 @llvm.vector.reduce.add.v16i64(<16 x i64> %waqn2)
      %wapn2 = sext <16 x i32> %apn2 to <16 x i64>
      %rapn2 = call i64 @llvm.vector.reduce.add.v16i64(<16 x i64> %wapn2)
      %wadpn2 = sext <16 x i32> %adpn2 to <16 x i64>
      %radpn2 = call i64 @llvm.vector.reduce.add.v16i64(<16 x i64> %wadpn2)
      %rach2 = call i64 @llvm.vector.reduce.add.v16i64(<16 x i64> %achn2)
      %po2_0 = getelementptr inbounds i64, ptr %out, i64 10
      %o2_0 = load i64, ptr %po2_0, align 8
      %on2_0 = add i64 %o2_0, %cntn2
      store i64 %on2_0, ptr %po2_0, align 8
      %po2_1 = getelementptr inbounds i64, ptr %out, i64 11
      %o2_1 = load i64, ptr %po2_1, align 8
      %on2_1 = add i64 %o2_1, %raqn2
      store i64 %on2_1, ptr %po2_1, align 8
      %po2_2 = getelementptr inbounds i64, ptr %out, i64 12
      %o2_2 = load i64, ptr %po2_2, align 8
      %on2_2 = add i64 %o2_2, %rapn2
      store i64 %on2_2, ptr %po2_2, align 8
      %po2_3 = getelementptr inbounds i64, ptr %out, i64 13
      %o2_3 = load i64, ptr %po2_3, align 8
      %on2_3 = add i64 %o2_3, %radpn2
      store i64 %on2_3, ptr %po2_3, align 8
      %po2_4 = getelementptr inbounds i64, ptr %out, i64 14
      %o2_4 = load i64, ptr %po2_4, align 8
      %on2_4 = add i64 %o2_4, %rach2
      store i64 %on2_4, ptr %po2_4, align 8
      %waqn3 = sext <16 x i32> %aqn3 to <16 x i64>
      %raqn3 = call i64 @llvm.vector.reduce.add.v16i64(<16 x i64> %waqn3)
      %wapn3 = sext <16 x i32> %apn3 to <16 x i64>
      %rapn3 = call i64 @llvm.vector.reduce.add.v16i64(<16 x i64> %wapn3)
      %wadpn3 = sext <16 x i32> %adpn3 to <16 x i64>
      %radpn3 = call i64 @llvm.vector.reduce.add.v16i64(<16 x i64> %wadpn3)
      %rach3 = call i64 @llvm.vector.reduce.add.v16i64(<16 x i64> %achn3)
      %po3_0 = getelementptr inbounds i64, ptr %out, i64 15
      %o3_0 = load i64, ptr %po3_0, align 8
      %on3_0 = add i64 %o3_0, %cntn3
      store i64 %on3_0, ptr %po3_0, align 8
      %po3_1 = getelementptr inbounds i64, ptr %out, i64 16
      %o3_1 = load i64, ptr %po3_1, align 8
      %on3_1 = add i64 %o3_1, %raqn3
      store i64 %on3_1, ptr %po3_1, align 8
      %po3_2 = getelementptr inbounds i64, ptr %out, i64 17
      %o3_2 = load i64, ptr %po3_2, align 8
      %on3_2 = add i64 %o3_2, %rapn3
      store i64 %on3_2, ptr %po3_2, align 8
      %po3_3 = getelementptr inbounds i64, ptr %out, i64 18
      %o3_3 = load i64, ptr %po3_3, align 8
      %on3_3 = add i64 %o3_3, %radpn3
      store i64 %on3_3, ptr %po3_3, align 8
      %po3_4 = getelementptr inbounds i64, ptr %out, i64 19
      %o3_4 = load i64, ptr %po3_4, align 8
      %on3_4 = add i64 %o3_4, %rach3
      store i64 %on3_4, ptr %po3_4, align 8
      %waqn4 = sext <16 x i32> %aqn4 to <16 x i64>
      %raqn4 = call i64 @llvm.vector.reduce.add.v16i64(<16 x i64> %waqn4)
      %wapn4 = sext <16 x i32> %apn4 to <16 x i64>
      %rapn4 = call i64 @llvm.vector.reduce.add.v16i64(<16 x i64> %wapn4)
      %wadpn4 = sext <16 x i32> %adpn4 to <16 x i64>
      %radpn4 = call i64 @llvm.vector.reduce.add.v16i64(<16 x i64> %wadpn4)
      %rach4 = call i64 @llvm.vector.reduce.add.v16i64(<16 x i64> %achn4)
      %po4_0 = getelementptr inbounds i64, ptr %out, i64 20
      %o4_0 = load i64, ptr %po4_0, align 8
      %on4_0 = add i64 %o4_0, %cntn4
      store i64 %on4_0, ptr %po4_0, align 8
      %po4_1 = getelementptr inbounds i64, ptr %out, i64 21
      %o4_1 = load i64, ptr %po4_1, align 8
      %on4_1 = add i64 %o4_1, %raqn4
      store i64 %on4_1, ptr %po4_1, align 8
      %po4_2 = getelementptr inbounds i64, ptr %out, i64 22
      %o4_2 = load i64, ptr %po4_2, align 8
      %on4_2 = add i64 %o4_2, %rapn4
      store i64 %on4_2, ptr %po4_2, align 8
      %po4_3 = getelementptr inbounds i64, ptr %out, i64 23
      %o4_3 = load i64, ptr %po4_3, align 8
      %on4_3 = add i64 %o4_3, %radpn4
      store i64 %on4_3, ptr %po4_3, align 8
      %po4_4 = getelementptr inbounds i64, ptr %out, i64 24
      %o4_4 = load i64, ptr %po4_4, align 8
      %on4_4 = add i64 %o4_4, %rach4
      store i64 %on4_4, ptr %po4_4, align 8
      %waqn5 = sext <16 x i32> %aqn5 to <16 x i64>
      %raqn5 = call i64 @llvm.vector.reduce.add.v16i64(<16 x i64> %waqn5)
      %wapn5 = sext <16 x i32> %apn5 to <16 x i64>
      %rapn5 = call i64 @llvm.vector.reduce.add.v16i64(<16 x i64> %wapn5)
      %wadpn5 = sext <16 x i32> %adpn5 to <16 x i64>
      %radpn5 = call i64 @llvm.vector.reduce.add.v16i64(<16 x i64> %wadpn5)
      %rach5 = call i64 @llvm.vector.reduce.add.v16i64(<16 x i64> %achn5)
      %po5_0 = getelementptr inbounds i64, ptr %out, i64 25
      %o5_0 = load i64, ptr %po5_0, align 8
      %on5_0 = add i64 %o5_0, %cntn5
      store i64 %on5_0, ptr %po5_0, align 8
      %po5_1 = getelementptr inbounds i64, ptr %out, i64 26
      %o5_1 = load i64, ptr %po5_1, align 8
      %on5_1 = add i64 %o5_1, %raqn5
      store i64 %on5_1, ptr %po5_1, align 8
      %po5_2 = getelementptr inbounds i64, ptr %out, i64 27
      %o5_2 = load i64, ptr %po5_2, align 8
      %on5_2 = add i64 %o5_2, %rapn5
      store i64 %on5_2, ptr %po5_2, align 8
      %po5_3 = getelementptr inbounds i64, ptr %out, i64 28
      %o5_3 = load i64, ptr %po5_3, align 8
      %on5_3 = add i64 %o5_3, %radpn5
      store i64 %on5_3, ptr %po5_3, align 8
      %po5_4 = getelementptr inbounds i64, ptr %out, i64 29
      %o5_4 = load i64, ptr %po5_4, align 8
      %on5_4 = add i64 %o5_4, %rach5
      store i64 %on5_4, ptr %po5_4, align 8
      ret void
    }
    attributes #0 = { alwaysinline }
    """, "entry")
@noinline function q1_tuned_v(c::Cols, lo, hi, acc::Matrix{Int64})
    sd, pr, q, d, t, rf, ls = c.sd, c.pr, c.q, c.d, c.t, c.rf, c.ls
    i = lo
    GC.@preserve sd pr q d t rf ls acc begin
        while i + 15 <= hi
            nb = min(256, (hi - i + 1) ÷ 16)
            Base.llvmcall(Q1_IR, Cvoid, Tuple{Ptr{Int32}, Ptr{Int32}, Ptr{UInt8}, Ptr{UInt8}, Ptr{UInt8}, Ptr{UInt8}, Ptr{UInt8}, Ptr{Int64}, Int64},
                          pointer(sd, i), pointer(pr, i), pointer(q, i), pointer(d, i), pointer(t, i), pointer(rf, i), pointer(ls, i),
                          pointer(acc), nb)
            i += 16 * nb
        end
    end
    i <= hi && q1_natural(c, i, hi, acc)  # reste (< 16 lignes)
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
        elseif v == "mt_pool_v"
            # v4, point 4 (mt_pool_v) : les tâches de mt (Threads.@spawn sur les fils gardés par le runtime : la réserve
            # de mt_pool, présente), chaque quart en tuned_v
            tasks = map(0:3) do t
                lo, hi = N6 ÷ 4 * t + 1, N6 ÷ 4 * (t + 1)
                Threads.@spawn q1 ? (local acc = zeros(Int64, 5, 6); q1_tuned_v(c, lo, hi, acc); sum(acc)) : q6_tuned_v(c, lo, hi)
            end
            s = sum(fetch.(tasks))
        elseif q1
            a = zeros(Int64, 5, 6)
            (v == "tuned" ? q1_tuned : v == "tuned_v" ? q1_tuned_v : v == "tuned_s" ? q1_tuned_s : q1_natural)(c, 1, N6, a)
            s = sum(a)
        else
            s = v == "tuned" ? q6_tuned(c, 1, N6) : v == "tuned_v" ? q6_tuned_v(c, 1, N6) : q6_natural(c, 1, N6)
        end
        dt = secs(t0)
        r >= 0 && result("k6", v, p, r, dt, string(s))
    end
end

# ------------------------------------------------------------------ K7
struct Slot
    key::UInt32; count::UInt32; sum::UInt64
end
# v4, point 4 (docs/V4_CONVERGE.md, 3.3, K7 tuned_pf ; forme de bench/julia_exp, remarque sur Julia, × 0,69) :
# préchargement en écriture, localité 0 (comme __builtin_prefetch(p, 1, 0) en C)
@inline prefetchw(p::Ptr) = ccall("llvm.prefetch.p0", llvmcall, Cvoid, (Ptr{Cvoid}, Int32, Int32, Int32), p, Int32(1), Int32(0), Int32(1))
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
        elseif v == "tuned_pf"
            # la table de tuned, clés par lots de 16 : hachages calculés et cases préchargées, puis les 16 insertions
            LOG = K7_LOG; CAP = 1 << LOG
            t0 = time_ns()
            tab = fill(Slot(0, 0, 0), CAP)
            ptab = pointer(tab)
            h = zeros(UInt32, 16)
            GC.@preserve tab @inbounds for i0 in 1:16:length(keys)
                for b in 1:16
                    hb = (keys[i0+b-1] * 0x9E3779B1) >> (32 - LOG)
                    h[b] = hb
                    prefetchw(ptab + hb * sizeof(Slot))
                end
                for b in 1:16
                    k = keys[i0+b-1]
                    s = h[b] + 1
                    while tab[s].count != 0 && tab[s].key != k
                        s = (s & (CAP - 1)) + 1
                    end
                    e = tab[s]
                    tab[s] = Slot(k, e.count + 1, e.sum + vals[i0+b-1])
                end
            end
            dt = secs(t0)
            for e in tab
                if e.count != 0
                    nk += 1; ws += e.sum * ((e.key & 1023) + 1)
                end
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
# v4, point 4 : constantes de taille des formes nouvelles (substituées comme les autres pour la campagne finale)
const K7_LOG = 21
const K8_REQ = 10
# v4, point 4 (docs/V4_CONVERGE.md, 3.5, rq_spec ; forme de bench/julia_exp, remarque sur Julia, × 0,83) : la variante
# tuned, profondeur en paramètre de compilation (Val) et incréments Int32 sans conversion vérifiée (forme propre à
# Julia, spécialisation : relevé, results/converge/inventory.md)
function a_build_spec(a::Vector{ANode}, top::Base.RefValue{Int32}, ::Val{d}, c::Base.RefValue{Int64}) where {d}
    i = top[]; top[] = i + Int32(1)
    @inbounds a[i] = ANode(c[], -1, -1); c[] += 1
    if d > 0
        l = a_build_spec(a, top, Val(d - 1), c); r = a_build_spec(a, top, Val(d - 1), c)
        @inbounds a[i] = ANode(a[i].v, l, r)
    end
    i
end
# v4, point 4 (docs/V4_CONVERGE.md, 3.3, K8 tuned_val ; forme de la frontière, Ada, et de bench/c_k8val) : l'état passe
# par valeur, l'indice du nœud en ordre préfixe (base 1 ; sa valeur : numéro de requête + indice de base 0) ; la fonction
# rend l'indice libre suivant. Même arène, mêmes liens et mêmes valeurs que a_build ; somme récursive (a_sum).
function a_build_val(a::Vector{ANode}, i::Int32, d, q::Int64)
    if d > 0
        l = i + Int32(1)
        r = a_build_val(a, l, d - 1, q)
        @inbounds a[i] = ANode(q + (i - 1), l, r)
        return a_build_val(a, r, d - 1, q)
    end
    @inbounds a[i] = ANode(q + (i - 1), Int32(-1), Int32(-1))
    i + Int32(1)
end
# v4, point 4 (docs/V4_CONVERGE.md, 3.3, K8 tuned_it ; forme de bench/c_k8it, remarque sur C) : construction et somme
# itératives, piles explicites (vecteurs de 64 entrées alloués une fois, hors chrono : au plus une entrée par niveau à
# la construction, au plus profondeur + 1 à la somme). La construction descend à gauche en empilant le sous-arbre droit
# de chaque nœud interne, puis le reprend à la feuille suivante : même ordre préfixe, mêmes liens et mêmes valeurs.
function a_build_it(a::Vector{ANode}, stp::Vector{Int32}, std::Vector{Int}, depth, q::Int64)
    sp = 0; top = Int32(1); parent = Int32(-1); right = false; d = depth
    @inbounds while true
        i = top; top += Int32(1)
        a[i] = ANode(q + (i - 1), Int32(-1), Int32(-1))
        if parent >= 0
            e = a[parent]
            a[parent] = right ? ANode(e.v, e.l, i) : ANode(e.v, i, e.r)
        end
        if d > 0
            sp += 1; stp[sp] = i; std[sp] = d - 1
            parent = i; right = false; d -= 1
        else
            sp == 0 && break
            parent = stp[sp]; d = std[sp]; right = true; sp -= 1
        end
    end
end
function a_sum_it(a::Vector{ANode}, st::Vector{Int32}, root::Int32)
    sp = 1; st[1] = root; s = Int64(0)
    @inbounds while sp > 0
        i = st[sp]; sp -= 1
        n = a[i]; s += n.v
        if n.l >= 0
            st[sp+1] = n.r; st[sp+2] = n.l; sp += 2
        end
    end
    s
end
const KEEP = Ref{Node}()
function run_k8(v, reps)
    Q = 16384
    tuned = v == "tuned"
    KEEP[] = t_build(20, Ref(0)); lsum = t_sum(KEEP[])
    lat = zeros(Int64, Q)
    arena = Vector{ANode}(undef, 2047)
    K8_REQ < 63 || error("piles de K8 tuned_it : 64 entrées")
    stp = Vector{Int32}(undef, 64); std = Vector{Int}(undef, 64); st = Vector{Int32}(undef, 64)
    for r in -WARMUP:reps-1
        total = 0
        t0 = time_ns()
        for q in 0:Q-1
            a = time_ns()
            c = Ref(Int64(q))
            if tuned
                top = Ref(Int32(1))
                s = a_sum(arena, a_build(arena, top, 10, c))
            elseif v == "tuned_val"
                a_build_val(arena, Int32(1), K8_REQ, c[])
                s = a_sum(arena, Int32(1))
            elseif v == "tuned_it"
                a_build_it(arena, stp, std, K8_REQ, c[])
                s = a_sum_it(arena, st, Int32(1))
            elseif v == "rq_spec"
                top = Ref(Int32(1))
                s = a_sum(arena, a_build_spec(arena, top, Val(K8_REQ), c))
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
# v4, point 4 (docs/V4_CONVERGE.md, 3.3, K9 tuned_v ; forme de la frontière, Swift) : vecteurs explicites de 8 f64 par
# llvmcall, le long de la dimension contiguë (colonnes de la Matrix) : voisins de même colonne chargés en vecteurs non
# alignés (i - 1 et i + 1), colonnes voisines en vecteurs, même ordre des additions que la spécification, résultat
# écrit en vecteur, reste scalaire ; l'indice contigu part de 1 comme chez Swift. Colonnes j0..j1 (base 0).
const K9_IR = ("""
    define void @entry(ptr %a, ptr %b, i64 %j0, i64 %j1) #0 {
    top:
      br label %col
    col:
      %j = phi i64 [ %j0, %top ], [ %jn, %rowend ]
      %base = mul i64 %j, $M9
      %pm = getelementptr inbounds double, ptr %a, i64 %base
      %pl = getelementptr inbounds double, ptr %pm, i64 -$M9
      %pr = getelementptr inbounds double, ptr %pm, i64 $M9
      %po = getelementptr inbounds double, ptr %b, i64 %base
      br label %row
    row:
      %i = phi i64 [ 1, %col ], [ %in, %row ]
      %im = add i64 %i, -1
      %ip = add i64 %i, 1
      %pu = getelementptr inbounds double, ptr %pm, i64 %im
      %pd = getelementptr inbounds double, ptr %pm, i64 %ip
      %pli = getelementptr inbounds double, ptr %pl, i64 %i
      %pri = getelementptr inbounds double, ptr %pr, i64 %i
      %poi = getelementptr inbounds double, ptr %po, i64 %i
      %vu = load <8 x double>, ptr %pu, align 8
      %vd = load <8 x double>, ptr %pd, align 8
      %vl = load <8 x double>, ptr %pli, align 8
      %vr = load <8 x double>, ptr %pri, align 8
      %s1 = fadd <8 x double> %vu, %vd
      %s2 = fadd <8 x double> %s1, %vl
      %s3 = fadd <8 x double> %s2, %vr
      %vo = fmul <8 x double> <double 0.25, double 0.25, double 0.25, double 0.25, double 0.25, double 0.25, double 0.25, double 0.25>, %s3
      store <8 x double> %vo, ptr %poi, align 8
      %in = add i64 %i, 8
      %in8 = add i64 %in, 8
      %cr = icmp sle i64 %in8, $(M9 - 1)
      br i1 %cr, label %row, label %tail
    tail:
      %ti = phi i64 [ %in, %row ], [ %tin, %tail ]
      %tm = add i64 %ti, -1
      %tp = add i64 %ti, 1
      %qu = getelementptr inbounds double, ptr %pm, i64 %tm
      %qd = getelementptr inbounds double, ptr %pm, i64 %tp
      %ql = getelementptr inbounds double, ptr %pl, i64 %ti
      %qr = getelementptr inbounds double, ptr %pr, i64 %ti
      %qo = getelementptr inbounds double, ptr %po, i64 %ti
      %xu = load double, ptr %qu, align 8
      %xd = load double, ptr %qd, align 8
      %xl = load double, ptr %ql, align 8
      %xr = load double, ptr %qr, align 8
      %y1 = fadd double %xu, %xd
      %y2 = fadd double %y1, %xl
      %y3 = fadd double %y2, %xr
      %yo = fmul double 0.25, %y3
      store double %yo, ptr %qo, align 8
      %tin = add i64 %ti, 1
      %ct = icmp slt i64 %tin, $(M9 - 1)
      br i1 %ct, label %tail, label %rowend
    rowend:
      %jn = add i64 %j, 1
      %cj = icmp sle i64 %jn, %j1
      br i1 %cj, label %col, label %done
    done:
      ret void
    }
    attributes #0 = { alwaysinline }
    """, "entry")
@noinline k9_cols_v(a::Matrix{Float64}, b::Matrix{Float64}, j0, j1) =
    GC.@preserve a b Base.llvmcall(K9_IR, Cvoid, Tuple{Ptr{Float64}, Ptr{Float64}, Int64, Int64}, pointer(a), pointer(b), j0, j1)
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
    # harnais commun de K9 (docs/K9.md) : grilles allouées une fois par processus, réinitialisées hors chrono
    ga = Matrix{Float64}(undef, M9, M9)
    gb = Matrix{Float64}(undef, M9, M9)
    for r in -WARMUP:reps-1
        for j in 0:M9-1, i in 0:M9-1
            ga[i + 1, j + 1] = k9_init(i, j)
        end
        copyto!(gb, ga)
        a, b = ga, gb
        t0 = time_ns()
        for _ in 1:4
            if v == "natural"
                k9_natural(a, b)
            elseif v == "tuned"
                k9_cols(a, b, 2, M9 - 1)
            elseif v == "tuned_v"
                k9_cols_v(a, b, 1, M9 - 2)
            elseif v == "mt_pool_v"
                # v4, point 4 (mt_pool_v) : les tâches de mt (réserve du runtime), chaque quart en tuned_v
                tasks = [Threads.@spawn k9_cols_v(a, b, 1 + (M9 - 2) * t ÷ 4, (M9 - 2) * (t + 1) ÷ 4) for t in 0:3]
                foreach(wait, tasks)
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
