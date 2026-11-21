// Sonde de mode (v4, point 3 : docs/V4_EQUAL.md, 4) : « 1d » : [Double], « 2d » : [[Double]] (K9 naturel).
let args = CommandLine.arguments
let n = Int(args[2])!
if args[1] == "1d" {
    let a = [Double](repeating: 1, count: n)
    print(a[n])
} else {
    let g = [[Double]](repeating: [Double](repeating: 1, count: n), count: 4)
    print(g[1][n])
}
