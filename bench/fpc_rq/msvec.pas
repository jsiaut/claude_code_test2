{ Copie de la remarque sur FreePascal (docs/FPC.md, section 5) : bench/fpc/msvec.pas, avec MIEUX (K5 par
  pointeurs avancés par Inc) et M128 (type __m128 de la branche main, accès aux voies par PSingle). }
{ Noyaux optimisés écrits avec le traitement vectoriel de FPC (option documentée -Sv, « Support vector processing ») :
  opérateurs arithmétiques sur des tableaux de 4 Single, traduits en instructions SSE de 128 bits. C'est le seul code
  du banc compilé sous cette forme, et seulement là où elle bat le scalaire (docs/FPC.md, 2.4) : K1 soa et K5 tuned.
  Contraintes relevées avec FPC 3.2.2 : 128 bits au plus (un tableau de 8 Single provoque l'erreur interne 200610072),
  opérandes mémoire en encodage SSE classique (alignement de 16 octets exigé, erreur d'exécution 216 sinon : d'où
  l'alignement des locaux ci-dessous et des tampons alignés sur 64 octets), vecteurs gardés en mémoire entre deux
  opérations, ni FMA ni conversion vectorielles. }
unit msvec;

{$mode objfpc}{$H+}
{$pointermath on}
{$CODEALIGN LOCALMIN=16}

interface

type
  {$ifdef M128}
  TV4 = __m128;
  {$else}
  TV4 = array[0..3] of Single;
  {$endif}
  PV4 = ^TV4;

function K1SoAV(vx, vy, vz, m: PV4; n: SizeInt): Double;
function K5TunedV(a, b: PV4; n: SizeInt): Single;

implementation

{ SoA : énergie de 4 particules par opération vectorielle (f32), accumulation f64 voie par voie (4 accumulateurs) }
function K1SoAV(vx, vy, vz, m: PV4; n: SizeInt): Double;
var
  a0, a1, a2, a3: Double;
  i: SizeInt;
  h, e: TV4;
begin
  a0 := 0; a1 := 0; a2 := 0; a3 := 0;
  {$ifdef M128}
  PSingle(@h)[0] := 0.5; PSingle(@h)[1] := 0.5; PSingle(@h)[2] := 0.5; PSingle(@h)[3] := 0.5;
  {$else}
  h[0] := 0.5; h[1] := 0.5; h[2] := 0.5; h[3] := 0.5;
  {$endif}
  for i := 0 to n div 4 - 1 do
  begin
    e := (h * m[i]) * ((vx[i] * vx[i] + vy[i] * vy[i]) + vz[i] * vz[i]);
    {$ifdef M128}
    a0 := a0 + PSingle(@e)[0];
    a1 := a1 + PSingle(@e)[1];
    a2 := a2 + PSingle(@e)[2];
    a3 := a3 + PSingle(@e)[3];
    {$else}
    a0 := a0 + e[0];
    a1 := a1 + e[1];
    a2 := a2 + e[2];
    a3 := a3 + e[3];
    {$endif}
  end;
  Result := (a0 + a1) + (a2 + a3);
end;

{ produit scalaire : 8 accumulateurs vectoriels de 4 voies (32 sommes partielles), réduction en arbre }
function K5TunedV(a, b: PV4; n: SizeInt): Single;
var
  s0, s1, s2, s3, s4, s5, s6, s7, t: TV4;
  i: SizeInt;
  {$ifdef MIEUX}
  e: PV4;
  {$endif}
begin
  FillChar(s0, SizeOf(s0), 0);
  s1 := s0; s2 := s0; s3 := s0; s4 := s0; s5 := s0; s6 := s0; s7 := s0;
  {$ifdef MIEUX}
  { pointeurs avancés par Inc (proposé par la remarque) }
  e := a + n div 4;
  while a < e do
  begin
    s0 := s0 + a[0] * b[0];
    s1 := s1 + a[1] * b[1];
    s2 := s2 + a[2] * b[2];
    s3 := s3 + a[3] * b[3];
    s4 := s4 + a[4] * b[4];
    s5 := s5 + a[5] * b[5];
    s6 := s6 + a[6] * b[6];
    s7 := s7 + a[7] * b[7];
    Inc(a, 8);
    Inc(b, 8);
  end;
  {$else}
  i := 0;
  while i < n div 4 do
  begin
    s0 := s0 + a[i] * b[i];
    s1 := s1 + a[i + 1] * b[i + 1];
    s2 := s2 + a[i + 2] * b[i + 2];
    s3 := s3 + a[i + 3] * b[i + 3];
    s4 := s4 + a[i + 4] * b[i + 4];
    s5 := s5 + a[i + 5] * b[i + 5];
    s6 := s6 + a[i + 6] * b[i + 6];
    s7 := s7 + a[i + 7] * b[i + 7];
    Inc(i, 8);
  end;
  {$endif}
  t := ((s0 + s1) + (s2 + s3)) + ((s4 + s5) + (s6 + s7));
  {$ifdef M128}
  Result := (PSingle(@t)[0] + PSingle(@t)[1]) + (PSingle(@t)[2] + PSingle(@t)[3]);
  {$else}
  Result := (t[0] + t[1]) + (t[2] + t[3]);
  {$endif}
end;

end.
