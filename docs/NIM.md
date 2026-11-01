# Remarque sur Nim (1er novembre) : vérifications, plan et résultats

Une remarque soutient que Nim perd environ 2 points à cause d'une erreur de banc, la même que celle corrigée pour D :
son Q1 optimisé est écrit « en blocs », hors de la convention. Elle soutient aussi que la cause donnée par le README
pour son stencil naturel est fausse. Ce document vérifie chaque affirmation (section 2), fixe le plan avant toute
mesure (section 3), puis donne les résultats (section 4).

## 1. La remarque

1. **Q1 optimisé** : écrit en blocs, forme que le dépôt « réserve aux langages qui n'ont pas accès aux instructions
   vectorielles » ; 98,5 ms, plus lent que le naturel (95,4 ms), contre 32,1 ms pour C ; 37,3 contre 13,4 ms à 4
   threads. Nim importe les intrinsèques de C (C2 = 1 en règle v2) et s'en sert déjà pour K1 soa et K5 tuned ; Rust,
   sans SIMD portable stable, écrit Q1 avec l'algorithme de la référence C. C'est l'écart corrigé pour D. Traduction
   ligne à ligne du `q1_tuned` de C : × 0,417 (0,397–0,439), 1,02 fois C ; à 4 threads × 0,403 et 1,03 fois C ; même
   résultat avec Nim 2.4.0. Effet : K6 0,52 → 0,85, plafond 72,9 → 77,6, score 69,7 → 71,6 (l'audit estimait
   + 0,8 point, sans la variante à 4 threads).
2. **Stencil naturel** : Nim passe toujours `-fno-strict-aliasing` au compilateur C (`config/nim.cfg` : « seqs_v2
   violates strict aliasing ») ; en `seq[seq[float]]`, ni `-d:danger` seul ni `-fstrict-aliasing` seul ne vectorisent,
   les deux ensemble oui ; `array[M, array[M, float]]` alloué par `new` vectorise en `-d:release` (12,0 ms contre 11,6
   pour C). Sensibilité (+ 0,2 point) ; texte à corriger (tableau, paragraphe, « Ce qui sépare vraiment les
   langages », `FINDINGS.md`).
3. **Ce qui tient** : la matrice (la justification de C4 oublie `{.localPassC.}`, la note de 0,5 reste méritée) ;
   `-d:release` ; la version (2.4.0 et 2.2.14 sortis le 28 octobre, une vingtaine de minutes après les premières
   mesures de Nim ; code identique pour 19 des 21 fonctions des noyaux, temps × 1,01) ; clang plutôt que gcc (avec
   gcc, K4 2,5 à 7,5 fois plus lent, l'arène de K8 23 à 31 % plus rapide, et le harnais de K5 naturel ne mesure plus
   rien, 0,02 ms) ; les écarts de K4 et K5 au plafond ne se reproduisent pas.
4. **K8 optimisé** : l'arène garde ses vérifications de débordement, contrairement aux autres noyaux optimisés du
   fichier ; sans elles, 0,85 de son temps (sensibilité). Scores : 69,7 publié ; 71,6 avec Q1 (7e au score) ; 72,4
   avec K8 et K9 (6e au score). Transferts proposés : Q1 tuned 0,333, Q1 `mt` 0,403.

## 2. Vérifications (faites avant le plan)

**Machine 12.** La VM a redémarré le 1er novembre vers 9 h 10 sur un hôte Emerald Rapids du même modèle que les
machines 3 et 8 à 11 (modèle 207, 4 vCPU), mais plus lent : 2,6 à 2,8 GHz effectifs (3,2 sur les machines 10 et 11),
latence à 4 Mio 36 ns, DRAM 15,3 Go/s (`results/hw/machine12/`). Chaîne du banc : Nim 2.2.12, clang 23.1.5. Preuves :
`results/nim_check/` (script `tools/nim_check/collect.sh`).

* **Chiffres (1)** : exacts à quelques dixièmes près (données principales, médianes des processus : Q1 tuned 98,1 ms,
  naturel 94,9 ms, `mt` 37,8 ms ; C 32,1 et 13,2 ms ; K6 = 0,519). L'audit du 29 octobre estimait bien + 0,8 point
  (`docs/AUDIT_2026-10-29.md`), et les deux audits avaient relevé ce Q1 plus lent que le naturel.
* **Le code fait ce qu'il annonce** (`q1_asm.txt`) : le commentaire dit « le compilateur C vectorise », et c'est le
  cas : la boucle interne traite 8 lignes par tour avec des additions masquées AVX-512 sur des vecteurs xmm et ymm
  (93 instructions vectorielles dans la fonction), la boucle scalaire ne servant qu'au reste. Comme pour le Q1 en
  blocs de D, la première phrase de la règle commune ne s'applique pas sous sa forme « ne fait pas ce qu'il annonce ».
* **La convention (1)** (`q1_convention.txt`) : la remarque cite mal le dépôt. `docs/DLANG.md` (section 2, poussée
  avant les mesures de D) définit la classe par les **types vectoriels portables standard** (C1 = 1 en règle v1),
  pas par l'accès aux instructions vectorielles : dans cette classe (C++, Zig, Odin, C3, Mojo, C#, D), tous écrivent
  Q1 en une passe, D seul s'en écartait. Le même texte range **nommément Nim** parmi les langages à blocs, avec
  Fortran, Chapel, Julia et Ada. Hors de cette classe, la pratique est partagée : C (C1 = 0,5, la référence) et Rust
  (0,5) écrivent une passe avec des intrinsèques ; Nim (0) et Ada (0,5), qui ont pourtant du SIMD explicite dans
  d'autres noyaux (intrinsèques importées pour Nim, `vector_type` et builtins GCC pour Ada), Chapel, Julia et Fortran
  écrivent des blocs. Il n'y a donc pas de convention dont Nim s'écarte : la traduction de la référence C est une
  meilleure forme (seconde phrase de la règle commune), comme les intrinsèques importées de Chapel pour Q1 et les
  formes en une passe de Julia, gardées en sensibilité. **Un autre critère** (« les implémentations qui écrivent leurs
  autres noyaux optimisés en SIMD explicite ») mettrait Nim et Ada en écart, à 9 contre 2 ; je ne le retiens pas, parce
  qu'il changerait après coup la règle fixée pour D, mais je donne son effet pour Nim en sensibilité.
* **Stencil (2)** (`k9_forms.txt`, `versions.txt`) : **exact**. `config/nim.cfg` de 2.2.12 et de 2.4.0 passe
  `-fno-strict-aliasing` à clang (« seqs_v2 violates strict aliasing »). En `seq[seq[float]]` : `-d:release` seul,
  `-d:danger` seul ou `-fstrict-aliasing` seul laissent la boucle scalaire ; `-d:danger` et `-fstrict-aliasing`
  ensemble la vectorisent ; `ref array[M, array[M, float]]` vectorise en `-d:release`. La cause écrite dans le README
  (les vérifications de bornes) est incomplète : il faut lever les vérifications **et** l'interdiction d'aliasing par
  type. Forme naturelle : `docs/NATURAL.md` range Nim (`seq[seq[float]]`) avec les langages à tableaux imbriqués ; les
  lignes de taille fixe restent une sensibilité, comme pour D et Rust.
* **C4 (3)** (`localpassc.txt`) : `{.localPassC.}` n'ajoute l'option qu'au fichier C du module qui la déclare (sonde) :
  granularité du module, pas de l'opération. **Texte précisé, note inchangée (0,5).**
* **Version (3)** (`nim240.txt`, `versions.txt`) : 2.4.0 et 2.2.14 sont sortis le 28 octobre (billet officiel, sans
  heure ; je ne peux pas vérifier « une vingtaine de minutes ») ; les premières mesures de Nim datent de 11 h 22 UTC le
  même jour, avec 2.2.12, la dernière stable à l'installation. Paquet officiel de 2.4.0 (somme SHA-256 conforme) :
  **20 des 21 fonctions des noyaux ont un code machine identique** ; seule la construction de l'arbre de K8 naturel
  diffère (92 → 89 instructions). **Exact** (à une fonction près).
* **gcc (3)** : vérification rapide (une répétition, non retenue) : compilé par gcc 16, K5 naturel prend 0,02 ms au
  lieu de 96 : le harnais ne mesure plus rien. K4 et K8 sont mesurés pour information (section 3.4).
* **K8 (4)** : exact ; l'arène est sous `{.push boundChecks: off.}` seulement, les autres noyaux optimisés sous
  `{.push boundChecks: off, overflowChecks: off.}`. Rien dans le fichier n'annonce que les variantes optimisées
  retirent toutes les vérifications : c'est une meilleure forme possible, comme l'arène de Rust (sensibilité).

## 3. Plan (poussé avant les mesures)

### 3.1 Règle commune

`docs/FORTRAN.md`, 3.1 : « Est une erreur : un code qui ne fait pas ce qu'il annonce (Ada) ou qui s'écarte d'une
convention que les autres implémentations suivent (ici, des noyaux isolés de la boucle de mesure). Une meilleure forme
ou une meilleure disposition, même plus proche de ce que fait C, est une optimisation nouvelle. » Le Q1 en blocs de Nim
fait ce qu'il annonce et suit la pratique de sa classe (section 2) ; le Q1 en intrinsèques, le K9 en tableau fixe et
l'arène sans vérification de débordement sont des optimisations nouvelles.

### 3.2 Ce qui entre dans le classement publié

* **Aucune donnée ne change** : ni correction de banc, ni erratum de note.
* **Le README** : cause du stencil naturel de Nim (vérifications **et** `-fno-strict-aliasing` imposé par Nim), aux
  endroits que cite la remarque (ligne du tableau, paragraphe de Nim, « Ce qui sépare vraiment les langages ») et dans
  `docs/FINDINGS.md` ; dans les limites, Nim 2.4.0 sorti pendant la campagne, sans effet sur le code des noyaux.
* **La matrice** : texte de C4 de Nim précisé (`{.localPassC.}`), note inchangée.

### 3.3 Sensibilités (hors classement publié)

* **Avant** (= publié) : le calcul publié, refait par le même code.
* **S-Q1 / S-Q1-T** : Q1 tuned et `mt` en intrinsèques (`nim_q1` / `nim_ref`), par la règle du pont de
  `analysis/transfer_check.py` (témoin : binaire C de `bench/c`) et par transfert seul. C'est aussi l'effet du critère
  « SIMD explicite dans les autres noyaux » pour Nim (Ada, concerné par ce critère, n'est pas mesuré).
* **S-K9 / S-K9-T** : K9 naturel en `ref array[M9, array[M9, float]]` (`nim_nat` / `nim_ref`).
* **S-K8 / S-K8-T** : arène sans vérification de débordement (`nim_k8` / `nim_ref`).
* **S-tout / S-tout-T** : les trois cumulés.
* **Information** : gcc 16 au lieu de clang 23 (`nim_gcc` / `nim_ref` : K4 naturel et sans branchement, K5 naturel,
  K8 tuned) ; Nim 2.4.0 (`nim_240` / `nim_ref` : K8 naturel, seule fonction dont le code change, et K8 tuned).

### 3.4 Mesures (machine 12)

`tools/measure_nim.py` : 7 processus par cellule en 7 passes, toutes les cellules de chaque passe dans un ordre tiré au
hasard (graine fixe), règle de vol du pilote, échauffements des données principales (1 ; 2 pour K5), répétitions de
`results/calib.json`. Sortie `results/raw_nim/`, étiquette `nim`. Rien d'autre ne tourne pendant la campagne.

| Implémentation | Cellules |
|---|---|
| `nim_ref` (source de la campagne, natif) | Q1 tuned, `mt` et naturel, Q6 tuned, K9 naturel et tuned, K8 tuned et naturel, K4 naturel et sans branchement, K5 naturel et tuned |
| `nim_q1` (Q1 en intrinsèques) | Q1 tuned et `mt` ; témoins Q1 naturel, Q6 tuned |
| `nim_nat` (K9 en tableau fixe) | K9 naturel ; témoin K9 tuned |
| `nim_k8` (arène sans vérification de débordement) | K8 tuned ; témoin K8 naturel |
| `nim_gcc` (gcc 16) | K4 naturel et sans branchement, K5 naturel, K8 tuned |
| `nim_240` (Nim 2.4.0) | K8 naturel et tuned |
| `c` (binaire de `bench/c`, compilé pour Cascade Lake) | Q1 tuned et `mt`, Q6 tuned, K9 naturel, K8 tuned, K4 naturel et sans branchement (témoin des ponts) |

### 3.5 Analyse

`analysis/nim_check.py` : rapports appariés (moyennes géométriques par processus, IC par bootstrap), report sur les
données principales (transfert, ou pont au-delà de 25 % d'écart), scénarios de la section 3.3 rejoués par
`analysis/confrontation.py` (`scenario`) ; sorties `results/nim_check.json` et `results/report_nim.md`.
`results/transfers.json` ne change pas.
