# Sonde de la grille de capacités pour BQN (CBQN 0.12.0, binaire du banc publié) : chaque ligne
# CAP;<id>;<note>;<preuve exécutée> (docs/BQN.md, 2.3). Les absences sont des notes, appuyées sur la documentation
# livrée avec CBQN (docs/system.md, docs/commands.md).
Cap ← {𝕊 id‿n‿s: •Out ∾⟨"CAP;", id, ";", n, ";", s⟩}
R ← {'-'¨⌾(('¯'=𝕩)⊸/) 𝕩} •Fmt
Ty ← •internal.Type
Live ← {𝕤 ⋄ •internal.GC @ ⋄ 1 ⊑ •internal.HeapStats @}

# A1 : une matrice n×16 de flottants est un seul bloc de f64 ; une liste d'espaces de noms est une liste de références
mat ← 1000‿16 ⥊ 0.5 + ↕16
MakeNs ← {x⇐0⊑𝕩 ⋄ vx⇐1⊑𝕩}
nsl ← MakeNs˘ 1000‿2 ⥊ 0.5
Cap "A1"‿"0.5"‿("matrice 1000×16 : " ∾ (Ty mat) ∾ " d'un seul tenant (rangées homogènes en ligne) ; liste d'espaces de noms : " ∾ (Ty nsl) ∾ " (références) ; pas d'enregistrement hétérogène en ligne")
Cap "A2"‿"0"‿"ni ordre ni taille de champs : un espace de noms n'a pas de disposition (les types de structure de •FFI ne servent qu'aux appels)"
# A3 : booléens rangés à 1 bit, réinterprétation bit à bit
b ← 1‿0‿1‿1‿0‿0‿0‿1
Cap "A3"‿"0.5"‿("booléens rangés à 1 bit (" ∾ (Ty b) ∾ ") ; ⟨1,'u'⟩‿⟨8,'i'⟩ •bit._cast 8 bits → " ∾ (R ⟨1,'u'⟩‿⟨8,'i'⟩ •bit._cast b) ∾ " ; pas de champs de bits dans un enregistrement")
Cap "A4"‿"0"‿"aucun contrôle de l'alignement"
Cap "A5"‿"0.5"‿("•bit._cast : 1.0 en f64 → deux i32 " ∾ (R ⟨64,'f'⟩‿⟨32,'i'⟩ •bit._cast ⟨1.0⟩) ∾ " (tableaux seulement ; ni union ni f32)")
t16 ← ⍉ mat
Cap "A6"‿"0.5"‿("⍉ fait passer la matrice 1000×16 (une particule par rangée) en 16×1000 (un champ par rangée, " ∾ (Ty t16) ∾ ") : AoS et SoA dans le même conteneur, sans champs nommés")
r3 ← 2‿16‿4 ⥊ 0.25
Cap "A7"‿"0.5"‿("tableau de rang 3 (2×16×4, " ∾ (Ty r3) ∾ ") : sous-tableaux fixes en ligne, homogènes seulement")
Cap "A8"‿"0.5"‿("stockage étroit choisi par l'implémentation : 1‿2‿3 " ∾ (Ty 1‿2‿3) ∾ ", 300‿1 " ∾ (Ty 300‿1) ∾ ", 70000‿1 " ∾ (Ty 70000‿1) ∾ ", 0.5‿1 " ∾ (Ty 0.5‿1) ∾ " ; •bit._cast force i8/i16/i32 ; pas de flottant 32 ou 16 bits")
# B1 : comptage de références, et un ramasse-miettes traçant automatique
x ← ↕1000
Cap "B1"‿"0.5"‿("comptage de références (•internal.Refc ↕1000 : " ∾ (R •internal.Refc x) ∾ ") ; ramasse-miettes traçant automatique, désactivable seulement par la commande )gc disable du REPL (docs/commands.md)")
Cap "B2"‿"0"‿"aucun allocateur à choisir ni arène"
m0 ← Live @
s ← {𝕩 + 1}⍟100000 0
Cap "B3"‿"0"‿("nombres jamais boxés (100 000 additions scalaires : tas vivant " ∾ (R (Live @) - m0) ∾ " octets de plus) ; tout tableau est sur le tas")
Cap "B4"‿"0"‿"chaque primitive alloue son résultat (sauf mise à jour en place d'un tableau non partagé)"
# B5 : pointeurs bruts par •FFI (malloc de la libc, écriture et relecture)
malloc ← ↑‿"libc.so.6" •FFI "*"‿"malloc"‿">u64"
free ← ↑‿"libc.so.6" •FFI ""‿"free"‿">*"
ptr ← Malloc 64
pw ← ptr.Cast "i32"
pw.Write 123456
rd ← pw.Read 0
Free ptr
Cap "B5"‿"0.5"‿("pointeurs par •FFI seulement : malloc, Write 123456, Read " ∾ (R rd) ∾ " (objets pointeurs Read/Write/Add/Cast)")
Cap "C1"‿"0"‿"aucun type vectoriel : les primitives travaillent sur des tableaux entiers"
Cap "C2"‿"0"‿"aucune intrinsèque"
# C4 : +´ ordonnée contre •math.Sum réassociée
f ← 1 ÷ 1 + ↕1000000
d1 ← +´ f
d2 ← •math.Sum f
Cap "C4"‿"0.5"‿("+´ ordonnée " ∾ (R d1) ∾ " ; •math.Sum (somme vectorielle réassociée) " ∾ (R d2) ∾ " ; écart " ∾ (R d1 - d2) ∾ " ; pour la somme seulement")
Cap "C5"‿"0"‿"ni threads ni boucle parallèle"
Cap "D1"‿"0"‿"pas de threads (la bibliothèque système n'en a pas ; CBQN n'est pas réentrant)"
Cap "D2"‿"0"‿"aucun atomique"
Cap "D3"‿"0"‿"aucune aide de ligne de cache"
Cap "D4"‿"0"‿"pas d'affinité (sched_setaffinity seulement par •FFI vers la libc)"
Cap "D5"‿"0"‿"ni barrière ni pause"
Cap "E1"‿"0.5"‿"interprète de bytecode avec un JIT x86-64 actif par défaut (src/vm/vm.h : JIT_START 2, une fonction compilée après deux appels) ; code machine visible seulement avec une option de construction (USE_PERF)"
Cap "E2"‿"0"‿"aucun"
Cap "E3"‿"0"‿"aucun"
Cap "E4"‿"0"‿"aucun"
Cap "E5"‿"0"‿"aucune annotation (valeurs immuables)"
Cap "E6"‿"0"‿("indices toujours vérifiés (5 ⊑ ↕3 : « " ∾ ({5 ⊑ 𝕩}⎊{𝕤 ⋄ •CurrentError @} ↕3) ∾ " ») ; aucun moyen de les désactiver")
Cap "E7"‿"0"‿"ni calcul à la compilation ni génériques"
r34 ← 3‿4‿5 ⥊ ↕60
Cap "F1"‿"1"‿("tableaux multidimensionnels natifs, contigus en ordre des rangées (3×4×5 : " ∾ (Ty r34) ∾ ", (⟨1,2,3⟩⊑r) = " ∾ (R ⟨1,2,3⟩ ⊑ r34) ∾ ")")
Cap "F2"‿"0"‿"aucun"
Cap "F3"‿"0.5"‿("entiers exacts jusqu'à 2⋆53 (f64) ; enveloppement par modulo : (2⋆32)|¯1 = " ∾ (R (2⋆32) | ¯1) ∾ ", par •bit._cast 300 → i8 " ∾ (R ⟨16,'i'⟩‿⟨8,'i'⟩ •bit._cast ⟨300⟩) ∾ " ; pas de type entier de largeur fixe")
# F4 : •file.MapBytes projette le fichier ; •bit._cast le réinterprète sans le recopier
mb0 ← Live @
mp ← •file.MapBytes "/opt/msdata/k7_keys.u32"
mb1 ← Live @
ki ← ⟨8,'c'⟩‿⟨32,'i'⟩ •bit._cast mp
mb2 ← Live @
Cap "F4"‿"1"‿("•file.MapBytes projette 64 Mio (" ∾ (Ty mp) ∾ ", tas vivant + " ∾ (R mb1 - mb0) ∾ " o) ; •bit._cast en i32 sans copie (" ∾ (Ty ki) ∾ ", tas + " ∾ (R mb2 - mb1) ∾ " o) ; somme des clés " ∾ R +´ 1024 | ki)
