-- Audit de la grille, Haskell, A2 et A3 : décalages et tailles de structures C, calculés par hsc2hs (livré avec GHC)
-- à partir du compilateur C, pour écrire les instances Storable.
module Layout (offB, offC, sizeS, sizeP, offPB) where
#include <stdint.h>
#def struct s { uint8_t a; uint32_t b; double c; };
#def struct __attribute__((packed)) p { uint8_t a; uint32_t b; };
offB, offC, sizeS, sizeP, offPB :: Int
offB = #{offset struct s, b}
offC = #{offset struct s, c}
sizeS = #{size struct s}
sizeP = #{size struct p}
offPB = #{offset struct p, b}
