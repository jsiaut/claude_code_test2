# v4 : plan (19 novembre 2026)

*Décidé par l'auteur de l'étude après la troisième remarque générale (`docs/AUDIT3_RESPONSE.md`) : le classement de 1 à
25 reste en tête du README ; les points de la v4 sont traités un à un, « dans l'ordre de pertinence ». Ce plan est
poussé avant tout travail ; chaque point reçoit son plan détaillé, poussé avant ses mesures ou ses calculs.*

## 1. Ordre de pertinence

L'ordre suit ce que chaque point peut changer dans le résultat publié, et à quel point ce résultat repose aujourd'hui sur
une hypothèse non vérifiée.

1. **Une sonde par case de la grille** (fait le 19 novembre : `docs/GRID_AUDIT.md`). Le contrôle explique 74 % des
   écarts de score entre les 14 premiers et décide de l'ordre du premier étage (sans lui, Chapel passe de la 10e à la 4e
   place, C++ de la 3e à la 5e) ; or 520 de ses 850 cases ne reposent que sur une lecture, et 56 des cases « sondées » à
   0 ne sont qu'imprimées par une sonde, sans preuve exécutée. 6 % des cases ont déjà été corrigées.
2. **Trois tailles par noyau** (fait le 20 novembre : `docs/V4_SIZES.md`, section 10). Toutes les mesures reposent
   sur une seule taille par noyau, sauf K2, où le rapport de Python au C varie de 1,1 à 30 selon la taille. C'est
   l'hypothèse non testée qui touche le plus de cases mesurées : tous les langages, tous les noyaux.
3. **Des conditions égales.** Les vérifications du code naturel (coupées dans cinq chaînes compilées, gardées dans sept
   et dans les langages gérés), la
   structure du stencil naturel (contiguë dans douze langages, imbriquée dans treize) et le SIMD explicite interdit dans
   K4 (l'absence de vectoriseur y compte deux fois) touchent des sous-ensembles de langages et de noyaux.
4. **Un code optimisé convergent.** Les formes mieux écrites que les remarques ont trouvées (Julia + 3 à 5 points, C#
   + 7 à 8) montrent que le plafond dépend aussi de l'effort ; un catalogue de formes porté dans tous les langages qui
   peuvent les écrire.
5. **Le coût d'accès au plafond.** Une quantité nouvelle (lignes ajoutées, code `unsafe`, intrinsèques propres à une
   architecture, portabilité), qui pourrait remplacer une partie de la grille jugée ; elle ne corrige rien de publié.
6. **Une piste ouverte.** Les bibliothèques tierces (NumPy, crate `libc`, MAX, `vector`…) répondent à une autre
   question, celle de l'écosystème ; elle demande une liste fixée d'avance et de nouvelles implémentations.

## 2. Point 1 : une sonde par case

### 2.1 Norme de preuve

Chaque case des 25 langages reçoit une ligne `CAP;<case>;<note>;<preuve>` produite par une exécution, dans
`results/probes/<langage>.txt`, confrontée à la matrice par `analysis/check_probes.py`. La preuve commence par sa
classe :
* **[exécutée]** pour une note de 1 ou de ½ : un programme se sert de la capacité, sous sa forme la plus forte que la
  chaîne livre, et imprime un fait observable (taille, décalage, adresse modulo, valeur, fil épinglé, instruction émise
  dans le code machine…). Pour ½, la preuve montre aussi la limite (option expérimentale exigée, sous-ensemble, portée).
* **[échec]** pour une note de 0 portée par la syntaxe ou la sémantique : la forme canonique est tentée, et le refus du
  compilateur ou l'erreur à l'exécution est imprimé ; ou le comportement contraire est mesuré (par exemple la taille
  d'un objet qui n'est pas en ligne).
* **[recherche]** pour une note de 0 portée par une API absente : les sources livrées de la bibliothèque standard (à
  défaut, la liste des API publiques obtenue par introspection ou par les documents de référence livrés avec la chaîne)
  sont fouillées avec des motifs fixés d'avance par capacité (`tools/grid_audit/patterns.json`) ; le nombre de résultats
  publics est imprimé, et chacun est examiné.
* C3 reste **[mesurée]** (`tools/c3_measure.py`).

Une sonde cherche à donner tort à la matrice : elle essaie la forme la plus forte, et une recherche qui trouve quelque
chose suspend la note (`?`) jusqu'à l'examen du résultat.

### 2.2 Ordre de travail

Le premier étage d'abord, puisque c'est là que la grille décide : Rust, Zig, Odin, C3, D, Nim, Ada, Fortran, Chapel,
Julia et Mojo (sondes à compléter), puis C, C++ et Swift (preuves des cases à 0) ; ensuite le deuxième étage (C#, Java,
Go, Haskell ; FreePascal pour ses cases à 0), puis le troisième (OCaml, JavaScript, Python, Lua ; BQN et PHP pour leurs
cases à 0). Chaque lot de langages est poussé dès qu'il est sondé.

### 2.3 Divergences et errata

* La sonde établit les faits ; la note suit la règle écrite (v1, et v2 pour le score central), sans la changer. Toute
  case dont la sonde contredit la note est un erratum, publié avec sa preuve dans `docs/GRID_AUDIT.md`.
* Les errata sont appliqués ensemble, une fois toutes les sondes faites : une seule régénération des sorties publiées,
  de la réplication et des états actuels, avec le classement d'avant (« Avant ») et d'après comparés.
* Une case où la sonde ne tranche pas (fait établi, mais note discutable sous la règle) reste à sa note et est listée
  comme telle, avec l'effet des deux notes possibles en sensibilité.

### 2.4 Sorties

`probes/<langage>/` (sondes complétées), `tools/grid_audit/` (motifs et recherche), `results/probes/<langage>.txt`,
`results/probes/summary.md`, `docs/GRID_AUDIT.md` (méthode, divergences, errata), `docs/CAPABILITIES.md` (état de
preuve par classe), puis les sorties publiées régénérées si des errata changent des notes.

## 3. Points 2 à 6

Point 2 : plan détaillé dans `docs/V4_SIZES.md` (19 novembre, poussé avant tout changement de code et toute mesure) ;
résultats le 20 novembre (section 10) : aucun langage ne bouge de plus de deux places entre la taille publiée et la
moyenne des trois tailles ; l'hôte en déplace cinq de trois ou quatre places.


Chacun recevra son plan détaillé (implémentations, données, cellules, campagne, scénarios), poussé avant ses mesures,
une fois le point précédent terminé. Machine : l'hôte actuel est un Xeon Granite Rapids (modèle 173), une troisième
micro-architecture ; les campagnes y seront appariées à un témoin C, comme les précédentes, et le choix de l'hôte sera
fixé dans chaque plan. (20 novembre : depuis le redémarrage de 1 h 19, l'hôte est un Xeon Emerald Rapids, modèle 207,
machine 31 : `docs/V4_SIZES.md`, 7.2.)
