const c = new Int32Array(new SharedArrayBuffer(4 * 32 * 5));
function rmw(c, idx, n) { for (let i = 0; i < n; i++) Atomics.add(c, idx, 1); }
function sw(c, idx, n) { for (let i = 0; i < n; i++) Atomics.store(c, idx, Atomics.load(c, idx) + 1); }
for (let r = 0; r < 200; r++) { rmw(c, 32, 100000); sw(c, 64, 100000); }
console.log(c[32], c[64]);
