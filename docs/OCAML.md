# Remarque sur OCaml : un Q6 « optimisé » qui branche encore, un `pow` dans K1, une horloge hors contrat

L'auteur de l'étude m'a transmis le 3 novembre une remarque sur OCaml. Elle juge la 18e place justifiée et stable,
mais le score (24,0) un peu bas, le code du banc en dessous de ce que permet OCaml 5.5.2, deux cases de la grille
discutables et trois passages du README inexacts. Ce document vérifie chaque affirmation (section 2), fixe le plan
avant toute mesure (section 3), puis donne les résultats (section 4). Je n'ai consulté aucune page web : les faits
viennent de la chaîne installée (OCaml 5.5.2 avec flambda), de ses sources de bibliothèque, du code machine, de sondes
et des données publiées.

## 1. La remarque

1. **Le rang tient** : pas de types valeur (144 octets par particule, parcours permuté environ 7 fois plus lent) ;
   pas de flottant 32 bits de calcul (le format n'existe que pour stocker, dans un `Bigarray`) ; ni SIMD ni
   vectorisation, et le générateur x86-64 n'émet ni `cmov`, ni préchargement, ni `popcnt` (les fonctions de comptage
   de bits de la 5.5 sont écrites en OCaml) ; atomiques seulement séquentiellement cohérentes, `fetch_and_add`,
   `exchange` et `compare_and_set` étant des appels C, seule la lecture compilée en ligne (K3 traité conformément à la
   spécification) ; entiers étiquetés ; domaines coûteux à créer. Haskell a 17,3 points d'avance (11,1 du plafond, 5,3
   du contrôle, 0,8 du code par défaut), JavaScript 10 de retard.
2. **Le code du banc** (OCaml est le seul langage compilé non relu) : (a) Q6 tuned : `Bool.to_int (a && b)` reste un
   branchement (274,9 ms, plus lent que le naturel, 200,6, et deux fois JavaScript) ; un masque de bits de signe
   donne × 3,7 ; (b) K1 aos : `x ** 2.` appelle `pow` (312 ms contre 48,7 en JavaScript) ; sans effet sur le score ;
   (c) K8 : l'arène passe sommet et compteur par références, comme C ; par valeur, × 1,5 ; (d) K7 : 3 mots par case au
   lieu de 2 (× 1,22) ; (e) K9 en `floatarray` × 1,45 à 1,56, K5 à 8 accumulateurs 35 à 51 ms contre 71,6 ; (f)
   l'horloge : `Runtime_events.Timestamp.get_current`, monotone et à la nanoseconde, existe depuis OCaml 5.4.
3. **La grille** : D5 = 1 trop généreux (pas de barrière explicite ; JavaScript a ½) ; E7 = 0 sévère (attributs de
   flambda), discutable ; A1, A2, A7 à 0 défendables.
4. **Le README** : « flottants boxés » est faux pour K1 (l'enregistrement de flottants est à plat ; 144 octets =
   16 flottants de 8 octets, un en-tête, un pointeur) ; « pas de flottant 32 bits non boxé » : il n'en existe aucun de
   calcul ; le point 6 (concurrence) oublie OCaml (écrivain unique 7 fois plus lent que C).
5. **Score** : 25,9 à 27,8 avec le code corrigé, − 0,3 avec la grille ; OCaml reste 18e. OxCaml (SIMD, `float32#`,
   tableaux non boxés, pile) est exclu par la règle, comme la version de développement de Zig. Mesures de l'auteur :
   OCaml 4.14.1 sans flambda, sur ses propres réécritures.

## 2. Vérifications (faites avant le plan)

**Machine 20.** La VM a redémarré le 3 novembre à 15 h 02 sur un hôte Emerald Rapids du même modèle que les machines
3 et 8 à 19 (modèle 207, 4 vCPU ; 2,93 à 3,19 GHz effectifs, latence à 4 Mio 55 ns, DRAM 12,2 à 12,9 Go/s :
`results/hw/machine20/`). Chaîne de l'étude : OCaml 5.5.2 avec flambda (`/opt/ocaml`, `ocamlopt -config` :
`flambda: true`) ; le binaire publié se recompile à l'identique. Les sources du compilateur ne sont plus sur la
machine : le code émis est vérifié par désassemblage. Sorties : `results/ocaml_check/`. Temps ci-dessous : médianes
d'un processus.

* **Le rang (1)** : exact pour ce que je peux vérifier. Pas de module de flottant 32 bits dans la bibliothèque (le
  type n'existe que comme `float32_elt` de `Bigarray`) ; `Int.popcount`, `leading_zeros` et `trailing_zeros` sont
  écrits en OCaml (`int.ml`, Hacker's Delight) ; sur un `max` et une sélection compilés par `ocamlopt -O3`, un
  branchement et pas de `cmov`, ni `popcnt` ni `prefetch` dans le code émis ; `Atomic.get` est une lecture de champ,
  `fetch_and_add` et `exchange` (donc `Atomic.set`) appellent `caml_atomic_fetch_add_field` et
  `caml_atomic_exchange_field` dans le binaire publié ; aucune barrière dans `atomic.mli` ni `domain.mli`. La
  décomposition de l'avance de Haskell est exacte (0,40 × 27,8 ; 0,35 × 15,2 ; 0,25 × 3,1). « Heavy-weight » n'est
  pas dans `domain.mli` ; le manuel n'est pas sur la machine.
* **(2a) Q6 tuned** : **exact, et c'est une erreur de mon implémentation.** Le désassemblage de `q6_tuned` montre deux
  branchements conditionnels par ligne (`jl`), ceux des `&&` en court-circuit. **La convention** : toutes les autres
  implémentations calculent ce prédicat sans branchement, et le code l'annonce (le masque multiplie la contribution).
  Comparaisons séparées, combinées par `land` : cinq `setcc`, plus aucun branchement de données ; 236 → 86 ms (`mt` :
  63 → 33 ms), même somme. Le masque des bits de signe de la remarque, une forme de plus : 78 et 19 ms.
* **(2b) K1 aos** : **exact, erreur de mon implémentation.** La fonction `e` n'est pas inlinée et appelle `pow@plt`
  trois fois par particule ; toutes les autres implémentations élèvent au carré par une multiplication. Corrigé :
  272 → 44 ms. Sans effet sur le score : le plafond de K1 prend le meilleur d'aos et de soa (12,3 ms publiés).
* **(2c) K8 tuned** : le passage par références est la forme de C, corrigée en sensibilité seulement pour C
  (`c_k8val`) : **sensibilité** ici aussi (par valeur : 205 → 167 ms). Mais les deux références sont **allouées à
  chaque requête** (`ref 0`, `ref qq`), quand la spécification exige « aucune allocation en régime permanent » et que
  C les tient sur la pile : **erreur de mon implémentation**, corrigée en allouant les deux références une fois
  (remises à zéro à chaque requête) ; effet nul sur le temps (200 et 205 ms). Le reste des allocations de la variante
  vient du harnais, hors de la section chronométrée (le tri des latences par `compare`).
* **(2d) K7 tuned** : exact sur le fait (3 mots par case), pas une erreur : le code fait ce qu'il annonce (« [clé ;
  compteur ; somme] par case »), et les autres langages n'atteignent 16 octets par case que par des champs de 32 bits,
  qu'OCaml n'a pas ; tasser clé et compteur dans un entier est une forme nouvelle. **Sensibilité** (644 → 560 ms).
* **(2e) K9 et K5** : **sensibilités.** K9 en `floatarray` : aucun gain avec flambda (35,9 → 35,5 ms ; `mt` 22,4 →
  20,1) ; l'écart de la remarque vient d'OCaml 4.14 sans flambda, qui ne compile pas en ligne les accès `Bigarray`.
  K5 à 8 accumulateurs : 69 → 65 ms ; JavaScript en utilise 8, Lua et OCaml 4 : pas de convention.
* **(2f) Horloge** : **exact, erreur de mon implémentation.** La spécification demande « l'horloge monotone de plus
  haute résolution du langage » ; l'écart (`Unix.gettimeofday`, murale, à la microseconde) était consigné depuis le
  premier audit, faute d'horloge monotone connue dans la distribution ; `Runtime_events.Timestamp.get_current` y est
  depuis 5.4 (`runtime_events.mli`, nanosecondes). Sonde : les deux horloges coûtent 30 à 36 ns et n'allouent rien ;
  l'écart entre deux lectures successives vaut 0 avec `gettimeofday`, 29 ns avec `Runtime_events`. Effet attendu
  nul sur les temps.
* **(3) Grille** : **D5 : exact, erratum.** Les langages qui n'ont que l'une des deux capacités (barrière ou
  indication d'attente) ont ½ : Zig, C3, Chapel, Fortran, JavaScript ; OCaml n'a que `Domain.cpu_relax`. **E7 :
  discutable, gardé** (flambda spécialise des fonctions sur leurs arguments, pas des types ; pas de calcul à la
  compilation dans le langage) : **sensibilité** (½). A1, A2, A7 : gardés, comme le dit la remarque.
* **(4) README** : **exact.** Le commentaire du banc le dit : l'enregistrement de 16 flottants est stocké à plat ;
  144 octets = 16 × 8 + en-tête + pointeur. Écrivain unique : 428,6 ms contre 59,7 en C (7,2 fois ; Go 6,2, Haskell
  6,5). S'y ajoutent deux chiffres dépassés du paragraphe d'OCaml : K8 naturel 319 ms (334,5 publiés) et parcours
  permuté 6,9 fois (7,0).
* **(5)** : versions et OxCaml non vérifiables sans le web ; OxCaml est hors de la règle (une seule version officielle
  par langage).

## 3. Plan (poussé avant les mesures)

### 3.1 Règle commune et application

`docs/FORTRAN.md`, 3.1. Erreurs : Q6 tuned (le prédicat branche), K1 aos (`pow`), K8 tuned (deux allocations par
requête), l'horloge ; erratum D5 ; texte du README. Sensibilités : Q6 au masque de signe, arène de K8 par valeur, K7 à
deux mots par case, K9 en `floatarray`, K5 à 8 accumulateurs, E7.

### 3.2 Ce qui entre dans le classement publié

* **O-E** : les clés dont le code chronométré change (Q6 tuned et `mt`, qui appelle la même fonction ; K1 aos ; K8
  tuned) × r(`ocaml_fix` / `ocaml_ref`), **par transfert** (règle de la remarque sur Haskell, `docs/HASKELL.md`, 3.2 :
  le rapport d'OCaml à C d'un même binaire change d'un modèle d'hôte à l'autre ; le pont par le C reste calculé en
  information). Les autres clés ne changent que d'horloge : comme pour Odin (`docs/ODIN.md`, 4.2), à code identique un
  rapport mesuré ailleurs ne porte qu'un effet de placement ; elles ne sont pas reportées, et leur rapport
  `fix` / `ref` sert de contrôle de l'horloge. Latences de K8 naturel (D3) : code inchangé, non reportées.
* **Matrice** : D5 = ½ (`analysis/capabilities.py`).
* **Réplication (machine 3)** : les mêmes clés × les mêmes rapports (transfert), par `results/ocaml_check.json`
  (« replication_ratios »), lu par `m3_ratios`.
* **Texte du README** : tableau, paragraphe d'OCaml, points 1 et 6 de « Ce qui sépare vraiment les langages »,
  errata, langages relus.

### 3.3 Copies (`tools/ocaml_check/make_copies.py`)

* `ocaml_ref` : copie exacte de `bench/ocaml_k9h` (le code publié avec le harnais commun de K9) ; binaire identique.
* `ocaml_fix` : quatre corrections : (a) Q6 tuned, comparaisons séparées combinées par `land` ; (b) K1 aos, `x *. x` ;
  (c) K8 tuned, références allouées une fois ; (d) horloge `Runtime_events.Timestamp.get_current`.
* `ocaml_exp` : `ocaml_fix` et des variantes nouvelles : K6 `tuned_m` et `mt_m` (Q6, masque de signe), K8 `tuned_val`
  (par valeur, comme `c_k8val`), K7 `tuned_p` (deux mots par case), K9 `tuned_fa` et `mt_fa` (`floatarray`), K5
  `tuned_8` (huit accumulateurs).
* Validation (`tools/ocaml_check/validate.py`) : sommes de contrôle de toutes les cellules OCaml de la campagne.

### 3.4 Mesures (`tools/measure_ocaml.py`, machine 20)

87 cellules en 7 passes (609 processus) ; dans chaque passe, toutes les cellules dans un ordre tiré au hasard (graine
20261703) : `ocaml_ref` et `ocaml_fix` sur les 36 clés d'OCaml ; `ocaml_exp` sur ses 7 variantes nouvelles ; `c`
(binaire de la campagne) sur les 8 clés corrigées ou de sensibilité (pont en information). Répétitions de
`results/calib.json` (variante d'origine pour les variantes nouvelles) ; échauffements de la campagne (2 pour K5,
1 sinon) ; règle de vol du pilote. Rien d'autre ne tourne. Sortie : `results/raw_ocaml/`.

### 3.5 Scénarios (`analysis/ocaml_check.py`, analyse globale de la v3 rejouée, mêmes tirages)

| Scénario | Contenu |
|---|---|
| Avant | classement publié d'avant (D5 = 1) ; doit reproduire `results/haskell_check.json` (H-E) à l'identique |
| O-code | les quatre clés corrigées × r(`ocaml_fix` / `ocaml_ref`), D5 = 1 |
| O-M | erratum D5 = ½ seul |
| **O-E (publié)** | les deux |
| O-E-P | O-E, clés reportées par le pont par le C (règle de `analysis/transfer_check.py`, règle de sens ; information) |
| S-Q6m | O-E ; Q6 tuned et `mt` × r(masque de signe / `ocaml_fix`) |
| S-K8v | O-E ; K8 tuned × r(`tuned_val` / `ocaml_fix` tuned) |
| S-K7p | O-E ; K7 tuned × r(`tuned_p` / `ocaml_fix` tuned) |
| S-K9fa | O-E ; K9 tuned et `mt` × r(`floatarray` / `ocaml_fix`) |
| S-K5 | O-E ; K5 tuned × r(`tuned_8` / `ocaml_fix` tuned) |
| S-mesures | toutes les formes |
| S-cases | O-E ; E7 = ½ |
| S-tout | S-mesures et S-cases |

Rapports : moyenne géométrique des médianes de processus, intervalle par bootstrap ; sensibilités en min(1, r) par
rapport à O-E. Sorties : `results/ocaml_check.json`, `results/report_ocaml.md`, `results/transfers.json` (OCaml) ;
puis régénération des sorties publiées (la réplication comprise) et de l'état actuel.

### 3.6 Ce que je ne fais pas

* Pas de mesure sur Cascade Lake ; pas d'OxCaml (expérimental, hors de la règle) ni d'OCaml 4.14.
* Pas de K10 (hors score) ; pas de remesure de l'empreinte (la structure ne change pas).
