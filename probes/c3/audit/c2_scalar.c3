// Contre-épreuve C2 : intrinsèques scalaires de LLVM par extern @cname (sonde de la remarque sur C3 : pause oui, pext non).
module c2_scalar;
import std::io;
extern fn uint pext32(uint a, uint mask) @cname("llvm.x86.bmi.pext.32");
extern fn void cpu_pause() @cname("llvm.x86.sse2.pause");
fn void main(String[] args)
{
	uint x = (uint)args.len * 0x12345678u;
	cpu_pause();
	io::printfn("%x", pext32(x | 0xF0F0, 0xFF00FF00u));
}
