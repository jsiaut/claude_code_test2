program q1_forms;
{$mode objfpc}{$H+}{$pointermath on}{$inline on}
uses cthreads, SysUtils, BaseUnix, UnixType, Linux;
const N6 = 1 shl 24;
type TQ1Acc = array[0..5, 0..4] of Int64;
var sd, pr: PLongInt; q, d, t, rf, ls: PByte;
function NowNs: QWord; var tt: timespec; begin clock_gettime(CLOCK_MONOTONIC, @tt); Result := QWord(tt.tv_sec) * 1000000000 + QWord(tt.tv_nsec); end;
function Load(const n: string): Pointer; var f: File; sz: Int64; raw: Pointer;
begin AssignFile(f, '/opt/msdata/' + n); Reset(f, 1); sz := FileSize(f); GetMem(raw, sz + 128); Result := Align(raw, 64); BlockRead(f, Result^, sz); CloseFile(f); end;

function Q6a(sd: PLongInt; d, q: PByte; pr: PLongInt; lo, hi: SizeInt): Int64;
var i: SizeInt; s, m: Int64;
begin
  s := 0;
  for i := lo to hi - 1 do begin
    m := ((Int64(LongWord(sd[i] - 8766)) - 365) shr 63) and ((Int64(Byte(d[i] - 5)) - 3) shr 63) and ((Int64(q[i]) - 24) shr 63);
    s := s + (Int64(pr[i] * LongInt(d[i])) and -m);
  end;
  Result := s;
end;
{$B+}
function Q6b(sd: PLongInt; d, q: PByte; pr: PLongInt; lo, hi: SizeInt): Int64;
var i: SizeInt; s: Int64;
begin
  s := 0;
  for i := lo to hi - 1 do
    if (LongWord(sd[i] - 8766) < 365) and (Byte(d[i] - 5) <= 2) and (q[i] < 24) then
      s := s + pr[i] * LongInt(d[i]);
  Result := s;
end;
{$B-}
procedure Q1n(lo, hi: SizeInt; var acc: TQ1Acc);
var i: SizeInt; g: Integer; p, dp: Int64;
begin
  for i := lo to hi - 1 do
    if sd[i] <= 10471 then begin
      g := rf[i] * 2 + ls[i]; p := pr[i]; dp := p * (100 - d[i]);
      Inc(acc[g, 0]); acc[g, 1] := acc[g, 1] + q[i]; acc[g, 2] := acc[g, 2] + p; acc[g, 3] := acc[g, 3] + dp; acc[g, 4] := acc[g, 4] + dp * (100 + t[i]);
    end;
end;
{ une table, pointeurs locaux, pointeur de ligne }
procedure Q1a(csd, cpr: PLongInt; cq, cd, ct, crf, cls: PByte; lo, hi: SizeInt; var acc: TQ1Acc);
var tb: array[0..7, 0..4] of Int64; i, g: SizeInt; p, dp: Int64; a: PInt64;
begin
  FillChar(tb, SizeOf(tb), 0);
  for i := lo to hi - 1 do begin
    g := crf[i] * 2 + cls[i];
    if csd[i] > 10471 then g := 6;
    a := @tb[g, 0];
    p := cpr[i]; dp := p * (100 - cd[i]);
    a[0] := a[0] + 1; a[1] := a[1] + cq[i]; a[2] := a[2] + p; a[3] := a[3] + dp; a[4] := a[4] + dp * (100 + ct[i]);
  end;
  for g := 0 to 5 do for i := 0 to 4 do acc[g, i] := acc[g, i] + tb[g, i];
end;
{ deux tables entrelacées }
procedure Q1b(csd, cpr: PLongInt; cq, cd, ct, crf, cls: PByte; lo, hi: SizeInt; var acc: TQ1Acc);
var tb: array[0..1, 0..7, 0..4] of Int64; i, g: SizeInt; p, dp: Int64; a: PInt64;
begin
  FillChar(tb, SizeOf(tb), 0);
  i := lo;
  while i + 2 <= hi do begin
    g := crf[i] * 2 + cls[i]; if csd[i] > 10471 then g := 6;
    a := @tb[0, g, 0]; p := cpr[i]; dp := p * (100 - cd[i]);
    a[0] := a[0] + 1; a[1] := a[1] + cq[i]; a[2] := a[2] + p; a[3] := a[3] + dp; a[4] := a[4] + dp * (100 + ct[i]);
    g := crf[i + 1] * 2 + cls[i + 1]; if csd[i + 1] > 10471 then g := 6;
    a := @tb[1, g, 0]; p := cpr[i + 1]; dp := p * (100 - cd[i + 1]);
    a[0] := a[0] + 1; a[1] := a[1] + cq[i + 1]; a[2] := a[2] + p; a[3] := a[3] + dp; a[4] := a[4] + dp * (100 + ct[i + 1]);
    Inc(i, 2);
  end;
  while i < hi do begin
    g := crf[i] * 2 + cls[i]; if csd[i] > 10471 then g := 6;
    a := @tb[0, g, 0]; p := cpr[i]; dp := p * (100 - cd[i]);
    a[0] := a[0] + 1; a[1] := a[1] + cq[i]; a[2] := a[2] + p; a[3] := a[3] + dp; a[4] := a[4] + dp * (100 + ct[i]);
    Inc(i);
  end;
  for g := 0 to 5 do for i := 0 to 4 do acc[g, i] := acc[g, i] + tb[0, g, i] + tb[1, g, i];
end;
type TColsP = record sd, pr: PLongInt; q, d, t, rf, ls: PByte; end;
procedure Q1d(const c: TColsP; lo, hi: SizeInt; var acc: TQ1Acc);
type TTab = array[0..6, 0..4] of Int64;
var t0, t1, t2, t3: TTab; i: SizeInt;
  procedure Row(var tb: TTab; j: SizeInt); inline;
  var g: SizeInt; p, dp: Int64;
  begin
    g := c.rf[j] * 2 + c.ls[j];
    g := g + ((6 - g) and -((Int64(10471) - c.sd[j]) shr 63));
    p := c.pr[j]; dp := p * (100 - c.d[j]);
    tb[g, 0] := tb[g, 0] + 1; tb[g, 1] := tb[g, 1] + c.q[j]; tb[g, 2] := tb[g, 2] + p; tb[g, 3] := tb[g, 3] + dp; tb[g, 4] := tb[g, 4] + dp * (100 + c.t[j]);
  end;
var g, k: Integer;
begin
  FillChar(t0, SizeOf(t0), 0); FillChar(t1, SizeOf(t1), 0); FillChar(t2, SizeOf(t2), 0); FillChar(t3, SizeOf(t3), 0);
  i := lo;
  while i + 4 <= hi do begin Row(t0, i); Row(t1, i + 1); Row(t2, i + 2); Row(t3, i + 3); Inc(i, 4); end;
  while i < hi do begin Row(t0, i); Inc(i); end;
  for g := 0 to 5 do for k := 0 to 4 do acc[g, k] := acc[g, k] + t0[g, k] + t1[g, k] + t2[g, k] + t3[g, k];
end;
function Sum(const acc: TQ1Acc): Int64; var g, k: Integer; begin Result := 0; for g := 0 to 5 do for k := 0 to 4 do Result := Result + acc[g, k]; end;
var r: Integer; t0: QWord; s: Int64; acc: TQ1Acc; cp: TColsP;
begin
  sd := Load('k6_shipdate.i32'); pr := Load('k6_extendedprice.i32'); q := Load('k6_quantity.u8'); d := Load('k6_discount.u8');
  t := Load('k6_tax.u8'); rf := Load('k6_returnflag.u8'); ls := Load('k6_linestatus.u8');
  cp.sd := sd; cp.pr := pr; cp.q := q; cp.d := d; cp.t := t; cp.rf := rf; cp.ls := ls;
  for r := 0 to 2 do begin
    t0 := NowNs; s := Q6a(sd, d, q, pr, 0, N6); WriteLn('Q6a ', s, ' ', (NowNs - t0) / 1e6:0:2, ' ms');
    t0 := NowNs; s := Q6b(sd, d, q, pr, 0, N6); WriteLn('Q6b ', s, ' ', (NowNs - t0) / 1e6:0:2, ' ms');
    FillChar(acc, SizeOf(acc), 0); t0 := NowNs; Q1n(0, N6, acc); WriteLn('Q1n ', Sum(acc), ' ', (NowNs - t0) / 1e6:0:2, ' ms');
    FillChar(acc, SizeOf(acc), 0); t0 := NowNs; Q1a(sd, pr, q, d, t, rf, ls, 0, N6, acc); WriteLn('Q1a ', Sum(acc), ' ', (NowNs - t0) / 1e6:0:2, ' ms');
    FillChar(acc, SizeOf(acc), 0); t0 := NowNs; Q1d(cp, 0, N6, acc); WriteLn('Q1d ', Sum(acc), ' ', (NowNs - t0) / 1e6:0:2, ' ms');
    FillChar(acc, SizeOf(acc), 0); t0 := NowNs; Q1b(sd, pr, q, d, t, rf, ls, 0, N6, acc); WriteLn('Q1b ', Sum(acc), ' ', (NowNs - t0) / 1e6:0:2, ' ms');
  end;
end.
