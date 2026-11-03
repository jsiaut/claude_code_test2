# Remarque sur Haskell : sondes de vérification (machine 19, 3 novembre, avant le plan)

Chaîne : GHC 9.14.1 (`/opt/ghc`), LLVM 18.1.3. Binaires de sonde dans `.work/haskell/` (hors dépôt), compilés depuis
`bench/haskell_k9h/Ms.hs` : `ref` (options du banc, identique au binaire publié), `noyield` (sans `-fno-omit-yields`),
`nofl` (sans `-fno-full-laziness`), `rel` (sans les deux). Temps : médiane et minimum d'un processus, `+RTS -N4`.

## Options (un processus)

| Clé | ref | noyield | nofl | rel | C (même hôte) |
|---|---|---|---|---|---|
| K4 naturel non trié | 81,36 ms | 12,28 | 72,46 | 12,37 | 1,95 |
| K5 naturel | 351,14 ms | 175,87 | 343,16 | 176,77 | 176,33 |
| K9 naturel | 199,50 ms | 189,04 | 123,79 | 109,88 | — |

Balayage ref → rel (un processus, 3 à 5 répétitions) : K1 naturel 88,9 → 85,7 ; mélangé 153,6 → 155,0 ; aos 22,4 →
23,2 ; soa 3,71 → 3,83 ; K4 trié 9,31 → 11,00 ; sans branchement 11,79 → 11,51 ; K5 tuned 6,27 → 6,54 ; Q6 naturel
47,5 → 51,2 ; Q1 naturel 59,2 → 57,8 ; Q6 tuned 33,2 → 29,3 ; Q1 tuned 56,0 → 58,6 ; K9 tuned 21,6 → 21,2 ms.
Variantes `mt` et K3, deux séries de 9 répétitions (ref puis rel) : Q6 `mt` 15,1 et 16,4 / 16,1 et 12,2 ms ; Q1 `mt`
22,6 et 18,9 / 20,3 et 19,8 ; K9 `mt` 13,4 et 13,3 / 12,8 et 13,4 ; K3 `sw_padded` 369 et 346 / 359 et 370 ; K3
`rmw_padded` 353 et 351 / 223 et 200 ms. Sommes de contrôle identiques partout.

K10 sans `-fno-omit-yields` (rel), trois processus de cinq répétitions et un échauffement : tuned 81, 140, 112 ms ;
natural 733, 787, 661 ms (médianes) ; aucun blocage. ref : tuned 97, natural 780 ms.

K7 naturel, une répétition (`k7_natural_probe.txt`) : ref `-N4` 50,86 s ; rel `-N4` 50,81 s ; rel `-N1` 51,25 s.

## Runtime (`+RTS -?` du binaire)

`-N[<n>]` : « Use <n> processors (default: 1, -N alone determines the number of processors) » ; `-qg[<n>]` : « Use
parallel GC only for generations >= <n> (default: 0, -qg alone turns off parallel GC) » ; `-qn<n>` : « Use <n> threads
for parallel GC (defaults to value of -N) ». Julia 1.12 de l'étude : `julia -t 4` → `Threads.ngcthreads()` = 4 ; sans
`-t` : 1 et 1.

`strace -f -c -e trace=futex,sched_yield`, K8 naturel, une répétition sans échauffement, binaire rel
(`strace_k8_natural_N4.txt`, `strace_k8_natural_N1.txt`) : `-N4` 87 414 `futex` et 465 `sched_yield` ; `-N1` 25
`futex` et 9 `sched_yield`.

## K5 et K1 : FMA vectorielle

`:browse GHC.Exts` (ghci 9.14.1) : aucune ligne `fmaddFloatX16#` ; `:browse GHC.Prim` : `fmaddFloatX16#`,
`fmsubFloatX16#`, `fnmaddFloatX16#` (définies dans `GHC.Internal.Prim`). Sonde `tools/haskell_check/probes/Fma.hs`
(`-O2 -fllvm -mavx512f -mfma`) : `fmaddFloatX16# 2 3 1` → `(7.0,7.0)`. Avec le générateur natif
(`ncg_wide_fma.txt`) : « sorry! (unimplemented feature or known bug) … Please use -fllvm for wide vector FMA support ».
K5 tuned, un processus de 7 répétitions : rel 6,16 ms ; avec `fmaddFloatX16#` 4,59 ms ; C 3,73 ms.

## K8 : allocation de l'arène et arbre longue durée

`+RTS -s`, K8 tuned sans échauffement, octets alloués pour 1 puis 3 répétitions :

| Binaire | 1 répétition | 3 répétitions | Par répétition |
|---|---|---|---|
| ref (`IORef Int`, compteur dans un n-uplet) | 2 065 442 232 | 5 323 392 064 | 1,63 Go |
| `IORef` remplacée par un `Ptr Int` | 718 805 256 | 1 281 282 040 | 281 Mo |
| les deux compteurs en mémoire brute (`haskell_fix`) | 450 365 048 | 476 005 120 | 12,8 Mo |

Le reste de 281 Mo : le compteur de valeurs rendu dans un n-uplet est boxé à chaque feuille
(`core_aBuild_counter_boxed.txt` : `(# s4, intToInt32# ipv1, I# (+# ww5 1#) #)`), 16 octets × 1 024 feuilles × 16 384
requêtes. Temps : 0,80 s (ref) → 0,26 s (`Ptr Int`) → 0,21 s.

K8 naturel, trois répétitions et un échauffement, `+RTS -s` : rel (arbre long mort après `lsum`) 1,786, 1,785,
1,722 s, 14 collections de génération 1 (pause moyenne 2,9 ms, maximum 9,4 ms), maximum des latences 4,6 à 8,6 ms ;
avec l'arbre gardé vivant (`touch#`) 1,866, 1,687, 1,726 s, 7 collections (pause moyenne 10,8 ms, maximum 32,0 ms),
maximum des latences 6,7 à 32,4 ms.

## K5 naturel

Core de `$wk5Natural` (`core_k5Natural.txt`) : boucle `joinrec` sur des `Float#` (`plusFloat# ww8 (timesFloat# ds4
ds1)`), deux vérifications de bornes par tableau, aucune allocation.

## Matrice (`tools/haskell_check/probes/Caps.hs`, `base` seul, `-O2`)

« B2 Foreign.Marshal.Pool : somme 8112000 » ; « B3 n-uplets non boxés : 71431071426 » (un million d'appels `NOINLINE`
rendant `(# Int#, Int# #)`, 2,0 Mo alloués pour tout le programme) ; « A7 Storable à tableau en ligne (taille, id,
somme) : (72,7,242.0) » (le 4e flottant du 8e enregistrement relu à plat à l'octet 7 × 72 + 8 + 12).
