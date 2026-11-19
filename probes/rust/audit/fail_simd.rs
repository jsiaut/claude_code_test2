use std::simd::f32x8;
fn main() { let a = f32x8::splat(1.0); println!("{:?}", a + a); }
