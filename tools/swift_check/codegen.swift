// Faits de génération de code relevés pendant l'implémentation (docs/SWIFT.md, 2.4) ; compilé par facts.sh.
// 1. conversions de la bibliothèque contre élargissement voie par voie
@inline(never) public func convLib(_ p: UnsafePointer<UInt8>) -> SIMD16<Int32> {
    SIMD16<Int32>(truncatingIfNeeded: UnsafeRawPointer(p).loadUnaligned(as: SIMD16<UInt8>.self))
}
@inline(never) public func convLanes(_ p: UnsafePointer<UInt8>) -> SIMD16<Int32> {
    var r = SIMD16<Int32>()
    for k in 0..<16 { r[k] = Int32(p[k]) }
    return r
}
// 2. comparaison vecteur contre scalaire et vecteur contre vecteur
@inline(never) public func cmpScalar(_ v: SIMD16<Int32>, _ a: SIMD16<Int32>) -> SIMD16<Int32> {
    SIMD16<Int32>().replacing(with: a, where: v .== 3)
}
@inline(never) public func cmpVector(_ v: SIMD16<Int32>, _ a: SIMD16<Int32>) -> SIMD16<Int32> {
    SIMD16<Int32>().replacing(with: a, where: v .== SIMD16<Int32>(repeating: 3))
}
// 3. sum() de la bibliothèque (ordre strict) contre réduction en arbre
@inline(never) public func sumLib(_ v: SIMD16<Float>) -> Float { v.sum() }
@inline(never) public func sumTree(_ v: SIMD16<Float>) -> Float {
    let a = v.lowHalf + v.highHalf, b = a.lowHalf + a.highHalf, c = b.lowHalf + b.highHalf
    return c[0] + c[1]
}
// 4. boucle naturelle de K4 en -O (piège de débordement conservé)
@inline(never) public func k4(_ v: [UInt8]) -> UInt64 {
    var s: UInt64 = 0
    for x in v { if x >= 128 { s += UInt64(x) } }
    return s
}
