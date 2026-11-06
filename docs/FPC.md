# Ajout de FreePascal : un 23e langage, mesuré sur la machine 25 et relié aux données publiées par le C

L'auteur de l'étude m'a demandé le 6 novembre d'ajouter FreePascal au banc. Ce document décrit la chaîne et les choix
d'implémentation, avec les faits relevés en écrivant le code (section 2). Il fixe le plan avant toute mesure de
campagne (section 3), puis donne les résultats (section 4). Comme pour Swift, je n'ai consulté aucune page web pour les
faits. Ils viennent de la chaîne installée (Free Pascal 3.2.2, ses unités, son `fpc.cfg`, l'aide de `fpc -h`), de
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
