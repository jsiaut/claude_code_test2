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
