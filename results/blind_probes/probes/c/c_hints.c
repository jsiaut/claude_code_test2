#include <stdio.h>
__attribute__((cold, noinline)) static int slow(int x) { return x * 3; }
int f(int x, const int *p) {
  __builtin_prefetch(p + 64, 0, 3);
  if (__builtin_expect(x > 0, 1)) return p[0];
  return slow(x); }
int main(void){ int a[128] = {7}; printf("hints ok %d\n", f(1, a)); return 0; }
