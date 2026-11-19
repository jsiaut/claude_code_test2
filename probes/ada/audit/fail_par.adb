pragma Ada_2022;
with Ada.Text_IO;
procedure Fail_Par is
   A : array (1 .. 1000) of Integer := (others => 0);
begin
   parallel for I in A'Range loop
      A (I) := I;
   end loop;
   Ada.Text_IO.Put_Line (A (1000)'Image);
end Fail_Par;
