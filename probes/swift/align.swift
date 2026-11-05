@_alignment(64) struct Al { var v: Int32 = 0 }
print(MemoryLayout<Al>.alignment)
