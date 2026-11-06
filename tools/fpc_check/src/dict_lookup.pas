program dict_lookup;
{$mode objfpc}{$H+}{$pointermath on}
uses cthreads, SysUtils, Linux, UnixType, Generics.Collections;
type TAgg = record count: LongWord; sum: QWord; end;
  TMap = specialize TDictionary<LongWord, TAgg>;
function NowNs: QWord; var tt: timespec; begin clock_gettime(CLOCK_MONOTONIC, @tt); Result := QWord(tt.tv_sec) * 1000000000 + QWord(tt.tv_nsec); end;
const SIZES: array[0..3] of SizeInt = (16, 1024, 65536, 1048576);
var m: TMap; a: TAgg; i, nk, reps, j, cnt, z: SizeInt; t0: QWord; k: array of LongWord;
begin
  for z := 0 to 3 do begin nk := SIZES[z];
    SetLength(k, nk); for i := 0 to nk - 1 do k[i] := LongWord(i) * 2654435761;
    m := TMap.Create; a := Default(TAgg);
    for i := 0 to nk - 1 do m.AddOrSetValue(k[i], a);
    reps := (1 shl 24) div nk; cnt := 0;
    t0 := NowNs;
    for j := 1 to reps do for i := 0 to nk - 1 do if m.TryGetValue(k[i], a) then Inc(cnt);
    WriteLn(nk:8, ' keys: ', (NowNs - t0) / (reps * nk):0:1, ' ns/lookup');
    m.Free;
  end;
end.
