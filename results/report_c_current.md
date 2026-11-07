# Remarque sur C : rapports appariés et scénarios

Plan : `docs/C.md`. Mesures : `results/raw_c/` (machine 16, 7 processus par cellule). Code : `analysis/c_check.py`.
Processus rejetés : aucun.
Contrôle : le scénario Publié reproduit results/php_check.json, P-E (écart maximal 0.0e+00).

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
État actuel : K9 au harnais commun pour toutes les implémentations (docs/K9.md), K5 et K1 soa de Java corrigés et F1 de Java à ½ (docs/JAVA.md), K5 et K9 de Go corrigés (docs/GO.md), options et K1, K5, K8 de Haskell corrigés et B2, B3, A7 de Haskell à ½ (docs/HASKELL.md), Q6, K1 aos, K7 et K8 d'OCaml corrigés et D5 d'OCaml à ½ (docs/OCAML.md), K7 de JavaScript corrigé et E1, A4, E6 de JavaScript à 1, ½, ½ (docs/JAVASCRIPT.md), K3, K6 mt, K9 mt et K8 naturel de Python corrigés et B1, F3 de Python à 1, ½ (docs/PYTHON.md), K3, K4, Q6 et K8 naturel de Lua corrigés et B3, B4 de Lua à ½ (docs/LUA.md), Swift ajouté (docs/SWIFT.md), puis D4 et E4 de Swift corrigés et son pont par la machine 24 (docs/SWIFT.md, 5), FreePascal ajouté (docs/FPC.md), puis C2, E4 et F4 de FreePascal corrigés (docs/FPC.md, 5), BQN ajouté (docs/BQN.md), puis K9, K7 naturel, A3 et A6 de BQN corrigés (docs/BQN.md, 5), PHP ajouté (docs/PHP.md) ; Publié = results/php_check.json (P-E).

## Scénarios (analyse globale de la v3 rejouée, 20 000 variantes)

| Scénario | Statut | C | C++ | Odin | Rang espéré de C | Place de C | C 1er | C devant C++ | C devant Odin | Tête |
|---|---|---|---|---|---|---|---|---|---|---|
| Publié | publié | 79,96 | 77,12 | 74,02 | 2,20 | 1 | 50 % | 76 % | 69 % | C, Odin, C++, C3 |
| S-K8-val | sensibilité | 82,43 | 77,12 | 74,02 | 1,65 | 1 | 71 % | 90 % | 81 % | C, Odin, C++, Zig |
| S-K8-it | sensibilité | 84,03 | 77,05 | 73,95 | 1,50 | 1 | 77 % | 93 % | 85 % | C, Odin, C++, Zig |
| S-K8 | sensibilité | 84,03 | 77,05 | 73,95 | 1,50 | 1 | 77 % | 93 % | 85 % | C, Odin, C++, Zig |
| R-v1 | info | 73,85 | 72,48 | 73,06 | 2,96 | 2 | 28 % | 68 % | 47 % | Odin, C, C3, C++ |
| R-ISO | info | 70,28 | 71,67 | 73,15 | 5,47 | 5 | 9 % | 39 % | 17 % | Odin, Zig, C3, C++ |
| T1 | info | 79,96 | 80,31 | 74,02 | 2,53 | 2 | 31 % | 43 % | 69 % | C++, C, Odin, Zig |
| T1+S-K8 | sensibilité | 84,03 | 80,24 | 73,95 | 1,60 | 1 | 72 % | 83 % | 85 % | C, C++, Odin, Zig |

## Classement publié : avant et après les errata

| Langage | Score | Contrôle v1 | Rang espéré avant → après | 1er avant → après |
|---|---|---|---|---|
| C | 79,96 | 77,8 → 74,2 | 2,20 → 2,20 | 50 % → 50 % |
| Odin | 74,02 | 81,3 → 81,3 | 3,17 → 3,17 | 18 % → 18 % |
| C++ | 77,12 | 82,7 → 79,1 | 3,79 → 3,79 | 12 % → 12 % |
| C3 | 71,64 | 77,7 → 77,7 | 5,11 → 5,11 | 5 % → 5 % |
| Zig | 72,30 | 83,2 → 83,2 | 5,14 → 5,14 | 9 % → 9 % |
| Rust | 69,95 | 73,1 → 73,1 | 6,97 → 6,97 | 1 % → 1 % |
| Nim | 69,30 | 73,4 → 73,4 | 7,16 → 7,16 | 2 % → 2 % |
| D | 72,65 | 78,9 → 78,9 | 7,19 → 7,19 | 1 % → 1 % |
| Ada | 71,06 | 71,7 → 71,7 | 8,30 → 8,30 | 1 % → 1 % |
| Chapel | 65,72 | 63,8 → 63,8 | 9,29 → 9,29 | 1 % → 1 % |
| Fortran | 65,44 | 59,2 → 59,2 | 10,85 → 10,85 | 0 % → 0 % |
| Swift | 66,45 | 64,1 → 64,1 | 10,86 → 10,86 | 0 % → 0 % |
| Julia | 62,36 | 68,9 → 68,9 | 12,15 → 12,15 | 0 % → 0 % |
| Mojo | 62,29 | 66,0 → 66,0 | 13,08 → 13,08 | 0 % → 0 % |
| C# | 54,88 | 65,8 → 65,8 | 15,30 → 15,30 | 0 % → 0 % |
| FreePascal | 48,06 | 58,5 → 58,5 | 16,73 → 16,73 | 0 % → 0 % |
| Java | 47,17 | 42,7 → 42,7 | 16,93 → 16,93 | 0 % → 0 % |
| Go | 45,37 | 44,9 → 44,9 | 17,12 → 17,12 | 0 % → 0 % |
| Haskell | 41,27 | 38,9 → 38,9 | 18,68 → 18,68 | 0 % → 0 % |
| OCaml | 23,92 | 23,2 → 23,2 | 20,31 → 20,31 | 0 % → 0 % |
| BQN | 17,72 | 21,2 → 21,2 | 21,17 → 21,17 | 0 % → 0 % |
| PHP | 16,56 | 25,9 → 25,9 | 22,32 → 22,32 | 0 % → 0 % |
| JavaScript | 15,63 | 14,6 → 14,6 | 22,34 → 22,34 | 0 % → 0 % |
| Python | 11,83 | 27,7 → 27,7 | 24,26 → 24,26 | 0 % → 0 % |
| Lua | 5,41 | 6,8 → 6,8 | 24,58 → 24,58 | 0 % → 0 % |

**Publié** : 1. C (2,20, 80,0), 2. Odin (3,17, 74,0), 3. C++ (3,79, 77,1), 4. C3 (5,11, 71,6), 5. Zig (5,14, 72,3), 6. Rust (6,97, 70,0), 7. Nim (7,16, 69,3), 8. D (7,19, 72,7).

**S-K8-val** : 1. C (1,65, 82,4), 2. Odin (3,29, 74,0), 3. C++ (3,93, 77,1), 4. Zig (5,20, 72,3), 5. C3 (5,20, 71,6), 6. Rust (6,99, 70,0), 7. Nim (7,19, 69,3), 8. D (7,21, 72,7).

**S-K8-it** : 1. C (1,50, 84,0), 2. Odin (3,33, 74,0), 3. C++ (3,96, 77,1), 4. Zig (5,22, 72,2), 5. C3 (5,23, 71,6), 6. Rust (7,00, 69,9), 7. Nim (7,19, 69,2), 8. D (7,22, 72,6).

**S-K8** : 1. C (1,50, 84,0), 2. Odin (3,33, 74,0), 3. C++ (3,96, 77,1), 4. Zig (5,22, 72,2), 5. C3 (5,23, 71,6), 6. Rust (7,00, 69,9), 7. Nim (7,19, 69,2), 8. D (7,22, 72,6).

**R-v1** : 1. Odin (2,75, 73,1), 2. C (2,96, 73,9), 3. C3 (4,17, 72,3), 4. C++ (4,46, 72,5), 5. Zig (4,98, 70,9), 6. Rust (6,50, 69,8), 7. Nim (7,00, 68,4), 8. D (7,64, 69,8).

**R-ISO** : 1. Odin (2,25, 73,1), 2. Zig (3,39, 72,3), 3. C3 (4,31, 71,2), 4. C++ (4,42, 71,7), 5. C (5,47, 70,3), 6. Rust (5,91, 69,5), 7. D (7,17, 69,3), 8. Nim (7,57, 66,7).

**T1** : 1. C++ (2,17, 80,3), 2. C (2,53, 80,0), 3. Odin (3,46, 74,0), 4. Zig (5,28, 72,3), 5. C3 (5,37, 71,6), 6. Rust (7,11, 70,0), 7. Nim (7,28, 69,3), 8. D (7,31, 72,7).

**T1+S-K8** : 1. C (1,60, 84,0), 2. C++ (2,57, 80,2), 3. Odin (3,62, 74,0), 4. Zig (5,37, 72,2), 5. C3 (5,49, 71,6), 6. Rust (7,14, 69,9), 7. Nim (7,31, 69,2), 8. D (7,34, 72,6).

