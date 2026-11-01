// Sonde F4 : projection d'un fichier par la bibliothèque standard (std::io::file::mmap), puis réinterprétation sans copie.
module probe_mmap;
import std::io, std::io::file::mmap;
fn int main(String[] args)
{
	mmap::FileMmap? m = file::mmap_open(args[1], "rb");
	if (catch err = m) { io::printfn("échec : %s", err); return 1; }
	char[] bytes = m.bytes();
	uint[] words = ((uint*)bytes.ptr)[:bytes.len / 4];
	io::printfn("octets %d, premier mot %x", bytes.len, words[0]);
	(void)m.destroy();
	return 0;
}
