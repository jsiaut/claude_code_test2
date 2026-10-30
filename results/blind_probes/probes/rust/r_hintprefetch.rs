pub fn f(p: &[u8]) { std::hint::prefetch_read_data(p.as_ptr(), std::hint::Locality::L1); }
fn main(){ let v = vec![0u8; 64]; f(&v); println!("ok"); }
