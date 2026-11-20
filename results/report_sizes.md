# v4, point 2 : trois tailles par noyau — résultats

*Plan : `docs/V4_SIZES.md` (sections 6 à 8, écart 4.1). Généré par `analysis/sizes_v4.py` à partir de `results/sizes/raw` (machine 31). Le classement de tête du README ne change pas au point 2 (section 9).*

## Classements

| Langage | Publié | Hôte | Trois tailles | Taille petite | Taille publiée | Taille grande |
|---|---|---|---|---|---|---|
| C++ | 3 (3.79 ; 77.1) | 2 (2.83 ; 69.5) | 1 (2.37 ; 70.9) | 1 (2.58 ; 67.0) | 3 (3.05 ; 69.6) | 1 (1.86 ; 77.3) |
| C | 1 (2.20 ; 80.0) | 1 (2.54 ; 68.6) | 2 (2.84 ; 68.7) | 2 (2.72 ; 65.5) | 1 (2.64 ; 68.9) | 3 (4.08 ; 72.6) |
| C3 | 4 (5.11 ; 71.6) | 3 (2.99 ; 65.8) | 3 (3.51 ; 66.1) | 3 (4.77 ; 60.4) | 2 (2.85 ; 66.7) | 2 (3.75 ; 72.4) |
| Odin | 2 (3.17 ; 74.0) | 6 (6.83 ; 60.6) | 4 (5.69 ; 62.3) | 4 (5.40 ; 58.8) | 6 (6.75 ; 61.3) | 5 (5.38 ; 68.1) |
| Nim | 7 (7.17 ; 69.3) | 4 (5.53 ; 63.6) | 5 (6.09 ; 64.4) | 6 (6.59 ; 60.4) | 4 (5.71 ; 64.0) | 6 (6.15 ; 69.8) |
| D | 8 (7.19 ; 72.7) | 5 (6.31 ; 65.6) | 6 (6.43 ; 66.6) | 7 (6.99 ; 61.9) | 5 (6.00 ; 66.7) | 7 (6.62 ; 72.1) |
| Zig | 5 (5.13 ; 72.3) | 8 (7.61 ; 60.4) | 7 (7.70 ; 61.4) | 10 (9.84 ; 55.5) | 8 (7.49 ; 61.1) | 4 (4.79 ; 69.8) |
| Rust | 6 (6.96 ; 70.0) | 7 (7.15 ; 59.2) | 8 (7.76 ; 60.0) | 8 (7.52 ; 56.9) | 7 (7.47 ; 59.5) | 9 (8.57 ; 64.6) |
| Chapel | 10 (9.29 ; 65.7) | 11 (9.45 ; 55.8) | 9 (8.47 ; 58.1) | 5 (6.40 ; 56.7) | 10 (9.27 ; 56.7) | 10 (10.29 ; 61.5) |
| Ada | 9 (8.30 ; 71.1) | 9 (9.25 ; 60.3) | 10 (10.32 ; 60.1) | 14 (12.28 ; 53.6) | 9 (9.02 ; 61.3) | 8 (8.08 ; 68.4) |
| Swift | 12 (10.86 ; 66.5) | 10 (9.30 ; 58.9) | 11 (10.65 ; 58.4) | 12 (10.45 ; 54.9) | 11 (9.54 ; 59.2) | 14 (11.75 ; 61.9) |
| Mojo | 14 (13.08 ; 62.3) | 12 (10.93 ; 56.8) | 12 (10.98 ; 58.3) | 11 (10.33 ; 55.6) | 12 (11.31 ; 56.9) | 11 (11.22 ; 63.3) |
| Fortran | 11 (10.85 ; 65.4) | 14 (12.88 ; 51.8) | 13 (11.05 ; 56.3) | 9 (8.79 ; 55.9) | 14 (12.62 ; 53.1) | 12 (11.42 ; 61.2) |
| Julia | 13 (12.15 ; 62.4) | 13 (11.78 ; 54.5) | 14 (11.44 ; 56.5) | 13 (10.80 ; 53.5) | 13 (11.61 ; 55.5) | 13 (11.68 ; 61.5) |
| C# | 15 (15.30 ; 54.9) | 15 (15.14 ; 48.2) | 15 (15.30 ; 48.6) | 15 (15.15 ; 44.9) | 15 (15.24 ; 48.5) | 16 (15.66 ; 54.5) |
| FreePascal | 16 (16.74 ; 48.1) | 17 (16.52 ; 43.9) | 16 (16.22 ; 45.8) | 16 (16.20 ; 41.2) | 17 (16.51 ; 45.4) | 15 (15.61 ; 55.2) |
| Java | 17 (16.96 ; 47.2) | 16 (16.36 ; 42.5) | 17 (16.69 ; 42.0) | 17 (16.96 ; 36.2) | 16 (16.51 ; 43.0) | 17 (16.34 ; 50.8) |
| Go | 18 (17.14 ; 45.4) | 18 (17.69 ; 38.4) | 18 (17.56 ; 40.2) | 18 (17.42 ; 35.9) | 18 (17.44 ; 40.8) | 18 (17.79 ; 45.6) |
| Haskell | 19 (18.62 ; 41.8) | 19 (18.94 ; 32.4) | 19 (18.98 ; 33.3) | 19 (18.92 ; 30.1) | 19 (19.00 ; 32.7) | 19 (18.97 ; 38.6) |
| OCaml | 20 (20.31 ; 23.9) | 20 (20.35 ; 20.5) | 20 (20.32 ; 21.7) | 20 (20.56 ; 21.1) | 20 (20.32 ; 21.1) | 20 (20.16 ; 25.9) |
| BQN | 21 (21.17 ; 17.7) | 21 (21.12 ; 16.2) | 21 (21.29 ; 16.5) | 21 (20.92 ; 16.8) | 21 (21.14 ; 16.5) | 21 (21.95 ; 16.2) |
| PHP | 22 (22.32 ; 16.6) | 22 (22.24 ; 15.8) | 22 (22.26 ; 16.3) | 23 (22.39 ; 15.7) | 22 (22.26 ; 16.0) | 23 (22.08 ; 17.6) |
| JavaScript | 23 (22.34 ; 15.6) | 23 (22.47 ; 14.0) | 23 (22.33 ; 15.1) | 22 (22.38 ; 15.0) | 23 (22.44 ; 14.3) | 22 (21.97 ; 17.5) |
| Python | 24 (24.26 ; 11.8) | 24 (24.20 ; 12.0) | 24 (24.17 ; 12.3) | 24 (23.98 ; 12.4) | 24 (24.21 ; 12.0) | 24 (24.22 ; 12.7) |
| Lua | 25 (24.58 ; 5.4) | 25 (24.58 ; 5.7) | 25 (24.60 ; 6.0) | 25 (24.67 ; 6.1) | 25 (24.57 ; 5.8) | 25 (24.60 ; 6.4) |

Chaque case : place (rang espéré ; score au centre). Ordre des lignes : « Trois tailles ». « Publié » : le classement de tête du README (`results/audit3.json`), calculé sur les données publiées (Cascade Lake, et Emerald Rapids pour K5, K9 et les latences de K8).

## Étages indicatifs (paires ordonnées dans au moins 95 % des variantes)

* Publié (règle v3, avec sa condition de réplication) : C, Odin, C++, C3, Zig, Rust, Nim, D, Ada, Chapel, Fortran, Swift, Julia, Mojo | C#, FreePascal, Java, Go, Haskell | OCaml, BQN, PHP, JavaScript, Python, Lua
* Hôte : C, C++, C3, Nim, D, Odin, Rust, Zig, Ada, Swift, Chapel, Mojo, Julia, Fortran, C#, Java, FreePascal, Go | Haskell | OCaml, BQN, PHP, JavaScript, Python, Lua
* Trois tailles : C++, C, C3, Odin, Nim, D, Zig, Rust, Chapel, Ada, Swift, Mojo, Fortran, Julia | C#, FreePascal, Java, Go | Haskell | OCaml, BQN, PHP, JavaScript, Python, Lua
* Taille petite : C++, C, C3, Odin, Chapel, Nim, D, Rust, Fortran, Zig, Mojo, Swift, Julia, Ada | C#, FreePascal, Java, Go, Haskell | OCaml, BQN, JavaScript, PHP, Python, Lua
* Taille publiée : C, C3, C++, Nim, D, Odin, Rust, Zig, Ada, Chapel, Swift, Mojo, Julia, Fortran, C#, Java, FreePascal, Go | Haskell | OCaml, BQN, PHP, JavaScript, Python, Lua
* Taille grande : C++, C3, C, Zig, Odin, Nim, D, Ada, Rust, Chapel, Mojo, Fortran, Julia, Swift, FreePascal, C#, Java, Go | Haskell | OCaml, BQN, JavaScript, PHP, Python, Lua

## Rangs qui bougent de plus de deux places entre « Hôte » et « Trois tailles » (effet des tailles)

* aucun

## Rangs qui bougent de plus de deux places entre « Publié » et « Hôte » (effet de l'hôte et du nouveau code)

* Nim : 7e → 4e
* D : 8e → 5e
* Odin : 2e → 6e
* Zig : 5e → 8e
* Fortran : 11e → 14e

## Cellules manquantes (temps le plus lent des autres langages)

* Hôte : aucune
* petite : aucune
* publiée : aucune
* grande : BQN ('k1', 'aos', 'energy'), Python ('k1', 'natural', 'energy'), BQN ('k1', 'natural', 'energy'), Python ('k1', 'natural_shuffled', 'energy'), BQN ('k1', 'natural_shuffled', 'energy'), BQN ('k1', 'soa', 'energy')

## Contrôle des anciens binaires (Odin, Chapel, Go, taille publiée)

115 cellules ; écart de plus de 5 % : 41 ; processus séparés (tous ceux d'une construction plus lents que tous ceux de l'autre, descriptif) : 3, dont 2 au-delà de 5 %. Médianes des processus en secondes, une par passe.

| Cellule | nouveau / ancien | processus nouveaux | processus anciens | séparés |
|---|---|---|---|---|
| chapel|k10|natural| | 1.001 | 1.6, 1.622, 1.662 | 1.563, 1.715, 1.606 |  |
| chapel|k10|tuned| | 1.192 **> 5 %** | 0.04939, 0.04555, 0.04563 | 0.05801, 0.0462, 0.0226 |  |
| chapel|k1|aos|energy | 1.013 | 0.02005, 0.02773, 0.02093 | 0.01985, 0.02224, 0.02539 |  |
| chapel|k1|natural_shuffled|energy | 1.027 | 0.02952, 0.04172, 0.03126 | 0.02916, 0.03149, 0.03873 |  |
| chapel|k1|natural|energy | 0.993 | 0.02842, 0.03629, 0.03123 | 0.02898, 0.03041, 0.03729 |  |
| chapel|k1|soa|energy | 1.223 **> 5 %** | 0.002423, 0.004977, 0.002427 | 0.002432, 0.002395, 0.002745 |  |
| chapel|k2|tuned|16384 | 0.990 | 0.00714, 0.007411, 0.00756 | 0.0073, 0.007614, 0.007417 |  |
| chapel|k2|tuned|16777216 | 1.020 | 0.4991, 0.5509, 0.6131 | 0.5284, 0.5472, 0.5495 |  |
| chapel|k2|tuned|2097152 | 0.967 | 0.1066, 0.108, 0.08465 | 0.08965, 0.1234, 0.09747 |  |
| chapel|k2|tuned|262144 | 0.986 | 0.02313, 0.02379, 0.02392 | 0.023, 0.02469, 0.02422 |  |
| chapel|k2|tuned|268435456 | 1.079 **> 5 %** | 0.5793, 0.6547, 0.7618 | 0.6139, 0.5909, 0.6333 |  |
| chapel|k2|tuned|33554432 | 1.024 | 0.5352, 0.5641, 0.6354 | 0.5574, 0.5814, 0.5508 |  |
| chapel|k2|tuned|524288 | 0.990 | 0.02584, 0.02732, 0.02699 | 0.02637, 0.02814, 0.02649 |  |
| chapel|k2|tuned|65536 | 1.000 | 0.02313, 0.0237, 0.02365 | 0.02326, 0.02356, 0.02368 |  |
| chapel|k2|tuned|67108864 | 1.050 **> 5 %** | 0.5399, 0.5787, 0.6725 | 0.5596, 0.5665, 0.5722 |  |
| chapel|k2|tuned|8388608 | 0.752 **> 5 %** | 0.1597, 0.1653, 0.1769 | 0.1595, 0.4423, 0.1556 |  |
| chapel|k3|rmw_packed| | 1.008 | 2.538, 2.554, 2.57 | 2.452, 2.593, 2.561 |  |
| chapel|k3|rmw_padded| | 1.035 | 0.2495, 0.2504, 0.2306 | 0.2272, 0.2384, 0.2399 |  |
| chapel|k3|sw_packed| | 1.013 | 0.09761, 0.0991, 0.09702 | 0.0935, 0.09663, 0.09994 |  |
| chapel|k3|sw_padded| | 1.005 | 0.08997, 0.08779, 0.08873 | 0.08851, 0.08814, 0.08837 |  |
| chapel|k4|branchless_unsorted| | 0.975 | 0.001121, 0.001163, 0.001171 | 0.001138, 0.001237, 0.001169 |  |
| chapel|k4|natural_sorted| | 1.001 | 0.00148, 0.001527, 0.001508 | 0.001457, 0.00153, 0.001526 |  |
| chapel|k4|natural_unsorted| | 0.971 | 0.001474, 0.001551, 0.001518 | 0.001515, 0.00161, 0.001553 |  |
| chapel|k5|natural| | 0.974 | 0.1913, 0.1855, 0.1848 | 0.1926, 0.1968, 0.1875 |  |
| chapel|k5|tuned| | 0.944 **> 5 %** | 0.004571, 0.004466, 0.004481 | 0.004625, 0.005208, 0.004516 |  |
| chapel|k6|mt|q1 | 1.155 **> 5 %** | 0.008772, 0.01916, 0.01012 | 0.009902, 0.01196, 0.009327 |  |
| chapel|k6|mt|q6 | 1.545 **> 5 %** | 0.001717, 0.007134, 0.001887 | 0.001827, 0.001996, 0.001719 |  |
| chapel|k6|natural|q1 | 1.089 **> 5 %** | 0.06271, 0.08739, 0.06274 | 0.06267, 0.06275, 0.06765 |  |
| chapel|k6|natural|q6 | 1.021 | 0.05115, 0.06334, 0.052 | 0.05178, 0.05885, 0.05192 |  |
| chapel|k6|tuned|q1 | 1.083 **> 5 %** | 0.0351, 0.05708, 0.03598 | 0.03506, 0.04484, 0.03613 |  |
| chapel|k6|tuned|q6 | 1.108 **> 5 %** | 0.01239, 0.02182, 0.01466 | 0.0138, 0.01456, 0.01451 |  |
| chapel|k7|natural| | 0.924 **> 5 %** | 0.798, 0.98, 0.9508 | 0.9769, 0.9138, 1.057 |  |
| chapel|k7|tuned| | 0.991 | 0.1348, 0.1396, 0.1452 | 0.1441, 0.138, 0.1412 |  |
| chapel|k8|natural| | 1.025 | 1.141, 1.409, 1.156 | 1.287, 1.229, 1.09 |  |
| chapel|k8|tuned| | 0.963 | 0.3413, 0.3022, 0.3344 | 0.329, 0.3478, 0.3376 |  |
| chapel|k9|mt| | 0.921 **> 5 %** | 0.00526, 0.003302, 0.002881 | 0.003801, 0.005501, 0.003066 |  |
| chapel|k9|natural| | 0.998 | 0.03619, 0.01361, 0.01155 | 0.02291, 0.0207, 0.01207 |  |
| chapel|k9|tuned| | 1.088 **> 5 %** | 0.03096, 0.01312, 0.01139 | 0.01889, 0.01601, 0.01187 |  |
| go|k10|natural| | 1.006 | 0.4114, 0.4609, 0.4737 | 0.4361, 0.4796, 0.4217 |  |
| go|k10|tuned| | 1.003 | 0.4907, 0.489, 0.4419 | 0.4924, 0.4865, 0.4394 |  |
| go|k1|aos|energy | 0.949 **> 5 %** | 1.363, 1.305, 1.206 | 1.337, 1.347, 1.394 |  |
| go|k1|natural_shuffled|energy | 1.083 **> 5 %** | 1.99, 2.13, 2.039 | 1.929, 2.15, 1.638 |  |
| go|k1|natural|energy | 1.195 **> 5 %** | 2.033, 2.022, 2.025 | 1.983, 1.241, 1.985 | oui |
| go|k1|soa|energy | 0.993 | 0.002401, 0.002425, 0.002371 | 0.002407, 0.002412, 0.002429 |  |
| go|k2|tuned|16384 | 0.980 | 0.007162, 0.007443, 0.007442 | 0.00726, 0.007667, 0.00758 |  |
| go|k2|tuned|16777216 | 0.905 **> 5 %** | 0.5153, 0.5444, 0.5876 | 0.5604, 0.5427, 0.7324 |  |
| go|k2|tuned|2097152 | 1.061 **> 5 %** | 0.08128, 0.09939, 0.08456 | 0.06387, 0.07601, 0.1179 |  |
| go|k2|tuned|262144 | 0.974 | 0.02311, 0.024, 0.02433 | 0.02383, 0.02403, 0.02552 |  |
| go|k2|tuned|268435456 | 0.953 | 0.5995, 0.6294, 0.6523 | 0.5867, 0.6219, 0.7801 |  |
| go|k2|tuned|33554432 | 0.899 **> 5 %** | 0.5564, 0.5615, 0.5749 | 0.5526, 0.5928, 0.7543 |  |
| go|k2|tuned|524288 | 0.965 | 0.02614, 0.0265, 0.02666 | 0.02571, 0.02635, 0.03033 |  |
| go|k2|tuned|65536 | 0.990 | 0.02282, 0.02377, 0.02392 | 0.02321, 0.02365, 0.02433 |  |
| go|k2|tuned|67108864 | 0.920 **> 5 %** | 0.5528, 0.5571, 0.5905 | 0.5707, 0.5979, 0.6844 |  |
| go|k2|tuned|8388608 | 0.285 **> 5 %** | 0.1557, 0.1645, 0.1597 | 0.5305, 0.5255, 0.6345 | oui |
| go|k3|rmw_packed| | 0.985 | 2.676, 2.687, 2.832 | 2.756, 2.771, 2.788 |  |
| go|k3|rmw_padded| | 0.983 | 0.2686, 0.2505, 0.2385 | 0.2779, 0.2469, 0.2466 |  |
| go|k3|sw_packed| | 1.007 | 4.037, 3.761, 3.974 | 3.886, 4.025, 3.774 |  |
| go|k3|sw_padded| | 1.021 | 0.4242, 0.4218, 0.405 | 0.4424, 0.405, 0.3802 |  |
| go|k4|branchless_unsorted| | 1.031 | 0.01163, 0.0132, 0.01217 | 0.01148, 0.01251, 0.01188 |  |
| go|k4|natural_sorted| | 1.005 | 0.01171, 0.0122, 0.01208 | 0.01154, 0.01238, 0.01188 |  |
| go|k4|natural_unsorted| | 0.994 | 0.01153, 0.01208, 0.01212 | 0.01131, 0.01288, 0.0118 |  |
| go|k5|natural| | 0.998 | 0.1014, 0.09537, 0.09512 | 0.09691, 0.101, 0.09445 |  |
| go|k5|tuned| | 1.019 | 0.01967, 0.019, 0.01894 | 0.01924, 0.0185, 0.01881 |  |
| go|k6|mt|q1 | 1.031 | 0.01674, 0.02665, 0.02746 | 0.01559, 0.02724, 0.02634 |  |
| go|k6|mt|q6 | 1.182 **> 5 %** | 0.002168, 0.003432, 0.003477 | 0.002117, 0.002548, 0.002904 |  |
| go|k6|natural|q1 | 1.011 | 0.07357, 0.08278, 0.076 | 0.07602, 0.07683, 0.07679 |  |
| go|k6|natural|q6 | 1.013 | 0.1293, 0.1445, 0.1344 | 0.1333, 0.1373, 0.1319 |  |
| go|k6|tuned|q1 | 0.986 | 0.05705, 0.05971, 0.0574 | 0.05784, 0.05907, 0.05971 |  |
| go|k6|tuned|q6 | 1.026 | 0.01358, 0.01721, 0.01711 | 0.01469, 0.01518, 0.0166 |  |
| go|k7|natural| | 1.009 | 1.366, 1.676, 1.308 | 1.524, 1.505, 1.27 |  |
| go|k7|tuned| | 1.005 | 0.1856, 0.2059, 0.1846 | 0.182, 0.2085, 0.1832 |  |
| go|k8|natural| | 0.991 | 1.006, 1.126, 0.9947 | 1.019, 1.157, 0.9832 |  |
| go|k8|tuned| | 0.934 **> 5 %** | 0.2424, 0.2478, 0.2212 | 0.2303, 0.2969, 0.2384 |  |
| go|k9|mt| | 1.031 | 0.008119, 0.009971, 0.008348 | 0.007783, 0.008927, 0.008874 |  |
| go|k9|natural| | 1.018 | 0.03949, 0.04293, 0.03806 | 0.03746, 0.03934, 0.04149 |  |
| go|k9|tuned| | 1.049 | 0.02257, 0.03096, 0.02537 | 0.02322, 0.02659, 0.02488 |  |
| odin|k10|natural| | 0.984 | 1.197, 1.218, 1.265 | 1.348, 1.197, 1.2 |  |
| odin|k10|tuned| | 1.180 **> 5 %** | 0.09091, 0.07442, 0.0673 | 0.0716, 0.04858, 0.07958 |  |
| odin|k1|aos|energy | 1.088 **> 5 %** | 0.02785, 0.02813, 0.03532 | 0.02781, 0.02864, 0.02694 |  |
| odin|k1|natural_shuffled|energy | 1.115 **> 5 %** | 0.03307, 0.03444, 0.0429 | 0.03264, 0.03322, 0.03248 |  |
| odin|k1|natural|energy | 1.098 **> 5 %** | 0.03358, 0.03329, 0.04289 | 0.03326, 0.03367, 0.03236 |  |
| odin|k1|soa|energy | 1.204 **> 5 %** | 0.003009, 0.002702, 0.005407 | 0.003597, 0.002583, 0.00271 |  |
| odin|k2|tuned|16384 | 1.004 | 0.007335, 0.007528, 0.007427 | 0.007274, 0.007472, 0.007449 |  |
| odin|k2|tuned|16777216 | 1.015 | 0.5345, 0.5415, 0.62 | 0.5247, 0.5498, 0.5945 |  |
| odin|k2|tuned|2097152 | 1.326 **> 5 %** | 0.0772, 0.106, 0.1379 | 0.08243, 0.0763, 0.07697 |  |
| odin|k2|tuned|262144 | 1.043 | 0.0232, 0.02545, 0.0259 | 0.02358, 0.02378, 0.02403 |  |
| odin|k2|tuned|268435456 | 0.995 | 0.6019, 0.6343, 0.6424 | 0.6103, 0.687, 0.5934 |  |
| odin|k2|tuned|33554432 | 1.063 **> 5 %** | 0.551, 0.5651, 0.6857 | 0.5445, 0.5677, 0.5742 |  |
| odin|k2|tuned|524288 | 1.039 | 0.02584, 0.02674, 0.03176 | 0.02611, 0.02799, 0.02677 |  |
| odin|k2|tuned|65536 | 1.003 | 0.02302, 0.02398, 0.02401 | 0.02345, 0.0237, 0.02363 |  |
| odin|k2|tuned|67108864 | 1.070 **> 5 %** | 0.5632, 0.5747, 0.7502 | 0.5507, 0.6416, 0.5614 |  |
| odin|k2|tuned|8388608 | 1.051 **> 5 %** | 0.1543, 0.1561, 0.6223 | 0.1546, 0.5174, 0.1612 |  |
| odin|k3|rmw_packed| | 1.001 | 2.64, 2.573, 2.682 | 2.601, 2.598, 2.683 |  |
| odin|k3|rmw_padded| | 0.924 **> 5 %** | 0.2403, 0.2289, 0.2463 | 0.2687, 0.2603, 0.2454 |  |
| odin|k3|sw_packed| | 0.957 | 0.09735, 0.09407, 0.09872 | 0.101, 0.1006, 0.1015 | oui |
| odin|k3|sw_padded| | 1.010 | 0.08841, 0.08895, 0.08869 | 0.08707, 0.08771, 0.08865 |  |
| odin|k4|branchless_unsorted| | 0.973 | 0.001506, 0.001537, 0.001534 | 0.001529, 0.001613, 0.001564 |  |
| odin|k4|natural_sorted| | 1.014 | 0.00152, 0.001523, 0.00158 | 0.00149, 0.001547, 0.001522 |  |
| odin|k4|natural_unsorted| | 1.007 | 0.001468, 0.001539, 0.001539 | 0.001483, 0.001548, 0.001481 |  |
| odin|k5|natural| | 1.011 | 0.0926, 0.09809, 0.09443 | 0.09445, 0.09406, 0.09354 |  |
| odin|k5|tuned| | 1.063 **> 5 %** | 0.003518, 0.005037, 0.003607 | 0.003741, 0.004006, 0.003549 |  |
| odin|k6|mt|q1 | 1.017 | 0.009764, 0.01361, 0.01449 | 0.01026, 0.01533, 0.01163 |  |
| odin|k6|mt|q6 | 0.780 **> 5 %** | 0.001774, 0.0022, 0.002324 | 0.001915, 0.004363, 0.002288 |  |
| odin|k6|natural|q1 | 0.983 | 0.06399, 0.06709, 0.06901 | 0.06813, 0.07067, 0.06478 |  |
| odin|k6|natural|q6 | 0.937 **> 5 %** | 0.05931, 0.0604, 0.06139 | 0.0593, 0.06924, 0.0652 |  |
| odin|k6|tuned|q1 | 0.957 | 0.03654, 0.03721, 0.03703 | 0.03666, 0.04245, 0.03691 |  |
| odin|k6|tuned|q6 | 1.000 | 0.01159, 0.01504, 0.01316 | 0.01151, 0.01626, 0.01226 |  |
| odin|k7|natural| | 1.051 **> 5 %** | 0.7323, 0.9363, 0.8583 | 0.6856, 0.9403, 0.7871 |  |
| odin|k7|tuned| | 1.037 | 0.166, 0.1736, 0.1715 | 0.1605, 0.1723, 0.1604 |  |
| odin|k8|natural| | 0.985 | 1.367, 1.431, 1.269 | 1.335, 1.478, 1.317 |  |
| odin|k8|tuned_alloc| | 0.968 | 0.9238, 0.9034, 0.8763 | 0.9101, 0.9552, 0.9277 |  |
| odin|k8|tuned| | 1.017 | 0.2858, 0.2944, 0.2865 | 0.2816, 0.2921, 0.2784 |  |
| odin|k9|mt| | 1.208 **> 5 %** | 0.01409, 0.008726, 0.008642 | 0.007184, 0.01048, 0.008001 |  |
| odin|k9|natural| | 1.228 **> 5 %** | 0.03432, 0.01608, 0.01653 | 0.01439, 0.02204, 0.01554 |  |
| odin|k9|tuned| | 1.351 **> 5 %** | 0.03609, 0.02065, 0.01817 | 0.0137, 0.02474, 0.01621 |  |

## Calculs refaits avec les anciens binaires d'Odin, de Chapel et de Go à la taille publiée (section 4)

Langages dont la place change dans au moins un calcul (place avec les nouveaux binaires → avec les anciens ; rang espéré entre parenthèses) :

| Langage | Hôte | Trois tailles | Taille petite | Taille publiée | Taille grande |
|---|---|---|---|---|---|
| Odin | 6 → 4 (6.83 → 5.69) | 4 → 4 (5.69 → 5.21) | 4 → 4 (5.40 → 5.15) | 6 → 4 (6.75 → 5.73) | 5 → 5 (5.38 → 5.24) |
| Nim | 4 → 5 (5.53 → 5.70) | 5 → 5 (6.09 → 6.14) | 6 → 5 (6.59 → 6.58) | 4 → 5 (5.71 → 5.89) | 6 → 6 (6.15 → 6.16) |
| D | 5 → 6 (6.31 → 6.47) | 6 → 6 (6.43 → 6.45) | 7 → 7 (6.99 → 6.98) | 5 → 6 (6.00 → 6.15) | 7 → 7 (6.62 → 6.61) |
| Zig | 8 → 8 (7.61 → 7.77) | 7 → 7 (7.70 → 7.74) | 10 → 10 (9.84 → 9.84) | 8 → 7 (7.49 → 7.66) | 4 → 4 (4.79 → 4.80) |
| Rust | 7 → 7 (7.15 → 7.36) | 8 → 8 (7.76 → 7.82) | 8 → 8 (7.52 → 7.50) | 7 → 8 (7.47 → 7.68) | 9 → 9 (8.57 → 8.54) |
| Chapel | 11 → 10 (9.45 → 9.38) | 9 → 9 (8.47 → 8.65) | 5 → 6 (6.40 → 6.80) | 10 → 9 (9.27 → 9.01) | 10 → 10 (10.29 → 10.57) |
| Ada | 9 → 9 (9.25 → 9.35) | 10 → 10 (10.32 → 10.33) | 14 → 14 (12.28 → 12.27) | 9 → 10 (9.02 → 9.13) | 8 → 8 (8.08 → 8.05) |
| Swift | 10 → 11 (9.30 → 9.41) | 11 → 11 (10.65 → 10.68) | 12 → 12 (10.45 → 10.45) | 11 → 11 (9.54 → 9.67) | 14 → 14 (11.75 → 11.72) |

Scores au centre d'Odin, de Chapel et de Go (nouveaux → anciens binaires) :

* Odin : Hôte 60.6 → 62.0 ; Trois tailles 62.3 → 62.9 ; Taille petite 58.8 → 59.2 ; Taille publiée 61.3 → 62.5 ; Taille grande 68.1 → 68.3
* Chapel : Hôte 55.8 → 56.2 ; Trois tailles 58.1 → 58.0 ; Taille petite 56.7 → 56.1 ; Taille publiée 56.7 → 57.3 ; Taille grande 61.5 → 61.1
* Go : Hôte 38.4 → 36.5 ; Trois tailles 40.2 → 38.4 ; Taille petite 35.9 → 34.2 ; Taille publiée 40.8 → 38.9 ; Taille grande 45.6 → 43.8

Rangs qui bougent de plus de deux places entre « Hôte » et « Trois tailles », anciens binaires : aucun.

Étages indicatifs, anciens binaires :

* Hôte : C, C++, C3, Odin, Nim, D, Rust, Zig, Ada, Chapel, Swift, Mojo, Julia, Fortran, C#, Java, FreePascal, Go, Haskell | OCaml, BQN, PHP, JavaScript, Python, Lua
* Trois tailles : C++, C, C3, Odin, Nim, D, Zig, Rust, Chapel, Ada, Swift, Mojo, Fortran, Julia | C#, FreePascal, Java, Go, Haskell | OCaml, BQN, PHP, JavaScript, Python, Lua
* Taille petite : C++, C, C3, Odin, Nim, Chapel, D, Rust, Fortran, Zig, Mojo, Swift, Julia, Ada | C#, FreePascal, Java, Go, Haskell | OCaml, BQN, JavaScript, PHP, Python, Lua
* Taille publiée : C, C3, C++, Odin, Nim, D, Zig, Rust, Chapel, Ada, Swift, Mojo, Julia, Fortran, C#, Java, FreePascal, Go | Haskell | OCaml, BQN, PHP, JavaScript, Python, Lua
* Taille grande : C++, C3, C, Zig, Odin, Nim, D, Ada, Rust, Chapel, Mojo, Fortran, Julia, Swift, FreePascal, C#, Java, Go, Haskell | OCaml, BQN, JavaScript, PHP, Python, Lua

Processeur des enregistrements (section 5) : 6/207/2 Intel(R) Xeon(R) Processor @ 2.10GHz (6594 enregistrements ; passes 0, 1, 2).

Processus écartés : 39 (toutes passes) ; vol de temps > 5 % après reprise : 0.

* hors mémoire (11 cellules) : BQN k1 large aos energy, BQN k1 large natural energy, BQN k1 large natural_ns energy, BQN k1 large natural_ns_shuffled energy, BQN k1 large natural_shuffled energy, BQN k1 large soa energy, PHP k1 large natural_arr energy, PHP k1 large natural_arr_shuffled energy, PHP k4 large natural_sorted, Python k1 large natural energy, Python k1 large natural_shuffled energy
* absentes par conception, hors score (K10 de BQN : ni threads ni coroutines) : BQN k10 pub natural, BQN k10 pub tuned
* autres échecs (0 cellules) : aucune

