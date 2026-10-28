{-# LANGUAGE BangPatterns, MagicHash, UnboxedTuples, ScopedTypeVariables #-}
-- Implémentation Haskell (GHC 9.14.1, paquets livrés avec GHC seulement :
-- base, ghc-prim, bytestring, array, containers). Voir docs/SPEC.md.
module Main (main) where

import Control.Concurrent
import Control.Monad
import Data.Bits
import qualified Data.ByteString as BS
import qualified Data.ByteString.Unsafe as BSU
import qualified Data.IntMap.Strict as IM
import Data.Array.Unboxed
import Data.Int
import Data.IORef
import Data.List (foldl', sort)
import Data.Word
import Foreign.ForeignPtr
import Foreign.Marshal.Utils (copyBytes, fillBytes)
import Foreign.Ptr
import Foreign.Storable
import GHC.Clock (getMonotonicTimeNSec)
import GHC.Exts
import GHC.ForeignPtr (mallocPlainForeignPtrAlignedBytes, unsafeWithForeignPtr)
import GHC.IO (IO (..))
import GHC.Word (Word32 (..), Word64 (..))
import System.Environment
import Text.Printf (printf)

-- ------------------------------------------------------------------ harnais
dataDir :: IO String
dataDir = maybe "/opt/msdata" id <$> lookupEnv "MS_DATA"

-- Tampon brut aligné sur 64 octets (non déplacé par le GC)
data Buf a = Buf !(ForeignPtr a) !Int

loadBuf :: forall a. Storable a => String -> IO (Buf a)
loadBuf name = do
  d <- dataDir
  bs <- BS.readFile (d ++ "/" ++ name)
  let n = BS.length bs
  fp <- mallocPlainForeignPtrAlignedBytes (n + 64) 64
  BSU.unsafeUseAsCString bs $ \src -> unsafeWithForeignPtr fp $ \dst -> copyBytes (castPtr dst) src n
  return (Buf fp (n `div` sizeOf (undefined :: a)))

withBuf :: Buf a -> (Ptr a -> IO b) -> IO b
withBuf (Buf fp _) = unsafeWithForeignPtr fp

result :: String -> String -> String -> Int -> Double -> String -> IO ()
result k v p rep sec chk = printf "RESULT;%s;%s;%s;%d;%.9f;%s\n" k v p rep sec chk

timed :: IO a -> IO (a, Double)
timed act = do
  t0 <- getMonotonicTimeNSec
  !x <- act
  t1 <- getMonotonicTimeNSec
  return (x, fromIntegral (t1 - t0) * 1e-9)

bench :: String -> String -> String -> Int -> Int -> IO String -> IO ()
bench k v p warm reps act = forM_ [-warm .. reps - 1] $ \r -> do
  (chk, dt) <- timed (act >>= \c -> length c `seq` return c)
  when (r >= 0) $ result k v p r dt chk

-- ------------------------------------------------------------------ K1
n1 :: Int
n1 = 1 `shiftL` 22

-- enregistrement à champs stricts (GHC « déballe » les petits champs stricts)
data Particle = Particle { px, py, pz, pvx, pvy, pvz, pax, pay, paz, pmass, pcharge, pradius, ptemp, ppressure, penergy, pdensity :: !Float }

k1Natural :: [Particle] -> Double
k1Natural = foldl' (\e p -> e + 0.5 * realToFrac (pmass p) * realToFrac (pvx p * pvx p + pvy p * pvy p + pvz p * pvz p)) 0

-- AoS manuel en mémoire brute (pas 16 flottants), 4 accumulateurs
k1AoS :: Ptr Float -> Int -> IO Double
k1AoS p n = go 0 0 0 0 0
  where
    e :: Int -> IO Double
    e i = do
      m <- peekElemOff p (16 * i + 9); x <- peekElemOff p (16 * i + 3); y <- peekElemOff p (16 * i + 4); z <- peekElemOff p (16 * i + 5)
      return $! realToFrac (0.5 * m * (x * x + y * y + z * z) :: Float)
    go !i !a0 !a1 !a2 !a3
      | i >= n = return (a0 + a1 + a2 + a3)
      | otherwise = do
          b0 <- e i; b1 <- e (i + 1); b2 <- e (i + 2); b3 <- e (i + 3)
          go (i + 4) (a0 + b0) (a1 + b1) (a2 + b2) (a3 + b3)

-- SoA + primitives SIMD de GHC (FloatX16#, générateur natif avec -mavx512f)
k1SoA :: Ptr Float -> Ptr Float -> Ptr Float -> Ptr Float -> Int -> IO Double
k1SoA (Ptr vx) (Ptr vy) (Ptr vz) (Ptr m) (I# n) = IO $ \s -> (# s, go 0# 0.0## #)
  where
    go i acc
      | isTrue# (i >=# n) = D# acc
      | otherwise =
          let x = indexFloatOffAddrAsFloatX16# vx i
              y = indexFloatOffAddrAsFloatX16# vy i
              z = indexFloatOffAddrAsFloatX16# vz i
              w = indexFloatOffAddrAsFloatX16# m i
              v2 = plusFloatX16# (timesFloatX16# x x) (plusFloatX16# (timesFloatX16# y y) (timesFloatX16# z z))
              e = timesFloatX16# (timesFloatX16# (broadcastFloatX16# 0.5#) w) v2
              (# e0, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10, e11, e12, e13, e14, e15 #) = unpackFloatX16# e
              f a = float2Double# a
              s8 = ((f e0 +## f e1) +## (f e2 +## f e3)) +## ((f e4 +## f e5) +## (f e6 +## f e7))
              s16 = ((f e8 +## f e9) +## (f e10 +## f e11)) +## ((f e12 +## f e13) +## (f e14 +## f e15))
           in go (i +# 16#) (acc +## (s8 +## s16))

runK1 :: String -> Int -> Int -> IO ()
runK1 v warm reps
  | v == "footprint0" = result "k1" v "energy" 0 0 "0"
  | otherwise = do
      raw <- loadBuf "k1_particles.f32" :: IO (Buf Float)
      case v of
        "aos" -> withBuf raw $ \p -> bench "k1" v "energy" warm reps (printf "%.6f" <$> k1AoS p n1)
        "soa" -> do
          cols <- forM [0 .. 15] $ \k -> do
            fp <- mallocPlainForeignPtrAlignedBytes (n1 * 4) 64
            withBuf raw $ \p -> unsafeWithForeignPtr fp $ \c -> forM_ [0 .. n1 - 1] $ \i -> peekElemOff p (16 * i + k) >>= pokeElemOff c i
            return fp
          let c k = cols !! k
          unsafeWithForeignPtr (c 3) $ \a -> unsafeWithForeignPtr (c 4) $ \b -> unsafeWithForeignPtr (c 5) $ \cc -> unsafeWithForeignPtr (c 9) $ \m ->
            bench "k1" v "energy" warm reps (printf "%.6f" <$> k1SoA a b cc m n1)
        _ -> do
          ps0 <- withBuf raw $ \p -> forM [0 .. n1 - 1] $ \i -> do
            f <- forM [0 .. 15] $ \k -> peekElemOff p (16 * i + k)
            let [a, b, c, d, e, f', g, h, ii, j, k, l, m, nn, o, q] = f
            return $! Particle a b c d e f' g h ii j k l m nn o q
          ps <- if v == "natural_shuffled"
            then do
              perm <- loadBuf "k1_perm.u32" :: IO (Buf Word32)
              let arr = listArray (0, n1 - 1) ps0 :: Array Int Particle
              withBuf perm $ \pp -> forM [0 .. n1 - 1] $ \i -> do j <- peekElemOff pp i; return $! arr ! fromIntegral j
            else return ps0
          if v == "footprint"
            then result "k1" v "energy" 0 0 (printf "%.6f" (k1Natural ps))
            else do
              ref <- newIORef ps
              bench "k1" v "energy" warm reps (readIORef ref >>= \x -> return $! printf "%.6f" (k1Natural x))

-- ------------------------------------------------------------------ K2
k2Chase :: Ptr Word32 -> Int -> IO Word32
k2Chase p = go 0
  where
    go !i 0 = return i
    go !i h = do j <- peekElemOff p (fromIntegral i); go j (h - 1)

runK2 :: String -> Int -> Int -> String -> IO ()
runK2 v warm reps p = do
  a <- loadBuf ("k2_chase_" ++ p ++ ".u32") :: IO (Buf Word32)
  withBuf a $ \pa -> bench "k2" v p warm reps (show <$> k2Chase pa 4200000)

-- ------------------------------------------------------------------ K3
iter3 :: Int
iter3 = 1 `shiftL` 25

data MBA = MBA (MutableByteArray# RealWorld)

newAligned :: Int -> IO MBA
newAligned (I# n) = IO $ \s -> case newAlignedPinnedByteArray# n 128# s of (# s', a #) -> (# s', MBA a #)

writeI, fetchAddI :: MBA -> Int -> Int -> IO ()
writeI (MBA a) (I# i) (I# x) = IO $ \s -> (# writeIntArray# a i x s, () #)
fetchAddI (MBA a) (I# i) (I# x) = IO $ \s -> case fetchAddIntArray# a i x s of (# s', _ #) -> (# s', () #)
readI :: MBA -> Int -> IO Int
readI (MBA a) (I# i) = IO $ \s -> case readIntArray# a i s of (# s', x #) -> (# s', I# x #)
atomicReadI :: MBA -> Int -> IO Int
atomicReadI (MBA a) (I# i) = IO $ \s -> case atomicReadIntArray# a i s of (# s', x #) -> (# s', I# x #)
atomicWriteI :: MBA -> Int -> Int -> IO ()
atomicWriteI (MBA a) (I# i) (I# x) = IO $ \s -> (# atomicWriteIntArray# a i x s, () #)

-- lance n fils sur des capacités distinctes (forkOn) et attend leur fin
parallelIO :: [IO ()] -> IO ()
parallelIO acts = do
  dones <- forM (zip [0 ..] acts) $ \(c, act) -> do
    mv <- newEmptyMVar
    _ <- forkOn c (act >> putMVar mv ())
    return mv
  mapM_ takeMVar dones

runK3 :: String -> Int -> Int -> IO ()
runK3 v warm reps = do
  let rmw = take 3 v == "rmw"
      stride = if drop (length v - 6) v == "padded" then 16 else 1
  putStrLn $ "META;k3_mechanism;" ++ if rmw then "fetchAddIntArray# (lock xadd)" else "atomicReadIntArray#/atomicWriteIntArray# (seuls accès garantis non élidables ; seq_cst)"
  a <- newAligned (128 * 8)
  let idx t = 16 + t * stride
      worker t
        | rmw = let go 0 = return (); go k = fetchAddI a (idx t) 1 >> go (k - 1 :: Int) in go iter3
        -- accès ordinaires : LLVM fusionne les 2^25 incréments en une addition (mesuré : 0,1 ms) ;
        -- la spécification exige l'accès le plus faible garanti visible et non élidable
        | otherwise = let go 0 = return (); go k = do { x <- atomicReadI a (idx t); atomicWriteI a (idx t) (x + 1); go (k - 1 :: Int) } in go iter3
  bench "k3" v "4x2^25" warm reps $ do
    forM_ [0 .. 3] $ \t -> writeI a (idx t) 0
    parallelIO [worker t | t <- [0 .. 3]]
    show . sum <$> mapM (readI a . idx) [0 .. 3]

-- ------------------------------------------------------------------ K4
{-# NOINLINE k4Natural #-}
{-# NOINLINE k4Branchless #-}
{-# NOINLINE k1Natural #-}
{-# NOINLINE k5Natural #-}
{-# NOINLINE k9Step #-}
k4Natural :: BS.ByteString -> Word64
k4Natural = BS.foldl' (\s x -> if x >= 128 then s + fromIntegral x else s) 0

k4Branchless :: BS.ByteString -> Word64
k4Branchless = BS.foldl' (\s x -> s + fromIntegral x * fromIntegral (x `shiftR` 7)) 0

runK4 :: String -> Int -> Int -> IO ()
runK4 v warm reps = do
  d <- dataDir
  bs0 <- BS.readFile (d ++ "/k4_bytes.u8")
  let bs = if v == "natural_sorted" then BS.sort bs0 else bs0
      f = if v == "branchless_unsorted" then k4Branchless else k4Natural
  ref <- newIORef bs
  bench "k4" v "16M" warm reps (readIORef ref >>= \x -> return $! show (f x))

-- ------------------------------------------------------------------ K5
inner5 :: Int
inner5 = 1 `shiftL` 16

k5Natural :: UArray Int Float -> UArray Int Float -> Float
k5Natural a b = foldl' (\s i -> s + a ! i * b ! i) 0 [0 .. 2047]

k5Tuned :: Ptr Float -> Ptr Float -> Int -> Float
k5Tuned (Ptr a) (Ptr b) (I# n) = go 0# z z z z
  where
    z = broadcastFloatX16# 0.0#
    go i s0 s1 s2 s3
      | isTrue# (i >=# n) =
          let s = plusFloatX16# (plusFloatX16# s0 s1) (plusFloatX16# s2 s3)
              (# e0, e1, e2, e3, e4, e5, e6, e7, e8, e9, e10, e11, e12, e13, e14, e15 #) = unpackFloatX16# s
           in F# ((((e0 `plusFloat#` e1) `plusFloat#` (e2 `plusFloat#` e3)) `plusFloat#` ((e4 `plusFloat#` e5) `plusFloat#` (e6 `plusFloat#` e7)))
                 `plusFloat#` (((e8 `plusFloat#` e9) `plusFloat#` (e10 `plusFloat#` e11)) `plusFloat#` ((e12 `plusFloat#` e13) `plusFloat#` (e14 `plusFloat#` e15))))
      | otherwise =
          let ld p k = indexFloatOffAddrAsFloatX16# p (i +# k)
              -- pas de primitive FMA vectorielle dans GHC 9.14 (seulement fmaddFloat# scalaire)
              fma x y z' = plusFloatX16# (timesFloatX16# x y) z'
           in go (i +# 64#) (fma (ld a 0#) (ld b 0#) s0) (fma (ld a 16#) (ld b 16#) s1)
                 (fma (ld a 32#) (ld b 32#) s2) (fma (ld a 48#) (ld b 48#) s3)

runK5 :: String -> Int -> Int -> IO ()
runK5 v warm reps = do
  ba <- loadBuf "k5_a.f32" :: IO (Buf Float)
  bb <- loadBuf "k5_b.f32" :: IO (Buf Float)
  ref <- newIORef ba
  if v == "tuned"
    then withBuf bb $ \pb -> bench "k5" v "2048x65536" warm reps $ do
      let loop :: Int -> Float -> IO Float
          loop 0 d = return d
          loop k _ = do Buf fa _ <- readIORef ref; d <- unsafeWithForeignPtr fa $ \pa -> return $! k5Tuned pa pb 2048; loop (k - 1) d
      printf "%.4f" <$> loop inner5 0
    else do
      la <- withBuf ba $ \p -> forM [0 .. 2047] (peekElemOff p)
      lb <- withBuf bb $ \p -> forM [0 .. 2047] (peekElemOff p)
      aref <- newIORef (listArray (0, 2047) la :: UArray Int Float)
      let ub = listArray (0, 2047) lb :: UArray Int Float
      bench "k5" v "2048x65536" warm reps $ do
        let loop :: Int -> Float -> IO Float
            loop 0 d = return d
            loop k _ = do ua <- readIORef aref; let !d = k5Natural ua ub in loop (k - 1) d
        printf "%.4f" <$> loop inner5 0

-- ------------------------------------------------------------------ K6
n6 :: Int
n6 = 1 `shiftL` 24

data Cols = Cols { csd, cpr :: !(Ptr Int32), cq, cd, ct, crf, cls :: !(Ptr Word8) }

rd8 :: Ptr Word8 -> Int -> IO Int
rd8 p i = fromIntegral <$> peekElemOff p i
rd32 :: Ptr Int32 -> Int -> IO Int
rd32 p i = fromIntegral <$> peekElemOff p i

q6Natural :: Cols -> Int -> Int -> IO Int
q6Natural c lo hi = go lo 0
  where
    go !i !s
      | i >= hi = return s
      | otherwise = do
          sd <- rd32 (csd c) i; d <- rd8 (cd c) i; q <- rd8 (cq c) i
          if sd >= 8766 && sd < 9131 && d >= 5 && d <= 7 && q < 24
            then do p <- rd32 (cpr c) i; go (i + 1) (s + p * d)
            else go (i + 1) s

-- Q6 optimisé : prédicat sans branchement (arithmétique), pointeurs bruts
q6Tuned :: Cols -> Int -> Int -> IO Int
q6Tuned c lo hi = go lo 0
  where
    go !i !s
      | i >= hi = return s
      | otherwise = do
          sd <- rd32 (csd c) i; d <- rd8 (cd c) i; q <- rd8 (cq c) i; p <- rd32 (cpr c) i
          let m = (fromEnum (fromIntegral (sd - 8766) < (365 :: Word)) .&. fromEnum (fromIntegral (d - 5) <= (2 :: Word))) .&. fromEnum (q < 24)
          go (i + 1) (s + (p * d) * m)

type Q1Acc = IORef [Int]

q1Natural :: Cols -> Int -> Int -> IO [Int]
q1Natural c lo hi = do
  acc <- mallocPlainForeignPtrAlignedBytes (30 * 8) 64 :: IO (ForeignPtr Int)
  unsafeWithForeignPtr acc $ \a -> do
    fillBytes a 0 (30 * 8)
    let add k x = peekElemOff a k >>= \y -> pokeElemOff a k (y + x)
        go !i
          | i >= hi = return ()
          | otherwise = do
              sd <- rd32 (csd c) i
              when (sd <= 10471) $ do
                rf <- rd8 (crf c) i; ls <- rd8 (cls c) i; q <- rd8 (cq c) i; d <- rd8 (cd c) i; t <- rd8 (ct c) i; p <- rd32 (cpr c) i
                let g = (rf * 2 + ls) * 5; dp = p * (100 - d)
                add g 1 >> add (g + 1) q >> add (g + 2) p >> add (g + 3) dp >> add (g + 4) (dp * (100 + t))
              go (i + 1)
    go lo
    forM [0 .. 29] (peekElemOff a)

-- Q1 optimisé : sans branchement, groupe 6 = rejet, accumulateurs en mémoire brute
q1Tuned :: Cols -> Int -> Int -> IO [Int]
q1Tuned c lo hi = do
  acc <- mallocPlainForeignPtrAlignedBytes (35 * 8) 64 :: IO (ForeignPtr Int)
  unsafeWithForeignPtr acc $ \a -> do
    fillBytes a 0 (35 * 8)
    let add k x = peekElemOff a k >>= \y -> pokeElemOff a k (y + x)
        go !i
          | i >= hi = return ()
          | otherwise = do
              sd <- rd32 (csd c) i; rf <- rd8 (crf c) i; ls <- rd8 (cls c) i; q <- rd8 (cq c) i
              d <- rd8 (cd c) i; t <- rd8 (ct c) i; p <- rd32 (cpr c) i
              let rej = (10471 - sd) `shiftR` 63 .&. 1
                  g = ((rf * 2 + ls) * (1 - rej) + 6 * rej) * 5
                  dp = p * (100 - d)
              add g 1 >> add (g + 1) q >> add (g + 2) p >> add (g + 3) dp >> add (g + 4) (dp * (100 + t))
              go (i + 1)
    go lo
    forM [0 .. 29] (peekElemOff a)

runK6 :: String -> Int -> Int -> String -> IO ()
runK6 v warm reps p = do
  sdB <- loadBuf "k6_shipdate.i32"; prB <- loadBuf "k6_extendedprice.i32"
  qB <- loadBuf "k6_quantity.u8"; dB <- loadBuf "k6_discount.u8"; tB <- loadBuf "k6_tax.u8"
  rfB <- loadBuf "k6_returnflag.u8"; lsB <- loadBuf "k6_linestatus.u8"
  withBuf sdB $ \sd -> withBuf prB $ \pr -> withBuf qB $ \q -> withBuf dB $ \d -> withBuf tB $ \t -> withBuf rfB $ \rf -> withBuf lsB $ \ls -> do
    let c = Cols sd pr q d t rf ls
        q1 = p == "q1"
        one lo hi = if q1 then sum <$> q1Tuned c lo hi else q6Tuned c lo hi
    bench "k6" v p warm reps $ case v of
      "mt" -> do
        parts <- forM [0 .. 3] $ \k -> newEmptyMVar >>= \mv -> forkOn k (one (n6 `div` 4 * k) (n6 `div` 4 * (k + 1)) >>= putMVar mv) >> return mv
        show . sum <$> mapM takeMVar parts
      "tuned" -> show <$> one 0 n6
      _ -> show <$> (if q1 then sum <$> q1Natural c 0 n6 else q6Natural c 0 n6)

-- ------------------------------------------------------------------ K7
runK7 :: String -> Int -> Int -> IO ()
runK7 v warm reps = do
  kB <- loadBuf "k7_keys.u32" :: IO (Buf Word32)
  vB <- loadBuf "k7_vals.u32" :: IO (Buf Word32)
  withBuf kB $ \keys -> withBuf vB $ \vals -> forM_ [-warm .. reps - 1] $ \r -> do
    let n = 1 `shiftL` 24 :: Int
    (chk, dt) <-
      if v == "natural"
        then do
          -- Data.IntMap.Strict : structure persistante idiomatique (arbre de Patricia)
          (m, dt) <- timed $ do
            let go !i !acc
                  | i >= n = return acc
                  | otherwise = do
                      k <- fromIntegral <$> peekElemOff keys i
                      x <- fromIntegral <$> peekElemOff vals i
                      go (i + 1) (IM.insertWith (\(!c1, !s1) (!c2, !s2) -> (c1 + c2, s1 + s2)) k (1 :: Int, x :: Int) acc)
            go 0 IM.empty
          let ws = IM.foldlWithKey' (\a k (_, s) -> a + s * ((k .&. 1023) + 1)) 0 m
          return (show (IM.size m) ++ ":" ++ show ws, dt)
        else do
          let logc = 21 :: Int; cap = 1 `shiftL` logc :: Int
          (tab, dt) <- timed $ do
            fp <- mallocPlainForeignPtrAlignedBytes (cap * 16) 64 :: IO (ForeignPtr Word8)
            unsafeWithForeignPtr fp $ \t -> do
              fillBytes t 0 (cap * 16)
              let go !i
                    | i >= n = return ()
                    | otherwise = do
                        k <- peekElemOff keys i
                        x <- peekElemOff vals i
                        let h = fromIntegral ((k * 0x9E3779B1) `shiftR` (32 - logc)) :: Int
                            probe !s = do
                              cnt <- peekByteOff t (s * 16 + 4) :: IO Word32
                              key <- peekByteOff t (s * 16) :: IO Word32
                              if cnt /= 0 && key /= k then probe ((s + 1) .&. (cap - 1)) else return s
                        s <- probe h
                        cnt <- peekByteOff t (s * 16 + 4) :: IO Word32
                        sm <- peekByteOff t (s * 16 + 8) :: IO Word64
                        pokeByteOff t (s * 16) k
                        pokeByteOff t (s * 16 + 4) (cnt + 1)
                        pokeByteOff t (s * 16 + 8) (sm + fromIntegral x)
                        go (i + 1)
              go 0
            return fp
          (nk, ws) <- unsafeWithForeignPtr tab $ \t -> foldM (\(!a, !b) s -> do
            cnt <- peekByteOff t (s * 16 + 4) :: IO Word32
            if cnt == 0 then return (a, b) else do
              key <- peekByteOff t (s * 16) :: IO Word32
              sm <- peekByteOff t (s * 16 + 8) :: IO Word64
              return (a + 1, b + sm * fromIntegral ((key .&. 1023) + 1))) (0 :: Int, 0 :: Word64) [0 .. cap - 1]
          return (show nk ++ ":" ++ show ws, dt)
    when (r >= 0) $ result "k7" v "16M/1M" r dt chk

-- ------------------------------------------------------------------ K8
data Tree = Leaf | Node !Int Tree Tree

tBuild :: Int -> Int -> (Tree, Int)
tBuild 0 c = (Node c Leaf Leaf, c + 1)
tBuild d c = let (l, c1) = tBuild (d - 1) (c + 1); (r, c2) = tBuild (d - 1) c1 in (Node c l r, c2)

tSum :: Tree -> Int
tSum Leaf = 0
tSum (Node v l r) = v + tSum l + tSum r

-- arène : nœuds indexés dans des tableaux mutables non boxés réutilisés
aBuild :: Ptr Int -> Ptr Int32 -> Ptr Int32 -> IORef Int -> Int -> Int -> IO (Int32, Int)
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

aSum :: Ptr Int -> Ptr Int32 -> Ptr Int32 -> Int32 -> IO Int
aSum av al ar i
  | i < 0 = return 0
  | otherwise = do
      v <- peekElemOff av (fromIntegral i); l <- peekElemOff al (fromIntegral i); r <- peekElemOff ar (fromIntegral i)
      a <- aSum av al ar l; b <- aSum av al ar r
      return $! v + a + b

runK8 :: String -> Int -> Int -> IO ()
runK8 v warm reps = do
  let q = 16384 :: Int
      (keep, _) = tBuild 20 0
      !lsum = tSum keep
  fv <- mallocForeignPtrArray 2047; fl <- mallocForeignPtrArray 2047; fr <- mallocForeignPtrArray 2047
  top <- newIORef 0
  unsafeWithForeignPtr fv $ \av -> unsafeWithForeignPtr fl $ \al -> unsafeWithForeignPtr fr $ \ar ->
    forM_ [-warm .. reps - 1] $ \r -> do
      t0 <- getMonotonicTimeNSec
      (total, lat) <- foldM (\(!tot, ls) qq -> do
        a <- getMonotonicTimeNSec
        !s <- if v == "tuned"
          then do writeIORef top 0; (root, _) <- aBuild av al ar top 10 qq; aSum av al ar root
          else return $! tSum (fst (tBuild 10 qq))
        b <- getMonotonicTimeNSec
        return (tot + s, (b - a) : ls)) (0, []) [0 .. q - 1]
      t1 <- getMonotonicTimeNSec
      when (r >= 0) $ do
        result "k8" v "16384x2047" r (fromIntegral (t1 - t0) * 1e-9) (show (total + lsum))
        let sl = listArray (0, q - 1) (sort lat) :: UArray Int Word64
        printf "LAT;%s;%d;%d;%d;%d;%d\n" v (sl ! (q `div` 2)) (sl ! (q * 9 `div` 10)) (sl ! (q * 99 `div` 100)) (sl ! (q * 999 `div` 1000)) (sl ! (q - 1))
  lsum `seq` return ()

-- ------------------------------------------------------------------ K9
m9 :: Int
m9 = 2048

k9Init :: Int -> Int -> Double
k9Init i j = fromIntegral ((i * 31 + j * 17) `mod` 1024) / 1024

-- naturel : tableau 2D non boxé immuable ; chaque itération construit un nouveau tableau
k9Step :: UArray (Int, Int) Double -> UArray (Int, Int) Double
k9Step a = listArray ((0, 0), (m9 - 1, m9 - 1))
  [ if i == 0 || j == 0 || i == m9 - 1 || j == m9 - 1 then a ! (i, j)
    else 0.25 * (((a ! (i - 1, j) + a ! (i + 1, j)) + a ! (i, j - 1)) + a ! (i, j + 1))
  | i <- [0 .. m9 - 1], j <- [0 .. m9 - 1] ]

-- optimisé : mémoire brute, vecteurs DoubleX8# (chargements non alignés), en place
k9Rows :: Ptr Double -> Ptr Double -> Int -> Int -> IO ()
k9Rows a b r0 r1 = forM_ [r0 .. r1 - 1] $ \i -> do
  let up = a `plusPtr` ((i - 1) * m9 * 8); mid = a `plusPtr` (i * m9 * 8); dn = a `plusPtr` ((i + 1) * m9 * 8)
      o = b `plusPtr` (i * m9 * 8) :: Ptr Double
      vec !j
        | j + 8 > m9 - 1 = return j
        | otherwise = do
            let !(Ptr u) = up; !(Ptr md) = mid; !(Ptr dw) = dn; !(Ptr oo) = o; !(I# jj) = j
                x = plusDoubleX8# (plusDoubleX8# (plusDoubleX8# (indexDoubleOffAddrAsDoubleX8# u jj) (indexDoubleOffAddrAsDoubleX8# dw jj))
                                    (indexDoubleOffAddrAsDoubleX8# md (jj -# 1#))) (indexDoubleOffAddrAsDoubleX8# md (jj +# 1#))
                y = timesDoubleX8# (broadcastDoubleX8# 0.25##) x
            IO (\s -> (# writeDoubleOffAddrAsDoubleX8# oo jj y s, () #))
            vec (j + 8)
      scal !j
        | j >= m9 - 1 = return ()
        | otherwise = do
            u <- peekElemOff up j; dw <- peekElemOff dn j; l <- peekElemOff mid (j - 1); rr <- peekElemOff mid (j + 1)
            pokeElemOff o j (0.25 * (((u + dw) + l) + rr))
            scal (j + 1)
  jEnd <- vec 1
  scal jEnd

runK9 :: String -> Int -> Int -> IO ()
runK9 v warm reps = forM_ [-warm .. reps - 1] $ \r ->
  if v == "natural"
    then do
      let a0 = listArray ((0, 0), (m9 - 1, m9 - 1)) [k9Init i j | i <- [0 .. m9 - 1], j <- [0 .. m9 - 1]] :: UArray (Int, Int) Double
      ref <- newIORef a0
      a0 `seq` return ()
      (a4, dt) <- timed (readIORef ref >>= \x -> return $! k9Step (k9Step (k9Step (k9Step x))))
      let s = foldl' (+) 0 (elems a4)
      when (r >= 0) $ result "k9" v "2048^2x4" r dt (printf "%.15e" s)
    else do
      fa <- mallocPlainForeignPtrAlignedBytes (m9 * m9 * 8) 64 :: IO (ForeignPtr Double)
      fb <- mallocPlainForeignPtrAlignedBytes (m9 * m9 * 8) 64 :: IO (ForeignPtr Double)
      unsafeWithForeignPtr fa $ \pa -> unsafeWithForeignPtr fb $ \pb -> do
        forM_ [0 .. m9 * m9 - 1] $ \k -> let x = k9Init (k `div` m9) (k `mod` m9) in pokeElemOff pa k x >> pokeElemOff pb k x
        let step a b = if v == "tuned" then k9Rows a b 1 (m9 - 1)
                       else parallelIO [k9Rows a b (1 + (m9 - 2) * t `div` 4) (1 + (m9 - 2) * (t + 1) `div` 4) | t <- [0 .. 3]]
        (_, dt) <- timed (step pa pb >> step pb pa >> step pa pb >> step pb pa)
        s <- foldM (\acc k -> (acc +) <$> peekElemOff pa k) 0 [0 .. m9 * m9 - 1]
        when (r >= 0) $ result "k9" v "2048^2x4" r dt (printf "%.15e" (s :: Double))

-- ------------------------------------------------------------------ K10
m10 :: Int
m10 = 1 `shiftL` 22
cap10 :: Int
cap10 = 1 `shiftL` 14

runK10 :: String -> Int -> Int -> IO ()
runK10 v warm reps = bench "k10" v "2^22" warm reps $
  if v == "natural"
    then do
      -- Control.Concurrent.Chan : canal (non borné) de base
      ch <- newChan
      res <- newEmptyMVar
      _ <- forkOn 1 (let go !s 0 = putMVar res s; go !s k = readChan ch >>= \x -> go (s + x) (k - 1 :: Int) in go (0 :: Int) m10)
      _ <- forkOn 2 (forM_ [1 .. m10] (writeChan ch))
      show <$> takeMVar res
    else do
      ctl <- newAligned (64 * 8) -- écriture @16, lecture @32 (128 o d'écart)
      atomicWriteI ctl 16 0 >> atomicWriteI ctl 32 0
      fb <- mallocPlainForeignPtrAlignedBytes (cap10 * 8) 64 :: IO (ForeignPtr Int)
      res <- newEmptyMVar
      unsafeWithForeignPtr fb $ \buf -> do
        let prod !w !rc !x
              | x > m10 = return ()
              | w - rc == cap10 = atomicReadI ctl 32 >>= \rc' -> prod w rc' x
              | otherwise = do pokeElemOff buf (w .&. (cap10 - 1)) x; atomicWriteI ctl 16 (w + 1); prod (w + 1) rc (x + 1)
            cons !rd !wc !s !k
              | k == 0 = putMVar res s
              | rd == wc = atomicReadI ctl 16 >>= \wc' -> cons rd wc' s k
              | otherwise = do x <- peekElemOff buf (rd .&. (cap10 - 1)); atomicWriteI ctl 32 (rd + 1); cons (rd + 1) wc (s + x) (k - 1)
        _ <- forkOn 1 (cons 0 0 0 m10)
        _ <- forkOn 2 (prod 0 0 1)
        show <$> takeMVar res

main :: IO ()
main = do
  args <- getArgs
  warm <- maybe 1 read <$> lookupEnv "WARMUP"
  let (k : v : repsS : rest) = args
      reps = read repsS
      p = case rest of (x : _) -> x; _ -> ""
  case k of
    "k1" -> runK1 v warm reps
    "k2" -> runK2 v warm reps p
    "k3" -> runK3 v warm reps
    "k4" -> runK4 v warm reps
    "k5" -> runK5 v warm reps
    "k6" -> runK6 v warm reps p
    "k7" -> runK7 v warm reps
    "k8" -> runK8 v warm reps
    "k9" -> runK9 v warm reps
    "k10" -> runK10 v warm reps
    _ -> return ()
