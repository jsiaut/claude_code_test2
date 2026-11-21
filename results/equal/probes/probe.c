// Sonde de mode (v4, point 3 : docs/V4_EQUAL.md, 4) : lecture hors des bornes ; « 1d » : tableau alloué (pointeur,
// comme les noyaux naturels du C), « 2d » : rangées de taille connue (double (*)[M], comme k9_natural).
#include <stdio.h>
#include <stdlib.h>
#define M 64
int main(int argc, char **argv) {
    int n = atoi(argv[2]);
    if (argv[1][0] == '1') {
        double *a = malloc((size_t)n * sizeof(double));
        for (int i = 0; i < n; i++) a[i] = 1.0;
        printf("%g\n", a[n]);
    } else {
        double (*g)[M] = malloc(4 * sizeof *g);
        for (int i = 0; i < 4; i++) for (int j = 0; j < M; j++) g[i][j] = 1.0;
        printf("%g\n", g[1][n]);
    }
    return 0;
}
