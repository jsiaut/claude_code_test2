use std::arch::x86_64::*;
#[inline(never)]
pub fn pf_et0(p: *const i8) { unsafe { _mm_prefetch::<_MM_HINT_ET0>(p) } }
#[inline(never)]
pub fn pf_t0(p: *const i8) { unsafe { _mm_prefetch::<_MM_HINT_T0>(p) } }
#[inline(never)]
pub fn pf_et1(p: *const i8) { unsafe { _mm_prefetch::<_MM_HINT_ET1>(p) } }
