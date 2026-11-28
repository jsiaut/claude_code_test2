// v7 (docs/V7.md ; olap/SPEC.md) : le banc OLAP en Rust. Même architecture que la référence (olap/c/olap.c), écrite
// avec les moyens du langage : routines par largeur instanciées par un paramètre constant, tâches des fils en
// fermetures qui rendent leur résultat au fil principal, `unsafe` pour les arènes, les tables et les tampons de
// partition. Niveau portable : aucune vectorisation explicite, aucune construction propre à une famille de
// processeurs. Le niveau spécialisé (--cfg special) remplace des primitives par celles de special.rs.
//
// Usage : olap <requête> <fils> <répétitions> <répertoire des données> [--print]
#![allow(clippy::too_many_arguments, clippy::missing_safety_doc, clippy::mut_from_ref)]

use std::cell::UnsafeCell;
use std::io::{Read, Write};
use std::mem::size_of;
use std::ptr::null_mut;
use std::sync::atomic::{AtomicU64, Ordering};
use std::sync::{Condvar, Mutex};

const PBITS: u32 = 10; // bits de partition
const VEC: usize = 2048; // lignes d'un vecteur
const CHUNK: usize = 16384; // octets utiles d'un morceau de tampon de partition
const BLOCK: usize = 65536; // lignes d'un bloc : un morceau
const NPART: usize = 1 << PBITS; // partitions des grandes tables
const MAXT: usize = 64; // fils au plus
const ARENA_BLOCK: usize = 32 << 20; // octets d'un bloc d'arène
const HUGE_PAGE: usize = 1 << 21; // octets d'une page large
const K1: u64 = 0x9E3779B97F4A7C15;
const K2: u64 = 0xC2B2AE3D27D4EB4F;

fn die(msg: &str) -> ! {
    eprintln!("olap : {msg}");
    std::process::exit(2)
}

// ------------------------------------------------------------------------------------------------ mémoire, arènes
unsafe extern "C" {
    fn madvise(addr: *mut u8, len: usize, advice: i32) -> i32;
}
const MADV_HUGEPAGE: i32 = 14;

/// Toute la mémoire du programme (colonnes chargées, arènes, vecteurs de travail) vient du système par zones
/// alignées sur 2 Mio et signalées comme pages larges.
fn huge_alloc(n: usize) -> *mut u8 {
    let n = (n + HUGE_PAGE - 1) & !(HUGE_PAGE - 1);
    unsafe {
        let p = std::alloc::alloc(std::alloc::Layout::from_size_align_unchecked(n, HUGE_PAGE));
        if p.is_null() {
            die("mémoire");
        }
        madvise(p, n, MADV_HUGEPAGE);
        p
    }
}

/// Une arène par fil : allocation par déplacement d'un pointeur, remise à zéro à chaque exécution ; la mémoire est
/// gardée d'une répétition à l'autre.
#[repr(C)]
struct ArenaBlock {
    next: *mut ArenaBlock,
    cap: usize,
    used: usize,
    pad: [u8; 40],
}
struct Arena {
    first: *mut ArenaBlock,
    cur: *mut ArenaBlock,
}
impl Arena {
    fn alloc(&mut self, n: usize) -> *mut u8 {
        let n = (n + 63) & !63;
        unsafe {
            loop {
                let b = self.cur;
                if !b.is_null() && (*b).used + n <= (*b).cap {
                    let p = (b.add(1) as *mut u8).add((*b).used);
                    (*b).used += n;
                    return p;
                }
                if !b.is_null() && !(*b).next.is_null() && (*(*b).next).cap >= n {
                    self.cur = (*b).next;
                    (*self.cur).used = 0;
                    continue;
                }
                let cap = n.max(ARENA_BLOCK - size_of::<ArenaBlock>());
                let nb = huge_alloc(size_of::<ArenaBlock>() + cap) as *mut ArenaBlock;
                (*nb).cap = cap;
                (*nb).used = 0;
                if b.is_null() {
                    (*nb).next = null_mut();
                    self.first = nb;
                } else {
                    (*nb).next = (*b).next;
                    (*b).next = nb;
                }
                self.cur = nb;
            }
        }
    }
    fn array<T>(&mut self, n: usize) -> *mut T {
        self.alloc(n * size_of::<T>()) as *mut T
    }
    fn reset(&mut self) {
        self.cur = self.first;
        if !self.cur.is_null() {
            unsafe { (*self.cur).used = 0 }
        }
    }
}

// ------------------------------------------------------------------------------------------------ fils persistants
/// Une case par fil : chaque fil n'écrit que la sienne pendant une phase ; le fil principal les lit entre deux phases.
#[repr(transparent)]
struct Slot<T>(UnsafeCell<T>);
unsafe impl<T: Send> Sync for Slot<T> {}
impl<T> Slot<T> {
    fn new(v: T) -> Self {
        Slot(UnsafeCell::new(v))
    }
    unsafe fn get(&self) -> &mut T {
        unsafe { &mut *self.0.get() }
    }
}

type Job = dyn Fn(usize) + Sync;
struct PoolState {
    generation: u64,
    pending: usize,
    job: Option<&'static Job>,
}
/// Les fils sont créés une fois et attendent, bloqués, entre deux phases.
struct Pool {
    n: usize,
    state: Mutex<PoolState>,
    work: Condvar,
    done: Condvar,
}
impl Pool {
    fn start(n: usize) -> &'static Pool {
        let pool: &'static Pool = Box::leak(Box::new(Pool {
            n,
            state: Mutex::new(PoolState { generation: 0, pending: 0, job: None }),
            work: Condvar::new(),
            done: Condvar::new(),
        }));
        for tid in 1..n {
            std::thread::spawn(move || pool.worker(tid));
        }
        pool
    }
    fn worker(&self, tid: usize) {
        let mut seen = 0;
        loop {
            let job = {
                let mut st = self.state.lock().unwrap();
                while st.generation == seen {
                    st = self.work.wait(st).unwrap();
                }
                seen = st.generation;
                st.job.unwrap()
            };
            job(tid);
            let mut st = self.state.lock().unwrap();
            st.pending -= 1;
            if st.pending == 0 {
                self.done.notify_one();
            }
        }
    }
    /// Exécute f(tid) sur tous les fils (le fil principal est le fil 0), attend la fin de tous et rend leurs
    /// résultats, dans l'ordre des fils.
    fn run<R: Send, F: Fn(usize) -> R + Sync>(&self, f: F) -> Vec<R> {
        let slots: Vec<Slot<Option<R>>> = (0..self.n).map(|_| Slot::new(None)).collect();
        let job = |tid: usize| unsafe { *slots[tid].get() = Some(f(tid)) };
        if self.n > 1 {
            let erased: &(dyn Fn(usize) + Sync + '_) = &job;
            // Durée de vie effacée : run ne rend la main qu'après la fin de tous les fils.
            let erased: &'static Job = unsafe { std::mem::transmute(erased) };
            let mut st = self.state.lock().unwrap();
            st.job = Some(erased);
            st.pending = self.n - 1;
            st.generation += 1;
            self.work.notify_all();
        }
        job(0);
        if self.n > 1 {
            let mut st = self.state.lock().unwrap();
            while st.pending > 0 {
                st = self.done.wait(st).unwrap();
            }
        }
        slots.into_iter().map(|s| s.0.into_inner().unwrap()).collect()
    }
}

/// Compteur de morceaux partagé : la seule opération atomique.
struct Counter {
    next: AtomicU64,
    n: u64,
}
impl Counter {
    fn new(n: u64) -> Counter {
        Counter { next: AtomicU64::new(0), n }
    }
    #[inline]
    fn take(&self) -> Option<usize> {
        let i = self.next.fetch_add(1, Ordering::Relaxed);
        (i < self.n).then_some(i as usize)
    }
}

// ------------------------------------------------------------------------------------------------ colonnes
#[repr(C)]
struct Entry {
    min: i64,
    max: i64,
    data_off: u64,
    aux_off: u64,
    width: u32,
    count: u32,
}
#[derive(Clone, Copy)]
struct Col {
    nrows: u64,
    nblocks: u64,
    aux_count: u64,
    dir: *const Entry,
    data: *const u64,
    aux: *const u8,
}
unsafe impl Sync for Col {}
unsafe impl Send for Col {}
impl Col {
    fn open(dir: &str, table: &str, name: &str) -> Col {
        let path = format!("{dir}/{table}/{name}.msc");
        let mut f = std::fs::File::open(&path).unwrap_or_else(|e| die(&format!("{path} : {e}")));
        let size = f.metadata().unwrap().len() as usize;
        let base = huge_alloc(size); // la colonne est lue en entier, en pages larges
        if f.read_exact(unsafe { std::slice::from_raw_parts_mut(base, size) }).is_err() {
            die("lecture");
        }
        let head = unsafe { std::slice::from_raw_parts(base, 64) };
        if &head[..4] != b"MSC1" {
            die("format");
        }
        let u32_at = |i: usize| u32::from_le_bytes(head[i..i + 4].try_into().unwrap());
        let u64_at = |i: usize| u64::from_le_bytes(head[i..i + 8].try_into().unwrap());
        if u32_at(12) as usize != BLOCK {
            die("taille de bloc");
        }
        unsafe {
            Col {
                nrows: u64_at(16),
                nblocks: u64_at(24),
                dir: base.add(u64_at(32) as usize) as *const Entry,
                data: base.add(u64_at(40) as usize) as *const u64,
                aux: base.add(u64_at(48) as usize),
                aux_count: u64_at(56),
            }
        }
    }
    #[inline]
    fn entry(&self, b: usize) -> &Entry {
        unsafe { &*self.dir.add(b) }
    }
    #[inline]
    fn words(&self, b: usize) -> *const u64 {
        unsafe { self.data.add((self.entry(b).data_off / 8) as usize) }
    }
    /// Octets des chaînes à partir de la position pos de la zone annexe.
    #[inline]
    fn bytes(&self, pos: u64, len: usize) -> &'static [u8] {
        unsafe { std::slice::from_raw_parts(self.aux.add(pos as usize), len) }
    }
    /// Entrée d'un dictionnaire : ses octets suivent la table des positions.
    fn dict(&self, code: u32) -> &'static [u8] {
        unsafe {
            let p = self.aux.add(4 * code as usize) as *const u32;
            let (lo, hi) = (p.read_unaligned(), p.add(1).read_unaligned());
            std::slice::from_raw_parts(self.aux.add(4 * (self.aux_count as usize + 1) + lo as usize), (hi - lo) as usize)
        }
    }
}

// ------------------------------------------------------------------------------------------------ décodage
// Une routine par largeur, instanciée par un paramètre constant : un groupe de 64 valeurs occupe W mots ; les
// positions sont des constantes. Deux formes : quand W divise 64, chaque valeur tient dans un mot ; sinon, deux mots
// voisins sont toujours combinés, sans test. `out` porte des groupes entiers de 64 valeurs.
unsafe fn unpack_word<const W: usize>(inp: *const u64, out: &mut [i32], base: u32) {
    let mask = (1u64 << W) - 1;
    for (g, o) in out.chunks_exact_mut(64).enumerate() {
        let p = unsafe { inp.add(g * W) };
        for (j, v) in o.iter_mut().enumerate() {
            let bit = j * W;
            *v = (((unsafe { *p.add(bit >> 6) } >> (bit & 63)) & mask) as u32).wrapping_add(base) as i32;
        }
    }
}
unsafe fn unpack_two<const W: usize>(inp: *const u64, out: &mut [i32], base: u32) {
    let mask = (1u64 << W) - 1;
    for (g, o) in out.chunks_exact_mut(64).enumerate() {
        let p = unsafe { inp.add(g * W) };
        for (j, v) in o.iter_mut().enumerate() {
            let (idx, sh) = ((j * W) >> 6, (j * W) & 63);
            let x = unsafe { (*p.add(idx) >> sh) | (*p.add(idx + 1) << 1 << (63 - sh)) };
            *v = ((x & mask) as u32).wrapping_add(base) as i32;
        }
    }
}
type UnpackFn = unsafe fn(*const u64, &mut [i32], u32);
static UNPACK_FN: [UnpackFn; 33] = [
    unpack_word::<1>, // largeur 0 : jamais appelée
    unpack_word::<1>, unpack_word::<2>, unpack_two::<3>, unpack_word::<4>, unpack_two::<5>, unpack_two::<6>,
    unpack_two::<7>, unpack_word::<8>, unpack_two::<9>, unpack_two::<10>, unpack_two::<11>, unpack_two::<12>,
    unpack_two::<13>, unpack_two::<14>, unpack_two::<15>, unpack_word::<16>, unpack_two::<17>, unpack_two::<18>,
    unpack_two::<19>, unpack_two::<20>, unpack_two::<21>, unpack_two::<22>, unpack_two::<23>, unpack_two::<24>,
    unpack_two::<25>, unpack_two::<26>, unpack_two::<27>, unpack_two::<28>, unpack_two::<29>, unpack_two::<30>,
    unpack_two::<31>, unpack_word::<32>,
];

/// Décode n valeurs du bloc b à partir de la ligne start (multiple de 64) ; écrit des groupes entiers de 64.
#[allow(dead_code)]
#[inline]
fn unpack_portable(c: &Col, b: usize, start: usize, n: usize, out: &mut [i32]) {
    let e = c.entry(b);
    if e.width == 0 {
        out[..n].fill(e.min as i32);
        return;
    }
    let groups = &mut out[..(n + 63) & !63];
    unsafe { UNPACK_FN[e.width as usize](c.words(b).add(start / 64 * e.width as usize), groups, e.min as u32) }
}
/// Décode les valeurs du bloc b aux positions pos (lignes dans le bloc), dans l'ordre : out[i] est celle de pos[i].
#[inline]
fn unpack_sel(c: &Col, b: usize, pos: &[i32], out: &mut [i32]) {
    let e = c.entry(b);
    let (w, base) = (e.width as u64, e.min as u32);
    let out = &mut out[..pos.len()];
    if w == 0 {
        out.fill(base as i32);
        return;
    }
    let (inp, mask) = (c.words(b), (1u64 << w) - 1);
    for (o, &p) in out.iter_mut().zip(pos) {
        let bit = p as u64 * w;
        let (idx, sh) = ((bit >> 6) as usize, bit & 63);
        let v = unsafe { (*inp.add(idx) >> sh) | (*inp.add(idx + 1) << 1 << (63 - sh)) };
        *o = ((v & mask) as u32).wrapping_add(base) as i32;
    }
}

// ------------------------------------------------------------------------------------------------ hachage
#[inline]
fn load64(p: *const u8) -> u64 {
    unsafe { (p as *const u64).read_unaligned() }
}
#[inline]
fn hash64(k: u64) -> u64 {
    let k = k.wrapping_mul(K1);
    k ^ (k >> 32)
}
/// Octets : deux voies de mots de 64 bits ; le dernier mot, incomplet, est masqué (8 octets lisibles après la fin).
#[inline]
fn hash_bytes(mut p: *const u8, mut n: usize) -> u64 {
    let (mut h1, mut h2) = (K1 ^ n as u64, K2);
    unsafe {
        while n >= 16 {
            h1 = (h1.rotate_left(5) ^ load64(p)).wrapping_mul(K1);
            h2 = (h2.rotate_left(5) ^ load64(p.add(8))).wrapping_mul(K2);
            p = p.add(16);
            n -= 16;
        }
        if n >= 8 {
            h1 = (h1.rotate_left(5) ^ load64(p)).wrapping_mul(K1);
            p = p.add(8);
            n -= 8;
        }
        if n > 0 {
            h2 = (h2.rotate_left(5) ^ (load64(p) & ((1u64 << (8 * n)) - 1))).wrapping_mul(K2);
        }
    }
    let h = (h1 ^ h2.rotate_left(32)).wrapping_mul(K1);
    let h = h ^ (h >> 32);
    if h != 0 { h } else { 1 } // 0 marque une case vide
}
#[inline]
fn part_of(h: u64) -> usize {
    (h >> (64 - PBITS)) as usize
}

// ------------------------------------------------------------------------------------------------ table de hachage
// Adressage ouvert, sondage linéaire, capacité en puissance de deux, clé et valeur dans la même case ; doublement
// quand la table est à moitié pleine. Clés entières positives ou nulles ; -1 marque une case vide.
fn pow2_for(n: u64) -> u64 {
    let mut cap = 16;
    while cap < 2 * n {
        cap *= 2;
    }
    cap
}
/// Capacité de départ d'une table d'agrégation qui recevra n tuples ; elle double ensuite à la demande.
fn pow2_start(n: u64) -> u64 {
    pow2_for(n / 8)
}

#[repr(C)]
#[derive(Clone, Copy)]
struct Cell {
    key: i64,
    val: i64,
}
#[derive(Clone, Copy)]
struct Map {
    cells: *mut Cell,
    mask: u64,
    count: u64,
    arena: *mut Arena,
}
unsafe impl Sync for Map {}
unsafe impl Send for Map {}
impl Map {
    fn new(a: &mut Arena, cap: u64) -> Map {
        let cells = a.array::<Cell>(cap as usize);
        unsafe { std::ptr::write_bytes(cells, 0xFF, cap as usize) };
        Map { cells, mask: cap - 1, count: 0, arena: a }
    }
    #[inline]
    fn cell(&self, i: u64) -> *mut Cell {
        unsafe { self.cells.add(i as usize) }
    }
    /// Case de la clé, dont h est le hash64 ; None si elle manque.
    #[inline]
    fn find_h(&self, key: i64, h: u64) -> Option<&Cell> {
        let mut i = h & self.mask;
        loop {
            let c = unsafe { &*self.cell(i) };
            if c.key == key {
                return Some(c);
            }
            if c.key == -1 {
                return None;
            }
            i = (i + 1) & self.mask;
        }
    }
    #[inline]
    fn find(&self, key: i64) -> Option<&Cell> {
        self.find_h(key, hash64(key as u64))
    }
    fn grow(&mut self) {
        let old = *self;
        *self = Map::new(unsafe { &mut *old.arena }, 2 * (old.mask + 1));
        for j in 0..=old.mask {
            let c = unsafe { *old.cell(j) };
            if c.key != -1 {
                let mut i = hash64(c.key as u64) & self.mask;
                while unsafe { (*self.cell(i)).key } != -1 {
                    i = (i + 1) & self.mask;
                }
                unsafe { *self.cell(i) = c };
            }
        }
        self.count = old.count;
    }
    /// Rend la case de la clé, créée avec la valeur 0 si elle manquait (le booléen le dit).
    #[inline]
    fn upsert_fresh(&mut self, key: i64) -> (&mut Cell, bool) {
        if (self.count + 1) * 2 > self.mask + 1 {
            self.grow();
        }
        let mut i = hash64(key as u64) & self.mask;
        loop {
            let c = unsafe { &mut *self.cell(i) };
            if c.key == key {
                return (c, false);
            }
            if c.key == -1 {
                *c = Cell { key, val: 0 };
                self.count += 1;
                return (c, true);
            }
            i = (i + 1) & self.mask;
        }
    }
    #[inline]
    fn upsert(&mut self, key: i64) -> &mut Cell {
        self.upsert_fresh(key).0
    }
    fn each(&self, mut f: impl FnMut(&Cell)) {
        for j in 0..=self.mask {
            let c = unsafe { &*self.cell(j) };
            if c.key != -1 {
                f(c);
            }
        }
    }
}

/// Filtre de Bloom par blocs, devant les sondes de semi-jointure : 16 bits par clé, deux bits dans un même mot de
/// 64 bits. Un refus est sûr ; une acceptation se confirme dans la table.
#[derive(Clone, Copy)]
struct Bloom {
    bits: *mut u64,
    mask: u64,
}
unsafe impl Sync for Bloom {}
impl Bloom {
    fn new(a: &mut Arena, nkeys: u64) -> Bloom {
        let mut words = 64;
        while words * 4 < nkeys {
            words *= 2;
        }
        let bits = a.array::<u64>(words as usize);
        unsafe { std::ptr::write_bytes(bits, 0, words as usize) };
        Bloom { bits, mask: words - 1 }
    }
    #[inline]
    fn two(h: u64) -> u64 {
        1u64 << (h & 63) | 1u64 << ((h >> 6) & 63)
    }
    #[inline]
    fn add(&mut self, h: u64) {
        unsafe { *self.bits.add(((h >> 12) & self.mask) as usize) |= Bloom::two(h) }
    }
    #[inline]
    fn test(&self, h: u64) -> bool {
        let m = Bloom::two(h);
        unsafe { *self.bits.add(((h >> 12) & self.mask) as usize) & m == m }
    }
}

/// Même table pour des clés faites d'un entier et d'une chaîne : la case garde le hachage, l'entier, la position et
/// la longueur de la chaîne, et un compte. Hachage nul : case vide.
#[repr(C)]
#[derive(Clone, Copy)]
struct SCell {
    hash: u64,
    ikey: i64,
    pos: u64,
    len: u32,
    count: u32,
}
#[derive(Clone, Copy)]
struct SMap {
    cells: *mut SCell,
    mask: u64,
    n: u64,
    arena: *mut Arena,
    bytes: *const u8,
}
impl SMap {
    fn new(a: &mut Arena, cap: u64, bytes: *const u8) -> SMap {
        let cells = a.array::<SCell>(cap as usize);
        unsafe { std::ptr::write_bytes(cells, 0, cap as usize) };
        SMap { cells, mask: cap - 1, n: 0, arena: a, bytes }
    }
    #[inline]
    fn cell(&self, i: u64) -> *mut SCell {
        unsafe { self.cells.add(i as usize) }
    }
    fn grow(&mut self) {
        let old = *self;
        *self = SMap::new(unsafe { &mut *old.arena }, 2 * (old.mask + 1), old.bytes);
        for j in 0..=old.mask {
            let c = unsafe { *old.cell(j) };
            if c.hash != 0 {
                let mut i = c.hash & self.mask;
                while unsafe { (*self.cell(i)).hash } != 0 {
                    i = (i + 1) & self.mask;
                }
                unsafe { *self.cell(i) = c };
            }
        }
        self.n = old.n;
    }
    #[inline]
    fn add(&mut self, hash: u64, ikey: i64, pos: u64, len: u32) {
        if (self.n + 1) * 2 > self.mask + 1 {
            self.grow();
        }
        let mut i = hash & self.mask;
        loop {
            let c = unsafe { &mut *self.cell(i) };
            if c.hash == hash && c.ikey == ikey && c.len == len && unsafe {
                std::slice::from_raw_parts(self.bytes.add(c.pos as usize), len as usize)
                    == std::slice::from_raw_parts(self.bytes.add(pos as usize), len as usize)
            } {
                c.count += 1;
                return;
            }
            if c.hash == 0 {
                *c = SCell { hash, ikey, pos, len, count: 1 };
                self.n += 1;
                return;
            }
            i = (i + 1) & self.mask;
        }
    }
}

// ------------------------------------------------------------------------------------------------ deux niveaux
// Les primitives du module `level` ont une forme portable, ici, et une forme spécialisée, dans special.rs.
#[repr(C)]
#[derive(Clone, Copy, Default)]
struct Agg1 {
    qty: i64,
    base: i64,
    disc_price: i64,
    charge: i64,
    disc: i64,
    count: i64,
    pad: [i64; 2],
} // un groupe de T1
#[repr(C)]
struct PChunk {
    next: *mut PChunk,
    used: u32,
    pad: u32,
    fill: [u8; 48],
} // 64 octets, puis CHUNK octets de tuples

#[cfg(special)]
#[path = "special.rs"]
mod level;

#[cfg(not(special))]
mod level {
    use super::*;

    pub const LEVEL: &str = "p";
    /// Ni préchargement ni recherche par 64 positions à ce niveau : ces appels disparaissent à la compilation.
    pub const PREFETCH: bool = false;
    pub const AHEAD: usize = 16;
    pub const SEARCH_STEP: usize = 0;
    #[inline(always)]
    pub fn prefetch<T>(_: *const T) {}
    pub unsafe fn search_candidates(_: *const u8, _: usize, _: u8, _: u8) -> u64 {
        0
    }

    #[inline]
    pub fn unpack(c: &Col, b: usize, start: usize, n: usize, out: &mut [i32]) {
        unpack_portable(c, b, start, n, out)
    }

    /// Sélection. Positions (base + i) des valeurs v[i] comprises entre lo et hi, bornes comprises ; sans branchement.
    #[inline]
    pub fn sel_between(v: &[i32], lo: i32, hi: i32, base: u32, pos: &mut [i32]) -> usize {
        assert!(pos.len() >= v.len());
        let mut k = 0;
        for (i, &x) in v.iter().enumerate() {
            unsafe { *pos.get_unchecked_mut(k) = (base + i as u32) as i32 };
            k += ((x >= lo) & (x <= hi)) as usize;
        }
        k
    }
    /// Parmi les entrées (position, charge) : garde celles dont la valeur v[i] est entre lo et hi.
    #[inline]
    pub fn keep_between(v: &[i32], pos_in: &[i32], pay_in: &[i32], lo: i32, hi: i32, pos_out: &mut [i32], pay_out: &mut [i32]) -> usize {
        let n = v.len();
        assert!(pos_in.len() >= n && pay_in.len() >= n && pos_out.len() >= n && pay_out.len() >= n);
        let mut k = 0;
        for i in 0..n {
            unsafe {
                *pos_out.get_unchecked_mut(k) = *pos_in.get_unchecked(i);
                *pay_out.get_unchecked_mut(k) = *pay_in.get_unchecked(i);
                k += ((*v.get_unchecked(i) >= lo) & (*v.get_unchecked(i) <= hi)) as usize;
            }
        }
        k
    }

    /// Agrégation de T1 : un vecteur de n lignes dans le tableau des six groupes ; avec ship, seules comptent les
    /// lignes dont la date ne dépasse pas cut (vecteur de sélection dans sel).
    #[inline]
    pub fn t1_aggregate(agg: &mut [Agg1; 6], grp: &[i32], qty: &[i32], ext: &[i32], disc: &[i32], dp: &[i64], ch: &[i64],
                        ship: Option<&[i32]>, cut: i32, n: usize, sel: &mut [i32]) {
        assert!(grp.len() >= n && qty.len() >= n && ext.len() >= n && disc.len() >= n && dp.len() >= n && ch.len() >= n);
        let mut add = |i: usize| unsafe {
            let g = agg.get_unchecked_mut(*grp.get_unchecked(i) as usize);
            g.qty += *qty.get_unchecked(i) as i64;
            g.base += *ext.get_unchecked(i) as i64;
            g.disc_price += *dp.get_unchecked(i);
            g.charge += *ch.get_unchecked(i);
            g.disc += *disc.get_unchecked(i) as i64;
            g.count += 1;
        };
        match ship {
            None => (0..n).for_each(&mut add),
            Some(ship) => {
                let k = sel_between(&ship[..n], i32::MIN, cut, 0, sel);
                sel[..k].iter().for_each(|&i| add(i as usize));
            }
        }
    }

    /// Partitions. Tampons d'un fil : pour chaque partition, une liste de morceaux de CHUNK octets pris dans son arène.
    pub struct Parts {
        cur: [*mut u8; NPART],
        end: [*mut u8; NPART],
        pub head: [*mut PChunk; NPART],
        tail: [*mut PChunk; NPART],
        pub tsize: usize,
        arena: *mut Arena,
    }
    impl Parts {
        pub fn init(&mut self, a: &mut Arena, tsize: usize) {
            unsafe { std::ptr::write_bytes(self, 0, 1) };
            self.tsize = tsize;
            self.arena = a;
        }
        #[cold]
        unsafe fn chunk(&mut self, k: usize) -> *mut u8 {
            unsafe {
                let c = (*self.arena).alloc(size_of::<PChunk>() + CHUNK) as *mut PChunk;
                (*c).next = null_mut();
                (*c).used = 0;
                if self.tail[k].is_null() {
                    self.head[k] = c;
                } else {
                    (*self.tail[k]).used = self.cur[k].offset_from(self.tail[k].add(1) as *mut u8) as u32;
                    (*self.tail[k]).next = c;
                }
                self.tail[k] = c;
                self.cur[k] = c.add(1) as *mut u8;
                self.end[k] = self.cur[k].add(CHUNK / self.tsize * self.tsize);
                self.cur[k]
            }
        }
        /// Écrit le tuple suivant de la partition k.
        #[inline]
        pub fn push<T>(&mut self, k: usize, t: T) {
            unsafe {
                let mut p = *self.cur.get_unchecked(k);
                if p == *self.end.get_unchecked(k) {
                    p = self.chunk(k);
                }
                *self.cur.get_unchecked_mut(k) = p.add(size_of::<T>());
                (p as *mut T).write(t);
            }
        }
        pub fn close(&mut self) {
            for k in 0..NPART {
                if !self.tail[k].is_null() {
                    unsafe { (*self.tail[k]).used = self.cur[k].offset_from(self.tail[k].add(1) as *mut u8) as u32 };
                }
            }
        }
    }
}
use level::*;
unsafe impl Sync for Parts {}
unsafe impl Send for Parts {}

fn parts_count(p: &[Parts], k: usize) -> u64 {
    let mut n = 0;
    for t in p {
        let mut c = t.head[k];
        while !c.is_null() {
            n += unsafe { (*c).used } as u64 / t.tsize as u64;
            c = unsafe { (*c).next };
        }
    }
    n
}
/// Parcours des tuples (de type T) de la partition k dans les tampons de tous les fils : f(tuple, fin du morceau en
/// cours) ; le niveau spécialisé lit la fin pour précharger les tuples à venir.
#[inline]
fn parts_each<T>(p: &[Parts], k: usize, mut f: impl FnMut(*const T, *const T)) {
    for t in p {
        let mut c = t.head[k];
        while !c.is_null() {
            unsafe {
                let mut it = c.add(1) as *const T;
                let end = (c.add(1) as *const u8).add((*c).used as usize) as *const T;
                while it < end {
                    f(it, end);
                    it = it.add(1);
                }
                c = (*c).next;
            }
        }
    }
}

// ------------------------------------------------------------------------------------------------ état des fils
struct Scratch {
    a: [i32; VEC],
    b: [i32; VEC],
    c: [i32; VEC],
    d: [i32; VEC],
    e: [i32; VEC],
    f: [i32; VEC],
    g: [i32; VEC],
    sel: [i32; VEC],
    sel2: [i32; VEC],
    pos: [i32; VEC],
    x: [i64; VEC],
    y: [i64; VEC],
    h: [u64; VEC],
    len: [i32; BLOCK],
    rows: [i32; BLOCK],
}
/// L'état du moteur : la réserve de fils et, pour chaque fil, son arène, ses vecteurs de travail et ses tampons de
/// partition. Pendant une phase, un fil ne touche que les siens ; les tampons de tous se lisent une fois répartis.
struct Engine {
    nt: usize,
    pool: &'static Pool,
    arena: Vec<Slot<Arena>>,
    scratch: Vec<*mut Scratch>,
    parts: Vec<Slot<Parts>>,
    parts2: Vec<Slot<Parts>>,
}
unsafe impl Sync for Engine {}
impl Engine {
    fn new(nt: usize) -> Engine {
        let new_parts = || Slot::new(unsafe { std::mem::zeroed::<Parts>() });
        Engine {
            nt,
            pool: Pool::start(nt),
            arena: (0..nt).map(|_| Slot::new(Arena { first: null_mut(), cur: null_mut() })).collect(),
            scratch: (0..nt)
                .map(|_| {
                    let s = huge_alloc(size_of::<Scratch>()) as *mut Scratch;
                    unsafe { std::ptr::write_bytes(s, 0, 1) };
                    s
                })
                .collect(),
            parts: (0..nt).map(|_| new_parts()).collect(),
            parts2: (0..nt).map(|_| new_parts()).collect(),
        }
    }
    unsafe fn arena(&self, tid: usize) -> &mut Arena {
        unsafe { self.arena[tid].get() }
    }
    unsafe fn scratch(&self, tid: usize) -> &mut Scratch {
        let p = self.scratch[tid];
        unsafe { &mut *p }
    }
    unsafe fn parts(&self, tid: usize) -> &mut Parts {
        unsafe { self.parts[tid].get() }
    }
    unsafe fn parts2(&self, tid: usize) -> &mut Parts {
        unsafe { self.parts2[tid].get() }
    }
    /// Tampons de tous les fils, en lecture, quand la répartition est finie.
    unsafe fn all_parts(&self) -> &[Parts] {
        unsafe { std::slice::from_raw_parts(self.parts.as_ptr() as *const Parts, self.nt) }
    }
    unsafe fn all_parts2(&self) -> &[Parts] {
        unsafe { std::slice::from_raw_parts(self.parts2.as_ptr() as *const Parts, self.nt) }
    }
}

/// Liste d'entiers de 64 bits dans une arène.
struct List {
    v: *mut i64,
    n: usize,
    cap: usize,
    arena: *mut Arena,
}
unsafe impl Send for List {}
impl List {
    fn new(a: &mut Arena) -> List {
        List { v: null_mut(), n: 0, cap: 0, arena: a }
    }
    #[inline]
    fn push(&mut self, x: i64) {
        unsafe {
            if self.n == self.cap {
                let cap = if self.cap > 0 { 2 * self.cap } else { 1024 };
                let v = (*self.arena).array::<i64>(cap);
                if self.n > 0 {
                    std::ptr::copy_nonoverlapping(self.v, v, self.n);
                }
                self.v = v;
                self.cap = cap;
            }
            *self.v.add(self.n) = x;
            self.n += 1;
        }
    }
    fn as_slice(&self) -> &[i64] {
        if self.n == 0 { &[] } else { unsafe { std::slice::from_raw_parts(self.v, self.n) } }
    }
}
/// Vecteurs d'un bloc de `count` lignes : (début dans le bloc, lignes du vecteur).
#[inline]
fn vectors(count: u32) -> impl Iterator<Item = (usize, usize)> {
    let count = count as usize;
    (0..count).step_by(VEC).map(move |st| (st, (count - st).min(VEC)))
}

// ------------------------------------------------------------------------------------------------ résultat
trait Emit {
    fn emit(&self, out: &mut Vec<u8>);
}
impl Emit for &str {
    fn emit(&self, out: &mut Vec<u8>) {
        out.extend_from_slice(self.as_bytes())
    }
}
impl Emit for &[u8] {
    fn emit(&self, out: &mut Vec<u8>) {
        out.extend_from_slice(self)
    }
}
macro_rules! emit_int {
    ($($t:ty)*) => { $(impl Emit for $t {
        fn emit(&self, out: &mut Vec<u8>) { write!(out, "{self}").unwrap() }
    })* };
}
emit_int!(i64 u64 u32);
macro_rules! emit {
    ($out:expr, $($x:expr),+) => {{ $( Emit::emit(&$x, $out); )+ }};
}
fn fnv1a(s: &[u8]) -> u64 {
    s.iter().fold(0xCBF29CE484222325u64, |h, &c| (h ^ c as u64).wrapping_mul(0x100000001B3))
}

// ------------------------------------------------------------------------------------------------ dates
const fn days_from_civil(y: i32, m: i32, d: i32) -> i32 {
    // jours depuis le 1er janvier 1970
    let y = if m <= 2 { y - 1 } else { y };
    let era = (if y >= 0 { y } else { y - 399 }) / 400;
    let yoe = (y - era * 400) as u32;
    let doy = (153 * (m + if m > 2 { -3 } else { 9 }) as u32 + 2) / 5 + d as u32 - 1;
    let doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;
    era * 146097 + doe as i32 - 719468
}
/// Premier jour de chaque année à partir de 1970 : table calculée à la compilation.
static YEAR_START: [i32; 200] = {
    let mut t = [0; 200];
    let mut y = 0;
    while y < 200 {
        t[y] = days_from_civil(1970 + y as i32, 1, 1);
        y += 1;
    }
    t
};
#[inline]
fn year_of(days: i32) -> i64 {
    let mut y = (days / 366) as usize;
    while YEAR_START[y + 1] <= days {
        y += 1;
    }
    1970 + y as i64
}

// ------------------------------------------------------------------------------------------------ sous-chaînes
// Lignes d'un bloc de chaînes qui contiennent l'aiguille (2 octets au moins) : les octets du bloc sont parcourus
// d'un trait, par mots de 8 octets ; un mot est candidat si, à une même position, il porte le premier octet de
// l'aiguille et le mot décalé de sa longueur moins un porte le dernier. Une occurrence compte si elle tient dans
// une ligne, et une ligne compte une fois.
const ONES: u64 = 0x0101010101010101;
const HIGHS: u64 = 0x8080808080808080;
#[inline]
fn zero_bytes(x: u64) -> u64 {
    // bit de poids fort de chaque octet nul de x, exactement
    !(((x & !HIGHS).wrapping_add(!HIGHS)) | x) & HIGHS
}
fn search_block(buf: *const u8, nbytes: usize, len: &[i32], needle: &[u8], rows: &mut [i32]) -> usize {
    let m = needle.len();
    let (mut r, mut k) = (0usize, 0usize);
    let mut row_end = if nbytes > 0 { len[0] as usize } else { 0 };
    let (c0, c1) = (needle[0], needle[m - 1]);
    let (first, last) = (ONES * c0 as u64, ONES * c1 as u64);
    let stop = if nbytes >= m { nbytes - m + 1 } else { 0 }; // positions de départ possibles : [0, stop)
    let mut i = 0;
    while i < stop {
        let (cand, mut next, shift);
        if SEARCH_STEP > 0 && i + SEARCH_STEP + m - 1 <= nbytes {
            // niveau spécialisé : 64 positions d'un coup, un bit candidat par position
            cand = unsafe { search_candidates(buf.add(i), m, c0, c1) };
            if cand == 0 {
                i += SEARCH_STEP;
                continue;
            }
            (next, shift) = (i + SEARCH_STEP, 0);
        } else if i + 8 <= stop {
            // les deux mots sont dans le bloc ; un bit candidat par octet du mot : rang du bit / 8
            cand = zero_bytes(unsafe { (load64(buf.add(i)) ^ first) | (load64(buf.add(i + m - 1)) ^ last) });
            if cand == 0 {
                i += 8;
                continue;
            }
            (next, shift) = (i + 8, 3);
        } else {
            let mut c = 0;
            for j in i..stop {
                if unsafe { *buf.add(j) == c0 && *buf.add(j + m - 1) == c1 } {
                    c |= 0x80u64 << (8 * (j - i));
                }
            }
            (cand, next, shift) = (c, i + 8, 3);
        }
        let mut cand = cand;
        while cand != 0 {
            let at = i + (cand.trailing_zeros() as usize >> shift);
            cand &= cand - 1;
            if unsafe { std::slice::from_raw_parts(buf.add(at + 1), m - 2) } != &needle[1..m - 1] {
                continue;
            }
            while row_end <= at {
                r += 1;
                row_end += len[r] as usize;
            }
            if at + m <= row_end {
                rows[k] = r as i32;
                k += 1;
                next = row_end; // la suite de la ligne est sautée
                break;
            }
        }
        i = next;
    }
    k
}
/// Longueurs d'un bloc de chaînes (dans len) ; rend le nombre de ses octets.
fn block_lengths(c: &Col, b: usize, len: &mut [i32]) -> usize {
    let n = c.entry(b).count as usize;
    unpack(c, b, 0, n, len);
    len[..n].iter().map(|&l| l as usize).sum()
}

// ------------------------------------------------------------------------------------------------ dix premiers
#[derive(Clone, Copy)]
struct Top {
    count: u32,
    len: u32,
    ikey: i64,
    pos: u64,
}
struct Top10 {
    t: [Top; 10],
    n: usize,
    str: Col,
}
impl Top10 {
    fn new(str: Col) -> Top10 {
        Top10 { t: [Top { count: 0, len: 0, ikey: 0, pos: 0 }; 10], n: 0, str }
    }
    /// Ordre : compte décroissant, entier croissant, chaîne croissante.
    fn before(&self, a: &Top, b: &Top) -> bool {
        if a.count != b.count {
            return a.count > b.count;
        }
        if a.ikey != b.ikey {
            return a.ikey < b.ikey;
        }
        self.str.bytes(a.pos, a.len as usize) < self.str.bytes(b.pos, b.len as usize)
    }
    fn add(&mut self, x: Top) {
        if self.n == 10 && !self.before(&x, &self.t[9]) {
            return;
        }
        let mut i = if self.n < 10 {
            self.n += 1;
            self.n - 1
        } else {
            9
        };
        while i > 0 && self.before(&x, &self.t[i - 1]) {
            self.t[i] = self.t[i - 1];
            i -= 1;
        }
        self.t[i] = x;
    }
}

// ================================================================================================ T1 (TPC-H Q1)
struct T1 {
    ship: Col,
    rf: Col,
    ls: Col,
    qty: Col,
    ext: Col,
    disc: Col,
    tax: Col,
    cut: i32,
}
impl T1 {
    fn open(d: &str) -> T1 {
        let col = |name| Col::open(d, "lineitem", name);
        T1 {
            ship: col("l_shipdate"), rf: col("l_returnflag"), ls: col("l_linestatus"), qty: col("l_quantity"),
            ext: col("l_extendedprice"), disc: col("l_discount"), tax: col("l_tax"), cut: days_from_civil(1998, 9, 2),
        }
    }
    fn run(&self, eng: &Engine, out: &mut Vec<u8>) {
        let ctr = Counter::new(self.ship.nblocks);
        let aggs = eng.pool.run(|tid| {
            let Scratch { a, b, c, d, e, f, g, sel, pos, x, y, .. } = unsafe { eng.scratch(tid) };
            let mut agg = [Agg1::default(); 6];
            while let Some(blk) = ctr.take() {
                let en = self.ship.entry(blk);
                if en.min > self.cut as i64 {
                    continue; // bloc exclu par sa carte de zones
                }
                let all = en.max <= self.cut as i64; // bloc retenu en entier : le filtre n'est pas évalué
                for (st, n) in vectors(en.count) {
                    unpack(&self.rf, blk, st, n, a);
                    unpack(&self.ls, blk, st, n, b);
                    unpack(&self.qty, blk, st, n, c);
                    unpack(&self.ext, blk, st, n, d);
                    unpack(&self.disc, blk, st, n, e);
                    unpack(&self.tax, blk, st, n, f);
                    for ((x, &d), &e) in x[..n].iter_mut().zip(&d[..n]).zip(&e[..n]) {
                        *x = d as i64 * (100 - e) as i64;
                    }
                    for ((y, &x), &f) in y[..n].iter_mut().zip(&x[..n]).zip(&f[..n]) {
                        *y = x * (100 + f) as i64;
                    }
                    for ((g, &a), &b) in g[..n].iter_mut().zip(&a[..n]).zip(&b[..n]) {
                        *g = a * 2 + b;
                    }
                    let ship = if all {
                        None
                    } else {
                        unpack(&self.ship, blk, st, n, pos);
                        Some(&pos[..])
                    };
                    t1_aggregate(&mut agg, g, c, d, e, x, y, ship, self.cut, n, sel);
                }
            }
            agg
        });
        for g in 0..6 {
            let mut a = Agg1::default();
            for x in aggs.iter().map(|t| &t[g]) {
                a.qty += x.qty;
                a.base += x.base;
                a.disc_price += x.disc_price;
                a.charge += x.charge;
                a.disc += x.disc;
                a.count += x.count;
            }
            if a.count == 0 {
                continue;
            }
            emit!(out, self.rf.dict(g as u32 / 2), "|", self.ls.dict(g as u32 % 2), "|", a.qty, "|", a.base, "|",
                  a.disc_price, "|", a.charge, "|", a.disc, "|", a.count, "\n");
        }
    }
}

// ================================================================================================ T6 (TPC-H Q6)
struct T6 {
    ship: Col,
    disc: Col,
    qty: Col,
    ext: Col,
    lo: i32,
    hi: i32,
}
impl T6 {
    fn open(d: &str) -> T6 {
        let col = |name| Col::open(d, "lineitem", name);
        T6 {
            ship: col("l_shipdate"), disc: col("l_discount"), qty: col("l_quantity"), ext: col("l_extendedprice"),
            lo: days_from_civil(1994, 1, 1), hi: days_from_civil(1995, 1, 1),
        }
    }
    fn run(&self, eng: &Engine, out: &mut Vec<u8>) {
        let ctr = Counter::new(self.ship.nblocks);
        let sums = eng.pool.run(|tid| {
            let Scratch { a, b, c, d, e, f, sel, sel2, pos, .. } = unsafe { eng.scratch(tid) };
            let mut sum = 0i64;
            while let Some(blk) = ctr.take() {
                let en = self.ship.entry(blk);
                if en.max < self.lo as i64 || en.min >= self.hi as i64 {
                    continue;
                }
                for (st, n) in vectors(en.count) {
                    unpack(&self.ship, blk, st, n, a);
                    let k = sel_between(&a[..n], self.lo, self.hi - 1, st as u32, pos);
                    if k == 0 {
                        continue;
                    }
                    unpack_sel(&self.disc, blk, &pos[..k], b);
                    let k2 = keep_between(&b[..k], pos, b, 5, 7, sel, c);
                    if k2 == 0 {
                        continue;
                    }
                    unpack_sel(&self.qty, blk, &sel[..k2], d);
                    let k3 = keep_between(&d[..k2], sel, c, i32::MIN, 2399, sel2, e);
                    if k3 == 0 {
                        continue;
                    }
                    unpack_sel(&self.ext, blk, &sel2[..k3], f);
                    sum += f[..k3].iter().zip(&e[..k3]).map(|(&p, &d)| p as i64 * d as i64).sum::<i64>();
                }
            }
            sum
        });
        emit!(out, sums.iter().sum::<i64>(), "\n");
    }
}

// ================================================================================================ T9 (TPC-H Q9)
// 1. part : noms qui contiennent « green » -> ensemble de pièces (table et filtre de Bloom) ;
// 2. partsupp : lignes de ces pièces -> (pièce, fournisseur) -> coût ; 3. supplier -> nation ;
// 4. lineitem : lignes de ces pièces, montant et nation, réparties par commande ;
// 5. orders : (commande, date) réparties de même ; 6. par partition : table des lignes de lineitem, sondée par les
//    commandes ; agrégat par nation et année.
#[repr(C)]
#[derive(Clone, Copy)]
struct T9Tuple {
    okey: i32,
    nation: i32,
    amount: i64,
}
#[repr(C)]
#[derive(Clone, Copy)]
struct T9Order {
    okey: i32,
    date: i32,
}
struct T9 {
    p_partkey: Col,
    p_name: Col,
    ps_partkey: Col,
    ps_suppkey: Col,
    ps_cost: Col,
    s_suppkey: Col,
    s_nationkey: Col,
    n_nationkey: Col,
    n_name: Col,
    l_partkey: Col,
    l_suppkey: Col,
    l_orderkey: Col,
    l_qty: Col,
    l_ext: Col,
    l_disc: Col,
    o_orderkey: Col,
    o_orderdate: Col,
}
/// Positions (dans le bloc) et clés des lignes d'un vecteur dont la clé est dans l'ensemble (filtre, puis table).
#[inline]
fn semi(set: &Map, filter: &Bloom, key: &[i32], st: usize, pos: &mut [i32], out: &mut [i32]) -> usize {
    let mut k = 0;
    for (i, &x) in key.iter().enumerate() {
        let h = hash64(x as u64);
        if filter.test(h) && set.find_h(x as i64, h).is_some() {
            pos[k] = (st + i) as i32;
            out[k] = x;
            k += 1;
        }
    }
    k
}
impl T9 {
    fn open(d: &str) -> T9 {
        let col = |table, name| Col::open(d, table, name);
        T9 {
            p_partkey: col("part", "p_partkey"), p_name: col("part", "p_name"),
            ps_partkey: col("partsupp", "ps_partkey"), ps_suppkey: col("partsupp", "ps_suppkey"),
            ps_cost: col("partsupp", "ps_supplycost"), s_suppkey: col("supplier", "s_suppkey"),
            s_nationkey: col("supplier", "s_nationkey"), n_nationkey: col("nation", "n_nationkey"),
            n_name: col("nation", "n_name"), l_partkey: col("lineitem", "l_partkey"),
            l_suppkey: col("lineitem", "l_suppkey"), l_orderkey: col("lineitem", "l_orderkey"),
            l_qty: col("lineitem", "l_quantity"), l_ext: col("lineitem", "l_extendedprice"),
            l_disc: col("lineitem", "l_discount"), o_orderkey: col("orders", "o_orderkey"),
            o_orderdate: col("orders", "o_orderdate"),
        }
    }
    fn run(&self, eng: &Engine, out: &mut Vec<u8>) {
        // 1. pièces dont le nom contient « green »
        let ctr = Counter::new(self.p_name.nblocks);
        let lists = eng.pool.run(|tid| {
            let s = unsafe { eng.scratch(tid) };
            let mut l = List::new(unsafe { eng.arena(tid) });
            while let Some(b) = ctr.take() {
                let nbytes = block_lengths(&self.p_name, b, &mut s.len);
                let buf = unsafe { self.p_name.aux.add(self.p_name.entry(b).aux_off as usize) };
                let k = search_block(buf, nbytes, &s.len, b"green", &mut s.rows);
                for i in (0..k).step_by(VEC) {
                    let n = (k - i).min(VEC);
                    unpack_sel(&self.p_partkey, b, &s.rows[i..i + n], &mut s.a);
                    s.a[..n].iter().for_each(|&key| l.push(key as i64));
                }
            }
            l
        });
        let n: usize = lists.iter().map(|l| l.n).sum();
        let mut part = Map::new(unsafe { eng.arena(0) }, pow2_for(n as u64));
        let mut fpart = Bloom::new(unsafe { eng.arena(0) }, n as u64);
        for &key in lists.iter().flat_map(|l| l.as_slice()) {
            part.upsert(key);
            fpart.add(hash64(key as u64));
        }
        // 2. partsupp de ces pièces : (pièce, fournisseur) -> coût
        let ctr = Counter::new(self.ps_partkey.nblocks);
        let lists = eng.pool.run(|tid| {
            let Scratch { a, b, c, d, pos, .. } = unsafe { eng.scratch(tid) };
            let mut l1 = List::new(unsafe { eng.arena(tid) });
            let mut l2 = List::new(unsafe { eng.arena(tid) });
            while let Some(blk) = ctr.take() {
                for (st, n) in vectors(self.ps_partkey.entry(blk).count) {
                    unpack(&self.ps_partkey, blk, st, n, a);
                    let k = semi(&part, &fpart, &a[..n], st, pos, b);
                    if k == 0 {
                        continue;
                    }
                    unpack_sel(&self.ps_suppkey, blk, &pos[..k], c);
                    unpack_sel(&self.ps_cost, blk, &pos[..k], d);
                    for i in 0..k {
                        l1.push((b[i] as i64) << 32 | c[i] as i64);
                        l2.push(d[i] as i64);
                    }
                }
            }
            (l1, l2)
        });
        let n: usize = lists.iter().map(|l| l.0.n).sum();
        let mut ps = Map::new(unsafe { eng.arena(0) }, pow2_for(n as u64));
        for (l1, l2) in &lists {
            for (&key, &cost) in l1.as_slice().iter().zip(l2.as_slice()) {
                ps.upsert(key).val = cost;
            }
        }
        // 3. fournisseur -> nation
        let mut supp = Map::new(unsafe { eng.arena(0) }, pow2_for(self.s_suppkey.nrows));
        {
            let s = unsafe { eng.scratch(0) };
            for blk in 0..self.s_suppkey.nblocks as usize {
                for (st, n) in vectors(self.s_suppkey.entry(blk).count) {
                    unpack(&self.s_suppkey, blk, st, n, &mut s.a);
                    unpack(&self.s_nationkey, blk, st, n, &mut s.b);
                    for i in 0..n {
                        supp.upsert(s.a[i] as i64).val = s.b[i] as i64;
                    }
                }
            }
        }
        // 4. lineitem de ces pièces : (commande, nation, montant), réparti par commande
        let ctr = Counter::new(self.l_partkey.nblocks);
        eng.pool.run(|tid| {
            let Scratch { a, b, c, d, e, f, g, pos, .. } = unsafe { eng.scratch(tid) };
            let p = unsafe { eng.parts(tid) };
            p.init(unsafe { eng.arena(tid) }, size_of::<T9Tuple>());
            while let Some(blk) = ctr.take() {
                for (st, n) in vectors(self.l_partkey.entry(blk).count) {
                    unpack(&self.l_partkey, blk, st, n, a);
                    let k = semi(&part, &fpart, &a[..n], st, pos, b);
                    if k == 0 {
                        continue;
                    }
                    unpack_sel(&self.l_suppkey, blk, &pos[..k], c);
                    unpack_sel(&self.l_orderkey, blk, &pos[..k], d);
                    unpack_sel(&self.l_qty, blk, &pos[..k], e);
                    unpack_sel(&self.l_ext, blk, &pos[..k], f);
                    unpack_sel(&self.l_disc, blk, &pos[..k], g);
                    if PREFETCH {
                        // les cases des deux tables sont préchargées pour tout le vecteur
                        for i in 0..k {
                            prefetch(ps.cell(hash64(((b[i] as i64) << 32 | c[i] as i64) as u64) & ps.mask));
                            prefetch(supp.cell(hash64(c[i] as u64) & supp.mask));
                        }
                    }
                    for i in 0..k {
                        let cost = ps.find((b[i] as i64) << 32 | c[i] as i64).unwrap().val;
                        let nation = supp.find(c[i] as i64).unwrap().val;
                        let amount = f[i] as i64 * (100 - g[i]) as i64 - cost * e[i] as i64;
                        p.push(part_of(hash64(d[i] as u64)), T9Tuple { okey: d[i], nation: nation as i32, amount });
                    }
                }
            }
            p.close();
        });
        // 5. orders : (commande, date), réparti de même
        let ctr = Counter::new(self.o_orderkey.nblocks);
        eng.pool.run(|tid| {
            let Scratch { a, b, h, .. } = unsafe { eng.scratch(tid) };
            let p = unsafe { eng.parts2(tid) };
            p.init(unsafe { eng.arena(tid) }, size_of::<T9Order>());
            while let Some(blk) = ctr.take() {
                for (st, n) in vectors(self.o_orderkey.entry(blk).count) {
                    unpack(&self.o_orderkey, blk, st, n, a);
                    unpack(&self.o_orderdate, blk, st, n, b);
                    for (h, &key) in h[..n].iter_mut().zip(&a[..n]) {
                        *h = hash64(key as u64);
                    }
                    for i in 0..n {
                        p.push(part_of(h[i]), T9Order { okey: a[i], date: b[i] });
                    }
                }
            }
            p.close();
        });
        // 6. jointure par partition ; agrégat par nation et année
        let ctr = Counter::new(NPART as u64);
        let (lines, orders) = unsafe { (eng.all_parts(), eng.all_parts2()) };
        let aggs = eng.pool.run(|tid| {
            let arena = unsafe { eng.arena(tid) };
            let mut agg = Map::new(arena, 1024);
            while let Some(k) = ctr.take() {
                let n = parts_count(lines, k) as usize;
                if n == 0 {
                    continue;
                }
                let tu = arena.array::<T9Tuple>(n);
                let next = arena.array::<i32>(n);
                // commande -> rang de son dernier tuple ; next chaîne les tuples d'une même commande
                let mut m = Map::new(arena, pow2_for(n as u64));
                let mut i = 0;
                parts_each::<T9Tuple>(lines, k, |t, _| unsafe {
                    let (c, fresh) = m.upsert_fresh((*t).okey as i64);
                    *tu.add(i) = *t;
                    *next.add(i) = if fresh { -1 } else { c.val as i32 };
                    c.val = i as i64;
                    i += 1;
                });
                parts_each::<T9Order>(orders, k, |o, end| unsafe {
                    if PREFETCH && o.add(AHEAD) < end {
                        prefetch(m.cell(hash64((*o.add(AHEAD)).okey as u64) & m.mask));
                    }
                    let Some(c) = m.find((*o).okey as i64) else { return };
                    let year = year_of((*o).date);
                    let mut j = c.val as i32;
                    while j >= 0 {
                        let t = &*tu.add(j as usize);
                        agg.upsert((t.nation as i64) << 16 | year).val += t.amount;
                        j = *next.add(j as usize);
                    }
                });
            }
            agg
        });
        // fusion ; nation -> nom ; tri par nom puis année décroissante
        let mut total = Map::new(unsafe { eng.arena(0) }, 1024);
        for agg in &aggs {
            agg.each(|c| total.upsert(c.key).val += c.val);
        }
        let mut nat = Map::new(unsafe { eng.arena(0) }, 64);
        let s = unsafe { eng.scratch(0) };
        let nn = self.n_nationkey.nrows as usize;
        unpack(&self.n_nationkey, 0, 0, nn, &mut s.a);
        unpack(&self.n_name, 0, 0, nn, &mut s.b);
        for i in 0..nn {
            nat.upsert(s.a[i] as i64).val = s.b[i] as i64;
        }
        let mut rows: Vec<(&[u8], i64, i64)> = Vec::with_capacity(total.count as usize);
        total.each(|c| rows.push((self.n_name.dict(nat.find(c.key >> 16).unwrap().val as u32), c.key & 0xFFFF, c.val)));
        rows.sort_unstable_by(|a, b| a.0.cmp(b.0).then(b.1.cmp(&a.1)));
        for (name, year, sum) in rows {
            emit!(out, name, "|", year, "|", sum, "\n");
        }
    }
}

// ================================================================================================ T18 (TPC-H Q18)
#[repr(C)]
#[derive(Clone, Copy)]
struct KQ {
    key: i32,
    qty: i32,
}
struct T18Row {
    okey: i64,
    cust: i64,
    date: i64,
    price: i64,
    sum: i64,
    name: &'static [u8],
}
struct T18 {
    l_orderkey: Col,
    l_qty: Col,
    o_orderkey: Col,
    o_custkey: Col,
    o_orderdate: Col,
    o_totalprice: Col,
    c_custkey: Col,
    c_name: Col,
}
impl T18 {
    fn open(d: &str) -> T18 {
        let col = |table, name| Col::open(d, table, name);
        T18 {
            l_orderkey: col("lineitem", "l_orderkey"), l_qty: col("lineitem", "l_quantity"),
            o_orderkey: col("orders", "o_orderkey"), o_custkey: col("orders", "o_custkey"),
            o_orderdate: col("orders", "o_orderdate"), o_totalprice: col("orders", "o_totalprice"),
            c_custkey: col("customer", "c_custkey"), c_name: col("customer", "c_name"),
        }
    }
    fn run(&self, eng: &Engine, out: &mut Vec<u8>) {
        // 1. lineitem réparti par commande
        let ctr = Counter::new(self.l_orderkey.nblocks);
        eng.pool.run(|tid| {
            let Scratch { a, b, h, .. } = unsafe { eng.scratch(tid) };
            let p = unsafe { eng.parts(tid) };
            p.init(unsafe { eng.arena(tid) }, size_of::<KQ>());
            while let Some(blk) = ctr.take() {
                for (st, n) in vectors(self.l_orderkey.entry(blk).count) {
                    unpack(&self.l_orderkey, blk, st, n, a);
                    unpack(&self.l_qty, blk, st, n, b);
                    for (h, &key) in h[..n].iter_mut().zip(&a[..n]) {
                        *h = hash64(key as u64);
                    }
                    for i in 0..n {
                        p.push(part_of(h[i]), KQ { key: a[i], qty: b[i] });
                    }
                }
            }
            p.close();
        });
        // 2. par partition : somme par commande ; 3. celles de plus de 300 unités
        let ctr = Counter::new(NPART as u64);
        let lines = unsafe { eng.all_parts() };
        let lists = eng.pool.run(|tid| {
            let arena = unsafe { eng.arena(tid) };
            let mut l = List::new(arena);
            while let Some(k) = ctr.take() {
                let mut m = Map::new(arena, pow2_start(parts_count(lines, k)));
                parts_each::<KQ>(lines, k, |t, end| unsafe {
                    if PREFETCH && t.add(AHEAD) < end {
                        prefetch(m.cell(hash64((*t.add(AHEAD)).key as u64) & m.mask));
                    }
                    m.upsert((*t).key as i64).val += (*t).qty as i64;
                });
                m.each(|c| {
                    if c.val > 30000 {
                        l.push(c.key)
                    }
                });
            }
            l
        });
        let n: usize = lists.iter().map(|l| l.n).sum();
        let mut big = Map::new(unsafe { eng.arena(0) }, pow2_for(n as u64));
        let mut fbig = Bloom::new(unsafe { eng.arena(0) }, n as u64);
        for &key in lists.iter().flat_map(|l| l.as_slice()) {
            big.upsert(key);
            fbig.add(hash64(key as u64));
        }
        // 4. leurs lignes dans orders : client, date, prix
        let ctr = Counter::new(self.o_orderkey.nblocks);
        let lists = eng.pool.run(|tid| {
            let Scratch { a, b, c, d, e, pos, .. } = unsafe { eng.scratch(tid) };
            let mut l: [List; 4] = std::array::from_fn(|_| List::new(unsafe { eng.arena(tid) }));
            while let Some(blk) = ctr.take() {
                for (st, n) in vectors(self.o_orderkey.entry(blk).count) {
                    unpack(&self.o_orderkey, blk, st, n, a);
                    let k = semi(&big, &fbig, &a[..n], st, pos, b);
                    if k == 0 {
                        continue;
                    }
                    unpack_sel(&self.o_custkey, blk, &pos[..k], c);
                    unpack_sel(&self.o_orderdate, blk, &pos[..k], d);
                    unpack_sel(&self.o_totalprice, blk, &pos[..k], e);
                    for i in 0..k {
                        l[0].push(b[i] as i64);
                        l[1].push(c[i] as i64);
                        l[2].push(d[i] as i64);
                        l[3].push(e[i] as i64);
                    }
                }
            }
            l
        });
        let mut rows: Vec<T18Row> = Vec::with_capacity(n);
        let mut cust = Map::new(unsafe { eng.arena(0) }, pow2_for(n as u64));
        let mut fcust = Bloom::new(unsafe { eng.arena(0) }, n as u64);
        for l in &lists {
            for i in 0..l[0].n {
                let (okey, c, date, price) = (l[0].as_slice()[i], l[1].as_slice()[i], l[2].as_slice()[i], l[3].as_slice()[i]);
                rows.push(T18Row { okey, cust: c, date, price, sum: 0, name: &[] });
                cust.upsert(c);
                fcust.add(hash64(c as u64));
            }
        }
        // 5. leurs clients : position et longueur de leur nom
        let ctr = Counter::new(self.c_custkey.nblocks);
        let lists = eng.pool.run(|tid| {
            let Scratch { a, b, .. } = unsafe { eng.scratch(tid) };
            let mut l: [List; 3] = std::array::from_fn(|_| List::new(unsafe { eng.arena(tid) }));
            while let Some(blk) = ctr.take() {
                let mut pos = self.c_name.entry(blk).aux_off;
                for (st, n) in vectors(self.c_custkey.entry(blk).count) {
                    unpack(&self.c_custkey, blk, st, n, a);
                    unpack(&self.c_name, blk, st, n, b);
                    for i in 0..n {
                        let h = hash64(a[i] as u64);
                        if fcust.test(h) && cust.find_h(a[i] as i64, h).is_some() {
                            l[0].push(a[i] as i64);
                            l[1].push(pos as i64);
                            l[2].push(b[i] as i64);
                        }
                        pos += b[i] as u64;
                    }
                }
            }
            l
        });
        let mut name = Map::new(unsafe { eng.arena(0) }, pow2_for(n as u64)); // client -> rang dans les listes
        let mut names: Vec<&'static [u8]> = Vec::with_capacity(n);
        for l in &lists {
            for i in 0..l[0].n {
                name.upsert(l[0].as_slice()[i]).val = names.len() as i64;
                names.push(self.c_name.bytes(l[1].as_slice()[i] as u64, l[2].as_slice()[i] as usize));
            }
        }
        // 6. second parcours de lineitem : somme des quantités des commandes retenues
        let ctr = Counter::new(self.l_orderkey.nblocks);
        let sums = eng.pool.run(|tid| {
            let Scratch { a, b, c, pos, .. } = unsafe { eng.scratch(tid) };
            let mut m = Map::new(unsafe { eng.arena(tid) }, 1024);
            while let Some(blk) = ctr.take() {
                for (st, n) in vectors(self.l_orderkey.entry(blk).count) {
                    unpack(&self.l_orderkey, blk, st, n, a);
                    let k = semi(&big, &fbig, &a[..n], st, pos, b);
                    if k == 0 {
                        continue;
                    }
                    unpack_sel(&self.l_qty, blk, &pos[..k], c);
                    for i in 0..k {
                        m.upsert(b[i] as i64).val += c[i] as i64;
                    }
                }
            }
            m
        });
        for r in rows.iter_mut() {
            r.sum = sums.iter().filter_map(|m| m.find(r.okey)).map(|c| c.val).sum();
            r.name = names[name.find(r.cust).unwrap().val as usize];
        }
        // 7. tri par prix décroissant, date, commande ; cent premières lignes
        rows.sort_unstable_by(|a, b| b.price.cmp(&a.price).then(a.date.cmp(&b.date)).then(a.okey.cmp(&b.okey)));
        for r in rows.iter().take(100) {
            emit!(out, r.name, "|", r.cust, "|", r.okey, "|", r.date, "|", r.price, "|", r.sum, "\n");
        }
    }
}

// ================================================================================================ C4
struct C4 {
    uid: Col,
}
impl C4 {
    fn open(d: &str) -> C4 {
        C4 { uid: Col::open(d, "hits", "UserID") }
    }
    fn run(&self, eng: &Engine, out: &mut Vec<u8>) {
        let ctr = Counter::new(self.uid.nblocks);
        eng.pool.run(|tid| {
            let h = unsafe { &mut eng.scratch(tid).h };
            let p = unsafe { eng.parts(tid) };
            p.init(unsafe { eng.arena(tid) }, size_of::<i64>());
            while let Some(blk) = ctr.take() {
                // 64 bits : valeurs telles quelles
                let v = unsafe { std::slice::from_raw_parts(self.uid.words(blk) as *const i64, self.uid.entry(blk).count as usize) };
                for (st, n) in vectors(v.len() as u32) {
                    let v = &v[st..st + n];
                    for (h, &x) in h[..n].iter_mut().zip(v) {
                        *h = hash64(x as u64);
                    }
                    for (&h, &x) in h[..n].iter().zip(v) {
                        p.push(part_of(h), x);
                    }
                }
            }
            p.close();
        });
        let ctr = Counter::new(NPART as u64);
        let all = unsafe { eng.all_parts() };
        let counts = eng.pool.run(|tid| {
            let arena = unsafe { eng.arena(tid) };
            let (mut count, mut minus1) = (0u64, false);
            while let Some(k) = ctr.take() {
                let mut m = Map::new(arena, pow2_start(parts_count(all, k)));
                parts_each::<i64>(all, k, |t, end| unsafe {
                    if PREFETCH && t.add(AHEAD) < end {
                        prefetch(m.cell(hash64(*t.add(AHEAD) as u64) & m.mask));
                    }
                    if *t == -1 {
                        minus1 = true; // la valeur qui marque les cases vides est comptée à part
                    } else {
                        m.upsert(*t);
                    }
                });
                count += m.count;
            }
            (count, minus1)
        });
        let count: u64 = counts.iter().map(|c| c.0).sum();
        emit!(out, count + counts.iter().any(|c| c.1) as u64, "\n");
    }
}

// ================================================================================================ agrégations par chaîne
// C12, C16, C33, C36 : les lignes retenues sont hachées, réparties, puis agrégées partition par partition ; chaque
// fil garde ses dix premiers groupes.
#[repr(C)]
#[derive(Clone, Copy)]
struct STuple {
    hash: u64,
    ikey: i64,
    pos: u64,
    len: u32,
    pad: u32,
}
struct CS {
    mode: u32, // 12, 16, 33, 36
    str: Col,
    uid: Option<Col>,
    filter: Option<[Col; 4]>, // C36 : compteur, date, DontCountHits, IsRefresh
    lo: i32,
    hi: i32,
}
impl CS {
    fn open(d: &str, mode: u32) -> CS {
        let col = |name| Col::open(d, "hits", name);
        CS {
            mode,
            str: col(if mode == 12 || mode == 16 { "SearchPhrase" } else { "URL" }),
            uid: (mode == 16).then(|| col("UserID")),
            filter: (mode == 36).then(|| [col("CounterID"), col("EventDate"), col("DontCountHits"), col("IsRefresh")]),
            lo: days_from_civil(2013, 7, 1),
            hi: days_from_civil(2013, 7, 31),
        }
    }
    fn run(&self, eng: &Engine, out: &mut Vec<u8>) {
        let ctr = Counter::new(self.str.nblocks);
        eng.pool.run(|tid| {
            let Scratch { a, b, c, d, e, sel, pos: vpos, x, h, .. } = unsafe { eng.scratch(tid) };
            let p = unsafe { eng.parts(tid) };
            p.init(unsafe { eng.arena(tid) }, size_of::<STuple>());
            let bytes = self.str.aux;
            while let Some(blk) = ctr.take() {
                if let Some([counter, date, _, _]) = &self.filter {
                    // cartes de zones : compteur et date
                    let (ec, ed) = (counter.entry(blk), date.entry(blk));
                    if ec.min > 62 || ec.max < 62 || ed.max < self.lo as i64 || ed.min > self.hi as i64 {
                        continue;
                    }
                }
                let count = self.str.entry(blk).count;
                let uid = self.uid.map(|u| unsafe { std::slice::from_raw_parts(u.words(blk) as *const i64, count as usize) });
                let mut pos = self.str.entry(blk).aux_off;
                for (st, n) in vectors(count) {
                    unpack(&self.str, blk, st, n, a); // longueurs
                    for (x, &len) in x[..n].iter_mut().zip(&a[..n]) {
                        *x = pos as i64;
                        pos += len as u64;
                    }
                    let k;
                    if let Some([counter, date, dch, refresh]) = &self.filter {
                        unpack(counter, blk, st, n, b);
                        let k1 = sel_between(&b[..n], 62, 62, st as u32, vpos);
                        if k1 == 0 {
                            continue;
                        }
                        unpack_sel(date, blk, &vpos[..k1], c);
                        unpack_sel(dch, blk, &vpos[..k1], d);
                        unpack_sel(refresh, blk, &vpos[..k1], e);
                        let mut k2 = 0;
                        for i in 0..k1 {
                            let j = vpos[i] as usize - st;
                            sel[k2] = j as i32;
                            k2 += ((c[i] >= self.lo) & (c[i] <= self.hi) & (d[i] == 0) & (e[i] == 0) & (a[j] > 0)) as usize;
                        }
                        k = k2;
                    } else if self.mode == 12 {
                        k = sel_between(&a[..n], 1, i32::MAX, 0, sel);
                    } else {
                        for (i, s) in sel[..n].iter_mut().enumerate() {
                            *s = i as i32;
                        }
                        k = n;
                    }
                    for (h, &i) in h[..k].iter_mut().zip(&sel[..k]) {
                        *h = hash_bytes(unsafe { bytes.add(x[i as usize] as usize) }, a[i as usize] as usize);
                    }
                    if let Some(uid) = uid {
                        for (h, &i) in h[..k].iter_mut().zip(&sel[..k]) {
                            let v = hash64(*h ^ (uid[st + i as usize] as u64).wrapping_mul(K2));
                            *h = if v != 0 { v } else { 1 };
                        }
                    }
                    for (&h, &i) in h[..k].iter().zip(&sel[..k]) {
                        let i = i as usize;
                        let ikey = uid.map_or(0, |u| u[st + i]);
                        p.push(part_of(h), STuple { hash: h, ikey, pos: x[i] as u64, len: a[i] as u32, pad: 0 });
                    }
                }
            }
            p.close();
        });
        let ctr = Counter::new(NPART as u64);
        let all = unsafe { eng.all_parts() };
        let tops = eng.pool.run(|tid| {
            let arena = unsafe { eng.arena(tid) };
            let mut top = Top10::new(self.str);
            while let Some(k) = ctr.take() {
                let mut m = SMap::new(arena, pow2_start(parts_count(all, k)), self.str.aux);
                parts_each::<STuple>(all, k, |t, end| unsafe {
                    if PREFETCH && t.add(AHEAD) < end {
                        // à AHEAD tuples : la case et les octets du tuple ; à mi-distance : les octets de la case
                        let far = &*t.add(AHEAD);
                        prefetch(m.cell(far.hash & m.mask));
                        prefetch(m.bytes.add(far.pos as usize));
                        let near = &*t.add(AHEAD / 2);
                        let c = &*m.cell(near.hash & m.mask);
                        if c.hash == near.hash {
                            prefetch(m.bytes.add(c.pos as usize));
                        }
                    }
                    m.add((*t).hash, (*t).ikey, (*t).pos, (*t).len);
                });
                for j in 0..=m.mask {
                    let c = unsafe { &*m.cell(j) };
                    if c.hash != 0 {
                        top.add(Top { count: c.count, len: c.len, ikey: c.ikey, pos: c.pos });
                    }
                }
            }
            top
        });
        let mut all = Top10::new(self.str);
        for top in &tops {
            top.t[..top.n].iter().for_each(|&x| all.add(x));
        }
        for t in &all.t[..all.n] {
            if self.mode == 16 {
                emit!(out, t.ikey, "|");
            }
            emit!(out, self.str.bytes(t.pos, t.len as usize), "|", t.count, "\n");
        }
    }
}

// ================================================================================================ C20
struct C20 {
    url: Col,
}
impl C20 {
    fn open(d: &str) -> C20 {
        C20 { url: Col::open(d, "hits", "URL") }
    }
    fn run(&self, eng: &Engine, out: &mut Vec<u8>) {
        let ctr = Counter::new(self.url.nblocks);
        let counts = eng.pool.run(|tid| {
            let s = unsafe { eng.scratch(tid) };
            let mut count = 0u64;
            while let Some(b) = ctr.take() {
                let nbytes = block_lengths(&self.url, b, &mut s.len);
                let buf = unsafe { self.url.aux.add(self.url.entry(b).aux_off as usize) };
                count += search_block(buf, nbytes, &s.len, b"google", &mut s.rows) as u64;
            }
            count
        });
        emit!(out, counts.iter().sum::<u64>(), "\n");
    }
}

// ================================================================================================ principal
fn main() {
    let args: Vec<String> = std::env::args().collect();
    if args.len() < 5 {
        die("usage : olap <requête> <fils> <répétitions> <répertoire des données> [--print]");
    }
    let (q, d) = (args[1].as_str(), args[4].as_str());
    let nt: usize = args[2].parse().unwrap_or(0);
    let reps: usize = args[3].parse().unwrap_or(0);
    let print = args.len() > 5 && args[5] == "--print";
    if !(1..=MAXT).contains(&nt) {
        die("nombre de fils");
    }
    let eng = Engine::new(nt);
    let run: Box<dyn Fn(&Engine, &mut Vec<u8>)> = match q {
        "t1" => { let x = T1::open(d); Box::new(move |e: &Engine, o: &mut Vec<u8>| x.run(e, o)) }
        "t6" => { let x = T6::open(d); Box::new(move |e: &Engine, o: &mut Vec<u8>| x.run(e, o)) }
        "t9" => { let x = T9::open(d); Box::new(move |e: &Engine, o: &mut Vec<u8>| x.run(e, o)) }
        "t18" => { let x = T18::open(d); Box::new(move |e: &Engine, o: &mut Vec<u8>| x.run(e, o)) }
        "c4" => { let x = C4::open(d); Box::new(move |e: &Engine, o: &mut Vec<u8>| x.run(e, o)) }
        "c12" | "c16" | "c33" | "c36" => { let x = CS::open(d, q[1..].parse().unwrap()); Box::new(move |e: &Engine, o: &mut Vec<u8>| x.run(e, o)) }
        "c20" => { let x = C20::open(d); Box::new(move |e: &Engine, o: &mut Vec<u8>| x.run(e, o)) }
        _ => die("requête inconnue"),
    };
    let mut out = Vec::new();
    let stdout = std::io::stdout();
    for r in 0..reps {
        for tid in 0..nt {
            unsafe { eng.arena(tid).reset() };
        }
        out.clear();
        let t0 = std::time::Instant::now();
        run(&eng, &mut out);
        let dt = t0.elapsed().as_secs_f64();
        let mut so = stdout.lock();
        writeln!(so, "RESULT;{q};{LEVEL};{nt};{r};{dt:.6};{:016x}", fnv1a(&out)).unwrap();
        if print && r == reps - 1 {
            so.write_all(&out).unwrap();
        }
        so.flush().unwrap();
    }
}
