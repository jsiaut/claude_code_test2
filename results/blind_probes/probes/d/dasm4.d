void f() { asm nothrow @nogc { addps XMM0, XMM1; mfence; prefetcht0 [RAX]; } }
