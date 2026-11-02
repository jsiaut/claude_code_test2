package main

import (
	"fmt"
	"os"
	"simd/archsimd"
	"sort"
	"time"
	"unsafe"
)

func load(name string) []float32 {
	b, err := os.ReadFile("/opt/msdata/" + name)
	if err != nil {
		panic(err)
	}
	return unsafe.Slice((*float32)(unsafe.Pointer(&b[0])), len(b)/4)
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

//go:noinline
func k5TunedClear(a, b []float32) float32 {
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
	archsimd.ClearAVXUpperBits()
	r := float32(0)
	for _, x := range t {
		r += x
	}
	return r
}

var sink []float32

func run(name string, f func(a, b []float32) float32, a, b []float32) {
	var ts []float64
	d := float32(0)
	for r := -2; r < 15; r++ {
		t0 := time.Now()
		for range 1 << 16 {
			sink = a
			d = f(sink, b)
		}
		if r >= 0 {
			ts = append(ts, time.Since(t0).Seconds()*1e3)
		}
	}
	sort.Float64s(ts)
	fmt.Printf("%s : médiane %.2f ms (min %.2f) somme %.4f\n", name, ts[len(ts)/2], ts[0], d)
}

func main() {
	a, b := load("k5_a.f32"), load("k5_b.f32")
	switch os.Args[1] {
	case "orig":
		run("K5 tuned du banc", k5Tuned, a, b)
	case "clear":
		run("K5 tuned + ClearAVXUpperBits", k5TunedClear, a, b)
	}
}
