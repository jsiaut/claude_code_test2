# v4.1, campagne finale : le classement — résultats

*Plans : `docs/V4_FINAL.md` (section 8, fixée avant les mesures) et `docs/V4_1.md` (corrections A1 à A4 de l'analyse, 24 novembre). Généré par `analysis/final_v4.py` à partir de `results/final/raw`, de `results/final/b3.jsonl` et du relevé des formes (`results/converge/forms.json`).*

Machines : 35 ; b3 de référence (le plus lent des 16 décalages, A2) : 75.42 ms ; b3 des groupes de K3 : passe 0 76.12 ms, passe 1 71.95 ms, passe 2 77.53 ms ; avec la médiane des 16 décalages (méthode du 23 novembre) : 65.14 ms.

## Classement « Final »

| Rang | Langage | Score | Score au centre | Rang espéré | Rang plausible | Devance le suivant | Plafond | Code par défaut | Contrôle |
|---|---|---|---|---|---|---|---|---|---|
| 1 | C | 81.4 | 87.1 | 1.40 | 1–3 | 75 % | 89.6 | 76.6 | 91.7 |
| 2 | C++ | 79.2 | 85.3 | 2.56 | 1–6 | 79 % | 90.1 | 67.8 | 92.4 |
| 3 | Odin | 76.4 | 80.7 | 4.32 | 2–8 | 53 % | 83.7 | 71.1 | 84.0 |
| 4 | Rust | 75.9 | 80.5 | 4.69 | 2–9 | 59 % | 88.3 | 77.6 | 73.6 |
| 5 | D | 74.8 | 80.9 | 5.78 | 3–10 | 52 % | 87.0 | 62.3 | 87.1 |
| 6 | Nim | 74.6 | 79.5 | 5.90 | 3–9 | 58 % | 85.9 | 73.8 | 76.1 |
| 7 | C3 | 74.2 | 78.9 | 6.28 | 3–9 | 62 % | 86.8 | 70.5 | 75.7 |
| 8 | Zig | 73.0 | 78.6 | 7.18 | 3–11 | 79 % | 84.4 | 57.0 | 87.2 |
| 9 | Ada | 71.0 | 76.8 | 8.85 | 5–11 | 66 % | 83.7 | 60.2 | 80.6 |
| 10 | Julia | 69.6 | 74.0 | 9.90 | 6–13 | 67 % | 78.4 | 67.7 | 73.3 |
| 11 | Fortran | 68.1 | 72.2 | 10.91 | 7–14 | 66 % | 79.1 | 71.1 | 65.3 |
| 12 | Chapel | 66.0 | 71.0 | 11.96 | 8–15 | 59 % | 89.9 | 53.7 | 61.8 |
| 13 | Swift | 65.2 | 69.3 | 12.60 | 10–14 | 61 % | 80.6 | 52.8 | 68.1 |
| 14 | Mojo | 64.5 | 68.8 | 13.00 | 11–15 | 93 % | 76.0 | 54.8 | 70.5 |
| 15 | C# | 59.3 | 64.2 | 14.88 | 13–16 | 93 % | 71.2 | 46.5 | 68.8 |
| 16 | Java | 51.2 | 54.8 | 16.75 | 15–18 | 56 % | 66.0 | 53.8 | 42.7 |
| 17 | Go | 50.6 | 53.6 | 16.97 | 16–18 | 58 % | 62.6 | 46.0 | 48.7 |
| 18 | FreePascal | 49.3 | 51.1 | 17.24 | 15–19 | 88 % | 43.0 | 48.5 | 62.3 |
| 19 | Haskell | 43.0 | 45.1 | 18.85 | 18–19 | 100 % | 52.3 | 38.5 | 41.5 |
| 20 | OCaml | 26.7 | 26.9 | 20.16 | 20–21 | 92 % | 22.7 | 38.7 | 23.2 |
| 21 | BQN | 19.9 | 18.3 | 21.75 | 20–23 | 47 % | 10.1 | 29.5 | 19.7 |
| 22 | JavaScript | 19.9 | 19.1 | 21.84 | 21–24 | 70 % | 15.6 | 31.1 | 14.6 |
| 23 | PHP | 18.0 | 17.5 | 22.43 | 21–23 | 97 % | 6.6 | 21.1 | 27.4 |
| 24 | Python | 10.5 | 12.8 | 24.05 | 22–25 | 76 % | 1.0 | 8.0 | 29.7 |
| 25 | Lua | 7.1 | 6.2 | 24.76 | 24–25 | — | 1.4 | 13.0 | 6.8 |

Score : moyenne du score sur les variantes de l'analyse ; il fixe l'ordre. Score au centre, plafond, code par défaut et contrôle : poids et choix principaux, estimation ponctuelle. Rang espéré : rang moyen sur les variantes.

Étages (paires ordonnées dans au moins 95 % des variantes) : C, C++, Odin, Rust, D, Nim, C3, Zig, Ada, Julia, Fortran, Chapel, Swift, Mojo, C#, Java, Go, FreePascal, Haskell | OCaml, BQN, JavaScript, PHP, Python, Lua

## Tous les calculs

| Langage | Final | Base, trois tailles | Sans les tailles (taille publiée seule) | Sans R1 | Sans R2 | Sans C1 | Sans R4 | R1' au lieu de R1 | Taille petite | Taille grande | Sélection indépendante | D3 et D4 sur trois processus | Sur les seules mesures | Sans A1 | Sans A2 | Sans A3 | Sans A4 | Méthode du 23 novembre | v3 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C | 1 | 1 | 1 | 1 | 1 | 1 | 2 | 1 | 1 | 2 | 1 | 1 | 2 | 1 | 1 | 1 | 1 | 2 | 1 |
| C++ | 2 | 2 | 2 | 2 | 2 | 3 | 1 | 2 | 2 | 1 | 2 | 2 | 4 | 2 | 2 | 2 | 2 | 1 | 3 |
| Odin | 3 | 5 | 3 | 4 | 3 | 2 | 5 | 3 | 3 | 3 | 3 | 3 | 6 ** | 3 | 3 | 3 | 3 | 3 | 2 |
| Rust | 4 | 6 | 4 | 5 | 4 | 4 | 6 | 6 | 4 | 4 | 4 | 4 | 1 ** | 4 | 4 | 4 | 4 | 4 | 6 |
| D | 5 | 4 | 6 | 7 | 7 | 6 | 3 | 7 | 6 | 6 | 5 | 5 | 7 | 7 | 5 | 5 | 5 | 7 | 8 |
| Nim | 6 | 8 | 7 | 8 | 5 | 7 | 7 | 5 | 5 | 5 | 6 | 6 | 3 ** | 6 | 6 | 6 | 6 | 6 | 7 |
| C3 | 7 | 3 ** | 5 | 6 | 6 | 5 | 4 ** | 8 | 7 | 7 | 7 | 7 | 5 | 5 | 7 | 7 | 7 | 5 | 4 |
| Zig | 8 | 7 | 8 | 3 ** | 8 | 8 | 9 | 4 ** | 9 | 8 | 8 | 8 | 11 ** | 8 | 8 | 8 | 8 | 8 | 5 |
| Ada | 9 | 9 | 9 | 9 | 9 | 9 | 8 | 9 | 12 ** | 9 | 9 | 9 | 12 ** | 9 | 9 | 9 | 9 | 9 | 9 |
| Julia | 10 | 12 | 11 | 12 | 10 | 11 | 10 | 11 | 10 | 10 | 10 | 10 | 9 | 10 | 10 | 10 | 10 | 12 | 13 |
| Fortran | 11 | 11 | 10 | 11 | 11 | 10 | 11 | 12 | 8 ** | 11 | 11 | 11 | 8 ** | 11 | 11 | 11 | 11 | 11 | 11 |
| Chapel | 12 | 10 | 12 | 10 | 12 | 13 | 13 | 10 | 11 | 14 | 12 | 12 | 10 | 12 | 12 | 12 | 12 | 10 | 10 |
| Swift | 13 | 14 | 13 | 13 | 13 | 12 | 14 | 13 | 13 | 13 | 13 | 13 | 13 | 13 | 13 | 13 | 13 | 13 | 12 |
| Mojo | 14 | 13 | 14 | 14 | 14 | 14 | 12 | 14 | 14 | 12 | 14 | 14 | 14 | 14 | 14 | 14 | 14 | 14 | 14 |
| C# | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 16 | 15 | 15 | 15 | 15 | 15 | 15 |
| Java | 16 | 17 | 16 | 16 | 16 | 16 | 17 | 16 | 18 | 16 | 16 | 16 | 15 | 16 | 16 | 17 | 17 | 18 | 17 |
| Go | 17 | 18 | 17 | 17 | 17 | 18 | 18 | 17 | 16 | 18 | 17 | 17 | 17 | 17 | 17 | 16 | 16 | 16 | 18 |
| FreePascal | 18 | 16 | 18 | 18 | 18 | 17 | 16 | 18 | 17 | 17 | 18 | 18 | 18 | 18 | 18 | 18 | 18 | 17 | 16 |
| Haskell | 19 | 19 | 19 | 19 | 19 | 19 | 19 | 19 | 19 | 19 | 19 | 19 | 19 | 19 | 19 | 19 | 19 | 19 | 19 |
| OCaml | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 |
| BQN | 21 | 21 | 21 | 21 | 22 | 21 | 21 | 22 | 21 | 22 | 21 | 22 | 22 | 21 | 21 | 22 | 21 | 21 | 21 |
| JavaScript | 22 | 22 | 22 | 22 | 21 | 22 | 22 | 21 | 22 | 21 | 22 | 21 | 21 | 22 | 22 | 21 | 22 | 22 | 23 |
| PHP | 23 | 23 | 23 | 23 | 23 | 23 | 23 | 23 | 23 | 23 | 23 | 23 | 23 | 23 | 23 | 23 | 23 | 23 | 22 |
| Python | 24 | 24 | 24 | 24 | 24 | 24 | 24 | 24 | 24 | 24 | 24 | 24 | 25 | 24 | 24 | 24 | 24 | 24 | 24 |
| Lua | 25 | 25 | 25 | 25 | 25 | 25 | 25 | 25 | 25 | 25 | 25 | 25 | 24 | 25 | 25 | 25 | 25 | 25 | 25 |

Chaque case : place dans le calcul ; ** : plus de deux places d'écart avec « Final ». Ordre des lignes : « Final ». « Sans A1 » à « Sans A4 » : « Final » sans une correction de la v4.1 ; « Méthode du 23 novembre » : sans aucune et classée au rang moyen, le classement publié le 23 novembre ; v3 : le classement publié jusqu'au 23 novembre.

## Rangs qui bougent de plus de deux places par rapport à « Final »

* Base, trois tailles : C3 3e (Final 7e)
* Sans les tailles (taille publiée seule) : aucun
* Sans R1 : Zig 3e (Final 8e)
* Sans R2 : aucun
* Sans C1 : aucun
* Sans R4 : C3 4e (Final 7e)
* R1' au lieu de R1 : Zig 4e (Final 8e)
* Taille petite : Ada 12e (Final 9e), Fortran 8e (Final 11e)
* Taille grande : aucun
* Sélection indépendante : aucun
* D3 et D4 sur trois processus : aucun
* Sur les seules mesures : Odin 6e (Final 3e), Rust 1er (Final 4e), Nim 3e (Final 6e), Zig 11e (Final 8e), Ada 12e (Final 9e), Fortran 8e (Final 11e)
* Sans A1 : aucun
* Sans A2 : aucun
* Sans A3 : aucun
* Sans A4 : aucun
* Méthode du 23 novembre : aucun
* Final contre la méthode du 23 novembre : aucun
* Final contre le classement de la v3 : D 8e → 5e, C3 4e → 7e, Zig 5e → 8e, Julia 13e → 10e

## Plafond par noyau et parts du code par défaut (« Final », au centre)

| Langage | K1 | K3 | K4 | K5 | K6 | K7 | K8 | K9 | D1 | D2 | D3 | D4 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C | 91 | 100 | 98 | 94 | 89 | 97 | 66 | 88 | 70 | 98 | 53 | 96 |
| C++ | 93 | 100 | 79 | 92 | 90 | 80 | 100 | 89 | 49 | 100 | 63 | 95 |
| Odin | 81 | 95 | 70 | 93 | 92 | 89 | 67 | 87 | 62 | 99 | 38 | 96 |
| Rust | 89 | 94 | 90 | 93 | 88 | 95 | 73 | 87 | 66 | 100 | 68 | 97 |
| D | 92 | 100 | 88 | 92 | 85 | 92 | 65 | 86 | 57 | 97 | 2 | 96 |
| Nim | 98 | 100 | 78 | 90 | 82 | 95 | 61 | 90 | 63 | 100 | 52 | 97 |
| C3 | 85 | 100 | 76 | 91 | 93 | 96 | 68 | 90 | 60 | 100 | 41 | 96 |
| Zig | 91 | 95 | 75 | 91 | 94 | 83 | 70 | 81 | 37 | 93 | 37 | 96 |
| Ada | 87 | 100 | 77 | 86 | 89 | 76 | 78 | 79 | 37 | 100 | 70 | 82 |
| Julia | 77 | 93 | 62 | 95 | 91 | 76 | 72 | 69 | 64 | 98 | 10 | 97 |
| Fortran | 89 | 98 | 50 | 85 | 75 | 77 | 86 | 83 | 56 | 99 | 73 | 88 |
| Chapel | 87 | 96 | 90 | 89 | 86 | 94 | 80 | 98 | 26 | 99 | 42 | 97 |
| Swift | 85 | 96 | 46 | 97 | 85 | 92 | 70 | 90 | 31 | 93 | 27 | 96 |
| Mojo | 82 | 100 | 50 | 92 | 89 | 95 | 46 | 77 | 33 | 100 | 38 | 89 |
| C# | 88 | 96 | 73 | 91 | 59 | 54 | 50 | 73 | 28 | 58 | 40 | 88 |
| Java | 45 | 92 | 54 | 84 | 76 | 70 | 51 | 71 | 33 | 58 | 59 | 98 |
| Go | 74 | 35 | 82 | 73 | 52 | 70 | 53 | 78 | 19 | 100 | 15 | 96 |
| FreePascal | 50 | 100 | 14 | 39 | 28 | 68 | 49 | 46 | 14 | 98 | 52 | 96 |
| Haskell | 48 | 35 | 34 | 91 | 33 | 90 | 69 | 51 | 16 | 76 | 9 | 89 |
| OCaml | 30 | 24 | 10 | 12 | 16 | 39 | 41 | 32 | 21 | 44 | 46 | 74 |
| BQN | 4 | 3 | 10 | 16 | 12 | 21 | 28 | 8 | 17 | 71 | 9 | 45 |
| JavaScript | 17 | 16 | 10 | 8 | 13 | 25 | 20 | 29 | 13 | 27 | 6 | 98 |
| PHP | 7 | 2 | 8 | 4 | 7 | 17 | 9 | 9 | 6 | 29 | 12 | 61 |
| Python | 0 | 4 | 1 | 0 | 1 | 2 | 1 | 1 | 1 | 21 | 1 | 20 |
| Lua | 1 | 4 | 0 | 1 | 1 | 6 | 2 | 1 | 3 | 24 | 1 | 39 |

## Forme retenue par « Final », cellule par cellule et taille par taille (estimation ponctuelle)

Chaque case : forme retenue aux tailles petite / publiée / grande (« pub » : une variante publiée) ; rapport de son temps à la meilleure forme publiée, à la taille publiée.

| Langage | K4 | K5 | Q6 | Q1 | Q6 mt | Q1 mt | K7 | K8 | K9 | K9 mt |
|---|---|---|---|---|---|---|---|---|---|---|
| C | k4 tuned/k4 tuned/k4 tuned 0.35 | pub/pub/pub 1.00 | q6 tuned_v/q6 tuned_v/q6 tuned_v 0.78 | pub/pub/pub 1.00 | q6 mt_pool/q6 mt_pool_v/q6 mt_pool_v 0.72 | q1 mt_pool/pub/pub 1.00 | pub/pub/pub 1.00 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.37 | k9 tuned_v/pub/k9 tuned_v 1.00 | k9 mt_pool/pub/k9 mt_pool_v 1.00 |
| C++ | k4 tuned/k4 tuned/k4 tuned 0.14 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | q6 mt_pool/q6 mt_pool/q6 mt_pool 0.86 | q1 mt_pool/pub/q1 mt_pool 1.00 | pub/pub/pub 1.00 | k8 tuned_val/k8 tuned_val/k8 tuned_val 0.31 | k9 tuned_v/k9 tuned_v/k9 tuned_v 0.87 | k9 mt_pool/k9 mt_pool_v/k9 mt_pool_v 0.81 |
| Odin | k4 tuned/k4 tuned/k4 tuned 0.49 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | q1 tuned_v/q1 tuned_v/q1 tuned_v 0.56 | q6 mt_pool/q6 mt_pool/pub 0.79 | q1 mt_pool_v/q1 mt_pool_v/q1 mt_pool_v 0.53 | pub/pub/pub 1.00 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.32 | pub/pub/pub 1.00 | k9 mt_pool/pub/k9 mt_pool 1.00 |
| Rust | k4 tuned/k4 tuned/k4 tuned 0.39 | pub/pub/pub 1.00 | q6 tuned_v/q6 tuned_v/q6 tuned_v 0.82 | pub/pub/pub 1.00 | q6 mt_pool/q6 mt_pool_v/q6 mt_pool_v 0.88 | q1 mt_pool/pub/pub 1.00 | pub/pub/pub 1.00 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.28 | k9 tuned_v/pub/k9 tuned_v 1.00 | k9 mt_pool/k9 mt_pool/k9 mt_pool_v 0.95 |
| D | k4 tuned/k4 tuned/k4 tuned 0.40 | pub/pub/pub 1.00 | q6 tuned_v/q6 tuned_v/q6 tuned_v 0.79 | pub/pub/pub 1.00 | q6 mt_pool/q6 mt_pool_v/q6 mt_pool_v 0.53 | q1 mt_pool/q1 mt_pool/q1 mt_pool 0.94 | pub/pub/pub 1.00 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.35 | pub/pub/pub 1.00 | k9 mt_pool/k9 mt_pool/k9 mt_pool 0.94 |
| Nim | k4 tuned/k4 tuned/k4 tuned 0.46 | pub/pub/pub 1.00 | q6 tuned_v/q6 tuned_v/q6 tuned_v 0.83 | q1 tuned_v/q1 tuned_v/q1 tuned_v 0.56 | q6 mt_pool_v/q6 mt_pool_v/q6 mt_pool_v 0.74 | q1 mt_pool_v/q1 mt_pool_v/q1 mt_pool_v 0.45 | pub/pub/pub 1.00 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.29 | k9 tuned_v/pub/k9 tuned_v 1.00 | k9 mt_pool/k9 mt_pool/k9 mt_pool_v 0.96 |
| C3 | k4 tuned/k4 tuned/k4 tuned 0.45 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | q1 tuned_v/pub/pub 1.00 | q6 mt_pool/q6 mt_pool/pub 0.82 | q1 mt_pool_v/q1 mt_pool_v/pub 0.89 | pub/pub/pub 1.00 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.35 | pub/pub/pub 1.00 | k9 mt_pool/k9 mt_pool/k9 mt_pool 0.84 |
| Zig | k4 tuned/k4 tuned/k4 tuned 0.11 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | q6 mt_pool/q6 mt_pool/q6 mt_pool 0.75 | q1 mt_pool/q1 mt_pool/q1 mt_pool 0.87 | pub/pub/pub 1.00 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.41 | pub/pub/pub 1.00 | k9 mt_pool/k9 mt_pool/k9 mt_pool 0.63 |
| Ada | k4 tuned/k4 tuned/k4 tuned 0.15 | pub/pub/pub 1.00 | q6 tuned_v/q6 tuned_v/q6 tuned_v 0.91 | q1 tuned_v/q1 tuned_v/q1 tuned_v 0.67 | q6 mt_pool/q6 mt_pool_v/q6 mt_pool_v 0.42 | q1 mt_pool_v/q1 mt_pool_v/q1 mt_pool_v 0.41 | pub/pub/pub 1.00 | k8 tuned_it/pub/pub 1.00 | pub/pub/pub 1.00 | k9 mt_pool/k9 mt_pool/k9 mt_pool 0.53 |
| Julia | k4 tuned/k4 tuned/k4 tuned 0.54 | k5 tuned_v/k5 tuned_v/k5 tuned_v 0.77 | q6 tuned_v/q6 tuned_v/q6 tuned_v 0.83 | q1 tuned_v/q1 tuned_v/q1 tuned_v 0.36 | q6 mt_pool_v/q6 mt_pool_v/q6 mt_pool_v 0.69 | q1 mt_pool_v/q1 mt_pool_v/q1 mt_pool_v 0.30 | k7 tuned_pf/k7 tuned_pf/k7 tuned_pf 0.97 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.25 | k9 tuned_v/k9 tuned_v/k9 tuned_v 0.90 | pub/k9 mt_pool_v/k9 mt_pool_v 0.99 |
| Fortran | k4 swar/k4 swar/k4 swar 0.20 | k5 rq_acc16/k5 rq_acc16/pub 0.96 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/k7 tuned_oa/pub 0.86 | k8 tuned_val/k8 tuned_val/k8 tuned_val 0.41 | pub/pub/pub 1.00 | pub/pub/pub 1.00 |
| Chapel | k4 tuned/k4 tuned/k4 tuned 0.58 | pub/pub/k5 tuned_v 1.00 | pub/q6 tuned_v/q6 tuned_v 0.95 | pub/q1 tuned_v/q1 tuned_v 0.92 | pub/pub/q6 mt_pool_v 1.00 | q1 mt_pool_v/q1 mt_pool_v/q1 mt_pool_v 0.71 | pub/pub/pub 1.00 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.25 | pub/k9 tuned_v/pub 0.93 | k9 mt_pool_v/k9 mt_pool_v/pub 0.98 |
| Swift | k4 tuned/k4 tuned/k4 tuned 0.71 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | q6 mt_pool/q6 mt_pool/pub 0.89 | q1 mt_pool/q1 mt_pool/q1 mt_pool 0.88 | pub/pub/pub 1.00 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.32 | pub/pub/pub 1.00 | k9 mt_pool/k9 mt_pool/k9 mt_pool 0.85 |
| Mojo | k4 tuned/k4 tuned/k4 tuned 0.12 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | q1 tuned_v/q1 tuned_v/q1 tuned_v 0.76 | pub/pub/pub 1.00 | q1 mt_pool_v/q1 mt_pool_v/q1 mt_pool_v 0.77 | pub/pub/pub 1.00 | k8 tuned_val/k8 tuned_val/k8 tuned_val 0.75 | pub/pub/pub 1.00 | pub/pub/pub 1.00 |
| C# | k4 tuned/k4 tuned/k4 tuned 0.05 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | q6 mt_pool/q6 mt_pool/q6 mt_pool 0.67 | q1 mt_pool/pub/q1 mt_pool 1.00 | pub/pub/pub 1.00 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.47 | pub/pub/pub 1.00 | k9 mt_pool/k9 mt_pool/pub 0.63 |
| Java | k4 tuned/k4 tuned/k4 tuned 0.23 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | q1 tuned_v/q1 tuned_v/q1 tuned_v 0.46 | q6 mt_pool/q6 mt_pool/q6 mt_pool 0.81 | q1 mt_pool_v/q1 mt_pool_v/q1 mt_pool_v 0.43 | k7 rq_iso/k7 rq_iso/k7 rq_iso 0.87 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.63 | pub/pub/k9 tuned_v 1.00 | k9 mt_pool/k9 mt_pool_v/k9 mt_pool_v 0.74 |
| Go | k4 tuned/k4 tuned/k4 tuned 0.07 | k5 tuned_v/pub/k5 tuned_v 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.51 | k9 tuned_v/k9 tuned_v/k9 tuned_v 0.53 | k9 mt_pool_v/k9 mt_pool_v/k9 mt_pool_v 0.64 |
| FreePascal | k4 swar/k4 swar/k4 swar 0.24 | k5 tuned_v/k5 tuned_v/k5 tuned_v 0.81 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | q6 mt_pool/pub/pub 1.00 | q1 mt_pool/pub/pub 1.00 | pub/pub/pub 1.00 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.39 | pub/pub/pub 1.00 | k9 mt_pool/k9 mt_pool/k9 mt_pool 0.87 |
| Haskell | k4 tuned/k4 tuned/k4 tuned 0.20 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.38 | pub/pub/pub 1.00 | pub/pub/pub 1.00 |
| OCaml | k4 tuned/k4 tuned/k4 swar 0.24 | pub/pub/pub 1.00 | q6 tuned_s/q6 tuned_s/q6 tuned_s 0.77 | pub/pub/pub 1.00 | q6 mt_pool_s/q6 mt_pool_s/q6 mt_pool_s 0.73 | q1 mt_pool/q1 mt_pool/q1 mt_pool 1.00 | k7 tuned_oa/k7 tuned_oa/k7 tuned_oa 0.88 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.71 | pub/pub/pub 1.00 | k9 mt_pool/k9 mt_pool/k9 mt_pool 0.67 |
| BQN | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 |
| JavaScript | k4 swar/k4 swar/k4 swar 0.38 | k5 rq_f64/k5 rq_f64/pub 0.89 | q6 tuned_s/q6 tuned_s/q6 tuned_s 0.55 | pub/pub/pub 1.00 | q6 mt_pool_s/q6 mt_pool_s/q6 mt_pool_s 0.55 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.63 | pub/k9 rq_slide/k9 rq_slide 0.93 | k9 rq_slide_mt/k9 rq_slide_mt/k9 rq_slide_mt 0.72 |
| PHP | k4 tuned/k4 tuned/k4 tuned 0.06 | pub/pub/pub 1.00 | q6 tuned_s/q6 tuned_s/q6 tuned_s 0.75 | pub/pub/pub 1.00 | q6 mt_pool_s/q6 mt_pool_s/q6 mt_pool_s 0.77 | pub/pub/pub 1.00 | k7 tuned_oa/k7 tuned_oa/pub 0.94 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 |
| Python | k4 tuned/k4 tuned/k4 tuned 0.13 | pub/pub/pub 1.00 | k6 rq_cols/k6 rq_cols/k6 rq_cols 0.54 | pub/pub/pub 1.00 | k6 rq_cols_mt/k6 rq_cols_mt/k6 rq_cols_mt 0.33 | q1 mt_pool/pub/q1 mt_pool 1.00 | pub/k7 tuned_oa/k7 tuned_oa 0.52 | k8 tuned_val/k8 tuned_val/k8 tuned_val 0.60 | pub/pub/pub 1.00 | k9 mt_pool/k9 mt_pool/k9 mt_pool 0.98 |
| Lua | k4 swar/k4 swar/k4 swar 0.84 | pub/pub/pub 1.00 | k6 rq_nest/k6 rq_nest/k6 rq_nest 0.94 | pub/pub/pub 1.00 | k6 rq_nest_mt/k6 rq_nest_mt/k6 rq_nest_mt 0.55 | pub/pub/pub 1.00 | k7 tuned_oa/k7 rq_pack/k7 rq_pack 0.55 | k8 tuned_val/k8 tuned_val/k8 tuned_val 0.92 | k9 rq_slide/pub/k9 rq_slide 1.00 | k9 rq_slide_mt/k9 rq_slide_mt/k9 rq_slide_mt 0.95 |

## Campagne

Écart entre la passe la plus lente et la plus rapide d'une cellule : médiane 8.2 % ; 576 cellules sur 2972 au-delà de 20 %.

Machine de chaque groupe et de chaque passe :

* machine 35 : 69 groupes

## Cellules

* Final : formes ou cellules substituées manquantes : aucune ; cellules de la base remplies (temps le plus lent des autres langages) : BQN k1 aos energy (grande), Python k1 natural energy (grande), BQN k1 natural energy (grande), Python k1 natural_shuffled energy (grande), BQN k1 natural_shuffled energy (grande), BQN k1 soa energy (grande)
* Base, trois tailles : formes ou cellules substituées manquantes : aucune ; cellules de la base remplies (temps le plus lent des autres langages) : BQN k1 aos energy (grande), Python k1 natural energy (grande), BQN k1 natural energy (grande), Python k1 natural_shuffled energy (grande), BQN k1 natural_shuffled energy (grande), BQN k1 soa energy (grande)
* Sans les tailles (taille publiée seule) : formes ou cellules substituées manquantes : aucune ; cellules de la base remplies (temps le plus lent des autres langages) : BQN k1 aos energy (grande), Python k1 natural energy (grande), BQN k1 natural energy (grande), Python k1 natural_shuffled energy (grande), BQN k1 natural_shuffled energy (grande), BQN k1 soa energy (grande)
* Sans R1 : formes ou cellules substituées manquantes : aucune ; cellules de la base remplies (temps le plus lent des autres langages) : BQN k1 aos energy (grande), Python k1 natural energy (grande), BQN k1 natural energy (grande), Python k1 natural_shuffled energy (grande), BQN k1 natural_shuffled energy (grande), BQN k1 soa energy (grande)
* Sans R2 : formes ou cellules substituées manquantes : aucune ; cellules de la base remplies (temps le plus lent des autres langages) : BQN k1 aos energy (grande), Python k1 natural energy (grande), BQN k1 natural energy (grande), Python k1 natural_shuffled energy (grande), BQN k1 natural_shuffled energy (grande), BQN k1 soa energy (grande)
* Sans C1 : formes ou cellules substituées manquantes : aucune ; cellules de la base remplies (temps le plus lent des autres langages) : BQN k1 aos energy (grande), Python k1 natural energy (grande), BQN k1 natural energy (grande), Python k1 natural_shuffled energy (grande), BQN k1 natural_shuffled energy (grande), BQN k1 soa energy (grande)
* Sans R4 : formes ou cellules substituées manquantes : aucune ; cellules de la base remplies (temps le plus lent des autres langages) : BQN k1 aos energy (grande), Python k1 natural energy (grande), BQN k1 natural energy (grande), Python k1 natural_shuffled energy (grande), BQN k1 natural_shuffled energy (grande), BQN k1 soa energy (grande)
* R1' au lieu de R1 : formes ou cellules substituées manquantes : aucune ; cellules de la base remplies (temps le plus lent des autres langages) : BQN k1 aos energy (grande), Python k1 natural energy (grande), BQN k1 natural energy (grande), Python k1 natural_shuffled energy (grande), BQN k1 natural_shuffled energy (grande), BQN k1 soa energy (grande)
* Taille petite : formes ou cellules substituées manquantes : aucune ; cellules de la base remplies (temps le plus lent des autres langages) : BQN k1 aos energy (grande), Python k1 natural energy (grande), BQN k1 natural energy (grande), Python k1 natural_shuffled energy (grande), BQN k1 natural_shuffled energy (grande), BQN k1 soa energy (grande)
* Taille grande : formes ou cellules substituées manquantes : aucune ; cellules de la base remplies (temps le plus lent des autres langages) : BQN k1 aos energy (grande), Python k1 natural energy (grande), BQN k1 natural energy (grande), Python k1 natural_shuffled energy (grande), BQN k1 natural_shuffled energy (grande), BQN k1 soa energy (grande)
* Sélection indépendante : formes ou cellules substituées manquantes : aucune ; cellules de la base remplies (temps le plus lent des autres langages) : BQN k1 aos energy (grande), Python k1 natural energy (grande), BQN k1 natural energy (grande), Python k1 natural_shuffled energy (grande), BQN k1 natural_shuffled energy (grande), BQN k1 soa energy (grande)
* D3 et D4 sur trois processus : formes ou cellules substituées manquantes : aucune ; cellules de la base remplies (temps le plus lent des autres langages) : BQN k1 aos energy (grande), Python k1 natural energy (grande), BQN k1 natural energy (grande), Python k1 natural_shuffled energy (grande), BQN k1 natural_shuffled energy (grande), BQN k1 soa energy (grande)
* Sur les seules mesures : formes ou cellules substituées manquantes : aucune ; cellules de la base remplies (temps le plus lent des autres langages) : BQN k1 aos energy (grande), Python k1 natural energy (grande), BQN k1 natural energy (grande), Python k1 natural_shuffled energy (grande), BQN k1 natural_shuffled energy (grande), BQN k1 soa energy (grande)
* Sans A1 : formes ou cellules substituées manquantes : aucune ; cellules de la base remplies (temps le plus lent des autres langages) : BQN k1 aos energy (grande), Python k1 natural energy (grande), BQN k1 natural energy (grande), Python k1 natural_shuffled energy (grande), BQN k1 natural_shuffled energy (grande), BQN k1 soa energy (grande)
* Sans A2 : formes ou cellules substituées manquantes : aucune ; cellules de la base remplies (temps le plus lent des autres langages) : BQN k1 aos energy (grande), Python k1 natural energy (grande), BQN k1 natural energy (grande), Python k1 natural_shuffled energy (grande), BQN k1 natural_shuffled energy (grande), BQN k1 soa energy (grande)
* Sans A3 : formes ou cellules substituées manquantes : aucune ; cellules de la base remplies (temps le plus lent des autres langages) : BQN k1 aos energy (grande), Python k1 natural energy (grande), BQN k1 natural energy (grande), Python k1 natural_shuffled energy (grande), BQN k1 natural_shuffled energy (grande), BQN k1 soa energy (grande)
* Sans A4 : formes ou cellules substituées manquantes : aucune ; cellules de la base remplies (temps le plus lent des autres langages) : BQN k1 aos energy (grande), Python k1 natural energy (grande), BQN k1 natural energy (grande), Python k1 natural_shuffled energy (grande), BQN k1 natural_shuffled energy (grande), BQN k1 soa energy (grande)
* Méthode du 23 novembre : formes ou cellules substituées manquantes : aucune ; cellules de la base remplies (temps le plus lent des autres langages) : BQN k1 aos energy (grande), Python k1 natural energy (grande), BQN k1 natural energy (grande), Python k1 natural_shuffled energy (grande), BQN k1 natural_shuffled energy (grande), BQN k1 soa energy (grande)

Processeur des enregistrements : 6/207/2 Intel(R) Xeon(R) Processor @ 2.10GHz (9738 enregistrements).

Processus écartés : 0 ; cellules non exécutées (étalonnage hors mémoire ou hors durée) : 18 ; vol de temps > 5 % après reprise : 0.
* non exécutée : BQN pub large k1 aos energy (oom)
* non exécutée : BQN pub large k1 natural energy (oom)
* non exécutée : BQN pub large k1 natural_shuffled energy (oom)
* non exécutée : BQN pub large k1 soa energy (oom)
* non exécutée : Python pub large k1 natural energy (oom)
* non exécutée : Python pub large k1 natural_shuffled energy (oom)
