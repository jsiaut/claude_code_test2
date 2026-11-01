{.localPassC: "-ffast-math".}
proc dot(a, b: seq[float32]): float32 {.noinline, exportc: "dotLp".} =
  for i in 0 ..< a.len: result += a[i] * b[i]
echo dot(@[1'f32, 2], @[3'f32, 4])
