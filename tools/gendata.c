// gendata.c — génère les jeux de données binaires décrits dans docs/SPEC.md.
// Déterministe : PRNG xorshift32 (Marsaglia 2003) avec graines fixes.
// Usage : gendata <répertoire>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static uint32_t st;
static inline uint32_t rnd(void) {
    uint32_t x = st;
    x ^= x << 13;
    x ^= x >> 17;
    x ^= x << 5;
    return st = x;
}
// flottant uniforme dans [0,1) exactement représentable sur 24 bits
static inline float rf(void) { return (float)(rnd() >> 8) * (1.0f / 16777216.0f); }

static const char *dir;
static void put(const char *name, const void *p, size_t bytes) {
    char path[4096];
    snprintf(path, sizeof path, "%s/%s", dir, name);
    FILE *f = fopen(path, "wb");
    if (!f || fwrite(p, 1, bytes, f) != bytes) { perror(path); exit(1); }
    fclose(f);
    fprintf(stderr, "wrote %s (%zu bytes)\n", path, bytes);
}

enum { N1 = 1 << 22, N4 = 1 << 24, N5 = 2048, N6 = 1 << 24, N7 = 1 << 24 };

int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "usage: gendata DIR\n"); return 1; }
    dir = argv[1];

    // K1 : particules AoS (16 f32) + permutation de Fisher–Yates
    st = 0x01234567u;
    float *pa = malloc((size_t)N1 * 16 * sizeof(float));
    for (size_t i = 0; i < (size_t)N1 * 16; i++) pa[i] = rf();
    put("k1_particles.f32", pa, (size_t)N1 * 16 * sizeof(float));
    free(pa);
    uint32_t *perm = malloc((size_t)N1 * 4);
    for (uint32_t i = 0; i < N1; i++) perm[i] = i;
    for (uint32_t i = N1 - 1; i > 0; i--) {
        uint32_t j = rnd() % (i + 1);
        uint32_t t = perm[i]; perm[i] = perm[j]; perm[j] = t;
    }
    put("k1_perm.u32", perm, (size_t)N1 * 4);
    free(perm);

    // K2 : cycles de Sattolo, un nœud par ligne de cache (16 u32)
    static const size_t sizes[] = {16u << 10, 64u << 10, 256u << 10, 512u << 10,
                                   2u << 20, 8u << 20, 16u << 20, 32u << 20,
                                   64u << 20, 256u << 20};
    for (size_t s = 0; s < sizeof sizes / sizeof sizes[0]; s++) {
        size_t S = sizes[s], nodes = S / 64;
        st = 0x9E3779B9u ^ (uint32_t)S;
        uint32_t *p = malloc(nodes * 4);
        for (size_t i = 0; i < nodes; i++) p[i] = (uint32_t)i;
        for (size_t i = nodes - 1; i > 0; i--) {   // Sattolo : j dans [0, i)
            size_t j = rnd() % i;
            uint32_t t = p[i]; p[i] = p[j]; p[j] = t;
        }
        uint32_t *a = calloc(S / 4, 4);
        for (size_t k = 0; k < nodes; k++) a[16 * k] = 16u * p[k];
        char name[64];
        snprintf(name, sizeof name, "k2_chase_%zu.u32", S);
        put(name, a, S);
        free(a); free(p);
    }

    // K4 : octets aléatoires (bits de poids fort)
    st = 0x0ABCDEF1u;
    uint8_t *b4 = malloc(N4);
    for (size_t i = 0; i < N4; i++) b4[i] = (uint8_t)(rnd() >> 24);
    put("k4_bytes.u8", b4, N4);
    free(b4);

    // K5 : deux vecteurs f32 de 2048 éléments
    st = 0x00005EEDu;
    float a5[N5], b5[N5];
    for (int i = 0; i < N5; i++) { a5[i] = rf(); b5[i] = rf(); }
    put("k5_a.f32", a5, sizeof a5);
    put("k5_b.f32", b5, sizeof b5);

    // K6 : colonnes lineitem simplifiées
    st = 0x0C0FFEE1u;
    int32_t *sd = malloc(N6 * 4), *pr = malloc(N6 * 4);
    uint8_t *q = malloc(N6), *d = malloc(N6), *t = malloc(N6), *rfl = malloc(N6), *ls = malloc(N6);
    for (size_t i = 0; i < N6; i++) {
        sd[i] = 8035 + (int32_t)(rnd() % 2557u);
        q[i] = (uint8_t)(1 + rnd() % 50u);
        d[i] = (uint8_t)(rnd() % 11u);
        t[i] = (uint8_t)(rnd() % 9u);
        rfl[i] = (uint8_t)(rnd() % 3u);
        ls[i] = (uint8_t)(rnd() % 2u);
        pr[i] = 100 + (int32_t)(rnd() % 49901u);
    }
    put("k6_shipdate.i32", sd, N6 * 4);
    put("k6_quantity.u8", q, N6);
    put("k6_discount.u8", d, N6);
    put("k6_tax.u8", t, N6);
    put("k6_returnflag.u8", rfl, N6);
    put("k6_linestatus.u8", ls, N6);
    put("k6_extendedprice.i32", pr, N6 * 4);
    free(sd); free(pr); free(q); free(d); free(t); free(rfl); free(ls);

    // K7 : clés brouillées (bijection multiplicative de 2^20 valeurs) + valeurs
    st = 0x00007777u;
    uint32_t *k7 = malloc(N7 * 4), *v7 = malloc(N7 * 4);
    for (size_t i = 0; i < N7; i++) {
        uint32_t r = rnd();
        k7[i] = (r % 1048576u) * 2654435761u;
        v7[i] = rnd() % 1000u;
    }
    put("k7_keys.u32", k7, N7 * 4);
    put("k7_vals.u32", v7, N7 * 4);
    free(k7); free(v7);
    return 0;
}
