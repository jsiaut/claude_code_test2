program k4forms;
{ K4 sans branchement : formes du masque de la remarque (s += v and -(v shr 7)) contre la forme publiée }
{$mode objfpc}{$H+}{$pointermath on}
uses cthreads, SysUtils, Linux, UnixType, BaseUnix;
function NowNs: QWord; var tt: timespec; begin clock_gettime(CLOCK_MONOTONIC, @tt); Result := QWord(tt.tv_sec) * 1000000000 + QWord(tt.tv_nsec); end;
function K4A(v: PByte; n: SizeInt): QWord; var i: SizeInt; s: QWord; begin s := 0; for i := 0 to n - 1 do s := s + QWord(v[i]) * (v[i] shr 7); Result := s; end;
function K4B(v: PByte; n: SizeInt): QWord; var i: SizeInt; s: QWord; begin s := 0; for i := 0 to n - 1 do s := s + QWord(v[i] and -(v[i] shr 7)); Result := s; end;
function K4C(v: PByte; n: SizeInt): QWord; var i: SizeInt; s, x: QWord; begin s := 0; for i := 0 to n - 1 do begin x := v[i]; s := s + (x and -(x shr 7)); end; Result := s; end;
function K4D(v: PByte; n: SizeInt): QWord; var i: SizeInt; s: QWord; x: Int64; begin s := 0; for i := 0 to n - 1 do begin x := v[i]; s := s + QWord(x and -(x shr 7)); end; Result := s; end;
function K4E(v: PByte; n: SizeInt): QWord; var i: SizeInt; s: QWord; x: SizeInt; begin s := 0; for i := 0 to n - 1 do begin x := v[i]; s := s + QWord(x and (0 - (x shr 7))); end; Result := s; end;
function K4F(v: PByte; n: SizeInt): QWord; var s: QWord; e: PByte; x: QWord; begin s := 0; e := v + n; while v < e do begin x := v^; s := s + (x and -(x shr 7)); Inc(v); end; Result := s; end;
function K4G(v: PByte; n: SizeInt): QWord; var i: SizeInt; s: QWord; x: LongWord; begin s := 0; for i := 0 to n - 1 do begin x := v[i]; s := s + (x and -(x shr 7)); end; Result := s; end;
var fd: cint; n: SizeInt; buf: PByte; st: Stat; t: QWord; r: QWord; k, rep: Integer; best: array[0..6] of Double; dt: Double;
  names: array[0..6] of string = ('A publié', 'B v[i] and -(v[i] shr 7)', 'C x:QWord', 'D x:Int64', 'E x:SizeInt 0-', 'F pointeur x:QWord', 'G x:LongWord');
begin
  fd := FpOpen('/opt/msdata/k4_bytes.u8', O_RDONLY); FpFStat(fd, st); n := st.st_size; buf := GetMem(n); FpRead(fd, buf^, n); FpClose(fd);
  for k := 0 to 6 do best[k] := 1e9;
  for rep := 1 to 5 do for k := 0 to 6 do begin
    t := NowNs;
    case k of 0: r := K4A(buf, n); 1: r := K4B(buf, n); 2: r := K4C(buf, n); 3: r := K4D(buf, n); 4: r := K4E(buf, n); 5: r := K4F(buf, n); 6: r := K4G(buf, n); end;
    dt := (NowNs - t) / 1e9; if dt < best[k] then best[k] := dt;
    if rep = 5 then WriteLn(names[k]:28, ' ', best[k]:0:5, ' s  rapport ', best[k] / best[0]:0:2, '  somme ', r);
  end;
end.
