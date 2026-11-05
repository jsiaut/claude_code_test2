import Glibc
struct UNode: ~Copyable {
    var v: Int64
    var l: UniqueBox<UNode>?
    var r: UniqueBox<UNode>?
    DEINIT
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
@main struct M { static func main() {
    var t = timespec(); clock_gettime(CLOCK_MONOTONIC, &t)
    let t0 = Double(t.tv_sec) + Double(t.tv_nsec) * 1e-9
    var total: Int64 = 0
    for q in 0..<16384 {
        var c = Int64(q)
        let tree = uBuild(10, &c)
        total += uSum(tree.value)
    }
    clock_gettime(CLOCK_MONOTONIC, &t)
    let t1 = Double(t.tv_sec) + Double(t.tv_nsec) * 1e-9
    let dt: Double = t1 - t0
    print("UniqueBox K8:", total, dt, "s")
} }
