function k5(a, b) { let s = 0; for (let i = 0; i < a.length; i++) s += a[i] * b[i]; return s; }
const a = new Float32Array(4096).fill(1.5), b = new Float32Array(4096).fill(2);
let d = 0; for (let it = 0; it < 20000; it++) d += k5(a, b);
console.log(d);
