/* Sonde (remarque sur Odin) : taille réellement occupée par un nœud de 24 octets, alloué directement (C) ou avec le
   surcroît de l'allocateur par défaut d'Odin (alignement 8 : 8 - 1 + 8 + 24 = 39 octets). glibc ajoute 8 octets
   d'en-tête au bloc utilisable. */
#include <malloc.h>
#include <stdio.h>
#include <stdlib.h>
int main(void) {
    size_t sizes[] = {24, 39};
    for (int i = 0; i < 2; i++) {
        void *p = calloc(1, sizes[i]);
        printf("demande %zu octets : utilisable %zu, bloc %zu\n", sizes[i], malloc_usable_size(p), malloc_usable_size(p) + 8);
        free(p);
    }
    return 0;
}
