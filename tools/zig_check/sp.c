#include <pthread.h>
#include <stdio.h>
#include <time.h>
static void *work(void *p) { (*(unsigned long *)p)++; return NULL; }
static double now(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return t.tv_sec * 1e6 + t.tv_nsec * 1e-3; }
int main(void) {
    unsigned long cnt[4] = {0};
    double best = 1e9, tot = 0;
    for (int rep = 0; rep < 200; rep++) {
        double t0 = now();
        pthread_t th[4];
        for (int t = 0; t < 4; t++) pthread_create(&th[t], NULL, work, &cnt[t]);
        for (int t = 0; t < 4; t++) pthread_join(th[t], NULL);
        double dt = (now() - t0) / 4;
        if (rep >= 10) { if (dt < best) best = dt; tot += dt; }
    }
    printf("par thread : min %.1f us, moyenne %.1f us (%lu)\n", best, tot / 190, cnt[0]);
}
