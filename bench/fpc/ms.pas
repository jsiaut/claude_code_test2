{ Implémentation Free Pascal (FPC 3.2.2, mode objfpc) des noyaux de docs/SPEC.md. Voir docs/FPC.md.
  Bibliothèques : RTL (System, SysUtils, unités Unix et Linux livrées), Generics.Collections (rtl-generics, livrée
  avec FPC 3.2) ; threads par BeginThread (unité cthreads, la première de la liste, comme l'exige la RTL sous Unix).
  Le code naturel suit les réglages par défaut (vérifications de bornes et de débordement désactivées par défaut en
  FPC : directives R- et Q-) ; le code optimisé passe par des pointeurs typés (pointermath), des boucles déroulées à
  plusieurs accumulateurs, les intrinsèques FMASingle / Prefetch du System et, pour K1 soa et K5, le traitement
  vectoriel de 128 bits de l'option -Sv (unité msvec) : FPC 3.2.2 n'a ni vectoriseur automatique ni type vectoriel
  plus large, et l'assembleur en ligne est exclu par la règle (docs/SPEC.md). Avec -dSCALAR (copie bench/fpc_scal),
  K1 soa et K5 tuned prennent leur version scalaire. }
program ms;

{$mode objfpc}{$H+}
{$pointermath on}
{$inline on}

uses
  cthreads, SysUtils, BaseUnix, UnixType, Linux, Generics.Collections{$ifndef SCALAR}, msvec{$endif};

{ ------------------------------------------------------------------ harnais }
var
  DataDir: string;
  Warmup: Integer;

function NowNs: QWord;
var
  t: timespec;
begin
  clock_gettime(CLOCK_MONOTONIC, @t);
  Result := QWord(t.tv_sec) * 1000000000 + QWord(t.tv_nsec);
end;

function Secs(t0: QWord): Double;
begin
  Result := Double(NowNs - t0) / 1e9;
end;

procedure Emit(const k, v, p: string; rep: Integer; sec: Double; const chk: string);
begin
  WriteLn('RESULT;', k, ';', v, ';', p, ';', rep, ';', Format('%.9f', [sec]), ';', chk);
  Flush(Output);
end;

{ tampon aligné : le pointeur d'origine est rangé juste avant le bloc rendu }
function AllocAligned(bytes, alignment: PtrUInt): Pointer;
var
  raw: Pointer;
begin
  GetMem(raw, bytes + alignment + SizeOf(Pointer));
  Result := Align(PByte(raw) + SizeOf(Pointer), alignment);
  PPointer(PByte(Result) - SizeOf(Pointer))^ := raw;
end;

procedure FreeAligned(p: Pointer);
begin
  if p <> nil then
    FreeMem(PPointer(PByte(p) - SizeOf(Pointer))^);
end;

function DataPath(const name: string): string;
begin
  Result := DataDir + '/' + name;
end;

function FileLen(const name: string): PtrUInt;
var
  st: Stat;
begin
  if FpStat(PChar(DataPath(name)), st) <> 0 then
  begin
    WriteLn(StdErr, 'stat ', DataPath(name));
    Halt(1);
  end;
  Result := st.st_size;
end;

procedure ReadInto(const name: string; dst: Pointer; n: PtrUInt);
var
  fd: cint;
  off: PtrUInt;
  r: TSsize;
begin
  fd := FpOpen(PChar(DataPath(name)), O_RDONLY);
  if fd < 0 then
  begin
    WriteLn(StdErr, 'open ', DataPath(name));
    Halt(1);
  end;
  off := 0;
  while off < n do
  begin
    r := FpRead(fd, PChar(dst) + off, n - off);
    if r <= 0 then
    begin
      WriteLn(StdErr, 'read ', DataPath(name));
      Halt(1);
    end;
    Inc(off, r);
  end;
  FpClose(fd);
end;

{ données du code optimisé : tampon aligné sur une ligne de cache (comme le C de référence) }
function LoadRaw(const name: string): Pointer;
var
  n: PtrUInt;
begin
  n := FileLen(name);
  Result := AllocAligned(n, 64);
  ReadInto(name, Result, n);
end;

{ données du code naturel : tableaux dynamiques (le conteneur par défaut) }
type
  TArrS = array of Single;
  TArrU8 = array of Byte;
  TArrU32 = array of LongWord;
  TArrI32 = array of LongInt;

function LoadS(const name: string): TArrS;
begin
  SetLength(Result, FileLen(name) div SizeOf(Single));
  ReadInto(name, @Result[0], Length(Result) * SizeOf(Single));
end;

function LoadU8(const name: string): TArrU8;
begin
  SetLength(Result, FileLen(name));
  ReadInto(name, @Result[0], Length(Result));
end;

function LoadU32(const name: string): TArrU32;
begin
  SetLength(Result, FileLen(name) div SizeOf(LongWord));
  ReadInto(name, @Result[0], Length(Result) * SizeOf(LongWord));
end;

function LoadI32(const name: string): TArrI32;
begin
  SetLength(Result, FileLen(name) div SizeOf(LongInt));
  ReadInto(name, @Result[0], Length(Result) * SizeOf(LongInt));
end;

{ ------------------------------------------------------------------ K1 }
const
  N1 = 1 shl 22;

type
  { enregistrement naturel : record (type valeur), rangé en ligne dans un tableau dynamique ; champs dans l'ordre
    déclaré, alignement naturel : 64 octets }
  TParticle = record
    x, y, z, vx, vy, vz, ax, ay, az, mass, charge, radius, temp, pressure, energy, density: Single;
  end;
  PParticle = ^TParticle;
  TParticles = array of TParticle;

function K1Natural(const ps: TParticles): Double;
var
  i: SizeInt;
  e: Double;
begin
  e := 0;
  for i := 0 to High(ps) do
    e := e + 0.5 * ps[i].mass * (ps[i].vx * ps[i].vx + ps[i].vy * ps[i].vy + ps[i].vz * ps[i].vz);
  Result := e;
end;

{ énergie d'une particule en f32, avec FMA explicite (la référence C est contractée en FMA par clang) }
function KE(q: PParticle): Single; inline;
begin
  Result := 0.5 * q^.mass * FMASingle(q^.vz, q^.vz, FMASingle(q^.vy, q^.vy, q^.vx * q^.vx));
end;

{ AoS optimisé : calcul f32, 8 accumulateurs f64 (un par particule du lot), tampon aligné sur 64 octets }
function K1AoS(p: PParticle; n: SizeInt): Double;
var
  a0, a1, a2, a3, a4, a5, a6, a7: Double;
  i: SizeInt;
begin
  a0 := 0; a1 := 0; a2 := 0; a3 := 0; a4 := 0; a5 := 0; a6 := 0; a7 := 0;
  i := 0;
  while i < n do
  begin
    a0 := a0 + KE(p + i);
    a1 := a1 + KE(p + i + 1);
    a2 := a2 + KE(p + i + 2);
    a3 := a3 + KE(p + i + 3);
    a4 := a4 + KE(p + i + 4);
    a5 := a5 + KE(p + i + 5);
    a6 := a6 + KE(p + i + 6);
    a7 := a7 + KE(p + i + 7);
    Inc(i, 8);
  end;
  Result := ((a0 + a1) + (a2 + a3)) + ((a4 + a5) + (a6 + a7));
end;

{ SoA optimisé, version scalaire (copie -dSCALAR) : tableaux séparés alignés, FMA, 4 accumulateurs f64 ; la version
  publiée est K1SoAV (unité msvec) }
function K1SoA(vx, vy, vz, m: PSingle; n: SizeInt): Double;
var
  a0, a1, a2, a3: Double;
  i: SizeInt;
begin
  a0 := 0; a1 := 0; a2 := 0; a3 := 0;
  i := 0;
  while i < n do
  begin
    a0 := a0 + (0.5 * m[i] * FMASingle(vz[i], vz[i], FMASingle(vy[i], vy[i], vx[i] * vx[i])));
    a1 := a1 + (0.5 * m[i + 1] * FMASingle(vz[i + 1], vz[i + 1], FMASingle(vy[i + 1], vy[i + 1], vx[i + 1] * vx[i + 1])));
    a2 := a2 + (0.5 * m[i + 2] * FMASingle(vz[i + 2], vz[i + 2], FMASingle(vy[i + 2], vy[i + 2], vx[i + 2] * vx[i + 2])));
    a3 := a3 + (0.5 * m[i + 3] * FMASingle(vz[i + 3], vz[i + 3], FMASingle(vy[i + 3], vy[i + 3], vx[i + 3] * vx[i + 3])));
    Inc(i, 4);
  end;
  Result := (a0 + a1) + (a2 + a3);
end;

{ empreinte K1 (D2a) : RSS courant en octets (/proc/self/statm, 2e champ ; pages de 4 Kio) }
function RssNow: Int64;
var
  f: TextFile;
  size, res: Int64;
begin
  Result := 0;
  AssignFile(f, '/proc/self/statm');
  {$I-}
  Reset(f);
  {$I+}
  if IOResult <> 0 then
    Exit;
  Read(f, size, res);
  CloseFile(f);
  Result := res * 4096;
end;

procedure RunK1(const v: string; reps: Integer);
var
  ps, s: TParticles;
  perm: TArrU32;
  f: array[0..15] of PSingle;
  a: PParticle;
  m1, m2: Int64;
  r, k: Integer;
  i: SizeInt;
  t0: QWord;
  dt, e: Double;
begin
  if (v = 'footprint0') or (v = 'footprint_raw') then
  begin
    Emit('k1', v, 'energy', 0, 0, '0');
    Exit;
  end;
  m1 := 0;
  if v = 'footprint' then
    m1 := RssNow; { P1 : avant la lecture (la collection naturelle est le tableau lu, comme en C) }
  SetLength(ps, FileLen('k1_particles.f32') div SizeOf(TParticle));
  ReadInto('k1_particles.f32', @ps[0], Length(ps) * SizeOf(TParticle));
  if v = 'footprint' then
  begin
    m2 := RssNow; { P2 : après la lecture }
    WriteLn('META;mem;rss;', m1, ';', m2);
    WriteLn('META;rss;', m1, ';', m2);
    Emit('k1', v, 'energy', 0, 0, Format('%.6f', [K1Natural(ps)]));
    Exit;
  end;
  if v = 'soa' then
  begin
    for k := 0 to 15 do
    begin
      f[k] := AllocAligned(N1 * SizeOf(Single), 64);
      for i := 0 to N1 - 1 do
        f[k][i] := PSingle(@ps[i])[k];
    end;
    SetLength(ps, 0);
    for r := -Warmup to reps - 1 do
    begin
      t0 := NowNs;
      {$ifdef SCALAR}
      e := K1SoA(f[3], f[4], f[5], f[9], N1);
      {$else}
      e := K1SoAV(PV4(f[3]), PV4(f[4]), PV4(f[5]), PV4(f[9]), N1);
      {$endif}
      dt := Secs(t0);
      if r >= 0 then
        Emit('k1', v, 'energy', r, dt, Format('%.6f', [e]));
    end;
    Exit;
  end;
  if v = 'aos' then
  begin
    a := AllocAligned(N1 * SizeOf(TParticle), 64);
    Move(ps[0], a^, N1 * SizeOf(TParticle));
    SetLength(ps, 0);
    for r := -Warmup to reps - 1 do
    begin
      t0 := NowNs;
      e := K1AoS(a, N1);
      dt := Secs(t0);
      if r >= 0 then
        Emit('k1', v, 'energy', r, dt, Format('%.6f', [e]));
    end;
    Exit;
  end;
  if v = 'natural_shuffled' then
  begin
    perm := LoadU32('k1_perm.u32');
    SetLength(s, Length(ps));
    for i := 0 to High(perm) do
      s[i] := ps[perm[i]];
    ps := s;
    s := nil;
    perm := nil;
  end;
  for r := -Warmup to reps - 1 do
  begin
    t0 := NowNs;
    e := K1Natural(ps);
    dt := Secs(t0);
    if r >= 0 then
      Emit('k1', v, 'energy', r, dt, Format('%.6f', [e]));
  end;
end;

{ ------------------------------------------------------------------ K2 }
function K2Chase(a: PLongWord; h: SizeInt): LongWord;
var
  i: LongWord;
  k: SizeInt;
begin
  i := 0;
  for k := 1 to h do
    i := a[i];
  Result := i;
end;

procedure RunK2(const v: string; reps: Integer; const p: string);
var
  a: PLongWord;
  r: Integer;
  t0: QWord;
  dt: Double;
  x: LongWord;
begin
  a := LoadRaw('k2_chase_' + p + '.u32');
  for r := -Warmup to reps - 1 do
  begin
    t0 := NowNs;
    x := K2Chase(a, 4200000);
    dt := Secs(t0);
    if r >= 0 then
      Emit('k2', v, p, r, dt, IntToStr(x));
  end;
end;

{ ------------------------------------------------------------------ K3 }
const
  ITER3 = 1 shl 25;

type
  TK3Arg = record
    c: PInt64;
    rmw: Boolean;
  end;
  PK3Arg = ^TK3Arg;

{ RMW : InterLockedIncrement64 (System ; lock xadd). Écriture simple : accès ordinaire par pointeur, que FPC garde en
  mémoire à chaque itération (vérifié dans le code produit) : FPC 3.2.2 n'a ni atomique relâché ni volatile. }
function K3Worker(p: Pointer): PtrInt;
var
  c: PInt64;
  i: SizeInt;
begin
  c := PK3Arg(p)^.c;
  if PK3Arg(p)^.rmw then
    for i := 1 to ITER3 do
      InterLockedIncrement64(c^)
  else
    for i := 1 to ITER3 do
      c^ := c^ + 1;
  Result := 0;
end;

procedure RunK3(const v: string; reps: Integer);
var
  padded, rmw: Boolean;
  mem: PInt64;
  stride, t, r: Integer;
  arg: array[0..3] of TK3Arg;
  th: array[0..3] of TThreadID;
  t0: QWord;
  dt: Double;
  s: Int64;
begin
  padded := Pos('padded', v) > 0;
  rmw := Copy(v, 1, 3) = 'rmw';
  mem := AllocAligned(4 * 128, 128);
  if padded then stride := 16 else stride := 1; { en Int64 : 128 o ou 8 o }
  if rmw then
    WriteLn('META;k3_mechanism;InterLockedIncrement64 (appel de la RTL, lock xadd)')
  else
    WriteLn('META;k3_mechanism;acces ordinaire par pointeur (add en memoire)');
  for r := -Warmup to reps - 1 do
  begin
    for t := 0 to 3 do
      mem[t * stride] := 0;
    t0 := NowNs;
    for t := 0 to 3 do
    begin
      arg[t].c := @mem[t * stride];
      arg[t].rmw := rmw;
      th[t] := BeginThread(@K3Worker, @arg[t]);
    end;
    for t := 0 to 3 do
      WaitForThreadTerminate(th[t], 0);
    dt := Secs(t0);
    s := 0;
    for t := 0 to 3 do
      s := s + mem[t * stride];
    if r >= 0 then
      Emit('k3', v, '4x2^25', r, dt, IntToStr(s));
  end;
end;

{ ------------------------------------------------------------------ K4 }
const
  N4 = 1 shl 24;

function K4Natural(const v: TArrU8): QWord;
var
  i: SizeInt;
  s: QWord;
begin
  s := 0;
  for i := 0 to High(v) do
    if v[i] >= 128 then
      s := s + v[i];
  Result := s;
end;

function K4Branchless(v: PByte; n: SizeInt): QWord;
var
  i: SizeInt;
  s: QWord;
begin
  s := 0;
  for i := 0 to n - 1 do
    s := s + QWord(v[i]) * (v[i] shr 7);
  Result := s;
end;

procedure RunK4(const v: string; reps: Integer);
var
  d: TArrU8;
  cnt: array[0..255] of SizeInt;
  i, k, c: SizeInt;
  b, r: Integer;
  t0: QWord;
  dt: Double;
  s: QWord;
begin
  d := LoadU8('k4_bytes.u8');
  if v = 'natural_sorted' then { tri par comptage, hors chrono (comme la référence C) }
  begin
    FillChar(cnt, SizeOf(cnt), 0);
    for i := 0 to High(d) do
      Inc(cnt[d[i]]);
    k := 0;
    for b := 0 to 255 do
      for c := 1 to cnt[b] do
      begin
        d[k] := b;
        Inc(k);
      end;
  end;
  for r := -Warmup to reps - 1 do
  begin
    t0 := NowNs;
    if v = 'branchless_unsorted' then
      s := K4Branchless(@d[0], Length(d))
    else
      s := K4Natural(d);
    dt := Secs(t0);
    if r >= 0 then
      Emit('k4', v, '16M', r, dt, IntToStr(s));
  end;
end;

{ ------------------------------------------------------------------ K5 }
const
  INNER5 = 1 shl 16;

function K5Natural(const a, b: TArrS): Single;
var
  i: SizeInt;
  s: Single;
begin
  s := 0;
  for i := 0 to High(a) do
    s := s + a[i] * b[i];
  Result := s;
end;

{ optimisé, version scalaire (copie -dSCALAR) : 8 accumulateurs f32 et FMA (latence 4, deux unités : 8 chaînes
  indépendantes), réduction en arbre ; la version publiée est K5TunedV (unité msvec) }
function K5Tuned(a, b: PSingle; n: SizeInt): Single;
var
  s0, s1, s2, s3, s4, s5, s6, s7: Single;
  i: SizeInt;
begin
  s0 := 0; s1 := 0; s2 := 0; s3 := 0; s4 := 0; s5 := 0; s6 := 0; s7 := 0;
  i := 0;
  while i < n do
  begin
    s0 := FMASingle(a[i], b[i], s0);
    s1 := FMASingle(a[i + 1], b[i + 1], s1);
    s2 := FMASingle(a[i + 2], b[i + 2], s2);
    s3 := FMASingle(a[i + 3], b[i + 3], s3);
    s4 := FMASingle(a[i + 4], b[i + 4], s4);
    s5 := FMASingle(a[i + 5], b[i + 5], s5);
    s6 := FMASingle(a[i + 6], b[i + 6], s6);
    s7 := FMASingle(a[i + 7], b[i + 7], s7);
    Inc(i, 8);
  end;
  Result := ((s0 + s1) + (s2 + s3)) + ((s4 + s5) + (s6 + s7));
end;

procedure RunK5(const v: string; reps: Integer);
var
  a, b: TArrS;
  pa, pb: PSingle;
  tuned: Boolean;
  r, it: Integer;
  t0: QWord;
  dt: Double;
  d: Single;
begin
  tuned := v = 'tuned';
  a := LoadS('k5_a.f32');
  b := LoadS('k5_b.f32');
  pa := LoadRaw('k5_a.f32');
  pb := LoadRaw('k5_b.f32');
  for r := -Warmup to reps - 1 do
  begin
    d := 0;
    t0 := NowNs;
    { FPC n'analyse pas les appels : chaque appel est exécuté et son résultat gardé (vérifié dans le code produit) }
    for it := 1 to INNER5 do
      if tuned then
        {$ifdef SCALAR}
        d := K5Tuned(pa, pb, Length(a))
        {$else}
        d := K5TunedV(PV4(pa), PV4(pb), Length(a))
        {$endif}
      else
        d := K5Natural(a, b);
    dt := Secs(t0);
    if r >= 0 then
      Emit('k5', v, '2048x65536', r, dt, Format('%.4f', [d]));
  end;
end;

{ ------------------------------------------------------------------ K6 }
const
  N6 = 1 shl 24;

type
  { colonnes naturelles : tableaux dynamiques }
  TCols = record
    sd, pr: TArrI32;
    q, d, t, rf, ls: TArrU8;
  end;
  TQ1Agg = record
    count, qty, price, discPrice, charge: Int64;
  end;
  TQ1Acc = array[0..5] of TQ1Agg;
  { colonnes du code optimisé : tampons alignés sur 64 octets }
  TColsP = record
    sd, pr: PLongInt;
    q, d, t, rf, ls: PByte;
  end;
  PColsP = ^TColsP;

function Q6Natural(const c: TCols): Int64;
var
  i: SizeInt;
  s: Int64;
begin
  s := 0;
  for i := 0 to High(c.sd) do
    if (c.sd[i] >= 8766) and (c.sd[i] < 9131) and (c.d[i] >= 5) and (c.d[i] <= 7) and (c.q[i] < 24) then
      s := s + Int64(c.pr[i]) * c.d[i];
  Result := s;
end;

procedure Q1Natural(const c: TCols; var acc: TQ1Acc);
var
  i: SizeInt;
  g: Integer;
  p, dp: Int64;
begin
  for i := 0 to High(c.sd) do
    if c.sd[i] <= 10471 then
    begin
      g := c.rf[i] * 2 + c.ls[i];
      p := c.pr[i];
      dp := p * (100 - c.d[i]);
      Inc(acc[g].count);
      acc[g].qty := acc[g].qty + c.q[i];
      acc[g].price := acc[g].price + p;
      acc[g].discPrice := acc[g].discPrice + dp;
      acc[g].charge := acc[g].charge + dp * (100 + c.t[i]);
    end;
end;

{ Q6 optimisé : prédicat évalué sans branchement (masques arithmétiques sur 64 bits), produit en 32 bits comme le C ;
  scalaire ; colonnes en paramètres (pointeurs gardés dans des registres : lus dans l'enregistrement, ils sont
  rechargés à chaque ligne par FPC) }
function Q6Tuned(sd: PLongInt; d, q: PByte; pr: PLongInt; lo, hi: SizeInt): Int64;
var
  i: SizeInt;
  s, m: Int64;
begin
  s := 0;
  for i := lo to hi - 1 do
  begin
    m := ((Int64(LongWord(sd[i] - 8766)) - 365) shr 63) and ((Int64(Byte(d[i] - 5)) - 3) shr 63) and
      ((Int64(q[i]) - 24) shr 63);
    s := s + (Int64(pr[i] * LongInt(d[i])) and -m);
  end;
  Result := s;
end;

{ Q1 optimisé (scalaire) : deux tables d'accumulateurs locales entrelacées (ligne paire / impaire) pour casser les
  dépendances par la mémoire entre lignes consécutives du même groupe ; 7e groupe fictif pour les lignes filtrées ;
  pointeur de ligne de table ; colonnes en paramètres ; fusion à la fin. (Quatre tables et une procédure imbriquée
  inline : plus lent, FPC recalcule les adresses à chaque accès ; docs/FPC.md, 2.4.) }
procedure Q1Tuned(csd, cpr: PLongInt; cq, cd, ct, crf, cls: PByte; lo, hi: SizeInt; var acc: TQ1Acc);
var
  tb: array[0..1, 0..7, 0..4] of Int64;
  i, g: SizeInt;
  p, dp: Int64;
  a: PInt64;
begin
  FillChar(tb, SizeOf(tb), 0);
  i := lo;
  while i + 2 <= hi do
  begin
    g := crf[i] * 2 + cls[i];
    if csd[i] > 10471 then
      g := 6;
    a := @tb[0, g, 0];
    p := cpr[i];
    dp := p * (100 - cd[i]);
    a[0] := a[0] + 1;
    a[1] := a[1] + cq[i];
    a[2] := a[2] + p;
    a[3] := a[3] + dp;
    a[4] := a[4] + dp * (100 + ct[i]);
    g := crf[i + 1] * 2 + cls[i + 1];
    if csd[i + 1] > 10471 then
      g := 6;
    a := @tb[1, g, 0];
    p := cpr[i + 1];
    dp := p * (100 - cd[i + 1]);
    a[0] := a[0] + 1;
    a[1] := a[1] + cq[i + 1];
    a[2] := a[2] + p;
    a[3] := a[3] + dp;
    a[4] := a[4] + dp * (100 + ct[i + 1]);
    Inc(i, 2);
  end;
  while i < hi do
  begin
    g := crf[i] * 2 + cls[i];
    if csd[i] > 10471 then
      g := 6;
    a := @tb[0, g, 0];
    p := cpr[i];
    dp := p * (100 - cd[i]);
    a[0] := a[0] + 1;
    a[1] := a[1] + cq[i];
    a[2] := a[2] + p;
    a[3] := a[3] + dp;
    a[4] := a[4] + dp * (100 + ct[i]);
    Inc(i);
  end;
  for g := 0 to 5 do
  begin
    acc[g].count := acc[g].count + tb[0, g, 0] + tb[1, g, 0];
    acc[g].qty := acc[g].qty + tb[0, g, 1] + tb[1, g, 1];
    acc[g].price := acc[g].price + tb[0, g, 2] + tb[1, g, 2];
    acc[g].discPrice := acc[g].discPrice + tb[0, g, 3] + tb[1, g, 3];
    acc[g].charge := acc[g].charge + tb[0, g, 4] + tb[1, g, 4];
  end;
end;

type
  TK6Arg = record
    c: PColsP;
    lo, hi: SizeInt;
    q1: Boolean;
    s6: Int64;
    acc: TQ1Acc;
  end;
  PK6Arg = ^TK6Arg;

function K6Worker(p: Pointer): PtrInt;
var
  a: PK6Arg;
begin
  a := PK6Arg(p);
  with a^.c^ do
    if a^.q1 then
      Q1Tuned(sd, pr, q, d, t, rf, ls, a^.lo, a^.hi, a^.acc)
    else
      a^.s6 := Q6Tuned(sd, d, q, pr, a^.lo, a^.hi);
  Result := 0;
end;

function Q1Sum(const acc: TQ1Acc): Int64;
var
  g: Integer;
begin
  Result := 0;
  for g := 0 to 5 do
    Result := Result + acc[g].count + acc[g].qty + acc[g].price + acc[g].discPrice + acc[g].charge;
end;

procedure RunK6(const v: string; reps: Integer; const p: string);
var
  c: TCols;
  cp: TColsP;
  q1: Boolean;
  acc: TQ1Acc;
  arg: array[0..3] of TK6Arg;
  th: array[0..3] of TThreadID;
  r, t: Integer;
  t0: QWord;
  dt: Double;
  s: Int64;
begin
  q1 := p = 'q1';
  if v = 'natural' then
  begin
    c.sd := LoadI32('k6_shipdate.i32');
    c.pr := LoadI32('k6_extendedprice.i32');
    c.q := LoadU8('k6_quantity.u8');
    c.d := LoadU8('k6_discount.u8');
    c.t := LoadU8('k6_tax.u8');
    c.rf := LoadU8('k6_returnflag.u8');
    c.ls := LoadU8('k6_linestatus.u8');
    for r := -Warmup to reps - 1 do
    begin
      FillChar(acc, SizeOf(acc), 0);
      s := 0;
      t0 := NowNs;
      if q1 then
        Q1Natural(c, acc)
      else
        s := Q6Natural(c);
      dt := Secs(t0);
      if q1 then
        s := Q1Sum(acc);
      if r >= 0 then
        Emit('k6', v, p, r, dt, IntToStr(s));
    end;
    Exit;
  end;
  cp.sd := LoadRaw('k6_shipdate.i32');
  cp.pr := LoadRaw('k6_extendedprice.i32');
  cp.q := LoadRaw('k6_quantity.u8');
  cp.d := LoadRaw('k6_discount.u8');
  cp.t := LoadRaw('k6_tax.u8');
  cp.rf := LoadRaw('k6_returnflag.u8');
  cp.ls := LoadRaw('k6_linestatus.u8');
  for r := -Warmup to reps - 1 do
  begin
    FillChar(acc, SizeOf(acc), 0);
    s := 0;
    t0 := NowNs;
    if v = 'mt' then
    begin
      for t := 0 to 3 do
      begin
        FillChar(arg[t], SizeOf(arg[t]), 0);
        arg[t].c := @cp;
        arg[t].lo := SizeInt(N6) * t div 4;
        arg[t].hi := SizeInt(N6) * (t + 1) div 4;
        arg[t].q1 := q1;
        th[t] := BeginThread(@K6Worker, @arg[t]);
      end;
      for t := 0 to 3 do
      begin
        WaitForThreadTerminate(th[t], 0);
        s := s + arg[t].s6;
        if q1 then
          s := s + Q1Sum(arg[t].acc);
      end;
    end
    else if q1 then
      Q1Tuned(cp.sd, cp.pr, cp.q, cp.d, cp.t, cp.rf, cp.ls, 0, N6, acc)
    else
      s := Q6Tuned(cp.sd, cp.d, cp.q, cp.pr, 0, N6);
    dt := Secs(t0);
    if q1 and (v <> 'mt') then
      s := Q1Sum(acc);
    if r >= 0 then
      Emit('k6', v, p, r, dt, IntToStr(s));
  end;
end;

{ ------------------------------------------------------------------ K7 }
const
  N7 = 1 shl 24;
  LOG7 = 21;
  CAP7 = 1 shl LOG7;
  BATCH7 = 16;

type
  TAgg = record
    count: LongWord;
    sum: QWord;
  end;
  { table naturelle : TDictionary de Generics.Collections (livrée avec FPC 3.2) }
  TAggMap = specialize TDictionary<LongWord, TAgg>;
  { case de la table optimisée (16 octets, 4 par ligne de cache) }
  TSlot = record
    key, count: LongWord;
    sum: QWord;
  end;
  PSlot = ^TSlot;

{ adressage ouvert, sondage linéaire, hachage de Fibonacci, lots préchargés (Prefetch du System : prefetchnta) ;
  fonction séparée, pointeurs en paramètres (dans RunK7, qui a des variables gérées, FPC garde les variables en
  mémoire) ; allocation et mise à zéro de la table comprises, comme en C }
function K7Tuned(keys, vals: PLongWord; n: SizeInt): PSlot;
var
  tab: PSlot;
  h: array[0..BATCH7 - 1] of LongWord;
  i: SizeInt;
  b: Integer;
  k, s: LongWord;
begin
  tab := AllocAligned(CAP7 * SizeOf(TSlot), 64);
  FillChar(tab^, CAP7 * SizeOf(TSlot), 0);
  i := 0;
  while i < n do
  begin
    for b := 0 to BATCH7 - 1 do
    begin
      h[b] := LongWord(QWord(keys[i + b]) * $9E3779B1) shr (32 - LOG7);
      Prefetch(tab[h[b]]);
    end;
    for b := 0 to BATCH7 - 1 do
    begin
      k := keys[i + b];
      s := h[b];
      while (tab[s].count <> 0) and (tab[s].key <> k) do
        s := (s + 1) and (CAP7 - 1);
      tab[s].key := k;
      Inc(tab[s].count);
      tab[s].sum := tab[s].sum + vals[i + b];
    end;
    Inc(i, BATCH7);
  end;
  Result := tab;
end;

{$ifdef EXP}
type
  { sensibilité (copie bench/fpc_exp) : valeurs de classe, une recherche par ligne pour une clé déjà présente }
  TAggC = class
    count: LongWord;
    sum: QWord;
  end;
  TAggCMap = specialize TObjectDictionary<LongWord, TAggC>;

function K7NaturalCls(const keys, vals: TArrU32; out nk, ws: QWord): Double;
var
  m: TAggCMap;
  a: TAggC;
  pair: specialize TPair<LongWord, TAggC>;
  i: SizeInt;
  t0: QWord;
begin
  t0 := NowNs;
  m := TAggCMap.Create([doOwnsValues]);
  for i := 0 to High(keys) do
  begin
    if not m.TryGetValue(keys[i], a) then
    begin
      a := TAggC.Create;
      m.Add(keys[i], a);
    end;
    Inc(a.count);
    a.sum := a.sum + vals[i];
  end;
  Result := Secs(t0);
  nk := 0;
  ws := 0;
  for pair in m do
  begin
    Inc(nk);
    ws := ws + pair.Value.sum * ((pair.Key and 1023) + 1);
  end;
  m.Free;
end;
{$endif}

procedure RunK7(const v: string; reps: Integer);
var
  keys, vals: TArrU32;
  m: TAggMap;
  pair: specialize TPair<LongWord, TAgg>;
  a: TAgg;
  tab: PSlot;
  i: SizeInt;
  r: Integer;
  t0: QWord;
  dt: Double;
  nk, ws: QWord;
begin
  keys := LoadU32('k7_keys.u32');
  vals := LoadU32('k7_vals.u32');
  for r := -Warmup to reps - 1 do
  begin
    nk := 0;
    ws := 0;
    {$ifdef EXP}
    if v = 'natural_cls' then
      dt := K7NaturalCls(keys, vals, nk, ws)
    else
    {$endif}
    if v = 'natural' then
    begin
      t0 := NowNs;
      m := TAggMap.Create;
      for i := 0 to High(keys) do
      begin
        if not m.TryGetValue(keys[i], a) then
          a := Default(TAgg);
        Inc(a.count);
        a.sum := a.sum + vals[i];
        m.AddOrSetValue(keys[i], a);
      end;
      dt := Secs(t0);
      for pair in m do
      begin
        Inc(nk);
        ws := ws + pair.Value.sum * ((pair.Key and 1023) + 1);
      end;
      m.Free;
    end
    else
    begin
      t0 := NowNs;
      tab := K7Tuned(@keys[0], @vals[0], Length(keys));
      dt := Secs(t0);
      for i := 0 to CAP7 - 1 do
        if tab[i].count <> 0 then
        begin
          Inc(nk);
          ws := ws + tab[i].sum * ((tab[i].key and 1023) + 1);
        end;
      FreeAligned(tab);
    end;
    if r >= 0 then
      Emit('k7', v, '16M/1M', r, dt, IntToStr(nk) + ':' + IntToStr(ws));
  end;
end;

{ ------------------------------------------------------------------ K8 }
type
  { nœud naturel : record et pointeur, New / Dispose (gestionnaire de mémoire de la RTL) }
  PNode = ^TNode;
  TNode = record
    v: Int64;
    l, r: PNode;
  end;
  { arène : nœuds compacts dans un tableau réutilisé, enfants par indice }
  TANode = record
    v: Int64;
    l, r: LongInt;
  end;
  PANode = ^TANode;
  TArrU64 = array of QWord;

function TBuild(depth: Integer; var counter: Int64): PNode;
var
  n: PNode;
begin
  New(n);
  n^.v := counter;
  Inc(counter);
  if depth > 0 then
  begin
    n^.l := TBuild(depth - 1, counter);
    n^.r := TBuild(depth - 1, counter);
  end
  else
  begin
    n^.l := nil;
    n^.r := nil;
  end;
  Result := n;
end;

function TSum(n: PNode): Int64;
begin
  if n = nil then
    Result := 0
  else
    Result := n^.v + TSum(n^.l) + TSum(n^.r);
end;

procedure TFree(n: PNode);
begin
  if n <> nil then
  begin
    TFree(n^.l);
    TFree(n^.r);
    Dispose(n);
  end;
end;

function ABuild(a: PANode; var top: LongInt; depth: Integer; var counter: Int64): LongInt;
var
  i, l: LongInt;
begin
  i := top;
  Inc(top);
  a[i].v := counter;
  Inc(counter);
  if depth > 0 then
  begin
    l := ABuild(a, top, depth - 1, counter);
    a[i].l := l;
    a[i].r := ABuild(a, top, depth - 1, counter);
  end
  else
  begin
    a[i].l := -1;
    a[i].r := -1;
  end;
  Result := i;
end;

function ASum(a: PANode; i: LongInt): Int64;
begin
  if i < 0 then
    Result := 0
  else
    Result := a[i].v + ASum(a, a[i].l) + ASum(a, a[i].r);
end;

{$ifdef EXP}
type
  { sensibilité (copie bench/fpc_exp) : nœuds de classe (TObject.Create / Free) }
  TCNode = class
    v: Int64;
    l, r: TCNode;
  end;

function CBuild(depth: Integer; var counter: Int64): TCNode;
begin
  Result := TCNode.Create;
  Result.v := counter;
  Inc(counter);
  if depth > 0 then
  begin
    Result.l := CBuild(depth - 1, counter);
    Result.r := CBuild(depth - 1, counter);
  end;
end;

function CSum(n: TCNode): Int64;
begin
  if n = nil then
    Result := 0
  else
    Result := n.v + CSum(n.l) + CSum(n.r);
end;

procedure CFree(n: TCNode);
begin
  if n <> nil then
  begin
    CFree(n.l);
    CFree(n.r);
    n.Free;
  end;
end;
{$endif}

procedure RunK8(const v: string; reps: Integer);
const
  Q = 16384;
  D = 10;
var
  tuned: Boolean;
  cnt, lsum, total, c, s: Int64;
  longlived, t: PNode;
  {$ifdef EXP}
  ct: TCNode;
  cls: Boolean;
  {$endif}
  lat: TArrU64;
  arena: PANode;
  top, root: LongInt;
  r, qi: Integer;
  t0, a: QWord;
  dt: Double;
begin
  tuned := v = 'tuned';
  {$ifdef EXP}
  cls := v = 'natural_cls';
  {$endif}
  cnt := 0;
  longlived := TBuild(20, cnt);
  lsum := TSum(longlived);
  SetLength(lat, Q);
  GetMem(arena, SizeOf(TANode) * 2047);
  for r := -Warmup to reps - 1 do
  begin
    total := 0;
    t0 := NowNs;
    for qi := 0 to Q - 1 do
    begin
      a := NowNs;
      c := qi;
      {$ifdef EXP}
      if cls then
      begin
        ct := CBuild(D, c);
        s := CSum(ct);
        CFree(ct);
      end
      else
      {$endif}
      if tuned then
      begin
        top := 0;
        root := ABuild(arena, top, D, c);
        s := ASum(arena, root);
      end
      else
      begin
        t := TBuild(D, c);
        s := TSum(t);
        TFree(t);
      end;
      total := total + s;
      lat[qi] := NowNs - a;
    end;
    dt := Secs(t0);
    if r >= 0 then
    begin
      Emit('k8', v, '16384x2047', r, dt, IntToStr(total + lsum));
      specialize TArrayHelper<QWord>.Sort(lat);
      WriteLn('LAT;', v, ';', lat[Q div 2], ';', lat[Q * 9 div 10], ';', lat[Q * 99 div 100], ';',
        lat[Q * 999 div 1000], ';', lat[Q - 1]);
      Flush(Output);
    end;
  end;
  TFree(longlived);
end;

{ ------------------------------------------------------------------ K9 }
const
  M9 = 2048;
  IT9 = 4;

type
  { naturel : tableau statique à deux dimensions (le tableau de base de Pascal, contigu), alloué par New }
  TGrid = array[0..M9 - 1, 0..M9 - 1] of Double;
  PGrid = ^TGrid;

procedure K9Natural(const inp: TGrid; var outp: TGrid);
var
  i, j: Integer;
begin
  for i := 1 to M9 - 2 do
    for j := 1 to M9 - 2 do
      outp[i, j] := 0.25 * (((inp[i - 1, j] + inp[i + 1, j]) + inp[i, j - 1]) + inp[i, j + 1]);
end;

{$ifdef EXP}
type
  { sensibilité (copie bench/fpc_exp) : tableau dynamique de tableaux dynamiques (SetLength à deux dimensions) }
  TDyn2 = array of array of Double;

procedure K9NaturalDyn(const inp: TDyn2; var outp: TDyn2);
var
  i, j: Integer;
begin
  for i := 1 to M9 - 2 do
    for j := 1 to M9 - 2 do
      outp[i][j] := 0.25 * (((inp[i - 1][j] + inp[i + 1][j]) + inp[i][j - 1]) + inp[i][j + 1]);
end;

procedure RunK9Dyn(const v: string; reps: Integer);
var
  ga, gb, gt: TDyn2;
  i, j, it, r: Integer;
  t0: QWord;
  dt, s: Double;
begin
  SetLength(ga, M9, M9);
  SetLength(gb, M9, M9);
  for r := -Warmup to reps - 1 do
  begin
    for i := 0 to M9 - 1 do
      for j := 0 to M9 - 1 do
      begin
        ga[i][j] := Double((i * 31 + j * 17) mod 1024) / 1024.0;
        gb[i][j] := ga[i][j];
      end;
    t0 := NowNs;
    for it := 1 to IT9 do
    begin
      K9NaturalDyn(ga, gb);
      gt := ga;
      ga := gb;
      gb := gt;
    end;
    dt := Secs(t0);
    s := 0;
    for i := 0 to M9 - 1 do
      for j := 0 to M9 - 1 do
        s := s + ga[i][j];
    if r >= 0 then
      Emit('k9', v, '2048^2x4', r, dt, Format('%.16e', [s]));
  end;
end;
{$endif}

{ optimisé : lignes d'un tableau plat aligné, pointeurs, indices SizeInt (pas d'extension de signe à chaque accès),
  fenêtre glissante sur la ligne du milieu (une lecture de moins par point) ; même ordre d'addition que le C ;
  scalaire (en -Sv sur 2 doubles, plus lent : docs/FPC.md, 2.4) }
procedure K9Rows(inp, outp: PDouble; r0, r1: SizeInt);
var
  i, j: SizeInt;
  up, mid, dn, o: PDouble;
  ml, mc, mr: Double;
begin
  for i := r0 to r1 - 1 do
  begin
    up := inp + (i - 1) * M9;
    mid := inp + i * M9;
    dn := inp + (i + 1) * M9;
    o := outp + i * M9;
    ml := mid[0];
    mc := mid[1];
    for j := 1 to M9 - 2 do
    begin
      mr := mid[j + 1];
      o[j] := 0.25 * (((up[j] + dn[j]) + ml) + mr);
      ml := mc;
      mc := mr;
    end;
  end;
end;

type
  TK9Arg = record
    inp, outp: PDouble;
    r0, r1: SizeInt;
  end;
  PK9Arg = ^TK9Arg;

function K9Worker(p: Pointer): PtrInt;
begin
  K9Rows(PK9Arg(p)^.inp, PK9Arg(p)^.outp, PK9Arg(p)^.r0, PK9Arg(p)^.r1);
  Result := 0;
end;

procedure RunK9(const v: string; reps: Integer);
var
  ga, gb, gt: PGrid;
  a, b, tmp: PDouble;
  arg: array[0..3] of TK9Arg;
  th: array[0..3] of TThreadID;
  i, j, it, t, r: Integer;
  k, n: SizeInt;
  t0: QWord;
  dt, s: Double;
begin
  { harnais commun de K9 (docs/K9.md) : grilles allouées une fois par processus, réinitialisées hors chrono }
  {$ifdef EXP}
  if v = 'natural_dyn' then
  begin
    RunK9Dyn(v, reps);
    Exit;
  end;
  {$endif}
  if v = 'natural' then
  begin
    New(ga);
    New(gb);
    for r := -Warmup to reps - 1 do
    begin
      for i := 0 to M9 - 1 do
        for j := 0 to M9 - 1 do
          ga^[i, j] := Double((i * 31 + j * 17) mod 1024) / 1024.0;
      gb^ := ga^; { le bord de b = bord initial }
      t0 := NowNs;
      for it := 1 to IT9 do
      begin
        K9Natural(ga^, gb^);
        gt := ga;
        ga := gb;
        gb := gt;
      end;
      dt := Secs(t0);
      s := 0;
      for i := 0 to M9 - 1 do
        for j := 0 to M9 - 1 do
          s := s + ga^[i, j];
      if r >= 0 then
        Emit('k9', v, '2048^2x4', r, dt, Format('%.16e', [s]));
    end;
    Exit;
  end;
  n := SizeInt(M9) * M9;
  a := AllocAligned(n * SizeOf(Double), 64);
  b := AllocAligned(n * SizeOf(Double), 64);
  for r := -Warmup to reps - 1 do
  begin
    for i := 0 to M9 - 1 do
      for j := 0 to M9 - 1 do
        a[SizeInt(i) * M9 + j] := Double((i * 31 + j * 17) mod 1024) / 1024.0;
    Move(a^, b^, n * SizeOf(Double));
    t0 := NowNs;
    for it := 1 to IT9 do
    begin
      if v = 'tuned' then
        K9Rows(a, b, 1, M9 - 1)
      else
      begin
        for t := 0 to 3 do
        begin
          arg[t].inp := a;
          arg[t].outp := b;
          arg[t].r0 := 1 + (M9 - 2) * t div 4;
          arg[t].r1 := 1 + (M9 - 2) * (t + 1) div 4;
          th[t] := BeginThread(@K9Worker, @arg[t]);
        end;
        for t := 0 to 3 do
          WaitForThreadTerminate(th[t], 0);
      end;
      tmp := a;
      a := b;
      b := tmp;
    end;
    dt := Secs(t0);
    s := 0;
    for k := 0 to n - 1 do
      s := s + a[k];
    if r >= 0 then
      Emit('k9', v, '2048^2x4', r, dt, Format('%.16e', [s]));
  end;
end;

{ ------------------------------------------------------------------ K10 }
const
  M10 = 1 shl 22;
  CAP10 = 1 shl 14;

type
  { naturel : file de Generics.Collections bornée par une section critique et deux événements de la RTL (FPC 3.2.2
    n'a ni file bloquante ni variable de condition dans sa RTL) }
  TU64Queue = specialize TQueue<QWord>;
  { optimisé : anneau SPSC (Lamport, copies locales des indices distants, à la Rigtorp), indices sur des lignes de
    128 octets ; accès ordinaires : FPC 3.2.2 n'a pas d'atomiques à ordre mémoire (ses barrières sont des appels à
    lfence / sfence / mfence) ; l'ordre TSO de x86-64 donne acquire / release aux mov, et FPC ne réordonne pas ces
    accès (vérifié dans le code produit) ; pas de pause (pas d'intrinsèque en FPC 3.2.2) }
  TSpsc = record
    writeIdx: SizeInt;
    pad0: array[0..14] of SizeInt;
    readIdx: SizeInt;
    pad1: array[0..14] of SizeInt;
    buf: array[0..CAP10 - 1] of QWord;
  end;
  PSpsc = ^TSpsc;

var
  bq: TU64Queue;
  bqLock: TRTLCriticalSection;
  bqNotEmpty, bqNotFull: PRTLEvent;
  sq: PSpsc;
  k10Sum: QWord;

function BqProd(p: Pointer): PtrInt;
var
  x: QWord;
begin
  for x := 1 to M10 do
  begin
    EnterCriticalSection(bqLock);
    while bq.Count = CAP10 do
    begin
      LeaveCriticalSection(bqLock);
      RTLEventWaitFor(bqNotFull);
      EnterCriticalSection(bqLock);
    end;
    bq.Enqueue(x);
    LeaveCriticalSection(bqLock);
    RTLEventSetEvent(bqNotEmpty);
  end;
  Result := 0;
end;

function BqCons(p: Pointer): PtrInt;
var
  k: SizeInt;
  s: QWord;
begin
  s := 0;
  for k := 1 to M10 do
  begin
    EnterCriticalSection(bqLock);
    while bq.Count = 0 do
    begin
      LeaveCriticalSection(bqLock);
      RTLEventWaitFor(bqNotEmpty);
      EnterCriticalSection(bqLock);
    end;
    s := s + bq.Dequeue;
    LeaveCriticalSection(bqLock);
    RTLEventSetEvent(bqNotFull);
  end;
  k10Sum := s;
  Result := 0;
end;

function SqProd(p: Pointer): PtrInt;
var
  w, rc: SizeInt;
  x: QWord;
begin
  w := 0;
  rc := 0;
  for x := 1 to M10 do
  begin
    while w - rc = CAP10 do
      rc := sq^.readIdx;
    sq^.buf[w and (CAP10 - 1)] := x;
    Inc(w);
    sq^.writeIdx := w;
  end;
  Result := 0;
end;

function SqCons(p: Pointer): PtrInt;
var
  rd, wc, k: SizeInt;
  s: QWord;
begin
  rd := 0;
  wc := 0;
  s := 0;
  for k := 1 to M10 do
  begin
    while rd = wc do
      wc := sq^.writeIdx;
    s := s + sq^.buf[rd and (CAP10 - 1)];
    Inc(rd);
    sq^.readIdx := rd;
  end;
  k10Sum := s;
  Result := 0;
end;

procedure RunK10(const v: string; reps: Integer);
var
  tuned: Boolean;
  r: Integer;
  tp, tc: TThreadID;
  t0: QWord;
  dt: Double;
begin
  tuned := v = 'tuned';
  for r := -Warmup to reps - 1 do
  begin
    if tuned then
    begin
      sq := AllocAligned(SizeOf(TSpsc), 128);
      FillChar(sq^, SizeOf(TSpsc), 0);
    end
    else
    begin
      bq := TU64Queue.Create;
      InitCriticalSection(bqLock);
      bqNotEmpty := RTLEventCreate;
      bqNotFull := RTLEventCreate;
    end;
    t0 := NowNs;
    if tuned then
    begin
      tc := BeginThread(@SqCons, nil);
      tp := BeginThread(@SqProd, nil);
    end
    else
    begin
      tc := BeginThread(@BqCons, nil);
      tp := BeginThread(@BqProd, nil);
    end;
    WaitForThreadTerminate(tp, 0);
    WaitForThreadTerminate(tc, 0);
    dt := Secs(t0);
    if r >= 0 then
      Emit('k10', v, '2^22', r, dt, IntToStr(k10Sum));
    if tuned then
      FreeAligned(sq)
    else
    begin
      RTLEventDestroy(bqNotEmpty);
      RTLEventDestroy(bqNotFull);
      DoneCriticalSection(bqLock);
      bq.Free;
    end;
  end;
end;

{ ------------------------------------------------------------------ main }
var
  k, v, p, w: string;
  reps: Integer;
begin
  if ParamCount < 3 then
  begin
    WriteLn(StdErr, 'usage: ms kernel variant reps [param]');
    Halt(1);
  end;
  DataDir := GetEnvironmentVariable('MS_DATA');
  if DataDir = '' then
    DataDir := '/opt/msdata';
  w := GetEnvironmentVariable('WARMUP');
  if w = '' then
    Warmup := 1
  else
    Warmup := StrToInt(w);
  k := ParamStr(1);
  v := ParamStr(2);
  reps := StrToInt(ParamStr(3));
  if ParamCount > 3 then
    p := ParamStr(4)
  else
    p := '';
  if k = 'k1' then RunK1(v, reps)
  else if k = 'k2' then RunK2(v, reps, p)
  else if k = 'k3' then RunK3(v, reps)
  else if k = 'k4' then RunK4(v, reps)
  else if k = 'k5' then RunK5(v, reps)
  else if k = 'k6' then RunK6(v, reps, p)
  else if k = 'k7' then RunK7(v, reps)
  else if k = 'k8' then RunK8(v, reps)
  else if k = 'k9' then RunK9(v, reps)
  else if k = 'k10' then RunK10(v, reps)
  else
  begin
    WriteLn(StdErr, 'noyau inconnu ', k);
    Halt(1);
  end;
end.
