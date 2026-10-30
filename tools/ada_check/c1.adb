package body C1 is
   function Add (A, B : V8) return V8 is
      R : V8;
   begin
      for I in R'Range loop
         R (I) := A (I) + B (I);
      end loop;
      return R;
   end Add;
   function Fma (A, B, C : V8) return V8 is
      R : V8;
   begin
      for I in R'Range loop
         R (I) := A (I) * B (I) + C (I);
      end loop;
      return R;
   end Fma;
   function Sum (A : V8) return Float is
      S : Float := 0.0;
   begin
      for X of A loop
         S := S + X;
      end loop;
      return S;
   end Sum;
end C1;
