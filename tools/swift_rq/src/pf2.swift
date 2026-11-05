// llvm.prefetch(ptr, rw, locality, cache type)
@_silgen_name("llvm.prefetch.p0")
func llvm_prefetch(_ p: UnsafeRawPointer, _ rw: Int32, _ locality: Int32, _ cache: Int32)
@_silgen_name("llvm.x86.sse2.pause")
func llvm_pause()

@inline(never) public func touch(_ p: UnsafeMutablePointer<UInt64>, _ n: Int) -> UInt64 {
    var s: UInt64 = 0
    for i in 0..<n {
        llvm_prefetch(UnsafeRawPointer(p + i + 64), 1, 3, 1)
        s &+= p[i]
    }
    return s
}
@inline(never) public func spin(_ f: UnsafeMutablePointer<Int>) {
    while f.pointee == 0 { llvm_pause() }
}
@main struct M { static func main() {
    let p = UnsafeMutablePointer<UInt64>.allocate(capacity: 4096); p.initialize(repeating: 1, count: 4096)
    let f = UnsafeMutablePointer<Int>.allocate(capacity: 1); f.pointee = 1
    spin(f)
    print(touch(p, 1000))
} }
