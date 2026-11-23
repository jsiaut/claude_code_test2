# v4, campagne finale : le classement de la v4 — résultats

*Plan : `docs/V4_FINAL.md` (section 8, fixée avant les mesures). Généré par `analysis/final_v4.py` à partir de `results/final/raw`, de `results/final/b3.jsonl` et du relevé des formes (`results/converge/forms.json`).*

Machines : 35 ; b3 de référence : 65.14 ms ; b3 des groupes de K3 : passe 0 68.09 ms, passe 1 63.05 ms, passe 2 63.20 ms.

## Classement « Final »

| Rang | Langage | Score | Rang espéré | Rang plausible | Devance le suivant | Plafond | Code par défaut | Contrôle |
|---|---|---|---|---|---|---|---|---|
| 1 | C++ | 78.9 | 2.53 | 1–6 | 51 % | 85.0 | 50.4 | 92.4 |
| 2 | C | 78.3 | 2.59 | 1–7 | 73 % | 83.1 | 51.8 | 91.7 |
| 3 | Odin | 72.7 | 4.17 | 1–8 | 58 % | 77.6 | 48.9 | 84.0 |
| 4 | Rust | 71.5 | 4.95 | 1–9 | 59 % | 80.5 | 54.1 | 73.6 |
| 5 | C3 | 71.1 | 5.41 | 2–9 | 61 % | 80.9 | 49.0 | 75.7 |
| 6 | Nim | 71.0 | 6.35 | 3–10 | 52 % | 79.0 | 51.2 | 76.1 |
| 7 | D | 73.5 | 6.62 | 3–12 | 58 % | 81.1 | 42.1 | 87.1 |
| 8 | Zig | 72.2 | 7.08 | 2–11 | 76 % | 76.8 | 44.0 | 87.2 |
| 9 | Ada | 71.4 | 8.99 | 5–12 | 65 % | 78.4 | 47.1 | 80.6 |
| 10 | Chapel | 67.7 | 10.02 | 3–14 | 54 % | 87.5 | 44.4 | 61.8 |
| 11 | Fortran | 67.0 | 10.54 | 6–14 | 49 % | 78.2 | 51.3 | 65.3 |
| 12 | Julia | 66.6 | 10.58 | 6–14 | 78 % | 74.4 | 44.8 | 73.3 |
| 13 | Swift | 64.4 | 12.73 | 10–14 | 53 % | 75.4 | 41.6 | 68.1 |
| 14 | Mojo | 64.7 | 12.83 | 10–15 | 91 % | 73.0 | 43.2 | 70.5 |
| 15 | C# | 60.2 | 14.89 | 13–16 | 97 % | 67.5 | 36.4 | 68.8 |
| 16 | Go | 50.5 | 16.95 | 16–18 | 50 % | 59.1 | 39.2 | 48.7 |
| 17 | FreePascal | 49.4 | 16.97 | 15–19 | 47 % | 41.6 | 43.6 | 62.3 |
| 18 | Java | 49.4 | 16.98 | 16–18 | 95 % | 60.0 | 41.8 | 42.7 |
| 19 | Haskell | 42.6 | 18.84 | 18–19 | 100 % | 49.6 | 32.8 | 41.5 |
| 20 | OCaml | 24.5 | 20.21 | 20–22 | 89 % | 21.4 | 31.3 | 23.2 |
| 21 | BQN | 17.0 | 21.61 | 20–23 | 54 % | 10.5 | 23.4 | 19.7 |
| 22 | JavaScript | 17.6 | 21.94 | 21–24 | 68 % | 14.6 | 26.4 | 14.6 |
| 23 | PHP | 16.9 | 22.42 | 21–23 | 97 % | 6.3 | 19.1 | 27.4 |
| 24 | Python | 12.7 | 24.05 | 22–25 | 76 % | 1.0 | 7.6 | 29.7 |
| 25 | Lua | 5.9 | 24.76 | 24–25 | — | 1.4 | 12.0 | 6.8 |

Étages (paires ordonnées dans au moins 95 % des variantes) : C++, C, Odin, Rust, C3, Nim, D, Zig, Ada, Chapel, Fortran, Julia, Swift, Mojo, C#, Go, FreePascal, Java, Haskell | OCaml, BQN, JavaScript, PHP, Python, Lua

## Tous les calculs

| Langage | Final | Base, trois tailles | Sans les tailles (taille publiée seule) | Sans R1 | Sans R2 | Sans C1 | Sans R4 | R1' au lieu de R1 | Taille petite | Taille grande | Sélection indépendante | D3 et D4 sur trois processus | Sur les seules mesures | Publié | Point 4 (R4) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C++ | 1 (2.53) | 3 (3.45) | 1 (2.90) | 1 (2.42) | 2 (2.50) | 4 ** (4.72) | 1 (2.02) | 1 (2.66) | 2 (2.98) | 1 (1.89) | 1 (2.49) | 1 (2.35) | 3 (3.75) | 3 | 1 |
| C | 2 (2.59) | 2 (3.33) | 2 (3.15) | 2 (2.58) | 1 (2.48) | 1 (2.63) | 2 (3.49) | 2 (2.82) | 1 (2.42) | 2 (3.26) | 2 (2.57) | 2 (2.48) | 1 (2.50) | 1 | 3 |
| Odin | 3 (4.17) | 4 (4.62) | 3 (3.74) | 3 (4.90) | 3 (3.97) | 2 (3.39) | 4 (5.04) | 3 (4.24) | 3 (4.73) | 3 (4.41) | 3 (3.92) | 3 (4.24) | 6 ** (6.19) | 2 | 5 |
| Rust | 4 (4.95) | 6 (7.06) | 4 (4.67) | 6 (5.60) | 5 (5.50) | 5 (5.03) | 6 (5.84) | 6 (6.06) | 4 (5.50) | 4 (5.23) | 4 (5.18) | 4 (5.08) | 2 (2.82) | 6 | 7 |
| C3 | 5 (5.41) | 1 ** (3.01) | 5 (5.07) | 4 (5.28) | 4 (5.17) | 3 (4.13) | 3 (4.20) | 5 (5.80) | 6 (6.33) | 5 (5.24) | 5 (5.36) | 5 (5.40) | 4 (5.12) | 4 | 4 |
| Nim | 6 (6.35) | 7 (7.96) | 8 (6.83) | 8 (7.17) | 6 (6.39) | 7 (6.55) | 7 (7.15) | 7 (6.12) | 5 (5.93) | 6 (6.18) | 6 (6.30) | 6 (6.41) | 5 (5.52) | 7 | 6 |
| D | 7 (6.62) | 5 (5.58) | 6 (6.76) | 7 (7.02) | 8 (7.08) | 6 (6.15) | 5 (5.30) | 8 (7.46) | 7 (6.86) | 8 (6.66) | 7 (6.71) | 7 (6.45) | 9 (9.45) | 8 | 8 |
| Zig | 8 (7.08) | 8 (8.13) | 7 (6.81) | 5 ** (5.28) | 7 (6.93) | 8 (9.36) | 9 (7.76) | 4 ** (5.72) | 8 (7.86) | 7 (6.41) | 8 (7.13) | 8 (7.11) | 12 ** (10.93) | 5 | 2 |
| Ada | 9 (8.99) | 10 (8.70) | 9 (7.48) | 10 (9.61) | 9 (8.88) | 9 (9.54) | 8 (7.37) | 9 (8.30) | 12 ** (10.83) | 9 (7.89) | 9 (9.13) | 9 (9.19) | 10 (9.95) | 9 | 10 |
| Chapel | 10 (10.02) | 9 (8.21) | 10 (10.16) | 9 (8.13) | 10 (9.92) | 10 (9.66) | 10 (10.70) | 10 (8.54) | 9 (8.49) | 12 (11.73) | 10 (10.18) | 10 (9.72) | 7 ** (6.21) | 10 | 9 |
| Fortran | 11 (10.54) | 11 (9.82) | 11 (10.91) | 11 (10.21) | 11 (10.44) | 11 (9.74) | 12 (11.01) | 11 (10.66) | 10 (8.61) | 11 (11.68) | 12 (10.65) | 12 (10.67) | 8 ** (6.86) | 11 | 11 |
| Julia | 12 (10.58) | 13 (12.02) | 12 (11.41) | 12 (11.14) | 12 (10.46) | 13 (11.32) | 11 (10.97) | 12 (11.45) | 11 (10.12) | 10 (9.78) | 11 (10.51) | 11 (10.41) | 11 (10.77) | 13 | 12 |
| Swift | 13 (12.73) | 14 (12.13) | 13 (12.43) | 13 (12.94) | 14 (12.86) | 12 (11.05) | 14 (13.04) | 13 (12.64) | 14 (12.42) | 14 (12.85) | 13 (12.57) | 13 (12.87) | 13 (12.19) | 12 | 14 |
| Mojo | 14 (12.83) | 12 (11.19) | 14 (13.17) | 14 (13.04) | 13 (12.81) | 14 (11.94) | 13 (11.51) | 14 (12.78) | 13 (12.34) | 13 (12.38) | 14 (12.68) | 14 (12.97) | 14 (13.05) | 14 | 13 |
| C# | 15 (14.89) | 15 (15.41) | 15 (14.89) | 15 (14.92) | 15 (14.88) | 15 (15.25) | 15 (14.98) | 15 (14.95) | 15 (14.78) | 15 (14.93) | 15 (14.90) | 15 (14.86) | 15 (15.66) | 15 | 15 |
| Go | 16 (16.95) | 18 (17.42) | 17 (16.94) | 17 (16.96) | 17 (16.97) | 18 (17.29) | 17 (17.08) | 18 (17.16) | 16 (16.78) | 18 (17.34) | 16 (16.91) | 16 (16.91) | 17 (16.60) | 18 | 17 |
| FreePascal | 17 (16.97) | 16 (16.19) | 18 (17.02) | 16 (16.96) | 18 (16.97) | 16 (16.65) | 16 (16.54) | 16 (16.91) | 17 (17.06) | 17 (16.74) | 17 (16.97) | 18 (17.08) | 18 (17.91) | 16 | 18 |
| Java | 18 (16.98) | 17 (17.02) | 16 (16.83) | 18 (17.00) | 16 (16.94) | 17 (16.91) | 18 (17.12) | 17 (16.92) | 18 (17.30) | 16 (16.49) | 18 (17.04) | 17 (16.96) | 16 (16.00) | 17 | 16 |
| Haskell | 19 (18.84) | 19 (18.77) | 19 (18.83) | 19 (18.84) | 19 (18.84) | 19 (18.71) | 19 (18.88) | 19 (18.83) | 19 (18.70) | 19 (18.93) | 19 (18.82) | 19 (18.83) | 19 (18.59) | 19 | 19 |
| OCaml | 20 (20.21) | 20 (20.33) | 20 (20.19) | 20 (20.22) | 20 (20.22) | 20 (20.31) | 20 (20.23) | 20 (20.20) | 20 (20.38) | 20 (20.14) | 20 (20.22) | 20 (20.20) | 20 (20.12) | 20 | 20 |
| BQN | 21 (21.61) | 21 (21.30) | 21 (21.60) | 21 (21.61) | 21 (21.61) | 21 (21.30) | 21 (21.61) | 21 (21.62) | 21 (21.23) | 22 (22.12) | 21 (21.61) | 21 (21.64) | 22 (21.58) | 21 | 21 |
| JavaScript | 22 (21.94) | 22 (22.10) | 22 (21.93) | 22 (21.94) | 22 (21.93) | 22 (22.08) | 22 (21.97) | 22 (21.93) | 22 (22.21) | 21 (21.63) | 22 (21.94) | 22 (21.88) | 21 (21.33) | 23 | 22 |
| PHP | 23 (22.42) | 23 (22.46) | 23 (22.41) | 23 (22.42) | 23 (22.41) | 23 (22.49) | 23 (22.39) | 23 (22.42) | 23 (22.49) | 23 (22.25) | 23 (22.41) | 23 (22.47) | 23 (22.92) | 22 | 23 |
| Python | 24 (24.05) | 24 (24.12) | 24 (24.12) | 24 (24.05) | 24 (24.06) | 24 (24.14) | 24 (24.04) | 24 (24.05) | 24 (23.81) | 24 (24.10) | 24 (24.05) | 24 (24.05) | 25 (24.99) | 24 | 24 |
| Lua | 25 (24.76) | 25 (24.66) | 25 (24.72) | 25 (24.76) | 25 (24.75) | 25 (24.66) | 25 (24.76) | 25 (24.76) | 25 (24.84) | 25 (24.75) | 25 (24.76) | 25 (24.76) | 24 (24.01) | 25 | 25 |

Chaque case : place (rang espéré) ; ** : plus de deux places d'écart avec « Final ». Ordre des lignes : « Final ».

## Rangs qui bougent de plus de deux places par rapport à « Final »

* Base, trois tailles : C3 1e (Final 5e)
* Sans les tailles (taille publiée seule) : aucun
* Sans R1 : Zig 5e (Final 8e)
* Sans R2 : aucun
* Sans C1 : C++ 4e (Final 1e)
* Sans R4 : aucun
* R1' au lieu de R1 : Zig 4e (Final 8e)
* Taille petite : Ada 12e (Final 9e)
* Taille grande : aucun
* Sélection indépendante : aucun
* D3 et D4 sur trois processus : aucun
* Sur les seules mesures : Odin 6e (Final 3e), Zig 12e (Final 8e), Chapel 7e (Final 10e), Fortran 8e (Final 11e)
* Final contre classement publié (v3) : Zig 5e → 8e
* Final contre point 4, avec R4 : Rust 7e → 4e, Zig 2e → 8e

## Plafond par noyau et parts du code par défaut (« Final », au centre)

| Langage | K1 | K3 | K4 | K5 | K6 | K7 | K8 | K9 | D1 | D2 | D3 | D4 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C++ | 93 | 100 | 79 | 92 | 70 | 80 | 100 | 71 | 14 | 100 | 63 | 95 |
| C | 91 | 87 | 98 | 94 | 69 | 97 | 66 | 70 | 20 | 98 | 53 | 96 |
| Odin | 81 | 82 | 70 | 93 | 72 | 89 | 67 | 70 | 18 | 99 | 38 | 96 |
| Rust | 89 | 81 | 90 | 93 | 65 | 95 | 73 | 66 | 19 | 100 | 68 | 97 |
| C3 | 85 | 100 | 76 | 91 | 70 | 96 | 68 | 68 | 17 | 100 | 41 | 96 |
| Nim | 98 | 88 | 78 | 90 | 63 | 95 | 61 | 69 | 18 | 100 | 52 | 97 |
| D | 92 | 100 | 88 | 92 | 64 | 92 | 65 | 65 | 16 | 97 | 2 | 96 |
| Zig | 91 | 82 | 75 | 91 | 68 | 83 | 70 | 60 | 11 | 93 | 37 | 96 |
| Ada | 87 | 100 | 77 | 86 | 68 | 76 | 78 | 62 | 11 | 100 | 70 | 82 |
| Chapel | 87 | 82 | 90 | 89 | 81 | 94 | 80 | 98 | 8 | 99 | 42 | 97 |
| Fortran | 89 | 85 | 50 | 85 | 78 | 77 | 86 | 86 | 16 | 99 | 73 | 88 |
| Julia | 77 | 80 | 62 | 95 | 82 | 76 | 72 | 58 | 18 | 98 | 10 | 97 |
| Swift | 85 | 82 | 46 | 97 | 70 | 92 | 70 | 75 | 9 | 93 | 27 | 96 |
| Mojo | 82 | 100 | 50 | 92 | 79 | 95 | 46 | 62 | 9 | 100 | 38 | 89 |
| C# | 88 | 83 | 73 | 91 | 50 | 54 | 50 | 65 | 8 | 58 | 40 | 88 |
| Go | 74 | 30 | 82 | 73 | 46 | 70 | 53 | 65 | 5 | 100 | 15 | 96 |
| FreePascal | 50 | 100 | 14 | 39 | 26 | 68 | 49 | 39 | 4 | 98 | 52 | 96 |
| Java | 45 | 79 | 54 | 84 | 53 | 70 | 51 | 55 | 10 | 58 | 59 | 98 |
| Haskell | 48 | 30 | 34 | 91 | 29 | 90 | 69 | 45 | 5 | 76 | 9 | 89 |
| OCaml | 30 | 21 | 10 | 12 | 14 | 39 | 41 | 26 | 6 | 44 | 46 | 74 |
| BQN | 4 | 3 | 10 | 16 | 15 | 21 | 28 | 10 | 5 | 71 | 9 | 45 |
| JavaScript | 17 | 13 | 10 | 8 | 11 | 25 | 20 | 23 | 4 | 27 | 6 | 98 |
| PHP | 7 | 1 | 8 | 4 | 7 | 17 | 9 | 8 | 2 | 29 | 12 | 61 |
| Python | 0 | 3 | 1 | 0 | 1 | 2 | 1 | 1 | 0 | 21 | 1 | 20 |
| Lua | 1 | 4 | 0 | 1 | 1 | 6 | 2 | 1 | 1 | 24 | 1 | 39 |

## Forme retenue par « Final », cellule par cellule et taille par taille (estimation ponctuelle)

Chaque case : forme retenue aux tailles petite / publiée / grande (« pub » : une variante publiée) ; rapport de son temps à la meilleure forme publiée, à la taille publiée.

| Langage | K4 | K5 | Q6 | Q1 | Q6 mt | Q1 mt | K7 | K8 | K9 | K9 mt |
|---|---|---|---|---|---|---|---|---|---|---|
| C++ | k4 tuned/k4 tuned/k4 tuned 0.14 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | q6 mt_pool/q6 mt_pool/q6 mt_pool 0.86 | q1 mt_pool/pub/q1 mt_pool 1.00 | pub/pub/pub 1.00 | k8 tuned_val/k8 tuned_val/k8 tuned_val 0.31 | k9 tuned_v/k9 tuned_v/k9 tuned_v 0.87 | k9 mt_pool/k9 mt_pool_v/k9 mt_pool_v 0.81 |
| C | k4 tuned/k4 tuned/k4 tuned 0.35 | pub/pub/pub 1.00 | q6 tuned_v/q6 tuned_v/q6 tuned_v 0.78 | pub/pub/pub 1.00 | q6 mt_pool/q6 mt_pool_v/q6 mt_pool_v 0.72 | q1 mt_pool/pub/pub 1.00 | pub/pub/pub 1.00 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.37 | k9 tuned_v/pub/k9 tuned_v 1.00 | k9 mt_pool/pub/k9 mt_pool_v 1.00 |
| Odin | k4 tuned/k4 tuned/k4 tuned 0.49 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | q1 tuned_v/q1 tuned_v/q1 tuned_v 0.56 | q6 mt_pool/q6 mt_pool/pub 0.79 | q1 mt_pool_v/q1 mt_pool_v/q1 mt_pool_v 0.53 | pub/pub/pub 1.00 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.32 | pub/pub/pub 1.00 | k9 mt_pool/pub/k9 mt_pool 1.00 |
| Rust | k4 tuned/k4 tuned/k4 tuned 0.39 | pub/pub/pub 1.00 | q6 tuned_v/q6 tuned_v/q6 tuned_v 0.82 | pub/pub/pub 1.00 | q6 mt_pool/q6 mt_pool_v/q6 mt_pool_v 0.88 | q1 mt_pool/pub/pub 1.00 | pub/pub/pub 1.00 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.28 | k9 tuned_v/pub/k9 tuned_v 1.00 | k9 mt_pool/k9 mt_pool/k9 mt_pool_v 0.95 |
| C3 | k4 tuned/k4 tuned/k4 tuned 0.45 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | q1 tuned_v/pub/pub 1.00 | q6 mt_pool/q6 mt_pool/pub 0.82 | q1 mt_pool_v/q1 mt_pool_v/pub 0.89 | pub/pub/pub 1.00 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.35 | pub/pub/pub 1.00 | k9 mt_pool/k9 mt_pool/k9 mt_pool 0.84 |
| Nim | k4 tuned/k4 tuned/k4 tuned 0.46 | pub/pub/pub 1.00 | q6 tuned_v/q6 tuned_v/q6 tuned_v 0.83 | q1 tuned_v/q1 tuned_v/q1 tuned_v 0.56 | q6 mt_pool_v/q6 mt_pool_v/q6 mt_pool_v 0.74 | q1 mt_pool_v/q1 mt_pool_v/q1 mt_pool_v 0.45 | pub/pub/pub 1.00 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.29 | k9 tuned_v/pub/k9 tuned_v 1.00 | k9 mt_pool/k9 mt_pool/k9 mt_pool_v 0.96 |
| D | k4 tuned/k4 tuned/k4 tuned 0.40 | pub/pub/pub 1.00 | q6 tuned_v/q6 tuned_v/q6 tuned_v 0.79 | pub/pub/pub 1.00 | q6 mt_pool/q6 mt_pool_v/q6 mt_pool_v 0.53 | q1 mt_pool/q1 mt_pool/q1 mt_pool 0.94 | pub/pub/pub 1.00 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.35 | pub/pub/pub 1.00 | k9 mt_pool/k9 mt_pool/k9 mt_pool 0.94 |
| Zig | k4 tuned/k4 tuned/k4 tuned 0.11 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | q6 mt_pool/q6 mt_pool/q6 mt_pool 0.75 | q1 mt_pool/q1 mt_pool/q1 mt_pool 0.87 | pub/pub/pub 1.00 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.41 | pub/pub/pub 1.00 | k9 mt_pool/k9 mt_pool/k9 mt_pool 0.63 |
| Ada | k4 tuned/k4 tuned/k4 tuned 0.15 | pub/pub/pub 1.00 | q6 tuned_v/q6 tuned_v/q6 tuned_v 0.91 | q1 tuned_v/q1 tuned_v/q1 tuned_v 0.67 | q6 mt_pool/q6 mt_pool_v/q6 mt_pool_v 0.42 | q1 mt_pool_v/q1 mt_pool_v/q1 mt_pool_v 0.41 | pub/pub/pub 1.00 | k8 tuned_it/pub/pub 1.00 | pub/pub/pub 1.00 | k9 mt_pool/k9 mt_pool/k9 mt_pool 0.53 |
| Chapel | k4 tuned/k4 tuned/k4 tuned 0.58 | pub/pub/k5 tuned_v 1.00 | pub/q6 tuned_v/q6 tuned_v 0.95 | pub/q1 tuned_v/q1 tuned_v 0.92 | pub/pub/q6 mt_pool_v 1.00 | q1 mt_pool_v/q1 mt_pool_v/q1 mt_pool_v 0.71 | pub/pub/pub 1.00 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.25 | pub/k9 tuned_v/pub 0.93 | k9 mt_pool_v/k9 mt_pool_v/pub 0.98 |
| Fortran | k4 swar/k4 swar/k4 swar 0.20 | k5 rq_acc16/k5 rq_acc16/pub 0.96 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/k7 tuned_oa/pub 0.86 | k8 tuned_val/k8 tuned_val/k8 tuned_val 0.41 | pub/pub/pub 1.00 | pub/pub/pub 1.00 |
| Julia | k4 tuned/k4 tuned/k4 tuned 0.54 | k5 tuned_v/k5 tuned_v/k5 tuned_v 0.77 | q6 tuned_v/q6 tuned_v/q6 tuned_v 0.83 | q1 tuned_v/q1 tuned_v/q1 tuned_v 0.36 | q6 mt_pool_v/q6 mt_pool_v/q6 mt_pool_v 0.69 | q1 mt_pool_v/q1 mt_pool_v/q1 mt_pool_v 0.30 | k7 tuned_pf/k7 tuned_pf/k7 tuned_pf 0.97 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.25 | k9 tuned_v/k9 tuned_v/k9 tuned_v 0.90 | pub/k9 mt_pool_v/k9 mt_pool_v 0.99 |
| Swift | k4 tuned/k4 tuned/k4 tuned 0.71 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | q6 mt_pool/q6 mt_pool/pub 0.89 | q1 mt_pool/q1 mt_pool/q1 mt_pool 0.88 | pub/pub/pub 1.00 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.32 | pub/pub/pub 1.00 | k9 mt_pool/k9 mt_pool/k9 mt_pool 0.85 |
| Mojo | k4 tuned/k4 tuned/k4 tuned 0.12 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | q1 tuned_v/q1 tuned_v/q1 tuned_v 0.76 | pub/pub/pub 1.00 | q1 mt_pool_v/q1 mt_pool_v/q1 mt_pool_v 0.77 | pub/pub/pub 1.00 | k8 tuned_val/k8 tuned_val/k8 tuned_val 0.75 | pub/pub/pub 1.00 | pub/pub/pub 1.00 |
| C# | k4 tuned/k4 tuned/k4 tuned 0.05 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | q6 mt_pool/q6 mt_pool/q6 mt_pool 0.67 | q1 mt_pool/pub/q1 mt_pool 1.00 | pub/pub/pub 1.00 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.47 | pub/pub/pub 1.00 | k9 mt_pool/k9 mt_pool/pub 0.63 |
| Go | k4 tuned/k4 tuned/k4 tuned 0.07 | k5 tuned_v/pub/k5 tuned_v 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.51 | k9 tuned_v/k9 tuned_v/k9 tuned_v 0.53 | k9 mt_pool_v/k9 mt_pool_v/k9 mt_pool_v 0.64 |
| FreePascal | k4 swar/k4 swar/k4 swar 0.24 | k5 tuned_v/k5 tuned_v/k5 tuned_v 0.81 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | q6 mt_pool/pub/pub 1.00 | q1 mt_pool/pub/pub 1.00 | pub/pub/pub 1.00 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.39 | pub/pub/pub 1.00 | k9 mt_pool/k9 mt_pool/k9 mt_pool 0.87 |
| Java | k4 tuned/k4 tuned/k4 tuned 0.23 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | q1 tuned_v/q1 tuned_v/q1 tuned_v 0.46 | q6 mt_pool/q6 mt_pool/q6 mt_pool 0.81 | q1 mt_pool_v/q1 mt_pool_v/q1 mt_pool_v 0.43 | k7 rq_iso/k7 rq_iso/k7 rq_iso 0.87 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.63 | pub/pub/k9 tuned_v 1.00 | k9 mt_pool/k9 mt_pool_v/k9 mt_pool_v 0.74 |
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

Processeur des enregistrements : 6/207/2 Intel(R) Xeon(R) Processor @ 2.10GHz (9738 enregistrements).

Processus écartés : 0 ; cellules non exécutées (étalonnage hors mémoire ou hors durée) : 18 ; vol de temps > 5 % après reprise : 0.
* non exécutée : BQN pub large k1 aos energy (oom)
* non exécutée : BQN pub large k1 natural energy (oom)
* non exécutée : BQN pub large k1 natural_shuffled energy (oom)
* non exécutée : BQN pub large k1 soa energy (oom)
* non exécutée : Python pub large k1 natural energy (oom)
* non exécutée : Python pub large k1 natural_shuffled energy (oom)
