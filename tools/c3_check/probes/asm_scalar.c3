module probe_asm;
fn int main(String[] args) { int x = (int)args.len; asm { addl x, 1; } return x; }
