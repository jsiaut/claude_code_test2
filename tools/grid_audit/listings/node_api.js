// API publique de la construction Node du banc : propriétés de l'objet global (et de leurs prototypes) et exports
// des modules intégrés (require('module').builtinModules, et les membres de leurs classes), un nom par ligne, pour
// tools/grid_audit/search.py.
const seen = new Set();
const out = new Set();
function walk(prefix, obj, depth) {
  if (obj === process.env) return;                // variables d'environnement : état, pas API
  if (obj === null || (typeof obj !== 'object' && typeof obj !== 'function') || depth > 2 || seen.has(obj)) return;
  seen.add(obj);
  let names = [];
  try { names = Object.getOwnPropertyNames(obj); } catch (e) { return; }
  for (const k of names) {
    if (k === 'caller' || k === 'arguments' || k === 'callee' || k === '_pathCache' || /[\x00-\x1f\/]/.test(k)) continue;
    out.add(prefix + '.' + k);
    let d;
    try { d = Object.getOwnPropertyDescriptor(obj, k); } catch (e) { continue; }
    if (!d || !('value' in d)) continue;          // accesseurs : nommés, jamais appelés
    const v = d.value;
    if (typeof v === 'function' && v.prototype) walk(prefix + '.' + k + '.prototype', v.prototype, depth + 1);
    if (typeof v === 'object' || typeof v === 'function') walk(prefix + '.' + k, v, depth + 1);
  }
}
process.removeAllListeners('warning');
process.on('warning', () => {});
process.on('unhandledRejection', () => {});
walk('globalThis', globalThis, 0);
for (const m of require('module').builtinModules) {
  let mod;
  try { mod = require(m.startsWith('node:') ? m : 'node:' + m); } catch (e) { continue; }
  walk('module ' + m, mod, 0);
}
for (const extra of ['node:ffi', 'node:sqlite', 'node:test', 'node:sea']) {
  try { walk('module ' + extra.slice(5), require(extra), 0); } catch (e) {}
}
console.log([...out].sort().join('\n'));
