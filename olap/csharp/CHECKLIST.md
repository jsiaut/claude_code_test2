# C# : liste de contrôle ([`SPEC.md`](../SPEC.md), 8)

* **Chaîne** : .NET 10 (SDK 10.0.403), configuration Release ; compilation à niveaux et PGO dynamique (réglages par
  défaut), ramasse-miettes de station.
* **Bibliothèques tierces** : aucune.
* **Niveaux** : portable et spécialisé (constante `SPECIAL` : intrinsèques AVX-512 de `System.Runtime.Intrinsics`,
  les mêmes que la référence, écritures non temporelles et préchargement compris ; les expressions et les hachages
  par vecteur y sont écrits à la main, faute de vectorisation automatique).
* **Échappatoires** : code `unsafe` (pointeurs, tampons `fixed`, `stackalloc`) ; mémoire native
  (`NativeMemory.AlignedAlloc`) ; une fonction du système par `DllImport` (`madvise`).

| Famille | Point | Ici |
|---|---|---|
| Calcul d'expressions | décodage par routines spécialisées par largeur | routines engendrées par un programme (`GenUnpack.cs` écrit `UnpackGen.cs`) ; table de pointeurs de fonctions. Une première forme, générique sur un type valeur qui porte la largeur, était spécialisée mais non déroulée par le compilateur à la volée (mesuré : T1 portable de 835 à 481 ms à un fil) |
| Calcul d'expressions | décodage aux seules positions retenues | comme la référence |
| Calcul d'expressions | arithmétique entière exacte sur 64 bits, primitives par vecteur | comme la référence ; le compilateur à la volée ne vectorise pas : ces boucles restent scalaires au niveau portable |
| Calcul d'expressions | recherche de sous-chaîne par mots de 8 octets | comme la référence |
| Localité | cartes de zones : blocs sautés, filtres évités | comme la référence |
| Localité | colonnes sur 64 bits lues sans copie ; chaînes lues en place | comme la référence (`ReadOnlySpan<byte>` sur les octets chargés) |
| Localité | colonnes chargées, arènes et vecteurs de travail en pages larges | comme la référence : mémoire native alignée sur 2 Mio, puis `madvise` |
| Agrégation | tableau indexé par les codes de deux petites clés | comme la référence |
| Agrégation | répartition puis table par partition, qui tient dans le cache | comme la référence |
| Agrégation | cases de 16 et de 32 octets, clé et valeur ensemble | comme la référence (structures, pointeurs) |
| Jointure | filtre de Bloom devant la sonde | comme la référence |
| Jointure | jointure par partition des deux côtés, clés répétées chaînées | comme la référence |
| Exécution parallèle | fils persistants, morceaux pris par un compteur atomique | `Thread`, `Monitor` (`Wait`, `PulseAll`), `Interlocked` |
| Exécution parallèle | état par fil, fusion par le fil principal ; arène par fil | comme la référence |

**Manque.** Pas de vectorisation automatique : au niveau portable, décodage, expressions et hachages par vecteur
sont scalaires.
