module probe_asm;
fn int main() { asm { vfmadd231ps $zmm0, $zmm1, $zmm2; } return 0; }
