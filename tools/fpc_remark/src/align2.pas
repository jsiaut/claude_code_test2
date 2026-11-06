program align2;
{ alignement d'un type « end align 64 » sur la pile et par New (branche main) }
{$mode objfpc}
type
  TA = record x: Int64; end align 64;
  PA = ^TA;
var bad, tot: Integer;
procedure Chk(p: Pointer); begin Inc(tot); if PtrUInt(p) mod 64 <> 0 then Inc(bad); end;
procedure L1; var l: TA; begin Chk(@l); end;
procedure L2; var b: array[0..2] of Byte; l: TA; begin b[0] := 1; Chk(@l); Chk(@b); Dec(tot); if PtrUInt(@b) mod 64 <> 0 then Dec(bad); end;
procedure L3(d: Integer); var l: TA; c: array[0..6] of Byte; begin c[0] := d; Chk(@l); if d > 0 then L3(d - 1); end;
var p: PA; i: Integer;
begin
  bad := 0; tot := 0;
  L1; L2; L3(7);
  WriteLn('pile : ', bad, ' sur ', tot, ' locaux TA non alignés sur 64');
  bad := 0; tot := 0;
  for i := 1 to 16 do begin New(p); Chk(p); end;
  WriteLn('New : ', bad, ' sur ', tot, ' non alignés sur 64');
end.
