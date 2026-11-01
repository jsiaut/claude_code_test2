module probe_asm;
fn int main() { asm { mfence; } return 0; }
