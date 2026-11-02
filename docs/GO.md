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
