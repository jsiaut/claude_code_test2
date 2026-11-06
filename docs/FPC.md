# Ajout de FreePascal : un 23e langage, mesuré sur la machine 25 et relié aux données publiées par le C

L'auteur de l'étude m'a demandé le 6 novembre d'ajouter FreePascal au banc. Ce document décrit la chaîne et les choix
d'implémentation, avec les faits relevés en écrivant le code (section 2). Il fixe le plan avant toute mesure de
campagne (section 3), puis donne les résultats (section 4) ; la section 5 traite la remarque d'un relecteur. Comme pour
Swift, je n'ai consulté aucune page web pour les faits. Ils viennent de la chaîne installée (Free Pascal 3.2.2, ses unités, son `fpc.cfg`, l'aide de `fpc -h`), de
sondes, du code machine produit et d'essais sur la machine 25. Seuls l'archive de la chaîne et la liste des versions
(index de distribution de freepascal.org, fil des fichiers du projet sur SourceForge) ont été téléchargés.

## 1. La demande

« Ajoute le langage FreePascal au benchmark » : implémenter les dix noyaux de `docs/SPEC.md`, noter la grille de
capacités, mesurer et ranger FreePascal dans le classement publié avec la même méthode que les 22 autres langages. Une
contrainte pratique pèse sur le plan : les données publiées viennent de plusieurs hôtes (machine 1, Cascade Lake, pour
la plupart des noyaux ; machines 3, 11 et 16, Emerald Rapids, pour K5, les latences de K8 et K9). Seule la machine 25
(Emerald Rapids, du même modèle que les machines 3, 11, 16 et 24) est disponible aujourd'hui. Contrairement à Swift,
mesuré d'abord sur un Cascade Lake, les clés de la machine 1 seront donc reliées d'un modèle à l'autre (3.2).

## 2. Chaîne, implémentation et faits relevés (avant le plan)

### 2.1 Chaîne

* **Free Pascal 3.2.2** (compilateur daté du 16 mai 2021), la dernière version publiée : l'index de distribution de
  freepascal.org et le fil des fichiers de SourceForge n'en listent pas de plus récente (la branche de développement
  3.3.1 n'est pas une version publiée, je ne l'utilise pas). Archive `fpc-3.2.2.x86_64-linux.tar` de 86 978 560 octets,
  SHA-256 `5adac308…1e83`, identique sur les deux canaux ; installée dans `/opt/fpc` par son `install.sh`, configuration
  `/opt/fpc/etc/fpc.cfg` produite par `samplecfg`. Les autres chaînes ont été fixées le 28 octobre ; FreePascal, ajouté
  le 6 novembre, prend la dernière version publiée à cette date, comme Swift le 5.
* **Générateur de code** propre à FPC (ni LLVM ni GCC). Cibles connues de la 3.2.2 : jusqu'à `COREAVX2` pour le jeu
  d'instructions et `AVX2` pour la FPU (`fpc -ic`, `fpc -if`) ; pas d'AVX-512, même dans l'assembleur en ligne.
* **Mode release** : aucun outil de construction n'en impose un. Le `fpc.cfg` livré en définit un (`-dRELEASE` :
  `-O2 -Xs`) ; `fpc -h` décrit `-O3` comme « -O2 + optimisations lentes » et `-O4` comme « -O3 + optimisations qui
  peuvent avoir des effets de bord inattendus » (vérifié : `-O4` réordonne les champs des classes et contracte les
  réductions en FMA, 2.4). Les vérifications de bornes et de débordement sont désactivées par défaut (`{$R-}`, `{$Q-}`).
* **Banc** : `fpc -O3 -CpCOREAVX2 -OpCOREAVX2 -CfAVX2 -Sv` (`bench/fpc/build.sh`) : le plus haut niveau sûr, comme
  `-O3` pour C, avec la cible la plus haute que connaît FPC, comme `-march=native` ailleurs. `-Sv` (« Support vector
  processing », option documentée de `fpc -h`) ne sert qu'à l'unité `msvec` (2.4, point 2). Le binaire est dépouillé de
  ses symboles, comme le veut le `fpc.cfg` livré hors du mode `DEBUG`.
* **Bibliothèques** : la RTL (System, SysUtils, BaseUnix, Unix, Linux, Syscall, cthreads) et `rtl-generics`
  (Generics.Collections), livrées avec la chaîne. Aucun paquet de Lazarus (comme `mtprocs`) : ce sont des dépendances
  tierces au sens de la règle.

### 2.2 Implémentation (`bench/fpc/ms.pas`, `bench/fpc/msvec.pas`)

Un seul binaire, comme en C et en Swift. Le code naturel suit les réglages par défaut ; le code optimisé passe par des
pointeurs typés (`{$pointermath on}`), des boucles déroulées à plusieurs accumulateurs, les intrinsèques `FMASingle`
et `Prefetch` du System et, pour K1 `soa` et K5, le traitement vectoriel de `-Sv`. L'assembleur en ligne, que FPC
permet, est exclu par la règle.

| Noyau | Naturel | Optimisé |
|---|---|---|
| K1 | `record` de 16 `Single` (64 o) dans un `array of`, boucle indicée | `aos` : copie alignée sur 64 o, 8 accumulateurs f64, `FMASingle` ; `soa` : 16 tableaux alignés, vecteurs `-Sv` de 4 `Single`, 4 accumulateurs f64 (un par voie) |
| K2 | — | chasse sur `PLongWord` |
| K3 | — | `InterLockedIncrement64` (procédure de la RTL : `lock xadd`) ou accès ordinaire par pointeur (`add` en mémoire : FPC n'a ni atomique relâché ni `volatile`) ; 4 `BeginThread` par répétition |
| K4 | `if v[i] >= 128` sur un `array of Byte` | `s += QWord(v) * (v shr 7)` sur `PByte` |
| K5 | boucle indicée sur `array of Single` | vecteurs `-Sv` : 8 accumulateurs de 4 voies, réduction en arbre |
| K6 | colonnes en tableaux dynamiques, Q1 dans un `array[0..5] of record` | Q6 : prédicat en masques arithmétiques de 64 bits ; Q1 : deux tables d'accumulateurs entrelacées, 7e groupe fictif pour les lignes filtrées, pointeur de ligne ; colonnes passées en paramètres ; `mt` : 4 fils |
| K7 | `TDictionary<LongWord, TAgg>` : `TryGetValue` puis `AddOrSetValue` (deux recherches par ligne ; pas d'accès en place) | adressage ouvert, hachage de Fibonacci, sondage linéaire, lots de 16 préchargés (`Prefetch` : `prefetchnta`), dans une fonction à part |
| K8 | `New` / `Dispose` d'un `record` pointé, construit en préordre, libéré dans le chrono | arène : nœuds compacts dans un tampon réutilisé, enfants par indice |
| K9 | `array[0..2047, 0..2047] of Double` alloué par `New`, harnais commun (grilles allouées une fois, réinitialisées hors chrono, échangées) | tableau plat aligné, pointeurs, indices `SizeInt`, fenêtre glissante sur la ligne du milieu, scalaire ; `mt` : 4 fils par itération |
| K10 | `TQueue<QWord>` de Generics.Collections + section critique + deux événements de la RTL (pas de file bloquante ni de variable de condition dans la RTL) | anneau SPSC, indices sur des lignes de 128 o, copies locales des indices distants, accès ordinaires (ordre TSO de x86-64 ; 2.4, point 8), attente active sans `pause` |

Harnais : horloge `CLOCK_MONOTONIC` (`Linux.clock_gettime`), comme le C ; fichiers lus par `FpOpen` / `FpRead` dans
des tableaux dynamiques (naturel) ou dans des tampons alignés sur 64 o (`GetMem` + `Align`) ; fils par `BeginThread` /
`WaitForThreadTerminate` (unité `cthreads`) ; somme de contrôle de K9 écrite par `Format('%.16e')`, soit les 16
chiffres significatifs du `%.15e` du C, avec l'exposant à la manière de FPC (`E+006`).

Copies (validées) : `bench/fpc_exp` (même source avec `-dEXP` : K7 `natural_cls`, valeurs de classe et une seule
recherche par ligne ; K8 `natural_cls`, nœuds de classe `TObject.Create` / `Free` ; K9 `natural_dyn`,
`array of array of Double`), `bench/fpc_scal` (`-dSCALAR`, sans `-Sv` : K1 `soa` et K5 `tuned` en scalaire, avec FMA),
`bench/fpc_o2` (mode `RELEASE` du `fpc.cfg` : `-O2 -Xs`). Le code `EXP` est hors du binaire publié (identique octet
pour octet avec et sans lui).

Validation par le pilote (`tools/driver.py --quick`) : les 41 cellules de `fpc` (toutes les tailles de K2 et
l'empreinte comprises), plus les 13 cellules des copies, sommes de contrôle toutes justes.

### 2.3 La grille (sonde `probes/fpc`, 33 cases notées, `results/probes/fpc.txt`)

| Cat. | Cases |
|---|---|
| A | A1 = 1 (`array of record` en ligne, 64 o) ; A2 = 1 (ordre déclaré, `{$PACKRECORDS C}`) ; A3 = 1 (`packed record`, `bitpacked record`) ; A4 = ½ (`GetMem` + `Align` à la main, `{$CODEALIGN VARMIN=64}` pour les seules variables globales ; pas d'alignement de type) ; A5 = 1 (`record` à variantes sans étiquette, `absolute`) ; A6 = 0 ; A7 = 1 ; A8 = 1 |
| B | B1 = 1 (pas de ramasse-miettes : comptage de références des chaînes et tableaux dynamiques) ; B2 = ½ (`SetMemoryManager` global, `NewInstance` par classe ; pas d'allocateur pour les conteneurs) ; B3 = 1 ; B4 = ½ (énumérateur d'un `TDictionary`, chaînes, exceptions) ; B5 = 1 |
| C | C1 = ½ (`-Sv`, expérimental, 128 bits, 2.4) ; C2 = 0 (aucune intrinsèque SSE/AVX) ; C3 mesurée ; C4 = 0 (`-OoFASTMATH` ne fait que contracter en FMA) ; C5 = 0 |
| D | D1 = 1 ; D2 = ½ (`InterLocked*` séquentiellement cohérents, sans ordre explicite ni chargement atomique) ; D3 = 0 ; D4 = ½ (appel système brut de l'unité `Syscall`, fil épinglé) ; D5 = ½ (barrières `lfence` / `sfence` / `mfence`, pas de `pause`) |
| E | E1 = 1 ; E2 = 1 (blocs `asm`, AVX2 ; AVX-512 inconnu de l'assembleur, octets bruts seulement) ; E3 = 0 (`Likely` inconnu) ; E4 = 1 (`Prefetch` du System) ; E5 = 0 ; E6 = 1 (`{$R+}` / `{$R-}` locaux) ; E7 = ½ (génériques spécialisés, pas d'évaluation de fonctions à la compilation) |
| F | F1 = ½ (tableau statique contigu, bornes fixées à la compilation) ; F2 = 0 ; F3 = 1 ; F4 = 1 (`Fpmmap` de BaseUnix) |

Règle v2 : D4 passe à 1 (liaison au système livrée avec la RTL, comme `syscall.RawSyscall` pour Go) ; les autres
demi-points sont partiels ou expérimentaux. Pilier C : 58,5 en règle v1 avec C3 = 0 (C3 est mesurée en campagne),
60,5 en règle v2 (sans C3), contre 68,1 pour Swift et 48,7 pour Go.

### 2.4 Faits relevés en écrivant le code (`tools/fpc_check/facts.sh`, `results/fpc_check/facts.txt`)

Les temps cités ici viennent d'essais de développement sur la machine 25 (quelques exécutions), pas de la campagne.

1. **Pas de vectorisation automatique** : K4 naturel garde un branchement par octet (`cmpb` puis `jnae`, aucun `cmov`),
   la forme sans branchement reste scalaire. Sur la machine 25 : K4 naturel 93 ms, contre 1,8 ms pour le C, qui
   vectorise ; forme sans branchement 17 ms.
2. **Traitement vectoriel `-Sv`** : les opérateurs arithmétiques sur des tableaux de 4 `Single` (ou de 2 `Double`) sont
   traduits en instructions SSE de 128 bits. Limites : un tableau de 8 `Single` provoque l'erreur interne 200610072 ;
   les opérandes mémoire sont en encodage SSE classique (`addps (%rdx),%xmm0`), qui exige l'alignement sur 16 octets
   (erreur d'exécution 216 avec des opérandes décalés de 4 octets) ; les vecteurs restent en mémoire entre deux
   opérations ; ni masque, ni comparaison, ni FMA, ni conversion. Sans expression vectorielle, `-Sv` ne change pas un
   octet du binaire. Gains : K5 optimisé 28 ms contre 48 ms en scalaire avec FMA (C : 5,2 ms, AVX-512) ; K1 `soa`
   3,6 ms contre 5,1 ms ; K9 en vecteurs de 2 `Double` est plus lent (34 à 37 ms contre 25 ms) et reste scalaire.
3. **Variables flottantes et appels** : dans K5 naturel, l'accumulateur reste sur la pile (`vaddss (%rsp)` puis
   `vmovss %xmm0,(%rsp)` à chaque élément) ; la procédure contient un appel, `fpc_dynarray_high`, que produit
   `High(a)`. Les procédures optimisées sans appel gardent leurs accumulateurs dans des registres. K5 naturel :
   0,38 s, contre 0,18 s pour le C.
4. **Allocation des registres** : chaque FMA scalaire de K5 passe par deux `vmovaps` (16 pour 8 FMA).
5. **Peu de factorisation** : FPC relit les champs d'un `record` passé en paramètre à chaque itération et recalcule les
   adresses à chaque accès. Q6 optimisé avec les colonnes dans un `record` : 35 ms, avec les colonnes en paramètres :
   29 ms ; Q1 à quatre tables et procédure imbriquée `inline` : 88 ms, plus lent que le naturel (73 ms), une table et
   un pointeur de ligne : 59 ms, deux tables : 54 ms (C : 27 ms, AVX-512) ; K7 optimisé dans une procédure qui a des
   variables gérées (tableaux dynamiques) : 0,32 s, dans une fonction à part à pointeurs : 0,17 s (C : 0,14 s). Les
   boucles chaudes du code optimisé sont donc écrites dans de petites procédures à pointeurs.
6. **`TDictionary`** : 30 ns par recherche même avec 16 clés (en cache), 63 ns avec 65 536 clés, 200 à 225 ns avec
   1 048 576, quelle que soit la distribution des clés ; le hachage seul coûte 7 ns. K7 naturel (deux recherches par
   ligne) : 4,1 à 4,9 s, contre 0,34 s pour le chaînage du C ; avec des valeurs de classe (une recherche) : 1,5 à
   1,9 s.
7. **Atomiques** : `InterLockedIncrement64` est une procédure de la RTL (appel, puis `lock xadd`), pas une
   intrinsèque ; l'écriture simple de K3 donne `addq $1,(%r12)` à chaque itération.
8. **Ordre mémoire** : `ReadBarrier`, `WriteBarrier` et `ReadWriteBarrier` sont des procédures de la RTL (`lfence`,
   `sfence`, `mfence`) ; il n'y a ni `volatile`, ni atomique à ordre explicite, ni `pause`. K10 optimisé repose donc
   sur l'ordre TSO de x86-64 : les boucles d'attente relisent l'indice distant à chaque tour, et FPC garde les accès
   dans l'ordre du source (vérifié dans le code produit). K10 est hors score.
9. **`-O4`** : il réordonne les champs des classes (instance de 32 à 24 octets ; les `record` ne bougent pas) et
   contracte la réduction en FMA ; `-OoFASTMATH` seul fait la même contraction, sans réassociation.
10. **K8 et K9 naturels** : `New` / `Dispose` (gestionnaire de mémoire de la RTL) : 1,07 s contre 0,68 s pour le
    `malloc` du C ; nœuds de classe : 2,2 s. K9 naturel : 37 ms en tableau statique, 39 à 49 ms en
    `array of array of Double`, 18,6 ms pour le C ; K9 optimisé : 28 ms (C : 18,4 ms).

## 3. Plan (poussé avant les mesures)

### 3.1 Ce qui entre dans le classement publié

* **FreePascal, 23e langage classé** (`RANKED`, en dernier) : ses temps reliés aux données publiées par le pont du C
  (3.2), sa grille (2.3, `analysis/capabilities.py`), sa vectorisation mesurée (C3, `tools/c3_measure.py fpc`) et son
  empreinte (`results/raw_post/fpc.jsonl`, étiquette `post_fp2`, puis `analysis/footprint.py`).
* **Les 22 autres langages** : leurs données ne changent pas. Leur score ne bouge que par FreePascal lui-même :
  références t* s'il est le plus rapide sur une mesure, rangs, étages.
* **Réplication (machine 3)** : FreePascal y entre par le même pont, avec le C natif d'Emerald Rapids. Ce n'est pas
  une réplication indépendante pour lui ; le rapport le dit.

### 3.2 Le pont par le C

Toutes les clés de FreePascal sont mesurées sur la machine 25. Pour chaque clé k du score (mesures de E et de D1,
K1 `natural_shuffled`, K2 tuned aux trois tailles de D4) : chaque processus de FreePascal est multiplié par
f(k) = G(C publié, k) / G(C machine 25, k), où G est la moyenne géométrique des médianes de processus. Le C mesuré sur
la machine 25 est la construction qui a produit les données publiées de chaque clé :
* `bench/c/ms` (`ff81685a…`, cible Cascade Lake) pour les clés de la machine 1 (K1 à K4, K6 à K8), pour K9 (machine 16)
  et pour les latences de K8 naturel (D3, machine 11 : chaque colonne [p50, p90, p99, p99,9, max] multipliée par le
  rapport des médianes du C, colonne par colonne) ;
* `bench/c_er/ms` (`ca4eeb97…`, construction native identique au binaire de la machine 3) pour K5 (machine 3) et pour
  la réplication (toutes les clés, machine 3).

FreePascal n'a qu'un binaire (la cible `COREAVX2` est la même sur les deux modèles). Les processus de FreePascal
gardent leur propre dispersion. Le pont est fait dans `analysis/analyze_v2.py` (`ADDED`, `ADDED_ER`), après toutes
les corrections du jeu publié, si bien que les sorties publiées, la réplication et les scripts d'état actuel voient
FreePascal de la même façon.

**Le pont entre modèles.** Pour les clés de la machine 1, le facteur traverse les modèles (Emerald Rapids vers
Cascade Lake). Il absorbe ce qui sépare les hôtes tel que le C le voit (la machine 25 tourne à 2,8 GHz effectifs,
contre 3,1 à 3,4 GHz pour la machine 24 ; latences, bande passante), mais pas ce qui toucherait FreePascal et le C
différemment, par exemple du code scalaire contre du code AVX-512 sur deux microarchitectures. Deux contrôles, fixés
ici : F-gcc (second témoin, compilé par un autre compilateur) et F-hôte (un seul facteur pour toutes ces clés), 3.5.

**Tirages isolés.** Les tirages du bootstrap et des latences de FreePascal viennent de leur propre générateur (graine
SEED + 2403). Celui de Swift garde SEED + 2402 : chaque langage ajouté a désormais son générateur, et la suite des
tirages de Swift ne change pas. Les résidus de FreePascal n'entrent pas dans les réservoirs des autres. Il est le
dernier de `RANKED`, donc ses bruits de jugement de la grille sont tirés après ceux des autres. Contrôle : le calcul
avec FreePascal retiré doit reproduire à l'identique le classement d'avant (R-E de `results/swift_remark.json`).

### 3.3 Copies

* `bench/fpc` : le banc publié.
* `bench/fpc_exp`, `bench/fpc_scal`, `bench/fpc_o2` : 2.2.
* `bench/c_gcc_cl` : le second témoin, la source C de `bench/c` compilée par GCC 16 en cible `cascadelake` ; identique
  octet pour octet au binaire des données publiées de `c_gcc` (`167a19fd…`, compilé sur la machine 2 :
  `results/hw/machine3/binaries.txt`), alors que `bench/c_gcc` contient la recompilation de la machine 3.

### 3.4 Mesures (`tools/measure_fpc.py`, machine 25)

132 cellules en 7 passes (924 processus) ; dans chaque passe, toutes les cellules dans un ordre tiré au hasard (graine
20263606) :
* `fpc` et `c` : les 31 cellules du classement et de K10 (K1 : 4 ; K2 tuned à 16 Kio, 256 Kio et 8 Mio ; K3 : 4 ;
  K4 : 3 ; K5 : 2 ; K6 : 6 ; K7 : 2 ; K8 : 2 ; K9 : 3 ; K10 : 2) ;
* `c_er` : les 29 cellules du score ;
* `c_gcc_cl` : les 24 cellules des clés de la machine 1 ;
* `fpc_exp` : K7, K8 et K9 natural, et `natural_cls`, `natural_cls`, `natural_dyn` ;
* `fpc_scal` : K1 `soa` et K5 `tuned` ;
* `fpc_o2` : les 9 cellules naturelles du score (K1 `natural` et `natural_shuffled`, K4, K5, K6 Q6 et Q1, K7, K8, K9).

Répétitions : celles de `results/calib.json` pour les trois C. Pour FreePascal, la règle du pilote (3 s divisées par le
temps d'une répétition, entre 3 et 10 ; 2 au-delà de 5 s), appliquée à une répétition de calibration faite au début et
écrite dans `results/calib.json`. Les copies prennent les répétitions de la cellule d'origine. Échauffement : 1 (code
compilé à l'avance) ; règle de vol du pilote. Puis l'empreinte (3 processus) et C3 (`tools/c3_measure.py fpc`). Rien
d'autre ne tourne. Sortie : `results/raw_fpc/`.

### 3.5 Scénarios (`analysis/fpc_check.py`, analyse globale de la v3 rejouée, mêmes tirages)

| Scénario | Contenu |
|---|---|
| Avant | le classement publié à 22 langages (R-E de `results/swift_remark.json`) ; le calcul avec FreePascal retiré doit le reproduire à l'identique |
| **F-E (publié)** | FreePascal ajouté : pont par le C (3.2), grille, empreinte, C3 mesurée |
| F-direct | information : les temps de la machine 25 sans pont pour les clés de la machine 1 (pont gardé pour K5, K9 et les latences, venus du même modèle) |
| F-hôte | F-E ; clés de la machine 1 multipliées par la médiane, sur ces clés, des facteurs f(k) du C (un facteur d'hôte au lieu d'un par clé) |
| F-gcc | F-E ; clés de la machine 1 reliées par le second témoin : G(`c_gcc` publié, k) / G(`c_gcc_cl` machine 25, k) |
| F-scal | F-E ; K1 `soa` et K5 `tuned` × r(`fpc_scal` / `fpc`) : le traitement vectoriel expérimental de `-Sv` n'est pas compté |
| F-O2 | F-E ; les 9 cellules naturelles × r(`fpc_o2` / `fpc`) : mode `RELEASE` du `fpc.cfg` livré |
| F-K7cls | F-E ; K7 naturel × r(`natural_cls` / `natural`, tous deux de `fpc_exp`) |
| F-K8cls | F-E ; K8 naturel (temps et latences) × r(`natural_cls` / `natural`, de `fpc_exp`) |
| F-K9dyn | F-E ; K9 naturel × r(`natural_dyn` / `natural`, de `fpc_exp`) |
| F-cases-bas | F-E ; A3 = ½ (champs de bits à disposition propre à FPC), E2 = ½ (assembleur sans AVX-512), E4 = ½ (`prefetchnta` seul, sans choix du niveau), F4 = ½ (liaison POSIX plutôt que RTL portable) |
| F-cases-haut | F-E ; A4 = 1 (`{$CODEALIGN}` + `Align`), B2 = 1 (gestionnaire de mémoire et `NewInstance`), C4 = ½ (contraction par `FASTMATH`), E7 = 1 (génériques spécialisés) |
| F-tout-bas, F-tout-haut | F-cases-bas avec F-scal, F-O2, F-K8cls et F-K9dyn ; F-cases-haut avec F-K7cls |

Les rapports des copies sont appliqués tels qu'ils sont mesurés, dans un sens ou dans l'autre (pas de min(1, r)) :
ce sont d'autres lectures de la règle, pas des améliorations. Rapports : moyenne géométrique des médianes de processus,
intervalle par bootstrap ; latences : médiane de toutes les répétitions, colonne par colonne. Pour chaque scénario :
score, piliers, rang espéré de FreePascal, ses voisins et les probabilités de précédence ; rangs espérés des 22 autres
et leurs écarts à « Avant ». Information : le rapport FreePascal / C de chaque cellule sur la machine 25, K10, les
facteurs du pont par clé avec les deux témoins. Sorties : `results/fpc_check.json`, `results/report_fpc.md` ; puis
régénération des sorties publiées (réplication comprise) et de l'état actuel.

### 3.6 Ce qui change ailleurs

`analysis/analyze.py` (`RANKED`), `analysis/analyze_v2.py` (pont, groupe de backend « natif, autre » avec Go et OCaml,
noms), `analysis/analyze_v3.py` (un générateur par langage ajouté, réplication), `analysis/capabilities.py` et
`capabilities_v2.py` (faits), `analysis/report.py` et `analysis/capabilities_md.py` (noms, ordre).
`analysis/nosimd_check.py` : variantes à vecteurs explicites de FreePascal classées V (K1 `soa`, K5 `tuned`) ; les
autres sont scalaires. Confrontation : FreePascal n'est pas dans l'étude « Banc », il sort des tests qui comparent à
elle, et c'est signalé. `tools/c3_measure.py` (liste, fait), graphiques. Texte : README (23 langages, tableau,
paragraphe de FreePascal), FINDINGS, METHODOLOGY (journal), `docs/NATURAL.md` (fait), CAPABILITIES (régénéré).

### 3.7 Ce que je ne fais pas

* Pas de mesure sur un Cascade Lake (aucun disponible) : le pont des clés de la machine 1 traverse les modèles ; F-gcc
  et F-hôte en donnent la sensibilité ; c'est écrit dans les limites.
* Pas d'assembleur en ligne dans le code optimisé (règle), pas de paquet de Lazarus, pas de branche de développement
  de FPC, pas de `-O4` (documenté comme pouvant avoir des effets de bord inattendus).
* K10 est mesuré (information) et reste hors score ; pas de sensibilité sur sa file.

## 4. Résultats (après les mesures)

Mesures (`tools/measure_fpc.py`, machine 25, 08:52:29 à 09:20:57) : 924 processus (132 cellules × 7 passes), aucune
somme de contrôle fausse ; 14 processus refaits pour vol de temps, un seul gardé au-dessus de 2 % (le C sur K3
`sw_padded`, 4,9 % après deux reprises, règle du pilote) ; vol médian nul. Empreinte de K1 : 64,0 octets par
particule, comme le C. C3 mesurée : 0 (boucles chaudes de K4 et de K9 naturels scalaires, 97 et 47 % des
échantillons). Contrôle : le scénario Avant (FreePascal retiré) reproduit à l'identique le classement d'avant (R-E de
`results/swift_remark.json`, écart 0). Sorties : `results/fpc_check.json`, `results/report_fpc.md`.

### 4.1 FreePascal face au C, sur le même hôte (machine 25)

Rapports FreePascal / C (moyennes géométriques des médianes de processus ; C de la construction des données publiées,
natif pour K5) :

| Groupe | Cellules (rapport) |
|---|---|
| Même code machine ou presque | K2 tuned 1,00 / 0,99 / 0,98 (16 Kio, 256 Kio, 8 Mio) ; K1 naturel 1,09 et mélangé 1,08 ; K1 `aos` 1,19 ; K3 `rmw_packed` 1,15, `sw_packed` 1,19, `sw_padded` 1,23 ; K7 tuned 1,17 ; K8 tuned 1,17 |
| Appel de la RTL | K3 `rmw_padded` 1,52 : sans contention, l'appel à `InterLockedIncrement64` se voit (338 contre 222 ms) |
| SIMD absent ou limité à 128 bits | K5 tuned 7,46 (vecteurs `-Sv` en mémoire contre AVX-512 ; 12,8 sans `-Sv`) ; K1 `soa` 1,46 ; Q6 tuned 1,73, Q1 tuned 2,59 ; K9 tuned 1,72 ; `mt` : Q6 2,01, Q1 2,77, K9 2,04 |
| Vectorisation automatique absente | K4 sans branchement 11,2, naturel trié 12,1, naturel non trié 54,4 (un branchement par octet, mal prédit une fois sur deux ; le C vectorise) |
| Code naturel | K5 2,07 (accumulateur sur la pile) ; Q6 2,54 (conditions évaluées en court-circuit) ; Q1 1,31 ; K9 2,41 ; K7 15,4 (`TDictionary`) ; K8 1,46 (gestionnaire de mémoire de la RTL ; latences p50 1,47, p99 1,36, p99,9 1,21, max 1,09) |
| K10 (hors score) | naturel 2,21 (`TQueue`, section critique, événements) ; optimisé 0,64 (attente active sans `pause`, plus rapide ici que le C, qui attend avec `pause`) |

### 4.2 Le pont et le classement publié (F-E)

Facteurs du pont (C publié / C machine 25) : 0,76 à 4,6 sur les clés de la machine 1, sauf K3 `sw_packed` (11,4) et
K7 naturel (17,6) ; la machine 1 était bien plus lente que la machine 25 sur le code lié à la mémoire et à
l'allocation (K2 à 8 Mio : 3,9 ; K1 `soa` : 3,1 ; K7 tuned : 3,1). Sur les clés venues du même modèle, ils sont proches
de 1 : K5 0,85 et 1,02, K9 1,02 à 1,10 ; latences de K8 naturel, colonne par colonne, 0,80 à 1,51. Le second témoin
(`c_gcc_cl`) donne des facteurs voisins sur la plupart des clés (K7 naturel 17,4, K1 `soa` 3,0), pas sur toutes (K4
0,95 à 1,29 contre 1,80 à 2,33 ; K1 naturel 1,67 contre 1,23 ; K8 naturel 1,82 contre 1,41).

**Classement publié (F-E)** : FreePascal **16e** sur 23, **47,44 points** [46,5–48,2], rang espéré 16,71, rang
plausible 15 à 19, 2e étage (avec C#, Go, Haskell et Java). Contrôle 60,5 (16e), plafond 36,3 [35,4–37,3] (19e : seuls
OCaml, JavaScript, Lua et Python sont plus bas), code par défaut 46,9 (12e). Le code par défaut tient à ce que donne la
mémoire gérée à la main (empreinte D2 1,0 ; queues de latence D3 0,66, au niveau de Rust et de Fortran ; hiérarchie
mémoire D4 0,98, la meilleure de l'étude, devant C, 0,97), pas à la vitesse du code naturel (D1 0,050, au niveau de
Haskell). Plafond par noyau : K1 0,64, K3 0,79,
K4 0,09, K5 0,13, K6 0,39, K7 0,86, K8 0,35, K9 0,43. C# (15e, 54,9 points) le devance dans 82 % des variantes ;
FreePascal devance Java (17e, 47,2) dans 53 %, Go dans 62 %, Haskell dans 86 %.

Les 22 autres gardent leurs scores (FreePascal devient la référence de K2 dans une partie des tirages : la borne haute
de l'intervalle de Zig passe de 74,0 à 73,9) ; ceux qu'il devance reculent d'un rang ; les rangs espérés de ceux qui le
précèdent bougent de 0,18 au plus (C#).

### 4.3 Sensibilités (plan 3.5)

| Scénario | Score | Contrôle | Plafond | Code par défaut | Rang espéré | Place | Rang à 90 % |
|---|---|---|---|---|---|---|---|
| **F-E (publié)** | 47,44 | 60,5 | 36,33 | 46,9 | 16,71 | 16e | 15–19 |
| F-direct (information) | 51,02 | 60,5 | 45,83 | 46,1 | 13,65 | 15e | 6–16 |
| F-hôte | 47,29 | 60,5 | 39,43 | 41,4 | 15,92 | 16e | 14–18 |
| F-gcc | 47,51 | 60,5 | 36,48 | 47,0 | 16,69 | 16e | 15–19 |
| F-scal | 45,89 | 60,5 | 32,46 | 46,9 | 17,05 | 18e | 15–19 |
| F-O2 | 47,45 | 60,5 | 36,33 | 47,0 | 16,71 | 16e | 15–19 |
| F-K7cls | 47,54 | 60,5 | 36,33 | 47,3 | 16,65 | 16e | 15–19 |
| F-K8cls | 46,30 | 60,5 | 36,33 | 42,4 | 16,83 | 16e | 15–19 |
| F-K9dyn | 47,45 | 60,5 | 36,33 | 47,0 | 16,71 | 16e | 15–19 |
| F-cases-bas | 45,96 | 56,3 | 36,33 | 46,9 | 16,98 | 17e | 15–19 |
| F-cases-haut | 49,81 | 67,3 | 36,33 | 46,9 | 16,30 | 16e | 14–19 |
| F-tout-bas | 43,28 | 56,3 | 32,46 | 42,4 | 17,41 | 18e | 15–19 |
| F-tout-haut | 49,91 | 67,3 | 36,33 | 47,3 | 16,24 | 16e | 14–19 |

* **Le pont entre modèles tient** : avec le second témoin (F-gcc), FreePascal a 47,51 points (+ 0,07) ; avec un seul
  facteur d'hôte (1,494, F-hôte), 47,29 points et un rang espéré de 15,92 (devant Java dans 74 % des variantes), le
  plafond monte et le code par défaut baisse. F-direct (15e) est biaisé : la machine 25 est plus rapide que la machine 1
  pour presque tous les codes.
* **Rapports des copies** (même hôte) : sans `-Sv`, K1 `soa` × 1,43 et K5 × 1,72 (F-scal : 18e) ; mode `RELEASE`
  (`-O2`) : 0,95 à 1,02 sur les neuf cellules naturelles, aucune différence nette ; K7 en valeurs de classe : 0,365
  (une recherche au lieu de deux) ; K8 en nœuds de classe : 2,16 (latences × 1,8 à 2,3) ; K9 en `array of array` :
  0,92 (les deux formes recalculent l'adresse des trois lignes à chaque point ; le tableau de tableaux relit trois
  pointeurs, le tableau statique refait trois décalages).
* FreePascal reste 16e dans neuf scénarios sur treize, 15e en F-direct (information, biaisé), 17e ou 18e dans les
  lectures défavorables (F-cases-bas, F-scal, F-tout-bas) ; il ne rattrape C# que dans F-direct.

### 4.4 Hors plan : K7 naturel et la table du C (F-K7tab, information)

Relié par le facteur de la table chaînée du C (17,6), K7 naturel de FreePascal vaut 78,4 s dans les données publiées,
derrière Python (28,3 s), devant le seul Haskell (88,7 s) ; sur la machine 25, il prend 4,45 s, 15,4 fois le C. Comme
pour Swift (R-K7), le facteur de la table chaînée, une allocation par entrée, est discutable pour `TDictionary`, une
table plate. Relié par celui de la table plate du C (K7 optimisé, 3,05), K7 naturel vaut 13,6 s : 47,62 points, rang
espéré 16,60, 16e. Ajouté après avoir vu les facteurs ; le classement garde la règle du plan.

### 4.5 Réplication (machine 3)

FreePascal entre dans la réplication par le pont du C natif (`c_er`) : 16e sur la machine 3 (45,2 points). Ce n'est pas
une réplication indépendante pour lui. L'accord entre machines et le test nul, calculés sur les 21 langages répliqués
indépendamment, ne changent pas ; étages [14, 5, 1, 3].

### 4.6 Écarts au plan

* F-K7tab, ajouté après avoir vu les facteurs du pont (4.4), comme R-K7 l'avait été pour Swift ; `analysis/fpc_check.py`
  a donc tourné deux fois, avec les mêmes graines : les scénarios du plan sont identiques d'une exécution à l'autre.
* Un processus gardé au-dessus de 2 % de vol de temps (le C sur K3 `sw_padded`, 4,9 %), selon la règle du pilote.
* Pendant la campagne, seule l'intégration à l'analyse a été écrite (pont, générateurs, `analysis/fpc_check.py`) ; rien
  n'a été exécuté hors de vérifications de syntaxe.

### 4.7 Bilan

FreePascal se classe **16e sur 23**, entre C# et Java, à côté des langages à ramasse-miettes alors qu'il compile en
natif et gère sa mémoire à la main. Son contrôle (60,5) est celui d'un langage système privé de SIMD : disposition des
données complète (records en ligne, `packed`, `bitpacked`, unions), pointeurs et assembleur en ligne, mais ni
intrinsèques, ni atomiques à ordre explicite, ni aide de ligne de cache. Son plafond (36,3, 19e) est celui d'un
compilateur scalaire : aucun vectoriseur, un traitement vectoriel expérimental limité à 128 bits, une cible qui
s'arrête à AVX2 sur une machine AVX-512, et un optimiseur qui garde des variables en mémoire et factorise peu. Son code
par défaut (46,9, 12e) profite de la mémoire gérée à la main (empreinte, queues de latence, hiérarchie mémoire) mais
pas de la vitesse du code naturel : la somme conditionnelle de K4 (54 fois le C) et `TDictionary` (15 fois le C) le
tirent vers le bas. Le rang résiste aux deux contrôles du pont entre modèles et à toutes les sensibilités du plan, à
deux places près.

## 5. Remarque sur FreePascal (6 novembre)

Un relecteur a revu l'ajout le jour même. Cette section fixe la vérification (5.2), les errata (5.3), les copies et
les mesures (5.4) et les scénarios (5.5) avant toute mesure de campagne ; les résultats suivront (5.8 et après).
Comme pour l'ajout, aucune page web : les faits viennent des chaînes installées depuis les archives officielles, de
leurs unités, du code machine produit et d'essais sur la machine 26 (`tools/fpc_remark/facts.sh`,
`results/fpc_remark/facts.txt`). Seuls les archives et les index de distribution (`downloads.freepascal.org`) ont été
téléchargés.

### 5.1 La remarque

« Oui sur le fond, avec des réserves » : la 16e place mesure honnêtement ce que donne Free Pascal 3.2.2 sans
assembleur. Le relecteur a installé la 3.2.2 officielle (même SHA-256), la 3.2.4-rc2 et l'instantané de main du
4 novembre (3.3.1-21612), régénéré les données (24 empreintes identiques), réécrit les noyaux avec les mêmes
algorithmes sans lancer le code du dépôt, avec un témoin C (clang 18), mesuré sur un Emerald Rapids (5 ou 6 processus
par cellule) et recalculé le score en estimations ponctuelles. Il confirme la version, ses rapports FreePascal / C
(K4 naturel 44 contre 54 ici, K5 naturel 2,05 contre 2,07, K5 optimisé 8,2 contre 7,5 à 8,1, K7 naturel 13 contre 15,
K8 1,35 et 1,13 contre 1,46 et 1,17, K9 2,6 et 2,2 contre 2,4 et 1,7, écarts qu'il attribue à clang 18) et les faits
relevés. Ce qu'il corrigerait :
1. **Grille** : C2 vaut ½ pour Zig, dont l'assembleur en ligne ne donne pas plus, et 0 pour FreePascal, dont
   l'assembleur couvre AVX2 ; aligner (sens Zig : + 0,9 point). E4 (`prefetchnta` seul) et F4 en v1 (Go a ½ pour
   `syscall.Mmap`) lui semblent un peu généreuses.
2. **Trois noyaux optimisés mieux écrits** : K8 en arène itérative (× 0,44), K5 en `-Sv` par pointeurs avancés par
   `Inc` (× 0,65), K4 par `s += v and -(v shr 7)` (× 0,66) ; ensemble + 3,4 points.
3. **README** : la « meilleure note de hiérarchie mémoire » (D4 0,98 contre 0,97 pour C, sur le même code) est du
   bruit ; K5 naturel écrit avec `Length(a) - 1`, tout aussi idiomatique, est 4 fois plus rapide.

Ce que le classement ne dit pas, selon lui : le compilateur est celui d'une branche créée en 2018 ; la branche main
apporte l'AVX-512 (assembleur et cibles), `record … end align 64`, `AtomicIncrement` et `Volatile`,
`TThread.SpinWait` avec `pause`, `TParallel.For`, la réduction de force, et contient environ 500 intrinsèques SSE
désactivées dans la RTL ; elle casse `-Sv` sur les tableaux simples (il faut `__m128`, avec un résultat faux en
`-CfSSE64`), ses vecteurs de 256 bits ne s'assemblent pas et `-CfX86-64-V4` produit du x87. Mesuré sous main : le
code naturel s'améliore (K5 × 4, Q6 × 1,8, `TDictionary` × 2,4), l'optimisé bouge de ± 10 %, avec deux reculs (K1
`soa` en `-Sv` 2,3 fois plus lent, K9 naturel 1,2 fois). Le générateur LLVM n'est pas mesuré. La règle « pas
d'assembleur » touche FreePascal plus que les autres : K5 en assembleur vaut 1,46 fois le C en AVX2 avec la 3.2.2 et
1,03 fois en AVX-512 sous main, contre 7 à 8 fois en `-Sv`. Enfin, FreePascal est le seul langage que personne n'a
relu. Sa table : publié 47,4 (16e) ; + C2 48,3 ; + 3 noyaux 50,8 ; les deux 51,7 ; main, même code 46,9 (17e) ; main
et grille de main (C 69,5) 50,0 (16e) ; main, meilleures formes et grille de main 55,2 (15e, 0,3 devant C#). Résumé :
classement pertinent à une ou deux places près, étage solide, ordre interne non ; publier une sensibilité « branche
main » comme pour Zig 0.18-dev, préciser que la branche stable date de 2018 et ajouter les trois noyaux mieux écrits
comme sensibilités.

### 5.2 Vérification (avant le plan)

**Chaînes.** Trois archives officielles, extraites a minima (compilateur, RTL, `rtl-objpas`, `rtl-generics`,
`rtl-extra`, `rtl-unicode`, `rtl-console`, `fcl-base`, `fcl-process`, `pthreads`, `vcl-compat`), puis effacées faute
de place, leurs sommes gardées ici :
* 3.2.2, celle du banc (`5adac308…`, `/opt/fpc`) ;
* 3.2.4-rc2 : `fpc-3.2.4-rc2.x86_64-linux.tar` (93 091 840 octets, SHA-256
  `63226d9b4002477e6a0ba2b62474fb6a62e8bc58ea759d61a55c3263d1988463`) de `fpc/beta/3.2.4-rc2/x86_64-linux/`, dans
  `/opt/fpc-324rc2`. L'index bêta date le répertoire 3.2.4-rc2 du 2026-09-06 (celui de la 3.2.4-rc1 du 2025-02-02) ; les
  fichiers x86_64-linux sont du 2026-08-17 et le compilateur se nomme lui-même « 3.2.4-rc1 [2026/08/16] » (`-iVDW`) ;
* main : `fpc-3.3.1.x86_64-linux.tar.gz` (100 572 845 octets, SHA-256
  `901aca0e410fb2cc41becf7bb20d027efcccc424b20c3670345ed4fb173db569`) de `fpc/snapshot/trunk/x86_64-linux/`,
  « 3.3.1-21612-gc58603b8dd » du 2026/11/04, la construction du relecteur, dans `/opt/fpc-main`.

**Machine 26.** La VM a redémarré à 10:58 sur un nouvel hôte Emerald Rapids du même modèle (207, 4 vCPU) :
2,76 à 2,84 GHz effectifs ; latence 18 ns à 2 Mio, 36 ns à 4 Mio, 138 ns à 32 Mio ; DRAM 14,8 à 15,2 Go/s
(`results/hw/machine26/`), comme la machine 25 ; les 24 fichiers d'entrée correspondent à `env/msdata.sha256`.

| Affirmation | Constat |
|---|---|
| 3.2.2, dernière version stable ; 3.2.4-rc2 en bêta depuis septembre 2026 ; mêmes cibles | **Exact** (index bêta ; listes `-ic`, `-if`, `-io` identiques). Le binaire x86_64-linux de la rc2 se nomme 3.2.4-rc1. |
| rc2 : mêmes temps (0,95 à 1,07) | **Pas pour K7 naturel** : les recherches de `TDictionary` sont 1,6 à 3,6 fois plus rapides avec la rc2 (17,7 contre 28,7 ns en cache, 56 contre 200 ns sur 1 M de clés, `dict_lookup`) ; essai rapide de K7 naturel : 1,84 s contre 4,26 s. Les autres cellules de l'essai rapide sont proches. Mesuré en campagne (R-rc2). |
| Branche 3.2 créée en août 2018 | Non vérifiable sans page web (listes fpc-devel). Ce qui se vérifie : 3.2.0-rc1 dans l'index bêta au 2020-03-29, compilateur 3.2.2 daté du 2021/05/16. |
| Faits de la 3.2.2 (zmm inconnu, `-Sv` à 4 `Single`, aucune intrinsèque SIMD, `Prefetch` en `prefetchnta`, atomiques et barrières en procédures de la RTL, ni `pause`, K4 un saut par octet, `High(a)` appelle `fpc_dynarray_high`) | **Exacts** (2.4). `TThread.SpinWait` : boucle qui incrémente un compteur global, sans `pause`, en 3.2.2 comme en rc2 ; avec `pause` dans main. |
| main : AVX-512 dans l'assembleur et les cibles | **Exact** : zmm assemblé (refusé par la 3.2.2 et la rc2) ; `-Cp` X86-64-V4, SKYLAKE-X, ICELAKE-SERVER, ZEN4, ZEN5 ; `-Cf` AVX512F, X86-64-V4. |
| main : `record … end align 64` | **En partie** : taille 64, décalage dans un enregistrement, variables globales et éléments de tableau alignés ; **pas sur la pile** (7 à 10 locaux sur 10 mal alignés, en `-O3` comme en `-O-`) **ni par `New`** (12 sur 16). |
| main : `AtomicIncrement` et `Volatile` | **Existent**, sans rien de neuf pour l'ordre mémoire : `AtomicIncrement` appelle `fpc_atomic_inc_64` de la RTL (`lock xadd`), aucune procédure atomique ne prend d'ordre ; `Volatile` est une lecture simple. |
| main : `TParallel.For` | **Exact** (`System.Threading`, paquet `vcl-compat`, absent de la 3.2.2 et de la rc2) : 64 tâches sur 8 fils. Le premier appel d'un processus passe parfois sur le seul fil appelant (1 280 ms, comme en série), les suivants sur 8 fils (240 ms). |
| main : réduction de force | STRENGTH figure dans les optimisations (`-io`, avec USELOADMODIFYSTORE, UNUSEDPARA, FORLOOP) ; effet non isolé. |
| main : environ 500 intrinsèques SSE désactivées | **Exact** : 518 identifiants `fpc_in_x86_*` dans `system`, dont 502 SSE, SSE2 ou MMX sans procédure déclarée ; l'unité `intrinsics` ne déclare que 15 procédures x86 (ports, segments, `cli`/`sti`, `pause`). |
| main : `-Sv` cassé sur les tableaux simples, `__m128` faux en `-CfSSE64`, 256 bits refusés, x87 en `-CfX86-64-V4` | **Exacts** : « Operator is not overloaded » sur la source du banc ; `__m128` : 5 533 au lieu de 21 840 en `-CfSSE64`, juste en `-CfAVX2` ; `__m256` : « vmulps xmmreg, ymmreg » refusé à l'assemblage ; `-CfX86-64-V4` : 6 instructions x87 et aucune AVX dans un produit scalaire. |
| main : naturel K5 × 4, Q6 × 1,8, `TDictionary` × 2,4 ; optimisé ± 10 % ; K1 `soa` 2,3 fois plus lent, K9 naturel 1,2 | Essais rapides (3 à 10 répétitions) : K5 0,386 → 0,097 s (main développe `High` en ligne : plus d'appel, l'accumulateur reste en registre) ; Q6 0,137 → 0,077 s ; K7 4,26 → 1,88 s (la rc2 fait autant) ; K1 `soa` 1,12 à 1,26 fois plus lent (pas 2,3) ; K9 naturel 1,29 à 1,39. Mesurés en campagne. |
| K5 en assembleur : 1,46 fois le C en AVX2, 1,03 en AVX-512 sous main, contre 7 à 8 en `-Sv` | **Exact à l'arrondi près** (essai, information) : 1,39 et 1,01 ; `-Sv` 8,0. |
| Trois noyaux mieux écrits : K8 × 0,44, K5 × 0,65, K4 × 0,66 | K8 en arène itérative 0,43 ; K5 par pointeurs 0,67 ; K4 par masque : 0,70 à 0,75 quand la valeur est lue une fois dans une variable locale, 1,03 écrit sur `v[i]` directement (FPC relit et recalcule), 0,48 à 0,68 par un pointeur (même code machine dans un programme d'essai et dans le banc : placement du code). |
| K5 naturel avec `Length(a) - 1` : 4 fois plus rapide | **Exact** : 0,386 → 0,094 s, sans appel, accumulateur en registre (section 10 de `results/fpc_remark/facts.txt`). Les autres boucles naturelles changent peu (0,9 à 1,1 dans l'essai rapide). |
| C2 incohérent avec Zig | **Exact** : FreePascal est le seul langage noté avec un assembleur en ligne (E2 > 0) et C2 = 0. |
| E4 généreux | **Exact** : `Prefetch` n'émet que `prefetchnta` (3.2.2, rc2, main), sans localité ni écriture ; les langages notés 1 ont ces choix (`_mm_prefetch`, `@prefetch`, `Sse.Prefetch0/1/2`, primops de GHC…). |
| F4 v1 généreux | **Exact** : `Fpmmap` est un appel système d'Unix (unité `BaseUnix`), comme `syscall.Mmap` de Go (½ en v1, 1 en v2) ; aucune projection de fichier portable dans les unités livrées (recherche dans celles de la 3.2.2). |
| README : D4 0,98 contre 0,97, du bruit | **Exact** : K2 a le même code machine que le C (rapports 1,00, 0,99, 0,98). |
| Seul langage pas relu | **Exact** jusqu'ici : sa grille a été notée après la relecture à l'aveugle et personne ne l'avait revue. |
| Générateur LLVM | Non mesuré ici non plus : l'instantané livre le générateur natif. |

### 5.3 Errata (classement publié)

Grille (`analysis/capabilities.py`, `analysis/capabilities_v2.py`), la règle des autres langages appliquée :
* **C2 : 0 → ½** : assembleur en ligne jusqu'à AVX2 et FMA, sans intrinsèques, comme Zig ;
* **E4 : 1 → ½** : `Prefetch` n'émet que `prefetchnta`, sans localité ni écriture ;
* **F4 : 1 → ½ en v1** (`Fpmmap` de `BaseUnix`, appel système propre à Unix, comme `syscall.Mmap` de Go), **1 en v2**
  (dérogation : unité livrée, comme Go).

Pilier capacités : 58,5 → 58,5 en v1 (C2 + 2,0, E4 − 0,7, F4 − 1,25) ; **60,5 → 62,3 en v2** (C2 + 2,5, E4 − 0,7).
Textes : la « meilleure note de hiérarchie mémoire » disparaît (README, 4.2, `docs/FINDINGS.md`) ; le README dira que
K5 naturel tient à `High(a)` (avec `Length(a) - 1`, 4 fois plus vite), que la branche stable est celle des 3.2.0
(2020) et 3.2.2 (2021) et ce que change la branche main. Les données publiées ne changent pas : le classement garde
les mesures de la machine 25, le code naturel et les noyaux optimisés publiés (5.7).

### 5.4 Copies et mesures (`tools/measure_fpc_rq.py`, machine 26)

**Source commun** `bench/fpc_rq/ms.pas` et `msvec.pas` : celui du banc, dont le code ne change que sous des
symboles : `LEN` (boucles naturelles bornées par `Length(x) - 1` : K1, K4, K5, K6 Q6 et Q1, K7), `MIEUX` (les trois
noyaux de la remarque : K4 `x := v[i]; s := s + (x and -(x shr 7))`, K5 en `-Sv` par pointeurs avancés par `Inc`, K8
en arène itérative, l'algorithme de `bench/c_k8it` ; plus la variante `k4 branchless_ptr`, le même masque parcouru par
un pointeur), `M128` (type `__m128` de main dans `msvec`, accès aux voies par `PSingle`), `ASM` et `ASM512`
(information, hors des règles du banc : K5 en assembleur en ligne, AVX2 + FMA et AVX-512, 8 accumulateurs). Sans
symbole, il redonne exactement le binaire publié (SHA-256 `b890f0c3…`, vérifié).

| Copie | Compilateur | Symboles | Cellules mesurées |
|---|---|---|---|
| `fpc` (publié) | 3.2.2 | — | les 29 du score |
| `fpc_rc2` | 3.2.4-rc2 | source de `bench/fpc` | les 29 du score |
| `fpc_main` | main 3.3.1-21612 | `M128` | les 29 du score |
| `fpc_len` | 3.2.2 | `LEN` | 8 : K1 `natural` et `natural_shuffled`, K4 `natural_unsorted` et `natural_sorted`, K5 `natural`, K6 `natural` Q6 et Q1, K7 `natural` |
| `fpc_mieux` | 3.2.2 | `MIEUX` | 4 : K4 `branchless_unsorted` et `branchless_ptr`, K5 `tuned`, K8 `tuned` |
| `fpc_main_mieux` | main | `M128`, `LEN`, `MIEUX` | les 12 de `fpc_len` et `fpc_mieux` |
| `fpc_main_scal` | main | `SCALAR` (sans `-Sv`) | K1 `soa`, K5 `tuned` |
| `fpc_asm`, `fpc_main_asm` | 3.2.2, main | `ASM` ; `M128`, `ASM512` | K5 `tuned` (information) |
| `c` (publié, Cascade Lake), `c_er` (natif) | clang 23 | — | témoins, information : K4 `natural_unsorted` et `branchless_unsorted`, K7 `natural`, K8 `natural` et `tuned`, K9 `natural` et `tuned` ; K5 `natural` et `tuned` (`c_er`) |

Options de `bench/fpc` pour toutes les copies (`-O3 -CpCOREAVX2 -OpCOREAVX2 -CfAVX2`, `-Sv` sauf `fpc_main_scal`) :
main garde la cible du banc, puisque `-CfX86-64-V4` donne du x87 et que ses vecteurs de 256 bits ne s'assemblent pas.
124 cellules × 7 passes = 868 processus, répétitions de `results/calib.json` (celles de `fpc` pour toutes les
constructions de FreePascal, `branchless_ptr` prenant celles de `branchless_unsorted`), échauffement 1, ordre tiré
au hasard dans chaque passe (graine 20261106 + 2600), règle de vol du pilote ; sortie `results/raw_fpc_rq/`,
étiquette `fpc_rq`. Les 124 cellules ont été validées une fois (sommes de contrôle justes). Pendant la campagne, seule
l'analyse (`analysis/fpc_remark.py`) et les textes s'écrivent, sans rien exécuter hors de vérifications de syntaxe.

### 5.5 Scénarios (`analysis/fpc_remark.py`, analyse globale de la v3 rejouée, mêmes tirages)

Rapports r(copie / `fpc`) de la machine 26 (moyennes géométriques des médianes de processus, intervalles par
bootstrap) appliqués aux données publiées de FreePascal (machine 25, reliée par le pont), cellule par cellule ; quand
une copie change K8 naturel (rc2, main), ses latences sont multipliées par le rapport, colonne par colonne. C3 et
empreinte inchangées (main n'a pas de vectoriseur : K5 naturel y reste scalaire ; disposition des records identique).

| Scénario | Définition |
|---|---|
| Avant | grille d'avant la remarque (C2 0, E4 1, F4 1) ; doit reproduire F-E de `results/fpc_check.json` à l'identique |
| R-C2 | Avant, C2 ½ (la première correction de la remarque, seule) |
| **R-E (publié)** | les trois errata (5.3) |
| R-len-K5 | R-E ; K5 `natural` × r(`fpc_len` / `fpc`) (la lecture de la remarque) |
| R-len | R-E ; les 8 cellules de `fpc_len` |
| R-mieux | R-E ; K4 `branchless_unsorted`, K5 `tuned`, K8 `tuned` × r(`fpc_mieux` / `fpc`) (formes de la remarque) |
| R-mieux-ptr | R-mieux, K4 par `branchless_ptr` |
| R-mieux-len | R-mieux et R-len |
| R-rem-3, R-rem-C2-3 | Avant et R-mieux (« + 3 noyaux » de la remarque) ; Avant, C2 ½ et R-mieux (« les deux ») |
| R-rc2 | R-E ; les 29 cellules × r(`fpc_rc2` / `fpc`) |
| R-main | R-E ; les 29 cellules × r(`fpc_main` / `fpc`) (« main, même code ») |
| R-main-grille | R-main, grille de main : R-E et C5 1 (`TParallel.For`), D5 1 (barrières et `pause`) ; A4 reste ½ (ni pile ni `New`), D2 ½ (aucun ordre explicite), C1 ½ (`__m128` seul, 128 bits) |
| R-main-mieux | R-E ; chaque cellule × le plus petit des rapports mesurés sous main (`fpc_main` ; `fpc_main_mieux` sur ses 12 cellules, K4 par la plus rapide de ses deux formes ; `fpc_main_scal` sur K1 `soa` et K5 `tuned`) : les « meilleures formes » de la remarque ; le minimum de rapports bruités tire un peu vers le bas, le rapport le dira |
| R-main-mieux-grille | R-main-mieux et grille de main (la lecture de la remarque à 55,2) |

Information : FreePascal / C sur la machine 26 (témoins), à côté de la machine 25 et des rapports de la remarque ; K5
en assembleur face au C natif ; rapports main / 3.2.2 et rc2 / 3.2.2 de chaque cellule. Avec les errata, le pilier
capacités de la grille de main vaut 64,0 en v1 et 68,8 en v2 (la remarque : 69,5, sans les errata E4 et F4).

### 5.6 Ce qui change ailleurs (après les mesures)

Errata dans `analysis/capabilities.py` et `analysis/capabilities_v2.py`, puis la chaîne publiée régénérée
(`analysis/analyze_v3.py`, graphiques, `analysis/capabilities_md.py`, figures du README, états actuels de la remarque
sur C, de la sensibilité sans SIMD et de la confrontation) ; README (tableau, paragraphe de FreePascal, branche stable
et branche main, D4, K5 naturel), `docs/FINDINGS.md`, journal de `docs/METHODOLOGY.md`, `docs/NOSIMD.md`,
`docs/CONFRONTATION.md`, `docs/CAPABILITIES.md`, `env/toolchains.txt`.

### 5.7 Ce que je ne fais pas

* Changer le code naturel : `High(a)` reste (règle de `docs/NATURAL.md`, fixée avant les mesures ; c'est la forme de
  la documentation pour un tableau dynamique) ; `Length(a) - 1` est une sensibilité. Ni les noyaux optimisés publiés :
  les formes mieux écrites sont des sensibilités, comme pour C, Lua, Java, Go et les autres.
* Classer la 3.2.4-rc2 ou main : le banc prend la dernière version publiée ; la rc2 est une bêta, main un instantané
  de développement ; ce sont des sensibilités, comme Zig 0.18-dev.
* Classer du code en assembleur (règle du banc) : K5 en assembleur reste une information.
* Mesurer le générateur LLVM (absent de l'instantané).
