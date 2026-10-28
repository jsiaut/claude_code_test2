// Implémentation Go 1.27 (bibliothèque standard ; GOEXPERIMENT=simd pour simd/archsimd).
package main

import (
	"fmt"
	"os"
	"runtime"
	"simd/archsimd"
	"slices"
	"strconv"
	"sync"
	"sync/atomic"
	"time"
	"unsafe"
)

// ------------------------------------------------------------------ harnais
func dataPath(name string) string {
	d := os.Getenv("MS_DATA")
	if d == "" {
		d = "/opt/msdata"
	}
	return d + "/" + name
}
func loadBytes(name string) []byte {
	b, err := os.ReadFile(dataPath(name))
	if err != nil {
		panic(err)
	}
	return b
}

// réinterprétation sans copie (les gros tampons Go sont alignés sur la page)
func loadAs[T any](name string) []T {
	b := loadBytes(name)
	var z T
	return unsafe.Slice((*T)(unsafe.Pointer(&b[0])), len(b)/int(unsafe.Sizeof(z)))
}
func warmup() int {
	if w, err := strconv.Atoi(os.Getenv("WARMUP")); err == nil {
		return w
	}
	return 1
}
func result(k, v, p string, rep int, sec float64, chk string) {
	fmt.Printf("RESULT;%s;%s;%s;%d;%.9f;%s\n", k, v, p, rep, sec, chk)
}
func bench(k, v, p string, reps int, f func() string) {
	for r := -warmup(); r < reps; r++ {
		t0 := time.Now()
		chk := f()
		dt := time.Since(t0).Seconds()
		if r >= 0 {
			result(k, v, p, r, dt, chk)
		}
	}
}

// ------------------------------------------------------------------ K1
const N1 = 1 << 22

type Particle struct {
	X, Y, Z, Vx, Vy, Vz, Ax, Ay, Az, Mass, Charge, Radius, Temp, Pressure, Energy, Density float32
}

//go:noinline
func k1Natural(ps []Particle) float64 {
	e := 0.0
	for _, p := range ps {
		e += 0.5 * float64(p.Mass) * float64(p.Vx*p.Vx+p.Vy*p.Vy+p.Vz*p.Vz)
	}
	return e
}

//go:noinline
func k1AoS(ps []Particle) float64 {
	var acc [8]float64
	for i := 0; i+8 <= len(ps); i += 8 {
		c := ps[i : i+8 : i+8]
		for k := range 8 {
			q := &c[k]
			acc[k] += float64(0.5 * q.Mass * (q.Vx*q.Vx + q.Vy*q.Vy + q.Vz*q.Vz))
		}
	}
	e := 0.0
	for _, a := range acc {
		e += a
	}
	return e
}

//go:noinline
func k1SoA(vx, vy, vz, m []float32) float64 {
	a0 := archsimd.BroadcastFloat64x8(0)
	a1 := a0
	h := archsimd.BroadcastFloat32x16(0.5)
	for i := 0; i+16 <= len(vx); i += 16 {
		x := archsimd.LoadFloat32x16(vx[i : i+16])
		y := archsimd.LoadFloat32x16(vy[i : i+16])
		z := archsimd.LoadFloat32x16(vz[i : i+16])
		w := archsimd.LoadFloat32x16(m[i : i+16])
		v2 := z.MulAdd(z, y.MulAdd(y, x.Mul(x)))
		e := h.Mul(w).Mul(v2)
		a0 = a0.Add(e.GetLo().ConvertToFloat64())
		a1 = a1.Add(e.GetHi().ConvertToFloat64())
	}
	var t [8]float64
	a0.Add(a1).StoreArray(&t)
	s := 0.0
	for _, x := range t {
		s += x
	}
	return s
}

func runK1(v string, reps int) {
	if v == "footprint0" {
		result("k1", v, "energy", 0, 0, "0")
		return
	}
	raw := loadAs[float32]("k1_particles.f32")
	ps := make([]Particle, N1)
	for i := range ps {
		f := raw[16*i : 16*i+16]
		ps[i] = Particle{f[0], f[1], f[2], f[3], f[4], f[5], f[6], f[7], f[8], f[9], f[10], f[11], f[12], f[13], f[14], f[15]}
	}
	switch v {
	case "footprint":
		raw = nil
		runtime.GC()
		result("k1", v, "energy", 0, 0, fmt.Sprintf("%.6f", k1Natural(ps)))
	case "soa":
		col := func(k int) []float32 {
			c := make([]float32, N1)
			for i := range c {
				c[i] = raw[16*i+k]
			}
			return c
		}
		vx, vy, vz, m := col(3), col(4), col(5), col(9)
		ps, raw = nil, nil
		bench("k1", v, "energy", reps, func() string { return fmt.Sprintf("%.6f", k1SoA(vx, vy, vz, m)) })
	case "aos":
		bench("k1", v, "energy", reps, func() string { return fmt.Sprintf("%.6f", k1AoS(ps)) })
	default:
		if v == "natural_shuffled" {
			perm := loadAs[uint32]("k1_perm.u32")
			s := make([]Particle, N1)
			for j, p := range perm {
				s[j] = ps[p]
			}
			ps = s
		}
		bench("k1", v, "energy", reps, func() string { return fmt.Sprintf("%.6f", k1Natural(ps)) })
	}
}

// ------------------------------------------------------------------ K2
//
//go:noinline
func k2Chase(a []uint32, h int) uint32 {
	i := uint32(0)
	for range h {
		i = a[i]
	}
	return i
}
func runK2(v string, reps int, p string) {
	a := loadAs[uint32]("k2_chase_" + p + ".u32")
	bench("k2", v, p, reps, func() string { return strconv.FormatUint(uint64(k2Chase(a, 4200000)), 10) })
}

// ------------------------------------------------------------------ K3
const ITER3 = 1 << 25

type padded struct {
	v atomic.Uint64
	_ [120]byte
}

func runK3(v string, reps int) {
	rmw := v[:3] == "rmw"
	if rmw {
		fmt.Println("META;k3_mechanism;atomic.Uint64.Add (lock xadd)")
	} else {
		fmt.Println("META;k3_mechanism;atomic.Uint64 Load + Store (Store = XCHG séquentiellement cohérent : Go n'offre pas d'ordre relaxed)")
	}
	var packed [4]atomic.Uint64
	var pad [4]padded
	ctr := make([]*atomic.Uint64, 4)
	for t := range 4 {
		if v[len(v)-6:] == "padded" {
			ctr[t] = &pad[t].v
		} else {
			ctr[t] = &packed[t]
		}
	}
	bench("k3", v, "4x2^25", reps, func() string {
		var wg sync.WaitGroup
		for _, c := range ctr {
			c.Store(0)
			wg.Add(1)
			go func() {
				defer wg.Done()
				if rmw {
					for range ITER3 {
						c.Add(1)
					}
				} else {
					for range ITER3 {
						c.Store(c.Load() + 1)
					}
				}
			}()
		}
		wg.Wait()
		s := uint64(0)
		for _, c := range ctr {
			s += c.Load()
		}
		return strconv.FormatUint(s, 10)
	})
}

// ------------------------------------------------------------------ K4
//
//go:noinline
func k4Natural(v []byte) uint64 {
	s := uint64(0)
	for _, x := range v {
		if x >= 128 {
			s += uint64(x)
		}
	}
	return s
}

//go:noinline
func k4Branchless(v []byte) uint64 {
	s := uint64(0)
	for _, x := range v {
		s += uint64(x) * uint64(x>>7)
	}
	return s
}
func runK4(v string, reps int) {
	d := loadBytes("k4_bytes.u8")
	if v == "natural_sorted" {
		slices.Sort(d)
	}
	bench("k4", v, "16M", reps, func() string {
		if v == "branchless_unsorted" {
			return strconv.FormatUint(k4Branchless(d), 10)
		}
		return strconv.FormatUint(k4Natural(d), 10)
	})
}

// ------------------------------------------------------------------ K5
const INNER5 = 1 << 16

//go:noinline
func k5Natural(a, b []float32) float32 {
	s := float32(0)
	for i := range a {
		s += a[i] * b[i]
	}
	return s
}

//go:noinline
func k5Tuned(a, b []float32) float32 {
	z := archsimd.BroadcastFloat32x16(0)
	s0, s1, s2, s3 := z, z, z, z
	for i := 0; i+64 <= len(a); i += 64 {
		s0 = archsimd.LoadFloat32x16(a[i:i+16]).MulAdd(archsimd.LoadFloat32x16(b[i:i+16]), s0)
		s1 = archsimd.LoadFloat32x16(a[i+16:i+32]).MulAdd(archsimd.LoadFloat32x16(b[i+16:i+32]), s1)
		s2 = archsimd.LoadFloat32x16(a[i+32:i+48]).MulAdd(archsimd.LoadFloat32x16(b[i+32:i+48]), s2)
		s3 = archsimd.LoadFloat32x16(a[i+48:i+64]).MulAdd(archsimd.LoadFloat32x16(b[i+48:i+64]), s3)
	}
	var t [16]float32
	s0.Add(s1).Add(s2.Add(s3)).StoreArray(&t)
	r := float32(0)
	for _, x := range t {
		r += x
	}
	return r
}

var sink []float32

func runK5(v string, reps int) {
	a := loadAs[float32]("k5_a.f32")
	b := loadAs[float32]("k5_b.f32")
	bench("k5", v, "2048x65536", reps, func() string {
		d := float32(0)
		for range INNER5 {
			sink = a // barrière : a s'échappe vers une globale
			if v == "tuned" {
				d = k5Tuned(sink, b)
			} else {
				d = k5Natural(sink, b)
			}
		}
		return fmt.Sprintf("%.4f", d)
	})
}

// ------------------------------------------------------------------ K6
const N6 = 1 << 24

type Cols struct {
	sd, pr          []int32
	q, d, t, rf, ls []uint8
}
type Q1Acc [6][5]int64

//go:noinline
func q6Natural(c *Cols, lo, hi int) int64 {
	s := int64(0)
	for i := lo; i < hi; i++ {
		if c.sd[i] >= 8766 && c.sd[i] < 9131 && c.d[i] >= 5 && c.d[i] <= 7 && c.q[i] < 24 {
			s += int64(c.pr[i]) * int64(c.d[i])
		}
	}
	return s
}

// Q6 optimisé : archsimd AVX-512, 16 lignes par itération, prédicat sous forme de masques
//
//go:noinline
func q6Tuned(c *Cols, lo, hi int) int64 {
	lo8766, hi9131 := archsimd.BroadcastInt32x16(8766), archsimd.BroadcastInt32x16(9131)
	c5, c7, c24 := archsimd.BroadcastInt32x16(5), archsimd.BroadcastInt32x16(7), archsimd.BroadcastInt32x16(24)
	acc := archsimd.BroadcastInt64x8(0)
	i := lo
	for ; i+16 <= hi; i += 16 {
		sd := archsimd.LoadInt32x16(c.sd[i : i+16])
		d := archsimd.LoadUint8x16(c.d[i : i+16]).ExtendToUint32().AsInt32x16()
		q := archsimd.LoadUint8x16(c.q[i : i+16]).ExtendToUint32().AsInt32x16()
		m := sd.GreaterEqual(lo8766).And(sd.Less(hi9131)).And(d.GreaterEqual(c5)).And(d.LessEqual(c7)).And(q.Less(c24))
		p := archsimd.LoadInt32x16(c.pr[i : i+16]).Mul(d).Masked(m)
		acc = acc.Add(p.GetLo().ExtendToInt64()).Add(p.GetHi().ExtendToInt64())
	}
	var t [8]int64
	acc.StoreArray(&t)
	s := int64(0)
	for _, x := range t {
		s += x
	}
	return s + q6Natural(c, i, hi)
}

//go:noinline
func q1Natural(c *Cols, lo, hi int, acc *Q1Acc) {
	for i := lo; i < hi; i++ {
		if c.sd[i] <= 10471 {
			g := c.rf[i]*2 + c.ls[i]
			p := int64(c.pr[i])
			dp := p * (100 - int64(c.d[i]))
			acc[g][0]++
			acc[g][1] += int64(c.q[i])
			acc[g][2] += p
			acc[g][3] += dp
			acc[g][4] += dp * (100 + int64(c.t[i]))
		}
	}
}

// Q1 optimisé : sans branchement, 4 jeux d'accumulateurs pour casser les dépendances
// mémoire entre lignes consécutives du même groupe ; groupe 6 = ligne rejetée.
//
//go:noinline
func q1Tuned(c *Cols, lo, hi int, acc *Q1Acc) {
	var a [4][7][5]int64
	sd, pr, q, d, t, rf, ls := c.sd[lo:hi], c.pr[lo:hi], c.q[lo:hi], c.d[lo:hi], c.t[lo:hi], c.rf[lo:hi], c.ls[lo:hi]
	n := len(sd)
	pr, q, d, t, rf, ls = pr[:n], q[:n], d[:n], t[:n], rf[:n], ls[:n]
	for i := range n {
		pass := int32(uint32(10471-sd[i]) >> 31) // 1 si sd > 10471
		g := int32(rf[i])*2 + int32(ls[i])
		g += (6 - g) * pass
		p := int64(pr[i])
		dp := p * (100 - int64(d[i]))
		r := &a[i&3][g]
		r[0]++
		r[1] += int64(q[i])
		r[2] += p
		r[3] += dp
		r[4] += dp * (100 + int64(t[i]))
	}
	for k := range 4 {
		for g := range 6 {
			for j := range 5 {
				acc[g][j] += a[k][g][j]
			}
		}
	}
}
func fold(a *Q1Acc) int64 {
	s := int64(0)
	for g := range 6 {
		for j := range 5 {
			s += a[g][j]
		}
	}
	return s
}
func runK6(v string, reps int, p string) {
	c := &Cols{loadAs[int32]("k6_shipdate.i32"), loadAs[int32]("k6_extendedprice.i32"), loadBytes("k6_quantity.u8"),
		loadBytes("k6_discount.u8"), loadBytes("k6_tax.u8"), loadBytes("k6_returnflag.u8"), loadBytes("k6_linestatus.u8")}
	q1 := p == "q1"
	bench("k6", v, p, reps, func() string {
		var s int64
		switch {
		case v == "natural" && !q1:
			s = q6Natural(c, 0, N6)
		case v == "natural":
			var a Q1Acc
			q1Natural(c, 0, N6, &a)
			s = fold(&a)
		case v == "tuned" && !q1:
			s = q6Tuned(c, 0, N6)
		case v == "tuned":
			var a Q1Acc
			q1Tuned(c, 0, N6, &a)
			s = fold(&a)
		default:
			var wg sync.WaitGroup
			part := make([]int64, 4)
			for t := range 4 {
				wg.Add(1)
				go func() {
					defer wg.Done()
					lo, hi := N6*t/4, N6*(t+1)/4
					if q1 {
						var a Q1Acc
						q1Tuned(c, lo, hi, &a)
						part[t] = fold(&a)
					} else {
						part[t] = q6Tuned(c, lo, hi)
					}
				}()
			}
			wg.Wait()
			for _, x := range part {
				s += x
			}
		}
		return strconv.FormatInt(s, 10)
	})
}

// ------------------------------------------------------------------ K7
type agg struct {
	count uint32
	sum   uint64
}
type slot struct {
	key, count uint32
	sum        uint64
}

func runK7(v string, reps int) {
	keys := loadAs[uint32]("k7_keys.u32")
	vals := loadAs[uint32]("k7_vals.u32")
	for r := -warmup(); r < reps; r++ {
		var dt float64
		var nk, ws uint64
		if v == "natural" {
			t0 := time.Now()
			m := make(map[uint32]agg)
			for i, k := range keys {
				e := m[k]
				e.count++
				e.sum += uint64(vals[i])
				m[k] = e
			}
			dt = time.Since(t0).Seconds()
			nk = uint64(len(m))
			for k, e := range m {
				ws += e.sum * uint64(k&1023+1)
			}
		} else {
			const LOG = 21
			const CAP = 1 << LOG
			t0 := time.Now()
			tab := make([]slot, CAP)
			for i, k := range keys {
				s := (k * 0x9E3779B1) >> (32 - LOG)
				for tab[s].count != 0 && tab[s].key != k {
					s = (s + 1) & (CAP - 1)
				}
				e := &tab[s]
				e.key = k
				e.count++
				e.sum += uint64(vals[i])
			}
			dt = time.Since(t0).Seconds()
			for _, e := range tab {
				if e.count != 0 {
					nk++
					ws += e.sum * uint64(e.key&1023+1)
				}
			}
		}
		if r >= 0 {
			result("k7", v, "16M/1M", r, dt, fmt.Sprintf("%d:%d", nk, ws))
		}
	}
}

// ------------------------------------------------------------------ K8
type Node struct {
	v    int64
	l, r *Node
}

func tBuild(d int, c *int64) *Node {
	n := &Node{v: *c}
	*c++
	if d > 0 {
		n.l = tBuild(d-1, c)
		n.r = tBuild(d-1, c)
	}
	return n
}
func tSum(n *Node) int64 {
	if n == nil {
		return 0
	}
	return n.v + tSum(n.l) + tSum(n.r)
}

type ANode struct {
	v    int64
	l, r int32
}

func aBuild(a *[]ANode, d int, c *int64) int32 {
	i := int32(len(*a))
	*a = append(*a, ANode{*c, -1, -1})
	*c++
	if d > 0 {
		l := aBuild(a, d-1, c)
		r := aBuild(a, d-1, c)
		(*a)[i].l, (*a)[i].r = l, r
	}
	return i
}
func aSum(a []ANode, i int32) int64 {
	if i < 0 {
		return 0
	}
	n := a[i]
	return n.v + aSum(a, n.l) + aSum(a, n.r)
}

var keepAlive *Node

func runK8(v string, reps int) {
	const Q = 16384
	c0 := int64(0)
	keepAlive = tBuild(20, &c0)
	lsum := tSum(keepAlive)
	lat := make([]int64, Q)
	arena := make([]ANode, 0, 2047)
	for r := -warmup(); r < reps; r++ {
		total := int64(0)
		t0 := time.Now()
		for q := range Q {
			a := time.Now()
			c := int64(q)
			var s int64
			if v == "tuned" {
				arena = arena[:0]
				root := aBuild(&arena, 10, &c)
				s = aSum(arena, root)
			} else {
				s = tSum(tBuild(10, &c))
			}
			total += s
			lat[q] = int64(time.Since(a))
		}
		dt := time.Since(t0).Seconds()
		if r >= 0 {
			result("k8", v, "16384x2047", r, dt, strconv.FormatInt(total+lsum, 10))
			slices.Sort(lat)
			fmt.Printf("LAT;%s;%d;%d;%d;%d;%d\n", v, lat[Q/2], lat[Q*9/10], lat[Q*99/100], lat[Q*999/1000], lat[Q-1])
		}
	}
}

// ------------------------------------------------------------------ K9
const M9 = 2048

func k9Init(i, j int) float64 { return float64((i*31+j*17)%1024) / 1024.0 }

//go:noinline
func k9Natural(in, out [][]float64) {
	for i := 1; i < M9-1; i++ {
		for j := 1; j < M9-1; j++ {
			out[i][j] = 0.25 * (((in[i-1][j] + in[i+1][j]) + in[i][j-1]) + in[i][j+1])
		}
	}
}

//go:noinline
func k9Rows(in, out []float64, r0, r1 int) {
	for i := r0; i < r1; i++ {
		up := in[(i-1)*M9 : i*M9 : i*M9]
		mid := in[i*M9 : (i+1)*M9 : (i+1)*M9]
		dn := in[(i+1)*M9 : (i+2)*M9 : (i+2)*M9]
		o := out[i*M9 : (i+1)*M9 : (i+1)*M9]
		for j := 1; j < M9-1; j++ {
			o[j] = 0.25 * (((up[j] + dn[j]) + mid[j-1]) + mid[j+1])
		}
	}
}
func runK9(v string, reps int) {
	for r := -warmup(); r < reps; r++ {
		var s, dt float64
		if v == "natural" {
			a, b := make([][]float64, M9), make([][]float64, M9)
			for i := range M9 {
				a[i], b[i] = make([]float64, M9), make([]float64, M9)
				for j := range M9 {
					a[i][j] = k9Init(i, j)
					b[i][j] = a[i][j]
				}
			}
			t0 := time.Now()
			for range 4 {
				k9Natural(a, b)
				a, b = b, a
			}
			dt = time.Since(t0).Seconds()
			for i := range M9 {
				for j := range M9 {
					s += a[i][j]
				}
			}
		} else {
			a, b := make([]float64, M9*M9), make([]float64, M9*M9)
			for k := range a {
				a[k] = k9Init(k/M9, k%M9)
				b[k] = a[k]
			}
			t0 := time.Now()
			for range 4 {
				if v == "tuned" {
					k9Rows(a, b, 1, M9-1)
				} else {
					var wg sync.WaitGroup
					for t := range 4 {
						wg.Add(1)
						go func() {
							defer wg.Done()
							k9Rows(a, b, 1+(M9-2)*t/4, 1+(M9-2)*(t+1)/4)
						}()
					}
					wg.Wait()
				}
				a, b = b, a
			}
			dt = time.Since(t0).Seconds()
			for _, x := range a {
				s += x
			}
		}
		if r >= 0 {
			result("k9", v, "2048^2x4", r, dt, fmt.Sprintf("%.15e", s))
		}
	}
}

// ------------------------------------------------------------------ K10
const M10 = 1 << 22
const CAP10 = 1 << 14

type spsc struct {
	writeIdx atomic.Uint64
	_        [120]byte
	readIdx  atomic.Uint64
	_        [120]byte
	buf      [CAP10]uint64
}

func runK10(v string, reps int) {
	bench("k10", v, "2^22", reps, func() string {
		var sum uint64
		var wg sync.WaitGroup
		wg.Add(2)
		if v == "natural" {
			ch := make(chan uint64, CAP10)
			go func() {
				defer wg.Done()
				for x := uint64(1); x <= M10; x++ {
					ch <- x
				}
				close(ch)
			}()
			go func() {
				defer wg.Done()
				for x := range ch {
					sum += x
				}
			}()
		} else {
			q := new(spsc)
			go func() {
				defer wg.Done()
				w, rc := uint64(0), uint64(0)
				for x := uint64(1); x <= M10; x++ {
					for w-rc == CAP10 {
						rc = q.readIdx.Load()
					}
					q.buf[w&(CAP10-1)] = x
					w++
					q.writeIdx.Store(w)
				}
			}()
			go func() {
				defer wg.Done()
				rd, wc := uint64(0), uint64(0)
				s := uint64(0)
				for range M10 {
					for rd == wc {
						wc = q.writeIdx.Load()
					}
					s += q.buf[rd&(CAP10-1)]
					rd++
					q.readIdx.Store(rd)
				}
				sum = s
			}()
		}
		wg.Wait()
		return strconv.FormatUint(sum, 10)
	})
}

func main() {
	k, v := os.Args[1], os.Args[2]
	reps, _ := strconv.Atoi(os.Args[3])
	p := ""
	if len(os.Args) > 4 {
		p = os.Args[4]
	}
	switch k {
	case "k1":
		runK1(v, reps)
	case "k2":
		runK2(v, reps, p)
	case "k3":
		runK3(v, reps)
	case "k4":
		runK4(v, reps)
	case "k5":
		runK5(v, reps)
	case "k6":
		runK6(v, reps, p)
	case "k7":
		runK7(v, reps)
	case "k8":
		runK8(v, reps)
	case "k9":
		runK9(v, reps)
	case "k10":
		runK10(v, reps)
	}
}
