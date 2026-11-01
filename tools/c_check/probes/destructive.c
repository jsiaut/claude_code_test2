/* Sonde : constante de ligne de cache en mode C (aucune dans ISO C23 ; __GCC_DESTRUCTIVE_SIZE est une macro prédéfinie) */
#include <stdio.h>
int main(void) {
#ifdef __GCC_DESTRUCTIVE_SIZE
    printf("__GCC_DESTRUCTIVE_SIZE=%d\n", __GCC_DESTRUCTIVE_SIZE);
#else
    printf("__GCC_DESTRUCTIVE_SIZE absent\n");
#endif
    return 0;
}
