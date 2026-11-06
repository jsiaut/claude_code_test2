# Implémentation BQN : CBQN 0.12.0, construit pour la cible de l'hôte des données (bench/bqn/build.sh,
# bench/bqn_er/build.sh). Voir docs/SPEC.md et
# docs/BQN.md. BQN n'a ni threads ni coroutines : les quatre « threads » de K3 et les variantes « mt » s'exécutent en
# séquence sur un seul cœur, comme pour Lua ; pas de K10. Horloge : •MonoTime (monotone, résolution de la
# nanoseconde). Les flottants de CBQN sont des f64 : les fichiers f32 sont décodés hors chrono, par arithmétique exacte
# (•bit._cast ne connaît ni f32 ni u32).
# Appel (bench/bqn/run) : BQN ms.bqn <dossier des données> <échauffements> <noyau> <variante> <répétitions> [paramètre]

dir‿warmS‿k‿v‿repsS ← 5↑•args
p ← 5 ⊑ •args ∾ <""
warm ← •ParseFloat warmS
reps ← •ParseFloat repsS

# ------------------------------------------------------------------ harnais
IntStr ← {𝕩<10 ? ⥊'0'+𝕩 ; (𝕊 ⌊𝕩÷10) ∾ '0'+10|𝕩}         # entier ≥ 0 exact (< 2⋆53)
Fix9 ← {ns ← ⌊0.5+1e9×𝕩 ⋄ (IntStr ⌊ns÷1e9) ∾ "." ∾ ¯9↑"00000000"∾IntStr 1e9|ns}
FltStr ← {'-'¨⌾(('¯'=𝕩)⊸/) 𝕩} •Repr                     # flottant lisible par le pilote (¯ → -)
Emit ← {𝕊 r‿t‿c: •Out ∾⟨"RESULT;",k,";",v,";",p,";",IntStr r,";",Fix9 t,";",c⟩}
Meta ← {•Out "META;"∾𝕩}
_bench ← {   # 𝔽 : la section chronométrée ; elle rend la somme de contrôle (chaîne)
  Kern ← 𝔽
  {𝕊 r: t0 ← •MonoTime @ ⋄ c ← Kern @ ⋄ t ← (•MonoTime @) - t0 ⋄ {𝕤 ⋄ Emit r‿t‿c}⍟(r≥0) @}¨ (-warm) + ↕warm+reps
  @
}

# ------------------------------------------------------------------ données (hors chrono)
Path ← (dir∾"/")⊸∾
Bytes ← •file.Bytes Path
I32 ← ⟨8,'c'⟩‿⟨32,'i'⟩ •bit._cast Bytes
I8 ← ⟨8,'c'⟩‿⟨8,'i'⟩ •bit._cast Bytes                   # octets < 128 seulement (colonnes de K6)
U8 ← @ -˜ Bytes                                           # octets 0..255 (entiers 16 bits)
U32 ← {𝕩 + 4294967296 × 𝕩 < 0} I32
F32 ← {   # binaire32 → f64, exact : signe, exposant, mantisse (dénormaux et zéros compris)
  w ← I32 𝕩
  sg ← w < 0
  u ← w + 4294967296 × sg
  e ← 256 | ⌊ u ÷ 8388608
  m ← 8388608 | u
  (1 - 2 × sg) × (m + 8388608 × e > 0) × 2 ⋆ (e ⌈ 1) - 150
}

# ------------------------------------------------------------------ K1
n1 ← 4194304
Energy ← {𝕊 vx‿vy‿vz‿m: +´ 0.5 × m × ((vx×vx) + vy×vy) + vz×vz}
K1Nat ← {Energy <˘ ⍉ 3‿4‿5‿9⊸⊏˘ 𝕩}                       # naturel : matrice n×16, colonnes extraites puis calcul
K1Tun ← {𝕊 vx‿vy‿vz‿m: •math.Sum 0.5 × m × ((vx×vx) + vy×vy) + vz×vz}
Live ← {𝕤 ⋄ •internal.GC @ ⋄ 1 ⊑ •internal.HeapStats @}
Split ← (¬-˜⊢×·+`»⊸>)∘≠⊔⊢                                  # 𝕨 : séparateur
Rss ← {𝕤 ⋄ 4096 × •ParseFloat 1 ⊑ ' ' Split 1 ⊑ •SH "sh"‿"-c"‿"cat /proc/$PPID/statm"}   # pages résidentes (/proc se lit vide par •file)
K1Load ← {𝕤 ⋄ n1‿16 ⥊ F32 "k1_particles.f32"}
K1Zero ← {𝕤 ⋄ Emit 0‿0‿"0"}
K1Fp ← {𝕤    # empreinte (docs/SPEC.md, K1) : P1 tampon brut chargé, P2 collection naturelle construite
  raw ← Bytes "k1_particles.f32"
  m1 ← Live @ ⋄ r1 ← Rss @
  ps ← K1Load @
  m2 ← Live @ ⋄ r2 ← Rss @
  Meta "mem;live;" ∾ (IntStr m1) ∾ ";" ∾ IntStr m2
  Meta "rss;" ∾ (IntStr r1) ∾ ";" ∾ IntStr r2
  •internal.Keep raw
  Emit 0‿0‿(FltStr K1Nat ps)
}
K1Soa ← {𝕤
  Meta "soa_repr;16 listes de f64 (BQN n'a pas de flottant 32 bits) ; 4 des 16 champs extraits"
  fs ← 3‿4‿5‿9 ⊏ <˘ ⍉ K1Load @
  {𝕤 ⋄ FltStr K1Tun fs} _bench @
}
K1Aos ← {𝕤
  Meta "aos_repr;matrice n×16 de f64 (pas d'enregistrement valeur ni de flottant 32 bits)"
  ps ← K1Load @
  {𝕤 ⋄ FltStr K1Tun <˘ ⍉ 3‿4‿5‿9⊸⊏˘ ps} _bench @           # extraction la plus rapide essayée (docs/BQN.md, 2.4)
}
K1Shuf ← {𝕤
  ps ← (U32 "k1_perm.u32") ⊏ K1Load @                     # ligne j ← ligne perm[j] (valeurs recopiées)
  {𝕤 ⋄ FltStr K1Nat ps} _bench @
}
K1N ← {𝕤
  ps ← K1Load @
  {𝕤 ⋄ FltStr K1Nat ps} _bench @
}
# sensibilité (docs/BQN.md, 2.2) : la lecture littérale de « type enregistrement » ; un espace de noms par particule
# (16 champs nommés) dans une liste, mélangée ou non
MakeNs ← {x⇐0⊑𝕩 ⋄ y⇐1⊑𝕩 ⋄ z⇐2⊑𝕩 ⋄ vx⇐3⊑𝕩 ⋄ vy⇐4⊑𝕩 ⋄ vz⇐5⊑𝕩 ⋄ ax⇐6⊑𝕩 ⋄ ay⇐7⊑𝕩 ⋄ az⇐8⊑𝕩 ⋄ mass⇐9⊑𝕩
  charge⇐10⊑𝕩 ⋄ radius⇐11⊑𝕩 ⋄ temp⇐12⊑𝕩 ⋄ pressure⇐13⊑𝕩 ⋄ energy⇐14⊑𝕩 ⋄ density⇐15⊑𝕩}
K1NsE ← {+´ {0.5 × 𝕩.mass × ((𝕩.vx × 𝕩.vx) + 𝕩.vy × 𝕩.vy) + 𝕩.vz × 𝕩.vz}¨ 𝕩}
K1Ns ← {𝕤
  Meta "natural_ns_repr;liste de 4 194 304 espaces de noms de 16 champs"
  ns ← MakeNs˘ K1Load @
  {𝕤 ⋄ FltStr K1NsE ns} _bench @
}
K1NsShuf ← {𝕤
  ns ← (U32 "k1_perm.u32") ⊏ MakeNs˘ K1Load @                # références réordonnées : parcours aléatoire en mémoire
  {𝕤 ⋄ FltStr K1NsE ns} _bench @
}
Unknown ← {𝕤 ⋄ •Out "variante inconnue : " ∾ v ⋄ •Exit 1}
_variant_ ← {(⊑ 𝕗 ⊐ <v) ◶ (𝕘 ∾ ⟨Unknown⟩) 𝕩}                    # choix de la fonction par le nom de la variante
RunK1 ← "footprint0"‿"footprint_raw"‿"footprint"‿"soa"‿"aos"‿"natural_shuffled"‿"natural"‿"natural_ns"‿"natural_ns_shuffled" _variant_ ⟨K1Zero, K1Zero, K1Fp, K1Soa, K1Aos, K1Shuf, K1N, K1Ns, K1NsShuf⟩

# ------------------------------------------------------------------ K2
RunK2 ← {𝕤
  a ← I32 "k2_chase_"∾p∾".u32"                              # tableau d'entiers 32 bits (le plus compact)
  {𝕤 ⋄ IntStr ⊑⟜a⍟4200000 0} _bench @
}

# ------------------------------------------------------------------ K3
RunK3 ← {𝕤
  Meta "k3_mechanism;pas de threads ni d'atomiques en BQN : 4 « threads » exécutés en séquence sur un seul cœur, compteur mis à jour dans le tableau (1⊸+⌾(i⊸⊑))"
  stride ← ("padded" ≡ ¯6↑v) ⊑ 1‿32                        # 32 × 4 = 128 octets (tableau i32 dès 32 768)
  {𝕤
    c ← (4×stride) ⥊ 0
    {𝕊 t: c ↩ 1⊸+⌾((t×stride)⊸⊑)⍟33554432 c}¨ ↕4
    IntStr +´ c
  } _bench @
}

# ------------------------------------------------------------------ K4
RunK4 ← {𝕤
  d ← U8 "k4_bytes.u8"
  {v ≡ "branchless_unsorted" ? {𝕤 ⋄ IntStr +´ d × 128 ≤ d} _bench @
   ; v ≡ "natural_sorted" ? s ← ∧ d ⋄ {𝕤 ⋄ IntStr +´ (128 ≤ s) / s} _bench @
   ; {𝕤 ⋄ IntStr +´ (128 ≤ d) / d} _bench @}
}

# ------------------------------------------------------------------ K5
RunK5 ← {𝕤
  a ← F32 "k5_a.f32" ⋄ b ← F32 "k5_b.f32"
  # le tableau a traverse chaque itération (état de ⍟) : aucune itération ne peut réutiliser la précédente
  {v ≡ "tuned" ? {𝕤 ⋄ FltStr ⊑ {𝕊 d‿x: ⟨•math.Sum x × b, x⟩}⍟65536 0‿a} _bench @
   ; {𝕤 ⋄ FltStr ⊑ {𝕊 d‿x: ⟨+´ x × b, x⟩}⍟65536 0‿a} _bench @}
}

# ------------------------------------------------------------------ K6
n6 ← 16777216
Q6Nat ← {𝕊 sd‿qt‿dc‿pr: +´ (((8766 ≤ sd) ∧ sd < 9131) ∧ ((5 ≤ dc) ∧ dc ≤ 7) ∧ qt < 24) / pr × dc}
Q6Tun ← {𝕊 sd‿qt‿dc‿pr: m ← ((8766 ≤ sd) ∧ sd < 9131) ∧ ((5 ≤ dc) ∧ dc ≤ 7) ∧ qt < 24 ⋄ +´ (m / pr) × m / dc}
Q1Agg ← {𝕊 sd‿qt‿dc‿tx‿rf‿ls‿pr:
  keep ← sd ≤ 10471
  g ← keep / (2 × rf) + ls
  q ← keep / qt ⋄ pp ← keep / pr
  dp ← pp × 100 - keep / dc
  ch ← dp × 100 + keep / tx
  (6 ↑ /⁼ g) ∾ ∾ {6 ↑ +´¨ g ⊔ 𝕩}¨ q‿pp‿dp‿ch
}
Q1Nat ← {+´ Q1Agg 𝕩}                                       # naturel : regroupement (⊔), l'idiome du GROUP BY
Q1Tun ← {𝕊 sd‿qt‿dc‿tx‿rf‿ls‿pr:                           # optimisé : un masque par groupe, sommes filtrées
  keep ← sd ≤ 10471
  g ← (2 × rf) + ls
  dp ← pr × 100 - dc
  ch ← dp × 100 + tx
  +´ ∾ {m ← keep ∧ g = 𝕩 ⋄ ⟨+´ m, +´ m / qt, +´ m / pr, +´ m / dp, +´ m / ch⟩}¨ ↕6
}
Chunks ← {<˘ 4‿4194304 ⥊ 𝕩}                                # 4 morceaux contigus d'une colonne
RunK6 ← {𝕤
  sd ← I32 "k6_shipdate.i32" ⋄ pr ← I32 "k6_extendedprice.i32"
  qt ← I8 "k6_quantity.u8" ⋄ dc ← I8 "k6_discount.u8" ⋄ tx ← I8 "k6_tax.u8"
  rf ← I8 "k6_returnflag.u8" ⋄ ls ← I8 "k6_linestatus.u8"
  q6c ← sd‿qt‿dc‿pr ⋄ q1c ← sd‿qt‿dc‿tx‿rf‿ls‿pr
  {p ≡ "q6" ?
     {v ≡ "natural" ? {𝕤 ⋄ IntStr Q6Nat q6c} _bench @
      ; v ≡ "tuned" ? {𝕤 ⋄ IntStr Q6Tun q6c} _bench @
      ; Meta "k6_mt;pas de threads : 4 morceaux traités en séquence"
        ch ← <˘ ⍉ > Chunks¨ q6c
        {𝕤 ⋄ IntStr +´ Q6Tun¨ ch} _bench @}
   ; {v ≡ "natural" ? {𝕤 ⋄ IntStr Q1Nat q1c} _bench @
      ; v ≡ "tuned" ? {𝕤 ⋄ IntStr Q1Tun q1c} _bench @
      ; Meta "k6_mt;pas de threads : 4 morceaux traités en séquence"
        ch ← <˘ ⍉ > Chunks¨ q1c
        {𝕤 ⋄ IntStr +´ Q1Tun¨ ch} _bench @}}
}

# ------------------------------------------------------------------ K7
K7Check ← {𝕊 ks‿cs‿ss: (IntStr ≠ks) ∾ ":" ∾ IntStr +´ ss × 1 + 1024 | ks}
RunK7 ← {𝕤
  keys ← U32 "k7_keys.u32" ⋄ vals ← I32 "k7_vals.u32"
  {v ≡ "natural" ?   # table de hachage de la bibliothèque système (•HashMap), valeur ⟨compte, somme⟩, ligne à ligne
     res ← @
     {𝕤
       m ← ⟨⟩ •HashMap ⟨⟩
       keys {𝕨 m.Set ⟨1, 𝕩⟩ + 0‿0 m.Get 𝕨}¨ vals
       res ↩ m
       "?"
     } {𝕤 ⋄ t0 ← •MonoTime @ ⋄ c ← 𝔽 @ ⋄ t ← (•MonoTime @) - t0
        cs‿ss ← <˘ ⍉ > res.Values @
        ⟨t, K7Check (res.Keys @)‿cs‿ss⟩} _timedRun @
   ; v ≡ "natural_arr" ?   # sensibilité : l'idiome tableau de BQN (classement ⊐, histogramme /⁼, regroupement ⊔)
     res ← @
     {𝕤
       i ← ⊐ keys
       res ↩ ((∊ keys) / keys)‿(/⁼ i)‿(+´¨ i ⊔ vals)
       "?"
     } {𝕤 ⋄ t0 ← •MonoTime @ ⋄ c ← 𝔽 @ ⋄ t ← (•MonoTime @) - t0 ⋄ ⟨t, K7Check res⟩} _timedRun @
   ; # optimisé : clés lues comme motifs binaires de 32 bits (entiers signés : même égalité, deux fois moins
     # d'octets que des f64), classement par hachage (⊐ de CBQN), histogramme, sommes par tri stable des classes
     ki ← I32 "k7_keys.u32"
     res ← @
     {𝕤
       i ← ⊐ ki
       cs ← /⁼ i
       o ← ⍋ i
       sc ← +` o ⊏ vals
       e ← (+` cs) - 1
       ss ← (e ⊏ sc) - » e ⊏ sc
       res ↩ (((» +` cs) ⊏ o) ⊏ ki)‿cs‿ss                     # clé de la première ligne de chaque classe
       "?"
     } {𝕤 ⋄ t0 ← •MonoTime @ ⋄ c ← 𝔽 @ ⋄ t ← (•MonoTime @) - t0 ⋄ ⟨t, K7Check res⟩} _timedRun @}
}
_timedRun ← {   # comme _bench, mais 𝔽 rend ⟨temps, somme de contrôle⟩ (somme de contrôle calculée hors chrono)
  Kern ← 𝔽
  {𝕊 r: t‿c ← Kern @ ⋄ {𝕤 ⋄ Emit r‿t‿c}⍟(r≥0) @}¨ (-warm) + ↕warm+reps
  @
}

# ------------------------------------------------------------------ K8
q8 ← 16384
Build ← {𝕊 d‿c: d = 0 ? ⟨⟨c, @, @⟩, c+1⟩ ;
  𝕊 d‿c: l‿c1 ← 𝕊 ⟨d-1, c+1⟩ ⋄ r‿c2 ← 𝕊 ⟨d-1, c1⟩ ⋄ ⟨⟨c, l, r⟩, c2⟩}
TSum ← {𝕊 val‿l‿r: @ ≡ l ? val ; 𝕊 val‿l‿r: val + (𝕊 l) + 𝕊 r}
# sensibilité : nœuds espaces de noms {v, l, r} au lieu de listes
NBuild ← {𝕊 d‿c: d = 0 ? ⟨{v⇐c ⋄ l⇐@ ⋄ r⇐@}, c+1⟩ ;
  𝕊 d‿c: lt‿c1 ← 𝕊 ⟨d-1, c+1⟩ ⋄ rt‿c2 ← 𝕊 ⟨d-1, c1⟩ ⋄ ⟨{v⇐c ⋄ l⇐lt ⋄ r⇐rt}, c2⟩}
NSum ← {@ ≡ 𝕩.l ? 𝕩.v ; 𝕩.v + (𝕊 𝕩.l) + 𝕊 𝕩.r}
# optimisé : arène de 2047 nœuds indexés (valeur, fils gauche, fils droit), construite niveau par niveau en
# opérations vectorielles, sommée par un parcours en largeur qui suit les indices des fils
ABuild ← {𝕊 c:
  val ← c + ↕2047
  lr ← {𝕊 lv‿sz‿ls‿rs:      # niveau courant : indices, taille de sous-arbre ; tableaux des fils
    h ← (sz - 1) ÷ 2
    ls ↩ (lv + 1)⌾(lv⊸⊏) ls ⋄ rs ↩ (lv + 1 + h)⌾(lv⊸⊏) rs
    ⟨(lv + 1) ∾ lv + 1 + h, h, ls, rs⟩}⍟10 ⟨⟨0⟩, 2047, 2047⥊¯1, 2047⥊¯1⟩
  ⟨val, 2⊑lr, 3⊑lr⟩
}
ASum ← {𝕊 val‿ls‿rs:
  ⊑ {𝕊 s‿f: c ← (f ⊏ ls) ∾ f ⊏ rs ⋄ ⟨s + +´ f ⊏ val, (c ≥ 0) / c⟩} •_while_ {0 < ≠ 1⊑𝕩} ⟨0, ⟨0⟩⟩
}
RunK8 ← {𝕤
  long‿· ← Build 20‿0
  lsum ← TSum long
  Query ← (⊑ "natural"‿"tuned"‿"natural_ns" ⊐ <v) ◶ ⟨{TSum ⊑ Build 10‿𝕩}, {ASum ABuild 𝕩}, {NSum ⊑ NBuild 10‿𝕩}⟩
  {𝕊 r:
    t0 ← •MonoTime @
    sl ← {𝕊 q: a ← •MonoTime @ ⋄ s ← Query q ⋄ ⟨s, (•MonoTime @) - a⟩}¨ ↕q8
    t ← (•MonoTime @) - t0
    {𝕤
      ss‿ls ← <˘ ⍉ > sl
      Emit r‿t‿(IntStr lsum + +´ ss)
      lat ← ∧ ⌊ 0.5 + 1e9 × ls
      •Out ∾ ⟨"LAT;", v⟩ ∾ ∾ {";" ∾ IntStr 𝕩 ⊑ lat}¨ ⌊ q8 × 0.5‿0.9‿0.99‿0.999 ∾ (q8-1) ÷ q8
    }⍟(r ≥ 0) @
  }¨ (-warm) + ↕warm+reps
  •internal.Keep long
}

# ------------------------------------------------------------------ K9
m9 ← 2048
g0 ← 1024 ÷˜ 1024 | (31 × ↕m9) +⌜ 17 × ↕m9
J9Nat ← {   # naturel : la matrice décalée dans les quatre directions ; bord recopié en recollant les rangées
  s ← 0.25 × (((»𝕩) + «𝕩) + »˘𝕩) + «˘𝕩
  mid ← 1↓¯1↓𝕩
  (1↑𝕩) ∾ ((1↑˘mid) ∾˘ (1↓˘¯1↓˘1↓¯1↓s) ∾˘ ¯1↑˘mid) ∾ ¯1↑𝕩
}
bi9 ← ⥊ (m9 × ↕m9-2) +⌜ 0‿(m9-1)                           # colonnes de bord dans les rangées intérieures
J9Tun ← {   # optimisé : grille plate ; voisins = tranches décalées de ±1 et ±M (sans copie), bord recopié
  seg ← 0.25 × ((((-2×m9) ↓ 𝕩) + (2×m9) ↓ 𝕩) + (m9-1) ↓ (-m9+1) ↓ 𝕩) + (m9+1) ↓ (1-m9) ↓ 𝕩
  core ← m9 ↓ (-m9) ↓ 𝕩
  seg ↩ (bi9 ⊏ core)⌾(bi9⊸⊏) seg
  (m9 ↑ 𝕩) ∾ seg ∾ (-m9) ↑ 𝕩
}
f0 ← ⥊ g0
RunK9 ← {𝕤
  {v ≡ "natural" ? {𝕤 ⋄ FltStr +´ ⥊ J9Nat⍟4 g0} _bench @
   ; v ≡ "tuned" ? {𝕤 ⋄ FltStr +´ J9Tun⍟4 f0} _bench @
   ; Meta "k9_mt;pas de threads : même code que tuned, sur un seul cœur"
     {𝕤 ⋄ FltStr +´ J9Tun⍟4 f0} _bench @}
}

# ------------------------------------------------------------------ choix du noyau
kernels ← "k1"‿"k2"‿"k3"‿"k4"‿"k5"‿"k6"‿"k7"‿"k8"‿"k9"
{⊑ (<k) ∊ kernels ?
   (⊑ kernels ⊐ <k) ◶ ⟨RunK1, RunK2, RunK3, RunK4, RunK5, RunK6, RunK7, RunK8, RunK9⟩ @
 ; •Out "noyau inconnu ou absent en BQN (pas de K10 : ni threads ni coroutines) : " ∾ k ⋄ •Exit 1}
