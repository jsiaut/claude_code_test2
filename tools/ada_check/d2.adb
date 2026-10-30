package body D2 is
   procedure Store_Seq (V : Integer_64) is
   begin
      C_Seq := V;
   end Store_Seq;
   procedure Store_Rel (V : Integer_64) is
   begin
      C_Rel := V;
   end Store_Rel;
   function Load_Rel return Integer_64 is (C_Rel);
end D2;
