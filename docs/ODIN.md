# Remarque sur Odin (1er novembre) : vérifications, plan et résultats

Les sections 1 à 3 ont été poussées avant les mesures ; la section 4 vient après.

## 1. La remarque

En résumé (texte reçu le 1er novembre) :

* **Verdict** : Odin a sa place en tête, rien ne le surestime ; la 3e place n'est pas établie et l'étude le sous-estime
  plutôt (une erreur de fait, une transcription probablement fautive, aucune erreur dans l'autre sens). L'auteur a lu
  le compilateur de l'étude (tag `dev-2026-10`, commit `84bc3fc`), master au 1er novembre et la documentation au 27
  octobre, et rejoué l'analyse (mêmes 20 000 variantes) : 72,6 points, 3e, devant Zig dans 55 %. Il n'a rien mesuré.
* **Ce qui est juste** : place d'équilibre (contrôle 81,5, plafond 78,6, code par défaut 50,6) ; `@(fast_math)` ne
  marche pas dans dev-2026-10 (drapeau de réassociation à 0 testé comme un masque), C4 = 0 défendable ; l'allocateur
  par défaut enveloppe `calloc` et sur-alloue (un nœud de 24 octets occupe 48 au lieu de 32), avec deux appels non
  inlinables et un appel indirect (1,9 s sur K8 naturel contre 0,98 en C) ; l'horloge fait un appel système à chaque
  lecture.
* **Erreur de fait, C2 en règle v2 = 1** : l'erratum du 30 octobre a baissé C2 à 0,5 sous les deux règles en citant le
  juge à l'aveugle, qui notait pourtant 1 sous la règle v2 (0,5 sous l'autre), sonde `vpconflictd` à l'appui. Odin
  appelle toute intrinsèque de LLVM par `foreign _` et `@(link_name="llvm.x86…")`, `#const` pour les immédiats ;
  documenté sur odin-lang.org depuis le 12 octobre ; 309 liaisons dans la bibliothèque standard, dont `core:sys/llvm`.
  C'est ce qui vaut 1 à Julia et à Mojo. Effet : 73,5 points, 3e, à égalité avec C++ (3,63 contre 3,61), devant Zig
  dans 59 %.
* **Transcription probablement fautive, Q1 tuned** : 46 ms contre 32 en C, 34,6 en Zig, 33,7 en C3 (même algorithme,
  même backend) ; 20,8 ms à 4 threads contre 13 à 15. Chaque groupe est compté par `simd.reduce_add_pairs(m & 1)`, six
  fois par paquet de 16 lignes, en arbre de permutations que LLVM ne reconnaît pas (environ 50 µops, 14 ms) ; C et Zig
  font un popcount du masque. Correctif d'une ligne : `card(simd.extract_msbs(m))`. « Le même type d'écart que le Q1
  de D. »
* **À mesurer** : `-o:speed` = pipeline O2 de LLVM, `-o:aggressive` = O3 (environ 1 point pour C3) ; K1 aos :
  `@(optimization_mode="favor_size")` n'empêche pas l'inlining contrairement au commentaire (`#force_no_inline` le
  ferait), « sans effet sur le score ».
* **README** : la table `map` fait 5 fois la table plate, mais toutes les tables standard sont dans ce cas, et c'est la
  3e plus rapide des 13 premiers (2,4 s ; Rust 3,8, C 5,1, C++ 10,6) ; l'horloge, environ 33 000 appels système par
  répétition de K8 (3 ms sur 1,9 s), ne pèse rien ; Odin n'a pas eu de relecture experte.
* **Version suivante** : la correction de `@(fast_math)` (PR #7068, fusionnée le 7 octobre) sera dans dev-2026-11 ; la
  règle de la dernière version l'exclut à juste titre.
* **Rejeu de l'auteur** : C2 = 1, 73,5 ; plus Q1 au niveau de Zig et C3 (hypothèse), 74,2, 2e ; C2 et `@(fast_math)`
  réparé, 75,2, 2e ; les trois, 76,0, 2e ; C reste 1er partout. `#soa` pèse environ 1 point sur 100.

## 2. Vérifications (faites avant le plan)

Machine 13 (`results/hw/machine13/`). Chaîne : Odin dev-2026-10 (commit `84bc3fc`, la version mesurée, sources
complètes dans `/opt/src/odin`). Preuves : `tools/odin_check/collect.sh` et `tools/odin_check/data_facts.py` →
`results/odin_check/*.txt` (sondes dans `tools/odin_check/probes/`). Je n'ai consulté ni le site ni master.

* **Rejeu** : exact, dans l'état publié actuel (après les errata de C3). 72,6 points, 3e, devant C++ dans 44 %, devant
  Zig dans 55 % ; avec C2 = 1 en v2 : 73,5 points, rang espéré 3,63 contre 3,61 pour C++, devant Zig dans 59 %.
* **`@(fast_math)`** (`fast_math.txt`) : **exact**. `OdinFastMath_Allow_Reassoc` vaut 0 (`src/types.cpp`) et
  `llvm_backend_opt.cpp` le teste comme un masque : jamais posé. Aucune option globale de mathématiques rapides
  (`odin build -help`). C4 reste 0.
* **Allocateur** (`allocator.txt`) : **exact**. `heap_allocator_proc` demande `alignement − 1 + 8 + taille` octets, soit
  39 pour un nœud de 24 : glibc rend un bloc de 48 (32 pour 24 octets demandés directement, sonde `usable.c`) ; mémoire
  remise à zéro par `calloc` ; `t_build` appelle `mem_alloc_bytes`, qui appelle l'allocateur par un appel indirect.
* **Horloge** (`clock.txt`) : **exact**. `time.tick_now` passe par `syscall(SYS_clock_gettime)`, sans vDSO.
* **C2** (`c2.txt`) : **exact, erratum**. Le juge notait Odin C2 = 1 sous la règle A (ma règle v2) et 0,5 sous la règle
  B, en citant à la fois la couverture partielle de `core:simd/x86` et l'import des intrinsèques de LLVM ; ma
  correction du 30 octobre n'a retenu que la première et a baissé les deux règles. Le mécanisme existe et sert la
  bibliothèque livrée : `foreign _` et `@(link_name="llvm.…")`, `#const` pour les immédiats, **554** liaisons actives
  dans `core` et `base` (246 dans `core:simd/x86`, qui est lui-même écrit ainsi, 77 dans `core:sys/llvm`) ; le chiffre
  de 309 de la remarque compte autrement. La sonde `c2.odin` émet `vpconflictd` et `vpternlogd` (immédiat), absentes
  de `core:simd/x86`. La règle v2 donne 1 aux « builtins importés par le mécanisme d'import d'intrinsèques du
  langage » ; Julia (`llvmcall`) et Mojo (`llvm_intrinsic`) ont 1 en v2. **Erratum : C2 = 1 en règle v2** ; la
  règle v1 reste 0,5 (comme Julia et Mojo).
* **Isolement des noyaux** (`inlining.txt`) : **erreur de mon banc, plus large que la remarque**. Les 14 noyaux du banc
  C sont `noinline` ; dans le binaire de la campagne d'Odin, 10 d'entre eux sont inlinés dans leur boucle de mesure
  (K1 naturel, aos et soa, K2, K4 naturel et sans branchement, K5 naturel et optimisé, Q6 optimisé, K9 naturel). La
  seule annotation du banc, `@(optimization_mode="favor_size")` sur K1 aos, ne l'empêche pas : son commentaire est faux.
  C'est l'écart à la convention que la règle commune nomme (« des noyaux isolés de la boucle de mesure »), corrigé pour
  Fortran. La remarque ne l'a vu que pour K1 aos. **Correction : `odin_fix`**, les 14 noyaux en `#force_no_inline`
  (aucun autre changement) ; `nm` montre les 14 noyaux comme fonctions.
* **Q1 tuned** (`q1.txt`, `data_facts.txt`) : **faits exacts**, 46,1 ms (C 32,1, Zig 34,6, C3 33,5), 20,5 ms à quatre
  threads (C 13,4, Zig 14,7, C3 12,4) ; `reduce_add_pairs(m & 1)` pour chaque groupe ; aucun `popcnt` dans la fonction,
  39 permutations. **Mais pas une erreur au sens de la règle** : l'algorithme est celui de la référence C (une passe de
  16 lignes, masques par groupe), et c'est ce que la convention fixée pour D demandait ; le comptage varie d'une
  implémentation à l'autre (popcount du masque en C, Zig, Rust, C++ et C# ; somme d'un vecteur en C3 et Mojo ; masque
  accumulé en vecteur en D) ; et le code n'annonce pas de popcount. Le Q1 de D s'écartait de l'algorithme de sa classe,
  pas d'une primitive. Le correctif proposé (`card(simd.extract_msbs(m))`, qui existe dans dev-2026-10) est une
  meilleure forme : sensibilité.
* **Niveaux d'optimisation** (`optlevels.txt`) : **exact**. `-o:speed` = `default<O2>`, `-o:aggressive` = `default<O3>`
  et génération de code agressive, sans autre effet. Option nouvelle : sensibilité.
* **README** (`data_facts.txt`) : **exact**. K7 naturel d'Odin 2,42 s, 4,9 fois sa table plate ; toutes les tables
  standard des 13 premiers sont 3,4 à 22 fois plus lentes que la leur ; Odin est 3e (Zig 1,66, Nim 2,10 ; Rust 3,77,
  C 5,11, C++ 10,64). K8 naturel 1,88 s, 11e des 13 (C 0,97). L'horloge : deux lectures par requête, 32 768 par
  répétition de K8. Odin n'a eu ni relecture de son implémentation ni remarque avant celle-ci (le juge à l'aveugle a
  noté sa grille).
* **`#soa`** : une case de la catégorie A (25 % du contrôle, huit cases), soit 0,35 × 0,25 / 8 = 1,1 point : exact.
* **dev-2026-11** : non vérifié (master non consulté) et hors règle de toute façon (dernière version publiée au moment
  des mesures) ; calculé en information seulement (H-fm).

## 3. Plan (poussé avant les mesures)

### 3.1 Règle commune

> « Les errata de faits (la grille) et les erreurs de mon implémentation entrent dans le classement publié ; une
> optimisation nouvelle reste une analyse de sensibilité. Est une erreur : un code qui ne fait pas ce qu'il annonce
> (Ada) ou qui s'écarte d'une convention que les autres implémentations suivent (ici, des noyaux isolés de la boucle de
> mesure). Une meilleure forme ou une meilleure disposition, même plus proche de ce que fait C, est une optimisation
> nouvelle ; de même pour les options réservées aux noyaux tuned appliquées au code naturel. » (`docs/FORTRAN.md`, 3.1)

### 3.2 Ce qui entre dans le classement publié

* **Erratum** : Odin C2 = 1 en règle v2 (surcharge dans `analysis/capabilities_v2.py`), texte de C2 corrigé.
* **Correction du banc** : rapports `odin_fix` / `odin_ref` sur les 14 clés dont le noyau était inliné (K1 naturel,
  mélangé, aos et soa ; K2 aux trois tailles ; K4 naturel et sans branchement ; K5 naturel et optimisé ; Q6 optimisé
  et mt ; K9 naturel), reportés sur les données principales et inscrits dans `results/transfers.json`. Règle du pont
  de `analysis/transfer_check.py` (pont par le C du même hôte si transfert et pont diffèrent de plus de 25 %), sauf
  pour K9 naturel et K1 aos, par transfert seul : le pont s'est trompé entre Cascade Lake et Emerald Rapids sur ces
  noyaux pour D, Chapel et C3 (exception fixée d'avance). Les 13 autres clés servent de témoins (rapports attendus
  proches de 1).
* **README** : tableau, ordre, paragraphe d'Odin (SIMD, table `map`, horloge, allocateur), errata, langages relus.

### 3.3 Sensibilités (hors classement publié)

Toutes partent du classement publié avec 3.2.

* **S-Q1** : Q1 tuned et mt × `odin_q1` / `odin_fix` (règle du pont, témoin C sur les deux clés).
* **S-agg** : les 27 clés × `odin_agg` / `odin_fix` (transfert seul).
* **S-Q1+agg** : les deux (produit des rapports sur Q1).
* **Information, hors règle** : H-fm, C4 = 1 sous les deux règles (un `@(fast_math)` qui marcherait par procédure,
  comme `@setFloatMode` de Zig ; version non publiée) ; H-tout, H-fm avec S-Q1+agg.
* Chaque fois : score, piliers, rang espéré, place, part des variantes où Odin devance C++ et Zig.

### 3.4 Mesures (`tools/measure_odin.py`, machine 13)

* `odin_ref`, `odin_fix` et `odin_agg` : les 27 mesures d'Odin du score ; `odin_q1` : Q1 tuned et mt ; `c` (binaire de
  la campagne) : les 14 clés corrigées et Q1 tuned et mt, témoin des ponts. 99 cellules, 7 processus chacune en 7
  passes, ordre tiré au hasard dans chaque passe (graine 20261901), répétitions de `results/calib.json`, échauffements
  des données principales (2 pour K5, 1 sinon), règle de vol du pilote. Sommes de contrôle validées avant la campagne
  (`odin_ref` est identique au binaire de la campagne). Rien d'autre ne tourne pendant les mesures.

### 3.5 Analyse (`analysis/odin_check.py`)

* Rapports appariés (moyenne géométrique des médianes de processus, intervalle par bootstrap). Scénarios (analyse v3
  rejouée, mêmes tirages) : Avant (doit reproduire le publié actuel), P-C2, P-fix, Publié (les deux), Publié-T
  (transfert seul partout, information), S-Q1, S-agg, S-Q1+agg, H-fm, H-tout.
* Puis classement publié régénéré et sorties recalculées dans l'état actuel (comme pour C3).
* Sorties : `results/odin_check.json`, `results/report_odin.md`.
