{ Sonde de mode (v4, point 3 : docs/V4_EQUAL.md, 4) : « 1d » : tableau dynamique, « 2d » : tableau 2D statique alloué
  (comme TGrid de K9Natural). }
program probe;
{$mode objfpc}{$H+}
uses SysUtils;
const M = 64;
type TGrid = array[0..3, 0..M - 1] of Double; PGrid = ^TGrid;
var a: array of Double; g: PGrid; n, i, j: Integer;
begin
  n := StrToInt(ParamStr(2));
  if ParamStr(1) = '1d' then begin
    SetLength(a, n);
    for i := 0 to n - 1 do a[i] := 1.0;
    WriteLn(a[n]:0:3);
  end else begin
    New(g);
    for i := 0 to 3 do for j := 0 to M - 1 do g^[i, j] := 1.0;
    WriteLn(g^[1, n]:0:3);
  end;
end.
