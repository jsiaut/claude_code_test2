package body E5c is
   procedure Scale_Param (X : CVec; Y : out CVec; A : Float) is
   begin
      for I in Y'Range loop
         Y (I) := A * X (I) + 1.0;
      end loop;
   end Scale_Param;
   procedure Scale_Access (X, Y : CVec_Acc; A : Float) is
   begin
      for I in Y'Range loop
         Y (I) := A * X (I) + 1.0;
      end loop;
   end Scale_Access;
   procedure Stencil (A : Grid; B : in out Grid) is
   begin
      for I in 1 .. 2046 loop
         for J in 1 .. 2046 loop
            B (I, J) := 0.25 * (((A (I - 1, J) + A (I + 1, J)) + A (I, J - 1)) + A (I, J + 1));
         end loop;
      end loop;
   end Stencil;
end E5c;
