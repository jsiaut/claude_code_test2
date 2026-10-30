{.passC: "-mavx512f -mavx512cd".}
type M512i {.importc: "__m512i", header: "immintrin.h".} = object
proc mm512_set1_epi32(x: int32): M512i {.importc: "_mm512_set1_epi32", header: "immintrin.h".}
proc mm512_conflict_epi32(a: M512i): M512i {.importc: "_mm512_conflict_epi32", header: "immintrin.h".}
proc mm512_reduce_add_epi32(a: M512i): int32 {.importc: "_mm512_reduce_add_epi32", header: "immintrin.h".}
proc prefetch(p: pointer, rw, loc: cint) {.importc: "__builtin_prefetch", nodecl.}
{.emit: """typedef float v8f __attribute__((vector_size(32)));
static inline v8f v8f_splat(float x){ return (v8f){x,x,x,x,x,x,x,x}; }
static inline v8f v8f_add(v8f a, v8f b){ return a + b; }
static inline v8f v8f_mul(v8f a, v8f b){ return a * b; }
static inline float v8f_lane(v8f a, int i){ return a[i]; }""".}
type V8f {.importc: "v8f", nodecl.} = object
proc `+`(a, b: V8f): V8f {.importc: "v8f_add", nodecl.}
proc `*`(a, b: V8f): V8f {.importc: "v8f_mul", nodecl.}
proc splat(x: float32): V8f {.importc: "v8f_splat", nodecl.}
proc lane(a: V8f, i: cint): float32 {.importc: "v8f_lane", nodecl.}
var arr: array[128, int]
prefetch(addr arr[64], 0, 3)
let v = splat(2.0'f32)
echo "emit vector_size v8f lane0 = ", lane(v * v + v, 0)
echo "AVX-512 conflict reduce = ", mm512_reduce_add_epi32(mm512_conflict_epi32(mm512_set1_epi32(7)))
