// Sonde de mode (v4, point 3 : docs/V4_EQUAL.md, 4) : « 1d » : tranche, « 2d » : tranche de tranches (K9 naturel).
package main

import (
	"fmt"
	"os"
	"strconv"
)

func main() {
	n, _ := strconv.Atoi(os.Args[2])
	if os.Args[1] == "1d" {
		a := make([]float64, n)
		fmt.Println(a[n])
	} else {
		g := make([][]float64, 4)
		for i := range g {
			g[i] = make([]float64, n)
		}
		fmt.Println(g[1][n])
	}
}
