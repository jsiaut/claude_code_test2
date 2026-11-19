fn main() { let v: Vec<u8, std::alloc::System> = Vec::new_in(std::alloc::System); println!("{}", v.len()); }
