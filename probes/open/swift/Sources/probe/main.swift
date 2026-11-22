// v4, point 6 (docs/V4_OPEN.md, 4) : sondes de la grille ouverte de Swift.
import Memory
import Memory_Allocator_Arena
import Matft

// ---------------------------------------------------------------- B2 : arène de swift-memory-allocation
struct Node {
  var v: Int64
  var l: UnsafeMutablePointer<Node>?
  var r: UnsafeMutablePointer<Node>?
}

func count(_ n: Int) -> Memory.Address.Count { Memory.Address.Count(_unchecked: Cardinal(UInt(n))) }

func b2() throws {
  let heap = Memory.Heap(byteCount: count(1 << 20), alignment: try Memory.Alignment(64))
  var arena = Memory.Allocator<Memory.Heap>.Arena(heap)
  let align = try Memory.Alignment(MemoryLayout<Node>.alignment)
  var prev: UnsafeMutablePointer<Node>? = nil
  var addrs: [UInt] = []
  for i in 0..<1000 {
    let a = try arena.allocate(count: count(MemoryLayout<Node>.stride), alignment: align)
    let p = a.mutablePointer.bindMemory(to: Node.self, capacity: 1)
    p.initialize(to: Node(v: Int64(i), l: prev, r: nil))
    addrs.append(UInt(bitPattern: p))
    prev = p
  }
  var s: Int64 = 0
  var q = prev
  while let n = q { s += n.pointee.v + (n.pointee.r?.pointee.v ?? 0); q = n.pointee.l }
  let deltas = Set(zip(addrs.dropFirst(), addrs).map { Int(bitPattern: $0) - Int(bitPattern: $1) })
  let used = arena.allocated.underlying.rawValue
  arena.reset()
  let again = try arena.allocate(count: count(MemoryLayout<Node>.stride), alignment: align)
  print("RESULT;B2;swift-memory-allocation;Memory.Allocator<Memory.Heap>.Arena : 1000 allocate(count:alignment:) de \(MemoryLayout<Node>.stride) octets, liés à Node (valeur, deux liens) par bindMemory : écarts d'adresse \(deltas.sorted()), somme en suivant les liens = \(s) ; allocated = \(used) ; après reset(), la première adresse revient = \(again.bitPattern == addrs[0])")
}

// ---------------------------------------------------------------- F1 : Matft
func f1() {
  let m = Int(CommandLine.arguments.count) * 300
  let n = 500
  let a = Matft.nums(0.0, shape: [m, n], mftype: .Double)
  a[2, 3] = MfArray([7.0])
  let flat = a.toFlattenArray(datatype: Double.self, { $0 })
  let idx = flat.firstIndex(of: 7.0) ?? -1
  print("RESULT;F1;Matft;Matft.nums(0, shape: [\(m), \(n)]) de dimensions connues à l'exécution : shape \(a.shape), strides \(a.strides), size \(a.size), a[2, 3] = 7 à l'indice \(idx) du tampon aplati (2*\(n)+3)")
}

try b2()
f1()
