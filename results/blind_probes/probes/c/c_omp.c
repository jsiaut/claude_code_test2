#include <omp.h>
#include <stdio.h>
int main(void){ double s = 0; int nt = 0;
#pragma omp parallel for reduction(+:s)
  for (int i = 0; i < 100000000; i++) { s += 1.0 / (1.0 + i); }
#pragma omp parallel
  {
#pragma omp single
    nt = omp_get_num_threads();
  }
  printf("omp ok s=%.3f threads=%d\n", s, nt); return 0; }
