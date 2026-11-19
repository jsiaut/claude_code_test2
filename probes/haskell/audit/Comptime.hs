-- Audit de la grille, Haskell, E7 : fonction évaluée pendant la compilation par une épissure de Template Haskell
-- (elle doit être définie dans un autre module que l'épissure).
module Comptime (fib) where

fib :: Int -> Int
fib n = if n < 2 then n else fib (n - 1) + fib (n - 2)
