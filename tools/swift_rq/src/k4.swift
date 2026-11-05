@inline(never) public func k4Checked(_ v: [UInt8]) -> UInt64 { var s: UInt64 = 0; for x in v { if x >= 128 { s += UInt64(x) } }; return s }
@inline(never) public func k4Wrapping(_ v: [UInt8]) -> UInt64 { var s: UInt64 = 0; for x in v { if x >= 128 { s &+= UInt64(x) } }; return s }
