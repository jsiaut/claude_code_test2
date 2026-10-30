use std::arch::x86_64::{_mm_prefetch, _MM_HINT_T0};
pub fn f(p: &[u8]) { unsafe { _mm_prefetch::<_MM_HINT_T0>(p.as_ptr() as *const i8); } }
fn main(){ let v = vec![0u8; 64]; f(&v); println!("ok"); }
