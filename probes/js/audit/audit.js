// Audit de la grille, JavaScript (Node 26.12.1, V8 ; réglages du banc : --expose-gc) : chaque case est exercée sous
// sa forme la plus forte et imprime un fait observable (docs/V4_PLAN.md 2.1). Lignes FACT (reprises par run.sh avec
// le code machine, les formes refusées et les recherches) et NOTE (contre-épreuves).
'use strict';
const v8 = require('node:v8');
const { PerformanceObserver } = require('node:perf_hooks');
const { Worker } = require('node:worker_threads');
const fs = require('node:fs');
process.removeAllListeners('warning');
const warnings = [];
process.on('warning', (w) => warnings.push(w.name + ': ' + w.message));
const fact = (c, ev) => console.log(`FACT;${c};${ev}`);
const note = (c, ev) => console.log(`NOTE;${c};${ev}`);
const used = () => { gc(); gc(); return v8.getHeapStatistics().used_heap_size; };
let gcEvents = 0;
const obs = new PerformanceObserver((list) => { gcEvents += list.getEntries().length; });
obs.observe({ entryTypes: ['gc'] });
const tick = () => new Promise((r) => setImmediate(r));
let sink;

async function main() {
  // ---------- A
  const n = 100000;
  let h0 = used();
  const arr = new Array(n);
  for (let i = 0; i < n; i++) arr[i] = { x: i + 0.5, y: 0.5, z: 0.5, w: 0.5 };
  let h1 = used();
  fact('A1', `tableau de ${n} objets {x, y, z, w} (flottants) : ${Math.round((h1 - h0) / n)} o de tas par élément pour 32 o de données (références vers des objets séparés, nombres non entiers en boîtes)`);
  sink = arr;
  const ffi = require('node:ffi');
  const ab = new ArrayBuffer(256 + 63);
  const raw = ffi.getRawPointer(ab);
  const al = (raw + 63n) & ~63n;
  fact('A4', `node:ffi (expérimental) : getRawPointer(ArrayBuffer) = ${raw % 64n} mod 64, adresse arrondie à la main ${al % 64n} mod 64 ; aucun paramètre d'alignement pour ArrayBuffer ni tableaux typés`);
  const b4 = new ArrayBuffer(4);
  new Float32Array(b4)[0] = 1.0;
  fact('A5', `vues typées sur un même ArrayBuffer : Float32Array 1.0 relu par Uint32Array = 0x${new Uint32Array(b4)[0].toString(16)} ; DataView.getUint32 = 0x${new DataView(b4).getUint32(0, true).toString(16)}`);
  h0 = used();
  const objs = new Array(10000);
  for (let i = 0; i < 10000; i++) objs[i] = { f: new Float32Array(16), n: i };
  h1 = used();
  fact('A7', `{f: Float32Array(16), n} : ${Math.round((h1 - h0) / 10000)} o de tas par objet pour 68 o de données (le tableau typé et son ArrayBuffer sont des objets séparés)`);
  sink = objs;
  fact('A8', `BYTES_PER_ELEMENT : Int8Array ${Int8Array.BYTES_PER_ELEMENT}, Int16Array ${Int16Array.BYTES_PER_ELEMENT}, Float16Array ${Float16Array.BYTES_PER_ELEMENT}, Float32Array ${Float32Array.BYTES_PER_ELEMENT} (stockage) ; lus, ce sont des Number de 64 bits (typeof ${typeof new Int8Array(1)[0]})`);

  // ---------- B
  await tick(); let g0 = gcEvents;
  for (let i = 0; i < 1 << 20; i++) sink = new Uint8Array(1024);
  await tick(); await tick();
  fact('B1', `1 Gio de Uint8Array(1024) sans référence : ${gcEvents - g0} collectes signalées par PerformanceObserver('gc'), sans appel du programme (ramasse-miettes traçant)`);
  const allocd = () => v8.getHeapStatistics().total_allocated_bytes;
  const escaped = (k) => { const slot = [null]; for (let i = 0; i < k; i++) slot[0] = { a: i, b: i + 1 }; return slot; };
  const local = (k) => { let t = 0; for (let i = 0; i < k; i++) { const p = { a: i, b: i + 1 }; t += p.a + p.b; } return t; };
  const closures = (k) => { const f = [null]; for (let i = 0; i < k; i++) f[0] = () => i; return f; };
  const boxed = (k) => { const b = [0.5, 'x']; for (let i = 0; i < k; i++) b[0] = i + 0.5; return b; };
  const per = (fn) => { for (let r = 0; r < 20; r++) sink = fn(100000); const a0 = allocd(); sink = fn(1e6); return ((allocd() - a0) / 1e6).toFixed(1); };
  fact('B3', `octets alloués par itération (v8 total_allocated_bytes, fonctions déjà optimisées) : objet {a, b} gardé dans un tableau ${per(escaped)} ; objet resté local ${per(local)} (l'analyse d'échappement de TurboFan le supprime, sans garantie du langage) ; aucune valeur composée en place`);
  fact('B4', `allocations implicites, octets par itération : fermeture créée ${per(closures)} ; flottant rangé dans un tableau générique ${per(boxed)} (boîte HeapNumber)`);
  const ib = new ArrayBuffer(32);
  const i32 = new Int32Array(ib);
  new DataView(ib).setInt32(12, 42, true);
  ffi.setInt32(ffi.getRawPointer(ib), 16, 7);
  fact('B5', `ArrayBuffer + DataView.setInt32(12, 42) → i32[3] = ${i32[3]} ; node:ffi.setInt32(getRawPointer(ib), 16, 7) → i32[4] = ${i32[4]} (pointeur brut, expérimental)`);

  // ---------- C
  fact('C1', `typeof SIMD = ${typeof globalThis.SIMD} (SIMD.js retiré) ; le SIMD de WebAssembly n'est pas exposé à JavaScript`);
  let st = 42n;
  const big = new Float64Array(1 << 20);
  for (let i = 0; i < big.length; i++) { st = (st * 6364136223846793005n + 1442695040888963407n) & 0xffffffffffffffffn; big[i] = Number(st >> 11n) / 2 ** 53 - 0.5; }
  let s = 0;
  for (let r = 0; r < 20; r++) { s = 0; for (let i = 0; i < big.length; i++) s += big[i]; }
  const pairwise = (a, lo, hi) => { if (hi - lo <= 8) { let t = 0; for (let i = lo; i < hi; i++) t += a[i]; return t; } const m = (lo + hi) >> 1; return pairwise(a, lo, m) + pairwise(a, m, hi); };
  const pw = pairwise(big, 0, big.length);
  fact('C4', `un million de Number : boucle optimisée par TurboFan ${s}, somme par paires écrite à la main ${pw} (écart ${Math.abs(pw - s).toExponential(3)}) : l'ordre est gardé, aucune option de réassociation`);

  // ---------- D
  const sab = new SharedArrayBuffer(16);
  const cnt = new Int32Array(sab);
  const code = `const { workerData, parentPort } = require('node:worker_threads');
    const c = new Int32Array(workerData.sab); for (let i = 0; i < 1000; i++) Atomics.add(c, 0, 1);
    workerData.obj.v = 99; parentPort.postMessage(workerData.obj.v);`;
  const obj = { v: 1 };
  const ws = [];
  for (let t = 0; t < 4; t++) ws.push(new Promise((res) => { const w = new Worker(code, { eval: true, workerData: { sab, obj } }); w.on('message', (m) => res(m)); }));
  const seenV = await Promise.all(ws);
  fact('D1', `4 Worker (worker_threads) sur un SharedArrayBuffer : ${Atomics.load(cnt, 0)} incréments ; un objet passé au fil y vaut ${seenV[0]} après modification, ici toujours ${obj.v} (copié : fils isolés, mémoire partagée par SharedArrayBuffer seulement)`);
  const a2 = new Int32Array(new SharedArrayBuffer(8));
  Atomics.store(a2, 0, 5);
  const old = Atomics.compareExchange(a2, 0, 5, 8);
  const prev = Atomics.add(a2, 0, 3);
  fact('D2', `Atomics : store 5, compareExchange(5, 8) → ${old}, add 3 → ${prev} puis ${Atomics.load(a2, 0)} (séquentiellement cohérents) ; Atomics.wait/notify`);
  for (let i = 0; i < 10; i++) Atomics.pause();
  fact('D5', `Atomics.pause (${typeof Atomics.pause}) exécuté ; aucune barrière explicite (Atomics est séquentiellement cohérent)`);
  const libc = ffi.dlopen('libc.so.6', {
    sched_setaffinity: { return: 'int32', arguments: ['int32', 'uint64', 'pointer'] },
    sched_getcpu: { return: 'int32', arguments: [] },
    mmap: { return: 'pointer', arguments: ['pointer', 'uint64', 'int32', 'int32', 'int32', 'int64'] },
  });
  const mask = new BigUint64Array(16); mask[0] = 2n;
  const rc = libc.functions.sched_setaffinity(0, 128n, ffi.getRawPointer(mask.buffer));
  note('D4', `sched_setaffinity de la glibc par node:ffi (expérimental) : retour ${rc}, processeur courant ${libc.functions.sched_getcpu()} (FFI vers la libc, non comptée)`);

  // ---------- E
  const ta = new Float64Array(4);
  const fa = ffi.getRawPointer(ta.buffer);
  fact('E6', `tableau typé : ta[10] = ${ta[10]} (lecture vérifiée, hors bornes → undefined) ; node:ffi.getFloat64(adresse, 80) lit hors du tampon de 32 o sans contrôle (${typeof ffi.getFloat64(fa, 80)}), expérimental`);

  // ---------- F
  const rows = [];
  for (let i = 0; i < 3; i++) rows.push(new Float64Array(4));
  rows[1] = new Float64Array(7);
  fact('F1', `pas de tableau multidimensionnel : tableau de lignes séparées (rows[1] remplacée par une ligne de ${rows[1].length}), indexation à la main dans un Float64Array à plat`);
  fact('F3', `(2 ** 31) | 0 = ${(2 ** 31) | 0}, -1 >>> 0 = ${-1 >>> 0}, Math.imul(0x7fffffff, 2) = ${Math.imul(0x7fffffff, 2)}, BigInt.asUintN(64, -1n) = ${BigInt.asUintN(64, -1n)} ; un seul type de nombre (f64)`);
  const fd = fs.openSync('/opt/msdata/k5_a.f32', 'r');
  const mp = libc.functions.mmap(0n, 8192n, 1, 2, fd, 0n);
  note('F4', `mmap de la glibc par node:ffi : premier float ${ffi.getFloat32(mp, 0).toPrecision(7)} (FFI vers la libc, non comptée)`);
  note('FFI', `avertissements : ${[...new Set(warnings)].join(' | ')}`);
  obs.disconnect();
}
main();
