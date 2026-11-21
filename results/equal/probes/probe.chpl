// Sonde de mode (v4, point 3 : docs/V4_EQUAL.md, 4) : « 1d » : tableau, « 2d » : tableau sur domaine 2D (K9 naturel).
config const which = "1d";
config const n = 1000;
proc main() {
  if which == "1d" {
    var a: [0..#n] real = 1.0;
    writeln(a[n]);
  } else {
    var g: [0..3, 0..#n] real = 1.0;
    writeln(g[1, n]);
  }
}
