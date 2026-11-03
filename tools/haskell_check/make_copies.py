#!/usr/bin/env python3
"""Copies de la remarque sur Haskell (plan : docs/HASKELL.md, section 3.3), produites par remplacements de texte
contrôlés (chaque texte remplacé doit apparaître exactement une fois ; le reste du fichier est identique à l'octet).

* bench/haskell_ref : copie exacte de bench/haskell_k9h (le code publié : bench/haskell, harnais commun de K9), mêmes
  options (-fno-full-laziness, -fno-omit-yields) et même lancement (+RTS -N4).
* bench/haskell_rel : le même source, compilé dans le mode « release » annoncé par docs/NATURAL.md (ghc -O2 -fllvm),
  avec les options de la cible (-mavx512f -mfma -mbmi2) et le runtime multi-thread (-threaded -rtsopts), sans
  -fno-full-laziness ni -fno-omit-yields. Sert à séparer l'effet des options de celui des corrections du code.
* bench/haskell_fix : correction publiée = options de haskell_rel et quatre corrections du code :
  (a) K5 tuned : FMA vectorielle fmaddFloatX16# (GHC.Prim, livrée avec GHC 9.14.1), au lieu d'une multiplication et
      d'une addition séparées justifiées par un commentaire faux (« pas de primitive FMA vectorielle dans GHC 9.14 ») ;
  (b) K1 soa : même FMA, pour la même raison (les autres implémentations à SIMD explicite l'utilisent aussi en K1) ;
  (c) K8 tuned : les compteurs de l'arène (indice du prochain nœud, valeur) en mémoire brute, comme les pointeurs du
      C, au lieu d'une IORef d'entier boxé et d'un compteur rendu dans un n-uplet (une allocation par nœud et par
      feuille, quand la spécification exige « aucune allocation en régime permanent ») ;
  (d) K8 : l'arbre longue durée reste vivant jusqu'à la fin (touch#), comme l'exige la spécification et comme le
      font les autres implémentations à ramasse-miettes ; le code publié le laissait mourir avant la mesure.
* bench/haskell_n1 : le binaire de haskell_fix lancé avec +RTS -N1 (sensibilité : noyaux séquentiels sur une seule
  capacité, sans ramasse-miettes parallèle).
Usage : make_copies.py (puis build.sh de haskell_ref, haskell_rel et haskell_fix)."""
import os, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REF_FLAGS = "-O2 -fllvm -mavx512f -mfma -mbmi2 -fno-full-laziness -threaded -rtsopts -fno-omit-yields"
REL_FLAGS = "-O2 -fllvm -mavx512f -mfma -mbmi2 -threaded -rtsopts"
REL_BUILD = """#!/bin/sh
# Remarque sur Haskell (docs/HASKELL.md) : mode « release » annoncé par docs/NATURAL.md (ghc -O2 -fllvm ; LLVM 18,
# le générateur natif de 9.14.1 calcule faux les vecteurs 256/512 bits et refuse la FMA large), options de la cible et
# RTS multi-thread ; ni -fno-full-laziness (les NOINLINE et les IORef du harnais suffisent contre le partage entre
# répétitions) ni -fno-omit-yields (ajoutée sans justification ; aucune variante mesurée n'en a besoin).
set -e
cd "$(dirname "$0")"
/opt/ghc/bin/ghc """ + REL_FLAGS + """ -outputdir obj Ms.hs -o ms
"""


def sub(text, old, new):
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"texte trouvé {n} fois (1 attendu) :\n{old[:300]}")
    return text.replace(old, new)


NOTE = "-- remarque sur Haskell (docs/HASKELL.md) : "
FIX = [
    # (a) et (b) : FMA vectorielle de GHC.Prim
    ("import GHC.Exts\n", "import GHC.Exts\nimport GHC.Prim (fmaddFloatX16#)  " + NOTE + "FMA vectorielle (absente de GHC.Exts)\n"),
    ("              v2 = plusFloatX16# (timesFloatX16# x x) (plusFloatX16# (timesFloatX16# y y) (timesFloatX16# z z))\n",
     "              v2 = fmaddFloatX16# z z (fmaddFloatX16# y y (timesFloatX16# x x))  " + NOTE + "FMA, comme les autres\n"),
    ("              -- pas de primitive FMA vectorielle dans GHC 9.14 (seulement fmaddFloat# scalaire)\n"
     "              fma x y z' = plusFloatX16# (timesFloatX16# x y) z'\n",
     "              " + NOTE + "fmaddFloatX16# (GHC.Prim, depuis GHC 9.12)\n"
     "              fma x y z' = fmaddFloatX16# x y z'\n"),
    # (c) : compteurs de l'arène en mémoire brute
    ("""aBuild :: Ptr Int -> Ptr Int32 -> Ptr Int32 -> IORef Int -> Int -> Int -> IO (Int32, Int)
aBuild av al ar top d c = do
  i <- readIORef top
  writeIORef top (i + 1)
  pokeElemOff av i c
  if d == 0
    then pokeElemOff al i (-1) >> pokeElemOff ar i (-1) >> return (fromIntegral i, c + 1)
    else do
      (l, c1) <- aBuild av al ar top (d - 1) (c + 1)
      (r, c2) <- aBuild av al ar top (d - 1) c1
      pokeElemOff al i l >> pokeElemOff ar i r
      return (fromIntegral i, c2)
""", NOTE + """indice du prochain nœud et compteur de valeurs en mémoire brute (comme
-- les pointeurs du C) : ni IORef d'entier boxé ni compteur rendu dans un n-uplet, aucune allocation par nœud
aBuild :: Ptr Int -> Ptr Int32 -> Ptr Int32 -> Ptr Int -> Ptr Int -> Int -> IO Int32
aBuild av al ar top cnt d = do
  i <- peek top
  poke top (i + 1)
  c <- peek cnt
  poke cnt (c + 1)
  pokeElemOff av i c
  if d == 0
    then pokeElemOff al i (-1) >> pokeElemOff ar i (-1) >> return (fromIntegral i)
    else do
      l <- aBuild av al ar top cnt (d - 1)
      r <- aBuild av al ar top cnt (d - 1)
      pokeElemOff al i l >> pokeElemOff ar i r
      return (fromIntegral i)
"""),
    ("""  top <- newIORef 0
  unsafeWithForeignPtr fv $ \\av -> unsafeWithForeignPtr fl $ \\al -> unsafeWithForeignPtr fr $ \\ar ->
""", """  fst8 <- mallocForeignPtrArray 2 :: IO (ForeignPtr Int)  -- [indice du prochain nœud, compteur de valeurs]
  unsafeWithForeignPtr fv $ \\av -> unsafeWithForeignPtr fl $ \\al -> unsafeWithForeignPtr fr $ \\ar -> unsafeWithForeignPtr fst8 $ \\top ->
"""),
    ("          then do writeIORef top 0; (root, _) <- aBuild av al ar top 10 qq; aSum av al ar root\n",
     "          then do poke top 0; pokeElemOff top 1 qq; root <- aBuild av al ar top (top `plusPtr` 8) 10; aSum av al ar root\n"),
    # (d) : l'arbre longue durée reste vivant jusqu'à la fin
    ("  lsum `seq` return ()\n",
     "  " + NOTE + "l'arbre longue durée reste vivant jusqu'à la fin (docs/SPEC.md, K8)\n"
     "  lsum `seq` IO (\\s -> (# touch# keep s, () #))\n"),
]


def fix(text):
    for a, b in FIX:
        text = sub(text, a, b)
    return text


def copy(dst, text, build):
    d = os.path.join(ROOT, "bench", dst)
    if os.path.exists(d):
        shutil.rmtree(d)
    os.makedirs(d)
    open(os.path.join(d, "Ms.hs"), "w", encoding="utf-8").write(text)
    shutil.copy2(os.path.join(ROOT, "bench", "haskell_k9h", "run"), os.path.join(d, "run"))
    if build is None:
        shutil.copy2(os.path.join(ROOT, "bench", "haskell_k9h", "build.sh"), os.path.join(d, "build.sh"))
    else:
        open(os.path.join(d, "build.sh"), "w").write(build)
        os.chmod(os.path.join(d, "build.sh"), 0o755)
    print(f"{dst} écrit")


def main():
    src = open(os.path.join(ROOT, "bench", "haskell_k9h", "Ms.hs"), encoding="utf-8").read()
    build = open(os.path.join(ROOT, "bench", "haskell_k9h", "build.sh")).read()
    assert REF_FLAGS in build, "options du banc publié changées"
    copy("haskell_ref", src, None)
    copy("haskell_rel", src, REL_BUILD)
    copy("haskell_fix", fix(src), REL_BUILD)
    d = os.path.join(ROOT, "bench", "haskell_n1")
    if os.path.exists(d):
        shutil.rmtree(d)
    os.makedirs(d)
    run = os.path.join(d, "run")
    open(run, "w").write('#!/bin/sh\n# binaire de haskell_fix sur une seule capacité (sensibilité, docs/HASKELL.md)\n'
                         'exec "$(dirname "$0")/../haskell_fix/ms" "$@" +RTS -N1 -RTS\n')
    os.chmod(run, 0o755)
    print("haskell_n1 écrit")


if __name__ == "__main__":
    main()
