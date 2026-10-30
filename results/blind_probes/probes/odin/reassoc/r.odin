package reassoc
@(export, fast_math={.Allow_Reassoc, .No_NaNs, .No_Infs, .No_Signed_Zeros, .Allow_Reciprocal, .Allow_Contract, .Approx_Func})
sum_fast :: proc "c" (v: []f32) -> f32 { s: f32 = 0; for x in v { s += x }; return s }
@(export)
sum_plain :: proc "c" (v: []f32) -> f32 { s: f32 = 0; for x in v { s += x }; return s }
