fn main(){ let b = std::thread::Builder::new(); let _ = b.affinity(0); }
