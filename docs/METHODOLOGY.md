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
  réassociation flottante ; C5 constructions de parallélisme de données.
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

