pragma Ada_2022;
with Ada.Text_IO; use Ada.Text_IO;
with Ada.Unchecked_Conversion;
with Interfaces; use Interfaces;
with System.Multiprocessors;
procedure Probe is
   type S is record
      A : Unsigned_8;
      B : Unsigned_32;
      C : Long_Float;
   end record;
   type BF is record
      X : Unsigned_8 range 0 .. 7;
      Y : Unsigned_8 range 0 .. 31;
   end record;
   for BF use record
      X at 0 range 0 .. 2;
      Y at 0 range 3 .. 7;
   end record;
   for BF'Size use 8;
   type Kind is (F, U);
   type UU (K : Kind := F) is record
      case K is
         when F => Fv : Float;
         when U => Uv : Unsigned_32;
      end case;
   end record with Unchecked_Union;
   function To_U32 is new Ada.Unchecked_Conversion (Float, Unsigned_32);
   V : S;
   task T with CPU => 1;
   task body T is begin null; end T;
begin
   Put_Line ("CAP;A2;1;S.C'Position =" & V.C'Position'Image);
   Put_Line ("CAP;A3;1;clause de représentation au bit près : BF'Size =" & BF'Size'Image);
   Put_Line ("CAP;A5;1;Unchecked_Conversion 0x" & To_U32 (1.0)'Image & " ; Unchecked_Union UU'Size =" & UU'Size'Image);
   Put_Line ("CAP;D4;1;aspect CPU => 1 sur une tâche ; CPU disponibles =" & System.Multiprocessors.Number_Of_CPUs'Image);
end Probe;
