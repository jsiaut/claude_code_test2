program k5k9_forms;
{$mode objfpc}{$H+}{$pointermath on}{$inline on}
{$CODEALIGN LOCALMIN=16}
{$CODEALIGN CONSTMIN=16}
{$CODEALIGN VARMIN=16}
uses cthreads, SysUtils, Linux, UnixType;
const M9 = 2048;
type TV2 = array[0..1] of Double; PV2 = ^TV2; TV4 = array[0..3] of Single; PV4 = ^TV4;
function NowNs: QWord; var tt: timespec; begin clock_gettime(CLOCK_MONOTONIC, @tt); Result := QWord(tt.tv_sec) * 1000000000 + QWord(tt.tv_nsec); end;
procedure K9S(inp, outp: PDouble; r0, r1: SizeInt);
var i, j: SizeInt; up, mid, dn, o: PDouble; ml, mc, mr: Double;
begin
  for i := r0 to r1 - 1 do begin
    up := inp + (i - 1) * M9; mid := inp + i * M9; dn := inp + (i + 1) * M9; o := outp + i * M9;
    ml := mid[0]; mc := mid[1];
    for j := 1 to M9 - 2 do begin mr := mid[j + 1]; o[j] := 0.25 * (((up[j] + dn[j]) + ml) + mr); ml := mc; mc := mr; end;
  end;
end;
procedure K9S2(inp, outp: PDouble; r0, r1: SizeInt);
var i, j: SizeInt; up, mid, dn, o: PDouble;
begin
  for i := r0 to r1 - 1 do begin
    up := inp + (i - 1) * M9; mid := inp + i * M9; dn := inp + (i + 1) * M9; o := outp + i * M9;
    for j := 1 to M9 - 2 do o[j] := 0.25 * (((up[j] + dn[j]) + mid[j - 1]) + mid[j + 1]);
  end;
end;
procedure K9V(inp, outp: PDouble; r0, r1: SizeInt);
var i, j: SizeInt; up, mid, dn, o: PDouble; ml, mr, s, q4: TV2;
begin
  q4[0] := 0.25; q4[1] := 0.25;
  for i := r0 to r1 - 1 do begin
    up := inp + (i - 1) * M9; mid := inp + i * M9; dn := inp + (i + 1) * M9; o := outp + i * M9;
    o[1] := 0.25 * (((up[1] + dn[1]) + mid[0]) + mid[2]);
    j := 2;
    while j + 1 <= M9 - 2 do begin
      ml := PV2(mid + j - 1)^;
      mr := PV2(mid + j + 1)^;
      s := PV2(up + j)^ + PV2(dn + j)^;
      s := s + ml;
      s := s + mr;
      PV2(o + j)^ := s * q4;
      Inc(j, 2);
    end;
    o[M9 - 2] := 0.25 * (((up[M9 - 2] + dn[M9 - 2]) + mid[M9 - 3]) + mid[M9 - 1]);
  end;
end;
function K5V(a, b: PV4; n: SizeInt): Single;
var s0, s1, s2, s3, s4, s5, s6, s7, t: TV4; i: SizeInt;
begin
  FillChar(s0, 16, 0); s1 := s0; s2 := s0; s3 := s0; s4 := s0; s5 := s0; s6 := s0; s7 := s0;
  i := 0;
  while i < n div 4 do begin
    s0 := s0 + a[i] * b[i]; s1 := s1 + a[i + 1] * b[i + 1]; s2 := s2 + a[i + 2] * b[i + 2]; s3 := s3 + a[i + 3] * b[i + 3];
    s4 := s4 + a[i + 4] * b[i + 4]; s5 := s5 + a[i + 5] * b[i + 5]; s6 := s6 + a[i + 6] * b[i + 6]; s7 := s7 + a[i + 7] * b[i + 7];
    Inc(i, 8);
  end;
  t := ((s0 + s1) + (s2 + s3)) + ((s4 + s5) + (s6 + s7));
  Result := (t[0] + t[1]) + (t[2] + t[3]);
end;
function K5V4(a, b: PV4; n: SizeInt): Single;
var s0, s1, s2, s3, t: TV4; i: SizeInt;
begin
  FillChar(s0, 16, 0); s1 := s0; s2 := s0; s3 := s0;
  i := 0;
  while i < n div 4 do begin
    s0 := s0 + a[i] * b[i]; s1 := s1 + a[i + 1] * b[i + 1]; s2 := s2 + a[i + 2] * b[i + 2]; s3 := s3 + a[i + 3] * b[i + 3];
    Inc(i, 4);
  end;
  t := (s0 + s1) + (s2 + s3);
  Result := (t[0] + t[1]) + (t[2] + t[3]);
end;
function Init(g: PDouble): Double; var i, j: SizeInt; begin for i := 0 to M9 - 1 do for j := 0 to M9 - 1 do g[i * M9 + j] := Double((i * 31 + j * 17) mod 1024) / 1024.0; Result := 0; end;
var raw: Pointer; a, b, tmp, ka, kb: PDouble; r, it, kind: Integer; t0: QWord; s, dt: Double; k: SizeInt; d: Single; f: File; pa: PSingle;
const NM: array[0..2] of string = ('K9S', 'K9S2', 'K9V');
begin
  GetMem(raw, M9 * M9 * 8 + 128); ka := Align(raw, 64); GetMem(raw, M9 * M9 * 8 + 128); kb := Align(raw, 64);
  for r := 0 to 2 do for kind := 0 to 2 do begin
    a := ka; b := kb; Init(a); Move(a^, b^, M9 * M9 * 8);
    t0 := NowNs;
    for it := 1 to 4 do begin
      case kind of 0: K9S(a, b, 1, M9 - 1); 1: K9S2(a, b, 1, M9 - 1); 2: K9V(a, b, 1, M9 - 1); end;
      tmp := a; a := b; b := tmp;
    end;
    dt := (NowNs - t0) / 1e6; s := 0; for k := 0 to M9 * M9 - 1 do s := s + a[k];
    WriteLn(NM[kind], ' ', Format('%.16e', [s]), ' ', dt:0:2, ' ms');
  end;
  GetMem(raw, 2048 * 8 + 128); pa := Align(raw, 64);
  AssignFile(f, '/opt/msdata/k5_a.f32'); Reset(f, 1); BlockRead(f, pa^, 8192); CloseFile(f);
  AssignFile(f, '/opt/msdata/k5_b.f32'); Reset(f, 1); BlockRead(f, (pa + 2048)^, 8192); CloseFile(f);
  for r := 0 to 2 do begin
    t0 := NowNs; for it := 1 to 65536 do d := K5V(PV4(pa), PV4(pa + 2048), 2048); WriteLn('K5V8 ', d:0:4, ' ', (NowNs - t0) / 1e6:0:2, ' ms');
    t0 := NowNs; for it := 1 to 65536 do d := K5V4(PV4(pa), PV4(pa + 2048), 2048); WriteLn('K5V4 ', d:0:4, ' ', (NowNs - t0) / 1e6:0:2, ' ms');
  end;
end.
