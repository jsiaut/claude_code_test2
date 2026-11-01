// Sonde E5 : sur quel paramètre l'attribut @noalias est-il posé dans l'IR de LLVM ?
module probe_noalias;
import std::io;
fn void first(int* a @noalias, int* b) @noinline { *a = *b + 1; *a += *b; }
fn void second(int* a, int* b @noalias) @noinline { *a = *b + 1; *a += *b; }
fn void slice_arg(int[] a @noalias, int[] b) @noinline { a[0] = b[0] + 1; a[0] += b[0]; }
fn int main()
{
	int x;
	int y = 1;
	first(&x, &y);
	second(&x, &y);
	int[2] p;
	int[2] q = { 1, 2 };
	slice_arg(&p, &q);
	io::printfn("%d %d", x, p[0]);
	return 0;
}
