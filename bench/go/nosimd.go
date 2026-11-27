//go:build !goexperiment.simd

// Binaire standard de l'implémentation Go (sans GOEXPERIMENT=simd) : les fonctions à SIMD explicite de simd.go n'y
// existent pas. Le lanceur (run) envoie les variantes qui les appellent au binaire ms ; atteindre un bouchon est une
// erreur du lanceur.
package main

func noSimd() {
	panic("variante à SIMD explicite appelée dans le binaire standard (bench/go/run)")
}
func k1SoA(vx, vy, vz, m []float32) float64     { noSimd(); return 0 }
func k4Tuned(v []byte) uint64                   { noSimd(); return 0 }
func k5Tuned(a, b []float32) float32            { noSimd(); return 0 }
func k5TunedR(a, b []float32) float32           { noSimd(); return 0 }
func q6Tuned(c *Cols, lo, hi int) int64         { noSimd(); return 0 }
func q1OnePass(c *Cols, lo, hi int, acc *Q1Acc) { noSimd() }
func k9RowsVec(in, out []float64, r0, r1 int)   { noSimd() }
