// v4, point 6 (docs/V4_OPEN.md, 4) : sondes de la grille ouverte de Go
// (C5 : samber/lo/parallel ; D3 : templexxx/cpu ; F1 : gonum/mat ; F2 : benjojo/numa).
package main

import (
	"fmt"
	"os"
	"runtime"
	"sync"
	"syscall"
	"unsafe"

	"github.com/benjojo/numa"
	"github.com/samber/lo/parallel"
	"github.com/templexxx/cpu"
	"gonum.org/v1/gonum/mat"
)

func c5() {
	chunks := make([]int, 4)
	var mu sync.Mutex
	tids := map[int]bool{}
	sums := parallel.Map(chunks, func(_ int, i int) int64 {
		runtime.LockOSThread()
		defer runtime.UnlockOSThread()
		var s int64
		for k := int64(i)*10000000 + 1; k <= int64(i+1)*10000000; k++ {
			s += k
		}
		mu.Lock()
		tids[syscall.Gettid()] = true
		mu.Unlock()
		return s
	})
	var t int64
	for _, s := range sums {
		t += s
	}
	fmt.Printf("RESULT;C5;lo/parallel;parallel.Map sur 4 éléments (une goroutine par élément) : somme = %d (attendu 800000020000000), %d fils système distincts ; aucune réduction ni découpage en tranches dans le paquet\n", t, len(tids))
}

type padded struct {
	v uint64
	_ [cpu.CacheLineSize - 8]byte
}

func d3() {
	var a [4]padded
	off := uintptr(unsafe.Pointer(&a[1])) - uintptr(unsafe.Pointer(&a[0]))
	fmt.Printf("RESULT;D3;templexxx/cpu;cpu.CacheLineSize = %d (constante par architecture) ; compteur bourré [cpu.CacheLineSize-8]byte : unsafe.Sizeof = %d, écart entre deux compteurs = %d octets\n", cpu.CacheLineSize, unsafe.Sizeof(a[0]), off)
}

func f1() {
	m, n := len(os.Args)*300, 500
	a := mat.NewDense(m, n, nil)
	a.Set(2, 3, 7)
	raw := a.RawMatrix()
	idx := -1
	for i, v := range raw.Data {
		if v == 7 {
			idx = i
		}
	}
	r, c := a.Dims()
	fmt.Printf("RESULT;F1;gonum/mat;mat.NewDense(%d, %d, nil) de dimensions connues à l'exécution : Dims = (%d, %d), RawMatrix().Stride = %d, len(Data) = %d (tampon contigu), a.At(2, 3) = %g à l'indice %d (2*%d+3)\n", m, n, r, c, raw.Stride, len(raw.Data), a.At(2, 3), idx, n)
}

func f2() {
	runtime.LockOSThread()
	defer runtime.UnlockOSThread()
	ok := numa.Available()
	err := numa.RunOnNode(0)
	cpuid, node := numa.GetCPUAndNode()
	mask := numa.NewBitmask(numa.NodePossibleCount())
	mask.Set(0, true)
	err2 := numa.SetMemPolicy(numa.MPOL_BIND, mask)
	got := numa.NewBitmask(numa.NodePossibleCount())
	mode, err3 := numa.GetMemPolicy(got, nil, 0)
	fmt.Printf("RESULT;F2;benjojo/numa;Available = %v, NodeCount = %d ; RunOnNode(0) : erreur %v, fil sur le CPU %d du nœud %d ; SetMemPolicy(MPOL_BIND, {0}) : erreur %v ; GetMemPolicy relu : mode %d (MPOL_BIND = %d), nœuds %v, erreur %v\n",
		ok, numa.NodeCount(), err, cpuid, node, err2, mode, numa.MPOL_BIND, got.OnesCount(), err3)
}

func main() {
	c5()
	d3()
	f1()
	f2()
}
