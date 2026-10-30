#include <threads.h>
#include <stdatomic.h>
#include <stdio.h>
#include <immintrin.h>
static atomic_int flag; static int data;
int prod(void *a){ (void)a; data = 42; atomic_thread_fence(memory_order_release); atomic_store_explicit(&flag, 1, memory_order_relaxed); return 0; }
int cons(void *a){ (void)a; while(!atomic_load_explicit(&flag, memory_order_relaxed)) _mm_pause(); atomic_thread_fence(memory_order_acquire); return data; }
int main(void){ thrd_t t1, t2; int r; thrd_create(&t2, cons, 0); thrd_create(&t1, prod, 0); thrd_join(t1, 0); thrd_join(t2, &r); printf("threads ok %d\n", r); return r != 42; }
