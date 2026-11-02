# Remarque sur C : rapports appariés et scénarios

Plan : `docs/C.md`. Mesures : `results/raw_c/` (machine 16, 7 processus par cellule). Code : `analysis/c_check.py`.
Processus rejetés : aucun.
Contrôle : le scénario Publié reproduit results/java_check.json, J-E (écart maximal 0.0e+00).

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
État actuel : K9 au harnais commun pour toutes les implémentations (docs/K9.md), K5 et K1 soa de Java corrigés et F1 de Java à ½ (docs/JAVA.md) ; Publié = results/java_check.json (J-E).

## Scénarios (analyse globale de la v3 rejouée, 20 000 variantes)

| Scénario | Statut | C | C++ | Odin | Rang espéré de C | Place de C | C 1er | C devant C++ | C devant Odin | Tête |
|---|---|---|---|---|---|---|---|---|---|---|
| Publié | publié | 79,94 | 77,10 | 74,00 | 2,21 | 1 | 49 % | 76 % | 69 % | C, Odin, C++, Zig |
| S-K8-val | sensibilité | 82,41 | 77,10 | 74,00 | 1,66 | 1 | 70 % | 90 % | 81 % | C, Odin, C++, Zig |
| S-K8-it | sensibilité | 84,01 | 77,03 | 73,94 | 1,52 | 1 | 77 % | 93 % | 85 % | C, Odin, C++, Zig |
| S-K8 | sensibilité | 84,01 | 77,03 | 73,94 | 1,52 | 1 | 77 % | 93 % | 85 % | C, Odin, C++, Zig |
| R-v1 | info | 73,83 | 72,47 | 73,04 | 2,97 | 2 | 28 % | 68 % | 47 % | Odin, C, C3, C++ |
| R-ISO | info | 70,26 | 71,65 | 73,13 | 5,26 | 5 | 9 % | 39 % | 17 % | Odin, Zig, C3, C++ |
| T1 | info | 79,94 | 80,29 | 74,00 | 2,54 | 2 | 30 % | 43 % | 69 % | C++, C, Odin, Zig |
| T1+S-K8 | sensibilité | 84,01 | 80,22 | 73,94 | 1,62 | 1 | 71 % | 83 % | 85 % | C, C++, Odin, Zig |

## Classement publié : avant et après les errata

| Langage | Score | Contrôle v1 | Rang espéré avant → après | 1er avant → après |
|---|---|---|---|---|
| C | 79,94 | 77,8 → 74,2 | 2,21 → 2,21 | 49 % → 49 % |
| Odin | 74,00 | 81,3 → 81,3 | 3,16 → 3,16 | 18 % → 18 % |
| C++ | 77,10 | 82,7 → 79,1 | 3,76 → 3,76 | 12 % → 12 % |
| Zig | 72,28 | 83,2 → 83,2 | 4,93 → 4,93 | 10 % → 10 % |
| C3 | 71,62 | 77,7 → 77,7 | 5,14 → 5,14 | 4 % → 4 % |
| Rust | 69,93 | 73,1 → 73,1 | 6,82 → 6,82 | 1 % → 1 % |
| Nim | 69,29 | 73,4 → 73,4 | 6,91 → 6,91 | 2 % → 2 % |
| D | 72,64 | 78,9 → 78,9 | 7,23 → 7,23 | 1 % → 1 % |
| Ada | 71,04 | 71,7 → 71,7 | 8,07 → 8,07 | 1 % → 1 % |
| Chapel | 65,70 | 63,8 → 63,8 | 8,85 → 8,85 | 1 % → 1 % |
| Fortran | 65,42 | 59,2 → 59,2 | 10,29 → 10,29 | 0 % → 0 % |
| Julia | 62,34 | 68,9 → 68,9 | 11,57 → 11,57 | 0 % → 0 % |
| Mojo | 62,28 | 66,0 → 66,0 | 12,18 → 12,18 | 0 % → 0 % |
| C# | 54,86 | 65,8 → 65,8 | 14,09 → 14,09 | 0 % → 0 % |
| Java | 47,15 | 42,7 → 42,7 | 15,18 → 15,18 | 0 % → 0 % |
| Go | 43,02 | 44,9 → 44,9 | 15,62 → 15,62 | 0 % → 0 % |
| Haskell | 34,47 | 33,4 → 33,4 | 17,00 → 17,00 | 0 % → 0 % |
| OCaml | 23,99 | 24,7 → 24,7 | 17,98 → 17,98 | 0 % → 0 % |
| JavaScript | 14,24 | 11,6 → 11,6 | 19,07 → 19,07 | 0 % → 0 % |
| Python | 9,94 | 22,4 → 22,4 | 20,30 → 20,30 | 0 % → 0 % |
| Lua | 3,91 | 2,8 → 2,8 | 20,63 → 20,63 | 0 % → 0 % |

**Publié** : 1. C (2,21, 79,9), 2. Odin (3,16, 74,0), 3. C++ (3,76, 77,1), 4. Zig (4,93, 72,3), 5. C3 (5,14, 71,6), 6. Rust (6,82, 69,9), 7. Nim (6,91, 69,3), 8. D (7,23, 72,6).

**S-K8-val** : 1. C (1,66, 82,4), 2. Odin (3,28, 74,0), 3. C++ (3,90, 77,1), 4. Zig (5,00, 72,3), 5. C3 (5,23, 71,6), 6. Rust (6,85, 69,9), 7. Nim (6,94, 69,3), 8. D (7,25, 72,6).

**S-K8-it** : 1. C (1,52, 84,0), 2. Odin (3,32, 73,9), 3. C++ (3,93, 77,0), 4. Zig (5,02, 72,2), 5. C3 (5,26, 71,5), 6. Rust (6,86, 69,9), 7. Nim (6,94, 69,2), 8. D (7,26, 72,6).

**S-K8** : 1. C (1,52, 84,0), 2. Odin (3,32, 73,9), 3. C++ (3,93, 77,0), 4. Zig (5,02, 72,2), 5. C3 (5,26, 71,5), 6. Rust (6,86, 69,9), 7. Nim (6,94, 69,2), 8. D (7,26, 72,6).

**R-v1** : 1. Odin (2,74, 73,0), 2. C (2,97, 73,8), 3. C3 (4,23, 72,3), 4. C++ (4,41, 72,5), 5. Zig (4,78, 70,9), 6. Rust (6,39, 69,8), 7. Nim (6,77, 68,3), 8. D (7,66, 69,8).

**R-ISO** : 1. Odin (2,24, 73,1), 2. Zig (3,22, 72,3), 3. C3 (4,31, 71,2), 4. C++ (4,32, 71,6), 5. C (5,26, 70,3), 6. Rust (5,71, 69,5), 7. Nim (7,13, 66,7), 8. D (7,13, 69,3).

**T1** : 1. C++ (2,20, 80,3), 2. C (2,54, 79,9), 3. Odin (3,44, 74,0), 4. Zig (5,08, 72,3), 5. C3 (5,40, 71,6), 6. Rust (6,97, 69,9), 7. Nim (7,03, 69,3), 8. D (7,34, 72,6).

**T1+S-K8** : 1. C (1,62, 84,0), 2. C++ (2,60, 80,2), 3. Odin (3,61, 73,9), 4. Zig (5,17, 72,2), 5. C3 (5,51, 71,5), 6. Rust (7,00, 69,9), 7. Nim (7,06, 69,2), 8. D (7,37, 72,6).

