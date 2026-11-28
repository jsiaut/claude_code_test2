# C++ : liste de contrôle ([`SPEC.md`](../SPEC.md), 8)

* **Chaîne** : clang 23.1.5 (`--driver-mode=g++`), C++26, bibliothèque standard du système (libstdc++ 13),
  `-O3 -march=native`. `MS_CC=gcc` construit la même source par g++ 16.2.
* **Bibliothèques tierces** : aucune.
* **Niveaux** : portable et spécialisé (intrinsèques AVX-512 de `<immintrin.h>`, les mêmes que la référence).
* **Échappatoires** : conversions de pointeurs (`reinterpret_cast`) sur la mémoire des arènes et des colonnes ;
  appels du système (`posix_memalign`, `madvise`, `pread`). Le langage ne vérifie pas les bornes.

| Famille | Point | Ici |
|---|---|---|
| Calcul d'expressions | décodage par routines spécialisées par largeur | comme la référence : gabarit `unpack_w<W>`, forme choisie par `if constexpr`, table bâtie à la compilation |
| Calcul d'expressions | décodage aux seules positions retenues | comme la référence |
| Calcul d'expressions | arithmétique entière exacte sur 64 bits, primitives par vecteur | comme la référence |
| Calcul d'expressions | recherche de sous-chaîne par mots de 8 octets | comme la référence |
| Localité | cartes de zones : blocs sautés, filtres évités | comme la référence |
| Localité | colonnes sur 64 bits lues sans copie ; chaînes lues en place | comme la référence (`std::string_view` sur les octets chargés) |
| Localité | colonnes chargées, arènes et vecteurs de travail en pages larges | comme la référence |
| Agrégation | tableau indexé par les codes de deux petites clés | comme la référence |
| Agrégation | répartition puis table par partition, qui tient dans le cache | comme la référence ; tuples typés (`Parts::push<T>`, `parts_each<T>`) |
| Agrégation | cases de 16 et de 32 octets, clé et valeur ensemble | comme la référence |
| Jointure | filtre de Bloom devant la sonde | comme la référence |
| Jointure | jointure par partition des deux côtés, clés répétées chaînées | comme la référence |
| Exécution parallèle | fils persistants, morceaux pris par un compteur atomique | comme la référence : `std::thread`, `std::mutex`, `std::condition_variable`, `std::atomic` ; les tâches sont des lambdas |
| Exécution parallèle | état par fil, fusion par le fil principal ; arène par fil | comme la référence |

Ce qui change de forme : les tables de l'année et du décodage spécialisé sont calculées à la compilation
(`constexpr`) ; les tris passent par `std::sort` ; le résultat est formaté par `std::to_chars`.

**Mesuré au portage** (28 novembre, hors campagne, moyenne géométrique des dix requêtes rapportée à C) : par clang,
0,99 à un fil et 1,01 à quatre au niveau portable ; par g++ 16.2, 1,05 et 1,08. L'écart est celui du compilateur.
