program asm512;
{ assembleur en ligne AVX-512 (zmm) }
{$asmmode intel}
procedure P; assembler; nostackframe;
asm
  vaddps zmm0, zmm1, zmm2
  vfmadd231ps zmm3, zmm4, zmm5
  ret
end;
begin
  WriteLn('ok');
end.
