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

## 4. Résultats (après les mesures)

Mesures du 3 novembre, de 17:45:01 à 17:50:43, sur la machine 21 : 175 processus (25 cellules, 7 processus chacune),
aucune somme de contrôle fausse, aucun refait pour vol de temps (vol médian 0,68 %). Aucun écart au plan. Le scénario
Avant reproduit le classement publié d'avant (O-E, avec le K7 d'OCaml) à l'identique. Rapports :
`results/report_js.md` ; temps : moyenne géométrique des médianes de processus, intervalle à 95 % par bootstrap.

### 4.1 La correction de K7 (`js_fix` / `js_ref`, même hôte)

| Clé | Banc d'origine (ms) | Corrigé (ms) | Rapport [IC 95 %] | C, même hôte (ms) | Publié d'avant → reporté (ms) |
|---|---|---|---|---|---|
| **K7 tuned** | 1 417,4 | 818,0 | **0,577** [0,541–0,618] | 184,4 | 2 715,8 → 1 567,3 |
| K5 tuned (contrôle) | 137,5 | 133,2 | 0,969 [0,916–1,015] | — | non reporté |
| K9 tuned (contrôle) | 58,9 | 57,2 | 0,971 [0,925–1,019] | — | non reporté |

Avec des cases de 16 octets, K7 tuned va 1,7 fois plus vite (× 0,48 à 0,70 selon la remarque, sous d'autres versions
de V8) ; il reste 4,4 fois C sur cet hôte, contre 7,7 fois avant. Les deux clés témoins, au code identique dans les
deux copies, restent dans le bruit. Pont par le C (information) : 2 026,6 ms, à 22,7 % du transfert, sous le seuil de
25 % : la règle garde le transfert, et J-E-P se confond avec J-E. Le K7 du C de clang va 2,5 fois plus vite sur cet
hôte que sur Cascade Lake (184 contre 457 ms) : le pont, s'il s'appliquait, importerait cet écart d'hôte.

### 4.2 Sensibilités (forme nouvelle / `js_ref`, même hôte)

| Forme (scénario) | Clé | `js_ref` (ms) | Forme nouvelle (ms) | Rapport [IC 95 %] | Remarque |
|---|---|---|---|---|---|
| Masque par négation, sommes par blocs (S-Q6m) | Q6 tuned | 83,5 | 49,8 | 0,596 [0,560–0,633] | × 0,53 à 0,60 |
| | Q6 `mt` | 35,9 | 23,5 | 0,654 [0,578–0,742] | |
| Vues de lignes, voisins dans des variables (S-K9v) | K9 tuned | 58,9 | 52,1 | 0,883 [0,828–0,935] | × 0,68 à 0,86 |
| | K9 `mt` | 29,1 | 24,1 | 0,828 [0,684–0,987] | |
| Site d'allocation distinct (S-K8s) | K8 naturel | 1 085,0 | 669,8 | 0,617 [0,558–0,714] | − 35 % |
| Arène itérative (S-K8it) | K8 tuned | 424,6 | 308,7 | 0,727 [0,701–0,751] | |
| Données en f64 (S-K5d) | K5 tuned | 137,5 | 121,4 | 0,883 [0,839–0,920] | |
| Colonnes en f64 (S-K1d) | K1 soa | 14,9 | 15,6 | 1,046 [0,981–1,132] | |

Latences de K8 naturel (médianes de toutes les répétitions), arbre longue durée par une fonction à part : p50 40 → 36
µs (× 0,890), p90 63 → 47 µs (× 0,749), p99 200 → 99 µs (× 0,496), p99,9 721 → 352 µs (× 0,488), maximum 81,6 → 1,1 ms
(× 0,014 [0,01–0,02]). La remarque l'avait vu juste : le pretenuring de V8 fait les pauses longues de K8 naturel. K1
soa en f64 ne gagne rien (compté 1) : l'écart de la validation (22 à 24 ms contre 14,7) venait d'un premier processus
à froid. Les autres formes gagnent dans le sens annoncé, Q6 autant que la remarque le disait, K9 un peu moins.

### 4.3 Information : Node 22 et Node 26 (même source, même hôte)

Q1 tuned : 269,9 ms sous Node 26, 111,7 ms sous Node 22 (× 0,414 [0,406–0,422]) ; Q1 naturel : 263,5 et 131,2 ms
(× 0,498 [0,481–0,522]). Node 26 est 2,0 à 2,4 fois plus lent que Node 22 sur Q1, dans les deux variantes, et Turbolev
n'y est pour rien (section 2). La règle mesure la version officielle actuelle : les temps publiés de Q1 restent ceux
de Node 26.

### 4.4 Classement (analyse globale de la v3 rejouée, 20 000 variantes)

| Scénario | Score | Contrôle | Plafond | Défaut | Rang espéré | Place | Rang 90 % | OCaml devant | Devant Python |
|---|---|---|---|---|---|---|---|---|---|
| Avant (publié d'avant) | 14,27 | 11,6 | 11,4 | 22,7 | 19,07 | 19 | 19–20 | 99,9 % | 92,8 % |
| J-code (K7) | 14,59 | 11,6 | 12,2 | 22,7 | 19,07 | 19 | 19–20 | 99,9 % | 93,2 % |
| J-M (errata E1, A4, E6) | 15,31 | 14,6 | 11,4 | 22,7 | 19,04 | 19 | 19–19 | 99,6 % | 95,2 % |
| **J-E (publié)** | **15,64** | 14,6 | 12,2 | 22,7 | 19,04 | 19 | 19–19 | 99,5 % | 95,5 % |
| J-E-P (pont, information) | 15,64 | 14,6 | 12,2 | 22,7 | 19,04 | 19 | 19–19 | 99,5 % | 95,5 % |
| S-Q6m | 15,78 | 14,6 | 12,5 | 22,7 | 19,04 | 19 | 19–19 | 99,5 % | 95,5 % |
| S-K9v | 15,73 | 14,6 | 12,4 | 22,7 | 19,04 | 19 | 19–19 | 99,5 % | 95,5 % |
| S-K8s | 17,30 | 14,6 | 12,2 | 29,3 | 19,00 | 19 | 19–19 | 96,4 % | 96,4 % |
| S-K8it | 15,84 | 14,6 | 12,7 | 22,7 | 19,04 | 19 | 19–19 | 99,5 % | 95,6 % |
| S-K5d | 15,71 | 14,6 | 12,4 | 22,7 | 19,04 | 19 | 19–19 | 99,5 % | 95,5 % |
| S-K1d | 15,64 | 14,6 | 12,2 | 22,7 | 19,04 | 19 | 19–19 | 99,5 % | 95,5 % |
| S-mesures | 17,84 | 14,6 | 13,5 | 29,3 | 18,99 | 19 | 19–19 | 95,8 % | 96,7 % |
| S-cases (C1, E2, A1, A2, A7 = ½) | 18,40 | 22,5 | 12,2 | 22,7 | 18,96 | 19 | 18–19 | 94,6 % | 99,0 % |
| S-tout | 20,60 | 22,5 | 13,5 | 29,3 | 18,84 | 19 | 18–19 | 83,5 % | 99,4 % |

« OCaml devant » : part des variantes où OCaml devance JavaScript ; « Devant Python » : part des variantes où
JavaScript devance Python. Au classement publié (J-E), JavaScript gagne 1,37 point (14,27 → 15,64) et reste 19e, rang
plausible 19 : la correction de K7 lui rend 0,32 point (plafond 11,4 → 12,2 ; K7 : 0,168 → 0,291 de la référence), les
errata 1,04 (contrôle 11,6 → 14,6). Les scores des autres langages ne changent pas ; leurs rangs espérés bougent de
0,03 au plus (Python, que JavaScript devance désormais dans 95,5 % des variantes, contre 92,8 %). De toutes les
formes, celle qui pèse le plus est un détour du pretenuring de V8 (S-K8s, + 1,66, code par défaut 22,7 → 29,3) ; avec
toutes les formes et les cases discutables, JavaScript atteint 20,6 points et devance OCaml dans 16,5 % des variantes,
sans changer de place. Dans les étages de la v3 (ordre établi dans 95 % des tirages, sans inversion sur la machine 3),
JavaScript forme désormais un étage à lui seul, entre OCaml et le groupe de Python et Lua (`results/report_v3.md`) ;
depuis la remarque sur Python (5 novembre), qui a fait passer la part des variantes où JavaScript devance Python de
95,5 à 91,1 %, les trois forment un seul étage (`docs/PYTHON.md`, 4.6).

### 4.5 Réplication (machine 3)

Données de JavaScript de la machine 3 multipliées par le rapport de K7 tuned (transfert, même modèle de processeur),
avec les errata : score 12,9 → 14,2, toujours 19e ; plafond 8,0 → 8,5. OCaml, avec son K7 : 21,6 → 21,7, toujours 18e.
L'ordre de la réplication ne change pas (Spearman 0,93 sur les 21 langages, comme avant).

### 4.6 Bilan

* **La remarque est juste sur l'essentiel.** Le K7 optimisé rangeait ses cases sur 32 octets quand la convention en
  prend 16 (erreur de mon implémentation) ; E1, A4 et E6 étaient faux (errata) ; les 416 octets sont ceux de V8 sans
  compression de pointeurs (erreur de mon texte) ; K3 paie un appel de fonction interne par opération atomique ; le
  code de K5 garde ses vérifications et ses accumulateurs sur la pile ; le pretenuring de V8 fait les pauses de K8
  naturel, et son détour vaut même plus que l'estimation de la remarque (1,7 point contre environ 1).
* **Une erreur de plus, chez OCaml** : la règle qui fait de K7 une erreur pour JavaScript en fait une pour OCaml, dont
  j'avais mis la forme à deux mots en sensibilité sur un motif faux (`docs/OCAML.md`, 4.8) : + 0,12 point, toujours
  18e.
* **Ce que je retiens autrement** : Q6 et K9 n'appliquent pas une convention que les autres suivraient (Lua et OCaml
  multiplient aussi par le masque ; Java écrit K9 comme JavaScript) : sensibilités ; K1 SoA ne gagne rien ; les cases
  C1, E2, A1, A2 et A7 restent discutables (sensibilité) ; la règle « FFI sans C » vaudrait pour tous les langages et
  n'est pas appliquée.
* **Une cause inexacte** : la lenteur de Q1 sous Node 26 est réelle (2 fois Node 22), mais Turbolev, désactivé par
  défaut dans Node 26, n'en est pas la cause : l'activer l'accélère.
* **Les estimations de la remarque**, avec ma classification, sont proches des miennes : 14,7 à 15,1 avec K6, K7 et K9
  (ici 14,59 avec K7 seul, environ 14,8 avec les formes de Q6 et de K9) ; 15,8 à 16,1 avec les errata (15,64 publié,
  environ 15,9 avec ces formes) ; 21,0 à 21,9 avec les cases discutables et la règle « FFI sans C » (20,60 sans cette
  règle). JavaScript reste 19e dans tous les scénarios.
