# Corrections du classement publié reportées dans les sources publiées (v4, point 4)

*`docs/V4_CONVERGE.md`, 4.1, écart 1 ; outil : `tools/converge/corrections.py` (correctifs dans `results/converge/patches/`) ; validation : `results/converge/validation_base.txt`. La source non corrigée de chaque langage est celle du commit `ea2da12` (code mesuré par les points 2 et 3).*

Chaque correction est la différence entre la source publiée au commit qui a créé la copie corrigée de la remarque et cette copie telle qu'elle est, reportée sur la source actuelle (tailles du point 2, modes du point 3). Les en-têtes des copies sont remplacés par une note qui cite la remarque.

| Langage | Copie(s) | Morceaux | Clés corrigées dans le classement publié | Notes |
|---|---|---|---|---|
| d | `d_fix`, `d_k9h` | d_fix : 2 ; d_k9h : 2 | k6 mt q1, k6 tuned q1 ; K9 (harnais commun, `docs/K9.md`) |  |
| rust | `rust_fix`, `rust_k9h` | rust_fix : 1 ; rust_k9h : 2 | k7 tuned ; K9 (harnais commun, `docs/K9.md`) |  |
| java | `java_fix`, `java_k9h` | java_fix : 5 ; java_k9h : 1 | k1 soa energy, k5 tuned ; K9 (harnais commun, `docs/K9.md`) |  |
| ada | `ada_fix` | ada_fix : 8 | k1 aos energy, k1 soa energy, k2 tuned 16384, k2 tuned 262144, k2 tuned 8388608, k6 mt q1, k6 mt q6, k6 tuned q1, k6 tuned q6, k9 mt, k9 tuned | K9 déjà au harnais commun |
| fortran | `fortran_fix_k9h` | fortran_fix_k9h : 11 | k1 natural_shuffled energy, k1 natural energy, k2 tuned 16384, k2 tuned 262144, k2 tuned 8388608, k4 branchless_unsorted, k4 natural_unsorted, k6 natural q1, k6 natural q6, k9 natural ; K9 (harnais commun, `docs/K9.md`) | copie `fortran_fix_k9h` : correction et harnais commun de K9 |
| go | `go_fix` | go_fix : 5 | k1 soa energy, k5 natural, k5 tuned, k6 mt q6, k6 tuned q6 ; K9 (harnais commun, `docs/K9.md`) (et rapports de K9 de la remarque) |  |
| haskell | `haskell_fix` | haskell_fix : 7 | k1 aos energy, k1 natural_shuffled energy, k1 natural energy, k1 soa energy, k2 tuned 16384, k2 tuned 16777216, k2 tuned 2097152, k2 tuned 262144, k2 tuned 268435456, k2 tuned 33554432, k2 tuned 524288, k2 tuned 65536, k2 tuned 67108864, k2 tuned 8388608, k3 rmw_packed, k3 rmw_padded, k3 sw_packed, k3 sw_padded, k4 branchless_unsorted, k4 natural_sorted, k4 natural_unsorted, k5 natural, k5 tuned, k6 mt q1, k6 mt q6, k6 natural q1, k6 natural q6, k6 tuned q1, k6 tuned q6, k7 natural, k7 tuned, k8 natural, k8 tuned ; K9 (harnais commun, `docs/K9.md`) (et rapports de K9 de la remarque) | morceau de K8 `tuned` reporté à la main (tailles du point 2) ; `build.sh` : ni `-fno-full-laziness` ni `-fno-omit-yields` |
| ocaml | `ocaml_fix` | ocaml_fix : 5 | k1 aos energy, k6 mt q6, k6 tuned q6, k7 tuned, k8 tuned ; K9 (harnais commun, `docs/K9.md`) | morceau de K8 `tuned` reporté à la main (tailles du point 2) ; `build.sh` : bibliothèque `runtime_events` (horloge monotone) |
| js | `js_fix` | js_fix : 2 | k7 tuned ; K9 (harnais commun, `docs/K9.md`) |  |
| python | `python_fix` | python_fix : 5 | k3 rmw_packed, k3 rmw_padded, k3 sw_packed, k3 sw_padded, k6 mt q1, k6 mt q6, k8 natural ; K9 (harnais commun, `docs/K9.md`) (et rapports de K9 de la remarque) |  |
| lua | `lua_fix` | lua_fix : 6 | k3 rmw_packed, k3 rmw_padded, k3 sw_packed, k3 sw_padded, k4 branchless_unsorted, k4 natural_sorted, k4 natural_unsorted, k6 mt q6, k6 tuned q6, k8 natural ; K9 (harnais commun, `docs/K9.md`) |  |
| cpp | `cpp_k9h` | cpp_k9h : 1 | K9 (harnais commun, `docs/K9.md`) |  |
| zig | `zig_k9h` | zig_k9h : 2 | K9 (harnais commun, `docs/K9.md`) |  |
| odin | `odin_k9h` | odin_k9h : 1 | K9 (harnais commun, `docs/K9.md`) |  |
| c3 | `c3_k9h` | c3_k9h : 1 | K9 (harnais commun, `docs/K9.md`) |  |
| nim | `nim_k9h` | nim_k9h : 2 | K9 (harnais commun, `docs/K9.md`) |  |
| csharp | `csharp_k9h` | csharp_k9h : 3 | K9 (harnais commun, `docs/K9.md`) |  |
| julia | `julia_k9h` | julia_k9h : 1 | K9 (harnais commun, `docs/K9.md`) |  |
| mojo | `mojo_k9h` | mojo_k9h : 2 | K9 (harnais commun, `docs/K9.md`) |  |
| bqn | `bqn_rq` (errata seuls) | à la main | k9 natural, tuned, mt (somme de contrôle hors chrono) ; k7 natural (idiome de la documentation) | les blocs de `bqn_rq` restent une sensibilité (`docs/BQN.md`, 5.4) ; `k7 natural_arr` devient `natural`, l'ancien naturel `natural_map` |

Langages sans correction à reporter : C, Chapel, Swift, FreePascal, PHP (K9 déjà au harnais commun ; aucune correction d'implémentation dans `results/transfers.json`). La correction d'Odin (`odin_fix`) n'a pas été reportée au classement publié (`docs/ODIN.md`, 4.2, écart au plan) : elle ne l'est pas ici.
