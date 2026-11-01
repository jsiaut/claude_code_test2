// Sonde P2795 (remarque sur C++) : un tableau local non initialisé est-il mis à zéro en C++26 par g++ 16 ?
#include <cstdint>
#include <cstddef>
extern void use(uint32_t *);
uint32_t f(const uint8_t *p, size_t n) {
    uint32_t h[16];          // non initialisé, comme dans le K7 optimisé du banc
    for (size_t i = 0; i < n && i < 16; i++) h[i] = p[i];
    use(h);
    return h[0];
}
