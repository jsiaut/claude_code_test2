// Audit de la grille, Go, C1 et C2 : paquets simd (portable) et simd/archsimd (GOEXPERIMENT=simd, run.sh).
package main

import (
	"fmt"
	"simd"
	"simd/archsimd"
)

//go:noinline
func cgPortable(a, b, c []float32) float32 {
	v := simd.LoadFloat32s(a).MulAdd(simd.LoadFloat32s(b), simd.LoadFloat32s(c))
	out := make([]float32, len(a))
	v.Store(out)
	return out[0]
}

//go:noinline
func cgArch(a, b []float32) float32 {
	v := archsimd.LoadFloat32x16(a).Add(archsimd.LoadFloat32x16(b))
	out := make([]float32, 16)
	v.Store(out)
	return out[0]
}

func main() {
	a, b, c := make([]float32, 16), make([]float32, 16), make([]float32, 16)
	for i := range a {
		a[i], b[i], c[i] = 2, 3, 1
	}
	fmt.Printf("%d %g %g\n", simd.VectorBitSize(), cgPortable(a, b, c), cgArch(a, b))
}
