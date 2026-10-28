// Implémentation C3 0.8.5 (bibliothèque standard seule). Voir docs/SPEC.md.
module ms;
import std::io, std::io::file, std::time, std::thread, std::thread::channel, std::collections::map;
import std::atomic, std::math, std::os::env, std::sort, std::core::mem;

// ------------------------------------------------------------------ harnais
int g_warmup = 1;
String g_data = "/opt/msdata";

fn char[] load_bytes(String name)
{
	char[] raw = file::load(mem, string::tformat("%s/%s", g_data, name))!!;
	char* a = alloc::malloc_aligned(mem, raw.len + 64, 64)!!; // copie alignée sur une ligne de cache
	mem::copy(a, raw.ptr, raw.len);
	free(raw.ptr);
	return a[:raw.len];
}
macro load($Type, String name)
{
	char[] b = load_bytes(name);
	return (($Type*)b.ptr)[:b.len / $Type::size];
}
fn void result(String k, String v, String p, int rep, double sec, String chk)
{
	io::printfn("RESULT;%s;%s;%s;%d;%.9f;%s", k, v, p, rep, sec, chk);
}
fn double secs(Clock t0) => (double)t0.to_now() * 1e-9;

// ------------------------------------------------------------------ K1
const N1 = 1 << 22;
struct Particle
{
	float x, y, z, vx, vy, vz, ax, ay, az, mass, charge, radius, temp, pressure, energy, density;
}
fn double k1_natural(Particle[] ps) @noinline
{
	double e;
	foreach (&p : ps) e += (double)(0.5f * p.mass * (p.vx * p.vx + p.vy * p.vy + p.vz * p.vz));
	return e;
}
fn double k1_aos(Particle[] ps) @noinline
{
	double[8] acc;
	for (usz i = 0; i < ps.len; i += 8)
	{
		$for var $k = 0; $k < 8; $k++:
		{
			Particle* q = &ps[i + $k];
			acc[$k] += (double)(0.5f * q.mass * (q.vx * q.vx + q.vy * q.vy + q.vz * q.vz));
		}
		$endfor
	}
	double e;
	foreach (a : acc) e += a;
	return e;
}
// SoA : colonnes séparées + vecteurs natifs float[<16>]
fn double k1_soa(float* vx, float* vy, float* vz, float* m, usz n) @noinline
{
	double[<8>] a0, a1;
	float[<8>] h = 0.5f;
	for (usz i = 0; i < n; i += 16)
	{
		$for var $u = 0; $u < 2; $u++:
		{
			usz j = i + 8 * $u;
			float[<8>] x = mem::load((float[<8>]*)&vx[j], 32);
			float[<8>] y = mem::load((float[<8>]*)&vy[j], 32);
			float[<8>] z = mem::load((float[<8>]*)&vz[j], 32);
			float[<8>] w = mem::load((float[<8>]*)&m[j], 32);
			float[<8>] e = h * w * math::fma(z, z, math::fma(y, y, x * x));
			$if $u == 0:
				a0 += (double[<8>])e;
			$else
				a1 += (double[<8>])e;
			$endif
		}
		$endfor
	}
	return (a0 + a1).sum();
}
fn void run_k1(String v, int reps)
{
	if (v == "footprint0") { result("k1", v, "energy", 0, 0, "0"); return; }
	float[] raw = load(float, "k1_particles.f32");
	Particle[] ps = mem::new_array(Particle, N1);
	for (usz i = 0; i < N1; i++) ps[i] = *(Particle*)&raw[16 * i];
	if (v == "footprint") { free(raw.ptr); result("k1", v, "energy", 0, 0, string::tformat("%.6f", k1_natural(ps))); return; }
	if (v == "soa")
	{
		float*[16] c;
		for (int k = 0; k < 16; k++)
		{
			c[k] = alloc::malloc_aligned(mem, N1 * 4, 64)!!;
			for (usz i = 0; i < N1; i++) c[k][i] = raw[16 * i + (usz)k];
		}
		for (int r = -g_warmup; r < reps; r++)
		{
			Clock t0 = clock::now();
			double e = k1_soa(c[3], c[4], c[5], c[9], N1);
			double dt = secs(t0);
			if (r >= 0) result("k1", v, "energy", r, dt, string::tformat("%.6f", e));
		}
		return;
	}
	if (v == "natural_shuffled")
	{
		uint[] perm = load(uint, "k1_perm.u32");
		Particle[] s = mem::new_array(Particle, N1);
		foreach (i, j : perm) s[i] = ps[j];
		ps = s;
	}
	bool aos = v == "aos";
	for (int r = -g_warmup; r < reps; r++)
	{
		Clock t0 = clock::now();
		double e = aos ? k1_aos(ps) : k1_natural(ps);
		double dt = secs(t0);
		if (r >= 0) result("k1", v, "energy", r, dt, string::tformat("%.6f", e));
	}
}

// ------------------------------------------------------------------ K2
fn uint k2_chase(uint[] a, usz h) @noinline
{
	uint i = 0;
	for (usz k = 0; k < h; k++) i = a[i];
	return i;
}
fn void run_k2(String v, int reps, String p)
{
	uint[] a = load(uint, string::tformat("k2_chase_%s.u32", p));
	for (int r = -g_warmup; r < reps; r++)
	{
		Clock t0 = clock::now();
		uint i = k2_chase(a, 4200000);
		double dt = secs(t0);
		if (r >= 0) result("k2", v, p, r, dt, string::tformat("%d", i));
	}
}

// ------------------------------------------------------------------ K3
const ITER3 = 1 << 25;
struct Padded @align(128) { Atomic{ulong} v; }
struct K3Arg { Atomic{ulong}* c; bool rmw; }
fn int k3_worker(void* arg)
{
	K3Arg* a = arg;
	if (a.rmw)
	{
		for (int i = 0; i < ITER3; i++) a.c.add(1, RELAXED);
	}
	else
	{
		for (int i = 0; i < ITER3; i++) a.c.store(a.c.load(RELAXED) + 1, RELAXED);
	}
	return 0;
}
fn void run_k3(String v, int reps)
{
	bool rmw = v.starts_with("rmw");
	bool padded = v.ends_with("padded");
	io::printfn("META;k3_mechanism;%s", rmw ? "Atomic.add(RELAXED) (lock xadd)" : "Atomic.load/store(RELAXED) (mov)");
	Padded[4] pad;
	Atomic{ulong}[4] packed @align(64);
	for (int r = -g_warmup; r < reps; r++)
	{
		K3Arg[4] args;
		for (int t = 0; t < 4; t++)
		{
			args[t] = { padded ? &pad[t].v : &packed[t], rmw };
			args[t].c.store(0);
		}
		Clock t0 = clock::now();
		Thread[4] th;
		for (int t = 0; t < 4; t++) th[t].create(&k3_worker, &args[t])!!;
		for (int t = 0; t < 4; t++) th[t].join()!!;
		double dt = secs(t0);
		ulong s;
		for (int t = 0; t < 4; t++) s += args[t].c.load();
		if (r >= 0) result("k3", v, "4x2^25", r, dt, string::tformat("%d", s));
	}
}

// ------------------------------------------------------------------ K4
fn ulong k4_natural(char[] v) @noinline
{
	ulong s;
	foreach (x : v) if (x >= 128) s += x;
	return s;
}
fn ulong k4_branchless(char[] v) @noinline
{
	ulong s;
	foreach (x : v) s += (ulong)x * (ulong)(x >> 7);
	return s;
}
fn void run_k4(String v, int reps)
{
	char[] d = load_bytes("k4_bytes.u8");
	if (v == "natural_sorted") sort::quicksort(d);
	bool bl = v == "branchless_unsorted";
	for (int r = -g_warmup; r < reps; r++)
	{
		Clock t0 = clock::now();
		ulong s = bl ? k4_branchless(d) : k4_natural(d);
		double dt = secs(t0);
		if (r >= 0) result("k4", v, "16M", r, dt, string::tformat("%d", s));
	}
}

// ------------------------------------------------------------------ K5
const INNER5 = 1 << 16;
fn float k5_natural(float[] a, float[] b) @noinline
{
	float s;
	for (usz i = 0; i < a.len; i++) s += a[i] * b[i];
	return s;
}
fn float k5_tuned(float[] a, float[] b) @noinline
{
	float[<16>] s0, s1, s2, s3;
	for (usz i = 0; i < a.len; i += 64)
	{
		s0 = math::fma(mem::load((float[<16>]*)&a[i], 64), mem::load((float[<16>]*)&b[i], 64), s0);
		s1 = math::fma(mem::load((float[<16>]*)&a[i + 16], 64), mem::load((float[<16>]*)&b[i + 16], 64), s1);
		s2 = math::fma(mem::load((float[<16>]*)&a[i + 32], 64), mem::load((float[<16>]*)&b[i + 32], 64), s2);
		s3 = math::fma(mem::load((float[<16>]*)&a[i + 48], 64), mem::load((float[<16>]*)&b[i + 48], 64), s3);
	}
	return ((s0 + s1) + (s2 + s3)).sum();
}
fn void run_k5(String v, int reps)
{
	float[] a = load(float, "k5_a.f32");
	float[] b = load(float, "k5_b.f32");
	bool tuned = v == "tuned";
	float* a_ptr = a.ptr;
	for (int r = -g_warmup; r < reps; r++)
	{
		float d;
		Clock t0 = clock::now();
		for (int it = 0; it < INNER5; it++)
		{
			float* pa = @volatile_load(a_ptr); // barrière d'optimisation
			d = tuned ? k5_tuned(pa[:a.len], b) : k5_natural(pa[:a.len], b);
		}
		double dt = secs(t0);
		if (r >= 0) result("k5", v, "2048x65536", r, dt, string::tformat("%.4f", d));
	}
}

// ------------------------------------------------------------------ K6
const N6 = 1 << 24;
struct Cols { int[] sd; int[] pr; char[] q; char[] d; char[] t; char[] rf; char[] ls; }
alias Q1Acc = long[5][6];
fn long q6_natural(Cols* c, usz lo, usz hi) @noinline
{
	long s;
	for (usz i = lo; i < hi; i++)
	{
		if (c.sd[i] >= 8766 && c.sd[i] < 9131 && c.d[i] >= 5 && c.d[i] <= 7 && c.q[i] < 24) s += (long)c.pr[i] * c.d[i];
	}
	return s;
}
macro int[<16>] ld8(char* p) => (int[<16>])mem::load((char[<16>]*)p, 16);
macro int[<16>] ld32(int* p) => mem::load((int[<16>]*)p, 64);
fn long q6_tuned(Cols* c, usz lo, usz hi) @noinline
{
	long[<16>] acc;
	usz i = lo;
	for (; i + 16 <= hi; i += 16)
	{
		int[<16>] sd = ld32(&c.sd[i]);
		int[<16>] d = ld8(&c.d[i]);
		int[<16>] q = ld8(&c.q[i]);
		bool[<16>] m = $$veccompge(sd, (int[<16>])8766) & $$veccomplt(sd, (int[<16>])9131) & $$veccompge(d, (int[<16>])5)
		             & $$veccomple(d, (int[<16>])7) & $$veccomplt(q, (int[<16>])24);
		int[<16>] zero;
		acc += (long[<16>])math::select(m, ld32(&c.pr[i]) * d, zero);
	}
	return acc.sum() + q6_natural(c, i, hi);
}
fn void q1_natural(Cols* c, usz lo, usz hi, Q1Acc* acc) @noinline
{
	for (usz i = lo; i < hi; i++)
	{
		if (c.sd[i] <= 10471)
		{
			int g = c.rf[i] * 2 + c.ls[i];
			long p = c.pr[i];
			long dp = p * (long)(100 - c.d[i]);
			(*acc)[g][0] += 1;
			(*acc)[g][1] += c.q[i];
			(*acc)[g][2] += p;
			(*acc)[g][3] += dp;
			(*acc)[g][4] += dp * (long)(100 + c.t[i]);
		}
	}
}
fn void q1_tuned(Cols* c, usz lo, usz hi, Q1Acc* acc) @noinline
{
	usz i = lo;
	while (i + 16 <= hi)
	{
		int[<16>][6] aq, ap, adp;
		long[<16>][6] ach;
		long[6] cnt;
		usz end = i + 4096 <= hi ? i + 4096 : hi - (hi - i) % 16;
		for (; i < end; i += 16)
		{
			bool[<16>] pass = $$veccomple(ld32(&c.sd[i]), (int[<16>])10471);
			int[<16>] vg = ld8(&c.rf[i]) * 2 + ld8(&c.ls[i]);
			int[<16>] vq = ld8(&c.q[i]);
			int[<16>] vd = ld8(&c.d[i]);
			int[<16>] vt = ld8(&c.t[i]) + 100;
			int[<16>] vp = ld32(&c.pr[i]);
			int[<16>] vdp = vp * (100 - vd);
			long[<16>] ch = (long[<16>])vdp * (long[<16>])vt;
			int[<16>] zi;
			long[<16>] zl;
			$for var $g = 0; $g < 6; $g++:
			{
				bool[<16>] m = pass & $$veccompeq(vg, (int[<16>])$g);
				cnt[$g] += math::select(m, (int[<16>])1, zi).sum();
				aq[$g] += math::select(m, vq, zi);
				ap[$g] += math::select(m, vp, zi);
				adp[$g] += math::select(m, vdp, zi);
				ach[$g] += math::select(m, ch, zl);
			}
			$endfor
		}
		for (int g = 0; g < 6; g++)
		{
			(*acc)[g][0] += cnt[g];
			(*acc)[g][1] += aq[g].sum();
			(*acc)[g][2] += ap[g].sum();
			(*acc)[g][3] += ((long[<16>])adp[g]).sum();
			(*acc)[g][4] += ach[g].sum();
		}
	}
	if (i < hi) q1_natural(c, i, hi, acc);
}
fn long fold(Q1Acc* a)
{
	long s;
	for (int g = 0; g < 6; g++) for (int k = 0; k < 5; k++) s += (*a)[g][k];
	return s;
}
struct K6Job { Cols* c; usz lo; usz hi; bool q1; long res; }
fn int k6_worker(void* arg)
{
	K6Job* j = arg;
	if (j.q1) { Q1Acc a; q1_tuned(j.c, j.lo, j.hi, &a); j.res = fold(&a); }
	else { j.res = q6_tuned(j.c, j.lo, j.hi); }
	return 0;
}
fn void run_k6(String v, int reps, String p)
{
	Cols c = { load(int, "k6_shipdate.i32"), load(int, "k6_extendedprice.i32"), load_bytes("k6_quantity.u8"), load_bytes("k6_discount.u8"),
	           load_bytes("k6_tax.u8"), load_bytes("k6_returnflag.u8"), load_bytes("k6_linestatus.u8") };
	bool q1 = p == "q1";
	for (int r = -g_warmup; r < reps; r++)
	{
		Clock t0 = clock::now();
		long s;
		if (v == "mt")
		{
			K6Job[4] jobs;
			Thread[4] th;
			for (usz t = 0; t < 4; t++)
			{
				jobs[t] = { &c, N6 / 4 * t, N6 / 4 * (t + 1), q1, 0 };
				th[t].create(&k6_worker, &jobs[t])!!;
			}
			for (int t = 0; t < 4; t++) { th[t].join()!!; s += jobs[t].res; }
		}
		else if (v == "tuned")
		{
			if (q1) { Q1Acc a; q1_tuned(&c, 0, N6, &a); s = fold(&a); } else { s = q6_tuned(&c, 0, N6); }
		}
		else
		{
			if (q1) { Q1Acc a; q1_natural(&c, 0, N6, &a); s = fold(&a); } else { s = q6_natural(&c, 0, N6); }
		}
		double dt = secs(t0);
		if (r >= 0) result("k6", v, p, r, dt, string::tformat("%d", s));
	}
}

// ------------------------------------------------------------------ K7
struct Agg { uint count; ulong sum; }
struct Slot { uint key; uint count; ulong sum; }
fn void run_k7(String v, int reps)
{
	uint[] keys = load(uint, "k7_keys.u32");
	uint[] vals = load(uint, "k7_vals.u32");
	for (int r = -g_warmup; r < reps; r++)
	{
		ulong nk, ws;
		double dt;
		if (v == "natural")
		{
			Clock t0 = clock::now();
			HashMap{uint, Agg} m;
			m.init(mem);
			foreach (i, k : keys)
			{
				if (try e = m.get_ref(k))
				{
					e.count++;
					e.sum += vals[i];
				}
				else
				{
					m.set(k, { 1, vals[i] });
				}
			}
			dt = secs(t0);
			nk = (ulong)m.len();
			m.@each(; uint k, Agg e) { ws += e.sum * (ulong)((k & 1023) + 1); };
			m.free();
		}
		else
		{
			const LOG = 21;
			const CAP = 1 << LOG;
			Clock t0 = clock::now();
			Slot* tab = alloc::calloc_aligned(mem, CAP * Slot::size, 64)!!;
			for (usz i = 0; i < keys.len; i += 16)
			{
				uint[16] h;
				$for var $b = 0; $b < 16; $b++:
				{
					h[$b] = (keys[i + $b] * 0x9E3779B1) >> (32 - LOG);
					@prefetch(&tab[h[$b]], VERY_NEAR, true);
				}
				$endfor
				$for var $b = 0; $b < 16; $b++:
				{
					uint k = keys[i + $b];
					uint s = h[$b];
					while (tab[s].count != 0 && tab[s].key != k) s = (s + 1) & (CAP - 1);
					tab[s].key = k;
					tab[s].count++;
					tab[s].sum += vals[i + $b];
				}
				$endfor
			}
			dt = secs(t0);
			for (usz s = 0; s < CAP; s++) if (tab[s].count != 0) { nk++; ws += tab[s].sum * (ulong)((tab[s].key & 1023) + 1); }
			alloc::free_aligned(mem, tab);
		}
		if (r >= 0) result("k7", v, "16M/1M", r, dt, string::tformat("%d:%d", nk, ws));
	}
}

// ------------------------------------------------------------------ K8
struct Node { long v; Node* l; Node* r; }
fn Node* t_build(Allocator a, int d, long* c)
{
	Node* n = alloc::new(a, Node);
	n.v = (*c)++;
	if (d > 0) { n.l = t_build(a, d - 1, c); n.r = t_build(a, d - 1, c); }
	return n;
}
fn long t_sum(Node* n) => n ? n.v + t_sum(n.l) + t_sum(n.r) : 0;
fn void t_free(Node* n) { if (n) { t_free(n.l); t_free(n.r); free(n); } }
struct ANode { long v; int l; int r; }
fn int a_build(ANode* a, int* top, int d, long* c)
{
	int i = (*top)++;
	a[i] = { (*c)++, -1, -1 };
	if (d > 0) { int l = a_build(a, top, d - 1, c); a[i].l = l; a[i].r = a_build(a, top, d - 1, c); }
	return i;
}
fn long a_sum(ANode* a, int i) => i < 0 ? 0 : a[i].v + a_sum(a, a[i].l) + a_sum(a, a[i].r);
fn void run_k8(String v, int reps)
{
	const Q = 16384;
	bool tuned = v == "tuned";
	bool talloc = v == "tuned_alloc";
	long c0;
	Node* keep = t_build(mem, 20, &c0);
	long lsum = t_sum(keep);
	ulong[] lat = mem::new_array(ulong, Q);
	ANode* arena = mem::new_array(ANode, 2047).ptr;
	for (int r = -g_warmup; r < reps; r++)
	{
		long total;
		Clock t0 = clock::now();
		for (int q = 0; q < Q; q++)
		{
			Clock a = clock::now();
			long c = q;
			long s;
			if (tuned)
			{
				int top = 0;
				s = a_sum(arena, a_build(arena, &top, 10, &c));
			}
			else if (talloc)
			{
				@pool() // allocateur temporaire de C3 : arène libérée en bloc à la fin de la portée
				{
					s = t_sum(t_build(tmem, 10, &c));
				};
			}
			else
			{
				Node* t = t_build(mem, 10, &c);
				s = t_sum(t);
				t_free(t);
			}
			total += s;
			lat[q] = (ulong)a.to_now();
		}
		double dt = secs(t0);
		if (r >= 0)
		{
			result("k8", v, "16384x2047", r, dt, string::tformat("%d", total + lsum));
			sort::quicksort(lat);
			io::printfn("LAT;%s;%d;%d;%d;%d;%d", v, lat[Q / 2], lat[Q * 9 / 10], lat[Q * 99 / 100], lat[Q * 999 / 1000], lat[Q - 1]);
		}
	}
	t_free(keep);
}

// ------------------------------------------------------------------ K9
const M9 = 2048;
fn double k9_init(usz i, usz j) => (double)((i * 31 + j * 17) % 1024) / 1024.0;
alias Grid = double[M9][M9];
// naturel : tableau 2D de taille fixe (contigu)
fn void k9_natural(Grid* a, Grid* b) @noinline
{
	for (usz i = 1; i < M9 - 1; i++)
	{
		for (usz j = 1; j < M9 - 1; j++) (*b)[i][j] = 0.25 * ((((*a)[i - 1][j] + (*a)[i + 1][j]) + (*a)[i][j - 1]) + (*a)[i][j + 1]);
	}
}
fn void k9_rows(double* a, double* b, usz r0, usz r1) @noinline
{
	for (usz i = r0; i < r1; i++)
	{
		double* up = a + (i - 1) * M9;
		double* mid = a + i * M9;
		double* dn = a + (i + 1) * M9;
		double* o = b + i * M9;
		usz j = 1;
		for (; j + 8 <= M9 - 1; j += 8)
		{
			double[<8>] u = mem::load((double[<8>]*)&up[j], 8);
			double[<8>] d = mem::load((double[<8>]*)&dn[j], 8);
			double[<8>] l = mem::load((double[<8>]*)&mid[j - 1], 8);
			double[<8>] rr = mem::load((double[<8>]*)&mid[j + 1], 8);
			mem::store((double[<8>]*)&o[j], 0.25 * (((u + d) + l) + rr), 8);
		}
		for (; j < M9 - 1; j++) o[j] = 0.25 * (((up[j] + dn[j]) + mid[j - 1]) + mid[j + 1]);
	}
}
struct K9Job { double* a; double* b; usz r0; usz r1; }
fn int k9_worker(void* arg) { K9Job* j = arg; k9_rows(j.a, j.b, j.r0, j.r1); return 0; }
fn void run_k9(String v, int reps)
{
	for (int r = -g_warmup; r < reps; r++)
	{
		double s;
		double dt;
		if (v == "natural")
		{
			Grid* a = mem::new(Grid);
			Grid* b = mem::new(Grid);
			for (usz i = 0; i < M9; i++) for (usz j = 0; j < M9; j++) { (*a)[i][j] = k9_init(i, j); (*b)[i][j] = (*a)[i][j]; }
			Clock t0 = clock::now();
			for (int it = 0; it < 4; it++) { k9_natural(a, b); Grid* tmp = a; a = b; b = tmp; }
			dt = secs(t0);
			for (usz i = 0; i < M9; i++) for (usz j = 0; j < M9; j++) s += (*a)[i][j];
			free(a); free(b);
		}
		else
		{
			double* a = alloc::malloc_aligned(mem, M9 * M9 * 8, 64)!!;
			double* b = alloc::malloc_aligned(mem, M9 * M9 * 8, 64)!!;
			for (usz k = 0; k < M9 * M9; k++) { a[k] = k9_init(k / M9, k % M9); b[k] = a[k]; }
			Clock t0 = clock::now();
			for (int it = 0; it < 4; it++)
			{
				if (v == "tuned")
				{
					k9_rows(a, b, 1, M9 - 1);
				}
				else
				{
					K9Job[4] jobs;
					Thread[4] th;
					for (usz t = 0; t < 4; t++)
					{
						jobs[t] = { a, b, 1 + (M9 - 2) * t / 4, 1 + (M9 - 2) * (t + 1) / 4 };
						th[t].create(&k9_worker, &jobs[t])!!;
					}
					for (int t = 0; t < 4; t++) th[t].join()!!;
				}
				double* tmp = a; a = b; b = tmp;
			}
			dt = secs(t0);
			for (usz k = 0; k < M9 * M9; k++) s += a[k];
			alloc::free_aligned(mem, a); alloc::free_aligned(mem, b);
		}
		if (r >= 0) result("k9", v, "2048^2x4", r, dt, string::tformat("%.15e", s));
	}
}

// ------------------------------------------------------------------ K10
const M10 = 1 << 22;
const CAP10 = 1 << 14;
struct Spsc @align(128)
{
	Atomic{usz} write_idx @align(128);
	Atomic{usz} read_idx @align(128);
	ulong[CAP10] buf @align(128);
}
struct SpscJob { Spsc* q; ulong res; }
fn int spsc_prod(void* arg)
{
	Spsc* q = ((SpscJob*)arg).q;
	usz w, rc;
	for (ulong x = 1; x <= M10; x++)
	{
		while (w - rc == CAP10)
		{
			rc = q.read_idx.load(ACQUIRE);

		}
		q.buf[w & (CAP10 - 1)] = x;
		q.write_idx.store(++w, RELEASE);
	}
	return 0;
}
fn int spsc_cons(void* arg)
{
	SpscJob* j = arg;
	Spsc* q = j.q;
	usz rd, wc;
	ulong s;
	for (usz k = 0; k < M10; k++)
	{
		while (rd == wc)
		{
			wc = q.write_idx.load(ACQUIRE);
		}
		s += q.buf[rd & (CAP10 - 1)];
		q.read_idx.store(++rd, RELEASE);
	}
	j.res = s;
	return 0;
}
struct ChanJob { BufferedChannel{ulong}* ch; ulong res; }
fn int chan_prod(void* arg)
{
	ChanJob* j = arg;
	for (ulong x = 1; x <= M10; x++) j.ch.push(x)!!;
	return 0;
}
fn int chan_cons(void* arg)
{
	ChanJob* j = arg;
	ulong s;
	for (usz k = 0; k < M10; k++) s += j.ch.pop()!!;
	j.res = s;
	return 0;
}
fn void run_k10(String v, int reps)
{
	for (int r = -g_warmup; r < reps; r++)
	{
		ulong s;
		Clock t0 = clock::now();
		Thread p, c;
		if (v == "natural") // std::thread::channel : canal borné de la bibliothèque standard
		{
			ChanJob j = { channel::create_buffered{ulong}(mem, CAP10)!!, 0 };
			c.create(&chan_cons, &j)!!;
			p.create(&chan_prod, &j)!!;
			p.join()!!; c.join()!!;
			s = j.res;
			j.ch.destroy();
		}
		else
		{
			Spsc* q = mem::new_aligned(Spsc);
			SpscJob j = { q, 0 };
			c.create(&spsc_cons, &j)!!;
			p.create(&spsc_prod, &j)!!;
			p.join()!!; c.join()!!;
			s = j.res;
			alloc::free_aligned(mem, q);
		}
		double dt = secs(t0);
		if (r >= 0) result("k10", v, "2^22", r, dt, string::tformat("%d", s));
	}
}

fn int main(String[] args)
{
	if (try w = env::get_var(mem, "WARMUP")) g_warmup = w.to_int()!!;
	if (try d = env::get_var(mem, "MS_DATA")) g_data = d;
	String k = args[1];
	String v = args[2];
	int reps = args[3].to_int()!!;
	String p = args.len > 4 ? args[4] : "";
	switch (k)
	{
		case "k1": run_k1(v, reps);
		case "k2": run_k2(v, reps, p);
		case "k3": run_k3(v, reps);
		case "k4": run_k4(v, reps);
		case "k5": run_k5(v, reps);
		case "k6": run_k6(v, reps, p);
		case "k7": run_k7(v, reps);
		case "k8": run_k8(v, reps);
		case "k9": run_k9(v, reps);
		case "k10": run_k10(v, reps);
	}
	return 0;
}
