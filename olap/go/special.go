//go:build goexperiment.simd

// Niveau spécialisé des primitives à deux niveaux (olap/SPEC.md, 7) : AVX-512 par le paquet expérimental
// simd/archsimd (GOEXPERIMENT=simd). Même plan, mêmes structures, mêmes fonctions de hachage.
//
//  0. décodage : seize valeurs à la fois, par permutation d'octets et décalages variables ;
//  1. sélection : comparaison de 16 valeurs et compression des positions retenues ;
//  2. agrégation de T1 : sommes masquées par groupe, huit lignes à la fois ;
//  3. recherche de sous-chaîne : premier et dernier octet de l'aiguille comparés à 64 positions à la fois ;
//  4. expressions de T1 et hachage des clés, huit lignes à la fois : le compilateur ne vectorise pas de lui-même.
//
// Le paquet n'offre ni écriture non temporelle ni préchargement : la répartition et les sondes restent celles du
// niveau portable. Ce sont deux manques.
package main

import (
	"math/bits"
	"simd/archsimd"
	"unsafe"
)

const (
	level      = "s"
	searchStep = 64
)

// ------------------------------------------------------------------------------------------------ 0. décodage

// Seize valeurs à la fois (largeur de 25 bits au plus) : elles occupent 2 x largeur octets ; une permutation
// d'octets amène dans chaque voie de 32 bits les 4 octets où commence sa valeur, un décalage variable la cale, un
// masque la borne. Au-delà de 25 bits : huit valeurs à la fois dans des voies de 64 bits. Chaque pas lit 64 octets :
// les colonnes sont chargées avec cette marge.
type unpackTab struct {
	idx  [64]uint8
	sh32 [16]uint32
	sh64 [8]uint64
}

var unpackTabs = func() (t [33]unpackTab) {
	for w := 1; w <= 32; w++ {
		lanes, size := 16, 4
		if w > 25 {
			lanes, size = 8, 8
		}
		for j := range lanes {
			for k := range size {
				t[w].idx[size*j+k] = uint8(j*w>>3 + k)
			}
			if w <= 25 {
				t[w].sh32[j] = uint32(j * w & 7)
			} else {
				t[w].sh64[j] = uint64(j * w & 7)
			}
		}
	}
	return
}()

// Décode n valeurs du bloc b à partir de la ligne start (multiple de 64) ; écrit des groupes entiers de 16.
func unpack(c *Col, b, start, n int, out []int32) {
	e := &c.dir[b]
	w := int(e.width)
	base := archsimd.BroadcastInt32x16(int32(e.min))
	if w == 0 {
		for i := 0; i < n; i += 16 {
			base.Store(out[i:])
		}
		archsimd.ClearAVXUpperBits()
		return
	}
	p := unsafe.Pointer(&c.words(b)[start/64*w])
	t := &unpackTabs[w]
	idx := archsimd.LoadUint8x64Array(&t.idx)
	if w <= 25 {
		sh, mask := archsimd.LoadUint32x16Array(&t.sh32), archsimd.BroadcastUint32x16(1<<w-1)
		for i := 0; i < n; i += 16 {
			x := archsimd.LoadUint8x64Array((*[64]uint8)(p)).Permute(idx).AsUint32x16()
			x.ShiftRight(sh).And(mask).AsInt32x16().Add(base).Store(out[i:])
			p = unsafe.Add(p, 2*w)
		}
	} else {
		sh, mask := archsimd.LoadUint64x8Array(&t.sh64), archsimd.BroadcastUint64x8(1<<w-1)
		base8 := archsimd.BroadcastInt32x8(int32(e.min))
		for i := 0; i < n; i += 8 {
			x := archsimd.LoadUint8x64Array((*[64]uint8)(p)).Permute(idx).AsUint64x8()
			x.ShiftRight(sh).And(mask).TruncToUint32().AsInt32x8().Add(base8).Store(out[i:])
			p = unsafe.Add(p, w)
		}
	}
	archsimd.ClearAVXUpperBits()
}

// ------------------------------------------------------------------------------------------------ 1. sélection

var iota16 = [16]int32{0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15}

// Voies vivantes d'un pas de 16 quand il reste `left` valeurs.
func live16(left int) uint16 {
	if left >= 16 {
		return 0xFFFF
	}
	return 1<<left - 1
}

// Positions (base + i) des valeurs v[i] comprises entre lo et hi, bornes comprises. Les vecteurs de travail ont 16
// cases de marge : chaque pas lit et écrit 16 voies entières.
func selBetween(v []int32, lo, hi int32, base uint32, pos []int32) int {
	vlo, vhi := archsimd.BroadcastInt32x16(lo), archsimd.BroadcastInt32x16(hi)
	idx := archsimd.BroadcastInt32x16(int32(base)).Add(archsimd.LoadInt32x16Array(&iota16))
	step := archsimd.BroadcastInt32x16(16)
	n, k := len(v), 0
	for i := 0; i < n; i += 16 {
		x := archsimd.LoadInt32x16(v[i : i+16])
		m := x.GreaterEqual(vlo).And(x.LessEqual(vhi)).ToBits() & live16(n-i)
		idx.Compress(archsimd.Mask32x16FromBits(m)).Store(pos[k : k+16])
		k += bits.OnesCount16(m)
		idx = idx.Add(step)
	}
	archsimd.ClearAVXUpperBits()
	return k
}

// Parmi les entrées (position, charge) : garde celles dont la valeur v[i] est entre lo et hi.
func keepBetween(v, posIn, payIn []int32, lo, hi int32, posOut, payOut []int32) int {
	vlo, vhi := archsimd.BroadcastInt32x16(lo), archsimd.BroadcastInt32x16(hi)
	n, k := len(v), 0
	for i := 0; i < n; i += 16 {
		x := archsimd.LoadInt32x16(v[i : i+16])
		bitsKept := x.GreaterEqual(vlo).And(x.LessEqual(vhi)).ToBits() & live16(n-i)
		m := archsimd.Mask32x16FromBits(bitsKept)
		archsimd.LoadInt32x16(posIn[i : i+16]).Compress(m).Store(posOut[k : k+16])
		archsimd.LoadInt32x16(payIn[i : i+16]).Compress(m).Store(payOut[k : k+16])
		k += bits.OnesCount16(bitsKept)
	}
	archsimd.ClearAVXUpperBits()
	return k
}

// ------------------------------------------------------------------------------------------------ 2. agrégation de T1

// Huit lignes à la fois, un groupe après l'autre : un masque et cinq additions masquées. Chaque groupe fait sa
// passe sur le vecteur pour que ses cinq accumulateurs soient des variables locales, que le compilateur garde en
// registres ; un tableau d'accumulateurs resterait en mémoire.
func t1Aggregate(agg *[6]Agg1, grp, qty, ext, disc []int32, dp, ch []int64, ship []int32, cut int32, sel []int32) {
	vcut := archsimd.BroadcastInt32x8(cut)
	n := len(grp)
	for g := range agg {
		var q, e, x, y, d archsimd.Int64x8
		vg := archsimd.BroadcastInt32x8(int32(g))
		cnt := 0
		for i := 0; i < n; i += 8 {
			kept := archsimd.LoadInt32x8(grp[i : i+8]).Equal(vg).ToBits()
			if n-i < 8 {
				kept &= 1<<(n-i) - 1
			}
			if ship != nil {
				kept &= archsimd.LoadInt32x8(ship[i : i+8]).LessEqual(vcut).ToBits()
			}
			m := archsimd.Mask64x8FromBits(kept)
			q = q.Add(archsimd.LoadInt32x8(qty[i : i+8]).ExtendToInt64().Masked(m))
			e = e.Add(archsimd.LoadInt32x8(ext[i : i+8]).ExtendToInt64().Masked(m))
			x = x.Add(archsimd.LoadInt64x8(dp[i : i+8]).Masked(m))
			y = y.Add(archsimd.LoadInt64x8(ch[i : i+8]).Masked(m))
			d = d.Add(archsimd.LoadInt32x8(disc[i : i+8]).ExtendToInt64().Masked(m))
			cnt += bits.OnesCount8(kept)
		}
		a := &agg[g]
		a.qty += sum8(q)
		a.base += sum8(e)
		a.discPrice += sum8(x)
		a.charge += sum8(y)
		a.disc += sum8(d)
		a.count += int64(cnt)
	}
	archsimd.ClearAVXUpperBits()
}

// Somme des huit voies, sans passer par la mémoire : tant que les registres vectoriels sont en usage, le code scalaire
// que le compilateur écrit pour un tableau (mise à zéro en SSE) subirait la pénalité de transition entre AVX et SSE.
func sum8(v archsimd.Int64x8) int64 {
	v4 := v.GetLo().Add(v.GetHi())
	v2 := v4.GetLo().Add(v4.GetHi())
	return v2.GetElem(0) + v2.GetElem(1)
}

// ------------------------------------------------------------------------------------------------ 3. sous-chaînes

// Candidates parmi les 64 positions qui partent de p : premier octet de l'aiguille en p + i, dernier en p + i + m - 1.
func searchCandidates(p []byte, m int, c0, c1 byte) uint64 {
	a := archsimd.LoadUint8x64Array((*[64]uint8)(unsafe.Pointer(&p[0])))
	b := archsimd.LoadUint8x64Array((*[64]uint8)(unsafe.Pointer(&p[m-1])))
	r := a.Equal(archsimd.BroadcastUint8x64(c0)).ToBits() & b.Equal(archsimd.BroadcastUint8x64(c1)).ToBits()
	archsimd.ClearAVXUpperBits()
	return r
}

// ------------------------------------------------------------------------------------------------ 4. expressions, hachage

// Expressions de T1 sur un vecteur, huit lignes à la fois : prix remisé, prix taxé, groupe. Les vecteurs de travail
// ont la marge qu'il faut pour des pas entiers.
func t1Expr(ext, disc, tax, rf, ls []int32, x, y []int64, g []int32) {
	hundred := archsimd.BroadcastInt64x8(100)
	for i := 0; i < len(x); i += 8 {
		e := archsimd.LoadInt32x8(ext[i : i+8]).ExtendToInt64()
		d := archsimd.LoadInt32x8(disc[i : i+8]).ExtendToInt64()
		t := archsimd.LoadInt32x8(tax[i : i+8]).ExtendToInt64()
		xv := e.Mul(hundred.Sub(d))
		xv.Store(x[i : i+8])
		xv.Mul(hundred.Add(t)).Store(y[i : i+8])
		archsimd.LoadInt32x8(rf[i : i+8]).ShiftAllLeft(1).Add(archsimd.LoadInt32x8(ls[i : i+8])).Store(g[i : i+8])
	}
	archsimd.ClearAVXUpperBits()
}

// Hachage d'un vecteur de clés de 32 bits, huit à la fois.
func hashKeys(key []int32, h []uint64) {
	k1 := archsimd.BroadcastUint64x8(K1)
	for i := 0; i < len(h); i += 8 {
		k := archsimd.LoadInt32x8(key[i : i+8]).ExtendToInt64().AsUint64x8().Mul(k1)
		k.Xor(k.ShiftAllRight(32)).Store(h[i : i+8])
	}
	archsimd.ClearAVXUpperBits()
}

// Hachage d'un vecteur de clés de 64 bits lues dans la colonne : huit à la fois, puis le reste une à une.
func hashLongs(v []int64, h []uint64) {
	k1 := archsimd.BroadcastUint64x8(K1)
	i := 0
	for ; i+8 <= len(v); i += 8 {
		k := archsimd.LoadInt64x8(v[i : i+8]).AsUint64x8().Mul(k1)
		k.Xor(k.ShiftAllRight(32)).Store(h[i : i+8])
	}
	for ; i < len(v); i++ {
		h[i] = hash64(uint64(v[i]))
	}
	archsimd.ClearAVXUpperBits()
}
