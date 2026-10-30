pub fn sum(v: &[f32]) -> f32 { v.iter().fold(0.0f32, |a, &x| a.algebraic_add(x)) }
fn main(){ let v: Vec<f32> = (0..1000).map(|i| i as f32).collect(); println!("{}", sum(&v)); }
