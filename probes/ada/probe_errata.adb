--  Sonde Ada 2022 / GNAT 16 ajoutée le 30/10 après la remarque sur Ada (docs/ADA.md) : C1, E5, B4.
--  Les preuves de code machine (un seul vaddps, boucle sans test de recouvrement) et la trace de __gnat_malloc sont
--  dans results/ada_check/probes.txt ; ici, le code compile et s'exécute.
pragma Ada_2022;
with Ada.Text_IO; use Ada.Text_IO;
procedure Probe_Errata is
   --  C1 : type vectoriel GCC déclaré en Ada
   type V8 is array (1 .. 8) of Float with Alignment => 32;
   pragma Machine_Attribute (V8, "vector_type");
   function Add (A, B : V8) return V8 is
      R : V8;
   begin
      for I in R'Range loop
         R (I) := A (I) + B (I);
      end loop;
      return R;
   end Add;
   --  E5 : paramètres d'un type tableau contraint (RM 6.2(12))
   type CVec is array (1 .. 4096) of Float;
   procedure Scale (X : CVec; Y : out CVec; A : Float) is
   begin
      for I in Y'Range loop
         Y (I) := A * X (I) + 1.0;
      end loop;
   end Scale;
   --  B4 : retour non contraint de 4 Mo, sans « new » (pile secondaire)
   type Vec is array (Positive range <>) of Long_Float;
   function Make (N : Positive) return Vec is
      R : Vec (1 .. N);
   begin
      for I in R'Range loop
         R (I) := Long_Float (I);
      end loop;
      return R;
   end Make;
   V : constant V8 := Add ([others => 1.0], [others => 2.0]);
   X : constant access CVec := new CVec'(others => 2.0);
   Y : constant access CVec := new CVec;
begin
   Put_Line ("CAP;C1;0.5;Machine_Attribute vector_type (extension GNAT) : Add = " & V (8)'Image);
   Scale (X.all, Y.all, 3.0);
   Put_Line ("CAP;E5;1;RM 6.2(12) exploitée par GNAT sur paramètres de type contraint : Y (1) = " & Y (1)'Image);
   declare
      W : constant Vec := Make (500_000);
   begin
      Put_Line ("CAP;B4;0.5;retour non contraint de 4 Mo par la pile secondaire (tas au-delà du morceau statique) : " &
                W (W'Last)'Image);
   end;
end Probe_Errata;
