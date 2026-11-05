import _Builtin_intrinsics.intel
@inline(never) public func touch(_ p: UnsafeMutablePointer<UInt64>, _ n: Int) -> UInt64 {
    var s: UInt64 = 0
    for i in 0..<n {
        _m_prefetchw(p + i + 64)
        _m_prefetch(p + i + 128)
        s &+= p[i]
    }
    return s
}
