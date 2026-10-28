// Implémentation JavaScript (Node.js 26 / V8 14.6, aucune dépendance). Voir docs/SPEC.md.
'use strict';
const fs = require('fs');
const { Worker, isMainThread, parentPort, workerData } = require('worker_threads');

// ------------------------------------------------------------------ harnais
const DATA = process.env.MS_DATA || '/opt/msdata';
function loadBuf(name) { return fs.readFileSync(`${DATA}/${name}`); }
function load(name, Ctor) { const b = loadBuf(name); return new Ctor(b.buffer, b.byteOffset, b.length / Ctor.BYTES_PER_ELEMENT); }
function loadShared(name, Ctor) { // copie dans un SharedArrayBuffer (partageable entre Workers)
  const b = loadBuf(name); const sab = new SharedArrayBuffer(b.length); new Uint8Array(sab).set(b);
  return new Ctor(sab);
}
const WARMUP = parseInt(process.env.WARMUP || '1', 10);
const now = () => process.hrtime.bigint();
function result(k, v, p, rep, sec, chk) { console.log(`RESULT;${k};${v};${p};${rep};${sec.toFixed(9)};${chk}`); }
function bench(k, v, p, reps, f) {
  for (let r = -WARMUP; r < reps; r++) {
    const t0 = now(); const chk = f(); const dt = Number(now() - t0) * 1e-9;
    if (r >= 0) result(k, v, p, r, dt, chk);
  }
}
async function benchAsync(k, v, p, reps, f) {
  for (let r = -WARMUP; r < reps; r++) {
    const t0 = now(); const chk = await f(); const dt = Number(now() - t0) * 1e-9;
    if (r >= 0) result(k, v, p, r, dt, chk);
  }
}
const fix = (x, d) => x.toFixed(d);

// ------------------------------------------------------------------ K1
const N1 = 1 << 22;
function k1Natural(ps) {
  let e = 0;
  for (const p of ps) e += 0.5 * p.mass * (p.vx * p.vx + p.vy * p.vy + p.vz * p.vz);
  return e;
}
function k1AoS(f) { // AoS manuel dans un Float32Array (pas de 16)
  let a0 = 0, a1 = 0, a2 = 0, a3 = 0;
  for (let i = 0; i < f.length; i += 64) {
    a0 += 0.5 * f[i + 9] * (f[i + 3] * f[i + 3] + f[i + 4] * f[i + 4] + f[i + 5] * f[i + 5]);
    a1 += 0.5 * f[i + 25] * (f[i + 19] * f[i + 19] + f[i + 20] * f[i + 20] + f[i + 21] * f[i + 21]);
    a2 += 0.5 * f[i + 41] * (f[i + 35] * f[i + 35] + f[i + 36] * f[i + 36] + f[i + 37] * f[i + 37]);
    a3 += 0.5 * f[i + 57] * (f[i + 51] * f[i + 51] + f[i + 52] * f[i + 52] + f[i + 53] * f[i + 53]);
  }
  return a0 + a1 + a2 + a3;
}
function k1SoA(vx, vy, vz, m) {
  let a0 = 0, a1 = 0, a2 = 0, a3 = 0;
  for (let i = 0; i < vx.length; i += 4) {
    a0 += 0.5 * m[i] * (vx[i] * vx[i] + vy[i] * vy[i] + vz[i] * vz[i]);
    a1 += 0.5 * m[i + 1] * (vx[i + 1] * vx[i + 1] + vy[i + 1] * vy[i + 1] + vz[i + 1] * vz[i + 1]);
    a2 += 0.5 * m[i + 2] * (vx[i + 2] * vx[i + 2] + vy[i + 2] * vy[i + 2] + vz[i + 2] * vz[i + 2]);
    a3 += 0.5 * m[i + 3] * (vx[i + 3] * vx[i + 3] + vy[i + 3] * vy[i + 3] + vz[i + 3] * vz[i + 3]);
  }
  return a0 + a1 + a2 + a3;
}
// Empreinte K1 (D2a) : octets vivants (tas JS + mémoire externe) après GC complet, et RSS courant
function liveNow() {
  if (typeof Bun !== 'undefined') Bun.gc(true); else if (global.gc) global.gc();
  const m = process.memoryUsage();
  return m.heapUsed + m.external;
}
function rssNow() { return process.memoryUsage().rss; }
function runK1(v, reps) {
  if (v === 'footprint0') { result('k1', v, 'energy', 0, 0, '0'); return; }
  const raw = load('k1_particles.f32', Float32Array);
  if (v === 'footprint_raw') { result('k1', v, 'energy', 0, 0, '0'); return; }
  if (v === 'aos') { bench('k1', v, 'energy', reps, () => fix(k1AoS(raw), 6)); return; }
  if (v === 'soa') {
    const c = []; for (let k = 0; k < 16; k++) { const a = new Float32Array(N1); for (let i = 0; i < N1; i++) a[i] = raw[16 * i + k]; c.push(a); }
    bench('k1', v, 'energy', reps, () => fix(k1SoA(c[3], c[4], c[5], c[9]), 6)); return;
  }
  const [m1, r1] = v === 'footprint' ? [liveNow(), rssNow()] : [0, 0]; // P1 : tampon brut chargé
  let ps = [];
  for (let i = 0; i < N1; i++) {
    const o = 16 * i;
    ps.push({ x: raw[o], y: raw[o + 1], z: raw[o + 2], vx: raw[o + 3], vy: raw[o + 4], vz: raw[o + 5], ax: raw[o + 6], ay: raw[o + 7], az: raw[o + 8],
      mass: raw[o + 9], charge: raw[o + 10], radius: raw[o + 11], temp: raw[o + 12], pressure: raw[o + 13], energy: raw[o + 14], density: raw[o + 15] });
  }
  if (v === 'footprint') {
    const m2 = liveNow(), r2 = rssNow(); // P2 : collection construite, tampon brut encore vivant
    console.log(`META;mem;live;${m1};${m2}\nMETA;rss;${r1};${r2}\nMETA;raw0;${raw[0]}`);
    result('k1', v, 'energy', 0, 0, fix(k1Natural(ps), 6)); return;
  }
  if (v === 'natural_shuffled') {
    const perm = load('k1_perm.u32', Uint32Array);
    const s = new Array(N1); for (let j = 0; j < N1; j++) s[j] = ps[perm[j]]; ps = s;
    if (global.gc) global.gc();
  }
  bench('k1', v, 'energy', reps, () => fix(k1Natural(ps), 6));
}

// ------------------------------------------------------------------ K2
function k2Chase(a, h) { let i = 0; for (let k = 0; k < h; k++) i = a[i]; return i; }
function runK2(v, reps, p) {
  const a = load(`k2_chase_${p}.u32`, Uint32Array);
  bench('k2', v, p, reps, () => String(k2Chase(a, 4200000)));
}

// ------------------------------------------------------------------ Workers génériques
// Les Workers sont créés AVANT la mesure (créer un isolat V8 coûte des dizaines de ms) ;
// la mesure démarre au signal de départ partagé.
function spawn(n, job) {
  return Array.from({ length: n }, (_, t) => new Worker(__filename, { workerData: { ...job, t } }));
}
function runWorkers(workers) { // renvoie une promesse résolue quand tous ont fini
  return Promise.all(workers.map(w => new Promise(res => { w.once('message', res); w.postMessage('go'); })));
}

// ------------------------------------------------------------------ K3
const ITER3 = 1 << 25;
async function runK3(v, reps) {
  const rmw = v.startsWith('rmw'), stride = v.endsWith('padded') ? 32 : 1; // Int32 : 128 o ou 4 o
  console.log(`META;k3_mechanism;${rmw ? 'Atomics.add (lock xadd, 32 bits)' : 'Atomics.load + Atomics.store (store séquentiellement cohérent = xchg ; JS n\'a pas d\'ordre relaxed)'}`);
  const sab = new SharedArrayBuffer(4 * 32 * 5);
  const c = new Int32Array(sab);
  for (let r = -WARMUP; r < reps; r++) {
    for (let t = 0; t < 4; t++) c[32 + t * stride] = 0;
    const ws = spawn(4, { kind: 'k3', sab, rmw, stride });
    await Promise.all(ws.map(w => new Promise(res => w.once('online', res))));
    const t0 = now();
    await runWorkers(ws);
    const dt = Number(now() - t0) * 1e-9;
    ws.forEach(w => w.terminate());
    let s = 0; for (let t = 0; t < 4; t++) s += Atomics.load(c, 32 + t * stride);
    if (r >= 0) result('k3', v, '4x2^25', r, dt, String(s));
  }
}

// ------------------------------------------------------------------ K4
function k4Natural(v) { let s = 0; for (let i = 0; i < v.length; i++) { const x = v[i]; if (x >= 128) s += x; } return s; }
function k4Branchless(v) { let s = 0; for (let i = 0; i < v.length; i++) { const x = v[i]; s += x * (x >> 7); } return s; }
function runK4(v, reps) {
  const d = load('k4_bytes.u8', Uint8Array);
  if (v === 'natural_sorted') d.sort();
  const bl = v === 'branchless_unsorted';
  bench('k4', v, '16M', reps, () => String(bl ? k4Branchless(d) : k4Natural(d)));
}

// ------------------------------------------------------------------ K5
const INNER5 = 1 << 16;
function k5Natural(a, b) { let s = 0; for (let i = 0; i < a.length; i++) s += a[i] * b[i]; return s; }
function k5Tuned(a, b) { // pas de SIMD en JS : 8 accumulateurs indépendants
  let s0 = 0, s1 = 0, s2 = 0, s3 = 0, s4 = 0, s5 = 0, s6 = 0, s7 = 0;
  for (let i = 0; i < a.length; i += 8) {
    s0 += a[i] * b[i]; s1 += a[i + 1] * b[i + 1]; s2 += a[i + 2] * b[i + 2]; s3 += a[i + 3] * b[i + 3];
    s4 += a[i + 4] * b[i + 4]; s5 += a[i + 5] * b[i + 5]; s6 += a[i + 6] * b[i + 6]; s7 += a[i + 7] * b[i + 7];
  }
  return ((s0 + s1) + (s2 + s3)) + ((s4 + s5) + (s6 + s7));
}
const sink = { a: null };
function runK5(v, reps) {
  const a = load('k5_a.f32', Float32Array), b = load('k5_b.f32', Float32Array);
  const f = v === 'tuned' ? k5Tuned : k5Natural;
  bench('k5', v, '2048x65536', reps, () => {
    let d = 0;
    for (let it = 0; it < INNER5; it++) { sink.a = a; d = f(sink.a, b); }
    return fix(d, 4);
  });
}

// ------------------------------------------------------------------ K6
const N6 = 1 << 24;
function q6Natural(c, lo, hi) {
  const { sd, d, q, pr } = c; let s = 0;
  for (let i = lo; i < hi; i++) if (sd[i] >= 8766 && sd[i] < 9131 && d[i] >= 5 && d[i] <= 7 && q[i] < 24) s += pr[i] * d[i];
  return s;
}
function q6Tuned(c, lo, hi) { // prédicat sans branchement en arithmétique 32 bits
  const { sd, d, q, pr } = c; let s0 = 0, s1 = 0;
  for (let i = lo; i < hi; i += 2) {
    const m0 = ((sd[i] - 8766) >>> 0 < 365) & ((d[i] - 5) >>> 0 <= 2) & (q[i] < 24);
    const m1 = ((sd[i + 1] - 8766) >>> 0 < 365) & ((d[i + 1] - 5) >>> 0 <= 2) & (q[i + 1] < 24);
    s0 += (pr[i] * d[i]) * m0; s1 += (pr[i + 1] * d[i + 1]) * m1;
  }
  return s0 + s1;
}
function q1Natural(c, lo, hi, acc) {
  const { sd, pr, q, d, t, rf, ls } = c;
  for (let i = lo; i < hi; i++) {
    if (sd[i] <= 10471) {
      const g = (rf[i] * 2 + ls[i]) * 5, p = pr[i], dp = p * (100 - d[i]);
      acc[g] += 1; acc[g + 1] += q[i]; acc[g + 2] += p; acc[g + 3] += dp; acc[g + 4] += dp * (100 + t[i]);
    }
  }
}
function q1Tuned(c, lo, hi, acc) { // sans branchement : groupe 6 = rejet ; accumulateurs dans un Float64Array
  const { sd, pr, q, d, t, rf, ls } = c;
  const a = new Float64Array(35);
  for (let i = lo; i < hi; i++) {
    const rej = (10471 - sd[i]) >>> 31;            // 1 si sd > 10471
    const g = ((rf[i] * 2 + ls[i]) * (1 - rej) + 6 * rej) * 5;
    const p = pr[i], dp = p * (100 - d[i]);
    a[g] += 1; a[g + 1] += q[i]; a[g + 2] += p; a[g + 3] += dp; a[g + 4] += dp * (100 + t[i]);
  }
  for (let k = 0; k < 30; k++) acc[k] += a[k];
}
const sum = (a) => a.reduce((x, y) => x + y, 0);
const K6COLS = [['sd', 'k6_shipdate.i32', Int32Array], ['pr', 'k6_extendedprice.i32', Int32Array], ['q', 'k6_quantity.u8', Uint8Array],
  ['d', 'k6_discount.u8', Uint8Array], ['t', 'k6_tax.u8', Uint8Array], ['rf', 'k6_returnflag.u8', Uint8Array], ['ls', 'k6_linestatus.u8', Uint8Array]];
async function runK6(v, reps, p) {
  const shared = v === 'mt';
  const c = {}; for (const [k, n, C] of K6COLS) c[k] = shared ? loadShared(n, C) : load(n, C);
  const q1 = p === 'q1';
  if (!shared) {
    bench('k6', v, p, reps, () => {
      if (!q1) return String(v === 'tuned' ? q6Tuned(c, 0, N6) : q6Natural(c, 0, N6));
      const acc = new Array(30).fill(0);
      (v === 'tuned' ? q1Tuned : q1Natural)(c, 0, N6, acc);
      return String(sum(acc));
    });
    return;
  }
  const out = new Float64Array(new SharedArrayBuffer(8 * 4));
  const ws = spawn(4, { kind: 'k6', cols: c, q1, out: out });
  await Promise.all(ws.map(w => new Promise(res => w.once('online', res))));
  await benchAsync('k6', v, p, reps, async () => { await runWorkers(ws); return String(out[0] + out[1] + out[2] + out[3]); });
  ws.forEach(w => w.terminate());
}

// ------------------------------------------------------------------ K7
function runK7(v, reps) {
  const keys = load('k7_keys.u32', Uint32Array), vals = load('k7_vals.u32', Uint32Array);
  for (let r = -WARMUP; r < reps; r++) {
    let nk = 0, ws = 0, dt;
    if (v === 'natural') {
      const t0 = now();
      const m = new Map();
      for (let i = 0; i < keys.length; i++) {
        const e = m.get(keys[i]);
        if (e) { e.count++; e.sum += vals[i]; } else m.set(keys[i], { count: 1, sum: vals[i] });
      }
      dt = Number(now() - t0) * 1e-9;
      nk = m.size; for (const [k, e] of m) ws += e.sum * ((k & 1023) + 1);
    } else {
      const LOG = 21, CAP = 1 << LOG;
      const t0 = now();
      const tab = new Float64Array(4 * CAP); // [clé, compteur, somme, -] : 32 o par case, 2 par ligne
      for (let i = 0; i < keys.length; i++) {
        const k = keys[i];
        let s = Math.imul(k, 0x9E3779B1) >>> (32 - LOG);
        while (tab[4 * s + 1] !== 0 && tab[4 * s] !== k) s = (s + 1) & (CAP - 1);
        tab[4 * s] = k; tab[4 * s + 1] += 1; tab[4 * s + 2] += vals[i];
      }
      dt = Number(now() - t0) * 1e-9;
      for (let s = 0; s < CAP; s++) if (tab[4 * s + 1] !== 0) { nk++; ws += tab[4 * s + 2] * ((tab[4 * s] & 1023) + 1); }
    }
    if (r >= 0) result('k7', v, '16M/1M', r, dt, `${nk}:${ws}`);
  }
}

// ------------------------------------------------------------------ K8
let cnt8 = 0;
function tBuild(dp) { const n = { v: cnt8++, l: null, r: null }; if (dp > 0) { n.l = tBuild(dp - 1); n.r = tBuild(dp - 1); } return n; }
function tSum(n) { return n === null ? 0 : n.v + tSum(n.l) + tSum(n.r); }
const av = new Float64Array(2047), al = new Int32Array(2047), ar = new Int32Array(2047); let top = 0;
function aBuild(dp) { const i = top++; av[i] = cnt8++; al[i] = ar[i] = -1; if (dp > 0) { al[i] = aBuild(dp - 1); ar[i] = aBuild(dp - 1); } return i; }
function aSum(i) { return i < 0 ? 0 : av[i] + aSum(al[i]) + aSum(ar[i]); }
function runK8(v, reps) {
  const Q = 16384, tuned = v === 'tuned';
  cnt8 = 0; const keep = tBuild(20); const lsum = tSum(keep);
  const lat = new Float64Array(Q);
  for (let r = -WARMUP; r < reps; r++) {
    let total = 0; const t0 = now();
    for (let q = 0; q < Q; q++) {
      const a = now(); cnt8 = q;
      let s; if (tuned) { top = 0; s = aSum(aBuild(10)); } else s = tSum(tBuild(10));
      total += s; lat[q] = Number(now() - a);
    }
    const dt = Number(now() - t0) * 1e-9;
    if (r >= 0) {
      result('k8', v, '16384x2047', r, dt, String(total + lsum));
      lat.sort();
      console.log(`LAT;${v};${lat[Q / 2]};${lat[Q * 9 / 10 | 0]};${lat[Q * 99 / 100 | 0]};${lat[Q * 999 / 1000 | 0]};${lat[Q - 1]}`);
    }
  }
  if (keep.v < 0) console.log('');
}

// ------------------------------------------------------------------ K9
const M9 = 2048;
const k9Init = (i, j) => ((i * 31 + j * 17) % 1024) / 1024;
function k9Natural(a, b) {
  for (let i = 1; i < M9 - 1; i++) for (let j = 1; j < M9 - 1; j++)
    b[i][j] = 0.25 * (((a[i - 1][j] + a[i + 1][j]) + a[i][j - 1]) + a[i][j + 1]);
}
function k9Rows(a, b, r0, r1) {
  for (let i = r0; i < r1; i++) {
    const up = (i - 1) * M9, mid = i * M9, dn = (i + 1) * M9;
    for (let j = 1; j < M9 - 1; j++) b[mid + j] = 0.25 * (((a[up + j] + a[dn + j]) + a[mid + j - 1]) + a[mid + j + 1]);
  }
}
const fmtE = (s) => s.toExponential(15).replace(/e\+(\d)$/, 'e+0$1');
async function runK9(v, reps) {
  if (v === 'natural') {
    for (let r = -WARMUP; r < reps; r++) {
      let a = Array.from({ length: M9 }, (_, i) => Array.from({ length: M9 }, (_, j) => k9Init(i, j)));
      let b = a.map(row => row.slice());
      const t0 = now();
      for (let it = 0; it < 4; it++) { k9Natural(a, b); [a, b] = [b, a]; }
      const dt = Number(now() - t0) * 1e-9;
      let s = 0; for (const row of a) for (const x of row) s += x;
      if (r >= 0) result('k9', v, '2048^2x4', r, dt, fmtE(s));
    }
    return;
  }
  const mk = () => { const g = new Float64Array(new SharedArrayBuffer(8 * M9 * M9)); for (let k = 0; k < M9 * M9; k++) g[k] = k9Init((k / M9) | 0, k % M9); return g; };
  const ga = mk(), gb = mk();
  let ws = null;
  if (v === 'mt') { ws = spawn(4, { kind: 'k9', ga, gb }); await Promise.all(ws.map(w => new Promise(res => w.once('online', res)))); }
  for (let r = -WARMUP; r < reps; r++) {
    for (let k = 0; k < M9 * M9; k++) ga[k] = gb[k] = k9Init((k / M9) | 0, k % M9);
    let a = ga, b = gb;
    const t0 = now();
    for (let it = 0; it < 4; it++) {
      if (v === 'tuned') k9Rows(a, b, 1, M9 - 1);
      else await Promise.all(ws.map(w => new Promise(res => { w.once('message', res); w.postMessage(a === ga ? 0 : 1); })));
      [a, b] = [b, a];
    }
    const dt = Number(now() - t0) * 1e-9;
    let s = 0; for (let k = 0; k < M9 * M9; k++) s += a[k];
    if (r >= 0) result('k9', v, '2048^2x4', r, dt, fmtE(s));
  }
  if (ws) ws.forEach(w => w.terminate());
}

// ------------------------------------------------------------------ K10
const M10 = 1 << 22, CAP10 = 1 << 14;
async function runK10(v, reps) {
  for (let r = -WARMUP; r < reps; r++) {
    let dt, s;
    if (v === 'natural') { // postMessage : mécanisme idiomatique entre threads JS
      const w = new Worker(__filename, { workerData: { kind: 'k10n' } });
      await new Promise(res => w.once('online', res));
      const t0 = now();
      s = await new Promise(res => {
        let acc = 0, n = 0;
        w.on('message', (x) => { acc += x; if (++n === M10) res(acc); });
        w.postMessage('go');
      });
      dt = Number(now() - t0) * 1e-9;
      w.terminate();
    } else {
      const ctl = new Int32Array(new SharedArrayBuffer(4 * 96)); // écriture @32, lecture @64 (128 o d'écart)
      const buf = new Float64Array(new SharedArrayBuffer(8 * CAP10));
      const out = new Float64Array(new SharedArrayBuffer(8));
      const ws = [new Worker(__filename, { workerData: { kind: 'k10p', ctl, buf } }), new Worker(__filename, { workerData: { kind: 'k10c', ctl, buf, out } })];
      await Promise.all(ws.map(w => new Promise(res => w.once('online', res))));
      const t0 = now();
      await runWorkers(ws);
      dt = Number(now() - t0) * 1e-9;
      s = out[0];
      ws.forEach(w => w.terminate());
    }
    if (r >= 0) result('k10', v, '2^22', r, dt, String(s));
  }
}

// ------------------------------------------------------------------ côté Worker
function workerMain() {
  const wd = workerData;
  if (wd.kind === 'k10n') { // producteur pour la variante naturelle
    parentPort.once('message', () => { for (let x = 1; x <= M10; x++) parentPort.postMessage(x); });
    return;
  }
  parentPort.on('message', (msg) => {
    if (wd.kind === 'k3') {
      const c = new Int32Array(wd.sab), idx = 32 + wd.t * wd.stride;
      if (wd.rmw) for (let i = 0; i < ITER3; i++) Atomics.add(c, idx, 1);
      else for (let i = 0; i < ITER3; i++) Atomics.store(c, idx, Atomics.load(c, idx) + 1);
      parentPort.postMessage(0);
    } else if (wd.kind === 'k6') {
      const lo = (N6 / 4) * wd.t, hi = (N6 / 4) * (wd.t + 1);
      if (wd.q1) { const acc = new Array(30).fill(0); q1Tuned(wd.cols, lo, hi, acc); wd.out[wd.t] = sum(acc); }
      else wd.out[wd.t] = q6Tuned(wd.cols, lo, hi);
      parentPort.postMessage(0);
    } else if (wd.kind === 'k9') {
      const [a, b] = msg === 0 ? [wd.ga, wd.gb] : [wd.gb, wd.ga];
      k9Rows(a, b, 1 + ((M9 - 2) * wd.t / 4 | 0), 1 + ((M9 - 2) * (wd.t + 1) / 4 | 0));
      parentPort.postMessage(0);
    } else if (wd.kind === 'k10p') {
      const ctl = wd.ctl, buf = wd.buf; let w = 0, rc = 0;
      for (let x = 1; x <= M10; x++) {
        while (w - rc === CAP10) { rc = Atomics.load(ctl, 64); if (w - rc === CAP10 && Atomics.pause) Atomics.pause(); }
        buf[w & (CAP10 - 1)] = x; Atomics.store(ctl, 32, ++w);
      }
      parentPort.postMessage(0);
    } else if (wd.kind === 'k10c') {
      const ctl = wd.ctl, buf = wd.buf; let rd = 0, wc = 0, s = 0;
      for (let k = 0; k < M10; k++) {
        while (rd === wc) { wc = Atomics.load(ctl, 32); if (rd === wc && Atomics.pause) Atomics.pause(); }
        s += buf[rd & (CAP10 - 1)]; Atomics.store(ctl, 64, ++rd);
      }
      wd.out[0] = s;
      parentPort.postMessage(0);
    }
  });
}

async function main() {
  const [k, v, repsS, p = ''] = process.argv.slice(2);
  const reps = parseInt(repsS, 10);
  switch (k) {
    case 'k1': runK1(v, reps); break;
    case 'k2': runK2(v, reps, p); break;
    case 'k3': await runK3(v, reps); break;
    case 'k4': runK4(v, reps); break;
    case 'k5': runK5(v, reps); break;
    case 'k6': await runK6(v, reps, p); break;
    case 'k7': runK7(v, reps); break;
    case 'k8': runK8(v, reps); break;
    case 'k9': await runK9(v, reps); break;
    case 'k10': await runK10(v, reps); break;
  }
}
if (isMainThread) main(); else workerMain();
