use std::simd::f32x8;
pub fn add(a: f32x8, b: f32x8) -> f32x8 { a + b }
fn main(){ let a = f32x8::splat(1.0); println!("{:?}", add(a,a)); }
