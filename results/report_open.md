# v4, point 6 : la piste ouverte — résultats

*Plan : `docs/V4_OPEN.md` (sections 5 à 7, écarts de la section 10). Généré par `analysis/open_v4.py` à partir de `results/open/raw` (machine 34), du relevé `results/open/forms.json`, de la grille ouverte `results/open/grid_open.json` et des données du point 4 (machine 33). Le classement de tête du README ne change pas (section 8).*

Contrôle : « Convergent, avec R4 » refait par l'outil : même ordre que le point 4 = True ; écart maximal des rangs espérés 0, des scores au centre 0.

## Classements

| Langage | Convergent, avec R4 | Ouverte | Plafond ouvert seul | Grille ouverte seule | Bibliothèques nommées | Cases comblées à ½ | Report par le témoin C |
|---|---|---|---|---|---|---|---|
| C++ | 1 (2,45 ; 81,9) | 2 (2,76 ; 82,8) | 1 (2,46 ; 81,9) | 2 (2,75 ; 82,8) | 1 (2,71 ; 81,9) | 1 (2,48 ; 82,4) | 2 (2,76 ; 82,8) |
| Zig | 2 (2,87 ; 78,7) | 4 (3,83 ; 78,7) | 2 (2,87 ; 78,7) | 4 (3,83 ; 78,7) | 3 (3,23 ; 78,7) | 3 (3,17 ; 78,7) | 4 (3,84 ; 78,7) |
| C | 3 (2,88 ; 80,6) | 3 (3,17 ; 81,5) | 3 (2,88 ; 80,6) | 3 (3,17 ; 81,5) | 2 (3,16 ; 80,6) | 2 (2,95 ; 81,1) | 3 (3,18 ; 81,5) |
| C3 | 4 (5,19 ; 73,5) | 6 (6,31 ; 73,5) | 4 (5,20 ; 73,5) | 6 (6,31 ; 73,5) | 5 (5,72 ; 73,5) | 6 (5,76 ; 73,5) | 6 (6,32 ; 73,5) |
| Odin | 5 (5,39 ; 75,0) | 7 (6,46 ; 75,0) | 5 (5,39 ; 75,0) | 7 (6,46 ; 75,0) | 6 (5,88 ; 75,0) | 7 (5,90 ; 75,0) | 7 (6,48 ; 75,0) |
| Nim | 6 (5,50 ; 74,5) | 5 (5,66 ; 75,8) | 6 (5,51 ; 74,5) | 5 (5,66 ; 75,8) | 7 (5,98 ; 74,5) | 5 (5,43 ; 75,4) | 5 (5,67 ; 75,8) |
| Rust | 7 (6,51 ; 73,3) | 1 ** (2,65 ; 80,9) | 7 (6,48 ; 73,3) | 1 ** (2,67 ; 80,9) | 4 ** (3,56 ; 78,0) | 4 ** (4,81 ; 76,1) | 1 ** (2,67 ; 80,9) |
| D | 8 (7,18 ; 75,2) | 8 (7,08 ; 76,7) | 8 (7,19 ; 75,2) | 8 (7,08 ; 76,7) | 8 (7,57 ; 75,2) | 8 (7,26 ; 75,7) | 8 (6,97 ; 77,0) |
| Chapel | 9 (9,59 ; 69,0) | 9 (10,21 ; 69,0) | 9 (9,60 ; 69,0) | 9 (10,20 ; 69,0) | 9 (9,81 ; 69,0) | 9 (9,87 ; 69,0) | 9 (10,22 ; 69,0) |
| Ada | 10 (11,06 ; 70,7) | 10 (10,26 ; 73,5) | 10 (11,07 ; 70,7) | 10 (10,25 ; 73,5) | 12 (11,33 ; 70,7) | 10 (10,61 ; 72,1) | 10 (10,27 ; 73,5) |
| Fortran | 11 (11,13 ; 67,3) | 13 (11,63 ; 67,3) | 12 (11,14 ; 67,3) | 13 (11,62 ; 67,3) | 11 (11,31 ; 67,3) | 11 (11,33 ; 67,3) | 13 (11,63 ; 67,3) |
| Julia | 12 (11,18 ; 67,7) | 11 (11,15 ; 68,7) | 11 (11,13 ; 67,8) | 11 (11,21 ; 68,6) | 13 (11,40 ; 67,7) | 12 (11,38 ; 67,8) | 11 (11,22 ; 68,6) |
| Mojo | 13 (12,20 ; 67,3) | 12 (11,60 ; 69,5) | 13 (12,20 ; 67,3) | 12 (11,60 ; 69,5) | 10 ** (11,18 ; 69,5) | 13 (11,94 ; 68,2) | 12 (11,56 ; 69,6) |
| Swift | 14 (12,30 ; 67,0) | 14 (12,56 ; 67,4) | 14 (12,31 ; 67,0) | 14 (12,55 ; 67,4) | 14 (12,53 ; 67,0) | 14 (12,51 ; 67,0) | 14 (12,56 ; 67,4) |
| C# | 15 (14,87 ; 62,3) | 15 (15,06 ; 62,3) | 15 (14,87 ; 62,3) | 15 (15,06 ; 62,3) | 15 (14,93 ; 62,3) | 15 (14,95 ; 62,3) | 15 (15,06 ; 62,3) |
| Java | 16 (16,31 ; 55,3) | 16 (16,22 ; 57,2) | 16 (16,31 ; 55,3) | 16 (16,22 ; 57,2) | 16 (16,31 ; 55,3) | 16 (16,28 ; 56,2) | 16 (16,22 ; 57,2) |
| Go | 17 (17,30 ; 51,1) | 17 (17,01 ; 54,4) | 17 (17,29 ; 51,1) | 17 (17,02 ; 54,3) | 17 (17,30 ; 51,1) | 17 (17,13 ; 53,0) | 17 (17,02 ; 54,3) |
| FreePascal | 18 (17,39 ; 49,3) | 18 (17,72 ; 49,3) | 18 (17,40 ; 49,3) | 18 (17,72 ; 49,3) | 18 (17,39 ; 49,3) | 18 (17,55 ; 49,3) | 18 (17,72 ; 49,3) |
| Haskell | 19 (18,72 ; 44,7) | 19 (18,67 ; 46,5) | 19 (18,73 ; 44,7) | 19 (18,67 ; 46,5) | 19 (18,72 ; 44,7) | 19 (18,73 ; 45,1) | 19 (18,67 ; 46,5) |
| OCaml | 20 (20,25 ; 23,2) | 20 (20,11 ; 26,9) | 20 (20,25 ; 23,2) | 20 (20,11 ; 26,9) | 20 (20,25 ; 23,2) | 20 (20,14 ; 25,5) | 20 (20,11 ; 26,9) |
| BQN | 21 (21,44 ; 16,7) | 21 (21,78 ; 16,7) | 21 (21,45 ; 16,7) | 21 (21,76 ; 16,7) | 21 (21,46 ; 16,7) | 21 (21,67 ; 16,7) | 21 (21,79 ; 16,7) |
| JavaScript | 22 (22,13 ; 16,4) | 22 (21,97 ; 18,0) | 22 (22,16 ; 16,4) | 22 (21,95 ; 18,0) | 22 (22,17 ; 16,4) | 22 (22,00 ; 17,6) | 22 (21,97 ; 18,0) |
| PHP | 23 (22,33 ; 16,7) | 23 (22,36 ; 18,0) | 23 (22,35 ; 16,7) | 23 (22,34 ; 18,0) | 23 (22,36 ; 16,7) | 23 (22,35 ; 17,6) | 23 (22,36 ; 18,0) |
| Python | 24 (24,09 ; 12,3) | 24 (23,85 ; 14,8) | 24 (23,86 ; 13,3) | 24 (24,11 ; 13,8) | 24 (23,81 ; 13,7) | 24 (23,90 ; 13,8) | 24 (23,83 ; 14,9) |
| Lua | 25 (24,73 ; 5,8) | 25 (24,90 ; 7,4) | 25 (24,91 ; 6,0) | 25 (24,70 ; 7,2) | 25 (24,92 ; 5,8) | 25 (24,90 ; 7,0) | 25 (24,91 ; 7,4) |

Chaque case : place (rang espéré ; score au centre) ; ** : plus de deux places d'écart avec « Convergent, avec R4 ». Ordre des lignes : « Convergent, avec R4 ».

## Rangs plausibles (90 %)

| Langage | Convergent, avec R4 | Ouverte | Plafond ouvert seul | Grille ouverte seule | Bibliothèques nommées | Cases comblées à ½ | Report par le témoin C |
|---|---|---|---|---|---|---|---|
| C++ | 1–6 | 1–6 | 1–6 | 1–6 | 1–7 | 1–6 | 1–6 |
| Zig | 1–6 | 1–7 | 1–6 | 1–7 | 1–7 | 1–7 | 1–7 |
| C | 1–7 | 1–7 | 1–7 | 1–7 | 1–7 | 1–7 | 1–7 |
| C3 | 2–9 | 3–10 | 2–9 | 3–10 | 2–9 | 2–9 | 3–10 |
| Odin | 2–9 | 3–9 | 2–9 | 3–9 | 3–9 | 2–9 | 3–9 |
| Nim | 2–9 | 2–9 | 2–9 | 2–9 | 2–9 | 2–9 | 2–9 |
| Rust | 3–10 | 1–6 | 3–10 | 1–6 | 1–7 | 2–8 | 1–6 |
| D | 3–11 | 3–11 | 3–11 | 3–11 | 4–11 | 3–11 | 3–11 |
| Chapel | 5–14 | 6–14 | 5–14 | 6–14 | 6–14 | 6–14 | 6–14 |
| Ada | 7–14 | 6–14 | 7–14 | 6–14 | 8–14 | 7–14 | 6–14 |
| Fortran | 7–14 | 7–15 | 7–14 | 7–15 | 7–15 | 7–14 | 7–15 |
| Julia | 8–14 | 8–14 | 8–14 | 8–14 | 8–14 | 8–14 | 8–14 |
| Mojo | 9–14 | 8–14 | 9–14 | 8–14 | 8–14 | 9–14 | 8–14 |
| Swift | 9–14 | 10–14 | 9–14 | 10–14 | 9–15 | 10–15 | 10–14 |
| C# | 13–16 | 13–16 | 13–16 | 13–16 | 13–16 | 13–16 | 13–16 |
| Java | 15–18 | 15–18 | 15–18 | 15–18 | 15–18 | 15–18 | 15–18 |
| Go | 16–18 | 16–18 | 16–18 | 16–18 | 16–18 | 16–18 | 16–18 |
| FreePascal | 15–19 | 15–19 | 15–19 | 15–19 | 15–19 | 15–19 | 15–19 |
| Haskell | 18–19 | 18–19 | 18–19 | 18–19 | 18–19 | 18–19 | 18–19 |
| OCaml | 20–22 | 20–21 | 20–22 | 20–21 | 20–22 | 20–21 | 20–21 |
| BQN | 20–23 | 20–24 | 20–23 | 20–23 | 20–23 | 20–23 | 20–24 |
| JavaScript | 21–24 | 21–24 | 21–24 | 21–24 | 21–24 | 21–24 | 21–24 |
| PHP | 20–23 | 21–23 | 20–23 | 21–23 | 20–23 | 21–23 | 21–23 |
| Python | 23–25 | 22–25 | 22–25 | 22–25 | 22–25 | 22–25 | 22–25 |
| Lua | 24–25 | 24–25 | 24–25 | 24–25 | 24–25 | 24–25 | 24–25 |

## Langages qui bougent de plus de deux places par rapport à « Convergent, avec R4 »

* Ouverte : Rust 7e → 1e
* Plafond ouvert seul : aucun
* Grille ouverte seule : Rust 7e → 1e
* Bibliothèques nommées : Rust 7e → 4e, Mojo 13e → 10e
* Cases comblées à ½ : Rust 7e → 4e
* Report par le témoin C : Rust 7e → 1e

## Étages indicatifs (paires ordonnées dans au moins 95 % des variantes)

* Convergent, avec R4 : C++, Zig, C, C3, Odin, Nim, Rust, D, Chapel, Ada, Fortran, Julia, Mojo, Swift, C#, Java, Go, FreePascal, Haskell | OCaml, BQN, JavaScript, PHP, Python, Lua
* Ouverte : Rust, C++, C, Zig, Nim, C3, Odin, D, Chapel, Ada, Julia, Mojo, Fortran, Swift, C#, Java, Go, FreePascal, Haskell | OCaml, BQN, JavaScript, PHP, Python, Lua
* Plafond ouvert seul : C++, Zig, C, C3, Odin, Nim, Rust, D, Chapel, Ada, Julia, Fortran, Mojo, Swift, C#, Java, Go, FreePascal, Haskell | OCaml, BQN, JavaScript, PHP, Python, Lua
* Grille ouverte seule : Rust, C++, C, Zig, Nim, C3, Odin, D, Chapel, Ada, Julia, Mojo, Fortran, Swift, C#, Java, Go, FreePascal, Haskell | OCaml, BQN, JavaScript, PHP, Python, Lua
* Bibliothèques nommées : C++, C, Zig, Rust, C3, Odin, Nim, D, Chapel, Mojo, Fortran, Ada, Julia, Swift, C#, Java, Go, FreePascal, Haskell | OCaml, BQN, JavaScript, PHP, Python, Lua
* Cases comblées à ½ : C++, C, Zig, Rust, Nim, C3, Odin, D, Chapel, Ada, Fortran, Julia, Mojo, Swift, C#, Java, Go, FreePascal, Haskell | OCaml, BQN, JavaScript, PHP, Python, Lua
* Report par le témoin C : Rust, C++, C, Zig, Nim, C3, Odin, D, Chapel, Ada, Julia, Mojo, Fortran, Swift, C#, Java, Go, FreePascal, Haskell | OCaml, BQN, JavaScript, PHP, Python, Lua

## Report des formes op_* (machine 34 → données du point 4)

r : médiane sur les passes du rapport (forme op_*) / (forme d'accès) ; w : témoin de construction (forme d'accès dans op / dans cv) ; dénominateur cv si |w − 1| > 0,10 (écart 7) ; r par C : (forme op_*) / (forme de C de la cellule), sur la machine 34.

| Langage | Cellule | Forme | Bibliothèque | Forme d'accès | r (op) | r (cv) | w | r retenu | r par C | passes |
|---|---|---|---|---|---|---|---|---|---|---|
| Rust | K3 | op_cache_padded | cache-padded | sw_padded | 6,13 | 0,99 | 0,16 | 0,99 (cv) | 1,04 | 3 |
| Rust | K3 | op_crossbeam | crossbeam (nommée) | sw_padded | 6,14 | 0,99 | 0,16 | 0,99 (cv) | 1,05 | 3 |
| Rust | K3 | op_libc | libc (nommée) | sw_padded | 6,12 | 0,99 | 0,16 | 0,99 (cv) | 1,05 | 3 |
| Rust | K8 | op_bumpalo | bumpalo | tuned_it | 1,47 | 1,39 | 0,99 | 1,47 (op) | 1,34 | 3 |
| D | K1 | op_soa energy | soa | soa energy | 1,01 | 1,01 | 1,00 | 1,01 (op) | 0,99 | 3 |
| Ada | K3 | op_cachelines | cachelines | sw_padded | 1,00 | 0,90 | 0,89 | 0,90 (cv) | 0,18 | 3 |
| Julia | K8 | op_bumper | Bumper | tuned_it | 0,97 | 0,96 | 0,98 | 0,97 (op) | 1,00 | 3 |
| Mojo | K3 | op_max | MAX 26.7.0 (nommée) | sw_padded | 4,65 | 4,53 | 0,97 | 4,65 (op) | 1,05 | 3 |
| Mojo | Q6 mt | op_max q6 | MAX 26.7.0 (nommée) | mt q6 | 1,01 | 0,98 | 0,99 | 1,01 (op) | 1,10 | 3 |
| Mojo | Q1 mt | op_max q1 | MAX 26.7.0 (nommée) | mt_pool_v q1 | 0,98 | 1,10 | 1,04 | 0,98 (op) | 1,05 | 3 |
| Mojo | K9 mt | op_max | MAX 26.7.0 (nommée) | mt | 1,18 | 1,14 | 0,92 | 1,18 (op) | 1,40 | 3 |
| Swift | K8 | op_arena | swift-memory-allocation | tuned_it | 1,23 | 1,46 | 1,18 | 1,46 (cv) | 1,45 | 3 |
| Go | K3 | op_cpu | github.com/templexxx/cpu | rmw_padded | 0,98 | 1,03 | 1,02 | 0,98 (op) | 3,21 | 3 |
| Go | K9 | op_gonum | gonum.org/v1/gonum/mat | tuned_v | 12,21 | 12,22 | 1,04 | 12,21 (op) | 13,70 | 3 |
| Go | K9 mt | op_gonum_mt | gonum.org/v1/gonum/mat | mt_pool_v | 5,81 | 5,80 | 1,00 | 5,81 (op) | 7,75 | 3 |
| OCaml | K4 | op_intrinsics | ocaml_intrinsics_kernel | tuned | 7,10 | 7,37 | 0,96 | 7,10 (op) | 60,79 | 3 |
| OCaml | Q6 | op_intrinsics q6 | ocaml_intrinsics_kernel | tuned_s q6 | 1,05 | 0,98 | 0,91 | 1,05 (op) | 5,03 | 3 |
| OCaml | Q6 mt | op_intrinsics_mt q6 | ocaml_intrinsics_kernel | mt_pool_s q6 | 1,18 | 1,17 | 0,99 | 1,18 (op) | 14,03 | 3 |
| JavaScript | K8 | op_pool | @protobufjs/pool | tuned_it | 2,96 | 2,58 | 0,87 | 2,58 (cv) | 11,17 | 3 |
| PHP | Q6 mt | op_amphp q6 | amphp/parallel-functions | mt_pool_s q6 | 1,04 | 1,00 | 0,98 | 1,04 (op) | 18,41 | 3 |
| PHP | Q1 mt | op_amphp q1 | amphp/parallel-functions | mt q1 | 1,12 | 1,15 | 0,93 | 1,12 (op) | 13,86 | 3 |
| PHP | K9 mt | op_amphp | amphp/parallel-functions | mt | 24,16 | 24,01 | 1,03 | 24,16 (op) | 322,79 | 3 |
| Python | K1 | op_numpy energy | numpy (nommée) | soa energy | 0,10 | 0,11 | 1,05 | 0,10 (op) | 30,23 | 3 |
| Python | K3 | op_dask | dask | sw_padded | 11,31 | 11,33 | 0,93 | 11,31 (op) | 309,39 | 3 |
| Python | K4 | op_numpy | numpy (nommée) | tuned | 2,31 | 2,16 | 0,99 | 2,31 (op) | 211,44 | 3 |
| Python | K5 | op_numpy | numpy (nommée) | tuned | 0,01 | 0,01 | 0,98 | 0,01 (op) | 10,18 | 3 |
| Python | Q6 | op_numpy q6 | numpy (nommée) | rq_cols q6 | 0,11 | 0,12 | 1,08 | 0,11 (op) | 4,25 | 3 |
| Python | Q1 | op_numpy q1 | numpy (nommée) | tuned q1 | 0,19 | 0,18 | 0,94 | 0,19 (op) | 25,81 | 3 |
| Python | Q6 mt | op_dask_mt q6 | dask | rq_cols_mt q6 | 0,70 | 0,56 | 0,97 | 0,70 (op) | 31,81 | 3 |
| Python | Q6 mt | op_numpy_mt q6 | numpy (nommée) | rq_cols_mt q6 | 0,18 | 0,14 | 0,97 | 0,18 (op) | 8,27 | 3 |
| Python | Q1 mt | op_dask_mt q1 | dask | mt_pool q1 | 0,25 | 0,20 | 0,85 | 0,20 (cv) | 32,15 | 3 |
| Python | Q1 mt | op_numpy_mt q1 | numpy (nommée) | mt_pool q1 | 0,25 | 0,21 | 0,85 | 0,21 (cv) | 32,49 | 3 |
| Python | K9 | op_numpy | numpy (nommée) | natural | 0,07 | 0,08 | 1,15 | 0,08 (cv) | 7,96 | 3 |
| Python | K9 mt | op_dask_mt | dask | mt | 0,37 | 0,37 | 1,00 | 0,37 (op) | 54,25 | 3 |
| Python | K9 mt | op_numpy_mt | numpy (nommée) | mt | 0,04 | 0,04 | 1,00 | 0,04 (op) | 5,99 | 3 |
| Lua | K5 | op_vmsl | pessoa736/vmsl | tuned | 0,05 | 0,05 | 0,92 | 0,05 (op) | 23,69 | 3 |
| Lua | Q6 mt | op_llthreads2 q6 | moteus/lua-llthreads2 | rq_nest_mt q6 | 2,41 | 2,25 | 0,93 | 2,41 (op) | 434,63 | 3 |
| Lua | Q1 mt | op_llthreads2 q1 | moteus/lua-llthreads2 | mt q1 | 1,28 | 1,27 | 1,01 | 1,28 (op) | 205,64 | 3 |
| Lua | K9 | op_vmsl | pessoa736/vmsl | natural | 4,85 | 5,05 | 1,01 | 4,85 (op) | 177,54 | 3 |
| Lua | K9 mt | op_llthreads2 | moteus/lua-llthreads2 | rq_slide_mt | 1,28 | 1,30 | 1,01 | 1,28 (op) | 184,00 | 3 |

## Forme retenue par cellule (« Ouverte », estimation centrale)

Chaque case : forme retenue et rapport de son temps à celui de la forme d'accès du point 4 (1,00 : la forme d'accès reste).

| Langage | Cellule | Forme d'accès | Forme retenue | Rapport |
|---|---|---|---|---|
| Rust | K3 | sw_padded | op_cache_padded | 0,99 |
| Rust | K8 | tuned_it | tuned_it | 1,00 |
| D | K1 | soa energy | soa energy | 1,00 |
| Ada | K3 | sw_padded | op_cachelines | 1,00 |
| Julia | K8 | tuned_it | op_bumper | 0,97 |
| Mojo | K3 | sw_padded | op_max | 1,00 |
| Mojo | Q6 mt | mt q6 | mt q6 | 1,00 |
| Mojo | Q1 mt | mt_pool_v q1 | op_max q1 | 0,98 |
| Mojo | K9 mt | mt | mt | 1,00 |
| Swift | K8 | tuned_it | tuned_it | 1,00 |
| Go | K3 | rmw_padded | op_cpu | 0,98 |
| Go | K9 | tuned_v | tuned_v | 1,00 |
| Go | K9 mt | mt_pool_v | mt_pool_v | 1,00 |
| OCaml | K4 | tuned | tuned | 1,00 |
| OCaml | Q6 | tuned_s q6 | tuned_s q6 | 1,00 |
| OCaml | Q6 mt | mt_pool_s q6 | mt_pool_s q6 | 1,00 |
| JavaScript | K8 | tuned_it | tuned_it | 1,00 |
| PHP | Q6 mt | mt_pool_s q6 | mt_pool_s q6 | 1,00 |
| PHP | Q1 mt | mt q1 | mt q1 | 1,00 |
| PHP | K9 mt | mt | mt | 1,00 |
| Python | K1 | soa energy | op_numpy energy | 0,10 |
| Python | K3 | sw_padded | sw_padded | 1,00 |
| Python | K4 | tuned | tuned | 1,00 |
| Python | K5 | tuned | op_numpy | 0,01 |
| Python | Q6 | rq_cols q6 | op_numpy q6 | 0,11 |
| Python | Q1 | tuned q1 | op_numpy q1 | 0,19 |
| Python | Q6 mt | rq_cols_mt q6 | op_numpy_mt q6 | 0,18 |
| Python | Q1 mt | mt_pool q1 | op_dask_mt q1 | 0,20 |
| Python | K9 | natural | op_numpy | 0,08 |
| Python | K9 mt | mt | op_numpy_mt | 0,04 |
| Lua | K5 | tuned | op_vmsl | 0,05 |
| Lua | Q6 mt | rq_nest_mt q6 | rq_nest_mt q6 | 1,00 |
| Lua | Q1 mt | mt q1 | mt q1 | 1,00 |
| Lua | K9 | natural | natural | 1,00 |
| Lua | K9 mt | rq_slide_mt | rq_slide_mt | 1,00 |

## Grille ouverte : cases comblées

Chaque case : capacité, note publiée → note ouverte (note des seules bibliothèques nommées) ; une case dont la note ne monte pas (bibliothèque limitée) garde sa note publiée.

* C++ : F2 0,0 → 1,0 (0,0)
* C : F2 0,0 → 1,0 (0,0)
* Nim : C1 0,0 → 0,5 (0,0), F1 0,5 → 1,0 (0,5)
* Rust : B2 0,5 → 1,0 (0,5), C1 0,5 → 1,0 (0,5), C5 0,0 → 1,0 (1,0), D3 0,0 → 1,0 (1,0), D4 0,0 → 1,0 (1,0), F1 0,5 → 1,0 (0,5), F2 0,0 → 1,0 (0,0), F4 0,0 → 1,0 (1,0)
* D : A6 0,0 → 1,0 (0,0), F1 0,5 → 1,0 (0,5)
* Ada : C5 0,0 → 1,0 (0,0), D3 0,0 → 1,0 (0,0)
* Julia : B2 0,5 → 0,5 (0,5), C1 0,5 → 0,5 (0,5), D4 0,5 → 1,0 (0,5), F2 0,5 → 1,0 (0,5)
* Mojo : C5 0,0 → 1,0 (1,0), D1 0,5 → 0,5 (0,5), F1 0,5 → 1,0 (1,0)
* Swift : B2 0,5 → 0,5 (0,5), F1 0,5 → 1,0 (0,5)
* Java : D4 0,0 → 1,0 (0,0), F1 0,5 → 1,0 (0,5), F2 0,0 → 0,5 (0,0)
* Go : C5 0,0 → 0,5 (0,0), D3 0,0 → 1,0 (0,0), F1 0,5 → 1,0 (0,5), F2 0,0 → 1,0 (0,0)
* Haskell : C5 0,5 → 1,0 (0,5), D2 0,5 → 0,5 (0,5), F4 0,0 → 1,0 (0,0)
* OCaml : C2 0,0 → 0,5 (0,0), C5 0,0 → 1,0 (0,0), D4 0,0 → 1,0 (0,0)
* JavaScript : B2 0,0 → 0,5 (0,0), F1 0,0 → 1,0 (0,0)
* PHP : C5 0,0 → 0,5 (0,0), F1 0,5 → 1,0 (0,5)
* Python : C5 0,5 → 0,5 (0,5), D2 0,0 → 1,0 (0,0), F1 0,5 → 1,0 (1,0)
* Lua : D1 0,0 → 0,5 (0,0), F1 0,0 → 1,0 (0,0)

## Calcul 7 (information) : coût d'accès des formes op_*

L : lignes de code de la forme (outil et règles de lecture du point 5) ; N : la référence naturelle de la cellule ; s = max(0 ; 1 − N / L).

| Langage | Cellule | Forme | L | s | Forme d'accès : L | s |
|---|---|---|---|---|---|---|
| Rust | K3 | op_cache_padded | 12 | 0,00 | 22 | 0,00 |
| Rust | K3 | op_crossbeam | 11 | 0,00 | 22 | 0,00 |
| Rust | K3 | op_libc | 15 | 0,00 | 22 | 0,00 |
| Rust | K8 | op_bumpalo | 56 | 0,82 | 54 | 0,81 |
| D | K1 | op_soa energy | 25 | 0,80 | 25 | 0,80 |
| Ada | K3 | op_cachelines | 28 | 0,00 | 57 | 0,00 |
| Julia | K8 | op_bumper | 39 | 0,72 | 35 | 0,69 |
| Mojo | K3 | op_max | 6 | 0,00 | 16 | 0,00 |
| Mojo | Q6 mt | op_max q6 | 31 | 0,77 | 34 | 0,79 |
| Mojo | Q1 mt | op_max q1 | 67 | 0,82 | 66 | 0,82 |
| Mojo | K9 mt | op_max | 21 | 0,43 | 26 | 0,54 |
| Swift | K8 | op_arena | 66 | 0,71 | 53 | 0,64 |
| Go | K3 | op_cpu | 20 | 0,00 | 30 | 0,13 |
| Go | K9 | op_gonum | 8 | 0,00 | 26 | 0,50 |
| Go | K9 mt | op_gonum_mt | 17 | 0,24 | 39 | 0,67 |
| OCaml | K4 | op_intrinsics | 8 | 0,12 | 19 | 0,63 |
| OCaml | Q6 | op_intrinsics q6 | 9 | 0,22 | 9 | 0,22 |
| OCaml | Q6 mt | op_intrinsics_mt q6 | 54 | 0,87 | 53 | 0,87 |
| JavaScript | K8 | op_pool | 24 | 0,92 | 20 | 0,90 |
| PHP | Q6 mt | op_amphp q6 | 30 | 0,67 | 62 | 0,84 |
| PHP | Q1 mt | op_amphp q1 | 37 | 0,57 | 70 | 0,77 |
| PHP | K9 mt | op_amphp | 36 | 0,44 | 107 | 0,81 |
| Python | K1 | op_numpy energy | 3 | 0,00 | 4 | 0,00 |
| Python | K3 | op_dask | 7 | 0,00 | 37 | 0,00 |
| Python | K4 | op_numpy | 1 | 0,00 | 3 | 0,00 |
| Python | K5 | op_numpy | 1 | 0,00 | 1 | 0,00 |
| Python | Q6 | op_numpy q6 | 5 | 0,00 | 19 | 0,63 |
| Python | Q1 | op_numpy q1 | 13 | 0,00 | 12 | 0,00 |
| Python | Q6 mt | op_dask_mt q6 | 5 | 0,00 | 82 | 0,91 |
| Python | Q6 mt | op_numpy_mt q6 | 36 | 0,81 | 82 | 0,91 |
| Python | Q1 mt | op_dask_mt q1 | 21 | 0,38 | 74 | 0,82 |
| Python | Q1 mt | op_numpy_mt q1 | 44 | 0,70 | 74 | 0,82 |
| Python | K9 | op_numpy | 8 | 0,38 | 5 | 0,00 |
| Python | K9 mt | op_dask_mt | 7 | 0,29 | 44 | 0,89 |
| Python | K9 mt | op_numpy_mt | 37 | 0,86 | 44 | 0,89 |
| Lua | K5 | op_vmsl | 2 | 0,00 | 7 | 0,29 |
| Lua | Q6 mt | op_llthreads2 q6 | 60 | 0,87 | 13 | 0,38 |
| Lua | Q1 mt | op_llthreads2 q1 | 73 | 0,84 | 15 | 0,20 |
| Lua | K9 | op_vmsl | 14 | 0,50 | 7 | 0,00 |
| Lua | K9 mt | op_llthreads2 | 64 | 0,89 | 11 | 0,36 |

b3 du point 4 (machine 33) : 85,12 ms ; machine 34 : start 68,95, 69,80 ; end 69,75, 69,40 ms.

Processeur des enregistrements : 6/207/2 Intel(R) Xeon(R) Processor @ 2.10GHz (363). Processus écartés : 0.
