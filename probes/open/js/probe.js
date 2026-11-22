// v4, point 6 (docs/V4_OPEN.md, 4) : sondes de la grille ouverte de JavaScript
// (B2 : @protobufjs/pool 1.1.0 ; F1 : ndarray 1.1.1). Exécutée par Node 26 avec les modules de /opt/open/js.
const path = "/opt/open/js/node_modules/";
const pool = require(path + "@protobufjs/pool");
const ndarray = require(path + "ndarray");

// B2 : tranches d'un bloc commun ; nœuds (valeur, deux liens) écrits dans des vues typées
function b2() {
  const alloc = pool((n) => new Uint8Array(n), Uint8Array.prototype.subarray, 8192);
  const slices = [];
  for (let i = 0; i < 100; i++) slices.push(alloc(24));
  const sameBlock = slices.slice(0, 50).every((s) => s.buffer === slices[0].buffer);
  const offsets = slices.slice(0, 5).map((s) => s.byteOffset);
  // un nœud = [valeur f64, lien gauche i32, lien droit i32] dans une tranche de 16 octets
  const nodes = [];
  for (let i = 0; i < 100; i++) {
    const s = alloc(16);
    const dv = new DataView(s.buffer, s.byteOffset, 16);
    dv.setFloat64(0, i, true); dv.setInt32(8, i - 1, true); dv.setInt32(12, -1, true);
    nodes.push(dv);
  }
  let sum = 0, k = 99;
  while (k >= 0) { sum += nodes[k].getFloat64(0, true); k = nodes[k].getInt32(8, true); }
  const big = alloc(8192);
  console.log(`RESULT;B2;@protobufjs/pool;pool(alloc, subarray, 8192) : 100 tranches de 24 octets, les 50 premières dans le même ArrayBuffer = ${sameBlock}, décalages ${JSON.stringify(offsets)} ; 100 nœuds (valeur, deux liens) en tranches de 16 octets, somme en suivant les liens = ${sum} ; une demande >= 4096 octets est allouée à part : ${big.buffer.byteLength} octets, hors du bloc = ${big.buffer !== slices[0].buffer}`);
}

// F1 : vue n-dimensionnelle sur un tableau typé contigu
function f1() {
  const m = process.argv.length * 150, n = 500;
  const data = new Float64Array(m * n);
  const a = ndarray(data, [m, n]);
  a.set(2, 3, 7);
  const idx = data.indexOf(7);
  const row = a.pick(2, null);
  console.log(`RESULT;F1;ndarray;ndarray(Float64Array(${m * n}), [${m}, ${n}]) de dimensions connues à l'exécution : shape ${JSON.stringify(a.shape)}, stride ${JSON.stringify(a.stride)}, a.get(2, 3) = ${a.get(2, 3)} écrit à l'indice ${idx} du tableau typé (2*${n}+3) ; pick(2, null) est une vue de forme ${JSON.stringify(row.shape)} ; le paquet n'a aucune opération de calcul (vues seulement)`);
}

b2(); f1();
