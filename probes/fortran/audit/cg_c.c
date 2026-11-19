/* Témoin C pour E5 : la même boucle sur deux pointeurs, sans restrict (clang 23, -O3 -march=native). */
void axpy_c(float *a, const float *b, int n) { for (int i = 0; i < n; i++) a[i] += 2 * b[i]; }
