package main

import "fmt"

type Adder interface{ Add(int) int }
type P struct{ v int }

func (p P) Add(x int) int { return p.v + x }

//go:noinline
func Sum[T int | float64](s []T) T {
	var t T
	for _, x := range s {
		t += x
	}
	return t
}

//go:noinline
func Apply[T Adder](a T, n int) int { return a.Add(n) }

func main() {
	fmt.Println(Sum([]int{1, 2}), Sum([]float64{1.5}), Apply(P{3}, 4))
}
