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

## 4. Résultats (après les mesures)

Mesures du 1er novembre, de 15:34:14 à 16:30:08, sur la machine 15 (sans redémarrage) : 1 715 processus (245 cellules
× 7), aucune somme de contrôle fausse ; 64 processus refaits pour vol de temps au-dessus de 2 % (dont 3 deux fois),
aucun gardé au-dessus (vol médian 0,22 %, maximum 1,98 %). Rien d'autre ne tournait. Sorties : `results/report_cpp.md`
et `results/cpp_check.json` (`analysis/cpp_check.py`) ; données : `results/raw_cpp/`, `results/raw_d24/`. Le scénario
Avant reproduit exactement le publié d'avant la remarque (écart 0).

### 4.1 Écarts au plan, décidés après avoir vu les données

Ordre des calculs : j'ai lu les rapports bruts, comparé le rapport C++/C de l'hôte à celui de Cascade Lake clé par clé,
puis regardé la remesure de D2 et D4 ; j'ai lancé l'analyse telle que le plan la prévoyait, et l'ai arrêtée après dix
scénarios, quand les transferts ont montré leur artefact (C à 73,1 points dans S-clang ; journal :
`results/cpp_check/run1_plan.log`). Les décisions ci-dessous ont été prises à ce moment-là.

1. **La remesure de D2 et D4 n'est pas publiée.** Elle devait réduire le bruit de ces deux composantes ; sur cet hôte,
   elle change ce qu'elles mesurent.
   * K2 à 8 Mio est bimodal : pour 21 implémentations sur 25, les sept processus d'une cellule s'écartent d'un facteur
     3,2 à 4,0 (C : cinq processus de 160 à 205 ms, deux à 480 et 584 ms, au même nombre de défauts de page ; pages de
     4 Kio, THP en `madvise`), contre 1,6 au plus dans la campagne pour les cinq clés. Le tableau tient dans le L3 de
     cet hôte ; son temps dépend sans doute de ce que les autres machines virtuelles y laissent.
   * La pénalité de désordre des langages à références y est deux fois plus faible que sur Cascade Lake (C# 4,70 →
     2,68, Java 4,91 → 2,75, JavaScript 5,93 → 3,48, OCaml 6,99 → 2,22, Lua 6,68 → 4,32, Python 5,20 → 3,84), et celle
     de Haskell passe de 0,93 à 1,50 : D2 y mesure un autre régime de cache.
   * Go met 2,2 s sur K1 naturel (56 ms sur Cascade Lake ; 1,8 à 1,9 s déjà sur la machine 3, en temps utilisateur ;
     cause non cherchée), au même rapport entre ordres naturel et mélangé.

   Publier ces valeurs déplacerait tous les langages pour des raisons d'hôte (scénario P-D24, information : C 80,01 →
   79,53, Odin 73,49 → 73,01, D 72,62 → 71,99, Mojo 62,76 → 63,02). La remesure de D3 (remarque sur Rust) visait un
   bruit démontré, lié au vol de temps ; celle-ci ajoute ses propres artefacts. Elle confirme en revanche le diagnostic
   de la remarque pour C++ : sur sept processus, son K1 mélangé fait 1,04 fois le naturel (1,09 dans la campagne, à
   cause d'un processus) et K2 à 256 Kio 24,9 ms, comme C (25,0). (Les corrections publiées d'Ada et de Fortran sur K1
   et K2 sont appliquées à leur remesure, faite avec les binaires de la campagne.)
2. **Le transfert seul ne tient pas pour plusieurs clés.** Le rapport C++/C de l'hôte s'écarte de celui de Cascade Lake
   de + 130 % sur K4 naturel, de + 60 à + 91 % sur K9, de − 42 % sur K3 en écrivain unique et de − 36 % sur K2 à 8 Mio.
   Reporté sur les temps de C++ de Cascade Lake, un rapport de l'hôte y donne des temps qui deviennent la référence du
   noyau et abaissent tous les autres langages : C tombe à 78,1 points (S-clang-K4), 73,6 (S-clang), 78,3 (S-K9) et
   71,7 (S-remarque). Ces scénarios du plan sont donnés tels quels, mais ne mesurent pas ce qu'ils annoncent. J'ai
   ajouté S-clang-pont, S-K9-pont et S-remarque-pont : chaque clé de C++ y vaut le temps de C de Cascade Lake multiplié
   par le rapport au C du même hôte, sauf K3 (temps dépendant du placement du code sur Emerald Rapids, laissé aux
   données principales) et K8 `tuned_alloc` (sans équivalent en C : transfert). Le pont a ses propres limites : il
   suppose le rapport C++/C indépendant de l'hôte, ce que démentent K9 (pénalité d'allocation bien plus forte ici) et
   K2 à 8 Mio (bimodal), et il prend pour D3 le maximum de latence de cet hôte. Seuls S-clang-K4-pont (prévu ; deux
   clés mesurées avec précision), S-K8 et S-intr (rapports de l'hôte proches de ceux de Cascade Lake) sont propres.
3. Précision : pour S-clang et S-remarque, les cinq colonnes de latence de K8 naturel sont multipliées (le plan nommait
   le p99,9 et le maximum ; le p50 ne sert qu'à la variante relative de D3).

### 4.2 Mesures appariées (machine 15)

| Question | Clé | Rapport [IC 95 %] |
|---|---|---|
| clang++ / g++ (`cpp_clang` / `cpp_ref`) | K4 naturel ; sans branchement | 0,285 [0,256–0,317] ; 0,423 [0,374–0,472] |
| | K8 tuned ; K8 naturel | 1,546 [1,488–1,605] ; 1,220 [1,084–1,356] |
| | K5 naturel ; Q6 naturel | 1,938 [1,834–2,035] ; 0,309 [0,291–0,327] |
| C++ / C, même hôte | K4 naturel ; sans branchement, clang++ | 1,06 [0,91–1,22] ; 1,11 [0,95–1,26] |
| | K4 naturel ; sans branchement, g++ | 3,72 [3,35–4,08] ; 2,63 [2,35–2,92] (Cascade Lake : 1,62 ; 2,39) |
| | 26 clés, moyenne géométrique : g++ ; clang++ ; corrections de la remarque | 1,105 ; 0,995 ; 0,901 |
| C, grilles de K9 réallouées (`c_k9` / `c_ref`) | naturel ; tuned ; `mt` | 1,70 [1,33–2,16] ; 1,93 [1,58–2,32] ; 2,01 [1,63–2,42] |
| C++, grilles allouées une fois (`cpp_k9` / `cpp_ref`) | naturel ; tuned ; `mt` | 0,63 [0,51–0,79] ; 0,72 [0,57–0,92] ; 0,41 [0,36–0,47] |
| `cpp_k9` / C, même hôte | naturel ; tuned ; `mt` | 1,13 [0,96–1,30] ; 1,09 [0,90–1,34] ; 0,98 [0,79–1,17] |
| Arène par `ANode*` (`cpp_k8` / `cpp_ref`) | K8 tuned | 0,766 [0,728–0,812] |
| Forme de C, g++ (`cpp_intr` / `cpp_ref`) | Q1 tuned ; Q1 `mt` | 1,037 [0,951–1,117] ; 0,898 [0,787–1,006] |
| | K5 tuned ; Q6 tuned ; Q6 `mt` ; K1 SoA | 1,109 ; 1,192 ; 1,152 ; 0,916 |

* **À compilateur égal, C++ fait comme C** : sur l'hôte, C++ compilé par clang++ fait 0,995 fois le temps de C en
  moyenne géométrique des 26 clés communes. Les écarts restants tiennent à la forme (K7 naturel, `unordered_map`, 2,25 ;
  Q6 naturel, que clang++ vectorise dans la forme de C++ et pas dans celle de C, 0,31), au harnais (K9, 1,7 à 2,1) et au
  placement du code (K3 en écrivain unique, 0,19).
* **K4** : clang++ divise le temps de g++ par 2,4 à 3,5 et rejoint C (1,06 et 1,11).
* **K9** : l'effet de la pratique d'allocation est établi (intervalles hors de 1). Sur cet hôte, réallouer les grilles
  double presque le temps de C lui-même, en un fil comme à quatre ; allouées une fois, les grilles de C++ lui donnent
  le temps de C (0,98 en `mt`). La pénalité dépend de l'hôte : dans les données principales (Cascade Lake), les
  implémentations qui réallouent font le temps de C en un fil, et 1,1 à 1,9 fois celui de C à quatre fils.
* **K8** : l'avantage de GCC se confirme (clang++ × 1,55 sur l'arène) ; l'arène par pointeur brut gagne 23 % sous g++.
* **Q1** : non confirmé sur cet hôte. La forme de C n'y est pas plus rapide sous g++ (1,04), et le Q1 de C++ ne fait
  que 1,03 fois celui de C (1,15 sur Cascade Lake).
* **clang++ ne gagne pas partout** : il perd l'arène de K8 (× 1,55) et K5 naturel (× 1,94 ; GCC y met moitié moins
  de temps que clang, en C comme en C++ : 79 contre 158 ms en C dans les données publiées de K5).

### 4.3 Classement publié : l'erratum C1

C++ garde 76,57 points (la règle v2, celle du score principal, ne change pas), mais son pilier de contrôle en règle v1
perd 2 points, et la moitié des variantes tire cette règle : son rang espéré passe de 3,61 à 3,80, celui d'Odin de 3,63
à 3,60. **Odin passe 2e et C++ 3e**, à égalité de fait (C++ devance Odin dans 50 % des variantes). C reste 1er (rang
espéré 1,90 ; 1er dans 57 % des variantes, C++ dans 11 % au lieu de 14 %). Aucun autre langage ne change de place.

### 4.4 Sensibilités (hors classement publié)

| Scénario | Statut | C++ | C | Rang espéré de C++ | Devant C | Devant Odin | Fiabilité |
|---|---|---|---|---|---|---|---|
| Publié | publié | 76,57 | 80,01 | 3,80 (3e) | 20 % | 50 % | |
| S-clang-K4-pont : K4 de clang++ | plan (information) | 79,71 | 80,01 | 2,24 (2e) | 49 % | 79 % | propre |
| S-K8 : arène par `ANode*` | plan | 77,64 | 80,01 | 3,28 (2e) | 29 % | 59 % | propre |
| S-intr : formes de C | plan | 76,09 | 79,82 | 3,97 (3e) | 18 % | 47 % | propre |
| S-K9 : grilles allouées une fois | plan | 77,77 | 78,30 | 2,52 (2e) | 46 % | 72 % | références déplacées |
| S-K9-pont | après coup | 77,00 | 80,01 | 3,64 (3e) | 22 % | 53 % | pénalité de l'hôte |
| S-clang-K4 | plan | 80,32 | 78,11 | 1,52 (1er) | 80 % | 92 % | références déplacées |
| S-clang : tout par clang++ | plan | 77,10 | 73,56 | 1,89 (1er) | 67 % | 86 % | références déplacées |
| S-clang-pont | après coup | 75,09 | 79,46 | 4,83 (4e) | 10 % | 35 % | K9 de l'hôte (2,6 points) |
| S-remarque : corrections 1 à 4 | plan | 78,42 | 71,70 | 1,55 (1er) | 83 % | 92 % | références déplacées |
| S-remarque-pont | après coup | 78,88 | 79,28 | 2,66 (2e) | 41 % | 73 % | K2 à 8 Mio, D3 de l'hôte |
| I-K9-C : C réalloue | plan (information) | 76,57 | 77,32 | 3,52 (3e) ; C 3,41 | 48 % | 50 % | majorant |
| I-K9-maj : C, C par gcc, Chapel, Ada, Fortran réallouent | plan (information) | 77,18 | 77,93 | 3,37 (3e) ; C 3,23 | 48 % | 50 % | majorant |

* **K4 suffit à combler l'écart** : avec le K4 de clang++, estimé par le pont prévu au plan, C++ aurait 79,7 points
  contre 80,0 à C, et le devancerait dans 49 % des variantes. C'est le point central de la remarque, et il est exact.
* **Mais le compilateur joue dans les deux sens.** g++ coûte K4 à C++ et lui rapporte l'arène de K8 et K5 naturel. Un
  score de C++ entièrement compilé par clang++ ne se déduit pas proprement de cet hôte : le transfert déplace les
  références (C à 73,6), et le pont importe la pénalité d'allocation de K9 propre à cet hôte (2,6 points de l'écart de
  S-clang-pont). Le classement garde g++, seul à livrer `std::simd`, comme il garde un compilateur par langage.
* **Toutes les corrections de la remarque ensemble** donnent, par le pont, 78,9 points contre 79,3 à C : C++ 2e, devant
  Odin dans 73 % des variantes et devant C dans 41 %. « À égalité avec C » est presque juste, mais ce sont des
  sensibilités (autre compilateur, meilleures formes, autre harnais), pas des erreurs.
* **Le harnais de K9 pèse aussi sur C.** Si C réallouait ses grilles comme la majorité, avec la pénalité de cet hôte,
  il perdrait 2,7 points et sa 1re place en rang espéré (3,41, derrière Odin, 3,33). Sur Cascade Lake, la pénalité est
  moindre (sensible seulement à quatre fils) : c'est un majorant. Harmoniser les harnais de K9 serait une révision du
  protocole pour toutes les implémentations, hors de cette remarque (plan, 3.3) : la limite est décrite dans le README.

### 4.5 Bilan de la remarque

* **Juste** : le code naturel de C++ est honnête ; `unordered_map` est 22 fois plus lent que sa table plate mais ne
  coûte que 0,25 point face à C ; la décomposition de l'écart est exacte ; l'écart tient d'abord à K4, donc à g++
  (79,7 points avec le K4 de clang++) ; le K9 à quatre fils de C++ tient au harnais (grilles réallouées) ; D2 et D4
  tenaient à un processus chacun (confirmé par la remesure) ; GCC avantage C++ sur K8 ; la note C1 de `std::simd`
  était trop haute en règle v1 (erratum) ; les faits sur GCC 16 et clang 23 vérifiables sans le web sont exacts.
* **Inexact ou à nuancer** : le harnais de K9 n'est pas un défaut de C++ mais la pratique de la majorité, que la
  spécification ne tranche pas ; D3 ne tient pas à un seul processus ; le compilateur ne joue pas que contre C++ (K8,
  K5 naturel) ; le Q1 en intrinsèques n'est pas plus rapide sur cet hôte ; P2795 ne touche aucun noyau ; A6 reste 0.
* **Ce qui change dans le classement publié** : l'erratum C1, qui fait passer C++ du 2e au 3e rang espéré, derrière
  Odin, à égalité de fait (50 %). Le README dit désormais ce qui sépare C++ de C (K4 et le compilateur, puis K9 et la
  pratique d'allocation, puis D3) et décrit deux limites du protocole : un compilateur par langage, et l'allocation
  des grilles de K9, libre.
