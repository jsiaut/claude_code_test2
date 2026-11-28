# Zig : liste de contrôle ([`SPEC.md`](../SPEC.md), 8)

* **Chaîne** : Zig 0.18.0-dev.1298 (LLVM 23), la version de développement, comme dans le banc actuel
  ([`docs/V5_2.md`](../../docs/V5_2.md)) ; `-O fast -mcpu native`.
* **Bibliothèques tierces** : aucune.
* **Niveaux** : portable et spécialisé ; le fichier racine (`olap_p.zig`, `olap_s.zig`) fixe une constante que le
  code teste à la compilation.
* **Échappatoires** : pointeurs à plusieurs éléments (`[*]T`) et conversions de pointeurs sur la mémoire prise au
  système ; appels du système directs (`mmap`, `madvise`, `open`, `pread`) ; au niveau spécialisé, trois instructions
  en assembleur en ligne. Le mode `-O fast` ne vérifie ni bornes ni débordements.

| Famille | Point | Ici |
|---|---|---|
| Calcul d'expressions | décodage par routines spécialisées par largeur | comme la référence : routines engendrées à la compilation (`comptime`), les 64 affectations déroulées par `inline for` |
| Calcul d'expressions | décodage aux seules positions retenues | comme la référence |
| Calcul d'expressions | arithmétique entière exacte sur 64 bits, primitives par vecteur | comme la référence |
| Calcul d'expressions | recherche de sous-chaîne par mots de 8 octets | comme la référence |
| Localité | cartes de zones : blocs sautés, filtres évités | comme la référence |
| Localité | colonnes sur 64 bits lues sans copie ; chaînes lues en place | comme la référence |
| Localité | colonnes chargées, arènes et vecteurs de travail en pages larges | comme la référence (`mmap` aligné sur 2 Mio, puis `madvise`) |
| Agrégation | tableau indexé par les codes de deux petites clés | comme la référence |
| Agrégation | répartition puis table par partition, qui tient dans le cache | comme la référence ; tuples typés (`push(T, k)`, `tuples(T, c)`) |
| Agrégation | cases de 16 et de 32 octets, clé et valeur ensemble | comme la référence (`extern struct`) |
| Jointure | filtre de Bloom devant la sonde | comme la référence |
| Jointure | jointure par partition des deux côtés, clés répétées chaînées | comme la référence |
| Exécution parallèle | fils persistants, morceaux pris par un compteur atomique | `std.Thread`, `std.Io.Mutex` et `std.Io.Condition`, `std.atomic.Value` |
| Exécution parallèle | état par fil, fusion par le fil principal ; arène par fil | comme la référence |

**Niveau spécialisé.** Types vectoriels du langage (`@Vector`) pour le décodage (la permutation d'octets de chaque
largeur est un masque de `@shuffle` calculé à la compilation), l'agrégation de T1 (`@select`), la recherche de
sous-chaîne et les comparaisons de la sélection ; `@prefetch` pour le préchargement. Trois instructions n'ont pas
d'opération dans le langage et passent par l'assembleur en ligne : la compression des positions (`vpcompressd`),
l'écriture non temporelle (`vmovntdq`) et `sfence`.
