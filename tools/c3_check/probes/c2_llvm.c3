// Sonde C2 : une intrinsèque de la cible (LLVM x86) appelée par extern @cname, sans fichier C.
module probe_c2;
import std::io;
extern fn uint pext32(uint a, uint mask) @cname("llvm.x86.bmi.pext.32");
extern fn void cpu_pause() @cname("llvm.x86.sse2.pause");
fn int main(String[] args)
{
	uint x = (uint)args.len * 0x12345678u;
	cpu_pause();
	io::printfn("%x", pext32(x | 0xF0F0, 0xFF00FF00u));
	return 0;
}
