// Audit de la grille, Go, B2 : le paquet arena (GOEXPERIMENT=arenas, run.sh).
package main

import (
	"arena"
	"fmt"
	"unsafe"
)

type T struct{ V [50]uint64 }

func main() {
	a := arena.NewArena()
	x, y := arena.New[T](a), arena.New[T](a)
	s := arena.MakeSlice[float64](a, 100, 100)
	d := int64(uintptr(unsafe.Pointer(y))) - int64(uintptr(unsafe.Pointer(x)))
	if d < 0 {
		d = -d
	}
	fmt.Printf("%d %d\n", d, len(s))
	a.Free()
}
