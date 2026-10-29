# Compteurs du noyau et contrôle du bruit (29 octobre 2026)

*Plan écrit et poussé avant les mesures qu'il décrit. Je l'écris après avoir lu la description d'un banc de mesure
voisin du mien, que l'utilisateur m'a soumise, et après avoir vérifié sur cet hôte ce qui y était disponible. La
machine n'a pas de PMU matérielle, mais le noyau expose d'autres compteurs. Les analyses v1 à v3 ne s'en servaient
pas, sauf le temps volé par l'hyperviseur et les comptes de `wait4` (défauts de page, changements de contexte),
relevés mais jamais analysés.*

## 1. Ce qui est disponible sur cet hôte (vérifié le 29 octobre vers 17:10)

Hôte du modèle de la machine 3 : microVM Firecracker, Xeon Emerald Rapids, 4 vCPU, noyau 6.18.

| Instrument | Disponible | Vérification | Utilisé avant |
|---|---|---|---|
| PMU matérielle (cycles, instructions, caches) | non | absente de `/sys/bus/event_source/devices` | — |
| Compteurs logiciels (temps CPU, changements de contexte, migrations, défauts de page) | oui | programme de test | en partie, par `wait4` |
| Tracepoints d'appels système | oui, une fois tracefs monté | 1 000 `getppid` comptés 1 000 | non |
| uprobes | oui, par `uprobe_events` de tracefs | 1 000 `malloc` comptés 1 000 | non |
| Points d'arrêt matériels en écriture | oui | 1 000 écritures comptées 1 000 | non |
| PMU `msr` | `tsc` et `smi` seulement, sans APERF ni MPERF | — | non |
| PMU `power` (RAPL) | `energy-psys` lit 0 | — | non |
| PSI (pression CPU, mémoire, E/S) | oui | `/proc/pressure` | non |
| Temps volé par l'hyperviseur | oui | `/proc/stat` | oui : mesure refaite au-delà de 2 % |
| Épinglage, `SCHED_FIFO`, affinité des interruptions | oui (root) | `taskset`, `chrt` | non |
| `isolcpus` | non | ligne de commande du noyau fixée par Firecracker | — |
| eBPF | noyau compatible, ni bpftrace ni bcc | `CONFIG_BPF_SYSCALL=y` | non, et pas nécessaire pour compter |
| Binaire `perf` | absent | — | remplacé par `tools/pecount.c` |
| valgrind (cachegrind), gdb, strace | oui | — | cachegrind en v1 |

Deux pièges trouvés en construisant l'outil :
* une uprobe ouverte par la PMU `uprobe` de `perf_event_open` fait échouer les `fork` du processus compté (le noyau
  relit un pointeur utilisateur à chaque héritage) ; l'outil définit donc ses uprobes dans `uprobe_events` ;
* chaque passage dans une uprobe coûte une trappe. Avec une uprobe sur `malloc` et `free`, une seule exécution de
  K8 naturel en C (33,5 millions d'allocations par répétition) a dépassé 5 minutes.

## 2. Passe de comptage (descriptive)

* **Outil** : `tools/pecount.c`, construit dans `/opt/pecount`. Compteurs ouverts sur le processus avant son `exec`,
  hérités par tous ses threads.
* **Mesures** : K1 naturel, K3 `sw_padded`, K6 naturel Q1, K7 naturel, K8 naturel, K8 `tuned`, K9 naturel. Toutes
  les implémentations : les 21 classées, plus C (gcc), Fortran (flang), JavaScript (Bun) et LuaJIT. Haskell sur K7
  naturel est exclu (88 s par répétition).
* **Méthode des deux points**, celle de l'empreinte : R1 et R2 répétitions dans deux processus ; par répétition,
  (c(R2) − c(R1)) / (R2 − R1). Le démarrage et l'échauffement s'annulent. d = R2 − R1 = max(2, min(30, arrondi de
  1 s / t)), R1 = max(1, d / 2), où t est le temps par répétition de la campagne ; au-delà de 10 s par répétition,
  R1 = 1 et R2 = 2. Échauffement : 3 répétitions pour les JIT (Java, C#, JavaScript, Bun, Julia, LuaJIT), 1 sinon.
* **Compteurs** : appels système (total et 20 types : `futex`, `mmap`, `munmap`, `madvise`, `brk`, `mprotect`,
  `mremap`, `clone`, `clone3`, `sched_yield`, `nanosleep`, `clock_nanosleep`, `read`, `write`, `openat`, `ioctl`,
  `epoll_wait`, `membarrier`, `rt_sigprocmask`, `getrusage`), défauts de page, changements de contexte, migrations,
  temps CPU de tous les threads. Le temps par répétition vient du benchmark lui-même.
* **Sorties** : par mesure et par implémentation, les comptes par répétition, et le rapport entre le temps CPU de
  tous les threads et le temps écoulé (travail parallèle caché du runtime). Rien n'entre dans les scores.
* **Contrôle** : chaque exécution doit rendre la somme de contrôle attendue.

## 3. Comptage des allocations par uprobe (descriptif)

* uprobes sur `malloc`, `calloc`, `realloc` et `free` de la libc du système, deux points comme ci-dessus, sur K1
  naturel, K6 naturel Q1, K7 naturel, K8 `tuned` et K9 naturel. K8 naturel est exclu : sa spécification impose
  33,5 millions de nœuds par répétition, et la trappe de chaque appel rend le comptage impraticable.
* Plafond de 120 s par exécution ; au-delà, la cellule est déclarée « trop d'appels pour une uprobe ».
* **Portée** : ces comptes ne voient que l'allocateur de la libc. Les runtimes à ramasse-miettes allouent leurs
  objets dans leur propre tas, souvent par incrément de pointeur dans le code compilé, invisible pour une uprobe.
  Go est lié statiquement. Un compte nul veut donc dire « pas d'appel au `malloc` de la libc », pas « pas
  d'allocation ». Les défauts de page et les `mmap` de la passe 2 en donnent l'autre face.

## 4. Pilote de contrôle du bruit (test fixé d'avance)

* **Question** : l'épinglage sur un CPU, `SCHED_FIFO` et le déplacement des interruptions réduisent-ils l'écart entre
  processus d'un même binaire, que le second audit juge dominant (§ 4.2.2) ?
* **Mesures** : K5 `tuned` (C compilé par clang, Rust), K2 `tuned` à 8 Mio (C, Rust), K1 SoA (C). Code natif à un
  seul thread : l'épinglage d'un runtime à plusieurs threads sur un CPU changerait ce qu'on mesure.
* **Protocoles** :
  * A, le protocole de la campagne ;
  * B, processus épinglé sur le CPU 3 en `SCHED_FIFO` (priorité 50), interruptions déplacées vers les CPU 0 à 2,
    pilote sur les CPU 0 à 2 ;
  * C, comme B, avec en plus une variable d'environnement de longueur tirée entre 0 et 4 095 octets (Mytkowicz et
    al.).
  Les interruptions restent déplacées pendant tout le pilote, y compris pour A ; elles sont remises en place après.
* **Plan** : 12 processus par mesure et par protocole, 180 en tout, dans un ordre tiré au hasard (graine fixe) ;
  répétitions de `results/calib.json`, échauffement 1. Chaque processus est lancé par `pecount` (compteurs
  logiciels seulement) ; PSI et temps volé sont relevés avant et après.
* **Sorties** : écart-type du logarithme des médianes de processus, par mesure et par protocole ; rapports B/A et
  C/A, avec un intervalle bootstrap à 95 % (2 000 tirages des processus) ; moyenne géométrique des rapports sur les
  cinq mesures. Pour le protocole A, corrélation de rang entre la lenteur d'un processus (écart à la moyenne de sa
  mesure) et chacun des indicateurs : PSI CPU, temps volé, changements de contexte, migrations.
* **Lecture fixée d'avance** :
  * un rapport moyen sous 0,7 avec un intervalle entièrement sous 1 établit que les contrôles réduisent le bruit ;
    sinon, ce n'est pas établi ;
  * un indicateur avec |ρ| ≥ 0,5 pourrait servir à rejeter les processus bruités ; en dessous, non.

## 5. Coûts système (caractérisation)

`tools/hwprobe.c` reçoit deux modes : le coût d'un appel système minimal (`getppid`, chaîne chronométrée au TSC) et
celui d'un défaut de page mineur (premier accès à une page anonyme).

## 6. Ce qui n'est pas fait

* **Points d'arrêt matériels** : quatre adresses de 8 octets au plus, et une trappe par écriture. C'est un outil de
  vérification ponctuelle (par exemple, compter les écritures sur le compteur de K3), pas une mesure de débit. Le
  désassemblage a déjà établi le nombre d'écritures des boucles de K3.
* **Nouvelle campagne sous contrôles** : elle dépend du résultat du pilote.

## 7. Résultats (ajoutés après les mesures)

Détail : `results/report_instruments_v3.md`, données dans `results/raw_v3/instruments_*.jsonl` et
`results/raw_v3/noise_pilot.jsonl`. Mesures du 29 octobre, 17:26 à 19:56.

* **Pilote du bruit, selon la règle fixée d'avance : les contrôles ne réduisent pas le bruit.** Rapport moyen des
  écarts-types B / A : 1,00 [0,64–1,33] ; C / A : 1,03 [0,73–1,37]. Aucune des cinq mesures n'a un rapport
  significativement sous 1. Aucun indicateur ne prédit la lenteur d'un processus : ρ = −0,03 pour la PSI CPU, 0,05
  pour le temps volé, 0,12 pour les changements de contexte, 0,23 pour les migrations (n = 60) ; la PSI mémoire
  n'a pas varié. Avec 12 processus par case, une réduction de plus d'un tiers est exclue, une réduction modeste ne
  l'est pas. Le bruit entre processus vient vraisemblablement d'en dehors de l'invité, qui ne peut ni le
  contrôler ni le voir.
* **Passe de comptage** (348 exécutions, toutes valides) :
  * en régime établi, le code des langages compilés ne fait qu'un ou deux appels système par répétition (l'écriture
    du résultat) et aucun défaut de page sur K1, K6 et K8 ;
  * Odin, Lua et LuaJIT font un appel système à chaque lecture d'horloge : `clock_gettime` sans vDSO pour Odin
    (vérifié par strace : 32 770 appels pour une répétition de K8 naturel), le temps CPU pour Lua, que le vDSO ne
    sert pas ; soit deux appels par requête chronométrée de K8 ;
  * sur K7 naturel, Rust, Zig, Odin et Fortran (flang) rendent la mémoire de leur table au système à chaque
    répétition puis la retouchent : 10 000 à 29 000 défauts de page par répétition, environ 1 à 5 % du temps à
    1,5 µs le défaut ; C, C++, C3, Nim et Fortran (gfortran) la réutilisent (0 ou 1 défaut) ;
  * sur K3, les implémentations créent leurs 4 threads à chaque répétition (4 `clone3`), sauf Zig (pile en `mmap`),
    Fortran (pool OpenMP) et Go ; flang, C# et Bun font des centaines à des milliers de `sched_yield` par
    répétition (attente active) ; Python, 24 000 `futex` et 9 300 changements de contexte par répétition, avec un
    rapport CPU / temps écoulé de 1,09 sur 4 threads : le verrou global sérialise ;
  * les runtimes à ramasse-miettes ou à threads de fond font des centaines à des dizaines de milliers d'appels
    système par répétition : Haskell 60 000 `futex` sur K8 naturel, Node 26 000 `futex` et 24 000 `malloc` sur K1
    naturel, 2 700 `mprotect` sur K7, D 22 800 `futex` sur K8 `tuned`. Une partie de cette activité suit le temps
    plutôt que le nombre de répétitions : la méthode des deux points donne alors des valeurs négatives, signalées
    comme telles.
* **Allocations par uprobe** (248 exécutions, 28 au-delà de 120 s : surtout K7 naturel, Julia et Lua). Sur K8
  `tuned`, censé n'allouer rien en régime permanent : 0 ou 1 appel à l'allocateur de la libc par répétition en C,
  C++, Zig, Odin, C3, D, Nim, Ada, Mojo, OCaml et LuaJIT ; 69 en Fortran, 114 en C#, 158 en Java, 389 en Haskell,
  839 en Node (allocations natives du runtime). Sur K9 naturel, C++ et Rust allouent 4 100 blocs par répétition,
  mais hors chronomètre : la grille, un vecteur de lignes, est recréée avant chaque mesure (`bench/cpp/ms.cpp`).
* **Coût des instruments à trappe dans cette microVM** (`probes/trap_cost`, `results/probes/trap_cost.txt`) :
  une paire `malloc` + `free` passe de 10 ns à 59 µs avec une uprobe sur chacune, soit environ 30 µs par passage ;
  une écriture passe de 0,2 ns à 30 µs avec un point d'arrêt matériel. Les comptes sont exacts (200 001 et
  200 008), mais ces instruments ne conviennent qu'aux événements rares.
* **Limite de la méthode des deux points** : sans marqueurs dans le code, un compte par répétition inclut le
  travail hors chronomètre. Sur K9, la grille est réinitialisée hors chronomètre à chaque répétition : ses défauts
  de page (16 384 par répétition en Zig, Odin, C3, gfortran et flang, qui la remappent) ne pèsent pas sur le temps
  mesuré.
