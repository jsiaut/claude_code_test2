pub fn f(x: i32) -> i32 { if std::hint::likely(x > 0) { 1 } else { 2 } }
fn main(){ println!("{}", f(3)); }
