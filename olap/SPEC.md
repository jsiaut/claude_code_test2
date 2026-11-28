# Banc OLAP (v7) : spécification commune

*Ce document dit ce que chaque implémentation doit faire, au même degré de détail pour tous les langages : format des
données, paramètres, primitives, table de hachage, plan physique de chaque requête, forme des résultats. Le plan daté
est [`docs/V7.md`](../docs/V7.md). L'implémentation de référence est [`c/olap.c`](c/olap.c) : en cas de doute, elle
fait foi. État : gelé le 28 novembre 2026, après la validation de la référence C contre DuckDB et ClickHouse.*

## 1. Contrat d'une implémentation

```
olap <requête> <fils> <répétitions> <répertoire des données> [--print]
```

* `requête` : `t1`, `t6`, `t9`, `t18` (TPC-H ; le répertoire contient `lineitem/`, `orders/`, …) ou `c4`, `c12`, `c16`,
  `c20`, `c33`, `c36` (ClickBench ; le répertoire contient `hits/`).
* Le processus charge en mémoire les colonnes que lit la requête (4.6), crée ses fils, puis exécute la requête
  `répétitions` fois. Chaque exécution part des octets du format et fabrique toutes ses structures ; la mémoire des
  arènes peut être gardée d'une exécution à l'autre. La mesure écarte les premières exécutions (échauffement).
* Pour chaque exécution, une ligne : `RESULT;<requête>;<niveau>;<fils>;<rang>;<secondes>;<empreinte>`. Le niveau est
  `p` (portable) ou `s` (spécialisé) ; l'empreinte est le FNV-1a 64 bits, en 16 chiffres hexadécimaux, du résultat
  canonique (section 6). Avec `--print`, le résultat canonique de la dernière exécution suit.
* Le temps mesuré couvre la requête entière, de la première ligne décodée au résultat formaté. Il ne couvre ni le
  chargement des fichiers ni la création des fils.

## 2. Format des colonnes

Un fichier par colonne (`<table>/<colonne>.msc`), petit-boutiste, en blocs de 65 536 lignes décodables séparément.

| Position | Type | Contenu |
|---|---|---|
| 0 | 4 octets | `MSC1` |
| 4 | u32 | genre : 0 entiers, 1 chaînes en dictionnaire, 2 chaînes en clair |
| 8 | u32 | type décodé : 0 si toutes les valeurs tiennent sur 32 bits signés, 1 sinon |
| 12 | u32 | lignes par bloc : 65 536 |
| 16 | u64 | nombre de lignes |
| 24 | u64 | nombre de blocs |
| 32 | u64 | position du répertoire des blocs |
| 40 | u64 | position de la zone des valeurs |
| 48 | u64 | position de la zone annexe |
| 56 | u64 | genre 1 : entrées du dictionnaire ; genre 2 : octets des chaînes |

* **Répertoire** : 40 octets par bloc : `i64` minimum, `i64` maximum, `u64` position des valeurs du bloc dans leur
  zone, `u64` position des octets du bloc dans la zone annexe (genre 2), `u32` largeur en bits, `u32` lignes du bloc.
* **Zone des valeurs** : pour chaque bloc, ses valeurs moins son minimum, sur `largeur` bits chacune (0 à 32), mises
  bout à bout, bit de poids faible d'abord, dans des mots de 64 bits. Un groupe de 64 valeurs occupe donc `largeur`
  mots ; le dernier groupe d'un bloc est complété par des zéros. Largeur 0 : toutes les valeurs valent le minimum.
  Largeur 64 : les valeurs telles quelles, une par mot (colonnes de type 1). La zone est suivie de 8 octets nuls.
* **Genre 1** : les valeurs sont des codes ; la zone annexe porte `u32 positions[entrées + 1]`, puis les octets des
  entrées, triées.
* **Genre 2** : les valeurs sont les longueurs ; la zone annexe porte les octets des chaînes dans l'ordre des lignes,
  suivis de 8 octets nuls. La position d'une chaîne est la position des octets de son bloc plus la somme des
  longueurs qui la précèdent dans le bloc.
* **Cartes de zones** : le minimum et le maximum d'un bloc (valeurs, codes ou longueurs).
* **Unités** : clés et compteurs tels quels ; montants de TPC-H en centièmes (`l_quantity` compris : 1700 pour 17) ;
  `l_discount` et `l_tax` en centièmes (0 à 10) ; dates en jours depuis le 1er janvier 1970.

Colonnes : `lineitem` (`l_orderkey`, `l_partkey`, `l_suppkey`, `l_quantity`, `l_extendedprice`, `l_discount`, `l_tax`,
`l_returnflag` et `l_linestatus` en dictionnaire, `l_shipdate`), `orders` (`o_orderkey`, `o_custkey`, `o_orderdate`,
`o_totalprice`), `part` (`p_partkey`, `p_name` en clair), `partsupp` (`ps_partkey`, `ps_suppkey`, `ps_supplycost`),
`supplier` (`s_suppkey`, `s_nationkey`), `nation` (`n_nationkey`, `n_name` en dictionnaire), `customer` (`c_custkey`,
`c_name` en clair), `hits` (`UserID` sur 64 bits, `SearchPhrase` et `URL` en clair, `CounterID`, `EventDate`,
`DontCountHits`, `IsRefresh`).

## 3. Paramètres

| Paramètre | Valeur |
|---|---|
| Lignes d'un bloc, qui est aussi un morceau | 65 536 |
| Lignes d'un vecteur | 2 048 |
| Partitions des grandes tables | 1 024 : les 10 bits de poids fort du hachage |
| Morceau d'un tampon de partition | 16 384 octets utiles |
| Table de hachage : remplissage au plus | la moitié |
| Filtre de Bloom | 16 bits par clé au moins, deux bits par clé dans un même mot de 64 bits |
| Bloc d'arène | 32 Mio |
| Mémoire | zones alignées sur 2 Mio, en pages larges |

Mesurés sur la référence C avant le gel : 256 à 4 096 partitions (T18 gagne 12 % de 256 à 1 024, le reste ne bouge
pas) ; vecteurs de 1 024 à 4 096 lignes (aucun effet mesurable) ; pages larges (4.6).

## 4. Primitives

### 4.1 Décodage

* `unpack(colonne, bloc, début, n)` : n valeurs de 32 bits à partir de la ligne `début` du bloc (multiple de 64). Le
  décodage travaille par groupes de 64 valeurs, dont les positions dans leurs `largeur` mots sont des constantes. Une
  routine par largeur, engendrée par le mécanisme du langage (macro, générique, calcul à la compilation). Un langage
  sans tel mécanisme écrit la boucle générale : c'est un manque.
* L'écriture du corps de ces routines est libre : c'est du réglage. La référence lit un mot par valeur quand la
  largeur divise 64 et, sinon, combine toujours deux mots, le groupe étant déroulé en entier : son compilateur
  vectorise ces deux formes (de 0,1 à 0,8 ns par valeur), pas celle qui teste si la valeur chevauche deux mots
  (jusqu'à 1,6 ns).
* `unpack_sel(colonne, bloc, positions, n)` : les valeurs aux positions données (lignes dans le bloc), dans l'ordre.
  Boucle générale : la valeur de la ligne p occupe les bits `p × largeur` et suivants.
* Colonnes sur 64 bits : aucune copie, le vecteur est la zone des valeurs.

### 4.2 Hachage

Multiplications et décalages sur 64 bits non signés ; `rotl` est une rotation à gauche.

```
K1 = 0x9E3779B97F4A7C15    K2 = 0xC2B2AE3D27D4EB4F

hash64(k):            k = k * K1 ; rend k xor (k >> 32)

hash_bytes(p, n):     h1 = K1 xor n ; h2 = K2
                      tant que n >= 16 : h1 = (rotl(h1, 5) xor mot(p)) * K1
                                         h2 = (rotl(h2, 5) xor mot(p + 8)) * K2 ; p += 16 ; n -= 16
                      si n >= 8 :        h1 = (rotl(h1, 5) xor mot(p)) * K1 ; p += 8 ; n -= 8
                      si n > 0 :         h2 = (rotl(h2, 5) xor (mot(p) limité à ses n premiers octets)) * K2
                      h = (h1 xor rotl(h2, 32)) * K1 ; h = h xor (h >> 32) ; rend h, ou 1 si h vaut 0

clé (entier u, chaîne s) :  h = hash64(hash_bytes(s) xor (u * K2)) ; rend h, ou 1 si h vaut 0
```

`mot(p)` lit 8 octets petit-boutistes à partir de p, sans alignement ; le format garantit 8 octets lisibles après la
fin des chaînes. Une clé va dans la partition `h >> 54` et, dans une table de capacité c, à la case `h mod c`.

### 4.3 Table de hachage

Adressage ouvert, sondage linéaire (case suivante, modulo la capacité), capacité en puissance de deux, clé et valeur
dans la même case.

* **Clés entières** : cases de 16 octets (`i64` clé, `i64` valeur). Une case vide a la clé −1 ; les clés sont
  positives ou nulles, sauf dans C4, qui compte −1 à part.
* **Clés faites d'un entier et d'une chaîne** : cases de 32 octets (`u64` hachage, `i64` entier, `u64` position de la
  chaîne, `u32` longueur, `u32` compte). Une case vide a le hachage 0. Deux clés sont égales si le hachage, l'entier,
  la longueur et les octets le sont.
* **Capacité** : `cap(n)` est la plus petite puissance de deux qui vaut au moins 2n, et au moins 16. Une table bâtie
  d'un coup sur n clés a la capacité `cap(n)`. Une table d'agrégation qui recevra n tuples part de `cap(n / 8)`
  (division entière) et double avant l'insertion qui la remplirait à plus de la moitié ; ses cases sont alors
  replacées dans l'ordre des cases de l'ancienne table.
* **Jointure à clés répétées** : la table donne, pour une clé, le rang de son dernier tuple ; un tableau `suivant`
  chaîne les tuples de même clé.

### 4.4 Filtre de Bloom

Devant toute sonde de semi-jointure. Pour n clés : la plus petite puissance de deux de mots de 64 bits qui en donne
au moins n / 4, et au moins 64. Une clé de hachage h pose les bits `h mod 64` et `(h >> 6) mod 64` du mot
`(h >> 12) mod mots`. Un refus est sûr ; une acceptation se confirme dans la table.

### 4.5 Partitions

Chaque fil a, pour chaque partition, une liste de morceaux de 16 384 octets pris dans son arène ; un tuple va à la
suite du dernier morceau de sa partition. Quand toute la table est répartie, chaque partition est traitée par un seul
fil, qui lit ses tuples fil après fil, dans l'ordre de leurs morceaux.

### 4.6 Fils, morceaux, arènes

* Les fils sont créés une fois par processus et attendent, bloqués, entre deux phases. Le fil principal travaille
  aussi : avec un fil, tout s'exécute dans le fil principal.
* Une phase parallèle distribue des morceaux (les blocs d'une colonne, ou les partitions) par un compteur partagé :
  chaque fil prend le suivant tant qu'il en reste. C'est la seule opération atomique.
* Chaque fil garde son état (agrégats, listes, tampons de partition) ; le fil principal fusionne à la fin de la phase.
* Chaque fil a une arène : allocation par déplacement d'un pointeur dans des blocs de 32 Mio, remise à zéro au début
  de chaque exécution.
* **Pages larges.** Les colonnes sont lues en entier dans la mémoire du processus ; cette mémoire, les blocs des
  arènes et les vecteurs de travail viennent du système par zones alignées sur 2 Mio, signalées comme pages larges
  (`madvise(MADV_HUGEPAGE)` sous Linux). Mesuré sur la référence, face à des pages de 4 Kio : de 10 à 27 % de temps en
  moins à un fil sur les requêtes à partitions, jusqu'à 11 % à quatre fils ; pour les colonnes, de 19 à 29 % sur C33 à
  un fil et de 8 à 14 % sur C20 ; des temps plus réguliers d'une exécution à l'autre.

### 4.7 Sélection, recherche, dates

* **Vecteur de sélection** : les positions retenues, écrites sans branchement (`sel[k] = i ; k += condition`).
* **Cartes de zones** : un bloc que ses bornes excluent n'est pas lu ; un bloc qu'elles retiennent en entier n'évalue
  pas le filtre.
* **Sous-chaîne** (T9, C20) : les octets d'un bloc sont parcourus d'un trait, par mots de 8 octets. Une position est
  candidate si elle porte le premier octet de l'aiguille et si la position décalée de sa longueur moins un porte le
  dernier ; les candidates sont comparées à l'aiguille. Une occurrence compte si elle tient dans une ligne ; une ligne
  compte une fois, et la suite de la ligne est sautée.
* **Année d'une date** : par une table des premiers jours de chaque année depuis 1970.

## 5. Plans physiques

« Parcours » : phase parallèle sur les blocs, vecteur par vecteur. « Sonde » : filtre de Bloom, puis table.
L'arithmétique est entière et exacte.

### T1 (TPC-H Q1) — agrégation à peu de groupes, calcul d'expressions

1. Parcours de `lineitem`. Carte de zones sur `l_shipdate` (≤ 2 septembre 1998).
2. Décodage complet de `l_returnflag`, `l_linestatus`, `l_quantity`, `l_extendedprice`, `l_discount`, `l_tax` ;
   de `l_shipdate` si le bloc n'est pas retenu en entier, avec un vecteur de sélection.
3. Trois primitives sur le vecteur entier : `prix × (100 − remise)` ; ce produit `× (100 + taxe)` ; le groupe,
   `code de l_returnflag × 2 + code de l_linestatus`.
4. Agrégation dans un tableau de six cases indexé par le groupe, propre au fil : cinq sommes et un compte.

### T6 (TPC-H Q6) — filtre très sélectif

1. Parcours de `lineitem`. Carte de zones sur `l_shipdate` (année 1994).
2. `l_shipdate` décodé en entier ; sélection. Puis, aux seules positions retenues, dans cet ordre : `l_discount`
   (5 à 7) ; `l_quantity` (< 2400) ; `l_extendedprice`. Somme de `prix × remise`.

### T9 (TPC-H Q9) — jointures

1. Parcours de `part` : recherche de « green » dans `p_name` ; `p_partkey` aux lignes retenues. Table et filtre de
   Bloom des pièces, bâtis par le fil principal.
2. Parcours de `partsupp` : sonde par `ps_partkey` ; aux lignes retenues, `ps_suppkey` et `ps_supplycost`. Table
   `(pièce × 2^32 + fournisseur) → coût`, bâtie par le fil principal.
3. `supplier` : table `fournisseur → nation`, par le fil principal.
4. Parcours de `lineitem` : sonde par `l_partkey` ; aux lignes retenues, `l_suppkey`, `l_orderkey`, `l_quantity`,
   `l_extendedprice`, `l_discount` ; coût et nation par les deux tables ; montant `prix × (100 − remise) − coût ×
   quantité`. Tuples (commande, nation, montant) répartis par le hachage de la commande.
5. Parcours de `orders` : `o_orderkey` et `o_orderdate` en entier ; tuples (commande, date) répartis de même.
6. Par partition : table des tuples de `lineitem` (clés répétées), sondée par les tuples de `orders` ; pour chaque
   correspondance, agrégat `(nation × 2^16 + année) → somme` dans une table propre au fil.
7. Fusion ; nom des nations ; tri par nom, puis par année décroissante.

### T18 (TPC-H Q18) — agrégation à beaucoup de groupes

1. Parcours de `lineitem` : `l_orderkey` et `l_quantity` en entier ; tuples (commande, quantité) répartis.
2. Par partition : agrégation `commande → somme` ; les commandes dont la somme passe 30 000 sont gardées.
3. Table et filtre de ces commandes, par le fil principal.
4. Parcours de `orders` : sonde par `o_orderkey` ; aux lignes retenues, client, date, prix.
5. Table et filtre des clients ; parcours de `customer` : sonde par `c_custkey` ; position et longueur du nom.
6. Second parcours de `lineitem` : sonde par `l_orderkey` ; aux lignes retenues, quantité ; somme par commande.
7. Tri par prix décroissant, date, commande ; cent premières lignes.

### C4 — valeurs distinctes

1. Parcours de `hits` : `UserID`, réparti par son hachage.
2. Par partition : ensemble des valeurs (table à clés entières) ; somme des tailles.

### C12, C16, C33, C36 — agrégations par chaîne

1. Parcours de `hits` : longueurs de la chaîne (`SearchPhrase` pour C12 et C16, `URL` pour C33 et C36) et positions.
   Lignes retenues : C12, longueur non nulle ; C16 et C33, toutes ; C36, carte de zones sur `CounterID` (62) et sur
   `EventDate` (juillet 2013), puis `CounterID` en entier et, aux positions retenues, `EventDate`, `DontCountHits`
   (0), `IsRefresh` (0), longueur non nulle.
2. Hachage des chaînes retenues (C16 : clé faite de `UserID` et de la chaîne) ; tuples (hachage, entier, position,
   longueur) répartis.
3. Par partition : agrégation dans la table à clés de chaînes ; chaque fil garde ses dix premiers groupes.
4. Fusion des dix premiers.

### C20 — recherche de sous-chaîne

Parcours de `hits` : longueurs de `URL` ; recherche de « google » dans les octets du bloc ; compte des lignes.

### Ce que les plans ne font pas

Ils n'exploitent ni la densité des clés de TPC-H (aucun adressage direct par la clé) ni l'ordre de `lineitem` par
commande (ni agrégation en flux, ni fusion de clés consécutives). Les clés de regroupement de T1 sont des codes de
dictionnaire : leur densité est une propriété du format.

## 6. Résultats canoniques

Une ligne par ligne de résultat, champs séparés par `|`, fin de ligne `\n`, octets des chaînes tels quels.

| Requête | Champs | Ordre |
|---|---|---|
| T1 | `l_returnflag`, `l_linestatus`, somme des quantités, des prix, des `prix × (100 − remise)`, des `prix × (100 − remise) × (100 + taxe)`, des remises, compte | les deux premiers champs |
| T6 | somme des `prix × remise` | |
| T9 | nation, année, somme des montants | nation, puis année décroissante |
| T18 | nom du client, client, commande, date, prix, somme des quantités | prix décroissant, date, commande ; 100 lignes |
| C4 | nombre de valeurs distinctes | |
| C12, C33, C36 | chaîne, compte | compte décroissant, puis chaîne ; 10 lignes |
| C16 | `UserID`, chaîne, compte | compte décroissant, `UserID`, chaîne ; 10 lignes |
| C20 | nombre de lignes | |

Les chaînes se comparent octet par octet. Les résultats de référence sont dans [`expected/`](expected) : calculés par
DuckDB sous cette forme et recoupés par ClickHouse ([`tools/engines.py`](tools/engines.py)). Les moyennes de Q1 se
déduisent de ses sommes et de son compte.

## 7. Niveaux et règles

* **Portable** (`p`) : aucune vectorisation explicite ni construction propre à une famille de processeurs : ni
  intrinsèques, ni types vectoriels, ni préchargement, ni assembleur.
* **Spécialisé** (`s`) : même plan, mêmes structures, mêmes fonctions de hachage ; les primitives peuvent employer le
  SIMD explicite, le préchargement, les écritures non temporelles et les instructions de la cible. La référence C
  ([`c/olap_special.h`](c/olap_special.h), AVX-512) spécialise : le décodage (seize valeurs à la fois, par permutation
  d'octets et décalages variables) ; la sélection (compression des positions retenues) ; l'agrégation de T1 (sommes
  masquées par groupe) ; la recherche de sous-chaîne (64 positions à la fois) ; la répartition (un tampon de 64 octets
  par partition, vidé par une écriture non temporelle) ; le préchargement des cases et des octets à venir dans les
  agrégations et les jointures par partition. Une implémentation spécialise ce que son langage permet d'écrire.
* Bibliothèque standard, plus l'infrastructure tierce déclarée : allocateur, réserve de fils, fonction de hachage
  (elle doit rendre les valeurs de 4.2). Aucune bibliothèque de requêtes, de trames de données ou de noyaux
  vectoriels.
* Code sans vérification, mémoire hors tas, arènes, FFI vers le système : admis, et comptés
  ([`docs/V7.md`](../docs/V7.md), 10).

## 8. Liste de contrôle d'une implémentation

Chaque implémentation tient cette liste dans un fichier `CHECKLIST.md` de son répertoire : pour chaque ligne, « comme
la référence », ou ce que le langage empêche et ce qui est fait à la place.

| Famille | Point | Requêtes |
|---|---|---|
| Calcul d'expressions | décodage par routines spécialisées par largeur | toutes |
| Calcul d'expressions | décodage aux seules positions retenues | T6, T9, T18, C36 |
| Calcul d'expressions | arithmétique entière exacte sur 64 bits, primitives par vecteur | T1, T6, T9 |
| Calcul d'expressions | recherche de sous-chaîne par mots de 8 octets | T9, C20 |
| Localité | cartes de zones : blocs sautés, filtres évités | T1, T6, C36 |
| Localité | colonnes sur 64 bits lues sans copie ; chaînes lues en place | C4, C16, C12, C33, C36 |
| Localité | colonnes chargées, arènes et vecteurs de travail en pages larges | toutes |
| Agrégation | tableau indexé par les codes de deux petites clés | T1 |
| Agrégation | répartition puis table par partition, qui tient dans le cache | T18, C4, C12, C16, C33, C36 |
| Agrégation | cases de 16 et de 32 octets, clé et valeur ensemble | toutes sauf T1, T6, C20 |
| Jointure | filtre de Bloom devant la sonde | T9, T18 |
| Jointure | jointure par partition des deux côtés, clés répétées chaînées | T9 |
| Exécution parallèle | fils persistants, morceaux pris par un compteur atomique | toutes |
| Exécution parallèle | état par fil, fusion par le fil principal ; arène par fil | toutes |
