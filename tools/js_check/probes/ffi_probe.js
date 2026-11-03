const ffi = require('node:ffi');
const show = (name) => { const f = ffi[name]; console.log(name, typeof f, f && f.length); };
['getRawPointer', 'getFloat64', 'setFloat64', 'toArrayBuffer', 'exportArrayBuffer', 'dlopen', 'dlsym', 'DynamicLibrary', 'types'].forEach(show);
const ab = new ArrayBuffer(4096 + 64);
let p;
try { p = ffi.getRawPointer(ab); console.log('getRawPointer(ArrayBuffer) =', typeof p, p, 'mod 64 =', Number(BigInt(p) % 64n)); } catch (e) { console.log('getRawPointer(ab) erreur :', e.message); }
try { const u8 = new Uint8Array(ab, 8, 16); console.log('getRawPointer(view) =', ffi.getRawPointer(u8)); } catch (e) { console.log('getRawPointer(view) erreur :', e.message); }
try { ffi.setFloat64(p, 16, 3.25); console.log('setFloat64/getFloat64 :', ffi.getFloat64(p, 16), new Float64Array(ab, 16, 1)[0]); } catch (e) { console.log('set/get erreur :', e.message); }
try { const small = new Float64Array(ab, 0, 2); console.log('lecture au-delà de la vue (offset 2048) :', ffi.getFloat64(ffi.getRawPointer(small), 2048)); } catch (e) { console.log('au-delà erreur :', e.message); }
try { const ab2 = ffi.toArrayBuffer(p, 64); console.log('toArrayBuffer :', ab2.byteLength, new Float64Array(ab2)[2]); } catch (e) { console.log('toArrayBuffer erreur :', e.message); }
console.log('types :', ffi.types && Object.keys(ffi.types).slice(0, 30).join(','));
