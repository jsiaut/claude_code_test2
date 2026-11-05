import Glibc
@main struct P {
    static func main() {
        var set = cpu_set_t()
        // CPU_ZERO / CPU_SET sont des macros C : on écrit le masque à la main (bit 1 = CPU 1)
        withUnsafeMutableBytes(of: &set) { b in for i in 0..<b.count { b[i] = 0 }; b[0] = 0b10 }
        let r = sched_setaffinity(0, MemoryLayout<cpu_set_t>.size, &set)
        print("sched_setaffinity ->", r, "sched_getcpu ->", sched_getcpu())
        var set2 = cpu_set_t()
        withUnsafeMutableBytes(of: &set2) { b in for i in 0..<b.count { b[i] = 0 }; b[0] = 0b100 }
        let r2 = pthread_setaffinity_np(pthread_self(), MemoryLayout<cpu_set_t>.size, &set2)
        print("pthread_setaffinity_np ->", r2, "sched_getcpu ->", sched_getcpu(), "gettid ->", gettid())
    }
}
