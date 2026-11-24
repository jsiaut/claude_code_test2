# Historique de l'étude et archive

*24 novembre 2026. Le dépôt ne garde plus que ce qui sert au classement de la v4 ; ce document dit d'où vient la
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

Le classement de la v3 a été publié du 30 octobre au 23 novembre, avec ses notes et ses errata
(`docs/RANKING_V3.md`, `results/report_v3.md`).

## Ce que ces étapes ont établi

Les chiffres ci-dessous viennent de campagnes séparées, chacune sur son hôte ; ils ne sont pas remesurés dans la
campagne finale. Leur détail est dans le document cité.

* **Classement de la v3** (une taille par noyau, hôtes reliés par un témoin C, répliqué sur deux
  micro-architectures) : C, Odin, C++, C3, Zig, Rust, Nim, D, Ada, Chapel, Fortran, Swift, Julia, Mojo, C#,
  FreePascal, Java, Go, Haskell, OCaml, BQN, PHP, JavaScript, Python, Lua ; trois étages de 14, 5 et 6 langages.
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
  mesurés pendant la v3 (`docs/RANKING_V3.md`), pas dans la campagne finale.
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
| `bench/<langage>_<suffixe>` autre que `_cv` | copies des relectures et des points 2, 3 et 6 | l'archive ; les formes retenues sont dans `bench/<langage>_cv` |
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
