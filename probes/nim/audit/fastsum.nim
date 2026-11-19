# Module compilé avec -ffast-math ({.localPassC.} : option du compilateur C pour ce seul module).
{.localPassC: "-ffast-math".}
proc sum_fast*(a: ptr UncheckedArray[float32], n: int): float32 {.exportc: "sum_fast", noinline.} =
  for i in 0 ..< n: result += a[i]
