// Code produit, inspecté par run.sh (asm et IR, mêmes options que le banc : -O -C target-cpu=native).
#![crate_type = "lib"]
use std::sync::atomic::{AtomicU64, Ordering, fence};
#[unsafe(no_mangle)] pub fn st_release(a: &AtomicU64) { a.store(1, Ordering::Release) }
#[unsafe(no_mangle)] pub fn st_seqcst(a: &AtomicU64) { a.store(1, Ordering::SeqCst) }
#[unsafe(no_mangle)] pub fn add_relaxed(a: &AtomicU64) -> u64 { a.fetch_add(1, Ordering::Relaxed) }
#[unsafe(no_mangle)] pub fn spin(f: &AtomicU64) { while f.load(Ordering::Acquire) == 0 { std::hint::spin_loop() } fence(Ordering::SeqCst) }
#[unsafe(no_mangle)] pub fn axpy(a: &mut [f32], b: &[f32]) { for (x, y) in a.iter_mut().zip(b) { *x += 2.0 * y } }
#[unsafe(no_mangle)] pub fn idx_checked(a: &[f32], i: usize) -> f32 { a[i] }
#[unsafe(no_mangle)] pub fn idx_unchecked(a: &[f32], i: usize) -> f32 { unsafe { *a.get_unchecked(i) } }
#[unsafe(no_mangle)] pub fn hinted(x: u64) -> u64 { if x == 7 { std::hint::cold_path(); return x * 3 } x + 1 }
#[unsafe(no_mangle)] pub fn pf(p: *const i8) { unsafe { std::arch::x86_64::_mm_prefetch::<{ std::arch::x86_64::_MM_HINT_T0 }>(p) } }
const fn fib(n: u64) -> u64 { let (mut a, mut b, mut i) = (0u64, 1u64, 0); while i < n { let t = a + b; a = b; b = t; i += 1; } a }
#[unsafe(no_mangle)] pub fn fib60() -> u64 { const F: u64 = fib(60); F }
#[inline(never)] pub fn gsum<T: Copy + std::iter::Sum<T>>(x: &[T]) -> T { x.iter().copied().sum() }
#[unsafe(no_mangle)] pub fn use_both(a: &[f32], b: &[f64]) -> f64 { gsum(a) as f64 + gsum(b) }
#[unsafe(no_mangle)] pub fn sum_plain(a: &[f32]) -> f32 { a.iter().sum() }
#[unsafe(no_mangle)] pub fn sum_alg(a: &[f32]) -> f32 { a.iter().fold(0.0, |s, &x| s.algebraic_add(x)) }
