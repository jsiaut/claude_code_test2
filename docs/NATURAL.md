# Choix des variantes « natural » (docs/METHOD.md, section 5)

Règle : le code qu'un développeur écrit spontanément en suivant la documentation officielle :
type d'enregistrement et conteneur **par défaut**, aucune annotation de performance, mode de
compilation « release » documenté de la chaîne, vérifications à l'exécution conservées
quand ce mode les conserve.

Les noyaux sont définis mono-thread, sauf les variantes `mt`. Quand l'idiome naturel d'un
langage est parallèle par défaut (`+ reduce` et `forall` en Chapel), la variante natural
utilise la boucle sérielle équivalente, et la forme parallèle n'apparaît que dans `mt`.

| Langage | Mode de compilation natural | K1 : enregistrement / collection | K7 : table de hachage | K8 : allocation des nœuds | K9 : tableau 2D | K10 : file entre threads |
|---|---|---|---|---|---|---|
| C | clang -O3 -march=native | `struct` / tableau `malloc` (valeurs) | aucune en bibliothèque standard : chaînage séparé, un `malloc` par entrée | `malloc` / `free` | tableau 2D C99 contigu | file bornée `pthread_mutex` + 2 `pthread_cond` |
| C++ | g++ -O3 -march=native | `struct` / `std::vector` (valeurs) | `std::unordered_map` | `std::unique_ptr` + `make_unique` | `std::vector<std::vector<double>>` | `std::queue` + `std::mutex` + 2 `std::condition_variable` |
| C# | `dotnet build -c Release` | `sealed class` (référence) / `List<T>` | `Dictionary<uint, (uint, ulong)>` | `class` (GC) | `double[,]` (rectangulaire) | `BlockingCollection<long>` bornée |
| Java | `javac` + HotSpot C2 | `record` (référence) / `ArrayList` | `HashMap<Integer, Agg>` | `new` (GC G1) | `double[][]` | `ArrayBlockingQueue<Long>` |
| Zig | `-O fast` | `struct` / `std.ArrayList` (valeurs) | `std.AutoHashMap` | `allocator.create` (allocateur généraliste) | tableau `[M][M]f64` | `std.Io.Queue` |
| Odin | `-o:speed` (vérification des bornes active) | `struct` / `[dynamic]` (valeurs) | `map[u32]Agg` | `new(Node)` (allocateur du contexte) | tableau `[M][M]f64` | `core:sync/chan` bufferisé |
| Julia | JIT, `-O3` | `struct` immuable isbits / `Vector` (valeurs en ligne) | `Dict` | `mutable struct` (GC) | `Matrix{Float64}` parcourue en colonnes (manuel) | `Channel{UInt64}` bornée |
| Ada | gnatmake -O3, **vérifications actives** (défaut GNAT) | `record` / tableau (valeurs) | `Ada.Containers.Hashed_Maps` | `new` + `Unchecked_Deallocation` | tableau 2D Ada contigu | objet protégé (entrées gardées) |
| Fortran | gfortran -O3 -march=native | type dérivé / tableau allouable (valeurs) | aucune en standard : chaînage avec pointeurs | `allocate` de pointeurs | tableau 2D allouable, syntaxe tableau | verrou OpenMP (pas de variable de condition) |
| Haskell | ghc -O2 -fllvm | `data` à champs stricts / liste | `Data.IntMap.Strict` | constructeurs (GC) | `UArray` immuable | `Control.Concurrent.Chan` |
| C3 | -O3 | `struct` / tranche `mem::new_array` (valeurs) | `HashMap` | `alloc::new` | tableau 2D fixe | `BufferedChannel` |
| D | ldc2 -O3 -release | `struct` / tableau dynamique (valeurs) | tableau associatif intégré `Agg[uint]` | `class` + `new` (GC) | `double[][]` | `std.concurrency` (messages) |
| Rust | `-C opt-level=3` (bornes vérifiées) | `struct` / `Vec` (valeurs) | `HashMap` (SipHash) | `Box<Node>` | `Vec<Vec<f64>>` | `mpsc::sync_channel` bornée |
| Chapel | `chpl --fast` (sans vérifications) | `record` / tableau (valeurs) | `map` (module Map) | classe `owned` | tableau 2D `[0..<M, 0..<M]` | tampon de variables `sync` |
| Nim | `-d:release` (vérifications conservées), ORC | `object` / `seq` (valeurs) | `Table` | `ref object` (ORC) | `seq[seq[float]]` | `Channel[T]` |
| Mojo | `mojo build` | `struct` / `List` (valeurs) | `Dict` | allocation manuelle par nœud (pas de type récursif possédé simple) | `List[List[Float64]]` | `Deque` + `BlockingSpinLock` (seules primitives de std) |
| Go | `go build`, GOAMD64=v4, sans `GOEXPERIMENT=simd` | `struct` / slice (valeurs) | `map[uint32]agg` | `&Node{}` (GC) | `[][]float64` | `chan uint64` bufferisé |
| OxCaml | ocamlopt -O3 (flambda2) ; la source d'OCaml, à l'octet près | enregistrement (champs flottants stockés à plat) / `array` de pointeurs vers les enregistrements | `Hashtbl` | variants (GC) | `float array array` | `Queue` + `Mutex` + `Condition` |
| Swift | `swiftc -O` (bornes et débordements vérifiés), module entier, mode Swift 6 | `struct` / `Array` (valeurs en ligne) | `Dictionary<UInt32, Agg>` (`subscript(_:default:)` et méthode `mutating`) | `class` à champs `var` (ARC) | `[[Double]]` | `AsyncStream` entre deux tâches (tampon non borné ; seule file de la bibliothèque standard) |
| FreePascal | `fpc -O3` (vérifications de bornes et de débordement désactivées par défaut), cible COREAVX2 | `record` / tableau dynamique `array of` (valeurs en ligne) | `TDictionary<LongWord, TAgg>` de Generics.Collections (`TryGetValue` puis `AddOrSetValue` : deux recherches par ligne, valeurs en `record`) | `New` / `Dispose` d'un `record` par pointeur (gestionnaire de mémoire de la RTL) | tableau statique `array[0..M-1, 0..M-1] of Double` (contigu, alloué par `New`) | `TQueue<QWord>` de Generics.Collections + section critique + deux événements de la RTL |

Annexes (hors classement) : `c_gcc` (même source C, gcc-16), `fortran_flang` (même source, flang-23).

Les documents et les répertoires cités ici qui ne sont plus dans le dépôt sont dans l'archive (`docs/HISTORY.md`).

## Justifications des cas discutables

* **Swift (ajouté le 5 novembre, `docs/SWIFT.md`)** : `swift build -c release` compile en `-O` sur le module entier, qui garde les vérifications de bornes et de débordement ; le banc appelle `swiftc` avec ces options et le mode de langage Swift 6 (celui des paquets créés par la chaîne 6.x). Le guide du langage recommande les structures par défaut (K1) ; K8 prend la classe à champs `var` des exemples du guide (la classe finale à champs `let` est une sensibilité, comme l'arbre en `UniqueBox` de la 6.4, qui ne compile qu'avec un `deinit {}` vide : remarque sur Swift, `docs/SWIFT.md`, 5) ; la bibliothèque standard n'a pas de file bornée : K10 prend `AsyncStream` (hors score).
* **FreePascal (ajouté le 6 novembre, `docs/FPC.md`)** : FPC n'a pas de mode « release » imposé par un outil de construction ; le `fpc.cfg` livré en propose un (`-dRELEASE` : `-O2 -Xs`), et la documentation de `fpc -h` décrit `-O3` comme « -O2 + optimisations lentes » et `-O4` comme pouvant avoir des « effets de bord inattendus ». Le banc prend `-O3`, le plus haut niveau sûr, comme `-O3` pour C ; le mode `RELEASE` du `fpc.cfg` est une sensibilité (`bench/fpc_o2`). Les vérifications de bornes et de débordement sont désactivées par défaut en FPC (`{$R-}`, `{$Q-}`) : le naturel les laisse ainsi. K1 : `record` dans un `array of` (le conteneur par défaut de l'Object Pascal moderne) ; K7 : `TDictionary` (Generics.Collections, livrée avec FPC 3.2, compatible Delphi), valeurs en `record`, sans accès en place (la bibliothèque n'en offre pas) ; K8 : `New` / `Dispose` d'un `record` pointé, la forme des manuels de Pascal (les nœuds de classe, `TObject.Create` / `Free`, sont une sensibilité) ; K9 : le tableau à deux dimensions de base du langage, contigu, de taille fixée à la compilation comme M (comme Ada, Zig, Odin et C3 ; `array of array of Double` est une sensibilité) ; K10 : la RTL n'a ni file bloquante ni variable de condition, d'où `TQueue` + section critique + événements (hors score).
* **OxCaml (28 novembre, `docs/V6_1.md`)** : OxCaml est un sur-ensemble d'OCaml, et il a pris sa place au classement.
  Son code naturel est la source d'OCaml, à l'octet près (`bench/oxcaml/ms.ml`), compilée par `ocamlopt -O3` : ses
  types non boxés, ses modes (`stack_`, `local`) et ses vecteurs sont des annotations de performance, que la règle
  écarte ; ils n'entrent que dans les formes du plafond (`bench/oxcaml/ox.ml`). Les variantes à quatre fils créent
  leurs domaines par `Domain.spawn`, comme en OCaml ; OxCaml le signale par une alerte et recommande `Multicore`, de sa
  bibliothèque `threads` : la source commune avec le témoin est gardée, l'alerte est tue à la compilation.
* **C et Fortran (K7)** : la bibliothèque standard n'a pas de table de hachage. Le chaînage
  séparé avec une allocation par entrée est la structure des manuels (K&R 6.6 pour C).
* **C# (K1)** : les directives de conception .NET recommandent une classe au-delà de 16
  octets. Le `struct` de 64 octets sert à la variante `aos`.
* **Java (K1)** : `record` est le type d'enregistrement par défaut depuis Java 16. Les
  types valeur (Valhalla) ne sont pas dans le JDK 27 stable.
* **Julia (K9)** : le manuel (*Performance Tips*) demande de parcourir les tableaux
  dans l'ordre des colonnes. C'est donc ce que fait le code naturel.
* **Ada** : les vérifications à l'exécution sont actives par défaut dans GNAT, et la
  documentation ne recommande pas de les retirer en production. La variante tuned les
  supprime localement (`pragma Suppress`).
* **Rust** : le mode release conserve la vérification des bornes. La variante tuned
  l'évite le plus souvent par itérateurs ou `get_unchecked` ; l'arène de K8 tuned garde `Vec::push` et des accès
  vérifiés (relevé par la remarque sur Rust, `docs/RUST.md` ; l'arène écrite comme en C y est une sensibilité).
* **Chapel** : `--fast` est l'option que recommande la documentation pour mesurer les
  performances, et elle retire les vérifications.
* **Haskell** : `ghc -O2 -fllvm` (le générateur natif de GHC 9.14.1 calcule faux le SIMD 256/512 bits et refuse la
  FMA vectorielle), avec les options de la cible et le runtime multi-thread ; `+RTS -N4` pour tous les noyaux, comme
  `-t 4` pour Julia. Le banc publié ajoutait `-fno-omit-yields` et `-fno-full-laziness`, hors de ce mode : ses données
  sont corrigées depuis la remarque sur Haskell (`docs/HASKELL.md`), la copie `bench/haskell_fix` suit ce mode.
* **Go** : `simd/archsimd` demande `GOEXPERIMENT=simd`. Seules les dix variantes à SIMD explicite sont compilées
  avec cette expérience ; le code naturel et toutes les autres variantes le sont sans elle, comme un programme Go qui
  n'utilise pas ce paquet. Jusqu'au 27 novembre, tout le banc l'était avec, ce qui faussait K1 (`docs/V5_4.md`).
* **Mojo** : Mojo 1.2 n'expose pas d'API publique de threads CPU (`parallelize` est dans
  MAX, hors `std`). Les variantes concurrentes utilisent `std.runtime._asyncrt`, privé
  mais livré avec `std`.
