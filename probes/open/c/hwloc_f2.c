/* v4, point 6 (docs/V4_OPEN.md, 4) : sonde de F2 avec hwloc 2.10.0 (paquet Ubuntu libhwloc-dev).
   Lie une zone de mémoire au premier nœud NUMA, relit la politique et l'emplacement réel des pages,
   puis lie le fil courant à un cœur et relit le cœur où il s'exécute. Compilée en C (clang 23) et en C++ (g++ 16). */
#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif
#include <hwloc.h>
#include <stdio.h>
#include <string.h>
#include <sched.h>

static const char *pol_name(hwloc_membind_policy_t p) {
    switch (p) {
    case HWLOC_MEMBIND_DEFAULT: return "DEFAULT";
    case HWLOC_MEMBIND_FIRSTTOUCH: return "FIRSTTOUCH";
    case HWLOC_MEMBIND_BIND: return "BIND";
    case HWLOC_MEMBIND_INTERLEAVE: return "INTERLEAVE";
    case HWLOC_MEMBIND_NEXTTOUCH: return "NEXTTOUCH";
    default: return "MIXED";
    }
}

int main(void) {
    hwloc_topology_t t;
    hwloc_topology_init(&t);
    hwloc_topology_load(t);
    int nn = hwloc_get_nbobjs_by_type(t, HWLOC_OBJ_NUMANODE);
    int nc = hwloc_get_nbobjs_by_type(t, HWLOC_OBJ_CORE);
    hwloc_obj_t node = hwloc_get_obj_by_type(t, HWLOC_OBJ_NUMANODE, 0);
    const struct hwloc_topology_support *s = hwloc_topology_get_support(t);
    size_t len = (size_t)1 << 22;
    void *p = hwloc_alloc_membind(t, len, node->nodeset, HWLOC_MEMBIND_BIND,
                                  HWLOC_MEMBIND_BYNODESET | HWLOC_MEMBIND_STRICT);
    if (!p) { printf("RESULT;F2;échec hwloc_alloc_membind\n"); return 1; }
    memset(p, 1, len);
    hwloc_bitmap_t ns = hwloc_bitmap_alloc(), loc = hwloc_bitmap_alloc();
    hwloc_membind_policy_t pol;
    int r1 = hwloc_get_area_membind(t, p, len, ns, &pol, HWLOC_MEMBIND_BYNODESET);
    int r2 = hwloc_get_area_memlocation(t, p, len, loc, HWLOC_MEMBIND_BYNODESET);
    char b1[64], b2[64];
    hwloc_bitmap_snprintf(b1, sizeof b1, ns);
    hwloc_bitmap_snprintf(b2, sizeof b2, loc);
    hwloc_cpuset_t cs = hwloc_bitmap_alloc(), got = hwloc_bitmap_alloc();
    hwloc_bitmap_only(cs, 1);
    int r3 = hwloc_set_cpubind(t, cs, HWLOC_CPUBIND_THREAD);
    int r4 = hwloc_get_cpubind(t, got, HWLOC_CPUBIND_THREAD);
    char b3[64];
    hwloc_bitmap_snprintf(b3, sizeof b3, got);
    printf("RESULT;F2;%d nœud(s) NUMA, %d cœurs ; zone de 4 Mio par hwloc_alloc_membind(BIND, STRICT) au nœud 0 : "
           "politique relue %s (%d), nœuds %s, pages sur %s (%d) ; set_membind %s, get_area_memlocation %s ; "
           "fil lié au PU 1 (%d) : cpuset relu %s (%d), sched_getcpu = %d\n",
           nn, nc, pol_name(pol), r1, b1, b2, r2,
           s->membind->set_thisthread_membind ? "pris en charge" : "absent",
           s->membind->get_area_memlocation ? "pris en charge" : "absent",
           r3, b3, r4, sched_getcpu());
    hwloc_free(t, p, len);
    hwloc_topology_destroy(t);
    return 0;
}
