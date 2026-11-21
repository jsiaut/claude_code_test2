# Sonde de mode (v4, point 3 : docs/V4_EQUAL.md, 4) : « 1d » : seq, « 2d » : seq de seq (K9 naturel).
import std/[os, strutils]
let n = parseInt(paramStr(2))
if paramStr(1) == "1d":
  var a = newSeq[float](n)
  for i in 0 ..< n: a[i] = 1.0
  echo a[n]
else:
  var g = newSeq[seq[float]](4)
  for r in g.mitems: r = newSeq[float](n)
  echo g[1][n]
