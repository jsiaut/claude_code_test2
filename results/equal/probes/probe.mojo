# Sonde de mode (v4, point 3 : docs/V4_EQUAL.md, 4) : « 1d » : List, « 2d » : List de List (K9 naturel).
from std.sys import argv
def main() raises:
    var args = argv()
    var n = Int(String(args[2]))
    if String(args[1]) == "1d":
        var a = List[Float64](length=n, fill=1.0)
        print(a[n])
    else:
        var g = List[List[Float64]]()
        for _ in range(4):
            g.append(List[Float64](length=n, fill=1.0))
        print(g[1][n])
