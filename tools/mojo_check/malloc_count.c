// Compteur d'allocations (LD_PRELOAD) : affiche à la sortie le nombre d'appels à malloc, calloc, realloc,
// posix_memalign, aligned_alloc et memalign. Sonde B4 de la remarque sur Mojo (docs/MOJO.md).
#define _GNU_SOURCE
#include <dlfcn.h>
#include <stdatomic.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
static atomic_long n_alloc;
static void *(*r_malloc)(size_t), *(*r_calloc)(size_t, size_t), *(*r_realloc)(void *, size_t);
static int (*r_pm)(void **, size_t, size_t);
static void *(*r_aa)(size_t, size_t), *(*r_ma)(size_t, size_t);
static char boot[1 << 16]; static size_t boot_used;
static void *boot_alloc(size_t n) { void *p = boot + boot_used; boot_used += (n + 15) & ~(size_t)15; return p; }
#define RESOLVE(v, name) do { if (!v) v = dlsym(RTLD_NEXT, name); } while (0)
void *malloc(size_t n) { if (!r_malloc) { static int in; if (in) return boot_alloc(n); in = 1; RESOLVE(r_malloc, "malloc"); in = 0; }
  atomic_fetch_add(&n_alloc, 1); return r_malloc(n); }
void *calloc(size_t a, size_t b) { if (!r_calloc) { static int in; if (in) return boot_alloc(a * b); in = 1; RESOLVE(r_calloc, "calloc"); in = 0; }
  atomic_fetch_add(&n_alloc, 1); return r_calloc(a, b); }
void *realloc(void *p, size_t n) { RESOLVE(r_realloc, "realloc"); atomic_fetch_add(&n_alloc, 1); return r_realloc(p, n); }
int posix_memalign(void **p, size_t a, size_t n) { RESOLVE(r_pm, "posix_memalign"); atomic_fetch_add(&n_alloc, 1); return r_pm(p, a, n); }
void *aligned_alloc(size_t a, size_t n) { RESOLVE(r_aa, "aligned_alloc"); atomic_fetch_add(&n_alloc, 1); return r_aa(a, n); }
void *memalign(size_t a, size_t n) { RESOLVE(r_ma, "memalign"); atomic_fetch_add(&n_alloc, 1); return r_ma(a, n); }
void free(void *p) { static void (*r_free)(void *); if ((char *)p >= boot && (char *)p < boot + sizeof boot) return;
  RESOLVE(r_free, "free"); r_free(p); }
__attribute__((destructor)) static void report(void) { char b[64]; int k = snprintf(b, sizeof b, "ALLOCS %ld\n", (long)n_alloc); write(2, b, k); }
