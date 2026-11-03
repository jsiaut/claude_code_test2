#!/usr/bin/env python3
"""Copies de la remarque sur JavaScript (plan : docs/JAVASCRIPT.md, section 3.3), produites par remplacements de texte
contrôlés (chaque texte remplacé doit apparaître exactement une fois ; le reste du fichier est identique à l'octet).

* bench/js_ref : copie exacte de bench/js_k9h (le code publié : bench/js, harnais commun de K9), Node.js 26.12.1.
* bench/js_fix : correction publiée : K7 tuned en cases de 16 octets (clé et compteur en u32, somme en f64, par deux
  vues typées sur le même ArrayBuffer), comme la référence C et toutes les autres implémentations qui disposent la
  mémoire (Java tasse clé et compteur dans un long pour y arriver), au lieu de 32 octets (quatre f64) par case.
* bench/js_exp : js_fix et des variantes nouvelles (sensibilités) : K6 `tuned_m` et `mt_m` (Q6 : masque par négation et
  sommes entières par blocs, comme q6_tuned en C), K9 `tuned_v` et `mt_v` (vues de lignes, voisins gardés dans des
  variables), K8 `natural_s` (arbre longue durée construit par une fonction à part : site d'allocation distinct, contre
  le pretenuring de V8), K8 `tuned_it` (arène construite et parcourue par itération, comme la copie c_k8it de C), K5
  `tuned_f64` (données copiées en f64 hors chrono), K1 `soa_f64` (colonnes en f64).
* bench/js_n22 : le source de js_ref exécuté par Node.js 22.22.0 (V8 12.4), en information (Q1).
Usage : make_copies.py"""
import os, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NOTE = "// remarque sur JavaScript (docs/JAVASCRIPT.md) : "


def sub(text, old, new):
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"texte trouvé {n} fois (1 attendu) :\n{old[:300]}")
    return text.replace(old, new)


FIX = [
    # K7 tuned : 16 octets par case
    ("""      const tab = new Float64Array(4 * CAP); // [clé, compteur, somme, -] : 32 o par case, 2 par ligne
      for (let i = 0; i < keys.length; i++) {
        const k = keys[i];
        let s = Math.imul(k, 0x9E3779B1) >>> (32 - LOG);
        while (tab[4 * s + 1] !== 0 && tab[4 * s] !== k) s = (s + 1) & (CAP - 1);
        tab[4 * s] = k; tab[4 * s + 1] += 1; tab[4 * s + 2] += vals[i];
      }
      dt = Number(now() - t0) * 1e-9;
      for (let s = 0; s < CAP; s++) if (tab[4 * s + 1] !== 0) { nk++; ws += tab[4 * s + 2] * ((tab[4 * s] & 1023) + 1); }
""",
     """      """ + NOTE + """cases de 16 o comme en C et dans les autres implémentations :
      // [clé u32, compteur u32, somme f64], par deux vues typées sur le même ArrayBuffer ; 4 cases par ligne
      const tb = new ArrayBuffer(16 * CAP), tk = new Uint32Array(tb), tsum = new Float64Array(tb);
      for (let i = 0; i < keys.length; i++) {
        const k = keys[i];
        let s = Math.imul(k, 0x9E3779B1) >>> (32 - LOG);
        while (tk[4 * s + 1] !== 0 && tk[4 * s] !== k) s = (s + 1) & (CAP - 1);
        tk[4 * s] = k; tk[4 * s + 1] += 1; tsum[2 * s + 1] += vals[i];
      }
      dt = Number(now() - t0) * 1e-9;
      for (let s = 0; s < CAP; s++) if (tk[4 * s + 1] !== 0) { nk++; ws += tsum[2 * s + 1] * ((tk[4 * s] & 1023) + 1); }
"""),
]


def fix(text):
    for a, b in FIX:
        text = sub(text, a, b)
    return text


EXP = [
    # K6 Q6 : masque par négation, sommes entières par blocs
    ("""function q1Natural(c, lo, hi, acc) {""",
     NOTE + """sensibilité : masque par négation et sommes entières (32 bits) par blocs de
// 4096 lignes, comme q6_tuned en C (|pr·d| <= 500 000 dans les données : la somme d'un bloc tient sur 32 bits)
function q6TunedM(c, lo, hi) {
  const { sd, d, q, pr } = c; let s = 0;
  for (let i0 = lo; i0 < hi; i0 += 4096) {
    const e = Math.min(i0 + 4096, hi); let b = 0;
    for (let i = i0; i < e; i++) {
      const m = ((sd[i] - 8766) >>> 0 < 365) & ((d[i] - 5) >>> 0 <= 2) & (q[i] < 24);
      b = (b + ((pr[i] * d[i]) & -m)) | 0;
    }
    s += b;
  }
  return s;
}
function q1Natural(c, lo, hi, acc) {"""),
    ("""  const shared = v === 'mt';""", """  const shared = v === 'mt' || v === 'mt_m';"""),
    ("""      if (!q1) return String(v === 'tuned' ? q6Tuned(c, 0, N6) : q6Natural(c, 0, N6));""",
     """      if (!q1) return String(v === 'tuned' ? q6Tuned(c, 0, N6) : v === 'tuned_m' ? q6TunedM(c, 0, N6) : q6Natural(c, 0, N6));"""),
    ("""  const ws = spawn(4, { kind: 'k6', cols: c, q1, out: out });""",
     """  const ws = spawn(4, { kind: 'k6', cols: c, q1, out: out, m: v === 'mt_m' });"""),
    ("""      else wd.out[wd.t] = q6Tuned(wd.cols, lo, hi);""",
     """      else wd.out[wd.t] = wd.m ? q6TunedM(wd.cols, lo, hi) : q6Tuned(wd.cols, lo, hi);"""),
    # K9 : vues de lignes, voisins dans des variables
    ("""const fmtE = (s) =>""",
     NOTE + """sensibilité : vues de lignes (subarray), voisins de gauche et du centre gardés
// dans des variables ; même ordre d'évaluation, résultat identique au bit
function k9RowsV(a, b, r0, r1) {
  for (let i = r0; i < r1; i++) {
    const up = a.subarray((i - 1) * M9, i * M9), mid = a.subarray(i * M9, (i + 1) * M9);
    const dn = a.subarray((i + 1) * M9, (i + 2) * M9), o = b.subarray(i * M9, (i + 1) * M9);
    let w = mid[0], c = mid[1];
    for (let j = 1; j < M9 - 1; j++) { const e = mid[j + 1]; o[j] = 0.25 * (((up[j] + dn[j]) + w) + e); w = c; c = e; }
  }
}
const fmtE = (s) =>"""),
    ("""  if (v === 'mt') { ws = spawn(4, { kind: 'k9', ga, gb }); """,
     """  if (v === 'mt' || v === 'mt_v') { ws = spawn(4, { kind: 'k9', ga, gb, rv: v === 'mt_v' }); """),
    ("""      if (v === 'tuned') k9Rows(a, b, 1, M9 - 1);
""", """      if (v === 'tuned') k9Rows(a, b, 1, M9 - 1);
      else if (v === 'tuned_v') k9RowsV(a, b, 1, M9 - 1);
"""),
    ("""      k9Rows(a, b, 1 + ((M9 - 2) * wd.t / 4 | 0), 1 + ((M9 - 2) * (wd.t + 1) / 4 | 0));""",
     """      (wd.rv ? k9RowsV : k9Rows)(a, b, 1 + ((M9 - 2) * wd.t / 4 | 0), 1 + ((M9 - 2) * (wd.t + 1) / 4 | 0));"""),
    # K8 : site d'allocation distinct pour l'arbre longue durée ; arène itérative
    ("""function tSum(n) {""",
     NOTE + """sensibilité : l'arbre longue durée construit par une fonction à part (site
// d'allocation distinct de celui des arbres des requêtes)
function tBuildLong(dp) { const n = { v: cnt8++, l: null, r: null }; if (dp > 0) { n.l = tBuildLong(dp - 1); n.r = tBuildLong(dp - 1); } return n; }
function tSum(n) {"""),
    ("""function runK8(v, reps) {""",
     NOTE + """sensibilité : arène construite et parcourue par itération (piles explicites),
// mêmes nœuds, mêmes valeurs, même ordre préfixe que aBuild et aSum (comme la copie c_k8it de C)
const stN = new Int32Array(64), stD = new Int32Array(64), stS = new Int8Array(64), stQ = new Int32Array(64);
function aNode(i) { av[i] = cnt8++; al[i] = ar[i] = -1; return i; }
function aBuildIt(dp0) {
  const root = aNode(top++); let sp = 0;
  if (dp0 > 0) { stN[0] = root; stD[0] = dp0; stS[0] = 0; sp = 1; }
  while (sp > 0) {
    const k = sp - 1, n = stN[k], d = stD[k];
    const c = aNode(top++);
    if (stS[k] === 0) { stS[k] = 1; al[n] = c; } else { sp--; ar[n] = c; }
    if (d > 1) { stN[sp] = c; stD[sp] = d - 1; stS[sp] = 0; sp++; }
  }
  return root;
}
function aSumIt(root) {
  let s = 0, sp = 0; stQ[sp++] = root;
  while (sp > 0) { const n = stQ[--sp]; s += av[n]; if (al[n] >= 0) { stQ[sp++] = ar[n]; stQ[sp++] = al[n]; } }
  return s;
}
function runK8(v, reps) {"""),
    ("""  const Q = 16384, tuned = v === 'tuned';
  cnt8 = 0; const keep = tBuild(20); const lsum = tSum(keep);""",
     """  const Q = 16384, tuned = v === 'tuned' || v === 'tuned_it', it8 = v === 'tuned_it';
  cnt8 = 0; const keep = (v === 'natural_s' ? tBuildLong : tBuild)(20); const lsum = tSum(keep);"""),
    ("""      let s; if (tuned) { top = 0; s = aSum(aBuild(10)); } else s = tSum(tBuild(10));""",
     """      let s; if (it8) { top = 0; s = aSumIt(aBuildIt(10)); } else if (tuned) { top = 0; s = aSum(aBuild(10)); } else s = tSum(tBuild(10));"""),
    # K5 : données copiées en f64 hors chrono
    ("""  const a = load('k5_a.f32', Float32Array), b = load('k5_b.f32', Float32Array);
  const f = v === 'tuned' ? k5Tuned : k5Natural;""",
     """  let a = load('k5_a.f32', Float32Array), b = load('k5_b.f32', Float32Array);
  if (v === 'tuned_f64') { a = Float64Array.from(a); b = Float64Array.from(b); } """ + NOTE + """sensibilité, données en f64
  const f = v === 'tuned' || v === 'tuned_f64' ? k5Tuned : k5Natural;"""),
    # K1 : colonnes en f64
    ("""  if (v === 'soa') {""",
     """  if (v === 'soa_f64') { """ + NOTE + """sensibilité : colonnes en f64
    const c = []; for (let k = 0; k < 16; k++) { const a = new Float64Array(N1); for (let i = 0; i < N1; i++) a[i] = raw[16 * i + k]; c.push(a); }
    bench('k1', v, 'energy', reps, () => fix(k1SoA(c[3], c[4], c[5], c[9]), 6)); return;
  }
  if (v === 'soa') {"""),
]


def exp(text):
    text = fix(text)
    for a, b in EXP:
        text = sub(text, a, b)
    return text


RUN_N22 = """#!/bin/sh
# Information (remarque sur JavaScript, docs/JAVASCRIPT.md) : le source de js_ref exécuté par Node.js 22.22.0 (V8 12.4)
exec /opt/node22/bin/node --expose-gc --max-old-space-size=8192 "$(dirname "$0")/../js_ref/ms.js" "$@"
"""
BUILD_N22 = """#!/bin/sh
# Node.js 22.22.0 (V8 12.4) : rien à compiler
/opt/node22/bin/node --check "$(dirname "$0")/../js_ref/ms.js"
"""


def copy(dst, text):
    d = os.path.join(ROOT, "bench", dst)
    if os.path.exists(d):
        shutil.rmtree(d)
    os.makedirs(d)
    open(os.path.join(d, "ms.js"), "w", encoding="utf-8").write(text)
    for f in ("run", "build.sh"):
        shutil.copy2(os.path.join(ROOT, "bench", "js_k9h", f), os.path.join(d, f))
    print(f"{dst} écrit")


def main():
    src = open(os.path.join(ROOT, "bench", "js_k9h", "ms.js"), encoding="utf-8").read()
    copy("js_ref", src)
    copy("js_fix", fix(src))
    copy("js_exp", exp(src))
    open(os.path.join(ROOT, "bench", "js_exp", "extra_variants"), "w").write(
        "k6 tuned_m q6\nk6 mt_m q6\nk9 tuned_v\nk9 mt_v\nk8 natural_s\nk8 tuned_it\nk5 tuned_f64\nk1 soa_f64 energy\n")
    d = os.path.join(ROOT, "bench", "js_n22")
    if os.path.exists(d):
        shutil.rmtree(d)
    os.makedirs(d)
    for f, t in (("run", RUN_N22), ("build.sh", BUILD_N22)):
        open(os.path.join(d, f), "w").write(t)
        os.chmod(os.path.join(d, f), 0o755)
    print("js_n22 écrit")


if __name__ == "__main__":
    main()
