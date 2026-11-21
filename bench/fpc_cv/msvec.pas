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
  TV4 = array[0..3] of Single;
  PV4 = ^TV4;

function K1SoAV(vx, vy, vz, m: PV4; n: SizeInt): Double;
function K5TunedV(a, b: PV4; n: SizeInt): Single;
function K5TunedVPtr(a, b: PV4; n: SizeInt): Single;

implementation

{ SoA : énergie de 4 particules par opération vectorielle (f32), accumulation f64 voie par voie (4 accumulateurs) }
function K1SoAV(vx, vy, vz, m: PV4; n: SizeInt): Double;
var
  a0, a1, a2, a3: Double;
  i: SizeInt;
  h, e: TV4;
begin
  a0 := 0; a1 := 0; a2 := 0; a3 := 0;
  h[0] := 0.5; h[1] := 0.5; h[2] := 0.5; h[3] := 0.5;
  for i := 0 to n div 4 - 1 do
  begin
    e := (h * m[i]) * ((vx[i] * vx[i] + vy[i] * vy[i]) + vz[i] * vz[i]);
    a0 := a0 + e[0];
    a1 := a1 + e[1];
    a2 := a2 + e[2];
    a3 := a3 + e[3];
  end;
  Result := (a0 + a1) + (a2 + a3);
end;

{ produit scalaire : 8 accumulateurs vectoriels de 4 voies (32 sommes partielles), réduction en arbre }
function K5TunedV(a, b: PV4; n: SizeInt): Single;
var
  s0, s1, s2, s3, s4, s5, s6, s7, t: TV4;
  i: SizeInt;
begin
  FillChar(s0, SizeOf(s0), 0);
  s1 := s0; s2 := s0; s3 := s0; s4 := s0; s5 := s0; s6 := s0; s7 := s0;
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
  t := ((s0 + s1) + (s2 + s3)) + ((s4 + s5) + (s6 + s7));
  Result := (t[0] + t[1]) + (t[2] + t[3]);
end;

{ v4, point 4 (docs/V4_CONVERGE.md, 3.3, K5 tuned_v) : la forme de la remarque sur FreePascal (bench/fpc_rq, MIEUX ;
  docs/FPC.md, 5) : le même calcul que K5TunedV (8 accumulateurs de 4 voies, 4 Single étant la plus grande largeur
  que -Sv accepte : 8 Single = erreur interne 200610072), pointeurs avancés par Inc au lieu d'indices ; mêmes
  additions dans le même ordre, donc le même résultat }
function K5TunedVPtr(a, b: PV4; n: SizeInt): Single;
var
  s0, s1, s2, s3, s4, s5, s6, s7, t: TV4;
  e: PV4;
begin
  FillChar(s0, SizeOf(s0), 0);
  s1 := s0; s2 := s0; s3 := s0; s4 := s0; s5 := s0; s6 := s0; s7 := s0;
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
  t := ((s0 + s1) + (s2 + s3)) + ((s4 + s5) + (s6 + s7));
  Result := (t[0] + t[1]) + (t[2] + t[3]);
end;

end.
