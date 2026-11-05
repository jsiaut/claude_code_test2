// Copie de sensibilité de bench/swift (remarque sur Swift, docs/SWIFT.md, section 5) : variantes k4 natural_w et
// k8 natural_ub en plus ; le reste est identique au source publié.
// Implémentation Swift 6.4 (bibliothèque standard, Synchronization ; Foundation et Dispatch, livrés avec la chaîne,
// pour les threads et les fichiers). Voir docs/SPEC.md et docs/SWIFT.md.
// Le code naturel garde les vérifications du mode release (-O : bornes et débordements) ; le code optimisé passe par
// des pointeurs non vérifiés (UnsafePointer), des opérateurs à enveloppe (&+, &*) et les types SIMD de la bibliothèque.
import Foundation
import Synchronization

// ------------------------------------------------------------------ harnais
let dataDir: String = ProcessInfo.processInfo.environment["MS_DATA"] ?? "/opt/msdata"
let warmup: Int = Int(ProcessInfo.processInfo.environment["WARMUP"] ?? "1") ?? 1

@inline(__always) func nowNs() -> UInt64 {
    var t = timespec()
    clock_gettime(CLOCK_MONOTONIC, &t)
    return UInt64(t.tv_sec) &* 1_000_000_000 &+ UInt64(t.tv_nsec)
}
func secs(_ t0: UInt64) -> Double { Double(nowNs() &- t0) * 1e-9 }
func result(_ k: String, _ v: String, _ p: String, _ rep: Int, _ sec: Double, _ chk: String) {
    print("RESULT;\(k);\(v);\(p);\(rep);\(String(format: "%.9f", sec));\(chk)")
    fflush(nil)
}
/// Lit un fichier de données dans un tampon aligné sur une ligne de cache (comme le C de référence).
func loadRaw(_ name: String) -> UnsafeMutableRawBufferPointer {
    let path = dataDir + "/" + name
    let fd = open(path, O_RDONLY)
    if fd < 0 { perror(path); exit(1) }
    var st = stat()
    fstat(fd, &st)
    let n = Int(st.st_size)
    let p = UnsafeMutableRawPointer.allocate(byteCount: max(n, 64), alignment: 64)
    var off = 0
    while off < n {
        let r = read(fd, p + off, n - off)
        if r <= 0 { perror("read"); exit(1) }
        off += r
    }
    close(fd)
    return UnsafeMutableRawBufferPointer(start: p, count: n)
}
func load<T>(_ name: String, _: T.Type) -> UnsafeMutableBufferPointer<T> { loadRaw(name).bindMemory(to: T.self) }
/// Données lues dans le conteneur par défaut (Array), pour le code naturel.
func loadArray<T>(_ name: String, _: T.Type) -> [T] {
    let b = load(name, T.self)
    defer { b.deallocate() }
    return Array(b)
}
func alignedBuffer<T>(_ n: Int, _: T.Type, alignment: Int = 64) -> UnsafeMutablePointer<T> {
    UnsafeMutableRawPointer.allocate(byteCount: n * MemoryLayout<T>.stride, alignment: alignment).bindMemory(to: T.self, capacity: n)
}
/// Lance n threads (Foundation.Thread) et attend leur fin : Thread n'a pas de join, un sémaphore de Dispatch en tient lieu.
func runThreads(_ n: Int, _ body: @escaping @Sendable (Int) -> Void) {
    let done = DispatchSemaphore(value: 0)
    for t in 0..<n {
        Thread { body(t); done.signal() }.start()
    }
    for _ in 0..<n { done.wait() }
}
@inline(__always) func ld16(_ p: UnsafePointer<Float>) -> SIMD16<Float> { UnsafeRawPointer(p).loadUnaligned(as: SIMD16<Float>.self) }
@inline(__always) func ld16(_ p: UnsafePointer<Int32>) -> SIMD16<Int32> { UnsafeRawPointer(p).loadUnaligned(as: SIMD16<Int32>.self) }
// élargissements écrits voie par voie (vectorisés en vpmovzxbd / vpmovsxdq) : init(truncatingIfNeeded:) de la
// bibliothèque n'est pas inliné (un appel de fonction par conversion)
@inline(__always) func ld16(_ p: UnsafePointer<UInt8>) -> SIMD16<Int32> {
    var r = SIMD16<Int32>()
    for k in 0..<16 { r[k] = Int32(p[k]) }
    return r
}
@inline(__always) func widen(_ v: SIMD16<Int32>) -> SIMD16<Int64> {
    var r = SIMD16<Int64>()
    for k in 0..<16 { r[k] = Int64(v[k]) }
    return r
}
@inline(__always) func ld8(_ p: UnsafePointer<Double>) -> SIMD8<Double> { UnsafeRawPointer(p).loadUnaligned(as: SIMD8<Double>.self) }
/// Réductions en arbre (sum() de la bibliothèque somme les voies dans l'ordre, sans réassociation)
@inline(__always) func hsum(_ v: SIMD16<Float>) -> Float {
    let a = v.lowHalf + v.highHalf, b = a.lowHalf + a.highHalf, c = b.lowHalf + b.highHalf
    return c[0] + c[1]
}
@inline(__always) func hsum(_ v: SIMD8<Double>) -> Double {
    let b = v.lowHalf + v.highHalf, c = b.lowHalf + b.highHalf
    return c[0] + c[1]
}

// ------------------------------------------------------------------ K1
let N1 = 1 << 22
/// Enregistrement naturel : struct (type valeur, recommandé par défaut), rangé en ligne dans un Array.
/// L'ordre des champs d'une struct Swift n'est pas garanti : construction champ par champ.
struct Particle {
    var x, y, z, vx, vy, vz, ax, ay, az, mass, charge, radius, temp, pressure, energy, density: Float
}
func particle(_ f: UnsafePointer<Float>) -> Particle {
    Particle(x: f[0], y: f[1], z: f[2], vx: f[3], vy: f[4], vz: f[5], ax: f[6], ay: f[7], az: f[8],
             mass: f[9], charge: f[10], radius: f[11], temp: f[12], pressure: f[13], energy: f[14], density: f[15])
}
@inline(never) func k1Natural(_ ps: [Particle]) -> Double {
    var e = 0.0
    for p in ps {
        e += 0.5 * Double(p.mass) * Double(p.vx * p.vx + p.vy * p.vy + p.vz * p.vz)
    }
    return e
}
// AoS optimisé : calcul f32, 8 accumulateurs f64 (une voie de SIMD8 par particule du lot), tampon aligné sur 64 octets
@inline(never) func k1AoS(_ p: UnsafePointer<Particle>, _ n: Int) -> Double {
    var acc = SIMD8<Double>()
    var i = 0
    while i < n {
        var t = SIMD8<Float>()
        for k in 0..<8 {
            let q = p[i &+ k]
            t[k] = 0.5 * q.mass * (q.vx * q.vx + q.vy * q.vy + q.vz * q.vz)
        }
        acc += SIMD8<Double>(t)
        i &+= 8
    }
    return acc.sum()
}
// SoA optimisé : SIMD16<Float> + FMA (addProduct), conversion f64 pour l'accumulation, 4 accumulateurs
@inline(never) func k1SoA(_ vx: UnsafePointer<Float>, _ vy: UnsafePointer<Float>, _ vz: UnsafePointer<Float>,
                          _ m: UnsafePointer<Float>, _ n: Int) -> Double {
    var a0 = SIMD8<Double>(), a1 = SIMD8<Double>(), a2 = SIMD8<Double>(), a3 = SIMD8<Double>()
    let h = SIMD16<Float>(repeating: 0.5)
    var i = 0
    while i < n {
        do {
            let x = ld16(vx + i), y = ld16(vy + i), z = ld16(vz + i), w = ld16(m + i)
            var v2 = x * x
            v2.addProduct(y, y)
            v2.addProduct(z, z)
            let e = (h * w) * v2
            a0 += SIMD8<Double>(e.lowHalf)
            a1 += SIMD8<Double>(e.highHalf)
        }
        do {
            let j = i &+ 16
            let x = ld16(vx + j), y = ld16(vy + j), z = ld16(vz + j), w = ld16(m + j)
            var v2 = x * x
            v2.addProduct(y, y)
            v2.addProduct(z, z)
            let e = (h * w) * v2
            a2 += SIMD8<Double>(e.lowHalf)
            a3 += SIMD8<Double>(e.highHalf)
        }
        i &+= 32
    }
    return hsum((a0 + a1) + (a2 + a3))
}
/// Empreinte K1 (D2a) : RSS courant en octets (/proc/self/statm, 2e champ ; pages de 4 Kio)
func rssNow() -> Int {
    guard let s = try? String(contentsOfFile: "/proc/self/statm", encoding: .utf8) else { return 0 }
    let f = s.split(separator: " ")
    return f.count > 1 ? (Int(f[1]) ?? 0) * 4096 : 0
}
func runK1(_ v: String, _ reps: Int) {
    if v == "footprint0" { return result("k1", v, "energy", 0, 0, "0") }
    let raw = load("k1_particles.f32", Float.self)
    if v == "footprint_raw" { return result("k1", v, "energy", 0, 0, "0") }
    let fp = v == "footprint"
    let m1 = fp ? rssNow() : 0  // P1 : tampon brut chargé
    let rp = UnsafePointer(raw.baseAddress!)
    var ps = (0..<N1).map { particle(rp + 16 * $0) }  // collection naturelle : [Particle]
    if fp {  // P2 : collection construite, tampon brut encore vivant
        let m2 = rssNow()
        print("META;mem;rss;\(m1);\(m2)\nMETA;rss;\(m1);\(m2)\nMETA;raw0;\(raw[0])")
        raw.deallocate()
        return result("k1", v, "energy", 0, 0, String(format: "%.6f", k1Natural(ps)))
    }
    raw.deallocate()
    if v == "soa" {
        var f = [UnsafeMutablePointer<Float>]()
        for _ in 0..<16 { f.append(alignedBuffer(N1, Float.self)) }
        ps.withUnsafeBytes { b in
            let src = b.bindMemory(to: Float.self).baseAddress!  // lecture des champs par leur décalage
            let off = [\Particle.x, \.y, \.z, \.vx, \.vy, \.vz, \.ax, \.ay, \.az, \.mass, \.charge, \.radius, \.temp,
                       \.pressure, \.energy, \.density].map { MemoryLayout<Particle>.offset(of: $0)! / 4 }
            for i in 0..<N1 { for k in 0..<16 { f[k][i] = src[16 * i + off[k]] } }
        }
        ps = []
        for r in -warmup..<reps {
            let t0 = nowNs()
            let e = k1SoA(f[3], f[4], f[5], f[9], N1)
            let dt = secs(t0)
            if r >= 0 { result("k1", v, "energy", r, dt, String(format: "%.6f", e)) }
        }
        return
    }
    if v == "natural_shuffled" {
        let perm = loadArray("k1_perm.u32", UInt32.self)
        ps = perm.map { ps[Int($0)] }
    }
    if v == "aos" {
        let a = alignedBuffer(N1, Particle.self)
        _ = UnsafeMutableBufferPointer(start: a, count: N1).initialize(from: ps)
        ps = []
        for r in -warmup..<reps {
            let t0 = nowNs()
            let e = k1AoS(a, N1)
            let dt = secs(t0)
            if r >= 0 { result("k1", v, "energy", r, dt, String(format: "%.6f", e)) }
        }
        return
    }
    for r in -warmup..<reps {
        let t0 = nowNs()
        let e = k1Natural(ps)
        let dt = secs(t0)
        if r >= 0 { result("k1", v, "energy", r, dt, String(format: "%.6f", e)) }
    }
}

// ------------------------------------------------------------------ K2
@inline(never) func k2Chase(_ a: UnsafePointer<UInt32>, _ h: Int) -> UInt32 {
    var i: UInt32 = 0
    for _ in 0..<h { i = a[Int(i)] }
    return i
}
func runK2(_ v: String, _ reps: Int, _ p: String) {
    let a = load("k2_chase_\(p).u32", UInt32.self)
    for r in -warmup..<reps {
        let t0 = nowNs()
        let i = k2Chase(a.baseAddress!, 4_200_000)
        let dt = secs(t0)
        if r >= 0 { result("k2", v, p, r, dt, "\(i)") }
    }
}

// ------------------------------------------------------------------ K3
let ITER3 = 1 << 25
func runK3(_ v: String, _ reps: Int) {
    let rmw = v.hasPrefix("rmw"), padded = v.hasSuffix("padded")
    print("META;k3_mechanism;" + (rmw ? "Atomic.wrappingAdd(.relaxed) (lock add)" : "Atomic.load/store(.relaxed) (mov)"))
    // compteurs Atomic<UInt64> (module Synchronization) dans un bloc aligné sur 128 octets : pas de 8 ou 128 octets
    let mem = UnsafeMutableRawPointer.allocate(byteCount: 4 * 128, alignment: 128).bindMemory(to: Atomic<UInt64>.self, capacity: 64)
    let stride = padded ? 16 : 1
    for t in 0..<4 { (mem + t * stride).initialize(to: Atomic<UInt64>(0)) }
    nonisolated(unsafe) let c = mem
    for r in -warmup..<reps {
        for t in 0..<4 { c[t * stride].store(0, ordering: .sequentiallyConsistent) }
        let t0 = nowNs()
        runThreads(4) { t in
            let x = c + t * stride
            if rmw {
                for _ in 0..<ITER3 { x.pointee.wrappingAdd(1, ordering: .relaxed) }
            } else {
                for _ in 0..<ITER3 { x.pointee.store(x.pointee.load(ordering: .relaxed) &+ 1, ordering: .relaxed) }
            }
        }
        let dt = secs(t0)
        var s: UInt64 = 0
        for t in 0..<4 { s += c[t * stride].load(ordering: .sequentiallyConsistent) }
        if r >= 0 { result("k3", v, "4x2^25", r, dt, "\(s)") }
    }
}

// ------------------------------------------------------------------ K4
@inline(never) func k4Natural(_ v: [UInt8]) -> UInt64 {
    var s: UInt64 = 0
    for x in v {
        if x >= 128 { s += UInt64(x) }
    }
    return s
}
@inline(never) func k4NaturalWrapping(_ v: [UInt8]) -> UInt64 {
    var s: UInt64 = 0
    for x in v {
        if x >= 128 { s &+= UInt64(x) }
    }
    return s
}
@inline(never) func k4Branchless(_ v: UnsafeBufferPointer<UInt8>) -> UInt64 {
    var s: UInt64 = 0
    for x in v { s &+= UInt64(x) &* UInt64(x >> 7) }
    return s
}
func runK4(_ v: String, _ reps: Int) {
    if v == "branchless_unsorted" {
        let d = UnsafeBufferPointer(load("k4_bytes.u8", UInt8.self))
        for r in -warmup..<reps {
            let t0 = nowNs()
            let s = k4Branchless(d)
            let dt = secs(t0)
            if r >= 0 { result("k4", v, "16M", r, dt, "\(s)") }
        }
        return
    }
    var d = loadArray("k4_bytes.u8", UInt8.self)
    if v == "natural_sorted" { d.sort() }  // hors chrono
    for r in -warmup..<reps {
        let t0 = nowNs()
        let s = v == "natural_w_unsorted" ? k4NaturalWrapping(d) : k4Natural(d)
        let dt = secs(t0)
        if r >= 0 { result("k4", v, "16M", r, dt, "\(s)") }
    }
}

// ------------------------------------------------------------------ K5
let INNER5 = 1 << 16
let sink = Atomic<UInt32>(0)
@inline(never) func k5Natural(_ a: [Float], _ b: [Float]) -> Float {
    var s: Float = 0
    for i in 0..<a.count { s += a[i] * b[i] }
    return s
}
@inline(never) func k5Tuned(_ a: UnsafePointer<Float>, _ b: UnsafePointer<Float>, _ n: Int) -> Float {
    var s0 = SIMD16<Float>(), s1 = SIMD16<Float>(), s2 = SIMD16<Float>(), s3 = SIMD16<Float>()
    var i = 0
    while i < n {
        s0.addProduct(ld16(a + i), ld16(b + i))
        s1.addProduct(ld16(a + (i &+ 16)), ld16(b + (i &+ 16)))
        s2.addProduct(ld16(a + (i &+ 32)), ld16(b + (i &+ 32)))
        s3.addProduct(ld16(a + (i &+ 48)), ld16(b + (i &+ 48)))
        i &+= 64
    }
    return hsum((s0 + s1) + (s2 + s3))
}
func runK5(_ v: String, _ reps: Int) {
    let tuned = v == "tuned"
    let pa = load("k5_a.f32", Float.self), pb = load("k5_b.f32", Float.self)
    let a = Array(pa), b = Array(pb)
    for r in -warmup..<reps {
        var d: Float = 0
        let t0 = nowNs()
        for _ in 0..<INNER5 {
            atomicMemoryFence(ordering: .acquiring)  // barrière du compilateur (aucune instruction sur x86), comme BARRIER(a) en C
            d = tuned ? k5Tuned(pa.baseAddress!, pb.baseAddress!, pa.count) : k5Natural(a, b)
            sink.store(d.bitPattern, ordering: .relaxed)  // rend le résultat observable, comme KEEP(d) en C
        }
        let dt = secs(t0)
        if r >= 0 { result("k5", v, "2048x65536", r, dt, String(format: "%.4f", d)) }
    }
}

// ------------------------------------------------------------------ K6
let N6 = 1 << 24
/// Colonnes naturelles : Array
struct Cols {
    let sd, pr: [Int32]
    let q, d, t, rf, ls: [UInt8]
}
/// Colonnes du code optimisé : tampons alignés sur 64 octets
struct ColsP: @unchecked Sendable {
    let sd, pr: UnsafePointer<Int32>
    let q, d, t, rf, ls: UnsafePointer<UInt8>
}
struct Q1Agg {
    var count: Int64 = 0, qty: Int64 = 0, price: Int64 = 0, discPrice: Int64 = 0, charge: Int64 = 0
}
@inline(never) func q6Natural(_ c: Cols) -> Int64 {
    var s: Int64 = 0
    for i in 0..<c.sd.count {
        if c.sd[i] >= 8766 && c.sd[i] < 9131 && c.d[i] >= 5 && c.d[i] <= 7 && c.q[i] < 24 {
            s += Int64(c.pr[i]) * Int64(c.d[i])
        }
    }
    return s
}
@inline(never) func q1Natural(_ c: Cols, _ acc: inout [Q1Agg]) {
    for i in 0..<c.sd.count {
        if c.sd[i] <= 10471 {
            let g = Int(c.rf[i]) * 2 + Int(c.ls[i])
            let p = Int64(c.pr[i])
            let dp = p * (100 - Int64(c.d[i]))
            acc[g].count += 1
            acc[g].qty += Int64(c.q[i])
            acc[g].price += p
            acc[g].discPrice += dp
            acc[g].charge += dp * (100 + Int64(c.t[i]))
        }
    }
}
// reste scalaire du code optimisé (< 16 lignes)
func q6Tail(_ c: ColsP, _ lo: Int, _ hi: Int) -> Int64 {
    var s: Int64 = 0
    for i in lo..<hi where c.sd[i] >= 8766 && c.sd[i] < 9131 && c.d[i] >= 5 && c.d[i] <= 7 && c.q[i] < 24 {
        s &+= Int64(c.pr[i]) &* Int64(c.d[i])
    }
    return s
}
func q1Tail(_ c: ColsP, _ lo: Int, _ hi: Int, _ acc: UnsafeMutablePointer<Int64>) {
    for i in lo..<hi where c.sd[i] <= 10471 {
        let g = Int(c.rf[i]) &* 2 &+ Int(c.ls[i])
        let p = Int64(c.pr[i]), dp = p &* (100 &- Int64(c.d[i]))
        acc[g * 5] &+= 1
        acc[g * 5 + 1] &+= Int64(c.q[i])
        acc[g * 5 + 2] &+= p
        acc[g * 5 + 3] &+= dp
        acc[g * 5 + 4] &+= dp &* (100 &+ Int64(c.t[i]))
    }
}
// Q6 optimisé : SIMD16<Int32>, prédicat en masques, replacing(with:where:), accumulation SIMD16<Int64>
@inline(never) func q6Tuned(_ c: ColsP, _ lo: Int, _ hi: Int) -> Int64 {
    var acc = SIMD16<Int64>()
    let d0 = SIMD16<Int32>(repeating: 8766), d1 = SIMD16<Int32>(repeating: 9131)
    let r5 = SIMD16<Int32>(repeating: 5), r7 = SIMD16<Int32>(repeating: 7), q24 = SIMD16<Int32>(repeating: 24)
    let zero = SIMD16<Int32>()
    var i = lo
    while i &+ 16 <= hi {
        let sd = ld16(c.sd + i), d = ld16(c.d + i), q = ld16(c.q + i), pr = ld16(c.pr + i)
        let m = (sd .>= d0) .& (sd .< d1) .& (d .>= r5) .& (d .<= r7) .& (q .< q24)
        acc &+= widen(zero.replacing(with: pr &* d, where: m))
        i &+= 16
    }
    return acc.wrappedSum() &+ q6Tail(c, i, hi)
}
// Q1 optimisé : agrégation masquée par groupe (6 groupes), accumulateurs 32 bits vidés toutes les 4096 lignes,
// produits 64 bits pour la colonne charge (même algorithme que la référence C) ; groupes déroulés à la main
// (la boucle sur un InlineArray de 6 groupes n'est pas déroulée : accumulateurs en mémoire)
struct Q1Lanes {
    var cnt = SIMD16<Int32>(), q = SIMD16<Int32>(), p = SIMD16<Int32>(), dp = SIMD16<Int32>()
    var ch = SIMD16<Int64>()
    @inline(__always) mutating func add(_ m: SIMDMask<SIMD16<Int32>>, _ m64: SIMDMask<SIMD16<Int64>>, _ vq: SIMD16<Int32>,
                                        _ vp: SIMD16<Int32>, _ vdp: SIMD16<Int32>, _ vch: SIMD16<Int64>) {
        let z = SIMD16<Int32>()
        cnt &+= z.replacing(with: SIMD16<Int32>(repeating: 1), where: m)
        q &+= z.replacing(with: vq, where: m)
        p &+= z.replacing(with: vp, where: m)
        dp &+= z.replacing(with: vdp, where: m)
        ch &+= SIMD16<Int64>().replacing(with: vch, where: m64)
    }
    @inline(__always) func flush(_ a: UnsafeMutablePointer<Int64>) {
        a[0] &+= Int64(cnt.wrappedSum())
        a[1] &+= Int64(q.wrappedSum())
        a[2] &+= Int64(p.wrappedSum())
        a[3] &+= widen(dp).wrappedSum()
        a[4] &+= ch.wrappedSum()
    }
}
@inline(never) func q1Tuned(_ c: ColsP, _ lo: Int, _ hi: Int, _ acc: UnsafeMutablePointer<Int64>) {
    let lim = SIMD16<Int32>(repeating: 10471), c100 = SIMD16<Int32>(repeating: 100)
    let two = SIMD16<Int32>(repeating: 2), minus1 = SIMD16<Int32>(repeating: -1)
    let k32 = (0..<6).map { SIMD16<Int32>(repeating: Int32($0)) }, k64 = (0..<6).map { SIMD16<Int64>(repeating: Int64($0)) }
    var i = lo
    while i &+ 16 <= hi {
        var g0 = Q1Lanes(), g1 = Q1Lanes(), g2 = Q1Lanes(), g3 = Q1Lanes(), g4 = Q1Lanes(), g5 = Q1Lanes()
        let end = i &+ 4096 <= hi ? i &+ 4096 : hi &- (hi &- i) % 16
        while i < end {
            // groupe de la ligne, -1 si elle ne passe pas le filtre (comparaisons vecteur contre vecteur : les formes
            // vecteur contre scalaire de la bibliothèque, vg .== 0, sont compilées voie par voie avec branchements)
            let vg = (ld16(c.rf + i) &* two &+ ld16(c.ls + i)).replacing(with: minus1, where: ld16(c.sd + i) .> lim)
            let vg64 = widen(vg)
            let vq = ld16(c.q + i), vd = ld16(c.d + i), vt = ld16(c.t + i) &+ c100, vp = ld16(c.pr + i)
            let vdp = vp &* (c100 &- vd)
            let vch = widen(vdp) &* widen(vt)
            g0.add(vg .== k32[0], vg64 .== k64[0], vq, vp, vdp, vch)
            g1.add(vg .== k32[1], vg64 .== k64[1], vq, vp, vdp, vch)
            g2.add(vg .== k32[2], vg64 .== k64[2], vq, vp, vdp, vch)
            g3.add(vg .== k32[3], vg64 .== k64[3], vq, vp, vdp, vch)
            g4.add(vg .== k32[4], vg64 .== k64[4], vq, vp, vdp, vch)
            g5.add(vg .== k32[5], vg64 .== k64[5], vq, vp, vdp, vch)
            i &+= 16
        }
        g0.flush(acc)
        g1.flush(acc + 5)
        g2.flush(acc + 10)
        g3.flush(acc + 15)
        g4.flush(acc + 20)
        g5.flush(acc + 25)
    }
    if i < hi { q1Tail(c, i, hi, acc) }
}
func runK6(_ v: String, _ reps: Int, _ p: String) {
    let q1 = p == "q1"
    if v == "natural" {
        let c = Cols(sd: loadArray("k6_shipdate.i32", Int32.self), pr: loadArray("k6_extendedprice.i32", Int32.self),
                     q: loadArray("k6_quantity.u8", UInt8.self), d: loadArray("k6_discount.u8", UInt8.self),
                     t: loadArray("k6_tax.u8", UInt8.self), rf: loadArray("k6_returnflag.u8", UInt8.self),
                     ls: loadArray("k6_linestatus.u8", UInt8.self))
        for r in -warmup..<reps {
            var s: Int64 = 0
            var acc = [Q1Agg](repeating: Q1Agg(), count: 6)
            let t0 = nowNs()
            if q1 { q1Natural(c, &acc) } else { s = q6Natural(c) }
            let dt = secs(t0)
            if q1 { for a in acc { s += a.count + a.qty + a.price + a.discPrice + a.charge } }
            if r >= 0 { result("k6", v, p, r, dt, "\(s)") }
        }
        return
    }
    let c = ColsP(sd: UnsafePointer(load("k6_shipdate.i32", Int32.self).baseAddress!),
                  pr: UnsafePointer(load("k6_extendedprice.i32", Int32.self).baseAddress!),
                  q: UnsafePointer(load("k6_quantity.u8", UInt8.self).baseAddress!),
                  d: UnsafePointer(load("k6_discount.u8", UInt8.self).baseAddress!),
                  t: UnsafePointer(load("k6_tax.u8", UInt8.self).baseAddress!),
                  rf: UnsafePointer(load("k6_returnflag.u8", UInt8.self).baseAddress!),
                  ls: UnsafePointer(load("k6_linestatus.u8", UInt8.self).baseAddress!))
    nonisolated(unsafe) let part = UnsafeMutablePointer<Int64>.allocate(capacity: 4 * 32)
    for r in -warmup..<reps {
        part.initialize(repeating: 0, count: 4 * 32)
        var s: Int64 = 0
        let t0 = nowNs()
        if v == "mt" {
            runThreads(4) { t in
                let lo = N6 / 4 * t, hi = N6 / 4 * (t + 1)
                if q1 { q1Tuned(c, lo, hi, part + 32 * t) } else { part[32 * t] = q6Tuned(c, lo, hi) }
            }
            for k in 0..<(4 * 32) { s &+= part[k] }
        } else {
            if q1 { q1Tuned(c, 0, N6, part) } else { s = q6Tuned(c, 0, N6) }
        }
        let dt = secs(t0)
        if q1 && v != "mt" { for k in 0..<30 { s &+= part[k] } }
        if r >= 0 { result("k6", v, p, r, dt, "\(s)") }
    }
}

// ------------------------------------------------------------------ K7
let N7 = 1 << 24
struct Agg {
    var count: UInt32 = 0
    var sum: UInt64 = 0
    mutating func add(_ v: UInt32) {
        count += 1
        sum += UInt64(v)
    }
}
/// Case de la table optimisée (16 octets, 4 par ligne de cache)
struct Slot {
    var key: UInt32
    var count: UInt32
    var sum: UInt64
}
func runK7(_ v: String, _ reps: Int) {
    let keys = loadArray("k7_keys.u32", UInt32.self), vals = loadArray("k7_vals.u32", UInt32.self)
    for r in -warmup..<reps {
        var nk: UInt64 = 0, ws: UInt64 = 0
        var dt = 0.0
        if v == "natural" {  // Dictionary de la bibliothèque standard
            let t0 = nowNs()
            var m: [UInt32: Agg] = [:]
            for (k, x) in zip(keys, vals) { m[k, default: Agg()].add(x) }
            dt = secs(t0)
            for (k, a) in m {
                nk += 1
                ws += a.sum * UInt64((k & 1023) + 1)
            }
        } else {  // adressage ouvert, sondage linéaire, hachage de Fibonacci (pas de préchargement logiciel en Swift)
            let LOG: UInt32 = 21, CAP = 1 << 21
            let t0 = nowNs()
            let tab = alignedBuffer(CAP, Slot.self)
            tab.initialize(repeating: Slot(key: 0, count: 0, sum: 0), count: CAP)
            keys.withUnsafeBufferPointer { kb in
                vals.withUnsafeBufferPointer { vb in
                    for i in 0..<kb.count {
                        let k = kb[i]
                        var s = Int((k &* 0x9E37_79B1) >> (32 &- LOG))
                        while tab[s].count != 0 && tab[s].key != k { s = (s &+ 1) & (CAP &- 1) }
                        tab[s].key = k
                        tab[s].count &+= 1
                        tab[s].sum &+= UInt64(vb[i])
                    }
                }
            }
            dt = secs(t0)
            for s in 0..<CAP where tab[s].count != 0 {
                nk += 1
                ws &+= tab[s].sum &* UInt64((tab[s].key & 1023) + 1)
            }
            tab.deallocate()
        }
        if r >= 0 { result("k7", v, "16M/1M", r, dt, "\(nk):\(ws)") }
    }
}

// ------------------------------------------------------------------ K8
/// Nœud naturel : classe (référence comptée par ARC), une allocation par nœud
class Node {
    var v: Int64
    var l: Node?
    var r: Node?
    init(_ v: Int64) { self.v = v }
}
func tBuild(_ d: Int, _ c: inout Int64) -> Node {
    let n = Node(c)
    c += 1
    if d > 0 {
        n.l = tBuild(d - 1, &c)
        n.r = tBuild(d - 1, &c)
    }
    return n
}
func tSum(_ n: Node?) -> Int64 {
    guard let n else { return 0 }
    return n.v + tSum(n.l) + tSum(n.r)
}
/// Variante natural_ub : arbre à propriété unique (UniqueBox, Swift 6.4), sans comptage de références ; le deinit vide
/// évite l'épuisement de mémoire de l'optimiseur de 6.4.2 sur ce type récursif
struct UNode: ~Copyable {
    var v: Int64
    var l: UniqueBox<UNode>?
    var r: UniqueBox<UNode>?
    deinit {}
}
func uBuild(_ d: Int, _ c: inout Int64) -> UniqueBox<UNode> {
    var n = UNode(v: c, l: nil, r: nil)
    c += 1
    if d > 0 {
        n.l = uBuild(d - 1, &c)
        n.r = uBuild(d - 1, &c)
    }
    return UniqueBox(n)
}
func uSum(_ n: borrowing UNode) -> Int64 {
    var s = n.v
    switch n.l { case .some(let b): s += uSum(b.value); case .none: break }
    switch n.r { case .some(let b): s += uSum(b.value); case .none: break }
    return s
}
/// Arène : nœuds compacts dans un tampon réutilisé, enfants par indice
struct ANode {
    var v: Int64
    var l: Int32
    var r: Int32
}
func aBuild(_ a: UnsafeMutablePointer<ANode>, _ top: inout Int32, _ d: Int, _ c: inout Int64) -> Int32 {
    let i = top
    top &+= 1
    a[Int(i)] = ANode(v: c, l: -1, r: -1)
    c &+= 1
    if d > 0 {
        let l = aBuild(a, &top, d &- 1, &c)
        let r = aBuild(a, &top, d &- 1, &c)
        a[Int(i)].l = l
        a[Int(i)].r = r
    }
    return i
}
func aSum(_ a: UnsafePointer<ANode>, _ i: Int32) -> Int64 {
    if i < 0 { return 0 }
    let n = a[Int(i)]
    return n.v &+ aSum(a, n.l) &+ aSum(a, n.r)
}
func runK8(_ v: String, _ reps: Int) {
    let Q = 16384
    let tuned = v == "tuned"
    var c0: Int64 = 0
    let keep = tBuild(20, &c0)
    let lsum = tSum(keep)
    var lat = [UInt64](repeating: 0, count: Q)
    let arena = UnsafeMutablePointer<ANode>.allocate(capacity: 2047)
    for r in -warmup..<reps {
        var total: Int64 = 0
        let t0 = nowNs()
        for q in 0..<Q {
            let a = nowNs()
            var c = Int64(q)
            let s: Int64
            if tuned {
                var top: Int32 = 0
                s = aSum(arena, aBuild(arena, &top, 10, &c))
            } else if v == "natural_ub" {
                let t = uBuild(10, &c)
                s = uSum(t.value)
            } else {
                let t = tBuild(10, &c)
                s = tSum(t)
            }  // l'arbre naturel est libéré ici (fin de la dernière utilisation : décomptes ARC), dans le chrono
            total += s
            lat[q] = nowNs() &- a
        }
        let dt = secs(t0)
        if r >= 0 {
            result("k8", v, "16384x2047", r, dt, "\(total + lsum)")
            lat.sort()
            print("LAT;\(v);\(lat[Q / 2]);\(lat[Q * 9 / 10]);\(lat[Q * 99 / 100]);\(lat[Q * 999 / 1000]);\(lat[Q - 1])")
            fflush(nil)
        }
    }
    withExtendedLifetime(keep) {}
}

// ------------------------------------------------------------------ K9
let M9 = 2048
@inline(__always) func k9Init(_ i: Int, _ j: Int) -> Double { Double((i * 31 + j * 17) % 1024) / 1024.0 }
/// Naturel : tableau 2D par défaut, [[Double]]
@inline(never) func k9Natural(_ inp: [[Double]], _ out: inout [[Double]]) {
    for i in 1..<M9 - 1 {
        for j in 1..<M9 - 1 {
            out[i][j] = 0.25 * (((inp[i - 1][j] + inp[i + 1][j]) + inp[i][j - 1]) + inp[i][j + 1])
        }
    }
}
// Optimisé : tableau plat contigu aligné, SIMD8<Double>
@inline(never) func k9Rows(_ inp: UnsafePointer<Double>, _ o: UnsafeMutablePointer<Double>, _ r0: Int, _ r1: Int) {
    let q4 = SIMD8<Double>(repeating: 0.25)
    for i in r0..<r1 {
        let up = inp + (i - 1) * M9, mid = inp + i * M9, dn = inp + (i + 1) * M9, op = o + i * M9
        var j = 1
        while j &+ 8 <= M9 - 1 {
            let u = ld8(up + j), d = ld8(dn + j), l = ld8(mid + (j &- 1)), rr = ld8(mid + (j &+ 1))
            UnsafeMutableRawPointer(op + j).storeBytes(of: q4 * (((u + d) + l) + rr), as: SIMD8<Double>.self)
            j &+= 8
        }
        while j < M9 - 1 {
            op[j] = 0.25 * (((up[j] + dn[j]) + mid[j &- 1]) + mid[j &+ 1])
            j &+= 1
        }
    }
}
func runK9(_ v: String, _ reps: Int) {
    // harnais commun de K9 (docs/K9.md) : grilles allouées une fois par processus, réinitialisées hors chrono
    if v == "natural" {
        var a = [[Double]](repeating: [Double](repeating: 0, count: M9), count: M9)
        var b = [[Double]](repeating: [Double](repeating: 0, count: M9), count: M9)
        for r in -warmup..<reps {
            for i in 0..<M9 {
                for j in 0..<M9 {
                    a[i][j] = k9Init(i, j)
                    b[i][j] = a[i][j]
                }
            }
            let t0 = nowNs()
            for _ in 0..<4 {
                k9Natural(a, &b)
                swap(&a, &b)
            }
            let dt = secs(t0)
            var s = 0.0
            for row in a { for x in row { s += x } }
            if r >= 0 { result("k9", v, "2048^2x4", r, dt, String(format: "%.15e", s)) }
        }
        return
    }
    let n = M9 * M9
    var a = alignedBuffer(n, Double.self), b = alignedBuffer(n, Double.self)
    for r in -warmup..<reps {
        for k in 0..<n {
            a[k] = k9Init(k / M9, k % M9)
            b[k] = a[k]
        }
        let t0 = nowNs()
        for _ in 0..<4 {
            if v == "tuned" {
                k9Rows(a, b, 1, M9 - 1)
            } else {
                nonisolated(unsafe) let (x, y) = (a, b)
                runThreads(4) { t in k9Rows(x, y, 1 + (M9 - 2) * t / 4, 1 + (M9 - 2) * (t + 1) / 4) }
            }
            swap(&a, &b)
        }
        let dt = secs(t0)
        var s = 0.0
        for k in 0..<n { s += a[k] }
        if r >= 0 { result("k9", v, "2048^2x4", r, dt, String(format: "%.15e", s)) }
    }
}

// ------------------------------------------------------------------ K10
let M10 = 1 << 22
let CAP10 = 1 << 14
/// Naturel : AsyncStream (seule file concurrente de la bibliothèque standard ; tampon non borné, sans contre-pression),
/// producteur et consommateur dans deux tâches enfants d'un groupe (exécuteur concurrent global)
func k10Natural() async -> UInt64 {
    let (stream, cont) = AsyncStream.makeStream(of: UInt64.self)
    return await withTaskGroup(of: UInt64.self) { g in
        g.addTask {
            var s: UInt64 = 0
            for await x in stream { s += x }
            return s
        }
        g.addTask {
            for x in 1...UInt64(M10) { cont.yield(x) }
            cont.finish()
            return 0
        }
        var s: UInt64 = 0
        for await x in g { s += x }
        return s
    }
}
/// Optimisé : anneau SPSC (Lamport, copies locales des indices distants, à la Rigtorp), acquire/release,
/// indices sur des lignes séparées (128 octets) ; attente active sans pause (pas d'indice de boucle d'attente en Swift)
func k10Tuned() -> UInt64 {
    let raw = UnsafeMutableRawPointer.allocate(byteCount: 256 + CAP10 * 8, alignment: 128)
    let widx = raw.bindMemory(to: Atomic<Int>.self, capacity: 1)
    widx.initialize(to: Atomic<Int>(0))
    let ridx = (raw + 128).bindMemory(to: Atomic<Int>.self, capacity: 1)
    ridx.initialize(to: Atomic<Int>(0))
    let buf = (raw + 256).bindMemory(to: UInt64.self, capacity: CAP10)
    nonisolated(unsafe) let (wi, ri, bf) = (widx, ridx, buf)
    nonisolated(unsafe) let res = UnsafeMutablePointer<UInt64>.allocate(capacity: 1)
    runThreads(2) { t in
        if t == 0 {  // consommateur
            var rd = 0, wc = 0
            var s: UInt64 = 0
            for _ in 0..<M10 {
                while rd == wc { wc = wi.pointee.load(ordering: .acquiring) }
                s &+= bf[rd & (CAP10 - 1)]
                rd &+= 1
                ri.pointee.store(rd, ordering: .releasing)
            }
            res.pointee = s
        } else {  // producteur
            var w = 0, rc = 0
            for x in 1...UInt64(M10) {
                while w &- rc == CAP10 { rc = ri.pointee.load(ordering: .acquiring) }
                bf[w & (CAP10 - 1)] = x
                w &+= 1
                wi.pointee.store(w, ordering: .releasing)
            }
        }
    }
    let s = res.pointee
    res.deallocate()
    raw.deallocate()
    return s
}
func runK10(_ v: String, _ reps: Int) async {
    for r in -warmup..<reps {
        let t0 = nowNs()
        let s = v == "natural" ? await k10Natural() : k10Tuned()
        let dt = secs(t0)
        if r >= 0 { result("k10", v, "2^22", r, dt, "\(s)") }
    }
}

@main struct MS {
    static func main() async {
        let args = CommandLine.arguments
        if args.count < 4 {
            print("usage: ms kernel variant reps [param]")
            exit(1)
        }
        let k = args[1], v = args[2], reps = Int(args[3])!, p = args.count > 4 ? args[4] : ""
        switch k {
        case "k1": runK1(v, reps)
        case "k2": runK2(v, reps, p)
        case "k3": runK3(v, reps)
        case "k4": runK4(v, reps)
        case "k5": runK5(v, reps)
        case "k6": runK6(v, reps, p)
        case "k7": runK7(v, reps)
        case "k8": runK8(v, reps)
        case "k9": runK9(v, reps)
        case "k10": await runK10(v, reps)
        default:
            print("noyau inconnu \(k)")
            exit(1)
        }
    }
}
