# v6.1 : le classement — résultats

*Plans : `docs/V4_FINAL.md` (section 8), `docs/V4_1.md` (corrections A1 à A4 de l'analyse), `docs/V5.md` (campagne rejouée, corrections A5 et A6), `docs/V5_1.md` (A7 et A8 : mode du code naturel tiré au sort) et `docs/V5_2.md` (Zig par sa version de développement), fixés avant les mesures ou avant leur analyse ; `docs/V5_3.md` (ce qui décide de l'ordre, tri des écarts) ; `docs/V5_4.md` (Go mesuré hors de l'expérience simd) ; `docs/V6.md` (classement réduit à 20 langages) ; `docs/V6_1.md` (OxCaml à la place d'OCaml, mesuré à part). Généré par `analysis/final_v4.py` à partir de `results/final/raw`, de `results/final/b3.jsonl` et du relevé des formes (`results/converge/forms.json`).*

Machines : 38 ; b3 de référence (le plus lent des 16 décalages, A2) : 64.24 ms ; b3 des groupes de K3 : passe 0 64.62 ms, passe 1 64.20 ms, passe 2 63.92 ms ; avec la médiane des 16 décalages (méthode du 23 novembre) : 58.12 ms.

## Classement « Final »

| Rang | Langage | Score | Score au centre | Rang espéré | Rang plausible | Devance le suivant | Plafond | Code par défaut | Contrôle |
|---|---|---|---|---|---|---|---|---|---|
| 1 | C | 83.3 | 86.0 | 1.80 | 1–4 | 68 % | 84.4 | 80.6 | 91.7 |
| 2 | C++ | 81.6 | 84.5 | 2.83 | 1–7 | 71 % | 87.5 | 68.5 | 92.4 |
| 3 | Zig* | 79.6 | 79.4 | 4.11 | 1–9 | 66 % | 83.1 | 62.5 | 87.2 |
| 4 | Odin | 78.6 | 79.7 | 5.04 | 2–9 | 53 % | 81.6 | 70.5 | 84.0 |
| 5 | Rust | 78.1 | 79.9 | 5.25 | 2–9 | 63 % | 86.4 | 78.3 | 73.6 |
| 6 | Nim | 77.4 | 79.1 | 6.08 | 3–9 | 61 % | 83.3 | 76.5 | 76.1 |
| 7 | C3 | 76.7 | 78.2 | 6.78 | 3–10 | 50 % | 84.0 | 72.2 | 75.7 |
| 8 | D | 76.5 | 79.7 | 6.83 | 3–12 | 76 % | 85.4 | 60.2 | 87.1 |
| 9 | Ada | 73.9 | 75.3 | 8.90 | 5–12 | 67 % | 81.4 | 57.9 | 80.6 |
| 10 | Julia | 72.3 | 73.6 | 10.29 | 7–13 | 56 % | 77.8 | 67.5 | 73.3 |
| 11 | Fortran | 71.8 | 72.4 | 10.61 | 6–14 | 56 % | 78.3 | 72.9 | 65.3 |
| 12 | Chapel | 70.9 | 70.3 | 10.98 | 7–14 | 71 % | 86.5 | 56.0 | 61.8 |
| 13 | Mojo | 68.3 | 69.3 | 12.69 | 10–14 | 58 % | 75.7 | 57.3 | 70.5 |
| 14 | Swift | 67.6 | 68.6 | 13.03 | 11–14 | 95 % | 79.5 | 51.8 | 68.1 |
| 15 | C# | 61.2 | 63.4 | 15.08 | 14–17 | 86 % | 69.8 | 45.7 | 68.8 |
| 16 | Go | 55.3 | 55.7 | 16.38 | 15–18 | 76 % | 62.4 | 54.8 | 48.7 |
| 17 | Java | 52.5 | 53.7 | 17.28 | 16–19 | 57 % | 65.2 | 50.9 | 42.7 |
| 18 | FreePascal | 51.5 | 50.5 | 17.58 | 15–20 | 78 % | 42.2 | 47.5 | 62.3 |
| 19 | OxCaml† | 46.9 | 47.8 | 19.05 | 18–20 | 63 % | 52.6 | 44.5 | 44.8 |
| 20 | Haskell | 45.7 | 45.6 | 19.40 | 18–20 | — | 54.1 | 37.7 | 41.5 |

Score : moyenne du score sur les variantes de l'analyse ; il fixe l'ordre. Score au centre, plafond, code par défaut et contrôle : poids et choix principaux, estimation ponctuelle. Rang espéré : rang moyen sur les variantes.

\* Zig est mesuré, par exception, par sa version de développement 0.18.0-dev.1298+4a0817482 (`docs/V5_2.md`) : ses temps sont ceux de la campagne, multipliés cellule par cellule par le rapport mesuré à côté d'un témoin ; ses latences de K8 naturel restent celles de la campagne. Avec sa version stable, celle de la campagne (« Zig 0.17 ») : 5e, score 77.8.

Go est mesuré hors de l'expérience `simd` de sa chaîne (`docs/V5_4.md`) : ses 15 cellules de K1 que la campagne faussait sont rebâties par un pont par le C ; ses autres cellules sont celles de la campagne. Avec ses cellules de la campagne (« Go de la campagne ») : 17e, score 51.6.

† OxCaml a pris la place d'OCaml (`docs/V6_1.md`) et n'a pas été mesuré dans la campagne : il l'est à part, sur la machine 41, à côté d'un témoin (OCaml 5.5.2, la source et le binaire de la campagne) et d'un pont (C). Ses cellules de même source qu'OCaml sont celles d'OCaml dans la campagne, multipliées par le rapport mesuré au témoin ; ses 12 cellules propres, celles de C dans la campagne, multipliées par le rapport mesuré à C. Avec les mesures d'OCaml et sa propre grille (« OxCaml, mesures d'OCaml ») : 20e, score 34.2.

Mode du code naturel, tiré dans chaque variante (A7, A8) : R1 dans 33.4 % des variantes, mode publié dans 33.5 % des variantes, R1' dans 33.1 % des variantes ; au centre, R1.

Étages (paires ordonnées dans au moins 95 % des variantes) : C, C++, Zig, Odin, Rust, Nim, C3, D, Ada, Julia, Fortran, Chapel, Mojo, Swift, C#, Go, Java, FreePascal, OxCaml, Haskell

## Tous les calculs

| Langage | Final | Base, trois tailles | Sans les tailles (taille publiée seule) | Sans R1 | Sans R2 | Sans C1 | Sans R4 | R1' au lieu de R1 | Taille petite | Taille grande | Sélection indépendante | D3 et D4 sur trois processus | Sur les seules mesures | Sans A1 | Sans A2 | Sans A3 | Sans A4 | Sans A5 | Sans A6 | Sans A7 | Sans A8 | Méthode du 23 novembre | C par gcc | Zig 0.17 | Zig 0.18, K4 et K9 seuls | Zig 0.18, latences du plan | Go de la campagne | Go, toutes les cellules | OxCaml, mesures d'OCaml | OxCaml, source d'OCaml seule | OxCaml, pont par le témoin | OxCaml, latences du plan | Campagne telle que mesurée | Campagne précédente |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C | 1 | 1 | 2 | 1 | 1 | 1 | 2 | 1 | 1 | 2 | 1 | 1 | 2 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| C++ | 2 | 2 | 1 | 2 | 2 | 3 | 1 | 2 | 2 | 1 | 2 | 2 | 5 ** | 3 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 |
| Zig | 3 | 3 | 3 | 3 | 3 | 2 | 6 ** | 3 | 3 | 3 | 3 | 3 | 6 ** | 2 | 3 | 3 | 3 | 3 | 3 | 6 ** | 3 | 5 | 3 | 5 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 5 | 8 |
| Odin | 4 | 7 ** | 4 | 4 | 4 | 4 | 7 ** | 4 | 5 | 4 | 4 | 4 | 7 ** | 4 | 4 | 4 | 4 | 4 | 4 | 3 | 4 | 4 | 4 | 3 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 4 | 3 | 3 |
| Rust | 5 | 5 | 6 | 5 | 5 | 6 | 3 | 6 | 4 | 6 | 5 | 5 | 1 ** | 5 | 5 | 5 | 5 | 5 | 5 | 4 | 5 | 3 | 5 | 4 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 5 | 4 | 4 |
| Nim | 6 | 9 ** | 5 | 6 | 6 | 8 | 8 | 5 | 7 | 5 | 6 | 6 | 3 ** | 7 | 6 | 6 | 6 | 6 | 6 | 5 | 6 | 7 | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 6 | 6 |
| C3 | 7 | 4 ** | 7 | 7 | 7 | 5 | 4 ** | 7 | 6 | 9 | 7 | 8 | 4 ** | 6 | 7 | 7 | 7 | 7 | 7 | 8 | 7 | 6 | 7 | 7 | 7 | 7 | 7 | 7 | 7 | 7 | 7 | 7 | 7 | 7 |
| D | 8 | 6 | 8 | 8 | 8 | 7 | 5 ** | 9 | 8 | 7 | 8 | 7 | 10 | 8 | 8 | 8 | 8 | 8 | 8 | 7 | 8 | 8 | 8 | 8 | 8 | 8 | 8 | 8 | 8 | 8 | 8 | 8 | 8 | 5 |
| Ada | 9 | 8 | 9 | 9 | 9 | 9 | 9 | 8 | 12 ** | 8 | 9 | 9 | 12 ** | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 | 9 |
| Julia | 10 | 13 ** | 11 | 12 | 10 | 12 | 10 | 10 | 11 | 10 | 10 | 10 | 11 | 10 | 10 | 11 | 11 | 10 | 10 | 10 | 10 | 12 | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 10 | 10 |
| Fortran | 11 | 11 | 10 | 11 | 11 | 10 | 11 | 12 | 10 | 11 | 11 | 11 | 9 | 12 | 11 | 10 | 10 | 11 | 11 | 11 | 11 | 11 | 11 | 11 | 11 | 11 | 11 | 11 | 11 | 11 | 11 | 11 | 11 | 11 |
| Chapel | 12 | 10 | 12 | 10 | 12 | 11 | 13 | 11 | 9 ** | 12 | 12 | 12 | 8 ** | 11 | 12 | 12 | 12 | 12 | 12 | 12 | 12 | 10 | 12 | 12 | 12 | 12 | 12 | 12 | 12 | 12 | 12 | 12 | 12 | 12 |
| Mojo | 13 | 12 | 13 | 13 | 13 | 14 | 12 | 13 | 13 | 13 | 13 | 13 | 14 | 13 | 13 | 13 | 13 | 13 | 13 | 13 | 13 | 13 | 13 | 13 | 13 | 13 | 13 | 13 | 13 | 13 | 13 | 13 | 13 | 14 |
| Swift | 14 | 14 | 14 | 14 | 14 | 13 | 14 | 14 | 14 | 14 | 14 | 14 | 13 | 14 | 14 | 14 | 14 | 14 | 14 | 14 | 14 | 14 | 14 | 14 | 14 | 14 | 14 | 14 | 14 | 14 | 14 | 14 | 14 | 13 |
| C# | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 16 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 | 15 |
| Go | 16 | 17 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 15 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 17 | 16 | 16 | 16 | 16 | 16 | 17 | 17 |
| Java | 17 | 18 | 17 | 17 | 17 | 18 | 18 | 17 | 18 | 18 | 17 | 17 | 17 | 17 | 17 | 17 | 17 | 17 | 17 | 17 | 17 | 17 | 17 | 17 | 17 | 17 | 16 | 17 | 17 | 17 | 17 | 17 | 16 | 16 |
| FreePascal | 18 | 16 | 18 | 18 | 18 | 17 | 17 | 18 | 17 | 17 | 18 | 18 | 20 | 18 | 18 | 18 | 18 | 18 | 18 | 18 | 18 | 18 | 18 | 18 | 18 | 18 | 18 | 18 | 18 | 18 | 18 | 18 | 18 | 18 |
| OxCaml | 19 | 20 | 19 | 19 | 19 | 20 | 19 | 19 | 19 | 19 | 19 | 19 | 18 | 19 | 19 | 19 | 19 | 19 | 19 | 19 | 19 | 19 | 19 | 19 | 19 | 19 | 19 | 19 | 20 | 20 | 19 | 19 | 20 | – |
| Haskell | 20 | 19 | 20 | 20 | 20 | 19 | 20 | 20 | 20 | 20 | 20 | 20 | 19 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 20 | 19 | 19 | 20 | 20 | 19 | 19 |

Chaque case : place dans le calcul ; ** : plus de deux places d'écart avec « Final ». Ordre des lignes : « Final ». « Sans A1 » à « Sans A8 » : « Final » sans une de ses corrections ; « Méthode du 23 novembre » : sans aucune et classée au rang moyen ; « Zig 0.17 » : « Final » avec les cellules de Zig de la campagne ; « Zig 0.18, K4 et K9 seuls » : le rapport au témoin appliqué à ces deux noyaux seulement ; « Zig 0.18, latences du plan » : les latences de K8 naturel de Zig multipliées elles aussi par leur rapport ; « Go de la campagne » : « Final » avec les cellules de Go de la campagne ; « Go, toutes les cellules » : les autres cellules de Go ramenées elles aussi par leur témoin ; « OxCaml, mesures d'OCaml » : « Final » où la place d'OxCaml porte les mesures d'OCaml dans la campagne, sans transport, avec la grille d'OxCaml ; « OxCaml, source d'OCaml seule » : sans les cellules propres à OxCaml, les variantes qu'elles remplacent gardant leur temps d'OCaml dans la campagne ; « OxCaml, pont par le témoin » : ses cellules propres ramenées par la cellule d'OCaml de même rôle au lieu de celle de C ; « OxCaml, latences du plan » : ses latences de K8 naturel prises à OCaml dans la campagne et multipliées, colonne par colonne, par leur rapport au témoin ; « Campagne telle que mesurée » : ni l'exception de Zig ni la correction de Go, et les mesures d'OCaml à la place d'OxCaml ; « Campagne précédente » : son classement publié, places comptées parmi ses 19 langages mesurés dans les deux campagnes et gardés ici.

## Rangs qui bougent de plus de deux places par rapport à « Final »

* Base, trois tailles : Odin 7e (Final 4e), Nim 9e (Final 6e), C3 4e (Final 7e), Julia 13e (Final 10e)
* Sans les tailles (taille publiée seule) : aucun
* Sans R1 : aucun
* Sans R2 : aucun
* Sans C1 : aucun
* Sans R4 : Zig 6e (Final 3e), Odin 7e (Final 4e), C3 4e (Final 7e), D 5e (Final 8e)
* R1' au lieu de R1 : aucun
* Taille petite : Ada 12e (Final 9e), Chapel 9e (Final 12e)
* Taille grande : aucun
* Sélection indépendante : aucun
* D3 et D4 sur trois processus : aucun
* Sur les seules mesures : C++ 5e (Final 2e), Zig 6e (Final 3e), Odin 7e (Final 4e), Rust 1er (Final 5e), Nim 3e (Final 6e), C3 4e (Final 7e), Ada 12e (Final 9e), Chapel 8e (Final 12e)
* Sans A1 : aucun
* Sans A2 : aucun
* Sans A3 : aucun
* Sans A4 : aucun
* Sans A5 : aucun
* Sans A6 : aucun
* Sans A7 : Zig 6e (Final 3e)
* Sans A8 : aucun
* Méthode du 23 novembre : aucun
* C par gcc : aucun
* Zig 0.17 : aucun
* Zig 0.18, K4 et K9 seuls : aucun
* Zig 0.18, latences du plan : aucun
* Go de la campagne : aucun
* Go, toutes les cellules : aucun
* OxCaml, mesures d'OCaml : aucun
* OxCaml, source d'OCaml seule : aucun
* OxCaml, pont par le témoin : aucun
* OxCaml, latences du plan : aucun
* Campagne telle que mesurée : aucun
* Final contre la méthode du 23 novembre : aucun
* « Campagne telle que mesurée » contre la campagne précédente, classement publié : Zig 8e → 5e, D 5e → 8e
* « Campagne telle que mesurée » contre la campagne précédente recalculée par la méthode de celle-ci : aucun
* Campagne précédente, du classement publié à son recalcul : Zig 8e → 5e

## C par gcc

« C par gcc » : « Final » où toutes les cellules de C viennent de ses constructions par gcc ; la grille et les autres langages ne changent pas.

| C compilé par | Place | Score | Premier | Devance C++ | Plafond | Code naturel | K1 | K3 | K4 | K5 | K6 | K7 | K8 | K9 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| clang (« Final ») | 1 | 83.3 | 56.8 % | 68.1 % | 84.4 | 70.7 | 85 | 99 | 95 | 84 | 81 | 81 | 68 | 86 |
| gcc | 1 | 83.0 | 56.0 % | 73.2 % | 87.9 | 61.7 | 90 | 100 | 86 | 89 | 80 | 75 | 95 | 92 |

## Réplication : cette campagne et la précédente

Les deux campagnes sont comparées à configurations égales : pour celle-ci, le calcul « Campagne telle que mesurée », sur les 19 langages mesurés dans les deux et gardés au classement : la place d'OxCaml, que tiennent dans ce calcul les mesures d'OCaml, est laissée de côté, et les places sont comptées parmi les autres.

Cellules mesurées dans les deux campagnes : 2348. Rapport des temps (cette campagne sur la précédente, estimations ponctuelles) : médiane 0.856 ; 65 % des cellules à moins de 10 % de cette médiane.

| Langage | Place | Précédente, recalculée | Précédente, publiée | Score | Précédent, recalculé | Précédent, publié | Plafond | Plafond précédent | Rapport médian des temps |
|---|---|---|---|---|---|---|---|---|---|
| C | 1 | 1 | 1 | 83.6 | 83.8 | 81.4 | 84.6 | 89.6 | 0.885 |
| C++ | 2 | 2 | 2 | 81.9 | 81.9 | 79.2 | 87.7 | 90.1 | 0.863 |
| Odin | 3 | 3 | 3 | 78.8 | 78.7 | 76.4 | 81.7 | 83.7 | 0.867 |
| Rust | 4 | 4 | 4 | 78.3 | 77.8 | 75.9 | 86.6 | 88.3 | 0.881 |
| Zig | 5 | 5 | 8 | 77.9 | 77.2 | 73.0 | 82.5 | 84.4 | 0.850 |
| Nim | 6 | 6 | 6 | 77.6 | 76.9 | 74.6 | 83.5 | 85.9 | 0.869 |
| C3 | 7 | 8 | 7 | 76.9 | 76.7 | 74.2 | 84.2 | 86.8 | 0.862 |
| D | 8 | 7 | 5 | 76.8 | 76.9 | 74.8 | 85.6 | 87.0 | 0.848 |
| Ada | 9 | 9 | 9 | 74.1 | 74.0 | 71.0 | 81.6 | 83.7 | 0.857 |
| Julia | 10 | 10 | 10 | 72.5 | 71.4 | 69.6 | 77.9 | 78.4 | 0.852 |
| Fortran | 11 | 11 | 11 | 72.0 | 71.0 | 68.1 | 78.5 | 79.1 | 0.862 |
| Chapel | 12 | 12 | 12 | 71.0 | 70.7 | 66.0 | 86.7 | 89.9 | 0.864 |
| Mojo | 13 | 14 | 14 | 68.4 | 67.0 | 64.5 | 75.9 | 76.0 | 0.848 |
| Swift | 14 | 13 | 13 | 67.8 | 67.6 | 65.2 | 79.7 | 80.6 | 0.856 |
| C# | 15 | 15 | 15 | 61.3 | 60.9 | 59.3 | 69.9 | 71.2 | 0.841 |
| Java | 16 | 16 | 16 | 52.7 | 52.6 | 51.2 | 65.3 | 66.0 | 0.844 |
| Go | 17 | 17 | 17 | 51.8 | 51.7 | 50.6 | 62.5 | 62.6 | 0.837 |
| FreePascal | 18 | 18 | 18 | 51.7 | 50.9 | 49.3 | 42.3 | 43.0 | 0.844 |
| Haskell | 19 | 19 | 19 | 45.9 | 44.2 | 43.0 | 54.2 | 52.3 | 0.839 |

« Publiée » : le classement de la campagne précédente tel qu'il était publié ; « recalculée » : la même campagne recalculée par la méthode de celle-ci (comparaison à méthode égale). Le plafond, donné au centre, est le même dans les deux.

## Zig par sa version de développement

Version 0.18.0-dev.1298+4a0817482, mesurée hors campagne sur la machine 39 avec son témoin, la version de la campagne remesurée dans les mêmes groupes : 777 et 777 processus retenus, 0 écartés, 0 cellules sans rapport. Chaque case : rapport du temps sous la version de développement au temps du témoin (moyenne géométrique des rapports appariés, et nombre de paires) ; les processus de Zig de la campagne sont multipliés par ce rapport.

| Noyau | Étiquette | Variante | petite | publiée | grande |
|---|---|---|---|---|---|
| K1 | chk | natural energy | 0.95 (6) | 0.94 (6) | 0.96 (6) |
| K1 | chk | natural_shuffled energy | 0.95 (6) | 0.96 (6) | 1.02 (6) |
| K1 | pub | aos energy | 0.87 (6) | 1.05 (6) | 1.01 (6) |
| K1 | pub | natural energy | 1.02 (6) | 0.99 (6) | 0.99 (6) |
| K1 | pub | natural_shuffled energy | 1.05 (6) | 1.03 (6) | 0.96 (6) |
| K1 | pub | soa energy | 1.00 (6) | 1.06 (6) | 1.14 (6) |
| K2 | pub | tuned 16384 | – | 1.00 (13) | – |
| K2 | pub | tuned 262144 | – | 1.00 (13) | – |
| K2 | pub | tuned 8388608 | – | 0.81 (13) | – |
| K3 | pub | rmw_padded | – | 1.01 (6) | – |
| K3 | pub | sw_padded | – | 1.01 (6) | – |
| K4 | chk | natural_unsorted | 0.99 (6) | 0.97 (6) | 0.99 (6) |
| K4 | cv | swar | 0.28 (6) | 0.31 (6) | 0.21 (6) |
| K4 | cv | tuned | 1.04 (6) | 1.12 (6) | 0.96 (6) |
| K4 | pub | branchless_unsorted | 0.25 (6) | 0.24 (6) | 0.34 (6) |
| K4 | pub | natural_unsorted | 0.24 (6) | 0.25 (6) | 0.35 (6) |
| K5 | chk | natural | 1.00 (6) | 0.99 (6) | 0.96 (6) |
| K5 | pub | natural | 1.00 (6) | 1.00 (6) | 1.04 (6) |
| K5 | pub | tuned | 1.01 (6) | 1.00 (6) | 0.93 (6) |
| K6 | chk | natural q1 | 1.06 (6) | 1.02 (6) | 1.02 (6) |
| K6 | chk | natural q6 | 0.99 (6) | 1.01 (6) | 1.10 (6) |
| K6 | cv | mt_pool q1 | 0.96 (6) | 1.00 (6) | 0.96 (6) |
| K6 | cv | mt_pool q6 | 1.01 (6) | 0.91 (6) | 1.00 (6) |
| K6 | pub | mt q1 | 1.38 (6) | 0.96 (6) | 1.05 (6) |
| K6 | pub | mt q6 | 1.38 (6) | 0.99 (6) | 1.08 (6) |
| K6 | pub | natural q1 | 0.99 (6) | 1.00 (6) | 1.00 (6) |
| K6 | pub | natural q6 | 0.86 (6) | 1.05 (6) | 1.05 (6) |
| K6 | pub | tuned q1 | 1.02 (6) | 1.01 (6) | 1.04 (6) |
| K6 | pub | tuned q6 | 1.00 (6) | 1.07 (6) | 0.99 (6) |
| K7 | chk | natural | 0.99 (6) | 0.99 (6) | 1.10 (6) |
| K7 | pub | natural | 0.98 (6) | 1.14 (6) | 0.99 (6) |
| K7 | pub | tuned | 0.95 (6) | 1.00 (6) | 0.88 (6) |
| K8 | chk | natural | 1.02 (13) | 1.02 (13) | 1.02 (13) |
| K8 | cv | tuned_it | 0.99 (6) | 1.00 (6) | 1.01 (6) |
| K8 | cv | tuned_val | 1.00 (6) | 0.98 (6) | 0.99 (6) |
| K8 | pub | natural | 1.03 (13) | 1.03 (13) | 1.02 (13) |
| K8 | pub | tuned | 1.00 (6) | 0.99 (6) | 1.00 (6) |
| K8 | pub | tuned_alloc | 0.98 (6) | 1.00 (6) | 1.00 (6) |
| K9 | chk | natural | 0.50 (6) | 0.98 (6) | 0.73 (6) |
| K9 | cv | mt_pool | 1.01 (6) | 0.84 (6) | 0.96 (6) |
| K9 | pub | mt | 1.43 (6) | 1.19 (6) | 0.98 (6) |
| K9 | pub | natural | 0.48 (6) | 0.81 (6) | 0.84 (6) |
| K9 | pub | tuned | 0.99 (6) | 1.03 (6) | 1.17 (6) |

Le témoin contre ses temps de la campagne : rapport médian 0.98, de 0.64 à 1.23 ; 74 % des cellules à moins de 10 %. Le transport annule cet écart. Latences de K8 naturel (p50, p90, p99, p99,9, maximum), rapport des médianes, appliqué dans le seul calcul « Zig 0.18, latences du plan » : chk, large : 1.02, 1.01, 1.06, 1.02, 0.99 ; chk, pub : 1.03, 0.98, 0.92, 0.84, 0.42 ; chk, small : 1.02, 1.02, 1.01, 0.99, 0.96 ; pub, large : 1.02, 1.02, 1.02, 0.92, 1.06 ; pub, pub : 1.02, 1.02, 1.02, 1.13, 0.75 ; pub, small : 1.02, 1.02, 1.02, 1.06, 1.16.

## Go hors de l'expérience simd

Go est remesuré hors campagne sur la machine 40 (`docs/V5_4.md`), dans les mêmes groupes : sa nouvelle configuration (les variantes sans SIMD explicite dans un binaire compilé sans `GOEXPERIMENT=simd`), son témoin (le binaire de la campagne) et, pour K1, le pont (C) ; 474, 474 et 36 processus retenus, 0 écartés, 0 cellules faussées sans rapport.

Cellules faussées, rebâties par le pont. Rapport au pont : temps de Go dans le binaire standard sur temps de la cellule de C, moyenne géométrique des rapports appariés (nombre de paires) ; la cellule prend les processus de C dans la campagne, multipliés par ce rapport. Artefact : rapport du témoin à la nouvelle configuration, moyenne géométrique (plus petit rapport apparié). Témoin sur campagne : temps du témoin dans la remesure sur temps de la cellule dans la campagne. Temps : celui de la campagne, puis le temps corrigé, en millisecondes.

| Étiquette | Variante | Grandeur | petite | publiée | grande |
|---|---|---|---|---|---|
| pub | aos | rapport au pont | 1.17 (6) | 0.92 (6) | 0.87 (6) |
| pub | aos | artefact | 75 (1) | 40 (34) | 46 (42) |
| pub | aos | témoin sur campagne | 0.46 | 1.18 | 1.12 |
| pub | aos | temps (ms) | 3.87 → 0.0198 | 954 → 26.8 | 3 960 → 97.1 |
| pub | natural | rapport au pont | 1.06 (6) | 0.91 (6) | 0.88 (6) |
| pub | natural | artefact | 117 (1) | 62 (52) | 73 (71) |
| pub | natural | témoin sur campagne | 3.05 | 1.16 | 1.20 |
| pub | natural | temps (ms) | 0.827 → 0.0178 | 1 489 → 26.5 | 5 930 → 98.2 |
| pub | natural_shuffled | rapport au pont | 0.93 (6) | 1.01 (6) | 1.03 (6) |
| pub | natural_shuffled | artefact | 343 (309) | 63 (57) | 72 (70) |
| pub | natural_shuffled | témoin sur campagne | 1.15 | 1.41 | 1.22 |
| pub | natural_shuffled | temps (ms) | 5.71 → 0.0157 | 1 141 → 27.4 | 5 590 → 114 |
| unc | natural | rapport au pont | 0.93 (6) | 0.93 (6) | 0.88 (6) |
| unc | natural | artefact | 137 (1) | 59 (51) | 71 (66) |
| unc | natural | témoin sur campagne | 2.54 | 1.11 | 1.16 |
| unc | natural | temps (ms) | 1.01 → 0.0156 | 1 517 → 27.2 | 5 987 → 98.5 |
| unc | natural_shuffled | rapport au pont | 1.02 (6) | 0.99 (6) | 1.07 (6) |
| unc | natural_shuffled | artefact | 316 (236) | 71 (67) | 69 (61) |
| unc | natural_shuffled | témoin sur campagne | 1.17 | 1.17 | 1.11 |
| unc | natural_shuffled | temps (ms) | 5.68 → 0.0173 | 1 518 → 26.8 | 6 145 → 120 |

Autres cellules, rapport de la nouvelle configuration au témoin (contrôle ; appliqué dans le seul calcul « Go, toutes les cellules ») : 113 cellules, médiane 0.99, de 0.64 à 1.13 ; 88 % à moins de 10 % de 1 ; hors de 0,8 à 1,25 : pub large k7 natural, unc large k7 natural (instruites : `docs/V5_4.md`, 9). Le témoin contre ses temps de la campagne : rapport médian 1.17, de 0.82 à 1.49.

| Noyau | Étiquette | Variante | petite | publiée | grande |
|---|---|---|---|---|---|
| K1 | pub | soa energy | 0.86 (6) | 1.00 (6) | 0.99 (6) |
| K2 | pub | tuned 16384 | – | 0.98 (7) | – |
| K2 | pub | tuned 262144 | – | 0.99 (7) | – |
| K2 | pub | tuned 8388608 | – | 1.01 (7) | – |
| K3 | pub | rmw_padded | – | 1.05 (3) | – |
| K3 | pub | sw_padded | – | 1.03 (3) | – |
| K4 | cv | swar | 0.97 (3) | 0.83 (3) | 1.00 (3) |
| K4 | cv | tuned | 1.06 (3) | 1.01 (3) | 0.99 (3) |
| K4 | pub | branchless_unsorted | 1.00 (3) | 0.97 (3) | 1.03 (3) |
| K4 | pub | natural_unsorted | 0.99 (3) | 0.97 (3) | 1.01 (3) |
| K4 | unc | natural_unsorted | 0.99 (3) | 0.92 (3) | 1.05 (3) |
| K5 | cv | tuned_v | 1.01 (3) | 1.06 (3) | 1.00 (3) |
| K5 | pub | natural | 0.96 (3) | 1.13 (3) | 0.95 (3) |
| K5 | pub | tuned | 1.03 (3) | 0.91 (3) | 0.99 (3) |
| K5 | unc | natural | 1.04 (3) | 0.94 (3) | 1.07 (3) |
| K6 | cv | mt_pool_v q1 | 1.00 (3) | 1.00 (3) | 0.92 (3) |
| K6 | cv | tuned_v q1 | 1.06 (3) | 0.93 (3) | 0.95 (3) |
| K6 | pub | mt q1 | 1.00 (3) | 1.12 (3) | 1.01 (3) |
| K6 | pub | mt q6 | 0.96 (3) | 0.86 (3) | 1.10 (3) |
| K6 | pub | natural q1 | 0.92 (3) | 0.91 (3) | 1.04 (3) |
| K6 | pub | natural q6 | 0.96 (3) | 1.04 (3) | 0.99 (3) |
| K6 | pub | tuned q1 | 0.97 (3) | 1.03 (3) | 0.92 (3) |
| K6 | pub | tuned q6 | 0.86 (3) | 0.99 (3) | 0.95 (3) |
| K6 | unc | natural q1 | 0.99 (3) | 1.11 (3) | 1.00 (3) |
| K6 | unc | natural q6 | 0.99 (3) | 1.05 (3) | 1.00 (3) |
| K7 | pub | natural | 0.95 (3) | 0.92 (3) | 0.78 (3) |
| K7 | pub | tuned | 1.06 (3) | 1.04 (3) | 1.01 (3) |
| K7 | unc | natural | 1.01 (3) | 1.03 (3) | 0.64 (3) |
| K8 | cv | tuned_it | 0.97 (3) | 0.93 (3) | 0.98 (3) |
| K8 | cv | tuned_val | 1.01 (3) | 0.91 (3) | 0.92 (3) |
| K8 | pub | natural | 0.98 (7) | 1.00 (7) | 0.97 (7) |
| K8 | pub | tuned | 0.98 (3) | 1.05 (3) | 1.04 (3) |
| K8 | unc | natural | 1.00 (7) | 1.01 (7) | 1.00 (7) |
| K9 | cv | mt_pool_v | 1.00 (3) | 1.06 (3) | 0.99 (3) |
| K9 | cv | natural_flat | 0.97 (3) | 1.02 (3) | 0.88 (3) |
| K9 | cv | tuned_v | 0.85 (3) | 1.03 (3) | 0.99 (3) |
| K9 | cv_unc | natural_flat | 0.99 (3) | 1.00 (3) | 0.96 (3) |
| K9 | pub | mt | 0.97 (3) | 1.00 (3) | 0.98 (3) |
| K9 | pub | natural | 1.01 (3) | 0.82 (3) | 1.01 (3) |
| K9 | pub | tuned | 1.01 (3) | 0.97 (3) | 1.10 (3) |
| K9 | unc | natural | 0.90 (3) | 1.01 (3) | 1.08 (3) |

## OxCaml mesuré à part

OxCaml 5.4.0-ox7 est mesuré hors campagne sur la machine 41 (`docs/V6_1.md`), dans les mêmes groupes que son témoin (OCaml 5.5.2 : la source et le binaire de la campagne) et que le pont (C) : 1047, 885 et 198 processus retenus, 0 écartés, 0 cellules sans rapport.

| Calcul | Place | Score | Plafond | Code par défaut | Contrôle | K1 | K3 | K4 | K5 | K6 | K7 | K8 | K9 | D1 | D3 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Final | 19 | 46.9 | 52.6 | 44.5 | 44.8 | 63 | 35 | 58 | 60 | 52 | 51 | 44 | 65 | 21 | 71 |
| OxCaml, pont par le témoin | 19 | 47.6 | 56.1 | 44.5 | 44.8 | 65 | 35 | 57 | 68 | 63 | 52 | 44 | 76 | 21 | 71 |
| OxCaml, latences du plan | 19 | 47.1 | 52.6 | 45.2 | 44.8 | 63 | 35 | 58 | 60 | 52 | 51 | 44 | 65 | 21 | 76 |
| OxCaml, source d'OCaml seule | 20 | 35.6 | 22.1 | 44.5 | 44.8 | 28 | 35 | 9 | 3 | 23 | 49 | 44 | 37 | 21 | 71 |
| OxCaml, mesures d'OCaml | 20 | 34.2 | 23.2 | 35.8 | 44.8 | 28 | 25 | 8 | 14 | 18 | 38 | 42 | 37 | 21 | 36 |

« OxCaml, mesures d'OCaml » : la grille d'OxCaml seule ; « OxCaml, source d'OCaml seule » : en plus, le compilateur et le runtime (les cellules de la source d'OCaml, ramenées par le témoin, et les latences) ; « Final » : en plus, les formes propres à OxCaml. Plafond, code par défaut, contrôle, noyaux, D1 et D3 : au centre.

Cellules de même source qu'OCaml (`bench/oxcaml/ms.ml`) : 128 cellules. Chaque case : rapport du temps sous OxCaml au temps du témoin (moyenne géométrique des rapports appariés, et nombre de paires) ; les processus d'OCaml dans la campagne sont multipliés par ce rapport. Médiane 0.93, de 0.37 à 4.59 ; 39 % des cellules à moins de 10 % de 1 ; hors de 0,5 à 2 : pub l2 k5 tuned, pub l3 k5 tuned, pub pub k5 tuned, pub small k1 natural_shuffled energy, unc l2 k5 natural, unc l3 k5 natural, unc pub k5 natural, unc small k1 natural_shuffled energy, unc small k1 natural energy (instruites : `docs/V6_1.md`, 11). Le témoin contre ses temps de la campagne : rapport médian 1.18, de 0.95 à 1.57 ; 21 % des cellules à moins de 10 % de 1. Le transport annule cet écart.

| Noyau | Étiquette | Variante | petite | publiée | grande |
|---|---|---|---|---|---|
| K1 | pub | natural energy | 0.51 (6) | 0.78 (6) | 0.75 (6) |
| K1 | pub | natural_shuffled energy | 0.37 (6) | 0.53 (6) | 0.61 (6) |
| K1 | unc | natural energy | 0.47 (6) | 0.70 (6) | 0.76 (6) |
| K1 | unc | natural_shuffled energy | 0.40 (6) | 0.55 (6) | 0.56 (6) |
| K2 | pub | tuned 16384 | – | 0.75 (13) | – |
| K2 | pub | tuned 262144 | – | 0.90 (13) | – |
| K2 | pub | tuned 8388608 | – | 0.95 (13) | – |
| K3 | pub | rmw_padded | – | 0.72 (6) | – |
| K3 | pub | sw_padded | – | 0.93 (6) | – |
| K4 | cv | swar | 0.70 (6) | 0.89 (6) | 0.96 (6) |
| K4 | pub | branchless_unsorted | 0.89 (6) | 1.02 (6) | 0.86 (6) |
| K4 | pub | natural_unsorted | 1.01 (6) | 1.02 (6) | 1.05 (6) |
| K4 | unc | natural_unsorted | 0.97 (6) | 0.92 (6) | 0.99 (6) |
| K5 | pub | natural | 1.49 (6) | 1.53 (6) | 1.49 (6) |
| K5 | pub | tuned | 4.59 (6) | 4.52 (6) | 3.31 (6) |
| K5 | unc | natural | 2.16 (6) | 2.19 (6) | 2.01 (6) |
| K6 | cv | mt_pool q1 | 0.97 (6) | 0.78 (6) | 0.86 (6) |
| K6 | cv | mt_pool q6 | 0.88 (6) | 0.71 (6) | 0.72 (6) |
| K6 | cv | mt_pool_s q1 | 1.53 (6) | 1.41 (6) | 1.36 (6) |
| K6 | cv | mt_pool_s q6 | 0.98 (6) | 0.91 (6) | 0.95 (6) |
| K6 | cv | tuned_s q1 | 1.44 (6) | 1.40 (6) | 1.40 (6) |
| K6 | cv | tuned_s q6 | 0.68 (6) | 0.92 (6) | 0.95 (6) |
| K6 | pub | mt q1 | 0.95 (6) | 0.83 (6) | 0.82 (6) |
| K6 | pub | mt q6 | 0.94 (6) | 0.85 (6) | 0.71 (6) |
| K6 | pub | natural q1 | 0.90 (6) | 0.94 (6) | 0.96 (6) |
| K6 | pub | natural q6 | 0.85 (6) | 0.81 (6) | 0.88 (6) |
| K6 | pub | tuned q1 | 0.76 (6) | 0.80 (6) | 0.83 (6) |
| K6 | pub | tuned q6 | 0.57 (6) | 0.68 (6) | 0.71 (6) |
| K6 | unc | natural q1 | 0.89 (6) | 0.95 (6) | 0.92 (6) |
| K6 | unc | natural q6 | 0.82 (6) | 0.79 (6) | 0.82 (6) |
| K7 | cv | tuned_oa | 0.73 (6) | 0.83 (6) | 0.86 (6) |
| K7 | pub | natural | 0.97 (6) | 1.01 (6) | 0.98 (6) |
| K7 | pub | tuned | 0.61 (6) | 0.78 (6) | 0.86 (6) |
| K7 | unc | natural | 0.98 (6) | 0.98 (6) | 0.98 (6) |
| K8 | cv | tuned_it | 0.92 (6) | 0.96 (6) | 0.96 (6) |
| K8 | cv | tuned_val | 0.96 (6) | 1.00 (6) | 0.98 (6) |
| K8 | pub | natural | 0.98 (13) | 0.94 (13) | 0.81 (13) |
| K8 | pub | tuned | 0.99 (6) | 0.99 (6) | 0.97 (6) |
| K8 | unc | natural | 1.05 (13) | 1.01 (13) | 0.80 (13) |
| K9 | cv | mt_pool | 1.00 (6) | 0.91 (6) | 1.04 (6) |
| K9 | cv | natural_flat | 1.17 (6) | 0.97 (6) | 1.00 (6) |
| K9 | cv_unc | natural_flat | 0.79 (6) | 0.84 (6) | 0.84 (6) |
| K9 | pub | mt | 0.94 (6) | 1.02 (6) | 0.98 (6) |
| K9 | pub | natural | 1.36 (6) | 1.32 (6) | 1.19 (6) |
| K9 | pub | tuned | 0.95 (6) | 0.95 (6) | 1.04 (6) |
| K9 | unc | natural | 0.66 (6) | 0.88 (6) | 0.86 (6) |

Cellules propres à OxCaml (`bench/oxcaml/ox.ml`), ramenées par un pont. Rapport au pont : temps d'OxCaml sur temps de la cellule du pont, moyenne géométrique des rapports appariés (nombre de paires) ; la cellule prend les processus du pont dans la campagne, multipliés par ce rapport. Rapport à OCaml : temps d'OxCaml sur temps de la cellule d'OCaml de même rôle, mesurée par le témoin ; il sert de pont dans le calcul « OxCaml, pont par le témoin ». Temps : celui mesuré ici, puis le temps ramené aux conditions de la campagne, en millisecondes.

| Noyau | Étiquette | Variante | Pont | Cellule d'OCaml | Grandeur | petite | publiée | grande |
|---|---|---|---|---|---|---|---|---|
| K1 | pub | aos energy | C pub k1 aos energy | pub k1 aos energy | rapport au pont | 4.56 (6) | 1.79 (6) | 1.77 (6) |
| K1 | pub | aos energy | C pub k1 aos energy | pub k1 aos energy | rapport à OCaml | 1.16 | 1.30 | 1.27 |
| K1 | pub | aos energy | C pub k1 aos energy | pub k1 aos energy | temps (ms) | 0.0558 → 0.0471 | 52.5 → 53.8 | 203 → 218 |
| K1 | pub | soa energy | C pub k1 soa energy | pub k1 soa energy | rapport au pont | 2.21 (6) | 1.05 (6) | 1.07 (6) |
| K1 | pub | soa energy | C pub k1 soa energy | pub k1 soa energy | rapport à OCaml | 0.27 | 0.43 | 0.68 |
| K1 | pub | soa energy | C pub k1 soa energy | pub k1 soa energy | temps (ms) | 0.00615 → 0.00468 | 3.14 → 3.39 | 21.4 → 20.1 |
| K4 | cv | tuned | C cv k4 tuned | cv k4 tuned | rapport au pont | 2.39 (6) | 1.25 (6) | 1.46 (6) |
| K4 | cv | tuned | C cv k4 tuned | cv k4 tuned | rapport à OCaml | 0.12 | 0.11 | 0.22 |
| K4 | cv | tuned | C cv k4 tuned | cv k4 tuned | temps (ms) | 0.0282 → 0.0205 | 0.851 → 0.757 | 33.6 → 31.2 |
| K5 | cv | tuned_v | C pub k5 tuned | pub k5 tuned | rapport au pont | 2.09 (6) | 1.33 (6) | 0.96 (6) |
| K5 | cv | tuned_v | C pub k5 tuned | pub k5 tuned | rapport à OCaml | 0.12 | 0.16 | 0.42 |
| K5 | cv | tuned_v | C pub k5 tuned | pub k5 tuned | temps (ms) | 7.61 → 6.57 | 10.1 → 8.89 | 40.1 → 52.2 |
| K6 | cv | mt_pool_v q1 | C cv k6 mt_pool q1 | cv k6 mt_pool q1 | rapport au pont | 2.02 (6) | 1.95 (6) | 1.95 (6) |
| K6 | cv | mt_pool_v q1 | C cv k6 mt_pool q1 | cv k6 mt_pool q1 | rapport à OCaml | 0.80 | 0.50 | 0.51 |
| K6 | cv | mt_pool_v q1 | C cv k6 mt_pool q1 | cv k6 mt_pool q1 | temps (ms) | 0.169 → 0.155 | 16.2 → 15.0 | 63.9 → 60.5 |
| K6 | cv | mt_pool_v q6 | C cv k6 mt_pool_v q6 | cv k6 mt_pool q6 | rapport au pont | 1.59 (6) | 1.31 (6) | 1.13 (6) |
| K6 | cv | mt_pool_v q6 | C cv k6 mt_pool_v q6 | cv k6 mt_pool q6 | rapport à OCaml | 0.52 | 0.11 | 0.16 |
| K6 | cv | mt_pool_v q6 | C cv k6 mt_pool_v q6 | cv k6 mt_pool q6 | temps (ms) | 0.103 → 0.0945 | 2.96 → 4.77 | 17.6 → 21.8 |
| K6 | cv | tuned_v q1 | C pub k6 tuned q1 | pub k6 tuned q1 | rapport au pont | 2.69 (6) | 1.77 (6) | 1.71 (6) |
| K6 | cv | tuned_v q1 | C pub k6 tuned q1 | pub k6 tuned q1 | rapport à OCaml | 0.52 | 0.57 | 0.50 |
| K6 | cv | tuned_v q1 | C pub k6 tuned q1 | pub k6 tuned q1 | temps (ms) | 0.183 → 0.166 | 53.0 → 46.9 | 201 → 195 |
| K6 | cv | tuned_v q6 | C cv k6 tuned_v q6 | pub k6 tuned q6 | rapport au pont | 1.61 (6) | 1.06 (6) | 1.15 (6) |
| K6 | cv | tuned_v q6 | C cv k6 tuned_v q6 | pub k6 tuned q6 | rapport à OCaml | 0.05 | 0.17 | 0.18 |
| K6 | cv | tuned_v q6 | C cv k6 tuned_v q6 | pub k6 tuned q6 | temps (ms) | 0.0169 → 0.0129 | 14.1 → 12.8 | 62.3 → 68.8 |
| K7 | cv | tuned_pf | C pub k7 tuned | cv k7 tuned_oa | rapport au pont | 2.64 (6) | 2.17 (6) | 1.40 (6) |
| K7 | cv | tuned_pf | C pub k7 tuned | cv k7 tuned_oa | rapport à OCaml | 0.85 | 0.75 | 0.72 |
| K7 | cv | tuned_pf | C pub k7 tuned | cv k7 tuned_oa | temps (ms) | 0.248 → 0.209 | 431 → 457 | 5 928 → 5 170 |
| K8 | pub | tuned_alloc | témoin pub k8 natural | pub k8 natural | rapport au pont | 0.91 (6) | 0.84 (6) | 0.61 (6) |
| K8 | pub | tuned_alloc | témoin pub k8 natural | pub k8 natural | rapport à OCaml | 0.91 | 0.84 | 0.61 |
| K8 | pub | tuned_alloc | témoin pub k8 natural | pub k8 natural | temps (ms) | 45.6 → 38.9 | 184 → 172 | 719 → 595 |
| K9 | cv | mt_pool_v | C cv k9 mt_pool_v | cv k9 mt_pool | rapport au pont | 1.65 (6) | 1.23 (6) | 1.03 (6) |
| K9 | cv | mt_pool_v | C cv k9 mt_pool_v | cv k9 mt_pool | rapport à OCaml | 0.79 | 0.45 | 0.59 |
| K9 | cv | mt_pool_v | C cv k9 mt_pool_v | cv k9 mt_pool | temps (ms) | 0.472 → 0.448 | 6.3 → 6.67 | 128 → 134 |
| K9 | cv | tuned_v | C cv k9 tuned_v | pub k9 tuned | rapport au pont | 1.80 (6) | 1.37 (6) | 1.11 (6) |
| K9 | cv | tuned_v | C cv k9 tuned_v | pub k9 tuned | rapport à OCaml | 0.29 | 0.52 | 0.58 |
| K9 | cv | tuned_v | C cv k9 tuned_v | pub k9 tuned | temps (ms) | 0.126 → 0.106 | 21.9 → 17.9 | 426 → 452 |

Latences de K8 naturel : celles qu'OxCaml a mesurées, multipliées à chaque taille par l'échelle de la machine, rapport du temps médian d'une requête d'OCaml dans la campagne à celui du témoin. « OxCaml, latences du plan » prend à la place les latences d'OCaml dans la campagne, multipliées colonne par colonne par le rapport d'OxCaml au témoin, ce qui suppose que chaque colonne du témoin se retrouve d'une machine à l'autre (`docs/V6_1.md`, 10). Colonnes : p50, p90, p99, p99,9, maximum (médianes sur les répétitions).

| Étiquette | Taille | Échelle | Témoin sur campagne | OxCaml sur témoin |
|---|---|---|---|---|
| pub | petite | 0.82 | 1.22, 1.26, 1.52, 1.03, 1.36 | 1.00, 1.01, 0.87, 1.05, 0.54 |
| pub | publiée | 0.86 | 1.16, 1.20, 1.07, 1.08, 2.65 | 0.99, 0.90, 0.92, 0.99, 0.29 |
| pub | grande | 0.80 | 1.25, 1.23, 1.17, 1.37, 1.06 | 1.00, 0.55, 0.92, 0.91, 0.06 |
| unc | petite | 0.85 | 1.17, 1.13, 1.34, 1.00, 1.15 | 1.06, 1.09, 0.90, 1.09, 0.56 |
| unc | publiée | 0.81 | 1.23, 1.46, 1.18, 1.28, 1.94 | 1.07, 0.96, 0.98, 1.04, 0.41 |
| unc | grande | 0.80 | 1.25, 1.24, 1.29, 1.49, 1.13 | 1.04, 0.54, 0.88, 0.93, 0.04 |

## Plafond par noyau et parts du code par défaut (« Final », au centre)

| Langage | K1 | K3 | K4 | K5 | K6 | K7 | K8 | K9 | D1 | D2 | D3 | D4 | D1, mode publié | D1, R1' |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C | 85 | 99 | 95 | 84 | 81 | 81 | 68 | 86 | 71 | 100 | 80 | 91 | 72 | 66 |
| C++ | 84 | 100 | 69 | 93 | 92 | 74 | 100 | 94 | 49 | 97 | 76 | 91 | 58 | 53 |
| Zig | 78 | 100 | 66 | 96 | 87 | 79 | 72 | 93 | 40 | 99 | 55 | 96 | 70 | 64 |
| Odin | 67 | 99 | 66 | 94 | 87 | 84 | 73 | 90 | 65 | 99 | 38 | 88 | 66 | 66 |
| Rust | 83 | 100 | 83 | 86 | 84 | 94 | 77 | 87 | 67 | 100 | 74 | 95 | 67 | 62 |
| Nim | 92 | 99 | 67 | 90 | 82 | 83 | 68 | 92 | 64 | 99 | 71 | 94 | 65 | 67 |
| C3 | 85 | 100 | 66 | 91 | 87 | 88 | 72 | 89 | 62 | 100 | 55 | 89 | 69 | 63 |
| D | 85 | 100 | 82 | 92 | 79 | 86 | 73 | 89 | 58 | 100 | 2 | 79 | 61 | 56 |
| Ada | 75 | 100 | 76 | 89 | 84 | 70 | 79 | 83 | 38 | 100 | 67 | 70 | 38 | 54 |
| Julia | 75 | 97 | 57 | 93 | 90 | 72 | 73 | 73 | 66 | 98 | 7 | 94 | 67 | 65 |
| Fortran | 84 | 100 | 47 | 86 | 73 | 74 | 92 | 84 | 57 | 99 | 82 | 87 | 66 | 60 |
| Chapel | 74 | 98 | 82 | 90 | 84 | 87 | 88 | 91 | 26 | 99 | 55 | 100 | 58 | 53 |
| Mojo | 82 | 100 | 51 | 86 | 82 | 88 | 49 | 85 | 34 | 99 | 49 | 90 | 34 | 43 |
| Swift | 89 | 98 | 45 | 97 | 81 | 80 | 72 | 90 | 33 | 96 | 32 | 82 | 33 | 42 |
| C# | 82 | 99 | 62 | 84 | 63 | 51 | 51 | 81 | 29 | 56 | 36 | 86 | 29 | 27 |
| Go | 69 | 37 | 73 | 76 | 53 | 66 | 58 | 77 | 39 | 97 | 11 | 94 | 40 | 42 |
| Java | 44 | 96 | 49 | 81 | 70 | 64 | 57 | 78 | 34 | 55 | 43 | 95 | 35 | 32 |
| FreePascal | 49 | 100 | 11 | 38 | 30 | 59 | 53 | 51 | 14 | 99 | 48 | 92 | 21 | 19 |
| OxCaml | 63 | 35 | 58 | 60 | 52 | 51 | 44 | 65 | 21 | 49 | 71 | 79 | 22 | 22 |
| Haskell | 46 | 37 | 30 | 86 | 37 | 95 | 71 | 67 | 17 | 75 | 9 | 83 | 17 | 16 |

D1 : code naturel sous R1 (le centre) ; « D1, mode publié » : dans le mode publié de chaque chaîne (centre de « Sans R1 ») ; « D1, R1' » : sans les vérifications qu'une option retire (centre de « R1' au lieu de R1 »). Les variantes de « Final » tirent l'un des trois (A7, A8).

## Ce qui décide de l'ordre (« Final », au centre)

Part de la variance du score au centre que porte chaque composante, parmi les langages d'un groupe (`docs/V5_3.md`, 2) : covariance de son apport au score avec le score, divisée par la variance du score. Les trois piliers somment à 100 % ; les noyaux se partagent la part du plafond, D1 à D4 celle du code par défaut. Une part négative : la composante joue, dans ce groupe, contre l'ordre du score. Le poids affiché est celui de la composante dans le score.

| Composante | Poids affiché | les 20 langages (20) | premier étage (20) | première moitié possible (14) | podium possible (8) |
|---|---|---|---|---|---|
| **Contrôle (grille)** | 35 % | **41 %** | **41 %** | **54 %** | **68 %** |
| **Plafond** | 40 % | **39 %** | **39 %** | **17 %** | **12 %** |
| K1 | 5.0 % | 4.1 % | 4.1 % | 0.4 % | 3.2 % |
| K3 | 5.0 % | 5.2 % | 5.2 % | 0.1 % | 0.2 % |
| K4 | 5.0 % | 8.8 % | 8.8 % | 8.5 % | 3.6 % |
| K5 | 5.0 % | 4.3 % | 4.3 % | 0.1 % | -0.9 % |
| K6 | 5.0 % | 6.9 % | 6.9 % | 0.7 % | 0.3 % |
| K7 | 5.0 % | 2.4 % | 2.4 % | 1.3 % | -0.2 % |
| K8 | 5.0 % | 3.3 % | 3.3 % | 4.2 % | 5.6 % |
| K9 | 5.0 % | 3.4 % | 3.4 % | 1.8 % | -0.2 % |
| **Code par défaut** | 25 % | **21 %** | **21 %** | **29 %** | **21 %** |
| D1, code naturel | 12.5 % | 14.6 % | 14.6 % | 22.3 % | 4.4 % |
| D2, coût de structure | 3.75 % | 3.3 % | 3.3 % | 0.2 % | -0.3 % |
| D3, queues de latence | 3.75 % | 2.7 % | 2.7 % | 5.2 % | 16.0 % |
| D4, hiérarchie mémoire | 5.0 % | 0.4 % | 0.4 % | 0.8 % | 0.5 % |

Écart-type du score au centre dans chaque groupe : 12.3 (les 20 langages), 12.3 (premier étage), 5.2 (première moitié possible), 2.6 (podium possible). Premier étage : C, C++, Zig*, Odin, Rust, Nim, C3, D, Ada, Julia, Fortran, Chapel, Mojo, Swift, C#, Go, Java, FreePascal, OxCaml†, Haskell. Première moitié possible : C, C++, Zig*, Odin, Rust, Nim, C3, D, Ada, Julia, Fortran, Chapel, Mojo, Swift. Podium possible : C, C++, Zig*, Odin, Rust, Nim, C3, D. « Première moitié possible » et « podium possible » : rang plausible commençant à 12 et à 3 ou mieux.

## Tri des écarts du code naturel

Règle (`docs/V5_3.md`, 3) : pour chaque mesure du code naturel, à chaque taille et dans chaque mode du tirage, le temps d'un langage est rapporté à la médiane des temps de 15 pairs, les langages dont la chaîne produit son code machine par LLVM ou par GCC (C, C++, Zig, Odin, Rust, Nim, C3, D, Ada, Julia, Fortran, Chapel, Mojo, Swift, Haskell). Pour les autres langages, ce rapport est divisé par leur niveau : la médiane de leurs rapports à cette taille et dans ce mode, au moins 1. Une cellule est lente à partir de 2.0 (arrondi au dixième), rapide quand elle est au moins 2.0 fois plus rapide que la médiane des pairs ; un couple (langage, mesure) est signalé dans un mode s'il l'est à une taille au moins. Chaque couple signalé est rattaché à une cause : « établie » (un contrôle nommé la montre), « attribuée » (cause probable, sans contrôle propre), « à corriger » (cellule faussée par l'étude, correction à planifier) ou « à examiner » (aucune cause).

44 couples signalés : 29 dont la cause est établie, 15 dont la cause est attribuée, 0 à corriger, 0 à examiner.

| n° | Statut | Cause | Contrôle | Couples |
|---|---|---|---|---|
| 1 | établie | clang fusionne par défaut la multiplication et l'addition du produit scalaire en une FMA (`-ffp-contract=on`), qui allonge la chaîne de dépendance de la somme | le même source compilé par gcc prend 0,45 à 0,51 fois le temps de clang (campagne, « C par gcc ») ; code machine (`docs/V5_3.md`, 8) | C K5 |
| 2 | attribuée | même facteur deux que le produit scalaire de C : fusion en FMA probable (Chapel `--fast`, Mojo, `ghc -mfma`) | aucun contrôle propre ; `docs/HASKELL.md` de l'archive (2) donne à Haskell le temps de C sur K5 | Chapel K5 (mode publié, R1'), Mojo K5, Haskell K5 |
| 3 | établie | GCC vectorise la somme conditionnelle d'octets moins bien que LLVM | le même source C compilé par gcc prend 3,9, 3,6 et 2,5 fois le temps de clang aux trois tailles (campagne, « C par gcc ») | C++ K4, Ada K4, Fortran K4 |
| 4 | établie | vérifications que R1 ajoute au mode publié (débordement des entiers de `-O safe` pour Zig, `--checks` pour Chapel, `-D_GLIBCXX_ASSERTIONS` pour C++, `-Cr -Co` pour FreePascal) : elles empêchent la vectorisation | l'écart disparaît en mode publié ; `docs/V5_1.md`, 2 (Zig) et 9.1 (Chapel) | C++ K9, Zig* K4, Chapel K5 (R1), Chapel Q6, Chapel Q1, Chapel K9, FreePascal K9 |
| 5 | établie | vérifications du mode publié qu'une option retire : contrôle de falsification des conteneurs d'Ada sur K7, bornes d'Ada, de Swift et de Mojo sur leurs tableaux, bornes de Go sur les colonnes de Q6 | l'écart disparaît en R1' ; `docs/V5_1.md`, 9.1 (Ada) ; `docs/SWIFT.md` (2.4) et `docs/MOJO.md` (2) de l'archive ; Go : Q6 naturel prend 2,1 à 2,6 fois son temps sans elles (campagne, `-gcflags=-B`) | Ada K7, Ada K9, Mojo Q1, Mojo K9 (R1, mode publié), Swift K9, Go Q6 |
| 6 | établie | somme conditionnelle que les pairs vectorisent et que la chaîne laisse scalaire : pas de vectoriseur de boucles dans les passes de Mojo ; un branchement par octet en Swift, avec le piège de débordement de `-O` ; pas de vectoriseur automatique pour cette boucle en Go, C#, Java, Haskell et OxCaml | `docs/MOJO.md` (2), `docs/SWIFT.md` (2.4) et `docs/GO.md` (2) de l'archive | Mojo K4, Swift K4, C# K4, Go K4, Java K4, OxCaml† K4, Haskell K4 |
| 7 | attribuée | boucle que les pairs vectorisent et que la chaîne laisse scalaire, sans relecture qui le consigne : somme conditionnelle de FreePascal ; stencil de C# et de Go ; stencil de Mojo une fois ses vérifications retirées | aucun contrôle propre | Mojo K9 (R1'), C# K9, Go K9, FreePascal K4 |
| 8 | attribuée | stencil de Nim sur une `seq` : vérifications de bornes de `-d:release`, et boucle que clang ne vectorise pas même sans elles (Nim lui passe `-fno-strict-aliasing`) | `docs/NIM.md` de l'archive (2), établi pour la forme imbriquée, non refait pour la forme contiguë | Nim K9 |
| 9 | établie | ramasse-miettes de D : chaque nœud de K8 est un `new` de classe | `docs/DLANG.md` de l'archive (2) | D K8 |
| 10 | attribuée | coût d'allocation du type par défaut : comptage de références de la classe de Swift, nœuds de Haskell confiés au ramasse-miettes | aucun contrôle propre ; `docs/SWIFT.md` de l'archive (2.4, point 9) chiffre une part du coût de Swift | Swift K8, Haskell K8 |
| 11 | établie | types par défaut de Haskell : liste chaînée pour K1, `Data.IntMap` pour K7 faute de table de hachage livrée, tableau immuable `UArray` pour K9 | `docs/NATURAL.md` ; `docs/HASKELL.md` de l'archive (1 et 2) | Haskell K1, Haskell K7, Haskell K9 |
| 12 | attribuée | types de bibliothèque par défaut : `TDictionary` de FreePascal (deux recherches par ligne) et `Hashtbl` d'OxCaml pour K7 ; produit scalaire de FreePascal | `docs/NATURAL.md` décrit ces types ; leur part dans l'écart n'a pas de contrôle propre | FreePascal K5, FreePascal K7, OxCaml† K7 |
| 13 | établie | ni C ni Fortran n'ont de table de hachage en bibliothèque standard : leur code naturel est le chaînage des manuels, écrit pour le noyau, au nombre de seaux fixé d'avance sur le nombre de clés et haché par un modulo ; les tables de bibliothèque des pairs grandissent et hachent plus fort. Avantage que la règle du code naturel accepte | `docs/NATURAL.md` (K7, cas discutables) ; sources de `bench/c` et de `bench/fortran` | C K7, Fortran K7 |
| 14 | attribuée | allocation par un ramasse-miettes générationnel : un nœud de K8 coûte un déplacement de pointeur, contre une allocation et une libération chez les pairs | aucun contrôle propre | Java K8, OxCaml† K8 |
| 15 | établie | sans vérification de bornes, LLVM vectorise la boucle naturelle de Q6 d'Odin ; celle des autres pairs reste scalaire | campagne, taille publiée : Odin 48,7 ms avec les bornes, 18,4 ms sans, 13,6 ms pour sa forme SIMD ; C 40,9 ms | Odin Q6 |

| Langage | Mesure | Sens | R1 | Mode publié | R1' | Niveau | Cause | Statut |
|---|---|---|---|---|---|---|---|---|
| C | K5 | lent | **2.0** | **2.1** | **2.1** | 1 | 1 | établie |
| C | K7 | rapide | **0.24** | **0.37** | **0.37** | 1 | 13 | établie |
| C++ | K4 | lent | **4.0** | **3.9** | **3.9** | 1 | 3 | établie |
| C++ | K9 | lent | **4.3** | 1.0 | 1.0 | 1 | 4 | établie |
| Zig* | K4 | lent | **51.1** | 1.0 | 1.0 | 1 | 4 | établie |
| Odin | Q6 | rapide | 0.96 | 1.02 | **0.23** | 1 | 15 | établie |
| Nim | K9 | lent | **3.2** | **3.5** | **2.3** | 1 | 8 | attribuée |
| D | K8 | lent | **2.6** | **2.9** | **2.9** | 1 | 9 | établie |
| Ada | K4 | lent | **3.9** | **3.8** | **3.9** | 1 | 3 | établie |
| Ada | K7 | lent | **7.0** | **7.4** | 1.5 | 1 | 5 | établie |
| Ada | K9 | lent | **4.2** | **4.6** | 1.0 | 1 | 5 | établie |
| Fortran | K4 | lent | **9.6** | **4.1** | **4.1** | 1 | 3 | établie |
| Fortran | K7 | rapide | **0.33** | **0.36** | **0.36** | 1 | 13 | établie |
| Chapel | K5 | lent | **4.5** | **2.0** | **2.0** | 1 | 4, 2 | attribuée |
| Chapel | Q6 | lent | **5.4** | 1.0 | 1.0 | 1 | 4 | établie |
| Chapel | Q1 | lent | **7.0** | 1.0 | 1.1 | 1 | 4 | établie |
| Chapel | K9 | lent | **32.9** | 1.0 | 1.1 | 1 | 4 | établie |
| Mojo | K4 | lent | **5.2** | **5.0** | **5.0** | 1 | 6 | établie |
| Mojo | K5 | lent | **2.0** | **2.0** | **2.0** | 1 | 2 | attribuée |
| Mojo | Q1 | lent | **2.0** | **2.4** | 0.9 | 1 | 5 | établie |
| Mojo | K9 | lent | **15.7** | **17.1** | **2.2** | 1 | 5, 7 | attribuée |
| Swift | K4 | lent | **50.7** | **49.4** | **11.6** | 1 | 6 | établie |
| Swift | K8 | lent | 1.9 | **2.1** | 1.9 | 1 | 10 | attribuée |
| Swift | K9 | lent | **3.3** | **3.6** | 1.0 | 1 | 5 | établie |
| C# | K4 | lent | **29.1** | **27.9** | **26.3** | 1.2 à 2.0 | 6 | établie |
| C# | K9 | lent | **4.3** | **4.4** | **4.7** | 1.2 à 2.0 | 7 | attribuée |
| Go | K4 | lent | **5.7** | **5.2** | **5.9** | 1.1 à 1.5 | 6 | établie |
| Go | Q6 | lent | **2.1** | **2.0** | 1.0 | 1.1 à 1.5 | 5 | établie |
| Go | K9 | lent | **2.8** | **2.8** | **2.9** | 1.1 à 1.5 | 7 | attribuée |
| Java | K4 | lent | **32.1** | **30.1** | **29.4** | 1.4 à 1.7 | 6 | établie |
| Java | K8 | rapide | **0.29** | **0.33** | **0.33** | 1.4 à 1.7 | 14 | attribuée |
| FreePascal | K4 | lent | **19.2** | **20.1** | **17.9** | 2.0 à 4.9 | 7 | attribuée |
| FreePascal | K5 | lent | 1.4 | **2.0** | 1.8 | 2.0 à 4.9 | 12 | attribuée |
| FreePascal | K7 | lent | 1.2 | **2.6** | **2.5** | 2.0 à 4.9 | 12 | attribuée |
| FreePascal | K9 | lent | **3.2** | 1.3 | 1.3 | 2.0 à 4.9 | 4 | établie |
| OxCaml† | K4 | lent | **18.2** | **22.1** | **19.1** | 2.1 à 3.7 | 6 | établie |
| OxCaml† | K7 | lent | **2.2** | **2.5** | **2.5** | 2.1 à 3.7 | 12 | attribuée |
| OxCaml† | K8 | rapide | **0.24** | **0.26** | **0.25** | 2.1 à 3.7 | 14 | attribuée |
| Haskell | K1 | lent | **5.7** | **5.8** | **5.9** | 1 | 11 | établie |
| Haskell | K4 | lent | **4.7** | **4.6** | **4.6** | 1 | 6 | établie |
| Haskell | K5 | lent | **2.4** | **2.4** | **2.3** | 1 | 2 | attribuée |
| Haskell | K7 | lent | **44.3** | **44.9** | **48.3** | 1 | 11 | établie |
| Haskell | K8 | lent | 1.7 | **2.0** | **2.0** | 1 | 10 | attribuée |
| Haskell | K9 | lent | **12.6** | **13.7** | **14.8** | 1 | 11 | établie |

Chaque case : le rapport le plus extrême des trois tailles (lent : rapport au niveau du langage, le plus grand ; rapide : rapport à la médiane des pairs, le plus petit), en gras dans les modes où le couple est signalé. Niveau : 1 pour un pair ; pour les autres, étendue sur les tailles et les modes.

## Forme retenue par « Final », cellule par cellule et taille par taille (estimation ponctuelle)

Chaque case : forme retenue aux tailles petite / publiée / grande (« pub » : une variante publiée) ; rapport de son temps à la meilleure forme publiée, à la taille publiée.

| Langage | K4 | K5 | Q6 | Q1 | Q6 mt | Q1 mt | K7 | K8 | K9 | K9 mt |
|---|---|---|---|---|---|---|---|---|---|---|
| C | k4 tuned/k4 tuned/k4 tuned 0.42 | pub/pub/pub 1.00 | q6 tuned_v/q6 tuned_v/q6 tuned_v 0.71 | pub/pub/pub 1.00 | q6 mt_pool_v/q6 mt_pool_v/q6 mt_pool_v 0.74 | q1 mt_pool/pub/q1 mt_pool 1.00 | pub/pub/pub 1.00 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.35 | k9 tuned_v/pub/k9 tuned_v 1.00 | k9 mt_pool/pub/k9 mt_pool_v 1.00 |
| C++ | k4 tuned/k4 tuned/k4 tuned 0.17 | pub/pub/pub 1.00 | pub/q6 tuned_v/pub 0.99 | pub/pub/pub 1.00 | q6 mt_pool/q6 mt_pool/pub 0.90 | q1 mt_pool/q1 mt_pool/pub 0.96 | pub/pub/pub 1.00 | k8 tuned_val/k8 tuned_val/k8 tuned_val 0.33 | k9 tuned_v/k9 tuned_v/k9 tuned_v 1.00 | k9 mt_pool_v/pub/k9 mt_pool_v 1.00 |
| Zig | k4 tuned/k4 tuned/k4 swar 0.43 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | q6 mt_pool/q6 mt_pool/q6 mt_pool 0.92 | q1 mt_pool/pub/q1 mt_pool 1.00 | pub/pub/pub 1.00 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.45 | pub/pub/pub 1.00 | k9 mt_pool/k9 mt_pool/k9 mt_pool 0.50 |
| Odin | k4 tuned/k4 tuned/k4 tuned 0.54 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | q1 tuned_v/q1 tuned_v/q1 tuned_v 0.47 | q6 mt_pool/pub/pub 1.00 | q1 mt_pool_v/q1 mt_pool_v/q1 mt_pool_v 0.50 | pub/pub/pub 1.00 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.31 | pub/pub/pub 1.00 | k9 mt_pool/pub/pub 1.00 |
| Rust | k4 tuned/k4 tuned/k4 tuned 0.42 | pub/pub/pub 1.00 | q6 tuned_v/q6 tuned_v/q6 tuned_v 0.85 | pub/pub/pub 1.00 | q6 mt_pool_v/q6 mt_pool_v/q6 mt_pool_v 0.92 | q1 mt_pool/pub/pub 1.00 | pub/pub/pub 1.00 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.27 | k9 tuned_v/pub/pub 1.00 | k9 mt_pool/k9 mt_pool_v/k9 mt_pool_v 0.86 |
| Nim | k4 tuned/k4 tuned/k4 tuned 0.52 | pub/pub/pub 1.00 | q6 tuned_v/q6 tuned_v/q6 tuned_v 0.82 | q1 tuned_v/q1 tuned_v/q1 tuned_v 0.57 | q6 mt_pool/q6 mt_pool_v/q6 mt_pool_v 0.81 | q1 mt_pool_v/q1 mt_pool_v/q1 mt_pool_v 0.48 | pub/pub/pub 1.00 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.30 | k9 tuned_v/pub/k9 tuned_v 1.00 | k9 mt_pool/pub/k9 mt_pool_v 1.00 |
| C3 | k4 tuned/k4 tuned/k4 tuned 0.44 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | q1 tuned_v/pub/q1 tuned_v 1.00 | q6 mt_pool/q6 mt_pool/pub 0.72 | q1 mt_pool/q1 mt_pool_v/pub 0.82 | pub/pub/pub 1.00 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.33 | pub/pub/pub 1.00 | k9 mt_pool/pub/k9 mt_pool 1.00 |
| D | k4 tuned/k4 tuned/k4 tuned 0.47 | pub/pub/pub 1.00 | q6 tuned_v/q6 tuned_v/q6 tuned_v 0.75 | pub/pub/pub 1.00 | q6 mt_pool/q6 mt_pool_v/q6 mt_pool_v 0.83 | q1 mt_pool/pub/q1 mt_pool 1.00 | pub/pub/pub 1.00 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.33 | pub/pub/pub 1.00 | k9 mt_pool/pub/k9 mt_pool 1.00 |
| Ada | k4 tuned/k4 tuned/k4 tuned 0.20 | pub/pub/pub 1.00 | q6 tuned_v/q6 tuned_v/pub 0.86 | q1 tuned_v/q1 tuned_v/q1 tuned_v 0.58 | q6 mt_pool/q6 mt_pool/pub 0.68 | q1 mt_pool_v/q1 mt_pool_v/q1 mt_pool_v 0.55 | pub/pub/pub 1.00 | k8 tuned_it/pub/pub 1.00 | pub/pub/pub 1.00 | k9 mt_pool/k9 mt_pool/k9 mt_pool 0.60 |
| Julia | k4 tuned/k4 tuned/k4 tuned 0.51 | k5 tuned_v/k5 tuned_v/k5 tuned_v 0.88 | q6 tuned_v/q6 tuned_v/q6 tuned_v 0.85 | q1 tuned_v/q1 tuned_v/q1 tuned_v 0.34 | q6 mt_pool_v/q6 mt_pool_v/q6 mt_pool_v 0.69 | q1 mt_pool_v/q1 mt_pool_v/q1 mt_pool_v 0.30 | pub/k7 tuned_pf/k7 tuned_pf 0.70 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.25 | k9 tuned_v/k9 tuned_v/k9 tuned_v 0.95 | pub/k9 mt_pool_v/pub 0.95 |
| Fortran | k4 swar/k4 swar/k4 swar 0.25 | k5 rq_acc16/k5 rq_acc16/k5 rq_acc16 0.89 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | k7 tuned_oa/pub/pub 1.00 | k8 tuned_val/k8 tuned_val/k8 tuned_val 0.39 | pub/pub/pub 1.00 | pub/pub/pub 1.00 |
| Chapel | k4 tuned/k4 tuned/k4 tuned 0.62 | pub/pub/pub 1.00 | q6 tuned_v/q6 tuned_v/pub 0.83 | pub/q1 tuned_v/q1 tuned_v 0.88 | q6 mt_pool_v/q6 mt_pool_v/pub 0.75 | q1 mt_pool_v/q1 mt_pool_v/q1 mt_pool_v 0.79 | pub/pub/pub 1.00 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.25 | pub/pub/k9 tuned_v 1.00 | k9 mt_pool_v/pub/k9 mt_pool_v 1.00 |
| Mojo | k4 tuned/k4 tuned/k4 tuned 0.11 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | q1 tuned_v/q1 tuned_v/q1 tuned_v 0.76 | pub/pub/pub 1.00 | q1 mt_pool_v/q1 mt_pool_v/q1 mt_pool_v 0.80 | pub/pub/pub 1.00 | k8 tuned_val/k8 tuned_val/k8 tuned_val 0.74 | pub/pub/pub 1.00 | pub/pub/pub 1.00 |
| Swift | k4 tuned/k4 tuned/k4 tuned 0.65 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | q6 mt_pool/pub/pub 1.00 | q1 mt_pool/pub/q1 mt_pool 1.00 | pub/k7 tuned_pf/pub 0.85 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.33 | pub/pub/pub 1.00 | k9 mt_pool/pub/k9 mt_pool 1.00 |
| C# | k4 tuned/k4 tuned/k4 tuned 0.07 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | q6 mt_pool/q6 mt_pool/pub 0.89 | q1 mt_pool/pub/q1 mt_pool 1.00 | pub/pub/pub 1.00 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.51 | pub/pub/pub 1.00 | k9 mt_pool/k9 mt_pool/k9 mt_pool 0.67 |
| Go | k4 tuned/k4 tuned/k4 tuned 0.07 | pub/k5 tuned_v/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.49 | k9 tuned_v/k9 tuned_v/k9 tuned_v 0.61 | k9 mt_pool_v/k9 mt_pool_v/k9 mt_pool_v 0.84 |
| Java | k4 tuned/k4 tuned/k4 tuned 0.26 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | q1 tuned_v/q1 tuned_v/q1 tuned_v 0.51 | q6 mt_pool/q6 mt_pool/q6 mt_pool 0.96 | q1 mt_pool_v/q1 mt_pool_v/q1 mt_pool_v 0.52 | k7 rq_iso/k7 rq_iso/k7 rq_iso 0.75 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.61 | pub/k9 tuned_v/k9 tuned_v 0.84 | k9 mt_pool/k9 mt_pool_v/pub 0.67 |
| FreePascal | k4 swar/k4 swar/k4 swar 0.29 | k5 tuned_v/k5 tuned_v/k5 tuned_v 0.83 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | q6 mt_pool/pub/q6 mt_pool 1.00 | q1 mt_pool/pub/pub 1.00 | pub/pub/pub 1.00 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.42 | pub/pub/pub 1.00 | k9 mt_pool/k9 mt_pool/k9 mt_pool 0.83 |
| OxCaml | k4 tuned/k4 tuned/k4 tuned 0.04 | k5 tuned_v/k5 tuned_v/k5 tuned_v 0.03 | q6 tuned_v/q6 tuned_v/q6 tuned_v 0.28 | q1 tuned_v/q1 tuned_v/q1 tuned_v 0.76 | q6 mt_pool_v/q6 mt_pool_v/q6 mt_pool_v 0.29 | q1 mt_pool_v/q1 mt_pool_v/q1 mt_pool_v 0.79 | pub/k7 tuned_oa/k7 tuned_pf 0.94 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.74 | k9 tuned_v/k9 tuned_v/k9 tuned_v 0.57 | k9 mt_pool_v/k9 mt_pool_v/k9 mt_pool_v 0.38 |
| Haskell | k4 tuned/k4 tuned/k4 tuned 0.23 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | pub/pub/pub 1.00 | k8 tuned_it/k8 tuned_it/k8 tuned_it 0.39 | pub/pub/pub 1.00 | pub/pub/pub 1.00 |

## Campagne

Écart entre la passe la plus lente et la plus rapide d'une cellule : médiane 13.4 % ; 919 cellules sur 2512 au-delà de 20 %. Une fois retiré l'effet commun de chaque groupe dans chaque passe (A5) : médiane 11.5 % ; 832 cellules au-delà de 20 %.

Effet commun d'un groupe dans une passe (A5) : médiane des valeurs absolues 1.7 % ; le plus fort : 12.9 % (k7 pub, passe 0).

Borne à quatre fils (STREAM triad sur 4 fils) : 42.9 Go/s avec la sonde corrigée (A6) ; relevé d'origine : 152.8 Go/s.

Machine de chaque groupe et de chaque passe :

* machine 38 : 69 groupes

Effet de machine : sans objet, une seule machine a mesuré la campagne.

## Cellules

* OxCaml, mesures d'OCaml, OxCaml, source d'OCaml seule, Campagne telle que mesurée : formes ou cellules substituées manquantes : OxCaml cv k5|tuned_v| (pub), OxCaml cv k7|tuned_pf| (small), OxCaml cv k9|mt_pool_v| (small), OxCaml cv k9|tuned_v| (small), OxCaml cv k6|mt_pool_v|q1 (small), OxCaml cv k6|tuned_v|q1 (small), OxCaml cv k6|mt_pool_v|q6 (small), OxCaml cv k6|tuned_v|q6 (small), OxCaml cv k5|tuned_v| (l2), OxCaml cv k7|tuned_pf| (pub), OxCaml cv k9|mt_pool_v| (pub), OxCaml cv k9|tuned_v| (pub), OxCaml cv k6|mt_pool_v|q1 (pub), OxCaml cv k6|tuned_v|q1 (pub), OxCaml cv k6|mt_pool_v|q6 (pub), OxCaml cv k6|tuned_v|q6 (pub), OxCaml cv k5|tuned_v| (l3), OxCaml cv k7|tuned_pf| (large), OxCaml cv k9|mt_pool_v| (large), OxCaml cv k9|tuned_v| (large), OxCaml cv k6|mt_pool_v|q1 (large), OxCaml cv k6|tuned_v|q1 (large), OxCaml cv k6|mt_pool_v|q6 (large), OxCaml cv k6|tuned_v|q6 (large) ; cellules de la base remplies (temps le plus lent des autres langages) : aucune

Processeur des enregistrements : 6/173/1 Intel(R) Xeon(R) Processor @ 2.30GHz (8139 enregistrements) ; C par gcc : 6/173/1 Intel(R) Xeon(R) Processor @ 2.30GHz (420 enregistrements).

Processus écartés : 0 ; cellules non exécutées (étalonnage hors mémoire ou hors durée) : 0 ; vol de temps > 5 % après reprise : 0.

C par gcc : processus écartés : 0 ; cellules non exécutées (étalonnage hors mémoire ou hors durée) : 0 ; vol de temps > 5 % après reprise : 0.
