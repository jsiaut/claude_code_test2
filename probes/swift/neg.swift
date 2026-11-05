import _Builtin_intrinsics.intel
// C2 : intrinsèque à corps (inline) importée ; E4 : préchargement ; E3 : indication de branchement
@inline(never) public func add16(_ a: UnsafePointer<Float>, _ o: UnsafeMutablePointer<Float>) {
    _mm512_storeu_ps(o, _mm512_add_ps(_mm512_loadu_ps(a), _mm512_loadu_ps(a)))
}
@inline(never) public func pf(_ p: UnsafeMutablePointer<UInt64>, _ h: UnsafePointer<UInt32>) -> UInt64 {
    for b in 0..<16 { _m_prefetchw(p + Int(h[b])) }
    var s: UInt64 = 0
    for b in 0..<16 { s &+= p[Int(h[b])] }
    return s
}
public func hint(_ x: Int) -> Int { if _slowPath(x == 3) { return 7 }; return x &+ 1 }
@inline(never) public func two(_ a: inout Int, _ b: inout Int) { a &+= 1; b &+= 1 }
