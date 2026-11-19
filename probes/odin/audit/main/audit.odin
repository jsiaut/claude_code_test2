// Audit de la grille (docs/V4_PLAN.md 2.1) : sonde exécutée d'Odin, cas positifs. run.sh y ajoute le code produit, les
// échecs et les recherches d'absence.
package audit

import "base:intrinsics"
import "base:runtime"
import "core:fmt"
import "core:mem"
import "core:mem/virtual"
import "core:os"
import "core:simd"
import "core:slice"
import "core:sys/linux"
import "core:thread"

Part :: struct { x, y, z: f32, m: u8 }
Inl :: struct { n: u32, a: [16]f32 }
Line :: struct #align(64) { v: u64 }

worker :: proc(t: int, out: ^u64, tid: ^int) {
	s: u64 = 0
	for i in t * 1000 ..< (t + 1) * 1000 do s += u64(i)
	out^ = s
	tid^ = int(linux.gettid())
}
gsum :: proc(x: []$T) -> T { s: T; for v in x do s += v; return s }

main :: proc() {
	// A1
	v := make([]Part, 8)
	for &e in v do e = Part{1, 2, 3, 4}
	stride := uintptr(&v[1]) - uintptr(&v[0])
	raw := (^[4]u8)(raw_data(v))^
	fmt.printf("CAP;A1;1;[exécutée] []Part : pas de %d o = size_of(Part) %d ; les 4 premiers octets du tampon sont le f32 x en ligne : %x\n", stride, size_of(Part), raw)
	// A4
	l := new(Line)
	ls := make([]Line, 4)
	fmt.printf("CAP;A4;1;[exécutée] struct #align(64) : align_of = %d, new(Line) à %d mod 64, []Line : pas %d o, éléments à %d mod 64\n", align_of(Line), uintptr(l) % 64, size_of(Line), uintptr(&ls[1]) % 64)
	// A6
	soa := make(#soa[]Part, 100)
	for i in 0 ..< 100 do soa[i].x = f32(i)
	fmt.printf("CAP;A6;1;[exécutée] #soa[]Part : &soa[1].x - &soa[0].x = %d o ; soa.y commence %d o après soa.x (un tableau par champ) ; soa[99].x = %v\n", uintptr(&soa[1].x) - uintptr(&soa[0].x), uintptr(soa.y) - uintptr(soa.x), soa[99].x)
	// A7, A8
	fmt.printf("CAP;A7;1;[exécutée] struct {{ n: u32, a: [16]f32 }} : %d o, offset_of(Inl, a) = %d (tableau en ligne)\n", size_of(Inl), offset_of(Inl, a))
	b8 := make([]u8, 1000); h16 := make([]i16, 1000)
	fmt.printf("CAP;A8;1;[exécutée] u8/i16/f16/f32 : %d/%d/%d/%d o ; []u8 de 1000 éléments : %d o, []i16 : %d o\n", size_of(u8), size_of(i16), size_of(f16), size_of(f32), len(b8) * size_of(u8), len(h16) * size_of(i16))
	// B1
	tasks := 0
	if d, err := os.open("/proc/self/task"); err == nil { if fis, e2 := os.read_dir(d, -1, context.temp_allocator); e2 == nil do tasks = len(fis); os.close(d) }
	fmt.printf("CAP;B1;1;[exécutée] aucune collecte : mémoire rendue par free/delete explicites ; %d fil dans /proc/self/task (aucun fil de collecteur)\n", tasks)
	// B2
	store: [4096]u8
	arena: mem.Arena
	mem.arena_init(&arena, store[:])
	blk: []u64
	{
		context.allocator = mem.arena_allocator(&arena)
		blk = make([]u64, 100)
		da: [dynamic]u32
		for i in 0 ..< 200 do append(&da, u32(i))
	}
	inside := uintptr(raw_data(blk)) >= uintptr(&store[0]) && uintptr(raw_data(blk)) < uintptr(&store[0]) + 4096
	fmt.printf("CAP;B2;1;[exécutée] context.allocator remplacé par mem.arena_allocator sur un tampon de pile : make et append y allouent (bloc dans le tampon = %v, %d o consommés)\n", inside, arena.offset)
	// B3
	local: [4096]u8
	local[0] = 1
	marker: u8 = local[0]
	ds := abs(int(uintptr(&marker)) - int(uintptr(&local)))
	dh := abs(int(uintptr(raw_data(b8))) - int(uintptr(&local)))
	fmt.printf("CAP;B3;1;[exécutée] [4096]u8 local à %d o d'une autre variable locale, à %d o du tas : sur la pile\n", ds, dh)
	// B4
	track: mem.Tracking_Allocator
	mem.tracking_allocator_init(&track, context.allocator)
	n1, n2: i64
	{
		context.allocator = mem.tracking_allocator(&track)
		data: [256]f32
		for i in 0 ..< 256 do data[i] = f32(i)
		slice.sort(data[:])
		buf: [64]u8
		s := fmt.bprintf(buf[:], "%.1f %v", data[255], gsum(data[:]))
		cb := proc(x: f32) -> f32 { return x * 2 }
		_ = cb(data[3])
		n1 = track.total_allocation_count
		dyn: [dynamic]f32
		append(&dyn, 1.0)
		n2 = track.total_allocation_count
		fmt.printf("CAP;B4;1;[exécutée] allocateur traceur dans le contexte : tri, formatage dans un tampon, tranches, procédures -> %d allocation (%s) ; append sur [dynamic] alloue par context.allocator (documenté) : %d\n", n1, s, n2 - n1)
	}
	// B5
	buf: [8]u32
	mp := ([^]u32)(&buf[0])
	mp[3] = 42
	bp := ([^]u8)(&buf[0])
	(^u32)(&bp[16])^ = 7
	fmt.printf("CAP;B5;1;[exécutée] [^]u32 : mp[3] = 42 -> buf[3] = %d ; écriture par décalage d'octets -> buf[4] = %d\n", buf[3], buf[4])
	// C1
	va := #simd[8]f32{1, 2, 3, 4, 5, 6, 7, 8}
	vb := va + va
	fmt.printf("CAP;C1;1;[exécutée] #simd[8]f32 : (a + a)[7] = %v, simd.reduce_add_ordered(a) = %v, simd.shuffle et simd.select dans core:simd\n", simd.extract(vb, 7), simd.reduce_add_ordered(va))
	// D1
	parts: [4]u64
	ids: [4]int
	th: [4]^thread.Thread
	for t in 0 ..< 4 do th[t] = thread.create_and_start_with_poly_data3(t, &parts[t], &ids[t], worker)
	for t in th { thread.join(t); thread.destroy(t) }
	ndist := 0
	for i in 0 ..< 4 { seen := false; for j in 0 ..< i do seen = seen || ids[j] == ids[i]; if !seen do ndist += 1 }
	fmt.printf("CAP;D1;1;[exécutée] core:thread : 4 fils, %d identifiants de fil (gettid) distincts, somme %d (attendu 7998000)\n", ndist, parts[0] + parts[1] + parts[2] + parts[3])
	// D3
	fmt.printf("FACT;D3;base:runtime.MAP_CACHE_LINE_SIZE = %d\n", runtime.MAP_CACHE_LINE_SIZE)
	// D4
	set: [16]u64
	set[0] = 2
	r, e := linux.sched_setaffinity(0, size_of(set), &set)
	cpu: u32 = 99
	linux.getcpu(&cpu, nil)
	fmt.printf("CAP;D4;1;[exécutée] core:sys/linux.sched_setaffinity (livré avec le compilateur ; ½ en v1, appel système brut) : retour %v %v, getcpu = %d\n", r, e, cpu)
	// F2, contre-épreuve : politique NUMA par appel système brut (SYS_mbind, pas de procédure dédiée)
	reg, merr2 := linux.mmap(0, 1 << 20, {.READ, .WRITE}, {.PRIVATE, .ANONYMOUS})
	nodemask: u64 = 1
	rb := linux.syscall(linux.SYS_mbind, uintptr(reg), uintptr(1 << 20), uintptr(2), uintptr(&nodemask), uintptr(64), uintptr(0))
	mode: i32 = -1
	rg := linux.syscall(linux.SYS_get_mempolicy, uintptr(&mode), uintptr(0), uintptr(0), uintptr(reg), uintptr(2))
	fmt.printf("NOTE;F2;[exécutée] linux.syscall(SYS_mbind, MPOL_BIND, nœud 0) sur une zone de 1 Mio (mmap %v) : retour %d ; get_mempolicy(MPOL_F_ADDR) : retour %d, mode %d (2 = MPOL_BIND) ; numéros d'appels système seulement, sans procédure dédiée\n", merr2, rb, rg, mode)
	// E2
	add64 :: asm(a: i64, b: i64) -> (r: i64) { mov r, a; add r, b; }
	fmt.printf("CAP;E2;1;[exécutée] procédure assembleur add64 :: asm(a: i64, b: i64) -> (r: i64) {{ mov r, a; add r, b; }} : add64(41, 1) = %d\n", add64(41, 1))
	// E7, F1, F3
	fmt.printf("FACT;E7;gsum(f32) = %v, gsum(f64) = %v\n", gsum([]f32{1.5, 2.5}), gsum([]f64{1.5, 2.25}))
	m: [3][4]f32
	mx: matrix[4, 4]f32
	fmt.printf("FACT;F1;[3][4]f32 contigu : &m[1][0] - &m[0][3] = %d o, size_of = %d o ; matrix[4, 4]f32 : %d o\n", uintptr(&m[1][0]) - uintptr(&m[0][3]), size_of([3][4]f32), size_of(mx))
	um: u32 = max(u32)
	im: i32 = max(i32)
	b250: u8 = 250
	fmt.printf("CAP;F3;1;[exécutée] max(u32) + 1 = %d, max(i32) + 1 = %d, u8 250 + 10 = %d (débordement défini, sans piège)\n", um + 1, im + 1, b250 + 10)
	// F4
	path := "/tmp/odin_audit_f4.bin"
	vals := [4]f32{1.5, 2.5, 3.5, 4.5}
	_ = os.write_entire_file(path, mem.slice_to_bytes(vals[:]))
	data, merr := virtual.map_file_from_path(path, {.Read})
	fl := slice.reinterpret([]f32, data)
	fmt.printf("CAP;F4;1;[exécutée] core:mem/virtual.map_file_from_path (portable) + slice.reinterpret : %v (erreur %v), adresse projetée = adresse lue : %v ; ½ en v1\n", fl, merr, rawptr(raw_data(fl)) == rawptr(raw_data(data)))
	virtual.unmap_file(data)
}
