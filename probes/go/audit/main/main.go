// Audit de la grille, Go 1.27.3 (réglages du banc : GOAMD64=v4) : chaque case est exercée sous sa forme la plus forte
// et imprime un fait observable (docs/V4_PLAN.md 2.1). Lignes FACT (complétées par run.sh avec le code machine des
// fonctions cg*, lu par go tool objdump) et NOTE (contre-épreuves).
package main

import (
	"fmt"
	"math"
	"os"
	"runtime"
	"runtime/debug"
	"strings"
	"sync"
	"sync/atomic"
	"syscall"
	"testing"
	"unsafe"
)

type Particle struct{ X, Y, Z, VX, VY, VZ, AX, AY, AZ, M, Q, R, T, P, E, D float32 }
type S struct {
	A uint8
	B uint32
	C float64
}
type Pk struct {
	A uint8
	B uint32
}
type S64 struct{ V [8]uint64 }
type In struct {
	V [16]float32
	N int32
}
type Pt struct{ X, Y float64 }
type Shape interface{ Area() float64 }

func (p Pt) Area() float64 { return p.X * p.Y }

var sink any
var sinkF float64
var gp *Pt

func fact(c, ev string)  { fmt.Printf("FACT;%s;%s\n", c, ev) }
func note(c, ev string)  { fmt.Printf("NOTE;%s;%s\n", c, ev) }
func numGC() uint32      { var m runtime.MemStats; runtime.ReadMemStats(&m); return m.NumGC }
func heapMiB() uint64    { var m runtime.MemStats; runtime.ReadMemStats(&m); return m.HeapAlloc >> 20 }

// fonctions dont run.sh lit le code machine
//go:noinline
func cgStore(p *atomic.Int32, v int32) { p.Store(v) }
//go:noinline
func cgLoad(p *atomic.Int32) int32 { return p.Load() }
//go:noinline
func cgAdd(p *atomic.Int64) int64 { return p.Add(1) }
//go:noinline
func cgIdx(s []float32, i int) float32 { return s[i] }
//go:noinline
func cgIdxUnsafe(s []float32, i int) float32 {
	return *(*float32)(unsafe.Add(unsafe.Pointer(unsafe.SliceData(s)), uintptr(i)*4))
}
//go:noinline
func cgSumF(s []float64) float64 {
	t := 0.0
	for _, e := range s {
		t += e
	}
	return t
}
//go:noinline
func cgSum[T int | float64](s []T) T {
	var t T
	for _, e := range s {
		t += e
	}
	return t
}
//go:noinline
func cgCount[T any](s []T) int {
	n := 0
	for _, e := range s {
		if any(e) != nil {
			n++
		}
	}
	return n
}

func pairwise(a []float64) float64 {
	if len(a) <= 8 {
		t := 0.0
		for _, e := range a {
			t += e
		}
		return t
	}
	m := len(a) / 2
	return pairwise(a[:m]) + pairwise(a[m:])
}
func axpy(y, x []float32, a float32) {
	for i := range y {
		y[i] += a * x[i]
	}
}
//go:noinline
func local3() float64 { p := Pt{1.5, 2}; q := &p; return q.X * q.Y }
//go:noinline
func escape3() { p := Pt{1.5, 2}; gp = &p }

func main() {
	// ---------- A
	ps := make([]Particle, 1000)
	fact("A1", fmt.Sprintf("[]Particle (struct de 16 float32) : unsafe.Sizeof = %d o, écart entre éléments %d o (valeurs en ligne)",
		unsafe.Sizeof(Particle{}), uintptr(unsafe.Pointer(&ps[1]))-uintptr(unsafe.Pointer(&ps[0]))))
	fact("A2", fmt.Sprintf("unsafe.Offsetof : A=%d B=%d C=%d (ordre déclaré gardé par gc, alignement naturel)",
		unsafe.Offsetof(S{}.A), unsafe.Offsetof(S{}.B), unsafe.Offsetof(S{}.C)))
	fact("A3", fmt.Sprintf("struct {uint8; uint32} : unsafe.Sizeof = %d o (bourrage imposé, aucun attribut packed)", unsafe.Sizeof(Pk{})))
	buf := make([]byte, 256+63)
	al := (uintptr(unsafe.Pointer(&buf[0])) + 63) &^ 63
	fact("A4", fmt.Sprintf("sur-allocation + arrondi d'adresse : %d mod 64 = 0 (à la main) ; pas d'attribut d'alignement : unsafe.Alignof(struct de 64 o) = %d",
		al, unsafe.Alignof(S64{})))
	f := float32(1.0)
	fact("A5", fmt.Sprintf("math.Float32bits(1) = 0x%08x ; *(*uint32)(unsafe.Pointer(&f)) = 0x%08x", math.Float32bits(1), *(*uint32)(unsafe.Pointer(&f))))
	fact("A7", fmt.Sprintf("struct {[16]float32; int32} : unsafe.Sizeof = %d o, N à %d (tableau fixe en ligne)", unsafe.Sizeof(In{}), unsafe.Offsetof(In{}.N)))
	fact("A8", fmt.Sprintf("unsafe.Sizeof : uint8 %d, int16 %d, float32 %d (pas de flottant 16 bits)", unsafe.Sizeof(uint8(0)), unsafe.Sizeof(int16(0)), unsafe.Sizeof(float32(0))))

	// ---------- B
	g0 := numGC()
	for i := 0; i < 1<<20; i++ {
		sink = make([]byte, 1024)
	}
	fact("B1", fmt.Sprintf("1 Gio de tranches de 1 Kio sans référence : %d collectes déclenchées par le runtime, sans appel du programme (ramasse-miettes traçant)", numGC()-g0))
	runtime.GC()
	old := debug.SetGCPercent(-1)
	h0, n0 := heapMiB(), numGC()
	for i := 0; i < 256*1024; i++ {
		sink = make([]byte, 1024)
	}
	h1, n1 := heapMiB(), numGC()
	debug.SetGCPercent(old)
	runtime.GC()
	note("B1", fmt.Sprintf("debug.SetGCPercent(-1) : 256 Mio alloués sans référence, %d collecte, tas vivant %d → %d Mio (rien n'est rendu) ; après SetGCPercent(%d) et runtime.GC : %d Mio", n1-n0, h0, h1, old, heapMiB()))
	a3 := testing.AllocsPerRun(1000, func() { sinkF += local3() })
	e3 := testing.AllocsPerRun(1000, escape3)
	fact("B3", fmt.Sprintf("testing.AllocsPerRun : struct locale dont l'adresse ne sort pas %.0f allocation, la même dont l'adresse est gardée dans une variable globale %.0f (décision de l'analyse d'échappement, go build -gcflags=-m)", a3, e3))
	var sh Shape
	ai := testing.AllocsPerRun(1000, func() { sh = Pt{float64(len(ps)), 2}; sink = sh })
	k := 3
	ac := testing.AllocsPerRun(1000, func() { k++; fn := func() int { return k + 1 }; sink = fn })
	aa := testing.AllocsPerRun(100, func() { var sl []int; for i := 0; i < 1000; i++ { sl = append(sl, i) }; sink = sl })
	am := testing.AllocsPerRun(1000, func() { sinkF += math.Sqrt(sinkF + 2) })
	fact("B4", fmt.Sprintf("testing.AllocsPerRun : arithmétique %.0f ; allocations implicites : struct mise dans une interface %.0f, fermeture qui s'échappe %.0f, 1000 append sur une tranche nil %.0f (croissance)", am, ai, ac, aa))
	b := make([]uint32, 8)
	p := unsafe.Pointer(&b[0])
	*(*uint32)(unsafe.Add(p, 3*4)) = 42
	*(*uint32)(unsafe.Add(p, 16)) = 7
	fact("B5", fmt.Sprintf("unsafe.Pointer + unsafe.Add : b[3] = %d ; écriture par décalage d'octets → b[4] = %d", b[3], b[4]))

	// ---------- C
	dv := make([]float64, 1<<20)
	x := uint64(42)
	for i := range dv {
		x = x*6364136223846793005 + 1442695040888963407
		dv[i] = float64(x>>11)/float64(1<<53) - 0.5
	}
	s := cgSumF(dv)
	pw := pairwise(dv)
	fact("C4", fmt.Sprintf("un million de float64 : boucle compilée %.17g, somme par paires écrite à la main %.17g (écart %.3g) : l'ordre du source est gardé", s, pw, math.Abs(pw-s)))

	// ---------- D
	var cnt atomic.Int64
	var wg sync.WaitGroup
	for t := 0; t < 4; t++ {
		wg.Add(1)
		go func() { defer wg.Done(); for i := 0; i < 1000; i++ { cnt.Add(1) } }()
	}
	wg.Wait()
	fact("D1", fmt.Sprintf("4 goroutines sur %d fils système (GOMAXPROCS) : %d incréments ; runtime.LockOSThread lie une goroutine à son fil", runtime.GOMAXPROCS(0), cnt.Load()))
	var i32 atomic.Int32
	var i64 atomic.Int64
	cgStore(&i32, 5)
	fact("D2", fmt.Sprintf("sync/atomic : Store/Load → %d, Add → %d ; aucune méthode à ordre relâché, acquire ou release", cgLoad(&i32), cgAdd(&i64)))
	runtime.LockOSThread()
	var set [16]uint64
	set[0] = 2
	_, _, e := syscall.RawSyscall(syscall.SYS_SCHED_SETAFFINITY, 0, uintptr(len(set)*8), uintptr(unsafe.Pointer(&set[0])))
	var cpu uint32
	syscall.RawSyscall(309, uintptr(unsafe.Pointer(&cpu)), 0, 0) // getcpu
	fact("D4", fmt.Sprintf("runtime.LockOSThread + syscall.RawSyscall(SYS_SCHED_SETAFFINITY) du paquet syscall livré : errno %d, processeur courant (getcpu) %d ; pas d'API d'affinité", e, cpu))
	runtime.UnlockOSThread()

	// ---------- E
	y := make([]float32, 16)
	for i := range y {
		y[i] = 1
	}
	axpy(y[1:9], y[0:8], 2)
	fact("E5", fmt.Sprintf("axpy(y[1:9], y[0:8], 2) sur des tranches qui se recouvrent : y[8] = %g (chaque écriture relue : le compilateur doit supposer l'alias)", y[8]))
	four := []float32{1, 2, 3, 4}
	msg := "rien"
	func() {
		defer func() { if r := recover(); r != nil { msg = fmt.Sprint(r) } }()
		sinkF += float64(cgIdx(four, 4+len(os.Args)-1))
	}()
	fact("E6", fmt.Sprintf("four[4] : panique « %s » ; unsafe.Add sans contrôle : %g", msg, cgIdxUnsafe(four, 2)))
	type A struct{ v int }
	type B struct{ w float64 }
	fact("E7", fmt.Sprintf("cgSum[int] = %d, cgSum[float64] = %g ; cgCount[*A] = %d, cgCount[*B] = %d", cgSum([]int{1, 2, 3}), cgSum([]float64{0.5, 0.25}),
		cgCount([]*A{{1}, {2}}), cgCount([]*B{{1}, {2}, {3}})))

	// ---------- F
	var g [3][4]float64
	off := uintptr(unsafe.Pointer(&g[2][3])) - uintptr(unsafe.Pointer(&g[0][0]))
	n := 3 + len(os.Args) - 1
	rows := make([][]float64, n)
	for i := range rows {
		rows[i] = make([]float64, 4)
	}
	rows[1] = make([]float64, 7)
	fact("F1", fmt.Sprintf("[3][4]float64 : [2][3] à %d o = élément %d du bloc contigu (tailles constantes) ; dimensions connues à l'exécution : [][]float64, lignes séparées (rows[1] remplacée par une ligne de %d)", off, off/8, len(rows[1])))
	u := uint32(math.MaxUint32)
	u += uint32(len(os.Args)) + 5
	i8 := int8(127)
	i8 += int8(len(os.Args))
	fact("F3", fmt.Sprintf("uint8…uint64, int8…int64 : MaxUint32 + 6 = %d, int8(127) + 1 = %d (enveloppement défini par la spécification)", u, i8))
	fd, _ := os.Open("/opt/msdata/k5_a.f32")
	mm, err := syscall.Mmap(int(fd.Fd()), 0, 8192, syscall.PROT_READ, syscall.MAP_PRIVATE)
	fl := unsafe.Slice((*float32)(unsafe.Pointer(&mm[0])), 2048)
	maps, _ := os.ReadFile("/proc/self/maps")
	fact("F4", fmt.Sprintf("syscall.Mmap du paquet syscall livré + unsafe.Slice : k5_a.f32 projeté (%v, /proc/self/maps), premier float32 %g, dernier %g, erreur %v",
		strings.Contains(string(maps), "/opt/msdata/k5_a.f32"), fl[0], fl[2047], err))
}
