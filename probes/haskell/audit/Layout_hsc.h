#ifndef __LAYOUT_HSC_H
#define __LAYOUT_HSC_H
#include <HsFFI.h>
#if __NHC__
#undef HsChar
#define HsChar int
#endif
#line 4 "Layout.hsc"
#include <stdint.h>
#line 5 "Layout.hsc"
struct s { uint8_t a; uint32_t b; double c; };
#line 6 "Layout.hsc"
struct __attribute__((packed)) p { uint8_t a; uint32_t b; };
#endif
