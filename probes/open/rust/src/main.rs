// v4, point 6 (docs/V4_OPEN.md, 4) : sondes de la grille ouverte de Rust. Chaque fonction se sert de l'API de la
// bibliothèque pour le levier de sa case et imprime une ligne RESULT;<case>;<bibliothèque>;<fait observé>.
// run.sh en tire les lignes CAP (note) et NOTE de results/open/probes/rust.txt.
use std::collections::HashSet;
use std::io::Write;
use std::sync::Mutex;
use std::sync::atomic::{AtomicU64, Ordering};

// ---------------------------------------------------------------- B2 : bumpalo
struct Node<'a> {
    v: i64,
    l: Option<&'a Node<'a>>,
    r: Option<&'a Node<'a>>,
}

fn b2_bumpalo() {
    let mut bump = bumpalo::Bump::new();
    let (deltas, sum, first) = {
        let mut addrs = Vec::new();
        let mut prev: Option<&Node> = None;
        for i in 0..1000 {
            let n: &Node = bump.alloc(Node { v: i, l: prev, r: None });
            addrs.push(n as *const Node as isize);
            prev = Some(n);
        }
        let mut s = 0;
        let mut p = prev;
        while let Some(n) = p {
            s += n.v + n.r.map_or(0, |x| x.v);
            p = n.l;
        }
        let d: HashSet<isize> = addrs.windows(2).map(|w| w[1] - w[0]).collect();
        (d, s, addrs[0])
    };
    let used = bump.allocated_bytes();
    let inside;
    {
        let mut v = bumpalo::collections::Vec::new_in(&bump);
        for i in 0..100u32 {
            v.push(i);
        }
        let vptr = v.as_ptr() as usize;
        inside = unsafe { bump.iter_allocated_chunks_raw() }.any(|(p, n)| vptr >= p as usize && vptr < p as usize + n);
    }
    let chunks_before = unsafe { bump.iter_allocated_chunks_raw() }.count();
    bump.reset();
    let after_reset = bump.allocated_bytes();
    let again = bump.alloc(Node { v: 0, l: None, r: None }) as *const Node as usize;
    let reused = unsafe { bump.iter_allocated_chunks_raw() }.any(|(p, n)| again >= p as usize && again < p as usize + n);
    let _ = first;
    println!(
        "RESULT;B2;bumpalo;Bump::alloc de 1000 nœuds (valeur, deux liens) : écarts d'adresse {:?} (size_of = {}), \
         somme en suivant les liens = {} ; allocated_bytes = {} ; bumpalo::collections::Vec::new_in(&bump) : tampon \
         dans un bloc de l'arène = {} ; reset() : {} blocs ramenés à 1, allocated_bytes {} -> {}, nouvel objet dans le \
         bloc gardé = {}",
        deltas,
        std::mem::size_of::<Node>(),
        sum,
        used,
        inside,
        chunks_before,
        used,
        after_reset,
        reused
    );
}

// ---------------------------------------------------------------- C1 : fearless_simd
use fearless_simd::{Level, Simd, SimdBase, SimdFloat, dispatch, f32x8};

#[inline(always)]
fn c1_dot_kernel<S: Simd>(simd: S, a: &[f32], b: &[f32]) -> f32 {
    let mut acc = f32x8::splat(simd, 0.0);
    for (x, y) in a.chunks_exact(8).zip(b.chunks_exact(8)) {
        let va = f32x8::from_slice(simd, x);
        let vb = f32x8::from_slice(simd, y);
        acc = va.mul_add(vb, acc);
    }
    acc.reduce_sum()
}

#[inline(never)]
#[unsafe(no_mangle)]
pub fn c1_dot_entry(a: &[f32], b: &[f32]) -> f32 {
    let level = Level::new();
    dispatch!(level, simd => c1_dot_kernel(simd, a, b))
}

fn c1_fearless() {
    let a: Vec<f32> = (0..4096).map(|i| (i % 7) as f32).collect();
    let b: Vec<f32> = (0..4096).map(|i| (i % 5) as f32).collect();
    let d = c1_dot_entry(&a, &b);
    let want: f32 = a.iter().zip(&b).map(|(x, y)| x * y).sum();
    println!(
        "RESULT;C1;fearless_simd;Level::new() = {:?} ; f32x8 (from_slice, mul_add, reduce_sum) : produit scalaire de \
         4096 = {} (somme scalaire {})",
        Level::new(),
        d,
        want
    );
}

// ---------------------------------------------------------------- C5 : rayon
fn c5_rayon() {
    use rayon::prelude::*;
    let seen = Mutex::new(HashSet::new());
    let v: Vec<u64> = (0..40_000_000u64).collect();
    let s: u64 = v
        .par_chunks(1 << 20)
        .map(|c| {
            seen.lock().unwrap().insert(std::thread::current().id());
            c.iter().sum::<u64>()
        })
        .sum();
    let t0 = std::time::Instant::now();
    let s2: u64 = v.par_iter().sum();
    let tp = t0.elapsed();
    let t1 = std::time::Instant::now();
    let s3: u64 = v.iter().sum();
    let ts = t1.elapsed();
    println!(
        "RESULT;C5;rayon;par_chunks(2^20).map(somme).sum() = {} sur {} fils distincts (rayon::current_num_threads = \
         {}) ; par_iter().sum() = {} en {:.1} ms contre {} en {:.1} ms en série",
        s,
        seen.lock().unwrap().len(),
        rayon::current_num_threads(),
        s2,
        tp.as_secs_f64() * 1e3,
        s3,
        ts.as_secs_f64() * 1e3
    );
}

// ---------------------------------------------------------------- D3 : cordyceps, cache-padded, crossbeam, libc
#[allow(deprecated)]
fn d3() {
    // cordyceps : CachePadded est pub(crate) (src/util.rs) ; aucun type public de bourrage. La ligne suivante, si on la
    // décommente, ne compile pas : use cordyceps::util::CachePadded;  (module util privé : run.sh le montre).
    type P1 = cache_padded::CachePadded<AtomicU64>;
    type P2 = crossbeam::utils::CachePadded<AtomicU64>;
    let a1: [P1; 4] = Default::default();
    let a2: [P2; 4] = Default::default();
    let o1 = (&a1[1] as *const P1 as usize) - (&a1[0] as *const P1 as usize);
    let o2 = (&a2[1] as *const P2 as usize) - (&a2[0] as *const P2 as usize);
    a1[0].fetch_add(1, Ordering::Relaxed);
    a2[3].fetch_add(1, Ordering::Relaxed);
    println!(
        "RESULT;D3;cache-padded;cache_padded::CachePadded<AtomicU64> : size_of = {}, align_of = {}, écart entre deux \
         compteurs d'un tableau = {} octets",
        std::mem::size_of::<P1>(),
        std::mem::align_of::<P1>(),
        o1
    );
    println!(
        "RESULT;D3;crossbeam;crossbeam::utils::CachePadded<AtomicU64> : size_of = {}, align_of = {}, écart entre deux \
         compteurs = {} octets",
        std::mem::size_of::<P2>(),
        std::mem::align_of::<P2>(),
        o2
    );
    let ls = unsafe { libc::sysconf(libc::_SC_LEVEL1_DCACHE_LINESIZE) };
    println!(
        "RESULT;D3;libc;libc::sysconf(_SC_LEVEL1_DCACHE_LINESIZE) = {} (valeur lue à l'exécution ; ni constante ni type \
         de bourrage)",
        ls
    );
}

// ---------------------------------------------------------------- D4 : core_affinity, libc
fn d4() {
    let ids = core_affinity::get_core_ids().unwrap_or_default();
    let target = ids.get(2).copied();
    let h = std::thread::spawn(move || {
        let ok = target.map(core_affinity::set_for_current).unwrap_or(false);
        let mut cpus = Vec::new();
        for _ in 0..1000 {
            cpus.push(unsafe { libc::sched_getcpu() });
        }
        let set: HashSet<i32> = cpus.into_iter().collect();
        (ok, set)
    });
    let (ok, set) = h.join().unwrap();
    println!(
        "RESULT;D4;core_affinity;get_core_ids() = {} cœurs ; set_for_current(CoreId {{ id: 2 }}) = {} ; sched_getcpu sur \
         1000 lectures dans le fil : {:?}",
        ids.len(),
        ok,
        set
    );
    let h2 = std::thread::spawn(|| unsafe {
        let mut cs: libc::cpu_set_t = std::mem::zeroed();
        libc::CPU_SET(3, &mut cs);
        let r = libc::sched_setaffinity(0, std::mem::size_of::<libc::cpu_set_t>(), &cs);
        let mut got: libc::cpu_set_t = std::mem::zeroed();
        libc::sched_getaffinity(0, std::mem::size_of::<libc::cpu_set_t>(), &mut got);
        let n = (0..64).filter(|&i| libc::CPU_ISSET(i, &got)).collect::<Vec<_>>();
        (r, n, libc::sched_getcpu())
    });
    let (r, n, c) = h2.join().unwrap();
    println!(
        "RESULT;D4;libc;libc::sched_setaffinity(CPU 3) = {} ; masque relu {:?} ; sched_getcpu = {}",
        r, n, c
    );
}

// ---------------------------------------------------------------- F1 : ndarray
fn f1_ndarray() {
    let (m, n) = (std::hint::black_box(300usize), std::hint::black_box(500usize));
    let mut a = ndarray::Array2::<f64>::zeros((m, n));
    a[[2, 3]] = 7.0;
    let s = a.as_slice().map(|x| x.len());
    let off = (&a[[2, 3]] as *const f64 as usize - a.as_ptr() as usize) / 8;
    println!(
        "RESULT;F1;ndarray;Array2::<f64>::zeros(({}, {})) de dimensions connues à l'exécution : shape {:?}, strides {:?}, \
         is_standard_layout = {}, as_slice() contigu de {:?} éléments, a[[2, 3]] à l'indice {} = 2*{}+3",
        m,
        n,
        a.shape(),
        a.strides(),
        a.is_standard_layout(),
        s,
        off,
        n
    );
}

// ---------------------------------------------------------------- F2 : hwlocality-sys
fn f2_hwloc() {
    use hwlocality_sys::*;
    unsafe {
        let mut t: hwloc_topology_t = std::ptr::null_mut();
        let _ = hwloc_topology_init(&mut t);
        let _ = hwloc_topology_load(t);
        let nn = hwloc_get_nbobjs_by_depth(t, HWLOC_TYPE_DEPTH_NUMANODE as _);
        let node = hwloc_get_obj_by_depth(t, HWLOC_TYPE_DEPTH_NUMANODE as _, 0);
        let len = 1usize << 22;
        let p = hwloc_alloc_membind(
            t,
            len,
            (*node).nodeset,
            HWLOC_MEMBIND_BIND,
            HWLOC_MEMBIND_BYNODESET | HWLOC_MEMBIND_STRICT,
        );
        std::ptr::write_bytes(p as *mut u8, 1, len);
        let ns = hwloc_bitmap_alloc();
        let loc = hwloc_bitmap_alloc();
        let mut pol: hwloc_membind_policy_t = 0;
        let r1 = hwloc_get_area_membind(t, p, len, ns, &mut pol, HWLOC_MEMBIND_BYNODESET);
        let r2 = hwloc_get_area_memlocation(t, p, len, loc, HWLOC_MEMBIND_BYNODESET);
        println!(
            "RESULT;F2;hwlocality-sys;{} nœud(s) NUMA ; zone de 4 Mio par hwloc_alloc_membind(BIND, STRICT) au nœud 0 : \
             politique relue {} (BIND = {}, retour {}), premier nœud de la politique {}, premier nœud des pages {} \
             (retour {})",
            nn,
            pol,
            HWLOC_MEMBIND_BIND,
            r1,
            hwloc_bitmap_first(ns),
            hwloc_bitmap_first(loc),
            r2
        );
        let _ = hwloc_free(t, p, len);
        hwloc_topology_destroy(t);
    }
}

// ---------------------------------------------------------------- F4 : memmap2, libc
fn f4() {
    let path = std::env::temp_dir().join("open_probe_f4.bin");
    {
        let mut f = std::fs::File::create(&path).unwrap();
        for i in 0..1024u32 {
            f.write_all(&i.to_le_bytes()).unwrap();
        }
    }
    let f = std::fs::File::open(&path).unwrap();
    let m = unsafe { memmap2::Mmap::map(&f).unwrap() };
    let (pre, ints, post) = unsafe { m.align_to::<u32>() };
    let maps = std::fs::read_to_string("/proc/self/maps").unwrap();
    let mapped = maps.lines().any(|l| l.contains("open_probe_f4.bin"));
    println!(
        "RESULT;F4;memmap2;Mmap::map : {} octets projetés (fichier dans /proc/self/maps = {}) ; align_to::<u32>() sans \
         copie : {} entiers, ints[1000] = {}, même adresse = {} (reste {}/{})",
        m.len(),
        mapped,
        ints.len(),
        ints[1000],
        ints.as_ptr() as usize == m.as_ptr() as usize,
        pre.len(),
        post.len()
    );
    unsafe {
        use std::os::unix::io::AsRawFd;
        let p = libc::mmap(std::ptr::null_mut(), 4096, libc::PROT_READ, libc::MAP_PRIVATE, f.as_raw_fd(), 0);
        let s = std::slice::from_raw_parts(p as *const u32, 1024);
        println!(
            "RESULT;F4;libc;libc::mmap : page projetée, lue sans copie comme &[u32] : s[1000] = {} (adresse {:#x})",
            s[1000], p as usize
        );
        libc::munmap(p, 4096);
    }
    std::fs::remove_file(&path).ok();
}

fn main() {
    let only: Vec<String> = std::env::args().skip(1).collect();
    let want = |c: &str| only.is_empty() || only.iter().any(|x| x == c);
    if want("B2") { b2_bumpalo(); }
    if want("C1") { c1_fearless(); }
    if want("C5") { c5_rayon(); }
    if want("D3") { d3(); }
    if want("D4") { d4(); }
    if want("F1") { f1_ndarray(); }
    if want("F2") { f2_hwloc(); }
    if want("F4") { f4(); }
}
