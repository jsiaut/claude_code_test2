import std/strutils
var gs {.exportc: "gs".}: float
proc work(n: int): float =
  gs = 0.0
  for i in `||`(0, n - 1, "parallel for reduction(+:gs)"):
    gs += 1.0 / float(1 + i)
  result = gs
proc nthreads(): cint {.importc: "omp_get_max_threads", header: "omp.h".}
echo "omp ||: ", formatFloat(work(100_000_000), ffDecimal, 3), " max_threads=", nthreads()
