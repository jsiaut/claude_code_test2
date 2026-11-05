@specialized(where T == Int)
@specialized(where T == Double)
@inline(never) public func sum<T: AdditiveArithmetic>(_ a: [T]) -> T { var s = T.zero; for x in a { s += x }; return s }
@inline(always) public func twice(_ x: Int) -> Int { x &* 2 }
