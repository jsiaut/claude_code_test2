# Quels langages incarnent le mieux la *mechanical sympathy* ? Une étude mesurée (28 octobre 2026)

{{RESUME}}

---

## 1. Ce que recouvre « mechanical sympathy » en 2026

L'expression vient du pilote Jackie Stewart (« pas besoin d'être ingénieur pour piloter, mais il faut
une sympathie mécanique pour la voiture »). Martin Thompson l'a importée dans le logiciel à partir de
2011 (blog *Mechanical Sympathy*, LMAX Disruptor). En 2026, la référence la plus récente est l'article
de Caer Sanders, [*Principles of Mechanical Sympathy*](https://martinfowler.com/articles/mechanical-sympathy-principles.html)
(martinfowler.com, 7 avril 2026), qui retient quatre principes. Le
[bliki de Martin Fowler](https://martinfowler.com/bliki/MechanicalSympathy.html) le reprend en juillet 2026.

1. **Accès mémoire prévisibles** (« not-so-random memory access ») : parcourir la mémoire dans un
   ordre que les préchargeurs et les caches récompensent.
2. **Lignes de cache et faux partage** : ne pas faire écrire deux cœurs dans la même ligne de 64 octets.
3. **Principe de l'écrivain unique** : une seule entité écrit une donnée ; les autres lui envoient
   des messages (Thompson, [*Single Writer Principle*](https://mechanical-sympathy.blogspot.com/2011/09/single-writer-principle.html), 2011).
4. **Regroupement naturel** (*natural batching*) : traiter tout ce qui est disponible d'un coup,
   comme le consommateur du [Disruptor](https://lmax-exchange.github.io/disruptor/disruptor.html).

Vous avez demandé le **sens large**, qui ajoute trois corpus convergents :

* **Data-Oriented Design** : M. Acton, [*Data-Oriented Design and C++*](https://www.youtube.com/watch?v=rX0ItVEVjHc)
  (CppCon 2014) ; R. Fabian, [*Data-Oriented Design*](https://www.dataorienteddesign.com/dodbook/) (2018) ;
  A. Kelley, [*A Practical Guide to Applying Data-Oriented Design*](https://vimeo.com/649009599) (2021).
  Ses principes : la donnée et sa transformation d'abord, structures de tableaux (SoA), données
  compactes, indices plutôt que pointeurs, arènes, aucune allocation cachée, traitement par lots.
* **Calcul haute performance** : modèle *roofline* (Williams, Waterman et Patterson, CACM 2009),
  bande passante mémoire ([STREAM](https://www.cs.virginia.edu/stream/)), vectorisation SIMD,
  tableaux multidimensionnels contigus, parallélisme de données, latence de la hiérarchie mémoire
  (U. Drepper, [*What Every Programmer Should Know About Memory*](https://people.freebsd.org/~lstewart/articles/cpumemory.pdf)).
* **SGBD analytiques (OLAP)** : stockage colonnaire, exécution vectorisée
  ([MonetDB/X100](https://www.cidrdb.org/cidr2005/papers/P19.pdf), CIDR 2005), sélection sans
  branchement, tables de hachage plates à adressage ouvert, parallélisme par morceaux (*morsels*,
  Leis et al., SIGMOD 2014).

**Définition opérationnelle retenue** (pré-enregistrée, `docs/METHODOLOGY.md`). Un langage incarne
la mechanical sympathy dans la mesure où :

1. il **donne le contrôle** des aspects matériels : disposition des données, allocation, SIMD,
   modèle mémoire, parallélisme, génération de code (pilier **C**) ;
2. ce contrôle **atteint réellement les limites du matériel** (pilier **E**, efficacité plafond) ;
3. le **code par défaut** va déjà dans le sens du matériel, avec un modèle de coût transparent :
   pas de coût caché, pas de pause, pas d'indirection imposée (pilier **D**).

Score : `MS = 0,35·C + 0,40·E + 0,25·D`. Un Monte-Carlo sur les poids (section 6) montre ce qui ne
dépend pas de ce choix.

## 2. Protocole

Le protocole complet, rédigé **avant** les mesures inter-langages, est dans
[`docs/METHODOLOGY.md`](docs/METHODOLOGY.md). Les écarts sont datés et justifiés dans son journal. La
spécification des noyaux, qui sert de contrat commun aux 21 langages, est dans [`docs/SPEC.md`](docs/SPEC.md).

### 2.1 Dix noyaux, chacun rattaché à un principe

| Noyau | Principe testé | Variantes |
|---|---|---|
| K1 énergie de 4 M particules | disposition AoS/SoA, indirection, en-têtes d'objets (DOD) | natural, natural_shuffled, aos, soa, empreinte |
| K2 chasse de pointeurs, 16 Kio → 256 Mio | latence L1/L2/L3/DRAM et « visibilité » de la hiérarchie | tuned |
| K3 4 threads × 2²⁵ incréments | faux partage, écrivain unique | rmw/sw × packed/padded |
| K4 somme conditionnelle de 16 M octets | prédiction de branchement, code sans branchement | naturel non trié et trié, sans branchement |
| K5 produit scalaire de 2 048 f32 (en L1) | SIMD, réassociation | natural, tuned |
| K6 TPC-H Q6 et Q1 sur 16 M lignes en colonnes | OLAP colonnaire, sélection sans branchement, agrégation | natural, tuned, mt (4 threads) |
| K7 GROUP BY 16 M lignes, 1 M clés | table de hachage plate contre table standard | natural, tuned |
| K8 16 384 arbres de 2 047 nœuds (+ arbre de 2 M nœuds vivant) | allocation, GC, latence de queue | natural, tuned (arène), tuned_alloc |
| K9 stencil de Jacobi 2 048², 4 itérations | HPC : tableaux 2D contigus, bande passante | natural, tuned, mt |
| K10 file SPSC de 4 M messages | écrivain unique, *batching*, ordres mémoire | natural (file standard), tuned (anneau sans verrou) |

* **`natural`** : le code qu'on écrit en suivant la documentation officielle, avec le conteneur et le
  type par défaut. Les choix sont justifiés langage par langage dans [`docs/NATURAL.md`](docs/NATURAL.md).
* **`tuned`** : le meilleur code possible **avec le langage et sa bibliothèque standard seulement** :
  types SIMD, intrinsèques, `unsafe`, pragmas et options documentées sont permis ; FFI vers du code
  natif écrit à côté, assembleur en ligne et paquets tiers sont interdits.
* Tous les langages lisent **les mêmes fichiers binaires** et doivent rendre **le même résultat**.
  Les entiers sont comparés au bit près, les flottants avec une tolérance relative de 1e-6 à 1e-3
  selon le noyau. Toute mesure au résultat faux est exclue. Un contrôle supplémentaire signale tout
  temps inférieur à la borne physique (octets ÷ bande passante mesurée, ou opérations ÷ débit crête),
  qui trahirait un calcul que le compilateur aurait sauté.

### 2.2 Mesure

* 3 processus indépendants par mesure, chacun avec une ou trois répétitions d'échauffement (trois
  pour les JIT), puis 3 à 10 répétitions chronométrées dans le programme, sur l'horloge monotone.
* Les 3 processus sont pris lors de **3 passes** successives. Dans chaque passe, l'ordre des blocs
  (langage, noyau) est **tiré au hasard** (graine fixe). La dérive temporelle d'une VM partagée se
  répartit ainsi entre tous les langages au lieu de pénaliser l'un d'eux.
* Le *steal time* de l'hyperviseur est relevé : une mesure où il dépasse 2 % est refaite.
* Le pilote enregistre en plus le pic RSS, les temps CPU utilisateur et système, les défauts de
  page et les changements de contexte (`tools/driver.py`).
* Statistiques : médiane des médianes ; IC à 95 % par bootstrap hiérarchique (processus puis
  répétitions, Kalibera et Jones, ISMM 2013) ; moyennes géométriques de ratios normalisés (Fleming
  et Wallace, 1986) ; 10 000 tirages de Dirichlet sur les poids pour les intervalles de rang.

## 3. L'environnement : ce qui existe, ce qui manque, ce que j'ai construit

**Machine.** VM Firecracker (KVM) avec 4 vCPU Intel Xeon (Cascade Lake, AVX-512 F/DQ/CD/BW/VL/VNNI),
15 Gio de RAM, noyau Linux 6.18. Ce que j'ai vérifié plutôt que supposé :

* **Pas de compteurs matériels.** Le noyau l'annonce au démarrage (« *Performance Events: unsupported
  CPU family 6 model 85 no PMU driver, software events only* »). La source `msr` n'expose que `tsc`
  et `smi` (ni APERF ni MPERF), et `/dev/cpu/*/msr` est absent. `perf` n'est pas installé.
  `perf_event_paranoid` vaut 2, ce qui autorise les événements logiciels sur ses propres processus.
* **Outils présents** : gdb, strace, objdump/llvm-objdump, readelf, Valgrind 3.22, horloge TSC
  invariante (`constant_tsc`, `nonstop_tsc`). Valgrind 3.22 **ne décode pas l'AVX-512** (SIGILL
  vérifié sur une FMA zmm). Il est donc inutilisable sur les binaires `-march=native`.
* **Chaînes de compilation** (`env/toolchains.txt`), les dernières versions stables au 28 octobre
  2026 : clang/flang 23.1.5, GCC 16.2 (C, C++, Fortran, Ada), Rust 1.99.1, Zig 0.17.0, Odin
  dev-2026-10, C3 0.8.5, LDC 1.43 (D 2.113), Nim 2.2.12, Julia 1.13.3, Chapel 2.10.0, Mojo 1.2.0,
  Go 1.27.3, OpenJDK 27.0.1, .NET 10.0.403, Node 26.12.1 (V8 14.6), Bun 1.4.4, CPython 3.15.2
  (avec et sans GIL), GHC 9.14.1, OCaml 5.5.2 (flambda), Lua 5.5.1, LuaJIT 2.1. Plusieurs
  téléchargements de binaires étant bloqués par le proxy, Odin, C3, LDC, Chapel, OCaml, GCC 16 et
  LuaJIT ont été **compilés depuis les sources**.

**Outils écrits pour l'étude**, pour remplacer ce qui manque :

* [`tools/hwprobe.c`](tools/hwprobe.c) caractérise le matériel par micro-expériences chronométrées
  au TSC (résultats dans `results/hw/`).
* [`tools/sampler.c`](tools/sampler.c) est un profileur par échantillonnage qui appelle
  directement `perf_event_open` avec l'événement logiciel `cpu-clock`, sur un événement par CPU
  hérité par tous les threads. Il recueille les adresses d'instruction et les projections
  mémoire, et copie à chaud (`process_vm_readv`) les octets du code JIT. Il sert à repérer la
  **boucle réellement exécutée** par chaque implémentation, même après inlining ou compilation
  JIT, puis à la classer (scalaire ou vectorisée, et sur quelle largeur) avec
  [`analysis/hotloop.py`](analysis/hotloop.py).
* [`tools/driver.py`](tools/driver.py) (pilote, `rusage`, *steal*, validation) et
  [`tools/campaign.py`](tools/campaign.py) (passes randomisées).
* [`probes/<langage>/`](probes) : une sonde compilée et exécutée par langage pour les capacités
  du pilier C.

**Ce que mesure la machine** (`tools/hwprobe.c`) :

| Mesure | Valeur |
|---|---|
| Fréquence cœur effective (scalaire / AVX2 dense / AVX-512 dense) | ≈ 3,2 / 2,8 / 2,2 GHz : licences de fréquence d'Intel |
| Débit FMA crête AVX-512 | 139 Gflop/s f32 (1 cœur) |
| Latence L1 / L2 / « L3 » / DRAM | 1,2 ns / 4,3 ns / 22–38 ns / 140–445 ns |
| Dernier niveau de cache réellement disponible | **≈ 2–3 Mio** (latence de DRAM dès 4 Mio, pages géantes ou non) |
| Bande passante en lecture, 1 thread | L1 184 Go/s, L2 120 Go/s, DRAM 7–10 Go/s |
| STREAM triad, 1 / 4 threads | 8,8 / 43 Go/s |
| Transfert d'une ligne entre deux cœurs | 120–210 ns |
| Mauvaise prédiction de branchement | ≈ 21 cycles |
| Accès aléatoire sur 64 Mio, pages de 4 Kio / pages géantes | 141 / 52 ns |

Deux erreurs de mesure de ma propre sonde ont été trouvées et corrigées en route : la boucle de
fréquence mesurait le coût du branchement, et le compilateur fusionnait les passes du test de bande
passante. C'est la raison d'être des contrôles de vraisemblance.

## 4. Résultats

### 4.1 Ce que permet la machine (bornes physiques)

Pour lire les tableaux, il faut les comparer à ce que le matériel autorise. Le calcul utilise les
mesures de la section 3 :

| Noyau | Facteur limitant | Borne inférieure sur cette machine |
|---|---|---|
| K1 soa | lire 4 colonnes × 16 Mio en DRAM (10 Go/s sur 1 thread) | ≈ 6,7 ms |
| K1 aos / natural | lire 64 o par particule (268 Mo) | ≈ 27 ms |
| K2 | latence d'un saut dépendant : L1 1,2 ns, L2 4,3 ns, DRAM 140–445 ns | — |
| K4 | lire 16 Mo ; une mauvaise prédiction coûte environ 21 cycles | ≈ 1,7 ms |
| K5 | 2 chargements par FMA (L1) ; débit crête de 139 Gflop/s | ≈ 2–4 ms |
| K6 Q6 / Q1 | lire 10 / 13 o par ligne × 16 M lignes | ≈ 17 / 22 ms (1 thread), ≈ 3–4 ms (4 threads) |
| K7 | accès aléatoires dans une table de 32 Mio, hors cache | dépend du parallélisme mémoire |
| K9 | lire et écrire 2 × 32 Mio, 4 fois | ≈ 27 ms (1 thread), ≈ 4–6 ms (4 threads) |
| K10 | aller-retour de lignes de cache entre 2 cœurs (120–210 ns) | dépend du *batching* |

Le script d'analyse signale tout temps inférieur à 90 % de sa borne : ce serait un calcul sauté.

{{RESULTATS}}

## 5. Classement justifié, langage par langage

{{JUSTIFICATIONS}}

## 6. Robustesse du classement

{{ROBUSTESSE}}

## 7. Menaces à la validité

* **Une seule machine, virtualisée.** Une VM partagée, sans compteurs matériels, avec un cache de
  dernier niveau effectif de 2–3 Mio et des transferts de ligne entre cœurs de 120 à 210 ns. Les
  effets mémoire y sont amplifiés par rapport à un serveur nu. Les classements de noyaux liés à la
  mémoire (K1, K2, K6, K7, K9) pourraient être plus serrés sur une autre machine. Les mitigations
  sont la randomisation de l'ordre, les 3 passes, la règle du *steal* et le bootstrap.
* **Ma compétence varie selon les langages.** Toutes les implémentations suivent le même
  algorithme et rendent le même résultat. Le code machine des boucles chaudes a été inspecté
  (désassemblage, et profils de `tools/sampler.c` pour les JIT). Plusieurs variantes tuned ont été
  réécrites quand le désassemblage révélait un défaut (Rust K5, Fortran Q1, Chapel Q1 et K5, Java
  Q1) ; ces corrections sont consignées dans `docs/FINDINGS.md`. Un expert de chaque langage ferait
  sans doute un peu mieux sur certaines variantes tuned. Le pilier E mesure donc « le meilleur que
  j'ai obtenu avec la bibliothèque standard », borné par la physique de la machine.
* **Le choix des noyaux est fait *a priori*** à partir de la littérature (un principe par noyau). Un
  autre choix changerait les poids implicites. L'analyse « un noyau retiré » mesure la sensibilité
  du classement à chacun d'eux.
* **Le pilier C repose sur des jugements** (0, 0,5 ou 1 par capacité). Chaque cellule est justifiée
  par une source ou une sonde (`analysis/capabilities.py`). L'analyse où chaque 0,5 est tiré au
  hasard à 0 ou 1 borne l'effet de ces jugements.
* **Pondération des piliers.** Elle est mise à l'épreuve par 10 000 tirages de Dirichlet (section 6).
* **Biais de mesure connus.** Alignement du code et environnement (Mytkowicz et al., ASPLOS 2009) :
  atténués par les processus multiples, pas éliminés. Échauffement des JIT (Barrett et al., OOPSLA
  2017) : trois répétitions d'échauffement, puis vérification de la stabilité des répétitions
  (coefficient de variation signalé au-delà de 5 %).
* **« Natural » est une interprétation.** Le code idiomatique d'un langage se discute. Les choix
  sont documentés et justifiés dans `docs/NATURAL.md`.
* **Les implémentations alternatives** (gcc pour C, flang pour Fortran, LuaJIT, Bun, CPython sans
  GIL) sont mesurées mais pas classées. Le classement de chaque langage repose sur son
  implémentation de référence.

## 8. Reproduire

```bash
python3 tools/driver.py c --quick          # validation d'un langage (1 processus, 1 répétition)
```

```bash
python3 tools/campaign.py                  # campagne complète (3 passes randomisées)
```

```bash
python3 analysis/analyze.py                # scores, IC, intervalles de rang -> results/summary.json
```

```bash
python3 analysis/tables.py                 # tableaux par noyau
```

Arborescence : `bench/<langage>/` (implémentation, `build.sh`, `run`), `tools/` (pilote, campagne,
`hwprobe.c`, `sampler.c`, générateur de données), `probes/<langage>/` (sondes de capacités),
`analysis/` (matrice de capacités, analyse), `results/` (données brutes, matériel, synthèse),
`docs/` (protocole, spécification, choix natural, faits vérifiés).
