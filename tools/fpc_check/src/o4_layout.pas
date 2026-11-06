program o4_layout;
{$mode objfpc}
type
  TR = record a: Byte; b: Int64; c: Byte; d: LongInt; end;
  TC = class a: Byte; b: Int64; c: Byte; d: LongInt; end;
var r: TR; o: TC;
begin
  o := TC.Create;
  writeln('record ', SizeOf(TR), ' ', PtrUInt(@r.b) - PtrUInt(@r), ' ', PtrUInt(@r.c) - PtrUInt(@r), ' ', PtrUInt(@r.d) - PtrUInt(@r));
  writeln('class ', TC.InstanceSize, ' ', PtrUInt(@o.a) - PtrUInt(o), ' ', PtrUInt(@o.b) - PtrUInt(o), ' ', PtrUInt(@o.c) - PtrUInt(o), ' ', PtrUInt(@o.d) - PtrUInt(o));
end.
