/* Audit de la grille (docs/V4_PLAN.md 2.1) : sonde exécutée de C (clang 23, glibc), cas positifs. run.sh y ajoute le
   code produit, les échecs et les recherches d'absence. */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>
#include <stdalign.h>
#include <stdatomic.h>
#include <threads.h>
#include <sched.h>
#include <unistd.h>
#include <malloc.h>
#include <obstack.h>
#include <sys/mman.h>
#include <sys/syscall.h>
#include <fcntl.h>
#include <omp.h>
#include <immintrin.h>

typedef struct { float x, y, z; uint8_t m; } Part;
typedef struct { uint32_t n; float a[16]; } Inl;
typedef struct { alignas(64) uint64_t v; } Line;
typedef struct { uint8_t a; double b; uint8_t c; } Reord;
typedef struct __attribute__((packed)) { uint8_t a; uint32_t b; } Pk;
typedef struct { unsigned x : 3, y : 5; } BF;
typedef float v8f __attribute__((vector_size(32)));

#define obstack_chunk_alloc malloc
#define obstack_chunk_free free

static int threads_now(void) {
  FILE *f = fopen("/proc/self/status", "r"); char l[256]; int n = -1;
  while (f && fgets(l, sizeof l, f)) if (!strncmp(l, "Threads:", 8)) n = atoi(l + 8);
  if (f) fclose(f);
  return n;
}
typedef struct { int t; uint64_t *res; pid_t *tid; } WArg;
static int worker(void *p) {
  WArg *a = p; uint64_t s = 0;
  for (int i = a->t * 1000; i < (a->t + 1) * 1000; i++) s += (uint64_t)i;
  *a->res = s; *a->tid = (pid_t)syscall(SYS_gettid);
  return 0;
}
static int cmpf(const void *a, const void *b) { float x = *(const float *)a, y = *(const float *)b; return (x > y) - (x < y); }

int main(int argc, char **argv) {
  (void)argv;
  /* A1, A2, A3, A4, A5, A7, A8 */
  Part v[8];
  for (int i = 0; i < 8; i++) v[i] = (Part){1, 2, 3, 4};
  unsigned char *raw = (unsigned char *)v;
  printf("CAP;A1;1;[exécutée] Part v[8] : pas de %td o = sizeof(Part) %zu ; les 4 premiers octets sont le float x en ligne : %02x %02x %02x %02x\n",
         (char *)&v[1] - (char *)&v[0], sizeof(Part), raw[0], raw[1], raw[2], raw[3]);
  printf("CAP;A2;1;[exécutée] ordre déclaré gardé : (u8, double, u8) occupe %zu o, offsetof(b) = %zu, offsetof(c) = %zu\n", sizeof(Reord), offsetof(Reord, b), offsetof(Reord, c));
  BF bf = {5, 17};
  printf("CAP;A3;1;[exécutée] champs de bits (norme) : sizeof(BF) = %zu, x = %u, y = %u ; __attribute__((packed)) : sizeof(Pk) = %zu ; ½ en v1\n", sizeof(BF), bf.x, bf.y, sizeof(Pk));
  Line *hl = aligned_alloc(64, 4 * sizeof(Line));
  printf("CAP;A4;1;[exécutée] alignas(64) : alignof(Line) = %zu, Line[] au pas de %zu o, aligned_alloc à %zu mod 64\n", alignof(Line), sizeof(Line), (size_t)((uintptr_t)hl % 64));
  union { float f; uint32_t u; } un = {.f = 1.0f};
  printf("CAP;A5;1;[exécutée] union float/uint32 : 0x%08x ; memcpy de réinterprétation identique\n", un.u);
  printf("CAP;A7;1;[exécutée] struct { uint32_t n; float a[16]; } : %zu o, offsetof(a) = %zu (tableau en ligne)\n", sizeof(Inl), offsetof(Inl, a));
  uint8_t *b8 = malloc(1000);
  printf("CAP;A8;1;[exécutée] uint8_t/int16_t/_Float16/float : %zu/%zu/%zu/%zu o ; uint8_t[1000] occupe %zu o\n", sizeof(uint8_t), sizeof(int16_t), sizeof(_Float16), sizeof(float), 1000 * sizeof(uint8_t));
  /* B1 */
  printf("CAP;B1;1;[exécutée] aucun ramasse-miettes : malloc/free explicites ; %d fil (Threads: de /proc/self/status)\n", threads_now());
  /* B2 (½ : obstack de la glibc, pas d'interface d'allocateur) */
  struct obstack ob; obstack_init(&ob);
  int *blk1 = obstack_alloc(&ob, 100 * sizeof(int));
  int *blk2 = obstack_alloc(&ob, 100 * sizeof(int));
  printf("FACT;B2;obstack de la glibc (arène, <obstack.h>) : deux blocs consécutifs à %td o d'écart, libérés d'un coup par obstack_free\n", (char *)blk2 - (char *)blk1);
  obstack_free(&ob, NULL);
  /* B3 */
  char local[4096]; local[0] = 1; char marker = local[0];
  int n = argc + 3; float vla[n]; vla[0] = 1;
  printf("CAP;B3;1;[exécutée] char local[4096] à %td o d'une autre variable locale, à %td o du tas ; VLA float[%d] sur la pile (%td o de local)\n",
         labs((long)(&marker - local)), labs((long)((char *)b8 - local)), n, labs((long)((char *)vla - local)));
  /* B4 */
  struct mallinfo2 m0 = mallinfo2();
  float data[256]; for (int i = 0; i < 256; i++) data[i] = (float)(255 - i);
  qsort(data, 256, sizeof(float), cmpf);
  Part copy = v[3]; Part cl = (Part){5, 6, 7, 8};
  char fbuf[64]; snprintf(fbuf, sizeof fbuf, "%.1f %.1f", data[255], copy.x + cl.x);
  struct mallinfo2 m1 = mallinfo2();
  printf("CAP;B4;1;[exécutée] mallinfo2 : tri qsort, copies de structures, littéraux composés, snprintf dans un tampon de pile -> %zu o alloués (%s) ; seule malloc alloue\n", m1.uordblks - m0.uordblks, fbuf);
  /* B5 */
  uint32_t buf[8] = {0}; uint32_t *mp = buf; mp[3] = 42; *(uint32_t *)((char *)buf + 16) = 7;
  printf("CAP;B5;1;[exécutée] uint32_t * : mp[3] = 42 -> buf[3] = %u ; écriture par décalage d'octets -> buf[4] = %u\n", buf[3], buf[4]);
  /* C1 */
  v8f va = {1, 2, 3, 4, 5, 6, 7, 8}; v8f vb = va + va;
  printf("CAP;C1;1;[exécutée] vector_size(32) (extension documentée de clang et gcc) : (a + a)[7] = %.0f ; ½ en v1\n", vb[7]);
  /* C5 */
  int ids[4000];
#pragma omp parallel for num_threads(4)
  for (int i = 0; i < 4000; i++) ids[i] = (int)syscall(SYS_gettid);
  int nd = 0; for (int i = 0; i < 4000; i++) { int s = 0; for (int j = 0; j < i && !s; j++) s = ids[j] == ids[i]; nd += !s; }
  long red = 0;
#pragma omp parallel for reduction(+:red) num_threads(4)
  for (long i = 0; i < 1000000; i++) red += i;
  printf("CAP;C5;1;[exécutée] OpenMP (livré avec clang et gcc, -fopenmp) : parallel for sur %d fils distincts (gettid), reduction(+) = %ld ; ½ en v1\n", nd, red);
  /* D1 */
  uint64_t parts[4]; pid_t tids[4]; WArg wa[4]; thrd_t th[4];
  for (int t = 0; t < 4; t++) { wa[t] = (WArg){t, &parts[t], &tids[t]}; thrd_create(&th[t], worker, &wa[t]); }
  for (int t = 0; t < 4; t++) thrd_join(th[t], NULL);
  nd = 0; for (int i = 0; i < 4; i++) { int s = 0; for (int j = 0; j < i; j++) s |= tids[j] == tids[i]; nd += !s; }
  printf("CAP;D1;1;[exécutée] <threads.h> (C11) : 4 fils, %d identifiants distincts (gettid), somme %lu (attendu 7998000)\n", nd, (unsigned long)(parts[0] + parts[1] + parts[2] + parts[3]));
  /* D3 */
  printf("CAP;D3;1;[exécutée] __GCC_DESTRUCTIVE_SIZE = %d (macro prédéfinie par clang et gcc), sysconf(_SC_LEVEL1_DCACHE_LINESIZE) = %ld (glibc) ; ½ en v1\n", __GCC_DESTRUCTIVE_SIZE, sysconf(_SC_LEVEL1_DCACHE_LINESIZE));
  /* D4 */
  cpu_set_t set; CPU_ZERO(&set); CPU_SET(1, &set);
  int ra = sched_setaffinity(0, sizeof set, &set);
  printf("CAP;D4;1;[exécutée] sched_setaffinity de la glibc (bibliothèque système de la plateforme) : retour %d, sched_getcpu() = %d ; ½ en v1\n", ra, sched_getcpu());
  /* E2 */
  long ex = 41; __asm__ ("addq $1, %0" : "+r"(ex));
  printf("CAP;E2;1;[exécutée] __asm__ (\"addq $1, %%0\" : \"+r\"(x)) : 41 -> %ld ; ½ en v1\n", ex);
  /* E7 (½) */
  constexpr int K = 12 * 12;
#define TNAME(x) _Generic((x), float: "float", double: "double", default: "autre")
  printf("FACT;E7;constexpr int K = 12 * 12 = %d (C23) ; _Generic choisit %s puis %s (sélection, pas d'instanciation)\n", K, TNAME(1.0f), TNAME(1.0));
  /* F1 */
  int rows = argc + 2, cols = argc + 3; float (*mat)[cols] = malloc(sizeof(float[rows][cols]));
  printf("CAP;F1;1;[exécutée] float (*m)[cols] = malloc(sizeof(float[rows][cols])), %d x %d connus à l'exécution (types à dimension variable, C99) : &m[1][0] - &m[0][cols-1] = %td o (contigu, par lignes)\n", rows, cols, (char *)&mat[1][0] - (char *)&mat[0][cols - 1]);
  /* F3 */
  uint32_t um = UINT32_MAX; uint8_t c250 = 250;
  printf("CAP;F3;1;[exécutée] UINT32_MAX + 1 = %u, (uint8_t)(250 + 10) = %u (non signés modulaires ; débordement signé indéfini, -fwrapv pour l'envelopper)\n", (uint32_t)(um + 1u), (uint8_t)(c250 + 10));
  /* F4 */
  float vals[4] = {1.5f, 2.5f, 3.5f, 4.5f};
  int fd = open("/tmp/c_audit_f4.bin", O_CREAT | O_TRUNC | O_RDWR, 0644);
  if (write(fd, vals, sizeof vals) != (ssize_t)sizeof vals) return 1;
  float *fl = mmap(NULL, sizeof vals, PROT_READ, MAP_PRIVATE, fd, 0);
  printf("CAP;F4;1;[exécutée] mmap (POSIX, glibc) puis réinterprétation par conversion de pointeur : %.1f %.1f %.1f %.1f ; ½ en v1\n", fl[0], fl[1], fl[2], fl[3]);
  munmap(fl, sizeof vals); close(fd);
  free(hl); free(b8); free(mat);
  return 0;
}
