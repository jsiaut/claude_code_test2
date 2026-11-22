# v4, point 4 : un code optimisé convergent — résultats

*Plan : `docs/V4_CONVERGE.md` (sections 3 à 8, écarts 4.1 et 4.2). Généré par `analysis/converge_v4.py` à partir de `results/converge/raw` et du relevé des formes (`results/converge/forms.json`). Le classement de tête du README ne change pas au point 4 (section 9).*

b3 = 85.12 ms (médianes des 16 décalages : start 84.90, 85.40 ; end 85.65, 84.55 ms).

## Classements

| Langage | Hôte | Convergent | Remarques | Convergent, sélection indépendante | Convergent, avec R4 | Hôte, source non corrigée |
|---|---|---|---|---|---|---|
| C | 1 (2.86 ; 69.6) | 2 (3.82 ; 73.2) | 1 (2.03 ; 72.6) | 4 ** (3.98 ; 72.9) | 3 (2.88 ; 80.6) | 1 (2.16 ; 69.8) |
| C++ | 2 (3.04 ; 72.9) | 1 (1.87 ; 81.7) | 2 (3.37 ; 72.9) | 1 (1.98 ; 81.4) | 1 (2.45 ; 81.9) | 3 (3.47 ; 70.6) |
| C3 | 3 (3.15 ; 68.5) | 3 (3.82 ; 73.5) | 3 (3.47 ; 68.5) | 2 (3.70 ; 73.7) | 4 (5.19 ; 73.5) | 2 (3.47 ; 66.4) |
| D | 4 (4.84 ; 69.7) | 5 (5.49 ; 74.7) | 4 (5.23 ; 69.7) | 5 (5.51 ; 74.7) | 8 ** (7.18 ; 75.2) | 4 (5.87 ; 66.6) |
| Odin | 5 (5.74 ; 63.2) | 6 (6.34 ; 67.8) | 5 (5.82 ; 63.6) | 6 (6.09 ; 68.0) | 5 (5.39 ; 75.0) | 5 (6.18 ; 61.5) |
| Zig | 6 (6.27 ; 63.3) | 4 (3.87 ; 71.3) | 8 (6.73 ; 63.3) | 3 ** (3.85 ; 71.3) | 2 ** (2.87 ; 78.7) | 6 (6.41 ; 62.1) |
| Rust | 7 (6.99 ; 61.2) | 8 (7.41 ; 65.9) | 6 (6.46 ; 62.3) | 8 (7.28 ; 66.1) | 7 (6.51 ; 73.3) | 8 (7.27 ; 59.7) |
| Nim | 8 (7.03 ; 61.3) | 7 (6.42 ; 67.1) | 7 (6.59 ; 62.3) | 7 (6.48 ; 67.0) | 6 (5.50 ; 74.5) | 7 (7.16 ; 60.0) |
| Ada | 9 (9.72 ; 62.9) | 9 (9.60 ; 69.2) | 9 (10.13 ; 62.9) | 9 (10.01 ; 68.6) | 10 (11.06 ; 70.7) | 10 (9.26 ; 62.4) |
| Chapel | 10 (10.02 ; 56.7) | 11 (10.40 ; 61.4) | 10 (10.33 ; 56.9) | 11 (10.50 ; 61.3) | 9 (9.59 ; 69.0) | 9 (8.80 ; 57.0) |
| Mojo | 11 (10.75 ; 60.3) | 10 (10.38 ; 67.3) | 12 (11.15 ; 60.3) | 10 (10.18 ; 67.6) | 13 (12.20 ; 67.3) | 12 (10.43 ; 59.6) |
| Swift | 12 (10.96 ; 57.6) | 14 (12.77 ; 60.1) | 13 (11.41 ; 57.6) | 14 (12.50 ; 60.6) | 14 (12.30 ; 67.0) | 11 (9.96 ; 57.9) |
| Fortran | 13 (11.43 ; 55.5) | 12 (11.60 ; 60.5) | 11 (10.91 ; 56.8) | 13 (11.77 ; 60.3) | 11 (11.13 ; 67.3) | 14 (12.87 ; 52.3) |
| Julia | 14 (12.57 ; 54.2) | 13 (11.64 ; 61.1) | 14 (12.07 ; 56.0) | 12 (11.61 ; 61.2) | 12 (11.18 ; 67.7) | 13 (12.05 ; 54.3) |
| C# | 15 (15.27 ; 49.0) | 15 (14.95 ; 56.2) | 15 (15.36 ; 50.7) | 15 (14.92 ; 56.4) | 15 (14.87 ; 62.3) | 15 (15.13 ; 48.6) |
| Java | 16 (16.20 ; 43.9) | 16 (16.46 ; 48.8) | 16 (15.83 ; 47.3) | 16 (16.45 ; 48.9) | 16 (16.31 ; 55.3) | 17 (16.50 ; 41.7) |
| FreePascal | 17 (16.72 ; 44.7) | 17 (16.97 ; 48.6) | 17 (16.46 ; 47.5) | 17 (16.96 ; 48.6) | 18 (17.39 ; 49.3) | 16 (16.29 ; 44.8) |
| Go | 18 (17.83 ; 39.5) | 18 (17.44 ; 45.8) | 18 (17.77 ; 41.4) | 18 (17.45 ; 45.7) | 17 (17.30 ; 51.1) | 18 (17.88 ; 37.6) |
| Haskell | 19 (18.65 ; 36.6) | 19 (18.81 ; 40.1) | 19 (18.91 ; 36.6) | 19 (18.82 ; 39.9) | 19 (18.72 ; 44.7) | 19 (18.90 ; 33.2) |
| OCaml | 20 (20.38 ; 20.8) | 20 (20.26 ; 21.6) | 20 (20.35 ; 21.0) | 20 (20.27 ; 21.5) | 20 (20.25 ; 23.2) | 20 (20.38 ; 20.6) |
| BQN | 21 (21.14 ; 16.3) | 21 (21.44 ; 15.8) | 21 (21.22 ; 16.3) | 21 (21.44 ; 15.8) | 21 (21.44 ; 16.7) | 21 (21.17 ; 16.1) |
| JavaScript | 22 (22.30 ; 15.0) | 22 (22.16 ; 15.4) | 22 (22.20 ; 15.4) | 22 (22.16 ; 15.4) | 22 (22.13 ; 16.4) | 23 (22.33 ; 14.8) |
| PHP | 23 (22.33 ; 15.9) | 23 (22.30 ; 16.2) | 23 (22.38 ; 15.9) | 23 (22.30 ; 16.2) | 23 (22.33 ; 16.7) | 22 (22.28 ; 15.9) |
| Python | 24 (24.15 ; 12.2) | 24 (24.08 ; 12.3) | 24 (24.17 ; 12.2) | 24 (24.07 ; 12.3) | 24 (24.09 ; 12.3) | 24 (24.18 ; 12.2) |
| Lua | 25 (24.65 ; 5.7) | 25 (24.73 ; 5.7) | 25 (24.64 ; 5.8) | 25 (24.74 ; 5.7) | 25 (24.73 ; 5.8) | 25 (24.61 ; 5.7) |

Chaque case : place (rang espéré ; score au centre) ; ** : plus de deux places d'écart avec « Hôte ». Ordre des lignes : « Hôte ».

## Par noyau (information) : « Convergent » sur un seul noyau

| Langage | Hôte | K4 | K5 | K6 | K7 | K8 | K9 | Convergent |
|---|---|---|---|---|---|---|---|---|
| C | 1 | 2 (3.53) | 1 (2.86) | 1 (2.99) | 1 (2.86) | 3 (3.07) | 1 (2.84) | 2 (3.82) |
| C++ | 2 | 1 (1.88) | 2 (3.05) | 2 (3.32) | 2 (3.04) | 1 (2.98) | 2 (3.05) | 1 (1.87) |
| C3 | 3 | 3 (3.77) | 3 (3.15) | 3 (3.35) | 3 (3.15) | 2 (3.02) | 3 (3.20) | 3 (3.82) |
| D | 4 | 5 (5.59) | 4 (4.86) | 4 (4.82) | 4 (4.85) | 4 (5.00) | 4 (4.79) | 5 (5.49) |
| Odin | 5 | 6 (6.66) | 5 (5.75) | 5 (5.49) | 5 (5.74) | 5 (5.64) | 5 (5.88) | 6 (6.34) |
| Zig | 6 | 4 (3.86) | 6 (6.31) | 7 (6.72) | 6 (6.29) | 6 (6.40) | 6 (6.11) | 4 (3.87) |
| Rust | 7 | 7 (7.95) | 7 (7.02) | 8 (7.19) | 7 (7.00) | 7 (6.42) | 7 (6.89) | 8 (7.41) |
| Nim | 8 | 8 (8.01) | 8 (7.06) | 6 (5.99) | 8 (7.04) | 8 (6.55) | 8 (7.07) | 7 (6.42) |
| Ada | 9 | 10 (8.54) | 9 (9.81) | 9 (9.03) | 9 (9.74) | 11 (11.44) | 9 (9.33) | 9 (9.60) |
| Chapel | 10 | 12 (11.33) | 10 (10.04) | 10 (10.09) | 10 (10.05) | 9 (8.85) | 10 (10.12) | 11 (10.40) |
| Mojo | 11 | 9 (8.41) | 11 (10.84) | 11 (10.87) | 11 (10.78) | 13 (11.67) | 11 (10.92) | 10 (10.38) |
| Swift | 12 | 13 (12.35) | 12 (11.06) | 12 (11.42) | 12 (10.97) | 10 (10.70) | 12 (10.98) | 14 (12.77) |
| Fortran | 13 | 11 (10.68) | 13 (11.45) | 13 (11.88) | 13 (11.34) | 12 (11.54) | 13 (11.57) | 12 (11.60) |
| Julia | 14 | 14 (13.45) | 14 (12.05) | 14 (12.15) | 14 (12.54) | 14 (11.98) | 14 (12.61) | 13 (11.64) |
| C# | 15 | 15 (14.37) | 15 (15.33) | 15 (15.36) | 15 (15.33) | 15 (15.36) | 15 (15.24) | 15 (14.95) |
| Java | 16 | 16 (16.50) | 16 (16.26) | 16 (16.08) | 16 (16.08) | 16 (16.29) | 16 (16.21) | 16 (16.46) |
| FreePascal | 17 | 17 (17.02) | 17 (16.58) | 17 (16.76) | 17 (16.76) | 17 (16.67) | 17 (16.76) | 17 (16.97) |
| Go | 18 | 18 (17.36) | 18 (17.86) | 18 (17.86) | 18 (17.85) | 18 (17.89) | 18 (17.74) | 18 (17.44) |
| Haskell | 19 | 19 (18.76) | 19 (18.70) | 19 (18.66) | 19 (18.65) | 19 (18.56) | 19 (18.71) | 19 (18.81) |
| OCaml | 20 | 20 (20.29) | 20 (20.38) | 20 (20.37) | 20 (20.37) | 20 (20.36) | 20 (20.37) | 20 (20.26) |
| BQN | 21 | 21 (21.33) | 21 (21.15) | 21 (21.17) | 21 (21.15) | 21 (21.19) | 21 (21.17) | 21 (21.44) |
| JavaScript | 22 | 22 (22.26) | 22 (22.30) | 22 (22.29) | 22 (22.31) | 22 (22.26) | 22 (22.28) | 22 (22.16) |
| PHP | 23 | 23 (22.27) | 23 (22.33) | 23 (22.33) | 23 (22.32) | 23 (22.35) | 23 (22.34) | 23 (22.30) |
| Python | 24 | 24 (24.09) | 24 (24.15) | 24 (24.14) | 24 (24.15) | 24 (24.14) | 24 (24.15) | 24 (24.08) |
| Lua | 25 | 25 (24.71) | 25 (24.65) | 25 (24.66) | 25 (24.64) | 25 (24.66) | 25 (24.64) | 25 (24.73) |

## Rangs plausibles (90 %)

| Langage | Hôte | Convergent | Remarques | Convergent, sélection indépendante | Convergent, avec R4 | Hôte, source non corrigée |
|---|---|---|---|---|---|---|
| C | 1–7 | 1–8 | 1–5 | 1–8 | 1–7 | 1–6 |
| C++ | 1–8 | 1–5 | 1–8 | 1–5 | 1–6 | 1–8 |
| C3 | 1–7 | 1–8 | 1–8 | 1–8 | 2–9 | 1–8 |
| D | 2–10 | 2–10 | 2–10 | 2–11 | 3–11 | 2–11 |
| Odin | 2–9 | 3–10 | 2–10 | 3–10 | 2–9 | 2–10 |
| Zig | 1–12 | 1–7 | 2–12 | 1–7 | 1–6 | 2–12 |
| Rust | 3–10 | 4–11 | 3–10 | 4–10 | 3–10 | 3–11 |
| Nim | 2–11 | 2–10 | 2–11 | 2–10 | 2–9 | 2–12 |
| Ada | 4–14 | 5–14 | 5–14 | 5–14 | 7–14 | 3–13 |
| Chapel | 6–14 | 7–14 | 6–14 | 7–14 | 5–14 | 3–13 |
| Mojo | 5–14 | 4–14 | 5–15 | 4–14 | 9–14 | 4–14 |
| Swift | 7–14 | 10–15 | 7–14 | 9–15 | 9–14 | 4–14 |
| Fortran | 7–14 | 7–15 | 6–14 | 7–15 | 7–14 | 9–15 |
| Julia | 9–15 | 8–14 | 8–15 | 8–14 | 8–14 | 8–15 |
| C# | 14–17 | 13–16 | 13–17 | 13–16 | 13–16 | 14–16 |
| Java | 15–18 | 15–18 | 13–18 | 15–18 | 15–18 | 15–18 |
| FreePascal | 15–19 | 15–19 | 14–18 | 15–19 | 15–19 | 15–18 |
| Go | 17–19 | 16–18 | 17–18 | 16–18 | 16–18 | 17–19 |
| Haskell | 17–19 | 18–19 | 18–19 | 18–19 | 18–19 | 18–19 |
| OCaml | 20–22 | 20–22 | 20–22 | 20–22 | 20–22 | 20–22 |
| BQN | 20–23 | 20–23 | 20–23 | 20–23 | 20–23 | 20–23 |
| JavaScript | 21–24 | 21–24 | 21–24 | 21–24 | 21–24 | 21–24 |
| PHP | 20–23 | 20–23 | 20–23 | 20–23 | 20–23 | 20–23 |
| Python | 22–25 | 22–25 | 22–25 | 22–25 | 23–25 | 22–25 |
| Lua | 24–25 | 24–25 | 24–25 | 24–25 | 24–25 | 24–25 |

## Rangs qui bougent de plus de deux places par rapport à « Hôte »

* Convergent : aucun
* Convergent, K4 seul : aucun
* Convergent, K5 seul : aucun
* Convergent, K6 seul : aucun
* Convergent, K7 seul : aucun
* Convergent, K8 seul : aucun
* Convergent, K9 seul : aucun
* Remarques : aucun
* Convergent, sélection indépendante : Zig 6e → 3e, C 1e → 4e
* Convergent, avec R4 : Zig 6e → 2e, D 4e → 8e
* Hôte, source non corrigée : aucun

## Étages indicatifs (paires ordonnées dans au moins 95 % des variantes)

* Hôte : C, C++, C3, D, Odin, Zig, Rust, Nim, Ada, Chapel, Mojo, Swift, Fortran, Julia, C#, Java, FreePascal, Go, Haskell | OCaml, BQN, JavaScript, PHP, Python, Lua
* Convergent : C++, C, C3, Zig, D, Odin, Nim, Rust, Ada, Mojo, Chapel, Fortran, Julia, Swift, C#, Java, FreePascal, Go, Haskell | OCaml, BQN, JavaScript, PHP, Python, Lua
* Remarques : C, C++, C3, D, Odin, Rust, Nim, Zig, Ada, Chapel, Fortran, Mojo, Swift, Julia, C#, Java, FreePascal, Go | Haskell | OCaml, BQN, JavaScript, PHP, Python, Lua
* Convergent, sélection indépendante : C++, C3, Zig, C, D, Odin, Nim, Rust, Ada, Mojo, Chapel, Julia, Fortran, Swift, C#, Java, FreePascal, Go, Haskell | OCaml, BQN, JavaScript, PHP, Python, Lua
* Convergent, avec R4 : C++, Zig, C, C3, Odin, Nim, Rust, D, Chapel, Ada, Fortran, Julia, Mojo, Swift, C#, Java, Go, FreePascal, Haskell | OCaml, BQN, JavaScript, PHP, Python, Lua
* Hôte, source non corrigée : C, C3, C++, D, Odin, Zig, Nim, Rust, Chapel, Ada, Swift, Mojo, Julia, Fortran, C#, FreePascal, Java, Go, Haskell | OCaml, BQN, PHP, JavaScript, Python, Lua

## Forme retenue par « Convergent », cellule par cellule (estimation ponctuelle)

Chaque case : forme retenue (« publiée » : une variante publiée ; R : trouvée par la remarque du langage) et rapport de son temps à la meilleure forme publiée ; « – » : pas de cellule.

| Langage | K4 | K5 | Q6 | Q1 | Q6 mt | Q1 mt | K7 | K8 | K9 | K9 mt |
|---|---|---|---|---|---|---|---|---|---|---|
| C | k4 tuned 0.39 | publiée 1.00 | q6 tuned_v 0.82 | publiée 1.00 | q6 mt_pool_v 0.72 | publiée 1.00 | publiée 1.00 | k8 tuned_it R 0.38 | k9 tuned_v 0.91 | k9 mt_pool_v 0.86 |
| C++ | k4 tuned 0.15 | publiée 1.00 | publiée 1.00 | publiée 1.00 | q6 mt_pool 0.90 | q1 mt_pool 0.99 | publiée 1.00 | k8 tuned_val 0.31 | k9 tuned_v 0.84 | k9 mt_pool_v 0.96 |
| C3 | k4 tuned 0.39 | publiée 1.00 | publiée 1.00 | q1 tuned_v 0.96 | q6 mt_pool 0.83 | q1 mt_pool 0.98 | publiée 1.00 | k8 tuned_it 0.32 | publiée 1.00 | k9 mt_pool 0.85 |
| D | k4 tuned 0.40 | publiée 1.00 | q6 tuned_v 0.80 | publiée 1.00 | q6 mt_pool_v 0.56 | q1 mt_pool 0.88 | publiée 1.00 | k8 tuned_it 0.36 | publiée 1.00 | k9 mt_pool 0.77 |
| Odin | k4 tuned 0.39 | publiée 1.00 | publiée 1.00 | q1 tuned_v R 0.56 | q6 mt_pool 0.78 | q1 mt_pool_v 0.54 | publiée 1.00 | k8 tuned_it 0.31 | publiée 1.00 | k9 mt_pool 0.88 |
| Zig | k4 tuned 0.09 | publiée 1.00 | publiée 1.00 | publiée 1.00 | q6 mt_pool 0.77 | q1 mt_pool 0.95 | publiée 1.00 | k8 tuned_it 0.34 | publiée 1.00 | k9 mt_pool 0.68 |
| Rust | k4 tuned 0.42 | publiée 1.00 | q6 tuned_v 0.75 | publiée 1.00 | q6 mt_pool_v 0.66 | q1 mt_pool 0.84 | publiée 1.00 | k8 tuned_it 0.27 | k9 tuned_v 0.86 | k9 mt_pool 0.89 |
| Nim | k4 tuned 0.42 | publiée 1.00 | q6 tuned_v 0.78 | q1 tuned_v R 0.36 | q6 mt_pool_v 0.64 | q1 mt_pool_v 0.37 | publiée 1.00 | k8 tuned_it 0.27 | k9 tuned_v 0.89 | k9 mt_pool_v 0.95 |
| Ada | k4 tuned 0.15 | publiée 1.00 | q6 tuned_v 0.89 | q1 tuned_v 0.50 | q6 mt_pool_v 0.44 | q1 mt_pool_v 0.43 | publiée 1.00 | publiée 1.00 | publiée 1.00 | k9 mt_pool 0.54 |
| Chapel | k4 tuned 0.51 | k5 tuned_v 1.00 | q6 tuned_v 0.93 | q1 tuned_v R 0.77 | q6 mt_pool_v 0.97 | q1 mt_pool_v 0.60 | publiée 1.00 | k8 tuned_it 0.22 | k9 tuned_v 0.93 | k9 mt_pool_v 0.96 |
| Mojo | k4 tuned 0.09 | publiée 1.00 | publiée 1.00 | q1 tuned_v 0.73 | publiée 1.00 | q1 mt_pool_v 0.59 | publiée 1.00 | k8 tuned_val 0.74 | publiée 1.00 | publiée 1.00 |
| Swift | k4 tuned 0.57 | publiée 1.00 | publiée 1.00 | publiée 1.00 | q6 mt_pool 0.90 | q1 mt_pool 0.94 | publiée 1.00 | k8 tuned_it 0.33 | publiée 1.00 | k9 mt_pool 0.85 |
| Fortran | k4 swar 0.17 | k5 rq_acc16 R 0.93 | publiée 1.00 | publiée 1.00 | publiée 1.00 | publiée 1.00 | k7 tuned_oa 0.95 | k8 tuned_val 0.40 | publiée 1.00 | publiée 1.00 |
| Julia | k4 tuned 0.42 | k5 tuned_v 0.56 | q6 tuned_v 0.81 | q1 tuned_v 0.28 | q6 mt_pool_v 0.95 | q1 mt_pool_v 0.30 | k7 tuned_pf R 0.95 | k8 tuned_it 0.23 | k9 tuned_v 0.93 | k9 mt_pool_v 0.97 |
| C# | k4 tuned 0.04 | publiée 1.00 | publiée 1.00 | publiée 1.00 | q6 mt_pool R 0.64 | publiée 1.00 | publiée 1.00 | k8 tuned_it R 0.57 | publiée 1.00 | k9 mt_pool R 0.71 |
| Java | k4 tuned 0.22 | publiée 1.00 | publiée 1.00 | q1 tuned_v R 0.41 | publiée 1.00 | q1 mt_pool_v R 0.43 | k7 rq_iso R 0.75 | k8 tuned_it R 0.62 | publiée 1.00 | k9 mt_pool_v R 0.80 |
| FreePascal | k4 swar 0.18 | k5 tuned_v R 0.66 | publiée 1.00 | publiée 1.00 | q6 mt_pool 0.83 | q1 mt_pool 0.92 | publiée 1.00 | k8 tuned_it R 0.41 | publiée 1.00 | k9 mt_pool 0.87 |
| Go | k4 tuned 0.05 | k5 tuned_v R 0.95 | publiée 1.00 | publiée 1.00 | publiée 1.00 | publiée 1.00 | publiée 1.00 | k8 tuned_it R 0.48 | k9 tuned_v R 0.67 | k9 mt_pool_v R 0.85 |
| Haskell | k4 tuned 0.16 | publiée 1.00 | publiée 1.00 | publiée 1.00 | publiée 1.00 | publiée 1.00 | publiée 1.00 | k8 tuned_it 0.39 | publiée 1.00 | publiée 1.00 |
| OCaml | k4 tuned 0.22 | publiée 1.00 | q6 tuned_s R 0.81 | publiée 1.00 | q6 mt_pool_s R 0.75 | publiée 1.00 | k7 tuned_oa R 0.91 | k8 tuned_it 0.69 | publiée 1.00 | k9 mt_pool 0.74 |
| BQN | publiée 1.00 | publiée 1.00 | publiée 1.00 | publiée 1.00 | publiée 1.00 | publiée 1.00 | publiée 1.00 | publiée 1.00 | publiée 1.00 | publiée 1.00 |
| JavaScript | k4 swar 0.33 | k5 rq_f64 R 0.95 | q6 tuned_s R 0.64 | publiée 1.00 | q6 mt_pool_s R 0.67 | publiée 1.00 | publiée 1.00 | k8 tuned_it R 0.66 | k9 rq_slide R 0.86 | k9 rq_slide_mt R 0.71 |
| PHP | k4 tuned 0.12 | publiée 1.00 | q6 tuned_s 0.67 | publiée 1.00 | q6 mt_pool_s 0.71 | publiée 1.00 | k7 tuned_oa 0.86 | publiée 1.00 | publiée 1.00 | publiée 1.00 |
| Python | k4 tuned 0.13 | publiée 1.00 | k6 rq_cols R 0.43 | publiée 1.00 | k6 rq_cols_mt R 0.26 | q1 mt_pool 0.95 | k7 tuned_oa 0.65 | k8 tuned_val 0.59 | publiée 1.00 | publiée 1.00 |
| Lua | k4 swar 0.83 | publiée 1.00 | k6 rq_nest R 0.89 | publiée 1.00 | k6 rq_nest_mt R 0.34 | publiée 1.00 | k7 rq_pack R 0.62 | k8 tuned_val 0.91 | publiée 1.00 | k9 rq_slide_mt R 0.86 |

Sélection indépendante (calcul 5) : 250 choix faits sur la passe 0 (détail dans `results/converge/analysis.json`).

## Contrôle de l'erratum : source non corrigée / source corrigée (même hôte)

| Langage | Cellules (rapport des temps) |
|---|---|
| C++ | k9 mt 2.63, k9 natural 1.65, k9 tuned 1.66 |
| C3 | k9 mt 2.23, k9 natural 1.63, k9 tuned 1.53 |
| D | k6 mt q1 2.64, k6 tuned q1 2.78, k9 mt 1.93, k9 natural 1.29, k9 tuned 1.55 |
| Odin | k9 mt 2.22, k9 natural 1.55, k9 tuned 1.70 |
| Zig | k9 mt 1.89, k9 natural 1.67, k9 tuned 1.51 |
| Rust | k7 tuned 1.00, k9 mt 2.46, k9 natural 0.98, k9 tuned 1.54 |
| Nim | k9 mt 2.25, k9 natural 1.01, k9 tuned 1.48 |
| Ada | k1 aos energy 1.00, k1 soa energy 0.94, k2 tuned 16384 1.00, k2 tuned 262144 0.99, k2 tuned 8388608 0.75, k6 mt q1 1.03, k6 mt q6 2.86, k6 tuned q1 1.01, k6 tuned q6 0.99, k9 mt 1.24, k9 tuned 1.18 |
| Mojo | k9 mt 1.47, k9 natural 0.98, k9 tuned 1.27 |
| Fortran | k1 natural_shuffled energy 1.01, k1 natural energy 1.02, k2 tuned 16384 1.00, k2 tuned 262144 1.00, k2 tuned 8388608 1.00, k4 branchless_unsorted 3.12, k4 natural_unsorted 2.48, k6 natural q1 1.01, k6 natural q6 1.00, k9 mt 1.04, k9 natural 1.68, k9 tuned 1.04 |
| Julia | k9 mt 1.08, k9 natural 1.01, k9 tuned 1.02 |
| C# | k9 mt 1.28, k9 natural 1.01, k9 tuned 1.33 |
| Java | k1 soa energy 1.05, k5 tuned 1.52, k9 mt 1.53, k9 natural 1.98, k9 tuned 1.51 |
| Go | k1 soa energy 1.01, k5 natural 1.00, k5 tuned 2.55, k6 mt q6 0.96, k6 tuned q6 0.99, k9 mt 1.36, k9 natural 1.17, k9 tuned 1.53 |
| Haskell | k1 aos energy 0.99, k1 natural_shuffled energy 1.02, k1 natural energy 1.00, k1 soa energy 1.06, k2 tuned 16384 0.99, k2 tuned 262144 0.98, k2 tuned 8388608 1.04, k3 rmw_padded 1.37, k3 sw_padded 0.96, k4 branchless_unsorted 0.80, k4 natural_unsorted 10.73, k5 natural 1.48, k5 tuned 1.15, k6 mt q1 0.92, k6 mt q6 1.32, k6 natural q1 1.24, k6 natural q6 0.97, k6 tuned q1 1.00, k6 tuned q6 1.58, k7 natural 1.01, k7 tuned 1.19, k8 natural 0.97, k8 tuned 2.97, k9 mt 1.06, k9 natural 2.04, k9 tuned 1.08 |
| OCaml | k1 aos energy 5.49, k6 mt q6 2.06, k6 tuned q6 2.42, k7 tuned 0.97, k8 tuned 1.03, k9 mt 1.24, k9 natural 1.01, k9 tuned 1.02 |
| BQN | k7 natural 7.28, k9 mt 1.07, k9 natural 0.95, k9 tuned 1.06 |
| JavaScript | k7 tuned 1.70, k9 mt 1.00, k9 natural 1.29, k9 tuned 1.02 |
| Python | k3 rmw_padded 4.25, k3 sw_padded 4.21, k6 mt q1 3.88, k6 mt q6 3.39, k8 natural 1.03, k9 mt 2.73, k9 natural 0.94, k9 tuned 0.96 |
| Lua | k3 rmw_padded 1.38, k3 sw_padded 1.36, k4 branchless_unsorted 2.91, k4 natural_unsorted 2.34, k6 mt q6 0.92, k6 tuned q6 0.93, k8 natural 0.72, k9 mt 1.00, k9 natural 1.02, k9 tuned 1.00 |

## Réplication descriptive : « Hôte » du point 3 (machine 32, source non corrigée) et de ce point

| Langage | point 3 | point 4 |
|---|---|---|
| C | 1 (1.85) | 1 (2.86) |
| C++ | 2 (3.35) | 2 (3.04) |
| C3 | 3 (3.39) | 3 (3.15) |
| D | 6 (6.47) | 4 (4.84) |
| Odin | 4 (5.66) | 5 (5.74) |
| Zig | 8 (7.41) | 6 (6.27) |
| Rust | 7 (7.25) | 7 (6.99) |
| Nim | 5 (6.10) | 8 (7.03) |
| Ada | 10 (8.96) | 9 (9.72) |
| Chapel | 9 (8.08) | 10 (10.02) |
| Mojo | 12 (11.55) | 11 (10.75) |
| Swift | 11 (10.47) | 12 (10.96) |
| Fortran | 14 (12.74) | 13 (11.43) |
| Julia | 13 (12.09) | 14 (12.57) |
| C# | 15 (14.92) | 15 (15.27) |
| Java | 17 (16.72) | 16 (16.20) |
| FreePascal | 16 (16.51) | 17 (16.72) |
| Go | 18 (17.59) | 18 (17.83) |
| Haskell | 19 (18.93) | 19 (18.65) |
| OCaml | 20 (20.40) | 20 (20.38) |
| BQN | 21 (21.22) | 21 (21.14) |
| JavaScript | 23 (22.32) | 22 (22.30) |
| PHP | 22 (22.25) | 23 (22.33) |
| Python | 24 (24.13) | 24 (24.15) |
| Lua | 25 (24.65) | 25 (24.65) |

## Cellules


Processeur des enregistrements : 6/207/2 Intel(R) Xeon(R) Processor @ 2.10GHz (3096 enregistrements ; passes 0, 1, 2).

Processus écartés : 0 (toutes passes) ; vol de temps > 5 % après reprise : 0.
