program k1soa_forms;
{$mode objfpc}{$H+}{$pointermath on}{$inline on}
{$CODEALIGN LOCALMIN=16}
uses cthreads, SysUtils, Linux, UnixType;
const N1 = 1 shl 22;
type TV4 = array[0..3] of Single; PV4 = ^TV4;
function NowNs: QWord; var tt: timespec; begin clock_gettime(CLOCK_MONOTONIC, @tt); Result := QWord(tt.tv_sec) * 1000000000 + QWord(tt.tv_nsec); end;
function SoAS(vx, vy, vz, m: PSingle; n: SizeInt): Double;
var a0, a1, a2, a3: Double; i: SizeInt;
begin
  a0 := 0; a1 := 0; a2 := 0; a3 := 0; i := 0;
  while i < n do begin
    a0 := a0 + (0.5 * m[i] * FMASingle(vz[i], vz[i], FMASingle(vy[i], vy[i], vx[i] * vx[i])));
    a1 := a1 + (0.5 * m[i + 1] * FMASingle(vz[i + 1], vz[i + 1], FMASingle(vy[i + 1], vy[i + 1], vx[i + 1] * vx[i + 1])));
    a2 := a2 + (0.5 * m[i + 2] * FMASingle(vz[i + 2], vz[i + 2], FMASingle(vy[i + 2], vy[i + 2], vx[i + 2] * vx[i + 2])));
    a3 := a3 + (0.5 * m[i + 3] * FMASingle(vz[i + 3], vz[i + 3], FMASingle(vy[i + 3], vy[i + 3], vx[i + 3] * vx[i + 3])));
    Inc(i, 4);
  end;
  Result := (a0 + a1) + (a2 + a3);
end;
function SoAV(vx, vy, vz, m: PV4; n: SizeInt): Double;
var a0, a1, a2, a3: Double; i: SizeInt; h, e: TV4;
begin
  a0 := 0; a1 := 0; a2 := 0; a3 := 0; h[0] := 0.5; h[1] := 0.5; h[2] := 0.5; h[3] := 0.5;
  for i := 0 to n div 4 - 1 do begin
    e := (h * m[i]) * ((vx[i] * vx[i] + vy[i] * vy[i]) + vz[i] * vz[i]);
    a0 := a0 + e[0]; a1 := a1 + e[1]; a2 := a2 + e[2]; a3 := a3 + e[3];
  end;
  Result := (a0 + a1) + (a2 + a3);
end;
var f: array[0..3] of PSingle; raw: Pointer; k, r: Integer; i: SizeInt; t0: QWord; e: Double; fl: File; buf: PSingle;
begin
  GetMem(buf, N1 * 64); AssignFile(fl, '/opt/msdata/k1_particles.f32'); Reset(fl, 1); BlockRead(fl, buf^, N1 * 64); CloseFile(fl);
  for k := 0 to 3 do begin GetMem(raw, N1 * 4 + 128); f[k] := Align(raw, 64); end;
  for i := 0 to N1 - 1 do begin f[0][i] := buf[16 * i + 3]; f[1][i] := buf[16 * i + 4]; f[2][i] := buf[16 * i + 5]; f[3][i] := buf[16 * i + 9]; end;
  for r := 0 to 4 do begin
    t0 := NowNs; e := SoAS(f[0], f[1], f[2], f[3], N1); WriteLn('SoAS ', e:0:6, ' ', (NowNs - t0) / 1e6:0:2, ' ms');
    t0 := NowNs; e := SoAV(PV4(f[0]), PV4(f[1]), PV4(f[2]), PV4(f[3]), N1); WriteLn('SoAV ', e:0:6, ' ', (NowNs - t0) / 1e6:0:2, ' ms');
  end;
end.
