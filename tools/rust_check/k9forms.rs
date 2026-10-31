// Formes de K9 naturel, mêmes options que le banc ; on compte les instructions vectorielles de chaque fonction.
pub const M9: usize = 2048;
#[inline(never)]
pub fn f_bench(inp: &Vec<Vec<f64>>, out: &mut Vec<Vec<f64>>) {
    for i in 1..M9 - 1 {
        for j in 1..M9 - 1 {
            out[i][j] = 0.25 * (((inp[i - 1][j] + inp[i + 1][j]) + inp[i][j - 1]) + inp[i][j + 1]);
        }
    }
}
#[inline(never)]
pub fn f_unchecked(inp: &Vec<Vec<f64>>, out: &mut Vec<Vec<f64>>) {
    for i in 1..M9 - 1 {
        for j in 1..M9 - 1 {
            unsafe {
                *out.get_unchecked_mut(i).get_unchecked_mut(j) = 0.25
                    * (((inp.get_unchecked(i - 1).get_unchecked(j) + inp.get_unchecked(i + 1).get_unchecked(j))
                        + inp.get_unchecked(i).get_unchecked(j - 1))
                        + inp.get_unchecked(i).get_unchecked(j + 1));
            }
        }
    }
}
#[inline(never)]
pub fn f_rowslices(inp: &Vec<Vec<f64>>, out: &mut Vec<Vec<f64>>) {
    for i in 1..M9 - 1 {
        let (up, mid, dn) = (&inp[i - 1][..], &inp[i][..], &inp[i + 1][..]);
        let o = &mut out[i][..];
        for j in 1..M9 - 1 {
            o[j] = 0.25 * (((up[j] + dn[j]) + mid[j - 1]) + mid[j + 1]);
        }
    }
}
#[inline(never)]
pub fn f_fixedrows(inp: &Vec<[f64; M9]>, out: &mut Vec<[f64; M9]>) {
    for i in 1..M9 - 1 {
        for j in 1..M9 - 1 {
            out[i][j] = 0.25 * (((inp[i - 1][j] + inp[i + 1][j]) + inp[i][j - 1]) + inp[i][j + 1]);
        }
    }
}
#[inline(never)]
pub fn f_flat(inp: &Vec<f64>, out: &mut Vec<f64>) {
    for i in 1..M9 - 1 {
        for j in 1..M9 - 1 {
            out[i * M9 + j] = 0.25 * (((inp[(i - 1) * M9 + j] + inp[(i + 1) * M9 + j]) + inp[i * M9 + j - 1]) + inp[i * M9 + j + 1]);
        }
    }
}
