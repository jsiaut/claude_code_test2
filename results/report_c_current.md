# Remarque sur C : rapports appariés et scénarios

Plan : `docs/C.md`. Mesures : `results/raw_c/` (machine 16, 7 processus par cellule). Code : `analysis/c_check.py`.
Processus rejetés : aucun.
Contrôle : le scénario Publié reproduit results/swift_check.json, S-E (écart maximal 0.0e+00).

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
État actuel : K9 au harnais commun pour toutes les implémentations (docs/K9.md), K5 et K1 soa de Java corrigés et F1 de Java à ½ (docs/JAVA.md), K5 et K9 de Go corrigés (docs/GO.md), options et K1, K5, K8 de Haskell corrigés et B2, B3, A7 de Haskell à ½ (docs/HASKELL.md), Q6, K1 aos, K7 et K8 d'OCaml corrigés et D5 d'OCaml à ½ (docs/OCAML.md), K7 de JavaScript corrigé et E1, A4, E6 de JavaScript à 1, ½, ½ (docs/JAVASCRIPT.md), K3, K6 mt, K9 mt et K8 naturel de Python corrigés et B1, F3 de Python à 1, ½ (docs/PYTHON.md), K3, K4, Q6 et K8 naturel de Lua corrigés et B3, B4 de Lua à ½ (docs/LUA.md), Swift ajouté (docs/SWIFT.md) ; Publié = results/swift_check.json (S-E).

## Scénarios (analyse globale de la v3 rejouée, 20 000 variantes)

| Scénario | Statut | C | C++ | Odin | Rang espéré de C | Place de C | C 1er | C devant C++ | C devant Odin | Tête |
|---|---|---|---|---|---|---|---|---|---|---|
| Publié | publié | 79,97 | 77,13 | 74,03 | 2,20 | 1 | 49 % | 76 % | 69 % | C, Odin, C++, Zig |
| S-K8-val | sensibilité | 82,43 | 77,13 | 74,03 | 1,66 | 1 | 71 % | 90 % | 81 % | C, Odin, C++, Zig |
| S-K8-it | sensibilité | 84,03 | 77,06 | 73,96 | 1,51 | 1 | 77 % | 93 % | 85 % | C, Odin, C++, Zig |
| S-K8 | sensibilité | 84,03 | 77,06 | 73,96 | 1,51 | 1 | 77 % | 93 % | 85 % | C, Odin, C++, Zig |
| R-v1 | info | 73,86 | 72,49 | 73,07 | 2,97 | 2 | 28 % | 68 % | 47 % | Odin, C, C3, C++ |
| R-ISO | info | 70,29 | 71,67 | 73,16 | 5,41 | 5 | 8 % | 39 % | 17 % | Odin, Zig, C3, C++ |
| T1 | info | 79,97 | 80,32 | 74,03 | 2,54 | 2 | 30 % | 43 % | 69 % | C++, C, Odin, Zig |
| T1+S-K8 | sensibilité | 84,03 | 80,25 | 73,96 | 1,61 | 1 | 72 % | 83 % | 85 % | C, C++, Odin, Zig |

## Classement publié : avant et après les errata

| Langage | Score | Contrôle v1 | Rang espéré avant → après | 1er avant → après |
|---|---|---|---|---|
| C | 79,97 | 77,8 → 74,2 | 2,20 → 2,20 | 49 % → 49 % |
| Odin | 74,03 | 81,3 → 81,3 | 3,18 → 3,18 | 18 % → 18 % |
| C++ | 77,13 | 82,7 → 79,1 | 3,80 → 3,80 | 12 % → 12 % |
| Zig | 72,31 | 83,2 → 83,2 | 5,12 → 5,12 | 9 % → 9 % |
| C3 | 71,64 | 77,7 → 77,7 | 5,12 → 5,12 | 5 % → 5 % |
| Rust | 69,96 | 73,1 → 73,1 | 6,95 → 6,95 | 1 % → 1 % |
| Nim | 69,31 | 73,4 → 73,4 | 7,14 → 7,14 | 2 % → 2 % |
| D | 72,66 | 78,9 → 78,9 | 7,22 → 7,22 | 1 % → 1 % |
| Ada | 71,07 | 71,7 → 71,7 | 8,29 → 8,29 | 1 % → 1 % |
| Chapel | 65,72 | 63,8 → 63,8 | 9,22 → 9,22 | 1 % → 1 % |
| Fortran | 65,44 | 59,2 → 59,2 | 10,80 → 10,80 | 0 % → 0 % |
| Swift | 65,24 | 61,9 → 61,9 | 11,01 → 11,01 | 0 % → 0 % |
| Julia | 62,37 | 68,9 → 68,9 | 12,11 → 12,11 | 0 % → 0 % |
| Mojo | 62,30 | 66,0 → 66,0 | 13,02 → 13,02 | 0 % → 0 % |
| C# | 54,88 | 65,8 → 65,8 | 15,11 → 15,11 | 0 % → 0 % |
| Java | 47,18 | 42,7 → 42,7 | 16,40 → 16,40 | 0 % → 0 % |
| Go | 45,37 | 44,9 → 44,9 | 16,50 → 16,50 | 0 % → 0 % |
| Haskell | 41,28 | 38,9 → 38,9 | 17,82 → 17,82 | 0 % → 0 % |
| OCaml | 23,92 | 23,2 → 23,2 | 19,02 → 19,02 | 0 % → 0 % |
| JavaScript | 15,64 | 14,6 → 14,6 | 20,08 → 20,08 | 0 % → 0 % |
| Python | 11,83 | 27,7 → 27,7 | 21,31 → 21,31 | 0 % → 0 % |
| Lua | 5,41 | 6,8 → 6,8 | 21,58 → 21,58 | 0 % → 0 % |

**Publié** : 1. C (2,20, 80,0), 2. Odin (3,18, 74,0), 3. C++ (3,80, 77,1), 4. Zig (5,12, 72,3), 5. C3 (5,12, 71,6), 6. Rust (6,95, 70,0), 7. Nim (7,14, 69,3), 8. D (7,22, 72,7).

**S-K8-val** : 1. C (1,66, 82,4), 2. Odin (3,30, 74,0), 3. C++ (3,94, 77,1), 4. Zig (5,19, 72,3), 5. C3 (5,22, 71,6), 6. Rust (6,97, 70,0), 7. Nim (7,16, 69,3), 8. D (7,24, 72,7).

**S-K8-it** : 1. C (1,51, 84,0), 2. Odin (3,34, 74,0), 3. C++ (3,97, 77,1), 4. Zig (5,20, 72,2), 5. C3 (5,24, 71,6), 6. Rust (6,98, 69,9), 7. Nim (7,17, 69,2), 8. D (7,25, 72,6).

**S-K8** : 1. C (1,51, 84,0), 2. Odin (3,34, 74,0), 3. C++ (3,97, 77,1), 4. Zig (5,20, 72,2), 5. C3 (5,24, 71,6), 6. Rust (6,98, 69,9), 7. Nim (7,17, 69,2), 8. D (7,25, 72,6).

**R-v1** : 1. Odin (2,75, 73,1), 2. C (2,97, 73,9), 3. C3 (4,19, 72,3), 4. C++ (4,47, 72,5), 5. Zig (4,96, 70,9), 6. Rust (6,50, 69,8), 7. Nim (6,99, 68,4), 8. D (7,67, 69,8).

**R-ISO** : 1. Odin (2,26, 73,2), 2. Zig (3,37, 72,3), 3. C3 (4,31, 71,2), 4. C++ (4,41, 71,7), 5. C (5,41, 70,3), 6. Rust (5,86, 69,5), 7. D (7,17, 69,3), 8. Nim (7,50, 66,7).

**T1** : 1. C++ (2,18, 80,3), 2. C (2,54, 80,0), 3. Odin (3,46, 74,0), 4. Zig (5,26, 72,3), 5. C3 (5,39, 71,6), 6. Rust (7,09, 70,0), 7. Nim (7,25, 69,3), 8. D (7,34, 72,7).

**T1+S-K8** : 1. C (1,61, 84,0), 2. C++ (2,58, 80,2), 3. Odin (3,63, 74,0), 4. Zig (5,35, 72,2), 5. C3 (5,50, 71,6), 6. Rust (7,12, 69,9), 7. Nim (7,28, 69,2), 8. D (7,37, 72,6).

