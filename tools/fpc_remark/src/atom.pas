program atom;
{ atomiques de la branche main : AtomicIncrement, AtomicCmpExchange, Volatile (code produit relevé par objdump) }
{$mode objfpc}
var x: Int64; y: LongInt; f: Boolean;
procedure IncX; noinline; begin AtomicIncrement(x); end;
procedure CasY; noinline; begin AtomicCmpExchange(y, 5, 0); end;
function ReadF: Boolean; noinline; begin Result := Volatile(f); end;
begin
  x := 0; y := 0; f := True;
  IncX; CasY;
  WriteLn(x, ' ', y, ' ', ReadF);
end.
