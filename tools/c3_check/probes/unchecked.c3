// Sonde E6 : l'attribut @unchecked existe-t-il ?
module probe_unchecked;
fn int get(int[] a, usz i) @unchecked => a[i];
fn int main() { int[2] x = { 1, 2 }; return get(&x, 1); }
