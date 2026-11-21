--  Sonde de mode (v4, point 3 : docs/V4_EQUAL.md, 4) : « 1d » : tableau alloué, « 2d » : tableau 2D alloué (K9 naturel).
with Ada.Text_IO;
with Ada.Command_Line; use Ada.Command_Line;
procedure Probe is
   N : constant Natural := Natural'Value (Argument (2));
   type Vec is array (Natural range <>) of Long_Float;
   type Vec_Acc is access Vec;
   type Grid is array (Natural range <>, Natural range <>) of Long_Float;
   type Grid_Acc is access Grid;
begin
   if Argument (1) = "1d" then
      declare
         A : constant Vec_Acc := new Vec'(0 .. N - 1 => 1.0);
      begin
         Ada.Text_IO.Put_Line (Long_Float'Image (A (N)));
      end;
   else
      declare
         G : constant Grid_Acc := new Grid'(0 .. 3 => (0 .. N - 1 => 1.0));
      begin
         Ada.Text_IO.Put_Line (Long_Float'Image (G (1, N)));
      end;
   end if;
end Probe;
