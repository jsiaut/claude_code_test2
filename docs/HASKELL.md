# Remarque sur Haskell : des options de compilation hors du mode annoncé, et trois noyaux à reprendre

L'auteur de l'étude m'a transmis le 3 novembre une remarque sur Haskell. Elle juge la 17e place justifiée, mais le
score (34,5) trop bas de 4 à 7 points : des options de compilation qui ne sont pas le mode « release » annoncé, deux
variantes optimisées en dessous de ce que permet GHC 9.14.1, trois cases de la matrice incohérentes avec celles des
autres langages, deux phrases du README qui attribuent au langage des effets du banc. Ce document vérifie chaque
affirmation (section 2), fixe le plan avant toute mesure (section 3), puis donne les résultats (section 4). Je n'ai
consulté aucune page web : les faits viennent de la chaîne installée (GHC 9.14.1, LLVM 18.1.3), de sondes et des
données publiées.

## 1. La remarque

1. **Ce qui est juste** : GHC 9.14.1 était la dernière version stable au 28 octobre ; le code par défaut va contre la
   machine (96 octets par particule de 64, pas de table de hachage livrée, d'où `Data.IntMap` sur K7, 33 à 39 s dont
   40 % de ramasse-miettes) ; atomiques à barrière complète (K3 écrivain unique 6 fois plus lent, D2 = ½) ; le SIMD
   large exige LLVM (C1 = ½) ; pas de vectorisation automatique (C3 = 0).
2. **Les options ne sont pas le mode annoncé.** `docs/NATURAL.md` annonce `ghc -O2 -fllvm` ; `build.sh` ajoute
   `-fno-omit-yields` et `-fno-full-laziness` à tout le programme, et `run` lance tous les noyaux avec `+RTS -N4`. Même
   code, avec et sans ces ajouts : K4 naturel non trié 79–81 → 7,8–7,9 ms (`-fno-omit-yields` empêche LLVM de
   supprimer le branchement) ; K5 naturel 390–420 → 200–210 ms (C 189) ; K9 naturel 230–250 → 112–122 ms
   (`-fno-full-laziness`) ; Q6 optimisé 33,5 → 21,8 ms (C 15,7) ; K8 naturel 147 318 → 35 `futex`, p99,9 476 → 287 µs
   (`-N`). Aucune n'est nécessaire : `-fno-omit-yields` ne sert qu'aux attentes actives de K10 (hors score),
   `-fno-full-laziness` double les `NOINLINE` et les `IORef` du harnais, et un noyau séquentiel n'a pas besoin de
   `-N4` (le guide de GHC : sans `-N`, `-N1` ; `-N` active le ramasse-miettes parallèle). Avec le générateur natif,
   K4 resterait vers 88 ms.
3. **Deux variantes optimisées en dessous de GHC 9.14.1** : K5 affirme qu'il n'y a « pas de primitive FMA vectorielle
   dans GHC 9.14 » ; `fmaddFloatX16#` existe depuis la 9.12 dans `GHC.Prim` (non réexportée par `GHC.Exts`) : 4,1 à
   4,4 ms contre 3,84 en C (1,1 fois au lieu de 1,77). L'arène de K8 range son compteur dans une `IORef` d'entier
   boxé (6,4 Go de plus par exécution, contre « aucune allocation en régime permanent ») : 300 ms au lieu de 690 à
   700 (C : 185 avec clang, 108 avec gcc).
4. **Trois cases incohérentes** : B2 = 0 (`Foreign.Marshal.Pool`, `malloc`/`free` dans `base` ; C, Julia et Fortran
   ont ½ pour « malloc et arènes à la main ») ; B3 = 0 (les n-uplets non boxés ne passent jamais par le tas ; Julia a
   ½ pour ses tuples sur la pile) ; A7 = 0 (A1 et A2 ont ½ par `Storable`, comme Java et Python en A7). Trois
   discutables : C2 (`pdep#`, `pext#`, `popCnt#`, prefetch), E7 (Template Haskell, `SPECIALISE`), F2 (`--numa`).
5. **Deux phrases du README** : « code naturel paresseux et boxé (K5 naturel en 639 ms) » (K5 est un `foldl'` sur un
   tableau non boxé ; sa lenteur vient de `-fno-omit-yields`) ; « son runtime fait 60 000 `futex` » (c'est le `-N4`).
6. **Mineurs** : l'arbre longue durée de K8 n'est pas gardé vivant (en faveur de Haskell, effet négligeable) ; Haskell
   n'est pas parmi les seize langages relus.
7. **Score** : 36,4 (options), 38,3 (+ K5 et K8), 40,3 (+ B2, B3, A7), 41,8 (+ cases discutables) ; Haskell reste
   derrière Go (45,3) sur chaque pilier. Réserve : la règle de la bibliothèque standard exclut `vector`,
   `unordered-containers` et `hashtables`, et pèse plus sur Haskell.

## 2. Vérifications (faites avant le plan)

**Machine 19.** La VM a redémarré le 3 novembre à 12 h 00 sur un hôte Emerald Rapids du même modèle que les machines
3 et 8 à 18 (modèle 207, 4 vCPU ; 3,02 à 3,18 GHz effectifs, latence à 4 Mio 55 ns, DRAM 10,6 à 12,7 Go/s :
`results/hw/machine19/`). Chaîne de l'étude : GHC 9.14.1 (`/opt/ghc`), LLVM 18.1.3. Le binaire publié se recompile à
l'identique (octet pour octet). Sondes : `tools/haskell_check/probes/` ; sorties et chiffres bruts :
`results/haskell_check/` (`probes.md`). Temps ci-dessous : médianes d'un processus.

* **Ce qui est juste (1)** : exact pour ce que je peux vérifier. La version est celle de l'inventaire (non vérifiable
  sans le web) ; 96 octets par particule (`docs/FINDINGS.md`) ; K7 naturel 50,9 s sur la machine 19 avec les options
  du banc ; atomiques : les primops `atomicReadIntArray#`, `atomicWriteIntArray#`, `fetchAddIntArray#` sont
  séquentiellement cohérentes. Le générateur natif refuse la FMA large (« sorry! … Please use -fllvm for wide vector
  FMA support ») ; `docs/FINDINGS.md` note qu'il calcule faux les autres opérations 256/512 bits.
* **(2) Options du banc** : **exact, et c'est une erreur de mon implémentation.** Même source, options du banc puis
  `-O2 -fllvm` (avec les options de la cible et le runtime multi-thread) : K4 naturel non trié 81,4 → 12,3 ms (C, même
  hôte : 1,95) ; K5 naturel 351 → 177 ms (C : 176) ; K9 naturel 200 → 110 ms ; Q6 optimisé 33,2 → 29,3 ms ; K3
  `rmw_padded` 353 → 200 à 223 ms ; les autres clés sondées changent de −11 à +18 % (un processus ; K6 `mt` et K9 `mt`
  sans écart net sur neuf répétitions) ; sommes de contrôle identiques. Effet par option : sans `-fno-omit-yields`
  seule, K4 12,3 ms et K5 176 ms ; sans `-fno-full-laziness` seule, K9 124 ms. **La règle** (`docs/NATURAL.md`) : le
  code naturel est compilé dans le mode « release » documenté de la chaîne, ce que la ligne de Haskell annonce
  (`ghc -O2 -fllvm`). `-fno-omit-yields` a été ajoutée à la première version (commit `dab7b69`) sans justification
  écrite ; K10 et K3, les seuls noyaux à boucles sans allocation sur plusieurs fils, tournent sans elle (K10 : trois
  processus de cinq répétitions, aucun blocage). `-fno-full-laziness` était justifiée (« éviter que les calculs purs
  soient partagés entre répétitions ») ; mais le harnais lit déjà chaque entrée dans une `IORef` à chaque répétition,
  et les noyaux naturels sont `NOINLINE` : sans l'option, aucun temps ne s'effondre (vérifié sur toutes les cellules à
  la validation). **`+RTS -N4` n'est pas une erreur** : c'est la convention de l'étude pour les runtimes dont le
  défaut est un seul fil (Julia est lancé avec `-t 4` pour tous les noyaux, et son ramasse-miettes marque alors avec
  quatre fils, `Threads.ngcthreads()` = 4) ; Go et Java prennent les quatre cœurs par défaut. Avec `-N4`, le runtime
  de GHC 9.14.1 active par défaut le ramasse-miettes parallèle (`-qg0`, `-qn` = `-N`, aide `+RTS -?`). Le README doit
  le dire : « réglages des runtimes par défaut », sauf le nombre de fils. **Sensibilité** (`-N1` pour les noyaux
  séquentiels).
* **(3a) K5 optimisé** : **exact, et c'est une erreur de mon implémentation.** `fmaddFloatX16#` est dans `GHC.Prim`
  (et `GHC.Internal.Prim`), absente de `GHC.Exts` (`:browse`) ; la sonde calcule 2 × 3 + 1 = 7. Avec elle : 6,16 →
  4,59 ms (C, même hôte : 3,73). **La convention** : toutes les autres implémentations à SIMD explicite écrivent K5
  (et K1 soa) avec une FMA vectorielle (C, Zig, Odin, C3, Nim, Ada, Mojo, C#…) ; mon commentaire affirmait un fait
  faux pour s'en dispenser. La même prémisse touche K1 soa, que la remarque ne cite pas : corrigé aussi.
* **(3b) K8 optimisé** : **exact, et c'est une erreur de mon implémentation** (la spécification exige « aucune
  allocation en régime permanent »). Mesuré par `+RTS -s` : 1,63 Go alloués par répétition (49 octets par nœud).
  L'`IORef` en compte 1,35 Go ; le reste vient du compteur de valeurs, rendu dans un n-uplet et boxé à chaque feuille
  (`I# (+# ww5 1#)` dans le Core). Les deux compteurs en mémoire brute, comme les pointeurs du C : 13 Mo par
  répétition (les latences du harnais), 0,80 → 0,21 s.
* **(4) Cases** : **B2, B3 et A7 : exact, errata de la matrice.** Sondes (`Caps.hs`, `base` seul) : `withPool` et
  `pooledMallocArray` libèrent une région d'un bloc (B2 ; le K8 optimisé est une arène à la main, comme en C, Julia,
  Fortran, Nim et Mojo, notés ½) ; un million d'appels d'une fonction `NOINLINE` qui rend un n-uplet non boxé
  n'allouent rien (B3 ; le type le garantit, comme les tuples isbits de Julia, notés ½, et contrairement au
  remplacement scalaire de Java, noté 0) ; un enregistrement `Storable` de 72 octets porte 16 flottants en ligne et se
  range à plat dans un tableau (A7 ; même mécanisme que A1 et A2, notés ½ ; Java et Python ont ½ en A7). **C2, E7,
  F2 : discutables, gardés.** Les primops `pdep#`, `pext#`, `popCnt#` sont génériques (repli portable), comme
  `Long.compress`/`expand` de Java, noté 0 ; `--numa` est un réglage du runtime, comme `-XX:+UseNUMA` de Java, noté 0
  (la remarque sur Java l'a rangé parmi les cases discutables) ; E7 = ½ : Template Haskell calcule à la compilation,
  mais la spécialisation reste à la demande (`SPECIALISE`). **Sensibilité** (C2 = ½, E7 = 1, F2 = ½).
* **(5) README** : **exact.** K5 naturel compile en boucle stricte non boxée (`plusFloat#`, `timesFloat#`, avec la
  vérification des bornes, Core de `$wk5Natural`) ; 639 ms est le chiffre de la v1 (Cascade Lake) ; le temps publié
  vient de la machine 3 (350 ms). Sous `strace`, K8 naturel fait 87 414 `futex` avec `-N4` et 25 avec `-N1` (une
  répétition et la construction de l'arbre long).
* **(6) L'arbre longue durée** : **exact, erreur de mon implémentation** (la spécification : « Il reste vivant
  jusqu'à la fin »). `lsum` est calculé avant la boucle, et l'arbre meurt ensuite ; C le libère après la boucle, Go,
  Java, C#, D et Julia le gardent dans une globale, OCaml par `Sys.opaque_identity`, JavaScript en le relisant.
  Gardé vivant (`touch#` après la boucle) : temps de K8 naturel inchangé (1,69 à 1,87 s contre 1,72 à 1,79), deux
  fois moins de collections majeures mais plus longues (maximum des pauses 32 ms contre 9) ; or D3 lit le p99,9 et le
  maximum des latences de K8 naturel. Haskell n'est pas parmi les seize langages relus : **exact**.
* **(7) Score** : à mesurer (section 4). La réserve de méthode est exacte : la règle de la bibliothèque standard est
  dans les limites du README, sans dire qu'elle pèse plus sur Haskell.

## 3. Plan (poussé avant les mesures)

### 3.1 Règle commune et application

`docs/FORTRAN.md`, 3.1 (« un code qui ne fait pas ce qu'il annonce ou qui s'écarte d'une convention que les autres
implémentations suivent » est une erreur ; une meilleure forme est une optimisation nouvelle). Erreurs : (2) les
options hors du mode release annoncé ; (3a) K5 et K1 soa sans FMA vectorielle ; (3b) l'arène de K8 qui alloue ;
(6) l'arbre longue durée de K8 ; (4) errata B2, B3, A7 ; (5) le texte du README. Sensibilités : `-N1` pour les noyaux
séquentiels, les cases C2, E7 et F2.

### 3.2 Ce qui entre dans le classement publié

* **H-E** : chaque clé de Haskell × r(`haskell_fix` / `haskell_ref`), **par transfert** (temps publié × rapport du
  même hôte). **Écart à la pratique des remarques précédentes**, décidé avant les mesures : la règle du pont
  (`analysis/transfer_check.py` : le C du même hôte remplace le transfert au-delà de 25 % d'écart) a été calibrée sur
  des clés corrigées une à une et des témoins mesurés sur le même modèle d'hôte (Ada et Fortran, Cascade Lake). Ici la
  correction touche les 36 clés, dont 31 sont publiées depuis un autre modèle d'hôte (Cascade Lake ; K5 et K9 viennent
  des machines 3 et 16, du même modèle que la machine 19), et le rapport de Haskell à C d'un même binaire change d'un
  modèle à l'autre : K4 naturel, binaire publié, 18 fois C sur Cascade Lake (73,4 contre 4,04 ms), 42 fois sur la
  machine 19 (81,4 contre 1,95 ms), parce que la boucle vectorisée de C gagne plus à changer d'hôte que la boucle
  scalaire de Haskell. Le pont importerait cet écart d'hôte comme une correction, y compris sur des clés que les
  options ne changent pas ; le transfert suppose seulement que le rapport entre deux versions de Haskell se conserve.
  Le pont est calculé en information (scénario H-E-P, avec une **règle de sens** : le facteur retenu ne va pas contre
  le rapport mesuré sur le même hôte, plafonné à 1 si r < 1 et au moins 1 si r > 1, généralisation du plafond adopté
  pour Java, `docs/JAVA.md`, 4).
* **Latences de K8 naturel (D3)** : les lignes publiées (machine 11) × le rapport, sur le même hôte, des médianes de
  p50, p90, p99, p99,9 et du maximum (`haskell_fix` / `haskell_ref`), par transfert seul : un pont par le C n'a pas de
  sens pour des queues dominées par les pauses du ramasse-miettes.
* **Matrice** : B2 = B3 = A7 = ½ (`analysis/capabilities.py`).
* **Réplication (machine 3)** : chaque clé de Haskell × r(`haskell_fix` / `haskell_ref`), latences de K8 naturel ×
  les rapports de latence (transfert, même modèle de processeur).
* **Mise en œuvre** : les rapports des clés hors K9 vont dans `results/transfers.json` (« ratios ») ; ceux de K9,
  appliqués après le remplacement de K9 par la machine 16, dans « ratios_k9h » ; ceux des latences dans une clé
  nouvelle « lat_ratios », lue après le remplacement des latences par la machine 11 (`apply_lat_ratios`,
  `analysis/analyze_v2.py`) ; ceux de la réplication dans `results/haskell_check.json` (« replication_ratios »,
  « replication_lat_ratios »), lus par `m3_ratios` et `m3_lat_ratios`. Ces points d'accroche sont poussés avant
  les résultats.
* **Texte du README** : tableau, paragraphe de Haskell (K5 naturel, `futex`), règles de construit (nombre de fils),
  langages relus, réserve sur la bibliothèque standard.

### 3.3 Copies (`tools/haskell_check/make_copies.py`)

* `haskell_ref` : copie exacte de `bench/haskell_k9h` (le code publié avec le harnais commun de K9), mêmes options,
  `+RTS -N4` ; binaire identique au binaire publié.
* `haskell_rel` : le même source, options `-O2 -fllvm -mavx512f -mfma -mbmi2 -threaded -rtsopts` (le mode annoncé,
  les options de la cible, le runtime multi-thread), `+RTS -N4`.
* `haskell_fix` : les options de `haskell_rel` et quatre corrections du code : (a) K5 tuned avec `fmaddFloatX16#` ;
  (b) K1 soa avec la même FMA ; (c) les deux compteurs de l'arène de K8 en mémoire brute ; (d) l'arbre longue durée
  gardé vivant (`touch#`). `+RTS -N4`.
* `haskell_n1` : le binaire de `haskell_fix` lancé avec `+RTS -N1` (sensibilité).
* Validation (`tools/haskell_check/validate.py`) : sommes de contrôle de toutes les cellules Haskell de la campagne
  (82 cellules, un processus : aucun échec ; aucun temps effondré sans `-fno-full-laziness`, rapports `fix` / `ref` de
  0,17 à 1,30 sur un processus).

### 3.4 Mesures (`tools/measure_haskell.py`, machine 19)

118 cellules en 7 passes (820 processus) ; dans chaque passe, toutes les cellules dans un ordre tiré au hasard (graine
20261603) : `haskell_ref` et `haskell_fix` sur les 36 clés de Haskell ; `haskell_rel` sur les 4 clés dont le code
change (K1 soa, K5 tuned, K8 natural et tuned) ; `haskell_n1` sur K1 naturel et mélangé, K4 naturel non trié, K5,
K8 et K9 naturels ; `c` (binaire de la campagne) sur les 36 clés. K7 naturel (environ 50 s par répétition) n'est
mesuré, pour `haskell_ref` et `haskell_fix`, que dans les passes 1 à 4 ; il n'entre pas dans `haskell_n1` (sonde : 50,8
s avec `-N4`, 51,3 s avec `-N1`, facteur 1). Répétitions de `results/calib.json` ; échauffements de la campagne (2
pour K5, 1 sinon) ; règle de vol du pilote. Rien d'autre ne tourne. Sortie : `results/raw_haskell/`. Durée estimée
d'après la validation : 70 minutes.

### 3.5 Scénarios (`analysis/haskell_check.py`, analyse globale de la v3 rejouée, mêmes tirages)

| Scénario | Contenu |
|---|---|
| Avant | classement publié d'avant ; doit reproduire `results/go_check.json` (G-E) à l'identique |
| H-opt | options seules : r(`haskell_rel` / `haskell_ref`) pour les 4 clés dont le code change, r(`haskell_fix` / `haskell_ref`) pour les autres ; latences r(`haskell_rel` / `haskell_ref`) |
| H-code | options et code : toutes les clés et les latences × r(`haskell_fix` / `haskell_ref`), matrice inchangée |
| H-M | errata de la matrice seuls |
| **H-E (publié)** | tout : H-code et les errata |
| H-E-P | H-E, chaque clé reportée par la règle du pont et la règle de sens (information) |
| S-N1 | H-E ; les 6 clés de `haskell_n1` × r(`haskell_n1` / `haskell_fix`), latences de K8 naturel × r(`haskell_n1` / `haskell_fix`) |
| S-cases | H-E ; C2 = ½, E7 = 1, F2 = ½ |
| S-tout | S-N1 et S-cases |

Rapports : moyenne géométrique des médianes de processus, intervalle par bootstrap ; latences : médianes de toutes
les répétitions (l'estimateur de D3) ; tous les reports par transfert, sauf H-E-P ; sensibilités en min(1, r) par
rapport à H-E (latences comprises). Sorties :
`results/haskell_check.json`, `results/report_haskell.md` ; puis régénération des sorties publiées (la réplication
comprise) et de l'état actuel.

### 3.6 Ce que je ne fais pas

* Pas de mesure sur Cascade Lake (aucun hôte disponible) : les clés qui en viennent sont corrigées par report.
* Pas de changement de `+RTS -N4` dans les données publiées (convention de l'étude) ; `-N1` reste une sensibilité.
* Pas de K10 (hors score) ni de remesure de l'empreinte (D2, la structure ne change pas).
* Pas de bibliothèque hors de GHC (`vector`, `primitive`, `unordered-containers`) : la règle vaut pour tous.

## 4. Résultats (après les mesures)

Mesures du 3 novembre, de 12:33:31 à 13:42:59, sur la machine 19 : 820 processus (118 cellules, 7 processus chacune,
4 pour K7 naturel de `haskell_ref` et `haskell_fix`), aucune somme de contrôle fausse ; 39 refaits pour vol de temps
(quatre deux fois), aucun gardé au-dessus de 2 % (vol médian 0,58 %). Aucun écart au plan. Le scénario Avant reproduit
le classement publié d'avant à l'identique (écart 0). Rapports : `results/report_haskell.md` ; temps : moyenne
géométrique des médianes de processus, intervalle à 95 % par bootstrap.

### 4.1 Les options (même hôte)

`haskell_fix` / `haskell_ref` pour les 32 clés dont le code ne change pas, `haskell_rel` / `haskell_ref` pour les
quatre autres :

| Clé | Options du banc (ms) | Mode release (ms) | Rapport [IC 95 %] | C, même hôte (ms) |
|---|---|---|---|---|
| K4 naturel non trié | 73,4 | 11,2 | 0,153 [0,148–0,159] | 1,97 |
| K5 naturel | 346,5 | 187,5 | 0,541 [0,515–0,574] | 168,3 |
| K9 naturel | 207,8 | 125,5 | 0,604 [0,569–0,651] | 14,1 |
| K7 tuned | 251,4 | 195,6 | 0,778 [0,729–0,834] | 198,8 |
| Q6 tuned | 36,5 | 31,2 | 0,854 [0,813–0,897] | 18,2 |
| Q6 `mt` | 15,0 | 12,6 | 0,840 [0,737–0,943] | 5,8 |
| K3 `rmw_padded` | 342,9 | 234,7 | 0,684 [0,624–0,776] | 218,4 |
| K3 `sw_packed` | 7 374 | 6 092 | 0,826 [0,784–0,874] | 12,5 |
| K3 `sw_padded` | 358,8 | 419,8 | 1,170 [1,003–1,429] | 12,4 |
| K3 `rmw_packed` | 4 118 | 4 601 | 1,117 [1,056–1,173] | 4 327 |
| K4 naturel trié | 10,3 | 11,6 | 1,126 [1,028–1,229] | 1,73 |
| Q6 naturel | 48,6 | 51,1 | 1,052 [1,019–1,091] | 51,1 |

Les 21 autres clés vont de 0,94 à 1,05 (K1, K2, Q1, K7 et K8 naturels, K9 tuned et `mt`), dont une seule hors de
l'intervalle de 1 (K2 à 16 Kio, 1,051). Le gain vient des boucles serrées : le désassemblage de l'IR de LLVM
(`results/haskell_check/llvm_k4_ref.txt`, `llvm_k4_rel.txt`) montre qu'avec `-fno-omit-yields` l'en-tête de la boucle
de K4 devient un bloc à part, qui teste `HpLim` (`Base[107]`) : chaque itération range son état sur la pile Haskell
et y revient par un appel terminal, si bien que LLVM ne peut ni garder la boucle dans les registres ni changer le
branchement en déplacement conditionnel (sur des octets aléatoires, il est mal prédit une fois sur deux). Sans
l'option, la boucle reste locale à une fonction. K5 naturel paie de même le passage de son accumulateur par la
mémoire ; il va désormais à 1,11 fois C sur cet hôte. K3 bouge dans les deux sens (0,68 à 1,17), comme le placement
du code le fait déjà sur cet hôte (`docs/FINDINGS.md`, une même boucle à 1 ou 7 cycles par incrément) : le transfert
reporte ces écarts tels quels, comme prévu.

### 4.2 Les corrections du code (`haskell_fix` / `haskell_rel`, même hôte)

* **K5 tuned (FMA vectorielle)** : 5,97 → 4,60 ms (× 0,770), 1,04 fois C (4,43 ms) ; avec les options, × 0,745 sur
  le binaire publié. Temps publié reporté : 6,35 → 4,73 ms (C : 3,94).
* **K1 soa (même FMA)** : 4,74 → 4,35 ms (× 0,917) ; avec les options, × 0,981 [0,78–1,24], dans le bruit : le noyau
  est limité par la mémoire.
* **K8 tuned (arène sans allocation)** : 719 → 214 ms (× 0,297) ; le C de clang fait 252 ms sur cet hôte. Temps
  publié reporté : 1 189 → 351 ms (C : 266).
* **K8 naturel (arbre longue durée gardé vivant)** : 1 639 → 1 690 ms (× 1,031) ; avec les options, × 1,027
  [1,002–1,055]. Comme prévu, la correction joue contre Haskell, de 3 %.

### 4.3 Latences de K8 naturel (D3)

Médianes de toutes les répétitions (µs), même hôte :

| | p50 | p90 | p99 | p99,9 | max |
|---|---|---|---|---|---|
| Options du banc (`haskell_ref`) | 57 | 253 | 505 | 1 729 | 6 002 |
| Mode release (`haskell_rel`) | 59 | 251 | 485 | 1 427 | 5 930 |
| Corrigé (`haskell_fix`) | 61 | 256 | 484 | 1 383 | 6 684 |
| Rapport `fix` / `ref` [IC 95 %] | 1,061 [1,05–1,11] | 1,010 [0,95–1,07] | 0,960 [0,89–1,05] | 0,800 [0,60–1,08] | 1,114 [0,70–1,38] |
| `-N1` (`haskell_n1`) | 60 | 97 | 147 | 404 | 3 550 |

Les options abaissent le p99,9 (× 0,825 [0,68–0,95]) ; l'arbre gardé vivant relève le maximum (pauses majeures plus
longues), dans un intervalle large. Les lignes publiées (machine 11) sont multipliées par la ligne `fix` / `ref`.

### 4.4 Sensibilités

* **S-N1** (`+RTS -N1` pour les noyaux séquentiels) : K8 naturel × 0,692 (1 690 → 1 170 ms), ses latences × 0,38
  (p90), 0,30 (p99), 0,29 (p99,9) et 0,53 (max) : le ramasse-miettes parallèle coûte cher à un noyau qui n'a qu'un fil.
  K9 naturel × 0,915, K1 naturel × 0,957 ; K1 mélangé, K4 et K5 naturels sans gain (0,995 à 1,046, comptés 1).
* **S-cases** : C2 = ½, E7 = 1, F2 = ½.
* **H-E-P** (information) : la règle du pont retiendrait le C du même hôte pour 11 clés sur 36, avec des facteurs de
  0,19 (K8 tuned) à 7,3 (K7 naturel : 89 s → 639 s, parce que le K7 naturel du C va 12 fois plus vite sur la
  machine 19 qu'à Cascade Lake, 433 contre 5 107 ms) ; la règle de sens en ramène trois à 1 (K1 mélangé, K4 sans
  branchement, K3 `sw_packed`), pas K4 trié (× 2,7) ni K3 `sw_padded` (× 6,1), dont le rapport mesuré dépasse 1.
  C'est l'écart d'hôte que le plan voulait éviter (3.2) ; le score qui en sort (42,9) dépasse celui du transfert,
  parce que le pont corrige davantage le plafond (K8, Q6 et K7 optimisés) qu'il ne pénalise le code par défaut.

### 4.5 Classement (analyse globale de la v3 rejouée, 20 000 variantes)

| Scénario | Score | Contrôle | Plafond | Défaut | Rang espéré | Place | Go devant | Devant OCaml |
|---|---|---|---|---|---|---|---|---|
| Avant (publié d'avant) | 34,47 | 34,4 | 34,6 | 34,4 | 17,01 | 17 | 100 % | 98 % |
| H-opt (options) | 36,08 | 34,4 | 38,0 | 35,4 | 16,98 | 17 | 100 % | 99 % |
| H-code (options et code) | 39,33 | 34,4 | 46,2 | 35,2 | 16,92 | 17 | 97 % | 99 % |
| H-M (errata seuls) | 36,42 | 39,9 | 34,6 | 34,4 | 16,98 | 17 | 100 % | 99 % |
| **H-E (publié)** | **41,28** | 39,9 | 46,2 | 35,2 | 16,82 | 17 | 93 % | 100 % |
| H-E-P (pont, information) | 42,88 | 39,9 | 50,8 | 34,4 | 16,64 | 17 | 83 % | 99 % |
| S-N1 | 42,11 | 39,9 | 46,2 | 38,6 | 16,62 | 17 | 86 % | 100 % |
| S-cases | 42,84 | 44,4 | 46,2 | 35,2 | 16,66 | 17 | 85 % | 100 % |
| S-tout | 43,67 | 44,4 | 46,2 | 38,6 | 16,41 | 17 | 73 % | 100 % |

« Go devant » : part des variantes où Go devance Haskell. Au classement publié (H-E), Haskell gagne 6,8 points et
reste 17e, rang plausible 16 à 17 ; aucun autre langage ne change de place (Go 45,37, Java 47,18, C# 54,88). Le
plafond de Haskell (46,2) dépasse désormais celui de Go (44,5), grâce à K5 (0,62 → 0,83 de la référence), K7 (0,63 →
0,81), K8 (0,09 → 0,31) et K3 (0,21 → 0,30) ; son contrôle (39,9 contre 48,7) et son code par défaut (35,2 contre
42,2) restent derrière.

Effet sur les autres langages : leurs scores bougent de +0,004 à +0,026 point, sans changement de place. Le K3
`rmw_padded` corrigé de Haskell (192,6 ms) devient le meilleur temps de sa clé, devant Nim (204,1), et K2 à 8 Mio
(593,8 contre 595,3) : les références communes bougent un peu. Sans SIMD explicite, à la lettre, Go passe ainsi
devant Java (rang moyen 15,13 contre 15,17, `docs/NOSIMD.md`, 4.13) ; dans la confrontation, D repasse devant Nim dans
le scénario B (`docs/CONFRONTATION.md`).

### 4.6 Réplication (machine 3)

Données de Haskell de la machine 3 multipliées par les rapports `haskell_fix` / `haskell_ref` (transfert, même modèle
de processeur), latences de K8 naturel comprises : score 29,2 → 34,7, toujours 17e ; code par défaut 0,026 → 0,039,
plafond 25,3 → 33,8. L'ordre de la réplication ne change pas.

### 4.7 Bilan

* **La remarque est juste sur l'essentiel.** Les options du banc sortaient tout le programme du mode release annoncé,
  et `-fno-omit-yields` découpe les boucles serrées (vérifié dans l'IR de LLVM) ; K5 se passait d'une FMA vectorielle
  que GHC 9.14.1 livre ; l'arène de K8 allouait à chaque nœud ; trois cases de la matrice étaient incohérentes avec
  celles des autres langages ; les deux phrases du README attribuaient au langage des effets du banc. S'y ajoutent
  K1 soa (même FMA) et l'arbre longue durée de K8, gardé vivant contre Haskell. Le score passe de 34,47 à 41,28
  points (+ 6,8), en haut de la fourchette de 4 à 7 points de la remarque ; Haskell reste 17e.
* **Les estimations de la remarque** (36,4 avec les options, 38,3 avec K5 et K8, 40,3 avec les errata, 41,8 avec les
  cases discutables) sont proches des miennes (36,1, 39,3, 41,3, 42,8), un peu en dessous à partir du code.
* **Une affirmation ne tient pas** : corrigé, le plafond de Haskell (46,2) dépasse celui de Go (44,5). Son contrôle
  (39,9 contre 48,7) et son code par défaut (35,2 contre 42,2) restent derrière, et Go devance Haskell dans 93 % des
  variantes, mais pas dans toutes : « aucune pondération ne le fait passer 16e » est faux pour 7 % des variantes, 27 %
  avec `-N1` et les cases discutables.
* **Ce que je retiens autrement** : `+RTS -N4` suit la convention de l'étude (Julia est lancé avec `-t 4`) et reste
  dans le classement publié ; le gain de `-N1` (K8 naturel 1,4 fois plus rapide, p99,9 3,4 fois plus bas) est une
  sensibilité. Le report se fait par transfert, sans le pont par le C, écart décidé avant les mesures : le pont aurait
  importé des facteurs de 0,19 à 7,3 venus de l'écart entre hôtes.
* **Réserve de méthode** : exacte ; la règle de la bibliothèque standard est désormais signalée comme pesant aussi sur
  Haskell dans les limites du README.
