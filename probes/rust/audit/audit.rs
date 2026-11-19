// Audit de la grille (docs/V4_PLAN.md 2.1) : sonde exécutée de Rust stable, cas positifs. Chaque ligne imprime un fait
// observé ; run.sh y ajoute les cas d'échec (canal stable), le code produit (asm, IR) et les recherches d'absence.
use std::alloc::{GlobalAlloc, Layout, System};
use std::mem::{align_of, offset_of, size_of};
use std::num::Wrapping;
use std::sync::atomic::{AtomicUsize, Ordering};

struct Counting;
static ALLOCS: AtomicUsize = AtomicUsize::new(0);
unsafe impl GlobalAlloc for Counting {
    unsafe fn alloc(&self, l: Layout) -> *mut u8 { ALLOCS.fetch_add(1, Ordering::Relaxed); unsafe { System.alloc(l) } }
    unsafe fn dealloc(&self, p: *mut u8, l: Layout) { unsafe { System.dealloc(p, l) } }
}
#[global_allocator]
static GA: Counting = Counting;
fn allocs() -> usize { ALLOCS.load(Ordering::Relaxed) }

#[derive(Clone, Copy)] struct Part { x: f32, y: f32, z: f32, m: u8 }
#[allow(dead_code)] struct Reord { a: u8, b: f64, c: u8 }
#[repr(C)] struct ReordC { a: u8, b: f64, c: u8 }
#[repr(C, align(64))] struct Line { v: u64 }
#[repr(C)] struct Inl { n: u32, a: [f32; 16] }
struct Noisy(&'static str);
impl Drop for Noisy { fn drop(&mut self) { print!("drop({}) ", self.0); } }
trait Shape { fn area(&self) -> f32; }
struct Sq(f32);
impl Shape for Sq { fn area(&self) -> f32 { self.0 * self.0 } }
struct StackBuf { b: [u8; 64], n: usize }
impl std::fmt::Write for StackBuf {
    fn write_str(&mut self, s: &str) -> std::fmt::Result {
        let e = self.n + s.len(); if e > 64 { return Err(std::fmt::Error); }
        self.b[self.n..e].copy_from_slice(s.as_bytes()); self.n = e; Ok(())
    }
}
const fn fib(n: u64) -> u64 { let (mut a, mut b, mut i) = (0u64, 1u64, 0); while i < n { let t = a + b; a = b; b = t; i += 1; } a }
const FIB60: u64 = fib(60);

fn main() {
    // A1
    let v = vec![Part { x: 1.0, y: 2.0, z: 3.0, m: 4 }; 8];
    let stride = (&v[1] as *const Part as usize) - (&v[0] as *const Part as usize);
    let raw = unsafe { std::slice::from_raw_parts(v.as_ptr() as *const u8, 4) };
    println!("CAP;A1;1;[exécutée] Vec<Part> : pas de {stride} o = size_of::<Part>() {} ; les 4 premiers octets du tampon sont le f32 x en ligne : {:02x?}", size_of::<Part>(), raw);
    // A2
    println!("CAP;A2;1;[exécutée] repr(Rust) réordonne (u8, f64, u8) : {} o ; repr(C) garde l'ordre : {} o, offset_of!(ReordC, b) = {}, offset_of!(ReordC, c) = {}",
        size_of::<Reord>(), size_of::<ReordC>(), offset_of!(ReordC, b), offset_of!(ReordC, c));
    // A4
    let bx = Box::new(Line { v: 1 });
    let lv: Vec<Line> = (0..4).map(|i| Line { v: i }).collect();
    println!("CAP;A4;1;[exécutée] repr(align(64)) : align_of = {}, Box à {} mod 64, Vec<Line> : pas {} o, éléments à {} mod 64",
        align_of::<Line>(), (&*bx as *const Line as usize) % 64, size_of::<Line>(), (&lv[1] as *const Line as usize) % 64);
    // A7
    println!("CAP;A7;1;[exécutée] struct Inl {{ n: u32, a: [f32; 16] }} : {} o, offset_of!(Inl, a) = {} (tableau en ligne)", size_of::<Inl>(), offset_of!(Inl, a));
    // A8
    let b8: Vec<u8> = vec![0; 1000]; let h16: Vec<i16> = vec![0; 1000];
    println!("CAP;A8;1;[exécutée] u8/i16/f32 : {}/{}/{} o ; Vec<u8> de 1000 éléments : {} o de capacité, Vec<i16> : {} o",
        size_of::<u8>(), size_of::<i16>(), size_of::<f32>(), b8.capacity() * size_of::<u8>(), h16.capacity() * size_of::<i16>());
    // B1
    print!("CAP;B1;1;[exécutée] destruction déterministe sans collecteur : ");
    { let _a = Noisy("a"); { let _b = Noisy("b"); } print!("fin-portée "); }
    let tasks = std::fs::read_dir("/proc/self/task").map(|d| d.count()).unwrap_or(0);
    println!("; {tasks} fil dans /proc/self/task (aucun fil de collecteur)");
    // B3
    let local = [0u8; 4096]; let probe_heap = Box::new(0u8); let marker = 0u8;
    let d_stack = (&marker as *const u8 as isize - local.as_ptr() as isize).unsigned_abs();
    let d_heap = (&*probe_heap as *const u8 as isize - local.as_ptr() as isize).unsigned_abs();
    println!("CAP;B3;1;[exécutée] [u8; 4096] local à {d_stack} o d'une autre variable locale, à {d_heap} o du tas : sur la pile");
    // B4
    let a0 = allocs();
    let data: [f32; 256] = std::array::from_fn(|i| i as f32);
    let k = 3.0f32;
    let s1: f32 = data.iter().map(|x| x * k).filter(|x| *x > 10.0).sum();
    let shapes: [&dyn Shape; 2] = [&Sq(2.0), &Sq(3.0)];
    let s2: f32 = shapes.iter().map(|s| s.area()).sum();
    let mut arr = data; arr.sort_unstable_by(|a, b| b.total_cmp(a));
    let mut sb = StackBuf { b: [0; 64], n: 0 };
    use std::fmt::Write; write!(sb, "{s1:.1} {s2:.1}").unwrap();
    let a1 = allocs();
    let mut big: Vec<f32> = (0..100_000).map(|i| i as f32).collect(); let a2 = allocs();
    big.sort_by(|a, b| b.total_cmp(a)); let a3 = allocs();
    println!("CAP;B4;1;[exécutée] allocateur global compteur : 0 allocation attendue pour fermetures, itérateurs, objets dyn par référence, tri sur place, formatage dans un tampon de pile : {} allocation(s) ({}) ; Vec explicite : {} ; slice::sort sur 100 000 f32 (tri stable, tampon auxiliaire documenté) : {}",
        a1 - a0, std::str::from_utf8(&sb.b[..sb.n]).unwrap(), a2 - a1, a3 - a2);
    // B5
    let mut buf = [0u32; 8];
    unsafe { let p = buf.as_mut_ptr(); *p.add(3) = 42; *(p.cast::<u8>().add(16)).cast::<u32>() = 7; }
    println!("CAP;B5;1;[exécutée] *mut u32 : *p.add(3) = 42 -> buf[3] = {} ; écriture par décalage d'octets -> buf[4] = {}", buf[3], buf[4]);
    // C2
    let r = c2();
    println!("CAP;C2;1;[exécutée] std::arch::x86_64 : is_x86_feature_detected!(\"avx512f\") = {} ; _mm512_add_ps -> {r}", is_x86_feature_detected!("avx512f"));
    // D1
    let mut parts = [0u64; 4]; let mut ids = Vec::new();
    std::thread::scope(|s| {
        let hs: Vec<_> = parts.iter_mut().enumerate().map(|(t, p)| s.spawn(move || { *p = (t as u64 * 1000..(t as u64 + 1) * 1000).sum(); std::thread::current().id() })).collect();
        for h in hs { ids.push(h.join().unwrap()); }
    });
    ids.sort_by_key(|i| format!("{i:?}")); ids.dedup();
    println!("CAP;D1;1;[exécutée] std::thread::scope : 4 fils, {} identifiants distincts, somme {} (attendu 7998000)", ids.len(), parts.iter().sum::<u64>());
    // E7
    println!("FACT;E7;const fn fib(60) = {FIB60} ; gsum::<f32> = {}, gsum::<f64> = {}", gsum(&[1.5f32, 2.5]), gsum(&[1.5f64, 2.25]));
    // F1
    let m = [[0f32; 4]; 3];
    let d = (&m[1][0] as *const f32 as usize) - (&m[0][3] as *const f32 as usize);
    println!("FACT;F1;[[f32; 4]; 3] contigu : &m[1][0] - &m[0][3] = {d} o, size_of = {} o", size_of::<[[f32; 4]; 3]>());
    // F3
    println!("CAP;F3;1;[exécutée] u32::MAX.wrapping_add(1) = {}, i32::MAX.wrapping_add(1) = {}, Wrapping(250u8) + Wrapping(10) = {}, u64::MAX.wrapping_mul(3) = {}",
        u32::MAX.wrapping_add(1), i32::MAX.wrapping_add(1), (Wrapping(250u8) + Wrapping(10u8)).0, u64::MAX.wrapping_mul(3));
    let _ = (Reord { a: 0, b: 0.0, c: 0 }.b, ReordC { a: 0, b: 0.0, c: 0 }.a, Inl { n: 0, a: [0.0; 16] }.n, lv[0].v, bx.v);
    let _ = (v[0].x, v[0].y, v[0].z, v[0].m);
}
fn gsum<T: Copy + std::iter::Sum<T>>(x: &[T]) -> T { x.iter().copied().sum() }
#[target_feature(enable = "avx512f")]
fn c2_inner() -> f32 {
    use std::arch::x86_64::*;
    let a = _mm512_set1_ps(1.5); let b = _mm512_set1_ps(2.0);
    _mm512_reduce_add_ps(_mm512_add_ps(a, b))
}
fn c2() -> f32 { if is_x86_feature_detected!("avx512f") { unsafe { c2_inner() } } else { -1.0 } }
