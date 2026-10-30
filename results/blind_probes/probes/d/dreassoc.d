import ldc.attributes;
extern(C) @llvmFastMathFlag("reassoc") float sum_reassoc(const(float)[] v) { float s = 0; foreach (x; v) s += x; return s; }
extern(C) @fastmath float sum_fast(const(float)[] v) { float s = 0; foreach (x; v) s += x; return s; }
extern(C) float sum_plain(const(float)[] v) { float s = 0; foreach (x; v) s += x; return s; }
