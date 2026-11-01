/* Sonde : #pragma clang fp reassociate(on) agit-il localement ? Deux sommes identiques, l'une sous le pragma. */
float sum_strict(const float *a, int n) {
    float s = 0;
    for (int i = 0; i < n; i++) s += a[i];
    return s;
}
float sum_reassoc(const float *a, int n) {
#pragma clang fp reassociate(on)
    float s = 0;
    for (int i = 0; i < n; i++) s += a[i];
    return s;
}
