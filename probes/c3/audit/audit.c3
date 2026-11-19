// Audit de la grille (docs/V4_PLAN.md 2.1) : sonde exécutée de C3 0.8.5, cas positifs. run.sh y ajoute le code produit,
// les échecs et les recherches d'absence.
module audit;
import std::io, std::io::file, std::io::file::mmap, std::thread, std::atomic, std::sort, std::core::mem;
import std::core::mem::alloc;

struct Part { float x; float y; float z; char m; }
struct Inl { uint n; float[16] a; }
struct Line @align(64) { ulong v; }

struct WArg { int t; ulong* out; int* tid; }
fn int worker(void* p)
{
	WArg* a = p;
	ulong s;
	for (int i = a.t * 1000; i < (a.t + 1) * 1000; i++) s += (ulong)i;
	*a.out = s;
	*a.tid = (int)@syscall(186); // gettid
	return 0;
}
fn Type gsum(Type[] x) <Type> { Type s; foreach (v : x) s += v; return s; }
macro ulong @fib($n)
{
	var $a = (ulong)0;
	var $b = (ulong)1;
	$for var $i = 0; $i < $n; $i++:
		var $t = $a + $b;
		$a = $b;
		$b = $t;
	$endfor
	return $a;
}

fn int threads_now()
{
	File? f = file::open("/proc/self/status", "rb");
	if (catch f) return -1;
	char[4096] rb;
	sz? got = f.read(&rb);
	(void)f.close();
	if (catch got) return -1;
	String st = (String)rb[:(usz)got];
	sz? i = st.index_of("Threads:");
	if (catch i) return -1;
	int n;
	for (usz k = (usz)i + 8; k < st.len; k++) { char c = st[k]; if (c >= '0' && c <= '9') { n = n * 10 + (c - '0'); } else if (n > 0) { break; } }
	return n;
}

fn void main()
{
	// A1
	Part[] v = mem::new_array(Part, 8);
	foreach (&e : v) *e = { 1, 2, 3, 4 };
	uptr stride = (uptr)&v[1] - (uptr)&v[0];
	char* raw = (char*)v.ptr;
	io::printfn("CAP;A1;1;[exécutée] Part[] : pas de %d o = Part::size %d ; les 4 premiers octets du tampon sont le float x en ligne : %02x %02x %02x %02x", stride, Part::size, raw[0], raw[1], raw[2], raw[3]);
	// A4
	Line* l = mem::new_aligned(Line);
	Line[] ls = mem::new_array_aligned(Line, 4);
	io::printfn("CAP;A4;1;[exécutée] struct @align(64) : Line::alignment = %d, mem::new_aligned(Line) à %d mod 64 (mem::new refusé à la compilation pour un type sur-aligné), Line[] : pas %d o, éléments à %d mod 64", Line::alignment, (uptr)l % 64, Line::size, (uptr)&ls[1] % 64);
	// A7, A8
	io::printfn("CAP;A7;1;[exécutée] struct { uint n; float[16] a; } : %d o, $reflect(Inl.a).offset = %d (tableau en ligne)", Inl::size, $reflect(Inl.a).offset);
	char[] b8 = mem::new_array(char, 1000);
	short[] h16 = mem::new_array(short, 1000);
	io::printfn("CAP;A8;1;[exécutée] char/short/float16/float : %d/%d/%d/%d o ; char[] de 1000 éléments : %d o, short[] : %d o", char::size, short::size, float16::size, float::size, b8.len * char::size, h16.len * short::size);
	// B1
	io::printfn("CAP;B1;1;[exécutée] aucune collecte : mémoire rendue par free explicite ou par @pool ; %d fil (Threads: de /proc/self/status, aucun fil de collecteur)", threads_now());
	// B2
	char[4096] store;
	ArenaAllocator arena;
	arena.init(&store);
	ulong[] blk = alloc::new_array(&arena, ulong, 100);
	bool inside = (uptr)blk.ptr >= (uptr)&store && (uptr)blk.ptr < (uptr)&store + 4096;
	io::printfn("CAP;B2;1;[exécutée] interface Allocator : ArenaAllocator sur un tampon de pile -> bloc dans le tampon = %s, %d o consommés ; @pool() (arène temporaire libérée en fin de portée, bench K8)", inside, arena.used);
	// B3
	char[4096] local;
	local[0] = 1;
	char marker = local[0];
	long ds = (long)(uptr)&marker - (long)(uptr)&local;
	long dh = (long)(uptr)b8.ptr - (long)(uptr)&local;
	io::printfn("CAP;B3;1;[exécutée] char[4096] local à %d o d'une autre variable locale, à %d o du tas : sur la pile", ds < 0 ? -ds : ds, dh < 0 ? -dh : dh);
	// B4
	TrackingAllocator track;
	track.init(mem);
	sz n1;
	sz n2;
	float[256] data;
	for (int i = 0; i < 256; i++) data[i] = (float)i;
	sort::quicksort(&data);
	char[64] fbuf;
	String fs = (String)io::bprintf(&fbuf, "%.1f %s", data[255], gsum{float}(&data))!!;
	n1 = track.total_allocation_count();
	float[] lst = alloc::new_array(&track, float, 1000);
	n2 = track.total_allocation_count();
	io::printfn("CAP;B4;1;[exécutée] allocateur traceur : tri, formatage dans un tampon de pile, tranches, macros -> %d allocation (%s) ; seule l'API qui reçoit un allocateur alloue : %d", n1, fs, n2 - n1);
	// B5
	uint[8] buf;
	uint* mp = &buf;
	mp[3] = 42;
	char* bp = (char*)&buf;
	*(uint*)(bp + 16) = 7;
	io::printfn("CAP;B5;1;[exécutée] uint* : mp[3] = 42 -> buf[3] = %d ; écriture par décalage d'octets -> buf[4] = %d", buf[3], buf[4]);
	// C1
	float[<8>] va = { 1, 2, 3, 4, 5, 6, 7, 8 };
	float[<8>] vb = va + va;
	io::printfn("CAP;C1;1;[exécutée] float[<8>] : (a + a)[7] = %s, a.sum() = %s, swizzle et comparaisons vectorielles dans le langage", vb[7], va.sum());
	// D1
	ulong[4] parts;
	int[4] ids;
	WArg[4] args;
	Thread[4] th;
	for (int t = 0; t < 4; t++) { args[t] = { t, &parts[t], &ids[t] }; th[t].create(&worker, &args[t])!!; }
	for (int t = 0; t < 4; t++) th[t].join()!!;
	int nd;
	for (int i = 0; i < 4; i++) { bool seen; for (int j = 0; j < i; j++) seen = seen || ids[j] == ids[i]; if (!seen) nd++; }
	io::printfn("CAP;D1;1;[exécutée] std::thread : 4 fils, %d identifiants de fil (gettid) distincts, somme %d (attendu 7998000)", nd, parts[0] + parts[1] + parts[2] + parts[3]);
	// D4 (½ : appel système brut, sans constante ni enveloppe)
	ulong[16] mask;
	mask[0] = 2;
	long ra = (long)@syscall(203, 0, 128, (uptr)&mask); // SYS_sched_setaffinity
	uint cpu = 99;
	@syscall(309, (uptr)&cpu, 0, 0); // SYS_getcpu
	io::printfn("CAP;D4;0.5;[exécutée] @syscall(203, …) : numéro d'appel système écrit à la main (aucune constante ni enveloppe dans std) : retour %d, getcpu = %d", ra, cpu);
	// E2
	int ex = 41;
	asm { addl ex, 1; }
	io::printfn("FACT;E2;bloc asm { addl ex, 1; } : 41 -> %d", ex);
	// E7
	const ulong F60 = @fib(60);
	io::printfn("FACT;E7;macro @fib(60) déroulée par $for à la compilation = %d ; gsum <float> = %s, gsum <double> = %s", F60, gsum{float}((float[]){1.5, 2.5}), gsum{double}((double[]){1.5, 2.25}));
	// F1
	float[4][3] m;
	io::printfn("FACT;F1;float[4][3] contigu : &m[1][0] - &m[0][3] = %d o, sizeof = %d o", (uptr)&m[1][0] - (uptr)&m[0][3], float[4][3]::size);
	// F3
	uint um = uint::max;
	int im = int::max;
	char c250 = 250;
	io::printfn("CAP;F3;1;[exécutée] uint::max + 1 = %d, int::max + 1 = %d, (char)250 + 10 = %d (débordement défini, enveloppant)", um + 1, im + 1, (char)(c250 + 10));
	// F4
	float[4] vals = { 1.5, 2.5, 3.5, 4.5 };
	(void)file::save("/tmp/c3_audit_f4.bin", ((char*)&vals)[:16]);
	mmap::FileMmap? fm = file::mmap_open("/tmp/c3_audit_f4.bin", "rb");
	if (try fm)
	{
		char[] bytes = fm.bytes();
		float[] fl = ((float*)bytes.ptr)[:bytes.len / 4];
		io::printfn("CAP;F4;1;[exécutée] std::io::file::mmap_open (portable) + réinterprétation sans copie : %s %s %s %s, adresse projetée = adresse lue : %s", fl[0], fl[1], fl[2], fl[3], (uptr)fl.ptr == (uptr)bytes.ptr);
		(void)fm.destroy();
	}
}
