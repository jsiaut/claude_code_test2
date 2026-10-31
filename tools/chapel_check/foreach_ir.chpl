// E5 : IR de foreach (llvm.loop.parallel_accesses) et noalias entre tableaux distincts
proc axpy(ref y: [] real, const ref x: [] real, a: real) {
  foreach i in y.domain do y[i] += a * x[i];
}
proc main() { var x, y: [0..<1000] real = 1.0; axpy(y, x, 2.0); writeln(y[10]); }
