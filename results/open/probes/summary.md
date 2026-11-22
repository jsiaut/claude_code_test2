# Grille ouverte : notes des sondes (v4, point 6)

*Écrit par `tools/open/probes_summary.py` à partir de `results/open/probes/<langage>.txt`. Note ouverte : la
meilleure des bibliothèques de la liste qui comblent la case, jamais sous la note publiée (une sonde qui échoue
laisse la note publiée) ; « nommées » : réduite aux bibliothèques nommées par le dossier (calcul 4).*

| Langage | Case | Publiée | Ouverte | Nommées seules | Sondes |
|---|---|---|---|---|---|
| ada | C5 | 0 | 1 | 0 | lwt 1.2.0 : 1 |
| ada | D3 | 0 | 1 | 0 | cachelines 0.1.0 : 1 |
| c | F2 | 0 | 1 | 0 | hwloc 2.10.0 (libhwloc-dev 2.10.0-1build1) : 1 |
| cpp | F2 | 0 | 1 | 0 | hwloc 2.10.0 (libhwloc-dev 2.10.0-1build1) : 1 |
| d | A6 | 0 | 1 | 0 | soa 0.2.0 : 1 |
| d | F1 | 0.5 | 1 | 0.5 | mir-algorithm 3.22.5 : 1 |
| go | C5 | 0 | 0.5 | 0 | github.com/samber/lo/parallel v1.53.0 : 0.5 |
| go | D3 | 0 | 1 | 0 | github.com/templexxx/cpu v0.1.1 : 1 |
| go | F1 | 0.5 | 1 | 0.5 | gonum.org/v1/gonum/mat v0.17.0 : 1 |
| go | F2 | 0 | 1 | 0 | github.com/benjojo/numa (révision 1058a77) : 1 |
| haskell | C5 | 0.5 | 1 | 0.5 | parallel 3.3.0.0 : 1 |
| haskell | D2 | 0.5 | 0.5 | 0.5 | atomic-primops 0.8.8 : 0.5 |
| haskell | F4 | 0 | 1 | 0 | mmap 0.5.9 : 1 |
| java | D4 | 0 | 1 | 0 | net.openhft:affinity 2026.2 : 1 |
| java | F1 | 0.5 | 1 | 0.5 | org.tensorflow:ndarray 1.0.0 : 1 |
| java | F2 | 0 | 0.5 | 0 | org.apache.ignite:ignite-numa-allocator 2.18.0 : 0.5 |
| js | B2 | 0 | 0.5 | 0 | @protobufjs/pool 1.1.0 : 0.5 |
| js | F1 | 0 | 1 | 0 | ndarray 1.1.1 : 1 |
| julia | B2 | 0.5 | 0.5 | 0.5 | Bumper 0.7.2 : 0.5 |
| julia | C1 | 0.5 | 0.5 | 0.5 | VectorizationBase 0.21.74 : 0.5 |
| julia | D4 | 0.5 | 1 | 0.5 | ThreadPinningCore 0.4.5 : 1 |
| julia | F2 | 0.5 | 1 | 0.5 | NUMA 0.1.1 : 1 |
| lua | D1 | 0 | 0.5 | 0 | lua-llthreads2 0.1.6 : 0.5 |
| lua | F1 | 0 | 1 | 0 | vmsl 1.1 : 1 |
| mojo | C5 | 0 | 1 | 1 | MAX 26.7.0 (nommée) : 1 |
| mojo | D1 | 0.5 | 0.5 | 0.5 | MAX 26.7.0 (nommée) : 0.5 |
| mojo | F1 | 0.5 | 1 | 1 | MAX 26.7.0 (nommée) : 1 |
| nim | C1 | 0 | 0.5 | 0 | mmops 0.1.1 : 0.5 |
| nim | F1 | 0.5 | 1 | 0.5 | arraymancer 0.7.33 : 1 |
| ocaml | C2 | 0 | 0.5 | 0 | ocaml_intrinsics_kernel v0.17.3 : 0.5 |
| ocaml | C5 | 0 | 1 | 0 | domainslib 0.5.2 : 1 |
| ocaml | D4 | 0 | 1 | 0 | processor 0.2 : 1 |
| php | C5 | 0 | 0.5 | 0 | amphp/parallel-functions 2.0.0 : 0.5 |
| php | F1 | 0.5 | 1 | 0.5 | rindow/rindow-math-matrix 2.2.0 : 1 |
| python | C5 | 0.5 | 0.5 | 0.5 | dask 2026.8.0 : 0.5 |
| python | D2 | 0 | 1 | 0 | atomics 1.0.3 : 1 |
| python | F1 | 0.5 | 1 | 1 | numpy 2.5.5 (nommée) : 1 |
| rust | B2 | 0.5 | 1 | 0.5 | bumpalo 3.20.4 : 1 |
| rust | C1 | 0.5 | 1 | 0.5 | fearless_simd 1.2.0 : 1 |
| rust | C5 | 0 | 1 | 1 | rayon 1.12.0 : 1 |
| rust | D3 | 0 | 1 | 1 | cache-padded 1.3.0 : 1 ; crossbeam 0.8.5 (nommée) : 1 ; libc 0.2.191 (nommée) : 0.5 |
| rust | D4 | 0 | 1 | 1 | core_affinity 0.8.3 : 1 ; libc 0.2.191 (nommée) : 1 |
| rust | F1 | 0.5 | 1 | 0.5 | ndarray 0.17.2 : 1 |
| rust | F2 | 0 | 1 | 0 | hwlocality-sys 0.7.2 : 1 |
| rust | F4 | 0 | 1 | 1 | memmap2 0.9.12 : 1 ; libc 0.2.191 (nommée) : 1 |
| swift | B2 | 0.5 | 0.5 | 0.5 | swift-memory-allocation (révision 8742a8c) : 0.5 |
| swift | F1 | 0.5 | 1 | 0.5 | Matft 1.0.1 : 1 |

47 cases comblées ; 41 relevées par la piste ouverte, 6 inchangées (bibliothèque limitée à la note publiée).
