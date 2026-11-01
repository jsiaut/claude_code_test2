module probe_asm;
fn int main() { float[16] a @align(64); asm { vmovaps $zmm0, [&a]; } return 0; }
