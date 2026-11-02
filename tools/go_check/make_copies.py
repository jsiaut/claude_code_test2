#!/usr/bin/env python3
"""Copies de la remarque sur Go (plan : docs/GO.md, section 3.3), produites par remplacements de texte contrôlés
(chaque texte remplacé doit apparaître exactement une fois ; le reste du fichier est identique à l'octet).

* bench/go_ref : copie exacte de bench/go_k9h (le code publié : bench/go, harnais commun de K9), GOEXPERIMENT=simd.
* bench/go_fix : correction publiée. Les trois fonctions archsimd (K1 soa, K5 tuned, Q6 tuned) appellent
  archsimd.ClearAVXUpperBits() (VZEROUPPER) après leur partie vectorielle, avant leur réduction scalaire : sans lui,
  les instructions SSE qui suivent paient la transition d'AVX à SSE. Rien d'autre ne change. GOEXPERIMENT=simd.
* bench/go_noexp : le code publié des variantes sans archsimd, compilé sans GOEXPERIMENT (la copie standard
  bench/go_std de la confrontation, dont les variantes naturelles et les noyaux scalaires sont ceux de bench/go, avec
  le harnais commun de K9 de bench/go_k9h) ; variante nouvelle K8 tuned_it (arène itérative, sensibilité).
* bench/go_exp : sensibilités archsimd, sur la base de go_fix : K5 tuned_r (réduction dans les registres), K9
  tuned_vec et mt_vec (Float64x8, même ordre des additions), K6 tuned_1p et mt_1p (Q1 en une passe). GOEXPERIMENT=simd.
* bench/go_nopre : le binaire de go_ref lancé avec GODEBUG=asyncpreemptoff=1 (information : mécanisme de l'artefact).
Usage : make_copies.py (puis build.sh de go_ref, go_fix, go_noexp et go_exp)."""
import os, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HERE = os.path.dirname(os.path.abspath(__file__))
K10 = "// ------------------------------------------------------------------ K10\n"


def sub(text, old, new):
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"texte trouvé {n} fois (1 attendu) :\n{old[:300]}")
    return text.replace(old, new)


# ------------------------------------------------------------------ correction (go_fix et go_exp)
CLEAR = "\tarchsimd.ClearAVXUpperBits() // remarque sur Go (docs/GO.md) : passage d'AVX à SSE sans pénalité\n"
FIX = [("\tvar t [8]float64\n\ta0.Add(a1).StoreArray(&t)\n", "\tvar t [8]float64\n\ta0.Add(a1).StoreArray(&t)\n" + CLEAR),
       ("\tvar t [16]float32\n\ts0.Add(s1).Add(s2.Add(s3)).StoreArray(&t)\n",
        "\tvar t [16]float32\n\ts0.Add(s1).Add(s2.Add(s3)).StoreArray(&t)\n" + CLEAR),
       ("\tvar t [8]int64\n\tacc.StoreArray(&t)\n", "\tvar t [8]int64\n\tacc.StoreArray(&t)\n" + CLEAR)]


def fix(text):
    for a, b in FIX:
        text = sub(text, a, b)
    return text


# ------------------------------------------------------------------ sensibilités archsimd (go_exp)
K5R = """// sensibilité tuned_r (remarque sur Go) : la réduction finale reste dans les registres (GetLo/GetHi, ConcatAddPairs)
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

var sink []float32
"""
K5_CALL_OLD = """			if v == "tuned" {
				d = k5Tuned(sink, b)
			} else {
				d = k5Natural(sink, b)
			}
"""
K5_CALL_NEW = """			switch v {
			case "tuned":
				d = k5Tuned(sink, b)
			case "tuned_r":
				d = k5TunedR(sink, b)
			default:
				d = k5Natural(sink, b)
			}
"""
K9V = """// sensibilité tuned_vec et mt_vec (remarque sur Go) : la boucle de k9Rows en archsimd (8 float64 par vecteur), même
// ordre des additions ; les 6 dernières colonnes par chargements partiels
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
		if n := M9 - 1 - j; n > 0 {
			u, _ := archsimd.LoadFloat64x8Part(up[j : j+n])
			w, _ := archsimd.LoadFloat64x8Part(dn[j : j+n])
			l, _ := archsimd.LoadFloat64x8Part(mid[j-1 : j-1+n])
			r, _ := archsimd.LoadFloat64x8Part(mid[j+1 : j+1+n])
			q.Mul(u.Add(w).Add(l).Add(r)).StorePart(o[j : j+n])
		}
	}
	archsimd.ClearAVXUpperBits()
}
func runK9(v string, reps int) {
"""
K9_CALL_OLD = """				if v == "tuned" {
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
"""
K9_CALL_NEW = """				if v == "tuned" {
					k9Rows(a, b, 1, M9-1)
				} else if v == "tuned_vec" {
					k9RowsVec(a, b, 1, M9-1)
				} else {
					var wg sync.WaitGroup
					for t := range 4 {
						wg.Add(1)
						go func() {
							defer wg.Done()
							if v == "mt_vec" {
								k9RowsVec(a, b, 1+(M9-2)*t/4, 1+(M9-2)*(t+1)/4)
							} else {
								k9Rows(a, b, 1+(M9-2)*t/4, 1+(M9-2)*(t+1)/4)
							}
						}()
					}
					wg.Wait()
				}
"""
Q1_CASE_OLD = """		case v == "tuned":
			var a Q1Acc
			q1Tuned(c, 0, N6, &a)
			s = fold(&a)
		default:
"""
Q1_CASE_NEW = """		case v == "tuned":
			var a Q1Acc
			q1Tuned(c, 0, N6, &a)
			s = fold(&a)
		case v == "tuned_1p":
			var a Q1Acc
			q1OnePass(c, 0, N6, &a)
			s = fold(&a)
		default:
"""
Q1_MT_OLD = """					if q1 {
						var a Q1Acc
						q1Tuned(c, lo, hi, &a)
						part[t] = fold(&a)
"""
Q1_MT_NEW = """					if q1 {
						var a Q1Acc
						if v == "mt_1p" {
							q1OnePass(c, lo, hi, &a)
						} else {
							q1Tuned(c, lo, hi, &a)
						}
						part[t] = fold(&a)
"""


def exp(text):
    text = fix(text)
    text = sub(text, '\t"fmt"\n', '\t"fmt"\n\t"math/bits"\n')
    text = sub(text, "var sink []float32\n", K5R)
    text = sub(text, K5_CALL_OLD, K5_CALL_NEW)
    text = sub(text, "func runK9(v string, reps int) {\n", K9V)
    text = sub(text, K9_CALL_OLD, K9_CALL_NEW)
    q1 = open(os.path.join(HERE, "q1_onepass.go.txt")).read()
    text = sub(text, "func fold(a *Q1Acc) int64 {\n", q1 + "func fold(a *Q1Acc) int64 {\n")
    text = sub(text, Q1_CASE_OLD, Q1_CASE_NEW)
    text = sub(text, Q1_MT_OLD, Q1_MT_NEW)
    return text


# ------------------------------------------------------------------ copie sans GOEXPERIMENT (go_noexp)
K8IT = """// sensibilité tuned_it (remarque sur Go) : construction et somme itératives, piles explicites ; même ordre préfixe et
// mêmes valeurs que aBuild et aSum (comme la copie c_k8it de la remarque sur C)
func aBuildIt(a []ANode, depth int, q int64) int32 {
	var stP, stD [64]int32
	sp, nxt, parent, d := 0, int32(0), int32(-1), int32(depth)
	right := false
	for {
		i := nxt
		nxt++
		a[i] = ANode{q + int64(i), -1, -1}
		if parent >= 0 {
			if right {
				a[parent].r = i
			} else {
				a[parent].l = i
			}
		}
		if d > 0 {
			stP[sp], stD[sp] = i, d-1
			sp++
			parent, right, d = i, false, d-1
		} else {
			if sp == 0 {
				break
			}
			sp--
			parent, d, right = stP[sp], stD[sp], true
		}
	}
	return 0
}
func aSumIt(a []ANode, root int32) int64 {
	var st [64]int32
	sp := 0
	st[sp] = root
	sp++
	s := int64(0)
	for sp > 0 {
		sp--
		n := a[st[sp]]
		s += n.v
		if n.l >= 0 {
			st[sp] = n.r
			sp++
			st[sp] = n.l
			sp++
		}
	}
	return s
}

var keepAlive *Node
"""
K8_CALL_OLD = """			if v == "tuned" {
				arena = arena[:0]
				root := aBuild(&arena, 10, &c)
				s = aSum(arena, root)
			} else {
"""
K8_CALL_NEW = """			if v == "tuned" {
				arena = arena[:0]
				root := aBuild(&arena, 10, &c)
				s = aSum(arena, root)
			} else if v == "tuned_it" {
				arena = arena[:2047]
				root := aBuildIt(arena, 10, c)
				s = aSumIt(arena, root)
			} else {
"""


def noexp(text_std, text_k9h):
    """Copie standard (bench/go_std) avec la fonction runK9 de bench/go_k9h (harnais commun) et K8 tuned_it."""
    a = text_k9h.index("func runK9(v string, reps int) {\n")
    b = text_k9h.index(K10)
    new_k9 = text_k9h[a:b]
    a2 = text_std.index("func runK9(v string, reps int) {\n")
    b2 = text_std.index(K10)
    text = text_std[:a2] + new_k9 + text_std[b2:]
    text = sub(text, "var keepAlive *Node\n", K8IT)
    text = sub(text, K8_CALL_OLD, K8_CALL_NEW)
    return text


def copy(src, dst, text, build=None):
    d = os.path.join(ROOT, "bench", dst)
    if os.path.exists(d):
        shutil.rmtree(d)
    os.makedirs(d)
    s = os.path.join(ROOT, "bench", src)
    for f in ("build.sh", "run", "go.mod"):
        shutil.copy2(os.path.join(s, f), os.path.join(d, f))
    if build:
        shutil.copy2(os.path.join(ROOT, "bench", build, "build.sh"), os.path.join(d, "build.sh"))
    open(os.path.join(d, "ms.go"), "w", encoding="utf-8").write(text)
    print(dst, "écrit")


def main():
    read = lambda n: open(os.path.join(ROOT, "bench", n, "ms.go"), encoding="utf-8").read()  # noqa: E731
    k9h, std = read("go_k9h"), read("go_std")
    copy("go_k9h", "go_ref", k9h)
    copy("go_k9h", "go_fix", fix(k9h))
    copy("go_k9h", "go_exp", exp(k9h))
    copy("go_std", "go_noexp", noexp(std, k9h))
    open(os.path.join(ROOT, "bench", "go_exp", "extra_variants"), "w").write(
        "k5 tuned_r\nk9 tuned_vec\nk9 mt_vec\nk6 tuned_1p q1\nk6 mt_1p q1\n")
    open(os.path.join(ROOT, "bench", "go_noexp", "extra_variants"), "w").write("k8 tuned_it\n")
    d = os.path.join(ROOT, "bench", "go_nopre")
    if os.path.exists(d):
        shutil.rmtree(d)
    os.makedirs(d)
    run = os.path.join(d, "run")
    open(run, "w").write('#!/bin/sh\n# binaire de go_ref, préemption asynchrone désactivée (information, docs/GO.md)\n'
                         'GODEBUG=asyncpreemptoff=1 exec "$(dirname "$0")/../go_ref/ms" "$@"\n')
    os.chmod(run, 0o755)
    print("go_nopre écrit")


if __name__ == "__main__":
    main()
