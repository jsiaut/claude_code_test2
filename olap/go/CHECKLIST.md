# Go : liste de contrôle ([`SPEC.md`](../SPEC.md), 8)

* **Chaîne** : go 1.27.3, `GOAMD64=v4`. Niveau spécialisé : `GOEXPERIMENT=simd` (paquet `simd/archsimd`,
  expérimental).
* **Bibliothèques tierces** : aucune.
* **Niveaux** : portable et spécialisé, ce dernier incomplet (voir les manques).
* **Échappatoires** : `unsafe` (pointeurs et tranches sur la mémoire hors tas des colonnes, des arènes, des tables
  et des tampons) ; mémoire hors tas par `syscall.Mmap` et `syscall.Madvise`. Les vérifications de bornes restent
  là où le code passe par des tranches ; aucune option ne les coupe.

| Famille | Point | Ici |
|---|---|---|
| Calcul d'expressions | décodage par routines spécialisées par largeur | routines engendrées par un programme (`gen_unpack.go` écrit `unpack_gen.go`) : le langage n'a pas de généricité sur les constantes ; chaque routine est la suite des 64 affectations d'un groupe, à positions constantes |
| Calcul d'expressions | décodage aux seules positions retenues | comme la référence |
| Calcul d'expressions | arithmétique entière exacte sur 64 bits, primitives par vecteur | comme la référence ; le compilateur ne vectorise pas : ces boucles restent scalaires au niveau portable |
| Calcul d'expressions | recherche de sous-chaîne par mots de 8 octets | comme la référence |
| Localité | cartes de zones : blocs sautés, filtres évités | comme la référence |
| Localité | colonnes sur 64 bits lues sans copie ; chaînes lues en place | comme la référence (tranches sur la mémoire chargée) |
| Localité | colonnes chargées, arènes et vecteurs de travail en pages larges | comme la référence : `mmap` anonyme aligné sur 2 Mio, puis `madvise` ; rien de tout cela n'est dans le tas du ramasse-miettes |
| Agrégation | tableau indexé par les codes de deux petites clés | comme la référence |
| Agrégation | répartition puis table par partition, qui tient dans le cache | comme la référence ; tuples typés par généricité (`push[T]`, `tuples[T]`) |
| Agrégation | cases de 16 et de 32 octets, clé et valeur ensemble | comme la référence |
| Jointure | filtre de Bloom devant la sonde | comme la référence |
| Jointure | jointure par partition des deux côtés, clés répétées chaînées | comme la référence |
| Exécution parallèle | fils persistants, morceaux pris par un compteur atomique | goroutines persistantes, bloquées sur un canal entre deux phases ; `sync.WaitGroup` ; `atomic.Uint64` ; `GOMAXPROCS` vaut le nombre de fils |
| Exécution parallèle | état par fil, fusion par le fil principal ; arène par fil | comme la référence |

**Manques.**

* Pas de vectorisation automatique : au niveau portable, décodage, expressions et hachages par vecteur sont
  scalaires.
* Niveau spécialisé : `simd/archsimd` donne le décodage, la sélection, l'agrégation de T1 et la recherche de
  sous-chaîne ; il n'a ni écriture non temporelle ni préchargement : la répartition et les sondes restent celles du
  niveau portable.
