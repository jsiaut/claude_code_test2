use std::arch::x86_64::*;
#[target_feature(enable = "avx512f")]
unsafe fn add(a: __m512, b: __m512) -> __m512 { _mm512_add_ps(a, b) }
#[target_feature(enable = "avx512vnni")]
unsafe fn dp(a: __m512i, b: __m512i, c: __m512i) -> __m512i { _mm512_dpbusd_epi32(a, b, c) }
fn main(){ if is_x86_feature_detected!("avx512f") { unsafe { let z = _mm512_setzero_ps(); let _ = add(z,z); } } println!("ok"); let _ = dp as unsafe fn(__m512i,__m512i,__m512i)->__m512i; }
