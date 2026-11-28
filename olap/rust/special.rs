// v7 : niveau spécialisé du banc OLAP en Rust (olap/SPEC.md, 7). Module `level` de olap.rs sous --cfg special, à la
// place des primitives portables de même nom. Même plan, mêmes structures, mêmes fonctions de hachage ; AVX-512 (F,
// BW, DQ, VL, VBMI) par les intrinsèques de std::arch.
//
//   0. décodage : seize valeurs à la fois, par permutation d'octets et décalages variables ;
//   1. sélection : comparaison de 16 valeurs et compression des positions retenues (vpcompressd) ;
//   2. agrégation de T1 : sommes masquées par groupe, huit lignes à la fois ;
//   3. recherche de sous-chaîne : premier et dernier octet de l'aiguille comparés à 64 positions à la fois ;
//   4. répartition : un tampon de 64 octets par partition, vidé par une écriture non temporelle ;
//   5. préchargement des cases et des octets à venir dans les agrégations et les sondes (dans olap.rs, sous PREFETCH).
use super::*;
use std::arch::x86_64::*;

pub const LEVEL: &str = "s";
pub const PREFETCH: bool = true;
pub const AHEAD: usize = 16; // tuples d'avance pour le préchargement
pub const SEARCH_STEP: usize = 64;

#[inline(always)]
pub fn prefetch<T>(p: *const T) {
    unsafe { _mm_prefetch::<_MM_HINT_T0>(p as *const i8) }
}

// ------------------------------------------------------------------------------------------------ 0. décodage
// Seize valeurs à la fois (largeur de 25 bits au plus) : elles occupent 2 x largeur octets ; une permutation
// d'octets (vpermb) amène dans chaque voie de 32 bits les 4 octets où commence sa valeur, un décalage variable la
// cale, un masque la borne. Au-delà de 25 bits : huit valeurs à la fois dans des voies de 64 bits. Les tables de
// permutation et de décalage sont calculées à la compilation.
#[repr(C, align(64))]
#[derive(Clone, Copy)]
struct UnpackTab {
    idx: [u8; 64],
    sh32: [u32; 16],
    sh64: [u64; 8],
}
static UNPACK_TAB: [UnpackTab; 33] = {
    let mut t = [UnpackTab { idx: [0; 64], sh32: [0; 16], sh64: [0; 8] }; 33];
    let mut w = 1;
    while w <= 32 {
        let (lanes, bytes) = if w <= 25 { (16, 4) } else { (8, 8) };
        let mut j = 0;
        while j < lanes {
            let mut k = 0;
            while k < bytes {
                t[w].idx[bytes * j + k] = ((j * w >> 3) + k) as u8;
                k += 1;
            }
            if w <= 25 {
                t[w].sh32[j] = (j * w & 7) as u32;
            } else {
                t[w].sh64[j] = (j * w & 7) as u64;
            }
            j += 1;
        }
        w += 1;
    }
    t
};

/// Décode n valeurs du bloc b à partir de la ligne start (multiple de 64) ; écrit des groupes entiers de 16.
#[inline]
pub fn unpack(c: &Col, b: usize, start: usize, n: usize, out: &mut [i32]) {
    let e = c.entry(b);
    let w = e.width as usize;
    let o = out[..(n + 15) & !15].as_mut_ptr();
    unsafe {
        let base = _mm512_set1_epi32(e.min as i32);
        if w == 0 {
            for i in (0..n).step_by(16) {
                _mm512_storeu_si512(o.add(i) as *mut _, base);
            }
            return;
        }
        let mut p = c.words(b).add(start / 64 * w) as *const i8;
        let tab = &UNPACK_TAB[w];
        let idx = _mm512_load_si512(tab.idx.as_ptr() as *const _);
        if w <= 25 {
            let sh = _mm512_loadu_si512(tab.sh32.as_ptr() as *const _);
            let mask = _mm512_set1_epi32(((1u32 << w) - 1) as i32);
            let need: __mmask64 = (1u64 << (2 * w + 4)) - 1; // octets lus : pas au-delà de ce que le format garantit
            for i in (0..n).step_by(16) {
                let x = _mm512_permutexvar_epi8(idx, _mm512_maskz_loadu_epi8(need, p));
                _mm512_storeu_si512(o.add(i) as *mut _, _mm512_add_epi32(_mm512_and_si512(_mm512_srlv_epi32(x, sh), mask), base));
                p = p.add(2 * w);
            }
        } else {
            let sh = _mm512_loadu_si512(tab.sh64.as_ptr() as *const _);
            let mask = _mm512_set1_epi64(((1u64 << w) - 1) as i64);
            let need: __mmask64 = (1u64 << (w + 8)) - 1;
            for i in (0..n).step_by(8) {
                let x = _mm512_permutexvar_epi8(idx, _mm512_maskz_loadu_epi8(need, p));
                let v = _mm512_cvtepi64_epi32(_mm512_and_si512(_mm512_srlv_epi64(x, sh), mask));
                _mm256_storeu_si256(o.add(i) as *mut __m256i, _mm256_add_epi32(v, _mm512_castsi512_si256(base)));
                p = p.add(w);
            }
        }
    }
}

// ------------------------------------------------------------------------------------------------ 1. sélection
/// Voies vivantes d'un pas de 16 quand il reste `left` valeurs.
#[inline(always)]
fn live16(left: usize) -> __mmask16 {
    if left >= 16 { 0xFFFF } else { ((1u32 << left) - 1) as u16 }
}
/// Positions (base + i) des valeurs v[i] comprises entre lo et hi, bornes comprises.
#[inline]
pub fn sel_between(v: &[i32], lo: i32, hi: i32, base: u32, pos: &mut [i32]) -> usize {
    let n = v.len();
    assert!(pos.len() >= n);
    unsafe {
        let (vlo, vhi) = (_mm512_set1_epi32(lo), _mm512_set1_epi32(hi));
        let mut idx = _mm512_add_epi32(
            _mm512_set1_epi32(base as i32),
            _mm512_setr_epi32(0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15),
        );
        let mut k = 0;
        for i in (0..n).step_by(16) {
            let live = live16(n - i);
            let x = _mm512_maskz_loadu_epi32(live, v.as_ptr().add(i));
            let m = _mm512_mask_cmpge_epi32_mask(live, x, vlo) & _mm512_cmple_epi32_mask(x, vhi);
            _mm512_mask_compressstoreu_epi32(pos.as_mut_ptr().add(k) as *mut _, m, idx);
            k += m.count_ones() as usize;
            idx = _mm512_add_epi32(idx, _mm512_set1_epi32(16));
        }
        k
    }
}
/// Parmi les entrées (position, charge) : garde celles dont la valeur v[i] est entre lo et hi.
#[inline]
pub fn keep_between(v: &[i32], pos_in: &[i32], pay_in: &[i32], lo: i32, hi: i32, pos_out: &mut [i32], pay_out: &mut [i32]) -> usize {
    let n = v.len();
    assert!(pos_in.len() >= n && pay_in.len() >= n && pos_out.len() >= n && pay_out.len() >= n);
    unsafe {
        let (vlo, vhi) = (_mm512_set1_epi32(lo), _mm512_set1_epi32(hi));
        let mut k = 0;
        for i in (0..n).step_by(16) {
            let live = live16(n - i);
            let x = _mm512_maskz_loadu_epi32(live, v.as_ptr().add(i));
            let m = _mm512_mask_cmpge_epi32_mask(live, x, vlo) & _mm512_cmple_epi32_mask(x, vhi);
            _mm512_mask_compressstoreu_epi32(pos_out.as_mut_ptr().add(k) as *mut _, m, _mm512_maskz_loadu_epi32(live, pos_in.as_ptr().add(i)));
            _mm512_mask_compressstoreu_epi32(pay_out.as_mut_ptr().add(k) as *mut _, m, _mm512_maskz_loadu_epi32(live, pay_in.as_ptr().add(i)));
            k += m.count_ones() as usize;
        }
        k
    }
}

// ------------------------------------------------------------------------------------------------ 2. agrégation de T1
/// Huit lignes à la fois : pour chacun des six groupes, un masque et cinq additions masquées.
#[inline]
pub fn t1_aggregate(agg: &mut [Agg1; 6], grp: &[i32], qty: &[i32], ext: &[i32], disc: &[i32], dp: &[i64], ch: &[i64],
                    ship: Option<&[i32]>, cut: i32, n: usize, _sel: &mut [i32]) {
    let m8 = (n + 7) & !7;
    assert!(grp.len() >= m8 && qty.len() >= m8 && ext.len() >= m8 && disc.len() >= m8 && dp.len() >= m8 && ch.len() >= m8);
    assert!(ship.is_none_or(|s| s.len() >= m8));
    unsafe {
        let mut acc = [[_mm512_setzero_si512(); 5]; 6];
        let mut cnt = [0u64; 6];
        let vcut = _mm256_set1_epi32(cut);
        let load8 = |p: &[i32], i: usize| _mm256_loadu_si256(p.as_ptr().add(i) as *const __m256i);
        for i in (0..n).step_by(8) {
            let mut live: __mmask8 = if n - i >= 8 { 0xFF } else { ((1u32 << (n - i)) - 1) as u8 };
            if let Some(ship) = ship {
                live &= _mm256_cmple_epi32_mask(load8(ship, i), vcut);
            }
            let g8 = load8(grp, i);
            let q = _mm512_cvtepi32_epi64(load8(qty, i));
            let e = _mm512_cvtepi32_epi64(load8(ext, i));
            let d = _mm512_cvtepi32_epi64(load8(disc, i));
            let x = _mm512_loadu_si512(dp.as_ptr().add(i) as *const _);
            let y = _mm512_loadu_si512(ch.as_ptr().add(i) as *const _);
            for g in 0..6 {
                let m = _mm256_mask_cmpeq_epi32_mask(live, g8, _mm256_set1_epi32(g as i32));
                acc[g][0] = _mm512_mask_add_epi64(acc[g][0], m, acc[g][0], q);
                acc[g][1] = _mm512_mask_add_epi64(acc[g][1], m, acc[g][1], e);
                acc[g][2] = _mm512_mask_add_epi64(acc[g][2], m, acc[g][2], x);
                acc[g][3] = _mm512_mask_add_epi64(acc[g][3], m, acc[g][3], y);
                acc[g][4] = _mm512_mask_add_epi64(acc[g][4], m, acc[g][4], d);
                cnt[g] += m.count_ones() as u64;
            }
        }
        for g in 0..6 {
            agg[g].qty += _mm512_reduce_add_epi64(acc[g][0]);
            agg[g].base += _mm512_reduce_add_epi64(acc[g][1]);
            agg[g].disc_price += _mm512_reduce_add_epi64(acc[g][2]);
            agg[g].charge += _mm512_reduce_add_epi64(acc[g][3]);
            agg[g].disc += _mm512_reduce_add_epi64(acc[g][4]);
            agg[g].count += cnt[g] as i64;
        }
    }
}

// ------------------------------------------------------------------------------------------------ 3. sous-chaînes
/// Candidates parmi les 64 positions qui partent de p : premier octet de l'aiguille en p + i, dernier en p + i + m - 1.
#[inline]
pub unsafe fn search_candidates(p: *const u8, m: usize, c0: u8, c1: u8) -> u64 {
    unsafe {
        let a = _mm512_loadu_si512(p as *const _);
        let b = _mm512_loadu_si512(p.add(m - 1) as *const _);
        _mm512_cmpeq_epi8_mask(a, _mm512_set1_epi8(c0 as i8)) & _mm512_cmpeq_epi8_mask(b, _mm512_set1_epi8(c1 as i8))
    }
}

// ------------------------------------------------------------------------------------------------ 4. répartition
/// Chaque partition a un tampon de 64 octets ; plein, il part d'un trait dans le morceau, sans passer par le cache.
/// La taille d'un tuple divise 64.
pub struct Parts {
    dst: [*mut u8; NPART],
    end: [*mut u8; NPART],
    pub head: [*mut PChunk; NPART],
    tail: [*mut PChunk; NPART],
    fill: [u8; NPART],
    pub tsize: usize,
    arena: *mut Arena,
    wc: *mut [u8; 64],
}
impl Parts {
    pub fn init(&mut self, a: &mut Arena, tsize: usize) {
        let wc = if self.wc.is_null() { huge_alloc(NPART * 64) as *mut [u8; 64] } else { self.wc };
        unsafe { std::ptr::write_bytes(self, 0, 1) };
        self.tsize = tsize;
        self.arena = a;
        self.wc = wc;
    }
    #[cold]
    unsafe fn chunk(&mut self, k: usize) {
        unsafe {
            let c = (*self.arena).alloc(size_of::<PChunk>() + CHUNK) as *mut PChunk;
            (*c).next = null_mut();
            (*c).used = 0;
            if self.tail[k].is_null() {
                self.head[k] = c;
            } else {
                (*self.tail[k]).used = self.dst[k].offset_from(self.tail[k].add(1) as *mut u8) as u32;
                (*self.tail[k]).next = c;
            }
            self.tail[k] = c;
            self.dst[k] = c.add(1) as *mut u8;
            self.end[k] = self.dst[k].add(CHUNK);
        }
    }
    /// Écrit le tuple suivant de la partition k.
    #[inline]
    pub fn push<T>(&mut self, k: usize, t: T) {
        unsafe {
            let mut f = *self.fill.get_unchecked(k) as usize;
            let wc = self.wc.add(k) as *mut u8;
            if f == 64 {
                // tampon plein : il est vidé avant de resservir
                if *self.dst.get_unchecked(k) == *self.end.get_unchecked(k) {
                    self.chunk(k);
                }
                let dst = *self.dst.get_unchecked(k);
                _mm512_stream_si512(dst as *mut _, _mm512_load_si512(wc as *const _));
                *self.dst.get_unchecked_mut(k) = dst.add(64);
                f = 0;
            }
            *self.fill.get_unchecked_mut(k) = (f + size_of::<T>()) as u8;
            (wc.add(f) as *mut T).write(t);
        }
    }
    pub fn close(&mut self) {
        unsafe {
            for k in 0..NPART {
                let f = self.fill[k] as usize;
                if f > 0 {
                    if self.dst[k] == self.end[k] {
                        self.chunk(k);
                    }
                    std::ptr::copy_nonoverlapping(self.wc.add(k) as *const u8, self.dst[k], f);
                    self.dst[k] = self.dst[k].add(f);
                    self.fill[k] = 0;
                }
                if !self.tail[k].is_null() {
                    (*self.tail[k]).used = self.dst[k].offset_from(self.tail[k].add(1) as *mut u8) as u32;
                }
            }
            _mm_sfence();
        }
    }
}
