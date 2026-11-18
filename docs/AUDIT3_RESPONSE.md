# Réponse à la troisième remarque générale (18 novembre 2026)

*Remarque archivée dans `docs/AUDIT3_2026-11-18.md`. Les sections 0 à 3 sont écrites et poussées **avant** les calculs
de la section 2 ; la section 4 rend compte des résultats. Rien n'est remesuré.*

La remarque ne conteste aucune mesure : elle dit que le tableau final mélange le langage avec la taille des données,
la chaîne de compilation (compilateur, version, vérifications) et le règlement (bibliothèque standard seule, grille
jugée). C'est exact, et le README ne le montre qu'en partie (ses « Limites »). Je vérifie ses neuf points, j'applique
ceux qui ne demandent aucune mesure nouvelle, et je chiffre ce que coûteraient les autres.

## 0. Vérification

| Point | Affirmation | Constat |
|---|---|---|
| 1 | Le plan v3 prévoit des étages sans ordre interne et relègue le score composite en sensibilité, alors que le README affiche des rangs de 1 à 25 | **Exact.** `docs/ANALYSIS_V3.md` (section 1, poussé le 29 octobre avant ses calculs) publie des étages, trois quantités séparées (plafond, code naturel, contrôle) et des énoncés de mécanisme, et fait du score composite une sensibilité ; le README de la v3 suivait ce plan (commit `5959cef`). Le classement de 1 à 25 est revenu le 30 octobre (commit `2e5b6b9`), **à la demande de l'auteur de l'étude** (« Moi je veux un vrai classement ») ; c'est un écart au plan v3 que le README ne dit pas |
| 1 | Les trois étages sont solides, l'ordre à l'intérieur ne l'est pas | **Exact.** Étages [14, 5, 6] (frontières tenues sur les deux machines et dans au moins 95 % des tirages) ; dans le premier étage, un langage devance le suivant dans 45 à 71 % des variantes seulement |
| 2 | La grille explique 74 % des écarts entre les 14 premiers | **Exact** (R² = 0,74, `results/readme_figures.json`) |
| 2 | Un tiers seulement des cases s'appuie sur une sonde ou une mesure | **À peu près** : 330 cases sur 850 (39 %) ont une ligne de sonde exécutée (`results/probes/*.txt`) ou sont mesurées (C3). Six langages sont sondés presque entièrement (C, C++, Swift, FreePascal, BQN, PHP : 34 ou 33 cases sur 34) ; les 19 autres le sont sur 2 à 10 cases. Le reste repose sur la lecture des sources et de la documentation, citée dans chaque justification |
| 2 | 6 % des cases ont déjà été corrigées | **Exact** : 53 errata de cases sur 850 (6,2 %), du juge à l'aveugle à la remarque sur BQN |
| 2 | Une seule règle pour la libc et les FFI | **La règle est unique, mais mal écrite là où on la lit.** La règle v2 (`analysis/capabilities_v2.py`) compte ce que la chaîne livre, « y compris les builtins importés par le mécanisme d'import d'intrinsèques du langage, et la bibliothèque système de la plateforme pour C et C++ », et met à 0 ce qui n'est accessible que « par une bibliothèque tierce ou une FFI vers du code non intrinsèque ». D'où : une FFI vers des intrinsèques compte (Nim, Chapel, C3, Odin), une FFI vers la libc ne compte pas (Rust, JavaScript, PHP, BQN), et les types C qu'une FFI livrée définit valent ½ (`ctypes`, FFM, FFI de PHP, `Foreign` de Haskell). La légende de `docs/CAPABILITIES.md` (« ○ = 0 : absente, ou seulement par une bibliothèque tierce ou une FFI ») ne le dit pas : elle est à corriger. Je n'ai pas relu les 850 cases contre cette règle (section 3) |
| 3 | Une bonne part des données des variantes existe déjà | **Exact** pour 13 variantes : cinq implémentations en annexe, mesurées dans la campagne principale (C par GCC, Fortran par flang, LuaJIT, Bun, CPython sans GIL), et huit scénarios des remarques (Zig 0.18-dev, le K4 de clang++ pour C++, .NET 11, la CLI de PHP sans JIT, le stencil de PHP compilé par 8.3, Swift `-Ounchecked`, FreePascal 3.2.4-rc2 et branche main) |
| 4 | Deux pistes (bibliothèque standard seule, ouverte) | **Demande de nouvelles implémentations** (NumPy, MAX, crates, paquets de Hackage) et une grille notée deux fois : section 3 |
| 5 | En code naturel, Zig, D, C3 et Chapel tournent sans vérifications ; Rust, Swift, Ada, Nim et Odin les gardent | **Exact** : `-O fast` (Zig), `-release` (D), `-O3` (C3, mode sans vérifications), `--fast` (Chapel), et FreePascal, dont les vérifications sont désactivées par défaut ; Rust, `-O` (Swift), Ada par défaut, `-d:release` (Nim), `-o:speed` (Odin), Julia et Mojo (assertions actives) gardent les leurs, comme les langages gérés. C'est la règle du mode de publication documenté de chaque chaîne (`docs/NATURAL.md`), pas un oubli ; mais des conditions égales sont impossibles par simple option : Rust ne retire pas ses vérifications de bornes sans changer le code, et C, C++ et Fortran n'en ont pas |
| 5 | Le stencil est contigu pour les uns, imbriqué pour les autres | **Exact, par construction** : le code naturel prend la structure 2D idiomatique de chaque langage (`docs/NATURAL.md`) : contiguë en C, C#, Zig, Odin, Julia, Ada, Fortran, C3, Chapel, FreePascal, Haskell et BQN ; imbriquée en C++, Java, JavaScript, Python, D, Rust, Nim, Mojo, Go, OCaml, Lua, Swift et PHP. Le code optimisé est en grille plate partout |
| 5 | K4 est le seul noyau où le SIMD explicite est interdit, ce qui compte deux fois l'absence de vectoriseur | **Exact** : la spécification n'admet pour K4 que deux formes scalaires ; son plafond (E) et son code naturel (D1) dépendent tous deux de la vectorisation automatique. Sensibilité existante : sans K4 dans le plafond, C++ passe 1er (`docs/MOJO.md`) |
| 6 | Julia gagnerait 3 à 5 points, C# 7 à 8 | **Exact** : ce sont les sensibilités publiées des remarques sur Julia et sur C# |
| 7 | Python passe de 30 fois à 1,2 fois le temps du C selon la taille de K2 | **Exact** : 30,0 fois à 16 Kio, 1,1 à 1,3 fois de 8 à 256 Mio |
| 7 | Trois tailles par noyau ne demandent aucun code nouveau | **Inexact** : hors K2, les tailles sont des constantes dans chaque implémentation (`N1 = 1 << 22` en C, Rust, Python, Go…), et les fichiers d'entrée (`/opt/msdata`) sont générés pour une seule taille ; il faudrait toucher les 25 implémentations, les générateurs et les sommes de contrôle attendues |
| 9 | Le coût d'accès au plafond est mesurable | **Plausible** ; rien n'est mesuré aujourd'hui (section 3) |

## 1. Ce que je fais sans remesurer

* **Point 1, la forme du résultat.** Le classement de 1 à 25 reste, puisque l'auteur l'a demandé ; mais le README dit
  désormais que c'est un écart au plan v3, et il montre ce que ce plan publiait :
  * une colonne « Étage » dans le tableau, avec les étages de la règle v3 ;
  * les trois quantités séparées, par langage : plafond, code naturel, contrôle (règles v2 et v1), chacune avec son
    rang ;
  * un classement sur les seules mesures (plafond et code par défaut, sans la grille), avec son incertitude.

  Repasser à des étages sans ordre interne est une décision de l'auteur : je la lui soumets (section 5).
* **Point 2, la grille.**
  * Le contrôle est publié à part, dans le tableau des trois quantités.
  * L'état de preuve de chaque case est publié : sonde exécutée, mesure ou lecture des sources (`docs/CAPABILITIES.md`,
    décompte par langage).
  * La règle unique est réécrite là où on la lit : la légende de `docs/CAPABILITIES.md` et les limites du README. Elle
    ne change aucune case.
* **Point 3, les variantes.** Un tableau des variantes, hors classement : chacune avec son score et le rang qu'elle
  aurait à la place de la chaîne classée, dans l'état de l'étude où le scénario a été calculé.

## 2. Calculs (`analysis/audit3.py`, analyse globale de la v3 rejouée, mêmes tirages)

* **Contrôle** : le scénario « Publié » reproduit le classement publié (P-E de `results/php_check.json`) à l'identique.
* **M-mesures** : le poids du contrôle vaut 0 dans le score central et dans chacune des 20 000 variantes ; le plafond
  et le code par défaut gardent leurs poids relatifs (0,40 et 0,25 au centre, renormalisés ; dans chaque variante, les
  poids tirés renormalisés). Les tirages ne changent pas. Sortie : score, rang espéré, rang à 90 % et étages selon la
  règle v3 (frontières à 95 % ; la condition de réplication sur la machine 3 n'est pas recalculée pour ce scénario, et
  ces étages restent donc indicatifs).
* **Substitutions** : pour chaque implémentation en annexe (C par GCC, Fortran par flang, LuaJIT, Bun, CPython sans
  GIL), les clés qu'elle a mesurées remplacent celles de la chaîne classée, les autres restent ; même grille (celle du
  langage). Sortie : score et rang espéré à la place de la chaîne classée.
* **Variantes des remarques** : relues dans leurs sorties (`results/zig_check.json`, `c_check_current.json`,
  `csharp_check_current.json`, `php_check.json`, `php_remark.json` : état actuel ; `swift_check.json` : état du 5
  novembre ; `fpc_remark.json` : état du 6 novembre), sans recalcul.
* **État de preuve de la grille** : décompte des cases sondées, mesurées ou lues, par langage et par catégorie.
* Sorties : `results/audit3.json`, `results/report_audit3.md`. Le classement publié ne change pas.

## 3. Ce qui demande de nouvelles règles ou de nouvelles mesures (v4, non lancée)

Ces points changent ce que l'étude mesure ; je les chiffre, je ne les lance pas sans l'accord de l'auteur.

| Point | Ce qu'il faudrait | Ordre de grandeur |
|---|---|---|
| 2 | Une sonde par case : 520 cases non sondées dans 19 langages, en commençant par celles qui séparent les 14 premiers | 19 sondes de 25 à 30 cases, comme celles de Swift, FreePascal, BQN et PHP ; une à deux heures par langage |
| 4 | Une piste ouverte : bibliothèques tierces admises (NumPy, Numba ou Polars pour Python ; `libc`, `crossbeam`, `rayon` pour Rust ; MAX pour Mojo ; `vector` pour Haskell…), grille notée deux fois | Une liste de bibliothèques à fixer d'avance par langage ; des variantes nouvelles pour la plupart des noyaux dans une quinzaine de langages ; une campagne complète |
| 5 | Conditions égales : deux modes par langage là où la chaîne les offre (avec et sans vérifications) ; un stencil naturel contigu et un imbriqué pour tous ; le SIMD explicite admis dans le K4 optimisé | Les modes : des recompilations (pas pour Rust ni les langages gérés) ; le stencil : une variante dans 25 langages ; K4 : une variante dans les langages à SIMD explicite ; une campagne des noyaux touchés |
| 6 | Code optimisé convergent : un catalogue des meilleures formes (arène itérative, Q1 en une passe, table plate, blocs…), portées dans tous les langages qui peuvent les écrire | Le travail le plus long : chaque forme dans chaque langage, puis une campagne complète |
| 7 | Trois tailles par noyau (dans le cache, au bord, en mémoire) | Tailles en paramètres dans les 25 implémentations, générateurs et sommes attendues ; une campagne environ trois fois plus longue que la principale |
| 9 | Le coût d'accès au plafond : lignes du code optimisé rapportées au naturel, blocs `unsafe`, intrinsèques propres à une architecture, cibles où le code compile | Une mesure statique des sources existantes, à définir d'avance ; elle peut se faire sans campagne |

## 5. Questions à l'auteur

* Garder le classement de 1 à 25 en tête du README, ou revenir aux étages sans ordre interne du plan v3 (le classement
  devenant une sensibilité) ?
* Lancer la v4, et lesquels de ses points (section 3) ?
