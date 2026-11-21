// Sonde de mode (v4, point 3 : docs/V4_EQUAL.md, 4) : « 1d » : std::vector, « 2d » : vecteur de vecteurs (K9 naturel).
#include <cstdio>
#include <cstdlib>
#include <vector>
int main(int, char **argv) {
    int n = std::atoi(argv[2]);
    if (argv[1][0] == '1') {
        std::vector<double> a(n, 1.0);
        std::printf("%g\n", a[n]);
    } else {
        std::vector<std::vector<double>> g(4, std::vector<double>(n, 1.0));
        std::printf("%g\n", g[1][n]);
    }
}
