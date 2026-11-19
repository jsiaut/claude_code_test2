// Contre-épreuve sur le canal nightly : ce que la grille note ½ (instable) ou laisse à 0 (unité interne).
#![feature(allocator_api, portable_simd, rustc_private)]
extern crate libc;
use std::alloc::{AllocError, Allocator, Layout};
use std::cell::Cell;
use std::ptr::NonNull;
use std::simd::f32x8;
struct Bump { base: *mut u8, cap: usize, off: Cell<usize> }
unsafe impl Allocator for &Bump {
    fn allocate(&self, l: Layout) -> Result<NonNull<[u8]>, AllocError> {
        let o = (self.off.get() + l.align() - 1) & !(l.align() - 1);
        if o + l.size() > self.cap { return Err(AllocError); }
        self.off.set(o + l.size());
        Ok(NonNull::slice_from_raw_parts(unsafe { NonNull::new_unchecked(self.base.add(o)) }, l.size()))
    }
    unsafe fn deallocate(&self, _: NonNull<u8>, _: Layout) {}
}
fn main() {
    let mut store = vec![0u8; 1 << 16];
    let arena = Bump { base: store.as_mut_ptr(), cap: store.len(), off: Cell::new(0) };
    let mut v: Vec<u64, &Bump> = Vec::with_capacity_in(100, &arena);
    v.extend(0..100);
    let inside = (v.as_ptr() as usize) >= arena.base as usize && (v.as_ptr() as usize) < arena.base as usize + arena.cap;
    println!("NIGHTLY;B2;Vec::with_capacity_in(&arena) : tampon dans l'arène = {inside}, {} o consommés", arena.off.get());
    let a = f32x8::from_array([1., 2., 3., 4., 5., 6., 7., 8.]);
    println!("NIGHTLY;C1;std::simd::f32x8 : (a + a)[7] = {}, somme réduite = {}", (a + a)[7], std::simd::num::SimdFloat::reduce_sum(a));
    unsafe {
        let mut set: libc::cpu_set_t = std::mem::zeroed();
        libc::CPU_SET(1, &mut set);
        let r = libc::sched_setaffinity(0, std::mem::size_of::<libc::cpu_set_t>(), &set);
        println!("NIGHTLY;D4;extern crate libc (crate du sysroot, #![feature(rustc_private)]) : sched_setaffinity = {r}, sched_getcpu() = {}", libc::sched_getcpu());
        let path = std::ffi::CString::new("/tmp/rust_audit_f4.bin").unwrap();
        let data: Vec<u8> = [1.5f32, 2.5, 3.5, 4.5].iter().flat_map(|x| x.to_le_bytes()).collect();
        std::fs::write("/tmp/rust_audit_f4.bin", &data).unwrap();
        let fd = libc::open(path.as_ptr(), libc::O_RDONLY);
        let p = libc::mmap(std::ptr::null_mut(), 16, libc::PROT_READ, libc::MAP_PRIVATE, fd, 0);
        let s = std::slice::from_raw_parts(p as *const f32, 4);
        println!("NIGHTLY;F4;libc::mmap (crate du sysroot, rustc_private) + from_raw_parts : {:?}, adresse projetée = adresse lue : {}", s, s.as_ptr() as usize == p as usize);
        libc::munmap(p, 16); libc::close(fd);
    }
    drop(v);
}
