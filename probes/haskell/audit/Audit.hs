{-# LANGUAGE MagicHash, UnboxedTuples, BangPatterns, TemplateHaskell, ScopedTypeVariables #-}
-- Audit de la grille, Haskell (GHC 9.14.1, réglages du banc : -O2 -fllvm -mavx512f -mfma -threaded) : chaque case
-- est exercée sous sa forme la plus forte et imprime un fait observable (docs/V4_PLAN.md 2.1). Lignes FACT (reprises
-- par run.sh avec le code machine, les statistiques du RTS et les recherches) et NOTE (contre-épreuves).
module Main (main, cgPrefetch, cgVec) where

import Control.Concurrent
import Control.Exception
import Control.Monad
import Data.Array.Base (unsafeAt)
import Data.Array.Unboxed
import Data.IORef
import Data.Int
import Data.Word
import Foreign.Marshal.Alloc
import Foreign.Marshal.Array
import Foreign.Marshal.Pool
import Foreign.Ptr
import Foreign.Storable
import GHC.Exts
import GHC.Prim (fmaddFloatX16#)
import GHC.Float (castFloatToWord32)
import GHC.IO (IO (..))
import GHC.Stats
import GHC.Conc (par, pseq)
import Language.Haskell.TH.Syntax (lift)
import System.Mem (getAllocationCounter, performGC)
import Text.Printf
import Layout
import Foreign.C.Types (CInt (..), CSize (..))
import System.Posix.Types (COff (..), Fd (..))
import System.Posix.IO (OpenMode (ReadOnly), defaultFileFlags, openFd)
import Comptime (fib)
import System.IO (hSetEncoding, stdout, utf8)

foreign import ccall unsafe "sched_getcpu" c_getcpu :: IO Int32   -- observation du processeur courant seulement
-- contre-épreuve F4 : mmap de la glibc par la FFI (FFI vers la libc, non comptée par la règle)
foreign import ccall unsafe "mmap" c_mmap :: Ptr () -> CSize -> CInt -> CInt -> CInt -> COff -> IO (Ptr ())

fact :: String -> String -> IO ()
fact c ev = putStrLn ("FACT;" ++ c ++ ";" ++ ev)

note :: String -> String -> IO ()
note c ev = putStrLn ("NOTE;" ++ c ++ ";" ++ ev)

-- A1 : enregistrement de 4 float, en Storable (tableau à plat) et en valeur du tas (Data.Array)
data P4 = P4 {-# UNPACK #-} !Float {-# UNPACK #-} !Float {-# UNPACK #-} !Float {-# UNPACK #-} !Float
instance Storable P4 where
  sizeOf _ = 16
  alignment _ = 4
  peek p = P4 <$> peekByteOff p 0 <*> peekByteOff p 4 <*> peekByteOff p 8 <*> peekByteOff p 12
  poke p (P4 a b c d) = pokeByteOff p 0 a >> pokeByteOff p 4 b >> pokeByteOff p 8 c >> pokeByteOff p 12 d

-- A2 : disposition C {uint8; uint32; double} écrite par Storable avec les décalages de hsc2hs
data S = S !Word8 !Word32 !Double
instance Storable S where
  sizeOf _ = sizeS
  alignment _ = 8
  peek p = S <$> peekByteOff p 0 <*> peekByteOff p offB <*> peekByteOff p offC
  poke p (S a b c) = pokeByteOff p 0 a >> pokeByteOff p offB b >> pokeByteOff p offC c

-- A3 : enregistrement compacté {uint8; uint32} de 5 octets (uint32 non aligné)
data Pk = Pk !Word8 !Word32
instance Storable Pk where
  sizeOf _ = sizeP
  alignment _ = 1
  peek p = Pk <$> peekByteOff p 0 <*> peekByteOff p offPB
  poke p (Pk a b) = pokeByteOff p 0 a >> pokeByteOff p offPB b

-- A7 : 16 float en ligne et un Int32 (68 octets)
data In = In [Float] !Int32
instance Storable In where
  sizeOf _ = 68
  alignment _ = 4
  peek p = In <$> peekArray 16 (castPtr p) <*> peekByteOff p 64
  poke p (In fs n) = pokeArray (castPtr p) (take 16 fs) >> pokeByteOff p 64 n

{-# NOINLINE pairU #-}
pairU :: Int -> (# Int#, Int# #)
pairU (I# i) = (# i, i +# 1# #)
{-# NOINLINE pairB #-}
pairB :: Int -> (Int, Int)
pairB i = (i, i + 1)
{-# NOINLINE addG #-}
addG :: Num a => a -> a -> a
addG = (+)

{-# NOINLINE cgPrefetch #-}
cgPrefetch :: Int -> IO ()
cgPrefetch (I# n) = IO (\s -> case newByteArray# n s of (# s1, mba #) -> case prefetchMutableByteArray3# mba 0# s1 of s2 -> case prefetchMutableByteArray0# mba 64# s2 of s3 -> (# s3, () #))
{-# NOINLINE cgVec #-}
cgVec :: Ptr Float -> IO ()
cgVec (Ptr a) = IO (\s -> case readFloatOffAddrAsFloatX16# a 0# s of
  (# s1, x #) -> case readFloatOffAddrAsFloatX16# a 16# s1 of
    (# s2, y #) -> case writeFloatOffAddrAsFloatX16# a 32# (fmaddFloatX16# x y x) s2 of
      s3 -> (# s3, () #))

garbage :: Int -> IO ()
garbage n = forM_ [1 .. n] $ \_ -> IO (\s -> case newByteArray# 1024# s of (# s1, _ #) -> (# s1, () #))

liveBytes :: IO Word64
liveBytes = performGC >> (gcdetails_live_bytes . gc <$> getRTSStats)

allocd :: IO a -> IO (a, Int)
allocd act = do
  c0 <- getAllocationCounter
  r <- act
  c1 <- getAllocationCounter
  return (r, fromIntegral (c0 - c1))

pairwise :: UArray Int Double -> Int -> Int -> Double
pairwise a lo hi
  | hi - lo <= 8 = foldl (\s i -> s + a ! i) 0 [lo .. hi - 1]
  | otherwise = let m = (lo + hi) `div` 2 in pairwise a lo m + pairwise a m hi

main :: IO ()
main = do
  hSetEncoding stdout utf8
  -- ---------- A
  let n = 100000 :: Int
  allocaArray n $ \(p :: Ptr P4) -> do
    pokeElemOff p 1 (P4 2.5 0 0 0)
    P4 v _ _ _ <- peekElemOff p 1
    l0 <- liveBytes
    let arr = listArray (0, n - 1) [P4 (fromIntegral i) 0 0 0 | i <- [0 .. n - 1]] :: Array Int P4
    forM_ [0 .. n - 1] $ \i -> evaluate (arr ! i)
    l1 <- liveBytes
    _ <- evaluate (arr ! 0)
    fact "A1" $ printf "Storable P4 (4 float) : tableau à plat, %d o par élément, élément 1 à %d o (vx = %.1f) ; Data.Array de P4 : %d o vivants par élément (pointeur vers une fermeture sur le tas)"
      (sizeOf (undefined :: P4)) (minusPtr (advancePtr p 1) p) v ((fromIntegral (l1 - l0) :: Int) `div` n)
  alloca $ \(p :: Ptr S) -> do
    poke p (S 1 2 3.5)
    S _ b c <- peek p
    fact "A2" $ printf "instance Storable écrite à la main, décalages de struct s {uint8_t; uint32_t; double} calculés par hsc2hs (livré avec GHC) : b=%d c=%d, taille %d ; relu b=%d c=%.1f ; les enregistrements du tas n'ont pas de disposition contrôlable" offB offC sizeS b c
  allocaArray 1000 $ \(p :: Ptr Pk) -> do
    pokeElemOff p 1 (Pk 7 123456789)
    Pk a b <- peekElemOff p 1
    fact "A3" $ printf "struct __attribute__((packed)) {uint8_t; uint32_t} : taille %d, b à %d (hsc2hs) ; instance Storable de 5 o : tableau de 1000 éléments à plat, élément 1 à %d o, relu %d et %d (uint32 non aligné) ; pas de champ de bits"
      sizeP offPB (minusPtr (advancePtr p 1) p) a b
  allocaBytesAligned 256 64 $ \(p :: Ptr Word8) ->
    fact "A4" $ printf "allocaBytesAligned 256 64 : adresse mod 64 = %d ; tableaux épinglés alignés (newAlignedPinnedByteArray#) ; pas d'alignement de type pour les enregistrements" (fromIntegral (ptrToWordPtr p `mod` 64) :: Int)
  alloca $ \(p :: Ptr Float) -> do
    poke p 1.0
    w <- peek (castPtr p) :: IO Word32
    fact "A5" $ printf "castFloatToWord32 1.0 = 0x%08x ; Float relu en Word32 par castPtr = 0x%08x ; pas d'union" (castFloatToWord32 1.0) w
  alloca $ \(p :: Ptr In) -> do
    poke p (In [0 ..] 9)
    In fs k <- peek p
    fact "A7" $ printf "instance Storable {16 float; int32} : %d o, n à 64 (relu %d, f[15] = %.0f) ; un champ tableau d'un enregistrement du tas est un pointeur" (sizeOf (undefined :: In)) k (fs !! 15)
  fact "A8" $ printf "sizeOf : Word8 %d, Int16 %d, Float %d ; UArray Int Word8 range un octet par élément ; pas de flottant 16 bits" (sizeOf (0 :: Word8)) (sizeOf (0 :: Int16)) (sizeOf (0 :: Float))

  -- ---------- B
  g0 <- gcs <$> getRTSStats
  garbage (1024 * 1024)
  g1 <- gcs <$> getRTSStats
  fact "B1" $ printf "1 Gio de tableaux de 1 Kio sans référence : %d collectes déclenchées par le RTS, sans appel du programme (ramasse-miettes traçant)" (g1 - g0)
  withPool $ \pool -> do
    p1 <- pooledMallocBytes pool 400 :: IO (Ptr Word8)
    p2 <- pooledMallocBytes pool 400 :: IO (Ptr Word8)
    fact "B2" $ printf "Foreign.Marshal.Pool : deux blocs pooledMallocBytes (%s), libérés d'un coup à la sortie de withPool ; mallocBytes pour une arène écrite à la main ; rien pour les objets du tas de GHC" (if p1 /= p2 then "distincts" else "identiques")
  (_, bu) <- allocd (forM_ [1 .. 100000 :: Int] $ \i -> case pairU i of (# a, b #) -> void (evaluate (I# (a +# b))))
  (_, bb) <- allocd (forM_ [1 .. 100000 :: Int] $ \i -> case pairB i of (a, b) -> void (evaluate (a + b)))
  fact "B3" $ printf "n-uplet non boxé (# Int#, Int# #) rendu par une fonction NOINLINE : %d o alloués pour 100 000 appels ; n-uplet boxé (Int, Int) : %d o ; enregistrements et tableaux toujours sur le tas" bu bb
  (_, bg) <- allocd (foldM (\acc i -> evaluate (addG acc (fromIntegral i :: Double))) 0 [1 .. 100000 :: Int])
  ref <- newIORef (0 :: Int)
  (_, bt) <- allocd (forM_ [1 .. 100000 :: Int] $ \i -> modifyIORef ref (+ i))
  _ <- readIORef ref >>= evaluate
  fact "B4" $ printf "allocations implicites : addG :: Num a => a -> a -> a (NOINLINE, dictionnaire) sur des Double, %d o par appel (boîtes) ; modifyIORef paresseux, %d o par appel (glaçons)" (bg `div` 100000) (bt `div` 100000)
  allocaBytes 32 $ \(p :: Ptr Word32) -> do
    pokeByteOff p 12 (42 :: Word32)
    poke (p `plusPtr` 16) (7 :: Word32)
    a3 <- peekElemOff p 3
    a4 <- peekElemOff p 4
    fact "B5" $ printf "Foreign.Ptr : pokeByteOff p 12 → p[3] = %d ; plusPtr 16 → p[4] = %d" a3 a4

  -- ---------- C
  allocaArray 48 $ \(pv :: Ptr Float) -> do
    pokeArray pv (replicate 16 2 ++ replicate 16 3 ++ replicate 16 0)
    cgVec pv
    r0 <- peekElemOff pv 32
    r15 <- peekElemOff pv 47
    fact "C1" $ printf "FloatX16# et fmaddFloatX16# (GHC.Exts, primops propres à GHC) : x*y + x sur 16 voies lues en mémoire, voies 0 et 15 = %.1f et %.1f" r0 r15
  let m = 1048576 :: Int
      xs = take m (iterate (\x -> x * 6364136223846793005 + 1442695040888963407) (42 :: Word64))
      dv = listArray (0, m - 1) [fromIntegral (x `shiftR'` 11) / 9007199254740992 - 0.5 | x <- xs] :: UArray Int Double
      shiftR' x k = x `div` (2 ^ k)
      sq = foldl (\s i -> s + dv ! i) 0 [0 .. m - 1]
      pw = pairwise dv 0 m
  fact "C4" $ "un million de Double : pli gauche compilé " ++ show sq ++ ", somme par paires écrite à la main " ++ show pw ++ " (écart " ++ printf "%.3g" (abs (pw - sq)) ++ ") : l'ordre est gardé, aucune option de réassociation (ni -ffast-math)"
  let ex k = sum [fromIntegral ((i * k) `mod` 7) :: Double | i <- [1 .. 40000000 :: Int]]
      parts = [ex k | k <- [1 .. 8]]
  r <- evaluate (foldr par () parts `pseq` sum parts)
  fact "C5" $ printf "par et pseq (étincelles par#) sur 8 calculs : somme %.0f ; étincelles converties lues par run.sh (+RTS -s)" r

  -- ---------- D
  caps <- getNumCapabilities
  mv <- newMVar (0 :: Int)
  dones <- forM [1 .. 4 :: Int] $ \_ -> do
    d <- newEmptyMVar
    _ <- forkIO (replicateM_ 1000 (modifyMVar_ mv (return . (+ 1))) >> putMVar d ())
    return d
  mapM_ takeMVar dones
  cnt <- readMVar mv
  fact "D1" $ printf "RTS multi-fil, %d capacités : 4 fils Haskell (forkIO), %d incréments ; forkOS et forkOn aussi" caps cnt
  ior <- newIORef (0 :: Int)
  replicateM_ 10 (atomicModifyIORef' ior (\x -> (x + 1, ())))
  v10 <- readIORef ior
  fa <- IO (\s -> case newByteArray# 8# s of
          (# s1, mba #) -> case writeIntArray# mba 0# 5# s1 of
            s2 -> case fetchAddIntArray# mba 0# 3# s2 of
              (# s3, old #) -> case casIntArray# mba 0# 8# 20# s3 of
                (# s4, prev #) -> case atomicReadIntArray# mba 0# s4 of
                  (# s5, cur #) -> (# s5, (I# old, I# prev, I# cur) #))
  fact "D2" $ printf "atomicModifyIORef' ×10 → %d ; primops fetchAddIntArray#, casIntArray#, atomicReadIntArray# → %s (séquentiellement cohérents)" v10 (show fa)
  dc <- newEmptyMVar
  _ <- forkOn 2 (c_getcpu >>= putMVar dc)
  cpu <- takeMVar dc
  fact "D4" $ printf "forkOn 2 avec +RTS -N4 -qa (capacités épinglées par le RTS) : le fil tourne sur le processeur %d ; pas d'API pour un ensemble de processeurs choisi" cpu

  -- ---------- E
  cgPrefetch 256
  fact "E4" "prefetchMutableByteArray3# et prefetchMutableByteArray0# (GHC.Exts)"
  let four = listArray (0, 3) [1, 2, 3, 4] :: UArray Int Int
  e <- try (evaluate (four ! 4))
  let msg = either (\(ErrorCall s) -> takeWhile (/= '\n') s) show e
  fact "E6" $ printf "four ! 4 : erreur « %s » ; unsafeAt four 2 = %d (sans contrôle, local)" msg (unsafeAt four 2)
  fact "E7" $ printf "Template Haskell : $(lift (fib 25)) = %d, calculé pendant la compilation ; spécialisation des classes par SPECIALIZE ou par l'optimiseur, non garantie (B4)" ($(lift (fib 25)) :: Int)

  -- ---------- F
  let rows = 3 :: Int
      g = listArray ((0, 0), (rows - 1, 3)) [0 ..] :: UArray (Int, Int) Double
  fact "F1" $ printf "UArray (Int, Int) Double de %d×4 : g ! (2, 3) = %.0f, élément 11 du tableau à plat (bornes connues à l'exécution)" rows (g ! (2, 3))
  fact "F3" $ printf "Word32 : maxBound + 6 = %d ; Int8 : 127 + 1 = %d (enveloppement)" (maxBound + 6 :: Word32) (127 + 1 :: Int8)
  Fd fd <- openFd "/opt/msdata/k5_a.f32" ReadOnly defaultFileFlags
  mp <- c_mmap nullPtr 8192 1 2 fd 0
  f0 <- peek (castPtr mp) :: IO Float
  note "F4" $ printf "mmap de la glibc appelée par la FFI (foreign import ccall) sur k5_a.f32 : premier float %.7f (FFI vers la libc, non comptée)" f0
