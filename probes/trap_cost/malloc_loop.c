#include <stdio.h>
#include <stdlib.h>
#include <time.h>
static void *volatile keep;
int main(void) {
    struct timespec a, b; clock_gettime(CLOCK_MONOTONIC, &a);
    for (int i = 0; i < 200000; i++) { void *p = malloc(64); keep = p; free(p); }
    clock_gettime(CLOCK_MONOTONIC, &b);
    printf("%.1f ns par paire malloc+free\n", ((b.tv_sec - a.tv_sec) * 1e9 + (b.tv_nsec - a.tv_nsec)) / 200000);
    return 0;
}
