// Sonde Rust (stable) : chaque println! n'est atteint que si le code compile sur le canal stable.
use std::arch::x86_64::*;
use std::mem::offset_of;
#[repr(C)] struct S { a: u8, b: u32, c: f64 }
#[repr(C, packed)] struct P { a: u8, b: u32 }
#[repr(C, align(64))] struct L { v: i32 }
union U { f: f32, u: u32 }
fn main() {
    println!("CAP;A2;1;offset_of!(S, c)={} (repr(C))", offset_of!(S, c));
    println!("CAP;A3;0.5;repr(packed) size_of::<P>()={}", std::mem::size_of::<P>());
    println!("CAP;A4;1;repr(align(64)) align_of::<L>()={}", std::mem::align_of::<L>());
    let u = U { f: 1.0 };
    println!("CAP;A5;1;union 0x{:08x} to_bits 0x{:08x}", unsafe { u.u }, 1.0f32.to_bits());
    let v = [1.0f32; 64];
    let s = v.iter().fold(0.0f32, |a, &x| a.algebraic_add(x));
    println!("CAP;C4;1;f32::algebraic_add stable : {}", s);
    let mut x: u64 = 1;
    unsafe { std::arch::asm!("add {0}, 1", inout(reg) x) };
    println!("CAP;E2;1;asm! stable : {}", x);
    if x == 3 { std::hint::cold_path(); }
    println!("CAP;E3;1;std::hint::cold_path stable");
    unsafe { _mm_prefetch::<_MM_HINT_T0>(v.as_ptr() as *const i8) };
    println!("CAP;E4;1;_mm_prefetch (std::arch)");
    let _ = L { v: 0 }.v; let _ = S { a: 0, b: 0, c: 0.0 }.c; let _ = P { a: 0, b: 0 }.a;
}
