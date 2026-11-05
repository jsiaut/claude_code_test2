public struct Big { public var a: (Int, Int, Int, Int, Int, Int, Int, Int) }
@inline(never) public func inoutInt(_ a: inout Int, _ b: inout Int) { a &+= 1; b &+= 1 }
@inline(never) public func inoutArr(_ a: inout [Float], _ b: inout [Float]) { a[0] += b[0] }
@inline(never) public func inoutBig(_ a: inout Big, _ b: inout Big) { a.a.0 &+= b.a.0 }
@inline(never) public func inoutPtr(_ a: inout UnsafeMutablePointer<Float>, _ b: inout UnsafeMutablePointer<Float>) { a.pointee += b.pointee }
@inline(never) public func rawPtrs(_ a: UnsafeMutablePointer<Float>, _ b: UnsafePointer<Float>, _ n: Int) { for i in 0..<n { a[i] += b[i] } }
