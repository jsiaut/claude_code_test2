fn main() { let n = std::env::args().count() + 3; let m = [[0f32; n]; 2]; println!("{}", m[1][0]); }
