const sab = new SharedArrayBuffer(64); const i32 = new Int32Array(sab);
Atomics.add(i32, 0, 1); Atomics.pause();
console.log(`CAP;D5;0.5;Atomics.pause existe (${typeof Atomics.pause}) ; pas de barrière explicite`);
const buf = new ArrayBuffer(4); new Float32Array(buf)[0] = 1.0;
console.log(`CAP;A5;0.5;vues typées sur un même ArrayBuffer : 0x${new Uint32Array(buf)[0].toString(16)}`);
