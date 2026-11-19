{ Audit de la grille (docs/V4_PLAN.md 2.1) : compléments exécutés de la sonde de FreePascal (B5, E5). }
program audit;
{$mode objfpc}{$pointermath on}
type PU32 = ^LongWord;
var buf: array[0..7] of LongWord; p: PU32; b: PByte;
procedure axpy(a, c: PSingle; n: Integer);
var i: Integer;
begin
  for i := 0 to n - 1 do a[i] := a[i] + 2 * c[i];
end;
var x: array[0..7] of Single; i: Integer;
begin
  FillChar(buf, SizeOf(buf), 0);
  p := @buf[0]; (p + 3)^ := 42;
  b := PByte(@buf[0]); PU32(b + 16)^ := 7;
  writeln('CAP;B5;1;[exécutée] pointeurs typés avec {$pointermath} : (p + 3)^ := 42 -> buf[3] = ', buf[3], ' ; écriture par décalage d''octets -> buf[4] = ', buf[4]);
  for i := 0 to 7 do x[i] := i;
  axpy(@x[1], @x[0], 7);   { recouvrement autorisé : aucune garantie de non-aliasing }
  writeln('FACT;E5;axpy(@x[1], @x[0], 7) sur des tampons qui se recouvrent : x[7] = ', x[7]:0:1, ' (le compilateur doit supposer l''alias)');
end.
