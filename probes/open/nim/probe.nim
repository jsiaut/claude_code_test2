# v4, point 6 (docs/V4_OPEN.md, 4) : sondes de la grille ouverte de Nim (C1 : mmops 0.1.1 ; F1 : arraymancer 0.7.33).
import std/strformat
import mmops
import arraymancer

proc c1dot(a, b: ptr UncheckedArray[float32], n: int): float32 {.exportc: "c1dot", noinline.} =
  var acc = splat(0.0'f32)
  var i = 0
  while i + 8 <= n:
    let va = load(cast[ptr array[8, float32]](addr a[i])[])
    let vb = load(cast[ptr array[8, float32]](addr b[i])[])
    acc = fma(va, vb, acc)
    i += 8
  result = acc.sum

proc c1() =
  var a = newSeq[float32](4096)
  var b = newSeq[float32](4096)
  for i in 0 ..< 4096:
    a[i] = float32(i mod 7)
    b[i] = float32(i mod 5)
  let d = c1dot(cast[ptr UncheckedArray[float32]](addr a[0]), cast[ptr UncheckedArray[float32]](addr b[0]), 4096)
  var want = 0.0'f32
  for i in 0 ..< 4096: want += a[i] * b[i]
  let v = splat(2.0'f32) * splat(3.0'f32) + splat(1.0'f32)
  echo &"RESULT;C1;mmops;Mm[8, float32] (load, fma, sum) : produit scalaire de 4096 = {d} (somme scalaire {want}) ; splat(2)*splat(3)+splat(1) = {v.toArray}"

proc f1() =
  let m = 300
  let n = 500
  var t = zeros[float64](m, n)
  t[2, 3] = 7.0
  let base = cast[uint](t.toUnsafeView())
  let off = (cast[uint](unsafeAddr t.unsafe_raw_offset()[2 * n + 3]) - base) div 8
  echo &"RESULT;F1;arraymancer;zeros[float64]({m}, {n}) de dimensions connues à l'exécution : shape {t.shape}, strides {t.strides}, is_C_contiguous = {t.is_C_contiguous}, t[2, 3] = {t[2, 3]} lu à l'indice {off} du tampon contigu (2*{n}+3)"

c1()
f1()
