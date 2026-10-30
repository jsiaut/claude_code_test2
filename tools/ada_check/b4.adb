--  Sonde B4 : une fonction qui rend un tableau non contraint passe par la pile secondaire ;
--  au-delà du morceau statique, GNAT alloue des morceaux sur le tas (s-secsta.adb, Allocate_Dynamic).
with Ada.Text_IO; use Ada.Text_IO;
procedure B4 is
   type Vec is array (Positive range <>) of Long_Float;
   function Make (N : Positive) return Vec is
      R : Vec (1 .. N);
   begin
      for I in R'Range loop
         R (I) := Long_Float (I);
      end loop;
      return R;
   end Make;
   S : Long_Float := 0.0;
begin
   for K in 1 .. 3 loop
      declare
         V : constant Vec := Make (500_000);   --  4 Mo, sans « new »
      begin
         S := S + V (V'Last);
      end;
   end loop;
   Put_Line ("somme" & S'Image);
end B4;
