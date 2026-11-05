# Remarque sur Lua : une partie hachée dans K3, des octets décodés dans la boucle de K4, un masque qui branche, des nœuds positionnels, deux cases de la grille, et LuaJIT

L'auteur de l'étude m'a transmis le 5 novembre une remarque sur Lua, le seul langage que personne n'avait relu. Elle
juge la place justifiée (PUC-Lua 5.5, avec sa seule bibliothèque standard, mérite le dernier étage) mais l'explication
du README à moitié juste : sur les deux piliers mesurés, Lua fait mieux que CPython, et seul le pilier jugé le met
derrière Python. Elle relève six défauts du banc, deux retouches, un point en sens inverse, trois cases discutables et
une sensibilité absente, LuaJIT. Ce document vérifie chaque affirmation (section 2), fixe le plan avant toute mesure
(section 3), puis donne les résultats (section 4). Je n'ai consulté aucune page web : les faits viennent des
interpréteurs de l'étude (PUC-Lua 5.5.1, LuaJIT 2.1.1792588164 et sa documentation, livrée avec ses sources), de
sondes, du bytecode et des données publiées.

## 1. La remarque

1. **Le fond** : PUC-Lua 5.5, avec sa seule bibliothèque standard, est bien au dernier étage, et rien ne le fait
   remonter. Mais sur les deux piliers mesurés, Lua fait environ deux fois mieux que CPython ; seul le pilier jugé le
   met derrière Python. Lua est aussi le seul langage que personne n'a relu.
2. **Ce que le README dit juste** : la 5.5.1 est la dernière version (5.5.0 sortie le 22 décembre 2025, 5.5.1 le
   3 août 2026) ; la 5.5 apporte des tableaux plus compacts (9 octets par case au lieu de 16), `table.create`, les
   réglages du ramasse-miettes par `collectgarbage("param", …)` et des collectes majeures incrémentales ; les 449
   octets par particule sont exacts à l'octet (48 pour la `Table`, 8 pour `lastfree`, 16 nœuds de 24 octets, 9 pour
   la case du tableau qui la contient) ; ni threads, ni SIMD, ni types valeur ; `os.clock` mesure du temps CPU par
   un appel système ; le code compilé de LuaJIT ignore `volatile`.
3. **Pourquoi Lua est 21e** : contrôle 2,8 contre 29,7 pour Python, plafond 1,08 contre 0,59, code par défaut 10,0
   contre 4,9 ; score 3,9 contre 11,8. L'écart de 7,9 points vient du contrôle (Python y gagne 9,4 points, Lua en
   reprend 1,5 sur les mesures). Les étages par quantité mettent Lua devant Python sur le plafond comme sur le code
   naturel ; Python ne repasse devant que si le contrôle pèse plus de 8 % du score, et il n'est devant que dans 72 %
   des variantes. Le contrôle de Python tient à `ctypes`, `mmap`, `array`/`memoryview` et aux sous-interpréteurs ;
   Lua confie le bas niveau au C par son API, que la règle exclut à juste titre : le 21e rang dit vrai sur « Lua sans
   C », l'ordre entre Lua et Python ne mesure pas la performance.
4. **Six défauts du banc**, mesurés sur Lua 5.4.6 : K4, `string.byte` appelé à chaque octet (un appel C, 62 ns par
   octet) : 8 octets par appel ou une table d'octets comme dans K6, × 3,4 ; Q6 tuned et `mt`, `and 1 or 0` branche
   dans le bytecode et évalue tous les prédicats (2,6 fois plus lent que le naturel) : date lue une fois, tests
   imbriqués, × 2,2 sur `mt` ; K9 tuned et `mt`, le calcul d'indices du tableau plat (1,6 fois le naturel) : un seul
   indice, voisins glissants, × 1,3 sur `mt` ; K3 `padded`, `c = {}` puis les indices 17, 33 et 49 rangent trois
   compteurs dans la partie hachée, d'où le « faux partage × 0,63 » sans fils : `table.create(64)` ou une table
   préremplie, × 1,45 ; K7 tuned, deux tables donc deux recherches par ligne : une table, compte et somme tassés dans
   un entier, × 1,2 ; K8 tuned, arène récursive : itérative comme `c_k8it`, × 1,2. Deux retouches : le 0,5 sorti de
   la boucle de K1 `soa` (× 1,16), les indices de K2 décalés au chargement (× 1,12). Plafond 1,08 → 1,47, score
   3,9 → 4,2. **En sens inverse** : le K8 naturel range ses nœuds en `{v, false, false}`, quand le K1 naturel utilise
   des champs nommés ; à champs nommés, K8 naturel est 1,85 fois plus lent.
5. **La grille, juste à trois cases près** : B4 = 0 (« allocations omniprésentes ») est l'erratum le plus net,
   l'arithmétique n'allouant jamais (nombres non boxés) : les allocations cachées sont `..`, les fermetures et la
   croissance des tables, la liste qui vaut ½ à D ; B3 = 0, alors que retours multiples et varargs passent par la
   pile de la VM, jamais par le tas, le motif de l'erratum de Haskell (n-uplets non boxés, ½) ; A8 = 0, alors que
   `string.pack` stocke `i1`, `i2`, `i4` et `f`, en lecture seule : un ½ « limité » se défend. Avec les trois à ½,
   contrôle 2,8 → 8,4, score environ 6,1, banc corrigé compris ; Lua reste 21e. La sonde de Lua ne teste que A5 et F3.
6. **La sensibilité absente, LuaJIT** : classer PUC-Lua est cohérent avec CPython plutôt que PyPy, mais LuaJIT est
   mesuré, et c'est ce qu'on prend quand on cherche la performance en Lua ; le README devrait en donner l'effet, comme
   pour Zig en développement ou le K4 de clang++. LuaJIT ne publie plus de versions (branche v2.1 numérotée par
   l'horodatage de son dernier commit). Avec les données publiées, il va 5 à 46 fois plus vite noyau par noyau, sauf
   K8 (× 1,3) ; plafond 10,7 à 14,3 (son K3 n'est pas conforme), code par défaut 18,0 ; score 9,8 à 11,2 avec la
   grille de Lua, au niveau de Python, et 14,9 à 16,4 si sa FFI est notée comme `ctypes` et `node:ffi` (contrôle
   d'environ 17,6), au niveau de JavaScript.
7. **Le README** : paragraphe proposé : « PUC-Lua 5.5, sans son API C. Un plafond et un code par défaut environ deux
   fois meilleurs que ceux de CPython, mais presque aucun levier dans la bibliothèque standard : ni threads, ni SIMD,
   ni types valeur, ni mémoire brute ; une particule coûte 449 octets. Seul le contrôle le place derrière Python.
   LuaJIT, mesuré à part, le mettrait au niveau de Python ou de JavaScript selon la notation de sa FFI. » Retirer Lua
   de la liste des langages jamais relus.
8. **Limites de sa vérification** : mesures sur Lua 5.4.6 (la compilation de la 5.5.1 a été bloquée dans son bac à
   sable), sur un Xeon à 2,1 GHz au L3 de 260 Mio ; sur Q6, K9 et K3, ses écarts (× 2,1, × 1,6, × 1,45) concordent avec
   ceux des données publiées (× 2,6, × 1,6, × 1,6).

## 2. Vérifications (faites avant le plan)

**Machine 23.** La VM a redémarré le 5 novembre à 12 h 23 sur un hôte Cascade Lake du même modèle que celui des
données principales (modèle 85, 4 vCPU, un fil par cœur ; 3,04 à 3,22 GHz effectifs ; latence 25 ns jusqu'à 2 Mio
mais 137 ns dès 4 Mio, la VM n'ayant qu'une part du L3, et 230 ns à 1 Gio ; DRAM 11,7 Go/s à 1 Gio :
`results/hw/machine23/`). Interpréteurs : PUC-Lua 5.5.1 (`/opt/lua55`), LuaJIT 2.1.1792588164 (commit du 21 octobre
2026, sources et documentation dans `/opt/dl/luajit`), CPython 3.15.2 ; les 24 fichiers d'entrée correspondent à
`env/msdata.sha256`. Sondes : `tools/lua_check/probes/`, sorties dans `results/lua_check/`. Temps ci-dessous : un
processus (validation des copies, `validate.txt`).

* **(2) Version et nouveautés** : **exact pour ce qui se vérifie.** `lua -v` donne 5.5.1 ; `table.create` existe ;
  `collectgarbage("param", "pause")` répond 250 ; une case de tableau de flottants coûte 9,00 octets (sonde
  `facts.lua`). Le mode par défaut du ramasse-miettes est générationnel (`collectgarbage("incremental")` rend
  « generational »). Les dates de sortie ne se vérifient pas ici.
* **(2) 449 octets** : **exact.** Sonde : une table vide coûte 48 octets, une particule à 16 champs nommés 440
  (48 + 8 + 16 × 24), sa case dans le tableau 9 : 449.
* **(3) Décomposition** : **exact.** Classement publié (`results/python_check.json`, P-E) : Lua 3,92 = 0,35 × 2,8 +
  0,40 × 1,08 + 0,25 × 10,0 ; Python 11,83 = 0,35 × 29,7 + 0,40 × 0,59 + 0,25 × 4,9. Avec plafond et code par défaut
  dans leur rapport de 40 à 25, Python ne passe devant Lua qu'au-dessus d'un poids de 7,8 % pour le contrôle. Les
  étages par quantité (`results/report_v3.md`) placent Lua devant Python sur le plafond et sur le code naturel.
* **(4) K4** : **exact, et c'est une erreur de mon implémentation.** Données publiées : 1,04 s pour 16,8 millions
  d'octets, 62 ns par octet. Tous les autres noyaux de Lua décodent leurs fichiers en tables hors chrono (`load`,
  `bytes` : « décode un fichier binaire en table Lua (hors chrono) ») ; K4 seul garde la chaîne et décode chaque
  octet dans la boucle chronométrée, par un appel à `string.byte`. Les autres implémentations indexent un tableau
  d'octets. Corrigé avec la table d'octets de K6 : × 0,35 (naturel non trié), × 0,26 (trié), × 0,32 (sans
  branchement).
* **(4) Q6 tuned et `mt`** : **exact, et c'est une erreur de mon implémentation**, par la règle appliquée au Q6
  d'OCaml (`docs/OCAML.md`, 2a). Le code annonce un masque (il multiplie la contribution par `m`), mais
  `cond and 1 or 0` compile en comparaison suivie de sauts conditionnels : par prédicat, `LT`, `JMP`, `LOADI`, `TEST`,
  `JMP` (`luac -l`, `q6_bytecode.txt`). Les autres implémentations qui multiplient par un masque le calculent sans
  branchement. Lua n'a pas de comparaison sans saut, mais le bit de signe d'une différence, décalé de 63 bits
  (décalage logique), donne le masque : plus aucun saut dans le bytecode, même somme ; × 0,80 (`mt`, qui appelle la
  même fonction en quatre morceaux, × 0,68). La forme de la remarque, des tests imbriqués qui lisent la date une
  fois, abandonne le masque : forme nouvelle, **sensibilité** (× 0,45 et × 0,53 par rapport au code corrigé ; elle
  rejoint le naturel).
* **(4) K9 tuned et `mt`** : **exact sur le coût, pas une erreur.** Données publiées : 1,30 s contre 0,82 en naturel.
  La spécification demande pour tuned un « tableau plat contigu », et le code prend des décalages de lignes, comme
  Java et JavaScript. Un seul indice et des voisins glissants : forme nouvelle, **sensibilité**, comme les voisins
  gardés en variables de JavaScript (S-K9v). Sur la 5.5.1, elle ne gagne rien (× 1,05 et × 1,00).
* **(4) K3 `padded`** : **exact, et c'est une erreur de mon implémentation.** Avec `c = {}`, la partie tableau ne
  grandit que si plus de la moitié de ses cases sont prises : les indices 17, 33 et 49 vont dans la partie hachée. Le
  « faux partage × 0,63 » publié pour Lua, qui n'a pas de fils, venait de là. Le code annonce des compteurs espacés,
  pas un autre conteneur. Corrigé par une table préremplie de 64 zéros : espacé × 0,76 (`rmw`) et × 0,62 (`sw`),
  serré inchangé dans le bruit d'un processus (× 0,90 et × 1,12).
* **(4) K7 tuned** : **exact, pas une erreur.** Deux tables, quatre accès par ligne. La convention de cases de 16
  octets vaut pour les langages qui disposent la mémoire (`docs/JAVASCRIPT.md`) ; Python fait aussi deux passes. Une
  table, compte et somme tassés dans un entier (somme ≤ 2^24 × 999 < 2^34 par la spécification, compte au-dessus du
  bit 35) : forme nouvelle, **sensibilité** (× 0,73).
* **(4) K8 tuned** : arène itérative, comme `c_k8it` (C) et `tuned_it` (JavaScript) : **sensibilité** (× 1,12 : plus
  lente sur la 5.5.1).
* **(4) Retouches** : le C multiplie par 0,5 dans la boucle de K1 `soa`, Python le sort ; Julia, à base 1 comme Lua,
  ajoute 1 à chaque saut de K2, Fortran déclare un tableau à base 0 : pas de convention, **sensibilités** (K1 × 1,00 ;
  K2 × 0,83, × 0,64 et × 1,10 aux trois tailles).
* **(4) En sens inverse, K8 naturel** : **exact, et c'est une erreur de mon implémentation**, qui avantageait Lua. La
  règle du naturel (`docs/NATURAL.md`, `docs/SPEC.md`) : le type d'enregistrement par défaut, sans annotation de
  performance. L'enregistrement de Lua est une table à champs nommés (le manuel ; le K1 naturel de Lua) ; `{v, false,
  false}` occupe la partie tableau, les `false` gardant sa forme : une astuce de performance. Corrigé en
  `{ v = …, l = false, r = false }` : × 1,51 (1,85 sur la 5.4.6 selon la remarque), latences × 1,5.
* **Conséquence pour Python**, par la même règle : son K8 naturel déclare `__slots__`, une annotation de mémoire et
  de vitesse (modèle de données de Python), quand son K1 naturel est une classe ordinaire « comme dans le tutoriel
  officiel » ; `docs/NATURAL.md` le documentait, contre la règle qu'il énonce. **Erreur de mon implémentation**,
  corrigée : classe ordinaire, × 1,15, pire pause 759 → 990 ms. L'annexe LuaJIT a les mêmes nœuds positionnels
  (corrigés dans sa copie, × 1,32, pour S-LuaJIT). Les champs stricts du `data` de Haskell, documentés pour K1 comme
  pour K8, changent la sémantique du type : la règle ne les vise pas.
* **(5) B4** : **exact, erratum ½.** Sonde : un million d'opérations flottantes et entières, 0 octet alloué ; un
  million d'appels à trois retours, 0 octet ; un million d'appels variadiques, 544 octets en tout ; mais 100 000
  concaténations allouent 8,2 Mo, 100 000 fermetures 8,0 Mo, et une table construite élément par élément 1,2 Mo.
  Python, JavaScript, OCaml, Java et Haskell valent 0 par le boxing ou les thunks ; D, Go, Nim, C# et Julia ½ pour
  fermetures, chaînes et croissance : Lua est de ce second groupe.
* **(5) B3** : **exact, erratum ½.** Les nombres ne sont jamais boxés, et retours multiples et arguments variadiques
  passent par la pile de la VM (sonde : 0 octet) ; c'est le motif du ½ de Haskell (« n-uplets et valeurs non boxés…
  jamais sur le tas »). Java (primitifs sur la pile, aucun agrégat) et Python, JavaScript, OCaml (n-uplets sur le
  tas) restent à 0.
* **(5) A8** : **discutable, sensibilité.** `string.pack("<i1i2i4f", …)` tient en 11 octets et se relit par
  `string.unpack`, mais une chaîne ne s'écrit pas en place (sonde) : un stockage étroit en lecture seule, ½
  « limité » en S-cases.
* **(5) La sonde de Lua** : **exact**, elle ne testait que A5 et F3 (`results/probes/lua.txt`) ; `facts.lua` couvre
  désormais B3, B4 et A8.
* **(6) LuaJIT** : **exact sur les chiffres.** Les plafonds par noyau de l'annexe publiée valent 5 à 46 fois ceux de
  Lua, sauf K8 (1,3 fois) ; sans K3, le plafond est indéfini, car le code compilé ignore `volatile` (documentation de
  LuaJIT : « The volatile type qualifier is currently ignored by compiled code » ; sonde : 0,32 à 0,64 ns par
  incrément, le compteur en registre). Sans K3, 14,3 ; avec le K3 de Lua, 10,7 ; code par défaut 18,0. Un K3
  conforme existe : la même boucle interprétée (`jit.off`) sur une table, chaque incrément lu et écrit en mémoire,
  8,8 à 9,5 ns par incrément (compilée, 1,2 ns : l'écriture a lieu, la lecture est transmise en registre ;
  `luajit_k3.txt`). `luajit -jdump=m` affiche le code machine des traces avec le binaire officiel
  (`luajit_facts.txt`). La version 2.1.1792588164 est l'horodatage du dernier commit (21 octobre 2026). **Sensibilité
  S-LuaJIT** (grille de Lua) et **S-LuaJIT-FFI** (sa FFI notée comme `ctypes` et `node:ffi`, `-jdump` comme le
  `--print-opt-code` de Node).
* **(7) Le README** : **exact.** Le paragraphe de Lua ne dit rien des piliers mesurés ; la liste des relectures dit
  « tous sauf Lua ».
* **(8)** Lua 5.4.6 n'est pas installé ici : ses écarts ne se reproduisent pas tels quels. Sur la 5.5.1, K4 (× 2,9
  à 3,8), Q6 (× 2,2 pour la forme imbriquée) et K3 (× 1,3 à 1,6) concordent ; les voisins glissants de K9, le 0,5 de
  K1 et l'arène itérative de K8 n'apportent rien.

## 3. Plan (poussé avant les mesures)

### 3.1 Règle commune et application

`docs/FORTRAN.md`, 3.1. Erreurs : K3 (compteurs espacés dans la partie hachée), K4 (octets décodés dans la boucle
chronométrée), Q6 tuned et `mt` (masque qui branche), K8 naturel (nœuds positionnels, en sens inverse) ; par la même
règle, K8 naturel de Python (`__slots__`, en sens inverse). Errata : B3 = ½, B4 = ½. Texte : README (paragraphe de
Lua, langages relus, limites). Sensibilités : Q6 par tests imbriqués, K9 aux voisins glissants, K7 tassé, K8 tuned
itératif, K1 `soa` au 0,5 sorti, K2 décalé, A8 = ½, LuaJIT (grille de Lua ; FFI notée).

### 3.2 Ce qui entre dans le classement publié

* **L-E** : K3 (quatre variantes), K4 (trois variantes), Q6 tuned et `mt`, K8 naturel (temps et latences)
  × r(`lua_fix` / `lua_ref`), **par transfert** (machine 23, du même modèle que l'hôte des données principales ; le
  pont par le C reste calculé en information pour K3 et K4). Les autres clés de Lua ne changent pas.
* **Python** : K8 naturel (temps et latences) × r(`python_k8n` / `python_ref`), par `analysis/python_check.py`
  rejoué avant `analysis/lua_check.py` : P-E l'inclut, P-E-511 garde le P-E du 5 novembre au matin (le contrôle
  impose de le reproduire à l'identique), et les errata postérieurs (B3, B4 de Lua) y sont neutralisés.
* **Matrice** : B3 = B4 = ½ (`analysis/capabilities.py`) ; note de A8 complétée.
* **Réplication (machine 3)** : les mêmes clés × les mêmes rapports (transfert de Cascade Lake vers Emerald Rapids),
  par `results/lua_check.json` et `results/python_check.json` (« replication_ratios », « replication_lat_ratios »).
* **Texte** : README (tableau ; paragraphe de Lua : PUC-Lua sans son API C, piliers mesurés contre jugé, LuaJIT ;
  langages relus ; errata ; limites), CAPABILITIES (régénéré), `docs/NATURAL.md` (nœuds de K8 de Lua et de Python).

### 3.3 Copies (`tools/lua_check/make_copies.py`)

* `lua_ref` : copie exacte de `bench/lua_k9h` (le code publié, harnais commun de K9).
* `lua_fix` : K3 dans une table préremplie, K4 sur une table d'octets décodée hors chrono, Q6 tuned au masque sans
  branchement (bit de signe), K8 naturel à champs nommés.
* `lua_exp` : `lua_fix` et des variantes nouvelles : K6 `tuned_n` et `mt_n` (Q6 imbriqué), K9 `tuned_s` et `mt_s`,
  K7 `tuned_p`, K8 `tuned_it`, K1 `soa_h`, K2 `tuned_s`.
* `luajit_ref` : copie exacte de `bench/luajit_k9h` ; `luajit_fix` : K3 conforme (interprété), K8 naturel à champs
  nommés.
* `python_k8n` : `bench/python_k9h`, K8 naturel sur une classe ordinaire.
* Validation (`tools/lua_check/validate.py`) : 48 cellules, sommes de contrôle toutes justes.

### 3.4 Mesures (`tools/measure_lua.py`, machine 23)

52 cellules en 7 passes (364 processus) ; dans chaque passe, toutes les cellules dans un ordre tiré au hasard (graine
20262105) : `lua_ref` sur K3, K4, Q6 tuned et `mt`, K8 naturel, Q6 naturel (contrôle), K9 tuned et `mt`, K7 tuned, K8
tuned, K1 `soa` et K2 tuned à trois tailles ; `lua_fix` sur les clés corrigées et Q6 naturel (code inchangé :
contrôle) ; `lua_exp` sur ses dix variantes ; `luajit_ref` et `luajit_fix` sur K8 naturel, `luajit_fix` sur K3 ;
`python_ref` et `python_k8n` sur K8 naturel ; `c` (binaire de la campagne) sur K3 `sw_padded` et `rmw_padded`, K4
`natural_unsorted` et `branchless_unsorted` (pont, information). Répétitions de `results/calib.json` (variante
d'origine pour les variantes nouvelles ; K3 de `luajit_fix` avec celles de K3 de Lua) ; échauffements de la campagne
(3 pour LuaJIT, 1 sinon) ; règle de vol du pilote. Environ 75 minutes ; rien d'autre ne tourne. Sortie :
`results/raw_lua/`.

### 3.5 Scénarios (`analysis/lua_check.py`, analyse globale de la v3 rejouée, mêmes tirages)

| Scénario | Contenu |
|---|---|
| Avant | classement publié d'avant (B3 = B4 = 0) ; doit reproduire `results/python_check.json` (P-E rejoué, avec le K8 de Python) à l'identique |
| L-code | K3, K4, Q6 tuned et `mt`, K8 naturel × r(`lua_fix` / `lua_ref`), grille d'avant |
| L-M | errata B3, B4 seuls |
| **L-E (publié)** | les deux |
| L-E-P | L-E, K3 et K4 reportés par le pont par le C (information) |
| S-Q6n | L-E ; Q6 tuned et `mt` × r(`tuned_n`, `mt_n` / `lua_fix`) |
| S-K9s | L-E ; K9 tuned et `mt` × r(`tuned_s`, `mt_s` / `lua_ref`) |
| S-K7p | L-E ; K7 tuned × r(`tuned_p` / `lua_ref`) |
| S-K8it | L-E ; K8 tuned × r(`tuned_it` / `lua_ref`) |
| S-K1h | L-E ; K1 `soa` × r(`soa_h` / `lua_ref`) |
| S-K2s | L-E ; K2 tuned aux trois tailles × r(`tuned_s` / `lua_ref`) |
| S-mesures | toutes les formes |
| S-cases | L-E ; A8 = ½ |
| S-tout | S-mesures et S-cases |
| S-LuaJIT | LuaJIT à la place de PUC-Lua, grille de Lua : données publiées de l'annexe, K3 = K3 corrigé de Lua × r(`luajit_fix` / `lua_fix`), K8 naturel × r(`luajit_fix` / `luajit_ref`) (temps et latences), empreinte de LuaJIT |
| S-LuaJIT-FFI | la même ; A1, A2, A3, A4, A7, A8, B5, E6 = ½ (comme `ctypes` et `node:ffi`), E1 = 1 (`-jdump`) |

Rapports : moyenne géométrique des médianes de processus, intervalle par bootstrap ; latences : médiane de toutes les
répétitions, colonne par colonne ; sensibilités en min(1, r) par rapport à L-E. Information : Q6 naturel sous
`lua_fix` / `lua_ref` (contrôle). Sorties : `results/lua_check.json`, `results/report_lua.md`,
`results/transfers.json` (Lua ; Python par `analysis/python_check.py`) ; puis régénération des sorties publiées (la
réplication comprise) et de l'état actuel.

### 3.6 Ce que je ne fais pas

* Ni l'API C (la règle de la bibliothèque standard), ni LuaJIT classé (annexe et sensibilité) ; pas de règle « FFI
  sans C » ; pas de mesure sous Lua 5.4.
* Pas de K10 (hors score) ; pas de remesure de l'empreinte ; rien sur les champs stricts du naturel de Haskell.

## 4. Résultats (après les mesures)

Mesures du 5 novembre, de 13:03:10 à 14:07:34, sur la machine 23 : 364 processus (52 cellules, 7 processus chacune),
aucune somme de contrôle fausse, sept processus refaits pour vol de temps (deux deux fois), aucun gardé au-dessus de
2 % (vol médian 0,63 %). Aucun écart au plan. `analysis/python_check.py`, rejoué d'abord, reproduit J-E (Avant) et le
P-E du matin (P-E-511) à l'identique ; le scénario Avant de Lua reproduit le P-E rejoué à l'identique. Rapports :
`results/report_lua.md` ; temps : moyenne géométrique des médianes de processus, intervalle à 95 % par bootstrap.

### 4.1 Les corrections (`lua_fix` / `lua_ref`, même hôte)

| Clé | Code publié (ms) | Corrigé (ms) | Rapport [IC 95 %] | Publié d'avant → reporté (ms) |
|---|---|---|---|---|
| **K3 `rmw_packed`** | 2 073,7 | 2 000,6 | **0,965** [0,913–1,019] | 2 542,5 → 2 452,9 |
| **K3 `rmw_padded`** | 2 938,8 | 2 104,9 | **0,716** [0,679–0,754] | 4 115,2 → 2 947,4 |
| **K3 `sw_packed`** | 2 065,8 | 2 187,0 | **1,059** [0,975–1,146] | 2 559,5 → 2 709,7 |
| **K3 `sw_padded`** | 2 931,6 | 2 154,6 | **0,735** [0,689–0,790] | 4 343,0 → 3 191,9 |
| **K4 naturel non trié** | 821,5 | 290,8 | **0,354** [0,331–0,380] | 1 040,3 → 368,2 |
| **K4 naturel trié** | 689,1 | 189,2 | **0,275** [0,242–0,312] | 874,8 → 240,2 |
| **K4 sans branchement** | 715,2 | 225,7 | **0,316** [0,288–0,345] | 985,2 → 310,9 |
| **Q6 tuned** | 1 212,5 | 900,2 | **0,742** [0,691–0,811] | 1 633,9 → 1 213,0 |
| **Q6 `mt`** | 1 209,6 | 933,5 | **0,772** [0,702–0,853] | 1 592,0 → 1 228,6 |
| **K8 naturel** | 8 538,3 | 12 259,4 | **1,436** [1,381–1,500] | 10 944,0 → 15 713,5 |
| Q6 naturel (contrôle) | 496,6 | 531,0 | 1,069 [1,013–1,124] | non reporté |

Dans la partie tableau, les compteurs espacés coûtent ce que coûtent les serrés (espacé contre serré : 1,05 en `rmw`,
0,99 en `sw`, contre 1,42 avant) : le « faux partage » publié de Lua disparaît. Sur une table d'octets, K4 va 2,8 à 3,6
fois plus vite, et la prédiction de branchement apparaît (trié 1,5 fois plus rapide que non trié, contre 1,2 fois).
Le masque sans branchement accélère Q6 tuned d'un quart, sans rattraper le naturel (900 contre 497 ms). À champs
nommés, K8 naturel coûte 1,44 fois plus, et ses latences 1,27 à 1,58 fois (`report_lua.md`) : médianes de la machine
11, p50 282 → 409 µs, p99,9 20,7 → 27,5 ms, pire pause 35,4 → 44,9 ms. La clé témoin, au code identique, dévie de 7 %
(IC 1,01–1,12) : c'est la précision de ces rapports, sous les effets mesurés, sauf pour K3 serré, qui reste dans le
bruit. Pont par le C (information) : écarts de 204 et 110 % sur K3 (le C de cet hôte est 2,1 et 1,5 fois plus lent
que celui des données principales), de − 16 et 23 % sur K4 : il donnerait 5,49 points (L-E-P), même place.

### 4.2 Sensibilités (forme nouvelle / base, même hôte)

| Forme (scénario) | Clé | Base | Rapport [IC 95 %] | Remarque (Lua 5.4.6) |
|---|---|---|---|---|
| Tests imbriqués (S-Q6n) | Q6 tuned | `lua_fix` | 0,511 [0,465–0,552] | |
| | Q6 `mt` | `lua_fix` | 0,485 [0,436–0,534] | × 0,45 |
| Voisins glissants (S-K9s) | K9 tuned | `lua_ref` | 0,873 [0,810–0,944] | |
| | K9 `mt` | `lua_ref` | 0,957 [0,888–1,040] | × 0,77 |
| Table tassée (S-K7p) | K7 tuned | `lua_ref` | 0,707 [0,684–0,730] | × 0,83 |
| Arène itérative (S-K8it) | K8 tuned | `lua_ref` | 1,064 [0,995–1,131] | × 0,83 |
| 0,5 sorti (S-K1h) | K1 `soa` | `lua_ref` | 0,831 [0,737–0,937] | × 0,86 |
| Indices décalés (S-K2s) | K2 à 16 Kio, 256 Kio, 8 Mio | `lua_ref` | 0,770 ; 0,821 ; 0,974 | × 0,89 |

Les tests imbriqués ramènent Q6 au niveau du naturel ; la table tassée de K7 gagne plus que sur la 5.4.6 ; l'arène
itérative, plus lente, ne compte pas (min(1, r)).

### 4.3 LuaJIT et Python

* **K3 conforme de LuaJIT** (boucle interprétée sur une table, `luajit_fix` / `lua_fix`) : × 0,736 à 0,776 ; LuaJIT
  interprété fait à peine mieux que PUC-Lua. **K8 naturel à champs nommés** (`luajit_fix` / `luajit_ref`) : × 1,370
  [1,286–1,457].
* **Python**, K8 naturel sans `__slots__` (`python_k8n` / `python_ref`) : × 1,061 [1,026–1,099], pire pause × 1,29 ;
  le P-E de Python passe de 11,833 à 11,830 points, toujours 20e (`docs/PYTHON.md`, 4.8).

### 4.4 Classement (analyse globale de la v3 rejouée, 20 000 variantes)

| Scénario | Score | Contrôle | Plafond | Défaut | Rang espéré | Place | Rang 90 % | Python devant |
|---|---|---|---|---|---|---|---|---|
| Avant (publié d'avant) | 3,92 | 2,8 | 1,08 | 10,0 | 20,72 | 21 | 20–21 | 72,1 % |
| L-code (K3, K4, Q6, K8) | 4,01 | 2,8 | 1,31 | 10,0 | 20,67 | 21 | 20–21 | 67,5 % |
| L-M (errata B3, B4) | 5,32 | 6,8 | 1,08 | 10,0 | 20,62 | 21 | 20–21 | 62,6 % |
| **L-E (publié)** | **5,41** | 6,8 | 1,31 | 10,0 | 20,58 | 21 | 20–21 | 58,3 % |
| L-E-P (pont, information) | 5,49 | 6,8 | 1,49 | 10,0 | 20,56 | 21 | 20–21 | 56,0 % |
| S-Q6n | 5,43 | 6,8 | 1,34 | 10,0 | 20,58 | 21 | 20–21 | 57,9 % |
| S-K9s | 5,42 | 6,8 | 1,31 | 10,0 | 20,58 | 21 | 20–21 | 58,2 % |
| S-K7p | 5,44 | 6,8 | 1,37 | 10,0 | 20,57 | 21 | 20–21 | 57,5 % |
| S-K8it | 5,41 | 6,8 | 1,31 | 10,0 | 20,58 | 21 | 20–21 | 58,3 % |
| S-K1h | 5,43 | 6,8 | 1,34 | 10,0 | 20,58 | 21 | 20–21 | 57,9 % |
| S-K2s | 5,73 | 6,8 | 1,31 | 11,3 | 20,56 | 21 | 20–21 | 55,7 % |
| S-mesures | 5,78 | 6,8 | 1,43 | 11,3 | 20,54 | 21 | 20–21 | 54,2 % |
| S-cases (A8 = ½) | 5,96 | 8,4 | 1,31 | 10,0 | 20,55 | 21 | 20–21 | 55,0 % |
| S-tout | 6,33 | 8,4 | 1,43 | 11,3 | 20,51 | 21 | 20–21 | 51,0 % |
| S-LuaJIT (grille de Lua) | 11,12 | 6,8 | 11,61 | 16,4 | 20,13 | 20 | 19–21 | 20,7 % |
| S-LuaJIT-FFI | 15,85 | 20,3 | 11,61 | 16,4 | 19,49 | 19 | 19–20 | 5,2 % |

« Python devant » : part des variantes où Python devance Lua (dans S-LuaJIT et S-LuaJIT-FFI, LuaJIT). Au classement
publié (L-E), Lua gagne 1,49 point (3,92 → 5,41) et reste 21e, rang plausible 20 à 21 : les errata lui rendent 1,40
point (contrôle 2,8 → 6,8), les corrections du banc 0,09 (plafond 1,08 → 1,31 : K3 0,0141 → 0,0198 de la référence,
K4 0,0029 → 0,0091, K6 0,0098 → 0,0104), le K8 naturel plus lent retirant presque autant au code par défaut que K4 lui
apporte (10,01 → 10,03). Python ne devance plus Lua que dans 58,3 % des variantes (72,1 %). Les scores des autres
langages ne changent pas, hors Python (− 0,004).

**LuaJIT** : avec la grille de Lua, errata compris, 11,12 points (plafond 11,61, code par défaut 16,4 : son K8
naturel à champs nommés compte), au niveau de Python, qu'il devance dans 79 % des variantes ; sa FFI notée comme
`ctypes` et `node:ffi` et son `-jdump` comme le `--print-opt-code` de Node (contrôle 20,3), 15,85 points : 19e,
devant JavaScript dans 52,5 % des variantes. La remarque estimait 9,8 à 11,2 et 14,9 à 16,4.

### 4.5 Réplication (machine 3)

Données de Lua de la machine 3 multipliées par les rapports des dix clés corrigées (transfert de Cascade Lake vers
Emerald Rapids ; latences de K8 naturel comprises), avec les errata : score 4,38 → 5,86, toujours 21e ; plafond 0,85 →
1,03. Python 11,985 → 11,983, toujours 20e. L'ordre de la réplication ne change pas (Spearman 0,93 sur les 21
langages, comme avant).

### 4.6 Hors de Lua

* **Étages de la v3** : inchangés ; JavaScript, Lua et Python forment toujours le dernier étage.
* **Sans SIMD explicite** (`docs/NOSIMD.md`, 4.17) : Lua 21e dans tous les scénarios (5,4 à 6,2 points), Python 20e.
* **Confrontation** (`docs/CONFRONTATION.md`) : Lua n'est pas dans l'autre étude ; rien ne change.
* **L'annexe LuaJIT** partage la grille de Lua (contrôle 2,8 → 6,8) ; son plafond reste indéfini au classement publié
  (K3 non conforme), d'où la sensibilité S-LuaJIT.

### 4.7 Bilan

* **La remarque est juste sur l'essentiel.** Trois défauts sont des erreurs de mon implémentation (K3 dans la partie
  hachée, K4 décodé dans la boucle, masque de Q6 qui branche), un quatrième aussi, en sens inverse (K8 naturel
  positionnel), et la même règle en trouve un chez Python (`__slots__`) ; B4 et B3 étaient faux (errata) ; seul le
  pilier jugé met Lua derrière Python, qui ne le devance plus que dans 58 % des variantes ; LuaJIT le mettrait au
  niveau de Python ou de JavaScript.
* **Ce que je retiens autrement** : le masque de Q6 est corrigé tel que le code l'annonce (sans branchement), et la
  forme de la remarque, des tests imbriqués, reste une sensibilité ; K9, K7, K8 tuned, K1 et K2 sont des formes
  nouvelles, des sensibilités, dont trois ne gagnent rien ou presque sur la 5.5.1 ; A8 reste à 0 (stockage en lecture
  seule : ½ discutable).
* **Les estimations de la remarque** : plafond 1,08 → 1,47 (ici 1,31 au publié, 1,43 avec les formes) ; score 4,2 avec
  le banc corrigé (ici 4,01 : le K8 naturel corrigé en sens inverse retire ce que K4 apporte au code par défaut),
  environ 6,1 avec les trois cases (ici 5,96 avec les errata et A8, 6,33 avec les formes) ; 21e partout, confirmé.
  LuaJIT : 9,8 à 11,2 et 14,9 à 16,4 points (ici 11,12 et 15,85, le K3 conforme et les errata compris).
* **Le README** dit désormais que le classement mesure PUC-Lua sans son API C, et que seul le contrôle le place
  derrière Python ; les 21 langages ont été relus.
