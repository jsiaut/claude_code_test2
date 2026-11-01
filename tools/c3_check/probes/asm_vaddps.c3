module probe_asm;
fn int main() { asm { vaddps $zmm0, $zmm1, $zmm2; } return 0; }
