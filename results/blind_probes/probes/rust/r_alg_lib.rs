#[unsafe(no_mangle)]
pub fn sum_alg(v: &[f32]) -> f32 { v.iter().fold(0.0f32, |a, &x| a.algebraic_add(x)) }
#[unsafe(no_mangle)]
pub fn sum_plain(v: &[f32]) -> f32 { v.iter().fold(0.0f32, |a, &x| a + x) }
