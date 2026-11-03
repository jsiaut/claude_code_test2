# Remarque sur JavaScript : sondes de vérification (machine 21, 3 novembre, avant le plan)

Moteurs : Node.js 26.12.1 (V8 14.6.202.34-node.40, celui de l'étude), Node.js 22.22.0 (V8 12.4), Bun 1.4.4. Sources des
sondes : `tools/js_check/probes/`. Temps : un processus, liste des répétitions.

* Compilation de Node 26 (`process.config.variables`) : `v8_enable_pointer_compression` = 0, `v8_enable_sandbox` = 0.
  Pas d'objet `SIMD` ; `WebAssembly`, `BigInt64Array`, `Float16Array`, `Math.f16round` et `Atomics.pause` présents.
* `--print-opt-code` (`k5_poc.js`) : le code machine de TurboFan s'affiche avec les binaires officiels de Node 26
  (`kind = TURBOFAN_JS`) et de Node 22 (`kind = TURBOFAN`) : `vmovss`, `vcvtss2sd`, `vmulsd`…
* `node:ffi` (`ffi_probe.js`, sortie `ffi_probe.txt`) : chargé par défaut, avec l'avertissement « ExperimentalWarning:
  FFI is an experimental feature » ; `getRawPointer` d'un `ArrayBuffer` rend son adresse (ici congrue à 32 modulo 64) ;
  `setFloat64` et `getFloat64` écrivent et lisent par pointeur, sans vérification (lecture au-delà d'une vue) ;
  `toArrayBuffer` enveloppe de la mémoire brute.
* K3 (`k3_atomics.js`, `k3_atomics_turbofan.txt`) : `Atomics.add`, `Atomics.load` et `Atomics.store` deviennent des
  appels aux fonctions internes `AtomicsAdd`, `AtomicsLoad`, `AtomicsStore`, sous Node 26 comme sous Node 22.
* K5 (`k5_tuned_turbofan_node26.txt`) : la boucle de `k5Tuned` porte, pour 8 éléments, 16 vérifications de bornes
  (`cmpq`, `jnc`), 8 vérifications de débordement (`jo` : 7 indices et l'incrément), un `leaq` qui recalcule l'adresse
  du tableau avant chaque chargement, et ses accumulateurs relus depuis la pile (`vaddsd xmm, xmm, [rbp-…]`).
* K8 naturel (`bench/js_k9h/ms.js`, `k8 natural 3`) : publié 1,099, 1,152, 1,135 s, pire pause 70,7, 87,8, 76,4 ms ;
  `--no-allocation-site-pretenuring` 0,697, 0,764, 0,702 s, pire pause 1,2, 1,0, 1,2 ms ; arbre longue durée construit
  par une fonction à part (comme la variante `natural_s` de `js_exp`) 0,739, 0,731, 0,666 s, pire pause 4,3, 9,1,
  0,8 ms.
* Q1 (`k6 tuned|natural 4 q1`) : Node 26 tuned 262,9, 262,7, 260,4, 258,4 ms, naturel 249,5, 247,2, 273,6, 309,7 ;
  Node 22 tuned 133,3, 120,9, 117,9, 114,2, naturel 143,7, 135,6, 118,5, 117,1 ; Node 26 avec `--turbolev` (désactivé
  par défaut) tuned 179,4, 176,9, 176,7, 178,9, naturel 161,1, 152,9, 152,1, 156,1 ; Node 26 avec `--no-maglev` tuned
  259,6, 260,4, 260,0, 259,4.
* K7 tuned et OSR (`k7 tuned 4`, copie `js_fix`) : construction de la table en ligne 890, 1 162, 813, 627 ms ; dans une
  fonction appelée à chaque répétition 887, 858, 645, 724 ms.
* Validation des copies (`validate_timings.txt`, un processus par cellule, sommes de contrôle justes) : K7 tuned 1 517 →
  861 ms ; Q6 tuned 96 à 98 → 58 à 62 ms (`mt` 29 à 43 → 22 à 24) ; K9 tuned 58 à 74 → 52 à 54 ms (`mt` 22 à 24 → 24
  à 29) ; K8 naturel 1 099 → 714 ms (site distinct), K8 tuned 404 → 293 ms (itératif) ; K5 tuned 129 à 133 → 118 à
  120 ms (f64) ; K1 soa 22 à 24 → 14,7 ms (f64) ; Q1 sous Node 22 110 à 143 ms (tuned), 138 à 151 ms (naturel).
