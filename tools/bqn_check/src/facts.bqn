# Faits relevés en écrivant le banc BQN (docs/BQN.md, 2.4) ; argument : dossier des données
d ← (⊑•args) ∾ "/"
R ← {'-'¨⌾(('¯'=𝕩)⊸/) 𝕩} •Fmt
_t ← {t0 ← •MonoTime @ ⋄ r ← 𝔽 𝕩 ⋄ ⟨(•MonoTime @) - t0, r⟩}
Bytes ← •file.Bytes d∾⊢
I32 ← ⟨8,'c'⟩‿⟨32,'i'⟩ •bit._cast Bytes
F32 ← {w ← I32 𝕩 ⋄ sg ← w < 0 ⋄ u ← w + 4294967296 × sg ⋄ e ← 256 | ⌊ u ÷ 8388608 ⋄ m ← 8388608 | u
  (1 - 2 × sg) × (m + 8388608 × e > 0) × 2 ⋆ (e ⌈ 1) - 150}
•Out "== 1. •bit._cast : largeurs refusées"
•Out "f32 : " ∾ {𝕤 ⋄ ⟨8,'c'⟩‿⟨32,'f'⟩ •bit._cast 4⥊@ ⋄ "accepté"}⎊{𝕤 ⋄ •CurrentError @} @
•Out "u32 : " ∾ {𝕤 ⋄ ⟨8,'c'⟩‿⟨32,'u'⟩ •bit._cast 4⥊@ ⋄ "accepté"}⎊{𝕤 ⋄ •CurrentError @} @
•Out "== 2. K5 : +´ ordonnée contre •math.Sum (65 536 produits scalaires de 2048)"
a ← F32 "k5_a.f32" ⋄ b ← F32 "k5_b.f32"
t1‿r1 ← {𝕤 ⋄ {𝕤 ⋄ +´ a × b}⍟65536 0} _t @
t2‿r2 ← {𝕤 ⋄ {𝕤 ⋄ •math.Sum a × b}⍟65536 0} _t @
t3‿r3 ← {𝕤 ⋄ {𝕤 ⋄ a × b}⍟65536 0} _t @
•Out "+´ : " ∾ (R t1) ∾ " s (" ∾ (R 1e9 × t1 ÷ 65536 × 2048) ∾ " ns par élément), " ∾ R r1
•Out "•math.Sum : " ∾ (R t2) ∾ " s, " ∾ R r2
•Out "produit seul (a × b) : " ∾ (R t3) ∾ " s ; la somme +´ seule : " ∾ (R 1e9 × (t1 - t3) ÷ 65536 × 2048) ∾ " ns par élément (chaîne d'additions)"
•Out "== 3. K2 : forme tacite contre bloc (4,2 M sauts, 16 Kio)"
c16 ← I32 "k2_chase_16384.u32"
t4‿r4 ← {𝕤 ⋄ ⊑⟜c16⍟4200000 0} _t @
t5‿r5 ← {𝕤 ⋄ {𝕩⊑c16}⍟4200000 0} _t @
•Out "⊑⟜a⍟n : " ∾ (R 1e9 × t4 ÷ 4200000) ∾ " ns par saut ; {𝕩⊑a}⍟n : " ∾ (R 1e9 × t5 ÷ 4200000) ∾ " ns par saut (" ∾ (R r4) ∾ ", " ∾ (R r5) ∾ ")"
•Out "== 4. K9 : recopier le bord (une itération, 2048×2048)"
g ← 1024 ÷˜ 1024 | (31 × ↕2048) +⌜ 17 × ↕2048
s ← 0.25 × (((»g) + «g) + »˘g) + «˘g
Inner ← 1↓¯1↓1↓˘¯1↓˘⊢
t6‿o6 ← {𝕤 ⋄ (Inner s)˙⌾Inner g} _t @
mid ← 1↓¯1↓g
t7‿o7 ← {𝕤 ⋄ (1↑g) ∾ ((1↑˘mid) ∾˘ (Inner s) ∾˘ ¯1↑˘mid) ∾ ¯1↑g} _t @
•Out "mise à jour structurelle (Inner s)˙⌾Inner : " ∾ (R t6) ∾ " s ; rangées recollées (∾ et ∾˘) : " ∾ (R t7) ∾ " s ; mêmes valeurs : " ∾ R o6 ≡ o7
•Out "== 5. K1 : place d'une matrice de 4 194 304 × 16 f64"
Split ← (¬-˜⊢×·+`»⊸>)∘≠⊔⊢
Rss ← {𝕤 ⋄ 4096 × •ParseFloat 1 ⊑ ' ' Split 1 ⊑ •SH "sh"‿"-c"‿"cat /proc/$PPID/statm"}
Live ← {𝕤 ⋄ •internal.GC @ ⋄ 1 ⊑ •internal.HeapStats @}
q0 ← Rss @ ⋄ l0 ← Live @
x ← 4194304‿16 ⥊ 0.5 + ↕16
q1 ← Rss @ ⋄ l1 ← Live @
•Out "octets par particule : RSS " ∾ (R (q1 - q0) ÷ 4194304) ∾ ", tas vivant " ∾ (R (l1 - l0) ÷ 4194304) ∾ " (" ∾ (•internal.Type x) ∾ ")"
•Out "== 6. •HashMap : coût par ligne (1 M lignes, Get puis Set d'un couple)"
keys ← 1048576 ↑ ⟨8,'c'⟩‿⟨32,'i'⟩ •bit._cast Bytes "k7_keys.u32"
vals ← 1048576 ↑ I32 "k7_vals.u32"
t8‿· ← {𝕤 ⋄ m ← ⟨⟩ •HashMap ⟨⟩ ⋄ keys {𝕨 m.Set ⟨1, 𝕩⟩ + 0‿0 m.Get 𝕨}¨ vals ⋄ m.Count @} _t @
t9‿· ← {𝕤 ⋄ i ← ⊐ keys ⋄ ⟨/⁼ i, +´¨ i ⊔ vals⟩} _t @
•Out "•HashMap : " ∾ (R 1e9 × t8 ÷ 1048576) ∾ " ns par ligne ; ⊐, /⁼ et ⊔ : " ∾ (R 1e9 × t9 ÷ 1048576) ∾ " ns par ligne"
