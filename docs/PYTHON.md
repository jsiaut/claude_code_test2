# Remarque sur Python : des fils sérialisés dans K3, K6 et K9, deux cases de la grille, et ce que mesure le classement

L'auteur de l'étude m'a transmis le 5 novembre une remarque sur Python. Elle juge le dernier étage mérité pour CPython
seul (build par défaut, bibliothèque standard seule), mais trouve « 20e sur 21 avec 9,9 points » beaucoup moins
précis : le score tient presque entièrement au pilier jugé ; Python n'a jamais été relu ; ses noyaux à fils ne tournent
pas en parallèle ; deux cases de la grille sont incohérentes ; et le classement mesure CPython sans son écosystème, ce
que le README ne dit pas. Ce document vérifie chaque affirmation (section 2), fixe le plan avant toute mesure
(section 3), puis donne les résultats (section 4). Je n'ai consulté aucune page web : les faits viennent des deux
interpréteurs de l'étude (CPython 3.15.2, build par défaut et build sans GIL), de sondes et des données publiées.

## 1. La remarque

1. **Le fond** : CPython seul mérite le dernier étage. L'auteur a réécrit les noyaux d'après la spécification et les a
   exécutés sous CPython 3.15.2, avec et sans GIL (Xeon à 2,8 GHz, 2 vCPU). Il confirme : environ 200 fois plus lent
   (produit scalaire 4,7 s contre 4,75 ms ; Q6 1,5 à 1,8 s contre 15 à 18 ms) ; 43 et 42 ns par saut dépendant en L1
   et en L2 ; 744 octets par particule (673 avec `__slots__`, 64 en `array('f')`) ; le GIL sérialise les fils (débit
   de 0,85 à 1,05 fois celui d'un fil) ; une pause de 1,03 s dans K8 ; le JIT apporte 25 % au mieux.
2. **Le rang est fragile** : le score tient presque entièrement au pilier jugé. Plafond 0,5 (Lua 1,1) ; 8,5 des 9,9
   points viennent du contrôle ; Python ne devance Lua que dans 62 % des variantes, et les étages les regroupent.
3. **Python n'a jamais été relu** : ses versions optimisées sont plus lentes que les naturelles sur Q6 (1,95 contre
   1,76 s) et sur K9 (2,28 contre 1,98 s). Trois corrections : Q6 en colonnes (`bytes.translate`, entiers longs,
   `find`), 0,45 s contre 1,5 ; K8 avec `gc.freeze()`, pause de 1,03 s ramenée à 7 ms et temps − 30 % ; K3 sans GIL :
   l'`array` partagé crée une contention, une `memoryview` propre à chaque fil donne 1,96 fois le débit avec deux
   fils, et le cas tassé (`packed`) est 1,75 fois plus lent que l'espacé (`padded`). Le rang ne change pas : plafond
   d'environ 0,5 à environ 1.
4. **Le build sans GIL** n'est qu'une annexe, alors qu'il est officiellement pris en charge depuis la 3.14 (PEP 779).
   La spécification de K3 exige « de vrais threads matériels parallèles » ; Mojo a pu, lui, utiliser un module privé
   de sa bibliothèque standard.
5. **La grille** : B1 (Nim reçoit 1 avec ORC ; Python 0, alors que `gc.disable` et `gc.freeze` existent) ; F3
   (JavaScript et Lua ½ ; Python 0, malgré `& 0xFFFFFFFF` et `ctypes.c_uint32`) ; D1 à ½ se défend ; B2 : des arènes à
   la main valent ½ à C, Julia et Haskell, et le 0 de Python se discute. Effet estimé : 5 à 7 points de contrôle,
   environ 2 points de score (environ 12) ; toujours 20e.
6. **Ce que le classement mesure** : la règle de la bibliothèque standard mesure CPython ; NumPy, Numba, Polars et
   DuckDB sont la façon dont on se sert de Python. Le README discute cette règle pour Haskell et Mojo, pas pour Python.
   LuaJIT et Bun ont leur annexe, PyPy (3.11) non. Avec NumPy 2.5.4, le plafond serait de 5 à 6, toujours sous
   JavaScript. Formulation proposée : « CPython sans son écosystème est dernier ».
7. **Ce qui a changé au 5 novembre 2026** : la 3.15 est sortie le 9 octobre ; son JIT reste expérimental et désactivé
   par défaut (PEP 836) ; le build sans GIL coûte 1 à 8 % ; abi3t ; la phase III n'est pas décidée ; la 3.14.5 est
   revenue au ramasse-miettes générationnel, que la 3.15 garde ; des sous-interpréteurs partageant une `memoryview`
   donnent un vrai parallélisme. « Le verrou global sérialise les threads » est donc daté sans « dans le build par
   défaut ».

## 2. Vérifications (faites avant le plan)

**Machine 22.** La VM a redémarré le 5 novembre à 7 h 59 sur un hôte Cascade Lake du même modèle que celui des
données principales (modèle 85, 4 vCPU, un fil par cœur ; 3,05 à 3,18 GHz effectifs, latence 25 ns à 4 Mio et 201 ns
à 1 Gio, DRAM 10,7 à 12,4 Go/s : `results/hw/machine22/`). Interpréteurs : CPython 3.15.2, `python3.15` (build par
défaut, avec GIL) et `python3.15t` (build sans GIL), ceux de l'étude ; les 24 fichiers d'entrée correspondent à
`env/msdata.sha256`. Sondes : `tools/python_check/probes/`, sorties dans `results/python_check/`. Temps ci-dessous :
un processus.

* **Le fond (1)** : **exact**, aux ordres de grandeur près. Données publiées : K5 tuned 3,10 s contre 3,94 ms pour C
  (787 fois ; c'est le « produit scalaire » de la remarque) ; Q6 tuned 1,90 s contre 21,4 ms (89 fois) ; un saut
  dépendant coûte 48,8 et 46,7 ns à 16 et 256 Kio (43 et 42 selon la remarque) ; 750 octets par particule (744) ;
  pire pause de K8 naturel 0,76 s (1,03 s). Sonde d'empreinte (`footprint.py`, tracemalloc, 200 000 particules) :
  608 octets par particule pour la classe ordinaire, 552 avec `__slots__` (− 9 % ; la remarque : − 10 %), 64,7 en
  `array('f')` ; la mesure publiée, en deux points après ramasse-miettes, compte aussi les blocs de l'allocateur. La
  classe ordinaire est le code naturel (« comme dans le tutoriel officiel ») : rien à changer. Les fils : K6 `mt`
  2,36 s contre 1,90 s en tuned (Q1 : 9,03 contre 7,94 s), K9 `mt` 1,89 contre 1,80 s (machine 16) ; ils ne gagnent
  rien. Le JIT : `sys._jit.is_available()` vaut `False` dans les deux binaires de l'étude, configurés sans option JIT ;
  les 25 % ne se vérifient pas ici, et l'étude mesure le build par défaut.
* **(2) Le rang** : **exact.** Décomposition (classement publié, `results/js_check.json`, J-E) : 9,94 = 0,35 × 24,4 +
  0,40 × 0,46 + 0,25 × 4,9 (8,54 + 0,18 + 1,22) ; plafond de Lua 1,08. Python devance Lua dans 62,45 % des variantes,
  et l'étage le plus bas de la v3 les réunit. Le tableau du README donne déjà ces 62 %.
* **(3) Versions optimisées plus lentes** : **exact, sans effet sur le score.** Q6 tuned 1,90 s contre 1,83 s en
  naturel ; K9 tuned 1,80 contre 1,56 s (machine 16 ; 2,28 et 1,98 s dans les données de Cascade Lake). Le plafond
  prend, pour chaque mesure, le meilleur du naturel et de l'optimisé (`E_MEASURES` de `analysis/analyze.py`), et le
  code par défaut ne lit que le naturel : un optimisé plus lent ne coûte rien.
* **(3) Q6 en colonnes** : **exact dans le sens annoncé, un peu moins fort.** Sonde (`q6_forms.py`, trois
  répétitions, même somme) : tuned 1,56 à 1,76 s ; masques 0/1 par `bytes.translate`, combinés en entiers longs, lignes
  retenues par `itertools.compress` et `math.sumprod`, 0,86 à 1,15 s ; mêmes masques, lignes retenues trouvées par
  `bytes.find`, 0,58 à 0,62 s (la remarque : 0,45 contre 1,5 s) ; le masque seul prend 0,70 s ; 300 971 lignes
  retenues sur 16 777 216 (1,79 %). Aucune autre implémentation ne calcule ses masques par des tables de traduction
  d'octets : c'est une forme nouvelle, propre à CPython, **sensibilité** (Q6 tuned et `mt`), comme les formes de Q6 de
  JavaScript. Validation : 0,53 à 0,60 s, et 0,19 s dans quatre sous-interpréteurs (`validate.txt`).
* **(3) K8 et `gc.freeze()`** : **exact.** Validation (machine 22) : K8 naturel 18,5 s, pire pause 763 ms ; avec
  `gc.freeze()` après la construction de l'arbre longue durée, 14,0 s (− 25 %) et 7,4 ms (16,9 s et 8,8 ms à une
  seconde validation ; `validate.txt`). Le collecteur de cycles parcourt l'arbre longue durée (2^21 − 1 nœuds) à
  chaque collecte de la plus vieille génération ; `gc.freeze()` le range dans une génération permanente. C'est un
  réglage du ramasse-miettes, que le code naturel des autres langages ne fait pas (« réglages des runtimes par
  défaut ») : **sensibilité**, sur le temps et les latences, comme le site d'allocation distinct de JavaScript.
* **(3), (4) K3, K6 `mt` et K9 `mt`** : **exact, et c'est une erreur de mon implémentation.** La spécification de K3
  exige « T = 4 threads (vrais threads matériels parallèles) », et les variantes `mt` de K6 et de K9 annoncent un
  calcul parallèle. Le code publié lance des `threading.Thread` du build par défaut, dont le GIL ne laisse tourner
  qu'un fil à la fois. Or CPython 3.15 livre dans sa bibliothèque standard des sous-interpréteurs
  (`concurrent.interpreters`, depuis la 3.14), chacun avec son propre GIL ; un tampon (`array`) se partage entre eux
  sans copie par `memoryview`. Mojo (module privé de sa `std`) et JavaScript (Workers et `SharedArrayBuffer`, D1 ½
  comme Python) obtiennent de vrais fils parallèles par ce que livre leur chaîne ; Lua, qui n'a pas de fils, exécute
  K3 en séquence. Sonde K3 (`k3_probe.py` et `k3_single.py`, `k3_probe.txt` : quatre fils de 2^22 incréments chacun ;
  un fil seul, dans une fonction, 0,34 à 0,49 s dans les deux builds) :

  | Build | `array` partagé (espacé / tassé) | `memoryview` propre au fil | Sous-interpréteurs |
  |---|---|---|---|
  | par défaut (GIL) | 1,88 / 1,65 s | 1,60 / 1,78 s | 1,07 / 2,29 s |
  | sans GIL | 6,74 / 9,44 s | 0,71 / 1,75 s | 2,06 / 3,59 s |

  Dans le build par défaut, seuls les sous-interpréteurs travaillent en parallèle, et le faux partage n'apparaît
  qu'avec eux (tassé 2,1 fois plus lent qu'espacé). Validation des copies (machine 22, 2^25 incréments par fil, mêmes
  sommes) : K3 `sw_padded` 13,5 → 4,2 s, `rmw_padded` 25,2 → 7,9 s ; K6 `mt` Q6 1,88 → 0,65 s, Q1 6,59 → 2,23 s ; K9
  `mt` 2,02 → 1,09 s.
* **(3) Le build sans GIL et l'`array` partagé** : **exact.** Le verrou par objet de l'`array` sérialise les fils
  (6,7 et 9,4 s, 3,6 et 5,7 fois le build par défaut) ; une `memoryview` propre à chaque fil les libère (0,71 s), et
  le cas tassé y est 2,5 fois plus lent que l'espacé (la remarque, avec deux fils : 1,75). L'annexe `python_ft`
  publiée (K3 de 61,8 à 73,4 s, contre 17,5 à 33,9 s avec le GIL) mesurait cette contention : erreur de mon
  implémentation dans une annexe, corrigée dans la sensibilité S-FT.
* **(4) Le build sans GIL comme build classé** : **la règle tient.** L'étude classe le build que lance `python3`, le
  build par défaut ; `python3.15t` est livré à côté (`Py_GIL_DISABLED` = 1), et le statut de la PEP 779 ne se vérifie
  pas ici. Son surcoût de « 1 à 8 % » est **inexact pour ces noyaux** : à source égale sur le même hôte
  (`ft_overhead.txt`), Q6 naturel 1,32 → 1,66 à 1,83 s, Q6 tuned 1,40 à 1,52 → 1,64 à 1,95 s, K9 naturel 1,79 à 1,83
  → 2,52 à 3,24 s, K9 tuned 2,12 à 2,38 → 2,95 à 3,17 s, K5 tuned 4,34 → 3,69 s ; dans l'annexe publiée, les noyaux
  séquentiels de K6 et K9 coûtent 1,25 à 1,98 fois le build par défaut. K10, deux fils qui échangent par une
  `queue.Queue`, passe de 5,6 à 29,1 s. **Sensibilité** S-FT : pour K3, K6 `mt` et K9 `mt`, le meilleur des deux
  builds ; c'est une borne haute, un programme ne choisissant qu'un build.
* **(5) B1** : **exact, erratum.** Sonde (`facts.py`, `facts.txt`, dans les deux builds) : `gc.disable()` arrête le
  collecteur de cycles (`gc.isenabled()` = `False`), `gc.freeze()` en retire les objets vivants (7 366 ici) ; le
  comptage de références libère seul tout ce qui n'est pas cyclique. C'est la situation de Nim avec ORC (comptage de
  références et collecteur de cycles), noté 1 : « pas de GC traçant imposé ». Lua (0 : son seul collecteur est traçant,
  et arrêté, il ne libère plus rien) et D (½ : le tas est ramassé par défaut, et `@nogc` interdit `new`) restent des
  cas différents. **B1 = 1.**
* **(5) F3** : **exact, erratum.** Sonde : `c_uint32(2**32 + 5)` vaut 5, `c_int32(2**31)` −2 147 483 648,
  `c_uint8(300)` 44 ; un tableau `c_uint32` enveloppe à l'affectation (2^32 + 7 → 7, −1 → 4 294 967 295) ;
  `array('I')` refuse les valeurs hors bornes (`OverflowError`). Les objets `ctypes` n'ont pas d'arithmétique : le
  calcul reste sur des entiers à précision arbitraire, rendus modulaires par masque (`& 0xFFFFFFFF`), comme `|0` et
  `>>>0` en JavaScript. **F3 = ½**, comme JavaScript, Lua, OCaml et Java.
* **(5) D1** : **½, inchangé**, la remarque le juge défendable ; la note nomme désormais les sous-interpréteurs et le
  build sans GIL livré à part. D1 = 1 (build sans GIL tenu pour standard) en **sensibilité** (S-cases).
* **(5) B2** : **discutable, gardé à 0, sensibilité.** Le ½ de C, Fortran, Julia, Haskell, Nim et Mojo repose sur une
  allocation et une libération explicites de mémoire brute, où l'arène range des enregistrements par valeur
  (`malloc`/`free`, `Libc.malloc`, `mallocBytes` et `Foreign.Marshal.Pool`, `alloc`/`free`). L'arène du K8 optimisé de
  Python est faite d'indices dans des listes préallouées, comme celles d'OCaml, de JavaScript et de Lua, notés 0. On
  pourrait ranger des enregistrements `ctypes` dans un `mmap` anonyme libéré par `close()`, mais JavaScript
  (`ArrayBuffer`, `DataView`) et OCaml (`Bigarray`) le pourraient aussi, et sont notés 0 : changer la case changerait
  la règle pour trois langages. B2 = ½ en sensibilité (S-cases).
* **(5) Effet** : essai de l'analyse sur les données de la validation (300 variantes) : environ 11,8 points avec les
  corrections et les errata (contrôle 24,4 → 29,7 ; plafond 0,5 → 0,6), environ 13,3 avec toutes les formes et les
  cases discutables ; 20e partout. La remarque estimait environ 12.
* **(6) Ce que le classement mesure** : **exact.** Le README discute la règle de la bibliothèque standard pour Haskell
  et pour Mojo (« Limites »), pas pour Python, dont l'outillage habituel (NumPy, Numba, Polars, DuckDB) est tiers et
  absent de cette machine (`facts.txt`) : son effet ne se mesure pas ici, et le plafond de 5 à 6 avec NumPy ne se
  vérifie pas. LuaJIT et Bun ont leur annexe, PyPy non (il n'est pas installé). Le README le dira : le classement
  mesure CPython sans son écosystème.
* **(7) Évolutions** : les deux binaires de l'étude sont des 3.15.2, sans JIT compilé ; le ramasse-miettes y est
  générationnel (`gc.get_threshold()` = (2000, 10, 10), trois générations dans `gc.get_stats()`), ce qui concorde avec
  la remarque ; les sous-interpréteurs sont vérifiés plus haut. Dates, PEP 836, abi3t et phase III : invérifiables
  ici, sans effet. **« Le verrou global sérialise les threads » est à préciser** : dans le build par défaut, et sauf
  par sous-interpréteurs.
* **Relectures** : **exact.** Le README dit « Dix-neuf langages ont été relus après coup » ; Python ne l'avait pas
  été.

## 3. Plan (poussé avant les mesures)

### 3.1 Règle commune et application

`docs/FORTRAN.md`, 3.1. Erreurs : K3 (quatre variantes), K6 `mt` (Q6 et Q1) et K9 `mt` tournent sur des fils que le
GIL sérialise, là où la spécification exige de vrais fils parallèles et où la bibliothèque standard en donne
(sous-interpréteurs) ; dans l'annexe `python_ft`, K3 partage un `array` dont le verrou d'objet sérialise les fils.
Errata : B1 = 1, F3 = ½. Texte : README (paragraphe de Python, point 6 des résultats solides, limites). Sensibilités :
Q6 en colonnes (tuned et `mt`), K8 naturel avec `gc.freeze()`, build sans GIL (S-FT), cases B2 = ½ et D1 = 1.

### 3.2 Ce qui entre dans le classement publié

* **P-E** : K3 (quatre variantes), K6 `mt` (Q6, Q1) et K9 `mt` × r(`python_fix` / `python_ref`), **par transfert**
  (`docs/HASKELL.md`, 3.2 ; la machine 22 est du même modèle que l'hôte des données principales). K9 `mt` va dans
  `ratios_k9h`, appliqué après les données de K9 de la machine 16 (Emerald Rapids : transfert entre modèles, comme pour
  les remarques mesurées sur Emerald Rapids et reportées sur Cascade Lake). Le pont par le C reste calculé en
  information. Les autres clés de Python ne changent pas.
* **Matrice** : B1 = 1, F3 = ½ (`analysis/capabilities.py`) ; note de D1 complétée.
* **Réplication (machine 3)** : les mêmes clés × les mêmes rapports (transfert de Cascade Lake vers Emerald Rapids),
  par `results/python_check.json` (« replication_ratios »), lu par `m3_ratios`.
* **Annexe `python_ft`** : ses temps publiés restent ceux de la campagne ; sa correction n'entre que dans S-FT.
* **Texte** : README (tableau ; paragraphe de Python : GIL du build par défaut, sous-interpréteurs, build sans GIL,
  poids du pilier jugé, 62 % ; point 6 ; errata ; limites : règle de la bibliothèque standard pour Python, PyPy,
  relectures), CAPABILITIES (régénéré).

### 3.3 Copies (`tools/python_check/make_copies.py`)

* `python_ref` : copie exacte de `bench/python_k9h` (le code publié, harnais commun de K9).
* `python_fix` : K3, K6 `mt` et K9 `mt` sur quatre sous-interpréteurs créés avant la mesure (comme les Workers de
  JavaScript), données partagées par `memoryview` ; K3 `rmw` garde un `threading.Lock` par compteur, propre à son
  sous-interpréteur ; K9 `mt` passe à deux grilles plates `array('d')`, mêmes opérations dans le même ordre.
* `python_exp` : `python_fix` et des variantes nouvelles : K6 `tuned_c` et `mt_c` (Q6 en colonnes, lignes retenues
  par `bytes.find`), K8 `natural_f` (`gc.freeze()` après l'arbre longue durée).
* `python_ftfix` : le code publié exécuté par `python3.15t` (l'annexe `python_ft`), K3 par une `memoryview` propre à
  chaque fil.
* Validation (`tools/python_check/validate.py`) : 27 cellules, sommes de contrôle toutes justes ; les variantes
  `tuned_c` (forme `find`) et `mt_c`, ajoutées ensuite, aussi.

### 3.4 Mesures (`tools/measure_python.py`, machine 22)

33 cellules en 7 passes (231 processus) ; dans chaque passe, toutes les cellules dans un ordre tiré au hasard (graine
20262005) : `python_ref` sur K3 (quatre variantes), K6 `mt` (Q6, Q1), K9 `mt`, Q6 tuned, Q6 naturel et K8 naturel ;
`python_fix` sur les mêmes clés parallèles et Q6 naturel (code inchangé : contrôle) ; `python_exp` sur ses trois
variantes ; `python_ftfix` sur les clés parallèles ; `c` (binaire de la campagne) sur K3 `sw_padded` et `rmw_padded`,
K6 `mt` et K9 `mt` (pont, information). Répétitions de `results/calib.json` (variante d'origine pour les variantes
nouvelles, `python_ft` pour `python_ftfix`) ; un échauffement ; règle de vol du pilote. Environ 90 minutes ; rien
d'autre ne tourne. Sortie : `results/raw_python/`.

### 3.5 Scénarios (`analysis/python_check.py`, analyse globale de la v3 rejouée, mêmes tirages)

| Scénario | Contenu |
|---|---|
| Avant | classement publié d'avant (B1 = 0, F3 = 0) ; doit reproduire `results/js_check.json` (J-E) à l'identique |
| P-code | K3, K6 `mt`, K9 `mt` × r(`python_fix` / `python_ref`), grille d'avant |
| P-M | errata B1, F3 seuls |
| **P-E (publié)** | les deux |
| P-E-P | P-E, clés reportées par le pont par le C (règle de `analysis/transfer_check.py`, règle de sens ; information) |
| S-Q6c | P-E ; Q6 tuned × r(`tuned_c` / `python_ref` tuned), Q6 `mt` × r(`mt_c` / `python_fix` `mt`) |
| S-K8f | P-E ; K8 naturel × r(`natural_f` / `python_ref`), ses latences × les rapports des latences |
| S-FT | P-E ; K3, K6 `mt`, K9 `mt` : le meilleur de `python_fix` et de `python_ftfix` (borne haute) |
| S-mesures | toutes les formes ; chaque clé prend la meilleure des siennes |
| S-cases | P-E ; B2 = ½, D1 = 1 |
| S-tout | S-mesures et S-cases |

Rapports : moyenne géométrique des médianes de processus, intervalle par bootstrap ; latences : médiane de toutes les
répétitions, colonne par colonne ; sensibilités en min(1, r) par rapport à P-E. Information : Q6 naturel sous
`python_fix` / `python_ref` (contrôle). Sorties : `results/python_check.json`, `results/report_python.md`,
`results/transfers.json` (Python) ; puis régénération des sorties publiées (la réplication comprise) et de l'état
actuel.

### 3.6 Ce que je ne fais pas

* Ni NumPy, ni Numba, ni Polars, ni DuckDB (tiers et absents : la règle de la bibliothèque standard, que le README
  discutera) ; ni PyPy, ni build avec JIT (absents de la machine ; pas de consultation du web).
* Pas de `__slots__` dans K1 (la classe ordinaire est le code naturel) ; rien sur Q6 et K9 tuned plus lents que leurs
  naturels (sans effet) ; pas de K10 (hors score), bien que ses deux fils passent aussi par le GIL ; pas de remesure
  de l'empreinte.
* Pas de changement de build classé : le build sans GIL reste une annexe et une sensibilité.
