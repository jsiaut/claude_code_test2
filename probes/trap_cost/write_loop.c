#include <stdio.h>
#include <stdlib.h>
#include <time.h>
volatile long target;
int main(void) {
    printf("%p\n", (void *)&target); fflush(stdout);
    struct timespec a, b; clock_gettime(CLOCK_MONOTONIC, &a);
    for (long i = 0; i < 200000; i++) target = i;
    clock_gettime(CLOCK_MONOTONIC, &b);
    printf("%.1f ns par écriture\n", ((b.tv_sec - a.tv_sec) * 1e9 + (b.tv_nsec - a.tv_nsec)) / 200000);
    return 0;
}
