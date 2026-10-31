// E5 : même noyau avec for : noalias sans foreach ?
proc axpy(ref y: [] real, const ref x: [] real, a: real) {
  for i in y.domain do y[i] += a * x[i];
}
proc main() { var x, y: [0..<1000] real = 1.0; axpy(y, x, 2.0); writeln(y[10]); }
