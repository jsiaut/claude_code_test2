# Java : liste de contrôle ([`SPEC.md`](../SPEC.md), 8)

* **Chaîne** : OpenJDK 27.0.1 ; options `-XX:+UseTransparentHugePages --enable-native-access=ALL-UNNAMED`. Niveau
  spécialisé : `--add-modules jdk.incubator.vector` (API vectorielle, en incubation).
* **Bibliothèques tierces** : aucune.
* **Niveaux** : portable et spécialisé, ce dernier incomplet (voir les manques).
* **Échappatoires** : mémoire hors tas par l'API FFM (`java.lang.foreign`) ; un segment qui couvre tout l'espace
  d'adressage (`MemorySegment.NULL.reinterpret`) donne l'accès par adresse brute ; deux fonctions du système appelées
  par `Linker` (`aligned_alloc`, `madvise`).

| Famille | Point | Ici |
|---|---|---|
| Calcul d'expressions | décodage par routines spécialisées par largeur | pas de généricité sur les constantes : un aiguillage appelle l'une des deux formes avec la largeur en constante, et le compilateur à la volée spécialise la forme là où il l'intègre ; il ne les vectorise pas |
| Calcul d'expressions | décodage aux seules positions retenues | comme la référence |
| Calcul d'expressions | arithmétique entière exacte sur 64 bits, primitives par vecteur | comme la référence, sur des tableaux du tas |
| Calcul d'expressions | recherche de sous-chaîne par mots de 8 octets | comme la référence |
| Localité | cartes de zones : blocs sautés, filtres évités | comme la référence |
| Localité | colonnes sur 64 bits lues sans copie ; chaînes lues en place | comme la référence, par adresses |
| Localité | colonnes chargées, arènes et vecteurs de travail en pages larges | colonnes et arènes : `aligned_alloc` sur 2 Mio puis `madvise` ; les vecteurs de travail sont des tableaux du tas, mis en pages larges par l'option de la machine virtuelle |
| Agrégation | tableau indexé par les codes de deux petites clés | comme la référence (un tableau de `long` par fil) |
| Agrégation | répartition puis table par partition, qui tient dans le cache | comme la référence ; les tuples sont écrits champ par champ à une adresse |
| Agrégation | cases de 16 et de 32 octets, clé et valeur ensemble | même disposition en mémoire, lue champ par champ : le langage n'a pas de types valeur pour la décrire |
| Jointure | filtre de Bloom devant la sonde | comme la référence |
| Jointure | jointure par partition des deux côtés, clés répétées chaînées | comme la référence |
| Exécution parallèle | fils persistants, morceaux pris par un compteur atomique | `Thread`, moniteur (`wait`, `notifyAll`), `AtomicLong` |
| Exécution parallèle | état par fil, fusion par le fil principal ; arène par fil | comme la référence ; les listes des fils sont des tableaux du tas, gardés d'une exécution à l'autre |

**Manques.**

* Pas de types valeur ni de pointeurs : tables, tuples et tampons sont des octets hors tas lus par décalages.
* Le compilateur à la volée ne vectorise pas le décodage : il est scalaire au niveau portable.
* Niveau spécialisé : l'API vectorielle donne le décodage, la sélection, l'agrégation de T1 et la recherche de
  sous-chaîne ; elle n'a ni écriture non temporelle ni préchargement : la répartition et les sondes restent celles
  du niveau portable.
