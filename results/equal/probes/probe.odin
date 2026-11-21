// Sonde de mode (v4, point 3 : docs/V4_EQUAL.md, 4) : « 1d » : tranche allouée, « 2d » : ^[4][M]f64 (comme k9_natural).
package main
import "core:fmt"
import "core:os"
import "core:strconv"
M :: 64
main :: proc() {
	n, _ := strconv.parse_int(os.args[2])
	if os.args[1] == "1d" {
		a := make([]f64, n)
		for i in 0 ..< n do a[i] = 1
		fmt.println(a[n])
	} else {
		g := new([4][M]f64)
		for i in 0 ..< 4 do for j in 0 ..< M do g[i][j] = 1
		fmt.println(g[1][n])
	}
}
