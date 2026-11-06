# Remarque sur FreePascal : errata, formes de la remarque, 3.2.4-rc2 et branche main

Plan : `docs/FPC.md`, section 5. Mesures : `results/raw_fpc_rq/` (machine 26, Emerald Rapids, 7 processus par cellule). Code : `analysis/fpc_remark.py`. Processus rejetés : aucun.
Contrôle : le scénario Avant (grille d'avant la remarque) reproduit F-E de `results/fpc_check.json` (écart maximal 0.0e+00).

## Rapports au binaire publié (machine 26)

Moyennes géométriques des médianes de processus ; intervalles à 95 % par bootstrap. `branchless_ptr` est rapporté à `branchless_unsorted` du binaire publié.

| Cellule | publié (ms) | 3.2.4-rc2 | main | Length (3.2.2) | mieux (3.2.2) | main, Length et mieux | main sans -Sv |
|---|---|---|---|---|---|---|---|
| k1:natural:energy | 36,974 | 0,991 [0,971–1,012] | 1,001 [0,976–1,028] | 0,947 [0,923–0,974] |  | 0,998 [0,974–1,021] |  |
| k1:aos:energy | 29,783 | 1,026 [1,012–1,041] | 1,023 [1,008–1,038] |  |  |  |  |
| k1:soa:energy | 3,715 | 1,082 [0,991–1,201] | 1,353 [1,303–1,415] |  |  |  | 1,456 [1,388–1,532] |
| k1:natural_shuffled:energy | 35,969 | 1,020 [1,002–1,040] | 1,029 [1,002–1,062] | 0,979 [0,958–1,001] |  | 1,023 [1,004–1,043] |  |
| k2:tuned:16384 | 7,531 | 0,995 [0,985–1,002] | 0,994 [0,983–1,003] |  |  |  |  |
| k2:tuned:262144 | 24,367 | 1,006 [0,982–1,029] | 0,991 [0,972–1,008] |  |  |  |  |
| k2:tuned:8388608 | 155,759 | 1,001 [0,984–1,021] | 1,010 [0,987–1,037] |  |  |  |  |
| k3:rmw_packed | 2945,130 | 0,985 [0,969–1,002] | 1,023 [1,000–1,043] |  |  |  |  |
| k3:rmw_padded | 341,668 | 0,997 [0,983–1,010] | 0,918 [0,901–0,937] |  |  |  |  |
| k3:sw_packed | 14,846 | 0,989 [0,955–1,025] | 1,045 [0,975–1,153] |  |  |  |  |
| k3:sw_padded | 16,217 | 0,819 [0,773–0,869] | 0,884 [0,804–0,988] |  |  |  |  |
| k4:natural_unsorted | 96,145 | 0,954 [0,898–0,989] | 0,858 [0,806–0,891] | 0,961 [0,904–0,997] |  | 0,861 [0,810–0,894] |  |
| k4:natural_sorted | 19,492 | 0,889 [0,864–0,914] | 0,550 [0,520–0,586] | 0,842 [0,823–0,858] |  | 0,503 [0,456–0,551] |  |
| k4:branchless_unsorted | 17,568 | 0,995 [0,979–1,009] | 0,890 [0,861–0,923] |  | 0,754 [0,685–0,884] | 0,700 [0,685–0,715] |  |
| k6:natural:q6 | 138,737 | 1,024 [1,017–1,032] | 0,550 [0,544–0,555] | 1,021 [1,013–1,030] |  | 0,505 [0,501–0,509] |  |
| k6:natural:q1 | 73,221 | 1,029 [0,985–1,106] | 0,963 [0,951–0,976] | 1,002 [0,989–1,015] |  | 0,963 [0,950–0,977] |  |
| k6:tuned:q6 | 29,805 | 1,015 [0,991–1,045] | 0,961 [0,946–0,978] |  |  |  |  |
| k6:tuned:q1 | 57,585 | 1,003 [0,968–1,045] | 0,831 [0,807–0,852] |  |  |  |  |
| k6:mt:q6 | 8,872 | 1,070 [0,921–1,240] | 1,093 [0,901–1,339] |  |  |  |  |
| k6:mt:q1 | 16,165 | 1,078 [0,878–1,277] | 0,919 [0,753–1,116] |  |  |  |  |
| k7:natural | 4322,643 | 0,402 [0,383–0,424] | 0,390 [0,369–0,411] | 0,980 [0,944–1,023] |  | 0,393 [0,376–0,413] |  |
| k7:tuned | 170,644 | 0,988 [0,975–1,002] | 0,946 [0,913–0,993] |  |  |  |  |
| k8:natural | 1008,090 | 0,988 [0,972–1,004] | 0,879 [0,863–0,894] |  |  |  |  |
| k8:tuned | 326,194 | 0,997 [0,988–1,005] | 1,028 [1,017–1,039] |  | 0,383 [0,377–0,391] | 0,400 [0,394–0,406] |  |
| k5:natural | 383,270 | 0,998 [0,992–1,003] | 0,251 [0,248–0,253] | 0,247 [0,245–0,250] |  | 0,246 [0,244–0,248] |  |
| k5:tuned | 28,940 | 0,998 [0,988–1,009] | 0,953 [0,943–0,962] |  | 0,677 [0,663–0,696] | 0,425 [0,397–0,481] | 1,152 [1,140–1,163] |
| k9:natural | 32,584 | 1,001 [0,970–1,032] | 1,332 [1,248–1,466] |  |  |  |  |
| k9:tuned | 24,839 | 1,032 [0,983–1,099] | 1,031 [0,986–1,090] |  |  |  |  |
| k9:mt | 9,200 | 1,014 [0,929–1,104] | 1,087 [1,006–1,181] |  |  |  |  |
| k4:branchless_ptr | 17,568 |  |  |  | 0,711 [0,697–0,728] | 0,480 [0,467–0,496] |  |

Latences de K8 naturel (rapports, colonne par colonne) : fpc_rc2 p50 0,97, p90 1,02, p99 1,06, p99,9 1,64, max 1,58 ; fpc_main p50 0,87, p90 0,93, p99 0,94, p99,9 1,11, max 1,85.

Meilleure forme sous main (R-main-mieux) : k1:natural:energy fpc_main_mieux ; k1:natural_shuffled:energy fpc_main_mieux ; k4:natural_sorted fpc_main_mieux ; k4:branchless_unsorted fpc_main_mieux:branchless_ptr ; k6:natural:q6 fpc_main_mieux ; k6:natural:q1 fpc_main_mieux ; k8:tuned fpc_main_mieux ; k5:natural fpc_main_mieux ; k5:tuned fpc_main_mieux (les autres cellules : `fpc_main`).

## FreePascal / C (information)

| Cellule | témoin | machine 26 [IC 95 %] | machine 25 | remarque (clang 18) | formes de la remarque, machine 26 | main, machine 26 |
|---|---|---|---|---|---|---|
| k4:branchless_unsorted | c | 10,41 [9,08–11,25] | 11,16 | — | 7,85 [6,53–9,63] | 9,26 [7,99–10,18] |
| k4:natural_unsorted | c | 61,74 [59,60–65,52] | 54,40 | 44,00 | 59,31 [58,76–59,96] | 52,94 [52,35–53,61] |
| k7:natural | c | 14,79 [14,18–15,35] | 15,36 | 13,00 | 14,50 [14,05–14,97] | 5,76 [5,49–6,03] |
| k8:natural | c | 1,45 [1,42–1,48] | 1,46 | 1,35 |  | 1,27 [1,24–1,30] |
| k8:tuned | c | 1,17 [1,16–1,17] | 1,17 | 1,13 | 0,45 [0,44–0,46] | 1,20 [1,19–1,21] |
| k9:natural | c | 2,47 [2,39–2,56] | 2,41 | 2,60 |  | 3,30 [3,09–3,62] |
| k9:tuned | c | 1,87 [1,79–1,94] | 1,72 | 2,20 |  | 1,92 [1,83–2,03] |
| k5:natural | c_er | 2,07 [2,05–2,08] | 2,07 | 2,05 | 0,51 [0,51–0,52] | 0,52 [0,51–0,52] |
| k5:tuned | c_er | 7,67 [6,79–8,28] | 7,46 | 8,20 | 5,19 [4,55–5,64] | 7,31 [6,48–7,86] |

K5 tuned face au C natif (`c_er`) : fpc_asm 1,39 [1,20–1,58] ; fpc_main_asm 1,03 [0,90–1,13] ; fpc 7,67 [6,78–8,28] ; fpc_mieux 5,19 [4,58–5,63] ; fpc_main_mieux 3,26 [2,76–3,75] (`fpc_asm`, `fpc_main_asm` : assembleur en ligne, hors des règles du banc).

## Scénarios (analyse globale de la v3 rejouée, 20 000 variantes)

| Scénario | Score | C | E | D | rang espéré | place | rang à 90 % |
|---|---|---|---|---|---|---|---|
| Avant | 47,44 | 60,5 | 36,33 | 46,9 | 16,71 | 16e | [15, 19] |
| R-C2 | 48,31 | 63,0 | 36,33 | 46,9 | 16,58 | 16e | [15, 19] |
| R-E | 48,06 | 62,3 | 36,33 | 46,9 | 16,66 | 16e | [15, 19] |
| R-len-K5 | 48,20 | 62,3 | 36,33 | 47,5 | 16,58 | 16e | [15, 19] |
| R-len | 48,21 | 62,3 | 36,33 | 47,5 | 16,57 | 16e | [15, 19] |
| R-mieux | 51,35 | 62,3 | 44,55 | 46,9 | 15,91 | 16e | [14, 18] |
| R-mieux-ptr | 51,48 | 62,3 | 44,87 | 46,9 | 15,89 | 16e | [14, 18] |
| R-mieux-len | 51,50 | 62,3 | 44,55 | 47,5 | 15,82 | 16e | [14, 18] |
| R-rem-3 | 50,73 | 60,5 | 44,55 | 46,9 | 15,96 | 16e | [14, 18] |
| R-rem-C2-3 | 51,60 | 63,0 | 44,55 | 46,9 | 15,83 | 16e | [14, 18] |
| R-rc2 | 47,37 | 62,3 | 36,70 | 43,6 | 16,90 | 16e | [15, 19] |
| R-main | 47,62 | 62,3 | 36,39 | 45,1 | 16,78 | 16e | [15, 19] |
| R-main-grille | 49,89 | 68,8 | 36,39 | 45,1 | 16,42 | 16e | [14, 19] |
| R-main-mieux | 52,64 | 62,3 | 48,92 | 45,1 | 15,68 | 16e | [14, 17] |
| R-main-mieux-grille | 54,92 | 68,8 | 48,92 | 45,1 | 15,30 | 15e | [13, 17] |
| R-rc2-t (hors plan) | 48,31 | 62,3 | 36,70 | 47,3 | 16,57 | 16e | [15, 19] |
| R-main-t (hors plan) | 48,37 | 62,3 | 36,39 | 48,1 | 16,48 | 16e | [14, 19] |
| R-main-mieux-grille-t (hors plan) | 55,66 | 68,8 | 48,92 | 48,1 | 14,95 | 15e | [12, 17] |

Voisins dans R-E : devant C# (FreePascal devant dans 18 % des variantes) ; derrière Java (FreePascal devant dans 54 % des variantes).

Écarts des autres langages entre Avant et R-E : rang espéré -0,000 à 0,021 ; score 0,000 à 0,000.

