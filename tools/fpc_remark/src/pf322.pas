program pf322;
{ Prefetch du System en 3.2.2 et 3.2.4-rc2 (code produit relevé par objdump) }
{$mode objfpc}
var a: array[0..1023] of LongInt; i: Integer;
procedure Pf(p: Pointer); begin Prefetch(p^); end;
begin
  for i := 0 to 1023 do a[i] := i;
  Pf(@a[10]);
  WriteLn(a[5]);
end.
