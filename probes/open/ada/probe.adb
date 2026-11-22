--  v4, point 6 (docs/V4_OPEN.md, 4) : sondes de la grille ouverte d'Ada
--  (C5 : lwt 1.2.0, boucle parallèle par tranches ; D3 : cachelines 0.1.0, type bourré à la ligne de cache).
pragma Ada_2022;
with Ada.Text_IO; use Ada.Text_IO;
with Interfaces; use Interfaces;
with Interfaces.C;
use type Interfaces.C.long;
with System.Storage_Elements; use System.Storage_Elements;
with LWT.OpenMP;
with LWT.Parallelism; use LWT.Parallelism;
with Cachelines;
with Cachelines.Padded;

procedure Probe is
   function Gettid return Interfaces.C.long;
   pragma Import (C, Gettid, "probe_gettid");

   Num_Chunks : constant := 4;
   Partial : array (1 .. Num_Chunks) of Integer_64 := (others => 0);
   Tid     : array (1 .. Num_Chunks) of Interfaces.C.long := (others => 0);

   procedure Body_Of (Low, High : Longest_Integer; Chunk_Index : Positive) is
      S : Integer_64 := 0;
   begin
      for I in Low .. High loop
         S := S + Integer_64 (I);
      end loop;
      Partial (Chunk_Index) := S;
      Tid (Chunk_Index) := Gettid;
   end Body_Of;

   Total : Integer_64 := 0;
   Distinct : Natural := 0;

   type Counter is mod 2 ** 64;
   package P is new Cachelines.Padded (Counter);
   Counters : array (1 .. 4) of P.Padded;
begin
   declare
      Control : LWT.OpenMP.OMP_Parallel (Num_Threads => 4);
      pragma Unreferenced (Control);
   begin
      Par_Range_Loop (1, 40_000_000, Num_Chunks => Num_Chunks, Loop_Body => Body_Of'Access);
   end;
   for C in Partial'Range loop
      Total := Total + Partial (C);
   end loop;
   for C in Tid'Range loop
      if (for all D in 1 .. C - 1 => Tid (D) /= Tid (C)) then
         Distinct := Distinct + 1;
      end if;
   end loop;
   Put_Line ("RESULT;C5;lwt;Par_Range_Loop (1 .. 40_000_000, Num_Chunks => 4) sous LWT.OpenMP.OMP_Parallel"
     & " (Num_Threads => 4) : somme des sommes partielles par tranche =" & Integer_64'Image (Total)
     & " (attendu 800000020000000) ; tranches exécutées sur" & Natural'Image (Distinct) & " fils distincts (gettid)");
   Counters (1) := P.Create (1);
   Put_Line ("RESULT;D3;cachelines;Cachelines.Destructive_Interference_Size ="
     & Positive'Image (Cachelines.Destructive_Interference_Size)
     & " ; Cachelines.Padded (compteur 64 bits) : taille" & Positive'Image (P.Padded_Size_In_Storage_Elements)
     & " octets, alignement" & Integer'Image (P.Padded'Alignment)
     & " ; écart entre Counters (1) et Counters (2) ="
     & Integer_Address'Image (To_Integer (Counters (2)'Address) - To_Integer (Counters (1)'Address)) & " octets");
end Probe;
