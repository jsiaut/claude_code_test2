package E5b is
   type Vec is array (Positive range <>) of Float;
   type Vec_Acc is access all Vec;
   --  la forme du stencil : l'écriture ne relit pas le tableau écrit
   procedure Scale_Param (X : Vec; Y : out Vec; A : Float);
   procedure Scale_Access (X, Y : Vec_Acc; A : Float);
   procedure Axpy_Param (X : Vec; Y : in out Vec; A : Float);
end E5b;
