{-# LANGUAGE MagicHash, UnboxedTuples #-}
import GHC.Exts
import GHC.IO (IO (..))
import GHC.Float (castFloatToWord32)
import Foreign.Marshal.Alloc (allocaBytesAligned)
import Foreign.Ptr (ptrToIntPtr)
import Numeric (showHex)
main :: IO ()
main = do
  putStrLn ("CAP;A5;0.5;castFloatToWord32 1.0 = 0x" ++ showHex (castFloatToWord32 1.0) "")
  allocaBytesAligned 256 64 $ \p -> do
    putStrLn ("CAP;A4;0.5;allocaBytesAligned 64 -> adresse mod 64 = " ++ show (ptrToIntPtr p `mod` 64))
    let !(Ptr a) = p
    IO (\s -> (# prefetchAddr3# a 0# s, () #))
    putStrLn "CAP;E4;1;prefetchAddr3# (GHC.Exts)"
