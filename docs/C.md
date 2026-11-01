# Remarque sur C (1er novembre, soir) : vérifications, plan et résultats

Les sections 1 à 3 ont été poussées avant les mesures ; la section 4 vient après.

## 1. La remarque

En résumé (texte reçu le 1er novembre au soir) :

* **Verdict** : la place de C dans le groupe de tête est justifiée et solidement soutenue par les données ; la 1re
  place seule ne l'est pas. À compilateur égal, C et C++ sont à égalité, et l'avance de C tient surtout à des choix de
  protocole, pas au langage : l'auteur les classerait ex aequo. À l'inverse, le plafond de C est sous-estimé sur K8.
  L'auteur a lu la ligne de C de la grille, `bench/c/ms.c`, la remarque sur C++ et les audits ; il n'a pas exécuté le
  code du dépôt, mais ses propres sondes, écrites d'après `SPEC.md`, sur une VM Emerald Rapids (Clang 23.1.5, GCC 15.2
  et un instantané de GCC 16 de mars 2026), et il a recalculé les scores avec la formule publiée.
* **Ce qui est solide** : l'ensemble de rangs simultané de C est {1, 2}, son rang est entre 1 et 5 dans 90 % des
  variantes ; compilé par GCC, C fait 79,5 points (1er) et 75,5 sur la machine 3 (1er aussi) ; réécrit en C ISO pur,
  il garde 94,5 % de son plafond et reste 1er ; les faits de sa grille sont justes (`__GCC_DESTRUCTIVE_SIZE` vaut 64 en
  mode C, absent de Clang 18 ; `#pragma clang fp reassociate` agit localement), sauf deux incohérences mineures en
  règle v1 : A3 vaut 1 alors que `packed` est une extension, E4 vaut ½ alors que `_mm_prefetch` est dans le même
  `immintrin.h` qui vaut 1 à C pour C2 (et 1 à Rust pour E4). Effet net : moins de 0,5 point.
* **Ce qui fragilise la 1re place** :
  1. L'écart C/C++ est un écart de compilateurs (K4 : sur quatre formes scalaires, Clang 23 est 2,6 à 4,2 fois plus
     rapide que GCC 16 ; GCC 16 vectorise maintenant la forme `if`, 6,7 ms contre 16,9 avec GCC 15) ; à compilateur
     égal, le reste tient au harnais de K9, au bruit et à l'arène de K8 ; C++ compile chaque noyau C, donc « C devant
     C++ » n'est pas une propriété du langage.
  2. Le harnais de K9 avantage C, qui alloue ses grilles une fois quand 12 des 16 implémentations relues les
     réallouent. Reproduit : avec des pages neuves à chaque répétition, le stencil passe de 11,9 à 16,4 ms en un fil
     (× 1,38) et de 6,7 à 11,7 ms à deux fils (× 1,74), toutes les pages étant touchées avant le chrono. Avec la pénalité
     de l'Emerald Rapids de la remarque sur C++, C perd 2,7 points et passe 3e en rang espéré ; avec une pénalité de
     type Cascade Lake (× 1,48 sur le multi-thread seulement), − 0,8 point. C'est le seul biais mesuré en faveur de C ;
     le README le décrit sans le corriger.
  3. Le pilier contrôle dépend de la règle : C vaut 91,7 en règle v2, 77,8 en v1 (5e de la grille, derrière Zig, C++,
     Odin et D) et 64,0 en règle « ISO seule », où il tombe 5e du classement et Odin passe 1er. Au 1er novembre 2026, le
     C ISO n'a ni types SIMD, ni préchargement, ni `likely`, ni constante de ligne de cache ; la proposition WG14 N3837
     (types vectoriels repris de l'extension de GCC) a reçu une direction favorable (14-1-5) en août 2026 mais ne vise
     pas C2y, dont le gel est prévu en avril 2027. Le « C » classé 1er est donc GNU C / Clang + glibc + OpenMP +
     intrinsèques d'Intel : défendable, mais il faudrait le dire dans le titre.
  4. C joue à domicile : la référence C a été mise au point avec des mesures avant le plan, et C est le seul des 13
     premiers sans remarque de connaisseur, alors que la relecture a presque toujours fait gagner les autres.
  5. La machine compte : sur Emerald Rapids, C par clang est 2e (69,4 contre 71,2 pour C++) ; K3 y dépend d'un facteur
     7 du placement du code.
* **Ce qui sous-estime C** : K8 tuned (0,41, le noyau le plus faible de C). L'arène du banc est construite par une
  récursion dont l'état (deux compteurs, `int32_t*` et `int64_t*`) passe par la mémoire : ces pointeurs peuvent
  désigner des champs de l'arène, ce qui oblige à relire et réécrire l'état à chaque nœud. Mesures de l'auteur (16 384
  requêtes, même algorithme, même somme de contrôle) : forme du banc 120–155 ms (GCC 16) et 276–287 ms (Clang 23) ;
  récursion à un seul état passé par valeur 62–65 et 144–151 ms ; itérative à piles explicites 116–126 et 102–104 ms.
  Corrigé de l'écart de sa VM, l'itératif sous clang ferait environ 89 ms (frontière de K8 : Ada, 87,6 ms), le par
  valeur sous GCC environ 55 ms : + 3 à + 4 points pour C seul ; une meilleure forme au sens des règles, dont C++, Rust
  ou Zig profiteraient aussi.
* **Tableau de l'auteur (estimations ponctuelles)** : publié C 80,0, C++ 76,6, Odin 73,5 ; C++ avec le K4 de clang++
  80,0 / 79,6 ; et C réallouant ses grilles de K9, 79,2 / 79,6 (C++ en tête) ; et arène itérative pour C, 83,2 / 79,2 ;
  contrôle en règle v1, 75,1 / 73,2 / 72,5 ; contrôle « ISO seul », C 5e, C++ 4e, Odin 1er ; machine 3, 69,4 / 71,2 /
  62,2 (C par gcc 75,5). « La tête change à chaque choix d'implémentation ou de protocole : c'est le signe d'une
  égalité. »
* **Recommandations** : présenter {C, C++} ex aequo en tête, Odin et Zig (version de développement) à portée ;
  harmoniser le harnais de K9 pour toutes les implémentations ; faire relire C, et autoriser partout les formes
  itératives ou par valeur pour K8 (la spécification n'impose pas la récursion) ; écrire dans le titre que le contrôle
  de C est celui de GNU C / Clang + glibc, et afficher les rangs en règle v1 et « ISO seule ».

## 2. Vérifications (faites avant le plan)

Machine 16 : la VM a redémarré vers 17 h 58 sur un hôte du même modèle (Emerald Rapids, modèle 207, 4 vCPU),
caractérisé avant toute mesure (`results/hw/machine16/` : 2,73 à 2,81 GHz effectifs, latence à 4 Mio 36,7 ns, DRAM
15,8 Go/s). Chaînes : clang 23.1.5 (celle du banc C), gcc 16.2.0 (celle de l'annexe c_gcc) ; GCC 15 n'est pas installé.
Preuves : `tools/c_check/collect.py` et `tools/c_check/data_facts.py` → `results/c_check/*.txt` (sondes dans
`tools/c_check/probes/`). Je n'ai consulté aucune page web : ce qui ne se vérifie qu'en ligne (WG14 N3837 et son vote,
calendrier de C2y) reste non vérifié.

* **Place de C** (`data_facts.txt`) : **exact**. Ensemble de rangs simultané {1, 2}, rang entre 1 et 5 dans 90 % des
  variantes, 1er dans 57 % des variantes ; C est dans le premier groupe, avec les douze autres premiers.
* **C par gcc** : **exact**. 79,45 points ; 75,52 sur la machine 3, où C++ est 1er des langages classés (71,19) et C
  2e (69,43) : l'annexe y serait 1re.
* **C ISO pur** (`docs/CONFRONTATION.md`, test 2) : **exact**. 94,5 % du plafond, C 1er dans le scénario C.
* **Grille de C** (`iso.txt`, `reassoc.txt`) : faits **exacts**. `__GCC_DESTRUCTIVE_SIZE` vaut 64 en mode C sous
  clang 23 comme sous gcc 16 (Clang 18 non installé) ; `#pragma clang fp reassociate(on)` agit localement (la somme
  sous le pragma est vectorisée, 11 additions vectorielles ; la même somme sans pragma reste scalaire, 9 `vaddss`).
  * **A3** : **incohérence réelle, erratum**. A3 (« disposition au bit près : packed, champs de bits ») vaut 1 à C et
    à C++ en règle v1, alors que les champs de bits sont standard (disposition propre à l'implémentation) et `packed`
    une extension (attribut) ; Rust, dans la situation symétrique (`repr(packed)` standard, pas de champs de bits),
    vaut ½. La règle v1 donne ½ à ce qui n'est que partiellement standard : **A3 = ½ en v1 pour C et C++** ; en règle
    v2 (extensions documentées comprises), 1, inchangé.
  * **E4 et C2** : **incohérence réelle, mais dans l'autre sens**. La règle v1 donne ½ à une capacité « non standard
    mais livrée avec la chaîne officielle » : c'est le cas de tout `<immintrin.h>`, hors de la norme ISO. E4
    (`_mm_prefetch`, `__builtin_prefetch`) et D5 (`_mm_pause`) suivent cette règle (½) ; **C2 (`immintrin.h`) ne la suit
    pas** (1), pour C comme pour C++. Nim, qui atteint le même en-tête par `importc`, a ½ pour C2 ; le juge à l'aveugle,
    sous la règle du standard seul, classe `immintrin.h` comme extension pour C et C++ (C2 et E4 à 0,25). Monter E4 à 1
    contredirait la règle ; **C2 = ½ en v1 pour C et C++** la rétablit. En règle v2, C2 reste 1 (intrinsèques
    documentées du compilateur).
  * Effet : le pilier contrôle en règle v1 de C et de C++ baisse chacun de 3,6 points (A : 0,25 × 0,5 / 8 ; C : 0,20 ×
    0,5 / 5) ; le score principal (règle v2) ne change pas ; seules les variantes qui tirent la règle v1 bougent.
    L'effet n'est donc pas « moins de 0,5 point » dans ces variantes, mais il est le même pour C et C++.
* **K4** : **exact** sur le fond, à partir de nos données (Cascade Lake : clang 1,5 et 1,8 fois plus rapide que gcc
  sur C ; machine 15 : C++ par g++ 3,7 et 2,6 fois le temps de C par clang). Le chiffre de GCC 15 (16,9 ms) n'est pas
  vérifiable ici. Que C++ puisse écrire chaque noyau C est vrai en principe ; la règle commune range ces formes et cet
  autre compilateur parmi les sensibilités (remarque sur C++ : 79,7 points avec le K4 de clang++, contre 80,0 à C).
* **K9** (`k9_code.txt`, `data_facts.txt`) : **exact, et mesurable sur Cascade Lake**. Compilés pour Cascade Lake,
  `k9_rows` de C par gcc et de C++ par g++ donnent les mêmes boucles (9 et 24 instructions, au renommage des
  registres près). Dans les données principales, C++ (grilles réallouées, fils `std::jthread`) fait 0,99 fois le
  temps de C par gcc (grilles allouées une fois, fils `pthread`) en un fil, et **1,58 fois à quatre fils** : la
  pénalité du harnais sur la machine de référence, proche des × 1,48 de la remarque. La reproduction de l'auteur
  (pages neuves : × 1,38 en un fil, × 1,74 à deux fils) va dans le sens de la machine 15 (× 1,7 à 2,0), plus forte.
  « Le README le décrit sans le corriger » : exact (limite du protocole, décision laissée en suspens).
* **Pilier contrôle selon la règle** (`data_facts.txt`, `iso.txt`) : **exact**. C : 91,7 (v2), 77,8 (v1, 5e de la
  grille derrière Zig 83,2, C++ 82,7, Odin 81,3, D 78,9), 64,0 sous la règle du « Banc » (scénario B de la
  confrontation : Odin, Zig, C3, C++, C). C23 n'a pas d'attribut `likely` (clang 23 l'ignore, gcc 16 le refuse en
  `-pedantic-errors`), ni type vectoriel, ni préchargement, ni constante de ligne de cache (`__GCC_DESTRUCTIVE_SIZE` est
  une macro des compilateurs). WG14 N3837 et C2y : non vérifiés. « Le C classé est GNU C / Clang + glibc + OpenMP +
  intrinsèques » : **exact** (la grille v2 compte les extensions documentées, la glibc et OpenMP).
* **« C joue à domicile »** : **exact**. Le préambule de `docs/METHODOLOGY.md` le dit (« Seules les mesures de mise au
  point de la référence C l'ont précédé ») ; C était le seul des 13 premiers sans remarque. « La relecture a presque
  toujours fait gagner » : exact à trois exceptions près (C++ a perdu une place, C# et Nim n'ont rien gagné).
* **Machine** : **exact** (C 2e sur la machine 3 ; K3 à un facteur 7 du placement, `docs/FINDINGS.md`).
* **K8** (`k8_code.txt`) : **mécanisme exact**. Dans `a8_build` (clang 23), quatre des huit accès mémoire relisent ou
  réécrivent `*top` et `*counter` à chaque nœud ; et ces deux compteurs sont redondants (`v = q + indice`). Premières
  mesures sur cet hôte (un processus, cinq répétitions, validation) : forme du banc 293 à 310 ms sous clang, 178 sous
  gcc ; par valeur 140 à 161 et 83 ; itérative 144 et 133 (215 sous clang avec une première version à machine à
  états, abandonnée). Les 102 ms de la remarque pour l'itératif sous clang ne se retrouvent pas avec ma forme ; son code
  n'est pas fourni. C'est une meilleure forme (la spécification admet toute arène) : sensibilité, comme pour les autres
  langages.

## 3. Plan (poussé avant les mesures)

### 3.1 Règle commune

> « Les errata de faits (la grille) et les erreurs de mon implémentation entrent dans le classement publié ; une
> optimisation nouvelle reste une analyse de sensibilité. Est une erreur : un code qui ne fait pas ce qu'il annonce
> (Ada) ou qui s'écarte d'une convention que les autres implémentations suivent (ici, des noyaux isolés de la boucle de
> mesure). Une meilleure forme ou une meilleure disposition, même plus proche de ce que fait C, est une optimisation
> nouvelle ; de même pour les options réservées aux noyaux tuned appliquées au code naturel. » (`docs/FORTRAN.md`, 3.1)

### 3.2 Ce qui entre dans le classement publié

* **Errata de la grille, règle v1** : A3 = ½ et C2 = ½ pour C et pour C++ (`analysis/capabilities.py`) ; en règle v2,
  surcharges à 1 (`analysis/capabilities_v2.py` : `packed` et `<immintrin.h>`, extensions documentées livrées avec la
  chaîne). Score principal inchangé ; variantes de la règle v1 recalculées.
* **README** : ce qu'est le « C » classé (C23 de clang 23 avec ses extensions, intrinsèques d'Intel, OpenMP et glibc),
  ses rangs en règle v1 et sous la règle « ISO seule » ; les choix qui font changer la 1re place ; C relu (quatorze
  langages) ; la référence C mise au point avant le plan (Limites).
* **Rien d'autre** : ni K8 (meilleure forme), ni K9 (harmoniser les harnais reste une révision du protocole pour toutes
  les implémentations, décision en suspens ; remarque sur C++, plan 3.3), ni ex aequo (l'ordre reste le rang espéré
  sur les variantes ; le README montre ce qui le fait basculer).

### 3.3 Sensibilités et informations (hors classement publié)

Toutes partent du classement publié avec 3.2.

* **S-K8-val, S-K8-it** : K8 tuned de C × `c_k8val / c_ref` ou `c_k8it / c_ref` (transfert sur les données de C) ;
  **S-K8** : la meilleure des deux. Information : les mêmes rapports sous gcc (`c_gcc_k8* / c_gcc_ref`) pour l'annexe
  C par gcc.
* **I-K9-CL** : K9 tuned et `mt` des cinq implémentations qui allouent leurs grilles une fois (C, C par gcc, Chapel,
  Ada, Fortran) × la pénalité du harnais mesurée sur Cascade Lake à code égal (C++ / C par gcc, données principales :
  tuned et `mt`) ; le naturel n'est pas touché (formes différentes). C'est la pénalité « de type Cascade Lake » de la
  remarque, mesurée.
* **R-v1** et **R-ISO** : configuration principale avec le pilier contrôle en règle v1, et sous la règle du « Banc »
  (« ISO seule ») ; scores et rangs.
* **Tableau de la remarque** : T1 = C++ avec le K4 de clang++ (pont de la remarque sur C++) ; T2 = T1 et I-K9-CL ;
  T3 = T2 et S-K8.
* Chaque fois : score, piliers, rang espéré, place de C, part des variantes où C est 1er et où il devance C++ et Odin.

### 3.4 Mesures (`tools/measure_c.py`, machine 16)

* Copies (`tools/c_check/make_copies.py`, remplacements exacts ; sources et scripts dans `bench/`) : `c_k8val`,
  `c_k8it` (clang 23), `c_gcc_ref`, `c_gcc_k8val`, `c_gcc_k8it` (gcc 16, options de c_gcc) ; `c_ref` (clang 23, source de
  la campagne). `c_ref` et `c_gcc_ref` sont identiques à l'octet aux binaires de la réplication. Sommes de contrôle
  validées (K8 naturel et tuned) : 0 échec.
* 12 cellules (6 implémentations × K8 tuned et K8 naturel, témoin), 7 processus chacune en 7 passes, ordre tiré au
  hasard dans chaque passe (graine 20262101) ; répétitions de `results/calib.json` ; un échauffement ; règle de vol du
  pilote. Rien d'autre ne tourne pendant les mesures.

### 3.5 Analyse (`analysis/c_check.py`)

* Rapports appariés (moyenne géométrique des médianes de processus, intervalle par bootstrap) ; témoin K8 naturel.
* Scénarios (analyse v3 rejouée, mêmes tirages) : Avant (doit reproduire le scénario Publié de
  `results/cpp_check.json`, écart 0), Publié (errata), puis 3.3.
* Sorties : `results/c_check.json`, `results/report_c.md` ; puis régénération des sorties publiées.

### 3.6 Ce que je ne fais pas

* Pas d'harmonisation des harnais de K9 (révision du protocole, décision en suspens) : I-K9-CL en donne l'effet sur C.
* Pas de formes itératives ou par valeur pour les autres langages (C++, Rust, Zig en profiteraient) : non mesurées.
* Pas d'ex aequo décrété : le classement reste le rang espéré sur les variantes, avec ses parts de 1re place.
* Pas de vérification en ligne (N3837, C2y) ni de GCC 15.

## 4. Résultats (après les mesures)

Mesures du 1er novembre, de 18:14:14 à 18:17:43, sur la machine 16 (sans redémarrage) : 84 processus (12 cellules
× 7), aucune somme de contrôle fausse, aucun processus refait (vol médian 0,31 %, maximum 1,63 %). Rien d'autre ne
tournait ; pendant les mesures, seuls des fichiers ont été écrits, et poussés une fois (18:16:10). Sorties :
`results/report_c.md` et `results/c_check.json` (`analysis/c_check.py`) ; données : `results/raw_c/`. Le scénario
Avant reproduit exactement le publié d'avant la remarque (écart 0). Aucun écart au plan.

### 4.1 Mesures appariées (machine 16)

| K8 tuned | Forme du banc | Par valeur | Itérative |
|---|---|---|---|
| clang 23 (C classé) | 289,6 ms | 165,5 ms : 0,572 [0,514–0,637] | 115,6 ms : 0,399 [0,353–0,463] |
| gcc 16 (annexe) | 154,9 ms | 69,8 ms : 0,450 [0,428–0,482] | 135,1 ms : 0,872 [0,795–0,967] |

* **La remarque a raison sur K8.** L'arène du banc, dont l'état passe par la mémoire, coûte à C plus de la moitié de
  son temps. Écrite par itération, elle prend 2,5 fois moins de temps sous clang ; reportée sur Cascade Lake, elle
  ferait 106 ms, au niveau de la frontière de K8 (Ada, 107,7 ms). Sous gcc, c'est la récursion par valeur qui gagne
  (× 0,45). Les processus de l'itératif sous clang vont de 94 à 151 ms : les 102 ms de la remarque en font partie.
* Le témoin (K8 naturel, code inchangé) reste à 0,98 et 1,02 sous clang ; sous gcc, 1,06 et 1,11, dans le bruit de
  cette mesure d'allocation.
* « Clang n'est pas en cause » : en partie. Sous la forme du banc, gcc fait 0,53 fois le temps de clang ; sous la forme
  itérative, clang fait mieux que gcc (116 contre 135 ms) ; sous la forme par valeur, gcc garde l'avantage (70 contre
  166 ms). Le score K8 de C mesurait donc surtout l'écriture de l'arène, et secondairement le compilateur.

### 4.2 Classement publié : les errata de la règle v1

A3 et C2 passent à ½ en règle v1 pour C et pour C++ ; la règle v2 ne change pas, ni donc les scores. Dans la moitié
des variantes qui tire la règle v1, le contrôle de C passe de 77,8 à 74,2 et celui de C++ de 82,7 à 79,1. **L'ordre ne
change pas** : C reste 1er, mais moins nettement (rang espéré 1,90 → 2,20 ; 1er dans 52 % des variantes au lieu de
57 % ; devant Odin dans 72 % au lieu de 79 %) ; Odin 2e (3,60 → 3,47), C++ 3e (3,80 → 4,16), Zig 4e (4,77 → 4,66).
Les autres rangs espérés bougent de 0,1 au plus.

### 4.3 Sensibilités et informations

| Scénario | C | C++ | Odin | Rang espéré de C | C 1er | Tête |
|---|---|---|---|---|---|---|
| Publié | 80,01 | 76,57 | 73,49 | 2,20 (1er) | 52 % | C, Odin, C++, Zig |
| S-K8-val : arène par valeur | 82,48 | 76,57 | 73,49 | 1,69 (1er) | 71 % | C, Odin, C++, Zig |
| S-K8 : arène itérative | 84,08 | 76,51 | 73,42 | 1,56 (1er) | 77 % | C, Odin, C++, Zig |
| I-K9-CL : grilles réallouées, pénalité de Cascade Lake | 79,69 | 77,18 | 74,10 | 2,52 (1er) | 42 % | C, Odin, C++, Zig |
| R-v1 : contrôle en règle v1 | 73,90 | 71,94 | 72,53 | 2,94 (1er) | 31 % | C, Odin, Zig, C3 |
| R-ISO : contrôle « ISO seul » | 70,33 | 71,12 | 72,61 | 5,31 (5e) | 10 % | Odin, Zig, C3, C++ |
| T1 : C++ avec le K4 de clang++ | 80,01 | 79,71 | 73,49 | 2,49 (2e) | 36 % | C++, C, Odin, Zig |
| T2 : T1 et I-K9-CL | 79,69 | 80,38 | 74,10 | 2,85 (2e) | 25 % | C++, C, Odin, Zig |
| T3 : T2 et S-K8 | 83,73 | 80,30 | 74,03 | 1,78 (1er) | 67 % | C, C++, Odin, Zig |

* **K8** : avec la meilleure forme, C gagne 4,1 points (le « + 3 à + 4 » de la remarque) et devient la frontière de
  K8. L'annexe C par gcc, par valeur, passerait de 79,45 à 82,97. Meilleure forme : sensibilité, et d'autres langages
  en profiteraient sans doute aussi (non mesurés).
* **K9** : avec la pénalité du harnais mesurée sur Cascade Lake à code égal (× 1,58 à quatre fils, × 0,99 en un fil),
  C perd 0,3 point et reste 1er. La remarque estimait − 0,8 : la frontière de K9 `mt` recule elle aussi (Chapel, qui
  alloue une fois, la tenait ; elle passe à Mojo), ce qui amortit la perte. Avec la pénalité de la machine 15
  (I-K9-C de la remarque sur C++), C perdait 2,7 points : c'est un majorant.
* **Règle de contrôle** : en règle v1 partout, C reste 1er (73,9 points, devant Odin 72,5) ; sous la règle « ISO seule »
  du « Banc », C tombe 5e et Odin passe 1er, comme dans la confrontation.
* **Le tableau de la remarque se vérifie sur mesures** : avec le K4 de clang++, C++ passe devant C au rang espéré, de
  justesse (2,45 contre 2,49 ; C reste devant au score, 80,0 contre 79,7) ; avec en plus des grilles de K9 réallouées
  pour C, C++ est 1er (80,4 contre 79,7) ; avec en plus l'arène itérative pour C, C redevient 1er (83,7 contre 80,3).
  La 1re place change avec ces choix : la remarque a raison de dire qu'elle n'est pas établie.

### 4.4 Bilan de la remarque

* **Juste** : la place de C dans le groupe de tête et ses chiffres (ensemble de rangs, annexe gcc, C ISO) ; les faits
  de sa grille ; deux incohérences de la règle v1 (A3 ; C2 contre E4) ; l'écart C/C++ tient d'abord au compilateur
  sur K4 ; le harnais de K9 avantage C, et la pénalité se mesure sur Cascade Lake même (× 1,58 à quatre fils) ; la
  règle de contrôle décide (C 5e en « ISO seule ») ; C jouait à domicile (référence mise au point avant le plan, aucune
  relecture jusqu'ici) ; l'arène de K8 sous-estime C, de 4 points.
* **À nuancer** : l'incohérence de E4 se corrige dans l'autre sens (C2 à ½, pas E4 à 1), et l'effet n'est pas de
  moins de 0,5 point mais de 3,6 points de contrôle en règle v1, pour C comme pour C++ ; la pénalité de K9 de type
  Cascade Lake coûte 0,3 point à C, pas 0,8 ; « à compilateur égal, C et C++ sont à égalité » se vérifie sur K4, mais C
  reprend l'avance dès que son arène de K8 est mieux écrite.
* **Recommandations** : C est relu (cette remarque) ; le README dit ce qu'est le C classé, ses rangs en règle v1 et
  « ISO seule », et les choix qui font changer la 1re place. Je ne déclare pas d'ex aequo : le classement reste le rang
  espéré sur les variantes, où C est 1er dans 52 % d'entre elles, et la remarque montre surtout que cette place dépend
  de choix de protocole, ce que le README dit maintenant. Harmoniser le harnais de K9 reste une décision de protocole,
  en suspens ; son effet sur C est désormais mesuré (− 0,3 point).

### 4.5 Conséquences hors de C (sorties de l'état actuel recalculées)

Les errata ne touchent que les variantes en règle v1 : aucun score ne change, seuls les rangs espérés bougent. Sorties
recalculées : classement, figures, matrice, scénarios de Zig, de Julia, de Mojo, de C#, de Rust et de Nim dans l'état
actuel, sensibilité sans SIMD (témoin pointé sur le scénario Publié de `results/c_check.json`), confrontation.

* **Sans K4 dans le plafond** (`results/report_mojo_current.md`, S-K4) : la tête se joue à trois. Zig passe 1er au
  rang espéré (2,65), devant C (2,79) et C++ (2,79), qui restent devant au score (79,2 et 79,4 points contre 76,0) ;
  chacun est 1er dans 27 à 30 % des variantes. Avant les errata : C 2,48, C++ 2,55, Zig 2,77.
* **Zig de développement** (`results/report_zig.md`, S1) : toujours 1er, dans 52 % des variantes (49 % avant), C dans
  35 % (37 %).
* **Nim avec toutes ses versions optimisées** (`results/report_nim_current.md`, S-tout) : 3e au rang espéré (4,18)
  au lieu de 4e (4,29) ; avec Q1 en intrinsèques seul, 5e comme avant.
* **Sans SIMD explicite** (`docs/NOSIMD.md`, 4.9) : à la lettre, C++ passe 9e (rang espéré 6,96), derrière Nim (6,74)
  et Zig (6,87) ; à forme égale, Zig passe 3e devant C (3,54 contre 3,65) ; sans les noyaux vectorisables, C, Odin et
  C++ restent aux trois premières places.
* **Julia, Mojo, C#, Rust** : places inchangées dans tous leurs scénarios (C# 13e ou 14e avec toutes ses formes ;
  Rust 4e avec la règle de la libc étendue, 2e avec toutes les corrections de sa remarque).
* **Confrontation** (`results/confrontation_current.json`) : ordres, corrélations (0,78, 0,85, 0,81, 0,87) et rangs de
  C (1er, 5e, 1er, 6e) inchangés ; seuls les rangs espérés bougent.
