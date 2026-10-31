# Choix des variantes « natural » (docs/METHODOLOGY.md, section 8)

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
| JavaScript | Node (V8) | objet littéral / `Array` | `Map` | objets (GC) | tableau de tableaux | `postMessage` entre Workers |
| Python | CPython 3.15 | `class` ordinaire / `list` | `dict` | objets `__slots__` (GC + comptage) | liste de listes | `queue.Queue` bornée + `threading` |
| Haskell | ghc -O2 -fllvm | `data` à champs stricts / liste | `Data.IntMap.Strict` | constructeurs (GC) | `UArray` immuable | `Control.Concurrent.Chan` |
| C3 | -O3 | `struct` / tranche `mem::new_array` (valeurs) | `HashMap` | `alloc::new` | tableau 2D fixe | `BufferedChannel` |
| D | ldc2 -O3 -release | `struct` / tableau dynamique (valeurs) | tableau associatif intégré `Agg[uint]` | `class` + `new` (GC) | `double[][]` | `std.concurrency` (messages) |
| Rust | `-C opt-level=3` (bornes vérifiées) | `struct` / `Vec` (valeurs) | `HashMap` (SipHash) | `Box<Node>` | `Vec<Vec<f64>>` | `mpsc::sync_channel` bornée |
| Chapel | `chpl --fast` (sans vérifications) | `record` / tableau (valeurs) | `map` (module Map) | classe `owned` | tableau 2D `[0..<M, 0..<M]` | tampon de variables `sync` |
| Nim | `-d:release` (vérifications conservées), ORC | `object` / `seq` (valeurs) | `Table` | `ref object` (ORC) | `seq[seq[float]]` | `Channel[T]` |
| Mojo | `mojo build` | `struct` / `List` (valeurs) | `Dict` | allocation manuelle par nœud (pas de type récursif possédé simple) | `List[List[Float64]]` | `Deque` + `BlockingSpinLock` (seules primitives de std) |
| Go | `go build`, GOAMD64=v4 | `struct` / slice (valeurs) | `map[uint32]agg` | `&Node{}` (GC) | `[][]float64` | `chan uint64` bufferisé |
| OCaml | ocamlopt -O3 (flambda) | enregistrement (champs flottants stockés à plat) / `array` de pointeurs vers les enregistrements | `Hashtbl` | variants (GC) | `float array array` | `Queue` + `Mutex` + `Condition` |
| Lua | PUC-Lua 5.5 | table à champs nommés / table | table | tables (GC) | table de tables | coroutines (pas de threads en Lua standard) |

Annexes (hors classement) : `c_gcc` (même source C, gcc-16), `fortran_flang` (même source,
flang-23), `luajit` (dialecte 5.1 + FFI), `js_bun` (même source JS, JavaScriptCore),
`python_ft` (CPython 3.15 sans GIL).

## Justifications des cas discutables

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
* **Lua** : le langage standard n'a ni threads ni tableaux typés. Les noyaux
  multi-threads s'exécutent en séquence ou en coroutines, et c'est signalé par `META`.
* **Mojo** : Mojo 1.2 n'expose pas d'API publique de threads CPU (`parallelize` est dans
  MAX, hors `std`). Les variantes concurrentes utilisent `std.runtime._asyncrt`, privé
  mais livré avec `std`.
