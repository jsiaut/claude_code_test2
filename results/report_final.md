# v5.3 : le classement — résultats

*Plans : `docs/V4_FINAL.md` (section 8), `docs/V4_1.md` (corrections A1 à A4 de l'analyse), `docs/V5.md` (campagne rejouée, corrections A5 et A6), `docs/V5_1.md` (A7 et A8 : mode du code naturel tiré au sort) et `docs/V5_2.md` (Zig par sa version de développement), fixés avant les mesures ou avant leur analyse ; `docs/V5_3.md` (ce qui décide de l'ordre, tri des écarts : deux lectures, le classement est celui de la v5.2). Généré par `analysis/final_v4.py` à partir de `results/final/raw`, de `results/final/b3.jsonl` et du relevé des formes (`results/converge/forms.json`).*

Machines : 38 ; b3 de référence (le plus lent des 16 décalages, A2) : 64.24 ms ; b3 des groupes de K3 : passe 0 64.62 ms, passe 1 64.20 ms, passe 2 63.92 ms ; avec la médiane des 16 décalages (méthode du 23 novembre) : 58.12 ms.

## Classement « Final »

| Rang | Langage | Score | Score au centre | Rang espéré | Rang plausible | Devance le suivant | Plafond | Code par défaut | Contrôle |
|---|---|---|---|---|---|---|---|---|---|
| 1 | C | 83.2 | 85.8 | 1.82 | 1–4 | 68 % | 84.4 | 80.0 | 91.7 |
| 2 | C++ | 81.5 | 84.3 | 2.85 | 1–7 | 71 % | 87.5 | 68.0 | 92.4 |
| 3 | Zig* | 79.6 | 79.3 | 4.09 | 1–9 | 67 % | 83.1 | 62.0 | 87.2 |
| 4 | Odin | 78.5 | 79.5 | 5.05 | 2–9 | 53 % | 81.6 | 70.0 | 84.0 |
| 5 | Rust | 78.0 | 79.7 | 5.28 | 2–9 | 62 % | 86.4 | 77.7 | 73.6 |
| 6 | Nim | 77.3 | 79.0 | 6.07 | 3–9 | 61 % | 83.3 | 76.0 | 76.1 |
| 7 | C3 | 76.6 | 78.0 | 6.79 | 3–10 | 50 % | 84.0 | 71.6 | 75.7 |
| 8 | D | 76.4 | 79.6 | 6.84 | 3–12 | 76 % | 85.4 | 59.7 | 87.1 |
| 9 | Ada | 73.8 | 75.2 | 8.92 | 5–12 | 65 % | 81.4 | 57.5 | 80.6 |
| 10 | Julia | 72.3 | 73.5 | 10.21 | 7–13 | 58 % | 77.8 | 66.9 | 73.3 |
| 11 | Fortran | 71.7 | 72.3 | 10.64 | 6–14 | 55 % | 78.3 | 72.4 | 65.3 |
| 12 | Chapel | 70.8 | 70.2 | 10.97 | 6–14 | 71 % | 86.5 | 55.7 | 61.8 |
| 13 | Mojo | 68.2 | 69.2 | 12.69 | 10–14 | 58 % | 75.7 | 56.9 | 70.5 |
| 14 | Swift | 67.6 | 68.5 | 13.01 | 11–14 | 95 % | 79.5 | 51.4 | 68.1 |
| 15 | C# | 61.2 | 63.3 | 14.94 | 14–16 | 96 % | 69.8 | 45.3 | 68.8 |
| 16 | Java | 52.6 | 53.6 | 16.82 | 16–18 | 61 % | 65.2 | 50.5 | 42.7 |
| 17 | Go | 51.6 | 52.5 | 17.13 | 16–18 | 49 % | 62.4 | 42.2 | 48.7 |
| 18 | FreePascal | 51.5 | 50.5 | 17.12 | 15–19 | 83 % | 42.2 | 47.2 | 62.3 |
| 19 | Haskell | 45.7 | 45.5 | 18.76 | 18–19 | 100 % | 54.1 | 37.4 | 41.5 |
| 20 | OCaml | 27.9 | 26.3 | 20.14 | 20–21 | 94 % | 23.2 | 35.5 | 23.2 |
| 21 | BQN | 20.3 | 17.9 | 21.76 | 21–23 | 53 % | 9.9 | 28.1 | 19.7 |
| 22 | JavaScript | 19.7 | 17.7 | 21.99 | 21–24 | 62 % | 15.8 | 25.2 | 14.6 |
| 23 | PHP | 18.8 | 17.8 | 22.29 | 21–23 | 97 % | 6.8 | 21.9 | 27.4 |
| 24 | Python | 10.7 | 12.7 | 24.08 | 22–25 | 73 % | 1.1 | 7.7 | 29.7 |
| 25 | Lua | 7.6 | 6.4 | 24.73 | 24–25 | — | 1.5 | 13.5 | 6.8 |

Score : moyenne du score sur les variantes de l'analyse ; il fixe l'ordre. Score au centre, plafond, code par défaut et contrôle : poids et choix principaux, estimation ponctuelle. Rang espéré : rang moyen sur les variantes.

\* Zig est mesuré, par exception, par sa version de développement 0.18.0-dev.1298+4a0817482 (`docs/V5_2.md`) : ses temps sont ceux de la campagne, multipliés cellule par cellule par le rapport mesuré à côté d'un témoin ; ses latences de K8 naturel restent celles de la campagne. Avec sa version stable, celle de la campagne (« Zig 0.17 ») : 5e, score 77.7.

Mode du code naturel, tiré dans chaque variante (A7, A8) : R1 dans 33.4 % des variantes, mode publié dans 33.5 % des variantes, R1' dans 33.1 % des variantes ; au centre, R1.

Étages (paires ordonnées dans au moins 95 % des variantes) : C, C++, Zig, Odin, Rust, Nim, C3, D, Ada, Julia, Fortran, Chapel, Mojo, Swift, C#, Java, Go, FreePascal, Haskell | OCaml, BQN, JavaScript, PHP, Python, Lua

## Tous les calculs

| Langage | Final | Base, trois tailles | Sans les tailles (taille publiée seule) | Sans R1 | Sans R2 | Sans C1 | Sans R4 | R1' au lieu de R1 | Taille petite | Taille grande | Sélection indépendante | D3 et D4 sur trois processus | Sur les seules mesures | Sans A1 | Sans A2 | Sans A3 | Sans A4 | Sans A5 | Sans A6 | Sans A7 | Sans A8 | Méthode du 23 novembre | C par gcc | Zig 0.17 | Zig 0.18, K4 et K9 seuls | Zig 0.18, latences du plan | Campagne précédente |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C | 1 | 1 | 2 | 1 | 1 | 1 | 2 | 1 | 1 | 2 | 1 | 1 | 2 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| C++ | 2 | 2 | 1 | 2 | 2 | 3 | 1 | 2 | 2 | 1 | 2 | 2 | 5 ** | 3 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 |
| Zig | 3 | 3 | 3 | 3 | 3 | 2 | 6 ** | 3 | 3 | 3 | 3 | 3 | 6 ** | 2 | 3 | 3 | 3 | 3 | 3 | 6 ** | 3 | 5 | 3 | 5 | 3 | 3 | 8 |
| Odin | 4 | 7 ** | 4 | 4 | 4 | 4 | 7 ** | 4 | 4 | 4 | 4 | 4 | 7 ** | 4 | 4 | 4 | 4 | 4 | 4 | 3 | 4 | 3 | 4 | 3 | 4 | 4 | 3 |
| Rust | 5 | 5 | 6 | 5 | 5 | 6 | 3 | 6 | 5 | 6 | 5 | 5 | 1 ** | 5 | 5 | 5 | 5 | 5 | 5 | 4 | 5 | 4 | 5 | 4 | 5 | 5 | 4 |
| Nim | 6 | 9 ** | 5 | 6 | 6 | 8 | 8 | 5 | 7 | 5 | 6 | 6 | 3 ** | 7 | 6 | 6 | 6 | 6 | 6 | 5 | 6 | 7 | 6 | 6 | 6 | 6 | 6 |
| C3 | 7 | 4 ** | 7 | 7 | 7 | 5 | 4 ** | 7 | 6 | 9 | 7 | 8 | 4 ** | 6 | 7 | 7 | 7 | 7 | 7 | 8 | 7 | 6 | 7 | 7 | 7 | 7 | 7 |
| D | 8 | 6 | 8 | 8 | 8 | 7 | 5 ** | 8 | 8 | 7 | 8 | 7 | 11 ** | 8 | 8 | 8 | 8 | 8 | 8 | 7 | 8 | 8 | 8 | 8 | 8 | 8 | 5 |
| Ada | 9 | 8 | 9 | 9 | 9 | 9 | 9 | 9 | 12 ** | 8 | 9 | 9 | 12 ** | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 |
| Julia | 10 | 13 ** | 11 | 11 | 10 | 12 | 10 | 10 | 11 | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 11 | 10 | 10 | 10 | 10 | 12 | 10 | 10 | 10 | 10 | 10 |
| Fortran | 11 | 11 | 10 | 12 | 11 | 10 | 11 | 12 | 10 | 11 | 11 | 11 | 9 | 12 | 11 | 11 | 10 | 11 | 11 | 11 | 11 | 11 | 11 | 11 | 11 | 11 | 11 |
| Chapel | 12 | 10 | 12 | 10 | 12 | 11 | 13 | 11 | 9 ** | 12 | 12 | 12 | 8 ** | 11 | 12 | 12 | 12 | 12 | 12 | 12 | 12 | 10 | 12 | 12 | 12 | 12 | 12 |
| Mojo | 13 | 12 | 13 | 13 | 13 | 14 | 12 | 13 | 13 | 13 | 13 | 13 | 14 | 13 | 13 | 13 | 13 | 13 | 13 | 13 | 13 | 13 | 13 | 13 | 13 | 13 | 14 |
| Swift | 14 | 14 | 14 | 14 | 14 | 13 | 14 | 14 | 14 | 14 | 14 | 14 | 13 | 14 | 14 | 14 | 14 | 14 | 14 | 14 | 14 | 14 | 14 | 14 | 14 | 14 | 13 |
| C# | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 |
| Java | 16 | 17 | 16 | 16 | 16 | 17 | 17 | 16 | 17 | 17 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 |
| Go | 17 | 18 | 17 | 18 | 17 | 18 | 18 | 18 | 18 | 18 | 18 | 17 | 17 | 17 | 18 | 18 | 18 | 17 | 18 | 17 | 17 | 18 | 17 | 17 | 17 | 17 | 17 |
| FreePascal | 18 | 16 | 18 | 17 | 18 | 16 | 16 | 17 | 16 | 16 | 17 | 18 | 19 | 18 | 17 | 17 | 17 | 18 | 17 | 18 | 18 | 17 | 18 | 18 | 18 | 18 | 18 |
| Haskell | 19 | 19 | 19 | 19 | 19 | 19 | 19 | 19 | 19 | 19 | 19 | 19 | 18 | 19 | 19 | 19 | 19 | 19 | 19 | 19 | 19 | 19 | 19 | 19 | 19 | 19 | 19 |
| OCaml | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 |
| BQN | 21 | 21 | 21 | 21 | 21 | 21 | 21 | 21 | 21 | 23 | 21 | 21 | 22 | 21 | 21 | 21 | 21 | 21 | 21 | 21 | 21 | 21 | 21 | 21 | 21 | 21 | 21 |
| JavaScript | 22 | 22 | 22 | 22 | 22 | 22 | 22 | 22 | 23 | 21 | 22 | 22 | 21 | 22 | 22 | 22 | 22 | 22 | 22 | 22 | 22 | 22 | 22 | 22 | 22 | 22 | 22 |
| PHP | 23 | 23 | 23 | 23 | 23 | 23 | 23 | 23 | 22 | 22 | 23 | 23 | 23 | 23 | 23 | 23 | 23 | 23 | 23 | 23 | 23 | 23 | 23 | 23 | 23 | 23 | 23 |
| Python | 24 | 24 | 24 | 24 | 24 | 24 | 24 | 24 | 24 | 24 | 24 | 24 | 25 | 24 | 24 | 24 | 24 | 24 | 24 | 24 | 24 | 24 | 24 | 24 | 24 | 24 | 24 |
| Lua | 25 | 25 | 25 | 25 | 25 | 25 | 25 | 25 | 25 | 25 | 25 | 25 | 24 | 25 | 25 | 25 | 25 | 25 | 25 | 25 | 25 | 25 | 25 | 25 | 25 | 25 | 25 |

Chaque case : place dans le calcul ; ** : plus de deux places d'écart avec « Final ». Ordre des lignes : « Final ». « Sans A1 » à « Sans A8 » : « Final » sans une de ses corrections ; « Méthode du 23 novembre » : sans aucune et classée au rang moyen ; « Zig 0.17 » : « Final » avec les cellules de Zig de la campagne ; « Zig 0.18, K4 et K9 seuls » : le rapport au témoin appliqué à ces deux noyaux seulement ; « Zig 0.18, latences du plan » : les latences de K8 naturel de Zig multipliées elles aussi par leur rapport ; « Campagne précédente » : son classement publié.

## Rangs qui bougent de plus de deux places par rapport à « Final »

* Base, trois tailles : Odin 7e (Final 4e), Nim 9e (Final 6e), C3 4e (Final 7e), Julia 13e (Final 10e)
* Sans les tailles (taille publiée seule) : aucun
* Sans R1 : aucun
* Sans R2 : aucun
* Sans C1 : aucun
* Sans R4 : Zig 6e (Final 3e), Odin 7e (Final 4e), C3 4e (Final 7e), D 5e (Final 8e)
* R1' au lieu de R1 : aucun
* Taille petite : Ada 12e (Final 9e), Chapel 9e (Final 12e)
* Taille grande : aucun
* Sélection indépendante : aucun
* D3 et D4 sur trois processus : aucun
* Sur les seules mesures : C++ 5e (Final 2e), Zig 6e (Final 3e), Odin 7e (Final 4e), Rust 1er (Final 5e), Nim 3e (Final 6e), C3 4e (Final 7e), D 11e (Final 8e), Ada 12e (Final 9e), Chapel 8e (Final 12e)
* Sans A1 : aucun
* Sans A2 : aucun
* Sans A3 : aucun
* Sans A4 : aucun
* Sans A5 : aucun
* Sans A6 : aucun
* Sans A7 : Zig 6e (Final 3e)
* Sans A8 : aucun
* Méthode du 23 novembre : aucun
* C par gcc : aucun
* Zig 0.17 : aucun
* Zig 0.18, K4 et K9 seuls : aucun
* Zig 0.18, latences du plan : aucun
* Final contre la méthode du 23 novembre : aucun
* « Zig 0.17 » contre la campagne précédente, classement publié : Zig 8e → 5e, D 5e → 8e
* « Zig 0.17 » contre la campagne précédente recalculée par la méthode de celle-ci : aucun
* Campagne précédente, du classement publié à son recalcul : Zig 8e → 5e

## C par gcc

« C par gcc » : « Final » où toutes les cellules de C viennent de ses constructions par gcc ; la grille et les autres langages ne changent pas.

| C compilé par | Place | Score | Premier | Devance C++ | Plafond | Code naturel | K1 | K3 | K4 | K5 | K6 | K7 | K8 | K9 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| clang (« Final ») | 1 | 83.2 | 55.5 % | 67.6 % | 84.4 | 69.8 | 85 | 99 | 95 | 84 | 81 | 81 | 68 | 86 |
| gcc | 1 | 82.9 | 54.9 % | 73.0 % | 87.9 | 60.8 | 90 | 100 | 86 | 89 | 80 | 75 | 95 | 92 |

## Réplication : cette campagne et la précédente

Les deux campagnes sont comparées à compilateurs égaux : pour celle-ci, le calcul « Zig 0.17 ».

Cellules mesurées dans les deux campagnes : 2972. Rapport des temps (cette campagne sur la précédente, estimations ponctuelles) : médiane 0.850 ; 66 % des cellules à moins de 10 % de cette médiane.

| Langage | Place | Précédente, recalculée | Précédente, publiée | Score | Précédent, recalculé | Précédent, publié | Plafond | Plafond précédent | Rapport médian des temps |
|---|---|---|---|---|---|---|---|---|---|
| C | 1 | 1 | 1 | 83.4 | 83.4 | 81.4 | 84.6 | 89.6 | 0.885 |
| C++ | 2 | 2 | 2 | 81.7 | 81.6 | 79.2 | 87.7 | 90.1 | 0.863 |
| Odin | 3 | 3 | 3 | 78.6 | 78.3 | 76.4 | 81.7 | 83.7 | 0.867 |
| Rust | 4 | 4 | 4 | 78.1 | 77.5 | 75.9 | 86.6 | 88.3 | 0.881 |
| Zig | 5 | 5 | 8 | 77.7 | 76.8 | 73.0 | 82.5 | 84.4 | 0.850 |
| Nim | 6 | 7 | 6 | 77.4 | 76.6 | 74.6 | 83.5 | 85.9 | 0.869 |
| C3 | 7 | 8 | 7 | 76.7 | 76.4 | 74.2 | 84.2 | 86.8 | 0.862 |
| D | 8 | 6 | 5 | 76.6 | 76.7 | 74.8 | 85.6 | 87.0 | 0.848 |
| Ada | 9 | 9 | 9 | 74.0 | 73.8 | 71.0 | 81.6 | 83.7 | 0.857 |
| Julia | 10 | 10 | 10 | 72.4 | 71.3 | 69.6 | 77.9 | 78.4 | 0.852 |
| Fortran | 11 | 11 | 11 | 71.8 | 70.7 | 68.1 | 78.5 | 79.1 | 0.862 |
| Chapel | 12 | 12 | 12 | 70.9 | 70.4 | 66.0 | 86.7 | 89.9 | 0.864 |
| Mojo | 13 | 14 | 14 | 68.3 | 66.7 | 64.5 | 75.9 | 76.0 | 0.848 |
| Swift | 14 | 13 | 13 | 67.7 | 67.3 | 65.2 | 79.7 | 80.6 | 0.856 |
| C# | 15 | 15 | 15 | 61.3 | 60.8 | 59.3 | 69.9 | 71.2 | 0.841 |
| Java | 16 | 16 | 16 | 52.7 | 52.5 | 51.2 | 65.3 | 66.0 | 0.844 |
| Go | 17 | 17 | 17 | 51.7 | 51.6 | 50.6 | 62.5 | 62.6 | 0.837 |
| FreePascal | 18 | 18 | 18 | 51.6 | 50.6 | 49.3 | 42.3 | 43.0 | 0.844 |
| Haskell | 19 | 19 | 19 | 45.8 | 44.1 | 43.0 | 54.2 | 52.3 | 0.839 |
| OCaml | 20 | 20 | 20 | 28.0 | 27.4 | 26.7 | 23.3 | 22.7 | 0.839 |
| BQN | 21 | 22 | 21 | 20.3 | 20.2 | 19.9 | 9.9 | 10.1 | 0.866 |
| JavaScript | 22 | 21 | 22 | 19.7 | 20.3 | 19.9 | 15.8 | 15.6 | 0.845 |
| PHP | 23 | 23 | 23 | 18.8 | 18.3 | 18.0 | 6.8 | 6.6 | 0.841 |
| Python | 24 | 24 | 24 | 10.7 | 10.6 | 10.5 | 1.1 | 1.0 | 0.823 |
| Lua | 25 | 25 | 25 | 7.7 | 7.2 | 7.1 | 1.5 | 1.4 | 0.830 |

« Publiée » : le classement de la campagne précédente tel qu'il était publié ; « recalculée » : la même campagne recalculée par la méthode de celle-ci (comparaison à méthode égale). Le plafond, donné au centre, est le même dans les deux.

## Zig par sa version de développement

Version 0.18.0-dev.1298+4a0817482, mesurée hors campagne sur la machine 39 avec son témoin, la version de la campagne remesurée dans les mêmes groupes : 777 et 777 processus retenus, 0 écartés, 0 cellules sans rapport. Chaque case : rapport du temps sous la version de développement au temps du témoin (moyenne géométrique des rapports appariés, et nombre de paires) ; les processus de Zig de la campagne sont multipliés par ce rapport.

| Noyau | Étiquette | Variante | petite | publiée | grande |
|---|---|---|---|---|---|
| K1 | chk | natural energy | 0.95 (6) | 0.94 (6) | 0.96 (6) |
| K1 | chk | natural_shuffled energy | 0.95 (6) | 0.96 (6) | 1.02 (6) |
| K1 | pub | aos energy | 0.87 (6) | 1.05 (6) | 1.01 (6) |
| K1 | pub | natural energy | 1.02 (6) | 0.99 (6) | 0.99 (6) |
| K1 | pub | natural_shuffled energy | 1.05 (6) | 1.03 (6) | 0.96 (6) |
| K1 | pub | soa energy | 1.00 (6) | 1.06 (6) | 1.14 (6) |
| K2 | pub | tuned 16384 | – | 1.00 (13) | – |
| K2 | pub | tuned 262144 | – | 1.00 (13) | – |
| K2 | pub | tuned 8388608 | – | 0.81 (13) | – |
| K3 | pub | rmw_padded | – | 1.01 (6) | – |
| K3 | pub | sw_padded | – | 1.01 (6) | – |
| K4 | chk | natural_unsorted | 0.99 (6) | 0.97 (6) | 0.99 (6) |
| K4 | cv | swar | 0.28 (6) | 0.31 (6) | 0.21 (6) |
| K4 | cv | tuned | 1.04 (6) | 1.12 (6) | 0.96 (6) |
| K4 | pub | branchless_unsorted | 0.25 (6) | 0.24 (6) | 0.34 (6) |
| K4 | pub | natural_unsorted | 0.24 (6) | 0.25 (6) | 0.35 (6) |
| K5 | chk | natural | 1.00 (6) | 0.99 (6) | 0.96 (6) |
| K5 | pub | natural | 1.00 (6) | 1.00 (6) | 1.04 (6) |
| K5 | pub | tuned | 1.01 (6) | 1.00 (6) | 0.93 (6) |
| K6 | chk | natural q1 | 1.06 (6) | 1.02 (6) | 1.02 (6) |
| K6 | chk | natural q6 | 0.99 (6) | 1.01 (6) | 1.10 (6) |
| K6 | cv | mt_pool q1 | 0.96 (6) | 1.00 (6) | 0.96 (6) |
| K6 | cv | mt_pool q6 | 1.01 (6) | 0.91 (6) | 1.00 (6) |
| K6 | pub | mt q1 | 1.38 (6) | 0.96 (6) | 1.05 (6) |
| K6 | pub | mt q6 | 1.38 (6) | 0.99 (6) | 1.08 (6) |
| K6 | pub | natural q1 | 0.99 (6) | 1.00 (6) | 1.00 (6) |
| K6 | pub | natural q6 | 0.86 (6) | 1.05 (6) | 1.05 (6) |
| K6 | pub | tuned q1 | 1.02 (6) | 1.01 (6) | 1.04 (6) |
| K6 | pub | tuned q6 | 1.00 (6) | 1.07 (6) | 0.99 (6) |
| K7 | chk | natural | 0.99 (6) | 0.99 (6) | 1.10 (6) |
| K7 | pub | natural | 0.98 (6) | 1.14 (6) | 0.99 (6) |
| K7 | pub | tuned | 0.95 (6) | 1.00 (6) | 0.88 (6) |
| K8 | chk | natural | 1.02 (13) | 1.02 (13) | 1.02 (13) |
| K8 | cv | tuned_it | 0.99 (6) | 1.00 (6) | 1.01 (6) |
| K8 | cv | tuned_val | 1.00 (6) | 0.98 (6) | 0.99 (6) |
| K8 | pub | natural | 1.03 (13) | 1.03 (13) | 1.02 (13) |
| K8 | pub | tuned | 1.00 (6) | 0.99 (6) | 1.00 (6) |
| K8 | pub | tuned_alloc | 0.98 (6) | 1.00 (6) | 1.00 (6) |
| K9 | chk | natural | 0.50 (6) | 0.98 (6) | 0.73 (6) |
| K9 | cv | mt_pool | 1.01 (6) | 0.84 (6) | 0.96 (6) |
| K9 | pub | mt | 1.43 (6) | 1.19 (6) | 0.98 (6) |
| K9 | pub | natural | 0.48 (6) | 0.81 (6) | 0.84 (6) |
| K9 | pub | tuned | 0.99 (6) | 1.03 (6) | 1.17 (6) |

Le témoin contre ses temps de la campagne : rapport médian 0.98, de 0.64 à 1.23 ; 74 % des cellules à moins de 10 %. Le transport annule cet écart. Latences de K8 naturel (p50, p90, p99, p99,9, maximum), rapport des médianes, appliqué dans le seul calcul « Zig 0.18, latences du plan » : chk, large : 1.02, 1.01, 1.06, 1.02, 0.99 ; chk, pub : 1.03, 0.98, 0.92, 0.84, 0.42 ; chk, small : 1.02, 1.02, 1.01, 0.99, 0.96 ; pub, large : 1.02, 1.02, 1.02, 0.92, 1.06 ; pub, pub : 1.02, 1.02, 1.02, 1.13, 0.75 ; pub, small : 1.02, 1.02, 1.02, 1.06, 1.16.

## Plafond par noyau et parts du code par défaut (« Final », au centre)

| Langage | K1 | K3 | K4 | K5 | K6 | K7 | K8 | K9 | D1 | D2 | D3 | D4 | D1, mode publié | D1, R1' |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C | 85 | 99 | 95 | 84 | 81 | 81 | 68 | 86 | 70 | 100 | 80 | 91 | 71 | 66 |
| C++ | 84 | 100 | 69 | 93 | 92 | 74 | 100 | 94 | 48 | 97 | 76 | 90 | 57 | 53 |
| Zig | 78 | 100 | 66 | 96 | 87 | 79 | 72 | 93 | 40 | 99 | 55 | 95 | 69 | 65 |
| Odin | 67 | 99 | 66 | 94 | 87 | 84 | 73 | 90 | 64 | 99 | 38 | 87 | 65 | 67 |
| Rust | 83 | 100 | 83 | 86 | 84 | 94 | 77 | 87 | 66 | 100 | 74 | 94 | 67 | 62 |
| Nim | 92 | 99 | 67 | 90 | 82 | 83 | 68 | 92 | 64 | 99 | 71 | 93 | 64 | 67 |
| C3 | 85 | 100 | 66 | 91 | 87 | 88 | 72 | 89 | 61 | 100 | 55 | 88 | 68 | 64 |
| D | 85 | 100 | 82 | 92 | 79 | 86 | 73 | 89 | 58 | 100 | 2 | 78 | 60 | 57 |
| Ada | 75 | 100 | 76 | 89 | 84 | 70 | 79 | 83 | 37 | 100 | 67 | 69 | 38 | 55 |
| Julia | 75 | 97 | 57 | 93 | 90 | 72 | 73 | 73 | 65 | 98 | 7 | 93 | 66 | 65 |
| Fortran | 84 | 100 | 47 | 86 | 73 | 74 | 92 | 84 | 56 | 99 | 82 | 86 | 65 | 61 |
| Chapel | 74 | 98 | 82 | 90 | 84 | 87 | 88 | 91 | 26 | 99 | 55 | 99 | 57 | 53 |
| Mojo | 82 | 100 | 51 | 86 | 82 | 88 | 49 | 85 | 34 | 99 | 49 | 89 | 34 | 44 |
| Swift | 89 | 98 | 45 | 97 | 81 | 80 | 72 | 90 | 32 | 96 | 32 | 81 | 33 | 42 |
| C# | 82 | 99 | 62 | 84 | 63 | 51 | 51 | 81 | 29 | 56 | 36 | 85 | 29 | 27 |
| Java | 44 | 96 | 49 | 81 | 70 | 64 | 57 | 78 | 34 | 55 | 43 | 94 | 35 | 32 |
| Go | 69 | 37 | 73 | 76 | 53 | 66 | 58 | 77 | 22 | 72 | 11 | 93 | 22 | 23 |
| FreePascal | 49 | 100 | 11 | 38 | 30 | 59 | 53 | 51 | 14 | 99 | 48 | 91 | 20 | 19 |
| Haskell | 46 | 37 | 30 | 86 | 37 | 95 | 71 | 67 | 17 | 75 | 9 | 82 | 17 | 16 |
| OCaml | 28 | 25 | 8 | 14 | 18 | 38 | 42 | 37 | 21 | 42 | 36 | 67 | 21 | 22 |
| BQN | 4 | 3 | 8 | 17 | 13 | 19 | 31 | 8 | 17 | 68 | 10 | 41 | 17 | 16 |
| JavaScript | 17 | 15 | 10 | 8 | 14 | 23 | 21 | 29 | 13 | 27 | 4 | 70 | 13 | 12 |
| PHP | 7 | 2 | 8 | 4 | 8 | 16 | 10 | 10 | 6 | 29 | 11 | 64 | 6 | 6 |
| Python | 0 | 4 | 1 | 0 | 1 | 2 | 1 | 1 | 1 | 21 | 1 | 19 | 1 | 1 |
| Lua | 1 | 5 | 0 | 1 | 1 | 5 | 2 | 1 | 3 | 25 | 0 | 41 | 3 | 3 |

D1 : code naturel sous R1 (le centre) ; « D1, mode publié » : dans le mode publié de chaque chaîne (centre de « Sans R1 ») ; « D1, R1' » : sans les vérifications qu'une option retire (centre de « R1' au lieu de R1 »). Les variantes de « Final » tirent l'un des trois (A7, A8).

## Ce qui décide de l'ordre (« Final », au centre)

Part de la variance du score au centre que porte chaque composante, parmi les langages d'un groupe (`docs/V5_3.md`, 2) : covariance de son apport au score avec le score, divisée par la variance du score. Les trois piliers somment à 100 % ; les noyaux se partagent la part du plafond, D1 à D4 celle du code par défaut. Une part négative : la composante joue, dans ce groupe, contre l'ordre du score. Le poids affiché est celui de la composante dans le score.

| Composante | Poids affiché | les 25 langages (25) | premier étage (19) | première moitié possible (14) | podium possible (8) |
|---|---|---|---|---|---|
| **Contrôle (grille)** | 35 % | **34 %** | **40 %** | **55 %** | **68 %** |
| **Plafond** | 40 % | **47 %** | **37 %** | **17 %** | **12 %** |
| K1 | 5.0 % | 6.6 % | 4.3 % | 0.4 % | 3.2 % |
| K3 | 5.0 % | 5.5 % | 3.7 % | 0.1 % | 0.2 % |
| K4 | 5.0 % | 6.5 % | 10.1 % | 8.5 % | 3.6 % |
| K5 | 5.0 % | 7.2 % | 4.1 % | 0.1 % | -0.9 % |
| K6 | 5.0 % | 5.9 % | 7.1 % | 0.7 % | 0.3 % |
| K7 | 5.0 % | 4.4 % | 1.8 % | 1.3 % | -0.2 % |
| K8 | 5.0 % | 5.1 % | 2.7 % | 4.2 % | 5.6 % |
| K9 | 5.0 % | 5.9 % | 3.3 % | 1.8 % | -0.2 % |
| **Code par défaut** | 25 % | **19 %** | **23 %** | **28 %** | **20 %** |
| D1, code naturel | 12.5 % | 9.2 % | 15.7 % | 22.0 % | 4.1 % |
| D2, coût de structure | 3.75 % | 3.8 % | 3.1 % | 0.2 % | -0.4 % |
| D3, queues de latence | 3.75 % | 2.8 % | 4.0 % | 5.3 % | 16.0 % |
| D4, hiérarchie mémoire | 5.0 % | 3.0 % | 0.0 % | 0.8 % | 0.5 % |

Écart-type du score au centre dans chaque groupe : 25.4 (les 25 langages), 11.7 (premier étage), 5.2 (première moitié possible), 2.6 (podium possible). Premier étage : C, C++, Zig*, Odin, Rust, Nim, C3, D, Ada, Julia, Fortran, Chapel, Mojo, Swift, C#, Java, Go, FreePascal, Haskell. Première moitié possible : C, C++, Zig*, Odin, Rust, Nim, C3, D, Ada, Julia, Fortran, Chapel, Mojo, Swift. Podium possible : C, C++, Zig*, Odin, Rust, Nim, C3, D. « Première moitié possible » et « podium possible » : rang plausible commençant à 12 et à 3 ou mieux.

## Tri des écarts du code naturel

Règle (`docs/V5_3.md`, 3) : pour chaque mesure du code naturel, à chaque taille et dans chaque mode du tirage, le temps d'un langage est rapporté à la médiane des temps de 15 pairs, les langages dont la chaîne produit son code machine par LLVM ou par GCC (C, C++, Zig, Odin, Rust, Nim, C3, D, Ada, Julia, Fortran, Chapel, Mojo, Swift, Haskell). Pour les autres langages, ce rapport est divisé par leur niveau : la médiane de leurs rapports à cette taille et dans ce mode, au moins 1. Une cellule est lente à partir de 2.0 (arrondi au dixième), rapide quand elle est au moins 2.0 fois plus rapide que la médiane des pairs ; un couple (langage, mesure) est signalé dans un mode s'il l'est à une taille au moins. Chaque couple signalé est rattaché à une cause : « établie » (un contrôle nommé la montre), « attribuée » (cause probable, sans contrôle propre), « à corriger » (cellule faussée par l'étude, correction à planifier) ou « à examiner » (aucune cause).

60 couples signalés : 31 dont la cause est établie, 28 dont la cause est attribuée, 1 à corriger, 0 à examiner.

| n° | Statut | Cause | Contrôle | Couples |
|---|---|---|---|---|
| 1 | à corriger | Go : binaire compilé avec `GOEXPERIMENT=simd` ; sur un processeur AVX-512, la préemption asynchrone de go1.27.3 restaure les registres ZMM sans `VZEROUPPER`, et la boucle de K1, qui mêle SSE hérité et FMA codées VEX (`GOAMD64=v4`), paie la transition. Erreur de mesure relevée et corrigée par transfert le 2 novembre, revenue avec la campagne finale de la v4 | `docs/GO.md` de l'archive (2 et 4.2) ; essai du 27 novembre (`docs/V5_3.md`, 8) | Go K1 |
| 2 | établie | clang fusionne par défaut la multiplication et l'addition du produit scalaire en une FMA (`-ffp-contract=on`), qui allonge la chaîne de dépendance de la somme | le même source compilé par gcc prend 0,45 à 0,51 fois le temps de clang (campagne, « C par gcc ») ; code machine (`docs/V5_3.md`, 8) | C K5 |
| 3 | attribuée | même facteur deux que le produit scalaire de C : fusion en FMA probable (Chapel `--fast`, Mojo, `ghc -mfma`) | aucun contrôle propre ; `docs/HASKELL.md` de l'archive (2) donne à Haskell le temps de C sur K5 | Chapel K5 (mode publié, R1'), Mojo K5, Haskell K5 |
| 4 | établie | GCC vectorise la somme conditionnelle d'octets moins bien que LLVM | le même source C compilé par gcc prend 3,9, 3,6 et 2,5 fois le temps de clang aux trois tailles (campagne, « C par gcc ») | C++ K4, Ada K4, Fortran K4 |
| 5 | établie | vérifications que R1 ajoute au mode publié (débordement des entiers de `-O safe` pour Zig, `--checks` pour Chapel, `-D_GLIBCXX_ASSERTIONS` pour C++, `-Cr -Co` pour FreePascal) : elles empêchent la vectorisation | l'écart disparaît en mode publié ; `docs/V5_1.md`, 2 (Zig) et 9.1 (Chapel) | C++ K9, Zig* K4, Chapel K5 (R1), Chapel Q6, Chapel Q1, Chapel K9, FreePascal K9 |
| 6 | établie | vérifications du mode publié qu'une option retire : contrôle de falsification des conteneurs d'Ada sur K7, bornes d'Ada, de Swift et de Mojo sur leurs tableaux | l'écart disparaît en R1' ; `docs/V5_1.md`, 9.1 (Ada) ; `docs/SWIFT.md` (2.4) et `docs/MOJO.md` (2) de l'archive | Ada K7, Ada K9, Mojo Q1, Mojo K9 (R1, mode publié), Swift K9 |
| 7 | établie | somme conditionnelle que les pairs vectorisent et que la chaîne laisse scalaire : pas de vectoriseur de boucles dans les passes de Mojo ; un branchement par octet en Swift, avec le piège de débordement de `-O` ; pas de vectoriseur automatique pour cette boucle en Go, C#, Java, Haskell, OCaml, JavaScript, Lua et Python | `docs/MOJO.md` (2), `docs/SWIFT.md` (2.4) et `docs/GO.md` (2) de l'archive | Mojo K4, Swift K4, C# K4, Java K4, Go K4, Haskell K4, OCaml K4, JavaScript K4, Python K4, Lua K4 |
| 8 | attribuée | boucle que les pairs vectorisent et que la chaîne laisse scalaire, sans relecture qui le consigne : somme conditionnelle de FreePascal et de PHP ; stencil de C#, Go, JavaScript, PHP, Python, Lua et BQN ; stencil de Mojo une fois ses vérifications retirées | aucun contrôle propre | Mojo K9 (R1'), C# K9, Go K9, FreePascal K4, BQN K9, JavaScript K9, PHP K4, PHP K9, Python K9, Lua K9 |
| 9 | attribuée | stencil de Nim sur une `seq` : vérifications de bornes de `-d:release`, et boucle que clang ne vectorise pas même sans elles (Nim lui passe `-fno-strict-aliasing`) | `docs/NIM.md` de l'archive (2), établi pour la forme imbriquée, non refait pour la forme contiguë | Nim K9 |
| 10 | établie | ramasse-miettes de D : chaque nœud de K8 est un `new` de classe | `docs/DLANG.md` de l'archive (2) | D K8 |
| 11 | attribuée | coût d'allocation du type par défaut : comptage de références de la classe de Swift, nœuds de Haskell confiés au ramasse-miettes | aucun contrôle propre ; `docs/SWIFT.md` de l'archive (2.4, point 9) chiffre une part du coût de Swift | Swift K8, Haskell K8 |
| 12 | établie | types par défaut de Haskell : liste chaînée pour K1, `Data.IntMap` pour K7 faute de table de hachage livrée, tableau immuable `UArray` pour K9 | `docs/NATURAL.md` ; `docs/HASKELL.md` de l'archive (1 et 2) | Haskell K1, Haskell K7, Haskell K9 |
| 13 | attribuée | types par défaut du langage : enregistrements en références de JavaScript, PHP et Lua et matrice de doubles de BQN pour K1 ; `TDictionary` de FreePascal (deux recherches par ligne) et `Hashtbl` d'OCaml pour K7 ; idiomes de tableaux de BQN pour Q1 et K8 ; produit scalaire de FreePascal | `docs/NATURAL.md` décrit ces types ; leur part dans l'écart n'a pas de contrôle propre | FreePascal K5, FreePascal K7, OCaml K7, BQN K1, BQN Q1, BQN K8, JavaScript K1, PHP K1, Lua K1 |
| 14 | établie | ni C ni Fortran n'ont de table de hachage en bibliothèque standard : leur code naturel est le chaînage des manuels, écrit pour le noyau, au nombre de seaux fixé d'avance sur le nombre de clés et haché par un modulo ; les tables de bibliothèque des pairs grandissent et hachent plus fort. Avantage que la règle du code naturel accepte | `docs/NATURAL.md` (K7, cas discutables) ; sources de `bench/c` et de `bench/fortran` | C K7, Fortran K7 |
| 15 | attribuée | allocation par un ramasse-miettes générationnel : un nœud de K8 coûte un déplacement de pointeur, contre une allocation et une libération chez les pairs | aucun contrôle propre | Java K8, OCaml K8 |
| 16 | établie | sans vérification de bornes, LLVM vectorise la boucle naturelle de Q6 d'Odin ; celle des autres pairs reste scalaire | campagne, taille publiée : Odin 48,7 ms avec les bornes, 18,4 ms sans, 13,6 ms pour sa forme SIMD ; C 40,9 ms | Odin Q6 |
| 17 | attribuée | primitives de tableaux de CBQN, vectorisées | aucun contrôle propre ; `docs/BQN.md` de l'archive | BQN Q6 |

| Langage | Mesure | Sens | R1 | Mode publié | R1' | Niveau | Cause | Statut |
|---|---|---|---|---|---|---|---|---|
| C | K5 | lent | **2.0** | **2.1** | **2.1** | 1 | 2 | établie |
| C | K7 | rapide | **0.24** | **0.37** | **0.37** | 1 | 14 | établie |
| C++ | K4 | lent | **4.0** | **3.9** | **3.9** | 1 | 4 | établie |
| C++ | K9 | lent | **4.3** | 1.0 | 1.0 | 1 | 5 | établie |
| Zig* | K4 | lent | **51.1** | 1.0 | 1.0 | 1 | 5 | établie |
| Odin | Q6 | rapide | 0.96 | 1.02 | **0.23** | 1 | 16 | établie |
| Nim | K9 | lent | **3.2** | **3.5** | **2.3** | 1 | 9 | attribuée |
| D | K8 | lent | **2.6** | **2.9** | **2.9** | 1 | 10 | établie |
| Ada | K4 | lent | **3.9** | **3.8** | **3.9** | 1 | 4 | établie |
| Ada | K7 | lent | **7.0** | **7.4** | 1.5 | 1 | 6 | établie |
| Ada | K9 | lent | **4.2** | **4.6** | 1.0 | 1 | 6 | établie |
| Fortran | K4 | lent | **9.6** | **4.1** | **4.1** | 1 | 4 | établie |
| Fortran | K7 | rapide | **0.33** | **0.36** | **0.36** | 1 | 14 | établie |
| Chapel | K5 | lent | **4.5** | **2.0** | **2.0** | 1 | 5, 3 | attribuée |
| Chapel | Q6 | lent | **5.4** | 1.0 | 1.0 | 1 | 5 | établie |
| Chapel | Q1 | lent | **7.0** | 1.0 | 1.1 | 1 | 5 | établie |
| Chapel | K9 | lent | **32.9** | 1.0 | 1.1 | 1 | 5 | établie |
| Mojo | K4 | lent | **5.2** | **5.0** | **5.0** | 1 | 7 | établie |
| Mojo | K5 | lent | **2.0** | **2.0** | **2.0** | 1 | 3 | attribuée |
| Mojo | Q1 | lent | **2.0** | **2.4** | 0.9 | 1 | 6 | établie |
| Mojo | K9 | lent | **15.7** | **17.1** | **2.2** | 1 | 6, 8 | attribuée |
| Swift | K4 | lent | **50.7** | **49.4** | **11.6** | 1 | 7 | établie |
| Swift | K8 | lent | 1.9 | **2.1** | 1.9 | 1 | 11 | attribuée |
| Swift | K9 | lent | **3.3** | **3.6** | 1.0 | 1 | 6 | établie |
| C# | K4 | lent | **29.1** | **27.9** | **26.3** | 1.2 à 2.0 | 7 | établie |
| C# | K9 | lent | **4.3** | **4.4** | **4.7** | 1.2 à 2.0 | 8 | attribuée |
| Java | K4 | lent | **32.1** | **30.1** | **29.4** | 1.4 à 1.7 | 7 | établie |
| Java | K8 | rapide | **0.29** | **0.33** | **0.33** | 1.4 à 1.7 | 15 | attribuée |
| Go | K1 | lent | **36.0** | **33.5** | **49.6** | 1.1 à 2.2 | 1 | à corriger |
| Go | K4 | lent | **3.7** | **4.2** | **5.1** | 1.1 à 2.2 | 7 | établie |
| Go | K9 | lent | 1.8 | 1.9 | **2.4** | 1.1 à 2.2 | 8 | attribuée |
| FreePascal | K4 | lent | **19.2** | **20.1** | **17.9** | 2.0 à 4.9 | 8 | attribuée |
| FreePascal | K5 | lent | 1.4 | **2.0** | 1.8 | 2.0 à 4.9 | 13 | attribuée |
| FreePascal | K7 | lent | 1.2 | **2.6** | **2.5** | 2.0 à 4.9 | 13 | attribuée |
| FreePascal | K9 | lent | **3.2** | 1.3 | 1.3 | 2.0 à 4.9 | 5 | établie |
| Haskell | K1 | lent | **5.7** | **5.8** | **5.9** | 1 | 12 | établie |
| Haskell | K4 | lent | **4.7** | **4.6** | **4.6** | 1 | 7 | établie |
| Haskell | K5 | lent | **2.4** | **2.4** | **2.3** | 1 | 3 | attribuée |
| Haskell | K7 | lent | **44.3** | **44.9** | **48.3** | 1 | 12 | établie |
| Haskell | K8 | lent | 1.7 | **2.0** | **2.0** | 1 | 11 | attribuée |
| Haskell | K9 | lent | **12.6** | **13.7** | **14.8** | 1 | 12 | établie |
| OCaml | K4 | lent | **15.8** | **18.3** | **22.1** | 2.1 à 4.5 | 7 | établie |
| OCaml | K7 | lent | 1.9 | **2.1** | **2.7** | 2.1 à 4.5 | 13 | attribuée |
| OCaml | K8 | rapide | **0.24** | **0.27** | **0.24** | 2.1 à 4.5 | 15 | attribuée |
| BQN | K1 | lent | **2.6** | **2.5** | **2.4** | 2.6 à 3.6 | 13 | attribuée |
| BQN | Q1 | lent | **2.1** | **2.4** | **2.6** | 2.6 à 3.6 | 13 | attribuée |
| BQN | K8 | lent | **2.2** | **2.4** | **2.5** | 2.6 à 3.6 | 13 | attribuée |
| BQN | K9 | lent | **5.6** | **5.7** | **6.0** | 2.6 à 3.6 | 8 | attribuée |
| BQN | Q6 | rapide | **0.29** | **0.30** | **0.32** | 2.6 à 3.6 | 17 | attribuée |
| JavaScript | K1 | lent | **4.8** | **4.3** | **4.2** | 2.8 à 4.7 | 13 | attribuée |
| JavaScript | K4 | lent | **21.2** | **18.5** | **17.9** | 2.8 à 4.7 | 7 | établie |
| JavaScript | K9 | lent | **5.3** | **5.3** | **5.2** | 2.8 à 4.7 | 8 | attribuée |
| PHP | K1 | lent | **4.3** | **3.6** | **3.5** | 4.8 à 6.2 | 13 | attribuée |
| PHP | K4 | lent | **21.1** | **18.3** | **17.4** | 4.8 à 6.2 | 8 | attribuée |
| PHP | K9 | lent | **30.6** | **29.6** | **30.5** | 4.8 à 6.2 | 8 | attribuée |
| Python | K4 | lent | **4.3** | **4.8** | **4.7** | 46.6 à 72.9 | 7 | établie |
| Python | K9 | lent | **3.8** | **3.9** | **4.3** | 46.6 à 72.9 | 8 | attribuée |
| Lua | K1 | lent | **2.2** | **2.0** | **2.0** | 16.0 à 25.1 | 13 | attribuée |
| Lua | K4 | lent | **8.6** | **8.4** | **8.3** | 16.0 à 25.1 | 7 | établie |
| Lua | K9 | lent | **4.4** | **4.4** | **4.6** | 16.0 à 25.1 | 8 | attribuée |

Chaque case : le rapport le plus extrême des trois tailles (lent : rapport au niveau du langage, le plus grand ; rapide : rapport à la médiane des pairs, le plus petit), en gras dans les modes où le couple est signalé. Niveau : 1 pour un pair ; pour les autres, étendue sur les tailles et les modes.

## Forme retenue par « Final », cellule par cellule et taille par taille (estimation ponctuelle)

Chaque case : forme retenue aux tailles petite / publiée / grande (« pub » : une variante publiée) ; rapport de son temps à la meilleure forme publiée, à la taille publiée.

| Langage | K4 | K5 | Q6 | Q1 | Q6 mt | Q1 mt | K7 | K8 | K9 | K9 mt |
|---|---|---|---|---|---|---|---|---|---|---|
| C | k4 tuned/k4 tuned/k4 tuned 0.42 | pub/pub/pub 1.00 | q6 tuned_v/q6 tuned_v/q6 tuned_v 0.71 | pub/pub/pub 1.00 | q6 mt_pool_v/q6 mt_pool_v/q6 mt_pool_v 0.74 | q1 mt_pool/pub/q1 mt_pool 1.00 | pub/pub/pub 1.00 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.35 | k9 tuned_v/pub/k9 tuned_v 1.00 | k9 mt_pool/pub/k9 mt_pool_v 1.00 |
| C++ | k4 tuned/k4 tuned/k4 tuned 0.17 | pub/pub/pub 1.00 | pub/q6 tuned_v/pub 0.99 | pub/pub/pub 1.00 | q6 mt_pool/q6 mt_pool/pub 0.90 | q1 mt_pool/q1 mt_pool/pub 0.96 | pub/pub/pub 1.00 | k8 tuned_val/k8 tuned_val/k8 tuned_val 0.33 | k9 tuned_v/k9 tuned_v/k9 tuned_v 1.00 | k9 mt_pool_v/pub/k9 mt_pool_v 1.00 |
| Zig | k4 tuned/k4 tuned/k4 swar 0.43 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | q6 mt_pool/q6 mt_pool/q6 mt_pool 0.92 | q1 mt_pool/pub/q1 mt_pool 1.00 | pub/pub/pub 1.00 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.45 | pub/pub/pub 1.00 | k9 mt_pool/k9 mt_pool/k9 mt_pool 0.50 |
| Odin | k4 tuned/k4 tuned/k4 tuned 0.54 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | q1 tuned_v/q1 tuned_v/q1 tuned_v 0.47 | q6 mt_pool/pub/pub 1.00 | q1 mt_pool_v/q1 mt_pool_v/q1 mt_pool_v 0.50 | pub/pub/pub 1.00 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.31 | pub/pub/pub 1.00 | k9 mt_pool/pub/pub 1.00 |
| Rust | k4 tuned/k4 tuned/k4 tuned 0.42 | pub/pub/pub 1.00 | q6 tuned_v/q6 tuned_v/q6 tuned_v 0.85 | pub/pub/pub 1.00 | q6 mt_pool_v/q6 mt_pool_v/q6 mt_pool_v 0.92 | q1 mt_pool/pub/pub 1.00 | pub/pub/pub 1.00 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.27 | k9 tuned_v/pub/pub 1.00 | k9 mt_pool/k9 mt_pool_v/k9 mt_pool_v 0.86 |
| Nim | k4 tuned/k4 tuned/k4 tuned 0.52 | pub/pub/pub 1.00 | q6 tuned_v/q6 tuned_v/q6 tuned_v 0.82 | q1 tuned_v/q1 tuned_v/q1 tuned_v 0.57 | q6 mt_pool/q6 mt_pool_v/q6 mt_pool_v 0.81 | q1 mt_pool_v/q1 mt_pool_v/q1 mt_pool_v 0.48 | pub/pub/pub 1.00 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.30 | k9 tuned_v/pub/k9 tuned_v 1.00 | k9 mt_pool/pub/k9 mt_pool_v 1.00 |
| C3 | k4 tuned/k4 tuned/k4 tuned 0.44 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | q1 tuned_v/pub/q1 tuned_v 1.00 | q6 mt_pool/q6 mt_pool/pub 0.72 | q1 mt_pool/q1 mt_pool_v/pub 0.82 | pub/pub/pub 1.00 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.33 | pub/pub/pub 1.00 | k9 mt_pool/pub/k9 mt_pool 1.00 |
| D | k4 tuned/k4 tuned/k4 tuned 0.47 | pub/pub/pub 1.00 | q6 tuned_v/q6 tuned_v/q6 tuned_v 0.75 | pub/pub/pub 1.00 | q6 mt_pool/q6 mt_pool_v/q6 mt_pool_v 0.83 | q1 mt_pool/pub/q1 mt_pool 1.00 | pub/pub/pub 1.00 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.33 | pub/pub/pub 1.00 | k9 mt_pool/pub/k9 mt_pool 1.00 |
| Ada | k4 tuned/k4 tuned/k4 tuned 0.20 | pub/pub/pub 1.00 | q6 tuned_v/q6 tuned_v/pub 0.86 | q1 tuned_v/q1 tuned_v/q1 tuned_v 0.58 | q6 mt_pool/q6 mt_pool/pub 0.68 | q1 mt_pool_v/q1 mt_pool_v/q1 mt_pool_v 0.55 | pub/pub/pub 1.00 | k8 tuned_it/pub/pub 1.00 | pub/pub/pub 1.00 | k9 mt_pool/k9 mt_pool/k9 mt_pool 0.60 |
| Julia | k4 tuned/k4 tuned/k4 tuned 0.51 | k5 tuned_v/k5 tuned_v/k5 tuned_v 0.88 | q6 tuned_v/q6 tuned_v/q6 tuned_v 0.85 | q1 tuned_v/q1 tuned_v/q1 tuned_v 0.34 | q6 mt_pool_v/q6 mt_pool_v/q6 mt_pool_v 0.69 | q1 mt_pool_v/q1 mt_pool_v/q1 mt_pool_v 0.30 | pub/k7 tuned_pf/k7 tuned_pf 0.70 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.25 | k9 tuned_v/k9 tuned_v/k9 tuned_v 0.95 | pub/k9 mt_pool_v/pub 0.95 |
| Fortran | k4 swar/k4 swar/k4 swar 0.25 | k5 rq_acc16/k5 rq_acc16/k5 rq_acc16 0.89 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | k7 tuned_oa/pub/pub 1.00 | k8 tuned_val/k8 tuned_val/k8 tuned_val 0.39 | pub/pub/pub 1.00 | pub/pub/pub 1.00 |
| Chapel | k4 tuned/k4 tuned/k4 tuned 0.62 | pub/pub/pub 1.00 | q6 tuned_v/q6 tuned_v/pub 0.83 | pub/q1 tuned_v/q1 tuned_v 0.88 | q6 mt_pool_v/q6 mt_pool_v/pub 0.75 | q1 mt_pool_v/q1 mt_pool_v/q1 mt_pool_v 0.79 | pub/pub/pub 1.00 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.25 | pub/pub/k9 tuned_v 1.00 | k9 mt_pool_v/pub/k9 mt_pool_v 1.00 |
| Mojo | k4 tuned/k4 tuned/k4 tuned 0.11 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | q1 tuned_v/q1 tuned_v/q1 tuned_v 0.76 | pub/pub/pub 1.00 | q1 mt_pool_v/q1 mt_pool_v/q1 mt_pool_v 0.80 | pub/pub/pub 1.00 | k8 tuned_val/k8 tuned_val/k8 tuned_val 0.74 | pub/pub/pub 1.00 | pub/pub/pub 1.00 |
| Swift | k4 tuned/k4 tuned/k4 tuned 0.65 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | q6 mt_pool/pub/pub 1.00 | q1 mt_pool/pub/q1 mt_pool 1.00 | pub/k7 tuned_pf/pub 0.85 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.33 | pub/pub/pub 1.00 | k9 mt_pool/pub/k9 mt_pool 1.00 |
| C# | k4 tuned/k4 tuned/k4 tuned 0.07 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | q6 mt_pool/q6 mt_pool/pub 0.89 | q1 mt_pool/pub/q1 mt_pool 1.00 | pub/pub/pub 1.00 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.51 | pub/pub/pub 1.00 | k9 mt_pool/k9 mt_pool/k9 mt_pool 0.67 |
| Java | k4 tuned/k4 tuned/k4 tuned 0.26 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | q1 tuned_v/q1 tuned_v/q1 tuned_v 0.51 | q6 mt_pool/q6 mt_pool/q6 mt_pool 0.96 | q1 mt_pool_v/q1 mt_pool_v/q1 mt_pool_v 0.52 | k7 rq_iso/k7 rq_iso/k7 rq_iso 0.75 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.61 | pub/k9 tuned_v/k9 tuned_v 0.84 | k9 mt_pool/k9 mt_pool_v/pub 0.67 |
| Go | k4 tuned/k4 tuned/k4 tuned 0.07 | pub/k5 tuned_v/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.49 | k9 tuned_v/k9 tuned_v/k9 tuned_v 0.61 | k9 mt_pool_v/k9 mt_pool_v/k9 mt_pool_v 0.84 |
| FreePascal | k4 swar/k4 swar/k4 swar 0.29 | k5 tuned_v/k5 tuned_v/k5 tuned_v 0.83 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | q6 mt_pool/pub/q6 mt_pool 1.00 | q1 mt_pool/pub/pub 1.00 | pub/pub/pub 1.00 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.42 | pub/pub/pub 1.00 | k9 mt_pool/k9 mt_pool/k9 mt_pool 0.83 |
| Haskell | k4 tuned/k4 tuned/k4 tuned 0.23 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.39 | pub/pub/pub 1.00 | pub/pub/pub 1.00 |
| OCaml | k4 tuned/k4 swar/k4 swar 0.32 | pub/pub/pub 1.00 | q6 tuned_s/q6 tuned_s/q6 tuned_s 0.84 | pub/pub/pub 1.00 | q6 mt_pool_s/q6 mt_pool_s/q6 mt_pool_s 0.94 | q1 mt_pool/pub/q1 mt_pool 1.00 | k7 tuned_oa/k7 tuned_oa/pub 0.88 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.73 | pub/pub/pub 1.00 | k9 mt_pool/k9 mt_pool/k9 mt_pool 0.56 |
| BQN | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 |
| JavaScript | k4 swar/k4 swar/k4 swar 0.35 | k5 rq_f64/k5 rq_f64/pub 0.90 | q6 tuned_s/q6 tuned_s/q6 tuned_s 0.64 | pub/pub/pub 1.00 | q6 mt_pool_s/q6 mt_pool_s/q6 mt_pool_s 0.60 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.72 | pub/pub/pub 1.00 | k9 rq_slide_mt/k9 rq_slide_mt/k9 rq_slide_mt 0.75 |
| PHP | k4 tuned/k4 tuned/k4 tuned 0.06 | pub/pub/pub 1.00 | q6 tuned_s/q6 tuned_s/q6 tuned_s 0.71 | pub/pub/pub 1.00 | pub/q6 mt_pool_s/q6 mt_pool_s 0.65 | pub/pub/pub 1.00 | k7 tuned_oa/k7 tuned_oa/pub 0.84 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 |
| Python | k4 tuned/k4 tuned/k4 tuned 0.12 | pub/pub/pub 1.00 | k6 rq_cols/k6 rq_cols/k6 rq_cols 0.58 | pub/pub/pub 1.00 | k6 rq_cols_mt/k6 rq_cols_mt/k6 rq_cols_mt 0.34 | pub/pub/pub 1.00 | pub/k7 tuned_oa/k7 tuned_oa 0.45 | k8 tuned_val/k8 tuned_val/k8 tuned_val 0.59 | pub/pub/pub 1.00 | k9 mt_pool/pub/pub 1.00 |
| Lua | k4 swar/k4 swar/k4 swar 0.94 | pub/pub/pub 1.00 | k6 rq_nest/k6 rq_nest/k6 rq_nest 0.92 | pub/pub/pub 1.00 | k6 rq_nest_mt/k6 rq_nest_mt/k6 rq_nest_mt 0.58 | pub/pub/pub 1.00 | k7 tuned_oa/k7 rq_pack/k7 rq_pack 0.62 | k8 tuned_val/k8 tuned_val/k8 tuned_val 0.94 | k9 rq_slide/k9 rq_slide/k9 rq_slide 0.92 | k9 rq_slide_mt/k9 rq_slide_mt/k9 rq_slide_mt 0.87 |

## Campagne

Écart entre la passe la plus lente et la plus rapide d'une cellule : médiane 13.1 % ; 1079 cellules sur 2972 au-delà de 20 %. Une fois retiré l'effet commun de chaque groupe dans chaque passe (A5) : médiane 11.2 % ; 974 cellules au-delà de 20 %.

Effet commun d'un groupe dans une passe (A5) : médiane des valeurs absolues 1.9 % ; le plus fort : 12.8 % (k7 pub, passe 0).

Borne à quatre fils (STREAM triad sur 4 fils) : 42.9 Go/s avec la sonde corrigée (A6) ; relevé d'origine : 152.8 Go/s.

Machine de chaque groupe et de chaque passe :

* machine 38 : 69 groupes

Effet de machine : sans objet, une seule machine a mesuré la campagne.

## Cellules

* Tous les calculs : formes ou cellules substituées manquantes : aucune ; cellules de la base remplies (temps le plus lent des autres langages) : BQN k1 aos energy (grande), Python k1 natural energy (grande), BQN k1 natural energy (grande), Python k1 natural_shuffled energy (grande), BQN k1 natural_shuffled energy (grande), BQN k1 soa energy (grande)

Processeur des enregistrements : 6/173/1 Intel(R) Xeon(R) Processor @ 2.30GHz (9738 enregistrements) ; C par gcc : 6/173/1 Intel(R) Xeon(R) Processor @ 2.30GHz (420 enregistrements).

Processus écartés : 0 ; cellules non exécutées (étalonnage hors mémoire ou hors durée) : 6 ; vol de temps > 5 % après reprise : 0.
* non exécutée : BQN pub large k1 aos energy (oom)
* non exécutée : BQN pub large k1 natural energy (oom)
* non exécutée : BQN pub large k1 natural_shuffled energy (oom)
* non exécutée : BQN pub large k1 soa energy (oom)
* non exécutée : Python pub large k1 natural energy (oom)
* non exécutée : Python pub large k1 natural_shuffled energy (oom)

C par gcc : processus écartés : 0 ; cellules non exécutées (étalonnage hors mémoire ou hors durée) : 0 ; vol de temps > 5 % après reprise : 0.
