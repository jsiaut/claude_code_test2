# Remarque sur JavaScript : des cases de 32 octets dans K7, trois cases de la grille, et ce qui tient à V8

L'auteur de l'étude m'a transmis le 3 novembre une remarque sur JavaScript. Elle juge la 19e place justifiée et
solide, le score (14,3) un peu sous-estimé, trois versions optimisées en dessous des techniques de la référence C,
trois cases de la grille fausses et plusieurs explications du dépôt inexactes, une bonne partie de ce que l'étude
attribue à JavaScript tenant à V8 et à sa version. Ce document vérifie chaque affirmation (section 2), fixe le plan
avant toute mesure (section 3), puis donne les résultats (section 4). Je n'ai consulté aucune page web : les faits
viennent des moteurs installés (Node.js 26.12.1, celui de l'étude, et Node.js 22.22.0 ; Bun 1.4.4), du code machine de
TurboFan, de sondes et des données publiées.

## 1. La remarque

1. **Le rang tient** : objets toujours en références ; nombres en f64, sans calcul en f32 ni entier 64 bits hors
   `BigInt` ; pas de SIMD dans le langage (SIMD.js retiré, le SIMD de WebAssembly non exposé à JavaScript) ; atomiques
   séquentiellement cohérentes seulement ; ramasse-miettes imposé. Pour rejoindre OCaml (23,8) sans toucher aux deux
   autres piliers, il faudrait un plafond de 35, 3,1 fois le plafond publié ; la lecture la plus généreuse donne
   environ 22. L'avance sur Python ne tient qu'à la vitesse (contrôle : Python 24,4, JavaScript 11,6), et l'étude
   rivale, qui ne compte pas la vitesse, classe JavaScript dernier.
2. **Trois versions optimisées** n'appliquent pas les techniques du C de référence (rapports mesurés par l'auteur sous
   V8 12.4, 13.6 et 15.3 et sous Bun) : Q6, masque par négation et sommes entières par blocs, × 0,53 à 0,60 ; K7,
   cases de 16 octets (clé, compteur, somme f64) au lieu de 32, × 0,48 à 0,70 sous V8 ; K9, vues de lignes et voisins
   gardés en registres, × 0,68 à 0,86. La compilation en cours de boucle (OSR) ne pénalise pas K7 (× 1,08, dans le
   bruit).
3. **La grille** : E1 doit valoir 1 (`--print-opt-code` affiche le code machine de TurboFan avec les binaires
   officiels de Node) ; le module expérimental `node:ffi` de Node 26.1, actif par défaut dans la 26.12.1 (lecture et
   écriture par pointeur, conversion d'un pointeur en `ArrayBuffer`) donne ½ en A4 et E6, comme `ctypes` pour Python ;
   « pas de mmap dans node » n'est plus exact, F4 restant à 0 par la règle « FFI = 0 », comme pour Rust. Discutables :
   WebAssembly à ½ en C1 et E2, comme `llvmcall` pour Julia ; des enregistrements faits à la main dans un `DataView` à
   ½ en A1, A2 et A7, comme `Storable` pour Haskell.
4. **Les explications** : les 416 octets par particule sont ceux de V8 sans compression de pointeurs (les binaires
   officiels de Node ne l'activent pas ; 272 octets sous Chrome 153, 170 sous Bun), alors que FINDINGS dit « avec » ;
   K3 mesure surtout V8, dont TurboFan appelle une fonction interne à chaque opération atomique (`call (AtomicsAdd)`),
   quand JavaScriptCore les compile en ligne : `rmw_padded` coûte 4,1 fois le C sous Node et 1,3 fois sous Bun, d'où
   un plafond de K3 de 6,2 contre 20,2 ; « V8 compile bien les tableaux typés » est généreux : pour les 8 éléments de
   K5, 16 vérifications de bornes et 7 de débordement, une adresse recalculée avant chaque accès, des accumulateurs
   sur la pile, et K5 naturel à 186 ms contre 91 pour du C scalaire.
5. **Deux anomalies propres à une version de V8** : les pauses de 59 à 133 ms de K8 naturel viennent du pretenuring
   par site d'allocation (l'arbre longue durée est construit par la même fonction que les arbres des requêtes, si bien
   que V8 alloue ensuite les nœuds jetables dans la vieille génération) ; avec un site distinct ou
   `--no-allocation-site-pretenuring`, la pire pause tombe de 62–95 à 0,3–3,4 ms et le temps de 35 %, environ 1 point.
   Q1 optimisé prend 340 ms sous Node 26 (machine 3) contre 125 à 145 ms sous V8 12.4, 13.6 et 15.3, et seul le
   compilateur expérimental Turbolev reproduit cette lenteur.
6. **Effet sur le score** : 14,7 à 15,1 avec les corrections de K6, K7 et K9 ; 15,8 à 16,1 avec les errata E1, A4,
   E6 ; 16,2 à 17,1 avec des sensibilités (K5 en f64, K1 SoA, K8 itératif) ; 21,0 à 21,9 avec les cases discutables et
   une règle « FFI sans C ». JavaScript reste 19e.
7. **Les évolutions récentes** ne changent rien : `Float16Array` pour le stockage seulement (ES2025) ; rien pour le
   matériel dans ES2026 ; `Atomics.pause` prévue pour 2027 ; Structs au stade 2 ; le SIMD passe par WebAssembly (K5 en
   Wasm SIMD 13,5 à 18,5 ms contre 115 à 160 en JavaScript et 3,2 en C), dont l'exclusion se défend, mais doit être
   écrite dans le README.

## 2. Vérifications (faites avant le plan)

**Machine 21.** La VM a redémarré le 3 novembre à 17 h 13 sur un hôte Emerald Rapids du même modèle que les machines 3
et 8 à 20 (modèle 207, 4 vCPU ; 2,95 à 3,19 GHz effectifs, latence à 4 Mio 55 ns, DRAM 12,7 à 13,3 Go/s :
`results/hw/machine21/`). Moteurs : Node.js 26.12.1 (V8 14.6.202.34, celui de l'étude), Node.js 22.22.0 (V8 12.4,
`/opt/node22`), Bun 1.4.4 ; les entrées correspondent à `env/msdata.sha256`. Sondes et code machine :
`results/js_check/`. Temps ci-dessous : médianes d'un processus.

* **Le rang (1)** : exact pour ce que je peux vérifier. Pas d'objet `SIMD` dans Node 26 ; `BigInt64Array` pour stocker
  des entiers 64 bits, l'arithmétique passant par `BigInt`. Décomposition : 14,27 = 0,35 × 11,6 + 0,40 × 11,4 + 0,25
  × 22,7 ; à contrôle et code par défaut égaux, rejoindre OCaml demande un plafond de 35,2, 3,1 fois 11,4. Contrôle :
  Python 24,4, JavaScript 11,6. L'étude rivale (`analysis/banc_data.py`) classe JavaScript dernier de ses 18 langages
  communs (28,9).
* **(2) Q6 tuned** : le code multiplie la contribution par le masque 0/1 et somme en f64 ; le C prend un ET avec `-m`
  et somme en entiers 64 bits ; Lua et OCaml multiplient aussi par le masque. Pas de convention entre langages
  scalaires, et JavaScript n'a pas d'entier 64 bits : des sommes entières par blocs sont une forme nouvelle,
  **sensibilité**. Les données le permettent : |pr · d| ≤ 500 000, si bien qu'un bloc de 4 096 lignes tient sur 32
  bits. Sonde : 96 à 98 → 58 à 62 ms (`mt` : 29 à 43 → 22 à 24), même somme.
* **(2) K7 tuned** : **exact, et c'est une erreur de mon implémentation.** Le code annonce ses 32 octets par case
  (quatre f64), mais toutes les implémentations qui disposent la mémoire en prennent 16, « 4 par ligne » : C, C++,
  Rust, Zig, Odin, C3, Nim, D, Ada, Chapel, Julia, Mojo, C#, Go, Haskell (mémoire brute) et Java, qui tasse clé et
  compteur dans un `long` « comme en C » ; seuls Python et Lua, qui ne disposent pas la mémoire, font autrement.
  JavaScript y arrive par deux vues typées sur le même `ArrayBuffer` (clé et compteur en `Uint32Array`, somme en
  `Float64Array`). Sonde : 1 517 → 861 ms, même somme. OSR : la construction de la table dans une fonction appelée à
  chaque répétition ne change rien de net (627 à 1 162 ms en ligne, 645 à 887 dans une fonction, un processus chacun).
* **Conséquence pour OCaml** : j'ai classé le K7 à deux mots d'OCaml en sensibilité (`docs/OCAML.md`, 2d) au motif que
  « les autres langages n'atteignent 16 octets par case que par des champs de 32 bits » et que tasser clé et compteur
  dans un entier serait une forme nouvelle. C'est faux : Java le fait dans un `long`, et OCaml peut le faire dans un
  entier de 63 bits. **Erreur de mon implémentation**, comme pour JavaScript : le rapport déjà mesuré en paires sur la
  machine 20 (× 0,875) passe des sensibilités au classement publié.
* **(2) K9 tuned** : le code prend des décalages de lignes dans un `Float64Array` plat, exactement comme Java
  (`k9Rows`), et comme les pointeurs de lignes du C ; des vues de lignes et des voisins gardés dans des variables sont
  une forme nouvelle, **sensibilité**. Sonde : 58 à 74 → 52 à 54 ms (`mt` : 22 à 24 → 24 à 29).
* **(3) E1** : **exact, erratum.** `--print-opt-code` affiche le code machine de TurboFan (`vmovss`, `vcvtss2sd`…)
  avec le binaire officiel de Node 26.12.1 comme de Node 22.22.0 : la note « selon la compilation de node » était
  fausse. 1, comme le désassemblage du JIT de C# ; Java garde ½, son désassembleur n'étant pas livré.
* **(3) node:ffi** : **exact, errata A4 et E6.** Le module est là et actif par défaut (avertissement « FFI is an
  experimental feature », option `--no-experimental-ffi`) ; il exporte `dlopen`, `dlsym`, `getRawPointer`,
  `getFloat64`/`setFloat64` et leurs pareils de 8 à 64 bits, `toArrayBuffer`. Sonde : `getRawPointer` d'un
  `ArrayBuffer` donne son adresse (ici congrue à 32 modulo 64 : une sur-allocation l'aligne, comme `ctypes.addressof`
  en Python, A4 ½) ; `getFloat64` lit sans vérification, même au-delà d'une vue (E6 ½, comme les pointeurs `ctypes`) ;
  `toArrayBuffer` enveloppe de la mémoire brute. F4 reste à 0 (mmap seulement par un appel à la libc : FFI), note
  corrigée ; B5 reste à ½, note complétée.
* **(3) Cases discutables** : **gardées, sensibilité.** `llvmcall` met de l'IR LLVM dans une fonction Julia, compilé
  avec elle ; WebAssembly est un autre langage, avec sa propre mémoire, appelé à travers une frontière, et son SIMD
  n'est pas exposé à JavaScript (C1, E2). `Storable` donne à un type sa taille, son alignement et ses champs, et des
  tableaux de tels enregistrements se lisent et s'écrivent par élément (`Foreign.Marshal.Array`) ; `DataView` ne lit
  ou n'écrit qu'un scalaire à un décalage d'octets, sans type d'enregistrement (A1, A2, A7). La règle « FFI sans C »
  changerait la règle pour tous les langages : hors du champ de cette remarque.
* **(4) 416 octets** : **exact, erreur de mon texte.** Le binaire officiel de Node est compilé sans compression de
  pointeurs (`process.config.variables.v8_enable_pointer_compression` = 0) ; 416 = 24 (en-tête : carte, propriétés,
  éléments) + 16 × 8 (champs) + 16 × 16 (un `HeapNumber` par flottant : carte et valeur) + 8 (case du tableau). Avec
  la compression : 12 + 64 + 16 × 12 + 4 = 272, le chiffre que la remarque donne pour Chrome (non mesuré ici).
* **(4) K3** : **exact.** Dans le code de TurboFan, sous Node 26 comme sous Node 22, `Atomics.add`, `Atomics.load` et
  `Atomics.store` sont des appels (`AtomicsAdd`, `AtomicsLoad`, `AtomicsStore`). Données publiées : `rmw_padded` 937
  ms contre 227 en C (4,1 fois) et 288 sous Bun (1,3 fois) ; plafond de K3 : 6,2 % de la référence sous Node, 20,2 %
  sous Bun. La compilation en ligne par JavaScriptCore n'est pas vérifiable ici (pas de sources), mais les temps de
  Bun la confirment. Explication à ajouter, sans effet sur le score : l'étude mesure Node.
* **(4) K5** : **exact.** Code de TurboFan de `k5Tuned` sous Node 26 : par tour de 8 éléments, 16 vérifications de
  bornes (`cmp`, `jae`), 7 vérifications de débordement des indices plus celle de l'incrément, l'adresse de chaque
  tableau typé recalculée (`lea`) avant chaque chargement, et les 8 accumulateurs rangés sur la pile et relus. Données
  publiées (machine 3) : K5 naturel 152 ms contre 79 pour le C scalaire de GCC (1,9 fois). La phrase du README est à
  corriger.
* **(5) K8 naturel** : **exact.** Sonde (Node 26, trois répétitions) : 1,10 à 1,15 s, pire pause 71 à 88 ms ; avec
  `--no-allocation-site-pretenuring`, 0,70 à 0,76 s et 1,0 à 1,2 ms ; avec un site d'allocation distinct pour l'arbre
  longue durée, 0,67 à 0,74 s et 0,8 à 9,1 ms. Pas une erreur : les autres implémentations construisent aussi l'arbre
  longue durée par la fonction des requêtes (OCaml, `t_build`), c'est le code naturel, et l'heuristique de V8 fait
  partie de ce que mesure le code par défaut : **sensibilité** (site distinct), sur le temps et les latences.
* **(5) Q1** : **exact sur la lenteur, inexact sur sa cause.** Sonde sur cet hôte : Q1 tuned 258 à 263 ms sous Node
  26, 114 à 133 ms sous Node 22 (naturel : 247 à 310 contre 117 à 144). Mais Turbolev est désactivé par défaut dans
  Node 26 (`--turbolev` : non), et l'activer accélère Q1 (177 à 179 ms) ; `--no-maglev` ne change rien. La lenteur
  vient du chemin par défaut de V8 14.6. L'étude mesure la version officielle actuelle, Node 26 : rien à corriger ; Q1
  sous Node 22 est mesuré en information.
* **(7) Évolutions** : `Float16Array` et `Math.f16round` sont dans Node 26 (stockage, arrondi ; le calcul reste en
  f64) ; `Atomics.pause` aussi, déjà comptée en D5 (½, sonde) : la norme la prévoit pour 2027, V8 la livre. Structs et
  Records & Tuples : invérifiables ici, sans effet. WebAssembly n'est pas JavaScript : exclu, ce que le README dira ;
  K5 en Wasm SIMD n'est pas mesuré.

## 3. Plan (poussé avant les mesures)

### 3.1 Règle commune et application

`docs/FORTRAN.md`, 3.1. Erreurs : K7 tuned de JavaScript (32 octets par case contre 16 par convention), et, par la
même règle, K7 tuned d'OCaml (24 octets, classé à tort en sensibilité) ; errata E1, A4, E6 ; texte de FINDINGS (416
octets) et du README. Sensibilités : Q6 (masque par négation, sommes entières par blocs), K9 (vues de lignes, voisins
dans des variables), K8 naturel (site d'allocation distinct), K8 tuned itératif, K5 tuned en f64, K1 soa en f64, cases
C1, E2, A1, A2, A7.

### 3.2 Ce qui entre dans le classement publié

* **J-E** : K7 tuned × r(`js_fix` / `js_ref`), **par transfert** (règle de la remarque sur Haskell, `docs/HASKELL.md`,
  3.2 ; le pont par le C reste calculé en information). Les autres clés de JavaScript ne changent pas.
* **Matrice** : E1 = 1, A4 = E6 = ½ (`analysis/capabilities.py`) ; notes de B5, C1 et F4 corrigées.
* **OCaml** : K7 tuned × r(`ocaml_exp` `tuned_p` / `ocaml_fix`), déjà mesuré sur la machine 20
  (`analysis/ocaml_check.py` : O-E ; le scénario O-E-311 garde l'O-E d'avant), reporté aussi sur la réplication.
* **Réplication (machine 3)** : la même clé × le même rapport (transfert), par `results/js_check.json`
  (« replication_ratios »), lu par `m3_ratios`.
* **Texte** : README (tableau, paragraphe de JavaScript : K3 et les appels de V8, le code de K5, Q1 sous Node 26,
  l'exclusion de WebAssembly ; errata, limites), FINDINGS (416 octets), CAPABILITIES (régénéré).

### 3.3 Copies (`tools/js_check/make_copies.py`)

* `js_ref` : copie exacte de `bench/js_k9h` (le code publié, harnais commun de K9).
* `js_fix` : K7 tuned en cases de 16 octets (deux vues typées sur un `ArrayBuffer`).
* `js_exp` : `js_fix` et des variantes nouvelles : K6 `tuned_m` et `mt_m` (Q6), K9 `tuned_v` et `mt_v`, K8 `natural_s`
  (arbre longue durée par une fonction à part) et `tuned_it` (arène itérative, comme `c_k8it`), K5 `tuned_f64`
  (données copiées en f64 hors chrono), K1 `soa_f64` (colonnes en f64).
* `js_n22` : le source de `js_ref` exécuté par Node.js 22.22.0 (information).
* Validation (`tools/js_check/validate.py`) : sommes de contrôle des 24 cellules JavaScript de la campagne, toutes
  justes.

### 3.4 Mesures (`tools/measure_js.py`, machine 21)

25 cellules en 7 passes (175 processus) ; dans chaque passe, toutes les cellules dans un ordre tiré au hasard (graine
20261803) : `js_ref` sur K7 tuned, les clés de base des sensibilités et Q1 tuned et naturel ; `js_fix` sur K7 tuned et
deux clés dont le code ne change pas (K5 tuned, K9 tuned : contrôle) ; `js_exp` sur ses 8 variantes ; `js_n22` sur Q1
tuned et naturel ; `c` (binaire de la campagne) sur K7 tuned (pont, information). Répétitions de `results/calib.json`
(variante d'origine pour les variantes nouvelles) ; échauffements de la campagne (2 pour K5, 1 sinon) ; règle de vol
du pilote. Rien d'autre ne tourne. Sortie : `results/raw_js/`.

### 3.5 Scénarios (`analysis/js_check.py`, analyse globale de la v3 rejouée, mêmes tirages)

| Scénario | Contenu |
|---|---|
| Avant | classement publié d'avant (E1 = ½, A4 = E6 = 0) ; doit reproduire `results/ocaml_check.json` (O-E, avec le K7 d'OCaml) à l'identique |
| J-code | K7 tuned × r(`js_fix` / `js_ref`), grille d'avant |
| J-M | errata E1, A4, E6 seuls |
| **J-E (publié)** | les deux |
| J-E-P | J-E, K7 reporté par le pont par le C (règle de `analysis/transfer_check.py`, règle de sens ; information) |
| S-Q6m | J-E ; Q6 tuned et `mt` × r(`tuned_m`, `mt_m` / `js_ref`) |
| S-K9v | J-E ; K9 tuned et `mt` × r(`tuned_v`, `mt_v` / `js_ref`) |
| S-K8s | J-E ; K8 naturel × r(`natural_s` / `js_ref`), ses latences × les rapports des latences |
| S-K8it | J-E ; K8 tuned × r(`tuned_it` / `js_ref`) |
| S-K5d | J-E ; K5 tuned × r(`tuned_f64` / `js_ref`) |
| S-K1d | J-E ; K1 soa × r(`soa_f64` / `js_ref`) |
| S-mesures | toutes les formes |
| S-cases | J-E ; C1, E2, A1, A2, A7 = ½ |
| S-tout | S-mesures et S-cases |

Rapports : moyenne géométrique des médianes de processus, intervalle par bootstrap ; latences : médiane de toutes les
répétitions, colonne par colonne ; sensibilités en min(1, r) par rapport à J-E. Information : K5 tuned et K9 tuned
sous `js_fix` / `js_ref` (contrôle), Q1 sous `js_n22` / `js_ref`. Sorties : `results/js_check.json`,
`results/report_js.md`, `results/transfers.json` (JavaScript) ; avant elles, `analysis/ocaml_check.py` rejoué (K7
d'OCaml) ; puis régénération des sorties publiées (la réplication comprise) et de l'état actuel.

### 3.6 Ce que je ne fais pas

* Pas de mesure sur Cascade Lake ; ni Chrome, ni Node 24, ni WebAssembly ; Node 22 seulement en information (la règle
  mesure la version officielle actuelle).
* Pas de règle « FFI sans C » (elle vaudrait pour tous les langages) ; pas de K10 (hors score) ; pas de remesure de
  l'empreinte.
