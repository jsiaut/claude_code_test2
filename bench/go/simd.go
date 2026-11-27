//go:build goexperiment.simd

// Fonctions à SIMD explicite de l'implémentation Go (simd/archsimd, expérimental : GOEXPERIMENT=simd). Elles ne
// sont compilées que dans le binaire ms ; le lanceur (run) y envoie les variantes qui les appellent.
package main

import (
	"math/bits"
	"simd/archsimd"
)

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
	archsimd.ClearAVXUpperBits() // remarque sur Go (docs/GO.md) : passage d'AVX à SSE sans pénalité
	s := 0.0
	for _, x := range t {
		s += x
	}
	return s
}

// v4, point 3 (docs/V4_EQUAL.md, R3) : variante tuned, SIMD explicite (simd/archsimd, GOEXPERIMENT=simd) : masque
// v >= 128 (VPCMPUB), octets hors masque à zéro, VPSADBW en sommes de 64 bits.
//
//go:noinline
func k4Tuned(v []byte) uint64 {
	lim := archsimd.BroadcastUint8x64(128)
	zero := archsimd.BroadcastUint8x64(0)
	var acc archsimd.Uint64x8
	n := len(v)
	i := 0
	for ; i+64 <= n; i += 64 {
		x := archsimd.LoadUint8x64(v[i : i+64])
		acc = acc.Add(x.Masked(x.GreaterEqual(lim)).SumOf8AbsDiff(zero))
	}
	var lanes [8]uint64
	acc.StoreArray(&lanes)
	s := uint64(0)
	for _, l := range lanes {
		s += l
	}
	for ; i < n; i++ {
		if v[i] >= 128 {
			s += uint64(v[i])
		}
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
	archsimd.ClearAVXUpperBits() // remarque sur Go (docs/GO.md) : passage d'AVX à SSE sans pénalité
	r := float32(0)
	for _, x := range t {
		r += x
	}
	return r
}

// v4, point 4 (3.3, K5 tuned_v) : la forme de la remarque sur Go (bench/go_exp, tuned_r ; docs/GO.md, 4.3 : × 0,75),
// recopiée : la boucle de k5Tuned, la réduction finale dans les registres (GetLo/GetHi, ConcatAddPairs) ; le résultat
// passe par la mémoire avant ClearAVXUpperBits, sans quoi le compilateur place VZEROUPPER avant la réduction (vérifié
// au désassemblage par la remarque).
//
//go:noinline
func k5TunedR(a, b []float32) float32 {
	z := archsimd.BroadcastFloat32x16(0)
	s0, s1, s2, s3 := z, z, z, z
	for i := 0; i+64 <= len(a); i += 64 {
		s0 = archsimd.LoadFloat32x16(a[i:i+16]).MulAdd(archsimd.LoadFloat32x16(b[i:i+16]), s0)
		s1 = archsimd.LoadFloat32x16(a[i+16:i+32]).MulAdd(archsimd.LoadFloat32x16(b[i+16:i+32]), s1)
		s2 = archsimd.LoadFloat32x16(a[i+32:i+48]).MulAdd(archsimd.LoadFloat32x16(b[i+32:i+48]), s2)
		s3 = archsimd.LoadFloat32x16(a[i+48:i+64]).MulAdd(archsimd.LoadFloat32x16(b[i+48:i+64]), s3)
	}
	s := s0.Add(s1).Add(s2.Add(s3))
	h := s.GetLo().Add(s.GetHi())
	q := h.GetLo().Add(h.GetHi())
	q = q.ConcatAddPairs(q)
	q = q.ConcatAddPairs(q)
	// le résultat passe par la mémoire : sinon le compilateur place VZEROUPPER avant la réduction (vérifié au
	// désassemblage), qui salit de nouveau les registres avant le retour en SSE
	var out [4]float32
	q.StoreArray(&out)
	archsimd.ClearAVXUpperBits()
	return out[0]
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
	archsimd.ClearAVXUpperBits() // remarque sur Go (docs/GO.md) : passage d'AVX à SSE sans pénalité
	s := int64(0)
	for _, x := range t {
		s += x
	}
	return s + q6Natural(c, i, hi)
}

// v4, point 4 (3.3, Q1 tuned_v) : la forme de la remarque sur Go (bench/go_exp, tuned_1p ; docs/GO.md, 4.3),
// recopiée : une passe, algorithme de la référence C (16 lignes par tour, masque de passage, un masque par groupe,
// compte par population du masque : bits.OnesCount16 de ToBits), accumulateurs des six groupes en variables locales,
// additions masquées par IfElse. La variante tuned publiée est scalaire. Exactitude : quantité, prix et
// prix × (100 − remise) en voies de 32 bits vidées toutes les 2 048 lignes, soit 128 lignes par voie : au plus
// 128 × 50 000 × 100 = 6,4 × 10^8 < 2^31 (prix ≤ 50 000, docs/SPEC.md) ; charge en 64 bits.
//
//go:noinline
func q1OnePass(c *Cols, lo, hi int, acc *Q1Acc) {
	lim, c100 := archsimd.BroadcastInt32x16(10471), archsimd.BroadcastInt32x16(100)
	k0 := archsimd.BroadcastInt32x16(0)
	k1 := archsimd.BroadcastInt32x16(1)
	k2 := archsimd.BroadcastInt32x16(2)
	k3 := archsimd.BroadcastInt32x16(3)
	k4 := archsimd.BroadcastInt32x16(4)
	k5 := archsimd.BroadcastInt32x16(5)
	z, zl := archsimd.BroadcastInt32x16(0), archsimd.BroadcastInt64x8(0)
	i := lo
	for i+16 <= hi {
		end := hi - (hi-i)%16
		if i+2048 <= hi {
			end = i + 2048
		}
		q0, p0, dp0, cl0, ch0, n0 := z, z, z, zl, zl, int64(0)
		q1, p1, dp1, cl1, ch1, n1 := z, z, z, zl, zl, int64(0)
		q2, p2, dp2, cl2, ch2, n2 := z, z, z, zl, zl, int64(0)
		q3, p3, dp3, cl3, ch3, n3 := z, z, z, zl, zl, int64(0)
		q4, p4, dp4, cl4, ch4, n4 := z, z, z, zl, zl, int64(0)
		q5, p5, dp5, cl5, ch5, n5 := z, z, z, zl, zl, int64(0)
		for ; i < end; i += 16 {
			pass := archsimd.LoadInt32x16(c.sd[i : i+16]).LessEqual(lim)
			rf := archsimd.LoadUint8x16(c.rf[i : i+16]).ExtendToUint32().AsInt32x16()
			gr := rf.Add(rf).Add(archsimd.LoadUint8x16(c.ls[i : i+16]).ExtendToUint32().AsInt32x16())
			vq := archsimd.LoadUint8x16(c.q[i : i+16]).ExtendToUint32().AsInt32x16()
			vd := archsimd.LoadUint8x16(c.d[i : i+16]).ExtendToUint32().AsInt32x16()
			vt := archsimd.LoadUint8x16(c.t[i : i+16]).ExtendToUint32().AsInt32x16().Add(c100)
			vp := archsimd.LoadInt32x16(c.pr[i : i+16])
			vdp := vp.Mul(c100.Sub(vd))
			chl := vdp.GetLo().ExtendToInt64().Mul(vt.GetLo().ExtendToInt64())
			chh := vdp.GetHi().ExtendToInt64().Mul(vt.GetHi().ExtendToInt64())
			m0 := pass.And(gr.Equal(k0))
			b0 := m0.ToBits()
			n0 += int64(bits.OnesCount16(b0))
			q0, p0, dp0 = q0.Add(vq).IfElse(m0, q0), p0.Add(vp).IfElse(m0, p0), dp0.Add(vdp).IfElse(m0, dp0)
			cl0 = cl0.Add(chl).IfElse(archsimd.Mask64x8FromBits(uint8(b0)), cl0)
			ch0 = ch0.Add(chh).IfElse(archsimd.Mask64x8FromBits(uint8(b0>>8)), ch0)
			m1 := pass.And(gr.Equal(k1))
			b1 := m1.ToBits()
			n1 += int64(bits.OnesCount16(b1))
			q1, p1, dp1 = q1.Add(vq).IfElse(m1, q1), p1.Add(vp).IfElse(m1, p1), dp1.Add(vdp).IfElse(m1, dp1)
			cl1 = cl1.Add(chl).IfElse(archsimd.Mask64x8FromBits(uint8(b1)), cl1)
			ch1 = ch1.Add(chh).IfElse(archsimd.Mask64x8FromBits(uint8(b1>>8)), ch1)
			m2 := pass.And(gr.Equal(k2))
			b2 := m2.ToBits()
			n2 += int64(bits.OnesCount16(b2))
			q2, p2, dp2 = q2.Add(vq).IfElse(m2, q2), p2.Add(vp).IfElse(m2, p2), dp2.Add(vdp).IfElse(m2, dp2)
			cl2 = cl2.Add(chl).IfElse(archsimd.Mask64x8FromBits(uint8(b2)), cl2)
			ch2 = ch2.Add(chh).IfElse(archsimd.Mask64x8FromBits(uint8(b2>>8)), ch2)
			m3 := pass.And(gr.Equal(k3))
			b3 := m3.ToBits()
			n3 += int64(bits.OnesCount16(b3))
			q3, p3, dp3 = q3.Add(vq).IfElse(m3, q3), p3.Add(vp).IfElse(m3, p3), dp3.Add(vdp).IfElse(m3, dp3)
			cl3 = cl3.Add(chl).IfElse(archsimd.Mask64x8FromBits(uint8(b3)), cl3)
			ch3 = ch3.Add(chh).IfElse(archsimd.Mask64x8FromBits(uint8(b3>>8)), ch3)
			m4 := pass.And(gr.Equal(k4))
			b4 := m4.ToBits()
			n4 += int64(bits.OnesCount16(b4))
			q4, p4, dp4 = q4.Add(vq).IfElse(m4, q4), p4.Add(vp).IfElse(m4, p4), dp4.Add(vdp).IfElse(m4, dp4)
			cl4 = cl4.Add(chl).IfElse(archsimd.Mask64x8FromBits(uint8(b4)), cl4)
			ch4 = ch4.Add(chh).IfElse(archsimd.Mask64x8FromBits(uint8(b4>>8)), ch4)
			m5 := pass.And(gr.Equal(k5))
			b5 := m5.ToBits()
			n5 += int64(bits.OnesCount16(b5))
			q5, p5, dp5 = q5.Add(vq).IfElse(m5, q5), p5.Add(vp).IfElse(m5, p5), dp5.Add(vdp).IfElse(m5, dp5)
			cl5 = cl5.Add(chl).IfElse(archsimd.Mask64x8FromBits(uint8(b5)), cl5)
			ch5 = ch5.Add(chh).IfElse(archsimd.Mask64x8FromBits(uint8(b5>>8)), ch5)
		}
		acc[0][0] += n0
		acc[0][1] += sum32(q0)
		acc[0][2] += sum32(p0)
		acc[0][3] += sum32(dp0)
		acc[0][4] += sum64(cl0.Add(ch0))
		acc[1][0] += n1
		acc[1][1] += sum32(q1)
		acc[1][2] += sum32(p1)
		acc[1][3] += sum32(dp1)
		acc[1][4] += sum64(cl1.Add(ch1))
		acc[2][0] += n2
		acc[2][1] += sum32(q2)
		acc[2][2] += sum32(p2)
		acc[2][3] += sum32(dp2)
		acc[2][4] += sum64(cl2.Add(ch2))
		acc[3][0] += n3
		acc[3][1] += sum32(q3)
		acc[3][2] += sum32(p3)
		acc[3][3] += sum32(dp3)
		acc[3][4] += sum64(cl3.Add(ch3))
		acc[4][0] += n4
		acc[4][1] += sum32(q4)
		acc[4][2] += sum32(p4)
		acc[4][3] += sum32(dp4)
		acc[4][4] += sum64(cl4.Add(ch4))
		acc[5][0] += n5
		acc[5][1] += sum32(q5)
		acc[5][2] += sum32(p5)
		acc[5][3] += sum32(dp5)
		acc[5][4] += sum64(cl5.Add(ch5))
	}
	archsimd.ClearAVXUpperBits()
	if i < hi {
		q1Natural(c, i, hi, acc)
	}
}

func sum32(v archsimd.Int32x16) int64 {
	var t [16]int32
	v.StoreArray(&t)
	s := int64(0)
	for _, x := range t {
		s += int64(x)
	}
	return s
}

func sum64(v archsimd.Int64x8) int64 {
	var t [8]int64
	v.StoreArray(&t)
	s := int64(0)
	for _, x := range t {
		s += x
	}
	return s
}

// v4, point 4 (3.3, K9 tuned_v) : la forme de la remarque sur Go (bench/go_exp, tuned_vec ; docs/GO.md, 4.3 : × 0,78),
// recopiée : par ligne, j depuis 1, vecteurs de 8 float64 (archsimd) chargés et écrits sans contrainte d'alignement,
// mêmes additions dans le même ordre. Les dernières colonnes : un vecteur entier calé sur la fin de la ligne, qui
// recouvre le précédent (v5, docs/V5.md, écart 1 : LoadFloat64x8Part charge 64 octets quelle que soit la longueur de
// la tranche et lisait après la fin de la grille à la dernière ligne, d'où une erreur de segmentation occasionnelle).
//
//go:noinline
func k9RowsVec(in, out []float64, r0, r1 int) {
	q := archsimd.BroadcastFloat64x8(0.25)
	for i := r0; i < r1; i++ {
		up := in[(i-1)*M9 : i*M9 : i*M9]
		mid := in[i*M9 : (i+1)*M9 : (i+1)*M9]
		dn := in[(i+1)*M9 : (i+2)*M9 : (i+2)*M9]
		o := out[i*M9 : (i+1)*M9 : (i+1)*M9]
		j := 1
		for ; j+8 <= M9-1; j += 8 {
			s := archsimd.LoadFloat64x8(up[j : j+8]).Add(archsimd.LoadFloat64x8(dn[j : j+8])).
				Add(archsimd.LoadFloat64x8(mid[j-1 : j+7])).Add(archsimd.LoadFloat64x8(mid[j+1 : j+9]))
			q.Mul(s).Store(o[j : j+8])
		}
		if j < M9-1 {
			j = M9 - 9
			s := archsimd.LoadFloat64x8(up[j : j+8]).Add(archsimd.LoadFloat64x8(dn[j : j+8])).
				Add(archsimd.LoadFloat64x8(mid[j-1 : j+7])).Add(archsimd.LoadFloat64x8(mid[j+1 : j+9]))
			q.Mul(s).Store(o[j : j+8])
		}
	}
	archsimd.ClearAVXUpperBits()
}
