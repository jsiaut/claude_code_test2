# Remarque sur C : rapports appariés et scénarios

Plan : `docs/C.md`. Mesures : `results/raw_c/` (machine 16, 7 processus par cellule). Code : `analysis/c_check.py`.
Processus rejetés : aucun.
Contrôle : le scénario Publié reproduit results/fpc_check.json, F-E (écart maximal 0.0e+00).

## Rapports appariés (même hôte)

| Rapport | Clé | Ancien (ms) | Nouveau (ms) | Rapport | IC 95 % |
|---|---|---|---|---|---|
| c_k8val / c_ref | k8:tuned | 289,6 | 165,5 | 0,572 | 0,514–0,637 |
| c_k8val / c_ref | k8:natural (témoin) | 771,3 | 756,9 | 0,981 | 0,898–1,071 |
| c_k8it / c_ref | k8:tuned | 289,6 | 115,6 | 0,399 | 0,353–0,463 |
| c_k8it / c_ref | k8:natural (témoin) | 771,3 | 784,3 | 1,017 | 0,915–1,152 |
| c_gcc_k8val / c_gcc_ref | k8:tuned | 154,9 | 69,8 | 0,450 | 0,428–0,482 |
| c_gcc_k8val / c_gcc_ref | k8:natural (témoin) | 602,2 | 665,2 | 1,105 | 0,982–1,245 |
| c_gcc_k8it / c_gcc_ref | k8:tuned | 154,9 | 135,1 | 0,872 | 0,795–0,967 |
| c_gcc_k8it / c_gcc_ref | k8:natural (témoin) | 602,2 | 640,3 | 1,063 | 0,942–1,207 |
| c_gcc_ref / c_ref | k8:tuned | 289,6 | 154,9 | 0,535 | 0,519–0,550 |
| c_gcc_ref / c_ref | k8:natural (témoin) | 771,3 | 602,2 | 0,781 | 0,700–0,871 |

Frontière de K8 dans le publié : Ada, 107,7 ms ; K8 tuned de C 265,6 ms, 106,0 ms avec la meilleure forme (S-K8).
État actuel : K9 au harnais commun pour toutes les implémentations (docs/K9.md), K5 et K1 soa de Java corrigés et F1 de Java à ½ (docs/JAVA.md), K5 et K9 de Go corrigés (docs/GO.md), options et K1, K5, K8 de Haskell corrigés et B2, B3, A7 de Haskell à ½ (docs/HASKELL.md), Q6, K1 aos, K7 et K8 d'OCaml corrigés et D5 d'OCaml à ½ (docs/OCAML.md), K7 de JavaScript corrigé et E1, A4, E6 de JavaScript à 1, ½, ½ (docs/JAVASCRIPT.md), K3, K6 mt, K9 mt et K8 naturel de Python corrigés et B1, F3 de Python à 1, ½ (docs/PYTHON.md), K3, K4, Q6 et K8 naturel de Lua corrigés et B3, B4 de Lua à ½ (docs/LUA.md), Swift ajouté (docs/SWIFT.md), puis D4 et E4 de Swift corrigés et son pont par la machine 24 (docs/SWIFT.md, 5), FreePascal ajouté (docs/FPC.md) ; Publié = results/fpc_check.json (F-E).

## Scénarios (analyse globale de la v3 rejouée, 20 000 variantes)

| Scénario | Statut | C | C++ | Odin | Rang espéré de C | Place de C | C 1er | C devant C++ | C devant Odin | Tête |
|---|---|---|---|---|---|---|---|---|---|---|
| Publié | publié | 79,96 | 77,12 | 74,02 | 2,22 | 1 | 49 % | 76 % | 69 % | C, Odin, C++, Zig |
| S-K8-val | sensibilité | 82,43 | 77,12 | 74,02 | 1,67 | 1 | 70 % | 90 % | 81 % | C, Odin, C++, Zig |
| S-K8-it | sensibilité | 84,03 | 77,05 | 73,95 | 1,52 | 1 | 77 % | 93 % | 85 % | C, Odin, C++, Zig |
| S-K8 | sensibilité | 84,03 | 77,05 | 73,95 | 1,52 | 1 | 77 % | 93 % | 85 % | C, Odin, C++, Zig |
| R-v1 | info | 73,85 | 72,48 | 73,06 | 2,97 | 2 | 28 % | 68 % | 47 % | Odin, C, C3, C++ |
| R-ISO | info | 70,28 | 71,67 | 73,15 | 5,46 | 5 | 9 % | 39 % | 17 % | Odin, Zig, C3, C++ |
| T1 | info | 79,96 | 80,31 | 74,02 | 2,55 | 2 | 30 % | 43 % | 69 % | C++, C, Odin, Zig |
| T1+S-K8 | sensibilité | 84,03 | 80,24 | 73,95 | 1,62 | 1 | 71 % | 83 % | 85 % | C, C++, Odin, Zig |

## Classement publié : avant et après les errata

| Langage | Score | Contrôle v1 | Rang espéré avant → après | 1er avant → après |
|---|---|---|---|---|
| C | 79,96 | 77,8 → 74,2 | 2,22 → 2,22 | 49 % → 49 % |
| Odin | 74,02 | 81,3 → 81,3 | 3,19 → 3,19 | 17 % → 17 % |
| C++ | 77,12 | 82,7 → 79,1 | 3,81 → 3,81 | 12 % → 12 % |
| Zig | 72,30 | 83,2 → 83,2 | 5,06 → 5,06 | 10 % → 10 % |
| C3 | 71,64 | 77,7 → 77,7 | 5,20 → 5,20 | 4 % → 4 % |
| Rust | 69,95 | 73,1 → 73,1 | 6,96 → 6,96 | 1 % → 1 % |
| Nim | 69,30 | 73,4 → 73,4 | 7,12 → 7,12 | 2 % → 2 % |
| D | 72,65 | 78,9 → 78,9 | 7,43 → 7,43 | 1 % → 1 % |
| Ada | 71,06 | 71,7 → 71,7 | 8,30 → 8,30 | 1 % → 1 % |
| Chapel | 65,72 | 63,8 → 63,8 | 9,19 → 9,19 | 1 % → 1 % |
| Swift | 66,45 | 64,1 → 64,1 | 10,70 → 10,70 | 0 % → 0 % |
| Fortran | 65,44 | 59,2 → 59,2 | 10,84 → 10,84 | 0 % → 0 % |
| Julia | 62,36 | 68,9 → 68,9 | 12,26 → 12,26 | 0 % → 0 % |
| Mojo | 62,29 | 66,0 → 66,0 | 13,01 → 13,01 | 0 % → 0 % |
| C# | 54,88 | 65,8 → 65,8 | 15,28 → 15,28 | 0 % → 0 % |
| FreePascal | 47,44 | 58,5 → 58,5 | 16,71 → 16,71 | 0 % → 0 % |
| Java | 47,17 | 42,7 → 42,7 | 16,93 → 16,93 | 0 % → 0 % |
| Go | 45,37 | 44,9 → 44,9 | 17,13 → 17,13 | 0 % → 0 % |
| Haskell | 41,27 | 38,9 → 38,9 | 18,68 → 18,68 | 0 % → 0 % |
| OCaml | 23,92 | 23,2 → 23,2 | 20,02 → 20,02 | 0 % → 0 % |
| JavaScript | 15,63 | 14,6 → 14,6 | 21,08 → 21,08 | 0 % → 0 % |
| Python | 11,83 | 27,7 → 27,7 | 22,31 → 22,31 | 0 % → 0 % |
| Lua | 5,41 | 6,8 → 6,8 | 22,58 → 22,58 | 0 % → 0 % |

**Publié** : 1. C (2,22, 80,0), 2. Odin (3,19, 74,0), 3. C++ (3,81, 77,1), 4. Zig (5,06, 72,3), 5. C3 (5,20, 71,6), 6. Rust (6,96, 70,0), 7. Nim (7,12, 69,3), 8. D (7,43, 72,7).

**S-K8-val** : 1. C (1,67, 82,4), 2. Odin (3,31, 74,0), 3. C++ (3,95, 77,1), 4. Zig (5,13, 72,3), 5. C3 (5,29, 71,6), 6. Rust (6,99, 70,0), 7. Nim (7,14, 69,3), 8. D (7,45, 72,7).

**S-K8-it** : 1. C (1,52, 84,0), 2. Odin (3,35, 74,0), 3. C++ (3,98, 77,1), 4. Zig (5,15, 72,2), 5. C3 (5,31, 71,6), 6. Rust (6,99, 69,9), 7. Nim (7,15, 69,2), 8. D (7,46, 72,6).

**S-K8** : 1. C (1,52, 84,0), 2. Odin (3,35, 74,0), 3. C++ (3,98, 77,1), 4. Zig (5,15, 72,2), 5. C3 (5,31, 71,6), 6. Rust (6,99, 69,9), 7. Nim (7,15, 69,2), 8. D (7,46, 72,6).

**R-v1** : 1. Odin (2,77, 73,1), 2. C (2,97, 73,9), 3. C3 (4,27, 72,3), 4. C++ (4,47, 72,5), 5. Zig (4,91, 70,9), 6. Rust (6,50, 69,8), 7. Nim (6,96, 68,4), 8. D (7,88, 69,8).

**R-ISO** : 1. Odin (2,28, 73,1), 2. Zig (3,35, 72,3), 3. C3 (4,40, 71,2), 4. C++ (4,43, 71,7), 5. C (5,46, 70,3), 6. Rust (5,91, 69,5), 7. D (7,42, 69,3), 8. Nim (7,52, 66,7).

**T1** : 1. C++ (2,21, 80,3), 2. C (2,55, 80,0), 3. Odin (3,47, 74,0), 4. Zig (5,21, 72,3), 5. C3 (5,46, 71,6), 6. Rust (7,11, 70,0), 7. Nim (7,23, 69,3), 8. D (7,54, 72,7).

**T1+S-K8** : 1. C (1,62, 84,0), 2. C++ (2,61, 80,2), 3. Odin (3,63, 74,0), 4. Zig (5,30, 72,2), 5. C3 (5,57, 71,6), 6. Rust (7,14, 69,9), 7. Nim (7,26, 69,2), 8. D (7,57, 72,6).

