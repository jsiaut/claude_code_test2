proc sumAttr(v: ptr UncheckedArray[float32], n: int): float32 {.exportc, codegenDecl: "__attribute__((optimize(\"associative-math\",\"no-signed-zeros\",\"no-trapping-math\"))) $# $#$#".} =
  var s = 0'f32
  for i in 0 ..< n: s += v[i]
  s
proc sumPlain(v: ptr UncheckedArray[float32], n: int): float32 {.exportc.} =
  var s = 0'f32
  for i in 0 ..< n: s += v[i]
  s
