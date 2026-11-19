--  Audit de la grille (docs/V4_PLAN.md 2.1) : sonde exécutée d'Ada (GNAT 16.2), cas positifs. run.sh y ajoute le
--  code produit, les échecs et les recherches d'absence.
pragma Ada_2022;
with Ada.Text_IO; use Ada.Text_IO;
with Ada.Command_Line;
with Ada.Streams.Stream_IO;
with Interfaces; use Interfaces;
with Interfaces.C;
with System; use System;
with System.Storage_Elements; use System.Storage_Elements;
with System.Storage_Pools; use System.Storage_Pools;
with System.Address_To_Access_Conversions;
with System.Machine_Code; use System.Machine_Code;
with System.Mmap; use System.Mmap;

procedure Audit is
   function Img (X : Integer_Address) return String is (Integer_Address'Image (X));
   function Addr (A : Address) return Integer_Address is (To_Integer (A));
   function Dist (A, B : Address) return Integer_Address is
     (if To_Integer (A) > To_Integer (B) then To_Integer (A) - To_Integer (B) else To_Integer (B) - To_Integer (A));

   type Part is record
      X, Y, Z : Float;
      M       : Unsigned_8;
   end record;
   type Part_Arr is array (Positive range <>) of Part;
   type F16 is array (1 .. 16) of Float;
   type Inl is record
      N : Unsigned_32;
      A : F16;
   end record;
   type Line is record
      V : Unsigned_64;
   end record with Alignment => 64;
   type Line_Ptr is access Line;
   type Line_Arr is array (1 .. 4) of Line;
   type Line_Arr_Ptr is access Line_Arr;

   --  B2 : pool de stockage utilisateur sur un tampon
   type Bump_Pool is new Root_Storage_Pool with record
      Buf : Storage_Array (1 .. 4096);
      Top : Storage_Offset := 0;
   end record;
   overriding procedure Allocate (P : in out Bump_Pool; A : out Address; Size, Alignment : Storage_Count);
   overriding procedure Deallocate (P : in out Bump_Pool; A : Address; Size, Alignment : Storage_Count) is null;
   overriding function Storage_Size (P : Bump_Pool) return Storage_Count is (P.Buf'Length);
   overriding procedure Allocate (P : in out Bump_Pool; A : out Address; Size, Alignment : Storage_Count) is
      T : constant Storage_Offset := (P.Top + Alignment - 1) / Alignment * Alignment;
   begin
      A := P.Buf (P.Buf'First + T)'Address;
      P.Top := T + Size;
   end Allocate;
   Pool : Bump_Pool;
   type Node is record
      V : Integer_64;
   end record;
   type Node_Ptr is access Node with Storage_Pool => Pool;

   function Gettid return Interfaces.C.int with Import, Convention => C, External_Name => "gettid"; --  observation

   generic
      type T is digits <>;
   function Gsum (A, B : T) return T;
   function Gsum (A, B : T) return T is (A + B);
   function Gsum_F is new Gsum (Float);
   function Gsum_D is new Gsum (Long_Float);
   function Sq (X : Integer) return Integer is (X * X) with Static;
   Sq1234 : constant := Sq (1234);

   function Threads_Now return Integer is
      F : File_Type;
      N : Integer := -1;
   begin
      Open (F, In_File, "/proc/self/status");
      while not End_Of_File (F) loop
         declare
            L : constant String := Get_Line (F);
         begin
            if L'Length > 8 and then L (L'First .. L'First + 7) = "Threads:" then
               N := 0;
               for C of L (L'First + 8 .. L'Last) loop
                  if C in '0' .. '9' then
                     N := N * 10 + (Character'Pos (C) - Character'Pos ('0'));
                  end if;
               end loop;
            end if;
         end;
      end loop;
      Close (F);
      return N;
   end Threads_Now;

   V : Part_Arr (1 .. 8) := (others => (1.0, 2.0, 3.0, 4));
   Raw : Storage_Array (1 .. 4) with Import, Address => V (1)'Address;
begin
   --  A1
   Put_Line ("CAP;A1;1;[exécutée] tableau de Part : pas de" & Img (Addr (V (2)'Address) - Addr (V (1)'Address))
             & " o = Part'Object_Size/8" & Integer'Image (Part'Object_Size / 8) & " ; les 4 premiers octets sont le Float X en ligne :"
             & Raw (1)'Image & Raw (2)'Image & Raw (3)'Image & Raw (4)'Image);
   --  A4
   declare
      L  : constant Line_Ptr := new Line;
      LA : constant Line_Arr_Ptr := new Line_Arr;
   begin
      Put_Line ("CAP;A4;1;[exécutée] aspect Alignment => 64 : Line'Alignment =" & Line'Alignment'Image & ", new Line à"
                & Img (Addr (L.all'Address) mod 64) & " mod 64, tableau de Line : pas" & Img (Addr (LA (2)'Address) - Addr (LA (1)'Address))
                & " o, éléments à" & Img (Addr (LA (2)'Address) mod 64) & " mod 64");
   end;
   --  A7, A8
   declare
      I : Inl;
   begin
      Put_Line ("CAP;A7;1;[exécutée] record (N : Unsigned_32; A : array (1 .. 16) of Float) :" & Integer'Image (Inl'Size / 8)
                & " o, I.A'Position =" & I.A'Position'Image & " (tableau en ligne)");
   end;
   Put_Line ("CAP;A8;1;[exécutée] Unsigned_8/Integer_16/Float :" & Integer'Image (Unsigned_8'Size / 8) & " /"
             & Integer'Image (Integer_16'Size / 8) & " /" & Integer'Image (Float'Size / 8)
             & " o ; un array (1 .. 1000) of Unsigned_8 occupe" & Integer'Image (1000 * Unsigned_8'Size / 8) & " o");
   --  B1
   Put_Line ("CAP;B1;1;[exécutée] aucun ramasse-miettes : mémoire rendue par Unchecked_Deallocation ou par la portée ;"
             & Threads_Now'Image & " fil (Threads: de /proc/self/status, aucun fil de collecteur)");
   --  B2
   declare
      P1 : constant Node_Ptr := new Node'(V => 7);
      P2 : constant Node_Ptr := new Node'(V => 8);
      Inside : constant Boolean := Addr (P2.all'Address) >= Addr (Pool.Buf (1)'Address)
        and then Addr (P2.all'Address) < Addr (Pool.Buf (1)'Address) + 4096;
   begin
      Put_Line ("CAP;B2;1;[exécutée] pool de stockage utilisateur (System.Storage_Pools) attaché au type d'accès : new y alloue,"
                & " bloc dans le tampon = " & Inside'Image & "," & Pool.Top'Image & " o consommés ; P1.V + P2.V ="
                & Integer_64'Image (P1.V + P2.V) & " ; sous-pools en System.Storage_Pools.Subpools");
   end;
   --  B3
   declare
      Local : Storage_Array (1 .. 4096) := (others => 1);
      Marker : Storage_Element := Local (1);
      Heap : constant Line_Ptr := new Line;
   begin
      Marker := Marker + 1;
      Put_Line ("CAP;B3;1;[exécutée] Storage_Array (1 .. 4096) local à" & Img (Dist (Marker'Address, Local'Address))
                & " o d'une autre variable locale, à" & Img (Dist (Heap.all'Address, Local'Address)) & " o du tas : sur la pile");
   end;
   --  B5
   declare
      type U32_Arr is array (1 .. 8) of Unsigned_32;
      Buf : U32_Arr := (others => 0);
      package Conv is new System.Address_To_Access_Conversions (Unsigned_32);
   begin
      Conv.To_Pointer (Buf (1)'Address + Storage_Offset (12)).all := 42;
      Conv.To_Pointer (Buf'Address + Storage_Offset (16)).all := 7;
      Put_Line ("CAP;B5;1;[exécutée] System.Address + Storage_Offset et Address_To_Access_Conversions : écriture à +12 -> Buf (4) ="
                & Buf (4)'Image & " ; à +16 -> Buf (5) =" & Buf (5)'Image);
   end;
   --  D1
   declare
      Parts : array (0 .. 3) of Unsigned_64 := (others => 0);
      Tids  : array (0 .. 3) of Interfaces.C.int := (others => 0);
      task type Worker (T : Natural);
      task body Worker is
         S : Unsigned_64 := 0;
      begin
         for I in T * 1000 .. (T + 1) * 1000 - 1 loop
            S := S + Unsigned_64 (I);
         end loop;
         Parts (T) := S;
         Tids (T) := Gettid;
      end Worker;
      Distinct : Natural := 0;
      use type Interfaces.C.int;
   begin
      declare
         W0 : Worker (0); W1 : Worker (1); W2 : Worker (2); W3 : Worker (3);
      begin
         null;
      end;
      for I in Tids'Range loop
         declare
            Seen : Boolean := False;
         begin
            for J in Tids'First .. I - 1 loop
               Seen := Seen or else Tids (J) = Tids (I);
            end loop;
            if not Seen then
               Distinct := Distinct + 1;
            end if;
         end;
      end loop;
      Put_Line ("CAP;D1;1;[exécutée] tâches Ada : 4 tâches," & Distinct'Image & " identifiants de fil (gettid) distincts, somme"
                & Unsigned_64'Image (Parts (0) + Parts (1) + Parts (2) + Parts (3)) & " (attendu 7998000)");
   end;
   --  E2
   declare
      X : Integer := 41;
   begin
      Asm ("addl $1, %0", Outputs => Integer'Asm_Output ("=r", X), Inputs => Integer'Asm_Input ("0", X), Volatile => True);
      Put_Line ("CAP;E2;1;[exécutée] System.Machine_Code.Asm (""addl $1, %0"") : 41 ->" & X'Image);
   end;
   --  E7
   Put_Line ("FACT;E7;fonction d'expression statique Sq (1234) en nombre nommé =" & Integer'Image (Sq1234)
             & " ; Gsum instanciée pour Float :" & Gsum_F (1.5, 2.5)'Image & ", pour Long_Float :" & Gsum_D (1.5, 2.25)'Image);
   --  F1
   declare
      type Matrix is array (Positive range <>, Positive range <>) of Float;
      N : constant Positive := Ada.Command_Line.Argument_Count + 3;
      M : Matrix (1 .. N, 1 .. 4) := (others => (others => 0.0));
      type CMatrix is array (Positive range <>, Positive range <>) of Float with Convention => Fortran;
      C : CMatrix (1 .. N, 1 .. 4) := (others => (others => 0.0));
   begin
      Put_Line ("CAP;F1;1;[exécutée] array (Positive range <>, Positive range <>) of Float, bornes connues à l'exécution (" & N'Image
                & " x 4) : M (2, 1)'Address - M (1, 4)'Address =" & Img (Addr (M (2, 1)'Address) - Addr (M (1, 4)'Address))
                & " o (ligne par ligne) ; avec Convention => Fortran, C (2, 1) - C (1, 1) =" & Img (Addr (C (2, 1)'Address) - Addr (C (1, 1)'Address))
                & " o (colonne par colonne)");
   end;
   --  F3
   declare
      type U8 is mod 256;
      X : U8 := 250;
      U : Unsigned_32 := Unsigned_32'Last;
      I : Integer := Integer'Last;
      Raised : Boolean := False;
   begin
      X := X + 10;
      U := U + 1;
      begin
         I := I + Integer (Ada.Command_Line.Argument_Count) + 1;
      exception
         when Constraint_Error => Raised := True;
      end;
      Put_Line ("CAP;F3;1;[exécutée] type modulaire mod 256 : 250 + 10 =" & X'Image & " ; Unsigned_32'Last + 1 =" & U'Image
                & " ; Integer'Last + 1 lève Constraint_Error : " & Raised'Image & " (signés vérifiés, modulaires enveloppants)" & I'Image (1 .. 0));
   end;
   --  F4 (½ : System.Mmap, unité interne de GNAT)
   declare
      use Ada.Streams.Stream_IO;
      Path : constant String := "/tmp/ada_audit_f4.bin";
      FS   : Ada.Streams.Stream_IO.File_Type;
      Vals : constant array (1 .. 4) of Float := (1.5, 2.5, 3.5, 4.5);
      MF   : Mapped_File;
      MR   : Mapped_Region;
   begin
      Create (FS, Out_File, Path);
      Write (FS, (1 .. 16 => 0));
      Close (FS);
      declare
         Out_F : Ada.Streams.Stream_IO.File_Type;
         SA : Ada.Streams.Stream_Element_Array (1 .. 16) with Import, Address => Vals'Address;
      begin
         Open (Out_F, Out_File, Path);
         Write (Out_F, SA);
         Close (Out_F);
      end;
      MF := Open_Read (Path);
      MR := Read (MF);
      declare
         FL : array (1 .. 4) of Float with Import, Address => Data (MR).all'Address;
      begin
         Put_Line ("CAP;F4;0.5;[exécutée] System.Mmap (unité interne de GNAT, s-mmap.ads) + réinterprétation par adresse :"
                   & FL (1)'Image & FL (4)'Image & " ; projeté (Is_Mutable = " & Is_Mutable (MR)'Image & ")");
      end;
      Free (MR);
      Close (MF);
   end;
end Audit;
