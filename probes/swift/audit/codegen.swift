// Code produit, lu par run.sh (swiftc -O -target-cpu native -emit-assembly).
@inline(never) public func idx(_ a: [Float], _ i: Int) -> Float { a[i] }
@inline(never) public func idxu(_ a: [Float], _ i: Int) -> Float { a.withUnsafeBufferPointer { $0[i] } }
@inline(never) public func gsum<T: AdditiveArithmetic>(_ x: [T]) -> T { var s = T.zero; for v in x { s += v }; return s }
public func useBoth(_ a: [Float], _ b: [Double]) -> Double { Double(gsum(a)) + gsum(b) }
