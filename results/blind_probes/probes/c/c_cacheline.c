#include <stdio.h>
#include <unistd.h>
int main(void){
#ifdef __GCC_DESTRUCTIVE_SIZE
  printf("__GCC_DESTRUCTIVE_SIZE=%d __GCC_CONSTRUCTIVE_SIZE=%d\n", __GCC_DESTRUCTIVE_SIZE, __GCC_CONSTRUCTIVE_SIZE);
#else
  printf("no __GCC_DESTRUCTIVE_SIZE in C mode\n");
#endif
  printf("sysconf L1D line=%ld\n", sysconf(_SC_LEVEL1_DCACHE_LINESIZE)); return 0; }
