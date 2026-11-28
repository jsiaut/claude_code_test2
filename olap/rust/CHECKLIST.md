# Rust : liste de contrôle ([`SPEC.md`](../SPEC.md), 8)

* **Chaîne** : rustc 1.99.1, édition 2024, `-C opt-level=3 -C target-cpu=native -C codegen-units=1`.
* **Bibliothèques tierces** : aucune (bibliothèque standard seule).
* **Niveaux** : portable et spécialisé (`--cfg special` : intrinsèques AVX-512 de `std::arch`, les mêmes que la
  référence).
* **Échappatoires** : `unsafe` pour les pointeurs bruts des arènes, des tables, des tampons de partition et des
  colonnes, et pour les accès sans vérification de bornes des primitives ; `unsafe impl Sync` et `Send` sur ces
  structures ; durée de vie de la tâche d'une phase effacée par `transmute` (les fils sont persistants) ; une fonction
  du système déclarée à la main (`madvise`).

| Famille | Point | Ici |
|---|---|---|
| Calcul d'expressions | décodage par routines spécialisées par largeur | comme la référence : fonctions à paramètre constant (`const W`), table de 33 pointeurs écrite à la main |
| Calcul d'expressions | décodage aux seules positions retenues | comme la référence |
| Calcul d'expressions | arithmétique entière exacte sur 64 bits, primitives par vecteur | comme la référence (tranches de même longueur, parcourues ensemble) |
| Calcul d'expressions | recherche de sous-chaîne par mots de 8 octets | comme la référence |
| Localité | cartes de zones : blocs sautés, filtres évités | comme la référence |
| Localité | colonnes sur 64 bits lues sans copie ; chaînes lues en place | comme la référence (tranches sur les octets chargés) |
| Localité | colonnes chargées, arènes et vecteurs de travail en pages larges | comme la référence (`std::alloc` aligné sur 2 Mio, puis `madvise`) |
| Agrégation | tableau indexé par les codes de deux petites clés | comme la référence |
| Agrégation | répartition puis table par partition, qui tient dans le cache | comme la référence ; tuples typés (`Parts::push<T>`, `parts_each::<T>`) |
| Agrégation | cases de 16 et de 32 octets, clé et valeur ensemble | comme la référence (`#[repr(C)]`) |
| Jointure | filtre de Bloom devant la sonde | comme la référence |
| Jointure | jointure par partition des deux côtés, clés répétées chaînées | comme la référence |
| Exécution parallèle | fils persistants, morceaux pris par un compteur atomique | comme la référence : `std::thread`, `Mutex`, `Condvar`, `AtomicU64` |
| Exécution parallèle | état par fil, fusion par le fil principal ; arène par fil | les tâches rendent leur résultat au fil principal (`Pool::run` rend un `Vec`) au lieu d'écrire dans un tableau partagé ; arènes, vecteurs de travail et tampons restent par fil |

Ce qui change de forme : le niveau est choisi par `--cfg special` (module `level`) ; au niveau portable, les appels de
préchargement sont des fonctions vides sous une constante fausse, et disparaissent à la compilation ; les lignes du
résultat final (quelques centaines) sont dans un `Vec` de l'allocateur général.
