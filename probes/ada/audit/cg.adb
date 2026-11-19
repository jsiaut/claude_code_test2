pragma Ada_2022;
with GNAT.Branch_Prediction;
package body Cg is
   --  builtins GCC importés (convention Intrinsic)
   procedure Atomic_Store (P : System.Address; V : Unsigned_64; Model : Integer)
     with Import, Convention => Intrinsic, External_Name => "__atomic_store_8";
   function Atomic_Fetch_Add (P : System.Address; V : Unsigned_64; Model : Integer) return Unsigned_64
     with Import, Convention => Intrinsic, External_Name => "__atomic_fetch_add_8";
   function Atomic_Load (P : System.Address; Model : Integer) return Unsigned_64
     with Import, Convention => Intrinsic, External_Name => "__atomic_load_8";
   procedure Fence (Model : Integer) with Import, Convention => Intrinsic, External_Name => "__atomic_thread_fence";
   procedure Pause with Import, Convention => Intrinsic, External_Name => "__builtin_ia32_pause";
   function Ternlog (A, B, C : V16I; Imm : Integer; K : Unsigned_16) return V16I
     with Import, Convention => Intrinsic, External_Name => "__builtin_ia32_pternlogd512_mask";
   procedure Prefetch (P : System.Address; RW, Loc : Integer) with Import, Convention => Intrinsic, External_Name => "__builtin_prefetch";
   procedure Ext (X : Unsigned_64) with Import, Convention => C, External_Name => "ext_hook";
   Relaxed : constant := 0; Acquire : constant := 2; Release : constant := 3; Seq_Cst : constant := 5;

   procedure St_Release (A : System.Address) is begin Atomic_Store (A, 1, Release); end St_Release;
   procedure St_Seqcst (A : System.Address) is begin Atomic_Store (A, 1, Seq_Cst); end St_Seqcst;
   function Add_Relaxed (A : System.Address) return Unsigned_64 is (Atomic_Fetch_Add (A, 1, Relaxed));
   procedure Spin (A : System.Address) is
   begin
      while Atomic_Load (A, Acquire) = 0 loop
         Pause;
      end loop;
      Fence (Seq_Cst);
   end Spin;
   function Tern (A, B, C : V16I) return V16I is (Ternlog (A, B, C, 16#96#, 16#FFFF#));
   function Hinted (X : Unsigned_64) return Unsigned_64 is
      R : Unsigned_64 := X;
   begin
      if GNAT.Branch_Prediction.Likely (X = 7) then
         Ext (X);
         R := X * 5;
      end if;
      return R + 1;
   end Hinted;
   function Unhinted (X : Unsigned_64) return Unsigned_64 is
      R : Unsigned_64 := X;
   begin
      if X = 9 then
         Ext (X);
         R := X * 7;
      end if;
      return R + 3;
   end Unhinted;
   procedure Pf (P : System.Address) is begin Prefetch (P, 0, 3); end Pf;
   function Idx_Checked (A : FA; I : Integer) return Float is (A (I));
   function Idx_Unchecked (A : FA; I : Integer) return Float is
      pragma Suppress (Index_Check);
   begin
      return A (I);
   end Idx_Unchecked;
   function Sum_Plain (A : FA) return Float is
      pragma Suppress (All_Checks);
      S : Float := 0.0;
   begin
      for X of A loop
         S := S + X;
      end loop;
      return S;
   end Sum_Plain;
   function Sq (X : Integer) return Integer is (X * X) with Static;
   function Sq_Const return Integer is (Sq (1234));
end Cg;
