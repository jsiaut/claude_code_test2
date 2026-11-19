--  Code produit, lu par run.sh (gcc-16 -S -O3 -gnat2022 -march=native ; -ffast-math pour la comparaison de C4).
pragma Ada_2022;
with Interfaces; use Interfaces;
with System;
package Cg is
   type V16I is array (0 .. 15) of Integer_32 with Alignment => 64;
   pragma Machine_Attribute (V16I, "vector_type");
   procedure St_Release (A : System.Address) with Export, Convention => C, External_Name => "st_release";
   procedure St_Seqcst (A : System.Address) with Export, Convention => C, External_Name => "st_seqcst";
   function Add_Relaxed (A : System.Address) return Unsigned_64 with Export, Convention => C, External_Name => "add_relaxed";
   procedure Spin (A : System.Address) with Export, Convention => C, External_Name => "spin";
   function Tern (A, B, C : V16I) return V16I with Export, Convention => C, External_Name => "tern";
   function Hinted (X : Unsigned_64) return Unsigned_64 with Export, Convention => C, External_Name => "hinted";
   function Unhinted (X : Unsigned_64) return Unsigned_64 with Export, Convention => C, External_Name => "unhinted";
   procedure Pf (P : System.Address) with Export, Convention => C, External_Name => "pf";
   type FA is array (Positive range <>) of Float;
   function Idx_Checked (A : FA; I : Integer) return Float with Export, Convention => C, External_Name => "idx_checked";
   function Idx_Unchecked (A : FA; I : Integer) return Float with Export, Convention => C, External_Name => "idx_unchecked";
   function Sum_Plain (A : FA) return Float with Export, Convention => C, External_Name => "sum_plain";
   function Sq_Const return Integer with Export, Convention => C, External_Name => "sq_const";
end Cg;
