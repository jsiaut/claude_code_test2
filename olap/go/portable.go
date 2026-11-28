//go:build !goexperiment.simd

// Niveau portable des primitives à deux niveaux : aucune vectorisation explicite, aucune construction propre à une
// famille de processeurs. Le compilateur de Go ne vectorise pas : ces boucles restent scalaires.
package main

import "math"

const (
	level      = "p"
	searchStep = 0 // pas de recherche par 64 positions à ce niveau
)

func searchCandidates(p []byte, m int, c0, c1 byte) uint64 { return 0 }

func unpack(c *Col, b, start, n int, out []int32) { unpackPortable(c, b, start, n, out) }

// 1 si x est entre lo et lo + span (bornes comprises), 0 sinon ; sans branchement : la distance à lo, non signée,
// est retranchée de span, et la retenue donne la réponse.
func inRange(x, lo int32, span uint64) int {
	return int(1 - (span-uint64(uint32(x)-uint32(lo)))>>63)
}

// Sélection. Positions (base + i) des valeurs v[i] comprises entre lo et hi, bornes comprises.
func selBetween(v []int32, lo, hi int32, base uint32, pos []int32) int {
	span := uint64(uint32(hi) - uint32(lo))
	pos = pos[:len(v)]
	k := 0
	for i, x := range v {
		pos[k] = int32(base + uint32(i))
		k += inRange(x, lo, span)
	}
	return k
}

// Parmi les entrées (position, charge) : garde celles dont la valeur v[i] est entre lo et hi.
func keepBetween(v, posIn, payIn []int32, lo, hi int32, posOut, payOut []int32) int {
	span := uint64(uint32(hi) - uint32(lo))
	n := len(v)
	posIn, payIn, posOut, payOut = posIn[:n], payIn[:n], posOut[:n], payOut[:n]
	k := 0
	for i, x := range v {
		posOut[k], payOut[k] = posIn[i], payIn[i]
		k += inRange(x, lo, span)
	}
	return k
}

// Agrégation de T1 : un vecteur dans le tableau des six groupes ; avec ship, seules comptent les lignes dont la
// date ne dépasse pas cut (vecteur de sélection dans sel).
func t1Aggregate(agg *[6]Agg1, grp, qty, ext, disc []int32, dp, ch []int64, ship []int32, cut int32, sel []int32) {
	n := len(grp)
	qty, ext, disc, dp, ch = qty[:n], ext[:n], disc[:n], dp[:n], ch[:n]
	add := func(i int) {
		g := &agg[grp[i]]
		g.qty += int64(qty[i])
		g.base += int64(ext[i])
		g.discPrice += dp[i]
		g.charge += ch[i]
		g.disc += int64(disc[i])
		g.count++
	}
	if ship == nil {
		for i := range grp {
			add(i)
		}
	} else {
		k := selBetween(ship, math.MinInt32, cut, 0, sel)
		for _, i := range sel[:k] {
			add(int(i))
		}
	}
}
