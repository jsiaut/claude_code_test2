// Audit de la grille (docs/V4_PLAN.md 2.1) : compléments exécutés de la sonde de Swift (B2, B5).
@main struct Audit {
    static func main() {
        // B2 (½) : pointeurs bruts ; arène à la main sur UnsafeMutableRawPointer.allocate
        let cap = 4096
        let base = UnsafeMutableRawPointer.allocate(byteCount: cap, alignment: 64)
        var off = 0
        func bump(_ n: Int, _ a: Int) -> UnsafeMutableRawPointer { off = (off + a - 1) & ~(a - 1); defer { off += n }; return base + off }
        let p1 = bump(400, 8), p2 = bump(400, 8)
        print("CAP;B2;0.5;[exécutée] UnsafeMutableRawPointer.allocate + arène à la main : deux blocs à \(p2 - p1) o d'écart dans le même tampon, libérés d'un coup par deallocate ; [recherche] interface d'allocateur : NOTE B2")
        base.deallocate()
        // B5
        let buf = UnsafeMutablePointer<UInt32>.allocate(capacity: 8)
        buf.initialize(repeating: 0, count: 8)
        (buf + 3).pointee = 42
        UnsafeMutableRawPointer(buf).storeBytes(of: 7, toByteOffset: 16, as: UInt32.self)
        print("CAP;B5;1;[exécutée] UnsafeMutablePointer<UInt32> : (p + 3).pointee = 42 -> buf[3] = \(buf[3]) ; écriture par décalage d'octets -> buf[4] = \(buf[4])")
        buf.deallocate()
    }
}
