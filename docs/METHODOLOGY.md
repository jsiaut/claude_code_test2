# Méthodologie (plan d'analyse pré-enregistré)

Rédigé le 2026-10-28, **avant** les mesures inter-langages. Seules les mesures de mise au point
de la référence C l'ont précédé. Toute modification ultérieure sera datée et justifiée dans
la section « Journal des écarts » en fin de document.

## 1. Construit mesuré

*Mechanical sympathy* (Jackie Stewart, puis Martin Thompson pour le logiciel)
désigne le fait d'écrire du logiciel qui travaille *avec* le matériel et non contre lui.
Thompson et Fowler 2026 (C. Sanders, « Principles of Mechanical Sympathy ») retiennent :
accès mémoire prévisibles, conscience des lignes de cache et du faux partage,
principe de l'écrivain unique, regroupement naturel (*natural batching*).
Sens large demandé : on y ajoute les principes du **Data-Oriented Design**
(Acton 2014, Fabian 2018, Kelley 2021 : SoA, données compactes, indices plutôt que
pointeurs, pas d'allocations cachées, traitement par lots), du **HPC** (roofline,
vectorisation SIMD, bande passante, tableaux multidimensionnels contigus,
parallélisme de données) et des **SGBD OLAP** (stockage colonnaire, exécution
vectorisée ou compilée, sélection sans branchement, tables de hachage plates,
parallélisme par morceaux).

**Définition opérationnelle.** Un langage incarne la mechanical sympathy dans la mesure où :
1. il **donne le contrôle** des aspects matériels de l'exécution : disposition des
   données, allocation, SIMD, modèle mémoire et parallélisme, génération de code ;
2. ce contrôle **atteint effectivement les limites matérielles** quand on l'exerce ;
3. le **code par défaut** va déjà dans le sens du matériel, et le modèle de coût est
   **transparent et prévisible** : pas de coût caché, pas de pause, pas d'indirection
   imposée.

## 2. Trois piliers

| Pilier | Ce qu'il mesure | Source des données |
|---|---|---|
| **C — Contrôle** | ce que le langage permet d'exprimer | matrice de capacités, vérifiée par des sondes compilées/exécutées et par la doc officielle |
| **E — Efficacité plafond** | ce que le meilleur code du langage atteint | noyaux K1, K3–K10, variantes optimisées |
| **D — Défaut et transparence** | ce que le code naturel donne ; prévisibilité ; visibilité du matériel | variantes `natural`, empreinte mémoire, latence de queue K8, courbe K2 |

Pondération principale : **C 35 %, E 40 %, D 25 %**.
Une analyse de sensibilité (section 7) montre que le classement ne dépend pas de ce choix.

## 3. Pilier C : matrice de capacités

Chaque capacité vaut 1 (présente, documentée et vérifiée), 0,5 (partielle :
expérimentale, non standard mais livrée avec la chaîne officielle, ou seulement via
une extension du compilateur) ou 0 (absente, ou seulement via une bibliothèque
tierce ou une FFI).
Pondération des catégories, avec des capacités équipondérées à l'intérieur :

* **A. Disposition des données (25 %)** : A1 agrégats valeurs stockés en ligne dans les
  tableaux ; A2 contrôle de l'ordre et de la taille des champs, disposition C,
  `offsetof` ; A3 disposition au bit près (packed, bitfields) ; A4 alignement
  explicite ≥ 64 o ; A5 unions et réinterprétation de bits ; A6 support SoA natif
  (langage ou bibliothèque standard) ; A7 tableaux de taille fixe en ligne dans les
  agrégats ; A8 types numériques étroits (u8, i16, f32…) comme types de stockage.
* **B. Gestion mémoire (20 %)** : B1 pas de GC traçant imposé ; B2 allocateurs
  personnalisés et arènes de premier ordre ; B3 allocation sur la pile ou en ligne
  d'agrégats et de tableaux ; B4 absence d'allocations cachées ; B5 accès à de la
  mémoire brute hors tas (pointeurs).
* **C. SIMD et vectorisation (20 %)** : C1 types vectoriels portables ;
  C2 intrinsèques spécifiques à la cible ; C3 vectorisation automatique des boucles
  simples (vérifiée sur le désassemblage de K4/K9 `natural`) ; C4 contrôle de la
  réassociation flottante ; C5 constructions de parallélisme de données sur plusieurs cœurs (boucles et réductions
  parallèles ; le SIMD relève de C1 à C4 ; précisé le 6 novembre, remarque sur BQN).
* **D. Concurrence et modèle mémoire (15 %)** : D1 threads parallèles en mémoire
  partagée ; D2 atomiques avec ordres mémoire explicites ; D3 aide « ligne de cache »
  (constante ou type de bourrage) ; D4 affinité CPU dans la bibliothèque standard ;
  D5 barrières et indication d'attente active (`pause`).
* **E. Contrôle de la génération de code (10 %)** : E1 compilation native avec code
  machine inspectable ; E2 assembleur en ligne ; E3 indications de branchement ;
  E4 préchargement explicite ; E5 garanties de non-aliasing ; E6 contrôle local des
  vérifications de bornes ; E7 calcul à la compilation et génériques sans coût
  (monomorphisation).
* **F. Spécifique HPC/OLAP (10 %)** : F1 tableaux multidimensionnels contigus à
  disposition définie ; F2 constructions de localité et de distribution (PGAS,
  NUMA) ; F3 entiers de largeur fixe signés et non signés à arithmétique modulaire ;
  F4 fichiers projetés en mémoire et réinterprétation sans copie.

## 4. Pilier E : efficacité plafond

Pour chaque mesure *m*, on prend le meilleur temps du langage L sur les variantes
autorisées, noté `t(L,m)` : médiane inter-processus des médianes intra-processus. On
prend aussi le meilleur temps observé tous langages confondus, noté `t*(m)`. Le score
est `s(L,m) = t*(m) / t(L,m)`, dans ]0, 1].

| Noyau | Mesures (variantes autorisées) |
|---|---|
| K1 | énergie : min(`aos`, `soa`) |
| K3 | min(`sw_padded`, `rmw_padded`) |
| K4 | min(`natural_unsorted`, `branchless_unsorted`) |
| K5 | min(`natural`, `tuned`) |
| K6 | q6 mono, q1 mono, q6 `mt`, q1 `mt` (moyenne géométrique des 4) |
| K7 | min(`natural`, `tuned`) |
| K8 | min(`natural`, `tuned`) (débit total) |
| K9 | mono min(`natural`, `tuned`), et `mt` (moyenne géométrique des 2) |
| K10 | min(`natural`, `tuned`) |

`E(L) = 100 × moyenne géométrique des 9 scores de noyau`. La moyenne géométrique est
la bonne moyenne pour des ratios normalisés (Fleming & Wallace 1986). Un noyau
impossible à paralléliser dans le langage (par exemple, pas de threads) est quand même
exécuté avec le mécanisme disponible (séquentiel, coroutines) et mesuré tel quel.

## 5. Pilier D : défaut, transparence, prévisibilité

* **D1 Efficacité du code naturel (50 %)** : comme E, mais avec les seules variantes
  `natural` (K1 `natural`, K4 `natural_unsorted`, K5, K6 q6/q1, K7, K8, K9, K10),
  normalisées par `t*(m)` du pilier E. On mesure ainsi la distance entre le code par
  défaut et l'optimum matériel observé. Moyenne géométrique.
* **D2 Coût de structure (15 %)** : moyenne géométrique de
  (a) `64 / octets_par_particule` (empreinte K1 `footprint`, plafonnée à 1) et
  (b) `t(natural) / t(natural_shuffled)` en K1 (plafonné à 1 : sensibilité à
  l'indirection).
* **D3 Prévisibilité (15 %)** : K8 `natural`, moyenne géométrique de
  `min_L(p99.9/p50) / (p99.9/p50)` et `min_L(max/p50) / (max/p50)`.
* **D4 Visibilité de la hiérarchie mémoire (20 %)** : K2, moyenne géométrique de
  `t_C(S)/t_L(S)` pour S = 16 Kio (L1), 256 Kio (L2) et 8 Mio, plafonnée à 1. Un
  langage à surcoût par itération écrase la courbe L1/L2/L3 : le programmeur ne
  « voit » plus la machine.

`D(L) = 100 × (0,5·D1 + 0,15·D2 + 0,15·D3 + 0,2·D4)`.

## 6. Protocole de mesure

* **Machine** : VM KVM/Firecracker, Xeon Cascade Lake 2,8 GHz, 4 vCPU, 16 Go, AVX-512.
  Le PMU n'est pas exposé : pas de compteurs matériels. Ils sont remplacés par
  (i) des micro-expériences maison (`tools/hwprobe.c`), (ii) l'inspection du code
  machine généré, (iii) une simulation de cache et de branches
  (Valgrind/cachegrind et DynamoRIO si disponibles), (iv) rusage (RSS, temps CPU,
  défauts de page, changements de contexte).
* **Chaînes de compilation** : dernières versions stables au 2026-10-28, installées
  depuis les sources ou binaires officiels, avec sommes SHA-256 ou signatures GPG
  vérifiées (`env/toolchains.md`).
  Option d'optimisation : la plus élevée documentée pour la machine cible
  (`-O3 -march=native` ou équivalent). Les JIT ciblent l'hôte automatiquement. Les
  variantes `natural` utilisent le mode « release » standard du langage, sans
  désactiver ses vérifications par défaut.
* **Exécution** : machine au repos (aucune compilation en arrière-plan), noyaux
  exécutés séquentiellement. P = 3 processus indépendants par (langage, noyau,
  variante), avec WARMUP = 1 répétition non mesurée (3 pour les langages à JIT), puis
  R = 3 à 10 répétitions (adaptatif : environ 3 s par processus). On ne fixe pas
  l'affinité CPU, pour laisser les threads auxiliaires des runtimes (JIT, GC) utiliser
  les autres cœurs, comme en production. En contrepartie, le temps CPU total est
  enregistré.
* **Bruit** : le *steal time* de l'hyperviseur est relevé pour chaque processus.
  Une exécution avec un steal > 2 % du temps mural est refaite. Un contrôle de
  fréquence (`hwprobe freq`) est lancé avant et après chaque campagne.
* **Validation** : chaque résultat est comparé aux sommes de contrôle attendues
  (`results/expected.json`). Elles sont établies par la référence C et
  contre-vérifiées par l'implémentation Python, indépendante. Une mesure dont le
  résultat est faux est exclue et signalée.
* **Statistiques** : estimateur = médiane. Intervalle de confiance à 95 % par
  bootstrap hiérarchique (rééchantillonnage des processus, puis des répétitions),
  selon Kalibera & Jones (ISMM 2013). On signale tout coefficient de variation > 5 %.

## 7. Score final et robustesse

`MS(L) = 0,35·C(L) + 0,40·E(L) + 0,25·D(L)` (sur 100).

Robustesse :
1. Classements séparés par pilier.
2. **Monte-Carlo sur les poids** : 10 000 tirages de (w_C, w_E, w_D) selon une loi de
   Dirichlet(1,1,1). On publie le rang médian et l'intervalle de rang [5 %, 95 %].
3. **Bootstrap des mesures** : propagation de l'incertitude des temps aux scores E et D.
4. Les écarts de rang non robustes (intervalles qui se chevauchent) sont présentés comme
   des égalités.

## 8. Règles d'implémentation

* Même algorithme, mêmes données, même résultat dans tous les langages (voir `SPEC.md`).
* `natural` : idiome documenté du langage (doc officielle ou tutoriel officiel),
  conteneur et type par défaut. Le choix est justifié dans `docs/NATURAL.md`.
* `tuned` : langage et bibliothèque standard uniquement, sans FFI vers du code natif écrit
  à côté, sans assembleur en ligne et sans paquet tiers.
* Implémentations alternatives mesurées à titre indicatif seulement : LuaJIT (dialecte
  5.1 + FFI) et Bun (JavaScriptCore). Le classement « Lua » et « JavaScript » se fait
  avec l'implémentation de référence de la version courante du langage (PUC-Lua 5.5,
  Node/V8).

## 9. Menaces à la validité (à compléter avec les résultats)

* Une seule machine, virtualisée, sans PMU, avec un L3 partagé avec d'autres locataires
  (bruit possible).
* Ma propre compétence varie d'un langage à l'autre. Mitigations : même algorithme,
  inspection systématique du code machine des noyaux, documentation officielle.
* Le choix des noyaux est fait *a priori* à partir de la littérature, chacun étant
  rattaché à un principe.
* Biais de mesure connus (Mytkowicz et al., ASPLOS 2009 : alignement, environnement) :
  ils sont atténués par plusieurs processus et signalés comme limite.
* Préchauffage des JIT (Barrett et al., OOPSLA 2017) : on vérifie la stabilité entre
  la première et la dernière répétition.

## Journal des écarts

* 2026-10-28, avant les mesures inter-langages : tolérance du checksum K9 portée de 1e-12 à
  1e-9 (relative). L'ordre de sommation du *checksum* (pas celui du stencil) diffère
  légitimement selon les langages : `sum()` de Python est compensée depuis 3.12, et
  certains langages somment par colonnes. Une erreur dans le stencil produit un écart de
  plusieurs ordres de grandeur supérieur.

* 2026-10-28, avant la campagne finale : **ordre d'exécution randomisé**. Au lieu de lancer les P = 3
  processus d'une même mesure à la suite, la campagne fait 3 passes. Chaque passe exécute un
  processus par mesure, dans un ordre de blocs (langage, noyau) tiré au hasard avec une graine fixe
  (`tools/campaign.py`). La dérive temporelle de la VM est ainsi répartie entre les langages au lieu
  d'être confondue avec l'un d'eux. Le nombre de répétitions est fixé par la passe 0
  (`results/calib.json`).
* Idem : la règle du *steal* (> 2 %) est appliquée en rapportant les ticks de vol de `/proc/stat`
  à la capacité totale (temps mural × 4 vCPU). Une mesure fautive est refaite deux fois au plus.
* Idem : **options globales**. Chapel compile le programme d'un seul bloc, avec des options
  globales. Il est donc construit en trois binaires : `natural` (options par défaut), `tuned`
  (vecteurs 512 bits autorisés) et `fm` (`--no-ieee-float`, réservé aux réductions flottantes que la
  spécification autorise à réassocier : K1 aos/soa et K5 tuned). Le stencil K9 garde ainsi son
  ordre d'évaluation imposé. Pour Fortran, les noyaux tuned sont compilés à part avec
  `-mprefer-vector-width=512`.
* Idem : l'annexe CPython sans GIL (`python_ft`) se limite aux noyaux multi-threads (K3, K6, K9, K10).
  Son code mono-thread est celui de `python`.
* Idem : **empreinte K1 (D2a)**. Dans la plupart des implémentations, la collection naturelle est
  construite à partir d'un tampon brut lu dans le fichier (64 o/particule), qui coexiste avec elle
  au moment du pic RSS. Le calcul prévu, `pic(footprint) - pic(footprint0)`, compterait donc ce
  tampon. Le calcul devient `pic(footprint) - pic(footprint_raw)`, où la nouvelle variante
  `footprint_raw` charge le tampon exactement comme le chemin naturel puis s'arrête. Les
  implémentations qui lisent le fichier directement dans la collection (C, Fortran, Ada) ont un
  `footprint_raw` vide. Limite connue : les déchets transitoires créés pendant la construction
  restent comptés pour les langages à GC.
* Idem, corrections hors section chronométrée : C3 trie les octets de K4 `natural_sorted` par
  comptage (le tri de la bibliothèque standard prenait 260 s) ; la référence C reçoit une barrière
  `KEEP` dans K5 (requise par gcc, sans effet sur le code de clang).
* 2026-10-28, pendant la campagne (après la passe 0) : **mesures sous la borne physique**. Haskell K3
  `sw_*` mesurait 0,1 ms pour 4 × 2²⁵ incréments, avec un résultat juste : LLVM avait fusionné les
  incréments, faits par des accès mémoire ordinaires. Ma version violait la spécification (accès
  « garanti visible et non élidable »). Elle est corrigée (`atomicReadIntArray#`/`atomicWriteIntArray#`)
  et K3 sera remesuré pour Haskell après la campagne, avec 3 processus à la suite, pour ne pas changer
  de binaire en cours de campagne. Pour l'avenir, l'analyse traite comme invalide toute mesure
  inférieure à 90 % de sa borne physique (`analysis/analyze.py`, `BOUNDS`, K3 compris). LuaJIT
  (annexe, non classé) garde le compteur en registre (`volatile` ignoré) ; son K3 est déclaré non
  conforme.
* Idem : **passe complémentaire pour les mesures instables**. Toute mesure dont le coefficient de
  variation entre ses processus dépasse 10 % reçoit 6 processus supplémentaires, exécutés en 6 tours
  d'ordre aléatoire (`tools/complement.py`). La règle est la même pour tous les langages. Motivation :
  K10 dépend de la paire de vCPU choisie par l'ordonnanceur (transferts de 120 à 210 ns), et le même
  binaire C variait de 11 à 147 ms d'une répétition à l'autre pendant la mise au point.
* 2026-10-28, 16:11 : **redémarrage de la VM pendant la passe 2** (après le bloc 146 sur 279). Après le
  redémarrage, le processeur est le même modèle, mais la hiérarchie mémoire mesurée a changé
  (`results/hw/after_restart/`). La latence à 4 Mio passe de 142 ns (DRAM) à 26 ns (cache). La bande
  passante DRAM augmente de 30 à 100 % et la latence DRAM baisse de 20 à 30 %. La fréquence et les
  latences L1/L2 sont identiques. Il s'agit très probablement d'un autre hôte physique. Pour ne pas
  mêler deux machines dans un même classement, **seules les mesures antérieures au redémarrage sont
  retenues** : passes 0 et 1 complètes, plus 146 blocs de la passe 2. Les mesures de C qui servent de
  référence n'avaient pas dérivé entre les passes avant le redémarrage (K2, K1 soa, K7, K3). Les
  mesures concernées ont donc P = 2 au lieu de 3, et le bootstrap en rend compte. La passe
  complémentaire prévue pour les mesures instables est **annulée**, pour la même raison.
  Ne dépendent pas de la vitesse de la machine et ont été faites après le redémarrage : sondes de
  capacités, mesure de vectorisation (C3, analyse du code machine) et empreinte K1 (octets). La
  remesure de K3 pour Haskell est faite après le redémarrage, en même temps qu'une remesure de K3
  pour C qui sert de pont ; elle n'est retenue que si C donne les mêmes temps qu'avant.
* 2026-10-28, vers 17:30 (pendant la mesure d'empreinte), **avant** la remesure de K3 (lancée à 17:33) : **règle d'acceptation du pont**, fixée avant de
  voir les données. Mesures de pont : les 4 variantes K3 de C, et `rmw_packed`/`rmw_padded` de
  Haskell (code que la correction ne touche pas). Pour chacune, ratio = médiane après redémarrage /
  médiane avant. Les valeurs Haskell `sw_*` d'après redémarrage sont retenues **telles quelles**
  (sans mise à l'échelle) si la moyenne géométrique des 6 ratios est dans [0,90 ; 1,10] et si aucun
  ratio ne sort de [0,80 ; 1,25]. Sinon, K3 de Haskell reste évalué sur `rmw_padded` seul, sa seule
  variante valide d'avant le redémarrage ; c'est la définition de E (meilleure variante admissible
  présente), au risque de sous-estimer Haskell.
* Idem : **variables d'environnement héritées**. L'outil qui lance les commandes exporte
  `BUN_OPTIONS=--smol` (mode mémoire réduite de Bun : ramasse-miettes plus fréquent),
  `JAVA_TOOL_OPTIONS` (propriétés réseau seulement, et désactivé par `bench/java/run`),
  `NODE_OPTIONS=--use-openssl-ca` (certificats TLS, sans effet sur le calcul) et
  `PYTHONUNBUFFERED=1` (quelques lignes de sortie par processus). Seul `--smol` peut changer une
  mesure : l'annexe Bun (`js_bun`, non classée) a donc été mesurée en mode `--smol` pendant toute la
  campagne. Son effet est quantifié après coup, sur la machine d'après redémarrage (section annexes).
* 2026-10-28, 17:40-18:06 : **empreinte K1 (D2a), deuxième écart : méthode en deux points**. La
  mesure par pic RSS (`pic(footprint) - pic(footprint_raw)`) donnait 0 octet par particule pour Rust,
  Zig, Odin, C3, D, Nim, Mojo et Julia, ce qui est physiquement impossible. Cause : leur chargement
  crée un tampon transitoire de 256 Mio (fichier lu, puis copié dans un tampon aligné). Le pic RSS
  est donc atteint pendant le chargement et masque la collection construite ensuite. La variante
  `footprint` lit désormais la mémoire M **dans le processus**, en deux points : P1 (tampon brut
  chargé ; pour C, Fortran et Ada, qui lisent le fichier directement dans la collection, avant la
  lecture) et P2 (collection construite, tampon brut toujours vivant). M = octets vivants comptés par
  le runtime après un GC complet pour les langages à ramasse-miettes traçant (Java, C#, Go,
  JavaScript, Julia, Haskell, OCaml, D, Lua), car leur tas garde la mémoire libérée et la réutilise ;
  RSS courant (`/proc/self/statm`) pour les autres. Le RSS est relevé partout comme contrôle.
  Résultat = (M(P2) - M(P1)) / 4 194 304, médiane de 3 processus (`tools/patch_footprint_mem.py`,
  `analysis/footprint.py`). Trois défauts trouvés en route et corrigés : la lecture « fichier
  entier » de Zig, Nim et D rend une chaîne vide sous `/proc` (taille annoncée nulle). Deux
  allocateurs faussent la mesure, avec un mécanisme vérifié : Nim (sa classe de taille arrondit
  256 Mio à 264 Mio, jamais touchés au-delà de 256 ; `getOccupiedMem` compte 66 o) et Mojo (son
  allocateur, qui réserve des zones de 1 Gio et libère par `madvise`, réutilise environ 24 Mo du
  tampon de chargement : le RSS ne voit que 58 o, alors que la liste a une capacité de 4 194 304
  éléments de 64 o). Pour ces deux collections de valeurs contiguës, on retient la taille de
  structure, 64 o, que mesurent les 11 autres implémentations du même type (64,00 à 64,03 o). Les
  mesures brutes restent publiées (`results/footprint_detail.json`). Les mesures par pic RSS restent
  dans `results/raw_post/` (étiquette `post_fp`), pour la trace.
* 2026-10-28, 18:06-18:25 : **mesure de la vectorisation (C3), corrections de l'outil avant usage**.
  Premier passage : la boucle analysée était celle de l'IP la plus fréquente, souvent hors du noyau
  (libc, OpenBLAS) car le chargement des données dominait des profils trop courts (70 échantillons
  pour C). Corrections, appliquées à tous les langages : 60 répétitions pour K4 et 20 pour K9
  (profil de plus de 0,3 s), échantillonnage à 4 kHz ; les échantillons sont regroupés par boucle
  (la plus petite boucle qui contient chaque IP chaude, jusqu'à 90 % des échantillons) ; la boucle
  retenue est la plus chaude du code du programme (exécutable ou code JIT), et non d'une bibliothèque
  partagée du runtime. Trois défauts de `tools/sampler.c` et `analysis/hotloop.py` sont corrigés :
  les projections anonymes (`//anon`) et le code JIT de .NET (`/memfd:`) étaient exclus de la copie
  du code ; la copie n'avait lieu qu'une fois par seconde ; la cible d'un saut écrite « 0x… » était
  lue comme 0. Enfin, objdump affiche comme données le code placé sous un symbole de type objet
  (tables d'info de GHC) : on désassemble alors les octets bruts. Les 50 boucles retenues et leur
  code machine sont dans `results/vectorization/*.txt`.
* Idem : **sondes de capacités**. Les 21 sondes ont été exécutées (154 lignes). Cinq ne compilaient
  plus avec les versions actuelles (C23 `alignas` sur une struct, noms de types tout en majuscules
  interdits en C3, `Atomic[T]` de Mojo 1.2, `**` retiré de Zig 0.17, import Nim) ; elles sont
  corrigées sans changer ce qu'elles testent. Six notes écrites dans les sondes divergeaient de la
  matrice ; tranchées par la règle de la section 3, elles donnent toutes raison à la matrice (C C5 :
  OpenMP livré avec clang et gcc mais hors norme, 0,5, désormais exécuté par la sonde ; C++ C4 :
  `std::reduce` et `std::simd::reduce` autorisent la réassociation dans la norme, 1 ; C++ C5 :
  `par_unseq` s'exécute en série dans libstdc++ sans TBB, 0,5 ; C++ D4 : libc, 0,5 comme C ; C++ E2 :
  `asm` est dans la norme C++, 1 ; Zig F4 : `mmap` POSIX seulement, 0,5 comme Go). Après correction
  des annotations : 0 divergence (`analysis/check_probes.py`, `results/probes/summary.md`).
* 2026-10-28, 18:28, **avant** de nouvelles données : **remesure des deux mesures instables pour tous
  les langages**. Critère objectif, calculé sur les données retenues : mesure du pilier E dont le
  coefficient de variation entre processus, médian sur les 21 langages classés, dépasse 10 %. Deux
  mesures le remplissent : K5 `tuned` (CV médian 15 %) et K10 `tuned` (15 %). Les autres vont de 2 à
  10 %. Diagnostic : pour K5, chaque processus est stable mais deux processus du même binaire
  diffèrent de 30 à 60 % (Zig 5,6 contre 8,2 ms) — un état de l'environnement de la VM qui dure le
  temps d'un processus ; pour K10, l'anneau SPSC est bistable (file pleine, lecture par rafales :
  6 à 10 ms ; file presque vide, une ligne échangée par message : jusqu'à 200 ms), quel que soit le
  langage. Avec 2 ou 3 processus, la médiane de ces deux mesures est un tirage au sort. C'est le
  problème que visait la passe complémentaire (annulée au redémarrage pour ne pas mêler deux
  machines). Application à l'échelle de la mesure entière : K5 `tuned` et K10 `tuned` sont
  remesurés pour **toutes** les implémentations sur la machine d'après redémarrage, 9 processus
  chacune, en 9 passes d'ordre aléatoire (graine fixe), avec les répétitions figées par
  `results/calib.json`. Ces données remplacent celles d'avant pour ces deux mesures. Aucune mesure
  n'est donc tirée de deux machines. Le classement avec les données d'avant est publié à côté, comme
  analyse de sensibilité.
* Idem : **simulation de cache non faite** (moyen (iii) de la section 6). Valgrind 3.22 ne décode
  pas l'AVX-512 (SIGILL vérifié sur une FMA zmm) et les binaires classés sont compilés pour la
  machine (`-march=native`). Recompiler sans AVX-512 aurait mesuré d'autres binaires que ceux du
  classement. La simulation est remplacée par les micro-expériences de `tools/hwprobe.c`, l'analyse
  du code machine des boucles chaudes (`tools/sampler.c`, `analysis/hotloop.py`) et le rusage.
* 2026-10-29 : **audit externe reçu** (`docs/AUDIT_2026-10-29.md`). Ses chiffres tirés des données se
  retrouvent tous ; réponse point par point : `docs/AUDIT_RESPONSE.md`. Il relève, entre autres, trois
  écarts au protocole que je n'avais pas consignés :
  * **Horloges hors du contrat** (section 7 de la spécification : temps mural, horloge monotone). Lua et
    LuaJIT mesurent le temps CPU du processus (`os.clock()`), OCaml et Chapel une horloge murale non
    monotone (`Unix.gettimeofday`, `Time.stopwatch`). Effet : pour les processus à un thread de la
    campagne, temps CPU / temps mural = 0,988 en médiane pour Lua (0,965 au pire), 0,986 pour C. L'écart
    est de l'ordre du pour cent, très loin des écarts qui séparent Lua des autres langages ; une horloge
    non monotone ne fausse une mesure que si l'heure système est réglée pendant celle-ci. Mesures gardées.
  * **Une phrase de la section 2 affirmait un résultat avant les données** (« une analyse de sensibilité
    montre que le classement ne dépend pas de ce choix »). Elle est démentie : l'ordre change à l'intérieur
    des groupes 1 et 2. Je laisse le texte d'origine, que cette note corrige.
  * **« Aucune mesure n'est tirée de deux machines »** (entrée de 18:28) : vrai variante par variante, faux
    au niveau du score. Pour K5 et K10, la mesure de E prend le minimum de `natural` (machine 1) et de
    `tuned` (machine 2), et la frontière t\* mêle les deux hôtes.
* 2026-10-29 : **analyse v2 décidée** en réponse à l'audit, plan dans `docs/ANALYSIS_V2.md`, poussé sur
  GitHub avant toute nouvelle mesure ; code d'analyse poussé avant son premier calcul. L'analyse v1 reste
  le résultat pré-enregistré, publié tel quel.
* 2026-10-29, 11:53 : **le conteneur redémarre sur un autre hôte** (machine 3) : Xeon de modèle 207
  (Emerald Rapids), TSC à 2,1 GHz, L2 de 2 Mio, L3 de 260 Mio, au lieu des Cascade Lake à 2,8 GHz des
  machines 1 et 2. Caractérisation : `results/hw/machine3/`. Deux défauts d'outil trouvés en la
  caractérisant, corrigés avant toute mesure : la sonde `freq` (chaîne d'`add $1`) donnait 14 à 18 GHz,
  parce que ce cœur replie les additions d'immédiats au renommage (additions registre-registre
  désormais) ; la première version du témoin construisait mal sa chasse de pointeurs. Les binaires
  compilés à l'avance sont recompilés sur la machine 3 par leurs scripts inchangés (empreintes avant et
  après : `results/hw/machine3/binaries.txt`). Nim réutilisait son cache d'objets compilés pour la
  machine 2 : cache supprimé, Nim recompilé. Le désassemblage du JIT de .NET et l'expérience des styles
  de K8 ont été faits sur la machine 3.
* 2026-10-29, 12:23 : **lancement des mesures v2** (`tools/measure_v2.py` : K5 complet, pages géantes,
  réplication). Une première exécution, arrêtée après trois processus pour la détacher du terminal, a été
  effacée sans être lue. Vers 12:37, pendant la passe 2 de K5, une capture d'écran de graphique (Chromium,
  environ 30 s) a tourné en même temps que les mesures : perturbation de mon fait, enregistrée par le
  témoin des processus concernés. Je n'ai plus rien lancé de lourd pendant les mesures.
* 2026-10-29, 13:00 : **K5 remesuré** (machine 3) : 50 mesures, 9 processus valides chacune, aucun
  invalide, un témoin par processus. Relevé des pages géantes terminé à 13:02 : seuls CPython (34 Mio) et
  Go (2 Mio) en obtiennent pendant K1 `natural`. Le plan disait la politique `madvise` « sur les trois
  machines » : elle n'a été relevée que sur les machines 1 et 3 (erratum dans `docs/ANALYSIS_V2.md`).
* 2026-10-29, 13:01 : **premier calcul de l'analyse v2**, après le K5 et avant la fin de la réplication,
  en priorité basse (`nice -n 19`) pour ne pas perturber les mesures en cours. La partie « réplication »
  n'y est pas encore calculée. Le calcul final reprend le même code et les mêmes graines.
* 2026-10-29, 14:18 : **réplication terminée** (203 blocs, 868 processus, tous valides). Calcul final de
  l'analyse v2 : même code et mêmes graines que le premier calcul, mêmes résultats pour la configuration
  principale, et partie « réplication » ajoutée. Diagnostics faits ensuite, hors plan, sur la machine au
  repos (`docs/ANALYSIS_V2.md`, section 10) :
  * latences : addition flottante 2 cycles, FMA 4 ;
  * K3 : l'alignement du code fait passer la même boucle d'un à sept cycles par incrément ;
  * K3 relancé trois fois pour C, Rust, C/gcc et Odin, gardé à part.
* 2026-10-29, 15:43 : **second audit reçu** (archivé dans `docs/AUDIT2_2026-10-29.md`). Au même moment, le
  conteneur redémarre (démarrage à 15:43:00) sur un hôte du même modèle que la machine 3 (Xeon de modèle 207,
  2,1 GHz). Sondes de vérification faites sur cet hôte, avant le plan : `probes/k5_reduction` (mécanisme de K5
  naturel) et `probes/csharp_jitvec_tiered` (JIT de .NET avec ses réglages par défaut).
* 2026-10-29, 15:54 : **plan de l'analyse v3 poussé** (`docs/ANALYSIS_V3.md`, commit `ae9e1a1`), avant tout
  calcul v3 et avant l'expérience de disposition. Il est écrit après lecture de l'audit et des résultats v1 et v2.
  J'y avais d'abord écrit « vers 16:30 » pour l'heure du plan : erreur, corrigée dans le plan.
* 2026-10-29, 15:56 : **expérience de disposition lancée** (`tools/layout_v3.py run`, 48 tâches, ordre tiré au
  hasard avec une graine fixe). Juste avant, la compilation avait révélé que GCC et rustc appelaient le lld 18 du
  système, qui ignore `--randomize-section-padding` : les deux passent désormais par un répertoire `-B` qui
  pointe sur lld 23 (commit `cfb2b79`). Les binaires de C (clang) étaient déjà liés par lld 23.
* 2026-10-29, 16:01 : **code de l'analyse v3 poussé** (commit `d0b959b`), avant son premier calcul sur les
  données. Ce premier calcul (16:01–16:04) a échoué à sa dernière étape : `layout_analysis()` lisait des
  processus de l'expérience de disposition encore en cours d'écriture, sans graine (`KeyError: 'layout_seed'`).
  Correction : ces processus sont ignorés. Le second calcul (16:04–16:07) a abouti. Les deux ont tourné en
  priorité basse (`nice -n 19`) pendant l'expérience de disposition, sur une machine à 4 cœurs : ils ont pu
  perturber les tâches 4 à 9. De même, `analysis/verify_audit2.py` (16:14:50–16:15:25) a recouvert les tâches
  17 et 18. Ces huit tâches sont publiées, et l'analyse donne aussi les résultats sans elles (hors plan). Je n'ai
  plus rien lancé de plus de quelques secondes avant la fin de l'expérience.
* 2026-10-29, 16:17 : **ajouts hors plan à l'analyse v3**, après avoir vu son premier calcul, tous marqués comme
  tels dans `results/report_v3.md` :
  * position dans l'intervalle par composante de D, pour localiser l'asymétrie qui reste sur MS ;
  * étages par quantité mesurée (E seul, D1 seul), avec la règle du plan et les mêmes tirages ;
  * Cascade Lake seul (K5 d'avant) ;
  * pour la disposition, un test par permutation des graines et une sensibilité sans les tâches perturbées.

  Ils ne consomment pas l'aléa des calculs prévus par le plan, dont les résultats restent identiques.
* 2026-10-29, 16:44 : **expérience de disposition terminée** : 48 tâches, 1 728 processus, tous valides, tous
  avec leur graine. Pendant qu'elle tournait, j'ai retiré du suivi Git les fichiers qu'elle écrivait, comme pour
  les mesures v2 ; ils reviennent complets avec le calcul final.
* 2026-10-29, 16:45 : **calcul final de l'analyse v3, et une erreur de reproductibilité.** Comparé au calcul de
  16:04, il donnait les mêmes étages et le même ordre, mais des intervalles un peu différents (jusqu'à 0,2 point).
  Cause : le code parcourait un ensemble Python, dont l'ordre d'itération change d'un processus à l'autre (hachage
  aléatoire des chaînes) ; l'ordre des résidus dans les réservoirs du bootstrap, donc les tirages, en dépendaient.
  Correction : clés triées. Deux calculs avec `PYTHONHASHSEED=1` et `PYTHONHASHSEED=2` donnent désormais des
  sorties identiques, octet pour octet. Par rapport aux calculs d'avant la correction, les écarts restent au niveau
  du bruit de Monte-Carlo : bornes d'IC à 0,2 point près, ensembles simultanés de Julia et d'Ada élargis d'un rang,
  p du test de réplication sur les 9 premiers de 0 à 0,0005. Les chiffres publiés sont ceux du calcul corrigé. Le
  graphique v3 a été rendu par Chromium après la fin de l'expérience.
* 2026-10-29, vers 17:05 : **inventaire des compteurs du noyau**, après une question de l'utilisateur, qui me
  soumettait la description d'un banc de mesure voisin. Sans PMU matérielle, le noyau expose pourtant des compteurs
  logiciels, des tracepoints d'appels système, des uprobes et des points d'arrêt matériels ; PSI est actif ;
  épinglage et `SCHED_FIFO` sont possibles. Je ne m'en servais pas, à part le temps volé (mesure refaite au-delà
  de 2 %) et les comptes de `wait4`, relevés mais jamais analysés. Vérification sur un programme de test : 1 000
  `getppid`, 1 000 `malloc` et 1 000 écritures comptés exactement. Deux pièges en construisant `tools/pecount.c` :
  une uprobe ouverte par la PMU `uprobe` fait échouer les `fork` du processus compté (d'où des uprobes définies
  dans tracefs), et `fopen(…, "a")` échoue sur tracefs (d'où `open` et `write` directs). Un essai d'uprobe sur
  `malloc` et `free` pendant K8 naturel en C (33,5 millions d'allocations par répétition) a dépassé 5 minutes et a
  été arrêté : K8 naturel est exclu du comptage des allocations. Coûts mesurés : appel système minimal environ
  100 ns, défaut de page mineur 1,4 à 1,7 µs, et 19 µs au premier passage sur une mémoire que la VM n'avait jamais
  touchée (défaut côté hôte) (`results/hw/machine3/syspf.txt`).
* 2026-10-29, 17:26 : **plan des compteurs poussé** (`docs/INSTRUMENTS_V3.md`, commit `ff9c188`), puis lancement
  de la passe de comptage, du comptage des allocations et du pilote de contrôle du bruit, l'un après l'autre. Code
  d'analyse poussé à 17:29 (commit `f50bdd3`), avant son premier calcul sur les données.
* 2026-10-29, 19:56 : **mesures des compteurs terminées**. Passe de comptage : 348 exécutions (17:26–17:57), toutes
  valides. Allocations par uprobe : 248 exécutions (17:57–19:53), dont 28 arrêtées à 120 s (trop d'appels pour une
  uprobe). Pilote du bruit : 180 processus (19:53–19:56) ; 23 des 29 interruptions ont pu être déplacées vers les
  CPU 0 à 2, et toutes ont été remises sur 0 à 3 ensuite (vérifié). Selon la règle fixée d'avance, les contrôles ne
  réduisent pas le bruit, et aucun indicateur ne prédit la lenteur d'un processus. Après coup : coût d'une trappe
  mesuré (`probes/trap_cost`, environ 30 µs par passage), et appel système d'Odin identifié par strace
  (`clock_gettime`). Pendant ces mesures, je n'ai lancé que l'analyse de la passe de comptage déjà terminée (moins
  d'une minute, pendant les allocations, qui ne sont pas chronométrées) et ce strace d'une répétition d'Odin, avant
  le pilote. Les fichiers de mesure étaient retirés du suivi Git pendant les mesures ; ils y reviennent complets.
* 2026-10-30 : **README réécrit autour d'un classement unique**, à la demande de l'utilisateur, qui voulait un vrai
  classement et un document lisible. L'ordre retenu est le rang moyen sur les 20 000 variantes de l'analyse globale
  v3 (1 + la somme, sur les autres langages, de la probabilité de passer devant). Ce critère est choisi après coup,
  en connaissant les résultats ; il suit le score de la configuration de référence, sauf pour deux paires voisines
  (C3 et Zig, Rust et D), que la plupart des variantes et la réplication sur la machine 3 inversent. Les plages de
  rang (5–95 %) et les probabilités de devancer le voisin sont publiées à côté. Les versions précédentes du README
  restent dans l'historique Git.

* 2026-10-30, 10:15 : **confrontation avec le « Banc de sympathie mécanique »**, à la demande de l'utilisateur
  (« fais les choses que tu veux tester pour trancher »). Plan pré-enregistré et poussé avant toute mesure :
  `docs/CONFRONTATION.md`. Le conteneur a redémarré le matin sur un nouvel hôte (machine 4) : Cascade Lake du même
  modèle que la machine 1 (modèle 85, révision 7, 4 vCPU), mais à la mémoire plus rapide (latence à 4 Mio de 107 ns
  contre 142, débit DRAM de 9,4 à 11 Go/s contre 6,7 à 7,7 ; `results/hw/machine4/`), plus proche de la machine 2.
  D'où le plan apparié du plan (section 4.5). Les binaires d'origine recompilés sur cet hôte par leurs scripts
  inchangés sont identiques octet pour octet à ceux de la campagne compilés sur Cascade Lake (C, C++, Nim, D, Ada,
  Fortran, Go : mêmes empreintes que `results/hw/machine3/binaries.txt`, section « avant »).
* 2026-10-30, avant les mesures : **écarts au plan de la confrontation**, trouvés en écrivant les réécritures.
  (1) L'audit de la section 4.2 avait manqué que `q6_tuned` et `q1_tuned` de Fortran (le plafond de K6 Q6 et Q1)
  portent aussi des directives `!$omp simd` : ces deux clés sont ajoutées aux mesures. (2) `ms.f90` utilise
  `omp_lib` dans les noyaux multi-threads, qui ne compile pas sans OpenMP : la copie standard de Fortran compile donc
  `tuned.f90` (tous les noyaux mesurés de la copie) sans `-fopenmp`, et garde `ms.f90` (harnais, variantes
  naturelles, noyaux multi-threads non mesurés) compilé comme l'original. Les variantes naturelles de Fortran sont
  ainsi identiques à celles de la campagne et ne sont pas remesurées. (3) Go : sans `GOEXPERIMENT`, le code machine
  des six fonctions naturelles comparées est identique (objdump normalisé) ; elles ne sont pas remesurées.
  (4) Réécritures : le Q1 standard de C compte ses lignes par voie, sans `stdc_count_ones` ; les copies standard de
  C, Nim et Ada sont compilées avec `-mprefer-vector-width=512` (choix de la largeur, permis par la section 4.1) ;
  Go, qui ne vectorise pas, reçoit 8 accumulateurs scalaires au lieu de tableaux de 64 voies ; la version standard de
  K5 en Nim coupe localement les vérifications par les pragmas standard que le fichier emploie déjà ailleurs.
* 2026-10-30, 10:37-10:56 : **mesures de la confrontation** (`tools/measure_conf.py`) : 96 cellules × 7 processus,
  aucune somme de contrôle fausse ; le pilote a refait une centaine de processus pour vol de temps au-dessus de 2 %,
  surtout des mesures à 4 threads (règle inchangée : le troisième essai est gardé). Rien d'autre ne tournait.
  Pendant les mesures, seuls des fichiers ont été écrits et poussés (aucun calcul).
* 2026-10-30, après les mesures : **analyse de la confrontation** (`analysis/confrontation.py`, poussé avant son
  premier calcul). Le scénario A rejoue exactement l'analyse v3 publiée (rangs espérés identiques). Verdicts et
  chiffres : `docs/CONFRONTATION.md`, section « Résultats ». **Contrôle hors plan**, décidé après avoir vu les
  rapports appariés : les données de K5 viennent de la machine 3 (Emerald Rapids) et leur rapport a été mesuré sur
  Cascade Lake ; le transfert n'est sûr que pour C et Fortran, dont la boucle chaude ne change pas (FMA 512 bits,
  quatre accumulateurs, vérifié au désassemblage) ; Nim et D perdent la FMA, Go, Java et Chapel passent au scalaire.
  Le scénario D recalculé avec les rapports de K5 forcés à 1 (`analysis/confrontation_posthoc.py`) donne les mêmes
  verdicts (Spearman 0,87, C 5e).
* 2026-10-30, après la confrontation : **notation à l'aveugle**, autorisée par l'utilisateur pour cette fois (un
  sous-agent, contre la règle générale de cette étude). Plan et script de comparaison poussés avant le lancement et
  avant la lecture des notes. Le juge travaillait dans un répertoire vide, avec interdiction de lire le dépôt,
  l'étude fournie et mes fichiers de travail. Il a écrit hors de son répertoire dans deux caches globaux (Zig,
  .NET), sans effet sur les résultats. Résultats : `docs/CONFRONTATION.md`, addendum.
* Idem : **erratum de la matrice de capacités**, trouvé par le juge et vérifié à la main : C D3, D D3, Odin D3,
  Odin C2 et Nim C5 (`analysis/capabilities.py`, `analysis/capabilities_v2.py`, `analysis/standard_rule.py`).
  La comparaison pré-enregistrée reste calculée sur la matrice d'avant correction. L'analyse v3, ses graphiques et
  le README sont recalculés avec la matrice corrigée ; l'effet sur le classement est publié avec la correction.
* Idem : **analyse v3 recalculée avec la matrice corrigée** (`analysis/analyze_v3.py`, graphiques, README). L'ordre
  final est identique ; les scores de C, d'Odin, de Nim et de D bougent d'au plus 1,1 point. La réplication sur la
  machine 3 change un peu (Spearman sur les 13 premiers 0,74 au lieu de 0,78). Deux chiffres du README n'avaient
  pas de script : la part des variantes où C ou C++ est premier et le R² du contrôle parmi les 13 premiers.
  `analysis/readme_figures.py` les calcule désormais. La même méthode, appliquée à la matrice d'avant correction,
  redonne les anciens chiffres (C 55 %, C++ 31 % ; R² 0,80). Pour compter les premières places,
  `analysis/confrontation.py` relève aussi le langage premier de chaque tirage, sans rien changer à ses autres
  sorties.
* 2026-10-30, 13:22 : **le conteneur redémarre sur un nouvel hôte** (machine 5) : Cascade Lake du même modèle que les
  machines 1, 2 et 4 (modèle 85, révision 7, 4 vCPU, 16 Go), latence à 4 Mio de 138 à 151 ns, débit DRAM de 9,4 à
  10 Go/s (`results/hw/machine5/`). Le binaire de Zig, compilé pour la machine 3, est recompilé par son script
  inchangé : identique octet pour octet au binaire de la campagne compilé sur Cascade Lake.
* 2026-10-30, après-midi : **remarque sur Zig** transmise par l'utilisateur (vectoriseur de boucles désactivé par
  l'équipe Zig en 0.16 et 0.17). Vérifications préalables (notes de version, sources du compilateur, mesures de K4
  et K9 avec un pilote commun pour quatre versions de Zig, coût des threads, sonde F4) et plan des mesures et de
  l'analyse : `docs/ZIG.md`, poussé avant les mesures. Chaînes ajoutées : Zig 0.15.2, 0.16.0 et
  0.18.0-dev.753+1420479be (archives de ziglang.org, SHA-256 et signatures minisign vérifiées), sources de 0.17.0 et
  de master. Erreur de fait trouvée : F4 de Zig en règle v1 (0,5 au lieu de 1).
* 2026-10-30, 13:55-14:10 : **mesures de la remarque sur Zig** (`tools/measure_zig.py`, machine 5) : 69 cellules ×
  7 processus, aucune somme de contrôle fausse ; 31 processus refaits pour vol de temps au-dessus de 2 % (règle
  inchangée : le troisième essai est gardé, une fois au-dessus du seuil). Rien d'autre ne tournait ; pendant les
  mesures, seuls des fichiers ont été écrits et poussés. Après les mesures : vectorisation mesurée de la boucle
  chaude de Zig master (`tools/c3_measure.py zig_master` : K4 et K9 vectorisées, C3 = 1), sondes de Zig et de C
  relancées. La sonde C déclarait encore D3 = 0 après l'erratum du juge à l'aveugle (la matrice dit 0,5) : alignée,
  0 divergence entre sondes et matrice.
* 2026-10-30, après les mesures : **analyse de la remarque sur Zig** (`analysis/zig_check.py`, poussé avant son
  premier calcul). Le scénario A' rejoue exactement l'analyse v3 publiée, correction de F4 comprise (rangs espérés
  identiques à `results/summary_v3.json` recalculé). Zig 0.18-dev (S1) : 74,8 points, 2e en rang espéré ; Zig 0.17
  reste 5e dans le classement publié, comme le plan l'avait fixé. **Analyse v3 recalculée** avec F4 corrigée
  (`analysis/analyze_v3.py`, `analysis/readme_figures.py`, `analysis/charts_v3.py`) : ordre et scores de référence
  inchangés ; C3 devance Zig dans 54 % des variantes (56 % avant), Zig devance Nim dans 62 % (60 %), C++ est premier
  dans 25 % des variantes (26 %). `analysis/confrontation.py` relève désormais le rang de chaque tirage (rang dans
  90 % des variantes), sans rien changer à ses autres sorties. Le second juge à l'aveugle avait noté que Zig 0.17
  ne vectorise aucune boucle (`results/blind_notes.md`) ; je ne l'avais pas suivi. Résultats : `docs/ZIG.md`,
  section 4.
* 2026-10-30, fin d'après-midi : **remarque sur Ada** transmise par l'utilisateur (piège `-fnon-call-exceptions` de
  GNAT, cases E5, C1 et B4, attributions du README). Vérifications préalables sur les sources de GCC 16.2.0 (archive
  téléchargée de nouveau, signature vérifiée avec le trousseau GNU : les sources de la compilation avaient été
  supprimées) et par des sondes compilées par GNAT 16.2 ; plan des mesures et de l'analyse : `docs/ADA.md`, poussé
  avant les mesures. Le binaire d'Ada recompilé sur la machine 5 est identique octet pour octet à celui de la
  campagne.
* 2026-10-30, 15:14-15:32 : **mesures de la remarque sur Ada** (`tools/measure_ada.py`, machine 5) : 60 cellules ×
  7 processus, aucune somme de contrôle fausse ; 23 processus refaits pour vol de temps au-dessus de 2 % (un gardé
  au-dessus du seuil au troisième essai). Rien d'autre ne tournait ; pendant les mesures, seuls des fichiers ont été
  écrits et poussés. Après les mesures : sonde Ada des errata (C1, E5, B4 ; 0 divergence avec la matrice).
* 2026-10-30, après les mesures : **analyse de la remarque sur Ada** (`analysis/ada_check.py`, poussé avant son
  premier calcul). Comme le plan l'avait fixé, les errata et la correction de l'implémentation entrent dans le
  classement publié : `analysis/analyze_v2.dataset_main` applique désormais les rapports appariés de
  `results/transfers.json` (12 clés d'Ada, K5 à 1) aux données principales, et l'analyse v3 recalculée redonne
  exactement le scénario S1 (rangs espérés et scores identiques). Ada passe de 68,0 à 71,6 points et de la 9e à la
  7e place ; C++, C3, Nim, D, Julia et Fortran perdent 0,1 point de score de référence, parce qu'Ada devient la
  référence de K1. Trois clés témoins dont le source ne change pas bougent de 18 à 25 % (K8 naturel et `tuned`, K9
  naturel) : effet de disposition du binaire, publié avec les résultats. La réplication sur la machine 3 garde les
  données d'Ada sans correction. Les scénarios de Zig sont recalculés sur ces données (écarts d'au plus 0,2 rang
  espéré, même verdict). Le chiffre du README sur le stencil naturel (« 56 à 73 ms ») était faux : 55 à 80 ms dans
  les données principales, corrigé.
* 2026-10-30, fin d'après-midi : **remarque sur Fortran** transmise par l'utilisateur (K4 inliné dans la boucle de
  mesure, formes de K5 et K8, cases A3, A4, B2 et F2). Vérifications préalables (binaire de la campagne, sondes
  gfortran 16.2), règle commune aux trois remarques et plan : `docs/FORTRAN.md`, poussé avant les mesures avec le
  code d'analyse (`analysis/fortran_check.py`) et les errata de la grille.
* 2026-10-30, 16:36-16:47 : **mesures de la remarque sur Fortran** (`tools/measure_fortran.py`, machine 5) : 58
  cellules × 7 processus (406), aucune somme de contrôle fausse ; 16 processus refaits pour vol de temps au-dessus de
  2 %, aucun gardé au-dessus du seuil. Rien d'autre ne tournait. Après les mesures : C3 de `fortran_fix` (1, contre
  0,5 pour le binaire de la campagne) et sondes Fortran des errata.
* 2026-10-30, après les mesures : **analyse de la remarque sur Fortran** (`analysis/fortran_check.py`, poussé avant
  les mesures). Le scénario S1 du plan donne 68,4 points et la 9e place. **Écart au plan, décidé après avoir vu les
  données** : le témoin du même hôte (C compilé par GCC) contredit le transfert de K4 sans branchement, qui mettait
  Fortran à 0,56 fois GCC dans les données principales, alors qu'ils font jeu égal sur la machine 5 (la boucle
  scalaire inlinée de la campagne dépend de l'hôte). Règle ajoutée, appliquée aux 8 clés transférées qui ont un
  témoin (6 d'Ada, 2 de Fortran) : quand le transfert s'écarte de plus de 25 % du pont par le témoin, le pont le
  remplace (`analysis/transfer_check.py`). Une seule clé change (K4 sans branchement de Fortran : rapport 0,384 au
  lieu de 0,224). Classement publié : Fortran 66,3 points, 10e (rang espéré 9,40) ; le scénario du plan est publié
  à côté (`docs/FORTRAN.md`, 4.2 et 4.3). L'analyse v3 recalculée redonne exactement le scénario retenu (scores
  et rangs plausibles identiques pour les 21 langages). Les scores des autres langages ne changent pas ; Chapel et
  Julia perdent une place, le plafond de Zig passe de la 10e à la 11e place, et la part des écarts de score entre
  les 13 premiers qu'explique le contrôle passe de 81 à 78 %. Les scénarios de Zig sont recalculés sur ces données
  (S1 : rang espéré 2,71 au lieu de 2,69, même verdict).
* 2026-10-30, 17:39 : **le conteneur redémarre sur un nouvel hôte** (machine 6) : Cascade Lake du même modèle que les
  machines 1, 2, 4 et 5 (modèle 85, révision 7, 4 vCPU, 16 Go), latence à 4 Mio 43 ns, débit DRAM 10 Go/s
  (`results/hw/machine6/`). Le binaire de Mojo du banc était celui compilé pour la machine 3 ; recompilé par son
  script inchangé, il est identique octet pour octet au binaire de la campagne compilé sur la machine 2.
* 2026-10-30, début de soirée : **remarque sur Mojo** transmise par l'utilisateur (cases A4, A5, C4, E5, D5 et B4 ;
  K4 dans le plafond ; diagnostic du stencil naturel). Vérifications préalables (sources de Mojo 1.2.0 au tag
  `mojo/v1.2.0`, notes de version, sondes compilées par Mojo 1.2.0, code machine, compteur d'allocations), errata de
  la matrice (A4, A5, C4, D5, E5 ; B4 gardé) et plan : `docs/MOJO.md`, poussé avant les mesures avec le code
  d'analyse (`analysis/mojo_check.py`). `confrontation.scenario` prend désormais, en option, des noyaux de poids nul
  dans le plafond (pour le scénario sans K4) ; par défaut, le calcul publié est inchangé.
* 2026-10-30, 18:05-18:07 : **mesures de la remarque sur Mojo** (`tools/measure_mojo.py`, machine 6) : 18 cellules
  × 7 processus (126), aucune somme de contrôle fausse ; 2 processus refaits pour vol de temps au-dessus de 2 %,
  aucun gardé au-dessus du seuil. Rien d'autre ne tournait.
* 2026-10-30, après les mesures : **analyse de la remarque sur Mojo**. La première version du scénario sans K4
  retirait K4 de la liste des mesures du plafond ; elle a échoué (`KeyError`), parce que le code par défaut D1 partage
  la référence de K4 naturel. Corrigée avant tout résultat de ce scénario : K4 garde ses références et reçoit un
  poids nul dans le plafond (le plan, section 3.4 de `docs/MOJO.md`, ne change pas).
* 2026-10-30, soir : **résultats de la remarque sur Mojo** (`results/report_mojo.md`). Les errata (A4, A5, D5 et E5
  à 1, C4 à 0,5) entrent dans le classement publié : Mojo passe de 60,0 à 62,7 points (contrôle 62,7 → 70,5) et reste
  13e (rang espéré 11,87) ; l'analyse v3 recalculée redonne exactement le scénario M-E, et les scores des autres
  langages ne bougent pas. Sensibilités : avec B4 à 0,5, 62,0 points ; sans K4 dans le plafond, Mojo 11e, mais aussi
  C++ 1er devant C et Zig 3e (dit dans le README). Les vérifications de bornes de `List` expliquent l'essentiel du
  stencil naturel de Mojo (×4,1), pas tout (×1,48 face au C vectorisé, au-delà du seuil de 1,2 fixé d'avance) : le
  README dit les deux causes ; pour Q1, elles expliquent tout (0,995). Les scénarios de Zig sont recalculés sur ces
  données (seul S3 bouge : 5,82 → 5,83).
* 2026-10-30, 19:14 : **le conteneur redémarre sur un nouvel hôte** (machine 7) : Cascade Lake du même modèle que
  les machines 1, 2, 4, 5 et 6 (modèle 85, révision 7, 4 vCPU, 16 Go), latence à 4 Mio 60 ns, débit DRAM 10 Go/s
  (`results/hw/machine7/`).
* 2026-10-30, soir : **remarque sur Julia** transmise par l'utilisateur (place due au plafond et non au runtime ;
  noyaux tuned moins travaillés ; cases B2, D3 et D5 ; diagnostic de K10). Vérifications préalables (sondes Julia
  1.13.3, code natif de K5, cinq variantes de K10 dont une bloquée, observée sous gdb, puis tuée par SIGKILL),
  errata de la matrice (B2 et D3 à 0,5, D5 à 1 en règle v2) et plan : `docs/JULIA.md`, poussé avant les mesures avec
  le code d'analyse (`analysis/julia_check.py`).
* 2026-10-30, 19:34-19:50 : **mesures de la remarque sur Julia** (`tools/measure_julia.py`, machine 7) : 25 cellules
  × 7 processus (175), aucune somme de contrôle fausse, aucun processus refait. Rien d'autre ne tournait.
* 2026-10-30, soir : **résultats de la remarque sur Julia** (`results/report_julia.md`). Les errata (B2 et D3 à 0,5,
  D5 à 1 en règle v2) entrent dans le classement publié : Julia passe de 62,2 à 64,0 points et reste 12e (rang espéré
  11,12) ; l'analyse v3 recalculée redonne exactement J-E, et les scores des autres langages ne bougent pas.
  Sensibilité, hors classement (formes de la remarque) : 67,1 points et la 10e place (S1) ; 68,9 et la 9e avec K5 en
  512 bits, reporté par le pont du C du même hôte parce que le transfert s'en écartait de 58 % (S1-K5). Le README
  attribue désormais la place de Julia à son plafond, et le diagnostic de K10 est corrigé (README, FINDINGS). Les
  scénarios de Zig sont recalculés (A' 5,73 → 5,75 ; S3 5,83 → 5,85 ; S1 inchangé).
* 2026-10-31, 9:47 : **le conteneur redémarre sur un nouvel hôte** (machine 8) : Emerald Rapids du même modèle que la
  machine 3 (modèle 207, révision 2, 4 vCPU), latence à 4 Mio 57 ns, débit DRAM 13,9 Go/s (`results/hw/machine8/`).
* 2026-10-31, matin : **remarque sur Chapel** transmise par l'utilisateur (cases B2, C2, E5, C4 et B3 ; Q1 en
  intrinsèques ; copie standard de la confrontation ; K7 naturel). Vérifications préalables (sources de Chapel 2.10.0,
  sondes compilées, IR LLVM, cas d'import qui échouent), errata de la matrice (B2, C2 et E5 à 0,5 ; textes de C4 et
  B3 corrigés ; règle du standard à 0,25 pour B2, C2 et E5) et plan : `docs/CHAPEL.md`, poussé avant les mesures
  avec le code d'analyse (`analysis/chapel_check.py`). Le runtime de Chapel n'accepte que la cible `native` : le
  source de la campagne est recompilé pour l'hôte (`bench/chapel_ref`) et sert de référence aux copies.
* 2026-10-31, 10:10-10:15 : **mesures de la remarque sur Chapel** (`tools/measure_chapel.py`, machine 8) : 27 cellules
  × 7 processus (189), aucune somme de contrôle fausse ; 8 processus refaits pour vol de temps au-dessus de 2 %,
  aucun gardé au-dessus du seuil. Rien d'autre ne tournait.
* 2026-10-31, matin : **résultats de la remarque sur Chapel** (`results/report_chapel.md`). Les errata (B2, C2 et E5 à
  0,5) entrent dans le classement publié : Chapel passe de 64,1 à 65,9 points et de la 11e à la 10e place (rang espéré
  9,03), devant Fortran dans 60 % des variantes ; l'analyse v3 recalculée redonne exactement C-E, et les scores des
  autres langages ne bougent pas. Deux écarts au plan, décidés après avoir vu les données : le scénario S1-T (rapports
  transférés sans pont), parce que le pont par le C se trompe entre Cascade Lake et Emerald Rapids sur K7 naturel et
  K1 aos ; et, pour la confrontation, la meilleure forme standard par clé (K1 aos garde la boucle d'origine, sans
  effet sur le résultat). Confrontation corrigée : sous la règle du standard, le plafond de Chapel passe de 49,3 à
  72,1 (scénario C, état actuel). Les scénarios de Zig sont recalculés (S1 : 2,72 ; A' : 5,80 ; même verdict).
* 2026-10-31, 12:08 : **machine 9**. La VM redémarre sur un hôte Emerald Rapids du même modèle que les machines 3 et 8
  (modèle 207, révision 2, 4 vCPU ; latence à 4 Mio 61 ns, DRAM 13,5 Go/s : `results/hw/machine9/`). Les données de
  `/opt/msdata`, régénérées par `tools/gendata.c`, sont identiques au bit près (`results/msdata_sha256.txt`).
* 2026-10-31, début d'après-midi : **plan de la remarque sur C#** (`docs/CSHARP.md`, sections 1 à 3), poussé avant les
  mesures. Vérifications faites avant le plan : versions (index officiel), désassemblage du JIT de .NET 10 et de .NET 11
  RC3 (installé dans `/opt/dotnet11`, hors classement), sources du JIT (`dotnet/runtime`, clone partiel), niveaux de
  compilation sous le protocole de la campagne, sondes (AVX-512, unions de C# 15, génériques de C# et de Go) :
  `results/csharp_check/`. Aucun fait de la remarque n'est faux dans le dépôt ; E7 reste un jugement (0,5) ; rien
  n'entre dans le classement publié en l'état. Copies du banc : `bench/csharp_exp`, `bench/csharp_nat2`,
  `bench/c_exp`, `bench/c_gcc_exp` ; protocoles : `bench/csharp_full`, `csharp_steady`, `csharp_net11`,
  `csharp_exp_full` (mêmes binaires).
* 2026-10-31, 12:47-13:24 : **mesures de la remarque sur C#** (`tools/measure_csharp.py`, machine 9) : 144 cellules
  × 7 processus (1 008) et 6 mesures d'empreinte ; aucune somme de contrôle fausse ; 22 processus refaits pour vol de
  temps au-dessus de 2 %, un seul gardé au-dessus du seuil (K4 en SIMD explicite de `csharp_exp`, 3,5 %, hors
  classement). Rien d'autre ne tournait.
* 2026-10-31, après-midi : **résultats de la remarque sur C#** (`results/report_csharp.md`). Rien n'entre dans le
  classement publié : C# garde 54,8 points et la 14e place (le calcul refait redonne 54,77). Les 19 scénarios de
  sensibilité laissent tous C# 14e ; avec tout ce qui lui est favorable (S-max), il rejoint Mojo au score (62,0 à 62,6
  contre 62,3), et Mojo ne le devance plus que dans 62 à 70 % des variantes. Effet moyen du protocole : 0 à 2,5 %
  (+0,7 à +0,9 point). Aucun écart au plan. Le README précise la phrase sur les 98 % des variantes ; le texte de la
  case E7 de C# est précisé (note inchangée).
* 2026-10-31, début d'après-midi : **audit du README** à la demande de l'utilisateur. L'analyse v3, ses figures et
  `results/readme_figures.json`, recalculées, sont identiques au bit près aux fichiers publiés, et le tableau du
  classement leur correspond ligne à ligne. Mais des chiffres du texte dataient d'états antérieurs : Nim, Zig et C3
  devant Ada dans 55 à 69 % des variantes (54 à 68 écrits), D derrière Nim et Rust dans 66 % (65), Mojo 12e et non 11e
  sans K4 dans le plafond (depuis les errata de Chapel), Julia 9e à 11e avec ses formes optimisées (9e ou 10e), un
  plafond calculé sur 8 noyaux et non 9 (K2 compte dans le code par défaut). La confrontation, datée du 30 octobre,
  est rejouée dans l'état actuel (`analysis/confrontation_current.py`, avec la copie standard de Chapel corrigée) :
  Spearman 0,76 (0,77), C 12e dans mon pilier contrôle sous leur règle (11e), accord des grilles 0,74 à 0,81 (0,83 à
  0,88) ; le README donne les deux états. Sensibilités de Julia rejouées dans l'état actuel
  (`results/julia_check_current.json`). Aucune donnée ni aucun score publié ne change.
* 2026-10-31, 14:39 : **machine 10**. La VM redémarre sur un hôte Emerald Rapids du même modèle (modèle 207, 4 vCPU ;
  latence à 4 Mio 52 ns, DRAM 13,4 Go/s : `results/hw/machine10/`).
* 2026-10-31, 15:00 : **plan de la remarque sur D** (`docs/DLANG.md`, sections 1 à 3), poussé avant les mesures
  (15:00:42). Vérifications faites avant le plan (`results/d_check/`) : chaîne (LDC 1.43.0 compilé depuis les sources
  contre LLVM 21.1.8 ; le paquet officiel, téléchargé dans `/opt/ldc143`, embarque LLVM 22.1.8), désassemblage de Q1 et
  du stencil, IR sans TBAA, contre-épreuve C++, sonde druntime. Décisions fixées d'avance : errata E3 et E4 de D en
  règle v1 ; le Q1 optimisé de D, écrit hors de la convention des langages à types vectoriels portables, est une
  erreur d'implémentation, corrigée dans le classement publié (`bench/d_fix`) ; la préférence 512 bits, le stencil en
  `double[M][]` et LLVM 22.1.8 restent des sensibilités.
* 2026-10-31, 15:00:48-15:12:32 : **mesures de la remarque sur D** (`tools/measure_d.py`, machine 10) : 77 cellules
  × 7 processus (539) ; aucune somme de contrôle fausse ; 21 processus refaits pour vol de temps au-dessus de 2 %, un
  seul gardé au-dessus du seuil (`d_ref`, K4 naturel, 6,2 %). **Incident** : j'ai compilé et lancé une sonde pendant la
  première passe (de 15:02:36 à 15:02:46 environ). Règle fixée avant de regarder les résultats : écarter les processus
  dont la durée recoupe cette fenêtre ; 8 sont écartés (`analysis/d_check.py`).
* 2026-10-31, fin d'après-midi : **résultats de la remarque sur D** (`results/report_d.md`, `results/d_check.json`).
  Entrent dans le classement publié les errata E3 et E4 de D en règle v1 et la correction de son Q1 optimisé : rapports
  appariés reportés sur les données principales par le pont pour Q1 tuned (× 0,332 ; le transfert, × 0,438, s'en
  écarte de 32 %) et par transfert pour Q1 `mt` (× 0,458), dans `results/transfers.json`. D passe de 71,0 à 72,6
  points et de la 9e à la 8e place (rang espéré 8,43 → 7,29) ; par transfert seul, 72,4 points et la 8e place.
  Sensibilités : préférence 512 bits 6e ; stencil en `double[M][]` 7e (transfert) ; tout cumulé 5e (transfert) ;
  LLVM 22.1.8 sans gain (1,01 en moyenne). **Écart au plan** : pour K9 naturel, le pont se trompe entre architectures
  (× 1,15, contre × 0,68 mesuré) ; j'ai ajouté S-nat-T et S-tout-T, par transfert seul, après avoir vu les chiffres. Le
  README corrige la cause du stencil de D (aliasing sans TBAA, pas vérifications de bornes) et un chiffre périmé de la
  même phrase (stencil naturel de Rust, Nim et Ada : 71 à 73 ms, et non 80). Sorties recalculées :
  classement, figures, scénarios de Zig et de Julia, confrontation (Spearman des scénarios C et D 0,79 et 0,88 ; le
  reste inchangé).
* 2026-10-31, vers 17:00 : **machine 11**. La VM redémarre sur un hôte Emerald Rapids du même modèle (modèle 207,
  4 vCPU ; 3,18 GHz effectifs, latence à 4 Mio 48 ns, DRAM 13,0 Go/s : `results/hw/machine11/`).
* 2026-10-31, soirée : **plan de la remarque sur Rust** (`docs/RUST.md`, sections 1 à 3), poussé avant les mesures.
  Vérifications faites avant le plan (`results/rust_check/`) : chiffres du score et décomposition, latences de K8
  naturel par processus et vol de temps, code machine des formes de K9 et de Q1 (cibles Cascade Lake et hôte),
  préchargement de K7 dans chaque implémentation, sonde `_MM_HINT_ET0`. Décisions fixées d'avance : le préchargement
  en lecture de K7 optimisé, seul écart à la convention des implémentations qui peuvent précharger en écriture, est une
  erreur d'implémentation, corrigée dans le classement publié (`bench/rust_fix`) ; K8 naturel est remesuré pour les
  25 implémentations (7 processus) et ses latences remplacent celles de la campagne dans D3 pour toutes, comme K5 en
  v2 ; `_popcnt32`, l'arène de K8, `Vec<[f64; M]>` pour K9 et la règle de la libc étendue restent des sensibilités.
* 2026-10-31, 17:27:57-17:54:01 : **mesures de la remarque sur Rust** (`tools/measure_rust.py`, machine 11) : 57
  cellules × 7 processus (399) ; aucune somme de contrôle fausse ; 9 processus des paires refaits pour vol de temps
  au-dessus de 2 %, aucun gardé au-dessus du seuil ; aucune reprise pour la remesure de D3 (vol médian 0,33 %, maximum
  1,28 %). Rien d'autre ne tournait. **Écart au plan (cellules)** : `rust_ref` n'a pas mesuré K8 naturel ; le témoin de
  `rust_k8` est comparé au binaire Rust de la remesure de D3 (même hôte, mêmes passes ; information seulement).
* 2026-10-31, soirée : **résultats de la remarque sur Rust** (`results/report_rust.md`, `results/rust_check.json`).
  Entrent dans le classement publié la remesure de D3 pour les 25 implémentations (latences de `results/raw_d3` lues
  par `analysis/analyze_v2.py`) et la correction de K7 optimisé de Rust (× 1,082 par transfert, le pont s'en écartant de
  5 %). Rust passe de 69,4 à 70,5 points et de la 9e à la 6e place (rang espéré 7,57 → 6,55), à égalité avec C3 et
  Nim ; Zig passe de la 5e à la 4e place, C3 de la 4e à la 5e, Nim de la 6e à la 7e, Ada de la 7e à la 9e ; C# de 54,8
  à 56,0 points. Sensibilités : K9 en `Vec<[f64; M]>`, `_popcnt32` et arène écrite comme en C, une place chacune
  (5e) ; libc étendue à Rust, 73,5 points et la 4e place ; à tous les langages à FFI, la 4e ; tout cumulé, 75,3 et la
  2e. Rejoués dans le nouvel état : Zig (0.18-dev 1er en rang espéré), Julia, Mojo et C# (sorties `*_current` ; avec
  S-max, C# passe 13e devant Mojo), confrontation (Spearman 0,78). README : paragraphe sur Rust réécrit, cause du
  stencil naturel de Rust (aliasing), latences de K8 tirées de la remesure, ordre et chiffres recalculés, règle de la
  libc dans les limites ; `docs/NATURAL.md`, `docs/AUDIT2_RESPONSE.md` et les notes d'état actuel (Zig, Julia, Mojo,
  C#, Ada, D, confrontation) mis à jour.
* 2026-11-01, vers 9:10 : **machine 12**. La VM redémarre sur un hôte Emerald Rapids du même modèle (modèle 207,
  4 vCPU), plus lent que les machines 10 et 11 : 2,6 à 2,8 GHz effectifs, latence à 4 Mio 36 ns, DRAM 15,3 Go/s
  (`results/hw/machine12/`).
* 2026-11-01, matinée : **plan de la remarque sur Nim** (`docs/NIM.md`, sections 1 à 3), poussé avant les mesures.
  Vérifications faites avant le plan (`results/nim_check/`) : code machine du Q1 en blocs (vectorisé, comme son
  commentaire l'annonce), forme de Q1 et SIMD explicite par langage, formes de K9 sous `-d:release`, `-d:danger` et
  `-fstrict-aliasing`, sonde `{.localPassC.}`, Nim 2.4.0 (paquet officiel) contre 2.2.12. Décisions fixées d'avance :
  le Q1 en blocs de Nim suit la pratique de sa classe (le plan de D le rangeait nommément parmi les langages à blocs) ;
  le Q1 en intrinsèques, le K9 en tableau fixe et l'arène sans vérification de débordement sont des sensibilités ;
  aucune donnée publiée ne change ; le README corrige la cause du stencil naturel de Nim et la matrice précise C4.
* 2026-11-01, 9:27:14-9:32:09 : **mesures de la remarque sur Nim** (`tools/measure_nim.py`, machine 12) : 33 cellules ×
  7 processus (231) ; aucune somme de contrôle fausse ; 12 processus refaits pour vol de temps au-dessus de 2 %, aucun
  gardé au-dessus du seuil. Rien d'autre ne tournait. Aucun écart au plan.
* 2026-11-01, matinée : **résultats de la remarque sur Nim** (`results/report_nim.md`, `results/nim_check.json`).
  Rien n'entre dans le classement publié : Nim reste 7e (69,7 points). Sensibilités : Q1 en intrinsèques × 0,302
  (au niveau de C), 71,8 points et la 5e place ; K9 naturel en tableau fixe et arène sans vérification de débordement,
  une place chacune ; les trois, 72,4 points et la 4e place. README : cause du stencil naturel de Nim (vérifications et
  `-fno-strict-aliasing`), Nim 2.4.0 dans les limites ; `docs/FINDINGS.md` : phrase ancienne sur le stencil de Rust, D,
  Nim et Ada corrigée ; matrice : texte de C4 de Nim précisé. Ajouté après les mesures : `results/nim_check/gcc_k5.txt`
  (harnais de K5 naturel compilé par gcc).

* 2026-11-01, fin de matinée : **sensibilité « sans SIMD explicite »**, demandée après la réponse sur la règle de D.
  Classement des variantes du plafond (scalaire, types vectoriels du langage, intrinsèques de la plateforme,
  intrinsèques importées) et plan de sept scénarios poussés avant tout calcul (`docs/NOSIMD.md`, commit `bf650a0`) ;
  `cf.scenario` reçoit deux paramètres optionnels sans effet par défaut (`e_meas`, `patch`). Résultats
  (`results/report_nosimd.md`) : le témoin reproduit le publié à l'identique ; à la lettre (S-scalaire), Chapel,
  Fortran et Julia passent devant, mais K1 et K5 expliquent 82 à 96 % de la baisse du plafond des langages à SIMD (la
  disposition SoA et la réassociation de K5 sont écrites dans leurs variantes SIMD) ; à forme égale pour tous et sans
  les noyaux vectorisables, C, C++ et Odin gardent les trois premières places. Dans les trois scénarios, les douze
  premières places reviennent aux mêmes langages et les positions 13 à 21 ne bougent pas. Le classement publié ne
  change pas. Correction : le décompte « 9 contre 2 » des formes de Q1 oubliait Java, Go et Haskell (9 contre 5 ; note
  datée dans `docs/NIM.md`). Page d'explication : `docs/page/simd.html` (`tools/nosimd/page.py`).
* 2026-11-01, midi : la page HTML d'explication est remplacée, à la demande, par une note Markdown dans le dépôt
  (`docs/SIMD_EXPLICATION.md`) ; `docs/page/` et `tools/nosimd/page.py` sont retirés. Rien n'est publié hors du dépôt.
* 2026-11-01, vers 11:00 : **machine 13**. La VM tourne sur un hôte Emerald Rapids du même modèle (modèle 207, 4 vCPU ;
  2,73 à 2,77 GHz effectifs, latence à 4 Mio 36 ns, DRAM 14,8 Go/s : `results/hw/machine13/`).
* 2026-11-01, 11:16 : **plan de la remarque sur C3** (`docs/C3.md`, sections 1 à 3, commit `0c4a503`), poussé avant les
  mesures. Vérifications sur les sources de la version mesurée (C3 0.8.5_1, `/opt/src/c3c`) et par des sondes de
  compilation (`tools/c3_check/`, `results/c3_check/`), sans consulter le site ni master : quatre errata de la remarque
  confirmés (C4, E2, E5, F4 en règle v1 ; `noalias` posé sur le mauvais paramètre, vu dans l'IR), un cinquième retenu
  (D4, appel système brut, comme Go et Odin en règle v1), D3 laissé à 0 ; le chiffre de 400 mnémoniques x86 est faux
  (217). Les trois pistes mesurées (réduction de K5, démarrage des fils de K9 mt, `--optlevel=max`) sont des formes ou
  des options nouvelles : sensibilités.
* 2026-11-01, 11:16:59-11:28:09 : **mesures de la remarque sur C3** (`tools/measure_c3.py`, machine 13) : 61 cellules
  × 7 processus (427) ; aucune somme de contrôle fausse ; 26 processus refaits pour vol de temps au-dessus de 2 %, un
  seul gardé au-dessus (2,4 %). Rien d'autre ne tournait. Aucun écart au plan.
* 2026-11-01, midi : **résultats de la remarque sur C3** (`results/report_c3.md`, `results/c3_check.json`). Classement
  publié : les cinq errata portent le contrôle de C3 de 73,1 à 75,7 et son score de 70,3 à 71,2 ; il reste 5e (rang
  espéré 6,47 → 5,74) ; Nim et Rust, à égalité, échangent leurs places (Nim 6e, 6,66 ; Rust 7e, 6,67). Sensibilités :
  réduction en arbre de K5 × 1,02 (rien), fils de K9 mt par `pthread_create` × 0,94 (non significatif),
  `--optlevel=max` × 0,98 en moyenne et 72,2 points ; D3 à 0,5, 71,8 points ; C3 reste 5e partout. Le pont par le C
  se trompe sur K9 entre Cascade Lake et Emerald Rapids (C3 / C : 1,58 et 2,18 sur cet hôte contre 0,93 et 1,40) : les
  variantes par transfert seul, calculées par le même code, sont la lecture retenue pour K9. Sorties recalculées :
  classement, figures, matrice, scénarios de Zig, de Julia, de Mojo, de C#, de Rust et de Nim et sensibilité sans SIMD
  dans l'état actuel (`_current`), confrontation. README : tableau, ordre, errata, paragraphe de C3, Nim et Rust
  échangés, langages relus.
* 2026-11-01, vers 12:37 : **machine 14**. La VM redémarre sur un hôte Emerald Rapids du même modèle (modèle 207,
  4 vCPU ; 2,72 à 2,80 GHz effectifs, latence à 4 Mio 34 ns, DRAM 15,2 Go/s : `results/hw/machine14/`, caractérisé
  après la campagne). Je ne l'ai vu qu'après les mesures de la remarque sur Odin, dont le plan nomme la machine 13.
* 2026-11-01, 12:53 : **plan de la remarque sur Odin** (`docs/ODIN.md`, sections 1 à 3, commit `1f023d3`), poussé
  avant les mesures. Vérifications sur les sources de la version mesurée (Odin dev-2026-10, commit `84bc3fc`,
  `/opt/src/odin`) et par des sondes (`tools/odin_check/`, `results/odin_check/`), sans consulter le site ni master :
  erratum C2 = 1 en règle v2 (le juge à l'aveugle notait 1 sous ma règle ; ma correction du 30 octobre avait baissé
  les deux règles en ne retenant que la couverture partielle de `core:simd/x86`) ; `@(fast_math)` sans effet dans la
  version mesurée (C4 reste 0) ; allocateur, horloge et chiffres du README exacts. Erreur de mon banc, plus large que
  la remarque : dix des quatorze noyaux d'Odin étaient inlinés dans leur boucle de mesure (la remarque ne l'avait vu
  que pour K1 aos), quand ceux de C sont `noinline` : correction (`bench/odin_fix`, `#force_no_inline`) mesurée et
  publiée. Q1 optimisé compté sans popcount mais conforme à l'algorithme de la référence : meilleure forme,
  sensibilité, comme `-o:aggressive`.
* 2026-11-01, 12:53:33-13:09:27 : **mesures de la remarque sur Odin** (`tools/measure_odin.py`, machine 14) : 99
  cellules × 7 processus (693) ; aucune somme de contrôle fausse ; 31 processus refaits pour vol de temps au-dessus de
  2 %, aucun gardé au-dessus (vol médian 0,27 %, maximum 1,99 %). Rien d'autre ne tournait. Écart au plan sur
  l'étiquette seulement : la VM avait redémarré vers 12 h 37 sur un hôte du même modèle (machine 14), avant les
  dernières vérifications ; le plan nomme la machine 13.
* 2026-11-01, 13 h 10 à 14 h : **résultats de la remarque sur Odin** (`results/report_odin.md`,
  `results/odin_check.json`, `results/odin_check/codegen.txt`). Classement publié : l'erratum C2 (règle v2) porte le
  contrôle d'Odin de 81,5 à 84,0 et son score de 72,6 à 73,5 ; il reste 3e (rang espéré 3,88 → 3,63), à égalité de
  fait avec C++ (3,61). **Écart au plan, décidé après avoir vu les rapports** : la correction du banc (noyaux isolés)
  n'est pas reportée sur les données principales. Ordre des calculs : j'ai d'abord appliqué le plan (règle du pont :
  74,2 points, 2e), vu que le pont se déclenchait sur K2 à 8 Mio et Q6 sans que la correction y change rien, refait le
  calcul par transfert seul (73,7, 2e ; interrompu), puis comparé le code machine : les boucles chaudes des noyaux
  isolés sont celles du binaire de la campagne (registres renommés près), pour Emerald Rapids comme pour Cascade Lake,
  sauf K1 aos, K5 naturel et des boucles externes de K9 (`tools/odin_check/codegen.py`). Les écarts mesurés sont donc
  des effets de placement (deux copies de la même boucle de K4 diffèrent de 8 % sur Cascade Lake et de 30 % sur cet
  hôte), et le pont ne tient pas pour un code inchangé (son écart au transfert vaut la variation du rapport Odin/C
  d'un hôte à l'autre) : le temps des données principales reste le meilleur estimateur. Les deux reports sont gardés
  en information (Fix-pont, Fix-T). Sensibilités : Q1 par popcount × 0,55 (74,3 points, 2e), `-o:aggressive`
  × 1,006 (73,3, 2e), `@(fast_math)` réparé hors règle (75,2, 2e) ; C reste 1er partout. Sorties recalculées :
  classement, figures, matrice, scénarios de Zig, de Julia, de Mojo, de C#, de Rust et de Nim et sensibilité sans SIMD
  dans l'état actuel (`_current`, témoin pointé sur le scénario Publié de `results/odin_check.json` ; Odin y passe
  1er à forme égale), confrontation. Leur règle du standard garde Odin C2 à 0,5 (`analysis/standard_rule.py`, comme
  le juge à l'aveugle sous cette règle) : elle partait de mes notes v2, et l'erratum s'y serait propagé. README :
  tableau, ordre, errata, paragraphe d'Odin (SIMD, Q1, allocateur, `map`, horloge), langages relus, limites.
* 2026-11-01, vers 14:42 : **machine 15**. La VM redémarre sur un hôte Emerald Rapids du même modèle (modèle 207,
  4 vCPU ; 2,63 à 2,64 GHz effectifs, latence à 4 Mio 35,7 ns, DRAM 14,8 Go/s : `results/hw/machine15/`, caractérisé
  avant la campagne de la remarque sur C++).
* 2026-11-01, 15:34 : **plan de la remarque sur C++** (`docs/CPP.md`, sections 1 à 3, commit `0ebe0af`), poussé avant
  les mesures. Vérifications par des sondes et sur les données (`tools/cpp_check/`, `results/cpp_check/`), sans
  consulter de page web : la décomposition de la remarque est exacte (K4 explique l'écart à C ; avec le K4 de C, C++
  aurait 80,03 points ; `unordered_map` ne pèse que 0,25 point), mais ni g++ (un compilateur par langage) ni la
  réallocation des grilles de K9 (la pratique de douze implémentations sur seize, la spécification n'impose que la
  réinitialisation hors chrono) ne sont des erreurs au sens de la règle commune. D2 et D4 tiennent chacun à un
  processus aberrant, D3 non (queue de C++ plus longue sur six processus sur sept). Erratum de la grille : C1 de C++
  à 0,5 en règle v1 (`std::simd` « highly experimental » dans GCC 16, `__cpp_lib_simd` non défini, x86 seulement,
  absent de libc++ 23) ; en règle v2, 1 par `vector_size`, comme C, justification explicitée. A6 reste 0. P2795
  (mise à zéro des variables locales en C++26 par GCC 16) ne touche aucune fonction de noyau. Décision : remesurer D2
  et D4 pour les 25 implémentations (7 processus, comme D3), publié ; clang++, formes de C et grilles de K9 allouées
  une fois en sensibilités ; C avec réallocation en information.
* 2026-11-01, 15:34:14-16:30:08 : **mesures de la remarque sur C++** (`tools/measure_cpp.py`, machine 15) : 245
  cellules × 7 processus (1 715), copies de C++ et de C (`results/raw_cpp/`) et remesure de D2 et D4 pour les 25
  implémentations (`results/raw_d24/`) mêlées dans chaque passe ; aucune somme de contrôle fausse ; 64 processus refaits
  pour vol de temps au-dessus de 2 % (3 deux fois), aucun gardé au-dessus (vol médian 0,22 %, maximum 1,98 %). Rien
  d'autre ne tournait.
* 2026-11-01, 16 h 30 à 17 h 30 : **résultats de la remarque sur C++** (`results/report_cpp.md`,
  `results/cpp_check.json`). Ordre des calculs : j'ai lu les rapports bruts, comparé le rapport C++/C de l'hôte à celui
  de Cascade Lake clé par clé, puis regardé la remesure de D2 et D4 ; j'ai lancé l'analyse du plan, et l'ai arrêtée
  après dix scénarios (`results/cpp_check/run1_plan.log`), quand les transferts ont montré leur artefact (C à 73,1 points
  dans S-clang).
  **Deux écarts au plan, décidés après avoir vu les données.** (1) La remesure de D2 et D4 n'est pas publiée : sur cet
  hôte, K2 à 8 Mio est bimodal (facteur 3,2 à 4,0 entre processus pour 21 implémentations sur 25) et la pénalité de
  désordre des langages à références est deux fois plus faible ; elle changerait ce que D2 et D4 mesurent (information :
  scénario P-D24). (2) Le transfert seul déplace les références de K4, K3 et K9 (le rapport C++/C de l'hôte s'écarte de
  celui de Cascade Lake de − 42 % à + 130 %) : les scénarios du plan sont donnés tels quels, et des variantes par le pont
  (C de Cascade Lake × rapport au C du même hôte, K3 inchangé) sont ajoutées, avec leurs propres limites. Classement
  publié : l'erratum C1 seul ; C++ garde 76,57 points mais passe du 2e au 3e rang espéré (3,61 → 3,80), derrière Odin
  (3,60), à égalité de fait (50 %). Sensibilités : K4 de clang++ par le pont prévu, 79,7 points contre 80,0 à C (devant
  C dans 49 % des variantes) ; toutes les corrections de la remarque par le pont, 78,9 contre 79,3 ; arène par
  pointeur, 77,6 ; formes de C, 76,1. Pratique d'allocation de K9 établie (C × 1,7 à 2,0 en réallouant ; C++ au temps
  de C en allouant une fois), décrite comme limite du protocole. Sorties recalculées : classement, figures, matrice,
  scénarios de Zig, de Julia, de Mojo, de C#, de Rust et de Nim et sensibilité sans SIMD dans l'état actuel (témoin
  pointé sur le scénario Publié de `results/cpp_check.json`), confrontation. Conséquences hors de C++ : sans SIMD
  explicite, à la lettre, C++ passe 7e derrière Odin (`docs/NOSIMD.md`, 4.8) ; sans K4 dans le plafond, C reprend la
  1re place à C++, à égalité ; la corrélation de rang avec le « Banc » passe de 0,77 à 0,78. README : tableau (Odin 2e,
  C++ 3e), ordre, errata, paragraphes d'Odin et de C++, langages relus, limites (compilateur, harnais de K9, D2 et D4),
  ces trois conséquences, Zig de développement 1er dans 49 % des variantes.
* 2026-11-01, vers 17:58 : **machine 16**. La VM redémarre sur un hôte Emerald Rapids du même modèle (modèle 207,
  4 vCPU ; 2,73 à 2,81 GHz effectifs, latence à 4 Mio 36,7 ns, DRAM 15,8 Go/s : `results/hw/machine16/`, caractérisé
  avant la campagne de la remarque sur C).
* 2026-11-01, 18:14 : **plan de la remarque sur C** (`docs/C.md`, sections 1 à 3, commit `a89dac6`), poussé avant les
  mesures. Vérifications par des sondes et sur les données (`tools/c_check/`, `results/c_check/`), sans consulter de
  page web : place de C, annexe gcc, C ISO pur, faits de la grille, pilier contrôle selon la règle exacts. Deux
  incohérences de la règle v1, corrigées dans le sens de son texte (½ pour « non standard mais livré avec la chaîne ») :
  A3 (`packed` par attribut) et C2 (`<immintrin.h>`, alors que E4 et D5, par le même en-tête, valaient ½) passent à ½
  pour C et C++ ; la remarque proposait de monter E4. Sur Cascade Lake, `k9_rows` de C par gcc et de C++ par g++ sont
  identiques : la pénalité du harnais de K9 s'y mesure (× 1,58 à quatre fils). Arène de K8 : état passé par la mémoire.
* 2026-11-01, 18:14:14-18:17:43 : **mesures de la remarque sur C** (`tools/measure_c.py`, machine 16) : 12 cellules
  × 7 processus (84) ; aucune somme de contrôle fausse, aucun processus refait (vol médian 0,31 %, maximum 1,63 %).
  Rien d'autre ne tournait ; pendant les mesures, seuls des fichiers ont été écrits, et poussés une fois (18:16:10).
* 2026-11-01, 18 h 20 à 19 h : **résultats de la remarque sur C** (`results/report_c.md`, `results/c_check.json`).
  Aucun écart au plan. Classement publié : les errata de la règle v1 ; scores inchangés, ordre inchangé ; C reste
  1er, moins nettement (rang espéré 1,90 → 2,20, 1er dans 52 % des variantes), Odin 2e (3,47), C++ 3e (4,16).
  Sensibilités : arène de K8 itérative + 4,1 points (C à la frontière de K8) ; harnais de K9 de la majorité, avec la
  pénalité de Cascade Lake, − 0,3 point (C reste 1er) ; règle v1 partout, C 1er ; « ISO seule », C 5e et Odin
  1er ; le tableau de la remarque se vérifie (C++ 1er avec le K4 de clang++ et le harnais de K9 de la majorité ; C
  1er avec en plus son arène itérative). Sorties recalculées : classement, figures, matrice, scénarios dans l'état
  actuel (témoin pointé sur le scénario Publié de `results/c_check.json`), confrontation. Conséquences hors de C :
  sans K4 dans le plafond, Zig passe 1er au rang espéré (2,65, devant C et C++, 2,79) ; sans SIMD explicite, à la
  lettre, C++ passe 9e (6,96, derrière Nim et Zig), et à forme égale Zig passe 3e devant C (`docs/NOSIMD.md`, 4.9) ;
  Zig de développement 1er dans 52 % des variantes ; Nim avec toutes ses versions optimisées 3e ; confrontation
  inchangée hors des rangs espérés. Rapport : colonne du contrôle en règle v1 complétée après coup
  (`analysis/c_check.py --report`, sans nouveau tirage). README : tableau, ordre, errata, paragraphes de C (ce qu'est
  le C classé, rangs selon la règle, arène de K8, harnais de K9) et d'Odin, 1re place de C selon le protocole, sans
  K4, Zig de développement, compilateur et arène de K8, langages relus, limites (versions optimisées, harnais de K9,
  sans SIMD), lecture et reproduction.
* 2026-11-01, 19:23 : **plan du harnais commun de K9** (`docs/K9.md`, sections 1 à 3), poussé avant les
  mesures. Décision de l'auteur de l'étude (« Oui harmonise le harnais K9 pour toutes les implémentations ») :
  révision du protocole, datée dans `docs/SPEC.md` (grilles allouées une fois par processus, réinitialisées hors
  chrono ; code chronométré et fils de `mt` inchangés). Inventaire lu dans les sources : C, C par gcc, Chapel et Ada
  allouaient une fois ; Fortran et JavaScript, sauf leur naturel ; toutes les autres implémentations réallouaient.
  Copies `bench/*_k9h` (`tools/k9h/`), identiques hors de la fonction de K9, compilées et validées. Mesures prévues
  sur la machine 16 (ancien harnais pour les 26 implémentations, harnais commun pour les copies, copies de
  sensibilité) ; K9 de toutes les implémentations viendra de la machine 16, comme K5 de la machine 3, avec les
  scénarios H-hôte (effet de l'hôte seul) et I-CL (transfert sur Cascade Lake) en information. Code d'analyse :
  `analysis/analyze_v2.py` (`apply_k9h`, `k9h_ratios`), `analysis/analyze_v3.py` (réplication, Cascade Lake seul),
  `analysis/k9_check.py`.
* 2026-11-01, 19:23:45-20:03:45 : **mesures du harnais commun de K9** (`tools/measure_k9h.py`, machine 16) : 143
  cellules × 7 processus (1 001), aucune somme de contrôle fausse ; 25 processus refaits pour vol de temps au-dessus de
  2 % (un deux fois), aucun gardé au-dessus (vol médian 0,39 %, maximum 2,00 %). Rien d'autre ne tournait ; pendant
  les mesures, seuls des fichiers ont été écrits, et poussés une fois (19:26:11, adaptation des scénarios de l'état
  actuel prévue au plan 3.5).
* 2026-11-01, 20 h 05 à 20 h 20 : **erreur de mon code d'analyse, avant toute publication.** Dans
  `analysis/analyze_v3.py`, la boucle ajoutée pour reporter le rapport du harnais de K9 sur la réplication réutilisait
  le nom `keys`, la liste des clés du score, que la simulation nulle de la réplication relit ensuite : toutes ses
  simulations ne gardaient plus que K9 et étaient écartées, et l'analyse s'arrêtait. Corrigé (variable renommée) ;
  la régénération a été relancée en entier. `analysis/k9_check.py` n'utilise pas ce code : ses résultats ne
  changent pas.
* 2026-11-01, 20 h 05 à 21 h : **résultats du harnais commun de K9** (`results/report_k9.md`, `results/k9_check.json`).
  Aucun écart au plan. À hôte égal, le harnais commun prend 0,41 à 0,65 fois le temps à quatre fils pour les compilés
  qui réallouaient (défauts de page divisés par 10), 0,73 à 0,99 pour les langages à ramasse-miettes, environ 1 pour
  les interprètes. Effet de l'hôte seul (H-hôte) : C renforcé (1er dans 66 % des variantes). Classement publié (K9 de
  la machine 16, harnais commun) : les cinq premiers ne bougent pas (C 79,94, 1er dans 49 % des variantes ; Odin,
  C++, Zig, C3) ; Rust et Nim, à égalité, échangent les 6e et 7e places ; Julia − 1,9 point. Réplication (machine 3) :
  C++, Rust, C. Information (I-CL) : la correction reportée sur Cascade Lake surcorrige (C 2e derrière Odin). Sorties
  recalculées : classement, figures, scénarios de l'état actuel (Zig, Julia, Mojo, C#, Rust, Nim), sensibilité sans
  SIMD, confrontation, sensibilités de la remarque sur C (`analysis/c_check.py --current`). README : tableau, ordre,
  révision, plafonds, paragraphes (C, Odin, C++, Zig, C3, Rust, Nim, Ada, Chapel, Julia), limites, lecture et
  reproduction ; `docs/SPEC.md`, `docs/FINDINGS.md`, `docs/CONFRONTATION.md`.

* 2026-11-02, 7 h 24 : **machine 17**. La VM redémarre sur un hôte Emerald Rapids du même modèle (modèle 207, 4 vCPU ;
  2,15 à 2,44 GHz effectifs, latence à 4 Mio 57 ns, DRAM 15 Go/s : `results/hw/machine17/`).
* 2026-11-02 : **remarque sur Java** transmise par l'utilisateur ; vérifications sans consulter de page web, sur le
  JDK 27.0.1 de l'étude, par des sondes et sur les données (`tools/java_check/`, `results/java_check/`). Exacts : place,
  piliers, en-têtes compacts, 78 octets (la somme de la remarque compte la référence deux fois), Valhalla, handicaps,
  K7 sur la machine 3, K10 (dans la remesure à 9 processus). Erreur de mon implémentation : K5 lisait ses vecteurs dans
  des tableaux du tas, à 12 octets de l'objet, quand toutes les autres implémentations à SIMD explicite alignent leurs
  données sur 64 octets (C# par la mémoire native). Erratum de la grille : F1 = ½ (`sequenceLayout` imbriqués, déjà
  crédités ½ en A7) ; A5 : texte corrigé, note ½ (règle FFM de toute la ligne). Inexact pour le JDK 27 : K9 optimisé
  « scalaire » (C2 le vectorise). Sensibilités : Q1 en une passe (Java a C1 = ½, hors de la classe de la règle de D),
  réserve de fils, K9 en Vector API, K7 isolé et par lots, K8 itératif, cases B3 et F2, libc. Plan (`docs/JAVA.md`,
  sections 1 à 3), copies (`tools/java_check/make_copies.py`, 30 cellules validées) et outil de mesure
  (`tools/measure_java.py`) poussés avant les mesures.
* 2026-11-02, 7:56:48-8:11:02 : **mesures de la remarque sur Java** (`tools/measure_java.py`, machine 17) : 280
  processus (40 cellules × 7), aucune somme de contrôle fausse ; 24 refaits pour vol de temps (trois deux fois), aucun
  gardé au-dessus de 2 % (vol médian 0,70 %). Le script d'analyse, l'erratum F1 et les contrôles de l'état actuel ont
  été poussés pendant les mesures, avant tout résultat (commit `4a5f53b`).
* 2026-11-02, vers 8:13 : **écart au plan** (commit `9a1f793`), décidé après avoir vu les ponts et avant tout score
  corrigé : un rapport de correction supérieur à 1 est ramené à 1. La règle du pont donnait × 1,085 à K1 soa (colonnes
  en cache L3 sur la machine 17, en mémoire sur Cascade Lake), un temps publié plus long pour un code 1,3 fois plus
  rapide sur le même hôte. Le calcul interrompu pour le corriger n'avait produit que les scénarios Avant et J-F1.
* 2026-11-02, 8:14 à 8:26 : **résultats de la remarque sur Java** (`results/report_java.md`). Correction : K5 tuned
  × 0,600 sur le même hôte (9,23 → 5,54 ms ; C 3,86), reporté par le pont (× 0,813 : 6,95 → 5,65 ms) ; K1 soa × 0,758,
  non reporté (écart au plan) ; témoins 1,01 à 1,02. Classement publié (J-E, avec l'erratum F1) : Java 47,15 points
  (46,14), 15e, devant Go dans 70 % des variantes (64 %) ; les autres langages ne bougent pas. Sensibilités : Q1 en
  une passe × 0,40 ; réserve de fils sans gain sur K6, × 0,81 sur K9 `mt` ; K9 en Vector API × 0,96 ; K7 isolé × 0,72,
  par lots × 0,80 ; K8 itératif × 0,64 ; toutes : 51,2 points ; avec les cases discutables et la libc : 53,9, toujours
  15e (à égalité avec C# au rang espéré).
* 2026-11-02, 8:27 à 9:05 : **sorties régénérées après la remarque sur Java** (`.work`, hors dépôt : même chaîne que
  pour K9) : classement, figures, matrice (`docs/CAPABILITIES.md`), scénarios de l'état actuel (Zig, Julia, Mojo, C#,
  Rust, Nim, confrontation, sans SIMD, remarque sur C) ; leurs contrôles reproduisent J-E à l'identique. Effets hors de
  Java : aucun changement de place au classement publié ; sans SIMD explicite, Java repasse devant Go à la lettre ;
  confrontation, Java 15e devant Go dans les scénarios C et D (Spearman 0,85 et 0,90). README : tableau, paragraphe de
  Java, errata, langages relus, versions optimisées, leçon sur le SIMD, limite des JIT, lecture et reproduction.
* 2026-11-02, 9 h 48 : **machine 18**. La VM redémarre sur un hôte Emerald Rapids du même modèle (modèle 207, 4 vCPU ;
  2,62 à 2,77 GHz effectifs, latence à 4 Mio 37 ns, DRAM 14 à 15 Go/s : `results/hw/machine18/`).
* 2026-11-02 : **remarque sur Go** transmise par l'utilisateur ; vérifications sans consulter de page web, sur les
  sources de go1.27.3, par des sondes et sur les données. Exacts : les faits du langage et de la matrice, l'artefact.
  Erreur de mon implémentation : K5 tuned (et les deux autres fonctions archsimd) passe d'AVX-512 à une réduction en
  SSE sans `ClearAVXUpperBits` (`VZEROUPPER`), que les compilateurs des autres langages émettent d'eux-mêmes ; 19 à
  27 ms → 7,4 ms avec une ligne. Défaut de ma mesure : toutes les variantes de Go étaient compilées avec
  `GOEXPERIMENT=simd`, et la préemption asynchrone de go1.27.3 restaure alors les registres ZMM sans `VZEROUPPER`
  (`runtime/preempt_amd64.s`) : K1 naturel 2,4 s contre 39 ms sur Emerald Rapids ; il touche la réplication et deux
  noyaux publiés depuis Emerald Rapids (K5 et K9), contrairement à ce qu'écrit la remarque. Sensibilités : K9 et Q1 en
  archsimd (Go a C1 = ½, hors de la classe de la règle de D), arène de K8 itérative, réduction de K5 dans les registres.
  Plan (`docs/GO.md`, sections 1 à 3), copies (`tools/go_check/make_copies.py`, 79 cellules validées) et outil de
  mesure (`tools/measure_go.py`) poussés avant les mesures.
* 2026-11-02, 10:07:12-10:38:43 : **mesures de la remarque sur Go** (`tools/measure_go.py`, machine 18) : 672
  processus (96 cellules × 7), aucune somme de contrôle fausse ; 26 refaits pour vol de temps (six deux fois), deux
  gardés au-dessus de 2 % après les deux reprises (2,72 et 2,08 %). Le script d'analyse et les deux points d'accroche du
  calcul publié (`ratios_k9h` appliqués après K9 de la machine 16, rapports de la réplication) ont été poussés pendant
  les mesures, avant tout résultat.
* 2026-11-02, 10:41 à 10:50 : **résultats de la remarque sur Go** (`results/report_go.md`). Aucun écart au plan.
  Transition AVX→SSE : K5 tuned × 0,384 (22,6 → 8,7 ms ; publié 18,86 → 7,24 ms), sans effet sur K1 soa et Q6 (un
  appel par répétition). Artefact : × 0,016 à 0,023 sur K1 naturel, aos et permuté ; 0,87 à 1,11 ailleurs ; clés
  publiées depuis Emerald Rapids peu touchées (K9 tuned × 0,820 par le pont, les autres 0,91 à 1,02). Classement
  publié (G-E) : Go 45,35 points (43,02), 16e, devant Java dans 43 % des variantes (30 %). Sensibilités : K9 en
  archsimd × 0,78 et 0,73, K8 itératif × 0,62 (pont 0,378), réduction de K5 dans les registres × 0,75, Q1 en une passe
  en archsimd plus lent (× 1,36) ; avec l'arène ou toutes les formes, Go passe 15e (47,6 à 49,2 points).
* 2026-11-02, 10:48 à 11:23 : **sorties régénérées après la remarque sur Go** (même chaîne que pour Java) :
  classement, figures, réplication (données de Go de la machine 3 corrigées : code naturel 5,8 → 10,7, score 37,3 →
  39,3, toujours 16e ; ordre de la réplication inchangé), scénarios de l'état actuel ; leurs contrôles reproduisent
  G-E à l'identique. Effets hors de Go : aucun changement de place au classement publié ; sans SIMD explicite, rien ne
  bouge (Java devant Go de 0,02 rang à la lettre) ; confrontation, Go devant Java dans le scénario C (Spearman 0,84).
* 2026-11-03, 12 h 00 : **machine 19**. La VM redémarre sur un hôte Emerald Rapids du même modèle (modèle 207, 4 vCPU ;
  3,02 à 3,18 GHz effectifs, latence à 4 Mio 55 ns, DRAM 10,6 à 12,7 Go/s : `results/hw/machine19/`).
* 2026-11-03 : **remarque sur Haskell** transmise par l'utilisateur ; vérifications sans consulter de page web, sur
  GHC 9.14.1 et LLVM 18.1.3, par des sondes et sur les données (`tools/haskell_check/`). Erreurs de mon
  implémentation : les options `-fno-omit-yields` (ajoutée sans justification) et `-fno-full-laziness` (redondante avec
  les `NOINLINE` et les `IORef` du harnais) sortent tout le programme du mode release annoncé par `docs/NATURAL.md`
  (K4 naturel 81 → 12 ms, K5 naturel 351 → 177 ms, K9 naturel 200 → 110 ms, un processus) ; K5 et K1 soa sans la
  FMA vectorielle `fmaddFloatX16#` de `GHC.Prim`, quand mon commentaire la disait absente ; l'arène de K8 alloue 1,6
  Go par répétition (une `IORef` d'entier boxé, un compteur rendu dans un n-uplet) contre « aucune allocation en
  régime permanent » ; l'arbre longue durée de K8 meurt avant la mesure. Errata de la matrice : B2, B3 et A7 à ½.
  Pas une erreur : `+RTS -N4` pour tous les noyaux, convention de l'étude (Julia est lancé avec `-t 4`) ;
  sensibilités : `-N1` pour les noyaux séquentiels, cases C2, E7 et F2. Écart à la pratique des remarques
  précédentes, décidé avant les mesures : report par transfert (le pont par le C est en information), parce que le
  rapport de Haskell à C d'un même binaire change d'un modèle d'hôte à l'autre (K4 naturel : 18 fois C sur Cascade
  Lake, 42 fois sur la machine 19). Plan (`docs/HASKELL.md`, sections 1 à 3), copies
  (`tools/haskell_check/make_copies.py`, 82 cellules validées), outil de mesure (`tools/measure_haskell.py`), script
  d'analyse et points d'accroche du calcul publié (latences de K8 naturel : `lat_ratios` ; réplication) poussés avant
  les mesures (commit `890b58c`) ; contrôles de l'état actuel pendant les mesures (commit `e54b69d`).
* 2026-11-03, 12:33:31-13:42:59 : **mesures de la remarque sur Haskell** (`tools/measure_haskell.py`, machine 19) :
  820 processus (118 cellules × 7, K7 naturel de `haskell_ref` et `haskell_fix` × 4), aucune somme de contrôle
  fausse ; 39 refaits pour vol de temps (quatre deux fois), aucun gardé au-dessus de 2 % (vol médian 0,58 %).
* 2026-11-03, 13:43 à 13:48 : **résultats de la remarque sur Haskell** (`results/report_haskell.md`). Aucun écart au
  plan ; le scénario Avant reproduit G-E à l'identique. Options (même hôte) : K4 naturel × 0,153, K5 naturel × 0,541,
  K9 naturel × 0,604, K7 tuned × 0,778, Q6 tuned × 0,854, K3 de 0,68 à 1,17 (placement) ; code : K5 tuned × 0,770
  (FMA), K8 tuned × 0,297 (arène sans allocation), K8 naturel × 1,031 (arbre gardé vivant) ; latences de K8 naturel :
  p99,9 × 0,80, maximum × 1,11. Classement publié (H-E, transfert et errata B2, B3, A7) : Haskell 41,28 points
  (34,47), 17e, Go devant dans 93 % des variantes (100 %) ; plafond 46,2, au-dessus de Go (44,5) ; aucun autre
  langage ne change de place. Sensibilités : `-N1` (K8 naturel × 0,69, p99,9 × 0,29) 42,1 ; cases C2, E7, F2 42,8 ;
  les deux 43,7, Go devant dans 73 %. Le pont par le C (information) aurait donné 42,9, avec des facteurs de 0,19 à
  7,3 importés de l'écart entre hôtes. Mécanisme de `-fno-omit-yields` vérifié dans l'IR de LLVM (en-tête de boucle en
  bloc séparé, état sur la pile Haskell).
* 2026-11-03, 13:48 à 14:17 : **sorties régénérées après la remarque sur Haskell** (même chaîne que pour Go) :
  classement, figures, matrice (`docs/CAPABILITIES.md`), réplication (données de Haskell de la machine 3 corrigées,
  latences de K8 comprises : score 29,2 → 34,7, toujours 17e ; ordre de la réplication inchangé), scénarios de l'état
  actuel ; leurs contrôles reproduisent H-E à l'identique. Effets hors de Haskell : aucun changement de place au
  classement publié, scores des autres langages de +0,004 à +0,026 point (le K3 `rmw_padded` corrigé de Haskell
  devient la référence de sa clé) ; sans SIMD explicite, à la lettre, Go passe devant Java (15,13 contre 15,17) ;
  confrontation, D repasse devant Nim dans le scénario B (Spearman 0,86). README : tableau, paragraphe de Haskell,
  grandes marches, errata, limites (langages relus, nombre de fils, bibliothèque standard, report par transfert),
  versions optimisées, lecture et reproduction ; `docs/NATURAL.md`, `docs/FINDINGS.md`, `docs/NOSIMD.md`,
  `docs/CONFRONTATION.md`.
* 2026-11-03, 15 h 02 : **machine 20**. La VM redémarre sur un hôte Emerald Rapids du même modèle (modèle 207, 4 vCPU ;
  2,93 à 3,19 GHz effectifs, latence à 4 Mio 55 ns, DRAM 12,2 à 12,9 Go/s : `results/hw/machine20/`).
* 2026-11-03 : **remarque sur OCaml** transmise par l'utilisateur ; vérifications sans consulter de page web, sur OCaml
  5.5.2 avec flambda, par la bibliothèque standard installée, le désassemblage et des sondes (`results/ocaml_check/`).
  Erreurs de mon implémentation : Q6 tuned branchait encore (`&&` en court-circuit) ; K1 aos appelait `pow` ; l'arène
  de K8 allouait deux références par requête ; l'horloge (`Unix.gettimeofday`) était murale et à la microseconde, quand
  `Runtime_events.Timestamp.get_current`, monotone et à la nanoseconde, est livrée depuis 5.4. Erratum : D5 à ½.
  Sensibilités : Q6 au masque de signe, arène par valeur, K7 à deux mots par case, K9 en `floatarray` (sans gain avec
  flambda), K5 à huit accumulateurs, E7. Plan (`docs/OCAML.md`, sections 1 à 3) : seules les clés dont le code change
  sont reportées, par transfert ; copies (`tools/ocaml_check/make_copies.py`, 79 cellules validées), outil de mesure
  (`tools/measure_ocaml.py`), script d'analyse, erratum et contrôles de l'état actuel poussés avant les mesures.
* 2026-11-03, 15:18:04-15:40:11 : **mesures de la remarque sur OCaml** (`tools/measure_ocaml.py`, machine 20) : 609
  processus (87 cellules × 7), aucune somme de contrôle fausse ; 14 refaits pour vol de temps, dont deux deux fois et
  gardés au-dessus de 2 % (2,2 et 3,3 %) ; vol médian 0,40 %.
* 2026-11-03, 15:40 à 15:47 : **résultats de la remarque sur OCaml** (`results/report_ocaml.md`). Aucun écart au
  plan ; le scénario Avant reproduit H-E à l'identique. Code (même hôte) : Q6 tuned × 0,409, `mt` × 0,467, K1 aos
  × 0,170, K8 tuned × 1,008 ; les 32 clés dont seule l'horloge change vont de 0,82 à 1,11 (moyenne géométrique 1,008 :
  placement, non reportées). Classement publié (O-E, transfert et erratum D5) : OCaml 23,80 points (24,01), 18e, rang
  plausible 18, Haskell devant dans 99,6 % des variantes ; plafond 18,4 → 19,1 (K6 seul : K1 prend soa), contrôle 24,7
  → 23,2 ; les scores des autres langages ne changent pas. Sensibilités : formes de la remarque 24,35 (masque de signe
  × 0,86 et 0,87, arène par valeur × 0,77, K7 à deux mots × 0,87, `floatarray` × 0,95 et 0,94, huit accumulateurs
  × 0,97), avec E7 à ½ 24,60, loin des 25,9 à 27,8 annoncés. Pont par le C (information) : écarts sous 25 %, transfert
  gardé pour les quatre clés. Une supposition de la section 2 d'OCAML.md (l'écart de K9 attribué, sans preuve, à OCaml
  4.14 sans flambda) est retirée, rayée et signalée (4.4).
* 2026-11-03, 15:49 à 16:18 : **sorties régénérées après la remarque sur OCaml** (même chaîne que pour Haskell) :
  classement, figures, matrice (`docs/CAPABILITIES.md`), réplication (données d'OCaml de la machine 3 corrigées :
  score 21,9 → 21,6, toujours 18e ; ordre de la réplication inchangé), scénarios de l'état actuel ; leurs contrôles
  reproduisent O-E à l'identique. Effets hors d'OCaml : aucun changement de score ni de place (rangs espérés à 0,0007
  près au classement publié, à 0,002 près dans la confrontation) ; sans SIMD explicite, OCaml reste 18e partout (27,8
  points dans le scénario symétrique, où K1 ne compte que par aos). README : tableau, paragraphe d'OCaml (les trois
  passages inexacts relevés par la remarque, deux chiffres dépassés), errata (et leur date, restée au 1er novembre),
  points 6 et 7 des résultats solides, limites (langages relus, report, versions optimisées), lecture et
  reproduction ; `docs/FINDINGS.md` (dont la taille de la particule d'OCaml), `docs/NOSIMD.md`,
  `docs/CONFRONTATION.md`.
* 2026-11-03, 17 h 13 : **machine 21**. La VM redémarre sur un hôte Emerald Rapids du même modèle (modèle 207, 4
  vCPU ; 2,95 à 3,19 GHz effectifs, latence à 4 Mio 55 ns, DRAM 12,7 à 13,3 Go/s : `results/hw/machine21/`).
* 2026-11-03 : **remarque sur JavaScript** transmise par l'utilisateur ; vérifications sans consulter de page web, sur
  Node.js 26.12.1 (et Node.js 22.22.0, Bun 1.4.4), par le code machine de TurboFan (`--print-opt-code`) et des sondes
  (`results/js_check/`). Erreur de mon implémentation : K7 tuned en cases de 32 octets, quand toutes les
  implémentations qui disposent la mémoire en prennent 16 (Java en tassant clé et compteur dans un `long`). Par la
  même règle, **erreur de mon classement pour OCaml** : son K7 à deux mots, mis en sensibilité au motif faux que les
  autres n'atteignaient 16 octets que par des champs de 32 bits, passe au classement publié avec le rapport déjà
  mesuré sur la machine 20 (× 0,875 ; `analysis/ocaml_check.py` rejoué : O-E 23,92 points contre 23,80, toujours 18e ;
  `docs/OCAML.md`, 4.8 ; sorties publiées régénérées à la fin de la remarque sur JavaScript). Errata : E1 = 1
  (`--print-opt-code` marche avec le binaire officiel), A4 = E6 = ½ (`node:ffi`, comme `ctypes` en Python). Texte :
  les 416 octets sont ceux de V8 sans compression de pointeurs. Sensibilités : Q6, K9, K8 naturel (site d'allocation
  distinct, contre le pretenuring de V8), K8 itératif, K5 et K1 soa en f64, cases C1, E2, A1, A2, A7. Q1 sous Node 22
  en information (Node 26 deux fois plus lent, Turbolev n'y étant pour rien). Plan (`docs/JAVASCRIPT.md`, sections 1 à
  3) : copies (`tools/js_check/make_copies.py`, 24 cellules validées), outil de mesure (`tools/measure_js.py`), script
  d'analyse (`analysis/js_check.py`), errata et réplication poussés avant les mesures.
* 2026-11-03, 17:45:01-17:50:43 : **mesures de la remarque sur JavaScript** (`tools/measure_js.py`, machine 21) : 175
  processus (25 cellules × 7), aucune somme de contrôle fausse, aucun refait pour vol de temps (vol médian 0,68 %).
* 2026-11-03, 17:51 à 17:58 : **résultats de la remarque sur JavaScript** (`results/report_js.md`). Aucun écart au
  plan ; le scénario Avant reproduit O-E (avec le K7 d'OCaml) à l'identique. Correction : K7 tuned × 0,577
  [0,541–0,618] (cases de 16 octets ; clés témoins au code identique : 0,969 et 0,971). Classement publié (J-E,
  transfert et errata E1, A4, E6) : JavaScript 15,64 points (14,27), 19e, rang plausible 19, OCaml devant dans 99,5 %
  des variantes, Python derrière dans 95,5 % (92,8 %) ; plafond 11,4 → 12,2, contrôle 11,6 → 14,6 ; les scores des
  autres langages ne changent pas. Sensibilités : Q6 × 0,60 et 0,65, K9 × 0,88 et 0,83, K8 naturel × 0,62 avec ses
  latences (pire pause 81,6 → 1,1 ms : le pretenuring de V8), K8 itératif × 0,73, K5 en f64 × 0,88, K1 soa en f64 sans
  gain ; S-mesures 17,84, S-cases 18,40, S-tout 20,60 (OCaml devant dans 83,5 %). Information : Q1 sous Node 22 × 0,41
  (tuned) et × 0,50 (naturel) par rapport à Node 26. Pont par le C : écart de 22,7 %, transfert gardé.
* 2026-11-03, 17:59 à 18:26 : **sorties régénérées après les remarques sur OCaml (K7) et JavaScript** (même chaîne) :
  classement, figures, matrice (`docs/CAPABILITIES.md`), réplication (machine 3 : JavaScript 12,9 → 14,2, OCaml 21,6 →
  21,7 ; ordre inchangé), scénarios de l'état actuel ; leurs contrôles reproduisent J-E à l'identique. Effets hors de
  JavaScript et d'OCaml : aucun changement de score ni de place ; dans les étages de la v3, JavaScript forme désormais
  un étage à lui seul, devant Python et Lua ; sans SIMD explicite, rien ne bouge (Chapel 1er à la lettre dans 46 % des
  variantes, contre 45) ; confrontation : Spearman inchangés, accord du principe P11 0,66 → 0,65. README : tableau
  (OCaml 23,9, JavaScript 15,6, Python 20–21), paragraphes d'OCaml et de JavaScript (code de K5, 416 octets, appels
  atomiques de V8, Q1 sous Node 26, pretenuring, WebAssembly exclu), grandes marches, errata, point 6 des résultats
  solides, limites (langages relus, versions optimisées, report, échauffements des JIT), lecture et reproduction ;
  `docs/FINDINGS.md` (416 octets corrigé, section JavaScript), `docs/NOSIMD.md` (4.15), `docs/CONFRONTATION.md`,
  `docs/JAVASCRIPT.md` (4), `docs/OCAML.md` (4.8).
* 2026-11-05, 7 h 59 : **machine 22**. La VM redémarre sur un hôte Cascade Lake du même modèle que celui des données
  principales (modèle 85, 4 vCPU, un fil par cœur ; 3,05 à 3,18 GHz effectifs, latence 25 ns à 4 Mio et 201 ns à 1
  Gio, DRAM 10,7 à 12,4 Go/s : `results/hw/machine22/`) ; les 24 fichiers d'entrée correspondent à
  `env/msdata.sha256`.
* 2026-11-05 : **remarque sur Python** transmise par l'utilisateur ; vérifications sans consulter de page web, sur
  CPython 3.15.2 (build par défaut et build sans GIL, ceux de l'étude), par des sondes (`tools/python_check/probes/`,
  `results/python_check/`) et les données publiées. Erreur de mon implémentation : K3 (quatre variantes), K6 `mt` (Q6,
  Q1) et K9 `mt` tournent sur des fils que le GIL sérialise, alors que la spécification exige de vrais fils parallèles
  et que la bibliothèque standard en donne par ses sous-interpréteurs (`concurrent.interpreters`, données partagées par
  `memoryview`), comme Mojo (module privé) et JavaScript (Workers) en obtiennent de leur chaîne ; dans l'annexe
  `python_ft`, l'`array` partagé de K3 sérialise aussi les fils par son verrou d'objet. Errata : B1 = 1 (le collecteur
  de cycles se désactive, comme celui d'ORC pour Nim), F3 = ½ (types `ctypes` de largeur fixe qui enveloppent, masques,
  comme JavaScript) ; D1 reste ½ (note complétée), B2 reste 0 (discutable). Sensibilités : Q6 en colonnes
  (`bytes.translate`, entiers longs, `bytes.find`), K8 naturel avec `gc.freeze()` (pire pause 763 → 7,4 ms à la
  validation), build sans GIL pour les noyaux parallèles (borne haute : son surcoût sur les noyaux séquentiels est de
  − 15 à + 59 % ici, non de 1 à 8 %), cases B2 = ½ et D1 = 1. Plan (`docs/PYTHON.md`, sections 1 à 3) : copies
  (`tools/python_check/make_copies.py`, 27 cellules validées, puis les deux variantes en colonnes), outil de mesure
  (`tools/measure_python.py`), script d'analyse (`analysis/python_check.py`), errata et réplication poussés avant les
  mesures.
* 2026-11-05, 8:48:28-10:15:42 : **mesures de la remarque sur Python** (`tools/measure_python.py`, machine 22) : 231
  processus (33 cellules × 7), aucune somme de contrôle fausse, un processus refait pour vol de temps, aucun gardé
  au-dessus de 2 % (vol médian 1,11 %).
* 2026-11-05, 10:16 à 10:24 : **résultats de la remarque sur Python** (`results/report_python.md`). Aucun écart au
  plan ; le scénario Avant reproduit J-E à l'identique. Correction : K3 espacé × 0,323 et 0,308, tassé × 0,699 et
  0,902, K6 `mt` × 0,371 et 0,343, K9 `mt` × 0,515 (clé témoin : 1,016). Classement publié (P-E, transfert et errata
  B1, F3) : Python 11,83 points (9,94), 20e, rang plausible 19 à 21, devant Lua dans 72,4 % des variantes (62,5 %),
  JavaScript devant lui dans 91,1 % (95,5 %) ; contrôle 24,4 → 29,7, plafond 0,46 → 0,59 ; les scores des autres
  langages ne changent pas. Build sans GIL (K3 par une vue propre à chaque fil) : il ne bat les sous-interpréteurs sur
  aucune clé, et S-FT se confond avec P-E. Sensibilités : Q6 en colonnes × 0,354 (`mt` × 0,286), K8 naturel avec
  `gc.freeze()` × 0,800 et pire pause 752 → 9,0 ms ; S-mesures 12,04, S-cases 13,06, S-tout 13,26. Pont par le C :
  écarts de 22,6 à 182 % au transfert, qui reste la règle (P-E-P 11,88).
* 2026-11-05, 10:24 à 11:11 : **sorties régénérées après la remarque sur Python** (même chaîne ; la tâche de fond qui
  les enchaînait a été arrêtée par sa limite de temps juste après l'étape de Rust, et la dernière,
  `analysis/c_check.py --current`, relancée seule de 11:05 à 11:11) : classement, figures, matrice
  (`docs/CAPABILITIES.md`), réplication (machine 3 : Python 10,1 → 12,0, toujours 20e ; ordre inchangé, Spearman
  0,93), scénarios de l'état actuel ; leurs contrôles reproduisent P-E à l'identique. Effets hors de Python : aucun
  changement de score ni de place ; rangs espérés de Lua + 0,10, de JavaScript + 0,04, des autres 0,01 au plus ; dans
  les étages de la v3, JavaScript rejoint Python et Lua (quatre étages au lieu de cinq) ; sans SIMD explicite, rien ne
  bouge ; confrontation : sous leur règle, la pénalité de K3 de Fortran et de Mojo, le temps de Python, s'allège
  (plafond 32,2 → 37,3 et 29,9 → 34,7 ; Fortran passe devant C# dans le scénario C, Spearman 0,84 → 0,82), accord du
  principe P7 0,94 → 0,93. README : tableau (JavaScript 19–20 et 91 % ; Python 11,8, 19–21, 72 %), paragraphe de
  Python (ce que mesure le classement, sous-interpréteurs, build sans GIL, poids du contrôle), errata, grandes
  marches, point 6 des résultats solides, limites (langages relus, versions optimisées, règle de la bibliothèque
  standard pour Python, PyPy), lecture et reproduction ; `docs/FINDINGS.md` (section Python, fils de K3),
  `docs/NOSIMD.md` (4.16), `docs/CONFRONTATION.md`, `docs/PYTHON.md` (4).
* 2026-11-05, 12 h 23 : **machine 23**. La VM redémarre sur un hôte Cascade Lake du même modèle que celui des données
  principales (modèle 85, 4 vCPU, un fil par cœur ; 3,04 à 3,22 GHz effectifs ; latence 25 ns jusqu'à 2 Mio, 137 ns
  dès 4 Mio : la VM n'a qu'une part du L3 ; DRAM 11,7 Go/s : `results/hw/machine23/`) ; les 24 fichiers d'entrée
  correspondent à `env/msdata.sha256`.
* 2026-11-05 : **remarque sur Lua** transmise par l'utilisateur (Lua était le seul langage jamais relu) ; vérifications
  sans consulter de page web, sur PUC-Lua 5.5.1 et LuaJIT 2.1.1792588164 (documentation livrée avec ses sources), par
  des sondes, le bytecode (`luac -l`) et les données publiées (`tools/lua_check/probes/`, `results/lua_check/`).
  Erreurs de mon implémentation : K3 (trois compteurs « espacés » dans la partie hachée de la table : le « faux
  partage × 0,63 » de Lua, sans fils, venait de là), K4 (octets décodés par `string.byte` dans la boucle
  chronométrée, quand les autres noyaux décodent leurs fichiers en tables hors chrono), Q6 tuned et `mt` (le masque
  annoncé branche : `cond and 1 or 0` compile en sauts ; corrigé par le bit de signe, comme le Q6 d'OCaml l'avait été),
  et, en sens inverse, K8 naturel (nœuds positionnels `{v, false, false}` au lieu de l'enregistrement à champs nommés,
  le type par défaut) ; par la même règle, **erreur de mon implémentation pour Python** : son K8 naturel déclarait
  `__slots__`, une annotation de performance (corrigé par `analysis/python_check.py` rejoué après la campagne ; P-E-511
  garde le P-E du matin). Errata : B4 = ½ (l'arithmétique n'alloue pas ; fermetures, chaînes et croissance des tables
  allouent, comme pour D) et B3 = ½ (nombres non boxés, retours multiples sur la pile de la VM, comme les n-uplets non
  boxés de Haskell). Sensibilités : Q6 par tests imbriqués, K9 aux voisins glissants, K7 tassé dans une table, K8
  tuned itératif, K1 `soa` au 0,5 sorti, K2 décalé, A8 = ½ (`string.pack`, en lecture seule), et LuaJIT à la place de
  PUC-Lua, avec la grille de Lua ou sa FFI notée comme `ctypes` (K3 conforme interprété : son code compilé ignore
  `volatile`). Plan (`docs/LUA.md`, sections 1 à 3) : copies (`tools/lua_check/make_copies.py`, 48 cellules validées),
  outil de mesure (`tools/measure_lua.py`), scripts d'analyse (`analysis/lua_check.py` ; `analysis/python_check.py`
  pour le K8 de Python), errata et réplication poussés avant les mesures.
* 2026-11-05, 13:03:10-14:07:34 : **mesures de la remarque sur Lua** (`tools/measure_lua.py`, machine 23) : 364
  processus (52 cellules × 7), aucune somme de contrôle fausse, sept processus refaits pour vol de temps (deux deux
  fois), aucun gardé au-dessus de 2 % (vol médian 0,63 %).
* 2026-11-05, 14:07 à 14:27 : **résultats de la remarque sur Lua** (`results/report_lua.md`). Aucun écart au plan.
  `analysis/python_check.py` rejoué d'abord : K8 naturel de Python sans `__slots__` × 1,061 [1,026–1,099], pire pause
  × 1,29 ; P-E 11,833 → 11,830, toujours 20e ; ses contrôles reproduisent J-E et le P-E du matin (P-E-511) à
  l'identique. Puis `analysis/lua_check.py`, dont le scénario Avant reproduit le P-E rejoué à l'identique. Corrections :
  K3 espacé × 0,716 et 0,735 (serré dans le bruit), K4 × 0,354, 0,275 et 0,316, Q6 tuned × 0,742 et `mt` × 0,772,
  K8 naturel × 1,436 (latences × 1,27 à 1,58) ; clé témoin 1,069 [1,013–1,124]. Classement publié (L-E, transfert et
  errata B3, B4) : Lua 5,41 points (3,92), 21e, rang plausible 20 à 21, Python devant dans 58,3 % des variantes
  (72,1 %) ; contrôle 2,8 → 6,8, plafond 1,08 → 1,31. Sensibilités : Q6 imbriqué × 0,51 et 0,49, K7 tassé × 0,71, K9
  × 0,87 et 0,96, K1 × 0,83, K2 × 0,77 à 0,97, arène itérative plus lente ; S-mesures 5,78, S-cases (A8) 5,96, S-tout
  6,33. LuaJIT à la place de PUC-Lua : 11,12 points avec la grille de Lua (20e, devant Python dans 79 % des
  variantes), 15,85 avec sa FFI notée comme `ctypes` (19e, devant JavaScript dans 52,5 %). Pont par le C : écarts de
  110 et 204 % sur K3 (l'hôte), transfert gardé (L-E-P 5,49).
* 2026-11-05, 14:27 à 15:11 : **sorties régénérées après la remarque sur Lua** (même chaîne, 2 612 s, lancée en tâche
  de fond avec un délai suffisant) : classement, figures, matrice (`docs/CAPABILITIES.md`), réplication (machine 3 :
  Lua 4,38 → 5,86, toujours 21e ; Python 11,985 → 11,983 ; ordre inchangé, Spearman 0,93), scénarios de l'état actuel
  ; leurs contrôles reproduisent L-E à l'identique. Effets hors de Lua : aucun changement de score ni de place, hors
  Python (− 0,004) ; étages inchangés ; sans SIMD explicite, rien ne bouge ; confrontation inchangée (Lua n'est pas
  dans l'autre étude). README : tableau (Lua 5,4 ; Python devant Lua dans 58 %), paragraphes de Python et de Lua
  (PUC-Lua sans son API C, piliers mesurés contre pilier jugé, LuaJIT), errata, limites (les 21 langages relus,
  versions optimisées), lecture et reproduction ; `docs/FINDINGS.md` (section Lua), `docs/NATURAL.md` (K8 de Python
  et de Lua), `docs/NOSIMD.md` (4.17), `docs/CONFRONTATION.md`, `docs/PYTHON.md` (4.8), `docs/LUA.md` (4).
* 2026-11-05, 15:19 à 16:03 : **ajout de Swift, à la demande de l'auteur** (`docs/SWIFT.md`). Chaîne : Swift 6.4.2
  (dernière version stable le 5 novembre ; archive et signature vérifiées), LLVM de la chaîne (clang 21). Mode release
  vérifié sur un paquet de `swift package init` : `-O -whole-module-optimization -swift-version 6` ; le banc ajoute
  `-target-cpu native`. Dix noyaux (`bench/swift/ms.swift`), copies de sensibilité `bench/swift_exp` (K8 en classe
  finale à champs `let`) et `bench/swift_ou` (`-Ounchecked`), 51 cellules validées. Faits relevés en écrivant le code
  (`tools/swift_check/facts.sh`) : conversions SIMD de la bibliothèque non inlinées, comparaisons vecteur contre scalaire
  compilées voie par voie, `sum()` dans l'ordre des voies, ni `pause` ni préchargement (intrinsèques sans corps
  inutilisables), module Glibc sans extensions GNU (pas d'affinité), `inout` sans `noalias`, `AsyncStream` à 14–19 s
  pour K10 naturel (hors score). Grille notée par une sonde exécutée (`probes/swift`, 36 lignes), sans case changée en
  règle v2 ; ligne de Swift dans `docs/NATURAL.md`. Plan (`docs/SWIFT.md`, sections 1 à 3) poussé avant les mesures :
  Swift 22e langage classé, relié aux données publiées par le pont du C (machine 23 : même modèle que la machine 1 ;
  K5, K9 et les latences de K8 viennent d'Emerald Rapids), tirages isolés ; outil de mesure `tools/measure_swift.py`
  (73 cellules × 7 passes), script d'analyse `analysis/swift_check.py` écrit pendant la campagne.
* 2026-11-05, 16:04:32-16:27:23 : **mesures de l'ajout de Swift** (`tools/measure_swift.py`, machine 23) : calibration
  de Swift (une répétition par cellule, règle du pilote), puis 511 processus (73 cellules × 7, 16:05:35-16:27:22),
  aucune somme de contrôle fausse, neuf processus refaits pour vol de temps, aucun gardé au-dessus de 2 % (vol médian
  0,31 %) ; empreinte de K1 (3 processus, 64,02 octets par particule) ; C3 mesurée après (`tools/c3_measure.py swift` :
  K4 et K9 naturels scalaires, C3 = 0).
* 2026-11-05, 16:28 à 17:04 : **résultats de l'ajout de Swift, sorties régénérées** (`analysis/swift_check.py`, puis
  la chaîne publiée : classement, réplication, figures, matrice, états actuels). Contrôles : le scénario Avant (Swift
  retiré) reproduit L-E de `results/lua_check.json` à l'identique (écart 0,0), et les états actuels de la sensibilité
  sans SIMD et de la remarque sur C reproduisent S-E à l'identique. Swift **12e sur 22** (65,24 points [63,97–66,40],
  rang espéré 11,01, rang plausible 6 à 14) ; contrôle 64,4 (14e), plafond 79,4 (6e), code par défaut 43,8 (12e).
  Les 21 autres gardent leur ordre et leurs scores ; ceux que Swift devance reculent d'un rang ; les précédences entre
  eux bougent de 2,4 points au plus (Swift devient, dans une partie des tirages, la référence du code naturel de K1).
  Sensibilités du plan : 11e à 13e ; S-direct 6e (information, biaisé : la machine 1 était plus lente pour tous les
  codes) ; S-hôte (hors plan, facteur d'hôte des autres langages) 13e, 60,77 points. Réplication : Swift 12e sur la
  machine 3, par le pont ; accord et test nul (sur les 21 langages répliqués indépendamment) inchangés ; étages
  [14, 4, 1, 3]. Corrigé en cours de route : les clés reliées à la machine 3 étaient contrôlées avec les bornes de la
  machine 1, ce qui écartait K1 `soa` de Swift (plafond 39,1 sur la machine 3, étages [18, 1, 3]) ; elles le sont
  désormais avec les bornes de l'hôte cible (`docs/SWIFT.md`, 4.6). Sans SIMD explicite (`docs/NOSIMD.md`, 4.18) :
  Swift 13e dans les trois lectures, 10e sans intrinsèques importées. Confrontation : rangs des 18 langages communs,
  corrélations et accords inchangés.
* 2026-11-05, 17:05 à 17:25 : **README et documents après l'ajout de Swift**. README : titre, tableau à 22 lignes,
  paragraphe de Swift, renumérotation ; chiffres recalés sur les sorties régénérées (précédences et rangs moyens de
  l'ordre, parts en tête, scénarios de C, de Zig, de Mojo, de C#, de Julia, de Nim et sans SIMD explicite) ; places
  citées dans l'historique des errata remplacées par « sans changer de place ». Les chiffres sur « les 13 premiers »
  portent désormais sur les langages classés devant C#, 14 avec Swift (`analysis/readme_figures.py` généralisé :
  R² 0,74, voisins 46 à 75 %, tous devant C# dans au moins 96 % des variantes). Au passage, quatre chiffres du README
  faux avant l'ajout, corrigés : Nim avec Q1 en intrinsèques passe 6e, et non 5e, depuis la remarque sur Haskell
  (d'où « une place », et non deux, dans les limites) ; sans K4 au plafond, C++ a 80,1 points et Zig 75,6 (80,0 et
  75,5 étaient tronqués) ; Odin devance C++ dans 55 % des variantes, et non 56 % comme l'écrivait son paragraphe.
  `docs/FINDINGS.md` (section Swift), `docs/SWIFT.md` (4.1 retouché, 4.5 à 4.7, erratum du point 8 de 2.4 : le test
  d'unicité du stencil naturel est fait à chaque écriture), `docs/NOSIMD.md` (4.18), `docs/CONFRONTATION.md`,
  `docs/CAPABILITIES.md` (colonne et section de Swift, rien d'autre ne change), `env/toolchains.txt`.
* 2026-11-05, 20 h 09 : **machine 24**. La VM redémarre sur un hôte Emerald Rapids du même modèle que les machines 3,
  11 et 16 (modèle 207, 4 vCPU ; 3,13 à 3,43 GHz effectifs ; latence 32 ns à 2 Mio, 56 ns à 4 Mio ; DRAM 13,5 Go/s :
  `results/hw/machine24/`) ; les 24 fichiers d'entrée correspondent à `env/msdata.sha256`.
* 2026-11-05, 20:15 à 20:45 : **remarque sur Swift, transmise par l'auteur ; vérification et plan** (`docs/SWIFT.md`,
  section 5, poussé avant les mesures). Faits vérifiés sur la chaîne installée, sans page web
  (`tools/swift_rq/facts.sh`, `results/swift_check/facts2.txt`) : D4 (affinité par le module Glibc avec
  `-Xcc -D_GNU_SOURCE`, fil épinglé : ma sonde ne définissait pas `_GNU_SOURCE`), préchargement (`_m_prefetchw`
  importée `[readnone]`, supprimée ; `@_silgen_name("llvm.prefetch.p0")` donne `prefetchw`, et `pause` de même),
  `noalias` sur les seuls `inout` de type pointeur, `@specialized` et `@inline(always)` sans option, `@const`
  expérimental, types de la 6.4, arbre en `UniqueBox` (mémoire épuisée sans `deinit {}` vide), K4 en `&+=` vectorisé et
  en `-Ounchecked` scalaire, comptages de références de K8, alignement. Provenance : le C recompilé ici en cible native
  est identique au binaire de la machine 3 (`ca4eeb97…`), en cible cascadelake au binaire publié (`ff81685a…`).
  Décisions fixées d'avance : errata D4 (½ en v1, 1 en v2) et E4 (½), K5, K9 et les latences de K8 reliés par les
  rapports mesurés sur la machine 24 dans la construction de leurs données publiées, réplication reliée par les
  constructions natives de la machine 24 ; copies `bench/swift_er`, `bench/c_er`, `bench/swift_ub` validées ; outil
  `tools/measure_swift_er.py` (72 cellules × 7 passes).
* 2026-11-05, 20:43:13-20:56:33 : **mesures de la remarque sur Swift** (`tools/measure_swift_er.py`, machine 24) :
  504 processus (72 cellules × 7), aucune somme de contrôle fausse, huit processus refaits pour vol de temps, aucun
  gardé au-dessus de 2 % (vol médian 0,14 %, maximum 1,82 %). Pendant la campagne, seule l'intégration à l'analyse a
  été écrite (pont par clé et par campagne dans `analysis/analyze_v2.py`, réplication et « Cascade Lake seul » dans
  `analysis/analyze_v3.py`, `analysis/swift_remark.py`), sans rien exécuter.
* 2026-11-05, 20:58 à 21:21 : **résultats de la remarque sur Swift, sorties régénérées** (`analysis/swift_remark.py`,
  puis la chaîne publiée). Contrôles : le scénario Avant reproduit S-E de `results/swift_check.json` à l'identique
  (0,0) ; les états actuels de la sensibilité sans SIMD et de la remarque sur C reproduisent R-E à l'identique.
  Swift / C sur Emerald Rapids : K5 naturel 0,50, K9 naturel 5,0, Q1 optimisé 1,03 (1,13 avec le code de Cascade
  Lake). Errata D4 (½ en v1, 1 en v2) et E4 (½) : + 1,3 point ; pont de la machine 24 : − 0,08 point (plafond + 1,0,
  code par défaut − 1,8 par les queues de latence de K8). Swift **11e sur 22** (66,46 points, rang espéré 10,69,
  devant Fortran dans 54 % des variantes) ; plafond 80,3 (3e), contrôle 68,1 (13e), code par défaut 42,0 (15e).
  Sensibilités : 11e ou 12e (chacune des deux lectures de la remarque, E4 = 0 ou D4 = ½ en v2, le laisse 12e de
  justesse). Réplication : Swift 11e sur la machine 3 ; accord, test nul et étages inchangés. Les 21 autres gardent
  leurs scores ; rangs espérés bougés de 0,19 au plus ; Fortran passe 12e.
* 2026-11-05, 21:05 à 21:30 : **README et documents après la remarque sur Swift**. README : tableau (Swift 11e,
  Fortran 12e), ordre (Swift derrière Chapel malgré un meilleur score), errata, paragraphes de Swift (3e plafond,
  contrôle, code par défaut, pont, relecture), de Chapel (6e plafond), de Fortran et de Julia (sensibilité : 12e, et
  11e avec K5 en 512 bits), parts en tête et figures (`analysis/readme_figures.py`), scénarios de C, de Zig et de Mojo
  (Mojo 13e sans K4 au plafond), machines, limites (pont, relecture des 22 langages, sans SIMD explicite),
  reproduction ; au passage, le rang moyen d'Odin en règle v1 cité dans le paragraphe de C (2,74, resté de l'état
  d'avant l'ajout de Swift) est mis à jour. `docs/SWIFT.md` (5.4, 5.5), `docs/FINDINGS.md`, `docs/NOSIMD.md` (4.19),
  `docs/CONFRONTATION.md`, `docs/CAPABILITIES.md` (D4 et E4 de Swift), sonde de Swift (`results/probes/swift.txt`).
* 2026-11-06, 07 h 47 : **machine 25**. La VM redémarre sur un hôte Emerald Rapids du même modèle que les machines 3,
  11, 16 et 24 (modèle 207, 4 vCPU), mais plus lent : 2,76 à 2,83 GHz effectifs (3,13 à 3,43 sur la machine 24) ;
  latence 21 ns à 2 Mio, 35 ns à 4 Mio, 129 ns à 32 Mio ; DRAM 14,8 Go/s (`results/hw/machine25/`) ; les 24 fichiers
  d'entrée correspondent à `env/msdata.sha256`.
* 2026-11-06, 07:50 à 08:55 : **ajout de FreePascal, demandé par l'auteur ; chaîne, implémentation, grille, faits et
  plan** (`docs/FPC.md`, sections 1 à 3, poussé avant les mesures). Free Pascal 3.2.2, la dernière version publiée
  (archive identique sur freepascal.org et SourceForge, SHA-256 `5adac308…`), dans `/opt/fpc` ; banc en `-O3` avec la
  cible la plus haute que connaît FPC (`COREAVX2`, sans AVX-512) et le traitement vectoriel `-Sv` pour K1 `soa` et K5
  seulement ; les 41 cellules et les 13 des copies (`bench/fpc_exp`, `bench/fpc_scal`, `bench/fpc_o2`) validées.
  Faits relevés sans page web (`tools/fpc_check/facts.sh`) : aucune vectorisation automatique ; `-Sv` limité à 128 bits
  (erreur interne pour 8 `Single`, opérandes à aligner sur 16 octets) ; accumulateur de K5 naturel sur la pile ;
  `TDictionary` à 30 ns par recherche en cache et 200 ns sur 1 M de clés ; atomiques et barrières en procédures de la
  RTL ; `-O4` réordonne les champs des classes. Grille (`probes/fpc`) : pilier C de 58,5 (v1, C3 = 0) et 60,5 (v2).
  Décisions fixées d'avance : toutes les clés mesurées sur la machine 25 et reliées par le C dans la construction de
  leurs données publiées (Cascade Lake pour les clés des machines 1, 11 et 16, native pour K5 et la réplication) ; le
  pont des clés de la machine 1 traverse les modèles, contrôlé par un second témoin (`bench/c_gcc_cl`, gcc en cible
  cascadelake, identique au binaire publié de `c_gcc`) et par un facteur d'hôte unique ; un générateur par langage
  ajouté (Swift garde le sien) ; outil `tools/measure_fpc.py` (132 cellules × 7 passes).
* 2026-11-06, 08:52:29-09:20:57 : **mesures de l'ajout de FreePascal** (`tools/measure_fpc.py`, machine 25) : 924
  processus (132 cellules × 7), aucune somme de contrôle fausse, 14 processus refaits pour vol de temps, un gardé
  au-dessus de 2 % (le C sur K3 `sw_padded`, 4,9 % après deux reprises), vol médian nul ; empreinte de K1 64,0 octets
  par particule ; C3 = 0. Pendant la campagne, seule l'intégration à l'analyse a été écrite (pont et générateurs dans
  `analysis/analyze_v2.py` et `analyze_v3.py`, `analysis/fpc_check.py`, états actuels), sans rien exécuter hors des
  vérifications de syntaxe.
* 2026-11-06, 09:21 à 09:51 : **résultats de l'ajout de FreePascal, sorties régénérées** (`analysis/fpc_check.py`, puis
  la chaîne publiée : classement, réplication, graphiques, matrice, figures du README, états actuels). Contrôles : le
  scénario Avant (FreePascal retiré) reproduit R-E de `results/swift_remark.json` à l'identique (écart 0) ; les états
  actuels de la remarque sur C et de la sensibilité sans SIMD reproduisent F-E à l'identique. FreePascal / C sur la
  machine 25 : 1,0 à 1,2 sur le code équivalent (K2, K1, K7 et K8 optimisés), 1,7 à 2,8 sur les noyaux SIMD du C
  écrits en scalaire, 7,5 sur K5 optimisé (`-Sv`, 128 bits), 54 sur K4 naturel, 15 sur K7 naturel (`TDictionary`).
  FreePascal **16e sur 23** (47,44 points, rang espéré 16,71, rang plausible 15 à 19, 2e étage) ; contrôle 60,5 (16e),
  plafond 36,3 (19e), code par défaut 46,9 (12e). Sensibilités : 16e dans neuf scénarios sur treize, 17e ou 18e dans
  les lectures défavorables, 15e sans pont (information) ; le second témoin (gcc) et un facteur d'hôte unique le laissent 16e. Hors plan, ajouté
  après avoir vu les facteurs du pont : K7 naturel au facteur de la table plate du C (3,05 au lieu de 17,6), 47,62
  points, 16e. Réplication : 16e sur la machine 3, par le pont ; accord et test nul (sur les 21 langages répliqués
  indépendamment) inchangés ; étages [14, 5, 1, 3]. Les 22 autres gardent leurs scores (à 0,1 point près dans une
  borne d'intervalle : FreePascal devient la référence de K2 à 256 Kio dans une partie des tirages) ; ceux qu'il devance
  reculent d'un rang ; les rangs espérés de ceux qui le précèdent bougent de 0,18 au plus (C#). Sans SIMD explicite
  (`docs/NOSIMD.md`, 4.20) : 16e, 15e en S-scalaire. Confrontation : rangs des 18 langages communs, corrélations et
  accords inchangés.
* 2026-11-06, 09:35 à 10:00 : **README et documents après l'ajout de FreePascal**. README : titre (23 langages), tableau
  (FreePascal 16e, rangs et rangs plausibles des sept suivants), paragraphe de FreePascal, renumérotation, étages,
  chaînes, machines, limites (pont entre modèles, relecture, version de chaîne), code par défaut de Swift désormais 16e,
  reproduction ; `docs/FPC.md` (section 4), `docs/FINDINGS.md`, `docs/NOSIMD.md` (4.20), `docs/CONFRONTATION.md`,
  `docs/CAPABILITIES.md` (régénéré : colonne de FreePascal). Corrigé avant publication : une phrase du paragraphe de
  FreePascal le disait 2e pour les queues de latence de K8, alors qu'il est au niveau de Rust et de Fortran (D3 0,66) ;
  c'est sa note de hiérarchie mémoire (D4 0,98) qui est la meilleure de l'étude.
* 2026-11-06, 10:58 : **machine 26**. La VM redémarre sur un nouvel hôte Emerald Rapids du même modèle (207, 4 vCPU) :
  2,76 à 2,84 GHz effectifs, latence 18 ns à 2 Mio, 36 ns à 4 Mio, 138 ns à 32 Mio, DRAM 14,8 à 15,2 Go/s
  (`results/hw/machine26/`), comme la machine 25 ; les 24 fichiers d'entrée correspondent à `env/msdata.sha256`.
* 2026-11-06, 11:00 à 12:00 : **remarque sur FreePascal : vérification, errata et plan** (`docs/FPC.md`, sections 5.1
  à 5.7, poussé avant les mesures). Chaînes installées depuis les archives officielles : 3.2.4-rc2 (`/opt/fpc-324rc2`,
  le compilateur se nomme 3.2.4-rc1) et l'instantané de main 3.3.1-21612 du 4 novembre (`/opt/fpc-main`), celui du
  relecteur. Faits (`tools/fpc_remark/facts.sh`) : exacts pour l'essentiel (AVX-512 et `TParallel.For` dans main,
  `pause` dans `TThread.SpinWait` de main seulement, 502 intrinsèques SSE sans déclaration, `-Sv` cassé, x87 en
  `-CfX86-64-V4`, K5 naturel 4 fois plus rapide avec `Length(a) - 1`) ; trois réserves : `end align 64` n'est
  respecté ni sur la pile ni par `New`, `AtomicIncrement` reste un appel à la RTL sans ordre mémoire, et la 3.2.4-rc2
  n'a pas « les mêmes temps » (`TDictionary` 1,6 à 3,6 fois plus rapide). K4 par masque : le gain (0,70) demande de lire
  la valeur dans une variable locale. Errata de la grille de FreePascal : C2 ½ (assembleur en ligne, comme Zig), E4 ½
  (`prefetchnta` seul), F4 ½ en v1 et 1 en v2 (comme Go) ; pilier 62,3 en v2 au lieu de 60,5. Copies (`bench/fpc_rq`,
  source commun à symboles, qui redonne sans symbole le binaire publié) : `fpc_len`, `fpc_mieux`, `fpc_rc2`,
  `fpc_main`, `fpc_main_mieux`, `fpc_main_scal`, `fpc_asm` et `fpc_main_asm` (information) ; outil
  `tools/measure_fpc_rq.py` (124 cellules × 7 passes, machine 26) ; scénarios fixés (R-E publié, sensibilités
  Length, noyaux mieux écrits, rc2, main, grille de main).
* 2026-11-06, 11:45:05-12:09:57 : **mesures de la remarque sur FreePascal** (`tools/measure_fpc_rq.py`, machine 26) :
  868 processus (124 cellules × 7), aucune somme de contrôle fausse, 14 processus refaits pour vol de temps, aucun
  gardé au-dessus de 2 % (1,93 % au plus), vol médian 0,08 %. Pendant la campagne, seuls l'analyse
  (`analysis/fpc_remark.py`), les errata de la grille, la sonde et les témoins des états actuels ont été écrits, sans
  rien exécuter hors des vérifications de syntaxe.
* 2026-11-06, 12:10 à 12:50 : **résultats de la remarque sur FreePascal, sorties régénérées** (`analysis/fpc_remark.py`,
  puis la chaîne publiée : classement, réplication, graphiques, matrice, figures du README, états actuels de la
  remarque sur C, de la sensibilité sans SIMD et de la confrontation). Contrôles : le scénario Avant reproduit F-E de
  `results/fpc_check.json` à l'identique ; les états actuels reproduisent le nouveau publié (R-E) à l'identique. Sonde de
  FreePascal relancée (C2, E4, F4 à ½) ; le résumé des sondes contient désormais FreePascal, oublié à l'ajout ; cinq
  divergences, les anciennes de C et C++. FreePascal **16e, 48,06 points** [47,1–48,8] (+ 0,62 par les errata ;
  contrôle 62,3, 15e) ; les 22 autres gardent leurs scores, leurs rangs espérés bougent de 0,02 au plus ; étages [14, 5,
  1, 3]. Machine 26 : rapports FreePascal / C comme sur la machine 25 (sauf K4 naturel, 62 contre 54) ; formes de la
  remarque K4 × 0,75, K5 × 0,68, K8 × 0,38 (+ 3,3 points, 16e) ; `Length(a) - 1` : K5 naturel × 0,25, 0,51 fois le C,
  qui fusionne la boucle en FMA (+ 0,15 point) ; 3.2.4-rc2 : K7 naturel × 0,40, le reste 0,95 à 1,08 (47,37 points) ;
  main : naturel × 0,25 à 0,96, K1 `soa` × 1,35 et K9 naturel × 1,33 (47,62 ; 49,89 avec sa grille ; 54,92 et 15e avec
  sa grille et ses meilleures formes, au score de C#). Les queues de latence de K8 (p99,9, max) sortent plus hautes avec
  la rc2 et main ; hors plan, ajouté après les avoir vues, les mêmes scénarios sans elles : 48,31, 48,37 et 55,66
  points. Une erreur de programmation (fusion de dictionnaires) a arrêté la première exécution avant tout scénario ;
  l'analyse a tourné deux fois, avec les mêmes graines, pour les scénarios hors plan.
* 2026-11-06, 12:45 à 13:00 : **README et documents après la remarque sur FreePascal**. README : tableau (48,1 ; devance
  Java dans 54 %), étages, paragraphe de FreePascal (errata, `High` et `Length`, FMA du C, branche stable 3.2 et branche
  main, formes mieux écrites), relecture des 23 langages, bilan des remarques, versions mesurées, machines, reproduction.
  La phrase de l'ajout qui disait sa note de hiérarchie mémoire (D4 0,98) « la meilleure de l'étude » est corrigée
  (README, `docs/FPC.md` 4.2, `docs/FINDINGS.md`) : 0,98 contre 0,97 pour C, sur le même code machine, est du bruit.
  `docs/FPC.md` (sections 5.8 à 5.12), `docs/FINDINGS.md`, `docs/NOSIMD.md` (4.21), `docs/CONFRONTATION.md`,
  `docs/CAPABILITIES.md` (régénéré : C2, E4 et F4 de FreePascal).
* 2026-11-06, 13:00 à 13:50 : **ajout de BQN (CBQN), demandé par l'auteur ; chaîne, implémentation, grille, faits et
  plan** (`docs/BQN.md`, sections 1 à 3, poussé avant les mesures). CBQN 0.12.0, la dernière version publiée (étiquette
  `v0.12.0`, commit `b4db324a`), construit avec clang 23 en trois binaires : la construction que recommande le README
  (`make o3n`) pour la cible de chaque hôte de données, Cascade Lake (`bench/bqn`, `target_from_cc=1`,
  `-march=cascadelake` : Singeli sans VBMI2 ni GFNI) et native de la machine 26 (`bench/bqn_er`), plus la cible par
  défaut (`bench/bqn_o3`, sensibilité). Premier langage de tableaux : code naturel en primitives (matrice n×16 pour K1,
  `•HashMap` pour K7, listes imbriquées pour K8, décalages pour K9 ; espaces de noms et idiome tableau en variantes de
  sensibilité) ; ni threads ni coroutines : K3 et `mt` en séquence, pas de K10. Cellules validées : 43 par binaire et
  36 pour la cible par défaut. Faits relevés sans page web (`tools/bqn_check/facts.sh`) : ni f32 ni u32 (décodage exact
  hors chrono, 128 o par particule) ; `+´` ordonnée plus rapide que le C naturel sur K5 (le C contracte en FMA) ;
  `•math.Sum` réassociée ; mise à jour structurelle `⌾` 70 à 80 fois plus lente que le recollage des rangées ;
  allocateur par blocs compagnons (le tas compte 256 o par particule, la mémoire physique 128) ; `•HashMap` à 300 à
  480 ns par ligne. Grille (`probes/bqn`) : pilier C de 22,3 (v1, C3 = 0) et 22,8 (v2). Décisions fixées d'avance : le
  pont du C de FreePascal, chaque clé prise au binaire BQN de la cible de ses données ; empreinte retenue à 128 o
  (comme Nim) ; générateur propre (SEED + 2404), classe JIT, groupe « JIT ou VM » ; scénarios B-E (publié), B-hôte,
  B-gcc, B-natif, B-o3, B-K1ns, B-K7arr, B-K8ns, B-fp, B-C3, cases basses et hautes ; outil `tools/measure_bqn.py`
  (153 cellules × 7 passes, machine 26).
* 2026-11-06, 13:47:26-15:11:40 : **mesures de l'ajout de BQN** (`tools/measure_bqn.py`, machine 26) : 1071 processus
  (153 cellules × 7), aucune somme de contrôle fausse, 18 processus refaits pour vol de temps, aucun gardé au-dessus de
  2 % (1,96 % au plus), vol médian 0,16 %. Empreinte : 256 o par particule au tas de CBQN, 128 retenus (taille de
  structure, fixée au plan). C3 mesurée : ½ (stencil vectorisé ; boucle chaude de K4, le filtre par `vpshufb`, comptée
  scalaire par la règle commune). Pendant la campagne, seuls l'intégration à l'analyse, `analysis/bqn_check.py` et les
  témoins des états actuels ont été écrits, sans rien exécuter hors des vérifications de syntaxe ; le scénario
  d'information B-K7tab (K7 naturel au facteur de la table plate du C, `•HashMap` étant une table à adressage ouvert)
  a été déclaré et poussé à 13:52, avant tout résultat de BQN.
* 2026-11-06, 15:12 à 15:40 : **résultats de l'ajout de BQN, sorties régénérées** (`analysis/bqn_check.py`, puis la
  chaîne publiée : classement, réplication, graphiques, figures du README, matrice, états actuels de la remarque sur C,
  de la sensibilité sans SIMD et de la confrontation). Contrôles : le scénario Avant (BQN retiré) reproduit R-E de
  `results/fpc_remark.json` à l'identique ; les états actuels reproduisent B-E à l'identique. BQN **21e sur 24, 18,65
  points** [18,5–18,8], rang plausible 20 à 22 (contrôle 22,8, plafond 12,45, code par défaut 22,7), entre OCaml (75 %)
  et JavaScript (87 %) ; 21e dans tous les scénarios du plan (20e sans pont, information). Les 23 autres gardent leurs
  scores ; JavaScript, Python et Lua reculent d'un rang, OCaml de 0,25 en rang espéré ; les étages passent de
  [14, 5, 1, 3] à [14, 5, 5]. Machine 26 : BQN / C de 0,60 (K5 naturel) à 211 (K3 sans threads) ; binaire natif contre
  cible Cascade Lake 0,85 à 1,10 ; construction par défaut 1,12 à 1,83 sur les noyaux de tableaux.
* 2026-11-06, 15:40 à 16:10 : **README et documents après l'ajout de BQN**. README : titre (24 langages), tableau
  (BQN 21e ; rangs plausibles et précédences du bas du tableau), étages, paragraphe de BQN, faits transversaux
  (empreinte, SIMD explicite, vectorisation, concurrence), chaînes, machines, limites, lectures (dont l'ajout de
  FreePascal, qui y manquait), reproduction ; « les neuf mêmes restent derrière » corrigé en « les onze » (le compte
  n'avait pas suivi l'ajout de FreePascal). `docs/BQN.md` (section 4), `docs/FINDINGS.md`, `docs/NOSIMD.md` (4.22),
  `docs/CONFRONTATION.md`, `docs/CAPABILITIES.md` (régénéré : colonne de BQN).
* 2026-11-06, 16:30 à 16:53 : **remarque sur BQN : vérification, errata et plan** (`docs/BQN.md`, sections 5.1 à
  5.7, poussé avant les mesures). Machine 27 (nouvel hôte Emerald Rapids du même modèle, caractérisé). Vérifié dans
  les sources (CBQN 0.12.0 et sa branche `develop`, dépôt officiel du langage : `doc/`, `spec/`, `implementation/`) :
  84 commits sur `develop`, sans threads ni f32 ; vecteurs de 256 bits (`arch_defvw`) ; `•bit._add`, `_sub`, `_mul`,
  `_neg` présents dans 0.12.0 mais absents de sa documentation ; options `-X` de la branche ; `⊐⊸⊔`, la façon directe
  de regrouper (`doc/group.md`) ; la somme `sum_i16` vectorisée (`vpdpwssd`, que `analysis/hotloop.py` ne compte
  pas, sans effet sur C3) ; la somme de contrôle de K9 dans le chrono (erreur de mon banc). Non retrouvé : « 10 fois
  plus lent que le C sur du code scalaire ». Errata : K9 (somme hors chrono), K7 naturel (idiome de la documentation,
  comme mon Q1 naturel), A6 et A3 à 0 (règle de Fortran et de Julia) ; C5 reste 0 (définition précisée : plusieurs
  cœurs). Les formes en blocs (K1, K4, K6, K9 ; essais : Q1 82 ms contre 229, K9 61 contre 92) restent une
  sensibilité (R-blocs), comme les formes mieux écrites des autres langages. Copie `bench/bqn_rq` (et `bqn_er_rq`),
  validée ; outil `tools/measure_bqn_rq.py` (56 cellules × 7 passes) ; scénarios Avant, R-grille, R-K9, R-K7, R-E,
  R-blocs, R-C5, R-blocs-C5, R-K7map.
* 2026-11-06, 16:53:17-17:19:15 : **mesures de la remarque sur BQN** (`tools/measure_bqn_rq.py`, machine 27) : 392
  processus (56 cellules × 7), aucune somme de contrôle fausse, aucun processus refait, vol médian 0,20 % (1,97 % au
  plus) ; témoins inchangés à 1,015 et 0,988. Pendant la campagne, seuls le report des rapports dans le pont
  (`ratios_added`), la grille, la sonde, `analysis/bqn_remark.py`, les témoins des états actuels et des textes ont été
  écrits, sans rien exécuter hors des vérifications de syntaxe.
* 2026-11-06, 17:20 à 17:41 : **résultats de la remarque sur BQN, sorties régénérées** (`analysis/bqn_remark.py`,
  puis la chaîne publiée et les états actuels). Contrôles : le scénario Avant reproduit B-E de
  `results/bqn_check.json` à l'identique ; les états actuels reproduisent R-E à l'identique. Sonde de BQN relancée
  (A3, A6 à 0 ; notes de C5 et F3) ; cinq divergences, les anciennes de C et C++. BQN **21e, 17,72 points**
  [17,5–17,9] (− 0,93 : grille − 1,10, K7 naturel + 0,16, K9 + 0,01) ; les 23 autres gardent leurs scores, leurs rangs
  espérés bougent de 0,04 au plus ; étages [14, 5, 5]. Rapports de la machine 27 : K7 naturel en idiome de la
  documentation × 0,133 ; somme de contrôle de K9 hors chrono, rapports dans le bruit (0,94 à 1,00) ; formes en blocs
  × 0,35 (Q1) à × 0,86 (Q6 `mt`) : R-blocs 19,72 points (plafond 17,45), toujours 21e ; R-blocs-C5 20,59.
* 2026-11-06, 17:43 à 17:49 : **R-K7tab, ajouté après les résultats** (information, hors du classement) : B-K7tab
  rejoué sur les données corrigées (K7 naturel de BQN relié par le facteur de la table plate du C : 3,7 s au lieu de
  19,0 s publiés ; 17,89 points, 21e), pour vérifier une phrase du README. `analysis/bqn_remark.py` relancé : les neuf
  autres scénarios et `results/transfers.json` sont identiques au bit près.
* 2026-11-06, 17:30 à 17:55 : **README et documents après la remarque sur BQN**. README : tableau (17,7 ; 79 et
  84 %), paragraphe de BQN (relu, errata, ce que mesure le rang, formes en blocs), limites (K7), relectures, bilan des
  errata, machines, lectures, reproduction ; le K7 de Haskell redevient le plus lent de l'étude. `docs/BQN.md`
  (sections 5.8 à 5.12), `docs/FINDINGS.md`, `docs/NATURAL.md` (K7 de BQN), `docs/NOSIMD.md` (4.23),
  `docs/CONFRONTATION.md`, `docs/CAPABILITIES.md` (régénéré : A3, A6 de BQN ; définition de C5).

* 2026-11-07, 07:00 à 08:20 : **ajout de PHP : chaîne, dix noyaux, grille, faits et plan** (`docs/PHP.md`, sections 1
  à 3, poussé avant les mesures). Machine 28 (nouvel hôte Emerald Rapids du même modèle, caractérisé :
  `results/hw/machine28` ; les 24 fichiers d'entrée vérifiés). PHP 8.5.12 (21 octobre 2026), la dernière version stable
  de la liste officielle de php.net (la 8.6.0 en est à sa RC5), construit par le `./configure` de production du README de
  php-src avec les extensions livrées `pcntl`, `shmop`, `sysvsem`, `sysvshm` et `ffi` ; `php.ini-production` ; le banc
  active OPcache et le JIT tracing, que la CLI laisse inactifs par défaut et que le manuel recommande (la CLI par défaut
  est une sensibilité, `bench/php_def`). Archive de Swift déjà installée supprimée de `/opt/dl` pour faire de la place
  (son SHA-256 est gardé à côté). Faits : OPcache ne met pas en cache un script de moins de 2 s (le JIT ne s'y applique
  pas : piège de mes premiers essais) ; un bogue du JIT tracing de 8.5.12 (deux `$st[$sp++]` de suite, reproduction dans
  `tools/php_check/src`) ; une fermeture qui capture les données double le temps de K1 naturel par le collecteur de
  cycles (harnais par nom de fonction) ; les entiers passent en flottant au-delà de 2^63. Grille (sonde `probes/php`,
  aucune divergence nouvelle) : pilier C 25,9 en v1 (C3 = 0), 27,4 en v2 (D4 à 1 comme Python). Validation de toutes
  les cellules, sommes justes. Outil `tools/measure_php.py` (122 cellules × 7 passes) ; scénarios Avant, P-E, P-direct,
  P-hôte, P-gcc, P-défaut, P-K1arr, P-C3, P-cases-bas et -haut, P-tout-bas et -haut, P-K7tab.
* 2026-11-07, 08:16:26 à 10:01:29 : **mesures de l'ajout de PHP** (`tools/measure_php.py`, machine 28) : calibration
  de 08:16:26 à 08:23:33, passes de 08:23:33 à 10:00:37, empreinte et C3 ensuite ; 854 processus (122 cellules × 7),
  aucune somme de contrôle fausse, 13 processus refaits pour vol de temps (aucun gardé au-dessus de 2 % : 1,82 % au
  plus, médiane 0,19 %). Empreinte de K1 : 352 o par particule. Pendant la campagne, seuls `analysis/php_check.py`
  (poussé à 08:23:42, avant tout résultat) et des textes du README ont été écrits, et les statistiques de vol de temps
  lues, sans calcul lourd. **Écart au plan** : la mesure de C3 s'est arrêtée sur une erreur, l'échantillonneur ne
  reconnaissant pas le code du JIT d'OPcache (une projection partagée de `/dev/zero`, « /dev/zero (deleted) » dans
  `/proc/<pid>/maps`) ; `tools/sampler.c` et `analysis/hotloop.py` corrigés (aucun autre profil publié n'a une telle
  projection), les deux profils de PHP refaits à 10:02 et 10:03 : C3 = 0, la valeur par défaut, mais mesurée.
* 2026-11-07, 10:05 à 10:44 : **résultats de l'ajout de PHP, sorties régénérées** (`analysis/php_check.py`, puis la
  chaîne publiée et les états actuels de C et de NOSIMD). Contrôles : le scénario Avant reproduit R-E de
  `results/bqn_remark.json` à l'identique ; les états actuels reproduisent P-E à l'identique. Premier calcul (10:11),
  selon le plan : PHP 16,60 points, 22e ; mais sur K2 à 8 Mio, la machine 28 mesure dans deux régimes de cache selon le
  processus (vers 160 ou 520 ms ; deux processus lents sur sept chez le témoin C, aucun chez PHP), et la moyenne
  géométrique du pont faisait de PHP le plus rapide des 25 à cette taille (0,72 fois le C), donc la référence de D4 :
  chacun des 24 autres perdait 0,06 à 0,42 point. **Écart au plan, décidé après avoir vu les données** : pour cette
  seule clé, le facteur du pont prend la médiane des médianes de processus (`BRIDGE_MEDIAN`,
  `analysis/analyze_v2.py` ; même règle pour le second témoin et la réplication) ; le calcul du plan reste un scénario
  d'information (P-E-plan). Résultat (10:25) : PHP **22e, 16,56 points** [16,3–16,8], à égalité de fait avec
  JavaScript (meilleur rang espéré, 22,32 contre 22,34, mais JavaScript devant dans 57 % des variantes) ; 22e ou 23e
  dans tous les scénarios ; les 24 autres gardent leurs scores ; étages [14, 5, 6]. Vérifications (10:26 à 10:28) :
  K2 à 8 Mio de PHP multiplié par 1,3, les rangs espérés des autres bougent encore (l'effet ne vient pas de K2) ;
  latence maximale de PHP doublée, seuls ses voisins bougent (l'effet vient de D3).
* 2026-11-07, 10:45 à 11:10 : **effet de PHP sur deux paires à égalité de fait, états actuels des remarques, README et
  documents**. Le tableau du README, vérifié contre `results/summary_v3.json`, montrait onze écarts : C3 passe 4e
  devant Zig (5,11 contre 5,14) et Fortran 11e devant Swift (10,85 contre 10,86), le duel direct penchant toujours de
  l'autre côté (46 et 48 %). Cause vérifiée : dans la moitié des variantes, D3 lit les queues de latence de K8
  relativement à la médiane, et PHP, lent mais régulier (max/p50 de 11,4), y devient la référence ; avec sa latence
  maximale doublée, les quatre retrouvent exactement leurs rangs espérés d'avant PHP. Le plan l'admettait (3.6 : les
  références suivent PHP) ; `docs/PHP.md` (4.4), qui disait ces rangs inchangés, est corrigé. Les états actuels des
  remarques sur Zig, Mojo, C#, Julia, Rust et Nim, que les ajouts de FreePascal et de BQN n'avaient pas relancés,
  sont régénérés à 25 langages (`.work/php/regen2.sh`) ; leurs chiffres cités par le README sont recalés (Zig 0.18-dev :
  du 5e au 1er rang ; K4 hors du plafond : C++ 80,0 points ; Julia mieux écrite : 11e). README : tableau, ordre (quatre
  écarts au score), ce qui est sûr, paragraphes de C3, de Zig, de Fortran et de Swift permutés et renumérotés,
  paragraphe de PHP (22e), JavaScript, Python et Lua renumérotés, machines, limites (pont de PHP, K2 à 8 Mio),
  versions, sensibilité sans SIMD explicite (Julia complète le groupe de tête dans les trois lectures ; Java devant Go
  dans les trois). `docs/PHP.md` (section 4), `docs/FINDINGS.md`, `docs/NOSIMD.md` (4.24), `docs/CONFRONTATION.md`,
  `docs/CAPABILITIES.md` (régénéré : colonne de PHP).
* 2026-11-07, 13:26 à 13:52 : **remarque sur PHP : vérification et plan** (`docs/PHP.md`, sections 5.1 à 5.7, poussé
  avant les mesures). Machine 29 (nouvel hôte Emerald Rapids du même modèle, caractérisé : `results/hw/machine29` ;
  les 24 fichiers d'entrée vérifiés). PHP 8.3.36, 8.4.27, 8.5.13RC1 et 8.6.0RC5 construits avec les options du banc,
  depuis les archives des listes officielles de php.net (SHA-256 vérifiés ; `tools/php_remark/build.sh`). Vérifié dans
  les sources et par reproductions (`tools/php_remark/facts.sh`, `results/php_remark/facts.txt`) : les réglages par
  défaut (en 8.3, `opcache.jit` = « tracing » mais tampon nul) ; aucun code de la FFI dans le JIT jusqu'à 8.6.0RC5 (la
  PR 14491 n'est pas fusionnée) ; rien sur les fils, le SIMD ou les `struct` dans `UPGRADING` de 8.6.0RC5 ; K9 naturel :
  16 erreurs de compilation de la boucle, puis liste noire, de 8.4.27 à 8.6.0RC5, pas en 8.3.36 (le déclencheur : lire
  **deux** autres lignes puis écrire `$b[$i][$j]`, pas une seule comme le dit la remarque) ; K1 naturel : 72 à 75 % du
  temps dans le collecteur de cycles (8 à 9 passes par parcours), sans effet du collecteur sur K6, K7 et K8 ; le bogue
  de pile de 8.4.27 à 8.6.0RC5, pas en 8.3.36 ; `node:ffi` sans `struct`. Non vérifiés (hors des sources) : la date de
  8.6.0, le gain de 20 fois de la PR 14491, GH-22115, l'état du RFC Structs. Errata d'explication (2.4 point 6, 4.1) ;
  aucune donnée ni case de la grille ne change. Copie `bench/php_rq` (K1 par indice, `gc_disable()`), lanceurs
  `bench/php83`, `php84`, `php8513rc1`, `php86rc5` ; outil `tools/measure_php_rq.py` (17 cellules × 7 passes) ;
  scénarios Avant, R-K1idx, R-K1gc, R-K9-83, R-tout, R-tout-idx.
* 2026-11-07, 13:51:38 à 14:03:00 : **mesures de la remarque sur PHP** (`tools/measure_php_rq.py`, machine 29) : 119
  processus (17 cellules × 7), aucune somme de contrôle fausse, aucun processus refait, vol de temps de 0,79 % au plus
  (médiane 0,20 %). Pendant la campagne, seul `analysis/php_remark.py` a été écrit (poussé à 13:52, avant tout
  résultat), sans rien exécuter hors des vérifications de syntaxe.
* 2026-11-07, 14:03 à 14:15 : **résultats de la remarque sur PHP, textes corrigés** (`analysis/php_remark.py`,
  `results/report_php_remark.md`). Contrôle : le scénario Avant reproduit P-E à l'identique ; copie `php_rq` /
  publié sur K1 naturel 1,005. K1 par indice 3,4 fois plus rapide, sans collecteur 4,0 fois ; K9 naturel sous 8.3.36
  3,4 fois plus rapide, sous 8.4.27, 8.5.13RC1 et 8.6.0RC5 comme sous 8.5.12. Scénarios : R-K1idx − 0,02 point (D2
  baisse plus que D1 ne monte), R-K1gc + 0,09, R-K9-83 + 0,04, R-tout + 0,13 (16,69 ; BQN 1,03 point devant) ; PHP
  22e partout, à égalité de fait avec JavaScript. **Écart au plan** : le rapport affiche en plus les parties D1 à D4
  de PHP, ajoutées après le premier calcul pour expliquer R-K1idx (calculs identiques, sorties comparées). Classement
  publié inchangé : ni régénération des sorties publiées ni des états actuels. Textes : `docs/PHP.md` (2.4 point 6 et
  4.1 corrigés, sections 5.8 à 5.13, reproductions pour php-src), README (paragraphe de PHP, égalités de fait dans le
  tableau et sa légende, « Ce qui sépare vraiment les langages », points 3 et 7, relectures, bilan des remarques,
  lectures, reproduction), `docs/FINDINGS.md`, `tools/php_check/src/jit_stack_bug.php` (versions touchées).
