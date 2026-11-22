--  Implémentation Ada 2022 (GNAT 16) des noyaux de docs/SPEC.md.
--  Correction de la remarque sur Ada (docs/ADA.md), reportée le 21 novembre (v4, point 4 : docs/V4_CONVERGE.md, 4.1) :
--  les sept sous-programmes « tuned » qui portent pragma Suppress (All_Checks) sont marqués « with No_Inline ». Sans
--  -gnatp, GNAT compile avec -fnon-call-exceptions ; inlinés dans un appelant à régions d'exceptions, leurs boucles
--  n'étaient pas vectorisées.
--  « natural » : enregistrements et tableaux Ada, vérifications à l'exécution actives (défaut GNAT),
--  Ada.Containers.Hashed_Maps, types accès + Unchecked_Deallocation, objets protégés, tâches.
--  « tuned » : pragma Suppress (All_Checks), clauses de représentation (alignement, taille),
--  types vectoriels GCC (Machine_Attribute "vector_type") + builtins importés (Intrinsic),
--  pool de stockage utilisateur, atomiques Ada 2022 et primitives GNAT (acquire/release).
pragma Ada_2022;
with Ada.Text_IO;                 use Ada.Text_IO;
with Cachelines.Padded;           --  piste ouverte (v4, point 6) : cachelines 0.1.0
with Ada.Real_Time;               use Ada.Real_Time;
with Ada.Command_Line;            use Ada.Command_Line;
with Ada.Environment_Variables;
with Ada.Strings;                 use Ada.Strings;
with Ada.Strings.Fixed;           use Ada.Strings.Fixed;
with Ada.Long_Float_Text_IO;
with Ada.Containers.Hashed_Maps;
with Ada.Unchecked_Deallocation;
with Ada.Unchecked_Conversion;
with Interfaces;                  use Interfaces;
with Interfaces.C;
with System;                      use System;
with System.Storage_Elements;     use System.Storage_Elements;
with System.Storage_Pools;        use System.Storage_Pools;
with System.Atomic_Operations.Integer_Arithmetic;
with System.Atomic_Primitives;    --  unité GNAT : __atomic_load_n / __atomic_store_n avec ordre mémoire
with GNAT.OS_Lib;

procedure Ms is

   ---------------------------------------------------------------- harnais
   T_Start : constant Time := Clock;
   function Now return Long_Float is (Long_Float (To_Duration (Clock - T_Start)));
   function Now_Ns return Integer_64 is (Integer_64 (Long_Float (To_Duration (Clock - T_Start)) * 1.0E9));

   function Env (Name, Default : String) return String is
     (if Ada.Environment_Variables.Exists (Name) then Ada.Environment_Variables.Value (Name) else Default);
   Data_Dir : constant String := Env ("MS_DATA", "/opt/msdata");
   Warm     : constant Integer := Integer'Value (Env ("WARMUP", "1"));

   function Img (X : Integer_64) return String is (Trim (X'Image, Left));
   function Imgu (X : Unsigned_64) return String is (Trim (X'Image, Left));
   function Fix (X : Long_Float; Aft : Natural) return String is
      S : String (1 .. 48);
   begin
      Ada.Long_Float_Text_IO.Put (S, X, Aft => Aft, Exp => 0);
      return Trim (S, Left);
   end Fix;
   function Sci (X : Long_Float) return String is
      S : String (1 .. 48);
   begin
      Ada.Long_Float_Text_IO.Put (S, X, Aft => 15, Exp => 3);
      return Trim (S, Left);
   end Sci;
   procedure Result (K, V, P : String; Rep : Integer; Sec : Long_Float; Chk : String) is
   begin
      Put_Line ("RESULT;" & K & ";" & V & ";" & P & ";" & Trim (Rep'Image, Left) & ";" & Fix (Sec, 9) & ";" & Chk);
      Flush;
   end Result;

   --  tableaux de données alignés sur 64 octets (clause d'alignement respectée par l'allocateur)
   type U8_Arr is array (Natural range <>) of Unsigned_8 with Alignment => 64;
   type U8_Acc is access U8_Arr;
   type I32_Arr is array (Natural range <>) of Integer_32 with Alignment => 64;
   type I32_Acc is access I32_Arr;
   type U32_Arr is array (Natural range <>) of Unsigned_32 with Alignment => 64;
   type U32_Acc is access U32_Arr;
   type F32_Arr is array (Natural range <>) of Float with Alignment => 64;
   type F32_Acc is access F32_Arr;

   generic
      type Elem is private;
      type Arr is array (Natural range <>) of Elem;
      type Arr_Acc is access Arr;
   function Load (Name : String) return Arr_Acc;
   function Load (Name : String) return Arr_Acc is
      use GNAT.OS_Lib;
      FD    : constant File_Descriptor := Open_Read (Data_Dir & "/" & Name, Binary);
      Bytes : constant Long_Integer := File_Length (FD);
      A     : constant Arr_Acc := new Arr (0 .. Natural (Bytes / Long_Integer (Elem'Size / 8)) - 1);
      Done  : Long_Integer := 0;
      Got   : Integer;
   begin
      while Done < Bytes loop
         Got := Read (FD, A.all'Address + Storage_Offset (Done), Integer (Long_Integer'Min (Bytes - Done, 2 ** 30)));
         exit when Got <= 0;
         Done := Done + Long_Integer (Got);
      end loop;
      Close (FD);
      return A;
   end Load;
   function Load_U8 is new Load (Unsigned_8, U8_Arr, U8_Acc);
   function Load_I32 is new Load (Integer_32, I32_Arr, I32_Acc);
   function Load_U32 is new Load (Unsigned_32, U32_Arr, U32_Acc);
   function Load_F32 is new Load (Float, F32_Arr, F32_Acc);

   --  builtins GCC importés (convention Intrinsic)
   procedure Prefetch (Addr : System.Address; RW, Locality : Integer);
   pragma Import (Intrinsic, Prefetch, "__builtin_prefetch");
   procedure Pause;
   pragma Import (Intrinsic, Pause, "__builtin_ia32_pause");
   type M512 is array (0 .. 15) of Float with Alignment => 64;
   pragma Machine_Attribute (M512, "vector_type");
   function Fmadd (A, B, C : M512; K : Interfaces.C.unsigned_short; R : Integer) return M512;
   pragma Import (Intrinsic, Fmadd, "__builtin_ia32_vfmaddps512_mask");
   function Vadd (A, B, Src : M512; K : Interfaces.C.unsigned_short; R : Integer) return M512;
   pragma Import (Intrinsic, Vadd, "__builtin_ia32_addps512_mask");

   Zero : Float := 0.0 with Volatile, Export, Convention => C, External_Name => "ms_zero";
   Sink : Float := 0.0 with Volatile;

   ---------------------------------------------------------------- K1
   N1 : constant := $MS_N1;
   type Particle is record
      X, Y, Z, Vx, Vy, Vz, Ax, Ay, Az, Mass, Charge, Radius, Temp, Pressure, Energy, Density : Float;
   end record;
   type Particle_Arr is array (Natural range <>) of Particle;
   type Particle_Acc is access Particle_Arr;
   function Load_P is new Load (Particle, Particle_Arr, Particle_Acc);

   function K1_Natural (Ps : Particle_Arr) return Long_Float is
      E : Long_Float := 0.0;
   begin
      for P of Ps loop
         E := E + 0.5 * Long_Float (P.Mass) * Long_Float (P.Vx * P.Vx + P.Vy * P.Vy + P.Vz * P.Vz);
      end loop;
      return E;
   end K1_Natural;
   function K1_Aos (Ps : Particle_Arr) return Long_Float with No_Inline is  --  No_Inline : correction du 30/10 (docs/ADA.md)
      pragma Suppress (All_Checks);
      Acc : array (0 .. 7) of Long_Float := [others => 0.0];
      E   : Long_Float := 0.0;
   begin
      for I in 0 .. Ps'Length / 8 - 1 loop
         for K in 0 .. 7 loop
            declare
               Q : Particle renames Ps (Ps'First + I * 8 + K);
            begin
               Acc (K) := Acc (K) + Long_Float (0.5 * Q.Mass * (Q.Vx * Q.Vx + Q.Vy * Q.Vy + Q.Vz * Q.Vz));
            end;
         end loop;
      end loop;
      for A of Acc loop
         E := E + A;
      end loop;
      return E;
   end K1_Aos;
   function K1_Soa (Vx, Vy, Vz, M : F32_Arr) return Long_Float with No_Inline is  --  No_Inline : correction du 30/10 (docs/ADA.md)
      pragma Suppress (All_Checks);
      Acc : array (0 .. 15) of Long_Float := [others => 0.0];
      E   : Long_Float := 0.0;
   begin
      for I in 0 .. Vx'Length / 16 - 1 loop
         for K in 0 .. 15 loop
            declare
               J : constant Natural := I * 16 + K;
            begin
               Acc (K) := Acc (K) + Long_Float (0.5 * M (J) * (Vx (J) * Vx (J) + Vy (J) * Vy (J) + Vz (J) * Vz (J)));
            end;
         end loop;
      end loop;
      for A of Acc loop
         E := E + A;
      end loop;
      return E;
   end K1_Soa;

   --  Empreinte K1 (D2a) : RSS courant en octets (/proc/self/statm, 2e champ ; pages de 4 Kio)
   function Rss_Now return Long_Long_Integer is
      F    : File_Type;
      Line : String (1 .. 256);
      Last : Natural;
      P, Q : Natural;
   begin
      Open (F, In_File, "/proc/self/statm");
      Get_Line (F, Line, Last);
      Close (F);
      P := Index (Line (1 .. Last), " ");
      Q := Index (Line (P + 1 .. Last), " ");
      return Long_Long_Integer'Value (Line (P + 1 .. Q - 1)) * 4096;
   exception
      when others => return 0;
   end Rss_Now;

   function Img (X : Long_Long_Integer) return String is (Trim (Long_Long_Integer'Image (X), Left));

   procedure Run_K1 (V : String; Reps : Integer) is
      Ps : Particle_Acc;
      M1 : Long_Long_Integer := 0;
      T0, T1, E : Long_Float;
   begin
      if V = "footprint0" or else V = "footprint_raw" then
         Result ("k1", V, "energy", 0, 0.0, "0");
         return;
      end if;
      if V = "footprint" then
         M1 := Rss_Now;  --  P1 : avant la lecture (la collection naturelle est le tableau lu)
      end if;
      Ps := Load_P ("k1_particles.f32");
      if V = "soa" then
         declare
            type Cols is array (0 .. 15) of F32_Acc;
            C : Cols;
         begin
            for K in 0 .. 15 loop
               C (K) := new F32_Arr (0 .. N1 - 1);
            end loop;
            for I in 0 .. N1 - 1 loop
               declare
                  P : Particle renames Ps (I);
               begin
                  C (0) (I) := P.X; C (1) (I) := P.Y; C (2) (I) := P.Z; C (3) (I) := P.Vx; C (4) (I) := P.Vy;
                  C (5) (I) := P.Vz; C (6) (I) := P.Ax; C (7) (I) := P.Ay; C (8) (I) := P.Az; C (9) (I) := P.Mass;
                  C (10) (I) := P.Charge; C (11) (I) := P.Radius; C (12) (I) := P.Temp; C (13) (I) := P.Pressure;
                  C (14) (I) := P.Energy; C (15) (I) := P.Density;
               end;
            end loop;
            for R in -Warm .. Reps - 1 loop
               T0 := Now;
               E := K1_Soa (C (3).all, C (4).all, C (5).all, C (9).all);
               T1 := Now;
               if R >= 0 then
                  Result ("k1", V, "energy", R, T1 - T0, Fix (E, 6));
               end if;
            end loop;
         end;
         return;
      end if;
      if V = "footprint" then
         declare
            M2 : constant Long_Long_Integer := Rss_Now;  --  P2 : après la lecture
         begin
            Put_Line ("META;mem;rss;" & Img (M1) & ";" & Img (M2));
            Put_Line ("META;rss;" & Img (M1) & ";" & Img (M2));
         end;
         Result ("k1", V, "energy", 0, 0.0, Fix (K1_Natural (Ps.all), 6));
         return;
      end if;
      if V = "natural_shuffled" then
         declare
            Perm : constant U32_Acc := Load_U32 ("k1_perm.u32");
            S    : constant Particle_Acc := new Particle_Arr (0 .. N1 - 1);
         begin
            for J in S'Range loop
               S (J) := Ps (Natural (Perm (J)));
            end loop;
            Ps := S;
         end;
      end if;
      for R in -Warm .. Reps - 1 loop
         T0 := Now;
         E := (if V = "aos" then K1_Aos (Ps.all) else K1_Natural (Ps.all));
         T1 := Now;
         if R >= 0 then
            Result ("k1", V, "energy", R, T1 - T0, Fix (E, 6));
         end if;
      end loop;
   end Run_K1;

   ---------------------------------------------------------------- K2
   function K2_Chase (A : U32_Arr; H : Integer) return Unsigned_32 with No_Inline is  --  No_Inline : correction du 30/10 (docs/ADA.md)
      pragma Suppress (All_Checks);
      I : Unsigned_32 := 0;
   begin
      for K in 1 .. H loop
         I := A (Natural (I));
      end loop;
      return I;
   end K2_Chase;
   procedure Run_K2 (V : String; Reps : Integer; P : String) is
      A : constant U32_Acc := Load_U32 ("k2_chase_" & P & ".u32");
      T0, T1 : Long_Float;
      I : Unsigned_32;
   begin
      for R in -Warm .. Reps - 1 loop
         T0 := Now;
         I := K2_Chase (A.all, 4_200_000);
         T1 := Now;
         if R >= 0 then
            Result ("k2", V, P, R, T1 - T0, Imgu (Unsigned_64 (I)));
         end if;
      end loop;
   end Run_K2;

   ---------------------------------------------------------------- K3
   procedure Run_K3 (V : String; Reps : Integer) is
      pragma Suppress (All_Checks);
      ITER3 : constant := 2 ** 25;
      type ACounter is new Integer_64 with Atomic;
      type VCounter is new Integer_64 with Volatile;
      package AI is new System.Atomic_Operations.Integer_Arithmetic (ACounter);
      --  compteurs espacés : un enregistrement de 128 octets aligné sur 128 (clauses de représentation)
      type A_Cell is record
         C : aliased ACounter;
      end record with Alignment => 128, Size => 1024;
      type V_Cell is record
         C : aliased VCounter;
      end record with Alignment => 128, Size => 1024;
      type A_Packed is array (0 .. 3) of aliased ACounter with Alignment => 64;
      type V_Packed is array (0 .. 3) of aliased VCounter with Alignment => 64;
      AP : A_Packed := [others => 0];
      VP : V_Packed := [others => 0];
      AD : array (0 .. 3) of A_Cell;
      VD : array (0 .. 3) of V_Cell;
      type A_Ptr is access all ACounter;
      type V_Ptr is access all VCounter;
      Rmw    : constant Boolean := V (V'First .. V'First + 2) = "rmw";
      Padded : constant Boolean := Index (V, "padded") > 0;
      T0, T1 : Long_Float;
      S      : Integer_64;

      task type Worker is
         entry Start (Id : Natural);
      end Worker;
      task body Worker is
         My : Natural;
      begin
         accept Start (Id : Natural) do
            My := Id;
         end Start;
         if Rmw then
            declare
               P : constant A_Ptr := (if Padded then AD (My).C'Access else AP (My)'Access);
            begin
               for I in 1 .. ITER3 loop
                  AI.Atomic_Add (P.all, 1);
               end loop;
            end;
         else
            declare
               P : constant V_Ptr := (if Padded then VD (My).C'Access else VP (My)'Access);
            begin
               for I in 1 .. ITER3 loop
                  P.all := P.all + 1;
               end loop;
            end;
         end if;
      end Worker;
   begin
      Put_Line ("META;k3_mechanism;" &
                (if Rmw then "System.Atomic_Operations.Integer_Arithmetic.Atomic_Add (lock add)"
                 else "objet Volatile (mov) ; un objet Atomic donnerait un store séquentiellement cohérent (xchg)"));
      for R in -Warm .. Reps - 1 loop
         for T in 0 .. 3 loop
            AP (T) := 0; VP (T) := 0; AD (T).C := 0; VD (T).C := 0;
         end loop;
         T0 := Now;
         declare
            W : array (0 .. 3) of Worker;
         begin
            for T in W'Range loop
               W (T).Start (T);
            end loop;
         end;  --  attend la fin des 4 tâches (join)
         T1 := Now;
         S := 0;
         for T in 0 .. 3 loop
            S := S + (if Rmw then (if Padded then Integer_64 (AD (T).C) else Integer_64 (AP (T)))
                      else (if Padded then Integer_64 (VD (T).C) else Integer_64 (VP (T))));
         end loop;
         if R >= 0 then
            Result ("k3", V, "4x2^25", R, T1 - T0, Img (S));
         end if;
      end loop;
   end Run_K3;


   ---------------------------------------------------------------- piste ouverte (v4, point 6 : docs/V4_OPEN.md, 5)
   --  op_cachelines (K3) : la forme d'accès sw_padded, les compteurs Volatile dans le type générique bourré et aligné
   --  de cachelines 0.1.0 (Cachelines.Padded, Destructive_Interference_Size = 128 sur x86-64) au lieu de
   --  l'enregistrement à clauses de représentation ; écrivain unique, P.all := P.all + 1.
   procedure Run_K3_Op (V : String; Reps : Integer) is
      pragma Suppress (All_Checks);
      ITER3 : constant := 2 ** 25;
      type VCounter is new Integer_64 with Volatile;
      package PV is new Cachelines.Padded (VCounter);
      VD : array (0 .. 3) of aliased PV.Padded;
      T0, T1 : Long_Float;
      S      : Integer_64;

      task type Worker is
         entry Start (Id : Natural);
      end Worker;
      task body Worker is
         My : Natural;
      begin
         accept Start (Id : Natural) do
            My := Id;
         end Start;
         for I in 1 .. ITER3 loop
            VD (My).Value := VD (My).Value + 1;
         end loop;
      end Worker;
   begin
      Put_Line ("META;k3_mechanism;objet Volatile (mov) dans Cachelines.Padded (taille" &
                Positive'Image (PV.Padded_Size_In_Storage_Elements) & " octets)");
      for R in -Warm .. Reps - 1 loop
         for T in 0 .. 3 loop
            VD (T).Value := 0;
         end loop;
         T0 := Now;
         declare
            W : array (0 .. 3) of Worker;
         begin
            for T in W'Range loop
               W (T).Start (T);
            end loop;
         end;
         T1 := Now;
         S := 0;
         for T in 0 .. 3 loop
            S := S + Integer_64 (VD (T).Value);
         end loop;
         if R >= 0 then
            Result ("k3", V, "4x2^25", R, T1 - T0, Img (S));
         end if;
      end loop;
   end Run_K3_Op;

   ---------------------------------------------------------------- K4
   function K4_Natural (B : U8_Arr) return Unsigned_64 is
      S : Unsigned_64 := 0;
   begin
      for X of B loop
         if X >= 128 then
            S := S + Unsigned_64 (X);
         end if;
      end loop;
      return S;
   end K4_Natural;
   function K4_Branchless (B : U8_Arr) return Unsigned_64 is
      S : Unsigned_64 := 0;
   begin
      for X of B loop
         S := S + Unsigned_64 (X) * Unsigned_64 (Shift_Right (X, 7));
      end loop;
      return S;
   end K4_Branchless;
   --  v4, point 3 (docs/V4_EQUAL.md, R3) : variante tuned, SIMD explicite (types vectoriels GCC et builtins importés,
   --  comme K5 tuned) : masque v >= 128 par le bit de poids fort (vpmovb2m), octets hors masque mis à zéro
   --  (vmovdqu8 masqué), vpsadbw en huit sommes de 64 bits.
   type V64I8 is array (0 .. 63) of Integer_8 with Alignment => 64;
   pragma Machine_Attribute (V64I8, "vector_type");
   type V8I64 is array (0 .. 7) of Integer_64 with Alignment => 64;
   pragma Machine_Attribute (V8I64, "vector_type");
   function B2Mask (A : V64I8) return Unsigned_64;
   pragma Import (Intrinsic, B2Mask, "__builtin_ia32_cvtb2mask512");
   function Mov_Masked (A, Src : V64I8; K : Unsigned_64) return V64I8;
   pragma Import (Intrinsic, Mov_Masked, "__builtin_ia32_movdquqi512_mask");
   function Sad (A, B : V64I8) return V8I64;
   pragma Import (Intrinsic, Sad, "__builtin_ia32_psadbw512");
   function Add_Q (A, B, Src : V8I64; K : Unsigned_8) return V8I64;
   pragma Import (Intrinsic, Add_Q, "__builtin_ia32_paddq512_mask");
   function K4_Tuned (B : U8_Arr) return Unsigned_64 is
      --  les builtins prennent des octets signés (__v64qi) : les mêmes octets, vus comme Integer_8 ; vpmovb2m ne lit
      --  que le bit de poids fort, et vpsadbw traite les octets comme non signés
      Zero_V : constant V64I8 := [others => 0];
      Acc    : V8I64 := [others => 0];
      S      : Unsigned_64 := 0;
      I      : Natural := B'First;
   begin
      while I + 63 <= B'Last loop
         declare
            X : V64I8 with Import, Address => B (I)'Address;
         begin
            Acc := Add_Q (Acc, Sad (Mov_Masked (X, Zero_V, B2Mask (X)), Zero_V), Acc, 16#FF#);
         end;
         I := I + 64;
      end loop;
      for K in 0 .. 7 loop
         S := S + Unsigned_64 (Acc (K));
      end loop;
      while I <= B'Last loop
         if B (I) >= 128 then
            S := S + Unsigned_64 (B (I));
         end if;
         I := I + 1;
      end loop;
      return S;
   end K4_Tuned;
   --  v4, point 4 (docs/V4_CONVERGE.md, 3.3, K4 swar) : octets traités par mots de 64 bits. Le bit de poids fort de
   --  chaque octet, ramené au bit 0 de l'octet et multiplié par 0xFF, donne un masque d'octet qui garde les octets
   --  >= 128 ; les octets gardés sont sommés par paires dans quatre voies de 16 bits. Exactitude pour toute donnée :
   --  une voie reçoit au plus 2 × 255 = 510 par mot, donc au plus 128 × 510 = 65 280 < 2^16 en 128 mots ; les voies
   --  sont vidées dans la somme de 64 bits toutes les 128 mots (et à la fin). Aucun branchement sur les données (le
   --  reste, < 8 octets, par produit). Le mot est lu par superposition à l'adresse de l'octet (tableau aligné sur 64
   --  octets, indices multiples de 8).
   function K4_Swar (B : U8_Arr) return Unsigned_64 with No_Inline is
      pragma Suppress (All_Checks);
      Ones : constant Unsigned_64 := 16#0101_0101_0101_0101#;
      Lo   : constant Unsigned_64 := 16#00FF_00FF_00FF_00FF#;
      Last : constant Natural := B'Last + 1;  --  borne exclue
      S    : Unsigned_64 := 0;
      I    : Natural := B'First;
      E    : Natural;
      Acc, Y : Unsigned_64;
   begin
      while I + 8 <= Last loop
         E := (if I + 128 * 8 <= Last then I + 128 * 8 else Last - (Last - I) mod 8);
         Acc := 0;
         while I < E loop
            declare
               W : Unsigned_64 with Import, Address => B (I)'Address;
            begin
               Y := W and ((Shift_Right (W, 7) and Ones) * 16#FF#);
            end;
            Acc := Acc + (Y and Lo) + (Shift_Right (Y, 8) and Lo);
            I := I + 8;
         end loop;
         Acc := (Acc and 16#0000_FFFF_0000_FFFF#) + (Shift_Right (Acc, 16) and 16#0000_FFFF_0000_FFFF#);
         S := S + (Acc and 16#FFFF_FFFF#) + Shift_Right (Acc, 32);
      end loop;
      while I <= B'Last loop
         S := S + Unsigned_64 (B (I)) * Unsigned_64 (Shift_Right (B (I), 7));
         I := I + 1;
      end loop;
      return S;
   end K4_Swar;
   procedure Run_K4 (V : String; Reps : Integer) is
      B : constant U8_Acc := Load_U8 ("k4_bytes.u8");
      T0, T1 : Long_Float;
      S : Unsigned_64;
   begin
      if V = "natural_sorted" then  --  tri par comptage, hors chrono
         declare
            Cnt : array (Unsigned_8) of Natural := [others => 0];
            K   : Natural := 0;
         begin
            for X of B.all loop
               Cnt (X) := Cnt (X) + 1;
            end loop;
            for X in Cnt'Range loop
               B (K .. K + Cnt (X) - 1) := [others => X];
               K := K + Cnt (X);
            end loop;
         end;
      end if;
      for R in -Warm .. Reps - 1 loop
         T0 := Now;
         S := (if V = "tuned" then K4_Tuned (B.all) elsif V = "swar" then K4_Swar (B.all)
               elsif V = "branchless_unsorted" then K4_Branchless (B.all) else K4_Natural (B.all));
         T1 := Now;
         if R >= 0 then
            Result ("k4", V, "16M", R, T1 - T0, Imgu (S));
         end if;
      end loop;
   end Run_K4;

   ---------------------------------------------------------------- K5
   function K5_Natural (A, B : F32_Arr) return Float is
      S : Float := 0.0;
   begin
      for I in A'Range loop
         S := S + A (I) * B (I);
      end loop;
      return S;
   end K5_Natural;
   --  AVX-512 explicite : type vectoriel GCC + FMA importé, 4 accumulateurs
   function K5_Tuned (A, B : F32_Arr) return Float with No_Inline is  --  No_Inline : correction du 30/10 (docs/ADA.md)
      pragma Suppress (All_Checks);
      S0, S1, S2, S3 : M512 := [others => 0.0];
      I : Natural := A'First;
      function V (Addr : System.Address) return M512 is
         X : M512 with Import, Address => Addr;
      begin
         return X;
      end V;
   begin
      while I < A'First + A'Length loop
         S0 := Fmadd (V (A (I)'Address), V (B (I)'Address), S0, 16#FFFF#, 4);
         S1 := Fmadd (V (A (I + 16)'Address), V (B (I + 16)'Address), S1, 16#FFFF#, 4);
         S2 := Fmadd (V (A (I + 32)'Address), V (B (I + 32)'Address), S2, 16#FFFF#, 4);
         S3 := Fmadd (V (A (I + 48)'Address), V (B (I + 48)'Address), S3, 16#FFFF#, 4);
         I := I + 64;
      end loop;
      S0 := Vadd (Vadd (S0, S1, S0, 16#FFFF#, 4), Vadd (S2, S3, S2, 16#FFFF#, 4), S0, 16#FFFF#, 4);
      declare
         T : array (0 .. 7) of Float;
      begin
         for K in 0 .. 7 loop
            T (K) := S0 (K) + S0 (K + 8);
         end loop;
         return ((T (0) + T (4)) + (T (1) + T (5))) + ((T (2) + T (6)) + (T (3) + T (7)));
      end;
   end K5_Tuned;
   procedure Run_K5 (V : String; Reps : Integer) is
      A : constant F32_Acc := Load_F32 ("k5_a.f32");
      B : constant F32_Acc := Load_F32 ("k5_b.f32");
      T0, T1 : Long_Float;
      D : Float := 0.0;
   begin
      for R in -Warm .. Reps - 1 loop
         T0 := Now;
         for It in 1 .. $MS_INNER5 loop
            A (0) := A (0) + Zero;  --  écriture opaque : empêche de sortir le calcul de la boucle
            D := (if V = "tuned" then K5_Tuned (A.all, B.all) else K5_Natural (A.all, B.all));
            Sink := D;
         end loop;
         T1 := Now;
         if R >= 0 then
            Result ("k5", V, "2048x65536", R, T1 - T0, Fix (Long_Float (D), 4));
         end if;
      end loop;
   end Run_K5;

   ---------------------------------------------------------------- K6
   N6 : constant := $MS_N6;
   type Cols6 is record
      Sd, Pr : I32_Acc;
      Q, D, T, Rf, Ls : U8_Acc;
   end record;
   type Q1_Acc is array (0 .. 5, 0 .. 4) of Integer_64;

   function Q6_Natural (C : Cols6; Lo, Hi : Natural) return Integer_64 is
      S : Integer_64 := 0;
   begin
      for I in Lo .. Hi loop
         if C.Sd (I) >= 8766 and then C.Sd (I) < 9131 and then C.D (I) >= 5 and then C.D (I) <= 7 and then C.Q (I) < 24 then
            S := S + Integer_64 (C.Pr (I)) * Integer_64 (C.D (I));
         end if;
      end loop;
      return S;
   end Q6_Natural;
   function Q6_Tuned (Sd, Pr : I32_Arr; D, Q : U8_Arr; Lo, Hi : Natural) return Integer_64 with No_Inline is  --  No_Inline : correction du 30/10 (docs/ADA.md)
      pragma Suppress (All_Checks);
      S : Integer_64 := 0;
   begin
      for I in Lo .. Hi loop
         pragma Loop_Optimize (Vector);
         S := S + Integer_64 (Pr (I) * Integer_32 (D (I)) *
                    (Boolean'Pos (Sd (I) in 8766 .. 9130) * Boolean'Pos (D (I) in 5 .. 7) * Boolean'Pos (Q (I) < 24)));
      end loop;
      return S;
   end Q6_Tuned;
   procedure Q1_Natural (C : Cols6; Lo, Hi : Natural; Acc : in out Q1_Acc) is
      G : Natural;
      P, Dp : Integer_64;
   begin
      for I in Lo .. Hi loop
         if C.Sd (I) <= 10471 then
            G := Natural (C.Rf (I)) * 2 + Natural (C.Ls (I));
            P := Integer_64 (C.Pr (I));
            Dp := P * (100 - Integer_64 (C.D (I)));
            Acc (G, 0) := Acc (G, 0) + 1;
            Acc (G, 1) := Acc (G, 1) + Integer_64 (C.Q (I));
            Acc (G, 2) := Acc (G, 2) + P;
            Acc (G, 3) := Acc (G, 3) + Dp;
            Acc (G, 4) := Acc (G, 4) + Dp * (100 + Integer_64 (C.T (I)));
         end if;
      end loop;
   end Q1_Natural;
   --  Q1 par blocs de 1024 lignes : conversions et produits une fois par bloc (tableaux larges),
   --  puis une passe vectorisable (masquée) par groupe.
   procedure Q1_Tuned (C : Cols6; Lo, Hi : Natural; Acc : in out Q1_Acc) with No_Inline is  --  No_Inline : correction du 30/10 (docs/ADA.md)
      pragma Suppress (All_Checks);
      B : constant := 1024;
      Gg, Qv, Pv : I32_Arr (0 .. B - 1);
      Dv, Cv : array (0 .. B - 1) of Integer_64;
      I0 : Natural := Lo;
      N  : Natural;
   begin
      while I0 <= Hi loop
         N := Natural'Min (B, Hi - I0 + 1);
         for K in 0 .. N - 1 loop
            declare
               I : constant Natural := I0 + K;
            begin
               Gg (K) := (if C.Sd (I) <= 10471 then Integer_32 (C.Rf (I)) * 2 + Integer_32 (C.Ls (I)) else -1);
               Qv (K) := Integer_32 (C.Q (I));
               Pv (K) := C.Pr (I);
               Dv (K) := Integer_64 (C.Pr (I) * (100 - Integer_32 (C.D (I))));
               Cv (K) := Dv (K) * Integer_64 (100 + Integer_32 (C.T (I)));
            end;
         end loop;
         for Grp in 0 .. 5 loop
            declare
               C1, C2, C3 : Integer_32 := 0;
               C4, C5 : Integer_64 := 0;
               Gi : constant Integer_32 := Integer_32 (Grp);
            begin
               for K in 0 .. N - 1 loop
                  pragma Loop_Optimize (Vector);
                  if Gg (K) = Gi then
                     C1 := C1 + 1; C2 := C2 + Qv (K); C3 := C3 + Pv (K); C4 := C4 + Dv (K); C5 := C5 + Cv (K);
                  end if;
               end loop;
               Acc (Grp, 0) := Acc (Grp, 0) + Integer_64 (C1);
               Acc (Grp, 1) := Acc (Grp, 1) + Integer_64 (C2);
               Acc (Grp, 2) := Acc (Grp, 2) + Integer_64 (C3);
               Acc (Grp, 3) := Acc (Grp, 3) + C4;
               Acc (Grp, 4) := Acc (Grp, 4) + C5;
            end;
         end loop;
         I0 := I0 + N;
      end loop;
   end Q1_Tuned;
   --  v4, point 4 (docs/V4_CONVERGE.md, 3.3) : types vectoriels GCC et builtins AVX-512 importés, comme K4 et K5 tuned.
   --  Les blocs de 16 lignes commencent à un indice multiple de 16 (0 ou un quart de N6) : les colonnes, alignées sur 64
   --  octets, sont lues par superposition alignée.
   type V16SI is array (0 .. 15) of Integer_32 with Alignment => 64;
   pragma Machine_Attribute (V16SI, "vector_type");
   type V16QI is array (0 .. 15) of Integer_8 with Alignment => 16;
   pragma Machine_Attribute (V16QI, "vector_type");
   function ZxBD (A : V16QI; Src : V16SI; K : Unsigned_16) return V16SI;
   pragma Import (Intrinsic, ZxBD, "__builtin_ia32_pmovzxbd512_mask");
   function CmpD (A, B : V16SI; P : Integer; K : Unsigned_16) return Unsigned_16;  --  P : 0 =, 1 <, 2 <=, 5 >=
   pragma Import (Intrinsic, CmpD, "__builtin_ia32_cmpd512_mask");
   function MulLoD (A, B, Src : V16SI; K : Unsigned_16) return V16SI;
   pragma Import (Intrinsic, MulLoD, "__builtin_ia32_pmulld512_mask");
   function PaddD (A, B, Src : V16SI; K : Unsigned_16) return V16SI;
   pragma Import (Intrinsic, PaddD, "__builtin_ia32_paddd512_mask");
   function PsubD (A, B, Src : V16SI; K : Unsigned_16) return V16SI;
   pragma Import (Intrinsic, PsubD, "__builtin_ia32_psubd512_mask");
   function SllD (A : V16SI; N : Integer; Src : V16SI; K : Unsigned_16) return V16SI;
   pragma Import (Intrinsic, SllD, "__builtin_ia32_pslldi512_mask");
   function SllQ (A : V8I64; N : Integer; Src : V8I64; K : Unsigned_8) return V8I64;
   pragma Import (Intrinsic, SllQ, "__builtin_ia32_psllqi512_mask");
   function SrlQ (A : V8I64; N : Integer; Src : V8I64; K : Unsigned_8) return V8I64;
   pragma Import (Intrinsic, SrlQ, "__builtin_ia32_psrlqi512_mask");
   function SraQ (A : V8I64; N : Integer; Src : V8I64; K : Unsigned_8) return V8I64;
   pragma Import (Intrinsic, SraQ, "__builtin_ia32_psraqi512_mask");
   function MulDQ (A, B : V16SI; Src : V8I64; K : Unsigned_8) return V8I64;
   pragma Import (Intrinsic, MulDQ, "__builtin_ia32_pmuldq512_mask");
   function Pext (A, M : Unsigned_32) return Unsigned_32;
   pragma Import (Intrinsic, Pext, "__builtin_ia32_pext_si");
   function Popcount (X : Unsigned_32) return Integer;
   pragma Import (Intrinsic, Popcount, "__builtin_popcount");
   function To_Q is new Ada.Unchecked_Conversion (V16SI, V8I64);
   function To_D is new Ada.Unchecked_Conversion (V8I64, V16SI);
   function Splat (X : Integer_32) return V16SI is ([others => X]);
   Z16 : constant V16SI := [others => 0];
   Z8  : constant V8I64 := [others => 0];

   --  v4, point 4 (docs/V4_CONVERGE.md, 3.3, K6 Q6 tuned_v ; forme de la frontière, Zig) : blocs de 16 lignes en
   --  vecteurs : colonnes élargies en i32, prédicat par comparaisons, produit prix × remise en i32 sélectionné par le
   --  masque, accumulation en i64 (voies paires et impaires). Exactitude pour toute donnée (docs/SPEC.md, K6) : prix
   --  <= 50 000 et remise <= 10, donc produit <= 500 000 < 2^31 ; une voie de 64 bits reçoit au plus N6 / 16
   --  produits. La variante tuned publiée est scalaire, vectorisée par GCC.
   function Q6_Tuned_V (C : Cols6; Lo, Hi : Natural) return Integer_64 with No_Inline is
      pragma Suppress (All_Checks);
      D0 : constant V16SI := Splat (8766);
      D1 : constant V16SI := Splat (9131);
      R0 : constant V16SI := Splat (5);
      R1 : constant V16SI := Splat (7);
      Q0 : constant V16SI := Splat (24);
      A0, A1 : V8I64 := Z8;
      I : Natural := Lo;
      S : Integer_64 := 0;
   begin
      while I + 15 <= Hi loop
         declare
            Sd : V16SI with Import, Address => C.Sd (I)'Address;
            Pr : V16SI with Import, Address => C.Pr (I)'Address;
            Db : V16QI with Import, Address => C.D (I)'Address;
            Qb : V16QI with Import, Address => C.Q (I)'Address;
            D  : constant V16SI := ZxBD (Db, Z16, 16#FFFF#);
            Q  : constant V16SI := ZxBD (Qb, Z16, 16#FFFF#);
            M  : constant Unsigned_16 := CmpD (Sd, D0, 5, 16#FFFF#) and CmpD (Sd, D1, 1, 16#FFFF#)
                                         and CmpD (D, R0, 5, 16#FFFF#) and CmpD (D, R1, 2, 16#FFFF#)
                                         and CmpD (Q, Q0, 1, 16#FFFF#);
            P  : constant V8I64 := To_Q (MulLoD (Pr, D, Z16, M));  --  zéro hors du masque
         begin
            A0 := Add_Q (A0, SraQ (SllQ (P, 32, Z8, 16#FF#), 32, Z8, 16#FF#), A0, 16#FF#);  --  lignes paires
            A1 := Add_Q (A1, SraQ (P, 32, Z8, 16#FF#), A1, 16#FF#);                          --  lignes impaires
         end;
         I := I + 16;
      end loop;
      for K in 0 .. 7 loop
         S := S + A0 (K) + A1 (K);
      end loop;
      return S + Q6_Natural (C, I, Hi);  --  reste (< 16 lignes)
   end Q6_Tuned_V;

   --  v4, point 4 (docs/V4_CONVERGE.md, 3.3, K6 Q1 tuned_v) : l'algorithme de la référence C, 16 lignes par tour,
   --  masque de passage, groupe 2 × rf + ls, par groupe un masque, compte par population du masque, additions masquées
   --  de la quantité, du prix et de prix × (100 − remise) en voies de 32 bits vidées toutes les 4 096 lignes (au plus
   --  256 lignes par voie : 256 × 5 000 000 < 2^31), charge en 64 bits (lignes paires et impaires). La variante tuned
   --  publiée agrège par blocs et par groupe en scalaire.
   procedure Q1_Tuned_V (C : Cols6; Lo, Hi : Natural; Acc : in out Q1_Acc) with No_Inline is
      pragma Suppress (All_Checks);
      Lim  : constant V16SI := Splat (10471);
      C100 : constant V16SI := Splat (100);
      type V16_6 is array (0 .. 5) of V16SI;
      type V8_6 is array (0 .. 5) of V8I64;
      Aq, Ap, Adp : V16_6;
      Ace, Aco : V8_6;
      Cnt : array (0 .. 5) of Integer_64;
      Last : constant Natural := Hi + 1;  --  borne exclue
      I : Natural := Lo;
      E : Natural;
      M : Unsigned_16;
   begin
      while I + 16 <= Last loop
         Aq := [others => Z16]; Ap := [others => Z16]; Adp := [others => Z16];
         Ace := [others => Z8]; Aco := [others => Z8]; Cnt := [others => 0];
         E := (if I + 4096 <= Last then I + 4096 else Last - (Last - I) mod 16);
         while I < E loop
            declare
               Sd  : V16SI with Import, Address => C.Sd (I)'Address;
               Pr  : V16SI with Import, Address => C.Pr (I)'Address;
               Rfb : V16QI with Import, Address => C.Rf (I)'Address;
               Lsb : V16QI with Import, Address => C.Ls (I)'Address;
               Qb  : V16QI with Import, Address => C.Q (I)'Address;
               Db  : V16QI with Import, Address => C.D (I)'Address;
               Tb  : V16QI with Import, Address => C.T (I)'Address;
               Pass : constant Unsigned_16 := CmpD (Sd, Lim, 2, 16#FFFF#);
               Vg  : constant V16SI := PaddD (SllD (ZxBD (Rfb, Z16, 16#FFFF#), 1, Z16, 16#FFFF#),
                                              ZxBD (Lsb, Z16, 16#FFFF#), Z16, 16#FFFF#);
               Vq  : constant V16SI := ZxBD (Qb, Z16, 16#FFFF#);
               Vd  : constant V16SI := ZxBD (Db, Z16, 16#FFFF#);
               Vt  : constant V16SI := PaddD (ZxBD (Tb, Z16, 16#FFFF#), C100, Z16, 16#FFFF#);
               Vdp : constant V16SI := MulLoD (Pr, PsubD (C100, Vd, Z16, 16#FFFF#), Z16, 16#FFFF#);
               Che : constant V8I64 := MulDQ (Vdp, Vt, Z8, 16#FF#);  --  lignes paires
               Cho : constant V8I64 := MulDQ (To_D (SrlQ (To_Q (Vdp), 32, Z8, 16#FF#)),
                                              To_D (SrlQ (To_Q (Vt), 32, Z8, 16#FF#)), Z8, 16#FF#);  --  impaires
            begin
               for G in 0 .. 5 loop
                  pragma Loop_Optimize (Unroll);  --  six groupes déroulés : accumulateurs en registres
                  M := CmpD (Vg, Splat (Integer_32 (G)), 0, Pass);
                  Cnt (G) := Cnt (G) + Integer_64 (Popcount (Unsigned_32 (M)));
                  Aq (G) := PaddD (Aq (G), Vq, Aq (G), M);
                  Ap (G) := PaddD (Ap (G), Pr, Ap (G), M);
                  Adp (G) := PaddD (Adp (G), Vdp, Adp (G), M);
                  Ace (G) := Add_Q (Ace (G), Che, Ace (G), Unsigned_8 (Pext (Unsigned_32 (M), 16#5555#)));
                  Aco (G) := Add_Q (Aco (G), Cho, Aco (G), Unsigned_8 (Pext (Unsigned_32 (M), 16#AAAA#)));
               end loop;
            end;
            I := I + 16;
         end loop;
         for G in 0 .. 5 loop
            Acc (G, 0) := Acc (G, 0) + Cnt (G);
            for K in 0 .. 15 loop
               Acc (G, 1) := Acc (G, 1) + Integer_64 (Aq (G) (K));
               Acc (G, 2) := Acc (G, 2) + Integer_64 (Ap (G) (K));
               Acc (G, 3) := Acc (G, 3) + Integer_64 (Adp (G) (K));
            end loop;
            for K in 0 .. 7 loop
               Acc (G, 4) := Acc (G, 4) + Ace (G) (K) + Aco (G) (K);
            end loop;
         end loop;
      end loop;
      if I <= Hi then
         Q1_Natural (C, I, Hi, Acc);  --  reste (< 16 lignes)
      end if;
   end Q1_Tuned_V;
   procedure Run_K6 (V : String; Reps : Integer; P : String) is
      C : constant Cols6 := (Load_I32 ("k6_shipdate.i32"), Load_I32 ("k6_extendedprice.i32"), Load_U8 ("k6_quantity.u8"),
                             Load_U8 ("k6_discount.u8"), Load_U8 ("k6_tax.u8"), Load_U8 ("k6_returnflag.u8"),
                             Load_U8 ("k6_linestatus.u8"));
      Is_Q1 : constant Boolean := P = "q1";
      T0, T1 : Long_Float;
      S6 : Integer_64;
      Acc : Q1_Acc;
      type Part_Acc is array (0 .. 3) of Q1_Acc;
      Parts : Part_Acc;
      P6 : array (0 .. 3) of Integer_64;
      task type Worker is
         entry Start (Id : Natural);
      end Worker;
      task body Worker is
         T : Natural;
      begin
         accept Start (Id : Natural) do
            T := Id;
         end Start;
         declare
            Lo : constant Natural := N6 / 4 * T;
            Hi : constant Natural := N6 / 4 * (T + 1) - 1;
         begin
            Parts (T) := [others => [others => 0]];
            if Is_Q1 then
               Q1_Tuned (C, Lo, Hi, Parts (T));
            else
               P6 (T) := Q6_Tuned (C.Sd.all, C.Pr.all, C.D.all, C.Q.all, Lo, Hi);
            end if;
         end;
      end Worker;
      --  v4, point 4 (docs/V4_CONVERGE.md, 3.3, mt_pool, mt_pool_v) : réserve de trois tâches (le fil principal fait le
      --  quart 0), créées une fois avant l'échauffement ; à chaque appel, le rendez-vous Go les réveille et le
      --  rendez-vous Done attend leur fin ; entre deux appels, elles attendent, bloquées, à Go (les rendez-vous
      --  ordonnent aussi les accès mémoire, RM 9.10). mt_pool exécute dans chaque quart la forme de mt (Q6_Tuned,
      --  Q1_Tuned), mt_pool_v les formes tuned_v.
      Use_V : constant Boolean := V = "mt_pool_v";
      procedure Quarter (T : Natural) is
         Lo : constant Natural := N6 / 4 * T;
         Hi : constant Natural := N6 / 4 * (T + 1) - 1;
      begin
         Parts (T) := [others => [others => 0]];
         if Is_Q1 then
            if Use_V then Q1_Tuned_V (C, Lo, Hi, Parts (T)); else Q1_Tuned (C, Lo, Hi, Parts (T)); end if;
         else
            P6 (T) := (if Use_V then Q6_Tuned_V (C, Lo, Hi) else Q6_Tuned (C.Sd.all, C.Pr.all, C.D.all, C.Q.all, Lo, Hi));
         end if;
      end Quarter;
      task type Pool_Worker is
         entry Start (Id : Natural);
         entry Go;
         entry Done;
      end Pool_Worker;
      task body Pool_Worker is
         T : Natural;
      begin
         accept Start (Id : Natural) do
            T := Id;
         end Start;
         loop
            select
               accept Go;
            or
               terminate;
            end select;
            Quarter (T);
            accept Done;
         end loop;
      end Pool_Worker;
      procedure Fold_Parts is
      begin
         for T in 0 .. 3 loop
            if Is_Q1 then
               for G in 0 .. 5 loop
                  for K in 0 .. 4 loop
                     Acc (G, K) := Acc (G, K) + Parts (T) (G, K);
                  end loop;
               end loop;
            else
               S6 := S6 + P6 (T);
            end if;
         end loop;
      end Fold_Parts;
      procedure Report (R : Integer) is
      begin
         if Is_Q1 then
            for G in 0 .. 5 loop
               for K in 0 .. 4 loop
                  S6 := S6 + Acc (G, K);
               end loop;
            end loop;
         end if;
         if R >= 0 then
            Result ("k6", V, P, R, T1 - T0, Img (S6));
         end if;
      end Report;
   begin
      if V = "mt_pool" or else V = "mt_pool_v" then
         declare
            W : array (1 .. 3) of Pool_Worker;
         begin
            for T in W'Range loop
               W (T).Start (T);
            end loop;
            for R in -Warm .. Reps - 1 loop
               Acc := [others => [others => 0]];
               S6 := 0;
               T0 := Now;
               for T in W'Range loop
                  W (T).Go;
               end loop;
               Quarter (0);
               for T in W'Range loop
                  W (T).Done;
               end loop;
               Fold_Parts;
               T1 := Now;
               Report (R);
            end loop;
         end;  --  les tâches se terminent à la sortie du bloc (alternative terminate)
         return;
      end if;
      for R in -Warm .. Reps - 1 loop
         Acc := [others => [others => 0]];
         S6 := 0;
         T0 := Now;
         if V = "mt" then
            declare
               W : array (0 .. 3) of Worker;
            begin
               for T in W'Range loop
                  W (T).Start (T);
               end loop;
            end;
            for T in 0 .. 3 loop
               if Is_Q1 then
                  for G in 0 .. 5 loop
                     for K in 0 .. 4 loop
                        Acc (G, K) := Acc (G, K) + Parts (T) (G, K);
                     end loop;
                  end loop;
               else
                  S6 := S6 + P6 (T);
               end if;
            end loop;
         elsif V = "tuned" then
            if Is_Q1 then
               Q1_Tuned (C, 0, N6 - 1, Acc);
            else
               S6 := Q6_Tuned (C.Sd.all, C.Pr.all, C.D.all, C.Q.all, 0, N6 - 1);
            end if;
         elsif V = "tuned_v" then
            if Is_Q1 then
               Q1_Tuned_V (C, 0, N6 - 1, Acc);
            else
               S6 := Q6_Tuned_V (C, 0, N6 - 1);
            end if;
         else
            if Is_Q1 then
               Q1_Natural (C, 0, N6 - 1, Acc);
            else
               S6 := Q6_Natural (C, 0, N6 - 1);
            end if;
         end if;
         T1 := Now;
         if Is_Q1 then
            for G in 0 .. 5 loop
               for K in 0 .. 4 loop
                  S6 := S6 + Acc (G, K);
               end loop;
            end loop;
         end if;
         if R >= 0 then
            Result ("k6", V, P, R, T1 - T0, Img (S6));
         end if;
      end loop;
   end Run_K6;

   ---------------------------------------------------------------- K7
   N7 : constant := $MS_N7;
   type Agg is record
      Count : Unsigned_32 := 0;
      Sum   : Unsigned_64 := 0;
   end record;
   function Hash_U32 (K : Unsigned_32) return Ada.Containers.Hash_Type is (Ada.Containers.Hash_Type (K));
   package U32_Maps is new Ada.Containers.Hashed_Maps
     (Key_Type => Unsigned_32, Element_Type => Agg, Hash => Hash_U32, Equivalent_Keys => "=");
   type Slot is record
      Key, Count : Unsigned_32;
      Sum        : Unsigned_64;
   end record with Size => 128;  --  16 octets, 4 par ligne
   type Slot_Arr is array (Natural range <>) of Slot with Alignment => 64;
   type Slot_Acc is access Slot_Arr;
   procedure Free is new Ada.Unchecked_Deallocation (Slot_Arr, Slot_Acc);

   procedure Run_K7 (V : String; Reps : Integer) is
      Keys : constant U32_Acc := Load_U32 ("k7_keys.u32");
      Vals : constant U32_Acc := Load_U32 ("k7_vals.u32");
      T0, T1 : Long_Float;
      Nk, Ws : Unsigned_64;
   begin
      for R in -Warm .. Reps - 1 loop
         Nk := 0;
         Ws := 0;
         if V = "natural" then
            declare
               M : U32_Maps.Map;
               Cur : U32_Maps.Cursor;
               Ins : Boolean;
            begin
               T0 := Now;
               for I in 0 .. N7 - 1 loop
                  M.Insert (Keys (I), (0, 0), Cur, Ins);
                  declare
                     E : Agg renames M.Reference (Cur);
                  begin
                     E.Count := E.Count + 1;
                     E.Sum := E.Sum + Unsigned_64 (Vals (I));
                  end;
               end loop;
               T1 := Now;
               for C in M.Iterate loop
                  Nk := Nk + 1;
                  Ws := Ws + U32_Maps.Element (C).Sum * Unsigned_64 ((U32_Maps.Key (C) and 1023) + 1);
               end loop;
            end;
         else  --  adressage ouvert, sondage linéaire, hachage de Fibonacci, lots préchargés
            declare
               pragma Suppress (All_Checks);
               LOG   : constant := $MS_K7_LOG2 + 1;
               CAP   : constant := 2 ** LOG;
               BATCH : constant := 16;
               Tab   : Slot_Acc;
               H     : array (0 .. BATCH - 1) of Natural;
               S     : Natural;
               K     : Unsigned_32;
            begin
               T0 := Now;
               Tab := new Slot_Arr'(0 .. CAP - 1 => (0, 0, 0));
               for I0 in 0 .. N7 / BATCH - 1 loop
                  for B in 0 .. BATCH - 1 loop
                     H (B) := Natural (Shift_Right (Keys (I0 * BATCH + B) * 16#9E3779B1#, 32 - LOG));
                     Prefetch (Tab (H (B))'Address, 1, 0);
                  end loop;
                  for B in 0 .. BATCH - 1 loop
                     K := Keys (I0 * BATCH + B);
                     S := H (B);
                     while Tab (S).Count /= 0 and then Tab (S).Key /= K loop
                        S := (S + 1) mod CAP;
                     end loop;
                     Tab (S).Key := K;
                     Tab (S).Count := Tab (S).Count + 1;
                     Tab (S).Sum := Tab (S).Sum + Unsigned_64 (Vals (I0 * BATCH + B));
                  end loop;
               end loop;
               T1 := Now;
               for E of Tab.all loop
                  if E.Count /= 0 then
                     Nk := Nk + 1;
                     Ws := Ws + E.Sum * Unsigned_64 ((E.Key and 1023) + 1);
                  end if;
               end loop;
               Free (Tab);
            end;
         end if;
         if R >= 0 then
            Result ("k7", V, "16M/1M", R, T1 - T0, Imgu (Nk) & ":" & Imgu (Ws));
         end if;
      end loop;
   end Run_K7;

   ---------------------------------------------------------------- K8
   type Node;
   type Node_Ptr is access Node;
   type Node is record
      V    : Integer_64;
      L, R : Node_Ptr;
   end record;
   procedure Free is new Ada.Unchecked_Deallocation (Node, Node_Ptr);
   function T_Build (D : Natural; C : in out Integer_64) return Node_Ptr is
      N : constant Node_Ptr := new Node'(C, null, null);
   begin
      C := C + 1;
      if D > 0 then
         N.L := T_Build (D - 1, C);
         N.R := T_Build (D - 1, C);
      end if;
      return N;
   end T_Build;
   function T_Sum (N : Node_Ptr) return Integer_64 is
     (if N = null then 0 else N.V + T_Sum (N.L) + T_Sum (N.R));
   procedure T_Free (N : in out Node_Ptr) is
   begin
      if N /= null then
         T_Free (N.L);
         T_Free (N.R);
         Free (N);
      end if;
   end T_Free;

   --  tuned : nœuds indexés dans des tableaux réutilisés
   type ANode is record
      V    : Integer_64;
      L, R : Integer_32;
   end record;
   Arena : array (0 .. 2 * 2 ** $MS_K8_REQ - 2) of ANode;
   function A_Build (Top : in out Integer_32; D : Natural; C : in out Integer_64) return Integer_32 is
      pragma Suppress (All_Checks);
      I : constant Integer_32 := Top;
      L : Integer_32;
   begin
      Top := Top + 1;
      Arena (Natural (I)).V := C;
      C := C + 1;
      if D > 0 then
         L := A_Build (Top, D - 1, C);
         Arena (Natural (I)).L := L;
         Arena (Natural (I)).R := A_Build (Top, D - 1, C);
      else
         Arena (Natural (I)).L := -1;
         Arena (Natural (I)).R := -1;
      end if;
      return I;
   end A_Build;
   function A_Sum (I : Integer_32) return Integer_64 is
      pragma Suppress (All_Checks);
   begin
      return (if I < 0 then 0 else Arena (Natural (I)).V + A_Sum (Arena (Natural (I)).L) + A_Sum (Arena (Natural (I)).R));
   end A_Sum;

   --  v4, point 4 (docs/V4_CONVERGE.md, 3.3, K8 tuned_it ; forme de bench/c_k8it, remarque sur C) : construction et
   --  somme itératives, piles explicites. La construction descend à gauche en empilant le sous-arbre droit de chaque
   --  nœud interne, puis le reprend à la feuille suivante : même ordre préfixe, mêmes liens et mêmes valeurs que
   --  A_Build. Les piles tiennent par construction : au plus une entrée par niveau à la construction, au plus
   --  profondeur + 1 à la somme.
   pragma Compile_Time_Error ($MS_K8_REQ >= 63, "piles de K8 tuned_it : 64 entrées");
   procedure A_Build_It (Depth : Natural; Q : Integer_64) is
      pragma Suppress (All_Checks);
      type Pend is record
         Parent : Integer_32;
         Depth  : Natural;
      end record;
      Stk : array (0 .. 63) of Pend;
      Sp : Natural := 0;
      Top : Integer_32 := 0;
      Parent : Integer_32 := -1;
      Right : Boolean := False;
      D : Natural := Depth;
      I : Integer_32;
   begin
      loop
         I := Top;
         Top := Top + 1;
         Arena (Natural (I)).V := Q + Integer_64 (I);
         if Parent >= 0 then
            if Right then
               Arena (Natural (Parent)).R := I;
            else
               Arena (Natural (Parent)).L := I;
            end if;
         end if;
         if D > 0 then
            Stk (Sp) := (I, D - 1);
            Sp := Sp + 1;
            Parent := I;
            Right := False;
            D := D - 1;
         else
            Arena (Natural (I)).L := -1;
            Arena (Natural (I)).R := -1;
            exit when Sp = 0;
            Sp := Sp - 1;
            Parent := Stk (Sp).Parent;
            D := Stk (Sp).Depth;
            Right := True;
         end if;
      end loop;
   end A_Build_It;
   function A_Sum_It (Root : Integer_32) return Integer_64 is
      pragma Suppress (All_Checks);
      Stk : array (0 .. 63) of Integer_32;
      Sp : Natural := 1;
      S : Integer_64 := 0;
      I : Integer_32;
   begin
      Stk (0) := Root;
      while Sp > 0 loop
         Sp := Sp - 1;
         I := Stk (Sp);
         S := S + Arena (Natural (I)).V;
         if Arena (Natural (I)).L >= 0 then
            Stk (Sp) := Arena (Natural (I)).R;
            Stk (Sp + 1) := Arena (Natural (I)).L;
            Sp := Sp + 2;
         end if;
      end loop;
      return S;
   end A_Sum_It;

   --  tuned_alloc : pool de stockage utilisateur (System.Storage_Pools), allocation par incrément
   type Bump_Pool is new Root_Storage_Pool with record
      Buf : Storage_Array (1 .. 64 * 2 ** $MS_K8_REQ);
      Top : Storage_Offset := 0;
   end record;
   overriding procedure Allocate (Pool : in out Bump_Pool; Addr : out Address; Size : Storage_Count;
                                  Alignment : Storage_Count);
   overriding procedure Deallocate (Pool : in out Bump_Pool; Addr : Address; Size : Storage_Count;
                                    Alignment : Storage_Count) is null;
   overriding function Storage_Size (Pool : Bump_Pool) return Storage_Count is (Pool.Buf'Length);
   overriding procedure Allocate (Pool : in out Bump_Pool; Addr : out Address; Size : Storage_Count;
                                  Alignment : Storage_Count) is
      pragma Suppress (All_Checks);
      T : constant Storage_Offset := (Pool.Top + Alignment - 1) / Alignment * Alignment;
   begin
      Addr := Pool.Buf (Pool.Buf'First + T)'Address;
      Pool.Top := T + Size;
   end Allocate;
   Pool : Bump_Pool;
   type PNode;
   type PNode_Ptr is access PNode with Storage_Pool => Pool;
   type PNode is record
      V    : Integer_64;
      L, R : PNode_Ptr;
   end record;
   function P_Build (D : Natural; C : in out Integer_64) return PNode_Ptr is
      pragma Suppress (All_Checks);
      N : constant PNode_Ptr := new PNode'(C, null, null);
   begin
      C := C + 1;
      if D > 0 then
         N.L := P_Build (D - 1, C);
         N.R := P_Build (D - 1, C);
      end if;
      return N;
   end P_Build;
   function P_Sum (N : PNode_Ptr) return Integer_64 is
     (if N = null then 0 else N.V + P_Sum (N.L) + P_Sum (N.R));

   procedure Run_K8 (V : String; Reps : Integer) is
      Q : constant := 16_384;
      type Lat_Arr is array (0 .. Q - 1) of Integer_64;
      Lat : Lat_Arr;
      Cnt : Integer_64 := 0;
      Keep : Node_Ptr := T_Build ($MS_K8_LONG, Cnt);
      LSum : constant Integer_64 := T_Sum (Keep);
      Total, C, S, A : Integer_64;
      T0, T1 : Long_Float;
      procedure Sort (X : in out Lat_Arr) is  --  tri par tas, hors chrono
         procedure Sift (Start, Last : Integer) is
            Rt : Integer := Start;
            Ch : Integer;
            Y  : Integer_64;
         begin
            while 2 * Rt + 1 <= Last loop
               Ch := 2 * Rt + 1;
               if Ch < Last and then X (Ch + 1) > X (Ch) then
                  Ch := Ch + 1;
               end if;
               exit when X (Rt) >= X (Ch);
               Y := X (Rt); X (Rt) := X (Ch); X (Ch) := Y;
               Rt := Ch;
            end loop;
         end Sift;
         Y : Integer_64;
      begin
         for I in reverse 0 .. Q / 2 - 1 loop
            Sift (I, Q - 1);
         end loop;
         for E in reverse 1 .. Q - 1 loop
            Y := X (0); X (0) := X (E); X (E) := Y;
            Sift (0, E - 1);
         end loop;
      end Sort;
   begin
      for R in -Warm .. Reps - 1 loop
         Total := 0;
         T0 := Now;
         for Qq in 0 .. Q - 1 loop
            A := Now_Ns;
            C := Integer_64 (Qq);
            if V = "tuned" then
               declare
                  Top  : Integer_32 := 0;
                  Root : constant Integer_32 := A_Build (Top, $MS_K8_REQ, C);
               begin
                  S := A_Sum (Root);
               end;
            elsif V = "tuned_it" then
               A_Build_It ($MS_K8_REQ, C);
               S := A_Sum_It (0);
            elsif V = "tuned_alloc" then
               Pool.Top := 0;  --  libération en bloc
               S := P_Sum (P_Build ($MS_K8_REQ, C));
            else
               declare
                  Tr : Node_Ptr := T_Build ($MS_K8_REQ, C);
               begin
                  S := T_Sum (Tr);
                  T_Free (Tr);
               end;
            end if;
            Total := Total + S;
            Lat (Qq) := Now_Ns - A;
         end loop;
         T1 := Now;
         if R >= 0 then
            Result ("k8", V, "16384x2047", R, T1 - T0, Img (Total + LSum));
            Sort (Lat);
            Put_Line ("LAT;" & V & ";" & Img (Lat (Q / 2)) & ";" & Img (Lat (Q * 9 / 10)) & ";" & Img (Lat (Q * 99 / 100)) &
                      ";" & Img (Lat (Q * 999 / 1000)) & ";" & Img (Lat (Q - 1)));
         end if;
      end loop;
      T_Free (Keep);
   end Run_K8;

   ---------------------------------------------------------------- K9
   M9 : constant := $MS_M9;
   type Grid is array (Natural range <>, Natural range <>) of Long_Float with Alignment => 64;
   type Grid_Acc is access Grid;
   procedure K9_Init (G : out Grid) is
   begin
      for I in G'Range (1) loop
         for J in G'Range (2) loop
            G (I, J) := Long_Float ((I * 31 + J * 17) mod 1024) / 1024.0;
         end loop;
      end loop;
   end K9_Init;
   procedure K9_Natural (A : Grid; B : in out Grid) is
   begin
      for I in 1 .. M9 - 2 loop
         for J in 1 .. M9 - 2 loop
            B (I, J) := 0.25 * (((A (I - 1, J) + A (I + 1, J)) + A (I, J - 1)) + A (I, J + 1));
         end loop;
      end loop;
   end K9_Natural;
   procedure K9_Rows (A : Grid; B : in out Grid; R0, R1 : Natural) with No_Inline is  --  No_Inline : correction du 30/10 (docs/ADA.md)
      pragma Suppress (All_Checks);
   begin
      for I in R0 .. R1 loop
         for J in 1 .. M9 - 2 loop
            pragma Loop_Optimize (Vector);
            B (I, J) := 0.25 * (((A (I - 1, J) + A (I + 1, J)) + A (I, J - 1)) + A (I, J + 1));
         end loop;
      end loop;
   end K9_Rows;
   --  v4, point 4 (docs/V4_CONVERGE.md, 3.3, K9 tuned_v ; forme de la frontière, Swift) : par ligne, vecteurs de 8 f64
   --  (type vectoriel GCC, builtins AVX-512 importés) : haut, bas, gauche et droite chargés en vecteurs, même ordre des
   --  additions que la spécification, résultat écrit en vecteur, reste scalaire. Grilles alignées sur 64 octets
   --  (Grid) ; comme chez Swift, la boucle part de j = 1, chargements et écriture non alignés. La variante tuned
   --  publiée est une boucle scalaire vectorisée par GCC.
   type V8DF is array (0 .. 7) of Long_Float with Alignment => 64;
   pragma Machine_Attribute (V8DF, "vector_type");
   function LoadU (P : System.Address; Src : V8DF; K : Unsigned_8) return V8DF;
   pragma Import (Intrinsic, LoadU, "__builtin_ia32_loadupd512_mask");
   procedure StoreU (P : System.Address; A : V8DF; K : Unsigned_8);
   pragma Import (Intrinsic, StoreU, "__builtin_ia32_storeupd512_mask");
   function AddPD (A, B, Src : V8DF; K : Unsigned_8; R : Integer) return V8DF;
   pragma Import (Intrinsic, AddPD, "__builtin_ia32_addpd512_mask");
   function MulPD (A, B, Src : V8DF; K : Unsigned_8; R : Integer) return V8DF;
   pragma Import (Intrinsic, MulPD, "__builtin_ia32_mulpd512_mask");
   procedure K9_Rows_V (A : Grid; B : in out Grid; R0, R1 : Natural) with No_Inline is
      pragma Suppress (All_Checks);
      Z : constant V8DF := [others => 0.0];
      Q : constant V8DF := [others => 0.25];
      J : Natural;
   begin
      for I in R0 .. R1 loop
         J := 1;
         while J + 8 <= M9 - 1 loop
            StoreU (B (I, J)'Address,
                    MulPD (Q, AddPD (AddPD (AddPD (LoadU (A (I - 1, J)'Address, Z, 16#FF#),
                                                   LoadU (A (I + 1, J)'Address, Z, 16#FF#), Z, 16#FF#, 4),
                                            LoadU (A (I, J - 1)'Address, Z, 16#FF#), Z, 16#FF#, 4),
                                     LoadU (A (I, J + 1)'Address, Z, 16#FF#), Z, 16#FF#, 4), Z, 16#FF#, 4),
                    16#FF#);
            J := J + 8;
         end loop;
         while J <= M9 - 2 loop
            B (I, J) := 0.25 * (((A (I - 1, J) + A (I + 1, J)) + A (I, J - 1)) + A (I, J + 1));
            J := J + 1;
         end loop;
      end loop;
   end K9_Rows_V;
   procedure Run_K9 (V : String; Reps : Integer) is
      A : Grid_Acc := new Grid (0 .. M9 - 1, 0 .. M9 - 1);
      B : Grid_Acc := new Grid (0 .. M9 - 1, 0 .. M9 - 1);
      Tmp : Grid_Acc;
      T0, T1, S : Long_Float;
      task type Worker is
         entry Start (Id : Natural);
      end Worker;
      task body Worker is
         T : Natural;
      begin
         accept Start (Id : Natural) do
            T := Id;
         end Start;
         K9_Rows (A.all, B.all, 1 + (M9 - 2) * T / 4, (M9 - 2) * (T + 1) / 4);
      end Worker;
      --  v4, point 4 (docs/V4_CONVERGE.md, 3.3, mt_pool, mt_pool_v) : réserve de trois tâches (le fil principal fait le
      --  quart 0), créées une fois avant l'échauffement, réveillées par le rendez-vous Go et attendues par Done (voir
      --  Run_K6) ; elles lisent A et B, échangées entre deux appels par le fil principal. mt_pool exécute K9_Rows (la
      --  forme de mt), mt_pool_v K9_Rows_V.
      Use_V : constant Boolean := V = "mt_pool_v";
      procedure Quarter (T : Natural) is
         R0 : constant Natural := 1 + (M9 - 2) * T / 4;
         R1 : constant Natural := (M9 - 2) * (T + 1) / 4;
      begin
         if Use_V then K9_Rows_V (A.all, B.all, R0, R1); else K9_Rows (A.all, B.all, R0, R1); end if;
      end Quarter;
      task type Pool_Worker is
         entry Start (Id : Natural);
         entry Go;
         entry Done;
      end Pool_Worker;
      task body Pool_Worker is
         T : Natural;
      begin
         accept Start (Id : Natural) do
            T := Id;
         end Start;
         loop
            select
               accept Go;
            or
               terminate;
            end select;
            Quarter (T);
            accept Done;
         end loop;
      end Pool_Worker;
   begin
      if V = "mt_pool" or else V = "mt_pool_v" then
         declare
            W : array (1 .. 3) of Pool_Worker;
         begin
            for T in W'Range loop
               W (T).Start (T);
            end loop;
            for R in -Warm .. Reps - 1 loop
               K9_Init (A.all);
               B.all := A.all;
               T0 := Now;
               for It in 1 .. 4 loop
                  for T in W'Range loop
                     W (T).Go;
                  end loop;
                  Quarter (0);
                  for T in W'Range loop
                     W (T).Done;
                  end loop;
                  Tmp := A; A := B; B := Tmp;
               end loop;
               T1 := Now;
               S := 0.0;
               for X of A.all loop
                  S := S + X;
               end loop;
               if R >= 0 then
                  Result ("k9", V, "2048^2x4", R, T1 - T0, Sci (S));
               end if;
            end loop;
         end;  --  les tâches se terminent à la sortie du bloc (alternative terminate)
         return;
      end if;
      for R in -Warm .. Reps - 1 loop
         K9_Init (A.all);
         B.all := A.all;
         T0 := Now;
         for It in 1 .. 4 loop
            if V = "natural" then
               K9_Natural (A.all, B.all);
            elsif V = "tuned" then
               K9_Rows (A.all, B.all, 1, M9 - 2);
            elsif V = "tuned_v" then
               K9_Rows_V (A.all, B.all, 1, M9 - 2);
            else
               declare
                  W : array (0 .. 3) of Worker;
               begin
                  for T in W'Range loop
                     W (T).Start (T);
                  end loop;
               end;
            end if;
            Tmp := A; A := B; B := Tmp;
         end loop;
         T1 := Now;
         S := 0.0;
         for X of A.all loop
            S := S + X;
         end loop;
         if R >= 0 then
            Result ("k9", V, "2048^2x4", R, T1 - T0, Sci (S));
         end if;
      end loop;
   end Run_K9;

   ---------------------------------------------------------------- K10
   M10   : constant := 4_194_304;
   CAP10 : constant := 16_384;
   type U64_Ring is array (0 .. CAP10 - 1) of Unsigned_64;
   --  naturel : tampon borné dans un objet protégé (entrées gardées par des barrières)
   protected type BQueue is
      entry Put (X : Unsigned_64);
      entry Get (X : out Unsigned_64);
   private
      Buf  : U64_Ring;
      Head : Unsigned_64 := 0;
      Tail : Unsigned_64 := 0;
   end BQueue;
   protected body BQueue is
      entry Put (X : Unsigned_64) when Tail - Head < CAP10 is
      begin
         Buf (Natural (Tail mod CAP10)) := X;
         Tail := Tail + 1;
      end Put;
      entry Get (X : out Unsigned_64) when Tail > Head is
      begin
         X := Buf (Natural (Head mod CAP10));
         Head := Head + 1;
      end Get;
   end BQueue;
   type BQueue_Acc is access BQueue;
   --  tuned : anneau SPSC, indices sur des lignes distinctes, ordres acquire/release (primitives GNAT)
   type Idx_Cell is record
      V : aliased Unsigned_64 := 0;
   end record with Alignment => 128, Size => 1024;
   type Spsc is record
      Write_Idx : Idx_Cell;
      Read_Idx  : Idx_Cell;
      Buf       : U64_Ring;
   end record;
   type Spsc_Acc is access Spsc;
   package AP renames System.Atomic_Primitives;

   procedure Run_K10 (V : String; Reps : Integer) is
      Sum : Unsigned_64;
      T0, T1 : Long_Float;
      BQ : BQueue_Acc;
      SQ : Spsc_Acc;
      Tuned : constant Boolean := V = "tuned";
      task type Producer;
      task type Consumer;
      task body Producer is
         pragma Suppress (All_Checks);
         W, Cache : Unsigned_64 := 0;
      begin
         if Tuned then
            for X in Unsigned_64 range 1 .. M10 loop
               while W - Cache = CAP10 loop
                  Cache := Unsigned_64 (AP.Atomic_Load_64 (SQ.Read_Idx.V'Address, AP.Acquire));
                  if W - Cache = CAP10 then
                     Pause;
                  end if;
               end loop;
               SQ.Buf (Natural (W and (CAP10 - 1))) := X;
               W := W + 1;
               AP.Atomic_Store_64 (SQ.Write_Idx.V'Address, AP.uint64 (W), AP.Release);
            end loop;
         else
            for X in Unsigned_64 range 1 .. M10 loop
               BQ.Put (X);
            end loop;
         end if;
      end Producer;
      task body Consumer is
         pragma Suppress (All_Checks);
         Rd, Cache, S, X : Unsigned_64 := 0;
      begin
         if Tuned then
            for K in 1 .. M10 loop
               while Rd = Cache loop
                  Cache := Unsigned_64 (AP.Atomic_Load_64 (SQ.Write_Idx.V'Address, AP.Acquire));
                  if Rd = Cache then
                     Pause;
                  end if;
               end loop;
               S := S + SQ.Buf (Natural (Rd and (CAP10 - 1)));
               Rd := Rd + 1;
               AP.Atomic_Store_64 (SQ.Read_Idx.V'Address, AP.uint64 (Rd), AP.Release);
            end loop;
         else
            for K in 1 .. M10 loop
               BQ.Get (X);
               S := S + X;
            end loop;
         end if;
         Sum := S;
      end Consumer;
   begin
      for R in -Warm .. Reps - 1 loop
         if Tuned then
            SQ := new Spsc;
         else
            BQ := new BQueue;
         end if;
         T0 := Now;
         declare
            C : Consumer;
            P : Producer;
         begin
            null;
         end;  --  attend la fin des deux tâches
         T1 := Now;
         if R >= 0 then
            Result ("k10", V, "2^22", R, T1 - T0, Imgu (Sum));
         end if;
      end loop;
   end Run_K10;

   K : constant String := Argument (1);
   V : constant String := Argument (2);
   Reps : constant Integer := Integer'Value (Argument (3));
   P : constant String := (if Argument_Count >= 4 then Argument (4) else "");
begin
   if K = "k1" then Run_K1 (V, Reps);
   elsif K = "k2" then Run_K2 (V, Reps, P);
   elsif K = "k3" and then V = "op_cachelines" then Run_K3_Op (V, Reps);
   elsif K = "k3" then Run_K3 (V, Reps);
   elsif K = "k4" then Run_K4 (V, Reps);
   elsif K = "k5" then Run_K5 (V, Reps);
   elsif K = "k6" then Run_K6 (V, Reps, P);
   elsif K = "k7" then Run_K7 (V, Reps);
   elsif K = "k8" then Run_K8 (V, Reps);
   elsif K = "k9" then Run_K9 (V, Reps);
   elsif K = "k10" then Run_K10 (V, Reps);
   else
      Put_Line (Standard_Error, "kernel inconnu " & K);
   end if;
end Ms;
