program dict_k7;
{$mode objfpc}{$H+}{$pointermath on}
uses cthreads, SysUtils, Linux, UnixType, Generics.Collections, Generics.Defaults;
type TAgg = record count: LongWord; sum: QWord; end;
  TMap = specialize TDictionary<LongWord, TAgg>;
  TCls = class count: LongWord; sum: QWord; end;
  TMapC = specialize TObjectDictionary<LongWord, TCls>;
var keys, vals: PLongWord; m: TMap; mc: TMapC; a: TAgg; c: TCls; i: SizeInt; t0: QWord; f: File; n: Int64; raw: Pointer; cnt: SizeInt;
function NowNs: QWord; var tt: timespec; begin clock_gettime(CLOCK_MONOTONIC, @tt); Result := QWord(tt.tv_sec) * 1000000000 + QWord(tt.tv_nsec); end;
function Rss: Int64; var tf: TextFile; s, r: Int64; begin AssignFile(tf, '/proc/self/statm'); Reset(tf); Read(tf, s, r); CloseFile(tf); Result := r * 4096; end;
type TCmp = specialize IEqualityComparer<LongWord>;
var r0: Int64; hc: TCmp; h: UInt32;
begin
  n := 1 shl 24; GetMem(keys, n * 4); GetMem(vals, n * 4);
  AssignFile(f, '/opt/msdata/k7_keys.u32'); Reset(f, 1); BlockRead(f, keys^, n * 4); CloseFile(f);
  AssignFile(f, '/opt/msdata/k7_vals.u32'); Reset(f, 1); BlockRead(f, vals^, n * 4); CloseFile(f);
  r0 := Rss;
  m := TMap.Create;
  t0 := NowNs;
  for i := 0 to n - 1 do begin
    if not m.TryGetValue(keys[i], a) then a := Default(TAgg);
    Inc(a.count); a.sum := a.sum + vals[i]; m.AddOrSetValue(keys[i], a);
  end;
  WriteLn('natural (Try+AddOrSet): ', (NowNs - t0) / 1e9:0:3, ' s, count ', m.Count, ', rss +', (Rss - r0) div (1 shl 20), ' MiB');
  t0 := NowNs; cnt := 0;
  for i := 0 to n - 1 do if m.TryGetValue(keys[i], a) then Inc(cnt);
  WriteLn('16M TryGetValue: ', (NowNs - t0) / 1e9:0:3, ' s');
  t0 := NowNs;
  for i := 0 to n - 1 do m.AddOrSetValue(keys[i], a);
  WriteLn('16M AddOrSetValue (existing): ', (NowNs - t0) / 1e9:0:3, ' s');
  t0 := NowNs; cnt := 0;
  for i := 0 to n - 1 do if m.ContainsKey(keys[i]) then Inc(cnt);
  WriteLn('16M ContainsKey: ', (NowNs - t0) / 1e9:0:3, ' s');
  m.Free;
  hc := specialize TEqualityComparer<LongWord>.Default;
  t0 := NowNs; h := 0;
  for i := 0 to n - 1 do h := h xor hc.GetHashCode(keys[i]);
  WriteLn('16M GetHashCode via comparer: ', (NowNs - t0) / 1e9:0:3, ' s ', h);
  r0 := Rss;
  mc := TMapC.Create([doOwnsValues]);
  t0 := NowNs;
  for i := 0 to n - 1 do begin
    if not mc.TryGetValue(keys[i], c) then begin c := TCls.Create; mc.Add(keys[i], c); end;
    Inc(c.count); c.sum := c.sum + vals[i];
  end;
  WriteLn('class values (Try + Add): ', (NowNs - t0) / 1e9:0:3, ' s, rss +', (Rss - r0) div (1 shl 20), ' MiB');
  mc.Free;
end.
