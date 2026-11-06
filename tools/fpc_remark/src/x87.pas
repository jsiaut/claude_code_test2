program x87;
{ code flottant produit selon la cible FPU (-Cf), relevé par objdump }
{$mode objfpc}
var a, b: array of Single; i: Integer;
function Dot(const x, y: array of Single): Single; noinline;
var k: Integer; s: Single;
begin s := 0; for k := 0 to High(x) do s := s + x[k] * y[k]; Result := s; end;
begin
  SetLength(a, 1000); SetLength(b, 1000);
  for i := 0 to 999 do begin a[i] := i; b[i] := 1; end;
  WriteLn(Dot(a, b):0:1);
end.
