module probe;
import std::io;

struct Sx { char a; uint b; double c; }
struct Pk @packed { char a; uint b; }
bitstruct Bf : ushort { char x : 0..2; char y : 3..7; }
union Un { float f; uint u; }

fn void main()
{
	io::printfn("CAP;A2;1;$reflect(Sx.c).offset=%d", $reflect(Sx.c).offset);
	io::printfn("CAP;A3;1;@packed P.sizeof=%d ; bitstruct BF.sizeof=%d", Pk::size, Bf::size);
	Un u = { .f = 1.0 };
	io::printfn("CAP;A5;1;union 0x%x bitcast 0x%x", u.u, bitcast(1.0f, uint));
	int x = 1;
	if (@likely(x == 1)) x++;
	io::printfn("CAP;E3;1;@likely : %d", x);
}
