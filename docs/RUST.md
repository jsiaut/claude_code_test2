# Remarque sur Rust (31 octobre) : vérifications, plan et résultats

Une remarque soutient que la 9e place de Rust n'est pas justifiée. Selon elle, la place tient surtout à un artefact de
mesure (la queue de latence de K8, D3), l'explication du README (« il perd sur les défauts ») contredit la
décomposition du score, et Rust serait entre la 4e et la 7e place, vers la 3e si la règle de la libc valait aussi
pour lui. Ce document vérifie chaque affirmation (section 2), fixe le plan avant toute mesure (section 3), puis donne
les résultats (section 4).

## 1. La remarque

1. **Le score** : Rust (69,4 [68,1–71,3]) est dans un groupe sans ordre établi avec D, Odin, Ada, Zig, C3 et Nim
   (69,5 à 72,6) ; il devance Zig, Nim, Ada et D dans 31 à 49 % des variantes ; ses rangs compatibles avec les paires
   établies vont du 2e au 12e ; « la règle des étages le met dans le premier étage, avec 15 autres langages ». 4e
   plafond (79,6 contre 85,3 pour C), 3e sur Emerald Rapids (4e sans K3). Contre C, il perd 10,7 points : 6,3 sur le
   contrôle, 2,3 sur le plafond, 2,1 sur les défauts, dont 1,9 sur D3 ; son code naturel (D1 = 19,5) bat celui de C
   (19,1), de C++ et de D. L'explication du README contredit cette décomposition.
2. **Les mesures** : (a) D3 est un artefact de la VM : même `malloc` que C, même médiane (54 contre 52 µs), mais
   p99,9 de 538 contre 218 µs ; les queues suivent le vol de temps (corrélation de rang 0,84 sur 22 processus) ; le
   processus 0 de Rust a le vol le plus élevé, et Rust n'a eu que 2 processus ; effet + 1,3 à + 1,9 point. (b) K9
   naturel : seule la forme `Vec<Vec<f64>>` indexée deux fois reste scalaire ; LLVM relit les en-têtes des lignes
   après chaque écriture, faute d'aliasing par type, et les bornes bloquent alors la vectorisation ; les autres formes
   (`&[f64]` par ligne, `Vec<[f64; M]>`, `Vec<f64>` plat) vectorisent. (c) Q1 optimisé : `m.count_ones() as i64`
   laisse LLVM vectoriser 4 des 6 popcounts sur Cascade Lake (203 instructions et 13 vidages contre 168 et 7 pour le
   C) ; `_popcnt32` rend le code du C (effet ≤ + 0,45). (d) À algorithme égal, Rust égale C (K4, K5, Q1, Q6, K7 sur sa
   machine). (e) K8 optimisé : une arène écrite comme en C gagne environ 10 % (+ 0,4, en sensibilité).
3. **Le pilier contrôle** : la règle v2 compte la libc pour C et C++ seulement (`sysconf`, `sched_setaffinity`,
   `mmap` : D3, D4 et F4 valent 1 pour C, 0 pour Rust), alors qu'un `extern "C"` appelle la même glibc en Rust
   stable ; seule, l'asymétrie coûte 3,0 points à Rust ; appliquée à tous les langages à FFI, Rust passe 7e ; avec D3
   et K9 corrigés, 3e (74,5). La règle « bibliothèque standard seule » pèse plus sur Rust ; des leviers ne sont pas
   comptés (`is_x86_feature_detected!` et `#[target_feature]`, réordonnancement des champs, non-aliasing par défaut).
4. **L'état de Rust** au 31 octobre (1.99.0 et 1.99.1, méthodes algébriques en 1.98, `cold_path`, AVX-512 depuis
   1.89, `std::simd` en nightly, SipHash 1-3, allocateurs).
5. **Propositions** : remesurer K8 naturel avec plus de processus en écartant les forts vols ; sensibilité K9 en
   `Vec<[f64; M]>` et cause corrigée ; `_popcnt32` pour Q1, arène sans `push` pour K8, `_MM_HINT_ET0` pour K7 ; règle
   de la libc symétrique, ou dans les limites ; paragraphe sur Rust réécrit.

## 2. Vérifications (faites avant le plan)

**Machine 11.** La VM a redémarré le 31 octobre vers 17 h 00 sur un hôte Emerald Rapids du même modèle que les
machines 3, 8, 9 et 10 (modèle 207, 4 vCPU ; 3,18 GHz effectifs, latence à 4 Mio 48 ns, DRAM 13,0 Go/s :
`results/hw/machine11/`). Chaîne du banc : rustc 1.99.1 (58cf8f9c3, 13 octobre 2026), LLVM 23.1.1. Preuves :
`results/rust_check/` (script `tools/rust_check/collect.sh`).

* **Le score (1)** : tous les chiffres sont exacts (`results/summary_v3.json`) : 69,37 [68,08–71,30] ; Rust devance
  Zig dans 31 % des variantes, Nim 43 %, Ada 48 %, D 49 % ; rangs compatibles avec les paires établies 2–12 ; plafond
  79,6 [76,8–82,6] contre 85,3 [82,4–88,5] pour C ; 3e sur la machine 3, 4e sans K3. La décomposition est exacte au
  dixième : contre C, − 10,73 = − 6,33 (contrôle) − 2,30 (plafond) − 2,09 (défauts, dont D3 − 1,89) ; contre D,
  − 3,27 = − 4,75 + 0,32 + 1,16 (D3 + 0,89) ; contre Zig, − 2,13 = − 4,79 + 3,53 − 0,87 (D3 − 0,64). D1 : Rust 0,195,
  C 0,191, C++ 0,182, D 0,170. **Une inexactitude** : le premier étage compte aujourd'hui 13 langages (12 autres que
  Rust) ; la liste de 16 langages vient de `docs/AUDIT2_RESPONSE.md` (section 7), datée du 29 octobre, avant les
  errata. **Le README se trompe** : il dit Rust « contrôle fin et sûr » qui « perd sur les défauts : vérifications de
  bornes, SipHash, SIMD portable en nightly » ; or c'est le contrôle qui lui coûte le plus, le SIMD portable compte dans
  le contrôle (C1), son code naturel est meilleur que celui de C, et sa perte sur les défauts vient de D3.
* **D3 (2a)** (`k8_steal.txt`) : les médianes sur toutes les répétitions sont exactes (Rust : p50 54,3 µs, p99,9
  537,8 µs, max 4 495 µs ; C : 51,5, 217,7, 1 365). Sur les 24 processus des 10 implémentations qui passent par `malloc`
  (C, C gcc, C++, Rust, Zig, Nim, Ada, Fortran, Odin, C3), la corrélation de rang entre le vol de temps et le p99,9
  vaut 0,81 (0,85 sans Odin ni C3 ; 0,45 sur les 62 processus, ramasse-miettes compris). Le processus 0 de Rust a le
  vol le plus élevé de ces 24 (0,84 % de la capacité des 4 vCPU ; p99,9 692 µs, contre 327 µs pour son processus 1),
  mais pas de tous (Go 1,43 %, Haskell 1,42 %). Rust n'a que 2 processus, comme beaucoup de cellules, à cause du
  redémarrage du 28 octobre ; la règle de vol (2 %) a été appliquée telle qu'écrite, et la passe complémentaire annulée
  visait la dispersion des temps, pas les queues. La réplication de la machine 3 (un processus par langage) donne à
  Rust une queue plus courte que celle de C (p99,9 142 contre 159 µs ; max 240 contre 420 µs). **Exact** : le D3 de
  Rust repose sur deux processus, dont le plus volé ; ce n'est pas son code.
* **K9 naturel (2b)** (`k9_forms.txt`) : la forme du banc (`Vec<Vec<f64>>`, double indexation) reste scalaire ; les
  trois autres formes vectorisent, vérifications actives. Mais la cause n'est pas les bornes : **sans aucune
  vérification** (`get_unchecked`), la boucle reste scalaire, déroulée par 3, et relit les pointeurs de lignes après
  chaque écriture. rustc ne transmet pas de métadonnées TBAA à LLVM (comme LDC pour D) : rien ne dit qu'une écriture
  de `f64` ne touche pas les en-têtes des lignes. **Exact sur le constat, inexact sur le rôle des bornes ; la cause
  écrite dans le README est fausse pour Rust.** Forme naturelle : `docs/NATURAL.md` range Rust avec les langages à
  tableaux imbriqués (C++, D, Nim, Go, Mojo, Java) ; pour D, `double[M][]` est resté une sensibilité.
* **Q1 (2c)** (`q1_asm.txt`) : même algorithme que la référence C ; seul le popcount diffère dans la forme
  (`__builtin_popcount` sur 32 bits en C, `u16::count_ones` en Rust). Code pour Cascade Lake (celui des données
  principales), boucle de 16 lignes : Rust 209 instructions, 15 écritures sur la pile, 2 `popcnt` et un popcount
  vectoriel émulé par `vpshufb` ; avec `_popcnt32`, 174, 12 et 6 `popcnt` ; C 169, 11 et 6. Sur l'hôte (qui a
  `vpopcnt`), l'écart s'inverse (Rust 159, C 147). Données principales : 38,0 contre 32,1 ms, 18,6 contre 13,2 à 4
  threads. **Exact** ; c'est une meilleure forme, pas un écart d'algorithme.
* **K8 optimisé (2e)** : même algorithme que C (arène indexée réutilisée) ; Rust l'écrit avec `Vec::push` dans une
  capacité réservée et des accès vérifiés. Meilleure forme possible, comme le dit la remarque. `docs/NATURAL.md` dit
  que la variante tuned de Rust évite les vérifications « par itérateurs ou `get_unchecked` » : faux pour K8 (texte à
  corriger).
* **K7 optimisé (proposition 3)** (`prefetch.txt`) : la référence C précharge en écriture
  (`__builtin_prefetch(p, 1, 0)`, `prefetchw`), comme C++, Zig, Odin, C3, Nim, D, Mojo et Ada ; Rust précharge en
  lecture (`_MM_HINT_T0`, `prefetcht0`). C# (`Sse.Prefetch0`) et Chapel (module Prefetch) préchargent en lecture,
  seule forme que je leur connaisse dans leur chaîne ; Fortran ne précharge pas. Sonde : `_MM_HINT_ET0` compile en Rust stable et émet
  `prefetchw` (cibles native et cascadelake). **Écart à la convention que suivent toutes les implémentations qui
  peuvent l'exprimer.**
* **Le contrôle (3)** : la règle v2 dit bien « la bibliothèque système de la plateforme pour C et C++ »
  (`analysis/capabilities_v2.py`) ; D3, D4 et F4 valent 0 pour Rust ; le second audit l'avait relevé (4.4.1 a) et j'avais
  répondu « je ne renote pas ». **Exact** ; c'est un choix de règle, pas un fait. Le crate `libc` est bien maintenu par
  le projet Rust (rust-lang/libc), mais il reste hors de la chaîne livrée. La grille n'a pas d'item pour la sélection
  du code selon le CPU ni pour le réordonnancement automatique des champs ; E5 vaut 1 pour Rust comme pour C : rien à
  corriger dans les cellules.
* **L'état de Rust (4)** : 1.99.0 le 1er octobre et 1.98.0 le 20 août (billets officiels) ; méthodes algébriques en
  1.98, que la matrice crédite déjà (C4 = 1) ; `std::hint::cold_path` stable depuis 1.95, déjà crédité (E3 = 1) ;
  `std::simd` en nightly (C1 = 0,5) ; SipHash 1-3 et sa limite sur les petites clés (documentation de `HashMap`) ;
  le billet de 1.99 parle de la stabilisation « à venir » des allocateurs (B2 = 0,5 reste juste en 1.99.1). **Exact.**

## 3. Plan (poussé avant les mesures)

### 3.1 Règle commune

`docs/FORTRAN.md`, 3.1 : « Est une erreur : un code qui ne fait pas ce qu'il annonce (Ada) ou qui s'écarte d'une
convention que les autres implémentations suivent (ici, des noyaux isolés de la boucle de mesure). Une meilleure forme
ou une meilleure disposition, même plus proche de ce que fait C, est une optimisation nouvelle. » Le préchargement en
lecture de K7 relève de la première phrase (écart à la convention de toutes les implémentations qui peuvent précharger
en écriture, Rust compris). Le popcount de Q1, l'arène de K8 et la forme `Vec<[f64; M]>` de K9 relèvent de la seconde.

### 3.2 Ce qui entre dans le classement publié

1. **Correction de K7 optimisé** : rapport apparié `rust_fix` / `rust_ref` (même hôte), reporté sur les données
   principales par la règle de `analysis/transfer_check.py` (pont par le C du même hôte au-delà de 25 % d'écart) ; la
   version par transfert seul est publiée à côté (« -T »).
2. **D3 remesuré pour toutes les implémentations.** Les queues de K8 des données principales reposent sur 2 ou 3
   processus par langage et suivent le vol de temps (section 2). Comme pour K5 en v2 (une mesure dont la dispersion
   entre processus était démontrée, remesurée pour toutes les implémentations sur la machine 3 et publiée), je
   remesure K8 naturel pour les 25 implémentations de la campagne, 7 processus chacune, et **les latences de ces
   mesures remplacent celles de la campagne dans D3, pour toutes les implémentations**. Même estimateur (médianes, sur
   toutes les répétitions, de p50, p99,9 et max), mêmes références (minimum des langages classés), même bootstrap. Les
   temps, y compris celui de K8 naturel, ne changent pas. La décision est prise avant de voir ces mesures, quel que
   soit leur effet sur Rust ou sur les autres.
3. **Le README** : paragraphe sur Rust réécrit (décomposition : contrôle et D3 ; code naturel meilleur que celui de C ;
   cause du stencil), cause du stencil naturel de Rust (aliasing, comme D), description du tableau ; dans les limites,
   l'asymétrie de la règle de la libc. `docs/NATURAL.md` : la phrase sur les vérifications de la variante tuned.
   `docs/AUDIT2_RESPONSE.md` : les étages de la section 7 sont datés.

### 3.3 Sensibilités (hors classement publié)

* **Avant** : le calcul publié avant la remarque, refait par le même code.
* **S-K9** : K9 naturel en `Vec<[f64; M9]>` (`rust_nat` / `rust_ref`), par la règle du pont et par transfert (S-K9-T),
  les deux annoncés d'avance (le pont s'est déjà trompé sur des clés liées à la mémoire, Chapel K7 et D K9).
* **S-Q1** : `_popcnt32` dans Q1 optimisé, tuned et `mt` (`rust_clpop` / `rust_cl`, compilés pour Cascade Lake, le
  code des données principales, exécutés sur l'hôte), par la règle du pont (témoin : binaire C compilé pour Cascade
  Lake) et par transfert (S-Q1-T).
* **S-K8** : arène écrite comme en C (`rust_k8` / `rust_ref`), règle du pont et transfert (S-K8-T).
* **S-libc-R** : D3, D4 et F4 de Rust à 1 (règle de la libc étendue à Rust seul). **S-libc-FFI** : la libc compte pour
  tout langage dont la chaîne livre un moyen d'appeler une fonction C sans écrire de C (Rust, Zig, Odin, C3, Nim, D,
  Ada, Fortran, Julia, Mojo, Chapel, C#, Java, Go par cgo, Haskell, Python par ctypes ; pas OCaml, JavaScript ni Lua) :
  D3, D4 et F4 au moins à 1.
* **S-tout** : S-K9, S-Q1, S-K8 et S-libc-R cumulés (par transfert : S-tout-T).
* **D3-ancien** : le classement publié avec les latences de la campagne (pour isoler l'effet de la remesure).
* **D3-strict** : D3 remesuré sans les processus dont le vol dépasse 0,5 % (information).

### 3.4 Mesures (machine 11)

`tools/measure_rust.py`, 7 processus par cellule en 7 passes, toutes les cellules de chaque passe dans un ordre tiré
au hasard (graine fixe), règle de vol du pilote. Paires Rust (`results/raw_rust/`, étiquette `rust`) :

| Implémentation | Cellules |
|---|---|
| `rust_ref` (source de la campagne, natif) | K7 tuned, K8 tuned, K9 naturel et tuned, Q1 tuned et `mt`, Q6 tuned, K4 sans branchement, K5 tuned, K1 aos |
| `rust_fix` (K7 : `_MM_HINT_ET0`) | K7 tuned ; témoins inchangés K9 tuned, Q6 tuned, K1 aos |
| `rust_nat` (K9 : `Vec<[f64; M9]>`) | K9 naturel ; témoin K9 tuned |
| `rust_k8` (K8 : arène comme en C) | K8 tuned ; témoin K8 naturel |
| `rust_cl`, `rust_clpop` (cascadelake, sans et avec `_popcnt32`) | Q1 tuned et `mt` |
| `c` (binaire de `bench/c`, compilé pour Cascade Lake) | les mêmes que `rust_ref` (témoin des ponts ; comparaison « à algorithme égal », pour information) |

Remesure de D3 (`results/raw_d3/`, étiquette `d3_m11`) : K8 naturel, les 25 implémentations de la campagne
(classées et annexes), échauffements de la campagne (3 pour les JIT, 1 sinon). Pendant la campagne, rien d'autre ne
tourne : ni compilation, ni sonde (incident de la remarque sur D).

### 3.5 Analyse

`analysis/rust_check.py` : rapports appariés (moyennes géométriques par processus, IC par bootstrap), report sur les
données principales, scénarios de la section 3.3 rejoués par `analysis/confrontation.py` (`scenario`) ; sorties
`results/rust_check.json` et `results/report_rust.md`. Le classement publié lit les latences de D3 dans
`results/raw_d3/` (`analysis/analyze_v2.py`) et le rapport de K7 dans `results/transfers.json` ; toutes les sorties
publiées sont recalculées (analyse v3, figures, scénarios de Zig et de Julia, confrontation).

## 4. Résultats

399 processus (57 cellules × 7 passes), le 31 octobre de 17 h 27 à 17 h 54 sur la machine 11 ; aucune somme de
contrôle fausse ; 9 processus des paires refaits pour vol de temps au-dessus de 2 %, aucun gardé au-dessus du seuil ;
aucun pour la remesure de D3 (vol médian 0,33 %, maximum 1,28 %). Rien d'autre ne tournait. **Écart au plan
(cellules)** : `rust_ref` n'a pas mesuré K8 naturel, si bien que le témoin de `rust_k8` est comparé au binaire Rust
de la remesure de D3 (même hôte, mêmes passes) ; c'est une information, sans effet sur les scénarios. Rapports et
scénarios : `results/report_rust.md`, `results/rust_check.json` ; données : `results/raw_rust/`, `results/raw_d3/`.

### 4.1 Mesures appariées (machine 11, même hôte)

| Clé | Forme | Rapport (IC 95 %) | Remarque |
|---|---|---|---|
| K7 tuned | `_MM_HINT_ET0` (`rust_fix` / `rust_ref`) | 1,082 (0,992–1,172) : 199,5 → 215,8 ms | — |
| 3 témoins (K9 tuned, Q6 tuned, K1 aos) | code inchangé | 1,029 ; 0,930 ; 0,955 | |
| K9 naturel | `Vec<[f64; M9]>` (`rust_nat` / `rust_ref`) | 0,553 (0,522–0,585) : 44,2 → 24,4 ms | 30–35 → 11–13 ms |
| K8 tuned | arène écrite comme en C (`rust_k8` / `rust_ref`) | 0,742 (0,691–0,811) : 260,0 → 193,0 ms | 283–302 → 251–293 ms |
| Q1 tuned / `mt` (code de Cascade Lake) | `_popcnt32` (`rust_clpop` / `rust_cl`) | 0,825 (0,714–0,958) / 0,879 (0,765–1,005) | « ≤ + 0,45 point » |

À algorithme égal, sur cet hôte (`rust_ref` / `c`) : Q1 1,00, Q6 1,02, K7 1,04, K8 tuned 1,05, K1 aos 1,07, K5 tuned
1,09 (0,88–1,37), K4 sans branchement 1,30 (0,98–1,77), K9 tuned 1,45 (1,18–1,71). La remarque a raison pour Q1, Q6,
K7 et K8 ; pas pour K9 tuned ici, et K4 reste incertain.

**Le préchargement en écriture n'accélère pas K7 sur cet hôte** : 8 % plus lent, mais l'intervalle contient 1 et les
témoins dont le code ne change pas varient de − 7 à + 3 % d'un binaire à l'autre (disposition du code). La correction
suit la convention ; son effet mesuré est nul ou légèrement négatif.

### 4.2 D3 remesuré (K8 naturel, 25 implémentations, 7 processus)

Les queues baissent pour presque tous les langages, et l'ordre change : sur la campagne principale, deux ou trois
processus par langage laissaient passer les queues dues au vol de temps. Rust : p99,9 538 → 132 µs, maximum 4 495 →
1 182 µs, D3 0,272 → 0,656 (C : 0,775 → 0,753). Hausses nettes aussi pour C# (0,352 → 0,674 ; p99,9 777 → 180 µs),
Zig (0,441 → 0,763), Odin (0,288 → 0,384) et Julia (0,095 → 0,169). Baisses pour C++ (0,763 → 0,640) et surtout C3
(0,516 → 0,330), dont la queue ne bouge pas (maximum 2,2 ms dans les deux campagnes) quand celle des autres raccourcit.
La latence la plus régulière est désormais celle de Zig (p99,9 = 3,0 fois la médiane), puis Nim et Mojo. Dans la
remesure, le vol corrèle encore avec les queues (corrélation de rang 0,49 pour le p99,9 sur les 70 processus des
langages qui passent par `malloc`), mais sept processus par langage en amortissent l'effet. Tableau complet :
`results/report_rust.md`.

### 4.3 Report sur les données principales et classement

K7 tuned : transfert 538,9 ms, pont 513,2 ms, écart 5 % : transfert retenu (× 1,082). Sensibilités : K9 naturel,
écart − 31 %, pont retenu (× 0,801 au lieu de 0,553 ; le C de ce stencil va 2,3 fois plus vite sur cet hôte que sur
Cascade Lake, le cas déjà vu pour D et Chapel) ; Q1 tuned transfert (× 0,825), Q1 `mt` pont (× 0,697, écart 26 %) ;
K8 tuned transfert (× 0,742).

| Scénario | Score de Rust | Contrôle C | Plafond E | Défaut D | Rang espéré | Place | Rang 90 % |
|---|---|---|---|---|---|---|---|
| Avant (publié avant la remarque, refait par le même code) | 69,4 | 73,6 | 79,6 | 47,2 | 7,57 | 9 | 4–11 |
| R-D3 : D3 remesuré, seul | 70,8 | 73,6 | 79,6 | 52,9 | 6,31 | 5 | 3–10 |
| R-K7 (= D3-ancien) : K7 corrigé, seul | 69,1 | 73,6 | 78,8 | 47,2 | 7,79 | 9 | 4–11 |
| **Publié** : D3 remesuré et K7 corrigé (Publié-T identique) | **70,5** | 73,6 | **78,8** | **52,9** | **6,55** | **6** | 3–10 |
| S-K9 / S-K9-T : K9 naturel en `Vec<[f64; M9]>` | 70,6 / 70,7 | 73,6 | 78,8 | 53,2 / 53,8 | 6,38 / 6,06 | 5 / 5 | 3–10 / 2–10 |
| S-Q1 / S-Q1-T : `_popcnt32` | 71,0 / 70,8 | 73,6 | 80,2 / 79,6 | 52,9 | 6,15 / 6,31 | 5 / 5 | 2–10 / 3–10 |
| S-K8 (= S-K8-T) : arène comme en C | 71,7 | 73,6 | 81,8 | 52,9 | 5,66 | 5 | 2–9 |
| S-libc-R : libc étendue à Rust | 73,5 | 82,1 | 78,8 | 52,9 | 4,49 | 4 | 1–8 |
| S-libc-FFI : libc étendue aux langages à FFI | 73,5 | 82,1 | 78,8 | 52,9 | 5,17 | 4 | 2–9 |
| S-tout / S-tout-T | 75,3 / 75,2 | 82,1 | 83,2 / 82,6 | 53,2 / 53,8 | 3,27 / 3,15 | 2 / 2 | 1–6 |
| D3-strict : processus à vol > 0,5 % écartés | 70,5 | 73,6 | 78,8 | 52,9 | 6,64 | 7 | 3–10 |

* **Publié** : Rust passe de 69,4 à 70,5 points et de la 9e à la 6e place (rang espéré 6,55), à égalité avec C3
  (6,47) et Nim (6,57) : il devance C3 dans 47 % des variantes et Nim dans 51 %. La remesure de D3 lui vaut 1,4 point
  et quatre places à elle seule ; la correction de K7 lui en reprend 0,3 et une place.
* **Les autres langages** : le nouvel ordre est C, C++, Odin, Zig (5e → 4e), C3 (4e → 5e), Rust, Nim (6e → 7e), D
  (8e), Ada (7e → 9e), Chapel, Fortran, Julia, Mojo, C# (54,8 → 56,0 points, toujours 14e). D3-strict donne le même
  ordre en tête, mais Nim 5e et Rust 7e : l'ordre de C3, Rust et Nim n'est pas établi.
* **Sensibilités** : chacune des trois formes de la remarque vaut une place à Rust (5e) ; la libc étendue à Rust, 3,0
  points et la 4e place ; étendue à tous les langages à FFI, la 4e aussi, Odin et C3 en profitant également ; tout
  cumulé, 75,3 points et la 2e place, entre C et C++.
* **La remarque estimait** 71,3 points et la 7e place avec D3 corrigé, 71,5 et la 6e avec K9, 72,3 et la 4e avec Q1
  et l'arène, la 7e avec la libc étendue à tous les langages à FFI, la 3e (74,5) avec D3, K9 et la libc ; mes calculs
  donnent 70,8 et la 5e (D3 seul), 70,5 et la 6e (publié, avec K7), la 4e avec la libc étendue à tous, 75,3 et la 2e
  avec tout.

### 4.4 Verdicts

* **(1) Le score et sa décomposition** : exacts, sauf le premier étage (13 langages, pas 16 : la liste de 16 datait du
  29 octobre). L'explication du README était fausse : Rust perd d'abord sur le contrôle, puis sur D3 ; son code naturel
  est meilleur que celui de C. Paragraphe réécrit.
* **(2a) D3** : exact. Rust ne reposait que sur deux processus, dont le plus volé ; remesuré avec sept processus, sa
  queue est proche de celle de C. La remesure, faite pour toutes les implémentations, change aussi d'autres places.
* **(2b) K9 naturel** : exact sur les formes, inexact sur les bornes : sans elles, la boucle reste scalaire ; c'est
  l'aliasing, comme pour D. Cause corrigée dans le README ; `Vec<[f64; M]>` reste une sensibilité (convention de
  `docs/NATURAL.md`), une place.
* **(2c) Q1** : exact (code de Cascade Lake) ; − 17,5 % sur Q1 tuned avec `_popcnt32`, une place en sensibilité.
* **(2d) À algorithme égal** : exact pour Q1, Q6, K7 et K8 ; pas pour K9 tuned sur cet hôte ; K4 incertain.
* **(2e) K8 optimisé** : l'arène écrite comme en C gagne 26 %, plus que les 10 % annoncés ; sensibilité, une place.
* **K7 (proposition 3)** : écart à la convention, corrigé dans le classement publié, sans gain mesuré.
* **(3) La règle de la libc** : exact ; c'est un choix de règle. Chiffré en sensibilité et inscrit dans les limites du
  README ; la règle publiée ne change pas. Les autres leviers cités sont hors de la grille.
* **(4) L'état de Rust** : exact.
* **Effet** : Rust passe de la 9e à la 6e place (70,5 points), dans la fourchette de la remarque (4e à 7e), mais pour
  une raison qui touche tous les langages : la queue de latence de K8 était mal mesurée pour beaucoup d'entre eux.
