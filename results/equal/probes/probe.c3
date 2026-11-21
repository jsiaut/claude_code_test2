// Sonde de mode (v4, point 3 : docs/V4_EQUAL.md, 4) : « 1d » : tranche allouée, « 2d » : Grid* carré (comme k9_natural).
module probe;
import std::io;
const M = 64;
alias Grid = double[M][M];
fn int main(String[] args)
{
	int n = args[2].to_int()!!;
	if (args[1][0] == '1')
	{
		double[] a = mem::new_array(double, n);
		for (int i = 0; i < n; i++) a[i] = 1.0;
		io::printfn("%f", a[n]);
	}
	else
	{
		Grid* g = mem::new(Grid);
		for (int i = 0; i < M; i++) for (int j = 0; j < M; j++) (*g)[i][j] = 1.0;
		io::printfn("%f", (*g)[1][n]);
	}
	return 0;
}
