program align64;
{ alignement d'un type : « end align 64 » (branche main) ; taille, décalage dans un enregistrement, variable globale }
{$mode objfpc}
type
  TA = record x: Int64; end align 64;
  TB = record a: Byte; c: TA; end;
var g1: Byte; g: TA; arr: array[0..3] of TA;
begin
  g1 := 0;
  WriteLn('SizeOf(TA)=', SizeOf(TA), ' SizeOf(TB)=', SizeOf(TB), ' décalage de c=', PtrUInt(@TB(nil^).c));
  WriteLn('globale mod 64 = ', PtrUInt(@g) mod 64, ' ; arr[1] mod 64 = ', PtrUInt(@arr[1]) mod 64, ' ', g1);
end.
