# Contre-épreuve B2 : régions (MemRegion, withRegion), seulement sous --mm:regions (mode mémoire global, livré).
var r: MemRegion
withRegion(r):
  var s = newSeq[int](100)
  s[0] = 1
  echo s[0]
