-- v4, point 6 (docs/V4_OPEN.md, 4) : sondes de la grille ouverte de Haskell
-- (C5 : parallel 3.3.0.0 ; D2 : atomic-primops 0.8.8 ; F4 : mmap 0.5.9).
{-# LANGUAGE BangPatterns #-}
module Main (main) where

import Control.Parallel.Strategies (parMap, rdeepseq, using, parListChunk, rseq)
import Control.Concurrent (getNumCapabilities, threadCapability, myThreadId)
import Control.Concurrent.MVar
import Control.Monad (forM_, replicateM_, forM)
import Data.Atomics (casIORef, readForCAS, peekTicket, storeLoadBarrier, loadLoadBarrier, writeBarrier,
                     fetchAddIntArray)
import Data.Atomics.Counter (newCounter, incrCounter, readCounter)
import Data.IORef
import Data.List (nub)
import Data.Primitive.ByteArray (newByteArray, readByteArray, writeByteArray)
import Control.Monad.Primitive (RealWorld)
import Control.Concurrent (forkOn)
import System.IO.MMap (mmapFileForeignPtr, Mode(ReadOnly))
import Foreign.ForeignPtr (ForeignPtr, withForeignPtr, castForeignPtr)
import Foreign.Ptr (Ptr, plusPtr)
import Foreign.Storable (peekElemOff)
import Data.Word (Word32)
import qualified Data.ByteString as B
import Data.Bits (shiftR, (.&.))
import GHC.Conc (numCapabilities)
import System.Directory (removeFile, getTemporaryDirectory)
import System.FilePath ((</>))
import System.IO (hSetEncoding, stdout, utf8)

c5 :: IO ()
c5 = do
  caps <- getNumCapabilities
  let chunk i = sum [i * 10000000 + 1 .. (i + 1) * 10000000] :: Int
      parts = parMap rdeepseq chunk [0 .. 3]
      total = sum parts
  let xs = [1 .. 4000000] :: [Int]
      s2 = sum (map (* 2) xs `using` parListChunk 100000 rdeepseq)
  total `seq` s2 `seq` putStrLn ("RESULT;C5;parallel;parMap rdeepseq sur 4 tranches : somme = " ++ show total
    ++ " (attendu 800000020000000) ; parListChunk 100000 rdeepseq : " ++ show s2 ++ " ; " ++ show caps
    ++ " capacités (+RTS -N4)")

d2 :: IO ()
d2 = do
  c <- newCounter 0
  dones <- forM [0 .. 3] $ \k -> do
    v <- newEmptyMVar
    _ <- forkOn k (replicateM_ 100000 (incrCounter 1 c) >> putMVar v ())
    return v
  mapM_ takeMVar dones
  n <- readCounter c
  r <- newIORef (0 :: Int)
  t <- readForCAS r
  (ok, t2) <- casIORef r t 41
  storeLoadBarrier
  loadLoadBarrier
  writeBarrier
  putStrLn ("RESULT;D2;atomic-primops;compteur atomique (incrCounter) incrémenté par 4 fils forkOn : " ++ show n
    ++ " (attendu 400000) ; casIORef réussi = " ++ show ok ++ ", valeur " ++ show (peekTicket t2)
    ++ " ; storeLoadBarrier, loadLoadBarrier, writeBarrier appelées ; aucun ordre relâché, acquire ou release sur les opérations elles-mêmes")

f4 :: IO ()
f4 = do
  dir <- getTemporaryDirectory
  let path = dir </> "open_probe_f4.bin"
      bytes = B.pack (concat [[fromIntegral (i .&. 255), fromIntegral ((i `shiftR` 8) .&. 255), 0, 0] | i <- [0 .. 1023 :: Int]])
  B.writeFile path bytes
  (fp, off, len) <- mmapFileForeignPtr path ReadOnly Nothing
  v <- withForeignPtr (castForeignPtr fp :: ForeignPtrW32) $ \p -> peekElemOff (p `plusPtr` off :: Ptr Word32) 1000
  maps <- readFile "/proc/self/maps"
  let mapped = any (\l -> "open_probe_f4.bin" `elem` words (map (\c -> if c == '/' then ' ' else c) l)) (lines maps)
  length maps `seq` putStrLn ("RESULT;F4;mmap;mmapFileForeignPtr : " ++ show len ++ " octets projetés (fichier dans /proc/self/maps = "
    ++ show mapped ++ ") ; castForeignPtr vers Word32, sans copie : élément 1000 = " ++ show v)
  removeFile path

type ForeignPtrW32 = ForeignPtr Word32

main :: IO ()
main = hSetEncoding stdout utf8 >> c5 >> d2 >> f4
