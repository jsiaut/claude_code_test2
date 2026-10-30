# Remarque sur Ada : un piège de GNAT, trois cases de la grille et trois attributions

Remarque transmise par l'utilisateur le 30 octobre 2026. Ce document la vérifie : faits établis avant toute mesure
nouvelle (section 2), plan des mesures et de l'analyse, poussé avant les mesures (section 3), résultats (section 4).
L'auteur de la remarque n'a pas pu exécuter GNAT 16.2 ni le code du dépôt : il a écrit ses propres reproductions,
compilées avec GNAT 14.2. Je n'ai pas ses fichiers (`repro_ada.zip`) ; toutes les vérifications ci-dessous sont les
miennes, sur GNAT 16.2.

## 1. Ce que dit la remarque

* (1) **Piège de GNAT.** Sans `-gnatp`, GNAT compile avec `-fnon-call-exceptions` (`gcc-interface/misc.cc`). Une
  fois un noyau inliné dans son appelant, chaque lecture de tableau peut lever une exception et le vectoriseur
  renonce ; un `pragma Suppress` local n'y change rien. Avec `-gnatp`, `-fno-non-call-exceptions` ou sans inlining,
  le stencil `tuned` va aussi vite que C ; une requête de type Q6 devient 2,1 fois plus rapide.
* (2) **« Les vérifications empêchent la vectorisation » dépend du style.** Dans un paquetage séparé, avec
  `'First`/`'Last` ou un type contraint, le stencil naturel vectorise, vérifications actives ; seule la forme du
  dépôt (bornes littérales sur un tableau non contraint) reste lente.
* (3) **E5 = 0 est faux** : RM 6.2(12) fait de l'accès croisé entre paramètres une erreur bornée, et GNAT l'exploite
  (`decl.cc`) ; s'y ajoutent `pragma Loop_Optimize (Ivdep)` et l'aliasing strict par type. Fortran reçoit 1.
* (4) **C1 = 0 est incohérent** avec la règle v2 : `pragma Machine_Attribute (T, "vector_type")` donne des types
  vectoriels GCC, comme `vector_size` en C, qui reçoit 1.
* (5) **« Atomiques seulement séquentiellement cohérentes » est faux pour GNAT** : `pragma
  Disable_Atomic_Synchronization` remplace `xchg` par `mov` ; la matrice v2 donne déjà D2 = 1 ; K3 ne montre pas de
  surcoût.
* (6) **« Meilleure arène grâce aux pools de stockage » est une mauvaise attribution** : les 108 ms de K8 viennent
  d'une arène de nœuds indexés (le pool de stockage prend 187 ms), et du compilateur GCC.
* (7) **Écarts mineurs** : K2, la borne inférieure dynamique ajoute une soustraction dans la chaîne de dépendances
  (l'extension GNAT de borne fixe la supprime) ; K4, le retard vient de GCC.
* En sens inverse : **B4 = 1 est généreux**, la pile secondaire de GNAT peut allouer sur le tas.
* Effet estimé par la remarque (ponctuel) : 68,0 (9e), puis 70,2 (7e) avec E5 et C1, 72,2 (4e) avec K9 corrigé,
  73,8 (3e) avec K6 corrigé (hypothèse).

## 2. Vérifications faites avant ce plan (machine 5)

Sources de GCC 16.2.0 (archive de ftp.gnu.org, signature vérifiée avec le trousseau GNU) et sondes compilées par
GNAT 16.2 : `tools/ada_check/`, `results/ada_check/probes.txt` et `results/ada_check/binaries.txt`.

* **(1) est exact.** `misc.cc`, lignes 423 à 434 : sans `-gnatp`, `flag_non_call_exceptions = 1` (et
  `flag_aggressive_loop_optimizations = 0`). Dans le binaire de la campagne (recompilé sur la machine 5, identique
  octet pour octet), `K9_Rows` est inliné dans le programme principal et dans la tâche de K9 `mt`, et `Q6_Tuned`
  dans la tâche de K6 `mt` : aucune instruction vectorielle dans ces trois corps, malgré `pragma Suppress
  (All_Checks)` et `pragma Loop_Optimize (Vector)`. Marqués `with No_Inline` (rien d'autre ne change), les sept
  noyaux `tuned` qui portent `pragma Suppress` sont compilés hors ligne et vectorisés (`K9_Rows`, `Q6_Tuned`,
  `Q1_Tuned`, `K1_Soa`…). Premières mesures isolées, un processus chacune, donc indicatives : K9 `mt` 23 → 17 ms,
  K6 `mt` Q6 19 → 9,6 ms, K6 `tuned` Q1 63 → 41 ms.
* **(2) est exact, et se décompose.** Hors ligne, vérifications actives, le stencil naturel du dépôt (bornes
  littérales sur `Grid` non contraint) reste scalaire : les vérifications restent, et GCC n'a pas de type vectoriel
  pour un accès à pas dynamique (« no vectype for stmt »). Un stencil sur un type contraint, dans un paquetage, se
  vectorise vérifications actives, sans test de recouvrement (sonde `e5c`). Dans le programme du dépôt, d'un seul
  fichier, le piège de (1) bloquerait de toute façon le naturel inliné.
* **(3) est exact, avec une limite.** GNAT marque `DECL_RESTRICTED_ALIASING_P` les paramètres passés par référence
  d'un type qui n'est pas « par référence » (`decl.cc`, l. 5855-5859, « We take advantage of 6.2(12) »), et à -O3
  déclare `ivdep` une boucle qui n'écrit que dans de tels paramètres (`trans.cc`, l. 3392-3396). Sonde : sur un type
  tableau contraint, la boucle est vectorisée sans test de recouvrement ; la même sur deux valeurs d'accès en exige
  un. Sur un tableau non contraint (pointeur « gras »), GNAT ne l'exploite pas : test de recouvrement aussi.
* **(4) est exact.** À -O3, `function Add (A, B : V8) return V8` écrite comme une boucle Ada, sur un type déclaré
  `vector_type`, se compile en un seul `vaddps ymm0,ymm0,ymm1` ; la même forme avec `*` et `+` en un seul
  `vfmadd132ps`, vérifications actives.
* **(5) est exact.** Un objet `Atomic` est écrit par `xchg` ; avec `pragma Disable_Atomic_Synchronization`, par un
  simple `mov`. K3 `sw_padded` : 61,2 ms contre 59,7 en C (données principales) ; `rmw_padded` : 269 contre 227.
* **(6) est exact.** K8 `tuned` (108 ms) est l'arène de nœuds indexés ; `tuned_alloc` (pool de stockage) prend
  187 ms. L'étude avait déjà établi que GCC compile cette arène 2,2 à 2,7 fois plus vite que clang (`FINDINGS`).
* **(7) est exact.** La boucle de chasse de K2 fait `sub rax,rcx` (borne inférieure dynamique) puis le chargement, à
  chaque saut. La borne fixe est une extension « curated » de GNAT (`-gnatX`), documentée. K4 : Ada 7,5 et 5,4 ms,
  C par gcc 6,1 et 5,2, C++ par g++ 6,5 et 6,8 (données principales).
* **B4 : la remarque a raison.** Une fonction qui rend un tableau non contraint de 4 Mo, sans `new`, appelle
  `__gnat_malloc (4 000 048)` depuis `System.Secondary_Stack.Allocate_Dynamic` (`s-secsta.adb:189`, tracé par gdb).

## 3. Plan (poussé avant les mesures)

### 3.1 Errata de la matrice (vérifiés ci-dessus)

| Case | Avant (v1 / v2) | Après (v1 / v2) | Règle du « standard » (R) |
|---|---|---|---|
| E5 non-aliasing | 0 / 0 | 1 / 1 : RM 6.2(12), exploitée par GNAT (tableaux contraints) ; `pragma Loop_Optimize (Ivdep)` | 1 (règle de la norme) |
| C1 types vectoriels portables | 0 / 0 | 0,5 / 1 : `Machine_Attribute "vector_type"`, extension livrée, comme `vector_size` en C | 0,25 (propre à GNAT) |
| B4 pas d'allocation cachée | 1 / 1 | 0,5 / 0,5 : la pile secondaire alloue sur le tas au-delà de son morceau statique | 0,5 |

### 3.2 Correction de l'implémentation

* `ada` : binaire de la campagne. `ada_fix` (`bench/ada_fix/ms.adb`) : les sept sous-programmes `tuned` qui portent
  `pragma Suppress (All_Checks)` (`K1_Aos`, `K1_Soa`, `K2_Chase`, `K5_Tuned`, `Q6_Tuned`, `Q1_Tuned`, `K9_Rows`)
  sont marqués `with No_Inline`. Même fichier, mêmes options, même algorithme ; sommes de contrôle valides.
* Mesures (`tools/measure_ada.py`) : `ada` et `ada_fix` sur les 27 clés du score ; C compilé par GCC
  (`bench/c_gcc`) sur K6 `tuned` et `mt` (Q6, Q1) et K9 `tuned` et `mt`, en témoin. 7 processus par cellule, en 7
  passes, ordre tiré au hasard dans chaque passe (graine 20261090 + passe), répétitions de `results/calib.json`,
  échauffement de 2. Sortie : `results/raw_ada/`.

### 3.3 Analyse (`analysis/ada_check.py`)

Rapports appariés et transfert aux processus d'Ada des données principales, comme pour Zig ; analyse globale de la v3
rejouée (20 000 variantes, même graine).

* **A-E** : le classement publié, avec les trois errata de la matrice.
* **S1** : A-E, plus les rapports `ada_fix`/`ada` sur les 12 clés dont le code change (K1 `aos` et `soa`, K2 ×3, K5
  `tuned`, K6 `tuned` et `mt` ×2, K9 `tuned` et `mt`), **K5 forcé à 1** (ses données principales viennent de la
  machine 3).
* S1-K5 : S1 avec le transfert de K5. S1-27 : les rapports des 27 clés (les 15 clés naturelles ou inchangées servent
  de témoin : leur source ne change pas).
* Témoin : rapport Ada/C par GCC sur les 6 clés de `c_gcc`, ici et dans les données principales.

### 3.4 Décisions fixées d'avance

1. **Les trois errata entrent dans le classement publié**, comme ceux du juge à l'aveugle et de F4 pour Zig. La règle
   R reçoit C1 = 0,25 pour Ada.
2. **La correction `No_Inline` entre aussi dans le classement publié (S1).** C'est une erreur de mon implémentation :
   le code `tuned` disait supprimer les vérifications et vectoriser, et ne le faisait pas. La correction ne change ni
   l'algorithme ni les options, et la spécification permet en `tuned` les pragmas et aspects documentés. Ce n'est pas
   le cas de Zig 0.18, une version non publiée que le protocole exclut.
3. **Le code naturel ne change pas.** La règle du naturel est commune aux 21 langages (aucune annotation de
   performance) ; la dépendance au style est publiée comme un fait.
4. **La borne inférieure fixe de K2 n'est pas adoptée** : c'est une optimisation nouvelle (par une extension), pas la
   correction d'une erreur ; son effet est publié comme un fait.
5. **Le README est corrigé** : K8 (arène et GCC, pas les pools), atomiques (`Disable_Atomic_Synchronization`),
   vérifications et vectorisation (style du naturel, piège du `tuned`).

## 4. Résultats

*À venir.*
