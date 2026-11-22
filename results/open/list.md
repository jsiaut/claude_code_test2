# Liste de la piste ouverte (v4, point 6)

*Relevé du 22 novembre 2026 (`docs/V4_OPEN.md`, 3.2 à 3.4 et 10). Requêtes et réponses :
`results/open/registry/<langage>.json` (`tools/open/registry.py`) ; décisions : `results/open/decisions.json` ;
ce fichier est écrit par `tools/open/listmd.py`. Pour chaque case, les bibliothèques sont examinées dans l'ordre
de la statistique d'usage du registre ; la première admise (3.3 a) est retenue, et chaque bibliothèque mieux
classée est refusée avec sa raison. Aucune sonde, aucune forme n'a été écrite avant ce relevé.*

*Lecture de 3.3 d : une bibliothèque comble les cases dont la recherche la retient ; une bibliothèque nommée par
le dossier (3.3 c), les cases que son API comble. Les cellules du plafond suivent l'écart 3 (`docs/V4_OPEN.md`,
10) : une bibliothèque n'y est attribuée que si elle apporte un levier que la bibliothèque standard n'offre pas en
entier et que son API fait le calcul de la cellule ou en remplace le conteneur.*

## C

Registre : archive d'Ubuntu 24.04 ; statistique : installations (popcon de Debian ; celui d'Ubuntu n'est plus publié : écart 2).

L'index d'Ubuntu publié par ecosyste.ms n'a pas de descriptions : la recherche ne lit que les noms des paquets.

| Case | Note publiée | Retenue | Version | Rang | Statistique | Refusées avant elle |
|---|---|---|---|---|---|---|
| A6 | 0 | aucune | — | — | — | aucune réponse |
| B2 | 0.5 | aucune | — | — | — | alien-arena-data (jeu) ; alien-arena (jeu) ; rust-id-arena (crate Rust empaquetée) ; rust-la-arena (crate Rust empaquetée) ; rust-typed-arena (crate Rust empaquetée) |
| F2 | 0 | hwloc | 2.10.0 (paquet Ubuntu libhwloc-dev 2.10.0-1build1) | 1 | 3 053 |  |

Cellules du plafond attribuées (3.4) :

* hwloc : **aucune** (F2 : levier hors de la table de l'écart 3)

## Odin

Registre : aucun : aucun gestionnaire (collection vendor livrée) ; statistique : —.

Odin n'a pas de gestionnaire de paquets : la collection vendor est livrée avec le compilateur (déjà comptée).

| Case | Note publiée | Retenue | Version | Rang | Statistique | Refusées avant elle |
|---|---|---|---|---|---|---|
| C5 | 0 | aucune | — | — | — | aucune réponse |
| D3 | 0.5 | aucune | — | — | — | aucune réponse |
| F1 | 0.5 | aucune | — | — | — | aucune réponse |
| F2 | 0 | aucune | — | — | — | aucune réponse |

## C++

Registre : archive d'Ubuntu 24.04 ; statistique : installations (popcon de Debian ; celui d'Ubuntu n'est plus publié : écart 2).

L'index d'Ubuntu publié par ecosyste.ms n'a pas de descriptions : la recherche ne lit que les noms des paquets.

| Case | Note publiée | Retenue | Version | Rang | Statistique | Refusées avant elle |
|---|---|---|---|---|---|---|
| A6 | 0 | aucune | — | — | — | aucune réponse |
| F2 | 0 | hwloc | 2.10.0 (paquet Ubuntu libhwloc-dev 2.10.0-1build1) | 1 | 3 053 |  |

Cellules du plafond attribuées (3.4) :

* hwloc : **aucune** (F2 : levier hors de la table de l'écart 3)

## C3

Registre : dépôt vendor de c3lang ; statistique : aucune : ancienneté de l'entrée dans le dépôt vendor (dépôt maintenu depuis le 22 novembre 2024).

Le dépôt vendor de C3 (27 bibliothèques, liaisons de bibliothèques C : box2d, curl, glfw, opengl…) ne contient aucune bibliothèque dont le nom ou la description porte un mot d'une case.

| Case | Note publiée | Retenue | Version | Rang | Statistique | Refusées avant elle |
|---|---|---|---|---|---|---|
| A6 | 0 | aucune | — | — | — | aucune réponse |
| C2 | 0.5 | aucune | — | — | — | aucune réponse |
| C5 | 0 | aucune | — | — | — | aucune réponse |
| D3 | 0 | aucune | — | — | — | aucune réponse |
| D4 | 0.5 | aucune | — | — | — | aucune réponse |
| D5 | 0.5 | aucune | — | — | — | aucune réponse |
| F1 | 0.5 | aucune | — | — | — | aucune réponse |
| F2 | 0 | aucune | — | — | — | aucune réponse |

## Zig

Registre : aucun : paquets par URL, sans registre ; statistique : —.

Zig n'a pas de registre : les paquets se déclarent par URL (build.zig.zon).

| Case | Note publiée | Retenue | Version | Rang | Statistique | Refusées avant elle |
|---|---|---|---|---|---|---|
| C2 | 0.5 | aucune | — | — | — | aucune réponse |
| C5 | 0 | aucune | — | — | — | aucune réponse |
| D5 | 0.5 | aucune | — | — | — | aucune réponse |
| F1 | 0.5 | aucune | — | — | — | aucune réponse |
| F2 | 0 | aucune | — | — | — | aucune réponse |

## Rust

Registre : crates.io ; statistique : téléchargements des 90 derniers jours (crates.io, recent_downloads).

A6 : la recherche de crates.io est en texte intégral ; « struct of arrays » ramène des crates très téléchargées sans rapport, et soa_derive, au 16e rang, n'est pas examinée (3.2 : les dix premières) : le trou reste.

| Case | Note publiée | Retenue | Version | Rang | Statistique | Refusées avant elle |
|---|---|---|---|---|---|---|
| A6 | 0 | aucune | — | — | — | arrayvec (vecteur de capacité fixe, pas de SoA) ; ndarray (tableaux à n dimensions, pas de SoA) ; daachorse (recherche de motifs) ; grid (grille 2D) ; array-macro (macro de construction) ; npyz (format de fichier NumPy) ; aneubeck-daachorse (recherche de motifs) ; cargo-make (outil de construction) ; clx (interface en ligne de commande) ; hdf5-pure (format HDF5) |
| B2 | 0.5 | bumpalo | 3.20.4 | 1 | 215 297 252 |  |
| C1 | 0.5 | fearless_simd | 1.2.0 | 5 | 15 119 210 | encoding_rs (encodages de texte) ; glam (géométrie 3D (2 à 4 composantes), pas de vecteurs SIMD de largeur et de type quelconques) ; simd_cesu8 (encodage CESU-8) ; pulp-wasm-simd-flag (drapeau de compilation de pulp) |
| C5 | 0 | rayon | 1.12.0 | 1 | 178 285 310 |  |
| D3 | 0 | cordyceps | 0.3.5 | 3 | 4 872 620 | unicode-ident (propriétés Unicode) ; unicode-id-start (propriétés Unicode) |
| D4 | 0 | core_affinity | 0.8.3 | 1 | 7 865 906 |  |
| F1 | 0.5 | ndarray | 0.17.2 | 1 | 37 960 350 |  |
| F2 | 0 | hwlocality-sys | 0.7.2 (sur libhwloc 2.10.0) | 1 | 738 576 |  |
| F4 | 0 | memmap2 | 0.9.12 | 1 | 124 137 808 |  |

Nommée par le dossier (3.3 c) : **libc** (0.2.191), pour D3, D4, F4 (sysconf(_SC_LEVEL1_DCACHE_LINESIZE), sched_setaffinity, mmap, comme pour C).

Nommée par le dossier (3.3 c) : **crossbeam** (0.8.5), pour D3 (crossbeam_utils::CachePadded).

Nommée par le dossier (3.3 c) : **rayon** (1.12.0), pour C5 (aussi retenue par la règle).

Cellules du plafond attribuées (3.4) :

* bumpalo : **K8** (B2 = ½ : arène (Bump) pour les nœuds de l'arbre)
  * K8 : op_bumpalo : nœuds de chaque requête alloués par Bump::alloc (liens &'b Node), arène remise à zéro par reset() ; parcours de la forme d'accès tuned_it
* cordyceps : **K3** (D3 = 0 : CachePadded pour espacer les compteurs)
  * K3 : op_cordyceps : compteurs de sw_padded dans cordyceps::util::CachePadded
* crossbeam : **K3** (D3 = 0 : crossbeam_utils::CachePadded)
  * K3 : op_crossbeam : compteurs de sw_padded dans crossbeam_utils::CachePadded
* libc : **K3** (D3 = 0 : taille de ligne lue par sysconf pour espacer les compteurs ; D4 et F4 hors de la table)
  * K3 : op_libc : compteurs de sw_padded espacés de sysconf(_SC_LEVEL1_DCACHE_LINESIZE) octets, lu à l'exécution
* fearless_simd : **aucune** (C2 = 1 : std::arch donne déjà les intrinsèques)
* ndarray : **aucune** (C2 = 1)
* rayon : **aucune** (D1 = 1 (std::thread))
* core_affinity : **aucune** (D4 : levier hors de la table de l'écart 3)
* hwlocality-sys : **aucune** (F2 : levier hors de la table de l'écart 3)
* memmap2 : **aucune** (F4 : levier hors de la table de l'écart 3)

## Nim

Registre : nimble (liste nim-lang/packages) ; statistique : aucune : ancienneté du premier commit (dépôt maintenu depuis le 22 novembre 2024).

| Case | Note publiée | Retenue | Version | Rang | Statistique | Refusées avant elle |
|---|---|---|---|---|---|---|
| A6 | 0 | aucune | — | — | — | aossoa (aucune version depuis le 22 novembre 2024 (3.3 b)) |
| B2 | 0.5 | aucune | — | — | — | sharedmempool (aucune version depuis le 22 novembre 2024 (3.3 b)) |
| C1 | 0 | mmops | 0.1.1 (étiquette 0.1.1, commit a3cf2a4 ; le fichier .nimble y porte 0.1.0 ; avec nimsimd 1.3.2) | 10 | 2025-07-27 → 2025-08-06 | constantine (cryptographie) ; nimsimd (liaisons aux intrinsèques x86, pas de types portables) ; crunchy (hachages) ; simdutf (Unicode) ; kaleidoscope (chaînes de caractères) ; floof (recherche floue) ; vecray (vecteurs de géométrie) ; sdfy (fonctions de distance) ; diffy (comparaison d'images) |
| C5 | 0.5 | aucune | — | — | — | httpx (serveur HTTP) ; nmr (gestionnaire de paquets) ; flowworkrunner (exécuteur de tâches d'une boîte à outils) ; sitmo (aucune version depuis le 22 novembre 2024) ; httpbeast (aucune version depuis le 22 novembre 2024) ; laser (aucune version depuis le 22 novembre 2024) ; css_html_minify (aucune version depuis le 22 novembre 2024) ; pipelines (aucune version depuis le 22 novembre 2024) ; StashTable (aucune version depuis le 22 novembre 2024) ; sha256_64B (aucune version depuis le 22 novembre 2024) |
| D3 | 0 | aucune | — | — | — | aucune réponse |
| F1 | 0.5 | arraymancer | 0.7.33 | 2 | 2017-04-13 → 2026-11-01 | glm (mathématiques graphiques) |
| F2 | 0 | aucune | — | — | — | aucune réponse |

Cellules du plafond attribuées (3.4) :

* mmops : **aucune** (C2 = 1 : importc depuis immintrin.h)
* arraymancer : **aucune** (C2 = 1)

## D

Registre : dub ; statistique : téléchargements du dernier mois (dub).

| Case | Note publiée | Retenue | Version | Rang | Statistique | Refusées avant elle |
|---|---|---|---|---|---|---|
| A6 | 0 | soa | 0.2.0 (étiquette v0.2.0) | 2 | 2 | soapclient (client SOAP) |
| B2 | 0.5 | aucune | — | — | — | aucune réponse |
| F1 | 0.5 | mir-algorithm | 3.22.5 (avec mir-core 1.7.4) | 1 | 21 245 |  |
| F2 | 0 | aucune | — | — | — | numath (bibliothèque mathématique) ; enumap (table d'énumération) |

Cellules du plafond attribuées (3.4) :

* soa : **K1** (A6 = 0 : conteneur SoA des particules)
  * K1 : op_soa : particules dans un SOA!Particle (un tableau par champ), boucle d'énergie de la forme soa sur ses champs
* mir-algorithm : **aucune** (C1 = C2 = 1)

## Ada

Registre : Alire (index) ; statistique : dépendants dans l'index.

| Case | Note publiée | Retenue | Version | Rang | Statistique | Refusées avant elle |
|---|---|---|---|---|---|---|
| A6 | 0 | aucune | — | — | — | aucune réponse |
| C5 | 0 | lwt | 1.2.0 (commit fedb90b de parasail, index d'Alire) | 3 | 0 | parallelize (exécution de commandes en parallèle) ; pico_st7789 (pilote d'écran) |
| D3 | 0 | cachelines | 0.1.0 (commit 5c97574, index d'Alire) | 1 | 0 |  |
| F2 | 0 | aucune | — | — | — | aucune réponse |
| F4 | 0.5 | aucune | — | — | — | aucune réponse |

Cellules du plafond attribuées (3.4) :

* lwt : **aucune** (D1 = 1 (tâches))
* cachelines : **K3** (D3 = 0 : compteurs alignés sur la ligne de cache)
  * K3 : op_cachelines : compteurs de sw_padded du type aligné et bourré de cachelines

## Chapel

Registre : Mason (registre) ; statistique : dépendants dans l'index.

Le registre Mason compte 28 bricks ; aucune ne porte un mot d'une case.

| Case | Note publiée | Retenue | Version | Rang | Statistique | Refusées avant elle |
|---|---|---|---|---|---|---|
| A6 | 0 | aucune | — | — | — | aucune réponse |
| B2 | 0.5 | aucune | — | — | — | aucune réponse |
| C1 | 0 | aucune | — | — | — | aucune réponse |
| C2 | 0.5 | aucune | — | — | — | aucune réponse |
| D3 | 0 | aucune | — | — | — | aucune réponse |
| D4 | 0.5 | aucune | — | — | — | aucune réponse |
| D5 | 0.5 | aucune | — | — | — | aucune réponse |
| E4 | 0.5 | aucune | — | — | — | aucune réponse |
| F4 | 0 | aucune | — | — | — | aucune réponse |

## Fortran

Registre : index des paquets de fortran-lang.org ; statistique : aucune : ancienneté du premier commit (dépôt maintenu depuis le 22 novembre 2024).

L'index de fortran-lang.org compte 272 bibliothèques ; aucune ne porte un mot d'une case.

| Case | Note publiée | Retenue | Version | Rang | Statistique | Refusées avant elle |
|---|---|---|---|---|---|---|
| A6 | 0 | aucune | — | — | — | aucune réponse |
| B2 | 0.5 | aucune | — | — | — | aucune réponse |
| C1 | 0 | aucune | — | — | — | aucune réponse |
| C2 | 0 | aucune | — | — | — | aucune réponse |
| D3 | 0 | aucune | — | — | — | aucune réponse |
| D5 | 0.5 | aucune | — | — | — | aucune réponse |
| E4 | 0 | aucune | — | — | — | aucune réponse |
| F2 | 0.5 | aucune | — | — | — | aucune réponse |
| F4 | 0 | aucune | — | — | — | aucune réponse |

## Swift

Registre : Swift Package Index ; statistique : aucune : ancienneté de la première version (versions depuis le 22 novembre 2024).

| Case | Note publiée | Retenue | Version | Rang | Statistique | Refusées avant elle |
|---|---|---|---|---|---|---|
| A6 | 0 | aucune | — | — | — | github.com/RedMadRobot/service-autograph (générateur de services) |
| B2 | 0.5 | github.com/swift-molecules/swift-memory-allocation | branche main, révision 8742a8c (aucune version publiée) | 1 | 2025-11-18 → 2025-12-19 |  |
| C2 | 0.5 | aucune | — | — | — | github.com/recp/cglm (mathématiques graphiques en C) |
| D3 | 0.5 | aucune | — | — | — | aucune réponse |
| D5 | 0.5 | aucune | — | — | — | github.com/Spinners/Spin.Swift (boucles de rétroaction, tests d'instantanés) ; github.com/kublaios/snapshotino (boucles de rétroaction, tests d'instantanés) |
| E4 | 0.5 | aucune | — | — | — | github.com/async-digital-ltd/look-ahead (préchargement de ressources ou d'images) ; github.com/malcommac/ImageSizeFetcher (préchargement de ressources ou d'images) |
| F1 | 0.5 | github.com/jjjkkkjjj/Matft | 1.0.1 (étiquette 1.0.1, commit bf66a10) | 4 | 2020-03-30 → 2026-09-27 | github.com/recp/cglm (mathématiques graphiques en C) ; github.com/capnslipp/Vuckt (vecteurs de géométrie) ; github.com/fireblade-engine/math (mathématiques 2D et 3D) |
| F2 | 0 | aucune | — | — | — | aucune réponse |

Cellules du plafond attribuées (3.4) :

* github.com/swift-molecules/swift-memory-allocation : **K8** (B2 = ½ : arène pour les nœuds de l'arbre)
  * K8 : op_arena : nœuds de chaque requête alloués par l'arène du produit « Memory Allocator Arena », libérée d'un bloc
* github.com/jjjkkkjjj/Matft : **aucune** (C1 = 1)

## Julia

Registre : General ; statistique : téléchargements du dernier mois (ecosyste.ms, JuliaHub).

Le relevé classe par les téléchargements du dernier mois publiés par ecosyste.ms ; contrôle par la statistique du plan, les requêtes du dernier mois aux serveurs de paquets (julialang-logs ; tools/open/julia_requests.py, results/open/registry/julia_requests.json) : les dix premières de chaque case sont les mêmes, dans le même ordre.

| Case | Note publiée | Retenue | Version | Rang | Statistique | Refusées avant elle |
|---|---|---|---|---|---|---|
| A6 | 0 | aucune | — | — | — | IndexedStructVectors (tables à identifiants stables, pas de SoA) |
| B2 | 0.5 | Bumper | 0.7.2 | 1 | 8 098 |  |
| C1 | 0.5 | VectorizationBase | 0.21.74 | 2 | 136 069 | CpuId (interrogation du processeur) |
| D3 | 0.5 | aucune | — | — | — | aucune réponse |
| D4 | 0.5 | ThreadPinningCore | 0.4.5 | 1 | 5 539 |  |
| F2 | 0.5 | NUMA | 0.1.1 | 5 | 45 | Hwloc_jll (paquet binaire (JLL) de la bibliothèque C, sans API Julia) ; Hwloc (lecture de la topologie, sans placement) ; ArrayAllocators (malloc et calloc seulement : l'allocation sur un nœud NUMA est dans le paquet séparé NumaAllocators) ; NUMA_jll (paquet binaire (JLL) de libnuma, sans API Julia) |

Cellules du plafond attribuées (3.4) :

* Bumper : **K8** (B2 = ½ : nœuds dans un tableau alloué par @alloc (allocateur à pointeur))
  * K8 : op_bumper : nœuds de chaque requête dans un tableau alloué par @alloc dans @no_escape (liens par indices)
* VectorizationBase : **aucune** (C2 = 1)
* ThreadPinningCore : **aucune** (D4 : levier hors de la table de l'écart 3)
* NUMA : **aucune** (F2 : levier hors de la table de l'écart 3)

## Mojo

Registre : paquets de Modular et canal modular-community ; statistique : aucune : ancienneté de la première version (canal modular-community ; MAX : paquet de Modular).

Le canal modular-community ne publie que des noms de paquets ; aucun ne porte un mot d'une case. MAX, nommé par le dossier, entre par 3.3 c.

| Case | Note publiée | Retenue | Version | Rang | Statistique | Refusées avant elle |
|---|---|---|---|---|---|---|
| A6 | 0 | aucune | — | — | — | aucune réponse |
| B2 | 0.5 | aucune | — | — | — | aucune réponse |
| C5 | 0 | aucune | — | — | — | aucune réponse |
| D1 | 0.5 | aucune | — | — | — | aucune réponse |
| D3 | 0 | aucune | — | — | — | aucune réponse |
| D4 | 0 | aucune | — | — | — | aucune réponse |
| F1 | 0.5 | aucune | — | — | — | aucune réponse |
| F2 | 0 | aucune | — | — | — | aucune réponse |
| F4 | 0 | aucune | — | — | — | aucune réponse |

Nommée par le dossier (3.3 c) : **MAX 26.7.0** (26.7.0 (paquet conda max-core 26.7.0)), pour C5, D1, F1 (max.algorithm.functional.sync_parallelize (boucle parallèle sur les cœurs), LayoutTensor ; paquet conda max-core 26.7.0, lié à Mojo 1.2.0).

Cellules du plafond attribuées (3.4) :

* MAX 26.7.0 : **Q6 mt, Q1 mt, K9 mt, K3** (D1 = ½ : sync_parallelize répartit le calcul sur les cœurs ; F1 sans cellule (C1 = 1))
  * Q6 mt : op_max : sync_parallelize sur quatre tranches de lignes, sommes partielles réunies
  * Q1 mt : op_max : sync_parallelize sur quatre tranches, agrégats partiels fusionnés
  * K9 mt : op_max : sync_parallelize sur quatre bandes de lignes à chaque pas
  * K3 : op_max : quatre éléments de travail de sync_parallelize, chacun écrivain unique de son compteur bourré

## C#

Registre : NuGet ; statistique : téléchargements totaux (NuGet).

| Case | Note publiée | Retenue | Version | Rang | Statistique | Refusées avant elle |
|---|---|---|---|---|---|---|
| A6 | 0 | aucune | — | — | — | ServiceStack.Client (SOAP ou services, pas de SoA) ; ServiceStack (SOAP ou services, pas de SoA) ; SoapCore (SOAP ou services, pas de SoA) ; Microsoft.TeamFoundationServer.ExtendedClient (SOAP ou services, pas de SoA) ; ServiceStack.Core (SOAP ou services, pas de SoA) ; nsoftware.SecureBlackbox (SOAP ou services, pas de SoA) ; SimpleSOAPClient (SOAP ou services, pas de SoA) ; SoapFormatter (SOAP ou services, pas de SoA) ; SoapHttpClient (SOAP ou services, pas de SoA) ; WCFExtrasPlus (SOAP ou services, pas de SoA) |
| B2 | 0.5 | aucune | — | — | — | Microsoft.IO.RecyclableMemoryStream (réserve de tampons de flux, pas d'allocateur d'objets) ; CommunityToolkit.HighPerformance (tampons loués à ArrayPool, pas d'allocateur d'objets) ; StackExchange.Redis.Extensions.Core (client Redis) ; AsyncKeyedLock (verrous) ; BetterBuffers (réserve de tampons) ; FAkka.Microsoft.IO.RecyclableMemoryStream (réserve de tampons de flux) ; Stratis.Features.MemoryPool (réserve de transactions (chaîne de blocs)) ; Blockcore.Features.MemoryPool (réserve de transactions (chaîne de blocs)) ; Microsoft.IO.RecyclableMemoryStream.Net35 (réserve de tampons de flux) ; MemoryPools (réutilisation d'objets et de tampons, pas un allocateur ni une arène) |
| D3 | 0 | aucune | — | — | — | Microsoft.Extensions.Caching.SqlConfig.Tools (caches de données, pas d'aide ligne de cache) ; dotnet-sql-cache (caches de données, pas d'aide ligne de cache) ; LineTen.Cache.Memory (caches de données, pas d'aide ligne de cache) ; BlitzCache (caches de données, pas d'aide ligne de cache) ; LineTen.Cache.Redis (caches de données, pas d'aide ligne de cache) ; LineTen.Cache.Redis.Mod (caches de données, pas d'aide ligne de cache) ; LiteX.Cache (caches de données, pas d'aide ligne de cache) ; LiteX.Cache.Redis (caches de données, pas d'aide ligne de cache) ; LiteX.Cache.Core (caches de données, pas d'aide ligne de cache) ; LiteX.Cache.Memcached (caches de données, pas d'aide ligne de cache) |
| D4 | 0.5 | aucune | — | — | — | Microsoft.WindowsAzure.Management (sans rapport avec l'affinité processeur) ; Accusoft.PrizmDocRestClient (sans rapport avec l'affinité processeur) ; uMigrate (sans rapport avec l'affinité processeur) ; uMigrate.Core (sans rapport avec l'affinité processeur) ; VanLangen.Locking.ReadersWriterLockAsync (sans rapport avec l'affinité processeur) ; Autofac.Extras.FileSystemRegistration (sans rapport avec l'affinité processeur) ; Lepracaun (sans rapport avec l'affinité processeur) ; NCV.ISPSession (sans rapport avec l'affinité processeur) ; uScheduler (sans rapport avec l'affinité processeur) ; FurAffinityFs (sans rapport avec l'affinité processeur) |
| F2 | 0 | aucune | — | — | — | TcKimlikNumarasi-Dogrulama (sans rapport avec NUMA) ; Numaka.Common (sans rapport avec NUMA) ; TurkishTaxNumber (sans rapport avec NUMA) ; Numaka.Functions.Infrastructure (sans rapport avec NUMA) ; nuMapper (sans rapport avec NUMA) ; Numani.TypedFilePath (sans rapport avec NUMA) ; FourOne.Memes (sans rapport avec NUMA) ; Icod.Host (sans rapport avec NUMA) ; Numaka.Cryptography (sans rapport avec NUMA) ; Numaka.Messaging.RabbitMQ (sans rapport avec NUMA) |

## FreePascal

Registre : fppkg ; statistique : aucune (fppkg ne publie ni téléchargements ni dates).

Le dépôt fppkg de FreePascal 3.2.2 compte 6 paquets (cnocThreadingTools, dcserver, cerialization, cnocExpressionEvaluator, fpcdab, log4fpc) ; aucun ne porte un mot d'une case.

| Case | Note publiée | Retenue | Version | Rang | Statistique | Refusées avant elle |
|---|---|---|---|---|---|---|
| A6 | 0 | aucune | — | — | — | aucune réponse |
| B2 | 0.5 | aucune | — | — | — | aucune réponse |
| C1 | 0.5 | aucune | — | — | — | aucune réponse |
| C2 | 0.5 | aucune | — | — | — | aucune réponse |
| C5 | 0 | aucune | — | — | — | aucune réponse |
| D2 | 0.5 | aucune | — | — | — | aucune réponse |
| D3 | 0 | aucune | — | — | — | aucune réponse |
| D5 | 0.5 | aucune | — | — | — | aucune réponse |
| E4 | 0.5 | aucune | — | — | — | aucune réponse |
| F1 | 0.5 | aucune | — | — | — | aucune réponse |
| F2 | 0 | aucune | — | — | — | aucune réponse |

## Java

Registre : Maven Central ; statistique : dépendants de la version par défaut (deps.dev).

| Case | Note publiée | Retenue | Version | Rang | Statistique | Refusées avant elle |
|---|---|---|---|---|---|---|
| A6 | 0 | aucune | — | — | — | com.isuwang:isuwang-soa (cadres d'architecture orientée services (SOA), pas de SoA) ; org.membrane-soa:service-proxy-parent (cadres d'architecture orientée services (SOA), pas de SoA) ; com.predic8:soa-model-parent (cadres d'architecture orientée services (SOA), pas de SoA) ; io.github.hpsocket:hp-soa-framework (cadres d'architecture orientée services (SOA), pas de SoA) ; io.github.hpsocket:hp-soa-parent (cadres d'architecture orientée services (SOA), pas de SoA) ; io.github.hpsocket:hp-soa-dependencies (cadres d'architecture orientée services (SOA), pas de SoA) ; io.github.hpsocket:hp-soa-starter (cadres d'architecture orientée services (SOA), pas de SoA) ; com.github.dapeng-soa:dapeng-counter (cadres d'architecture orientée services (SOA), pas de SoA) ; com.github.dapeng-soa:dapeng-registry (cadres d'architecture orientée services (SOA), pas de SoA) ; com.github.dapeng-soa:dapeng-transaction (cadres d'architecture orientée services (SOA), pas de SoA) |
| B2 | 0.5 | aucune | — | — | — | org.uqbar-project:arena-core (cadre d'interface graphique « Arena ») ; org.uqbar-project:arena-jface (cadre d'interface graphique « Arena ») ; com.github.amitkhosla:memory-pool (réserve d'objets (ObjectPool), pas un allocateur ni une arène) ; com.arena-returns:Pbbl (application) ; im.arena:livescorecard (applications « arena ») ; im.arena:basiccard (applications « arena ») ; im.arena:header (applications « arena ») ; im.arena:profile (applications « arena ») ; im.arena:realtimedata (applications « arena ») ; im.arena:player (applications « arena ») |
| B5 | 0.5 | aucune | — | — | — | io.kjson:kjson-pointer-core (pointeurs JSON (RFC 6901)) ; org.webjars.npm:swaggerexpert__json-pointer (pointeurs JSON (RFC 6901)) ; org.webjars.npm:hyperjump__json-pointer (pointeurs JSON (RFC 6901)) ; org.webjars.npm:swagger-api__apidom-json-pointer (pointeurs JSON (RFC 6901)) ; io.kjson:kjson-pointer (pointeurs JSON (RFC 6901)) ; io.circe:circe-pointer_3 (pointeurs JSON (RFC 6901)) ; com.armanbilge:circe-pointer_3 (pointeurs JSON (RFC 6901)) ; com.armanbilge:circe-pointer_2.13 (pointeurs JSON (RFC 6901)) ; com.armanbilge:circe-pointer_2.12 (pointeurs JSON (RFC 6901)) ; io.circe:circe-pointer_2.13 (pointeurs JSON (RFC 6901)) |
| C1 | 0.5 | aucune | — | — | — | org.webjars.npm:types__mapbox__vector-tile (SIMD interne d'un interpréteur WebAssembly, d'un sérialiseur ou d'une bibliothèque d'inférence, ou types de tuiles vectorielles : pas de types vectoriels) ; com.dylibso.chicory:simd (SIMD interne d'un interpréteur WebAssembly, d'un sérialiseur ou d'une bibliothèque d'inférence, ou types de tuiles vectorielles : pas de types vectoriels) ; io.gravitee.inference.math.simd:gravitee-inference-math-simd (SIMD interne d'un interpréteur WebAssembly, d'un sérialiseur ou d'une bibliothèque d'inférence, ou types de tuiles vectorielles : pas de types vectoriels) ; org.apache.fory:fory-simd (SIMD interne d'un interpréteur WebAssembly, d'un sérialiseur ou d'une bibliothèque d'inférence, ou types de tuiles vectorielles : pas de types vectoriels) ; com.dylibso.chicory:simd-experimental (SIMD interne d'un interpréteur WebAssembly, d'un sérialiseur ou d'une bibliothèque d'inférence, ou types de tuiles vectorielles : pas de types vectoriels) ; au.gov.nehta:simd-wsdl-tls (SIMD interne d'un interpréteur WebAssembly, d'un sérialiseur ou d'une bibliothèque d'inférence, ou types de tuiles vectorielles : pas de types vectoriels) |
| C2 | 0 | aucune | — | — | — | org.webjars.npm:math-intrinsics (intrinsèques de JavaScript (webjars), d'un journal ou d'un compilateur ; bibliothèques natives qui n'exposent pas d'intrinsèques) ; org.mvnpm:math-intrinsics (intrinsèques de JavaScript (webjars), d'un journal ou d'un compilateur ; bibliothèques natives qui n'exposent pas d'intrinsèques) ; org.nd4j:nd4j-native-preset (intrinsèques de JavaScript (webjars), d'un journal ou d'un compilateur ; bibliothèques natives qui n'exposent pas d'intrinsèques) ; org.nd4j:nd4j-native (intrinsèques de JavaScript (webjars), d'un journal ou d'un compilateur ; bibliothèques natives qui n'exposent pas d'intrinsèques) ; br.dev.dig.logger:intrinsics (intrinsèques de JavaScript (webjars), d'un journal ou d'un compilateur ; bibliothèques natives qui n'exposent pas d'intrinsèques) ; org.qbicc:qbicc-plugin-intrinsics (intrinsèques de JavaScript (webjars), d'un journal ou d'un compilateur ; bibliothèques natives qui n'exposent pas d'intrinsèques) ; de.datexis:texoo-avx2 (intrinsèques de JavaScript (webjars), d'un journal ou d'un compilateur ; bibliothèques natives qui n'exposent pas d'intrinsèques) ; de.datexis:texoo-avx512 (intrinsèques de JavaScript (webjars), d'un journal ou d'un compilateur ; bibliothèques natives qui n'exposent pas d'intrinsèques) ; org.nd4j:libnd4j (intrinsèques de JavaScript (webjars), d'un journal ou d'un compilateur ; bibliothèques natives qui n'exposent pas d'intrinsèques) ; com.github.stephengold:jolt-jni-Windows64_avx2 (intrinsèques de JavaScript (webjars), d'un journal ou d'un compilateur ; bibliothèques natives qui n'exposent pas d'intrinsèques) |
| D3 | 0.5 | aucune | — | — | — | aucune réponse |
| D4 | 0 | net.openhft:affinity | 2026.2 | 3 | 51 | org.apache.bookkeeper:cpu-affinity (n'attribue que des cœurs isolés par le noyau (isolcpus), absents de cet hôte : ne s'exécute pas ici (3.3 a, 2)) ; io.streamnative:cpu-affinity (copie de la précédente, même limite) |
| E4 | 0 | aucune | — | — | — | org.commonjava.indy:indy-subsys-prefetch (préchargement de dépôts, de requêtes ou simulation, pas d'instruction de préchargement) ; at.borkowski.prefetch-simulation:core (préchargement de dépôts, de requêtes ou simulation, pas d'instruction de préchargement) ; at.borkowski.scovillej:prefetch (préchargement de dépôts, de requêtes ou simulation, pas d'instruction de préchargement) ; at.borkowski.prefetch-simulation:prefetch-simulation (préchargement de dépôts, de requêtes ou simulation, pas d'instruction de préchargement) ; at.borkowski.prefetch-simulation:visualiser (préchargement de dépôts, de requêtes ou simulation, pas d'instruction de préchargement) ; at.borkowski.prefetch-simulation:runner (préchargement de dépôts, de requêtes ou simulation, pas d'instruction de préchargement) ; at.borkowski.prefetch-simulation:regression (préchargement de dépôts, de requêtes ou simulation, pas d'instruction de préchargement) ; at.borkowski.prefetch-simulation:materialiser (préchargement de dépôts, de requêtes ou simulation, pas d'instruction de préchargement) |
| F1 | 0.5 | org.tensorflow:ndarray | 1.0.0 | 3 | 18 | org.webjars.npm:ndarray (bibliothèque JavaScript empaquetée (webjar)) ; org.webjars.npm:ndarray-ops (bibliothèque JavaScript empaquetée (webjar)) |
| F2 | 0 | org.apache.ignite:ignite-numa-allocator | 2.18.0 | 1 | 0 |  |

Cellules du plafond attribuées (3.4) :

* net.openhft:affinity : **aucune** (D4 : levier hors de la table de l'écart 3)
* org.tensorflow:ndarray : **aucune** (aucune opération de calcul (écart 3))
* org.apache.ignite:ignite-numa-allocator : **aucune** (F2 : levier hors de la table de l'écart 3)

## Go

Registre : modules (pkg.go.dev) ; statistique : « imported by » (pkg.go.dev).

| Case | Note publiée | Retenue | Version | Rang | Statistique | Refusées avant elle |
|---|---|---|---|---|---|---|
| A6 | 0 | aucune | — | — | — | github.com/SeanDolphin/bqschema (schémas, sérialisation, tableaux de bits ou tenseurs, pas de SoA) ; github.com/mumax/3/data (schémas, sérialisation, tableaux de bits ou tenseurs, pas de SoA) ; golang.org/x/tools/go/analysis/passes/unusedwrite (schémas, sérialisation, tableaux de bits ou tenseurs, pas de SoA) ; github.com/guonaihong/gout (schémas, sérialisation, tableaux de bits ou tenseurs, pas de SoA) ; github.com/vmihailenco/msgpack/v4 (schémas, sérialisation, tableaux de bits ou tenseurs, pas de SoA) ; github.com/go-openapi/swag/jsonutils (schémas, sérialisation, tableaux de bits ou tenseurs, pas de SoA) ; github.com/shamaton/msgpack (schémas, sérialisation, tableaux de bits ou tenseurs, pas de SoA) ; goki.dev/etable/v2/etensor (schémas, sérialisation, tableaux de bits ou tenseurs, pas de SoA) ; github.com/yourbasic/bit (schémas, sérialisation, tableaux de bits ou tenseurs, pas de SoA) ; github.com/USA-RedDragon/configulator (schémas, sérialisation, tableaux de bits ou tenseurs, pas de SoA) |
| B2 | 0.5 | aucune | — | — | — | github.com/valyala/bytebufferpool (réserve de tampons d'octets) ; github.com/pingcap/tidb/util/arena (arène d'octets d'un module interne de TiDB, sans objets typés) ; github.com/CannibalVox/cgoparam (paramètres de cgo) ; github.com/andy-kimball/arenaskl (liste à enjambements dans une arène) ; github.com/gobwas/pool (réserves de structures) ; github.com/rclone/rclone/lib/pool (réserve de tampons) ; github.com/kubeflow/arena/pkg/apis/types (outil Kubernetes) ; github.com/prysmaticlabs/prysm/v4/beacon-chain/operations/slashings (réserves applicatives, analyse JSON ou arène de mémoire C par cgo, sans objets Go) ; github.com/wundergraph/astjson (réserves applicatives, analyse JSON ou arène de mémoire C par cgo, sans objets Go) ; github.com/google/gapid/core/memory/arena (réserves applicatives, analyse JSON ou arène de mémoire C par cgo, sans objets Go) |
| C1 | 0.5 | aucune | — | — | — | github.com/bytedance/sonic (JSON, hachages, géométrie 2D/3D ou images : pas de types vectoriels SIMD) ; github.com/g3n/engine/math32 (JSON, hachages, géométrie 2D/3D ou images : pas de types vectoriels SIMD) ; github.com/minio/sha256-simd (JSON, hachages, géométrie 2D/3D ou images : pas de types vectoriels SIMD) ; golang.org/x/image/math/f64 (JSON, hachages, géométrie 2D/3D ou images : pas de types vectoriels SIMD) ; github.com/minio/blake2b-simd (JSON, hachages, géométrie 2D/3D ou images : pas de types vectoriels SIMD) ; github.com/templexxx/xor (JSON, hachages, géométrie 2D/3D ou images : pas de types vectoriels SIMD) ; github.com/minio/md5-simd (JSON, hachages, géométrie 2D/3D ou images : pas de types vectoriels SIMD) ; github.com/ungerik/go3d/vec3 (JSON, hachages, géométrie 2D/3D ou images : pas de types vectoriels SIMD) ; github.com/bamiaux/rez (JSON, hachages, géométrie 2D/3D ou images : pas de types vectoriels SIMD) ; github.com/emer/emergent/evec (JSON, hachages, géométrie 2D/3D ou images : pas de types vectoriels SIMD) |
| C2 | 0.5 | aucune | — | — | — | github.com/decred/dcrd/crypto/blake256 (hachages, journaux ou moteurs internes : pas d'intrinsèques exposées) ; github.com/emer/leabra/deep (hachages, journaux ou moteurs internes : pas d'intrinsèques exposées) ; github.com/seekerror/logw (hachages, journaux ou moteurs internes : pas d'intrinsèques exposées) ; github.com/monetarium/monetarium-node/crypto/blake256 (hachages, journaux ou moteurs internes : pas d'intrinsèques exposées) ; github.com/lemon4ksan/foundation/silicon/endian (hachages, journaux ou moteurs internes : pas d'intrinsèques exposées) ; github.com/gomlx/compute/gobackend (hachages, journaux ou moteurs internes : pas d'intrinsèques exposées) ; github.com/1lann/sha256-simd (hachages, journaux ou moteurs internes : pas d'intrinsèques exposées) ; github.com/znasllc-io/memql/component/provenance (hachages, journaux ou moteurs internes : pas d'intrinsèques exposées) ; github.com/bridgecrewio/goformation/v5/intrinsics (hachages, journaux ou moteurs internes : pas d'intrinsèques exposées) ; github.com/awslabs/goformation/v7/intrinsics (hachages, journaux ou moteurs internes : pas d'intrinsèques exposées) |
| C5 | 0 | github.com/samber/lo/parallel | v1.53.0 (module github.com/samber/lo) | 7 | 82 | github.com/influxdata/telegraf/plugins/inputs/lustre2 (greffon de collecte de Telegraf (Lustre)) ; go.chromium.org/luci/common/sync/parallel (réserve de tâches, sans boucle ni réduction parallèle) ; github.com/rlmcpherson/s3gof3r (transferts S3) ; github.com/u-root/u-root/pkg/dhclient (client DHCP) ; github.com/libp2p/go-libp2p-kad-dht/dual (table de hachage distribuée) ; github.com/Workiva/go-datastructures/btree/palm (arbre B parallèle) |
| D2 | 0.5 | aucune | — | — | — | sync/atomic (bibliothèque standard elle-même) ; go.uber.org/atomic (enveloppes des atomiques de sync/atomic, sans ordres explicites) ; golang.org/x/net/html/atom (fichiers, flux ou analyse, pas d'atomiques en mémoire) ; github.com/mmcdole/gofeed (fichiers, flux ou analyse, pas d'atomiques en mémoire) ; golang.org/x/tools/go/analysis/passes/atomic (fichiers, flux ou analyse, pas d'atomiques en mémoire) ; github.com/moby/sys/atomicwriter (fichiers, flux ou analyse, pas d'atomiques en mémoire) ; github.com/larksuite/oapi-sdk-go/v3 (fichiers, flux ou analyse, pas d'atomiques en mémoire) ; github.com/rogpeppe/go-internal/lockedfile (fichiers, flux ou analyse, pas d'atomiques en mémoire) ; github.com/dchest/safefile (fichiers, flux ou analyse, pas d'atomiques en mémoire) ; github.com/natefinch/atomic (fichiers, flux ou analyse, pas d'atomiques en mémoire) |
| D3 | 0 | github.com/templexxx/cpu | v0.1.1 | 1 | 19 |  |
| D5 | 0 | aucune | — | — | — | github.com/coreos/etcd/clientv3/concurrency (verrous distribués d'etcd) ; go.etcd.io/etcd/client/v3/concurrency (verrous distribués d'etcd) ; go.etcd.io/etcd/clientv3/concurrency (verrous distribués d'etcd) ; github.com/tj/go-spin (indicateur d'attente en terminal) ; github.com/gernest/wow/spin (indicateur d'attente en terminal) ; github.com/spinnaker/spin/cmd/gateclient (outil Spinnaker) ; github.com/elodina/siesta (client Kafka) ; github.com/marusama/cyclicbarrier (barrière de rendez-vous entre fils : ni barrière mémoire ni indication d'attente active (légende de D5, 3.3 a, 1)) ; github.com/cockroachdb/errors/barriers (« barrières » d'erreurs) ; github.com/fermyon/spin/sdk/go/v2/http (cadriciel Spin (WebAssembly)) |
| E4 | 0 | aucune | — | — | — | www.velocidex.com/golang/go-prefetch (préchargement de fichiers, de couches ou de requêtes, pas d'instruction de préchargement) ; github.com/ava-labs/avalanchego/vms/evm/prefetch (préchargement de fichiers, de couches ou de requêtes, pas d'instruction de préchargement) ; github.com/containerd/nydus-snapshotter/pkg/prefetch (préchargement de fichiers, de couches ou de requêtes, pas d'instruction de préchargement) ; github.com/Lakshmi-Priya-Ramisetty/healthcare-data-harmonization/mapping_engine/fetch (préchargement de fichiers, de couches ou de requêtes, pas d'instruction de préchargement) ; github.com/GoogleCloudPlatform/healthcare-data-harmonization/mapping_engine/fetch (préchargement de fichiers, de couches ou de requêtes, pas d'instruction de préchargement) ; github.com/springml-code/reltio-healthcare-data-harmonization/mapping_engine/fetch (préchargement de fichiers, de couches ou de requêtes, pas d'instruction de préchargement) ; github.com/spiral/jobs/v2 (préchargement de fichiers, de couches ou de requêtes, pas d'instruction de préchargement) ; github.com/bazel-contrib/rules_img/img_tool/pkg/prefetch (préchargement de fichiers, de couches ou de requêtes, pas d'instruction de préchargement) ; github.com/dmundt/go-cask/cas/cache/prefetch (préchargement de fichiers, de couches ou de requêtes, pas d'instruction de préchargement) ; github.com/networkservicemesh/integration-tests/extensions/prefetch (préchargement de fichiers, de couches ou de requêtes, pas d'instruction de préchargement) |
| F1 | 0.5 | gonum.org/v1/gonum/mat | v0.17.0 (module gonum.org/v1/gonum) | 1 | 2 504 |  |
| F2 | 0 | github.com/benjojo/numa | v0.0.0-20260918214945-1058a779f434 (aucune version publiée) | 8 | 0 | github.com/jaypipes/ghw (découverte du matériel, sans placement) ; github.com/k8stopologyawareschedwg/numaplacement (ordonnancement Kubernetes) ; github.com/lrita/numa (ne se construit pas avec Go 1.27 (go:linkname vers runtime.systemstack, interdit) (3.3 a, 2)) ; github.com/zededa/ghw (découverte du matériel, sans placement) ; github.com/Jaganathancse/numautils (lecture de la topologie, sans placement) ; gitlab.com/blockforge/blockforge/pkg/hwloc (lecture de la topologie (hwloc), sans placement) ; github.com/arcticflint/numa (refusé par le proxy des modules de Go (403 SECURITY ERROR) : ne s'installe pas) |

Cellules du plafond attribuées (3.4) :

* github.com/samber/lo/parallel : **aucune** (D1 = 1 (goroutines))
* github.com/templexxx/cpu : **K3** (D3 = 0 : CacheLineSize pour espacer les compteurs)
  * K3 : op_cpu : compteurs de rmw_padded bourrés à cpu.CacheLineSize (type de bourrage du paquet s'il existe)
* gonum.org/v1/gonum/mat : **K9, K9 mt** (C1 = C2 = ½ : vues (Slice), Add et Scale de matrices float64 font la moyenne à quatre points ; K5 et K1 (float32), Q6 et Q1 (colonnes entières) : types absents ; K4 : aucune somme conditionnelle)
  * K9 : op_gonum : grilles en mat.Dense ; vues Slice des quatre voisins, Add trois fois puis Scale(0.25) dans la vue intérieure (ordre ((haut+bas)+gauche)+droite gardé)
  * K9 mt : op_gonum : la même suite d'opérations sur quatre bandes de lignes, une goroutine par bande
* github.com/benjojo/numa : **aucune** (F2 : levier hors de la table de l'écart 3)

## Haskell

Registre : Hackage ; statistique : téléchargements (page « top » de Hackage).

La page « top » de Hackage, titrée « Total downloads », donne en fait les téléchargements des 30 derniers jours : contrôlé paquet par paquet sur la page de chaque candidate (tools/open/hackage30.py, results/open/registry/haskell_30d.json : mêmes nombres, mêmes rangs). vector, primitive, unordered-containers et hashtables, nommées par le dossier, ne comblent aucun trou de Haskell.

| Case | Note publiée | Retenue | Version | Rang | Statistique | Refusées avant elle |
|---|---|---|---|---|---|---|
| A6 | 0 | aucune | — | — | — | moonlight-triangulation (triangulation) |
| B2 | 0.5 | aucune | — | — | — | frag (moteur de jeu) ; memory-pool (réserve de tampons épinglés, pas d'allocateur d'objets) ; arena (magasin de données journalisé) ; memorypool (réserve de mémoire brute hors tas, comme Foreign.Marshal.Pool déjà livré) ; cek-pykinos (pile et magasin d'un interpréteur) |
| C1 | 0.5 | aucune | — | — | — | hw-dsv (analyse CSV) ; hw-simd (primitives internes des analyseurs hw-*) ; sized-vector (vecteurs de taille au niveau des types, pas de SIMD) ; sdr (radio logicielle) ; hw-json-simd (analyse JSON) ; mersenne-random (générateur pseudo-aléatoire) ; wireform-core (primitives de formats) ; solana-haskell-sdk (chaîne de blocs) ; wireform-columnar-core (primitives de formats) ; simd (dépendances non résolubles avec GHC 9.14.1 (paquet de 2014) : ne s'installe pas) |
| C2 | 0 | aucune | — | — | — | llvm (liaisons au compilateur LLVM) ; blake3 (hachage) |
| C5 | 0.5 | parallel | 3.3.0.0 | 2 | 289 | futhark (autre langage et compilateur (3.3 a, 3)) |
| D2 | 0.5 | atomic-primops | 0.8.8 | 2 | 192 | hapistrano (déploiement) |
| D3 | 0 | aucune | — | — | — | pykinos-core (structures bloquées, pas d'aide ligne de cache) |
| D4 | 0.5 | aucune | — | — | — | aucune réponse |
| D5 | 0 | aucune | — | — | — | doctest-extract (tests) ; barrier (générateur de badges) ; concurrent-barrier (barrière de rendez-vous entre fils : ni barrière mémoire ni indication d'attente active (légende de D5, 3.3 a, 1)) ; cloudy (outil en ligne de commande pour lancer des machines dans le nuage) ; barrier-monad (monade de « barrière » (coroutines), sans barrière mémoire ni attente active) |
| F2 | 0 | aucune | — | — | — | aucune réponse |
| F4 | 0 | mmap | 0.5.9 | 2 | 72 | JuicyPixels (images) |

Cellules du plafond attribuées (3.4) :

* parallel : **aucune** (D1 = 1 (forkOn))
* atomic-primops : **aucune** (D2 : levier hors de la table de l'écart 3)
* mmap : **aucune** (F4 : levier hors de la table de l'écart 3)

## OCaml

Registre : opam ; statistique : dépendants inverses (« Required by », opam.ocaml.org).

Statistique : nombre de paquets d'opam qui en dépendent (« Required by », opam.ocaml.org), relevé page par page. opam n'est pas sur l'hôte : les versions publiées dans opam sont prises à leurs sources (archives de version, ou étiquette git quand l'archive n'est pas joignable) et construites avec dune 3.25.0, amorcé depuis ses sources avec OCaml 5.5.2.

| Case | Note publiée | Retenue | Version | Rang | Statistique | Refusées avant elle |
|---|---|---|---|---|---|---|
| A6 | 0 | aucune | — | — | — | aucune réponse |
| B2 | 0 | aucune | — | — | — | aucune réponse |
| B5 | 0.5 | aucune | — | — | — | hweak (table de hachage à pointeurs faibles) ; json-pointer (JSON Pointer (RFC 6901)) ; ocaml-options-only-flambda-fp (option de construction du compilateur (pointeurs de trame)) ; jsonschema-core (schémas JSON) ; ocaml-options-only-fp (option de construction du compilateur (pointeurs de trame)) |
| C1 | 0 | aucune | — | — | — | rake (autre langage (compilateur de Rake), pas une API OCaml) ; xoshiro-simd (générateur pseudo-aléatoire ; aucun type vectoriel exposé) |
| C2 | 0 | ocaml_intrinsics_kernel | v0.17.3 | 2 | 2 | bigstringaf (ses « intrinsics » sont des primitives d'accès aux bigstrings, pas des instructions de la cible) |
| C5 | 0 | domainslib | 0.5.2 (avec saturn 1.0.0, domain-local-await 1.0.1, multicore-magic 2.3.2, backoff 0.1.1, thread-table 1.0.0) | 2 | 4 | domain_shims (Domain non parallèle, pour OCaml 4) |
| D2 | 0.5 | aucune | — | — | — | dscheck (vérificateur de modèle pour les tests) ; atomic (rétroportage du module Atomic de la bibliothèque standard, sans ordre mémoire explicite) ; multicore-magic-dscheck (variante de test de multicore-magic pour DScheck) |
| D4 | 0 | processor | 0.2 | 1 | 1 |  |
| D5 | 0.5 | aucune | — | — | — | spin (générateur de projets) ; opam-spin (greffon d'opam pour le générateur Spin) |
| E4 | 0 | aucune | — | — | — | aucune réponse |
| F2 | 0 | aucune | — | — | — | numalib (ne s'installe pas avec OCaml 5.5.2 (3.3 a, 2) : construite par jbuilder ; dune 3.25 ignore ses fichiers jbuild et n'en construit aucun module ; dépend aussi de core et async ≥ v0.9 (2017)) ; conf-numa (paquet de configuration (présence de libnuma), sans API) |

Cellules du plafond attribuées (3.4) :

* ocaml_intrinsics_kernel : **K4, Q6, Q6 mt** (C1 = C2 = 0 : Conditional.select_int fait sans branchement la somme sous condition de K4 et de Q6 ; ni vecteurs ni opérations sur tableaux pour K1, K5, Q1 et K9)
  * K4 : op_intrinsics : somme conditionnelle de la forme tuned par Conditional.select_int
  * Q6 : op_intrinsics : filtre de la forme tuned_s par Conditional.select_int
  * Q6 mt : op_intrinsics : la même sélection dans la forme mt_pool_s
* domainslib : **aucune** (D1 = 1 (Domain))
* processor : **aucune** (D4 : levier hors de la table de l'écart 3)

## BQN

Registre : aucun : aucun gestionnaire de paquets ; statistique : —.

BQN n'a pas de gestionnaire de paquets.

| Case | Note publiée | Retenue | Version | Rang | Statistique | Refusées avant elle |
|---|---|---|---|---|---|---|
| A6 | 0 | aucune | — | — | — | aucune réponse |
| B2 | 0 | aucune | — | — | — | aucune réponse |
| B5 | 0.5 | aucune | — | — | — | aucune réponse |
| C1 | 0 | aucune | — | — | — | aucune réponse |
| C2 | 0 | aucune | — | — | — | aucune réponse |
| C5 | 0 | aucune | — | — | — | aucune réponse |
| D1 | 0 | aucune | — | — | — | aucune réponse |
| D2 | 0 | aucune | — | — | — | aucune réponse |
| D3 | 0 | aucune | — | — | — | aucune réponse |
| D4 | 0 | aucune | — | — | — | aucune réponse |
| D5 | 0 | aucune | — | — | — | aucune réponse |
| E4 | 0 | aucune | — | — | — | aucune réponse |
| F2 | 0 | aucune | — | — | — | aucune réponse |

## JavaScript

Registre : npm ; statistique : téléchargements du dernier mois (api.npmjs.org).

| Case | Note publiée | Retenue | Version | Rang | Statistique | Refusées avant elle |
|---|---|---|---|---|---|---|
| A6 | 0 | aucune | — | — | — | json5 (sérialisation, files, copies ou interpolation, pas de SoA) ; yocto-queue (sérialisation, files, copies ou interpolation, pas de SoA) ; jest-util (sérialisation, files, copies ou interpolation, pas de SoA) ; available-typed-arrays (sérialisation, files, copies ou interpolation, pas de SoA) ; d3-interpolate (sérialisation, files, copies ou interpolation, pas de SoA) ; fast-copy (sérialisation, files, copies ou interpolation, pas de SoA) ; shallow-clone (sérialisation, files, copies ou interpolation, pas de SoA) ; restructure (sérialisation, files, copies ou interpolation, pas de SoA) ; arr-union (sérialisation, files, copies ou interpolation, pas de SoA) ; json-stringify-pretty-compact (sérialisation, files, copies ou interpolation, pas de SoA) |
| B2 | 0 | @protobufjs/pool | 1.1.0 | 1 | 404 490 890 |  |
| B5 | 0.5 | aucune | — | — | — | lru-cache (caches, analyse ou pointeurs JSON, pas de mémoire brute) ; mdast-util-to-markdown (caches, analyse ou pointeurs JSON, pas de mémoire brute) ; yauzl (caches, analyse ou pointeurs JSON, pas de mémoire brute) ; is-unsafe (caches, analyse ou pointeurs JSON, pas de mémoire brute) ; @cacheable/memory (caches, analyse ou pointeurs JSON, pas de mémoire brute) ; @jsonjoy.com/json-pointer (caches, analyse ou pointeurs JSON, pas de mémoire brute) ; hast-util-raw (caches, analyse ou pointeurs JSON, pas de mémoire brute) ; rehype-raw (caches, analyse ou pointeurs JSON, pas de mémoire brute) ; @better-auth/memory-adapter (caches, analyse ou pointeurs JSON, pas de mémoire brute) ; stream-json (caches, analyse ou pointeurs JSON, pas de mémoire brute) |
| C1 | 0 | aucune | — | — | — | mime-types (types MIME) ; @supabase/storage-js (client de stockage) ; gl-matrix (vecteurs et matrices de géométrie (2 à 4 composantes), pas de types SIMD) ; @mapbox/vector-tile (tuiles vectorielles, icônes ou géométrie) ; @maplibre/geojson-vt (tuiles vectorielles, icônes ou géométrie) ; @maplibre/vt-pbf (tuiles vectorielles, icônes ou géométrie) ; @expo/vector-icons (tuiles vectorielles, icônes ou géométrie) ; @dnd-kit/geometry (tuiles vectorielles, icônes ou géométrie) ; @math.gl/core (tuiles vectorielles, icônes ou géométrie) ; zbsearch (tuiles vectorielles, icônes ou géométrie) |
| C2 | 0 | aucune | — | — | — | get-intrinsic (intrinsèques du langage JavaScript, pas du processeur) ; math-intrinsics (intrinsèques du langage JavaScript) ; call-bound (intrinsèques du langage JavaScript) ; cpu-features (détection des fonctions du processeur) ; bun (autre mise en œuvre du langage (3.3 a, 3)) ; @oven/bun-linux-x64-baseline (binaires de Bun ou outils de test) ; ses (binaires de Bun ou outils de test) ; @oven/bun-windows-x64-baseline (binaires de Bun ou outils de test) ; @oven/bun-darwin-x64-baseline (binaires de Bun ou outils de test) ; jest-light-runner (binaires de Bun ou outils de test) |
| C5 | 0 | aucune | — | — | — | run-parallel (fonctions asynchrones sur un seul fil, outils en ligne de commande ou géométrie : pas de boucle parallèle sur plusieurs cœurs) ; merge2 (fonctions asynchrones sur un seul fil, outils en ligne de commande ou géométrie : pas de boucle parallèle sur plusieurs cœurs) ; asynckit (fonctions asynchrones sur un seul fil, outils en ligne de commande ou géométrie : pas de boucle parallèle sur plusieurs cœurs) ; npm-run-all (fonctions asynchrones sur un seul fil, outils en ligne de commande ou géométrie : pas de boucle parallèle sur plusieurs cœurs) ; parallel-transform (fonctions asynchrones sur un seul fil, outils en ligne de commande ou géométrie : pas de boucle parallèle sur plusieurs cœurs) ; npm-run-all2 (fonctions asynchrones sur un seul fil, outils en ligne de commande ou géométrie : pas de boucle parallèle sur plusieurs cœurs) ; @turf/boolean-parallel (fonctions asynchrones sur un seul fil, outils en ligne de commande ou géométrie : pas de boucle parallèle sur plusieurs cœurs) ; fastparallel (fonctions asynchrones sur un seul fil, outils en ligne de commande ou géométrie : pas de boucle parallèle sur plusieurs cœurs) ; run-parallel-limit (fonctions asynchrones sur un seul fil, outils en ligne de commande ou géométrie : pas de boucle parallèle sur plusieurs cœurs) ; array-parallel (fonctions asynchrones sur un seul fil, outils en ligne de commande ou géométrie : pas de boucle parallèle sur plusieurs cœurs) |
| D1 | 0.5 | aucune | — | — | — | @emnapi/wasi-threads (fils de WebAssembly (WASI)) ; @tailwindcss/oxide-wasm32-wasi (binaire d'un outil) ; react-native-worklets (React Native) ; @loaders.gl/worker-utils (tâches sur des workers, déjà livrés (worker_threads)) ; @sanity/worker-channels (canaux entre workers) ; threads (enveloppe de worker_threads, déjà livrés : n'ajoute rien à la case) ; @copilotkit/web-components (composants web) ; @convex-dev/agent (agents) ; @phenomnomnominal/worker-require (enveloppe de worker_threads) ; bare-worker (autre environnement d'exécution (Bare)) |
| D2 | 0.5 | aucune | — | — | — | write-file-atomic (écritures de fichiers atomiques, CSS atomique ou limiteurs de débit, pas d'atomiques à ordres explicites) ; styleq (écritures de fichiers atomiques, CSS atomique ou limiteurs de débit, pas d'atomiques à ordres explicites) ; rate-limiter-flexible (écritures de fichiers atomiques, CSS atomique ou limiteurs de débit, pas d'atomiques à ordres explicites) ; @unocss/core (écritures de fichiers atomiques, CSS atomique ou limiteurs de débit, pas d'atomiques à ordres explicites) ; @vanilla-extract/sprinkles (écritures de fichiers atomiques, CSS atomique ou limiteurs de débit, pas d'atomiques à ordres explicites) ; @deepseek-ai/dsh-atomic-write (écritures de fichiers atomiques, CSS atomique ou limiteurs de débit, pas d'atomiques à ordres explicites) ; unocss (écritures de fichiers atomiques, CSS atomique ou limiteurs de débit, pas d'atomiques à ordres explicites) ; @types/write-file-atomic (écritures de fichiers atomiques, CSS atomique ou limiteurs de débit, pas d'atomiques à ordres explicites) ; coincident (écritures de fichiers atomiques, CSS atomique ou limiteurs de débit, pas d'atomiques à ordres explicites) ; @ava/write-file-atomic (écritures de fichiers atomiques, CSS atomique ou limiteurs de débit, pas d'atomiques à ordres explicites) |
| D3 | 0 | aucune | — | — | — | lru-cache (caches de données ou de fichiers) ; ws (caches de données ou de fichiers) ; globals (caches de données ou de fichiers) ; keyv (caches de données ou de fichiers) ; fresh (caches de données ou de fichiers) ; flat-cache (caches de données ou de fichiers) ; file-entry-cache (caches de données ou de fichiers) ; yn (caches de données ou de fichiers) ; v8-compile-cache-lib (caches de données ou de fichiers) ; read-cache (caches de données ou de fichiers) |
| D4 | 0 | aucune | — | — | — | pirates (chargement de modules, réserves de workers ou détection de l'architecture, pas d'affinité) ; @napi-rs/wasm-runtime (chargement de modules, réserves de workers ou détection de l'architecture, pas d'affinité) ; thread-stream (chargement de modules, réserves de workers ou détection de l'architecture, pas d'affinité) ; tinypool (chargement de modules, réserves de workers ou détection de l'architecture, pas d'affinité) ; cpu-features (chargement de modules, réserves de workers ou détection de l'architecture, pas d'affinité) ; arch (chargement de modules, réserves de workers ou détection de l'architecture, pas d'affinité) ; workerpool (chargement de modules, réserves de workers ou détection de l'architecture, pas d'affinité) ; expo-modules-jsi (chargement de modules, réserves de workers ou détection de l'architecture, pas d'affinité) ; system-architecture (chargement de modules, réserves de workers ou détection de l'architecture, pas d'affinité) ; pidusage (chargement de modules, réserves de workers ou détection de l'architecture, pas d'affinité) |
| D5 | 0.5 | aucune | — | — | — | prismjs (coloration, temporisation ou attente d'un port, pas de barrière ni d'attente active) ; debounce (coloration, temporisation ou attente d'un port, pas de barrière ni d'attente active) ; throttleit (coloration, temporisation ou attente d'un port, pas de barrière ni d'attente active) ; debounce-fn (coloration, temporisation ou attente d'un port, pas de barrière ni d'attente active) ; wait-on (coloration, temporisation ou attente d'un port, pas de barrière ni d'attente active) ; tcp-port-used (coloration, temporisation ou attente d'un port, pas de barrière ni d'attente active) ; wait-port (coloration, temporisation ou attente d'un port, pas de barrière ni d'attente active) ; @types/wait-on (coloration, temporisation ou attente d'un port, pas de barrière ni d'attente active) ; p-wait-for (coloration, temporisation ou attente d'un port, pas de barrière ni d'attente active) ; @1natsu/wait-element (coloration, temporisation ou attente d'un port, pas de barrière ni d'attente active) |
| E4 | 0 | aucune | — | — | — | @module-federation/data-prefetch (préchargement de ressources web) ; @deepseek-ai/dsh-client-hmr (préchargement de ressources web) ; dns-prefetch-control (préchargement de ressources web) ; @plasmicapp/prepass (préchargement de ressources web) ; promise-memoize (préchargement de ressources web) ; node-red-contrib-amqp-ack (préchargement de ressources web) ; vue-router-prefetch (préchargement de ressources web) ; @edgio/svelte (préchargement de ressources web) ; gatsby-plugin-prefetch-google-fonts (préchargement de ressources web) ; @layer0/svelte (préchargement de ressources web) |
| F1 | 0 | ndarray | 1.1.1 | 2 | 11 788 151 | gl-matrix (matrices de géométrie (2 à 4 composantes)) |
| F2 | 0 | aucune | — | — | — | testcheck (sans rapport avec NUMA) ; react-native-ansi-view (sans rapport avec NUMA) ; @tokensrc/codex (sans rapport avec NUMA) ; @numa-tech/numa (sans rapport avec NUMA) ; @numa-tech/cli-auth (sans rapport avec NUMA) ; nminer (sans rapport avec NUMA) ; @sinete/rejeicoes (sans rapport avec NUMA) ; @numacli/cli (sans rapport avec NUMA) ; @henriquegnandt/freelens-cluster-groups (sans rapport avec NUMA) ; @henriquegnandt/openlens-cluster-groups (sans rapport avec NUMA) |
| F4 | 0 | aucune | — | — | — | convert-source-map (cartes de sources ou fonctions « map », pas de projection en mémoire) ; @jridgewell/gen-mapping (cartes de sources ou fonctions « map », pas de projection en mémoire) ; side-channel-map (cartes de sources ou fonctions « map », pas de projection en mémoire) ; concat-map (cartes de sources ou fonctions « map », pas de projection en mémoire) ; is-map (cartes de sources ou fonctions « map », pas de projection en mémoire) ; p-map (cartes de sources ou fonctions « map », pas de projection en mémoire) ; @jridgewell/source-map (cartes de sources ou fonctions « map », pas de projection en mémoire) ; jest-haste-map (cartes de sources ou fonctions « map », pas de projection en mémoire) ; quick-lru (cartes de sources ou fonctions « map », pas de projection en mémoire) ; @cacheable/memory (cartes de sources ou fonctions « map », pas de projection en mémoire) |

Cellules du plafond attribuées (3.4) :

* @protobufjs/pool : **K8** (B2 = 0 : nœuds de l'arbre dans des tranches d'un bloc commun)
  * K8 : op_pool : nœuds de chaque requête dans des vues typées de tranches données par pool(alloc, slice, taille)
* ndarray : **aucune** (aucune opération de calcul (écart 3))

## PHP

Registre : Packagist ; statistique : téléchargements du dernier mois (Packagist).

| Case | Note publiée | Retenue | Version | Rang | Statistique | Refusées avant elle |
|---|---|---|---|---|---|---|
| A6 | 0 | aucune | — | — | — | laminas/laminas-soap (SOAP, pas de SoA) ; codeception/lib-xml (SOAP, pas de SoA) ; php-soap/wsdl (SOAP, pas de SoA) ; php-soap/engine (SOAP, pas de SoA) ; phpro/soap-client (SOAP, pas de SoA) ; php-soap/psr18-transport (SOAP, pas de SoA) ; php-soap/wsdl-reader (SOAP, pas de SoA) ; php-soap/ext-soap-engine (SOAP, pas de SoA) ; robrichards/wse-php (SOAP, pas de SoA) ; microsoft/bingads (SOAP, pas de SoA) |
| B2 | 0 | aucune | — | — | — | voku/agent-learning (sans rapport avec l'allocation) ; bvanhoekelen/performance (sans rapport avec l'allocation) ; voku/agent-loop (sans rapport avec l'allocation) ; vizra/vizra-adk (sans rapport avec l'allocation) ; jenner/timer (sans rapport avec l'allocation) ; keyagency/statamic-asset-usage (sans rapport avec l'allocation) ; ashrafic/laravel-ai-orbit (sans rapport avec l'allocation) ; axisvela/praxo-core (sans rapport avec l'allocation) ; fillup/fake-bower-assets (sans rapport avec l'allocation) ; atannex/limiting (sans rapport avec l'allocation) |
| B5 | 0.5 | aucune | — | — | — | ergebnis/json-pointer (pointeurs JSON (RFC 6901), pas de mémoire brute) ; php-jsonpointer/php-jsonpointer (pointeurs JSON (RFC 6901), pas de mémoire brute) ; swaggest/json-diff (pointeurs JSON (RFC 6901), pas de mémoire brute) ; phrity/util-accessor (pointeurs JSON (RFC 6901), pas de mémoire brute) ; laminas/laminas-navigation (pointeurs JSON (RFC 6901), pas de mémoire brute) ; zendframework/zend-navigation (pointeurs JSON (RFC 6901), pas de mémoire brute) ; psx/json (pointeurs JSON (RFC 6901), pas de mémoire brute) ; remorhaz/php-json-pointer (pointeurs JSON (RFC 6901), pas de mémoire brute) ; stefna/json-pointer (pointeurs JSON (RFC 6901), pas de mémoire brute) ; gamringer/php-json-pointer (pointeurs JSON (RFC 6901), pas de mémoire brute) |
| C1 | 0 | aucune | — | — | — | martin-georgiev/postgresql-for-doctrine (vecteurs de PostgreSQL, icônes ou analyse JSON, pas de types vectoriels) ; symfony/ai-store (vecteurs de PostgreSQL, icônes ou analyse JSON, pas de types vectoriels) ; victor-prdh/recaptcha-bundle (vecteurs de PostgreSQL, icônes ou analyse JSON, pas de types vectoriels) ; partitech/doctrine-pgvector (vecteurs de PostgreSQL, icônes ou analyse JSON, pas de types vectoriels) ; dmhendricks/file-icon-vectors (vecteurs de PostgreSQL, icônes ou analyse JSON, pas de types vectoriels) ; log1x/blade-filetype-icons (vecteurs de PostgreSQL, icônes ou analyse JSON, pas de types vectoriels) ; awesome/simdjson_plus (vecteurs de PostgreSQL, icônes ou analyse JSON, pas de types vectoriels) ; siberfx/typesense-scout (vecteurs de PostgreSQL, icônes ou analyse JSON, pas de types vectoriels) ; jxlwqq/simditor (vecteurs de PostgreSQL, icônes ou analyse JSON, pas de types vectoriels) ; erikwang2013/webman-scout (vecteurs de PostgreSQL, icônes ou analyse JSON, pas de types vectoriels) |
| C2 | 0 | aucune | — | — | — | hcesrl/php-responsive-image-sizes (sans intrinsèques exposées) ; avxman/github (sans intrinsèques exposées) ; sanix-darker/cisv (sans intrinsèques exposées) ; regexp1987/blake3 (sans intrinsèques exposées) ; avxman/rewrite-url (sans intrinsèques exposées) ; avxman/rel-nofollow (sans intrinsèques exposées) ; avxman/ratings (sans intrinsèques exposées) ; avxman/clear-cache (sans intrinsèques exposées) ; avxman/breadcrumbs (sans intrinsèques exposées) |
| C5 | 0 | amphp/parallel-functions | 2.0.0 (avec amphp/parallel 2.4.0) | 10 | 154 931 | jean85/pretty-package-versions (versions des paquets) ; brianium/paratest (tests en parallèle (outil)) ; amphp/parallel (tâches dans des processus ou des fils, sans boucle ni réduction parallèle) ; php-parallel-lint/php-parallel-lint (outil de vérification de syntaxe) ; amphp/http-client (client HTTP) ; php-parallel-lint/php-console-highlighter (coloration de code) ; php-parallel-lint/php-console-color (couleurs de console) ; nette/tester (tests) ; spatie/async (tâches asynchrones dans des processus, sans boucle ni réduction parallèle) |
| D1 | 0.5 | aucune | — | — | — | amphp/parallel (des processus ; des fils seulement avec l'extension parallel, qui exige un PHP compilé ZTS (le PHP classé ne l'est pas)) ; nette/safe-stream (flux de fichiers) ; danog/loop (boucle d'événements) ; danog/ipc (communication entre processus) ; pocketmine/snooze (exige l'extension pthreads (ZTS)) ; pocketmine/raklib-ipc (communication entre fils de pthreads) ; spryker/oms-multi-thread (module de commerce) ; duncan3dc/fork-helper (processus (fork)) ; cheprasov/php-redis-lock (verrou Redis) ; ramon/chat (messagerie) |
| D2 | 0 | aucune | — | — | — | nette/safe-stream (opérations atomiques sur fichiers ou motifs de conception, pas d'atomiques en mémoire) ; spiral/files (opérations atomiques sur fichiers ou motifs de conception, pas d'atomiques en mémoire) ; kstmostofa/laravel-backfill (opérations atomiques sur fichiers ou motifs de conception, pas d'atomiques en mémoire) ; haddowg/json-api (opérations atomiques sur fichiers ou motifs de conception, pas d'atomiques en mémoire) ; contenir/contenir-config (opérations atomiques sur fichiers ou motifs de conception, pas d'atomiques en mémoire) ; packagefactory/atomicfusion-proptypes (opérations atomiques sur fichiers ou motifs de conception, pas d'atomiques en mémoire) ; yalesites-org/atomic (opérations atomiques sur fichiers ou motifs de conception, pas d'atomiques en mémoire) ; pattern-lab/core (opérations atomiques sur fichiers ou motifs de conception, pas d'atomiques en mémoire) ; alexhackney/laravel-doppler (opérations atomiques sur fichiers ou motifs de conception, pas d'atomiques en mémoire) ; flametrench/tenancy (opérations atomiques sur fichiers ou motifs de conception, pas d'atomiques en mémoire) |
| D3 | 0 | aucune | — | — | — | kevinrob/guzzle-cache-middleware (caches HTTP ou d'application) ; se7enxweb/ezownerchange (caches HTTP ou d'application) ; cobweb/flush_language_cache (caches HTTP ou d'application) ; smart-core/accelerator-cache-bundle (caches HTTP ou d'application) ; andydefer/php-jsonl (caches HTTP ou d'application) ; thekaziomar/laravel-atomic-cache (caches HTTP ou d'application) ; darkghosthunter/rememberable-query (caches HTTP ou d'application) ; ornicar/apc-bundle (caches HTTP ou d'application) ; soflomo/cache (caches HTTP ou d'application) ; sterner-stuff/cloudflare-cli (caches HTTP ou d'application) |
| D5 | 0 | aucune | — | — | — | phpmd/phpmd (widgets d'attente et outils, pas d'attente active) ; kartik-v/yii2-widget-touchspin (widgets d'attente et outils, pas d'attente active) ; kartik-v/yii2-widget-spinner (widgets d'attente et outils, pas d'attente active) ; serversideup/spin (widgets d'attente et outils, pas d'attente active) ; spinen/laravel-geometry (widgets d'attente et outils, pas d'attente active) ; alecrabbit/php-cli-snake (widgets d'attente et outils, pas d'attente active) ; spinx/sidekiq-job-php (widgets d'attente et outils, pas d'attente active) ; diversen/php-cli-spinners (widgets d'attente et outils, pas d'attente active) ; alecrabbit/php-console-spinner (widgets d'attente et outils, pas d'attente active) ; prismjs/prism (widgets d'attente et outils, pas d'attente active) |
| E4 | 0 | aucune | — | — | — | symfony/web-link (préchargement de pages web) ; facile-it/laminas-link-headers-module (préchargement de pages web) ; spatie/laravel-mix-preload (préchargement de pages web) ; katsana/prefetch (préchargement de pages web) ; wearerequired/required-google-analytics (préchargement de pages web) ; collab/module-quicklink (préchargement de pages web) ; tfd/laravel-well-known-traffic-advice (préchargement de pages web) ; hryvinskyi/magento2-external-media-prefetcher (préchargement de pages web) ; bnomei/kirby3-htmlhead (préchargement de pages web) ; hellonico/timber-weblink-extension (préchargement de pages web) |
| F1 | 0.5 | rindow/rindow-math-matrix | 2.2.0 | 7 | 33 861 | markbaker/matrix (matrices en tableaux PHP imbriqués, non contigus) ; tecnickcom/tc-lib-barcode (codes-barres) ; alexpechkarev/google-maps (API de cartes) ; markrogoyski/math-php (matrices en tableaux PHP imbriqués, non contigus) ; rogervila/array-diff-multidimensional (comparaison de tableaux) ; rubix/tensor (matrices en tableaux PHP imbriqués (l'extension C tensor, distincte, n'est pas ce paquet)) |
| F2 | 0 | aucune | — | — | — | epigra/tckimlik (sans rapport avec NUMA) ; numaxlab/nova-ckeditor5-classic (sans rapport avec NUMA) ; bahricanli/tckimlik (sans rapport avec NUMA) ; alcea/ro-num (sans rapport avec NUMA) ; numaxlab/geslib-files (sans rapport avec NUMA) ; hwlowell/request-cache (sans rapport avec NUMA) ; numaxlab/dilve-client (sans rapport avec NUMA) ; numaxlab/atomic-laravel (sans rapport avec NUMA) ; numaxlab/cegal-client (sans rapport avec NUMA) ; numaxlab/lunar-geslib (sans rapport avec NUMA) |
| F4 | 0 | aucune | — | — | — | symfony/routing (« map » au sens de correspondance, pas de projection en mémoire) ; ramsey/collection (« map » au sens de correspondance, pas de projection en mémoire) ; dasprid/enum (« map » au sens de correspondance, pas de projection en mémoire) ; composer/class-map-generator (« map » au sens de correspondance, pas de projection en mémoire) ; doctrine/persistence (« map » au sens de correspondance, pas de projection en mémoire) ; marc-mabe/php-enum (« map » au sens de correspondance, pas de projection en mémoire) ; doctrine/orm (« map » au sens de correspondance, pas de projection en mémoire) ; netresearch/jsonmapper (« map » au sens de correspondance, pas de projection en mémoire) ; cuyz/valinor (« map » au sens de correspondance, pas de projection en mémoire) ; symfony/asset-mapper (« map » au sens de correspondance, pas de projection en mémoire) |

Cellules du plafond attribuées (3.4) :

* amphp/parallel-functions : **Q6 mt, Q1 mt, K9 mt** (D1 = ½ : parallelMap répartit le calcul sur des processus ; sans mémoire partagée, pas K3)
  * Q6 mt : op_amphp : Amp\ParallelFunctions\parallelMap sur quatre tranches de lignes, sommes partielles réunies
  * Q1 mt : op_amphp : parallelMap sur quatre tranches, agrégats partiels fusionnés
  * K9 mt : op_amphp : parallelMap sur quatre bandes de lignes à chaque pas, bandes réassemblées
* rindow/rindow-math-matrix : **aucune** (opérations écrites en PHP (pilote MatlibPHP) : rien de compilé)

## Python

Registre : PyPI ; statistique : téléchargements du dernier mois (pypistats).

| Case | Note publiée | Retenue | Version | Rang | Statistique | Refusées avant elle |
|---|---|---|---|---|---|---|
| A6 | 0 | aucune | — | — | — | ibmmq (messagerie IBM MQ) ; pymqi (messagerie IBM MQ) |
| B2 | 0 | aucune | — | — | — | localarena (évaluation de modèles) |
| B5 | 0.5 | aucune | — | — | — | python-jsonpath (pointeurs JSON) ; json-spec (pointeurs JSON) ; pyjsonpatch (pointeurs JSON) ; pymemoryeditor (lecture de la mémoire d'autres processus, pas d'accès à de la mémoire brute du programme) |
| C1 | 0 | aucune | — | — | — | stringzilla (chaînes de caractères) ; numkong (fonctions de calcul sur tableaux, pas de types vectoriels) ; pysimdjson (analyse JSON) ; chonkie-core (découpage de texte) ; fastpybase64 (base64) ; pillow-simd (images) ; turbovec (quantification de vecteurs) ; pycrc32 (sommes de contrôle) |
| C2 | 0 | aucune | — | — | — | ovphysx (simulation physique) |
| C5 | 0.5 | dask | 2026.8.0 | 2 | 31 736 728 | pytest-cov (mesure de couverture des tests) |
| D1 | 0.5 | aucune | — | — | — | greenlet (coroutines sur un seul fil) ; multiprocess (processus, sans mémoire partagée ni fils parallèles) ; gevent (coroutines) ; func-timeout (délais) ; janus (files asynchrones) ; zthreading (enveloppes d'événements) ; pyleak (détection de fuites) ; stopit (délais) ; zernio-sdk (client d'API) ; aws-logging-handlers (journaux) |
| D2 | 0 | atomics | 1.0.3 | 10 | 52 810 | atomicwrites (écritures de fichiers) ; ase (simulation atomique) ; ufmt (formatage) ; atomicwrites-homeassistant (écritures de fichiers) ; django-pgtransaction (transactions de base de données) ; atomicx (entiers atomiques sans ordres mémoire explicites) ; nvalchemi-toolkit-ops (primitives GPU) ; atomos (primitives atomiques sans ordres mémoire explicites) ; atomic-physics (physique atomique) |
| D3 | 0 | aucune | — | — | — | aucune réponse |
| D5 | 0 | aucune | — | — | — | spin (outil de développement) |
| E4 | 0 | aucune | — | — | — | django-memoized-prefetch (préchargement de requêtes de base de données ou générateur en arrière-plan, pas d'instruction de préchargement) ; django-eagle (préchargement de requêtes de base de données ou générateur en arrière-plan, pas d'instruction de préchargement) ; graphene-django-optimizer (préchargement de requêtes de base de données ou générateur en arrière-plan, pas d'instruction de préchargement) ; prefetch-generator (préchargement de requêtes de base de données ou générateur en arrière-plan, pas d'instruction de préchargement) ; django-auto-prefetch (préchargement de requêtes de base de données ou générateur en arrière-plan, pas d'instruction de préchargement) |
| F1 | 0.5 | aucune | — | — | — | segno (codes QR) ; apprise (notifications) ; affine (transformations affines du plan) ; bitsandbytes (quantification pour GPU) ; blosc2 (tableaux compressés par blocs, non contigus en mémoire) ; svgelements (SVG) ; cma (optimisation) ; matrix-nio (client Matrix) ; cmaes (optimisation) ; canmatrix (bus automobile) |
| F2 | 0 | aucune | — | — | — | nsj-rest-lib2 (routes REST) |

Nommée par le dossier (3.3 c) : **numpy** (2.5.5), pour F1 (ndarray : tableau multidimensionnel contigu à disposition définie ; Numba et Polars, aussi nommés, sont exclus (3.3 a, 3)).

Cellules du plafond attribuées (3.4) :

* numpy : **K1, K4, K5, Q6, Q1, K9, Q6 mt, Q1 mt, K9 mt** (C1 = C2 = 0 : opérations compilées sur tableaux entiers ; formes à quatre fils par threading (le GIL est rendu pendant les opérations))
  * K1 : op_numpy : champs en tableaux float32, énergie par expression sur tableaux entiers sommée en float64
  * K4 : op_numpy : somme conditionnelle par masque (np.sum(a, where=a >= 128, dtype=np.int64))
  * K5 : op_numpy : np.dot sur float32
  * Q6 : op_numpy : masques booléens combinés, puis np.dot des colonnes filtrées
  * Q1 : op_numpy : groupes par np.bincount(clé, weights=…) sur les lignes filtrées
  * K9 : op_numpy : moyenne à quatre points par tranches de tableaux (((haut + bas) + gauche) + droite) * 0.25
  * Q6 mt : op_numpy : la forme Q6 sur quatre tranches, une par threading.Thread (NumPy rend le GIL)
  * Q1 mt : op_numpy : la forme Q1 sur quatre tranches, une par fil
  * K9 mt : op_numpy : la forme K9 sur quatre bandes de lignes, une par fil, à chaque pas
* dask : **Q6 mt, Q1 mt, K9 mt, K3** (D1 = ½ : ordonnanceur à fils (dask.array sur NumPy, delayed))
  * Q6 mt : op_dask : dask.array en quatre blocs, réduction calculée par l'ordonnanceur à fils (num_workers=4)
  * Q1 mt : op_dask : dask.array en quatre blocs, groupes par bloc (map_blocks) réduits par l'ordonnanceur à fils
  * K9 mt : op_dask : map_overlap(depth=1) de la moyenne à quatre points sur quatre bandes, ordonnanceur à fils
  * K3 : op_dask : quatre tâches dask.delayed, chacune écrivain unique de son compteur dans un tableau NumPy espacé de 64 octets
* atomics : **aucune** (D2 : levier hors de la table de l'écart 3)

## Lua

Registre : LuaRocks ; statistique : téléchargements (LuaRocks).

| Case | Note publiée | Retenue | Version | Rang | Statistique | Refusées avant elle |
|---|---|---|---|---|---|---|
| A6 | 0 | aucune | — | — | — | djerius/luaxml (XML, SOAP, structures C ou tableaux de bits, pas de SoA) ; tomasguisasola/luasoap (XML, SOAP, structures C ou tableaux de bits, pas de SoA) ; oberhofer/luacwrap (XML, SOAP, structures C ou tableaux de bits, pas de SoA) ; uoa-c4e/kong-plugin-uoa-soap-to-rest (XML, SOAP, structures C ou tableaux de bits, pas de SoA) ; cleoold/bitarray (XML, SOAP, structures C ou tableaux de bits, pas de SoA) ; marcosher1993-imit/kong-plugin-soap4kong (XML, SOAP, structures C ou tableaux de bits, pas de SoA) ; marcosher1993-imit/kong-plugin-soap4kong-generator (XML, SOAP, structures C ou tableaux de bits, pas de SoA) ; alex-mak/cmdbuild (XML, SOAP, structures C ou tableaux de bits, pas de SoA) ; arulkumaran456/kong-plugin-soap-transform (XML, SOAP, structures C ou tableaux de bits, pas de SoA) ; nessan/scribe (XML, SOAP, structures C ou tableaux de bits, pas de SoA) |
| B2 | 0 | aucune | — | — | — | mtdowling/tecs (LuaJIT seulement (FFI)) ; corrm/polyplug-guest (greffons) ; fastipc/fipc (LuaJIT seulement) ; jinganix/pbwire (codec Protobuf) |
| B5 | 0 | aucune | — | — | — | karlp/lua-mosquitto (liaisons à des bibliothèques C (MQTT, Modbus, compression, entrées), pas de mémoire brute) ; mah0x211/io-pread (liaisons à des bibliothèques C (MQTT, Modbus, compression, entrées), pas de mémoire brute) ; karlp/lua-libmodbus (liaisons à des bibliothèques C (MQTT, Modbus, compression, entrées), pas de mémoire brute) ; niecore/lua-mosquitto-v5 (liaisons à des bibliothèques C (MQTT, Modbus, compression, entrées), pas de mémoire brute) ; osch/compress.lzma (liaisons à des bibliothèques C (MQTT, Modbus, compression, entrées), pas de mémoire brute) ; -asm/mjolnir._asm.sys.mouse (liaisons à des bibliothèques C (MQTT, Modbus, compression, entrées), pas de mémoire brute) ; darkwiiplayer/rgbstr (liaisons à des bibliothèques C (MQTT, Modbus, compression, entrées), pas de mémoire brute) ; bluelua/bluelua-evdev (liaisons à des bibliothèques C (MQTT, Modbus, compression, entrées), pas de mémoire brute) ; jamescmartin/luasubprocess (liaisons à des bibliothèques C (MQTT, Modbus, compression, entrées), pas de mémoire brute) ; topogibra/lua-mosquitto-v52 (liaisons à des bibliothèques C (MQTT, Modbus, compression, entrées), pas de mémoire brute) |
| C1 | 0 | aucune | — | — | — | jdonaldson/hx-lua-simdjson (liaisons à simdjson, tableaux C ou champs de bits, pas de types vectoriels) ; fouriertransformer/lua-simdjson (liaisons à simdjson, tableaux C ou champs de bits, pas de types vectoriels) ; membphis/api7-lua-resty-simdjson (liaisons à simdjson, tableaux C ou champs de bits, pas de types vectoriels) ; mambrus/lua-ctables (liaisons à simdjson, tableaux C ou champs de bits, pas de types vectoriels) ; omikhleia/printoptions.sile (liaisons à simdjson, tableaux C ou champs de bits, pas de types vectoriels) ; freed-wu/bitset (liaisons à simdjson, tableaux C ou champs de bits, pas de types vectoriels) ; freed-wu/mpfonts (liaisons à simdjson, tableaux C ou champs de bits, pas de types vectoriels) ; luarocks/bitfield (liaisons à simdjson, tableaux C ou champs de bits, pas de types vectoriels) |
| C2 | 0 | aucune | — | — | — | 5inq-kiji/ion7-core (LuaJIT seulement (llama.cpp)) |
| C5 | 0 | aucune | — | — | — | benoitgermain/lanes (ne se construit pas avec Lua 5.5 (lua_newstate a changé de signature) (3.3 a, 2)) ; askyrme/luaproc (processus légers à messages, sans boucle ni réduction parallèle) ; pc/opencl (noyaux écrits en OpenCL C, autre langage) ; moyu/dromozoa-prl (virtualisation) ; luarocks/leda (chaînes de traitement à étages) ; seba/activelua-learningtool (objets actifs) ; aimingoo/harpseal (distribution de tâches) ; luarocks/simulua (simulation à événements discrets) ; aimingoo/tundrawolf (distribution de tâches pour nginx) ; freed-wu/oberdiek (paquets TeX) |
| D1 | 0 | moteus/lua-llthreads2 | 0.1.6-1 (étiquette v0.1.6) | 1 | 1 992 072 |  |
| D2 | 0 | aucune | — | — | — | slact/feedparser (thèmes, flux RSS ou limiteurs, pas d'atomiques) ; neorocks/onedarkpro.nvim (thèmes, flux RSS ou limiteurs, pas d'atomiques) ; neorocks/onenord.nvim (thèmes, flux RSS ou limiteurs, pas d'atomiques) ; neorocks/onedark.nvim (thèmes, flux RSS ou limiteurs, pas d'atomiques) ; neo451/feed.nvim (thèmes, flux RSS ou limiteurs, pas d'atomiques) ; benrob0329/lambda (thèmes, flux RSS ou limiteurs, pas d'atomiques) ; cxinu/rllib (thèmes, flux RSS ou limiteurs, pas d'atomiques) ; cvar1984/atomas (thèmes, flux RSS ou limiteurs, pas d'atomiques) ; snap/chemical-element (thèmes, flux RSS ou limiteurs, pas d'atomiques) ; mrjavad-seydi/lua-resty-adaptive-limit (thèmes, flux RSS ou limiteurs, pas d'atomiques) |
| D3 | 0 | aucune | — | — | — | kaio326/luamemo (sans rapport avec la ligne de cache) ; pyrex41/shen (sans rapport avec la ligne de cache) |
| D4 | 0 | aucune | — | — | — | umegaya/ffiex (LuaJIT seulement (FFI)) ; mahkoe/ezserv (serveur HTTP) |
| D5 | 0 | aucune | — | — | — | j-hui/fidget.nvim (indicateurs d'attente en terminal ou barrière d'OpenResty, pas de barrière ni d'attente active pour Lua) ; nstefan002/donut.nvim (indicateurs d'attente en terminal ou barrière d'OpenResty, pas de barrière ni d'attente active pour Lua) ; freed-wu/mpfonts (indicateurs d'attente en terminal ou barrière d'OpenResty, pas de barrière ni d'attente active pour Lua) ; tkolleh/roda (indicateurs d'attente en terminal ou barrière d'OpenResty, pas de barrière ni d'attente active pour Lua) ; xieyonn/spinner.nvim (indicateurs d'attente en terminal ou barrière d'OpenResty, pas de barrière ni d'attente active pour Lua) ; fesily/lua-resty-latch (indicateurs d'attente en terminal ou barrière d'OpenResty, pas de barrière ni d'attente active pour Lua) ; pigpigyyy/yarnflow (indicateurs d'attente en terminal ou barrière d'OpenResty, pas de barrière ni d'attente active pour Lua) |
| E4 | 0 | aucune | — | — | — | aucune réponse |
| F1 | 0 | pessoa736/vmsl | 1.1-2 (étiquette v1.1) | 7 | 109 | birchpointswe/santoku-matrix (exige Lua 5.1 (rockspec) : ne s'installe pas avec Lua 5.5) ; luarocks/numlua (archive source introuvable (GitHub Downloads) : ne s'installe pas) ; ladc/lgsl (LuaJIT seulement) ; luarocks/numextra (complément de numlua) ; wrwrwr/glyphify (images) ; erickprogramer/luandarray (le rockspec publié désigne des fichiers absents du dépôt : l'installation échoue) |
| F2 | 0 | aucune | — | — | — | aucune réponse |
| F4 | 0 | aucune | — | — | — | shmul/lightningmdb (base de données projetée (LMDB), pas d'API de projection de fichiers) ; geoffleyland/mmapfile (exige Lua 5.1 ou LuaJIT (rockspec) : ne s'installe pas avec Lua 5.5) ; engin33r/lua-shmem (mémoire partagée POSIX entre processus, pas de fichiers projetés) ; kaio326/luamemo (mémoire d'agents) ; starius/annoy (plus proches voisins) ; nubix-devbot/ht16k33 (pilote de matrice de DEL) ; fperrad/lua-loja (persistance clé-valeur) ; mtdowling/tecs (LuaJIT seulement) ; nnengine/sheets (tableurs CSV) |

Cellules du plafond attribuées (3.4) :

* pessoa736/vmsl : **K5, K9** (C1 = C2 = 0 : produit scalaire (Vector * Vector), sommes et échelles de matrices (submatrix, +, *) en C ; ni produit terme à terme (K1) ni comparaison (K4, Q6, Q1) ; aucun fil pour les formes à quatre fils)
  * K5 : op_vmsl : produit scalaire Vector * Vector
  * K9 : op_vmsl : grille en Matrix ; submatrix des quatre voisins, sommes (+) puis échelle (* 0.25), intérieur recopié dans la grille
* moteus/lua-llthreads2 : **Q6 mt, Q1 mt, K9 mt** (D1 = 0 : fils dans des états Lua séparés, données passées par copie ; sans mémoire partagée, pas K3)
  * Q6 mt : op_llthreads2 : quatre fils llthreads2, chacun reçoit sa tranche de colonnes en chaînes (string.pack) et rend sa somme
  * Q1 mt : op_llthreads2 : quatre fils, tranches en chaînes, agrégats partiels rendus et fusionnés
  * K9 mt : op_llthreads2 : à chaque pas, quatre fils reçoivent leur bande (et ses voisines) en chaînes et rendent la bande calculée

## Récapitulatif

| Langage | Case | Bibliothèque | Version | Entrée | Cellules du plafond |
|---|---|---|---|---|---|
| C | F2 | hwloc | 2.10.0 (paquet Ubuntu libhwloc-dev 2.10.0-1build1) | règle | — |
| C++ | F2 | hwloc | 2.10.0 (paquet Ubuntu libhwloc-dev 2.10.0-1build1) | règle | — |
| Rust | B2 | bumpalo | 3.20.4 | règle | K8 |
| Rust | C1 | fearless_simd | 1.2.0 | règle | — |
| Rust | C5 | rayon | 1.12.0 | règle | — |
| Rust | D3 | cordyceps | 0.3.5 | règle | K3 |
| Rust | D4 | core_affinity | 0.8.3 | règle | — |
| Rust | F1 | ndarray | 0.17.2 | règle | — |
| Rust | F2 | hwlocality-sys | 0.7.2 (sur libhwloc 2.10.0) | règle | — |
| Rust | F4 | memmap2 | 0.9.12 | règle | — |
| Rust | D3 | libc | 0.2.191 | nommée | K3 |
| Rust | D4 | libc | 0.2.191 | nommée | K3 |
| Rust | F4 | libc | 0.2.191 | nommée | K3 |
| Rust | D3 | crossbeam | 0.8.5 | nommée | K3 |
| Rust | C5 | rayon | 1.12.0 | nommée | — |
| Nim | C1 | mmops | 0.1.1 (étiquette 0.1.1, commit a3cf2a4 ; le fichier .nimble y porte 0.1.0 ; avec nimsimd 1.3.2) | règle | — |
| Nim | F1 | arraymancer | 0.7.33 | règle | — |
| D | A6 | soa | 0.2.0 (étiquette v0.2.0) | règle | K1 |
| D | F1 | mir-algorithm | 3.22.5 (avec mir-core 1.7.4) | règle | — |
| Ada | C5 | lwt | 1.2.0 (commit fedb90b de parasail, index d'Alire) | règle | — |
| Ada | D3 | cachelines | 0.1.0 (commit 5c97574, index d'Alire) | règle | K3 |
| Swift | B2 | github.com/swift-molecules/swift-memory-allocation | branche main, révision 8742a8c (aucune version publiée) | règle | K8 |
| Swift | F1 | github.com/jjjkkkjjj/Matft | 1.0.1 (étiquette 1.0.1, commit bf66a10) | règle | — |
| Julia | B2 | Bumper | 0.7.2 | règle | K8 |
| Julia | C1 | VectorizationBase | 0.21.74 | règle | — |
| Julia | D4 | ThreadPinningCore | 0.4.5 | règle | — |
| Julia | F2 | NUMA | 0.1.1 | règle | — |
| Mojo | C5 | MAX 26.7.0 | 26.7.0 (paquet conda max-core 26.7.0) | nommée | Q6 mt, Q1 mt, K9 mt, K3 |
| Mojo | D1 | MAX 26.7.0 | 26.7.0 (paquet conda max-core 26.7.0) | nommée | Q6 mt, Q1 mt, K9 mt, K3 |
| Mojo | F1 | MAX 26.7.0 | 26.7.0 (paquet conda max-core 26.7.0) | nommée | Q6 mt, Q1 mt, K9 mt, K3 |
| Java | D4 | net.openhft:affinity | 2026.2 | règle | — |
| Java | F1 | org.tensorflow:ndarray | 1.0.0 | règle | — |
| Java | F2 | org.apache.ignite:ignite-numa-allocator | 2.18.0 | règle | — |
| Go | C5 | github.com/samber/lo/parallel | v1.53.0 (module github.com/samber/lo) | règle | — |
| Go | D3 | github.com/templexxx/cpu | v0.1.1 | règle | K3 |
| Go | F1 | gonum.org/v1/gonum/mat | v0.17.0 (module gonum.org/v1/gonum) | règle | K9, K9 mt |
| Go | F2 | github.com/benjojo/numa | v0.0.0-20260918214945-1058a779f434 (aucune version publiée) | règle | — |
| Haskell | C5 | parallel | 3.3.0.0 | règle | — |
| Haskell | D2 | atomic-primops | 0.8.8 | règle | — |
| Haskell | F4 | mmap | 0.5.9 | règle | — |
| OCaml | C2 | ocaml_intrinsics_kernel | v0.17.3 | règle | K4, Q6, Q6 mt |
| OCaml | C5 | domainslib | 0.5.2 (avec saturn 1.0.0, domain-local-await 1.0.1, multicore-magic 2.3.2, backoff 0.1.1, thread-table 1.0.0) | règle | — |
| OCaml | D4 | processor | 0.2 | règle | — |
| JavaScript | B2 | @protobufjs/pool | 1.1.0 | règle | K8 |
| JavaScript | F1 | ndarray | 1.1.1 | règle | — |
| PHP | C5 | amphp/parallel-functions | 2.0.0 (avec amphp/parallel 2.4.0) | règle | Q6 mt, Q1 mt, K9 mt |
| PHP | F1 | rindow/rindow-math-matrix | 2.2.0 | règle | — |
| Python | C5 | dask | 2026.8.0 | règle | Q6 mt, Q1 mt, K9 mt, K3 |
| Python | D2 | atomics | 1.0.3 | règle | — |
| Python | F1 | numpy | 2.5.5 | nommée | K1, K4, K5, Q6, Q1, K9, Q6 mt, Q1 mt, K9 mt |
| Lua | D1 | moteus/lua-llthreads2 | 0.1.6-1 (étiquette v0.1.6) | règle | Q6 mt, Q1 mt, K9 mt |
| Lua | F1 | pessoa736/vmsl | 1.1-2 (étiquette v1.1) | règle | K5, K9 |

52 entrées (case comblée) ; 40 couples (bibliothèque, cellule du plafond) dans 18 bibliothèques de 12 langages.
