#define _GNU_SOURCE
#include <pthread.h>
#include <sched.h>
#include <stdio.h>
int main(void){ cpu_set_t s; CPU_ZERO(&s); CPU_SET(0, &s);
  int r1 = pthread_setaffinity_np(pthread_self(), sizeof s, &s);
  int r2 = sched_setaffinity(0, sizeof s, &s);
  printf("affinity rc=%d,%d cpu=%d\n", r1, r2, sched_getcpu()); return 0; }
