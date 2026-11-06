program brhint;
{ indications de branchement : Likely est-il connu ? }
{$mode objfpc}
var v: LongInt;
begin
  v := ParamCount;
  if Likely(v > 0) then WriteLn('1') else WriteLn('2');
end.
