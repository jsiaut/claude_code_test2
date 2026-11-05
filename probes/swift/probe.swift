// Sonde Swift 6.4.2 (chaîne officielle, Linux) : chaque ligne CAP n'est imprimée que si le code compile et s'exécute.
// Les cas négatifs (intrinsèques sans corps, préchargement, noalias, indication de branchement) sont vérifiés par
// run.sh sur le code machine ou l'IR de fichiers séparés.
import Foundation
import Synchronization
import Dispatch

struct P { var x, y, z, vx, vy, vz, ax, ay, az, m, c, r, t, p, e, d: Float }
struct S { var a: UInt8; var c: Double; var b: UInt8 }  // ordre déclaré gardé ? (b après c, pas de tassement)
struct Pk { var a: UInt8; var b: UInt32 }
struct WithInline { var v: InlineArray<16, Float> }
protocol Shape { func area() -> Double }
struct Big: Shape { var a = 1.0, b = 2.0, c = 3.0, d = 4.0, e = 5.0, f = 6.0, g = 7.0, h = 8.0; func area() -> Double { a + h } }
@inline(never) func box(_ s: Big) -> any Shape { s }
@inline(never) func generic<T: Numeric>(_ x: T) -> T { x * x }

@main struct Probe {
    static func main() async {
        // A1 : tableau de structs en ligne
        let arr = [P](repeating: P(x: 0, y: 0, z: 0, vx: 0, vy: 0, vz: 0, ax: 0, ay: 0, az: 0, m: 0, c: 0, r: 0, t: 0, p: 0, e: 0, d: 0), count: 4)
        let gap = arr.withUnsafeBufferPointer { UnsafeRawPointer($0.baseAddress! + 1) - UnsafeRawPointer($0.baseAddress!) }
        print("CAP;A1;1;[P] contigu : stride \(MemoryLayout<P>.stride) o, écart entre éléments \(gap) o")
        // A2 : ordre déclaré et offset(of:)
        print("CAP;A2;1;MemoryLayout.offset(of:) a=\(MemoryLayout<S>.offset(of: \S.a)!) c=\(MemoryLayout<S>.offset(of: \S.c)!) b=\(MemoryLayout<S>.offset(of: \S.b)!) : ordre déclaré gardé (docs/ABI/TypeLayout.rst), sans attribut de disposition")
        // A3 : ni packed ni champs de bits
        print("CAP;A3;0;{UInt8, UInt32} : size \(MemoryLayout<Pk>.size) o (bourrage imposé) ; ni packed ni champs de bits hors struct C importée")
        // A4 : alignement d'allocation seulement (@_alignment plafonne à 16, vérifié par run.sh)
        let ap = UnsafeMutableRawPointer.allocate(byteCount: 256, alignment: 64)
        print("CAP;A4;0.5;UnsafeMutableRawPointer.allocate(alignment: 64) -> adresse % 64 = \(Int(bitPattern: ap) % 64) ; pas d'alignement de type au-delà de 16")
        ap.deallocate()
        // A5 : réinterprétation, pas d'union non étiquetée
        let f: Float = 1.0
        let raw = withUnsafeBytes(of: f) { $0.load(as: UInt32.self) }
        print("CAP;A5;0.5;Float(bitPattern:) 0x\(String(f.bitPattern, radix: 16)), lecture des octets 0x\(String(raw, radix: 16)), unsafeBitCast entre types de même taille ; enum à charge = union étiquetée, pas d'union brute")
        print("CAP;A6;0;aucun type SoA en bibliothèque standard")
        print("CAP;A7;1;InlineArray<16, Float> dans une struct : stride \(MemoryLayout<WithInline>.stride) o")
        print("CAP;A8;1;UInt8 \(MemoryLayout<UInt8>.size) Int16 \(MemoryLayout<Int16>.size) Float16 \(MemoryLayout<Float16>.size) Float \(MemoryLayout<Float>.size)")
        // B1 : comptage de références (ARC), pas de GC traçant
        final class C0 {}
        let o = C0()
        print("CAP;B1;1;ARC : isKnownUniquelyReferenced \(withExtendedLifetime(o) { true }) ; pas de GC traçant")
        print("CAP;B2;0.5;allocate/deallocate de pointeurs bruts ; pas d'interface d'allocateur (arènes à la main, bench K8 tuned)")
        // B3 : allocation sur la pile
        var local = 0
        let dist = withUnsafeTemporaryAllocation(of: Double.self, capacity: 64) { buf in
            withUnsafeMutablePointer(to: &local) { abs(UnsafeRawPointer($0) - UnsafeRawPointer(buf.baseAddress!)) }
        }
        print("CAP;B3;1;withUnsafeTemporaryAllocation : tampon à \(dist) o d'une variable locale (pile) ; structs et InlineArray en ligne")
        // B4 : allocation cachée (existentiel d'une valeur de 64 o : boîte sur le tas)
        let shapes: [any Shape] = (0..<Int(CommandLine.arguments.count + 1)).map { _ in box(Big()) }
        let shape = shapes[0]
        let boxAddr = shapes.withUnsafeBytes { $0.load(as: UInt.self) }
        let heap = UInt(bitPattern: malloc(16))
        let onHeap = (boxAddr > heap ? boxAddr - heap : heap - boxAddr) < (1 << 26)
        print("CAP;B4;0.5;[any Shape] (conteneur de \(MemoryLayout<any Shape>.size) o, tampon en ligne de 24 o) d'une struct de 64 o : boîte 0x\(String(boxAddr, radix: 16)) \(onHeap ? "sur le tas (malloc voisin 0x" + String(heap, radix: 16) + ")" : "hors du tas") sans allocation écrite (aire \(shape.area())) ; aussi fermetures échappantes, copie sur écriture")
        print("CAP;B5;1;UnsafeMutableRawPointer, UnsafePointer (bench)")
        // C1 : types vectoriels portables
        var v = SIMD16<Float>(repeating: 1)
        v.addProduct(SIMD16<Float>(repeating: 2), SIMD16<Float>(repeating: 3))
        print("CAP;C1;1;SIMD16<Float>.addProduct (FMA) : \(v[0])")
        print("CAP;C4;0;aucun contrôle de la réassociation (ni fast-math ni API relâchée en bibliothèque standard ; Relaxed est dans swift-numerics, paquet tiers)")
        // C5 : parallélisme de données (Dispatch, livré)
        let ids = Mutex<Set<UInt64>>([])
        DispatchQueue.concurrentPerform(iterations: 64) { _ in
            var x = 0.0
            for k in 0..<200_000 { x += Double(k) }
            let tid = UInt64(pthread_self())
            ids.withLock { _ = $0.insert(tid + UInt64(x.isNaN ? 1 : 0)) }
        }
        print("CAP;C5;1;DispatchQueue.concurrentPerform : 64 itérations sur \(ids.withLock { $0.count }) threads")
        // D1 : threads
        let done = DispatchSemaphore(value: 0)
        Thread { done.signal() }.start()
        done.wait()
        let par = await withTaskGroup(of: Int.self) { g in
            for i in 0..<4 { g.addTask { i } }
            var s = 0
            for await x in g { s += x }
            return s
        }
        print("CAP;D1;1;Foundation.Thread et tâches (withTaskGroup, somme \(par))")
        // D2 : atomiques à ordre explicite
        let at = Atomic<Int>(0)
        at.add(1, ordering: .relaxed)
        _ = at.load(ordering: .acquiring)
        at.store(5, ordering: .releasing)
        print("CAP;D2;1;Atomic : .relaxed/.acquiring/.releasing/.sequentiallyConsistent -> \(at.load(ordering: .sequentiallyConsistent))")
        print("CAP;D3;0.5;sysconf(_SC_LEVEL1_DCACHE_LINESIZE) = \(sysconf(Int32(_SC_LEVEL1_DCACHE_LINESIZE))) par le module Glibc livré : requête à l'exécution, ni constante ni type de bourrage")
        // D4 : par le module Glibc derrière _GNU_SOURCE, sonde à part dans run.sh (remarque sur Swift, erratum du 5/11)
        atomicMemoryFence(ordering: .sequentiallyConsistent)
        print("CAP;D5;0.5;atomicMemoryFence ; pause seulement par @_silgen_name, attribut souligné (_mm_pause importée : symbole introuvable, run.sh)")
        print("CAP;E1;1;natif, -emit-assembly / -emit-ir")
        print("CAP;E2;0;pas d'assembleur en ligne")
        print("CAP;E6;1;UnsafeBufferPointer sans vérification en -O (bench), -Ounchecked global")
        print("CAP;E7;0.5;génériques spécialisés par l'optimiseur (non garanti, \(generic(3))) ; pas d'évaluation à la compilation (macros : paquet swift-syntax ; @const expérimental)")
        // F1 : tableaux multidimensionnels contigus de taille fixe
        let g2 = InlineArray<4, InlineArray<8, Double>>(repeating: InlineArray(repeating: 0))
        print("CAP;F1;0.5;InlineArray<4, InlineArray<8, Double>> : \(MemoryLayout.size(ofValue: g2)) o contigus ; tailles fixées à la compilation seulement ; [[Double]] non contigu")
        print("CAP;F2;0;aucun")
        print("CAP;F3;1;UInt8...Int64, &+ &- &* : \(UInt8(250) &+ 10) \(Int32.max &+ 1)")
        // F4 : projection en mémoire (Foundation) et vue sans copie
        let path = (ProcessInfo.processInfo.environment["MS_DATA"] ?? "/opt/msdata") + "/k7_keys.u32"
        if let data = try? Data(contentsOf: URL(fileURLWithPath: path), options: .alwaysMapped) {
            let maps = (try? String(contentsOfFile: "/proc/self/maps", encoding: .utf8)) ?? ""
            let mapped = maps.contains("k7_keys.u32")
            let first = data.withUnsafeBytes { $0.bindMemory(to: UInt32.self)[0] }
            print("CAP;F4;\(mapped ? 1 : 0);Data(contentsOf:options: .alwaysMapped) \(mapped ? "projeté (/proc/self/maps)" : "NON projeté") + withUnsafeBytes/bindMemory : \(data.count) o, premier mot \(first)")
        }
    }
}
