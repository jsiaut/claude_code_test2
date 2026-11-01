// Sonde C4 et K5 : somme flottante naturelle et .sum() d'un vecteur, en mode strict et avec --fp-math=relaxed.
module probe_fp;
import std::io;
fn float dot(float[] a, float[] b) @noinline
{
	float s;
	for (usz i = 0; i < a.len; i++) s += a[i] * b[i];
	return s;
}
fn float vsum(float[<16>] v) @noinline => v.sum();
fn int main()
{
	float[64] a;
	float[64] b;
	for (int i = 0; i < 64; i++) { a[i] = (float)i; b[i] = 1.0f; }
	float[<16>] v;
	for (int i = 0; i < 16; i++) v[i] = (float)i;
	io::printfn("%f %f", dot(&a, &b), vsum(v));
	return 0;
}
