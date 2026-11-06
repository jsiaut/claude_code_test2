program hints;
{ unité intrinsics de la branche main (pause) et Prefetch du System (code produit relevé par objdump) }
{$mode objfpc}
uses intrinsics;
var a: array[0..1023] of LongInt; i: Integer;
procedure Spin; noinline; begin fpc_x86_pause; end;
procedure Pf(p: Pointer); noinline; begin Prefetch(p^); end;
begin
  for i := 0 to 1023 do a[i] := i;
  Spin; Pf(@a[10]);
  WriteLn(a[5]);
end.
