{-# LANGUAGE MagicHash, UnboxedTuples #-}
module Main (main) where
import GHC.Exts
import GHC.Prim (fmaddFloatX16#)
main :: IO ()
main = do
  let x = broadcastFloatX16# 2.0#; y = broadcastFloatX16# 3.0#; z = broadcastFloatX16# 1.0#
      r = fmaddFloatX16# x y z
      (# e0, _, _, _, _, _, _, _, _, _, _, _, _, _, _, e15 #) = unpackFloatX16# r
  print (F# e0, F# e15)
