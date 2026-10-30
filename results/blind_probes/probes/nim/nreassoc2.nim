{.localPassC: "-fassociative-math -fno-signed-zeros -fno-trapping-math".}
proc sumMod(v: ptr UncheckedArray[float32], n: int): float32 {.exportc.} =
  var s = 0'f32
  for i in 0 ..< n: s += v[i]
  s
