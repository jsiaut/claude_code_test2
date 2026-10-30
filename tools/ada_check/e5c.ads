package E5c is
   type CVec is array (1 .. 4096) of Float;
   type CVec_Acc is access all CVec;
   --  type contraint : passage par référence simple (pointeur fin)
   procedure Scale_Param (X : CVec; Y : out CVec; A : Float);
   procedure Scale_Access (X, Y : CVec_Acc; A : Float);
   type Grid is array (0 .. 2047, 0 .. 2047) of Long_Float;
   procedure Stencil (A : Grid; B : in out Grid);
end E5c;
