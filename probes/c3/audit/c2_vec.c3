// Contre-épreuve C2 : intrinsèque vectorielle de LLVM par extern @cname (les vecteurs passent par l'ABI C, sret/byval).
module c2_vec;
import std::io;
extern fn int[<16>] pternlog(int[<16>] a, int[<16>] b, int[<16>] c, int imm) @cname("llvm.x86.avx512.pternlog.d.512");
fn void main(String[] args)
{
	int k = (int)args.len;
	int[<16>] a = { [0..15] = 12 * k };
	int[<16>] b = { [0..15] = 10 * k };
	int[<16>] c = { [0..15] = k };
	io::printfn("%d", pternlog(a, b, c, 0x96)[0]);
}
