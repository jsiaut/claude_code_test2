// Implémentation Odin (dev-2026-10, bibliothèques core/base seules). Voir docs/SPEC.md.
package ms

import "base:intrinsics"
import "core:fmt"
import "core:mem"
import "core:os"
import "core:simd"
import "core:slice"
import "core:strconv"
import "core:sync"
import "core:sync/chan"
import "core:thread"
import "core:time"

// ------------------------------------------------------------------ harnais
WARMUP := 1
DATA := "/opt/msdata"

load_bytes :: proc(name: string) -> []byte {
	data, err := os.read_entire_file(fmt.tprintf("%s/%s", DATA, name), context.allocator)
	assert(err == nil)
	// copie dans un tampon aligné sur 64 octets
	a, _ := mem.make_aligned([]byte, len(data), 64)
	copy(a, data)
	delete(data)
	return a
}
load :: proc($T: typeid, name: string) -> []T {
	return slice.reinterpret([]T, load_bytes(name))
}
result :: proc(k, v, p: string, rep: int, sec: f64, chk: string) {
	fmt.printf("RESULT;%s;%s;%s;%d;%.9f;%s\n", k, v, p, rep, sec, chk)
}
secs :: proc(t0: time.Tick) -> f64 {return time.duration_seconds(time.tick_since(t0))}

// ------------------------------------------------------------------ K1
N1 :: 1 << 22
Particle :: struct {
	x, y, z, vx, vy, vz, ax, ay, az, mass, charge, radius, temp, pressure, energy, density: f32,
}
k1_natural :: proc(ps: []Particle) -> f64 {
	e: f64
	for p in ps do e += 0.5 * f64(p.mass) * f64(p.vx * p.vx + p.vy * p.vy + p.vz * p.vz)
	return e
}
@(optimization_mode = "favor_size") // empêche l'inlining agressif de la boucle mesurée (comme noinline)
k1_aos :: proc(ps: []Particle) -> f64 #no_bounds_check {
	acc: [8]f64
	for i := 0; i < len(ps); i += 8 {
		#unroll for k in 0 ..< 8 {
			q := &ps[i + k]
			acc[k] += f64(0.5 * q.mass * (q.vx * q.vx + q.vy * q.vy + q.vz * q.vz))
		}
	}
	e: f64
	for a in acc do e += a
	return e
}
// SoA : tranche #soa intégrée au langage + vecteurs #simd[16]f32
k1_soa :: proc(ps: #soa[]Particle) -> f64 #no_bounds_check {
	V :: #simd[16]f32
	D :: #simd[8]f64
	a0, a1: D
	h := V(0.5)
	vx, vy, vz, m := ps.vx, ps.vy, ps.vz, ps.mass // pointeurs vers les colonnes
	for i := 0; i < len(ps); i += 16 {
		x := intrinsics.unaligned_load((^V)(&vx[i]))
		y := intrinsics.unaligned_load((^V)(&vy[i]))
		z := intrinsics.unaligned_load((^V)(&vz[i]))
		w := intrinsics.unaligned_load((^V)(&m[i]))
		e := h * w * simd.fma(z, z, simd.fma(y, y, x * x))
		ea := simd.to_array(e)
		lo := simd.from_array([8]f32{ea[0], ea[1], ea[2], ea[3], ea[4], ea[5], ea[6], ea[7]})
		hi := simd.from_array([8]f32{ea[8], ea[9], ea[10], ea[11], ea[12], ea[13], ea[14], ea[15]})
		a0 += cast(D)lo
		a1 += cast(D)hi
	}
	return simd.reduce_add_pairs(a0 + a1)
}
// Empreinte K1 (D2a) : RSS courant en octets (/proc/self/statm, 2e champ ; pages de 4 Kio)
rss_now :: proc() -> int {
	data, err := os.read_entire_file("/proc/self/statm", context.temp_allocator)
	if err != nil {return 0}
	s := string(data)
	i := 0
	for i < len(s) && s[i] != ' ' do i += 1
	j := i + 1
	for j < len(s) && s[j] != ' ' do j += 1
	if j > len(s) {return 0}
	res, _ := strconv.parse_int(s[i + 1:j])
	return res * 4096
}
run_k1 :: proc(v: string, reps: int) {
	if v == "footprint0" {result("k1", v, "energy", 0, 0, "0"); return}
	raw := load(f32, "k1_particles.f32")
	if v == "footprint_raw" {result("k1", v, "energy", 0, 0, "0"); return}
	m1 := v == "footprint" ? rss_now() : 0 // P1 : tampon brut chargé
	ps := make([dynamic]Particle, 0, N1)
	for i in 0 ..< N1 do append(&ps, (cast(^Particle)&raw[16 * i])^)
	if v == "footprint" { // P2 : collection construite, tampon brut encore vivant
		m2 := rss_now()
		fmt.printf("META;mem;rss;%d;%d\nMETA;rss;%d;%d\nMETA;raw0;%v\n", m1, m2, m1, m2, raw[0])
	}
	delete(slice.reinterpret([]byte, raw))
	switch v {
	case "footprint":
		result("k1", v, "energy", 0, 0, fmt.tprintf("%.6f", k1_natural(ps[:])))
	case "soa":
		s := make_soa(#soa[]Particle, N1)
		for p, i in ps do s[i] = p
		delete(ps)
		for r := -WARMUP; r < reps; r += 1 {
			t0 := time.tick_now()
			e := k1_soa(s)
			dt := secs(t0)
			if r >= 0 do result("k1", v, "energy", r, dt, fmt.tprintf("%.6f", e))
		}
	case:
		if v == "natural_shuffled" {
			perm := load(u32, "k1_perm.u32")
			s := make([dynamic]Particle, N1)
			for j, i in perm do s[i] = ps[j]
			delete(ps)
			ps = s
		}
		aos := v == "aos"
		for r := -WARMUP; r < reps; r += 1 {
			t0 := time.tick_now()
			e := aos ? k1_aos(ps[:]) : k1_natural(ps[:])
			dt := secs(t0)
			if r >= 0 do result("k1", v, "energy", r, dt, fmt.tprintf("%.6f", e))
		}
	}
}

// ------------------------------------------------------------------ K2
k2_chase :: proc(a: []u32, h: int) -> u32 #no_bounds_check {
	i: u32 = 0
	for _ in 0 ..< h do i = a[i]
	return i
}
run_k2 :: proc(v: string, reps: int, p: string) {
	a := load(u32, fmt.tprintf("k2_chase_%s.u32", p))
	for r := -WARMUP; r < reps; r += 1 {
		t0 := time.tick_now()
		i := k2_chase(a, 4200000)
		dt := secs(t0)
		if r >= 0 do result("k2", v, p, r, dt, fmt.tprintf("%d", i))
	}
}

// ------------------------------------------------------------------ K3
ITER3 :: 1 << 25
Padded :: struct #align (128) {
	v: u64,
}
Packed4 :: struct #align (64) {
	v: [4]u64,
}
k3_worker :: proc(c: ^u64, rmw: bool) {
	if rmw {
		for _ in 0 ..< ITER3 do intrinsics.atomic_add_explicit(c, 1, .Relaxed)
	} else {
		for _ in 0 ..< ITER3 do intrinsics.atomic_store_explicit(c, intrinsics.atomic_load_explicit(c, .Relaxed) + 1, .Relaxed)
	}
}
run_k3 :: proc(v: string, reps: int) {
	rmw := v[:3] == "rmw"
	padded := v[len(v) - 6:] == "padded"
	fmt.printf("META;k3_mechanism;%s\n", rmw ? "atomic_add_explicit(.Relaxed) (lock xadd)" : "atomic_load/store_explicit(.Relaxed) (mov)")
	packed: Packed4
	pad: [4]Padded
	for r := -WARMUP; r < reps; r += 1 {
		ctr: [4]^u64
		for t in 0 ..< 4 {
			ctr[t] = padded ? &pad[t].v : &packed.v[t]
			ctr[t]^ = 0
		}
		t0 := time.tick_now()
		th: [4]^thread.Thread
		for t in 0 ..< 4 do th[t] = thread.create_and_start_with_poly_data2(ctr[t], rmw, k3_worker)
		for t in th {thread.join(t); thread.destroy(t)}
		dt := secs(t0)
		s: u64
		for c in ctr do s += c^
		if r >= 0 do result("k3", v, "4x2^25", r, dt, fmt.tprintf("%d", s))
	}
}

// ------------------------------------------------------------------ K4
k4_natural :: proc(v: []u8) -> u64 {
	s: u64
	for x in v do if x >= 128 do s += u64(x)
	return s
}
k4_branchless :: proc(v: []u8) -> u64 {
	s: u64
	for x in v do s += u64(x) * u64(x >> 7)
	return s
}
run_k4 :: proc(v: string, reps: int) {
	d := load(u8, "k4_bytes.u8")
	if v == "natural_sorted" do slice.sort(d)
	bl := v == "branchless_unsorted"
	for r := -WARMUP; r < reps; r += 1 {
		t0 := time.tick_now()
		s := bl ? k4_branchless(d) : k4_natural(d)
		dt := secs(t0)
		if r >= 0 do result("k4", v, "16M", r, dt, fmt.tprintf("%d", s))
	}
}

// ------------------------------------------------------------------ K5
INNER5 :: 1 << 16
k5_natural :: proc(a, b: []f32) -> f32 {
	s: f32
	for i in 0 ..< len(a) do s += a[i] * b[i]
	return s
}
k5_tuned :: proc(a, b: []f32) -> f32 #no_bounds_check {
	V :: #simd[16]f32
	s0, s1, s2, s3: V
	for i := 0; i < len(a); i += 64 {
		s0 = simd.fma((^V)(&a[i])^, (^V)(&b[i])^, s0)
		s1 = simd.fma((^V)(&a[i + 16])^, (^V)(&b[i + 16])^, s1)
		s2 = simd.fma((^V)(&a[i + 32])^, (^V)(&b[i + 32])^, s2)
		s3 = simd.fma((^V)(&a[i + 48])^, (^V)(&b[i + 48])^, s3)
	}
	return simd.reduce_add_pairs((s0 + s1) + (s2 + s3))
}
sink_a: []f32
run_k5 :: proc(v: string, reps: int) {
	a := load(f32, "k5_a.f32")
	b := load(f32, "k5_b.f32")
	tuned := v == "tuned"
	for r := -WARMUP; r < reps; r += 1 {
		d: f32
		t0 := time.tick_now()
		for _ in 0 ..< INNER5 {
			intrinsics.volatile_store(&sink_a, a) // barrière : a relu via une écriture volatile
			aa := intrinsics.volatile_load(&sink_a)
			d = tuned ? k5_tuned(aa, b) : k5_natural(aa, b)
		}
		dt := secs(t0)
		if r >= 0 do result("k5", v, "2048x65536", r, dt, fmt.tprintf("%.4f", d))
	}
}

// ------------------------------------------------------------------ K6
N6 :: 1 << 24
Cols :: struct {
	sd, pr:          []i32,
	q, d, t, rf, ls: []u8,
}
Q1Acc :: [6][5]i64
q6_natural :: proc(c: ^Cols, lo, hi: int) -> i64 {
	s: i64
	for i in lo ..< hi {
		if c.sd[i] >= 8766 && c.sd[i] < 9131 && c.d[i] >= 5 && c.d[i] <= 7 && c.q[i] < 24 do s += i64(c.pr[i]) * i64(c.d[i])
	}
	return s
}
q6_tuned :: proc(c: ^Cols, lo, hi: int) -> i64 #no_bounds_check {
	I :: #simd[16]i32
	L :: #simd[16]i64
	acc: L
	i := lo
	for ; i + 16 <= hi; i += 16 {
		sd := (^I)(&c.sd[i])^
		d := cast(I)(^#simd[16]u8)(&c.d[i])^
		q := cast(I)(^#simd[16]u8)(&c.q[i])^
		pr := (^I)(&c.pr[i])^
		m := simd.lanes_ge(sd, 8766) & simd.lanes_lt(sd, 9131) & simd.lanes_ge(d, 5) & simd.lanes_le(d, 7) & simd.lanes_lt(q, 24)
		acc += cast(L)simd.select(m, pr * d, I(0))
	}
	return simd.reduce_add_pairs(acc) + q6_natural(c, i, hi)
}
q1_natural :: proc(c: ^Cols, lo, hi: int, acc: ^Q1Acc) {
	for i in lo ..< hi {
		if c.sd[i] <= 10471 {
			g := c.rf[i] * 2 + c.ls[i]
			p := i64(c.pr[i])
			dp := p * (100 - i64(c.d[i]))
			acc[g][0] += 1
			acc[g][1] += i64(c.q[i])
			acc[g][2] += p
			acc[g][3] += dp
			acc[g][4] += dp * (100 + i64(c.t[i]))
		}
	}
}
q1_tuned :: proc(c: ^Cols, lo, hi: int, acc: ^Q1Acc) #no_bounds_check {
	I :: #simd[16]i32
	L :: #simd[16]i64
	i := lo
	for i + 16 <= hi {
		aq, ap, adp: [6]I
		ach: [6]L
		cnt: [6]i64
		end := i + 4096 <= hi ? i + 4096 : hi - (hi - i) % 16
		for ; i < end; i += 16 {
			pass := simd.lanes_le((^I)(&c.sd[i])^, 10471)
			vg := cast(I)(^#simd[16]u8)(&c.rf[i])^ * 2 + cast(I)(^#simd[16]u8)(&c.ls[i])^
			vq := cast(I)(^#simd[16]u8)(&c.q[i])^
			vd := cast(I)(^#simd[16]u8)(&c.d[i])^
			vt := cast(I)(^#simd[16]u8)(&c.t[i])^ + 100
			vp := (^I)(&c.pr[i])^
			vdp := vp * (100 - vd)
			ch := cast(L)vdp * cast(L)vt
			#unroll for g in 0 ..< 6 {
				m := pass & simd.lanes_eq(vg, I(g))
				cnt[g] += i64(simd.reduce_add_pairs(m & 1))
				aq[g] += simd.select(m, vq, I(0))
				ap[g] += simd.select(m, vp, I(0))
				adp[g] += simd.select(m, vdp, I(0))
				ach[g] += simd.select(cast(L)m, ch, L(0))
			}
		}
		for g in 0 ..< 6 {
			acc[g][0] += cnt[g]
			acc[g][1] += i64(simd.reduce_add_pairs(aq[g]))
			acc[g][2] += i64(simd.reduce_add_pairs(ap[g]))
			acc[g][3] += simd.reduce_add_pairs(cast(L)adp[g])
			acc[g][4] += simd.reduce_add_pairs(ach[g])
		}
	}
	if i < hi do q1_natural(c, i, hi, acc)
}
fold :: proc(a: ^Q1Acc) -> i64 {
	s: i64
	for row in a do for x in row do s += x
	return s
}
K6Job :: struct {
	c:      ^Cols,
	lo, hi: int,
	q1:     bool,
	res:    i64,
}
k6_worker :: proc(j: ^K6Job) {
	if j.q1 {a: Q1Acc; q1_tuned(j.c, j.lo, j.hi, &a); j.res = fold(&a)} else do j.res = q6_tuned(j.c, j.lo, j.hi)
}
run_k6 :: proc(v: string, reps: int, p: string) {
	c := Cols{load(i32, "k6_shipdate.i32"), load(i32, "k6_extendedprice.i32"), load(u8, "k6_quantity.u8"), load(u8, "k6_discount.u8"), load(u8, "k6_tax.u8"), load(u8, "k6_returnflag.u8"), load(u8, "k6_linestatus.u8")}
	q1 := p == "q1"
	for r := -WARMUP; r < reps; r += 1 {
		t0 := time.tick_now()
		s: i64
		switch v {
		case "mt":
			jobs: [4]K6Job
			th: [4]^thread.Thread
			for t in 0 ..< 4 {
				jobs[t] = {&c, N6 / 4 * t, N6 / 4 * (t + 1), q1, 0}
				th[t] = thread.create_and_start_with_poly_data(&jobs[t], k6_worker)
			}
			for t in 0 ..< 4 {thread.join(th[t]); thread.destroy(th[t]); s += jobs[t].res}
		case "tuned":
			if q1 {a: Q1Acc; q1_tuned(&c, 0, N6, &a); s = fold(&a)} else do s = q6_tuned(&c, 0, N6)
		case:
			if q1 {a: Q1Acc; q1_natural(&c, 0, N6, &a); s = fold(&a)} else do s = q6_natural(&c, 0, N6)
		}
		dt := secs(t0)
		if r >= 0 do result("k6", v, p, r, dt, fmt.tprintf("%d", s))
	}
}

// ------------------------------------------------------------------ K7
Agg :: struct {
	count: u32,
	sum:   u64,
}
Slot :: struct {
	key, count: u32,
	sum:        u64,
}
run_k7 :: proc(v: string, reps: int) {
	keys := load(u32, "k7_keys.u32")
	vals := load(u32, "k7_vals.u32")
	for r := -WARMUP; r < reps; r += 1 {
		nk, ws: u64
		dt: f64
		if v == "natural" {
			t0 := time.tick_now()
			m := make(map[u32]Agg)
			for k, i in keys {
				if e, ok := &m[k]; ok {e.count += 1; e.sum += u64(vals[i])} else {m[k] = Agg{1, u64(vals[i])}}
			}
			dt = secs(t0)
			nk = u64(len(m))
			for k, e in m do ws += e.sum * u64((k & 1023) + 1)
			delete(m)
		} else {
			LOG :: 21
			CAP :: 1 << LOG
			t0 := time.tick_now()
			tab, _ := mem.make_aligned([]Slot, CAP, 64)
			for i := 0; i < len(keys); i += 16 {
				h: [16]u32
				#unroll for b in 0 ..< 16 {
					h[b] = (keys[i + b] * 0x9E3779B1) >> (32 - LOG)
					intrinsics.prefetch_write_data(&tab[h[b]], 3)
				}
				#unroll for b in 0 ..< 16 {
					k := keys[i + b]
					s := h[b]
					for tab[s].count != 0 && tab[s].key != k do s = (s + 1) & (CAP - 1)
					tab[s].key = k
					tab[s].count += 1
					tab[s].sum += u64(vals[i + b])
				}
			}
			dt = secs(t0)
			for e in tab do if e.count != 0 {nk += 1; ws += e.sum * u64((e.key & 1023) + 1)}
			delete(tab)
		}
		if r >= 0 do result("k7", v, "16M/1M", r, dt, fmt.tprintf("%d:%d", nk, ws))
	}
}

// ------------------------------------------------------------------ K8
Node :: struct {
	v:    i64,
	l, r: ^Node,
}
t_build :: proc(d: int, c: ^i64) -> ^Node {
	n := new(Node) // allocateur implicite du contexte
	n.v = c^
	c^ += 1
	if d > 0 {n.l = t_build(d - 1, c); n.r = t_build(d - 1, c)}
	return n
}
t_sum :: proc(n: ^Node) -> i64 {return n == nil ? 0 : n.v + t_sum(n.l) + t_sum(n.r)}
t_free :: proc(n: ^Node) {if n != nil {t_free(n.l); t_free(n.r); free(n)}}
ANode :: struct {
	v:    i64,
	l, r: i32,
}
a_build :: proc(a: ^[2047]ANode, top: ^i32, d: int, c: ^i64) -> i32 #no_bounds_check {
	i := top^
	top^ += 1
	a[i] = {c^, -1, -1}
	c^ += 1
	if d > 0 {l := a_build(a, top, d - 1, c); a[i].l = l; a[i].r = a_build(a, top, d - 1, c)}
	return i
}
a_sum :: proc(a: ^[2047]ANode, i: i32) -> i64 #no_bounds_check {return i < 0 ? 0 : a[i].v + a_sum(a, a[i].l) + a_sum(a, a[i].r)}
run_k8 :: proc(v: string, reps: int) {
	Q :: 16384
	tuned, talloc := v == "tuned", v == "tuned_alloc"
	arena := new([2047]ANode)
	c0: i64
	keep := t_build(20, &c0)
	lsum := t_sum(keep)
	lat := make([]i64, Q)
	for r := -WARMUP; r < reps; r += 1 {
		total: i64
		t0 := time.tick_now()
		for q in 0 ..< Q {
			a := time.tick_now()
			c := i64(q)
			s: i64
			if tuned { // nœuds compacts indexés dans un tableau réutilisé (DOD)
				top: i32 = 0
				s = a_sum(arena, a_build(arena, &top, 10, &c))
			} else if talloc {
				// arène : idiome Odin « par trame » -> allocateur temporaire du contexte,
				// libéré en bloc (l'arène vmem.Arena, protégée par mutex, est 2x plus lente : mesuré)
				context.allocator = context.temp_allocator
				s = t_sum(t_build(10, &c))
				free_all(context.temp_allocator)
			} else {
				t := t_build(10, &c)
				s = t_sum(t)
				t_free(t)
			}
			total += s
			lat[q] = i64(time.tick_since(a))
		}
		dt := secs(t0)
		if r >= 0 {
			result("k8", v, "16384x2047", r, dt, fmt.tprintf("%d", total + lsum))
			slice.sort(lat)
			fmt.printf("LAT;%s;%d;%d;%d;%d;%d\n", v, lat[Q / 2], lat[Q * 9 / 10], lat[Q * 99 / 100], lat[Q * 999 / 1000], lat[Q - 1])
		}
	}
	t_free(keep)
}

// ------------------------------------------------------------------ K9
M9 :: 2048
k9_init :: proc(i, j: int) -> f64 {return f64((i * 31 + j * 17) % 1024) / 1024.0}
// naturel : tableau 2D de taille fixe (contigu)
k9_natural :: proc(a, b: ^[M9][M9]f64) {
	for i in 1 ..< M9 - 1 do for j in 1 ..< M9 - 1 do b[i][j] = 0.25 * (((a[i - 1][j] + a[i + 1][j]) + a[i][j - 1]) + a[i][j + 1])
}
k9_rows :: proc(a, b: []f64, r0, r1: int) #no_bounds_check {
	V :: #simd[8]f64
	for i in r0 ..< r1 {
		up, mid, dn, o := a[(i - 1) * M9:], a[i * M9:], a[(i + 1) * M9:], b[i * M9:]
		j := 1
		for ; j + 8 <= M9 - 1; j += 8 {
			ld :: intrinsics.unaligned_load
			intrinsics.unaligned_store((^V)(&o[j]), V(0.25) * (((ld((^V)(&up[j])) + ld((^V)(&dn[j]))) + ld((^V)(&mid[j - 1]))) + ld((^V)(&mid[j + 1]))))
		}
		for ; j < M9 - 1; j += 1 do o[j] = 0.25 * (((up[j] + dn[j]) + mid[j - 1]) + mid[j + 1])
	}
}
K9Job :: struct {
	a, b:   []f64,
	r0, r1: int,
}
run_k9 :: proc(v: string, reps: int) {
	for r := -WARMUP; r < reps; r += 1 {
		s, dt: f64
		if v == "natural" {
			a, b := new([M9][M9]f64), new([M9][M9]f64)
			for i in 0 ..< M9 do for j in 0 ..< M9 {a[i][j] = k9_init(i, j); b[i][j] = a[i][j]}
			t0 := time.tick_now()
			for _ in 0 ..< 4 {k9_natural(a, b); a, b = b, a}
			dt = secs(t0)
			for i in 0 ..< M9 do for j in 0 ..< M9 do s += a[i][j]
			free(a); free(b)
		} else {
			a, _ := mem.make_aligned([]f64, M9 * M9, 64)
			b, _ := mem.make_aligned([]f64, M9 * M9, 64)
			for k in 0 ..< M9 * M9 {a[k] = k9_init(k / M9, k % M9); b[k] = a[k]}
			t0 := time.tick_now()
			for _ in 0 ..< 4 {
				if v == "tuned" {k9_rows(a, b, 1, M9 - 1)} else {
					jobs: [4]K9Job
					th: [4]^thread.Thread
					for t in 0 ..< 4 {
						jobs[t] = {a, b, 1 + (M9 - 2) * t / 4, 1 + (M9 - 2) * (t + 1) / 4}
						th[t] = thread.create_and_start_with_poly_data(&jobs[t], proc(j: ^K9Job) {k9_rows(j.a, j.b, j.r0, j.r1)})
					}
					for t in th {thread.join(t); thread.destroy(t)}
				}
				a, b = b, a
			}
			dt = secs(t0)
			for x in a do s += x
			delete(a); delete(b)
		}
		if r >= 0 do result("k9", v, "2048^2x4", r, dt, fmt.tprintf("%.15e", s))
	}
}

// ------------------------------------------------------------------ K10
M10 :: 1 << 22
CAP10 :: 1 << 14
Spsc :: struct #align (128) {
	write_idx: int,
	_:         [120]u8,
	read_idx:  int,
	_:         [120]u8,
	buf:       [CAP10]u64,
}
spsc_prod :: proc(q: ^Spsc) {
	w, rc := 0, 0
	for x in 1 ..= u64(M10) {
		for w - rc == CAP10 {
			rc = intrinsics.atomic_load_explicit(&q.read_idx, .Acquire)
			if w - rc == CAP10 do intrinsics.cpu_relax()
		}
		q.buf[w & (CAP10 - 1)] = x
		w += 1
		intrinsics.atomic_store_explicit(&q.write_idx, w, .Release)
	}
}
SpscCons :: struct {
	q:   ^Spsc,
	res: u64,
}
spsc_cons :: proc(j: ^SpscCons) {
	rd, wc := 0, 0
	s: u64
	for _ in 0 ..< M10 {
		for rd == wc {
			wc = intrinsics.atomic_load_explicit(&j.q.write_idx, .Acquire)
			if rd == wc do intrinsics.cpu_relax()
		}
		s += j.q.buf[rd & (CAP10 - 1)]
		rd += 1
		intrinsics.atomic_store_explicit(&j.q.read_idx, rd, .Release)
	}
	j.res = s
}
ChanJob :: struct {
	c:   chan.Chan(u64),
	res: u64,
}
run_k10 :: proc(v: string, reps: int) {
	for r := -WARMUP; r < reps; r += 1 {
		s: u64
		t0 := time.tick_now()
		if v == "natural" { // core:sync/chan : canal borné de la bibliothèque
			c, _ := chan.create_buffered(chan.Chan(u64), CAP10, context.allocator)
			job := ChanJob{c, 0}
			cons := thread.create_and_start_with_poly_data(&job, proc(j: ^ChanJob) {
				for _ in 0 ..< M10 {x, _ := chan.recv(j.c); j.res += x}
			})
			prod := thread.create_and_start_with_poly_data(&job, proc(j: ^ChanJob) {
				for x in 1 ..= u64(M10) do chan.send(j.c, x)
			})
			thread.join(prod); thread.join(cons)
			thread.destroy(prod); thread.destroy(cons)
			s = job.res
			chan.destroy(c)
		} else {
			q := new(Spsc)
			job := SpscCons{q, 0}
			cons := thread.create_and_start_with_poly_data(&job, spsc_cons)
			prod := thread.create_and_start_with_poly_data(q, spsc_prod)
			thread.join(prod); thread.join(cons)
			thread.destroy(prod); thread.destroy(cons)
			s = job.res
			free(q)
		}
		dt := secs(t0)
		if r >= 0 do result("k10", v, "2^22", r, dt, fmt.tprintf("%d", s))
	}
}

main :: proc() {
	if w, ok := os.lookup_env("WARMUP", context.allocator); ok do WARMUP, _ = strconv.parse_int(w)
	if d, ok := os.lookup_env("MS_DATA", context.allocator); ok do DATA = d
	k, v := os.args[1], os.args[2]
	reps, _ := strconv.parse_int(os.args[3])
	p := len(os.args) > 4 ? os.args[4] : ""
	switch k {
	case "k1": run_k1(v, reps)
	case "k2": run_k2(v, reps, p)
	case "k3": run_k3(v, reps)
	case "k4": run_k4(v, reps)
	case "k5": run_k5(v, reps)
	case "k6": run_k6(v, reps, p)
	case "k7": run_k7(v, reps)
	case "k8": run_k8(v, reps)
	case "k9": run_k9(v, reps)
	case "k10": run_k10(v, reps)
	}
}
