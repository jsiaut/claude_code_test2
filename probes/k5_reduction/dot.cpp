// Même boucle que K5 natural : réduction en ordre strict.
extern "C" __attribute__((noinline)) float dot(const float *a, const float *b, int n) {
    float s = 0;
    for (int i = 0; i < n; i++) s += a[i] * b[i];
    return s;
}
