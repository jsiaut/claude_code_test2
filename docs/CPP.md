# Remarque sur C++ (1er novembre) : vérifications, plan et résultats

Les sections 1 à 3 ont été poussées avant les mesures ; la section 4 vient après.

## 1. La remarque

En résumé (texte reçu le 1er novembre) :

* **Verdict** : la place de C++ dans le groupe de tête est justifiée, mais pas sa 2e place derrière C, ni la raison
  qu'en donne le README. L'écart de 3,4 points (76,6 contre 80,0) viendrait surtout du compilateur choisi (g++ 16 pour
  C++, clang 23 pour C) et d'un défaut du harnais C++ ; une fois ces deux points corrigés, C++ serait à égalité avec C
  et nettement devant Odin. Point de départ : à compilateur égal, le plafond de C++ ne peut pas être plus bas que celui
  de C, puisque chaque noyau C se compile en C++ en remplaçant `restrict` par `__restrict` et `_Atomic` par
  `std::atomic`. L'auteur a refait les calculs sur les données brutes et reproduit deux mécanismes sur une VM du même
  type (GCC 13 et Clang 18 seulement).
* **Ce qui est juste** : le code naturel est honnête (K1 37,5 contre 41,8 ms en C ; Q1 73,4 contre 82,1 ; K9 en
  `vector<vector<double>>` 36,3 contre 37,9, quand Rust, 72,7, et D, 55,6, ne sont pas vectorisés) ;
  `std::unordered_map` est 22 fois plus lent que la table plate (la norme impose des nœuds chaînés) ; le contrôle
  (92,4) est globalement correct.
* **1. L'écart C/C++ est d'abord un écart clang/GCC.** Le plafond de K4 n'admet que deux boucles scalaires et mesure
  donc le vectoriseur. K4 : C par clang 4,05 / 2,85 ms (score 1,00), C par gcc 6,06 / 5,22 (0,55), C++ par g++
  6,48 / 6,51 (0,43). Avec le K4 de clang, C++ passerait de 76,6 à 80,0 points, le score de C. Reproduit : g++ 13
  laisse la boucle naturelle scalaire (14,9 ms), clang++ 18 la vectorise (1,34 ms). L'audit du 29 octobre demandait
  gcc et clang pour C et C++ ; c'est fait pour C et Fortran, pas pour C++, qui n'a pas non plus eu de relecture experte.
* **2. Un défaut du harnais C++ sur K9.** C alloue ses grilles une fois, C++ réalloue deux `std::vector` de 32 Mio à
  chaque répétition (180 600 défauts de page par processus contre 16 600) : K9 `mt` 19,6 ms contre 12,8 (C) et 12,2
  (C par gcc) ; 9,0 contre 6,0 à 6,3 ms sur Emerald Rapids. Reproduit à deux fils : 7,19 ms contre 6,44 quand les
  grilles sont allouées une fois ; rien en un fil. Mécanisme non isolé. Environ 0,9 point.
* **3. À compilateur égal, le reste est surtout du bruit.** C par gcc 79,5, C++ 76,6 : K9 0,9 point ; K4 0,9 (même
  code machine, processus de C++ de 5,5 à 8,8 ms) ; défauts 0,9 (D2 : un K1 mélangé 10 % plus lent, « mesure marquée
  comme bruitée » ; D3 : la queue de K8 tient à un seul processus sur sept, 573 µs contre 121 à 257 ; D4 : K2, la même
  boucle `i = a[i]`) ; K8 0,5 (arène passée par référence au lieu d'un pointeur brut) ; le contrôle et les autres
  noyaux rendent environ 0,5 point à C++.
* **4. Le README a les mauvaises proportions** : `unordered_map` ne coûte à C++ qu'environ 0,25 point face à C ; le
  code naturel ne pèse que 12,5 % du score, et la table naturelle de C est lente elle aussi (5,1 s contre 10,6).
* **Pour être équitable** : sur K8, GCC avantage C++ (0,59 contre 0,41) ; sur Emerald Rapids, C++ est 1er (K3) ; la
  libc ne compte que pour C et C++ (environ 3 points d'avance sur Rust) ; C1 vaut 1 au titre de `std::simd` alors que
  le manuel de GCC 16 qualifie le mode C++26 de « highly experimental » et que Rust (`std::simd` en nightly) a 0,5 : la
  note se défend par les `vector_size` de GCC, comme pour C, mais la justification devrait le dire ; A6 (SoA) vaut 0
  malgré la réflexion de GCC 16, qui permet d'écrire un SoA générique : 0,5 se défendrait.
* **C++26 au 1er novembre** : norme achevée en mars 2026 (Croydon) ; GCC 16.1 passe à C++20 par défaut, livre la
  réflexion (`-std=c++26 -freflection`) et `std::simd` (expérimental, x86 seulement) ; Clang 23.1 (25 août 2026) :
  pas de `std::simd` dans libc++, ni réflexion, ni contrats, ni P2795. GCC applique P2795 : en C++26, les variables
  locales non initialisées sont mises à zéro par défaut (`[[indeterminate]]` ou `-ftrivial-auto-var-init=uninitialized`
  pour s'en dispenser) ; effet probablement négligeable ici (seul `uint32_t h[16]` de K7 optimisé), mais c'est un coût
  caché qu'un classement de sympathie mécanique devrait relever.
* **Corrections proposées** : (1) mesurer C++ avec clang++ 23 (variantes en intrinsèques, comme C) et lui appliquer
  la règle des couples (langage, compilateur) ; (2) K9 : allouer les grilles une fois ; (3) Q1 optimisé en
  intrinsèques (36,5 contre 32,1 ms ; `std::simd` y fait un produit 64 bits que C évite avec `vpmuldq`) ; (4) K8 :
  passer un `ANode*` ; (5) ajouter des processus pour K1 mélangé, K2 et la queue de latence de K8.

## 2. Vérifications (faites avant le plan)

Machines 14 puis 15 : la VM a redémarré vers 14 h 42 sur un hôte du même modèle (Emerald Rapids, modèle 207,
4 vCPU), caractérisé avant les mesures (`results/hw/machine15/` : 2,63 à 2,64 GHz effectifs, latence à 4 Mio 35,7 ns,
DRAM 14,8 Go/s) ; les vérifications ne dépendent pas de l'hôte. Chaînes : g++ 16.2.0 (celle du banc), clang et
clang++ 23.1.5, libc++ 23. Preuves : `tools/cpp_check/collect.py` et `tools/cpp_check/data_facts.py` →
`results/cpp_check/*.txt` (sondes dans `tools/cpp_check/probes/`). Je n'ai consulté aucune page web : ce qui ne se
vérifie qu'en ligne (dates de l'ISO et de Clang 23.1, pages de statut, contrats) reste non vérifié.

* **Rejeu et décomposition** (`data_facts.txt`) : **exact**. C 80,01, C++ 76,57 : l'écart de 3,44 points se répartit
  en contrôle − 0,25 (en faveur de C++), plafond + 2,64 (K4 + 3,42, K9 + 0,69, K7 + 0,24, K5 + 0,09, K3 + 0,02, K1
  − 0,11, K6 − 0,11, K8 − 1,57) et défauts + 1,03 (D1 0,12, D2 0,16, D3 0,42, D4 0,32). Avec le score K4 de C (1,0),
  C++ aurait 80,03 points. Contre C par gcc (79,45) : 2,88 = K9 0,91, K4 0,92, D2 + D3 + D4 0,92, D1 0,14, K8 0,50,
  contrôle − 0,25, autres noyaux − 0,27. Les chiffres de la remarque sont exacts.
* **Point de départ** : **vrai en principe, mais pas une erreur au sens de la règle** (3.1). Le C++ peut écrire le
  code de C ; le banc mesure les implémentations telles qu'écrites, et une meilleure forme, même celle de C, est une
  optimisation nouvelle. Les formes de C en C++ (copies `cpp_intr`, `cpp_k8`, `cpp_k9`) sont des sensibilités.
* **Code naturel, `unordered_map`, contrôle** : **exact** (K1 naturel 37,54 contre 41,78 ms ; Q1 73,36 contre
  82,11 ; K9 36,33 contre 37,93 ; Rust 72,72 et D 55,64 ; K7 naturel de C++ 10,64 s, 22,0 fois sa table plate ; celui
  de C 5,11 s, 11,2 fois).
* **K4** (`k4.txt`, `clang_loops.txt`) : **exact**. Temps et scores de la remarque (médianes ; en moyennes
  géométriques, C 4,04 / 2,84 ms, C++ 6,54 / 6,79). Sous GCC, C et C++ donnent pour chaque forme la même boucle (61 et
  44 instructions, mêmes mnémoniques). clang++ 23 vectorise les deux formes comme clang (`vpminsb`, `vpmovzxbq`,
  `vpaddq`), en boucle plus courte (19 instructions, contre 35 pour C sur Cascade Lake et 67 sur Emerald Rapids).
  L'audit demandait bien les deux compilateurs pour C et C++ (recommandation 8) ; ma réponse ne l'a fait que pour C et
  Fortran. **Mais pas une erreur au sens de la règle** : le classement retient un compilateur par langage (README,
  Limites ; Fortran est classé avec gfortran, flang en annexe), et g++ 16 était le seul à livrer `std::simd`. Mesurer
  C++ avec clang++ est une sensibilité (S-clang-K4, S-clang), présentée à côté du couple (C, gcc).
* **K9** (`k9_harness.txt`, `data_facts.txt`) : **faits exacts, mais pas un défaut du harnais C++**. `k9_rows` est le
  même ligne à ligne (au `__restrict` près) et donne la même boucle sous clang ; C++ réalloue ses grilles à chaque
  répétition (180 658 défauts par processus en naturel, 180 572 en `mt`), C les alloue une fois (16 636). Mais la
  spécification n'impose que la réinitialisation hors chrono, et réallouer est la pratique de la majorité : d'après
  les sources, les grilles du chemin tuned et `mt` sont allouées une fois en C (et C par gcc), Chapel, Ada et Fortran,
  à chaque répétition en C++, Zig, Odin, C3, Rust, Nim, D, Julia, C#, Mojo, Go et Java. L'écart suit la pratique plus
  que le langage : sur Cascade Lake, K9 `mt` prend 10,8 à 12,8 ms pour C, C par gcc, Chapel et Fortran, 14,6 à
  24,4 ms pour les douze qui réallouent (C++ 19,6), alors qu'en un fil (tuned) les deux groupes sont entre 35 et 43 ms
  (hors Go et Ada, lents dès un fil). Corriger C++ seul l'avantagerait sur les onze autres qui réallouent. C'est une
  variable du protocole que la spécification ne fixe pas : sensibilité S-K9 (C++ comme C) et information I-K9-C (C
  comme la majorité), qui mesure l'effet sur C lui-même. Le mécanisme n'est pas établi (le nombre de défauts de page
  ne suffit pas à classer : Fortran en a 106 800 en tuned et `mt` avec des grilles allouées une fois, Mojo 107 800 en
  les réallouant).
* **Bruit à compilateur égal** (`data_facts.txt`) :
  * K4 : **en partie exact**. Même boucle en C par gcc et en C++, mais les trois processus de C++ en naturel (6,28 à
    6,88 ms) sont tous au-dessus des deux de C par gcc (6,03 et 6,10) ; en sans branchement, 5,46 à 8,83 ms (le plus
    lent passe de 9,2 à 5,4 ms au fil de ses répétitions) contre 5,13 et 5,31. À code identique, l'écart tient au
    placement du code ou au bruit (leçon de la remarque sur Odin), pas au langage.
  * D2 : **exact sur le fait**. Un processus de K1 mélangé à 45,1 ms, l'autre à 37,3 ms, au niveau du naturel ; sans
    lui, D2 vaudrait 1, comme pour C. La mesure n'est « marquée comme bruitée » dans aucune sortie.
  * D3 : **inexact**. Les sept processus de la remesure de D3 donnent à C++ des p99,9 de 121 à 573 µs (C : 95 à 217 ;
    C par gcc : 55 à 279). Sans le plus haut, la queue regroupée de C++ reste à 155 µs (C 114, C par gcc 90) : ce
    processus explique environ un quart de l'écart de D3 (0,640 contre 0,753 ; environ 0,670 sans lui).
  * D4 : **exact**. À 256 Kio, un processus de C++ à 28,4 ms (répétitions de 22 à 34 ms), l'autre à 19,2 ; sans lui,
    D4 vaudrait environ 0,965, comme pour C (0,968).
  * Ces processus n'ont pas de vol de temps notable (0 à 0,55 %) : ce sont des phases lentes à l'intérieur d'un
    processus. D'autres implémentations en ont : sur les cinq clés de D2 et D4 (K1 naturel et mélangé, K2 à trois
    tailles), l'écart entre processus d'une même cellule va jusqu'à 1,48 pour C++, 1,60 pour JavaScript, 1,42 pour
    Fortran, 1,40 pour Lua, et chaque cellule n'a que 2 ou 3 processus (`data_facts.txt`).
  * K8 (`k8_q1.txt`) : **exact**, `std::vector<ANode>&` contre `ANode*` en C. Le code fait ce qu'il annonce : meilleure
    forme, sensibilité (S-K8).
* **Q1 optimisé** (`k8_q1.txt`) : **exact**. 36,92 ms en moyenne géométrique (médiane 36,47) contre 32,11 ; six
  `vpmullq` (produit 64 bits) dans le C++, deux `vpmuldq` dans le C. Même algorithme (16 lignes par pas, masques par
  groupe), donc pas un écart à la convention de Q1 fixée pour D : forme de primitive, sensibilité (S-intr).
* **README** : **exact**. Avec le K7 naturel de C, C++ gagnerait 0,25 point ; le code naturel (D1) pèse 12,5 % du
  score. Ce qui sépare C++ de C est K4 (3,42 points), puis K9 (0,69), D3 (0,42), D4 (0,32) et D2 (0,16) ; K8 (1,57) et
  le contrôle (0,25) jouent pour C++. « Ses conteneurs standard vont contre le cache » est vrai mais n'explique pas sa
  place : à corriger.
* **Équité** :
  * K8, Emerald Rapids, libc : **exact** (`results/summary_v3.json`, README).
  * **C1** (`gcc_manual.txt`, `simd.txt`, `versions.txt`) : **exact, erratum en règle v1**. Le manuel de GCC 16.2
    qualifie `-std=c++26` de « highly experimental, and will almost certainly change in incompatible ways in future
    releases » ; libstdc++ ne définit pas `__cpp_lib_simd` et ne fournit `std::simd` qu'en C++26 hébergé, avec les
    liaisons structurées et les instructions d'expansion de C++26, et `__SSE2__` (x86 seulement) ; libc++ 23 n'a pas
    d'en-tête `<simd>` (seulement `<experimental/simd>`, celui du TS Parallelism v2). La règle v1 donne 0,5 à une
    capacité « expérimentale, propre à un compilateur » : `std::simd` en relève, comme `vector_size` (extension de gcc
    et clang, 0,5 en v1 pour C) et le `std::simd` de Rust (nightly, 0,5). **Erratum : C++ C1 = 0,5 en règle v1.** En
    règle v2 (« extensions … documentées du compilateur, sous une forme stable »), le `vector_size` de g++ vaut 1, comme
    pour C : C1 reste 1, et la justification le dira. Le score principal (règle v2) ne change pas ; le pilier C en
    règle v1, tiré dans la moitié des variantes, baisse d'environ 2 points.
  * **A6** : **pas d'erratum**. La réflexion de GCC 16 (`-freflection`, « experimental ») permet bien d'écrire un SoA
    générique (sonde `refl.cpp` : le nombre de membres d'une structure, calculé à la compilation). Mais A6 note un SoA
    livré par le langage ou sa bibliothèque : 1 pour Zig (`std.MultiArrayList`) et Odin (`#soa`), 0 pour D, Nim et
    Rust, dont la métaprogrammation, stable, permettrait aussi d'en écrire un. Donner 0,5 à C++ pour un mécanisme
    expérimental qui permet de l'écrire contredirait ces notes.
* **C++26** (`versions.txt`, `gcc_manual.txt`, `reflection.txt`) : g++ 16 sans `-std` définit `__cplusplus` à
  202002L (C++20 par défaut, **exact**) ; la sonde de réflexion compile et s'exécute avec `-std=c++26 -freflection`
  et échoue sans `-freflection` (**exact**) ; clang++ 23 ignore `-freflection` (« argument unused ») et refuse
  l'opérateur `^^` (**exact**) ; `std::simd` : voir C1 (**exact**).
* **P2795** (`p2795.txt`) : **exact pour GCC, inexact pour l'effet**. Sonde : un tableau local non initialisé est mis
  à zéro sous `-std=c++26` (deux rangements), pas sous `-std=c++23`, ni avec `-ftrivial-auto-var-init=uninitialized`,
  ni par clang++ 23. Le binaire de la campagne recompilé sans cette mise à zéro garde ses 17 fonctions de noyaux
  identiques ; seules changent des fonctions du harnais, hors chrono (`main`, `run_k1`, `run_k2`, `run_k3`, `run_k4`,
  `run_k6`, `run_k8`, `fmt`, enveloppes de threads). K7 optimisé n'est pas touché : coût nul sur les noyaux mesurés.

## 3. Plan (poussé avant les mesures)

### 3.1 Règle commune

> « Les errata de faits (la grille) et les erreurs de mon implémentation entrent dans le classement publié ; une
> optimisation nouvelle reste une analyse de sensibilité. Est une erreur : un code qui ne fait pas ce qu'il annonce
> (Ada) ou qui s'écarte d'une convention que les autres implémentations suivent (ici, des noyaux isolés de la boucle de
> mesure). Une meilleure forme ou une meilleure disposition, même plus proche de ce que fait C, est une optimisation
> nouvelle ; de même pour les options réservées aux noyaux tuned appliquées au code naturel. » (`docs/FORTRAN.md`, 3.1)

### 3.2 Ce qui entre dans le classement publié

* **Erratum C1** : C++ C1 = 0,5 en règle v1 (texte corrigé dans `analysis/capabilities.py`) ; en règle v2, surcharge
  `("cpp", "C1")` = 1 dans `analysis/capabilities_v2.py`, justifiée par `vector_size` (extension documentée de g++ et
  clang++, stable, comme pour C), `std::simd` de C++26 étant expérimental dans GCC 16.
* **Remesure de D2 et D4 pour les 25 implémentations de la campagne** (le point 5 de la remarque, sous sa forme
  équitable ; la queue de K8 a déjà sept processus par implémentation depuis la remesure de D3) : K1 naturel et
  mélangé, K2 à 16 Kio, 256 Kio et 8 Mio, 7 processus chacune, machine 15, binaires de `bench/` (ceux de la remesure de
  D3). Comme pour D3 (remarque sur Rust) et pour K5 (v2), les valeurs remesurées remplacent celles de la campagne,
  pour toutes les implémentations : dans D2, le rapport K1 naturel / K1 mélangé (la part d'empreinte ne change pas) ;
  dans D4, les temps de K2 et leurs références (même règle que l'analyse v3, recalculée sur la remesure). D1 garde le
  K1 naturel de la campagne, que la frontière de Cascade Lake normalise. Même estimateur et mêmes tirages par
  processus que l'analyse v3.
* **README** : ligne et paragraphe de C++ (ce qui le sépare de C : K4 et le compilateur, K9 et la pratique
  d'allocation, D3 ; `unordered_map` à sa juste place) ; Limites (le couple C++/clang++ en sensibilité ; la pratique
  d'allocation de K9 si l'effet est établi, voir 3.3) ; errata. FINDINGS : `std::simd` et la réflexion dans GCC 16,
  P2795.
* **Rien d'autre** : ni K9 (spécification muette, pas de convention suivie par les autres), ni K8 ni Q1 (meilleures
  formes), ni clang++ (un compilateur par langage), ni K4 (non demandé ; l'analyse d'incertitude tire déjà les
  processus de K4).

### 3.3 Sensibilités (hors classement publié)

Toutes partent du classement publié avec 3.2. Rapports appariés `cpp_x / cpp_ref` mesurés sur la machine 15,
reportés sur les données de C++ par transfert seul (comme S-agg pour Odin) ; pour S-clang et S-remarque, les latences
de K8 naturel de C++ (p99,9 et maximum de D3) sont multipliées par le rapport des médianes regroupées
`cpp_x / cpp_ref`.

* **S-clang-K4** : K4 naturel et sans branchement × `cpp_clang / cpp_ref`. Information : S-clang-K4-pont, K4 de C++ =
  K4 de C (données principales) × `cpp_clang / c_ref` (l'hypothèse de la remarque, « K4 au niveau de clang »).
* **S-clang** : les 27 clés × `cpp_clang / cpp_ref` (clang++ 23 ; faute de `std::simd`, les quatre noyaux qui s'en
  servent y prennent la forme de C).
* **S-intr** : K1 soa, K5 tuned, Q6 tuned et `mt`, Q1 tuned et `mt` × `cpp_intr / cpp_ref` (g++ 16).
* **S-K8** : K8 tuned × `cpp_k8 / cpp_ref`.
* **S-K9** : K9 naturel, tuned et `mt` × `cpp_k9 / cpp_ref`.
* **S-remarque** : les 27 clés × `cpp_all / cpp_ref` (les corrections 1 à 4 de la remarque ensemble, sous clang++).
* **Information, hors règle** : I-K9-C, les trois clés de K9 de C × `c_k9 / c_ref` (C avec la pratique de la
  majorité) ; I-K9-maj, les mêmes rapports appliqués aux clés de K9 des cinq implémentations qui allouent une fois
  (C, C par gcc, Chapel et Ada pour les trois clés ; Fortran pour tuned et `mt`, son naturel réallouant déjà) ; I-pareil, rapports du même hôte `cpp_ref / c_ref`, `cpp_clang / c_ref` et `cpp_all / c_ref`, clé par
  clé, sans score (à compilateur égal, C++ fait-il comme C ?).
* Chaque fois : score, piliers, rang espéré, place, part des variantes où C++ devance C et Odin.

**Interprétation fixée d'avance pour K9** : l'effet de la pratique d'allocation est établi si l'intervalle de
`c_k9 / c_ref` ou de `cpp_k9 / cpp_ref` sur K9 `mt` exclut 1. Il est alors décrit dans les Limites du README et dans
FINDINGS, avec les implémentations de chaque pratique ; harmoniser les harnais de K9 serait une révision du protocole
pour toutes les implémentations, hors de cette remarque.

### 3.4 Mesures (`tools/measure_cpp.py`, machine 15)

* **Copies** (`tools/cpp_check/make_copies.py`, remplacements exacts ; sources et scripts dans `bench/`) : `cpp_ref`
  (source de la campagne, g++ 16 et options du banc), `cpp_clang` (source de `cpp_intr` par clang++ 23, libstdc++ de
  GCC 16), `cpp_all` (`cpp_intr` + `cpp_k9` + `cpp_k8` par clang++ 23) : les 27 mesures de C++ du score ; `c_ref`
  (source C de la campagne, clang 23) : ses 26 ; `cpp_intr` (K1 soa, K5 tuned, Q6 tuned et Q1 tuned dans la forme de
  C, g++ 16) : 6 clés ; `cpp_k9` (grilles allouées une fois) et `c_k9` (grilles réallouées à chaque répétition) : les
  3 clés de K9 ; `cpp_k8` (arène par `ANode*`) : K8 tuned. `cpp_ref` et `c_ref` sont identiques à l'octet aux binaires
  de la réplication sur Emerald Rapids (`results/hw/machine3/binaries.txt`, « après »). Sommes de contrôle validées
  (`--quick`) : 0 échec.
* **Remesure** : les 25 implémentations × K1 naturel et mélangé, K2 à 16 Kio, 256 Kio et 8 Mio ; validation (K2 à
  16 Kio, 25 implémentations) : 0 échec.
* 245 cellules, 7 processus chacune en 7 passes, toutes les cellules de chaque passe dans un ordre tiré au hasard
  (graine 20262001) ; répétitions de `results/calib.json` ; échauffements : copies 2 pour K5, 1 sinon ; remesure 3
  pour les JIT, 1 sinon ; règle de vol du pilote. Rien d'autre ne tourne pendant les mesures.

### 3.5 Analyse (`analysis/cpp_check.py`)

* Rapports appariés (moyenne géométrique des médianes de processus, intervalle par bootstrap).
* Scénarios (analyse v3 rejouée, mêmes tirages) : Avant (doit reproduire le publié actuel, scénario Publié de
  `results/odin_check.json`, écart 0), P-C1 (erratum seul), P-D24 (remesure seule), Publié (les deux), puis les
  sensibilités et informations de 3.3.
* Décomposition de l'écart entre C et C++ dans le Publié (par composante et par noyau), pour le README.
* Sorties : `results/cpp_check.json`, `results/report_cpp.md` ; puis régénération des sorties publiées.

### 3.6 Ce que je ne fais pas

* Le couple (C++, clang++) n'entre pas au classement (un compilateur par langage, comme pour Fortran) ; il est mesuré
  (S-clang) et présenté à côté.
* Pas d'harmonisation des harnais de K9 dans cette remarque (voir l'interprétation de 3.3).
* Pas de remesure de K4 pour tous (non demandée).
* Pas de vérification en ligne (dates, pages de statut, contrats).
