// Audit de la grille (docs/V4_PLAN.md 2.1) : sonde exécutée de Chapel (chpl --fast, CHPL_COMM=none, qthreads).
// run.sh y ajoute le code produit (objdump des procédures exportées), une compilation vérifiée et les recherches.
use CTypes, BlockDist, MemDiagnostics, Prefetch, Time;
require "obs.h";
use Map;

record Part { var x, y, z: real(32); var m: int(8); }
record Inl { var n: uint(32); var a: 16*real(32); }
class Noisy { var name: string; proc deinit() { write("deinit(", name, ") "); } }

extern proc gettid(): c_int;       // observation seulement
extern proc sched_getcpu(): c_int; // observation seulement

proc gsum(x: ?t, y: t): t { return x + y; }
proc pfib(param n: int) param : int { if n < 2 then return n; else return pfib(n-1) + pfib(n-2); }

// procédures exportées, lues par objdump (run.sh)
var ga: atomic uint(64);
export proc st_release() { ga.write(1, memoryOrder.release); }
export proc st_seqcst() { ga.write(1, memoryOrder.seqCst); }
export proc add_relaxed(): uint(64) { return ga.fetchAdd(1, memoryOrder.relaxed); }
export proc fence_it() { atomicFence(); }
export proc pf(p: c_ptr(real(32))) { prefetch(p); }
export proc f20(): int { return pfib(20); }
export proc idx_ptr(p: c_ptr(real(32)), i: int): real(32) { return p[i]; }
var garr: [0..<64] real(32);
export proc idx_arr(i: int): real(32) { return garr[i]; }

proc main() {
  // A1
  var v: [0..<8] Part;
  for e in v do e = new Part(1.0, 2.0, 3.0, 4);
  writeln("CAP;A1;1;[exécutée] tableau de records : pas de ", (c_ptrTo(v[1]): c_uintptr - c_ptrTo(v[0]): c_uintptr),
          " o = c_sizeof(Part) ", c_sizeof(Part), " ; records stockés en ligne dans le tableau");
  // A7, A8
  writeln("CAP;A7;1;[exécutée] record (n: uint(32), a: 16*real(32)) : ", c_sizeof(Inl), " o, c_offsetof(Inl, \"a\") = ",
          c_offsetof(Inl, "a"), " (tuple homogène en ligne)");
  writeln("CAP;A8;1;[exécutée] int(8)/int(16)/real(32) : ", numBytes(int(8)), "/", numBytes(int(16)), "/", numBytes(real(32)),
          " o ; [0..<1000] int(8) occupe ", 1000 * numBytes(int(8)), " o");
  // B1
  write("CAP;B1;1;[exécutée] pas de ramasse-miettes (owned, shared, unmanaged) : ");
  { var a = new owned Noisy("a"); { var b = new owned Noisy("b"); } write("fin-portée "); }
  writeln("; destruction déterministe à la sortie de portée");
  // B4 (½ : tableaux locaux et tâches allouent implicitement)
  startVerboseMem(); stopVerboseMem();
  const m0 = memoryUsed();
  var loc: [0..<1000] real;
  loc[0] = 1.0;
  const m1 = memoryUsed();
  writeln("CAP;B4;0.5;[exécutée] memoryUsed (MemDiagnostics) : un tableau local [0..<1000] real alloue ", m1 - m0,
          " o sur le tas, sans new ni appel explicite ; les tâches (begin, coforall) allouent aussi leur pile");
  // B5
  var buf: [0..<8] uint(32);
  var p = c_ptrTo(buf[0]);
  p[3] = 42;
  var bp = p: c_ptr(uint(8));
  ((bp + 16): c_ptr(void): c_ptr(uint(32))).deref() = 7;
  writeln("CAP;B5;1;[exécutée] c_ptr(uint(32)) : p[3] = 42 -> buf[3] = ", buf[3], " ; écriture par décalage d'octets -> buf[4] = ", buf[4]);
  // C5
  var ids: [0..<4000] c_int;
  forall i in 0..<4000 do ids[i] = gettid();
  var seen: map(c_int, int);
  for t in ids do seen.addOrReplace(t, 1);
  const r = + reduce [i in 0..<1000000] i;
  writeln("CAP;C5;1;[exécutée] forall sur ", seen.size, " fils distincts (gettid), + reduce = ", r, " (attendu 499999500000)");
  // D1
  var parts: [0..<4] uint(64);
  var tids: [0..<4] c_int;
  coforall t in 0..<4 with (ref parts, ref tids) {
    var s: uint(64) = 0;
    for i in t*1000..<(t+1)*1000 do s += i: uint(64);
    parts[t] = s; tids[t] = gettid();
  }
  var seen2: map(c_int, int);
  for t in tids do seen2.addOrReplace(t, 1);
  writeln("CAP;D1;1;[exécutée] coforall : 4 tâches sur ", seen2.size, " fils distincts (gettid), somme ", + reduce parts, " (attendu 7998000)");
  // D4 (½ : placement par l'exécutif)
  var cpus: [0..<4] c_int;
  coforall t in 0..<4 with (ref cpus) { cpus[t] = sched_getcpu(); }
  writeln("FACT;D4;coforall de 4 tâches : processeurs ", cpus, " (placement décidé par l'exécutif qthreads)");
  // E7
  writeln("FACT;E7;proc pfib(param n) param, évaluée à la compilation : pfib(20) = ", pfib(20), " ; gsum générique : ",
          gsum(1.5: real(32), 2.5: real(32)), " (real(32)), ", gsum(1.5, 2.25), " (real(64))");
  // F1
  const n = 3 + 0 * here.id;
  var M: [1..n, 1..4] real(32);
  writeln("CAP;F1;1;[exécutée] [1..n, 1..4] real(32) avec n = ", n, " connu à l'exécution : &M[2,1] - &M[1,4] = ",
          (c_ptrTo(M[2,1]): c_uintptr - c_ptrTo(M[1,4]): c_uintptr), " o (contigu, par lignes) ; domaines et tranches multidimensionnels");
  // F2
  const D = blockDist.createDomain({1..100});
  var B: [D] int;
  forall i in D with (ref B) do B[i] = here.id;
  writeln("CAP;F2;1;[exécutée] blockDist.createDomain({1..100}) : tableau distribué sur ", D.targetLocales().size,
          " locale(s) (CHPL_COMM=none : une seule ici), propriétaire de B[100] = locale ", B[100], " ; locales, on, distributions Block, Cyclic, Stencil");
  // F3
  var u = max(uint(32));
  u += 1;
  var b250: uint(8) = 250;
  b250 += 10;
  writeln("CAP;F3;1;[exécutée] max(uint(32)) + 1 = ", u, ", uint(8) 250 + 10 = ", b250, " (non signés enveloppants ; int(N) de largeur fixe)");
}
