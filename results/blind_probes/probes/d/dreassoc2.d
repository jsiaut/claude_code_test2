import ldc.attributes;
extern(C) @llvmFastMathFlag("reassoc") @llvmFastMathFlag("nsz") float sum_rn(const(float)[] v) { float s = 0; foreach (x; v) s += x; return s; }
