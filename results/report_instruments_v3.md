# Compteurs du noyau et contrôle du bruit (plan : docs/INSTRUMENTS_V3.md)

Comptes par répétition, méthode des deux points (le démarrage et l'échauffement s'annulent). Une valeur négative ou fractionnaire vient d'une activité qui n'est pas strictement proportionnelle au nombre de répétitions (ramasse-miettes, compilation à la volée, threads de fond).

## K1 naturel (`k1:natural:energy`)

| Implémentation | Temps par rép. (ms) | CPU / temps écoulé | Appels système | `futex` | `mmap` | `munmap` | `madvise` | `brk` | `mprotect` | `clone3` | `sched_yield` | `write` | Défauts de page | Changements de contexte | Migrations | malloc + calloc + realloc | free |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C | 32,2 | 1,00 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | -0 | 0 | 0 | 0 | 0 |
| C (gcc) | 33,1 | 1,10 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| C++ | 21,8 | 1,07 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | -0 | 0 | 0 | 0 | 0 |
| Rust | 33,8 | 0,99 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | -0 | 0 | 0 | 2 | 1 |
| Zig | 32,3 | 1,08 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | -0 | 0 | 0 |
| Odin | 27,7 | 1,20 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | -0 | 0 | 0 | 0 | 0 |
| C3 | 28,8 | 0,86 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | -0 | 0 | 0 | 0 | 0 |
| D | 33,6 | 1,20 | 1 | 0 | -0 | -0 | 0 | 0 | 0 | 0 | 0 | 1 | -0 | 0 | 0 | 0 | 0 |
| Nim | 29,4 | 1,24 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| Ada | 30,7 | 0,83 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| Fortran | 33,1 | 0,91 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | -0 | 0 | 28 | 34 |
| Fortran (flang) | 33,1 | -0,31 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 7 | 7 |
| Chapel | 25,7 | 0,77 | -32 | 1 | 0 | -0 | 0 | 0 | 0 | 0 | -33 | 1 | 0 | 0 | 0 | 0 | 0 |
| Julia | 27,5 | 1,59 | 12 | 1 | 0 | 0 | -1 | 0 | 0 | 0 | 0 | 6 | -18 | 1 | 0 | — | — |
| Mojo | 27,1 | 0,99 | 1 | -0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | -0 | -0 | 0 | 0 |
| C# | 32,4 | 2,78 | 5 | 1 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 1 | 4 | 1 | 0 | 53 | 42 |
| Java | 37,6 | -3,45 | -120 | -35 | -0 | -0 | -0 | 0 | -1 | -0 | -0 | 13 | 654 | -86 | -2 | 3 | 2 |
| Go | 1758,1 | 0,98 | 749 | 168 | 0 | 0 | 0 | 0 | 0 | 0 | -6 | 1 | 2 | 253 | 1 | 0 | 0 |
| Haskell | 81,9 | 2,10 | 0 | 23 | 0 | -0 | 0 | 0 | 0 | 0 | -57 | 0 | 18 | 23 | 0 | 0 | 0 |
| OCaml | 73,0 | -2,87 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | -2 | -3 | 0 | 0 | 0 |
| JavaScript | 186,7 | 7,26 | 26205 | 26118 | 1 | 3 | 3 | -2 | 74 | 0 | 1 | 1 | 132 | 1364 | -6 | 23821 | 23821 |
| JS (Bun) | 88,6 | -0,09 | 19 | 22 | 0 | -0 | -4 | 0 | 0 | 0 | 0 | 1 | 25 | 6 | 1 | -0 | -0 |
| Python | 646,0 | 2,25 | 4 | 0 | 0 | 1 | 1 | 0 | 0 | 0 | 0 | 2 | -82 | 58 | 0 | 0 | 0 |
| Lua | 373,7 | -0,82 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 4 | 1 | — | — |
| LuaJIT | 197,7 | 2,91 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | -1 | 2 | 0 | 0 | 0 |

## K3 écrivain unique (`k3:sw_padded:`)

| Implémentation | Temps par rép. (ms) | CPU / temps écoulé | Appels système | `futex` | `mmap` | `munmap` | `madvise` | `brk` | `mprotect` | `clone3` | `sched_yield` | `write` | Défauts de page | Changements de contexte | Migrations | malloc + calloc + realloc | free |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C | 74,7 | 3,73 | 39 | 2 | 0 | 0 | 4 | 0 | 0 | 4 | 0 | 1 | 0 | 17 | 1 | — | — |
| C (gcc) | 15,3 | 3,04 | 40 | 3 | 0 | 0 | 4 | 0 | 0 | 4 | 0 | 1 | 0 | 7 | 0 | — | — |
| C++ | 15,9 | 3,51 | 39 | 2 | 0 | 0 | 4 | 0 | 0 | 4 | 0 | 1 | -0 | 6 | 1 | — | — |
| Rust | 12,4 | 3,54 | 71 | 2 | 4 | 4 | 4 | 0 | 4 | 4 | 0 | 1 | -0 | 5 | 0 | — | — |
| Zig | 75,5 | 3,90 | 27 | 2 | 4 | 4 | 0 | 0 | 4 | 0 | 0 | 0 | 264 | 11 | 0 | — | — |
| Odin | 78,1 | 3,72 | 77 | 6 | 0 | 0 | 4 | 0 | 0 | 4 | 0 | 1 | 0 | 12 | -0 | — | — |
| C3 | 15,0 | 3,42 | 51 | 10 | 0 | 0 | 4 | 0 | 0 | 4 | 0 | 1 | 0 | 12 | 0 | — | — |
| D | 16,9 | 3,41 | 55 | 14 | 0 | 0 | 4 | 0 | 0 | 4 | 0 | 1 | 0 | 11 | 2 | — | — |
| Nim | 14,1 | 3,51 | 39 | 2 | 0 | 0 | 4 | 0 | 0 | 4 | 0 | 1 | 0 | 7 | 0 | — | — |
| Ada | 19,9 | 2,39 | 102 | 37 | 0 | 0 | 4 | 0 | 0 | 4 | 0 | 1 | 4 | 21 | 3 | — | — |
| Fortran | 78,5 | 3,84 | 5 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | -0 | 3 | 0 | — | — |
| Fortran (flang) | 77,0 | 4,17 | 651 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 650 | 1 | -1 | 2 | 0 | — | — |
| Chapel | 78,2 | 3,92 | -49 | 4 | 0 | -0 | 0 | 0 | 0 | 0 | -54 | 1 | 1 | 8 | 0 | — | — |
| Julia | 80,2 | 3,62 | 37 | 20 | 0 | -0 | 3 | 0 | 0 | 0 | 0 | 6 | 8 | 13 | 1 | — | — |
| Mojo | 14,8 | 3,35 | 15 | 10 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | -1 | 3 | -0 | — | — |
| C# | 80,1 | 3,59 | 1428 | 24 | 4 | 4 | 4 | 0 | 7 | 4 | 1263 | 5 | 13 | 29 | 0 | — | — |
| Java | 81,8 | 3,57 | 149 | 56 | 8 | 0 | 4 | 0 | 5 | 4 | 0 | 13 | 67 | 29 | 2 | — | — |
| Go | 329,3 | 3,50 | 222 | 17 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | -7 | 47 | 1 | — | — |
| Haskell | 365,1 | 3,83 | 97 | 21 | 0 | -0 | 0 | 0 | 0 | 0 | 0 | 0 | 7 | 87 | 1 | — | — |
| OCaml | 410,1 | 3,66 | 212 | 96 | 10 | 4 | 8 | 0 | 4 | 8 | 0 | 1 | 13 | 66 | 6 | — | — |
| JavaScript | 759,5 | 3,77 | 980 | 164 | 100 | 76 | 54 | 0 | 46 | 4 | 0 | 46 | 1993 | 164 | 37 | — | — |
| JS (Bun) | 459,0 | 3,87 | 3204 | -1112 | -1 | 0 | 592 | 0 | -0 | 6 | 3320 | 45 | 3928 | -773 | 47 | — | — |
| Python | 8206,3 | 1,09 | 23874 | 23806 | 4 | 6 | 8 | 0 | 0 | 4 | 0 | 2 | 7 | 9319 | 72 | — | — |
| Lua | 2285,1 | 1,04 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | -2 | 6 | 0 | — | — |
| LuaJIT | 42,3 | 1,02 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | — | — |

## K6 Q1 naturel (`k6:natural:q1`)

| Implémentation | Temps par rép. (ms) | CPU / temps écoulé | Appels système | `futex` | `mmap` | `munmap` | `madvise` | `brk` | `mprotect` | `clone3` | `sched_yield` | `write` | Défauts de page | Changements de contexte | Migrations | malloc + calloc + realloc | free |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C | 45,7 | 1,15 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | -0 | 0 | 0 | 0 | 0 |
| C (gcc) | 54,7 | 0,86 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | -0 | 0 | 0 | 0 | 0 |
| C++ | 54,4 | 1,16 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | 1 |
| Rust | 50,9 | 2,82 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 4 | 0 | 1 | 1 |
| Zig | 55,3 | 1,01 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| Odin | 80,8 | 1,30 | 3 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| C3 | 54,4 | 1,11 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | -0 | 0 | 0 |
| D | 52,4 | 0,83 | 0 | -1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | -0 | 0 | -0 | 0 | 0 |
| Nim | 59,6 | 1,22 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | -0 | 0 | 0 | 0 | 0 |
| Ada | 94,5 | 0,73 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | -1 | 0 | 0 | 0 | 0 |
| Fortran | 51,9 | 0,98 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | -0 | 0 | 0 | 28 | 34 |
| Fortran (flang) | 43,7 | 1,05 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | -0 | 0 | 0 | 8 | 8 |
| Chapel | 54,8 | 0,71 | -266 | -1 | 0 | -0 | 0 | 0 | 0 | 0 | -265 | 1 | 0 | -0 | 0 | 0 | 0 |
| Julia | 71,0 | 2,16 | 11 | 5 | -0 | 0 | -4 | -2 | 0 | 0 | 0 | 6 | -634 | 4 | 0 | — | — |
| Mojo | 137,5 | 0,90 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | -2 | 2 | 0 | 0 | 0 |
| C# | 86,7 | -0,43 | 6 | 3 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 1 | -26 | -45 | -0 | 25 | 19 |
| Java | 73,2 | 1,09 | 33 | 22 | -0 | -0 | 0 | 0 | 1 | -0 | 0 | 13 | -20 | 5 | -1 | -128 | -12 |
| Go | 77,7 | 1,32 | 349 | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 295 | 1 | 2 | 22 | -0 | 0 | 0 |
| Haskell | 57,4 | 1,09 | -33 | -1 | 0 | -0 | -0 | 0 | 0 | 0 | -44 | 0 | 6 | 2 | -2 | 0 | -0 |
| OCaml | 103,3 | 0,84 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | -0 | 1 | 0 | 0 | 0 |
| JavaScript | 243,4 | 1,65 | 12 | 8 | -0 | -3 | -0 | 0 | 10 | 0 | 0 | 1 | 40 | 2 | 3 | 4 | 4 |
| JS (Bun) | 116,0 | 0,94 | -17 | -16 | 0 | 0 | -2 | 0 | 0 | 0 | 0 | 1 | 67 | 94 | -1 | 0 | 0 |
| Python | 5198,9 | 0,65 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | -2 | -1 | 1 | 0 | 0 |
| Lua | 1559,5 | 2,47 | 78 | 0 | 0 | 0 | 0 | 78 | 0 | 0 | 0 | 1 | 10175 | 9 | 1 | 17 | 8 |
| LuaJIT | 64,7 | 2,85 | 4 | 0 | 0 | -0 | 0 | 0 | 1 | 0 | 0 | 1 | -0 | 1 | 0 | 0 | 0 |

## K7 naturel (`k7:natural:`)

| Implémentation | Temps par rép. (ms) | CPU / temps écoulé | Appels système | `futex` | `mmap` | `munmap` | `madvise` | `brk` | `mprotect` | `clone3` | `sched_yield` | `write` | Défauts de page | Changements de contexte | Migrations | malloc + calloc + realloc | free |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C | 368,7 | 1,35 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 2 | -0 | — | — |
| C (gcc) | 402,5 | 1,28 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 2 | 0 | — | — |
| C++ | 906,1 | 1,08 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 4 | 1 | — | — |
| Rust | 1184,5 | 1,09 | 13 | 0 | 1 | 1 | 0 | 10 | 0 | 0 | 0 | 1 | 25568 | 3 | 0 | 22 | 21 |
| Zig | 715,4 | 1,12 | 24 | 0 | 11 | 12 | 0 | 0 | 0 | 0 | 0 | 0 | 21508 | -4 | 0 | 0 | 0 |
| Odin | 911,8 | 0,77 | 15 | 0 | 1 | 1 | 0 | 10 | 0 | 0 | 0 | 1 | 28642 | 2 | 0 | 19 | 19 |
| C3 | 934,8 | 1,03 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 2 | 0 | — | — |
| D | 896,9 | 1,19 | 7 | 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | -2 | 10 | 0 | 0 | 0 |
| Nim | 684,6 | 0,96 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | -0 | 0 | 0 |
| Ada | 7216,9 | 0,97 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | -7 | 3 | — | — |
| Fortran | 448,7 | 1,55 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 2 | 0 | — | — |
| Fortran (flang) | 1122,6 | 0,47 | 4 | 0 | 1 | 1 | 0 | 1 | 0 | 0 | 0 | 1 | 10255 | 1 | -1 | — | — |
| Chapel | 1298,5 | 1,07 | -3392 | 42 | 0 | 0 | 1 | 0 | 0 | 0 | -3436 | 1 | -7 | -10 | -0 | 0 | 0 |
| Julia | 1013,8 | 1,72 | 90 | 54 | 2 | 4 | -4 | 8 | 12 | 0 | 0 | 7 | 12890 | 28 | 2 | — | — |
| Mojo | 1239,2 | 0,87 | 0 | -0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 18 | 2 | -0 | 0 | 0 |
| C# | 1152,9 | 1,10 | 48 | 10 | 4 | 2 | 4 | -0 | 4 | 0 | 2 | 1 | 11242 | 1 | 1 | 188 | 106 |
| Java | 3211,7 | 0,99 | 708 | 444 | 0 | 2 | -0 | 0 | 12 | 0 | -2 | 13 | 14088 | 226 | 19 | 1598 | 458 |
| Go | 1589,8 | 1,03 | 675 | 158 | 6 | 0 | 0 | 0 | 0 | 0 | -2 | 1 | 5572 | 215 | -5 | 0 | 0 |
| OCaml | 4983,6 | 1,06 | 586 | 0 | 584 | 0 | 0 | 1 | 0 | 0 | 0 | 1 | 5182 | 4 | 0 | 41 | 38 |
| JavaScript | 5169,9 | 1,05 | 8564 | 5055 | 197 | 398 | 192 | 8 | 2690 | 0 | 5 | 2 | 28450 | 482 | 15 | 16825 | 16830 |
| JS (Bun) | 2420,4 | 1,31 | 191 | 42 | 1 | 0 | -65 | 0 | 0 | 0 | 0 | 1 | 47696 | 36 | 4 | 102 | 102 |
| Python | 19182,7 | 0,92 | 247 | 0 | 82 | 82 | 81 | 0 | 0 | 0 | 0 | 2 | 30385 | 47 | 1 | 18 | 17 |
| Lua | 5986,8 | 1,15 | 568 | 0 | 1 | 1 | 0 | 563 | 0 | 0 | 0 | 1 | 30724 | 10 | 2 | — | — |
| LuaJIT | 1832,0 | 2,71 | 253 | 0 | 242 | 7 | 0 | 0 | 0 | 0 | 0 | 1 | 13937 | 24 | 3 | 0 | 0 |

## K8 naturel (`k8:natural:`)

| Implémentation | Temps par rép. (ms) | CPU / temps écoulé | Appels système | `futex` | `mmap` | `munmap` | `madvise` | `brk` | `mprotect` | `clone3` | `sched_yield` | `write` | Défauts de page | Changements de contexte | Migrations | malloc + calloc + realloc | free |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C | 578,8 | 0,96 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 14 | 0 | 0 | — | — |
| C (gcc) | 437,9 | 1,12 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 16 | 2 | 0 | — | — |
| C++ | 605,5 | 1,10 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 2 | 0 | — | — |
| Rust | 631,2 | 0,87 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 3 | 0 | — | — |
| Zig | 681,5 | 1,04 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | -2 | 2 | 0 | — | — |
| Odin | 1157,4 | 0,99 | 32772 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | -1 | 0 | — | — |
| C3 | 868,3 | 1,21 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 1 | 2 | 0 | — | — |
| D | 1943,4 | 0,97 | 89 | 90 | 0 | 0 | 0 | 0 | 0 | 0 | -2 | 1 | 0 | 42 | -0 | — | — |
| Nim | 564,9 | 1,20 | 2 | 0 | -0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 2 | 0 | — | — |
| Ada | 570,6 | 1,08 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | -0 | 4 | 0 | — | — |
| Fortran | 558,1 | 0,96 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | -0 | 0 | 0 | — | — |
| Fortran (flang) | 2299,1 | 0,91 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 4 | 6 | 2 | — | — |
| Chapel | 1008,5 | 1,07 | 720 | 16 | 0 | 0 | 0 | 0 | 0 | 0 | 704 | 1 | 14 | 6 | 0 | — | — |
| Julia | 661,7 | 1,74 | 3000 | 776 | -0 | -3 | 2054 | 14 | 142 | 0 | 0 | 9 | 8624 | 240 | -1 | — | — |
| Mojo | 913,2 | 0,73 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | -4 | 2 | -0 | — | — |
| C# | 504,6 | 1,04 | 136 | 4 | 3 | 0 | 20 | 0 | 19 | 0 | 1 | 2 | 264 | 7 | -0 | — | — |
| Java | 241,1 | 1,39 | 196 | 113 | 2 | 0 | 0 | 0 | -1 | 0 | -6 | 26 | -13 | 58 | 19 | — | — |
| Go | 866,1 | 1,95 | 2006 | 966 | 1 | 0 | 40 | 0 | 0 | 0 | 442 | 2 | 1696 | 615 | 12 | — | — |
| Haskell | 1607,8 | 1,05 | 64972 | 59787 | 0 | -0 | -0 | 0 | 0 | 0 | -228 | 0 | 4 | 21732 | 114 | — | — |
| OCaml | 236,0 | 0,97 | 240 | 0 | 238 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 1901 | 1 | 0 | — | — |
| JavaScript | 1094,6 | 1,24 | 646 | 565 | 7 | 16 | 10 | -1 | 44 | 0 | -0 | 2 | 748 | 160 | 23 | — | — |
| JS (Bun) | 654,8 | 0,82 | 6260 | 2190 | 0 | 0 | 4 | 0 | 0 | 0 | 0 | 2 | 462 | 708 | 11 | — | — |
| Python | 14050,3 | 0,98 | 13 | 0 | 3 | 3 | 3 | 0 | 0 | 0 | 0 | 4 | -154 | 16 | 0 | — | — |
| Lua | 6685,2 | 0,89 | 32545 | 0 | 0 | 0 | 0 | -226 | 0 | 0 | 0 | 1 | -7442 | 13 | 0 | — | — |
| LuaJIT | 4057,5 | 1,16 | 32772 | 0 | -0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | -12 | 4 | -0 | — | — |

## K8 tuned (`k8:tuned:`)

| Implémentation | Temps par rép. (ms) | CPU / temps écoulé | Appels système | `futex` | `mmap` | `munmap` | `madvise` | `brk` | `mprotect` | `clone3` | `sched_yield` | `write` | Défauts de page | Changements de contexte | Migrations | malloc + calloc + realloc | free |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C | 235,4 | 0,87 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 1 | 1 |
| C (gcc) | 130,4 | 1,03 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 1 | 0 | 1 | 1 |
| C++ | 175,9 | 1,12 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 1 | 0 | 0 | 0 |
| Rust | 273,7 | 1,00 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 2 | 1 | 0 | — | — |
| Zig | 177,4 | 1,13 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |
| Odin | 253,5 | 0,99 | 32772 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 1 | 0 | 0 | 0 |
| C3 | 225,9 | 1,12 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 1 | 1 | 0 | 0 | 0 |
| D | 214,2 | 1,36 | 22932 | 22755 | 0 | 0 | 0 | 0 | 0 | 0 | 176 | 1 | 2 | 654 | 1 | 0 | 0 |
| Nim | 307,7 | 1,01 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 1 | 2 | 0 | 0 | 0 |
| Ada | 63,0 | 1,21 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 1 | 0 | 0 | 0 | 0 |
| Fortran | 172,5 | 1,10 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 2 | 4 | 0 | 69 | 85 |
| Fortran (flang) | 270,5 | 0,93 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 1 | 0 | 23 | 23 |
| Chapel | 269,1 | 0,87 | 276 | 8 | 0 | -0 | 0 | 0 | 0 | 0 | 268 | 1 | 4 | -6 | 0 | 0 | 0 |
| Julia | 324,7 | 4,19 | -21 | -17 | -1 | -1 | -10 | -5 | -3 | 0 | 0 | 8 | 1636 | 775 | 13 | — | — |
| Mojo | 171,4 | 0,94 | 2 | 0 | 0 | -0 | 0 | 0 | 0 | 0 | 0 | 2 | -0 | 1 | 0 | 0 | 0 |
| C# | 241,3 | 1,10 | 12 | 6 | 1 | 1 | 0 | -0 | 1 | 0 | 1 | 2 | 5 | 3 | 0 | 114 | 48 |
| Java | 187,1 | 1,14 | 47 | 10 | 1 | 0 | 0 | 0 | -0 | 0 | -0 | 26 | 34 | 6 | -4 | 158 | 144 |
| Go | 223,1 | 1,01 | 171 | 53 | 1 | 0 | 0 | 0 | 0 | 0 | 58 | 2 | 17 | 51 | 1 | 0 | 0 |
| Haskell | 692,3 | 1,05 | 16204 | 15644 | 4 | -0 | 8 | 0 | 0 | 0 | -762 | 0 | 1260 | 5719 | 39 | 389 | 390 |
| OCaml | 204,3 | 1,15 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 1 | 1 | 0 | 0 | 0 |
| JavaScript | 454,8 | 1,13 | -14 | -60 | 2 | 4 | 2 | 0 | 36 | 0 | 0 | 2 | 460 | -22 | -8 | 839 | 839 |
| JS (Bun) | 303,4 | 1,04 | -2068 | -2076 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 406 | -652 | 10 | 3 | 3 |
| Python | 8404,9 | 0,92 | 4 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 4 | -174 | 14 | -1 | 8 | 8 |
| Lua | 3605,8 | 1,02 | 32771 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | -1 | 8 | 0 | — | — |
| LuaJIT | 2133,3 | 0,69 | 32733 | 0 | 0 | 0 | 0 | 0 | -38 | 0 | 0 | 1 | -0 | 5 | 0 | 0 | 0 |

## K9 naturel (`k9:natural:`)

| Implémentation | Temps par rép. (ms) | CPU / temps écoulé | Appels système | `futex` | `mmap` | `munmap` | `madvise` | `brk` | `mprotect` | `clone3` | `sched_yield` | `write` | Défauts de page | Changements de contexte | Migrations | malloc + calloc + realloc | free |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C | 12,5 | 1,62 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | -0 | 0 | 0 | 0 |
| C (gcc) | 14,2 | 2,03 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | -0 | 0 | 0 |
| C++ | 15,0 | 3,21 | 461 | 0 | 0 | 0 | 0 | 460 | 0 | 0 | 0 | 1 | 16392 | 0 | 0 | 4100 | 4100 |
| Rust | 29,8 | 1,38 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 4101 | 4099 |
| Zig | 18,2 | 2,94 | 5 | 0 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 16384 | 0 | 0 | 0 | 0 |
| Odin | 13,3 | 2,90 | 7 | 0 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 1 | 16386 | 0 | 0 | 2 | 2 |
| C3 | 13,8 | 3,00 | 5 | 0 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 1 | 16386 | 0 | 0 | 2 | 2 |
| D | 29,3 | 2,66 | 12 | 4 | 4 | 4 | 0 | 0 | 0 | 0 | 0 | 1 | 19527 | 2 | -0 | 26 | 22 |
| Nim | 34,8 | 1,29 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | -0 | 0 | 0 | 0 | 0 |
| Ada | 30,7 | 1,41 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | -0 | -0 | 0 | 0 | 0 |
| Fortran | 13,4 | 3,21 | 5 | 0 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 1 | 16386 | 0 | 0 | 30 | 36 |
| Fortran (flang) | 11,0 | 3,10 | 5 | 0 | 2 | 2 | 0 | 0 | 0 | 0 | 0 | 1 | 16386 | 2 | 0 | 8 | 10 |
| Chapel | 12,6 | 2,57 | 14 | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 4 | 1 | 1 | 3 | -0 | 0 | 0 |
| Julia | 20,2 | 22,52 | 290 | 209 | 2 | 2 | 10 | -0 | 53 | 0 | 0 | 7 | 16518 | 76 | 3 | — | — |
| Mojo | 155,2 | 1,39 | 4 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 1 | 260 | 2 | -0 | 0 | 0 |
| C# | 54,0 | 1,89 | 235 | 21 | 1 | 0 | 1 | 0 | 0 | 0 | 3 | 1 | 4 | 31 | 0 | 45 | 41 |
| Java | 14,9 | 4,80 | 42 | 24 | -0 | 0 | -0 | 0 | 0 | -0 | 0 | 13 | 1211 | 10 | 2 | 165 | 34 |
| Go | 36,8 | 1,83 | 161 | 44 | 1 | 0 | 45 | 0 | 0 | 0 | 23 | 1 | 766 | 32 | 2 | 0 | 0 |
| Haskell | 234,9 | 1,41 | 50 | 306 | 3 | 0 | 8 | 0 | 0 | 0 | -348 | 0 | 24616 | 137 | 4 | 7 | 7 |
| OCaml | 49,6 | 1,59 | 77 | 0 | 0 | 0 | 0 | 76 | 0 | 0 | 0 | 1 | 620 | 0 | 0 | 4098 | 4098 |
| JavaScript | 103,5 | 3,44 | 725 | 222 | 116 | 231 | 118 | 2 | 26 | 0 | 0 | 1 | 7429 | 207 | 9 | 9206 | 9205 |
| JS (Bun) | 116,9 | 2,28 | 454 | 178 | 0 | 0 | 108 | 0 | 0 | 0 | 0 | 1 | 15162 | 62 | 0 | 85 | 85 |
| Python | 1239,1 | 1,55 | 754 | 0 | 246 | 246 | 246 | 13 | 0 | 0 | 0 | 2 | 63538 | 6 | 0 | 55348 | 4098 |
| Lua | 547,8 | 1,43 | 42 | 0 | 0 | 0 | 0 | 39 | 0 | 0 | 0 | 1 | 3768 | 2 | 0 | 1,07e+05 | 53276 |
| LuaJIT | 41,8 | 1,49 | 58 | 0 | 54 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 1738 | 0 | 0 | 0 | 0 |

## Exécutions écartées

* allocations : Lua k7:natural: R=2 (code -1, délai dépassé : trop d'appels pour une uprobe)
* allocations : Fortran (flang) k7:natural: R=1 (code -1, délai dépassé : trop d'appels pour une uprobe)
* allocations : C3 k7:natural: R=1 (code -1, délai dépassé : trop d'appels pour une uprobe)
* allocations : Julia k1:natural:energy R=37 (code -1, délai dépassé : trop d'appels pour une uprobe)
* allocations : Julia k9:natural: R=39 (code -1, délai dépassé : trop d'appels pour une uprobe)
* allocations : Ada k7:natural: R=2 (code -1, délai dépassé : trop d'appels pour une uprobe)
* allocations : Julia k6:natural:q1 R=4 (code -1, délai dépassé : trop d'appels pour une uprobe)
* allocations : Lua k1:natural:energy R=3 (code -1, délai dépassé : trop d'appels pour une uprobe)
* allocations : Lua k7:natural: R=1 (code -1, délai dépassé : trop d'appels pour une uprobe)
* allocations : Julia k6:natural:q1 R=12 (code -1, délai dépassé : trop d'appels pour une uprobe)
* allocations : Lua k8:tuned: R=1 (code -1, délai dépassé : trop d'appels pour une uprobe)
* allocations : Julia k7:natural: R=1 (code -1, délai dépassé : trop d'appels pour une uprobe)
* allocations : Julia k8:tuned: R=4 (code -1, délai dépassé : trop d'appels pour une uprobe)
* allocations : Rust k8:tuned: R=6 (code -1, délai dépassé : trop d'appels pour une uprobe)
* allocations : C (gcc) k7:natural: R=3 (code -1, délai dépassé : trop d'appels pour une uprobe)
* allocations : Lua k1:natural:energy R=1 (code -1, délai dépassé : trop d'appels pour une uprobe)
* allocations : Lua k8:tuned: R=3 (code -1, délai dépassé : trop d'appels pour une uprobe)
* allocations : Fortran k7:natural: R=3 (code -1, délai dépassé : trop d'appels pour une uprobe)
* allocations : C++ k7:natural: R=1 (code -1, délai dépassé : trop d'appels pour une uprobe)
* allocations : Julia k1:natural:energy R=12 (code -1, délai dépassé : trop d'appels pour une uprobe)
* allocations : Julia k8:tuned: R=1 (code -1, délai dépassé : trop d'appels pour une uprobe)
* allocations : Julia k9:natural: R=13 (code -1, délai dépassé : trop d'appels pour une uprobe)
* allocations : Ada k7:natural: R=1 (code -1, délai dépassé : trop d'appels pour une uprobe)
* allocations : Fortran (flang) k7:natural: R=2 (code -1, délai dépassé : trop d'appels pour une uprobe)
* allocations : C k7:natural: R=3 (code -1, délai dépassé : trop d'appels pour une uprobe)
* allocations : C3 k7:natural: R=3 (code -1, délai dépassé : trop d'appels pour une uprobe)
* allocations : Julia k7:natural: R=3 (code -1, délai dépassé : trop d'appels pour une uprobe)
* allocations : C++ k7:natural: R=2 (code -1, délai dépassé : trop d'appels pour une uprobe)

## Pilote de contrôle du bruit

Écart-type du logarithme des médianes de processus (12 processus par case). A : protocole de la campagne ; B : CPU 3, `SCHED_FIFO`, interruptions ailleurs ; C : B et taille d'environnement aléatoire.

| Mesure | Médiane A (ms) | σ A | σ B | σ C | B / A [IC 95 %] | C / A [IC 95 %] |
|---|---|---|---|---|---|---|
| c:k1:soa:energy | 2,66 | 0,076 | 0,064 | 0,084 | 0,85 [0,33–1,43] | 1,11 [0,60–1,85] |
| c:k2:tuned:8388608 | 257,52 | 0,065 | 0,063 | 0,074 | 0,97 [0,49–1,91] | 1,14 [0,52–2,22] |
| c:k5:tuned: | 3,72 | 0,225 | 0,178 | 0,243 | 0,79 [0,23–1,40] | 1,08 [0,68–1,75] |
| rust:k2:tuned:8388608 | 265,09 | 0,046 | 0,059 | 0,054 | 1,28 [0,35–3,39] | 1,16 [0,49–3,06] |
| rust:k5:tuned: | 3,70 | 0,199 | 0,239 | 0,147 | 1,20 [0,74–1,98] | 0,74 [0,25–1,25] |

Moyenne géométrique B / A : 1,00 [0,64–1,33] ; règle du plan (moins de 0,7, intervalle sous 1) : non remplie.

Moyenne géométrique C / A : 1,03 [0,73–1,37] ; règle du plan (moins de 0,7, intervalle sous 1) : non remplie.

Indicateurs de la lenteur d'un processus (protocole A, corrélation de rang ; règle du plan : |ρ| ≥ 0,5) :

* psi_cpu_some_per_s : ρ = -0,03 (n = 60) ; non utilisable
* psi_mem_some_per_s : ρ = — (n = 60) ; non utilisable
* steal_per_s : ρ = 0,05 (n = 60) ; non utilisable
* context_switches : ρ = 0,12 (n = 60) ; non utilisable
* cpu_migrations : ρ = 0,23 (n = 60) ; non utilisable
