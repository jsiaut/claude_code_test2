// Implémentation Rust (stable 1.99, bibliothèque standard seule) — voir docs/SPEC.md.
#![allow(unsafe_op_in_unsafe_fn)]
use std::arch::x86_64::*;
use std::cell::UnsafeCell;
use std::collections::HashMap;
use std::hint::black_box;
use std::sync::atomic::{AtomicU64, AtomicUsize, Ordering};
use std::time::Instant;

// ------------------------------------------------------------------ harnais
fn data_path(name: &str) -> String {
    format!("{}/{}", std::env::var("MS_DATA").unwrap_or("/opt/msdata".into()), name)
}
fn load_bytes(name: &str) -> Vec<u8> {
    std::fs::read(data_path(name)).expect("lecture")
}
fn load_u32(name: &str) -> Vec<u32> {
    load_bytes(name).chunks_exact(4).map(|c| u32::from_le_bytes(c.try_into().unwrap())).collect()
}
fn load_i32(name: &str) -> Vec<i32> {
    load_bytes(name).chunks_exact(4).map(|c| i32::from_le_bytes(c.try_into().unwrap())).collect()
}
fn load_f32(name: &str) -> Vec<f32> {
    load_bytes(name).chunks_exact(4).map(|c| f32::from_le_bytes(c.try_into().unwrap())).collect()
}
/// Tampon aligné sur 64 octets (une ligne de cache) : Vec d'un type #[repr(align(64))].
#[derive(Clone, Copy)]
#[repr(C, align(64))]
struct Line([u8; 64]);
struct ABuf { v: Vec<Line>, bytes: usize }
impl ABuf {
    fn from_bytes(b: &[u8]) -> ABuf {
        let mut v = vec![Line([0; 64]); b.len().div_ceil(64)];
        unsafe { std::ptr::copy_nonoverlapping(b.as_ptr(), v.as_mut_ptr() as *mut u8, b.len()) };
        ABuf { v, bytes: b.len() }
    }
    fn load(name: &str) -> ABuf { ABuf::from_bytes(&load_bytes(name)) }
    fn of<T: Copy>(src: &[T]) -> ABuf {
        ABuf::from_bytes(unsafe { std::slice::from_raw_parts(src.as_ptr() as *const u8, std::mem::size_of_val(src)) })
    }
    fn as_slice<T>(&self) -> &[T] {
        unsafe { std::slice::from_raw_parts(self.v.as_ptr() as *const T, self.bytes / std::mem::size_of::<T>()) }
    }
}
fn warmup() -> i32 {
    std::env::var("WARMUP").ok().and_then(|s| s.parse().ok()).unwrap_or(1)
}
fn result(k: &str, v: &str, p: &str, rep: i32, sec: f64, chk: &str) {
    println!("RESULT;{k};{v};{p};{rep};{sec:.9};{chk}");
}
/// Exécute `f` WARMUP fois sans mesure puis `reps` fois en mesurant.
fn bench<F: FnMut() -> String>(k: &str, v: &str, p: &str, reps: i32, mut f: F) {
    for r in -warmup()..reps {
        let t0 = Instant::now();
        let chk = f();
        let dt = t0.elapsed().as_secs_f64();
        if r >= 0 {
            result(k, v, p, r, dt, &chk);
        }
    }
}

// ------------------------------------------------------------------ K1
const N1: usize = 1 << 22;
#[derive(Clone, Copy, Default)]
#[repr(C)]
struct Particle {
    x: f32, y: f32, z: f32, vx: f32, vy: f32, vz: f32, ax: f32, ay: f32, az: f32,
    mass: f32, charge: f32, radius: f32, temp: f32, pressure: f32, energy: f32, density: f32,
}
impl Particle {
    fn from(f: &[f32]) -> Self {
        Particle {
            x: f[0], y: f[1], z: f[2], vx: f[3], vy: f[4], vz: f[5], ax: f[6], ay: f[7], az: f[8],
            mass: f[9], charge: f[10], radius: f[11], temp: f[12], pressure: f[13], energy: f[14], density: f[15],
        }
    }
}
// naturel : itérateur idiomatique, accumulation f64 séquentielle
#[inline(never)]
fn k1_natural(p: &[Particle]) -> f64 {
    p.iter().map(|q| 0.5 * q.mass as f64 * (q.vx * q.vx + q.vy * q.vy + q.vz * q.vz) as f64).sum()
}
// AoS optimisé : 8 accumulateurs indépendants (ILP), calcul f32
#[inline(never)]
fn k1_aos(p: &[Particle]) -> f64 {
    let mut acc = [0f64; 8];
    for c in p.chunks_exact(8) {
        for k in 0..8 {
            let q = &c[k];
            acc[k] += (0.5f32 * q.mass * (q.vx * q.vx + q.vy * q.vy + q.vz * q.vz)) as f64;
        }
    }
    acc.iter().sum()
}
// SoA optimisé : AVX-512 via std::arch (stable)
#[target_feature(enable = "avx512f")]
unsafe fn k1_soa(vx: &[f32], vy: &[f32], vz: &[f32], m: &[f32]) -> f64 {
    let n = vx.len();
    let (mut a0, mut a1) = (_mm512_setzero_pd(), _mm512_setzero_pd());
    let h = _mm512_set1_ps(0.5);
    let mut i = 0;
    while i < n {
        let x = _mm512_loadu_ps(vx.as_ptr().add(i));
        let y = _mm512_loadu_ps(vy.as_ptr().add(i));
        let z = _mm512_loadu_ps(vz.as_ptr().add(i));
        let w = _mm512_loadu_ps(m.as_ptr().add(i));
        let v2 = _mm512_fmadd_ps(z, z, _mm512_fmadd_ps(y, y, _mm512_mul_ps(x, x)));
        let e = _mm512_mul_ps(_mm512_mul_ps(h, w), v2);
        a0 = _mm512_add_pd(a0, _mm512_cvtps_pd(_mm512_castps512_ps256(e)));
        a1 = _mm512_add_pd(a1, _mm512_cvtps_pd(_mm256_castpd_ps(_mm512_extractf64x4_pd(_mm512_castps_pd(e), 1))));
        i += 16;
    }
    _mm512_reduce_add_pd(_mm512_add_pd(a0, a1))
}
/// Empreinte K1 (D2a) : RSS courant en octets (/proc/self/statm, 2e champ ; pages de 4 Kio)
fn rss_now() -> i64 {
    std::fs::read_to_string("/proc/self/statm")
        .ok()
        .and_then(|s| s.split_whitespace().nth(1).and_then(|x| x.parse::<i64>().ok()))
        .unwrap_or(0)
        * 4096
}

fn run_k1(v: &str, reps: i32) {
    if v == "footprint0" {
        result("k1", v, "energy", 0, 0.0, "0");
        return;
    }
    let raw = load_f32("k1_particles.f32");
    if v == "footprint_raw" {
        result("k1", v, "energy", 0, 0.0, "0");
        return;
    }
    let m1 = if v == "footprint" { rss_now() } else { 0 }; // P1 : tampon brut chargé
    let mut ps: Vec<Particle> = raw.chunks_exact(16).map(Particle::from).collect();
    if v == "footprint" {
        let m2 = rss_now(); // P2 : collection construite, tampon brut encore vivant
        println!("META;mem;rss;{m1};{m2}\nMETA;rss;{m1};{m2}\nMETA;raw0;{}", raw[0]);
        drop(raw);
        result("k1", v, "energy", 0, 0.0, &format!("{:.6}", k1_natural(&ps)));
        return;
    }
    match v {
        "soa" => {
            let f: Vec<ABuf> = (0..16).map(|k| ABuf::of(&raw.iter().skip(k).step_by(16).copied().collect::<Vec<f32>>())).collect();
            drop(raw);
            drop(ps);
            let c = |k: usize| f[k].as_slice::<f32>();
            bench("k1", v, "energy", reps, || format!("{:.6}", unsafe { k1_soa(c(3), c(4), c(5), c(9)) }));
        }
        "aos" => bench("k1", v, "energy", reps, || format!("{:.6}", k1_aos(&ps))),
        _ => {
            if v == "natural_shuffled" {
                let perm = load_u32("k1_perm.u32");
                ps = perm.iter().map(|&j| ps[j as usize]).collect();
            }
            bench("k1", v, "energy", reps, || format!("{:.6}", k1_natural(&ps)))
        }
    }
}

// ------------------------------------------------------------------ K2
#[inline(never)]
fn k2_chase(a: &[u32], h: usize) -> u32 {
    let mut i = 0u32;
    for _ in 0..h {
        i = unsafe { *a.get_unchecked(i as usize) };
    }
    i
}
fn run_k2(v: &str, reps: i32, p: &str) {
    let a = load_u32(&format!("k2_chase_{p}.u32"));
    bench("k2", v, p, reps, || k2_chase(black_box(&a), 4_200_000).to_string());
}

// ------------------------------------------------------------------ K3
const ITER3: u64 = 1 << 25;
#[repr(align(128))]
struct Padded(AtomicU64);
fn run_k3(v: &str, reps: i32) {
    let rmw = v.starts_with("rmw");
    let padded = v.ends_with("padded");
    println!("META;k3_mechanism;{}", if rmw { "AtomicU64::fetch_add(Relaxed) (lock xadd)" } else { "AtomicU64 load/store Relaxed (mov)" });
    let packed: [AtomicU64; 4] = Default::default();
    let pad: [Padded; 4] = [Padded(AtomicU64::new(0)), Padded(AtomicU64::new(0)), Padded(AtomicU64::new(0)), Padded(AtomicU64::new(0))];
    let counters: Vec<&AtomicU64> = if padded { pad.iter().map(|p| &p.0).collect() } else { packed.iter().collect() };
    bench("k3", v, "4x2^25", reps, || {
        for c in &counters {
            c.store(0, Ordering::Relaxed);
        }
        std::thread::scope(|s| {
            for c in &counters {
                s.spawn(move || {
                    if rmw {
                        for _ in 0..ITER3 {
                            c.fetch_add(1, Ordering::Relaxed);
                        }
                    } else {
                        for _ in 0..ITER3 {
                            c.store(c.load(Ordering::Relaxed) + 1, Ordering::Relaxed);
                        }
                    }
                });
            }
        });
        counters.iter().map(|c| c.load(Ordering::Relaxed)).sum::<u64>().to_string()
    });
}

// ------------------------------------------------------------------ K4
#[inline(never)]
fn k4_natural(v: &[u8]) -> u64 {
    v.iter().filter(|&&x| x >= 128).map(|&x| x as u64).sum()
}
#[inline(never)]
fn k4_branchless(v: &[u8]) -> u64 {
    v.iter().map(|&x| x as u64 * (x >> 7) as u64).sum()
}
fn run_k4(v: &str, reps: i32) {
    let mut d = load_bytes("k4_bytes.u8");
    if v == "natural_sorted" {
        d.sort_unstable();
    }
    let bl = v == "branchless_unsorted";
    bench("k4", v, "16M", reps, || (if bl { k4_branchless(&d) } else { k4_natural(&d) }).to_string());
}

// ------------------------------------------------------------------ K5
const INNER5: usize = 1 << 16;
#[inline(never)]
fn k5_natural(a: &[f32], b: &[f32]) -> f32 {
    a.iter().zip(b).map(|(x, y)| x * y).sum()
}
// optimisé : AVX-512 + FMA via std::arch (stable). Note : la version portable à
// 64 accumulateurs (sans intrinsèques) est vectorisée en ymm sans FMA (pas de
// contraction en Rust) et sa réduction finale reste séquentielle : ~4x plus lente.
#[target_feature(enable = "avx512f")]
unsafe fn k5_tuned(a: &[f32], b: &[f32]) -> f32 {
    let (mut s0, mut s1, mut s2, mut s3) = (_mm512_setzero_ps(), _mm512_setzero_ps(), _mm512_setzero_ps(), _mm512_setzero_ps());
    let (pa, pb) = (a.as_ptr(), b.as_ptr());
    let mut i = 0;
    while i + 64 <= a.len() {
        s0 = _mm512_fmadd_ps(_mm512_load_ps(pa.add(i)), _mm512_load_ps(pb.add(i)), s0);
        s1 = _mm512_fmadd_ps(_mm512_load_ps(pa.add(i + 16)), _mm512_load_ps(pb.add(i + 16)), s1);
        s2 = _mm512_fmadd_ps(_mm512_load_ps(pa.add(i + 32)), _mm512_load_ps(pb.add(i + 32)), s2);
        s3 = _mm512_fmadd_ps(_mm512_load_ps(pa.add(i + 48)), _mm512_load_ps(pb.add(i + 48)), s3);
        i += 64;
    }
    _mm512_reduce_add_ps(_mm512_add_ps(_mm512_add_ps(s0, s1), _mm512_add_ps(s2, s3)))
}
fn run_k5(v: &str, reps: i32) {
    let (ab, bb) = (ABuf::load("k5_a.f32"), ABuf::load("k5_b.f32"));
    let (a, b) = (ab.as_slice::<f32>(), bb.as_slice::<f32>());
    let tuned = v == "tuned";
    bench("k5", v, "2048x65536", reps, || {
        let mut d = 0f32;
        for _ in 0..INNER5 {
            let aa = black_box(a);
            d = if tuned { unsafe { k5_tuned(aa, b) } } else { k5_natural(aa, b) };
        }
        format!("{d:.4}")
    });
}

// ------------------------------------------------------------------ K6
const N6: usize = 1 << 24;
struct Cols { sd: Vec<i32>, pr: Vec<i32>, q: Vec<u8>, d: Vec<u8>, t: Vec<u8>, rf: Vec<u8>, ls: Vec<u8> }
type Q1Acc = [[i64; 5]; 6];

#[inline(never)]
fn q6_natural(c: &Cols, lo: usize, hi: usize) -> i64 {
    let mut s = 0i64;
    for i in lo..hi {
        if c.sd[i] >= 8766 && c.sd[i] < 9131 && c.d[i] >= 5 && c.d[i] <= 7 && c.q[i] < 24 {
            s += c.pr[i] as i64 * c.d[i] as i64;
        }
    }
    s
}
#[inline(never)]
fn q6_tuned(sd: &[i32], d: &[u8], q: &[u8], pr: &[i32]) -> i64 {
    let n = sd.len();
    let (d, q, pr) = (&d[..n], &q[..n], &pr[..n]); // élimine les vérifications de bornes
    let mut s = 0i64;
    for i in 0..n {
        let m = ((sd[i].wrapping_sub(8766) as u32) < 365) & (d[i].wrapping_sub(5) <= 2) & (q[i] < 24);
        s += (pr[i] * d[i] as i32) as i64 & -(m as i64);
    }
    s
}
#[inline(never)]
fn q1_natural(c: &Cols, lo: usize, hi: usize, acc: &mut Q1Acc) {
    for i in lo..hi {
        if c.sd[i] <= 10471 {
            let g = (c.rf[i] * 2 + c.ls[i]) as usize;
            let p = c.pr[i] as i64;
            let dp = p * (100 - c.d[i] as i64);
            acc[g][0] += 1;
            acc[g][1] += c.q[i] as i64;
            acc[g][2] += p;
            acc[g][3] += dp;
            acc[g][4] += dp * (100 + c.t[i] as i64);
        }
    }
}
// Q1 optimisé : même algorithme AVX-512 masqué que la référence C (std::arch stable)
#[target_feature(enable = "avx512f,avx512bw,avx512vl,bmi2")]
unsafe fn q1_tuned(c: &Cols, lo: usize, hi: usize, acc: &mut Q1Acc) {
    let lim = _mm512_set1_epi32(10471);
    let c100 = _mm512_set1_epi32(100);
    let mut i = lo;
    while i + 16 <= hi {
        let z = _mm512_setzero_si512();
        let (mut aq, mut ap, mut adp, mut ace, mut aco) = ([z; 6], [z; 6], [z; 6], [z; 6], [z; 6]);
        let mut cnt = [0i64; 6];
        let end = if i + 4096 <= hi { i + 4096 } else { hi - (hi - i) % 16 };
        while i < end {
            let pass = _mm512_cmple_epi32_mask(_mm512_loadu_si512(c.sd.as_ptr().add(i) as *const _), lim);
            let ld8 = |p: &Vec<u8>| _mm512_cvtepu8_epi32(_mm_loadu_si128(p.as_ptr().add(i) as *const __m128i));
            let vg = _mm512_add_epi32(_mm512_slli_epi32(ld8(&c.rf), 1), ld8(&c.ls));
            let vq = ld8(&c.q);
            let vd = ld8(&c.d);
            let vt = _mm512_add_epi32(ld8(&c.t), c100);
            let vp = _mm512_loadu_si512(c.pr.as_ptr().add(i) as *const _);
            let vdp = _mm512_mullo_epi32(vp, _mm512_sub_epi32(c100, vd));
            let che = _mm512_mul_epi32(vdp, vt);
            let cho = _mm512_mul_epi32(_mm512_srli_epi64(vdp, 32), _mm512_srli_epi64(vt, 32));
            for g in 0..6 {
                let m = _mm512_mask_cmpeq_epi32_mask(pass, vg, _mm512_set1_epi32(g as i32));
                cnt[g] += _popcnt32(m as i32) as i64; // remarque sur Rust : popcnt sur 32 bits, comme __builtin_popcount en C
                aq[g] = _mm512_mask_add_epi32(aq[g], m, aq[g], vq);
                ap[g] = _mm512_mask_add_epi32(ap[g], m, ap[g], vp);
                adp[g] = _mm512_mask_add_epi32(adp[g], m, adp[g], vdp);
                ace[g] = _mm512_mask_add_epi64(ace[g], _pext_u32(m as u32, 0x5555) as u8, ace[g], che);
                aco[g] = _mm512_mask_add_epi64(aco[g], _pext_u32(m as u32, 0xAAAA) as u8, aco[g], cho);
            }
            i += 16;
        }
        for g in 0..6 {
            acc[g][0] += cnt[g];
            acc[g][1] += _mm512_reduce_add_epi32(aq[g]) as i64;
            acc[g][2] += _mm512_reduce_add_epi32(ap[g]) as i64;
            acc[g][3] += _mm512_reduce_add_epi64(_mm512_add_epi64(
                _mm512_cvtepi32_epi64(_mm512_castsi512_si256(adp[g])),
                _mm512_cvtepi32_epi64(_mm512_extracti64x4_epi64(adp[g], 1))));
            acc[g][4] += _mm512_reduce_add_epi64(_mm512_add_epi64(ace[g], aco[g]));
        }
    }
    if i < hi {
        q1_natural(c, i, hi, acc);
    }
}
fn run_k6(v: &str, reps: i32, p: &str) {
    let c = Cols {
        sd: load_i32("k6_shipdate.i32"), pr: load_i32("k6_extendedprice.i32"), q: load_bytes("k6_quantity.u8"),
        d: load_bytes("k6_discount.u8"), t: load_bytes("k6_tax.u8"), rf: load_bytes("k6_returnflag.u8"),
        ls: load_bytes("k6_linestatus.u8"),
    };
    let q1 = p == "q1";
    let fold = |acc: &Q1Acc| acc.iter().flatten().sum::<i64>();
    bench("k6", v, p, reps, || {
        let s: i64 = match (v, q1) {
            ("natural", false) => q6_natural(&c, 0, N6),
            ("natural", true) => {
                let mut a = [[0i64; 5]; 6];
                q1_natural(&c, 0, N6, &mut a);
                fold(&a)
            }
            ("tuned", false) => q6_tuned(&c.sd, &c.d, &c.q, &c.pr),
            ("tuned", true) => {
                let mut a = [[0i64; 5]; 6];
                unsafe { q1_tuned(&c, 0, N6, &mut a) };
                fold(&a)
            }
            _ => std::thread::scope(|s| {
                let hs: Vec<_> = (0..4)
                    .map(|t| {
                        let (lo, hi) = (N6 * t / 4, N6 * (t + 1) / 4);
                        let c = &c;
                        s.spawn(move || {
                            if q1 {
                                let mut a = [[0i64; 5]; 6];
                                unsafe { q1_tuned(c, lo, hi, &mut a) };
                                a.iter().flatten().sum::<i64>()
                            } else {
                                q6_tuned(&c.sd[lo..hi], &c.d[lo..hi], &c.q[lo..hi], &c.pr[lo..hi])
                            }
                        })
                    })
                    .collect();
                hs.into_iter().map(|h| h.join().unwrap()).sum()
            }),
        };
        s.to_string()
    });
}

// ------------------------------------------------------------------ K7
#[derive(Clone, Copy, Default)]
#[repr(C, align(16))]
struct Slot7 { key: u32, count: u32, sum: u64 }
fn run_k7(v: &str, reps: i32) {
    let keys = load_u32("k7_keys.u32");
    let vals = load_u32("k7_vals.u32");
    for r in -warmup()..reps {
        let (dt, nk, ws);
        if v == "natural" {
            let t0 = Instant::now();
            let mut m: HashMap<u32, (u32, u64)> = HashMap::new();
            for (&k, &x) in keys.iter().zip(&vals) {
                let e = m.entry(k).or_insert((0, 0));
                e.0 += 1;
                e.1 += x as u64;
            }
            dt = t0.elapsed().as_secs_f64();
            nk = m.len() as u64;
            ws = m.iter().map(|(&k, &(_, s))| s * ((k & 1023) as u64 + 1)).sum::<u64>();
        } else {
            const LOG: u32 = 21;
            const CAP: usize = 1 << LOG;
            let t0 = Instant::now();
            let mut tab = vec![Slot7::default(); CAP];
            for (kc, vc) in keys.chunks_exact(16).zip(vals.chunks_exact(16)) {
                let mut h = [0u32; 16];
                for b in 0..16 {
                    h[b] = kc[b].wrapping_mul(0x9E37_79B1) >> (32 - LOG);
                    unsafe { _mm_prefetch::<_MM_HINT_T0>(tab.as_ptr().add(h[b] as usize) as *const i8) };
                }
                for b in 0..16 {
                    let k = kc[b];
                    let mut s = h[b] as usize;
                    while tab[s].count != 0 && tab[s].key != k {
                        s = (s + 1) & (CAP - 1);
                    }
                    let e = &mut tab[s];
                    e.key = k;
                    e.count += 1;
                    e.sum += vc[b] as u64;
                }
            }
            dt = t0.elapsed().as_secs_f64();
            nk = tab.iter().filter(|e| e.count != 0).count() as u64;
            ws = tab.iter().filter(|e| e.count != 0).map(|e| e.sum * ((e.key & 1023) as u64 + 1)).sum::<u64>();
        }
        if r >= 0 {
            result("k7", v, "16M/1M", r, dt, &format!("{nk}:{ws}"));
        }
    }
}

// ------------------------------------------------------------------ K8
struct Node { v: i64, l: Option<Box<Node>>, r: Option<Box<Node>> }
fn t_build(d: u32, c: &mut i64) -> Box<Node> {
    let v = *c;
    *c += 1;
    let (l, r) = if d > 0 { let l = t_build(d - 1, c); (Some(l), Some(t_build(d - 1, c))) } else { (None, None) };
    Box::new(Node { v, l, r })
}
fn t_sum(n: &Node) -> i64 {
    n.v + n.l.as_ref().map_or(0, |x| t_sum(x)) + n.r.as_ref().map_or(0, |x| t_sum(x))
}
#[derive(Clone, Copy, Default)]
struct ANode { v: i64, l: i32, r: i32 }
fn a_build(a: &mut Vec<ANode>, d: u32, c: &mut i64) -> i32 {
    let i = a.len() as i32;
    a.push(ANode { v: *c, l: -1, r: -1 });
    *c += 1;
    if d > 0 {
        let l = a_build(a, d - 1, c);
        let r = a_build(a, d - 1, c);
        a[i as usize].l = l;
        a[i as usize].r = r;
    }
    i
}
fn a_sum(a: &[ANode], i: i32) -> i64 {
    if i < 0 { 0 } else { let n = a[i as usize]; n.v + a_sum(a, n.l) + a_sum(a, n.r) }
}
fn run_k8(v: &str, reps: i32) {
    const Q: usize = 16384;
    let tuned = v == "tuned";
    let mut c0 = 0i64;
    let long = t_build(20, &mut c0);
    let lsum = t_sum(&long);
    let mut lat = vec![0u64; Q];
    let mut arena: Vec<ANode> = Vec::with_capacity(2047);
    for r in -warmup()..reps {
        let mut total = 0i64;
        let t0 = Instant::now();
        for q in 0..Q {
            let a = Instant::now();
            let mut c = q as i64;
            let s = if tuned {
                arena.clear(); // réutilise la capacité : aucune allocation
                let root = a_build(&mut arena, 10, &mut c);
                a_sum(&arena, root)
            } else {
                let t = t_build(10, &mut c);
                t_sum(&t) // libéré à la sortie de portée
            };
            total += s;
            lat[q] = a.elapsed().as_nanos() as u64;
        }
        let dt = t0.elapsed().as_secs_f64();
        if r >= 0 {
            result("k8", v, "16384x2047", r, dt, &(total + lsum).to_string());
            lat.sort_unstable();
            println!("LAT;{v};{};{};{};{};{}", lat[Q / 2], lat[Q * 9 / 10], lat[Q * 99 / 100], lat[Q * 999 / 1000], lat[Q - 1]);
        }
    }
    black_box(&long);
}

// ------------------------------------------------------------------ K9
const M9: usize = 2048;
fn k9_init(i: usize, j: usize) -> f64 {
    ((i * 31 + j * 17) % 1024) as f64 / 1024.0
}
#[inline(never)]
fn k9_natural(inp: &Vec<Vec<f64>>, out: &mut Vec<Vec<f64>>) {
    for i in 1..M9 - 1 {
        for j in 1..M9 - 1 {
            out[i][j] = 0.25 * (((inp[i - 1][j] + inp[i + 1][j]) + inp[i][j - 1]) + inp[i][j + 1]);
        }
    }
}
#[inline(never)]
fn k9_rows(inp: &[f64], out: &mut [f64], r0: usize) {
    // out = lignes [r0, r0 + out.len()/M9) ; inp = grille complète
    for (k, o) in out.chunks_exact_mut(M9).enumerate() {
        let i = r0 + k;
        let up = &inp[(i - 1) * M9..i * M9];
        let mid = &inp[i * M9..(i + 1) * M9];
        let dn = &inp[(i + 1) * M9..(i + 2) * M9];
        for j in 1..M9 - 1 {
            o[j] = 0.25 * (((up[j] + dn[j]) + mid[j - 1]) + mid[j + 1]);
        }
    }
}
fn run_k9(v: &str, reps: i32) {
    if v == "natural" {
        let init: Vec<Vec<f64>> = (0..M9).map(|i| (0..M9).map(|j| k9_init(i, j)).collect()).collect();
        for r in -warmup()..reps {
            let mut a = init.clone();
            let mut b = init.clone();
            let t0 = Instant::now();
            for _ in 0..4 {
                k9_natural(&a, &mut b);
                std::mem::swap(&mut a, &mut b);
            }
            let dt = t0.elapsed().as_secs_f64();
            let s: f64 = a.iter().flatten().sum();
            if r >= 0 {
                result("k9", v, "2048^2x4", r, dt, &format!("{s:.15e}"));
            }
        }
        return;
    }
    let init: Vec<f64> = (0..M9 * M9).map(|k| k9_init(k / M9, k % M9)).collect();
    for r in -warmup()..reps {
        let mut a = init.clone();
        let mut b = init.clone();
        let t0 = Instant::now();
        for _ in 0..4 {
            let inner = &mut b[M9..(M9 - 1) * M9];
            if v == "tuned" {
                k9_rows(&a, inner, 1);
            } else {
                let rows = M9 - 2;
                std::thread::scope(|s| {
                    let mut rest = inner;
                    let mut r0 = 1;
                    for t in 0..4 {
                        let nr = (rows * (t + 1)) / 4 - (rows * t) / 4;
                        let (chunk, tail) = rest.split_at_mut(nr * M9);
                        rest = tail;
                        let a = &a;
                        let start = r0;
                        s.spawn(move || k9_rows(a, chunk, start));
                        r0 += nr;
                    }
                });
            }
            std::mem::swap(&mut a, &mut b);
        }
        let dt = t0.elapsed().as_secs_f64();
        let s: f64 = a.iter().sum();
        if r >= 0 {
            result("k9", v, "2048^2x4", r, dt, &format!("{s:.15e}"));
        }
    }
}

// ------------------------------------------------------------------ K10
const M10: u64 = 1 << 22;
const CAP10: usize = 1 << 14;
#[repr(align(128))]
struct CachePadded<T>(T);
struct Spsc {
    write_idx: CachePadded<AtomicUsize>,
    read_idx: CachePadded<AtomicUsize>,
    buf: Box<[UnsafeCell<u64>]>,
}
unsafe impl Sync for Spsc {}
fn run_k10(v: &str, reps: i32) {
    bench("k10", v, "2^22", reps, || {
        let s = if v == "natural" {
            let (tx, rx) = std::sync::mpsc::sync_channel::<u64>(CAP10);
            std::thread::scope(|s| {
                s.spawn(move || {
                    for x in 1..=M10 {
                        tx.send(x).unwrap();
                    }
                });
                s.spawn(move || rx.iter().sum::<u64>()).join().unwrap()
            })
        } else {
            let q = Spsc {
                write_idx: CachePadded(AtomicUsize::new(0)),
                read_idx: CachePadded(AtomicUsize::new(0)),
                buf: (0..CAP10).map(|_| UnsafeCell::new(0)).collect(),
            };
            std::thread::scope(|s| {
                let q = &q;
                s.spawn(move || {
                    let mut w = 0usize;
                    let mut rcache = 0usize;
                    for x in 1..=M10 {
                        while w - rcache == CAP10 {
                            rcache = q.read_idx.0.load(Ordering::Acquire);
                            if w - rcache == CAP10 { std::hint::spin_loop(); }
                        }
                        unsafe { *q.buf[w & (CAP10 - 1)].get() = x };
                        w += 1;
                        q.write_idx.0.store(w, Ordering::Release);
                    }
                });
                s.spawn(move || {
                    let mut rd = 0usize;
                    let mut wcache = 0usize;
                    let mut sum = 0u64;
                    for _ in 0..M10 {
                        while rd == wcache {
                            wcache = q.write_idx.0.load(Ordering::Acquire);
                            if rd == wcache { std::hint::spin_loop(); }
                        }
                        sum += unsafe { *q.buf[rd & (CAP10 - 1)].get() };
                        rd += 1;
                        q.read_idx.0.store(rd, Ordering::Release);
                    }
                    sum
                })
                .join()
                .unwrap()
            })
        };
        s.to_string()
    });
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let (k, v, reps) = (a[1].as_str(), a[2].as_str(), a[3].parse::<i32>().unwrap());
    let p = a.get(4).map(|s| s.as_str()).unwrap_or("");
    match k {
        "k1" => run_k1(v, reps),
        "k2" => run_k2(v, reps, p),
        "k3" => run_k3(v, reps),
        "k4" => run_k4(v, reps),
        "k5" => run_k5(v, reps),
        "k6" => run_k6(v, reps, p),
        "k7" => run_k7(v, reps),
        "k8" => run_k8(v, reps),
        "k9" => run_k9(v, reps),
        "k10" => run_k10(v, reps),
        _ => panic!("kernel inconnu"),
    }
}
