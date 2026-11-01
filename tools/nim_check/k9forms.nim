# Formes de K9 naturel (remarque sur Nim) : on compte les instructions vectorielles de chaque procédure.
const M9 = 2048
type Grid = array[M9, array[M9, float]]
proc k9Seq(a: seq[seq[float]], b: var seq[seq[float]]) {.noinline, exportc: "k9Seq".} =
  for i in 1 ..< M9 - 1:
    for j in 1 ..< M9 - 1:
      b[i][j] = 0.25 * (((a[i - 1][j] + a[i + 1][j]) + a[i][j - 1]) + a[i][j + 1])
proc k9Arr(a: ref Grid, b: ref Grid) {.noinline, exportc: "k9Arr".} =
  for i in 1 ..< M9 - 1:
    for j in 1 ..< M9 - 1:
      b[i][j] = 0.25 * (((a[i - 1][j] + a[i + 1][j]) + a[i][j - 1]) + a[i][j + 1])
var s1 = newSeq[seq[float]](M9)
for i in 0 ..< M9: s1[i] = newSeq[float](M9)
var s2 = s1
k9Seq(s1, s2)
var g1, g2: ref Grid
new(g1); new(g2)
k9Arr(g1, g2)
echo s2[1][1] + g2[1][1]
