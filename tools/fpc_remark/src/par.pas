program par;
{ TParallel.&For de System.Threading (paquet vcl-compat de la branche main) : fils distincts et durée de 4 appels
  successifs (64 tâches de 20 ms d'attente active chacune) }
{$mode objfpc}{$modeswitch anonymousfunctions}{$modeswitch functionreferences}
uses cthreads, SysUtils, Classes, System.Threading;
const N = 64;
var tid: array[0..N-1] of TThreadID; i, j, distinct, rep: Integer; seen: Boolean; t0: QWord;
begin
  for rep := 1 to 4 do begin
    t0 := GetTickCount64;
    TParallel.&For(0, N - 1, procedure(k: Integer)
      var t: QWord; begin tid[k] := GetCurrentThreadId; t := GetTickCount64; while GetTickCount64 - t < 20 do ; end);
    distinct := 0;
    for i := 0 to N - 1 do begin
      seen := False;
      for j := 0 to i - 1 do if tid[j] = tid[i] then seen := True;
      if not seen then Inc(distinct);
    end;
    WriteLn('passage ', rep, ' : fils distincts ', distinct, ' ; durée ', GetTickCount64 - t0, ' ms (série : ', N * 20, ' ms)');
  end;
end.
