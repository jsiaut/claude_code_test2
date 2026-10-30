use std::sync::atomic::{AtomicBool, AtomicU64, Ordering, fence};
static F: AtomicBool = AtomicBool::new(false);
static X: AtomicU64 = AtomicU64::new(0);
fn main(){
  std::thread::scope(|s| {
    s.spawn(|| { X.store(42, Ordering::Relaxed); fence(Ordering::Release); F.store(true, Ordering::Relaxed); });
    s.spawn(|| { while !F.load(Ordering::Relaxed) { std::hint::spin_loop(); } fence(Ordering::Acquire); assert_eq!(X.load(Ordering::Relaxed), 42); });
  });
  println!("ok {}", std::thread::available_parallelism().unwrap());
}
