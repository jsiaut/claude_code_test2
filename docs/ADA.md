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

Mesures du 30/10, 15:14 à 15:32 (machine 5) : 60 cellules × 7 processus, aucune somme de contrôle fausse, rien
d'autre ne tournait. Rapports, témoin et scénarios : `results/report_ada.md` et `results/ada_check.json`.

### 4.1 Ce que change la correction

Rapports appariés `ada_fix` / `ada` (moyenne géométrique de 7 processus chacun, IC à 95 %) :

* **Le stencil et Q6 à 4 threads, que le piège rendait scalaires** : K9 `tuned` 0,75 (0,67–0,84), qui fait désormais
  jeu égal avec C compilé par GCC sur le même hôte (27,3 contre 27,1 ms) ; K6 `mt` Q6 0,51 (0,47–0,55) ; K9 `mt` 0,85
  (0,79–0,91).
* **K2 en cache** : 0,83 (16 Kio) et 0,89 (256 Kio), 1,01 en mémoire. Inlinée, la boucle de chasse enchaînait
  `movsxd`, `sub` et le chargement ; hors ligne, `sub` et un chargement qui étend le signe : une instruction de moins
  par saut, ce qui compte quand le saut coûte 4 à 5 cycles (`results/ada_check/binaries.txt`).
* **Inchangés** : K6 `tuned` Q6 et Q1, K6 `mt` Q1 (`Q1_Tuned` était déjà hors ligne, `Q6_Tuned` déjà vectorisé
  dans la procédure de K6) ; K1 `aos` et `soa` 0,95 et 0,94 (intervalles qui contiennent 1) ; K5 `tuned` 1,09
  (0,93–1,28), dont les builtins vectoriels explicites ne dépendent pas du vectoriseur (forcé à 1, comme prévu).
* **Témoins, dont le source ne change pas** : la plupart restent entre 0,96 et 1,05, mais trois bougent nettement :
  K8 naturel 0,82, K8 `tuned` 0,79 et K9 naturel 1,25. Le binaire a changé autour d'eux (inlining dans les
  procédures appelantes, disposition) : des effets de cet ordre étaient déjà établis sur K3 (`FINDINGS`). Ils
  n'entrent pas dans le classement, puisque le plan n'y transfère que les 12 clés dont le code change ; ils rappellent
  qu'un rapport proche de 1 n'est pas distinguable de la disposition.
* **Ce qui reste** : avec la correction, Ada reste derrière C compilé par GCC sur K6 Q1 (1,78 en `tuned`, 2,32 en
  `mt`) et sur les versions à 4 threads (K9 `mt` 1,77, K6 `mt` Q6 1,49). Les deux créent leurs threads ou leurs
  tâches à chaque passe ; je n'ai pas mesuré ce que coûte la création d'une tâche GNAT.

### 4.2 Effet sur le classement (analyse globale rejouée, 20 000 variantes)

| Scénario | Score d'Ada | Plafond E | Contrôle C | Rang espéré | Rang dans 90 % des variantes |
|---|---|---|---|---|---|
| Publié avant la remarque | 68,0 | 73,9 (8e) | 76,2 | 8,45 (9e) | 3–12 |
| A-E : errata de la matrice seuls | 69,5 | 73,9 | 80,6 | 7,97 (9e) | 3–11 |
| **S1 : errata et correction (classement publié)** | **71,6** | **78,1 (7e)** | 80,6 | **6,78 (7e)** | 2–11 |
| S1-K5 : avec le transfert de K5 | 71,2 | 77,2 | 80,6 | 6,96 (7e) | 2–11 |
| S1-27 : les 27 rapports | 70,9 | 76,6 | 80,6 | 6,65 (7e) | 2–11 |

Depuis les corrections de Fortran, de Mojo, de Julia et de Chapel (`docs/FORTRAN.md`, `docs/MOJO.md`, `docs/JULIA.md`,
`docs/CHAPEL.md`), le classement publié donne à Ada un rang espéré de 7,09, sans changer son score, sa place (7e) ni son
rang plausible (2–11). Depuis la correction de D (`docs/DLANG.md`) et surtout la remesure des queues de latence de K8
pour tous les langages (31 octobre, `docs/RUST.md`), Ada a 71,7 points et n'est plus que 9e (rang espéré 7,94 ; rang
plausible 3–12) : sa propre queue change peu (D3 0,551 → 0,570), mais celles de Rust, de Zig et d'autres raccourcissent,
et C3, Rust et Nim la devancent désormais dans 64 à 66 % des variantes.

* **S1** : C, C++, Odin, C3, Zig, Nim, **Ada**, Rust, D, Chapel… Ada est 4e au score de référence (71,6, derrière C,
  C++ et Odin), mais 7e en rang espéré : il devance Rust dans 52 % des variantes, D dans 62 %, et Nim le devance dans
  54 %. Son code naturel (D1 = 14, parmi les plus bas des langages compilés : vérifications actives) le retient dans
  les variantes qui pèsent le code par défaut.
* **Plafond par noyau** : K9 passe de 53 à 67 % du meilleur temps, K6 de 51 à 60 % ; sur K1, Ada devient la
  référence (K1 `soa`, 7,2 ms).

### 4.3 Verdicts sur la remarque

* **(1) Exact**, et c'était une erreur de mon implémentation : les noyaux `tuned` annonçaient la suppression des
  vérifications et la vectorisation, et le binaire ne vectorisait pas le stencil ni Q6 à 4 threads. Corrigé.
* **(2) Exact.** Le stencil naturel du dépôt reste scalaire même hors ligne (bornes littérales sur un tableau non
  contraint) ; sur un type contraint, GNAT le vectorise vérifications actives. Le code naturel ne change pas
  (décision 3), le fait est publié.
* **(3) Exact, avec une limite** : RM 6.2(12) est exploitée par GNAT pour les tableaux contraints, pas pour les
  tableaux non contraints. E5 passe à 1, comme Fortran.
* **(4), (5), (6) Exacts.** C1 passe à 0,5 et 1 (comme `vector_size` en C) ; le README ne dit plus que les atomiques
  d'Ada sont seulement séquentiellement cohérentes, ni que le meilleur temps de K8 vient des pools de stockage.
* **(7) Exact.** K2 : la soustraction de la borne dynamique est dans la chaîne ; la correction d'inlining enlève déjà
  une instruction ; la borne fixe (extension `-gnatX`) n'est pas adoptée (décision 4). K4 : niveau de GCC.
* **B4 : exact**, et c'est la seule correction qui fait baisser Ada (1 → 0,5).
* **Effet chiffré** : la remarque estimait, en score ponctuel, 72,2 (4e) avec K9 corrigé et 73,8 (3e) avec K6.
  Mesuré : 71,6, 4e au score ; K6 ne gagne qu'à 4 threads sur Q6. Sur les 20 000 variantes, Ada passe de la 9e à la
  7e place, et son rang plausible reste large (2–11).

### 4.4 Ce qui change dans l'étude

* Le classement publié est désormais S1 : `analysis/analyze_v2.dataset_main` applique les rapports de
  `results/transfers.json` (12 clés d'Ada, K5 à 1) aux données principales ; la réplication sur la machine 3 garde
  les données d'Ada sans correction (rapports mesurés sur Cascade Lake seulement).
* Matrice : E5, C1, B4 d'Ada (v1, v2 et règle R) ; sondes alignées (0 divergence).
* README et FINDINGS : attributions corrigées (K8, atomiques, vérifications et vectorisation).
