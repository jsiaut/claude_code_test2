/* F2, contre-épreuve : allocateur OpenMP avec le trait de partition entrelacée ; politique relue par get_mempolicy. */
#define _GNU_SOURCE
#include <omp.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/syscall.h>
int main(void) {
  omp_alloctrait_t tr[1] = {{omp_atk_partition, omp_atv_interleaved}};
  omp_allocator_handle_t a = omp_init_allocator(omp_default_mem_space, 1, tr);
  size_t n = 1 << 22;
  char *p = omp_alloc(n, a);
  if (!p) { printf("omp_alloc NULL (allocator %lu)\n", (unsigned long)a); return 0; }
  memset(p, 1, n);
  int mode = -1;
  long r = syscall(SYS_get_mempolicy, &mode, NULL, 0, p + 4096, 2 /* MPOL_F_ADDR */);
  printf("allocator=%lu ptr=%p get_mempolicy=%ld mode=%d (3 = MPOL_INTERLEAVE)\n", (unsigned long)a, (void*)p, r, mode);
  omp_free(p, a);
  return 0;
}
