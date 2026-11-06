{ Sonde Free Pascal (FPC 3.2.2) de la grille de capacités (analysis/capabilities.py) : cas positifs compilés et
  exécutés ; les cas négatifs (refusés par le compilateur ou mesurés sur le code produit) sont dans run.sh. }
program probe;

{$mode objfpc}{$H+}
{$pointermath on}
{$inline on}
{$asmmode intel}

uses
  cthreads, SysUtils, BaseUnix, Syscall, Generics.Collections;

type
  TParticle = record
    x, y, z, vx, vy, vz, ax, ay, az, mass, charge, radius, temp, pressure, energy, density: Single;
  end;
  TOrd = record
    a: Byte;
    b: Int64;
    c: Word;
  end;
  {$PACKRECORDS C}
  TCLay = record
    a: Byte;
    b: LongWord;
    c: Byte;
  end;
  {$PACKRECORDS DEFAULT}
  TPacked = packed record
    a: Byte;
    b: LongWord;
  end;
  TBits = bitpacked record
    f1: 0..7;
    f2: 0..31;
  end;
  TUnion = record
    case Integer of
      0: (f: Single);
      1: (u: LongWord);
      2: (b: array[0..3] of Byte);
  end;
  TInl = record
    v: array[0..15] of Single;
  end;
  TV4 = array[0..3] of Single;
  TGrid = array[0..3, 0..7] of Double;
  PGrid = ^TGrid;

{ ---- B2 : gestionnaire de mémoire remplacé (SetMemoryManager) et allocation par classe (NewInstance) }
var
  OldMM: TMemoryManager;
  Allocs: SizeInt;

function CountGetMem(size: PtrUInt): Pointer;
begin
  Inc(Allocs);
  Result := OldMM.GetMem(size);
end;

type
  TArenaObj = class
    v: Int64;
    class function NewInstance: TObject; override;
    procedure FreeInstance; override;
  end;

var
  Arena: array[0..4095] of Byte;
  ArenaTop: SizeInt = 0;

class function TArenaObj.NewInstance: TObject;
begin
  Result := InitInstance(@Arena[ArenaTop]);
  Inc(ArenaTop, InstanceSize);
end;

procedure TArenaObj.FreeInstance;
begin
  { rien : l'arène est libérée d'un bloc }
end;

{ ---- D1 }
var
  Cnt: array[0..3] of Int64;

function Worker(p: Pointer): PtrInt;
var
  i: Integer;
begin
  for i := 1 to 1000 do
    Inc(Cnt[PtrUInt(p)]);
  Result := 0;
end;

{ ---- E2 }
function AsmAnswer: Int64; assembler; nostackframe;
asm
  mov rax, 42
end;

{ ---- E6 }
function Checked(i: Integer): Boolean;
{$push}{$R+}
var
  a: array[0..3] of Integer;
  j: Integer;
begin
  Result := False;
  try
    j := i;
    a[j] := 1;
  except
    on ERangeError do
      Result := True;
  end;
end;
{$pop}

function Unchecked(i: Integer): Boolean;
var
  a: array[0..7] of Integer;
begin
  a[i and 7] := 1;
  Result := a[i and 7] = 1;
end;

{ ---- E7 }
generic function GMax<T>(a, b: T): T;
begin
  if a > b then
    Result := a
  else
    Result := b;
end;

const
  KFold = (1 shl 10) + Ord('A') * 3;

var
  ps: array of TParticle;
  o: TOrd;
  cl: TCLay;
  bits: TBits;
  un: TUnion;
  v1, v2, v3: TV4;
  g: PGrid;
  dyn: array of array of Double;
  mm: TMemoryManager;
  obj: TArenaObj;
  d: specialize TDictionary<Integer, Integer>;
  pair: specialize TPair<Integer, Integer>;
  s1, s2: string;
  n0, n1, n2, n3: SizeInt;
  th: array[0..3] of TThreadID;
  t: Integer;
  x64: Int64;
  q: QWord;
  li: LongInt;
  fd: cint;
  map: PLongWord;
  mask, back: array[0..15] of QWord;
  f: TextFile;
  stat: string;
  fields: TStringArray;
  raw: Pointer;
  al: PByte;
  local: array[0..63] of Byte;
  heapp: PByte;
begin
  { A1 }
  SetLength(ps, 4);
  WriteLn('CAP;A1;1;array of record : SizeOf(TParticle) = ', SizeOf(TParticle), ' o, écart entre éléments ',
    PtrUInt(@ps[1]) - PtrUInt(@ps[0]), ' o (valeurs en ligne)');
  { A2 }
  WriteLn('CAP;A2;1;record : décalages a=', PtrUInt(@o.a) - PtrUInt(@o), ' b=', PtrUInt(@o.b) - PtrUInt(@o), ' c=',
    PtrUInt(@o.c) - PtrUInt(@o), ' (ordre déclaré, alignement naturel) ; {$PACKRECORDS C} : taille ', SizeOf(cl),
    ' o, b à ', PtrUInt(@cl.b) - PtrUInt(@cl), ' (disposition C)');
  { A3 }
  bits.f1 := 5;
  bits.f2 := 17;
  WriteLn('CAP;A3;1;packed record {Byte; LongWord} : ', SizeOf(TPacked), ' o ; bitpacked record {0..7; 0..31} : ',
    SizeOf(TBits), ' o, champs relus ', bits.f1, ' et ', bits.f2);
  { A4 (alignement explicite : voir aussi run.sh) }
  GetMem(raw, 4096 + 64);
  al := Align(raw, 64);
  WriteLn('CAP;A4;0.5;GetMem + Align(p, 64) : adresse mod 64 = ', PtrUInt(al) mod 64,
    ' (à la main) ; {$CODEALIGN VARMIN=64} pour les variables globales ; pas d''alignement de type (run.sh)');
  { A5 }
  un.f := 1.0;
  WriteLn('CAP;A5;1;record à variantes sans champ d''étiquette (union brute) : Single 1.0 = $', HexStr(un.u, 8),
    ', octets ', un.b[0], ' ', un.b[1], ' ', un.b[2], ' ', un.b[3], ' ; absolute, transtypage de pointeur');
  WriteLn('CAP;A6;0;aucun type SoA');
  WriteLn('CAP;A7;1;record avec array[0..15] of Single : ', SizeOf(TInl), ' o en ligne');
  WriteLn('CAP;A8;1;Byte ', SizeOf(Byte), ' SmallInt ', SizeOf(SmallInt), ' Word ', SizeOf(Word), ' Single ',
    SizeOf(Single), ' ; intervalles bitpacked (A3) ; pas de flottant 16 bits');
  { B1 }
  s1 := 'abc';
  s1 := s1 + IntToStr(Length(ps));
  WriteLn('CAP;B1;1;pas de ramasse-miettes : comptage de références des chaînes, tableaux dynamiques et interfaces (',
    'StringRefCount = ', StringRefCount(s1), ')');
  { B2 }
  GetMemoryManager(OldMM);
  mm := OldMM;
  mm.GetMem := @CountGetMem;
  Allocs := 0;
  SetMemoryManager(mm);
  New(PInt64(raw));
  n0 := Allocs;
  SetMemoryManager(OldMM);
  obj := TArenaObj.Create;
  obj.v := 7;
  WriteLn('CAP;B2;0.5;SetMemoryManager (gestionnaire global remplaçable : ', n0, ' appel compté pour New) ; ',
    'NewInstance/FreeInstance redéfinissables par classe (objet construit dans une arène : décalage ',
    PtrUInt(obj) - PtrUInt(@Arena[0]), ', v = ', obj.v, ') ; pas d''allocateur passé aux conteneurs');
  obj.Free;
  { B3 }
  GetMem(heapp, 64);
  WriteLn('CAP;B3;1;records et tableaux statiques locaux sur la pile (distance à une variable locale : ',
    Abs(PtrInt(@local[0]) - PtrInt(@t)), ' o ; au tas : ', Abs(PtrInt(heapp) - PtrInt(@t)) > 1 shl 20, ')');
  FreeMem(heapp);
  { B4 : allocations implicites comptées par le gestionnaire de mémoire }
  d := specialize TDictionary<Integer, Integer>.Create;
  d.Add(1, 2);
  SetMemoryManager(mm);
  Allocs := 0;
  for t := 0 to High(ps) do
    ps[t].mass := t;
  n0 := Allocs;
  Allocs := 0;
  for pair in d do
    x64 := pair.Value;
  n1 := Allocs;
  Allocs := 0;
  s2 := s1 + 'x';
  n2 := Allocs;
  Allocs := 0;
  try
    raise Exception.Create('e');
  except
    on E: Exception do
      n3 := Allocs;
  end;
  SetMemoryManager(OldMM);
  WriteLn('CAP;B4;0.5;allocations implicites : boucle sur un tableau ', n0, ', énumération d''un TDictionary ', n1,
    ' (objet énumérateur), concaténation de chaînes ', n2, ', exception ', n3);
  d.Free;
  WriteLn('CAP;B5;1;Pointer, pointeurs typés, arithmétique ({$pointermath}), GetMem/FreeMem (bench)');
  { C1 (compilé avec -Sv) }
  v1[0] := 1; v1[1] := 2; v1[2] := 3; v1[3] := 4;
  v2 := v1;
  v3 := v1 * v2 + v1;
  WriteLn('CAP;C1;0.5;-Sv : opérations sur array[0..3] of Single (SSE 128 bits) : ', v3[0]:0:0, ' ', v3[1]:0:0, ' ',
    v3[2]:0:0, ' ', v3[3]:0:0, ' ; expérimental : 8 Single = erreur interne, alignement de 16 o exigé, ni masque ni ',
    'FMA ni conversion (run.sh)');
  WriteLn('CAP;C2;0.5;assembleur en ligne jusqu''à AVX2 et FMA (E2), sans intrinsèques SSE/AVX, comme Zig : seulement ',
    'des intrinsèques portables (FMASingle/FMADouble, Prefetch, PopCnt, BsfQWord…) ; erratum du 6/11, remarque sur ',
    'FreePascal : 0 avant');
  WriteLn('CAP;C5;0;aucune boucle parallèle ni réserve de tâches dans la RTL et les paquets livrés (mtprocs est un ',
    'paquet de Lazarus)');
  { D1 }
  for t := 0 to 3 do
    th[t] := BeginThread(@Worker, Pointer(PtrUInt(t)));
  for t := 0 to 3 do
    WaitForThreadTerminate(th[t], 0);
  WriteLn('CAP;D1;1;BeginThread (unité cthreads) et TThread : 4 fils, ', Cnt[0] + Cnt[1] + Cnt[2] + Cnt[3],
    ' incréments');
  { D2 }
  x64 := 5;
  InterLockedIncrement64(x64);
  InterLockedCompareExchange64(x64, 10, 6);
  WriteLn('CAP;D2;0.5;InterLockedIncrement64 / CompareExchange64 / ExchangeAdd64 (RMW séquentiellement cohérents, ',
    'appels de la RTL) : ', x64, ' ; ni ordre mémoire explicite ni lecture/écriture atomique');
  WriteLn('CAP;D3;0;aucune constante, requête ni type de bourrage de ligne de cache dans la RTL (l''unité cpu ne ',
    'détecte que des jeux d''instructions : AVXSupport, AVX2Support, FMASupport…)');
  { D4 : appel système brut de l'unité Syscall livrée }
  FillChar(mask, SizeOf(mask), 0);
  mask[0] := 2;
  n0 := Do_SysCall(syscall_nr_sched_setaffinity, 0, SizeOf(mask), TSysParam(@mask));
  FillChar(back, SizeOf(back), 0);
  Do_SysCall(syscall_nr_sched_getaffinity, 0, SizeOf(back), TSysParam(@back));
  for t := 1 to 20000000 do
    x64 := x64 + t;
  AssignFile(f, '/proc/self/stat');
  Reset(f);
  ReadLn(f, stat);
  CloseFile(f);
  fields := Copy(stat, Pos(')', stat) + 2, Length(stat)).Split(' ');
  WriteLn('CAP;D4;0.5;Do_SysCall(syscall_nr_sched_setaffinity) de l''unité Syscall livrée : retour ', n0,
    ', masque relu ', back[0], ', processeur courant (/proc/self/stat) ', fields[36],
    ' ; pas d''API d''affinité (ni TThread ni unité Linux)');
  ReadWriteBarrier;
  ReadBarrier;
  WriteBarrier;
  WriteLn('CAP;D5;0.5;ReadBarrier / WriteBarrier / ReadWriteBarrier (lfence, sfence, mfence dans des procédures de ',
    'la RTL) ; ThreadSwitch (sched_yield) ; pas de pause (run.sh)');
  { E }
  WriteLn('CAP;E1;1;code natif, -al garde l''assembleur produit');
  WriteLn('CAP;E2;1;blocs asm (syntaxe Intel ou AT&T, procédures assembler) : ', AsmAnswer,
    ' ; AVX2 accepté, AVX-512 inconnu de l''assembleur de FPC 3.2.2 (octets bruts seulement, run.sh)');
  WriteLn('CAP;E3;0;pas d''indication de branchement (Likely/Unlikely inconnus, run.sh)');
  WriteLn('CAP;E4;0.5;Prefetch(x) du System (intrinsèque : prefetchnta seulement, sans localité ni écriture, run.sh) ; ',
    'erratum du 6/11, remarque sur FreePascal : 1 avant');
  WriteLn('CAP;E5;0;ni restrict ni garantie de non-aliasing');
  WriteLn('CAP;E6;1;{$R+} / {$R-} locaux : indice 5 hors bornes détecté sous {$R+} : ', Checked(5),
    ' ; sans vérification ailleurs (défaut) : ', Unchecked(9));
  WriteLn('CAP;E7;0.5;génériques spécialisés à la compilation (specialize) : ', specialize GMax<Integer>(3, 7), ' ',
    specialize GMax<Double>(2.5, 1.5):0:1, ' ; expressions constantes (', KFold, '), pas d''évaluation de fonctions ',
    'à la compilation');
  { F1 }
  New(g);
  SetLength(dyn, 4, 8);
  WriteLn('CAP;F1;0.5;array[0..3, 0..7] of Double : ', SizeOf(TGrid), ' o contigus (écart entre lignes ',
    PtrUInt(@g^[1, 0]) - PtrUInt(@g^[0, 0]), ' o), bornes fixées à la compilation ; array of array : lignes séparées ',
    '(écart ', PtrInt(@dyn[1][0]) - PtrInt(@dyn[0][0]), ' o)');
  Dispose(g);
  WriteLn('CAP;F2;0;aucun');
  { F3 }
  q := High(QWord) - QWord(ParamCount); { valeurs connues à l'exécution seulement (sinon le repli des constantes refuse }
  q := q + 1;                            { le débordement à la compilation) }
  li := High(LongInt) - ParamCount;
  li := li + 1;
  WriteLn('CAP;F3;1;Byte...QWord et ShortInt...Int64, arithmétique modulaire sans {$Q+} (défaut) : ', q, ' ', li);
  { F4 }
  fd := FpOpen('/opt/msdata/k7_keys.u32', O_RDONLY);
  map := Fpmmap(nil, 1 shl 26, PROT_READ, MAP_PRIVATE, fd, 0);
  WriteLn('CAP;F4;0.5;Fpmmap (unité BaseUnix livrée, appel système propre à Unix, comme syscall.Mmap de Go ; 1 en ',
    'règle v2) + pointeur typé : premier mot ', map[0], ', dernier ', map[(1 shl 24) - 1], ' ; erratum du 6/11, ',
    'remarque sur FreePascal : 1 avant');
  Fpmunmap(map, 1 shl 26);
  FpClose(fd);
end.
