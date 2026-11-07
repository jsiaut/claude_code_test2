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
| Python | CPython 3.15 | `class` ordinaire / `list` | `dict` | objets d'une `class` ordinaire (GC + comptage ; `__slots__` jusqu'au 5/11, corrigé par la remarque sur Lua) | liste de listes | `queue.Queue` bornée + `threading` |
| Haskell | ghc -O2 -fllvm | `data` à champs stricts / liste | `Data.IntMap.Strict` | constructeurs (GC) | `UArray` immuable | `Control.Concurrent.Chan` |
| C3 | -O3 | `struct` / tranche `mem::new_array` (valeurs) | `HashMap` | `alloc::new` | tableau 2D fixe | `BufferedChannel` |
| D | ldc2 -O3 -release | `struct` / tableau dynamique (valeurs) | tableau associatif intégré `Agg[uint]` | `class` + `new` (GC) | `double[][]` | `std.concurrency` (messages) |
| Rust | `-C opt-level=3` (bornes vérifiées) | `struct` / `Vec` (valeurs) | `HashMap` (SipHash) | `Box<Node>` | `Vec<Vec<f64>>` | `mpsc::sync_channel` bornée |
| Chapel | `chpl --fast` (sans vérifications) | `record` / tableau (valeurs) | `map` (module Map) | classe `owned` | tableau 2D `[0..<M, 0..<M]` | tampon de variables `sync` |
| Nim | `-d:release` (vérifications conservées), ORC | `object` / `seq` (valeurs) | `Table` | `ref object` (ORC) | `seq[seq[float]]` | `Channel[T]` |
| Mojo | `mojo build` | `struct` / `List` (valeurs) | `Dict` | allocation manuelle par nœud (pas de type récursif possédé simple) | `List[List[Float64]]` | `Deque` + `BlockingSpinLock` (seules primitives de std) |
| Go | `go build`, GOAMD64=v4 | `struct` / slice (valeurs) | `map[uint32]agg` | `&Node{}` (GC) | `[][]float64` | `chan uint64` bufferisé |
| OCaml | ocamlopt -O3 (flambda) | enregistrement (champs flottants stockés à plat) / `array` de pointeurs vers les enregistrements | `Hashtbl` | variants (GC) | `float array array` | `Queue` + `Mutex` + `Condition` |
| Lua | PUC-Lua 5.5 | table à champs nommés / table | table | tables à champs nommés (GC ; tables positionnelles `{v, false, false}` jusqu'au 5/11, corrigé par la remarque sur Lua) | table de tables | coroutines (pas de threads en Lua standard) |
| Swift | `swiftc -O` (bornes et débordements vérifiés), module entier, mode Swift 6 | `struct` / `Array` (valeurs en ligne) | `Dictionary<UInt32, Agg>` (`subscript(_:default:)` et méthode `mutating`) | `class` à champs `var` (ARC) | `[[Double]]` | `AsyncStream` entre deux tâches (tampon non borné ; seule file de la bibliothèque standard) |
| FreePascal | `fpc -O3` (vérifications de bornes et de débordement désactivées par défaut), cible COREAVX2 | `record` / tableau dynamique `array of` (valeurs en ligne) | `TDictionary<LongWord, TAgg>` de Generics.Collections (`TryGetValue` puis `AddOrSetValue` : deux recherches par ligne, valeurs en `record`) | `New` / `Dispose` d'un `record` par pointeur (gestionnaire de mémoire de la RTL) | tableau statique `array[0..M-1, 0..M-1] of Double` (contigu, alloué par `New`) | `TQueue<QWord>` de Generics.Collections + section critique + deux événements de la RTL |
| BQN | CBQN 0.12.0, `make o3n` (la construction que recommande le README de CBQN sur x86-64 : -O3 -march=native), JIT actif par défaut, indices toujours vérifiés | matrice n×16 de f64, une particule par rangée (pas de type d'enregistrement ni de f32 : les espaces de noms à champs nommés sont une sensibilité) | l'idiome de la documentation : classement `⊐`, histogramme `/⁼`, regroupement `⊔` puis `+´¨` (corrigé le 6/11, remarque sur BQN ; `•HashMap` ligne à ligne jusque-là) | listes imbriquées ⟨valeur, gauche, droite⟩ (comptage de références et ramasse-miettes ; les espaces de noms sont une sensibilité) | matrice 2048×2048 de f64, voisins par décalages (`»`, `«`, `»˘`, `«˘`) et bords recollés | aucune : ni threads ni coroutines dans la bibliothèque système (pas de K10) |
| PHP | CLI de PHP 8.5.12, php.ini-production, OPcache et JIT tracing (le mode que recommande le manuel ; la CLI n'active ni l'un ni l'autre par défaut : sensibilité) | classe à propriétés `float` typées, promues par le constructeur / tableau (liste) d'objets, en références (les tableaux associatifs à clés nommées sont une sensibilité) | le tableau de PHP (table de hachage ordonnée), un couple `[compte, somme]` par clé | objets d'une classe (comptage de références et collecteur de cycles) | tableau de tableaux | Fibers (ni threads ni file entre processus dans le langage ; hors score) |

Annexes (hors classement) : `c_gcc` (même source C, gcc-16), `fortran_flang` (même source,
flang-23), `luajit` (dialecte 5.1 + FFI), `js_bun` (même source JS, JavaScriptCore),
`python_ft` (CPython 3.15 sans GIL).

## Justifications des cas discutables

* **Python et Lua (K8, corrigé le 5 novembre)** : le naturel de K8 déclarait `__slots__` en Python (une annotation de
  mémoire et de vitesse) et rangeait ses nœuds dans des tables positionnelles en Lua (une astuce : la partie tableau),
  contre la règle ci-dessus et contre leur propre K1 naturel. Les copies publiées (`python_k9h`, `lua_k9h`) gardent leur
  code ; la correction (`python_k8n`, `lua_fix`) est reportée par transfert (`docs/LUA.md`, `docs/PYTHON.md` 4.8).

* **Swift (ajouté le 5 novembre, `docs/SWIFT.md`)** : `swift build -c release` compile en `-O` sur le module entier, qui garde les vérifications de bornes et de débordement ; le banc appelle `swiftc` avec ces options et le mode de langage Swift 6 (celui des paquets créés par la chaîne 6.x). Le guide du langage recommande les structures par défaut (K1) ; K8 prend la classe à champs `var` des exemples du guide (la classe finale à champs `let` est une sensibilité, comme l'arbre en `UniqueBox` de la 6.4, qui ne compile qu'avec un `deinit {}` vide : remarque sur Swift, `docs/SWIFT.md`, 5) ; la bibliothèque standard n'a pas de file bornée : K10 prend `AsyncStream` (hors score).
* **FreePascal (ajouté le 6 novembre, `docs/FPC.md`)** : FPC n'a pas de mode « release » imposé par un outil de construction ; le `fpc.cfg` livré en propose un (`-dRELEASE` : `-O2 -Xs`), et la documentation de `fpc -h` décrit `-O3` comme « -O2 + optimisations lentes » et `-O4` comme pouvant avoir des « effets de bord inattendus ». Le banc prend `-O3`, le plus haut niveau sûr, comme `-O3` pour C ; le mode `RELEASE` du `fpc.cfg` est une sensibilité (`bench/fpc_o2`). Les vérifications de bornes et de débordement sont désactivées par défaut en FPC (`{$R-}`, `{$Q-}`) : le naturel les laisse ainsi. K1 : `record` dans un `array of` (le conteneur par défaut de l'Object Pascal moderne) ; K7 : `TDictionary` (Generics.Collections, livrée avec FPC 3.2, compatible Delphi), valeurs en `record`, sans accès en place (la bibliothèque n'en offre pas) ; K8 : `New` / `Dispose` d'un `record` pointé, la forme des manuels de Pascal (les nœuds de classe, `TObject.Create` / `Free`, sont une sensibilité) ; K9 : le tableau à deux dimensions de base du langage, contigu, de taille fixée à la compilation comme M (comme Ada, Zig, Odin et C3 ; `array of array of Double` est une sensibilité) ; K10 : la RTL n'a ni file bloquante ni variable de condition, d'où `TQueue` + section critique + événements (hors score).
* **BQN (ajouté le 6 novembre, `docs/BQN.md`)** : langage de tableaux ; CBQN, son implémentation de référence en performance, est construit par `make o3n`, la cible que son README recommande pour une construction locale sur x86-64, pour la cible de l'hôte des données de chaque clé (Cascade Lake pour celles de la machine 1, comme le C publié : `docs/BQN.md`, 2.1 ; la cible par défaut `make o3`, sans `-march=native`, est une sensibilité : `bench/bqn_o3`) ; le JIT est actif par défaut et rien ne désactive la vérification des indices. Le code naturel est écrit en primitives sur des tableaux entiers, comme le montrent la documentation et les exemples du langage : une boucle élément par élément y serait l'exception. K1 : BQN n'a ni type d'enregistrement ni flottant 32 bits ; la collection par défaut de valeurs homogènes est la matrice (une particule par rangée, f64), les espaces de noms à 16 champs nommés (`x⇐…`), plus proches d'un enregistrement, sont une sensibilité ; K4 : filtre `/` puis `+´` ; K5 : `+´ a × b` (la réduction ordonnée de la primitive ; `•math.Sum`, somme réassociée, sert au code optimisé) ; K6 : masques booléens et groupement `⊔` ; K7 : `⊐` pour classer les clés, `/⁼` pour compter, `⊔` pour regrouper les valeurs (`doc/group.md` : « the most direct application of Group », par Classify), comme le Q1 naturel ; corrigé le 6 novembre par la remarque sur BQN (`docs/BQN.md`, 5.3) : j'avais pris `•HashMap` ligne à ligne, à la lettre de `docs/SPEC.md` (« table de hachage de la bibliothèque standard »), contre ma propre règle pour BQN ; `⊐` est lui-même une table de hachage ; K8 : listes imbriquées de trois éléments, la façon de représenter un arbre des exemples du langage (les espaces de noms sont une sensibilité) ; K9 : matrice et décalages, bords recollés par `∾` et `∾˘` (la mise à jour structurelle `⌾` est 70 à 80 fois plus lente : `docs/BQN.md`, 2.4) ; K3 et les variantes `mt` s'exécutent en séquence, comme en Lua, et c'est signalé par `META` ; pas de K10.
* **PHP (ajouté le 7 novembre, `docs/PHP.md`)** : la CLI de PHP n'active par défaut ni OPcache ni son JIT (`opcache.enable_cli=0`, `opcache.jit=disable`) ; le manuel recommande le JIT tracing (« Recommended for most users », `reference/opcache/ini.xml` du dépôt php/doc-en). Le banc l'active, comme on passe `-O` à un compilateur, avec `php.ini-production` ; la CLI par défaut est une sensibilité (`bench/php_def`). K1 : le manuel présente les classes à propriétés typées et leur promotion par le constructeur (PHP 8.0) ; le tableau associatif à clés nommées, l'autre enregistrement courant de PHP, est une sensibilité ; la liste est un tableau de PHP. K7 : le tableau de PHP est la table de hachage du langage (« an ordered map », `language/types/array.xml`), avec un couple `[compte, somme]` par clé, comme le `dict` de listes de Python. K8 : objets d'une classe à propriétés promues, libérés par comptage de références. K9 : tableau de tableaux et double indice. PHP n'a pas de fils : K3 et les variantes `mt` emploient des processus (`pcntl_fork`, extension livrée avec php-src) créés avant la mesure, comme les Workers de JavaScript, et un segment partagé (`shmop`) ; K10 prend des Fibers (hors score).
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
* **Lua** : le langage standard n'a ni threads ni tableaux typés. Les noyaux
  multi-threads s'exécutent en séquence ou en coroutines, et c'est signalé par `META`.
* **Mojo** : Mojo 1.2 n'expose pas d'API publique de threads CPU (`parallelize` est dans
  MAX, hors `std`). Les variantes concurrentes utilisent `std.runtime._asyncrt`, privé
  mais livré avec `std`.
