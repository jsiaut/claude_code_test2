# Historique de l'étude et archive

*État au 28 novembre 2026. Le dépôt ne garde que ce qui sert au classement publié (v6.1) ; ce document dit d'où vient la
méthode, ce que les étapes précédentes ont établi, et où retrouver tout ce qui a été retiré de la branche.*

## L'archive

L'état complet du dépôt avant le nettoyage est le commit `5fbe6a6864db5fd1ce28fcf37fc45fc09379a350`, ancêtre de cette
branche et tête de la branche `claude/great-goodall-49iwdz` : 3 711 fichiers, dont les données brutes de toutes les
campagnes, les 246 répertoires du banc, tous les plans, audits, journaux et rapports. Rien n'en a été effacé.

```bash
git show 5fbe6a6:docs/METHODOLOGY.md
```

```bash
git checkout 5fbe6a6 -- docs/V4_EQUAL.md
```

La première commande lit un fichier de l'archive, la seconde le remet dans l'arbre de travail.

Deux jeux de mesures plus récents ont quitté la branche le 26 novembre, quand la campagne de la v5 a pris la place
de la précédente : les mesures de la campagne des 22 et 23 novembre (machine 35) et la campagne inachevée des 24 et
25 novembre. Ils sont dans le commit `76d07af` ; les commandes pour les relire ou les recalculer sont dans
[`V5.md`](V5.md), 9.8.

Cinq langages ont quitté la branche le 27 novembre (v6 : Python, JavaScript, PHP, BQN et Lua), avec leurs
implémentations, leurs sondes, leurs mesures et leurs cases de la grille. L'état à 25 langages, celui de la v5.4, est
le commit `de697499dcd4e6286cbc8a4ef04ed84cb40e4641` ; son calcul redonne les classements à 25 langages cités plus
bas, et un fichier retiré s'y relit par `git show de69749:<chemin>` ([`V6.md`](V6.md)).

OCaml a quitté la branche le 28 novembre (v6.1), remplacé par OxCaml : son implémentation (`bench/ocaml`, dont
`bench/oxcaml/ms.ml` garde la source à l'octet près), ses sondes et sa ligne de la grille. Ses mesures de la campagne
restent dans `results/final` : elles servent de base au transport d'OxCaml. L'état avec OCaml, celui de la v6, est le
commit `be0936fad9225a4cf97bd5622fe8c145aef83060` ; son calcul redonne le classement de la v6 cité plus bas, et un
fichier retiré s'y relit par `git show be0936f:<chemin>` ([`V6_1.md`](V6_1.md)).

## Les étapes

| Date (2026) | Étape | Ce qu'elle a fixé dans la méthode actuelle | Documents, dans l'archive |
|---|---|---|---|
| 28 octobre | v1 : spécification et plan écrits avant les mesures, campagne de 21 langages sur un Cascade Lake | noyaux, trois piliers, poids 35 / 40 / 25, grille (règle v1) | `docs/METHODOLOGY.md` (plan, puis journal daté de tous les écarts jusqu'au 23 novembre) |
| 29 octobre | Premier audit, v2 | règle v2 de la grille, K10 hors score, 20 000 variantes de l'analyse | `docs/AUDIT_2026-10-29.md`, `docs/AUDIT_RESPONSE.md`, `docs/ANALYSIS_V2.md` |
| 29 octobre | Second audit, v3 | estimateur, références fixes, rééchantillonnage à résidus regroupés, étages | `docs/AUDIT2_2026-10-29.md`, `docs/AUDIT2_RESPONSE.md`, `docs/ANALYSIS_V3.md`, `docs/INSTRUMENTS_V3.md` |
| 30 octobre | Confrontation avec une étude voisine, second juge à l'aveugle | errata de la grille | `docs/CONFRONTATION.md` |
| 30 octobre au 7 novembre | Relecture de chaque langage ; harnais commun de K9 ; ajout de Swift, FreePascal, BQN et PHP | corrections des implémentations et de la grille, reprises dans `bench/` | `docs/<LANGAGE>.md` (25 documents), `docs/K9.md`, `docs/NOSIMD.md`, `docs/FINDINGS.md` |
| 18 et 19 novembre | Troisième remarque générale, plan de la v4 | les six points ci-dessous | `docs/AUDIT3_2026-11-18.md`, `docs/AUDIT3_RESPONSE.md`, `docs/V4_PLAN.md` |
| 19 novembre | Point 1 : une sonde par case de la grille | classes de preuve, sondes de `probes/` | `docs/GRID_AUDIT.md` |
| 19 et 20 novembre | Point 2 : trois tailles par noyau | tailles, règle des cellules manquantes | `docs/V4_SIZES.md` |
| 21 novembre | Point 3 : des conditions égales | R1 à R5 | `docs/V4_EQUAL.md` |
| 21 et 22 novembre | Point 4 : un code optimisé convergent | C1 à C6, catalogue des formes | `docs/V4_CONVERGE.md` |
| 22 novembre | Point 5 : le coût d'accès au plafond | rien : publié à côté du classement | `docs/V4_COST.md` |
| 22 novembre | Point 6 : une piste ouverte aux bibliothèques tierces | rien : publiée à côté du classement | `docs/V4_OPEN.md` |
| 22 et 23 novembre | Campagne finale : le classement de la v4 | — | [`V4_FINAL.md`](V4_FINAL.md), gardé dans le dépôt |
| 24 novembre | Nettoyage du dépôt, sans changement de chiffre | [`METHOD.md`](METHOD.md), `tools/check.sh` | ce document |
| 24 novembre | v4.1 : quatre corrections de l'analyse, sans mesure nouvelle | A1 à A4 ; ordre publié : le score moyen des variantes, qui est aussi le score affiché | [`V4_1.md`](V4_1.md), gardé dans le dépôt |
| 24 au 26 novembre | v5 : script d'installation des chaînes, une source par langage, C aussi par gcc ; campagne rejouée sur un autre processeur (machine 38), dont viennent les mesures du classement publié | A5 et A6 ; une campagne par modèle de processeur | [`V5.md`](V5.md), gardé dans le dépôt |
| 26 novembre | v5.1 : le mode du code naturel tiré au sort, entre deux modes puis entre trois, sans mesure nouvelle | A7 et A8 | [`V5_1.md`](V5_1.md), gardé dans le dépôt |
| 26 novembre | v5.2 : Zig classé, par exception, avec sa version de développement, remesurée à côté d'un témoin | l'exception et son astérisque ; le transport par témoin | [`V5_2.md`](V5_2.md), gardé dans le dépôt |
| 27 novembre | v5.3 : deux lectures ajoutées au rapport après une veille sur les bancs comparables, sans mesure nouvelle ; le classement reste celui de la v5.2 | la part de la variance du score que porte chaque composante ; le tri des écarts du code naturel, son registre des causes et son garde-fou | [`V5_3.md`](V5_3.md), gardé dans le dépôt |
| 27 novembre | v5.4 : l'erreur de mesure que le tri a retrouvée sur K1 de Go est corrigée ; Go est remesuré à part hors de l'expérience `simd` de sa chaîne, à côté de son binaire de la campagne et de C | la construction de Go en deux binaires ; le pont par une cellule de C ; les calculs « Go de la campagne » et « Campagne telle que mesurée » | [`V5_4.md`](V5_4.md), gardé dans le dépôt |
| 27 novembre | v6 : Python, JavaScript, PHP, BQN et Lua retirés du banc, sans mesure nouvelle ; le classement porte sur 20 langages | le périmètre ; les références prises parmi 20 langages ; deux classes de bruit au lieu de trois | [`V6.md`](V6.md), gardé dans le dépôt |
| 28 novembre | v6.1 : OxCaml à la place d'OCaml ; il est mesuré à part, à côté d'OCaml 5.5.2 pris pour témoin et de C pris pour pont : le classement publié | le transport d'un langage entier, par témoin pour la source commune et par pont pour ses formes propres ; la règle de la grille pour les extensions d'OxCaml ; la réplication sur les langages communs aux deux campagnes | [`V6_1.md`](V6_1.md), gardé dans le dépôt |

Le classement de la v3 a été publié du 30 octobre au 23 novembre, avec ses notes et ses errata
(`docs/RANKING_V3.md`, `results/report_v3.md`).

## Ce que ces étapes ont établi

Hors les classements des 23, 24, 26 et 27 novembre, les chiffres ci-dessous viennent de campagnes séparées, chacune sur
son hôte ; ils ne sont pas remesurés dans la campagne publiée. Leur détail est dans le document cité. Les classements
ci-dessous comptent 25 langages, sauf le dernier ; depuis la v6, le calcul du dépôt n'en classe plus que 20, et ceux
qu'il redonnait à l'identique se recalculent depuis le commit `de69749`.

* **Classement de la v3** (une taille par noyau, hôtes reliés par un témoin C, répliqué sur deux
  micro-architectures) : C, Odin, C++, C3, Zig, Rust, Nim, D, Ada, Chapel, Fortran, Swift, Julia, Mojo, C#,
  FreePascal, Java, Go, Haskell, OCaml, BQN, PHP, JavaScript, Python, Lua ; trois étages de 14, 5 et 6 langages.
* **Classement du 23 novembre** (v4, avant les quatre corrections de l'analyse) : C++, C, Odin, Rust, C3, Nim, D, Zig,
  Ada, Chapel, Fortran, Julia, Swift, Mojo, C#, Go, FreePascal, Java, Haskell, OCaml, BQN, JavaScript, PHP, Python,
  Lua ; deux étages de 19 et 6 langages ; C++ devant C dans 51 % des variantes. Son procès-verbal est
  [`V4_FINAL.md`](V4_FINAL.md), 12. Sur les mesures de la campagne publiée, la même méthode (« Méthode du 23
  novembre » de `results/report_final.md`) place C devant C++.
* **Classement du 24 novembre** (v4.1 : la même campagne, celle de la machine 35, après les corrections A1 à A4 ;
  publié jusqu'au 26 novembre) : C, C++, Odin, Rust, D, Nim, C3, Zig, Ada, Julia, Fortran, Chapel, Swift, Mojo, C#,
  Java, Go, FreePascal, Haskell, OCaml, BQN, JavaScript, PHP, Python, Lua ; deux étages de 19 et 6 langages ; C
  premier dans 69 % des variantes. La campagne publiée le redonne à deux échanges de voisins près
  ([`V5.md`](V5.md), 9.6).
* **Classement du 26 novembre au matin** (v5 : la campagne publiée, avant que le mode du code naturel soit tiré au
  sort) : C, C++, Odin, Rust, Nim, D, C3, Zig, Ada, Julia, Fortran, Chapel, Mojo, Swift, C#, Java, Go, FreePascal,
  Haskell, OCaml, BQN, JavaScript, PHP, Python, Lua ; trois étages de 15, 4 et 6 langages ; C premier dans 69 % des
  variantes. Sans l'exception de Zig ni la correction de Go (`FINAL_ZIG17=1 FINAL_GOSIMD=1`), le calcul de la v5.4 le
  redonne à l'identique (« Sans A7 ») ; son procès-verbal est [`V5.md`](V5.md), 9.
* **Classement du 26 novembre, 15 h** (v5.1, première forme : le mode du code naturel tiré entre R1 et le mode publié
  de chaque chaîne) : C, C++, Odin, Rust, Zig, Nim, C3, D, Ada, Julia, Fortran, Chapel, Mojo, Swift, C#, Java, Go,
  FreePascal, Haskell, OCaml, BQN, JavaScript, PHP, Python, Lua ; deux étages de 19 et 6 langages ; C premier dans
  63 % des variantes. Publié quelques heures : le tirage entre trois modes, qui l'a remplacé, garde les 25 places.
  Sans l'exception de Zig ni la correction de Go (`FINAL_ZIG17=1 FINAL_GOSIMD=1`), le calcul de la v5.4 le redonne à
  l'identique (« Sans A8 ») ; son procès-verbal est [`V5_1.md`](V5_1.md), 8.
* **Classement du 26 novembre, 17 h** (v5.1 : le mode du code naturel tiré entre trois politiques, Zig mesuré par sa
  version stable comme les 24 autres) : C, C++, Odin, Rust, Zig, Nim, C3, D, Ada, Julia, Fortran, Chapel, Mojo, Swift,
  C#, Java, Go, FreePascal, Haskell, OCaml, BQN, JavaScript, PHP, Python, Lua ; deux étages de 19 et 6 langages ; C
  premier dans 59 % des variantes. Le calcul de la v5.4 le redonne à l'identique (« Campagne telle que mesurée ») ;
  son procès-verbal est [`V5_1.md`](V5_1.md), 10.
* **Classement du 26 novembre au soir et du 27 novembre** (v5.2 et v5.3 : Zig par sa version de développement, Go
  encore mesuré dans le binaire de la campagne, dont K1 était faussé) : C, C++, Zig, Odin, Rust, Nim, C3, D, Ada,
  Julia, Fortran, Chapel, Mojo, Swift, C#, Java, Go, FreePascal, Haskell, OCaml, BQN, JavaScript, PHP, Python, Lua ;
  deux étages de 19 et 6 langages ; C premier dans 56 % des variantes. Le calcul de la v5.4 le redonne à l'identique
  (« Go de la campagne ») ; ses procès-verbaux sont [`V5_2.md`](V5_2.md), 9, et [`V5_3.md`](V5_3.md), 9.
* **Classement du 27 novembre, 17 h** (v5.4 : K1 de Go corrigé ; le dernier à 25 langages) : C, C++, Zig, Odin,
  Rust, Nim, C3, D, Ada, Julia, Fortran, Chapel, Mojo, Swift, C#, Go, Java, FreePascal, Haskell, OCaml, BQN,
  JavaScript, PHP, Python, Lua ; deux étages de 19 et 6 langages ; C premier dans 57 % des variantes. C'est l'état
  du commit `de69749` ; son procès-verbal est [`V5_4.md`](V5_4.md), 9. Le classement de la v6 en garde les 20
  premiers, dans le même ordre, avec des scores plus hauts de 0,3 point au plus ([`V6.md`](V6.md), 9).
* **Classement du 27 novembre au soir** (v6 : 20 langages, OCaml encore classé ; publié jusqu'au 28 novembre) : C,
  C++, Zig, Odin, Rust, Nim, C3, D, Ada, Julia, Fortran, Chapel, Mojo, Swift, C#, Go, Java, FreePascal, Haskell,
  OCaml ; deux étages, les 19 premiers puis OCaml seul (27,9) ; C premier dans 57 % des variantes. C'est l'état du
  commit `be0936f` ; son procès-verbal est [`V6.md`](V6.md), 9. Le classement publié en garde les 19 premiers, dans le
  même ordre, avec des scores plus bas de 0,1 point au plus, et place OxCaml 19e, devant Haskell ([`V6_1.md`](V6_1.md),
  11).
* **Point 2, tailles** (`docs/V4_SIZES.md`). Entre la taille publiée seule et la moyenne des trois tailles, aucun
  langage ne bouge de plus de deux places ; l'effet de l'hôte est plus grand que celui des tailles.
* **Point 3, conditions égales** (`docs/V4_EQUAL.md`). Les vérifications et le stencil contigu ne déplacent aucun
  langage de plus de deux places ; le SIMD explicite dans K4 fait monter Zig de quatre places ; K3 rapporté à une
  boucle de référence fait reculer Nim et D de trois.
* **Point 4, convergence** (`docs/V4_CONVERGE.md`). 20 formes au catalogue, portées dans les 25 langages (230 formes
  écrites, 87 déjà présentes, 61 non écrivibles) ; aucun langage ne bouge de plus de deux places ; le gain vient des
  formes portées d'un langage à l'autre, surtout dans K4 et K8.
* **Point 5, coût d'accès au plafond** (`docs/V4_COST.md`, `results/report_cost.md`). La forme la plus rapide a
  3,5 fois les lignes du code naturel (médiane des 25 langages) ; un indice d'accès combine lignes ajoutées, code sans
  vérification et constructions propres à x86 : Mojo (0,50) et Odin (0,40) atteignent le plafond au meilleur prix. Mis
  à la place des catégories C et E de la grille, il ne déplace que Mojo de plus de deux places. Décision de l'auteur de
  l'étude (22 novembre) : la grille est gardée, l'indice est publié à côté.
* **Point 6, piste ouverte** (`docs/V4_OPEN.md`, `results/report_open.md`). 47 bibliothèques tierces dans 17 langages
  comblent 47 cases de la grille ; mesurées, elles ne battent la forme standard la plus rapide que dans 13 cellules
  sur 35, de beaucoup seulement en Python (NumPy) et en Lua ; par la grille seule, Rust passerait 1er (huit cases
  comblées), 4e avec les seules bibliothèques nommées d'avance. Décision de l'auteur de l'étude (22 novembre) : la
  piste ouverte reste à côté du classement.
* **Confrontation** (`docs/CONFRONTATION.md`). Une étude voisine classe C 11e sur 18 langages communs ; appliquer sa
  règle du « standard » à la grille et au code mesuré explique l'essentiel de l'écart : la règle de notation, et non
  les faits, fait le renversement.
* **Autres chaînes, versions et modes** (C par GCC, flang, Zig 0.18-dev, .NET 11, LuaJIT, Bun, CPython sans GIL…) :
  mesurés pendant la v3 (`docs/RANKING_V3.md`), pas dans la campagne publiée, sauf C par gcc
  ([`V5.md`](V5.md), 9.5).
* **Faits de mécanisme** (`docs/FINDINGS.md` et les documents par langage) : la source des constats résumés dans le
  README, « Ce qui sépare vraiment les langages ».

## Renvois du code vers des documents archivés

Les sources de `bench/` et de `probes/` ne sont pas retouchées : leurs commentaires citent les plans d'origine. Les
documents gardés tels qu'écrits ([`SPEC.md`](SPEC.md), [`NATURAL.md`](NATURAL.md), [`V4_FINAL.md`](V4_FINAL.md)) en
citent aussi, ainsi que des copies du banc et des outils retirés.

| Cité | Ce que c'était | Où lire la règle aujourd'hui |
|---|---|---|
| `docs/METHODOLOGY.md` | plan de la v1 et journal des écarts | [`METHOD.md`](METHOD.md) pour la méthode ; l'archive pour le journal |
| `docs/V4_PLAN.md` | plan de la v4 ; norme de preuve des sondes (2.1) | `METHOD.md`, 7 |
| `docs/V4_SIZES.md` | point 2 | `METHOD.md`, 3 |
| `docs/V4_EQUAL.md` | point 3 | `METHOD.md`, 5 |
| `docs/V4_CONVERGE.md` | point 4 | `METHOD.md`, 4 |
| `docs/K9.md` | harnais commun de K9 | [`SPEC.md`](SPEC.md), K9 |
| `docs/GRID_AUDIT.md`, `docs/ANALYSIS_V2.md` | audit de la grille ; règle v2 | `METHOD.md`, 7 |
| `docs/ANALYSIS_V3.md` | inférence, étages | `METHOD.md`, 9 |
| `docs/<LANGAGE>.md` | relecture d'un langage | l'archive |
| `bench/<langage>_<suffixe>` | copies des relectures et des points 2, 3, 4 et 6 | l'archive ; les formes retenues sont dans `bench/<langage>` (la copie `_cv` du point 4 est devenue la source unique le 24 novembre) |
| `analysis/analyze_v2.py`, `analysis/analyze_v3.py` | analyses des v2 et v3 | leur code utile est dans `analysis/final_v4.py` |
| `tools/<x>_check/`, `tools/measure_*.py`, `tools/equal/`, `tools/open/`… | outils des relectures et des points | l'archive |
| `results/raw*`, `results/report_*.md`, `results/sizes/`, `results/equal/`… | données et rapports des étapes | l'archive |

## Ce que le nettoyage a changé

* 2 911 fichiers retirés de la branche ; 3 711 avant, environ 800 après.
* Le classement est calculé par un seul module, `analysis/final_v4.py`, qui reprend tel quel le code qu'il importait
  de dix-huit autres ; `results/report_final.md` et `results/final/analysis.json` sont identiques à l'octet près.
* `tools/driver.py` ne fait plus que la validation rapide d'une implémentation ; `tools/final/save_progress.sh` pousse
  sur la branche courante.
* [`METHOD.md`](METHOD.md) remplace, pour la méthode en vigueur, la lecture de quatre versions de plans.
* Une phrase de l'ancien README n'était plus exacte et n'a pas été reprise : « un temps sous la borne physique de la
  machine est rejeté ». Cette règle des v1 à v3 n'est pas dans le calcul de la v4, où les bornes physiques servent de
  seconde référence ; hors K3, que R4 traite, aucune frontière de la campagne finale n'est sous 0,9 fois sa borne.
