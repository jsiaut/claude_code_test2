# v5.1 : le classement — résultats

*Plans : `docs/V4_FINAL.md` (section 8), `docs/V4_1.md` (corrections A1 à A4 de l'analyse), `docs/V5.md` (campagne rejouée, corrections A5 et A6) et `docs/V5_1.md` (A7 et A8 : mode du code naturel tiré au sort), fixés avant les mesures ou avant leur analyse. Généré par `analysis/final_v4.py` à partir de `results/final/raw`, de `results/final/b3.jsonl` et du relevé des formes (`results/converge/forms.json`).*

Machines : 38 ; b3 de référence (le plus lent des 16 décalages, A2) : 64.24 ms ; b3 des groupes de K3 : passe 0 64.62 ms, passe 1 64.20 ms, passe 2 63.92 ms ; avec la médiane des 16 décalages (méthode du 23 novembre) : 58.12 ms.

## Classement « Final »

| Rang | Langage | Score | Score au centre | Rang espéré | Rang plausible | Devance le suivant | Plafond | Code par défaut | Contrôle |
|---|---|---|---|---|---|---|---|---|---|
| 1 | C | 83.4 | 85.9 | 1.70 | 1–4 | 68 % | 84.6 | 79.9 | 91.7 |
| 2 | C++ | 81.7 | 84.4 | 2.64 | 1–7 | 80 % | 87.7 | 68.0 | 92.4 |
| 3 | Odin | 78.6 | 79.6 | 4.77 | 2–8 | 54 % | 81.7 | 69.9 | 84.0 |
| 4 | Rust | 78.1 | 79.8 | 5.08 | 2–9 | 54 % | 86.6 | 77.6 | 73.6 |
| 5 | Zig | 77.7 | 78.5 | 5.70 | 2–10 | 54 % | 82.5 | 59.8 | 87.2 |
| 6 | Nim | 77.4 | 79.0 | 5.86 | 2–9 | 61 % | 83.5 | 75.9 | 76.1 |
| 7 | C3 | 76.7 | 78.1 | 6.59 | 3–10 | 50 % | 84.2 | 71.6 | 75.7 |
| 8 | D | 76.6 | 79.6 | 6.69 | 3–12 | 76 % | 85.6 | 59.6 | 87.1 |
| 9 | Ada | 74.0 | 75.2 | 8.84 | 5–12 | 66 % | 81.6 | 57.5 | 80.6 |
| 10 | Julia | 72.4 | 73.5 | 10.16 | 6–13 | 58 % | 77.9 | 66.8 | 73.3 |
| 11 | Fortran | 71.8 | 72.3 | 10.58 | 6–14 | 55 % | 78.5 | 72.4 | 65.3 |
| 12 | Chapel | 70.9 | 70.2 | 10.92 | 6–14 | 71 % | 86.7 | 55.6 | 61.8 |
| 13 | Mojo | 68.3 | 69.3 | 12.70 | 10–14 | 58 % | 75.9 | 56.9 | 70.5 |
| 14 | Swift | 67.7 | 68.6 | 13.00 | 11–14 | 95 % | 79.7 | 51.4 | 68.1 |
| 15 | C# | 61.3 | 63.4 | 14.94 | 14–16 | 96 % | 69.9 | 45.3 | 68.8 |
| 16 | Java | 52.7 | 53.7 | 16.83 | 16–18 | 61 % | 65.3 | 50.5 | 42.7 |
| 17 | Go | 51.7 | 52.6 | 17.13 | 16–18 | 49 % | 62.5 | 42.2 | 48.7 |
| 18 | FreePascal | 51.6 | 50.5 | 17.12 | 15–19 | 83 % | 42.3 | 47.2 | 62.3 |
| 19 | Haskell | 45.8 | 45.6 | 18.76 | 18–19 | 100 % | 54.2 | 37.4 | 41.5 |
| 20 | OCaml | 28.0 | 26.3 | 20.14 | 20–21 | 94 % | 23.3 | 35.5 | 23.2 |
| 21 | BQN | 20.3 | 17.9 | 21.76 | 21–23 | 52 % | 9.9 | 28.1 | 19.7 |
| 22 | JavaScript | 19.7 | 17.7 | 21.99 | 21–24 | 62 % | 15.8 | 25.1 | 14.6 |
| 23 | PHP | 18.8 | 17.8 | 22.30 | 21–23 | 97 % | 6.8 | 21.9 | 27.4 |
| 24 | Python | 10.7 | 12.7 | 24.08 | 22–25 | 73 % | 1.1 | 7.7 | 29.7 |
| 25 | Lua | 7.7 | 6.4 | 24.73 | 24–25 | — | 1.5 | 13.5 | 6.8 |

Score : moyenne du score sur les variantes de l'analyse ; il fixe l'ordre. Score au centre, plafond, code par défaut et contrôle : poids et choix principaux, estimation ponctuelle. Rang espéré : rang moyen sur les variantes.

Mode du code naturel, tiré dans chaque variante (A7, A8) : R1 dans 33.4 % des variantes, mode publié dans 33.5 % des variantes, R1' dans 33.1 % des variantes ; au centre, R1.

Étages (paires ordonnées dans au moins 95 % des variantes) : C, C++, Odin, Rust, Zig, Nim, C3, D, Ada, Julia, Fortran, Chapel, Mojo, Swift, C#, Java, Go, FreePascal, Haskell | OCaml, BQN, JavaScript, PHP, Python, Lua

## Tous les calculs

| Langage | Final | Base, trois tailles | Sans les tailles (taille publiée seule) | Sans R1 | Sans R2 | Sans C1 | Sans R4 | R1' au lieu de R1 | Taille petite | Taille grande | Sélection indépendante | D3 et D4 sur trois processus | Sur les seules mesures | Sans A1 | Sans A2 | Sans A3 | Sans A4 | Sans A5 | Sans A6 | Sans A7 | Sans A8 | Méthode du 23 novembre | C par gcc | Campagne précédente |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C | 1 | 1 | 2 | 1 | 1 | 1 | 2 | 1 | 1 | 2 | 1 | 1 | 2 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| C++ | 2 | 2 | 1 | 2 | 2 | 2 | 1 | 2 | 2 | 1 | 2 | 2 | 5 ** | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 |
| Odin | 3 | 6 ** | 3 | 4 | 3 | 3 | 6 ** | 3 | 3 | 3 | 3 | 3 | 6 ** | 3 | 3 | 4 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 |
| Rust | 4 | 4 | 5 | 5 | 5 | 5 | 3 | 6 | 4 | 6 | 5 | 5 | 1 ** | 4 | 4 | 5 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 |
| Zig | 5 | 7 | 7 | 3 | 4 | 8 ** | 7 | 4 | 5 | 4 | 4 | 4 | 9 ** | 5 | 5 | 3 | 5 | 5 | 5 | 8 ** | 5 | 6 | 5 | 8 |
| Nim | 6 | 9 ** | 4 | 6 | 6 | 7 | 8 | 5 | 7 | 5 | 6 | 6 | 3 ** | 7 | 6 | 6 | 6 | 6 | 6 | 5 | 6 | 7 | 6 | 6 |
| C3 | 7 | 3 ** | 6 | 7 | 7 | 4 ** | 4 ** | 7 | 6 | 9 | 7 | 8 | 4 ** | 6 | 7 | 7 | 7 | 7 | 7 | 7 | 7 | 5 | 7 | 7 |
| D | 8 | 5 ** | 8 | 8 | 8 | 6 | 5 ** | 8 | 8 | 7 | 8 | 7 | 10 | 8 | 8 | 8 | 8 | 8 | 8 | 6 | 8 | 8 | 8 | 5 |
| Ada | 9 | 8 | 9 | 9 | 9 | 9 | 9 | 9 | 12 ** | 8 | 9 | 9 | 12 ** | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 |
| Julia | 10 | 13 ** | 11 | 11 | 10 | 12 | 10 | 10 | 11 | 10 | 10 | 10 | 11 | 10 | 10 | 10 | 11 | 10 | 10 | 10 | 10 | 12 | 10 | 10 |
| Fortran | 11 | 11 | 10 | 12 | 11 | 10 | 11 | 12 | 10 | 11 | 11 | 11 | 8 ** | 12 | 11 | 11 | 10 | 11 | 11 | 11 | 11 | 11 | 11 | 11 |
| Chapel | 12 | 10 | 12 | 10 | 12 | 11 | 13 | 11 | 9 ** | 12 | 12 | 12 | 7 ** | 11 | 12 | 12 | 12 | 12 | 12 | 12 | 12 | 10 | 12 | 12 |
| Mojo | 13 | 12 | 13 | 13 | 13 | 14 | 12 | 13 | 13 | 13 | 13 | 13 | 14 | 13 | 13 | 13 | 13 | 13 | 13 | 13 | 13 | 13 | 13 | 14 |
| Swift | 14 | 14 | 14 | 14 | 14 | 13 | 14 | 14 | 14 | 14 | 14 | 14 | 13 | 14 | 14 | 14 | 14 | 14 | 14 | 14 | 14 | 14 | 14 | 13 |
| C# | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 |
| Java | 16 | 17 | 16 | 16 | 16 | 17 | 17 | 16 | 17 | 17 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 |
| Go | 17 | 18 | 17 | 18 | 17 | 18 | 18 | 18 | 18 | 18 | 18 | 17 | 17 | 17 | 18 | 18 | 18 | 17 | 18 | 17 | 17 | 18 | 17 | 17 |
| FreePascal | 18 | 16 | 18 | 17 | 18 | 16 | 16 | 17 | 16 | 16 | 17 | 18 | 19 | 18 | 17 | 17 | 17 | 18 | 17 | 18 | 18 | 17 | 18 | 18 |
| Haskell | 19 | 19 | 19 | 19 | 19 | 19 | 19 | 19 | 19 | 19 | 19 | 19 | 18 | 19 | 19 | 19 | 19 | 19 | 19 | 19 | 19 | 19 | 19 | 19 |
| OCaml | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 |
| BQN | 21 | 21 | 21 | 21 | 21 | 21 | 21 | 21 | 21 | 23 | 21 | 21 | 22 | 21 | 21 | 21 | 21 | 21 | 21 | 21 | 21 | 21 | 21 | 21 |
| JavaScript | 22 | 22 | 22 | 22 | 22 | 22 | 22 | 22 | 23 | 21 | 22 | 22 | 21 | 22 | 22 | 22 | 22 | 22 | 22 | 22 | 22 | 22 | 22 | 22 |
| PHP | 23 | 23 | 23 | 23 | 23 | 23 | 23 | 23 | 22 | 22 | 23 | 23 | 23 | 23 | 23 | 23 | 23 | 23 | 23 | 23 | 23 | 23 | 23 | 23 |
| Python | 24 | 24 | 24 | 24 | 24 | 24 | 24 | 24 | 24 | 24 | 24 | 24 | 25 | 24 | 24 | 24 | 24 | 24 | 24 | 24 | 24 | 24 | 24 | 24 |
| Lua | 25 | 25 | 25 | 25 | 25 | 25 | 25 | 25 | 25 | 25 | 25 | 25 | 24 | 25 | 25 | 25 | 25 | 25 | 25 | 25 | 25 | 25 | 25 | 25 |

Chaque case : place dans le calcul ; ** : plus de deux places d'écart avec « Final ». Ordre des lignes : « Final ». « Sans A1 » à « Sans A8 » : « Final » sans une de ses corrections ; « Méthode du 23 novembre » : sans aucune et classée au rang moyen ; « Campagne précédente » : son classement publié.

## Rangs qui bougent de plus de deux places par rapport à « Final »

* Base, trois tailles : Odin 6e (Final 3e), Nim 9e (Final 6e), C3 3e (Final 7e), D 5e (Final 8e), Julia 13e (Final 10e)
* Sans les tailles (taille publiée seule) : aucun
* Sans R1 : aucun
* Sans R2 : aucun
* Sans C1 : Zig 8e (Final 5e), C3 4e (Final 7e)
* Sans R4 : Odin 6e (Final 3e), C3 4e (Final 7e), D 5e (Final 8e)
* R1' au lieu de R1 : aucun
* Taille petite : Ada 12e (Final 9e), Chapel 9e (Final 12e)
* Taille grande : aucun
* Sélection indépendante : aucun
* D3 et D4 sur trois processus : aucun
* Sur les seules mesures : C++ 5e (Final 2e), Odin 6e (Final 3e), Rust 1er (Final 4e), Zig 9e (Final 5e), Nim 3e (Final 6e), C3 4e (Final 7e), Ada 12e (Final 9e), Fortran 8e (Final 11e), Chapel 7e (Final 12e)
* Sans A1 : aucun
* Sans A2 : aucun
* Sans A3 : aucun
* Sans A4 : aucun
* Sans A5 : aucun
* Sans A6 : aucun
* Sans A7 : Zig 8e (Final 5e)
* Sans A8 : aucun
* Méthode du 23 novembre : aucun
* C par gcc : aucun
* Final contre la méthode du 23 novembre : aucun
* Final contre la campagne précédente, classement publié : Zig 8e → 5e, D 5e → 8e
* Final contre la campagne précédente recalculée par la méthode de celle-ci : aucun
* Campagne précédente, du classement publié à son recalcul : Zig 8e → 5e

## C par gcc

« C par gcc » : « Final » où toutes les cellules de C viennent de ses constructions par gcc ; la grille et les autres langages ne changent pas.

| C compilé par | Place | Score | Premier | Devance C++ | Plafond | Code naturel | K1 | K3 | K4 | K5 | K6 | K7 | K8 | K9 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| clang (« Final ») | 1 | 83.4 | 59.1 % | 67.5 % | 84.6 | 69.7 | 85 | 99 | 95 | 84 | 81 | 81 | 68 | 87 |
| gcc | 1 | 83.1 | 59.3 % | 73.0 % | 88.1 | 60.7 | 90 | 100 | 86 | 89 | 80 | 75 | 95 | 93 |

## Réplication : cette campagne et la précédente

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

## Plafond par noyau et parts du code par défaut (« Final », au centre)

| Langage | K1 | K3 | K4 | K5 | K6 | K7 | K8 | K9 | D1 | D2 | D3 | D4 | D1, mode publié | D1, R1' |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C | 85 | 99 | 95 | 84 | 81 | 81 | 68 | 87 | 70 | 100 | 80 | 91 | 71 | 66 |
| C++ | 84 | 100 | 69 | 93 | 92 | 74 | 100 | 95 | 48 | 97 | 76 | 90 | 57 | 53 |
| Odin | 67 | 99 | 66 | 94 | 87 | 84 | 73 | 92 | 64 | 99 | 38 | 87 | 65 | 67 |
| Rust | 83 | 100 | 83 | 86 | 84 | 94 | 77 | 88 | 66 | 100 | 74 | 94 | 67 | 62 |
| Zig | 83 | 100 | 69 | 94 | 86 | 74 | 72 | 86 | 38 | 100 | 55 | 89 | 55 | 51 |
| Nim | 92 | 99 | 67 | 90 | 83 | 83 | 68 | 94 | 63 | 99 | 71 | 93 | 65 | 67 |
| C3 | 85 | 100 | 66 | 91 | 87 | 88 | 72 | 90 | 61 | 100 | 55 | 88 | 68 | 64 |
| D | 85 | 100 | 82 | 92 | 79 | 86 | 73 | 90 | 58 | 100 | 2 | 78 | 60 | 57 |
| Ada | 75 | 100 | 76 | 89 | 84 | 70 | 79 | 85 | 37 | 100 | 67 | 69 | 38 | 55 |
| Julia | 75 | 97 | 57 | 93 | 90 | 72 | 73 | 74 | 65 | 98 | 7 | 93 | 66 | 65 |
| Fortran | 84 | 100 | 47 | 86 | 73 | 74 | 92 | 86 | 56 | 99 | 82 | 86 | 65 | 61 |
| Chapel | 74 | 98 | 82 | 90 | 84 | 87 | 88 | 93 | 26 | 99 | 55 | 99 | 57 | 53 |
| Mojo | 82 | 100 | 51 | 86 | 82 | 88 | 49 | 86 | 34 | 99 | 49 | 89 | 34 | 44 |
| Swift | 89 | 98 | 45 | 97 | 81 | 80 | 72 | 91 | 32 | 96 | 32 | 81 | 33 | 42 |
| C# | 82 | 99 | 62 | 84 | 63 | 51 | 51 | 82 | 29 | 56 | 36 | 85 | 29 | 27 |
| Java | 44 | 96 | 49 | 81 | 70 | 64 | 57 | 79 | 34 | 55 | 43 | 94 | 35 | 32 |
| Go | 69 | 37 | 73 | 76 | 54 | 66 | 58 | 78 | 22 | 72 | 11 | 93 | 22 | 23 |
| FreePascal | 49 | 100 | 11 | 38 | 30 | 59 | 53 | 52 | 14 | 99 | 48 | 91 | 20 | 19 |
| Haskell | 46 | 37 | 30 | 86 | 37 | 95 | 71 | 68 | 17 | 75 | 9 | 82 | 17 | 16 |
| OCaml | 28 | 25 | 8 | 14 | 18 | 38 | 42 | 37 | 21 | 42 | 36 | 67 | 21 | 22 |
| BQN | 4 | 3 | 8 | 17 | 13 | 19 | 31 | 8 | 16 | 68 | 10 | 41 | 17 | 16 |
| JavaScript | 17 | 15 | 10 | 8 | 14 | 23 | 21 | 30 | 13 | 27 | 4 | 70 | 13 | 12 |
| PHP | 7 | 2 | 8 | 4 | 8 | 16 | 10 | 10 | 6 | 29 | 11 | 64 | 6 | 6 |
| Python | 0 | 4 | 1 | 0 | 1 | 2 | 1 | 1 | 1 | 21 | 1 | 19 | 1 | 1 |
| Lua | 1 | 5 | 0 | 1 | 1 | 5 | 2 | 1 | 3 | 25 | 0 | 41 | 3 | 3 |

D1 : code naturel sous R1 (le centre) ; « D1, mode publié » : dans le mode publié de chaque chaîne (centre de « Sans R1 ») ; « D1, R1' » : sans les vérifications qu'une option retire (centre de « R1' au lieu de R1 »). Les variantes de « Final » tirent l'un des trois (A7, A8).

## Forme retenue par « Final », cellule par cellule et taille par taille (estimation ponctuelle)

Chaque case : forme retenue aux tailles petite / publiée / grande (« pub » : une variante publiée) ; rapport de son temps à la meilleure forme publiée, à la taille publiée.

| Langage | K4 | K5 | Q6 | Q1 | Q6 mt | Q1 mt | K7 | K8 | K9 | K9 mt |
|---|---|---|---|---|---|---|---|---|---|---|
| C | k4 tuned/k4 tuned/k4 tuned 0.42 | pub/pub/pub 1.00 | q6 tuned_v/q6 tuned_v/q6 tuned_v 0.71 | pub/pub/pub 1.00 | q6 mt_pool_v/q6 mt_pool_v/q6 mt_pool_v 0.74 | q1 mt_pool/pub/q1 mt_pool 1.00 | pub/pub/pub 1.00 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.35 | k9 tuned_v/pub/k9 tuned_v 1.00 | k9 mt_pool/pub/k9 mt_pool_v 1.00 |
| C++ | k4 tuned/k4 tuned/k4 tuned 0.17 | pub/pub/pub 1.00 | pub/q6 tuned_v/pub 0.99 | pub/pub/pub 1.00 | q6 mt_pool/q6 mt_pool/pub 0.90 | q1 mt_pool/q1 mt_pool/pub 0.96 | pub/pub/pub 1.00 | k8 tuned_val/k8 tuned_val/k8 tuned_val 0.33 | k9 tuned_v/k9 tuned_v/k9 tuned_v 1.00 | k9 mt_pool_v/pub/k9 mt_pool_v 1.00 |
| Odin | k4 tuned/k4 tuned/k4 tuned 0.54 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | q1 tuned_v/q1 tuned_v/q1 tuned_v 0.47 | q6 mt_pool/pub/pub 1.00 | q1 mt_pool_v/q1 mt_pool_v/q1 mt_pool_v 0.50 | pub/pub/pub 1.00 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.31 | pub/pub/pub 1.00 | k9 mt_pool/pub/pub 1.00 |
| Rust | k4 tuned/k4 tuned/k4 tuned 0.42 | pub/pub/pub 1.00 | q6 tuned_v/q6 tuned_v/q6 tuned_v 0.85 | pub/pub/pub 1.00 | q6 mt_pool_v/q6 mt_pool_v/q6 mt_pool_v 0.92 | q1 mt_pool/pub/pub 1.00 | pub/pub/pub 1.00 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.27 | k9 tuned_v/pub/pub 1.00 | k9 mt_pool/k9 mt_pool_v/k9 mt_pool_v 0.86 |
| Zig | k4 tuned/k4 tuned/k4 tuned 0.09 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | q6 mt_pool/pub/q6 mt_pool 1.00 | q1 mt_pool/q1 mt_pool/q1 mt_pool 0.96 | pub/pub/pub 1.00 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.44 | pub/pub/pub 1.00 | k9 mt_pool/k9 mt_pool/k9 mt_pool 0.70 |
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
