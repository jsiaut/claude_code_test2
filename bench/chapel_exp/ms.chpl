// Copie de la remarque sur Chapel (docs/CHAPEL.md), sensibilité seulement : K5 tuned et K1 aos/soa avec l'attribut
// @llvm.metadata(("llvm.loop.vectorize.enable", true)) au lieu du binaire --no-ieee-float ; Q1 tuned en intrinsèques
// AVX-512 importées de immintrin.h (une passe masquée, comme C) ; K7 naturel en une recherche (ref e = m[k]).
// Implémentation Chapel 2.10 des noyaux de docs/SPEC.md.
// « natural » : records dans des tableaux, boucles for sérielles (les noyaux sont définis
// mono-thread ; les formes idiomatiques « + reduce » / forall de Chapel sont parallèles et
// ne servent que pour les variantes mt), map du module Map, classes owned, variables sync.
// « tuned » : sans vérifications (--fast), vecteurs 512 bits autorisés, --no-ieee-float pour les
// réductions flottantes que la spec permet de réassocier, atomiques avec memoryOrder, coforall/forall.
// Horloge : Time.stopwatch (gettimeofday dans le runtime : microseconde, non monotone).
use Time, IO, CTypes, Map, Sort, Prefetch;  // Prefetch : module « package » livré avec Chapel
use BitOps;
require "immintrin.h";
extern type __m512i;
extern type __m256i;
extern type __m128i;
extern proc _mm512_setzero_si512(): __m512i;
extern proc _mm512_set1_epi32(x: int(32)): __m512i;
extern proc _mm512_loadu_si512(p: c_ptrConst(void)): __m512i;
extern proc _mm_loadu_si128(p: c_ptrConst(void)): __m128i;
extern proc _mm512_cvtepu8_epi32(x: __m128i): __m512i;
extern proc _mm512_add_epi32(a: __m512i, b: __m512i): __m512i;
extern proc _mm512_sub_epi32(a: __m512i, b: __m512i): __m512i;
extern proc _mm512_xor_si512(a: __m512i, b: __m512i): __m512i;
extern proc _mm512_mullo_epi32(a: __m512i, b: __m512i): __m512i;
extern proc _mm512_mul_epi32(a: __m512i, b: __m512i): __m512i;
extern proc _mm512_srli_epi64(a: __m512i, n: c_uint): __m512i;
extern proc _mm512_movepi32_mask(a: __m512i): uint(16);
extern proc _mm512_mask_testn_epi32_mask(u: uint(16), a: __m512i, b: __m512i): uint(16);
extern proc _mm512_mask_add_epi32(src: __m512i, k: uint(16), a: __m512i, b: __m512i): __m512i;
extern proc _mm512_mask_add_epi64(src: __m512i, k: uint(8), a: __m512i, b: __m512i): __m512i;
extern proc _mm512_reduce_add_epi32(a: __m512i): int(32);
extern proc _mm512_reduce_add_epi64(a: __m512i): int(64);
extern proc _mm512_cvtepi32_epi64(a: __m256i): __m512i;
extern proc _mm512_castsi512_si256(a: __m512i): __m256i;
extern proc _mm512_maskz_compress_epi64(k: uint(8), a: __m512i): __m512i;
extern proc _pext_u32(a: c_uint, m: c_uint): c_uint;

config const dataDir = "/opt/msdata";
config const warm = 1;
config var zero: real(32) = 0.0;  // valeur inconnue du compilateur (barrière d'optimisation K5)

proc result(k: string, v: string, p: string, rep: int, sec: real, chk: string) {
  writef("RESULT;%s;%s;%s;%i;%.9dr;%s\n", k, v, p, rep, sec, chk);
  stdout.flush();
}
proc loadArr(name: string, type t) {
  var f = open(dataDir + "/" + name, ioMode.r);
  const n = f.size / numBytes(t);
  var a: [0..<n] t;
  var r = f.reader(locking=false);
  r.readBinary(a);
  r.close(); f.close();
  return a;
}

// ------------------------------------------------------------------ K1
const N1 = 4194304;
record Particle {
  var x, y, z, vx, vy, vz, ax, ay, az, mass, charge, radius, temp, pressure, energy, density: real(32);
}
proc k1Natural(const ref ps: [] Particle): real {
  var e = 0.0;
  for p in ps do e += 0.5 * p.mass * (p.vx * p.vx + p.vy * p.vy + p.vz * p.vz);
  return e;
}
// K1 aos/soa tuned : boucles simples, binaire ms_fm compilé avec --no-ieee-float (réassociation
// permise par la spec pour l'accumulation) : LLVM vectorise alors la réduction.
proc k1Aos(const ref ps: [] Particle): real {
  var e = 0.0;
  @llvm.metadata(("llvm.loop.vectorize.enable", true))
  for p in ps do e += (0.5: real(32) * p.mass * (p.vx * p.vx + p.vy * p.vy + p.vz * p.vz)): real;
  return e;
}
proc k1Soa(const ref vx: [] real(32), const ref vy: [] real(32), const ref vz: [] real(32), const ref m: [] real(32)): real {
  var e = 0.0;
  @llvm.metadata(("llvm.loop.vectorize.enable", true))
  for i in vx.domain do e += (0.5: real(32) * m[i] * (vx[i] * vx[i] + vy[i] * vy[i] + vz[i] * vz[i])): real;
  return e;
}
// Empreinte K1 (D2a) : RSS courant en octets (/proc/self/statm, 2e champ ; pages de 4 Kio)
proc rssNow(): int {
  try {
    var r = openReader("/proc/self/statm");
    var size, res: int;
    r.read(size, res);
    r.close();
    return res * 4096;
  } catch { return 0; }
}
proc runK1(v: string, reps: int) {
  if v == "footprint0" { result("k1", v, "energy", 0, 0.0, "0"); return; }
  const raw = loadArr("k1_particles.f32", real(32));
  if v == "footprint_raw" { result("k1", v, "energy", 0, 0.0, "0"); return; }
  const m1 = if v == "footprint" then rssNow() else 0;  // P1 : tampon brut chargé
  var sw: stopwatch;
  if v == "soa" {
    var cols: [0..<16] [0..<N1] real(32);
    for k in 0..<16 do for i in 0..<N1 do cols[k][i] = raw[16 * i + k];
    for r in -warm..<reps {
      sw.clear(); sw.start();
      const e = k1Soa(cols[3], cols[4], cols[5], cols[9]);
      sw.stop();
      if r >= 0 then result("k1", v, "energy", r, sw.elapsed(), "%.6dr".format(e));
    }
    return;
  }
  var ps: [0..<N1] Particle;
  for i in 0..<N1 {
    const o = 16 * i;
    ps[i] = new Particle(raw[o], raw[o+1], raw[o+2], raw[o+3], raw[o+4], raw[o+5], raw[o+6], raw[o+7], raw[o+8],
                         raw[o+9], raw[o+10], raw[o+11], raw[o+12], raw[o+13], raw[o+14], raw[o+15]);
  }
  if v == "footprint" {
    const m2 = rssNow();  // P2 : collection construite, tampon brut encore vivant
    writeln("META;mem;rss;", m1, ";", m2);
    writeln("META;rss;", m1, ";", m2);
    writeln("META;raw0;", raw[0]);
    result("k1", v, "energy", 0, 0.0, "%.6dr".format(k1Natural(ps))); return;
  }
  if v == "natural_shuffled" {
    const perm = loadArr("k1_perm.u32", uint(32));
    const s = [j in 0..<N1] ps[perm[j]: int];
    ps = s;
  }
  for r in -warm..<reps {
    sw.clear(); sw.start();
    const e = if v == "aos" then k1Aos(ps) else k1Natural(ps);
    sw.stop();
    if r >= 0 then result("k1", v, "energy", r, sw.elapsed(), "%.6dr".format(e));
  }
}

// ------------------------------------------------------------------ K2
proc k2Chase(const ref a: [] uint(32), h: int): uint(32) {
  var i: uint(32) = 0;
  for 1..h do i = a[i: int];
  return i;
}
proc runK2(v: string, reps: int, p: string) {
  const a = loadArr("k2_chase_" + p + ".u32", uint(32));
  var sw: stopwatch;
  for r in -warm..<reps {
    sw.clear(); sw.start();
    const i = k2Chase(a, 4200000);
    sw.stop();
    if r >= 0 then result("k2", v, p, r, sw.elapsed(), i: string);
  }
}

// ------------------------------------------------------------------ K3
proc runK3(v: string, reps: int) {
  const rmw = v.startsWith("rmw"), stride = if v.endsWith("padded") then 16 else 1;  // en int : 128 o ou 8 o
  writeln("META;k3_mechanism;", if rmw then "atomic int add(memoryOrder.relaxed) (lock add)"
                                      else "atomic int read/write(memoryOrder.relaxed) (mov)");
  var c: [0..<80] atomic int;
  var sw: stopwatch;
  for r in -warm..<reps {
    for x in c do x.write(0);
    sw.clear(); sw.start();
    coforall t in 0..<4 with (ref c) {
      const idx = t * stride;
      if rmw then
        for 1..(1 << 25) do c[idx].add(1, memoryOrder.relaxed);
      else
        for 1..(1 << 25) do c[idx].write(c[idx].read(memoryOrder.relaxed) + 1, memoryOrder.relaxed);
    }
    sw.stop();
    var s = 0;
    for x in c do s += x.read();
    if r >= 0 then result("k3", v, "4x2^25", r, sw.elapsed(), s: string);
  }
}

// ------------------------------------------------------------------ K4
proc k4Natural(const ref b: [] uint(8)): uint {
  var s: uint = 0;
  for x in b do if x >= 128 then s += x;
  return s;
}
proc k4Branchless(const ref b: [] uint(8)): uint {
  var s: uint = 0;
  for x in b do s += (x * (x >> 7)): uint;
  return s;
}
proc runK4(v: string, reps: int) {
  var b = loadArr("k4_bytes.u8", uint(8));
  if v == "natural_sorted" then sort(b);  // hors chrono
  var sw: stopwatch;
  for r in -warm..<reps {
    sw.clear(); sw.start();
    const s = if v == "branchless_unsorted" then k4Branchless(b) else k4Natural(b);
    sw.stop();
    if r >= 0 then result("k4", v, "16M", r, sw.elapsed(), s: string);
  }
}

// ------------------------------------------------------------------ K5
proc k5Natural(const ref a: [] real(32), const ref b: [] real(32)): real(32) {
  var s: real(32) = 0;
  for i in a.domain do s += a[i] * b[i];
  return s;
}
// K5 tuned : boucle simple compilée avec --no-ieee-float (binaire ms_fm). Mesuré : un tuple de 64
// accumulateurs (boucle param) n'est vectorisé par LLVM qu'en <2 x float> (25 ms contre 5 ms).
proc k5Tuned(const ref a: [] real(32), const ref b: [] real(32)): real(32) {
  var s: real(32) = 0;
  @llvm.metadata(("llvm.loop.vectorize.enable", true))  // remarque : réassociation par boucle, sans option globale
  for i in a.domain do s += a[i] * b[i];
  return s;
}
proc runK5(v: string, reps: int) {
  var a = loadArr("k5_a.f32", real(32));
  const b = loadArr("k5_b.f32", real(32));
  var sink: atomic real(32);
  var sw: stopwatch;
  var d: real(32);
  for r in -warm..<reps {
    sw.clear(); sw.start();
    for 1..65536 {
      a[0] += zero;  // écriture opaque : le compilateur ne peut pas sortir le calcul de la boucle
      d = if v == "tuned" then k5Tuned(a, b) else k5Natural(a, b);
      sink.write(d, memoryOrder.relaxed);
    }
    sw.stop();
    if r >= 0 then result("k5", v, "2048x65536", r, sw.elapsed(), "%.4dr".format(d));
  }
}

// ------------------------------------------------------------------ K6
const N6 = 16777216;
proc q6Natural(const ref sd: [] int(32), const ref d: [] uint(8), const ref q: [] uint(8), const ref pr: [] int(32),
               lo: int, hi: int): int {
  var s = 0;
  for i in lo..hi do
    if sd[i] >= 8766 && sd[i] < 9131 && d[i] >= 5 && d[i] <= 7 && q[i] < 24 then s += pr[i]: int * d[i];
  return s;
}
proc q6Tuned(const ref sd: [] int(32), const ref d: [] uint(8), const ref q: [] uint(8), const ref pr: [] int(32),
             lo: int, hi: int): int {
  var s = 0;
  for i in lo..hi {
    const m = ((sd[i] - 8766): uint(32) < 365): int(32) * ((d[i] - 5): uint(8) <= 2): int(32) * (q[i] < 24): int(32);
    s += pr[i] * d[i]: int(32) * m;
  }
  return s;
}
proc q1Natural(const ref sd, const ref pr, const ref q, const ref d, const ref t, const ref rf, const ref ls,
               lo: int, hi: int, ref acc: [] int) {
  for i in lo..hi {
    if sd[i] <= 10471 {
      const g = (rf[i] * 2 + ls[i]): int;
      const p = pr[i]: int, dp = p * (100 - d[i]);
      acc[g * 5] += 1;
      acc[g * 5 + 1] += q[i];
      acc[g * 5 + 2] += p;
      acc[g * 5 + 3] += dp;
      acc[g * 5 + 4] += dp * (100 + t[i]);
    }
  }
}
// Q1 par blocs de 1024 lignes : conversions et produits une fois par bloc, puis une passe
// par groupe avec sélection arithmétique (masque 0/1), vectorisée par LLVM. Mesuré : le if dans
// la passe par groupe coûte 1,4x (67-85 ms contre 48-54 ms).
// Colonnes passées en c_ptr : mesuré, des formels tableaux génériques doublent le temps (103-114 ms
// contre 49-58 ms), l'indirection du descripteur de tableau gênant la vectorisation.
proc q1Tuned(sd: c_ptrConst(int(32)), pr: c_ptrConst(int(32)), q: c_ptrConst(uint(8)), d: c_ptrConst(uint(8)),
             t: c_ptrConst(uint(8)), rf: c_ptrConst(uint(8)), ls: c_ptrConst(uint(8)), lo: int, hi: int, ref acc: [] int) {
  // remarque : une passe masquée par tranche de 16 lignes, comme le C (les comparaisons à immédiat, des macros, ne
  // s'importent pas : sd <= 10471 par le bit de signe de sd - 10472, l'égalité au groupe par testn)
  const lim = _mm512_set1_epi32(10472), c100 = _mm512_set1_epi32(100);
  var i = lo;
  const stop = hi + 1 - (hi + 1 - lo) % 16;
  while i < stop {
    var aq, ap, adp, ace, aco: 6*__m512i;
    var cnt: 6*int;
    for param g in 0..<6 {
      aq[g] = _mm512_setzero_si512(); ap[g] = aq[g]; adp[g] = aq[g]; ace[g] = aq[g]; aco[g] = aq[g];
    }
    const blockEnd = min(i + 4096, stop);
    while i < blockEnd {
      const pass = _mm512_movepi32_mask(_mm512_sub_epi32(_mm512_loadu_si512((sd + i): c_ptrConst(void)), lim));
      const rfv = _mm512_cvtepu8_epi32(_mm_loadu_si128((rf + i): c_ptrConst(void)));
      const vg = _mm512_add_epi32(_mm512_add_epi32(rfv, rfv), _mm512_cvtepu8_epi32(_mm_loadu_si128((ls + i): c_ptrConst(void))));
      const vq = _mm512_cvtepu8_epi32(_mm_loadu_si128((q + i): c_ptrConst(void)));
      const vd = _mm512_cvtepu8_epi32(_mm_loadu_si128((d + i): c_ptrConst(void)));
      const vt = _mm512_add_epi32(_mm512_cvtepu8_epi32(_mm_loadu_si128((t + i): c_ptrConst(void))), c100);
      const vp = _mm512_loadu_si512((pr + i): c_ptrConst(void));
      const vdp = _mm512_mullo_epi32(vp, _mm512_sub_epi32(c100, vd));
      const che = _mm512_mul_epi32(vdp, vt);                                                  // lignes paires
      const cho = _mm512_mul_epi32(_mm512_srli_epi64(vdp, 32), _mm512_srli_epi64(vt, 32));   // lignes impaires
      for param g in 0..<6 {
        const x = _mm512_xor_si512(vg, _mm512_set1_epi32(g: int(32)));
        const m = _mm512_mask_testn_epi32_mask(pass, x, x);
        cnt[g] += popCount(m);
        aq[g] = _mm512_mask_add_epi32(aq[g], m, aq[g], vq);
        ap[g] = _mm512_mask_add_epi32(ap[g], m, ap[g], vp);
        adp[g] = _mm512_mask_add_epi32(adp[g], m, adp[g], vdp);
        ace[g] = _mm512_mask_add_epi64(ace[g], _pext_u32(m: c_uint, 0x5555: c_uint): uint(8), ace[g], che);
        aco[g] = _mm512_mask_add_epi64(aco[g], _pext_u32(m: c_uint, 0xAAAA: c_uint): uint(8), aco[g], cho);
      }
      i += 16;
    }
    for param g in 0..<6 {
      acc[g * 5] += cnt[g];
      acc[g * 5 + 1] += _mm512_reduce_add_epi32(aq[g]);
      acc[g * 5 + 2] += _mm512_reduce_add_epi32(ap[g]);
      acc[g * 5 + 3] += _mm512_reduce_add_epi64(_mm512_cvtepi32_epi64(_mm512_castsi512_si256(adp[g])))
                      + _mm512_reduce_add_epi64(_mm512_cvtepi32_epi64(_mm512_castsi512_si256(
                          _mm512_maskz_compress_epi64(0xF0: uint(8), adp[g]))));
      acc[g * 5 + 4] += _mm512_reduce_add_epi64(ace[g]) + _mm512_reduce_add_epi64(aco[g]);
    }
  }
  for j in i..hi {  // reste (moins de 16 lignes) : scalaire
    if sd[j] <= 10471 {
      const g = (rf[j] * 2 + ls[j]): int;
      const p = pr[j]: int, dp = p * (100 - d[j]);
      acc[g * 5] += 1; acc[g * 5 + 1] += q[j]; acc[g * 5 + 2] += p; acc[g * 5 + 3] += dp; acc[g * 5 + 4] += dp * (100 + t[j]);
    }
  }
}
proc runK6(v: string, reps: int, p: string) {
  const sd = loadArr("k6_shipdate.i32", int(32)), pr = loadArr("k6_extendedprice.i32", int(32));
  const q = loadArr("k6_quantity.u8", uint(8)), d = loadArr("k6_discount.u8", uint(8)), t = loadArr("k6_tax.u8", uint(8));
  const rf = loadArr("k6_returnflag.u8", uint(8)), ls = loadArr("k6_linestatus.u8", uint(8));
  const isQ1 = p == "q1";
  const psd = c_ptrToConst(sd[0]), ppr = c_ptrToConst(pr[0]), pq = c_ptrToConst(q[0]), pd = c_ptrToConst(d[0]),
        pt = c_ptrToConst(t[0]), prf = c_ptrToConst(rf[0]), pls = c_ptrToConst(ls[0]);
  var sw: stopwatch;
  for r in -warm..<reps {
    var acc: [0..<30] int;
    var s6 = 0;
    sw.clear(); sw.start();
    if v == "mt" {
      var parts: [0..<4] [0..<30] int;
      var p6: [0..<4] int;
      coforall th in 0..<4 with (ref parts, ref p6) {
        const lo = N6 / 4 * th, hi = N6 / 4 * (th + 1) - 1;
        if isQ1 then q1Tuned(psd, ppr, pq, pd, pt, prf, pls, lo, hi, parts[th]);
        else p6[th] = q6Tuned(sd, d, q, pr, lo, hi);
      }
      for th in 0..<4 { acc += parts[th]; s6 += p6[th]; }
    } else if v == "tuned" {
      if isQ1 then q1Tuned(psd, ppr, pq, pd, pt, prf, pls, 0, N6 - 1, acc); else s6 = q6Tuned(sd, d, q, pr, 0, N6 - 1);
    } else {
      if isQ1 then q1Natural(sd, pr, q, d, t, rf, ls, 0, N6 - 1, acc); else s6 = q6Natural(sd, d, q, pr, 0, N6 - 1);
    }
    sw.stop();
    if isQ1 then for x in acc do s6 += x;
    if r >= 0 then result("k6", v, p, r, sw.elapsed(), s6: string);
  }
}

// ------------------------------------------------------------------ K7
const N7 = 16777216;
record Agg { var count: uint(32); var sum: uint; }
record Slot { var key, count: uint(32); var sum: uint; }  // 16 octets, 4 par ligne
proc runK7(v: string, reps: int) {
  const keys = loadArr("k7_keys.u32", uint(32)), vals = loadArr("k7_vals.u32", uint(32));
  var sw: stopwatch;
  for r in -warm..<reps {
    var nk: uint = 0, ws: uint = 0;
    if v == "natural" {
      sw.clear(); sw.start();
      var m = new map(uint(32), Agg);
      for i in 0..<N7 {
        const k = keys[i];
        ref e = m[k];  // remarque : une seule recherche (l'indexation ajoute la valeur par défaut)
        e.count += 1;
        e.sum += vals[i];
      }
      sw.stop();
      for (k, e) in zip(m.keys(), m.values()) { nk += 1; ws += e.sum * ((k & 1023) + 1); }
    } else {  // adressage ouvert, sondage linéaire, hachage de Fibonacci, lots préchargés
      param LOG = 21, CAP = 1 << LOG, BATCH = 16;
      sw.clear(); sw.start();
      var tab: [0..<CAP] Slot;
      var h: BATCH * int;
      for i in 0..<N7 by BATCH {
        for param b in 0..<BATCH {
          h[b] = ((keys[i + b] * 0x9E3779B1: uint(32)) >> (32 - LOG)): int;
          prefetch(c_ptrTo(tab[h[b]]));
        }
        for param b in 0..<BATCH {
          const k = keys[i + b];
          var s = h[b];
          while tab[s].count != 0 && tab[s].key != k do s = (s + 1) & (CAP - 1);
          tab[s].key = k;
          tab[s].count += 1;
          tab[s].sum += vals[i + b];
        }
      }
      sw.stop();
      for e in tab do if e.count != 0 { nk += 1; ws += e.sum * ((e.key & 1023) + 1); }
    }
    if r >= 0 then result("k7", v, "16M/1M", r, sw.elapsed(), nk: string + ":" + ws: string);
  }
}

// ------------------------------------------------------------------ K8
class Node { var v: int; var l, r: owned Node?; }
proc tBuild(d: int, ref c: int): owned Node {
  var n = new Node(c);
  c += 1;
  if d > 0 { n.l = tBuild(d - 1, c); n.r = tBuild(d - 1, c); }
  return n;
}
proc tSum(n: borrowed Node?): int {
  if n == nil then return 0;
  const nn = n!;
  return nn.v + tSum(nn.l.borrow()) + tSum(nn.r.borrow());
}
record ANode { var v: int; var l, r: int(32); }
proc aBuild(ref a: [] ANode, ref top: int(32), d: int, ref c: int): int(32) {
  const i = top;
  top += 1;
  a[i].v = c;
  c += 1;
  if d > 0 { const l = aBuild(a, top, d - 1, c); a[i].l = l; a[i].r = aBuild(a, top, d - 1, c); }
  else { a[i].l = -1; a[i].r = -1; }
  return i;
}
proc aSum(const ref a: [] ANode, i: int(32)): int {
  return if i < 0 then 0 else a[i].v + aSum(a, a[i].l) + aSum(a, a[i].r);
}
proc runK8(v: string, reps: int) {
  param Q = 16384;
  var cnt = 0;
  const keep = tBuild(20, cnt);
  const lsum = tSum(keep.borrow());
  var lat: [0..<Q] int;
  var arena: [0..<2047] ANode;
  var sw, sq: stopwatch;
  for r in -warm..<reps {
    var total = 0;
    sw.clear(); sw.start();
    for qq in 0..<Q {
      sq.clear(); sq.start();
      var c = qq, s: int;
      if v == "tuned" {
        var top: int(32) = 0;
        const root = aBuild(arena, top, 10, c);
        s = aSum(arena, root);
      } else {
        const t = tBuild(10, c);
        s = tSum(t.borrow());
      }  // l'arbre owned est libéré ici (désinitialisation récursive)
      total += s;
      sq.stop();
      lat[qq] = (sq.elapsed() * 1e9): int;
    }
    sw.stop();
    if r >= 0 {
      result("k8", v, "16384x2047", r, sw.elapsed(), (total + lsum): string);
      sort(lat);
      writeln("LAT;", v, ";", lat[Q / 2], ";", lat[Q * 9 / 10], ";", lat[Q * 99 / 100], ";", lat[Q * 999 / 1000], ";", lat[Q - 1]);
    }
  }
}

// ------------------------------------------------------------------ K9
const M9 = 2048;
proc k9Init(ref g: [] real) {
  for (i, j) in g.domain do g[i, j] = ((i * 31 + j * 17) % 1024): real / 1024.0;
}
proc k9Natural(const ref a: [] real, ref b: [] real) {
  for (i, j) in {1..M9 - 2, 1..M9 - 2} do
    b[i, j] = 0.25 * (((a[i - 1, j] + a[i + 1, j]) + a[i, j - 1]) + a[i, j + 1]);
}
proc k9Rows(const ref a: [] real, ref b: [] real, r0: int, r1: int) {
  for i in r0..r1 do
    foreach j in 1..M9 - 2 do
      b[i, j] = 0.25 * (((a[i - 1, j] + a[i + 1, j]) + a[i, j - 1]) + a[i, j + 1]);
}
proc k9Par(const ref a: [] real, ref b: [] real) {
  forall i in 1..M9 - 2 with (ref b) do  // forall : répartition par blocs sur les 4 cœurs
    foreach j in 1..M9 - 2 do
      b[i, j] = 0.25 * (((a[i - 1, j] + a[i + 1, j]) + a[i, j - 1]) + a[i, j + 1]);
}
proc runK9(v: string, reps: int) {
  var a, b: [0..<M9, 0..<M9] real;
  var sw: stopwatch;
  for r in -warm..<reps {
    k9Init(a);
    b = a;
    sw.clear(); sw.start();
    for 1..2 {  // 4 itérations : a -> b -> a -> b -> a
      if v == "natural" { k9Natural(a, b); k9Natural(b, a); }
      else if v == "tuned" { k9Rows(a, b, 1, M9 - 2); k9Rows(b, a, 1, M9 - 2); }
      else { k9Par(a, b); k9Par(b, a); }
    }
    sw.stop();
    var s = 0.0;
    for x in a do s += x;
    if r >= 0 then result("k9", v, "2048^2x4", r, sw.elapsed(), "%.15er".format(s));
  }
}

// ------------------------------------------------------------------ K10
const M10 = 1 << 22, CAP10 = 1 << 14;
record Padded { var x: atomic int; var pad: 15 * int; proc init() { } }  // 128 octets
proc runK10(v: string, reps: int) {
  var sw: stopwatch;
  for r in -warm..<reps {
    var sum = 0;
    if v == "tuned" {
      // anneau SPSC : indices sur des lignes distinctes, copies locales, acquire/release
      var widx, ridx: Padded;
      var buf: [0..<CAP10] int;
      sw.clear(); sw.start();
      cobegin with (ref sum, ref buf, ref widx, ref ridx) {
        {  // producteur
          var w = 0, cache = 0;
          for x in 1..M10 {
            var spins = 0;
            while w - cache == CAP10 {
              cache = ridx.x.read(memoryOrder.acquire);
              spins += 1;
              if spins % 1024 == 0 then currentTask.yieldExecution();
            }
            buf[w & (CAP10 - 1)] = x;
            w += 1;
            widx.x.write(w, memoryOrder.release);
          }
        }
        {  // consommateur
          var rd = 0, cache = 0, s = 0;
          for 1..M10 {
            var spins = 0;
            while rd == cache {
              cache = widx.x.read(memoryOrder.acquire);
              spins += 1;
              if spins % 1024 == 0 then currentTask.yieldExecution();
            }
            s += buf[rd & (CAP10 - 1)];
            rd += 1;
            ridx.x.write(rd, memoryOrder.release);
          }
          sum = s;
        }
      }
      sw.stop();
    } else {
      // naturel : tampon borné de variables sync (plein/vide), idiome producteur-consommateur de Chapel
      var buf: [0..<CAP10] sync int;
      sw.clear(); sw.start();
      cobegin with (ref sum) {
        for x in 1..M10 do buf[x % CAP10].writeEF(x);
        {
          var s = 0;
          for x in 1..M10 do s += buf[x % CAP10].readFE();
          sum = s;
        }
      }
      sw.stop();
    }
    if r >= 0 then result("k10", v, "2^22", r, sw.elapsed(), sum: string);
  }
}

proc main(args: [] string) {
  const k = args[1], v = args[2], reps = args[3]: int, p = if args.size > 4 then args[4] else "";
  select k {
    when "k1" do runK1(v, reps);
    when "k2" do runK2(v, reps, p);
    when "k3" do runK3(v, reps);
    when "k4" do runK4(v, reps);
    when "k5" do runK5(v, reps);
    when "k6" do runK6(v, reps, p);
    when "k7" do runK7(v, reps);
    when "k8" do runK8(v, reps);
    when "k9" do runK9(v, reps);
    when "k10" do runK10(v, reps);
    otherwise do halt("kernel inconnu ", k);
  }
}
