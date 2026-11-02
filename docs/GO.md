# Remarque sur Go : une transition AVX→SSE oubliée, et un artefact du runtime sur Emerald Rapids

L'auteur de l'étude m'a transmis le 2 novembre une remarque sur Go. Elle juge le groupe de Go (avec C# et Java, derrière
les treize langages compilés sans ramasse-miettes imposé) justifié, mais pas le détail : un banc jamais relu qui
sous-estime le langage, et des mesures sur Emerald Rapids faussées par un défaut du runtime de Go 1.27. Ce document
vérifie chaque affirmation (section 2), fixe le plan avant toute mesure (section 3), puis donne les résultats
(section 4). Je n'ai consulté aucune page web : les faits viennent des sources de go1.27.3, de sondes et des données
publiées.

## 1. La remarque

1. **Ce qui est juste** : pas de vectoriseur automatique ; SIMD expérimental (`simd/archsimd` et, nouveau dans Go 1.27,
   le paquet portable `simd`, sous `GOEXPERIMENT=simd`) ; atomiques seulement séquentiellement cohérentes (XCHG pour
   un `Store`), alors que le runtime a des chargements acquire et des écritures release qu'il n'exporte pas ; Green Tea
   actif par défaut depuis Go 1.26 ; matrice de Go exacte. Ces trois traits expliquent l'écart avec Mojo.
2. **Un banc jamais relu**, quatre défauts : (a) K5 tuned réduit son accumulateur par un tableau puis une boucle
   scalaire, et paie une pénalité AVX→SSE à chaque appel (≈ 20 → 7,5 ms en ajoutant `ClearAVXUpperBits`, 5,5 ms
   réécrit ; C 3,5) ; le README l'attribue à tort au SIMD expérimental ; (b) K9 tuned est scalaire, alors que Mojo, C#
   et Zig l'écrivent en SIMD explicite (18,4 → 11,9 ms) ; (c) Q1 tuned est scalaire (60,5 → 40,6 ms) ; (d) l'arène
   de K8 passe son état par des pointeurs (257 → 132 ms en itératif).
3. **Un artefact de mesure** : tout le banc est compilé avec `GOEXPERIMENT=simd` ; la préemption asynchrone de
   go1.27.3 sauvegarde et restaure alors les 32 registres ZMM sans `VZEROUPPER`, et le code scalaire qui mêle SSE
   hérité et VEX paie ensuite la transition. K1 naturel : 32 ms sans l'expérience, 2 100 ms avec, 34 ms avec
   `GODEBUG=asyncpreemptoff=1`. C'est l'anomalie de `docs/FINDINGS.md` (« cause non cherchée »). Elle pèserait surtout
   sur la réplication (code naturel 5,8 sur la machine 3 contre 12,3), peu sur le classement publié.
4. **Score** : 45,8 (errata a minima), 47,3 (formes expertes), 47,4 à 49,0 (avec l'arène) ; Go 15e ou 16e, loin de
   C# (54,9).

## 2. Vérifications (faites avant le plan)

**Machine 18.** La VM a redémarré le 2 novembre à 9 h 48 sur un hôte Emerald Rapids du même modèle que les machines 3
et 8 à 17 (modèle 207, 4 vCPU ; 2,62 à 2,77 GHz effectifs, latence à 4 Mio 37 ns, DRAM 14 à 15 Go/s :
`results/hw/machine18/`). Chaîne de l'étude : go1.27.3 (`/opt/go127`), `GOAMD64=v4`. Preuves : `results/go_check/`.

* **Ce qui est juste (1)** : exact. `simd/archsimd` et `simd` (portable) portent `//go:build goexperiment.simd` ;
  `internal/buildcfg/exp.go` active `GreenTeaGC` par défaut ; `internal/runtime/atomic` a `LoadAcq` et `StoreRel`,
  que `sync/atomic` n'exporte pas ; la note C3 = 0 de Go est mesurée. K3, écrivain unique : 370 ms contre 60 en C dans
  les données publiées.
* **(2a) K5 tuned** : **exact, et c'est une erreur de mon implémentation.** Après la boucle AVX-512, la réduction
  scalaire s'exécute en SSE hérité (`XORPS`, `ADDSS`, désassemblage) sans `VZEROUPPER`. Sonde sur la machine 18 : 19 à
  27 ms la forme du banc, 7,4 ms avec `archsimd.ClearAVXUpperBits()` après `StoreArray` ; couper la préemption ne
  change rien (19 à 20 ms) : c'est la transition à chaque appel (65 536 par répétition), pas l'artefact (3). La
  documentation d'archsimd donne cette fonction « pour passer d'AVX à SSE, en éliminant les pénalités ». **La
  convention** : dans toutes les autres implémentations à SIMD explicite, le code vectoriel rend l'unité propre avant
  le code scalaire, parce que leur compilateur ou leur JIT émet `VZEROUPPER` (clang, GCC et les compilateurs LLVM,
  le JIT de .NET, C2) ; en Go, c'est au programmeur de l'écrire, et je ne l'ai pas fait. Même nature que le K5
  désaligné de Java : une étape que les autres franchissent, oubliée. Le README (« K5 5 fois plus lent que C avec le
  SIMD expérimental ») attribue donc à la maturité du SIMD de Go ce qui vient de mon banc.
* **(2b) K9 tuned** : exact sur le fait (scalaire), mais pas une erreur : C, C++, Rust, Java, Nim et Ada écrivent aussi
  K9 tuned en scalaire (`docs/NOSIMD.md`, tableau), et la règle appliquée à D ne vaut que pour la classe C1 = 1, où Go
  n'est pas (archsimd expérimental, C1 = ½). **Sensibilité**, comme pour Java.
* **(2c) Q1 tuned** : même verdict ; `docs/NOSIMD.md` (2.3) range déjà Go parmi les cinq implémentations à SIMD
  explicite qui écrivent Q1 autrement qu'en une passe vectorielle. **Sensibilité.**
* **(2d) K8 tuned** : `aBuild(a *[]ANode, d int, c *int64)` passe la tranche et le compteur par pointeur ; l'arène
  itérative est une forme nouvelle, comme pour C. **Sensibilité.**
* **(3) L'artefact** : **exact, et il touche aussi le classement publié.** `runtime/preempt_amd64.s` : sous
  `GOEXPERIMENT_simd`, sur un processeur AVX-512, la préemption asynchrone sauvegarde Z0 à Z31 (et les registres de
  masque) et les restaure, puis revient sans `VZEROUPPER`. Sonde sur la machine 18 (un processus) : K1 naturel
  2 434 ms avec le binaire publié, 38,9 ms avec la copie standard de la confrontation (`bench/go_std`, même code
  machine pour les variantes naturelles, compilée sans `GOEXPERIMENT`), 39,9 ms avec `GODEBUG=asyncpreemptoff=1` ;
  K5 naturel 129, 103 et 94 ms ; K9 sans écart net. Dans les données publiées, la machine 3 donne à Go 1 875 ms sur
  K1 naturel (Cascade Lake : 50 ms) et 3,4 fois le temps de C sur K7 naturel (Cascade Lake : 1,13). **La remarque
  sous-estime sa portée** : K5 (machine 3) et K9 (machine 16) entrent au classement publié depuis Emerald Rapids. Le
  défaut est dans ma mesure : les variantes qui n'utilisent pas archsimd n'ont pas besoin de l'expérience, et le code
  naturel d'un programme Go ne serait pas compilé avec elle ; `docs/METHODOLOGY.md` (confrontation) avait conclu que,
  le code machine étant identique, il était inutile de les remesurer sans `GOEXPERIMENT`, sans voir l'effet du runtime.
  Sur Cascade Lake, d'où vient le reste du classement publié, rien ne montre l'artefact (K1 naturel 50 ms, 1,22 fois
  C) ; je ne peux pas y mesurer.
* **(1) Code naturel de la réplication** : D1 de Go 0,123 sur Cascade Lake, 0,058 sur la machine 3. **Exact.**
* **(4) Les quinze langages devant Go** ont été relus (Java le dernier). **Exact.**
* Non vérifiables sans le web : les numéros de ticket, la proposition SLP du 26 mai.

## 3. Plan (poussé avant les mesures)

### 3.1 Règle commune et application

`docs/FORTRAN.md`, 3.1 (« un code qui ne fait pas ce qu'il annonce ou qui s'écarte d'une convention que les autres
implémentations suivent » est une erreur ; une meilleure forme est une optimisation nouvelle). Erreurs : (2a) la
transition AVX→SSE (convention : l'unité vectorielle rendue propre avant le code scalaire) ; (3) la mesure des
variantes sans archsimd dans un binaire compilé avec l'expérience. Formes nouvelles : (2b), (2c), (2d), et la réduction
de K5 dans les registres.

### 3.2 Ce qui entre dans le classement publié

* **G-K5** : les quatre clés archsimd (K5 tuned, K1 soa, Q6 tuned, Q6 `mt`) × r(`go_fix` / `go_ref`), report par la
  règle de `analysis/transfer_check.py` (pont par le C du même hôte au-delà de 25 % d'écart), rapport retenu plafonné
  à 1 (une correction qui accélère le code sur le même hôte ne peut pas allonger le temps publié, `docs/JAVA.md`, 4).
* **G-pre** : les clés publiées depuis Emerald Rapids qui n'utilisent pas archsimd (K5 naturel, machine 3 ; K9
  naturel, tuned et `mt`, machine 16) × r(`go_noexp` / `go_ref`), même règle du pont, sans plafond : c'est la
  configuration de mesure qui change, dans un sens ou dans l'autre. Les clés venues de Cascade Lake ne changent pas.
* **Réplication (machine 3)** : chaque clé de Go × r(`go_noexp` / `go_ref`) (clés sans archsimd) ou r(`go_fix` /
  `go_ref`) (clés archsimd), mesurés sur la machine 18, du même modèle (transfert, comme les rapports du harnais de
  K9 : `analysis/analyze_v3.py`).
* **Mise en œuvre** : les rapports de K5, K1 et K6 vont dans `results/transfers.json` ; ceux de K9, appliqués après le
  remplacement de K9 par les données de la machine 16, dans une clé `ratios_k9h` du même fichier, lue par
  `apply_k9h` (`analysis/analyze_v2.py`).
* **Texte du README** : paragraphe de Go (K5), leçons et limites.

### 3.3 Copies (`tools/go_check/make_copies.py`)

* `go_ref` : copie exacte de `bench/go_k9h` (le code publié avec le harnais commun de K9), `GOEXPERIMENT=simd`.
* `go_fix` : `archsimd.ClearAVXUpperBits()` après la partie vectorielle de `k1SoA`, `k5Tuned` et `q6Tuned` (trois
  lignes), rien d'autre.
* `go_noexp` : `bench/go_std` (variantes sans archsimd identiques à celles du banc publié), avec la fonction `runK9`
  de `bench/go_k9h`, compilée sans `GOEXPERIMENT` ; variante K8 `tuned_it` (arène itérative, comme `c_k8it`).
* `go_exp` : `go_fix` et des variantes archsimd nouvelles : K5 `tuned_r` (réduction dans les registres ; le résultat
  passe par la mémoire avant `ClearAVXUpperBits`, sans quoi le compilateur place `VZEROUPPER` avant la réduction, qui
  salit de nouveau les registres : vérifié au désassemblage), K9
  `tuned_vec` et `mt_vec` (`Float64x8`, même ordre des additions, résultat identique au bit près), K6 `tuned_1p` et
  `mt_1p` (Q1 en une passe, algorithme de la référence C, six groupes en variables locales, additions masquées par
  `IfElse`) ; chaque fonction archsimd finit par `ClearAVXUpperBits`.
* `go_nopre` : le binaire de `go_ref` lancé avec `GODEBUG=asyncpreemptoff=1` (information sur le mécanisme).
* Validation (`tools/go_check/validate.py`) : sommes de contrôle de toutes les cellules Go de la campagne.

### 3.4 Mesures (`tools/measure_go.py`, machine 18)

96 cellules, 7 processus chacune (672 processus), en 7 passes ; dans chaque passe, toutes les cellules dans un ordre
tiré au hasard (graine 20261502) : `go_ref` sur les 36 clés de Go ; `go_noexp` sur les 32 clés sans archsimd et K8
`tuned_it` ; `go_fix` sur les 4 clés archsimd ; `go_exp` sur K5 tuned et ses 5 formes nouvelles ; `go_nopre` sur 6
clés ; `c` (binaire de la campagne) sur les 11 clés reportées. Répétitions de `results/calib.json` ; échauffements de la
campagne (2 pour K5, 1 sinon) ; règle de vol du pilote. Rien d'autre ne tourne. Sortie : `results/raw_go/`.

### 3.5 Scénarios (`analysis/go_check.py`, analyse globale de la v3 rejouée, mêmes tirages)

| Scénario | Contenu |
|---|---|
| Avant | classement publié d'avant ; doit reproduire `results/java_check.json` (J-E) à l'identique |
| G-K5, G-K5-T | correction des clés archsimd seule (pont ; transfert seul) |
| G-pre, G-pre-T | correction de l'artefact sur les clés d'Emerald Rapids seule |
| **G-E (publié)**, G-E-T | les deux |
| S-K5r | G-E ; K5 tuned × r(`go_exp` `tuned_r` / `go_exp` tuned) |
| S-K9v | G-E ; K9 tuned × r(`go_exp` `tuned_vec` / `go_noexp` tuned), K9 `mt` × r(`go_exp` `mt_vec` / `go_noexp` `mt`) |
| S-Q1 | G-E ; Q1 tuned × r(`go_exp` `tuned_1p` / `go_noexp` tuned), Q1 `mt` × r(`go_exp` `mt_1p` / `go_noexp` `mt`) |
| S-K8 | G-E ; K8 tuned × r(`go_noexp` `tuned_it` / `go_noexp` tuned) |
| S-mesures, S-mesures-T | toutes les formes (pont ; transfert seul) |

Rapports : moyenne géométrique des médianes de processus, intervalle par bootstrap ; ceux des sensibilités en
min(1, r). Sorties : `results/go_check.json`, `results/report_go.md` ; puis régénération des sorties publiées (la
réplication comprise) et de l'état actuel.

### 3.6 Ce que je ne fais pas

* Pas de mesure sur Cascade Lake (aucun hôte disponible) : les clés de Go qui en viennent gardent leurs temps.
* Pas de `GODEBUG` ni d'option du runtime dans les données publiées : `go_nopre` ne sert qu'à montrer le mécanisme.
* Pas de changement de la matrice : ses cellules de Go sont exactes.

## 4. Résultats (après les mesures)

Mesures du 2 novembre, de 10:07:12 à 10:38:43, sur la machine 18 : 672 processus (96 cellules × 7), aucune somme de
contrôle fausse ; 26 processus refaits pour vol de temps (six deux fois), deux gardés au-dessus de 2 % après les deux
reprises que prévoit la règle (C, K9 `mt`, 2,72 % ; `go_fix`, K5 tuned, 2,08 %) ; vol médian 0,50 % ; 2,57 à 2,76 GHz
effectifs avant et après. Rien d'autre ne tournait. Sorties : `results/report_go.md` et `results/go_check.json`
(`analysis/go_check.py`) ; données : `results/raw_go/`. Le scénario Avant reproduit exactement le classement publié
d'avant (écart 0). Aucun écart au plan.

### 4.1 La transition AVX→SSE (`go_fix` / `go_ref`, même hôte)

| Clé | `go_ref` | `go_fix` | Rapport (IC 95 %) | C, même hôte | Retenu |
|---|---|---|---|---|---|
| K5 tuned | 22,57 ms | 8,66 ms | 0,384 (0,318–0,482) | 4,32 ms | 0,384 : 18,86 → 7,24 ms (C 3,94) |
| K1 soa | 2,56 ms | 2,77 ms | 1,081 (1,029–1,141) | 2,77 ms | 1 (plafond) |
| Q6 tuned | 17,15 ms | 17,67 ms | 1,031 (0,955–1,123) | 17,75 ms | 1 (plafond) |
| Q6 `mt` | 4,92 ms | 4,51 ms | 0,917 (0,812–1,021) | 4,84 ms | 0,917 |

K5 appelle son noyau 65 536 fois par répétition, et payait la transition à chaque appel : corrigé, Go passe de 4,8 à
1,8 fois le temps de C. K1 soa et Q6 n'appellent le leur qu'une fois par répétition : rien à gagner, comme attendu.

### 4.2 L'artefact (`go_noexp` / `go_ref`, même hôte)

* **Massif sur K1, nul ailleurs.** K1 naturel, aos et permuté : × 0,017, 0,023 et 0,016 (2 241 → 38 ms, 1 464 → 34,
  2 298 → 37) ; sans préemption asynchrone (`go_nopre`), K1 naturel fait aussi 37 ms. Les 29 autres clés sans
  archsimd : 0,87 à 1,11, presque toutes dans l'intervalle de 1. Le désassemblage dit pourquoi : K1 mêle SSE hérité
  (`MOVSS`, `CVTSS2SD`, `MULSD`) et VEX (les FMA de `GOAMD64=v4`), K9 est tout en SSE ; c'est le passage d'un encodage à
  l'autre, une fois les registres salis par la préemption, qui coûte.
* **Clés publiées depuis Emerald Rapids** : K5 naturel × 1,023, K9 naturel × 0,989, `mt` × 0,914 (transfert) ; K9 tuned
  : transfert 27,64 ms, pont 21,88 ms, écart 26 %, la règle retient le pont (× 0,820). L'effet sur le classement publié
  est donc faible, comme le dit la remarque, mais pas parce que le publié viendrait de Cascade Lake : K5 et K9 viennent
  d'Emerald Rapids, et l'artefact ne touche presque pas ces deux noyaux.
* **Information** : sans préemption asynchrone, K9 tuned va 1,38 fois plus lentement (non expliqué ; hors du publié).

### 4.3 Les sensibilités

| Forme | Clé | Rapport (IC 95 %), même hôte | Remarque | Facteur retenu |
|---|---|---|---|---|
| Réduction de K5 dans les registres | K5 tuned | 0,753 (0,616–0,929) : 10,60 → 7,98 ms (`go_exp`) | 5,5 ms | 0,289 (5,45 ms) |
| K9 en archsimd | K9 tuned | 0,776 (0,674–0,879) : 20,0 → 15,5 ms (C 14,5) | 18,4 → 11,9 ms | 0,636 |
| K9 en archsimd, quatre goroutines | K9 `mt` | 0,730 (0,657–0,817) : 7,9 → 5,8 ms (C 4,8) | | 0,667 |
| Q1 en une passe, archsimd | K6 tuned Q1 | 1,361 (1,088–1,644) : 75,9 → 103,2 ms (C 24,5) | 60,5 → 40,6 ms | 1 |
| idem, quatre goroutines | K6 `mt` Q1 | 0,940 (0,898–0,988) | | 0,940 |
| Arène itérative | K8 tuned | 0,621 (0,556–0,691) : 277 → 172 ms (C 295) | 257 → 132 ms | pont 0,378 |

* **Mon Q1 en une passe est plus lent que la forme scalaire** : trente accumulateurs vectoriels et les additions
  masquées par `IfElse` ne tiennent pas en registres avec ce compilateur ; la forme de la remarque (40,6 ms sur son
  hôte) n'est pas la mienne, et je ne la connais pas. La règle du plan (min(1, r)) n'en retient rien.
* **K8** : sur Cascade Lake, le K8 optimisé de Go fait 1,54 fois le temps de C ; sur la machine 18, 0,94 fois (le K8 de
  C, compilé par clang, y est lent : `docs/C.md`). Le pont (155 ms) s'écarte du transfert (255 ms) de 64 % ; la règle
  retient le pont. S-mesures-T, en transfert seul, donne l'autre lecture.
* Dans `go_exp`, le K5 tuned corrigé fait 10,6 ms, contre 8,7 dans `go_fix` : même code, autre binaire (placement).

### 4.4 Classement (analyse globale de la v3 rejouée, 20 000 variantes)

| Scénario | Score de Go | Plafond | Rang espéré | Place | Devant Java |
|---|---|---|---|---|---|
| Avant | 43,0 | 38,7 | 15,62 | 16 | 30 % |
| G-K5 ; G-K5-T | 45,0 ; 45,0 | 43,7 | 15,47 | 16 | 42 % |
| G-pre ; G-pre-T | 43,3 ; 43,1 | 39,4 ; 38,8 | 15,61 ; 15,62 | 16 | 31 % |
| **G-E (publié)** ; G-E-T | **45,3** ; 45,1 | 44,5 ; 43,9 | 15,45 ; 15,47 | 16 | 43 % ; 42 % |
| S-K5r | 46,0 | 46,1 | 15,39 | 16 | 48 % |
| S-K9v | 46,0 | 46,1 | 15,41 | 16 | 47 % |
| S-Q1 | 45,4 | 44,6 | 15,45 | 16 | 44 % |
| S-K8 | 47,7 | 50,3 | 15,17 | 15 | 62 % |
| S-mesures ; S-mesures-T | 49,2 ; 47,6 | 54,1 ; 50,1 | 15,01 ; 15,21 | 15 | 71 % ; 60 % |

* **Classement publié** : Go gagne 2,3 points (45,3 : 2,0 par K5, 0,3 par l'artefact) et reste 16e, mais l'avance de
  Java n'est plus solide : Go le devance dans 43 % des variantes (30 % avant). C# reste loin (54,9). Les autres
  langages ne bougent pas.
* **Les estimations de la remarque tiennent** : 45,8 avec les errata a minima (ici 45,3), 47,3 avec les formes expertes
  (46,0 pour K5 ou K9 seuls), 47,4 à 49,0 avec l'arène (S-mesures-T 47,6, S-mesures 49,2). Avec l'arène seule, ou avec
  toutes ses formes optimisées, Go passe 15e, devant Java.

### 4.5 Réplication (machine 3)

Avec les rapports de la machine 18 (`go_noexp` / `go_ref` pour les clés sans archsimd, `go_fix` / `go_ref` pour les
autres), le code naturel de Go passe de 5,8 à 10,7 sur la machine 3 (12,3 sur Cascade Lake) et son score de réplication
de 37,3 à 39,3 ; il y reste 16e, et l'ordre de la réplication ne change pas (C++, Rust, C en tête).

### 4.6 Bilan

* **Exact** : les faits du langage et de la matrice ; le défaut de K5, une erreur de mon banc, corrigée ; l'artefact,
  un défaut de ma mesure, corrigé dans le classement publié et dans la réplication ; les estimations de score.
* **À nuancer** : K9 et Q1 ne relèvent pas de la règle appliquée à D (Go est hors de la classe C1 = 1, et C, C++, Rust
  et Java écrivent aussi K9 en scalaire) : sensibilités ; l'artefact « pèse peu sur le classement publié », mais parce
  qu'il ne touche presque que K1, pas parce que le publié viendrait de Cascade Lake (K5 et K9 viennent d'Emerald
  Rapids) ; ma forme de Q1 en une passe ne retrouve pas le gain annoncé.
* **Effet** : + 2,3 points au classement publié (45,3), toujours 16e, mais à portée de Java (devant lui dans 43 % des
  variantes) ; 15e avec l'arène itérative ou toutes ses formes optimisées (47,6 à 49,2 points) ; C# reste loin (54,9),
  par son contrôle.
