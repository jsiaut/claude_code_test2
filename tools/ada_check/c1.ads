package C1 is
   --  type vectoriel GCC déclaré en Ada : 8 flottants, une ligne ymm
   type V8 is array (1 .. 8) of Float with Alignment => 32;
   pragma Machine_Attribute (V8, "vector_type");
   function Add (A, B : V8) return V8;
   function Fma (A, B, C : V8) return V8;
   function Sum (A : V8) return Float;
end C1;
