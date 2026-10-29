# Réponse au second audit (29 octobre 2026)

*L'audit est archivé tel quel dans [`docs/AUDIT2_2026-10-29.md`](AUDIT2_2026-10-29.md) ; les numéros de section
cités ici sont les siens. J'ai recalculé chacune de ses affirmations chiffrées avec
[`analysis/verify_audit2.py`](../analysis/verify_audit2.py) (sortie : `results/verify_audit2.txt`) et vérifié ses
explications de mécanisme par des sondes. J'y réponds par une analyse v3. Son plan
([`docs/ANALYSIS_V3.md`](ANALYSIS_V3.md)) a été poussé avant tout calcul (15:54, commit `ae9e1a1`), et son code
avant son premier calcul sur les données (commit `d0b959b`). Les analyses v1 et v2 restent publiées telles
quelles.*

## 1. En bref

* **L'audit a raison sur l'essentiel : l'ordre fin du premier groupe n'est pas une propriété des langages.** La v3
  va plus loin, avec un test fixé d'avance. Le désaccord entre les deux machines dépasse ce que le bruit de mesure
  peut produire : p < 0,001 pour les quatre statistiques, même en doublant le bruit supposé de la machine 3. C'est
  une interaction entre langage et machine, pas seulement du bruit.
* **Je retrouve tous ses chiffres**, à l'arrondi ou à l'erreur de Monte-Carlo près (section 2). Deux écarts
  mineurs tiennent à des choix de calcul et ne changent rien.
* **Une de ses explications est fausse, et la mienne aussi.** Ni le réglage `avoid_fma256_chains` de GCC (son
  hypothèse) ni le « mode ISO » (la mienne) n'expliquent K5 naturel sur la machine 3. GCC vectorise la réduction en
  ordre strict : multiplications en vecteur, chaîne d'additions scalaires. clang laisse la boucle scalaire et la
  fusionne en FMA (section 3).
* **Une objection juste, à conclusion inchangée** : ma sonde du JIT de .NET désactivait la compilation par
  niveaux. Avec les réglages par défaut, PGO dynamique comprise, les boucles restent scalaires.
* **Ce que la v3 change** (section 4) :
  * la forme de la réponse : des étages fixés par une règle écrite d'avance, trois quantités publiées séparément
    et des énoncés de mécanisme ; le score composite n'est plus qu'une analyse de sensibilité ;
  * l'inférence : références fixes, bootstrap à résidus regroupés, test « bruit ou interaction », décomposition
    de la variance ;
  * une expérience : huit dispositions aléatoires du code pour C (clang), C (gcc) et Rust.
* **La réponse qui en sort** (section 7) : quatre étages, {Ada, C, C#, C++, C3, Chapel, D, Fortran, Go, Java,
  Julia, Mojo, Nim, Odin, Rust, Zig} > Haskell > OCaml > {JavaScript, Lua, Python}, sans ordre à l'intérieur
  d'un étage. Les écarts à l'intérieur du premier étage se lisent dans les profils, pas dans un rang.
* **Ce que je ne fais pas** (section 6) : nouvelle campagne entrelacée, plusieurs micro-architectures avec
  compteurs, régimes « base » et « peak », relecture experte, nouveaux noyaux. Rien de cela n'est faisable ici
  par un auteur seul ; je dis pour chacun pourquoi.

## 2. Affirmations chiffrées, recalculées sur les données

| Section | Affirmation de l'audit | Ce que je trouve | Verdict |
|---|---|---|---|
| 4.3.4 | Accord entre machines : 21 paires inversées sur 210, toutes dans les 13 premiers ; Spearman 0,70 et 21 inversions sur 78 pour les 13 premiers ; 0,22 et 17 sur 36 pour les 9 premiers | 21 sur 210, aucune hors des 13 premiers ; 0,70 et 21 sur 78 ; 0,22 et 17 sur 36. Machine 3 : C++ 1er, Rust 2e, C 3e | exact |
| 4.3.4 | Corrélations par mesure : médiane 0,75 sur 35 mesures ; K2 à 32 et 64 Mio et à 512 Kio, K3 `rmw_packed`, K1 AoS presque nulles | Médiane 0,70 sur 35 mesures, avec mon estimateur et les 21 langages classés. Les plus basses sont les mêmes : K2 512 Kio −0,05, 64 Mio 0,06, 32 Mio 0,08, 16 Mio 0,12, 8 Mio 0,18 ; K3 `rmw_packed` 0,28 ; K1 AoS 0,41 | exact sur le fond ; la médiane dépend de l'estimateur |
| 4.3.1 | Position du score MS dans son intervalle v2 : moyenne 0,78, C 0,96, les 21 au-dessus de 0,5 | 0,78 ; C 0,96 ; 21 sur 21, de 0,59 (Lua) à 0,96 | exact |
| 4.3.1 | Biais de la frontière : la frontière bootstrap est sous la frontière observée dans 83 à 98 % des tirages sur K1, K5 et K9 ; le tenant ne garde la note 1 que dans 14 à 31 % | Même calcul (1 000 tirages, processus puis répétitions, sans coupure) : K1 0,90 et 0,21 ; K5 0,84 et 0,31 ; K9 0,99 et 0,12. Ailleurs de 0,27 à 0,77 | exact |
| 4.3.5 | Parmi les 13 premiers, le pilier C explique 78 % de la variance de MS, E 52 %, D 27 % | 0,78 ; 0,52 ; 0,27 | exact |
| 4.6 | Aucun choix isolé ne déplace un langage de plus de 3 rangs, mais réintégrer K10 en déplace 11 des 13 premiers et met C++ en tête | Déplacement maximal 3 (pilier C v1 et K10) ; avec K10, 11 des 13 premiers bougent, C++ premier | exact |
| 4.2.3 | 289 coupures de régime : 154 accélérations, 135 ralentissements ; 207 en AOT, dont 89 ralentissements ; 146 sur K5 | 289 ; 154 et 135 ; 146 sur K5. En comptant Java, C#, Node, Bun, Julia et LuaJIT comme JIT : 203 coupures en AOT, dont 88 ralentissements | exact ; l'écart de 4 tient au classement des implémentations |
| 4.1.2 | K5 naturel, machine 3 : 160 à 166 ms avec chaîne de FMA (C/clang, Chapel, Mojo, flang), 77 à 87 ms sans | C/clang 160,4, Chapel 163,6, Mojo 165,6, flang 165,7 ; C++ 76,6 à C# 87,1 | exact |
| 4.1.2 | Sur Cascade Lake, l'écart n'existe pas | Machine 1 (v1) : C (gcc) 163,4 ms, C (clang) 169,2, flang 170,5, Mojo 172,8, Chapel 175,7 | exact |
| 4.2.2 | K5 `tuned`, machine 3 : un même binaire varie d'un facteur 2 entre processus (C++ 2,71 à 5,26 ms…) ; médianes de 3,74 (C gcc) à 5,71 ms (Julia) | Mêmes valeurs, au centième : C++ 4,05 (2,71–5,26), Odin 4,03 (2,80–6,00), C 3,88 (2,81–5,36), Rust 3,98 (3,72–5,43), C# 4,32 (3,05–6,06) | exact |
| 4.1.3 | Les 21 implémentations commitées entre 08:54 et 11:03 le 28 octobre ; matrice de capacités à 11:49 | `git log` : 08:54 (référence C), 09:39, 10:16, 11:03 ; matrice dans `e9af238` à 11:49 | exact |
| 4.4.1 a | Cellules de capacités incohérentes (F4, A6, D3, Mojo, E2 de Go) | Les cellules citées sont bien notées ainsi dans `analysis/capabilities.py` et `capabilities_v2.py` | exact ; je ne renote pas (section 6) |

## 3. Mécanismes et faits d'outils

| Section | Point | Vérification | Verdict |
|---|---|---|---|
| 4.1.2 | GCC éviterait la chaîne de FMA sur K5 naturel grâce à `avoid_fma256_chains` | Sonde [`probes/k5_reduction`](../probes/k5_reduction) (machine 3, GCC 16, clang 23 ; `results/probes/k5_reduction.txt`). Avec `--param avoid-fma-max-bits=0`, la boucle de GCC ne change pas : `vmulps`, puis deux `vaddss`, 73,4 ms contre 73,3. GCC vectorise la réduction en ordre strict (multiplications en vecteur, additions scalaires dans l'ordre des indices). g++ et gfortran produisent la même boucle | **erroné** pour la cause, exact pour le constat |
| 4.1.2 | Mon explication : « GCC en mode ISO garde une multiplication vectorielle et une chaîne d'additions scalaires » | Avec `-std=gnu23`, où GCC autorise la contraction, la boucle est identique ; les trois FMA du binaire sont hors de la boucle | **ma propre erreur**, corrigée dans `docs/FINDINGS.md` et le README |
| 4.1.2 | clang contracte en FMA | La boucle de clang est scalaire : `vfmadd231ss`, 158,6 ms. Avec `-ffp-contract=off` : `vmulss` et `vaddss`, 82,2 ms. Avec `-mllvm -force-ordered-reductions`, qui fait vectoriser la réduction ordonnée comme GCC : 80,3 ms | exact. La chaîne coûte 4 cycles par élément avec une FMA, 2 avec une addition (`tools/addfma.c`) |
| 4.1.2 | K3 : renommage mémoire appliqué selon l'adresse | Cohérent avec mes mesures à 16 décalages ; non vérifiable sans compteurs. L'expérience de disposition (section 7) mesure l'effet du placement sur les binaires réels | plausible, non vérifié |
| 4.1.2, 4.4.2 | La borne de 5 cycles par incrément de K3 n'est pas une borne sur la machine 3 | Exact. Elle ne sert qu'aux données de la machine 1, dans l'alternative « bornes physiques » de E, où le meilleur temps vaut 5,7 cycles à 3,3 GHz. Le contrôle de vraisemblance de la machine 3 utilise 1 incrément par cycle à 3,9 GHz | exact, sans effet sur les résultats |
| 4.5 | La sonde C# désactivait la compilation par niveaux, donc la PGO dynamique | Sonde [`probes/csharp_jitvec_tiered`](../probes/csharp_jitvec_tiered) : réglages par défaut, boucle de 3 s, désassemblage de chaque niveau. Au niveau 1 « *optimized using Dynamic PGO* » (ou *Synthesized PGO*), la somme d'entiers (`add eax, dword ptr [rdi]`), l'addition de tableaux de `float` (`vaddss`) et la somme conditionnelle restent scalaires (`results/probes/csharp_jitvec_tiered_disasm.txt`) | objection **juste**, conclusion **inchangée** |
| 4.2.2 | « C# en régime établi : 4,3 ms, contre 3,9 ms pour C » n'est pas un ordre | Médianes de processus : C# 3,05 à 6,06 ms, C 2,81 à 5,36 | exact : c'est une égalité, corrigé |

## 4. Critiques de méthode : ce que la v3 change

| Critique | Ce que fait la v3 | Ce qui en sort |
|---|---|---|
| L'ordre du premier groupe n'est pas établi (4.3.4, 4.6) | Des étages, selon une règle fixée d'avance (plan, section 3) : une frontière n'est retenue que si aucune paire de part et d'autre n'est inversée sur la machine 3 et si chaque paire est ordonnée dans le même sens dans au moins 95 % des tirages de l'analyse globale. Pas d'ordre dans un étage | Quatre étages ; 16 langages dans le premier (section 7) |
| Bruit ou différence de machine ? (4.3.4) | Test fixé d'avance : simulation de la machine 1 et de la machine 3 sans interaction, avec le bruit mesuré entre processus, 2 000 fois | Le désaccord observé est hors de la distribution nulle : p < 0,001 pour les quatre statistiques, y compris avec un bruit de la machine 3 multiplié par 1,5 ou 2 |
| Frontière recalculée à chaque tirage : biais (4.3.1) | Références fixes, calculées une fois sur les estimations ponctuelles | Position moyenne de E dans son intervalle : 0,46 (C 0,50), contre 0,72 (C 0,94) en v2. MS reste un peu décentré, 0,43 en moyenne : ⟨cause⟩ |
| Deux ou trois processus ne permettent pas d'estimer la variance entre processus (4.3.2) | Bootstrap à résidus regroupés : la variance entre processus vient de toutes les cellules d'un même noyau et d'une même classe (AOT, JIT, interprète) | Intervalles plus étroits qu'en v2 (largeur médiane de E : 4,8 points contre 6,4), parce que la frontière n'ajoute plus son bruit. Ils supposent des résidus échangeables dans un réservoir, et ne valent que pour la machine 1 : le test de réplication montre que la machine compte davantage |
| Ensembles de Mogstad sans garantie (4.3.3) | Recalculés sur ce bootstrap, publiés au second rang | Même condition de validité que le bootstrap |
| Coupure du « régime établi » (4.2.3) | Supprimée. Chaque processus est classé (plat, accélération, ralentissement), comme chez Barrett et al. | Sans coupure, l'estimateur change peu les rangs (Nim et D échangent leur place). Processus AOT : 1 548 plats, 115 accélérations, 88 ralentissements ; JIT : 519, 36, 46 ; interprètes : 218, 3, 1 |
| Décomposition de la variance (6, P0 3) | Pour chaque mesure présente sur les deux machines : part du langage, de l'interaction langage × machine et du processus | Sur les 21 langages, le langage domine (82 à 99 %) sauf K2 à 8 Mio (89 % de bruit entre processus). Dans les 13 premiers (hors plan), l'interaction domine sur K3 `sw_padded` (97 %) et pèse sur K1 AoS (52 %), K7 naturel (41 %), K1 permuté (38 %) ; le bruit domine sur les mesures limitées par la bande passante |
| Disposition du code non contrôlée (4.2.4) | Expérience : C (clang), C (gcc) et Rust, huit dispositions chacune (`--randomize-section-padding` de lld), deux processus par disposition, K1 à K9 | ⟨résultats⟩ |
| Score composite, pilier C décisif (4.3.5, 4.3.6, P0 1) | Trois quantités publiées séparément : plafond E (avec la part de la borne physique), code naturel D1 (et l'écart du langage à son propre meilleur code), contrôle C sous les règles v1 et v2. Le composite n'est plus qu'une sensibilité | Section 7 |
| Le score mêle deux micro-architectures (4.2.6) | E et D1 publiés aussi pour la machine 3 seule ; Cascade Lake seul en sensibilité (hors plan) | Section 7 |

## 5. Erreurs de ma part, corrigées

1. **Le mécanisme de K5 naturel** (« GCC en mode ISO »). Corrigé dans `docs/FINDINGS.md` et le README (section 3).
2. **« C et C++ sont les deux seuls langages qui peuvent être premiers. »** Retiré : sur la machine 3, l'ordre est
   C++, Rust, C, et le test de réplication montre que cet ordre dépend de la machine.
3. **« Le haut du classement s'ordonne en partie. »** Retiré pour la même raison.
4. **Le résumé de la réplication en v2** (« Spearman 0,93, aucun langage ne sort de son groupe ») masquait le
   désaccord à l'intérieur du premier groupe. La v3 publie l'accord par sous-ensemble et le test.
5. **« C# en régime établi : 4,3 ms contre 3,9 ms pour C »** présenté comme un écart. C'est une égalité.
6. **La sonde C#** observait un JIT réglé autrement que celui du benchmark. Refaite avec les réglages par défaut.
7. **Une phrase périmée du README** : « même en SIMD explicite, K5 plafonne à 17 ms » (section 5 du README),
   alors que la remesure v2 donne 4,3 ms une fois le JIT stabilisé. Corrigée.
8. **L'heure du plan v3** : j'avais écrit « vers 16:30 » ; il a été poussé à 15:54. Corrigé dans le plan.

## 6. Ce que je ne fais pas, et pourquoi

| Recommandation de l'audit | Raison |
|---|---|
| Campagne entrelacée et randomisée de 10 à 30 processus par mesure (P0 2) | Environ 15 heures par machine avec 9 processus ; davantage avec 30. Sur cette seule machine, elle ne dirait pas si l'ordre fin est une propriété des langages, puisque la v3 montre qu'il dépend de la machine |
| Trois micro-architectures avec compteurs matériels (P1 6) | Pas d'autre machine ni de PMU dans cet environnement. Les explications de mécanisme restent des inférences, sauf là où une sonde change une seule chose (K5, K3, K8) |
| Régimes « base » (x86-64-v3) et « peak » (PGO, LTO, BOLT, options du runtime) (P1 5) | Les variantes `tuned` en AVX-512 explicite ne compilent pas en x86-64-v3 sans réécriture ; reporté |
| Relecture experte, deux implémentations par noyau, entrées réservées (P0 4) | Impossible pour un auteur seul. Les tailles sont fixées dans 21 implémentations ; les changer après coup serait du sur-ajustement inverse |
| Nouvelle notation du pilier C par plusieurs évaluateurs à l'aveugle (P1 7) | Un seul évaluateur. Le pilier C est publié à part, sous ses deux règles, comme un inventaire jugé |
| Modèle mixte complet, indices de Sobol (P0 3, 4.3.6) | Le bootstrap à résidus regroupés joue le rôle d'un effet aléatoire « processus » par noyau et classe ; la décomposition de la variance donne les parts. Pas de modèle avec effets de chaîne et de disposition croisés : deux chaînes seulement pour C et Fortran, une seule machine pour la disposition |
| Nouveaux noyaux : parallélisme mémoire, décompression, JSON, tri et jointure, E/S groupées, thread par cœur, démarrage, front-end (P1 8) | 21 implémentations par noyau ; reportés. La conclusion « tous les noyaux sont des microbenchmarks » reste vraie |
| Pré-enregistrement externe (P2 9) | Les plans v2 et v3 sont poussés avant les calculs, mais écrits après avoir vu les données précédentes ; ils le disent |

## 7. Résultats de la v3

Sorties complètes : [`results/report_v3.md`](../results/report_v3.md) et `results/summary_v3.json`. Le README en
donne la lecture.

**Étages (règle du plan).**
1. Ada, C, C#, C++, C3, Chapel, D, Fortran, Go, Java, Julia, Mojo, Nim, Odin, Rust, Zig
2. Haskell
3. OCaml
4. JavaScript, Lua, Python

L'audit proposait quatre étages un peu différents (§ 5) : il séparait C#, Java et Go des 13 premiers, et mettait
Haskell avec OCaml. La règle fixée d'avance ne retient pas la première frontière. Dans les tirages de l'analyse
globale où le pilier de contrôle pèse lourd, C# (contrôle 68,8) passe devant Fortran, Chapel ou Mojo, et Java et
Go chevauchent C#. Elle sépare en revanche Haskell d'OCaml. ⟨étages hors plan⟩

**Réplication : bruit ou interaction ?** 2 000 simulations sans interaction, avec le bruit mesuré entre processus.

| Statistique | Observée | Sans interaction : médiane [5–95 %] | p |
|---|---|---|---|
| Spearman, 21 langages | 0,95 | 0,99 [0,98–1,00] | < 0,001 |
| Spearman, 13 premiers | 0,78 | 0,97 [0,93–0,99] | < 0,001 |
| Spearman, 9 premiers | 0,43 | 0,93 [0,80–0,98] | < 0,001 |
| Paires inversées parmi les 13 premiers | 17 | 3 [1–7] | < 0,001 |

Aucune simulation n'atteint le désaccord observé, ni avec le bruit de la machine 3 multiplié par 1,5 ou 2 (hors
plan). L'estimateur v3 rapproche un peu les deux machines (17 paires inversées au lieu de 21 en v2), sans changer la
conclusion. ⟨K3⟩

**Décomposition de la variance** (part de chaque source, mesures présentes sur les deux machines). Sur les 21
langages, le langage domine partout (82 à 99 %), sauf K2 à 8 Mio, où le bruit entre processus fait 89 %. Restreinte
aux 13 premiers (hors plan), elle change de visage :
* l'interaction langage × machine domine K3 `sw_padded` (97 %) et pèse sur K1 AoS (52 %), K7 naturel (41 %) et K1
  permuté (38 %) ;
* le bruit entre processus domine les mesures limitées par la bande passante : K1 SoA (100 %), K2 à 256 Kio et
  8 Mio (98 et 100 %), K6 Q6 `tuned` et naturel (90 et 80 %) ;
* le langage domine K4 (91 à 92 %), K8 (92 à 94 %), K6 Q1 (76 à 90 %) et K9 naturel (95 %).

**Disposition du code.** ⟨résultats de l'expérience⟩

**Diagnostic des intervalles.** ⟨positions par composante⟩
