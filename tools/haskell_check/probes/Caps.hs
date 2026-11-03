{-# LANGUAGE MagicHash, UnboxedTuples #-}
-- Sondes de la remarque sur Haskell (cases B2, B3, A7), paquets livrés avec GHC 9.14.1 seulement (base).
module Main (main) where
import Control.Monad (forM_)
import Foreign.Marshal.Alloc (mallocBytes, free)
import Foreign.Marshal.Array (peekArray, pokeArray, advancePtr)
import Foreign.Marshal.Pool (withPool, pooledMallocArray)
import Foreign.Ptr
import Foreign.Storable
import GHC.Exts

-- B2 : région (pool) de base : toutes les allocations libérées ensemble à la sortie de withPool
b2 :: IO Int
b2 = withPool $ \pool -> do
  xs <- mapM (\k -> do p <- pooledMallocArray pool 16 :: IO (Ptr Int); pokeArray p [k .. k + 15]; return p) [0 .. 999]
  sum <$> mapM (\p -> sum <$> peekArray 16 p) xs

-- B3 : n-uplet non boxé : jamais alloué sur le tas (type de sorte TYPE (TupleRep ...))
divMod# :: Int# -> Int# -> (# Int#, Int# #)
divMod# a b = (# quotInt# a b, remInt# a b #)
{-# NOINLINE divMod# #-}
b3 :: Int -> Int
b3 (I# n) = go 0# 0#
  where go i acc | isTrue# (i >=# n) = I# acc
                 | otherwise = case divMod# i 7# of (# q, r #) -> go (i +# 1#) (acc +# q +# r)

-- A7 : enregistrement à tableau fixe en ligne (16 flottants) par Storable : disposition à plat, tableau d'enregistrements
data P = P { pid :: !Int, pv :: [Float] }
instance Storable P where
  sizeOf _ = 8 + 16 * 4
  alignment _ = 8
  peek p = P <$> peekByteOff p 0 <*> peekArray 16 (castPtr p `plusPtr` 8)
  poke p (P i v) = pokeByteOff p 0 i >> pokeArray (castPtr p `plusPtr` 8) v
a7 :: IO (Int, Int, Float)
a7 = do
  buf <- mallocBytes (10 * sizeOf (undefined :: P)) :: IO (Ptr P)
  forM_ [0 .. 9] $ \k -> pokeElemOff buf k (P k (map fromIntegral [k .. k + 15]))
  P i v <- peekElemOff buf 7
  x <- peekByteOff buf (7 * 72 + 8 + 3 * 4) :: IO Float  -- 4e flottant du 8e enregistrement, lu à plat
  free buf
  return (sizeOf (undefined :: P), i, sum v + x)

main :: IO ()
main = do
  b2 >>= \s -> putStrLn ("B2 Foreign.Marshal.Pool : somme " ++ show s)
  putStrLn ("B3 n-uplets non boxés : " ++ show (b3 1000000))
  a7 >>= \r -> putStrLn ("A7 Storable à tableau en ligne (taille, id, somme) : " ++ show r)
