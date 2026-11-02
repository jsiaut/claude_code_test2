#define _POSIX_C_SOURCE 200809L
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
static volatile long sink;
static void *body(void *p) { sink += (long)p; return NULL; }
static double now(void){struct timespec t;clock_gettime(CLOCK_MONOTONIC,&t);return t.tv_sec+t.tv_nsec*1e-9;}
static int cmp(const void *a, const void *b){double x=*(double*)a,y=*(double*)b;return x<y?-1:x>y;}
int main(void){ enum{N=2000}; static double t[N];
  for(int r=-500;r<N;r++){ double t0=now(); pthread_t th[4];
    for(long k=0;k<4;k++) pthread_create(&th[k],NULL,body,(void*)k);
    for(int k=0;k<4;k++) pthread_join(th[k],NULL);
    double t1=now(); if(r>=0) t[r]=(t1-t0)*1e6; }
  qsort(t,N,sizeof t[0],cmp);
  printf("C : 4 fils créés, lancés, attendus : médiane %.1f µs (p10 %.1f, p90 %.1f)\n", t[N/2], t[N/10], t[9*N/10]); return 0; }
