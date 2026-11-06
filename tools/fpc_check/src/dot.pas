unit dot;
{$mode objfpc}{$pointermath on}
interface
function dot1(a, b: PSingle; n: SizeInt): Single;
implementation
function dot1(a, b: PSingle; n: SizeInt): Single;
var i: SizeInt; s: Single;
begin
  s := 0;
  for i := 0 to n - 1 do s := s + a[i] * b[i];
  Result := s;
end;
end.
