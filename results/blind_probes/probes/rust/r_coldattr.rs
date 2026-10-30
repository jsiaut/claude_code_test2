#[cold] #[inline(never)] fn slow() -> i32 { 2 }
pub fn f(x: i32) -> i32 { if x > 0 { 1 } else { slow() } }
fn main(){ println!("{}", f(3)); }
