// Sonde de mode (v4, point 3 : docs/V4_EQUAL.md, 4) : « 1d » : tableau dynamique, « 2d » : tableau de tableaux (K9 naturel).
import std.stdio, std.conv;
void main(string[] args) {
    int n = to!int(args[2]);
    if (args[1] == "1d") {
        auto a = new double[n];
        a[] = 1.0;
        writeln(a[n]);
    } else {
        auto g = new double[][](4, n);
        foreach (r; g) r[] = 1.0;
        writeln(g[1][n]);
    }
}
