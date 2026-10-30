package body E5b is
   procedure Scale_Param (X : Vec; Y : out Vec; A : Float) is
   begin
      for I in Y'Range loop
         Y (I) := A * X (I) + 1.0;
      end loop;
   end Scale_Param;
   procedure Scale_Access (X, Y : Vec_Acc; A : Float) is
   begin
      for I in Y'Range loop
         Y (I) := A * X (I) + 1.0;
      end loop;
   end Scale_Access;
   procedure Axpy_Param (X : Vec; Y : in out Vec; A : Float) is
   begin
      for I in Y'Range loop
         Y (I) := Y (I) + A * X (I);
      end loop;
   end Axpy_Param;
end E5b;
