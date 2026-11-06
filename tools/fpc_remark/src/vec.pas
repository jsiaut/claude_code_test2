program vec;
{ -Sv de la branche main sur __m128 (ou __m256 avec -dM256) : somme comparée au calcul scalaire }
{$mode objfpc}
{$ifdef M256} type TV = __m256; const W = 8; {$else} type TV = __m128; const W = 4; {$endif}
type PV = ^TV;
var a, b: array[0..63] of Single; s: TV; i, k: Integer; tot, ref: Double; pa, pb: PV;
begin
  for i := 0 to 63 do begin a[i] := i * 0.5; b[i] := 64 - i; end;
  FillChar(s, SizeOf(s), 0);
  i := 0;
  while i < 64 do begin
    pa := PV(@a[i]); pb := PV(@b[i]);
    s := s + pa^ * pb^;
    Inc(i, W);
  end;
  tot := 0; for k := 0 to W - 1 do tot := tot + PSingle(@s)[k];
  ref := 0; for i := 0 to 63 do ref := ref + a[i] * b[i];
  WriteLn('W=', W, ' somme=', tot:0:3, ' attendu=', ref:0:3);
end.
