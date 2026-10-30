pub fn f(x: i32) -> i32 { if x > 0 { 1 } else { std::hint::cold_path(); 2 } }
fn main(){ println!("{}", f(3)); }
