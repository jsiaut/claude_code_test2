// Contre-épreuve de la remarque sur D (docs/DLANG.md) : stencil naturel en vector<vector<double>>, avec et sans -fno-strict-aliasing.
#include <vector>
using V = std::vector<std::vector<double>>;
__attribute__((noinline)) void k9n(const V& a, V& b) {
    const int M = 2048;
    for (int i = 1; i < M - 1; i++)
        for (int j = 1; j < M - 1; j++)
            b[i][j] = 0.25 * (((a[i - 1][j] + a[i + 1][j]) + a[i][j - 1]) + a[i][j + 1]);
}
