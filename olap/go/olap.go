// v7 (docs/V7.md ; olap/SPEC.md) : le banc OLAP en Go. Même architecture que la référence (olap/c/olap.c), écrite
// avec les moyens du langage : mémoire hors tas (mmap) pour les colonnes, les arènes et les tampons, lue par des
// tranches et des pointeurs `unsafe` ; goroutines persistantes qui attendent sur un canal ; routines de décodage
// engendrées (unpack_gen.go). Les primitives qui ont deux niveaux sont dans portable.go et special.go.
//
// Usage : olap <requête> <fils> <répétitions> <répertoire des données> [--print]
package main

import (
	"bytes"
	"cmp"
	"fmt"
	"math"
	"math/bits"
	"os"
	"runtime"
	"slices"
	"strconv"
	"sync"
	"sync/atomic"
	"syscall"
	"time"
	"unsafe"
)

const (
	PBITS      = 10         // bits de partition
	VEC        = 2048       // lignes d'un vecteur
	CHUNK      = 16384      // octets utiles d'un morceau de tampon de partition
	BLOCK      = 65536      // lignes d'un bloc : un morceau
	NPART      = 1 << PBITS // partitions des grandes tables
	MAXT       = 64         // fils au plus
	arenaBlock = 32 << 20   // octets d'un bloc d'arène
	hugePage   = 1 << 21    // octets d'une page large
	K1         = 0x9E3779B97F4A7C15
	K2         = 0xC2B2AE3D27D4EB4F
)

func die(msg string) {
	fmt.Fprintln(os.Stderr, "olap :", msg)
	os.Exit(2)
}

// ------------------------------------------------------------------------------------------------ mémoire, arènes

// Toute la mémoire du programme (colonnes chargées, arènes, vecteurs de travail) est hors du tas : des zones
// alignées sur 2 Mio, signalées comme pages larges. Le ramasse-miettes ne les voit pas.
func hugeAlloc(n uintptr) unsafe.Pointer {
	n = (n + hugePage - 1) &^ (hugePage - 1)
	b, err := syscall.Mmap(-1, 0, int(n+hugePage), syscall.PROT_READ|syscall.PROT_WRITE, syscall.MAP_ANON|syscall.MAP_PRIVATE)
	if err != nil {
		die("mémoire")
	}
	off := (hugePage - uintptr(unsafe.Pointer(&b[0]))%hugePage) % hugePage
	b = b[off : off+n]
	syscall.Madvise(b, syscall.MADV_HUGEPAGE)
	return unsafe.Pointer(&b[0])
}

// Une arène par fil : allocation par déplacement d'un pointeur, remise à zéro à chaque exécution ; la mémoire est
// gardée d'une répétition à l'autre.
type arenaHdr struct {
	next      *arenaHdr
	cap, used uintptr
	_         [40]byte
}
type Arena struct{ first, cur *arenaHdr }

func (a *Arena) alloc(n uintptr) unsafe.Pointer {
	n = (n + 63) &^ 63
	for {
		b := a.cur
		if b != nil && b.used+n <= b.cap {
			p := unsafe.Add(unsafe.Pointer(b), 64+b.used)
			b.used += n
			return p
		}
		if b != nil && b.next != nil && b.next.cap >= n {
			a.cur = b.next
			a.cur.used = 0
			continue
		}
		capacity := max(n, arenaBlock-64)
		nb := (*arenaHdr)(hugeAlloc(64 + capacity))
		nb.cap, nb.used = capacity, 0
		if b != nil {
			nb.next, b.next = b.next, nb
		} else {
			nb.next, a.first = nil, nb
		}
		a.cur = nb
	}
}
func (a *Arena) reset() {
	a.cur = a.first
	if a.cur != nil {
		a.cur.used = 0
	}
}

// Tableau de n éléments dans l'arène.
func array[T any](a *Arena, n uint64) []T {
	var t T
	return unsafe.Slice((*T)(a.alloc(uintptr(n)*unsafe.Sizeof(t))), n)
}

// ------------------------------------------------------------------------------------------------ fils persistants

// Les goroutines sont créées une fois et attendent, bloquées sur leur canal, entre deux phases. run(f) exécute
// f(tid) sur toutes (le fil principal est le fil 0) et attend la fin de toutes.
type Pool struct {
	n    int
	work []chan func(int)
	wg   sync.WaitGroup
}

func (p *Pool) start(n int) {
	p.n, p.work = n, make([]chan func(int), n)
	for tid := 1; tid < n; tid++ {
		p.work[tid] = make(chan func(int))
		go func() {
			for f := range p.work[tid] {
				f(tid)
				p.wg.Done()
			}
		}()
	}
}
func (p *Pool) run(f func(tid int)) {
	p.wg.Add(p.n - 1)
	for tid := 1; tid < p.n; tid++ {
		p.work[tid] <- f
	}
	f(0)
	p.wg.Wait()
}

// Compteur de morceaux partagé : la seule opération atomique.
type Counter struct {
	next atomic.Uint64
	n    uint64
}

func (c *Counter) set(n uint64) { c.next.Store(0); c.n = n }
func (c *Counter) take() int {
	if i := c.next.Add(1) - 1; i < c.n {
		return int(i)
	}
	return -1
}

// ------------------------------------------------------------------------------------------------ colonnes

type Entry struct {
	min, max        int64
	dataOff, auxOff uint64
	width, count    uint32
}
type Col struct {
	nrows, nblocks, auxCount uint64
	dir                      []Entry
	data                     []uint64 // la zone des valeurs, jusqu'à la fin du fichier
	aux                      []byte   // la zone annexe, jusqu'à la fin du fichier
}

var dataDir string // répertoire des données

func colOpen(table, name string) Col {
	path := dataDir + "/" + table + "/" + name + ".msc"
	f, err := os.Open(path)
	if err != nil {
		die(err.Error())
	}
	st, _ := f.Stat()
	size := int(st.Size())
	// La colonne est lue en entier, en pages larges, avec 64 octets nuls de marge après le dernier.
	base := unsafe.Slice((*byte)(hugeAlloc(uintptr(size)+64)), size+64)
	for off := 0; off < size; {
		n, err := f.Read(base[off:size])
		if n <= 0 || err != nil {
			die("lecture")
		}
		off += n
	}
	f.Close()
	if string(base[:4]) != "MSC1" {
		die("format")
	}
	u32 := func(i int) uint32 { return *(*uint32)(unsafe.Pointer(&base[i])) }
	u64 := func(i int) uint64 { return *(*uint64)(unsafe.Pointer(&base[i])) }
	if u32(12) != BLOCK {
		die("taille de bloc")
	}
	c := Col{nrows: u64(16), nblocks: u64(24), auxCount: u64(56)}
	c.dir = unsafe.Slice((*Entry)(unsafe.Pointer(&base[u64(32)])), c.nblocks)
	c.data = unsafe.Slice((*uint64)(unsafe.Pointer(&base[u64(40)])), (uint64(size)+64-u64(40))/8)
	c.aux = base[u64(48):]
	return c
}
func (c *Col) words(b int) []uint64 { return c.data[c.dir[b].dataOff/8:] }

// Entrée d'un dictionnaire : ses octets suivent la table des positions.
func (c *Col) dict(code uint32) []byte {
	pos := unsafe.Slice((*uint32)(unsafe.Pointer(&c.aux[0])), c.auxCount+1)
	return c.aux[4*(c.auxCount+1):][pos[code]:pos[code+1]]
}

// ------------------------------------------------------------------------------------------------ décodage

// Décode n valeurs du bloc b à partir de la ligne start (multiple de 64) par la routine de la largeur du bloc
// (unpack_gen.go) ; écrit des groupes entiers de 64.
func unpackPortable(c *Col, b, start, n int, out []int32) {
	e := &c.dir[b]
	if e.width == 0 {
		out = out[:n]
		for i := range out {
			out[i] = int32(e.min)
		}
		return
	}
	unpackFn[e.width](c.words(b)[start/64*int(e.width):], out[:(n+63)&^63], uint32(e.min))
}

// Décode les valeurs du bloc b aux positions pos (lignes dans le bloc), dans l'ordre : out[i] est celle de pos[i].
func unpackSel(c *Col, b int, pos []int32, out []int32) {
	e := &c.dir[b]
	w, base := uint64(e.width), uint32(e.min)
	out = out[:len(pos)]
	if w == 0 {
		for i := range out {
			out[i] = int32(base)
		}
		return
	}
	in := unsafe.Pointer(&c.words(b)[0])
	mask := uint64(1)<<w - 1
	for i, p := range pos {
		bit := uint64(p) * w
		word := (*[2]uint64)(unsafe.Add(in, bit>>6<<3))
		sh := bit & 63
		out[i] = int32(uint32((word[0]>>sh|word[1]<<1<<(63-sh))&mask) + base)
	}
}

// ------------------------------------------------------------------------------------------------ hachage

func load64(p unsafe.Pointer) uint64 { return *(*uint64)(p) }
func hash64(k uint64) uint64 {
	k *= K1
	return k ^ k>>32
}

// Octets : deux voies de mots de 64 bits ; le dernier mot, incomplet, est masqué (8 octets lisibles après la fin).
func hashBytes(p unsafe.Pointer, n uint64) uint64 {
	h1, h2 := K1^n, uint64(K2)
	for ; n >= 16; n -= 16 {
		h1 = (bits.RotateLeft64(h1, 5) ^ load64(p)) * K1
		h2 = (bits.RotateLeft64(h2, 5) ^ load64(unsafe.Add(p, 8))) * K2
		p = unsafe.Add(p, 16)
	}
	if n >= 8 {
		h1 = (bits.RotateLeft64(h1, 5) ^ load64(p)) * K1
		p = unsafe.Add(p, 8)
		n -= 8
	}
	if n > 0 {
		h2 = (bits.RotateLeft64(h2, 5) ^ load64(p)&(1<<(8*n)-1)) * K2
	}
	h := (h1 ^ bits.RotateLeft64(h2, 32)) * K1
	h ^= h >> 32
	if h == 0 {
		return 1 // 0 marque une case vide
	}
	return h
}
func partOf(h uint64) uint32 { return uint32(h >> (64 - PBITS)) }

// ------------------------------------------------------------------------------------------------ table de hachage

// Adressage ouvert, sondage linéaire, capacité en puissance de deux, clé et valeur dans la même case ; doublement
// quand la table est à moitié pleine. Clés entières positives ou nulles ; -1 marque une case vide.
func pow2For(n uint64) uint64 { // capacité pour n clés : au moins le double, 16 au moins
	c := uint64(16)
	for c < 2*n {
		c *= 2
	}
	return c
}

// Capacité de départ d'une table d'agrégation qui recevra n tuples ; elle double ensuite à la demande.
func pow2Start(n uint64) uint64 { return pow2For(n / 8) }

type Cell struct{ key, val int64 }
type Map struct {
	cells       unsafe.Pointer
	mask, count uint64
	arena       *Arena
}

func newMap(a *Arena, capacity uint64) Map {
	cells := array[Cell](a, capacity)
	for i := range cells {
		cells[i] = Cell{-1, -1}
	}
	return Map{unsafe.Pointer(&cells[0]), capacity - 1, 0, a}
}
func (m *Map) cell(i uint64) *Cell { return (*Cell)(unsafe.Add(m.cells, i<<4)) }

// Case de la clé, dont h est le hash64 ; nil si elle manque.
func (m *Map) findH(key int64, h uint64) *Cell {
	for i := h & m.mask; ; i = (i + 1) & m.mask {
		c := m.cell(i)
		if c.key == key {
			return c
		}
		if c.key == -1 {
			return nil
		}
	}
}
func (m *Map) find(key int64) *Cell { return m.findH(key, hash64(uint64(key))) }
func (m *Map) grow() {
	old := *m
	*m = newMap(old.arena, 2*(old.mask+1))
	for j := uint64(0); j <= old.mask; j++ {
		if c := old.cell(j); c.key != -1 {
			i := hash64(uint64(c.key)) & m.mask
			for m.cell(i).key != -1 {
				i = (i + 1) & m.mask
			}
			*m.cell(i) = *c
		}
	}
	m.count = old.count
}

// Rend la case de la clé, créée avec la valeur 0 si elle manquait (le booléen le dit).
func (m *Map) upsertFresh(key int64) (*Cell, bool) {
	if (m.count+1)*2 > m.mask+1 {
		m.grow()
	}
	for i := hash64(uint64(key)) & m.mask; ; i = (i + 1) & m.mask {
		c := m.cell(i)
		if c.key == key {
			return c, false
		}
		if c.key == -1 {
			c.key, c.val = key, 0
			m.count++
			return c, true
		}
	}
}
func (m *Map) upsert(key int64) *Cell {
	c, _ := m.upsertFresh(key)
	return c
}

// Cases occupées, dans l'ordre de la table.
func (m *Map) all() []Cell { return unsafe.Slice((*Cell)(m.cells), m.mask+1) }

// Filtre de Bloom par blocs, devant les sondes de semi-jointure : 16 bits par clé, deux bits dans un même mot de
// 64 bits. Un refus est sûr ; une acceptation se confirme dans la table.
type Bloom struct {
	bits unsafe.Pointer
	mask uint64
}

func newBloom(a *Arena, nkeys uint64) Bloom {
	words := uint64(64)
	for words*4 < nkeys {
		words *= 2
	}
	b := array[uint64](a, words)
	clear(b)
	return Bloom{unsafe.Pointer(&b[0]), words - 1}
}
func bloomTwo(h uint64) uint64         { return 1<<(h&63) | 1<<(h>>6&63) }
func (f *Bloom) word(h uint64) *uint64 { return (*uint64)(unsafe.Add(f.bits, (h>>12&f.mask)<<3)) }
func (f *Bloom) add(h uint64)          { *f.word(h) |= bloomTwo(h) }
func (f *Bloom) test(h uint64) bool    { m := bloomTwo(h); return *f.word(h)&m == m }

// Même table pour des clés faites d'un entier et d'une chaîne : la case garde le hachage, l'entier, la position et
// la longueur de la chaîne, et un compte. Hachage nul : case vide.
type SCell struct {
	hash       uint64
	ikey       int64
	pos        uint64
	len, count uint32
}
type SMap struct {
	cells   unsafe.Pointer
	mask, n uint64
	arena   *Arena
	bytes   []byte
}

func newSMap(a *Arena, capacity uint64, b []byte) SMap {
	cells := array[SCell](a, capacity)
	clear(cells)
	return SMap{unsafe.Pointer(&cells[0]), capacity - 1, 0, a, b}
}
func (m *SMap) cell(i uint64) *SCell { return (*SCell)(unsafe.Add(m.cells, i<<5)) }
func (m *SMap) grow() {
	old := *m
	*m = newSMap(old.arena, 2*(old.mask+1), old.bytes)
	for j := uint64(0); j <= old.mask; j++ {
		if c := old.cell(j); c.hash != 0 {
			i := c.hash & m.mask
			for m.cell(i).hash != 0 {
				i = (i + 1) & m.mask
			}
			*m.cell(i) = *c
		}
	}
	m.n = old.n
}
func (m *SMap) add(hash uint64, ikey int64, pos uint64, length uint32) {
	if (m.n+1)*2 > m.mask+1 {
		m.grow()
	}
	for i := hash & m.mask; ; i = (i + 1) & m.mask {
		c := m.cell(i)
		if c.hash == hash && c.ikey == ikey && c.len == length &&
			bytes.Equal(m.bytes[c.pos:c.pos+uint64(length)], m.bytes[pos:pos+uint64(length)]) {
			c.count++
			return
		}
		if c.hash == 0 {
			*c = SCell{hash, ikey, pos, length, 1}
			m.n++
			return
		}
	}
}

// ------------------------------------------------------------------------------------------------ partitions

// Tampons d'un fil : pour chaque partition, une liste de morceaux de CHUNK octets pris dans son arène. Le langage
// n'a pas d'écriture non temporelle : la répartition est la même aux deux niveaux.
type PChunk struct {
	next      *PChunk
	used, pad uint32
	_         [48]byte
} // 64 octets, puis CHUNK octets de tuples
type Parts struct {
	cur, end   [NPART]uintptr
	head, tail [NPART]*PChunk
	tsize      uintptr
	arena      *Arena
}

func (p *Parts) init(a *Arena, tsize uintptr) {
	*p = Parts{tsize: tsize, arena: a}
}
func (p *Parts) chunk(k uint32) uintptr {
	c := (*PChunk)(p.arena.alloc(64 + CHUNK))
	c.next, c.used = nil, 0
	if t := p.tail[k]; t != nil {
		t.used = uint32(p.cur[k] - uintptr(unsafe.Pointer(t)) - 64)
		t.next = c
	} else {
		p.head[k] = c
	}
	p.tail[k] = c
	p.cur[k] = uintptr(unsafe.Pointer(c)) + 64
	p.end[k] = p.cur[k] + CHUNK/p.tsize*p.tsize
	return p.cur[k]
}

// Place du prochain tuple (de type T, de taille tsize) de la partition k.
func push[T any](p *Parts, k uint32) *T {
	k &= NPART - 1
	t := p.cur[k]
	if t == p.end[k] {
		t = p.chunk(k)
	}
	var zero T
	p.cur[k] = t + unsafe.Sizeof(zero)
	return (*T)(unsafe.Pointer(t))
}
func (p *Parts) close() {
	for k, t := range p.tail {
		if t != nil {
			t.used = uint32(p.cur[k] - uintptr(unsafe.Pointer(t)) - 64)
		}
	}
}
func partsCount(ps []*Parts, k int) uint64 {
	n := uint64(0)
	for _, p := range ps {
		for c := p.head[k]; c != nil; c = c.next {
			n += uint64(c.used) / uint64(p.tsize)
		}
	}
	return n
}

// Tuples (de type T) d'un morceau.
func tuples[T any](c *PChunk) []T {
	var zero T
	return unsafe.Slice((*T)(unsafe.Add(unsafe.Pointer(c), 64)), uintptr(c.used)/unsafe.Sizeof(zero))
}

// ------------------------------------------------------------------------------------------------ état des fils

// Les vecteurs de 32 bits ont 16 cases de marge : le niveau spécialisé y écrit des pas entiers de 16 voies.
type Scratch struct {
	a, b, c, d, e, f, g, sel, sel2, pos [VEC + 16]int32
	x, y                                [VEC]int64
	h                                   [VEC]uint64
	len, rows                           [BLOCK]int32
}

var (
	NT            int
	pool          Pool
	arena         [MAXT]Arena
	scratch       [MAXT]*Scratch
	parts, parts2 []*Parts
)

// Liste d'entiers de 64 bits dans une arène.
type List struct {
	v []int64
	a *Arena
}

func (l *List) init(a *Arena) { l.v, l.a = nil, a }
func (l *List) push(x int64) {
	if len(l.v) == cap(l.v) {
		v := array[int64](l.a, uint64(max(2*cap(l.v), 1024)))
		l.v = v[:copy(v, l.v)]
	}
	l.v = append(l.v, x)
}

// ------------------------------------------------------------------------------------------------ résultat

var res []byte

func emit(parts ...any) {
	for _, p := range parts {
		switch v := p.(type) {
		case string:
			res = append(res, v...)
		case []byte:
			res = append(res, v...)
		case int64:
			res = strconv.AppendInt(res, v, 10)
		case uint64:
			res = strconv.AppendUint(res, v, 10)
		case uint32:
			res = strconv.AppendUint(res, uint64(v), 10)
		}
	}
}
func fnv1a(s []byte) uint64 {
	h := uint64(0xCBF29CE484222325)
	for _, c := range s {
		h = (h ^ uint64(c)) * 0x100000001B3
	}
	return h
}

// ------------------------------------------------------------------------------------------------ dates

func daysFromCivil(y, m, d int) int32 { // jours depuis le 1er janvier 1970
	if m <= 2 {
		y--
	}
	era := y / 400
	yoe := y - era*400
	mp := m - 3
	if m <= 2 {
		mp = m + 9
	}
	doy := (153*mp+2)/5 + d - 1
	doe := yoe*365 + yoe/4 - yoe/100 + doy
	return int32(era*146097 + doe - 719468)
}

var yearStart [200]int32 // premier jour de chaque année à partir de 1970

func yearOf(days int32) int64 {
	y := days / 366
	for yearStart[y+1] <= days {
		y++
	}
	return 1970 + int64(y)
}

// ------------------------------------------------------------------------------------------------ sous-chaînes

// Lignes d'un bloc de chaînes qui contiennent l'aiguille (2 octets au moins) : les octets du bloc sont parcourus
// d'un trait, par mots de 8 octets ; un mot est candidat si, à une même position, il porte le premier octet de
// l'aiguille et le mot décalé de sa longueur moins un porte le dernier. Une occurrence compte si elle tient dans
// une ligne, et une ligne compte une fois.
const (
	ones  = 0x0101010101010101
	highs = 0x8080808080808080
)

func zeroBytes(x uint64) uint64 { // bit de poids fort de chaque octet nul de x, exactement
	return ^((x&^highs + ^uint64(highs)) | x) & highs
}
func searchBlock(buf []byte, nbytes int, length []int32, needle string, rows []int32) int {
	m := len(needle)
	r, k := 0, 0
	rowEnd := 0
	if nbytes > 0 {
		rowEnd = int(length[0])
	}
	c0, c1 := needle[0], needle[m-1]
	first, last := ones*uint64(c0), ones*uint64(c1)
	stop := max(nbytes-m+1, 0) // positions de départ possibles : [0, stop)
	base := unsafe.Pointer(&buf[0])
	for i := 0; i < stop; {
		var cand uint64
		next, shift := i+8, 3 // un bit candidat par octet du mot : rang du bit / 8
		if searchStep > 0 && i+searchStep+m-1 <= nbytes {
			// niveau spécialisé : 64 positions d'un coup, un bit candidat par position
			cand = searchCandidates(buf[i:], m, c0, c1)
			if cand == 0 {
				i += searchStep
				continue
			}
			next, shift = i+searchStep, 0
		} else if i+8 <= stop { // les deux mots sont dans le bloc
			cand = zeroBytes((load64(unsafe.Add(base, i)) ^ first) | (load64(unsafe.Add(base, i+m-1)) ^ last))
			if cand == 0 {
				i += 8
				continue
			}
		} else {
			for j := i; j < stop; j++ {
				if buf[j] == c0 && buf[j+m-1] == c1 {
					cand |= 0x80 << (8 * (j - i))
				}
			}
		}
		for ; cand != 0; cand &= cand - 1 {
			at := i + bits.TrailingZeros64(cand)>>shift
			if string(buf[at+1:at+m-1]) != needle[1:m-1] {
				continue
			}
			for rowEnd <= at {
				r++
				rowEnd += int(length[r])
			}
			if at+m <= rowEnd {
				rows[k] = int32(r)
				k++
				next = rowEnd // la suite de la ligne est sautée
				break
			}
		}
		i = next
	}
	return k
}

// Longueurs d'un bloc de chaînes (dans length) ; rend le nombre de ses octets.
func blockLengths(c *Col, b int, length []int32) int {
	n := int(c.dir[b].count)
	unpack(c, b, 0, n, length)
	total := 0
	for _, l := range length[:n] {
		total += int(l)
	}
	return total
}

// ------------------------------------------------------------------------------------------------ dix premiers

type Top struct {
	count, len uint32
	ikey       int64
	pos        uint64
}
type Top10 struct {
	t     [10]Top
	n     int
	bytes []byte
}

// Ordre : compte décroissant, entier croissant, chaîne croissante.
func (t *Top10) before(a, b *Top) bool {
	if a.count != b.count {
		return a.count > b.count
	}
	if a.ikey != b.ikey {
		return a.ikey < b.ikey
	}
	return bytes.Compare(t.bytes[a.pos:a.pos+uint64(a.len)], t.bytes[b.pos:b.pos+uint64(b.len)]) < 0
}
func (t *Top10) add(x Top) {
	if t.n == 10 && !t.before(&x, &t.t[9]) {
		return
	}
	i := 9
	if t.n < 10 {
		i = t.n
		t.n++
	}
	for ; i > 0 && t.before(&x, &t.t[i-1]); i-- {
		t.t[i] = t.t[i-1]
	}
	t.t[i] = x
}

// ================================================================================================ T1 (TPC-H Q1)

type Agg1 struct { // un groupe de T1
	qty, base, discPrice, charge, disc, count int64
	_                                         [2]int64
}
type T1 struct {
	ship, rf, ls, qty, ext, disc, tax Col
	ctr                               Counter
	cut                               int32
}

func (q *T1) open() {
	q.ship, q.rf, q.ls = colOpen("lineitem", "l_shipdate"), colOpen("lineitem", "l_returnflag"), colOpen("lineitem", "l_linestatus")
	q.qty, q.ext = colOpen("lineitem", "l_quantity"), colOpen("lineitem", "l_extendedprice")
	q.disc, q.tax = colOpen("lineitem", "l_discount"), colOpen("lineitem", "l_tax")
	q.cut = daysFromCivil(1998, 9, 2)
}
func (q *T1) run() {
	var aggs [MAXT][6]Agg1
	q.ctr.set(q.ship.nblocks)
	pool.run(func(tid int) {
		s := scratch[tid]
		var agg [6]Agg1
		for b := q.ctr.take(); b >= 0; b = q.ctr.take() {
			e := &q.ship.dir[b]
			if e.min > int64(q.cut) {
				continue // bloc exclu par sa carte de zones
			}
			all := e.max <= int64(q.cut) // bloc retenu en entier : le filtre n'est pas évalué
			for st, count := 0, int(e.count); st < count; st += VEC {
				n := min(count-st, VEC)
				unpack(&q.rf, b, st, n, s.a[:])
				unpack(&q.ls, b, st, n, s.b[:])
				unpack(&q.qty, b, st, n, s.c[:])
				unpack(&q.ext, b, st, n, s.d[:])
				unpack(&q.disc, b, st, n, s.e[:])
				unpack(&q.tax, b, st, n, s.f[:])
				rf, ls, ext, disc, tax := s.a[:n], s.b[:n], s.d[:n], s.e[:n], s.f[:n]
				x, y, g := s.x[:n], s.y[:n], s.g[:n]
				t1Expr(ext, disc, tax, rf, ls, x, y, g)
				var ship []int32
				if !all {
					unpack(&q.ship, b, st, n, s.pos[:])
					ship = s.pos[:n]
				}
				t1Aggregate(&agg, g, s.c[:n], ext, disc, x, y, ship, q.cut, s.sel[:])
			}
		}
		aggs[tid] = agg
	})
	for g := range uint32(6) {
		var a Agg1
		for t := range NT {
			x := &aggs[t][g]
			a.qty += x.qty
			a.base += x.base
			a.discPrice += x.discPrice
			a.charge += x.charge
			a.disc += x.disc
			a.count += x.count
		}
		if a.count == 0 {
			continue
		}
		emit(q.rf.dict(g/2), "|", q.ls.dict(g%2), "|", a.qty, "|", a.base, "|", a.discPrice, "|", a.charge, "|", a.disc, "|", a.count, "\n")
	}
}

// ================================================================================================ T6 (TPC-H Q6)

type T6 struct {
	ship, disc, qty, ext Col
	ctr                  Counter
	lo, hi               int32
}

func (q *T6) open() {
	q.ship, q.disc = colOpen("lineitem", "l_shipdate"), colOpen("lineitem", "l_discount")
	q.qty, q.ext = colOpen("lineitem", "l_quantity"), colOpen("lineitem", "l_extendedprice")
	q.lo, q.hi = daysFromCivil(1994, 1, 1), daysFromCivil(1995, 1, 1)
}
func (q *T6) run() {
	var sums [MAXT][8]int64
	q.ctr.set(q.ship.nblocks)
	pool.run(func(tid int) {
		s := scratch[tid]
		sum := int64(0)
		for b := q.ctr.take(); b >= 0; b = q.ctr.take() {
			e := &q.ship.dir[b]
			if e.max < int64(q.lo) || e.min >= int64(q.hi) {
				continue
			}
			for st, count := 0, int(e.count); st < count; st += VEC {
				n := min(count-st, VEC)
				unpack(&q.ship, b, st, n, s.a[:])
				k := selBetween(s.a[:n], q.lo, q.hi-1, uint32(st), s.pos[:])
				if k == 0 {
					continue
				}
				unpackSel(&q.disc, b, s.pos[:k], s.b[:])
				k2 := keepBetween(s.b[:k], s.pos[:], s.b[:], 5, 7, s.sel[:], s.c[:])
				if k2 == 0 {
					continue
				}
				unpackSel(&q.qty, b, s.sel[:k2], s.d[:])
				k3 := keepBetween(s.d[:k2], s.sel[:], s.c[:], math.MinInt32, 2399, s.sel2[:], s.e[:])
				if k3 == 0 {
					continue
				}
				unpackSel(&q.ext, b, s.sel2[:k3], s.f[:])
				price, disc := s.f[:k3], s.e[:k3]
				for i := range price {
					sum += int64(price[i]) * int64(disc[i])
				}
			}
		}
		sums[tid][0] = sum
	})
	sum := int64(0)
	for t := range NT {
		sum += sums[t][0]
	}
	emit(sum, "\n")
}

// ================================================================================================ T9 (TPC-H Q9)

//  1. part : noms qui contiennent « green » -> ensemble de pièces (table et filtre de Bloom) ;
//  2. partsupp : lignes de ces pièces -> (pièce, fournisseur) -> coût ; 3. supplier -> nation ;
//  4. lineitem : lignes de ces pièces, montant et nation, réparties par commande ;
//  5. orders : (commande, date) réparties de même ; 6. par partition : table des lignes de lineitem, sondée par les
//     commandes ; agrégat par nation et année.
type T9Tuple struct {
	okey, nation int32
	amount       int64
}
type T9Order struct{ okey, date int32 }
type T9 struct {
	pPartkey, pName, psPartkey, psSuppkey, psCost, sSuppkey, sNationkey, nNationkey, nName Col
	lPartkey, lSuppkey, lOrderkey, lQty, lExt, lDisc, oOrderkey, oOrderdate                Col
	ctr                                                                                    Counter
	l1, l2                                                                                 [MAXT]List // listes des fils
	part, ps, supp                                                                         Map
	agg                                                                                    [MAXT]Map
	fpart                                                                                  Bloom
}

func (q *T9) open() {
	q.pPartkey, q.pName = colOpen("part", "p_partkey"), colOpen("part", "p_name")
	q.psPartkey, q.psSuppkey, q.psCost = colOpen("partsupp", "ps_partkey"), colOpen("partsupp", "ps_suppkey"), colOpen("partsupp", "ps_supplycost")
	q.sSuppkey, q.sNationkey = colOpen("supplier", "s_suppkey"), colOpen("supplier", "s_nationkey")
	q.nNationkey, q.nName = colOpen("nation", "n_nationkey"), colOpen("nation", "n_name")
	q.lPartkey, q.lSuppkey, q.lOrderkey = colOpen("lineitem", "l_partkey"), colOpen("lineitem", "l_suppkey"), colOpen("lineitem", "l_orderkey")
	q.lQty, q.lExt, q.lDisc = colOpen("lineitem", "l_quantity"), colOpen("lineitem", "l_extendedprice"), colOpen("lineitem", "l_discount")
	q.oOrderkey, q.oOrderdate = colOpen("orders", "o_orderkey"), colOpen("orders", "o_orderdate")
}

// Positions (dans le bloc) et clés des lignes d'un vecteur dont la clé est dans l'ensemble (filtre, puis table).
func semi(set *Map, filter *Bloom, key []int32, st int, pos, out []int32) int {
	k := 0
	for i, x := range key {
		h := hash64(uint64(x))
		if filter.test(h) && set.findH(int64(x), h) != nil {
			pos[k], out[k] = int32(st+i), x
			k++
		}
	}
	return k
}
func (q *T9) partTask(tid int) {
	s := scratch[tid]
	l := &q.l1[tid]
	l.init(&arena[tid])
	for b := q.ctr.take(); b >= 0; b = q.ctr.take() {
		nbytes := blockLengths(&q.pName, b, s.len[:])
		k := searchBlock(q.pName.aux[q.pName.dir[b].auxOff:], nbytes, s.len[:], "green", s.rows[:])
		for i := 0; i < k; i += VEC {
			n := min(k-i, VEC)
			unpackSel(&q.pPartkey, b, s.rows[i:i+n], s.a[:])
			for _, key := range s.a[:n] {
				l.push(int64(key))
			}
		}
	}
}
func (q *T9) psTask(tid int) {
	s := scratch[tid]
	l1, l2 := &q.l1[tid], &q.l2[tid]
	l1.init(&arena[tid])
	l2.init(&arena[tid])
	for b := q.ctr.take(); b >= 0; b = q.ctr.take() {
		for st, count := 0, int(q.psPartkey.dir[b].count); st < count; st += VEC {
			n := min(count-st, VEC)
			unpack(&q.psPartkey, b, st, n, s.a[:])
			k := semi(&q.part, &q.fpart, s.a[:n], st, s.pos[:], s.b[:])
			if k == 0 {
				continue
			}
			unpackSel(&q.psSuppkey, b, s.pos[:k], s.c[:])
			unpackSel(&q.psCost, b, s.pos[:k], s.d[:])
			for i := range k {
				l1.push(int64(s.b[i])<<32 | int64(s.c[i]))
				l2.push(int64(s.d[i]))
			}
		}
	}
}
func (q *T9) lineTask(tid int) {
	s := scratch[tid]
	p := parts[tid]
	p.init(&arena[tid], unsafe.Sizeof(T9Tuple{}))
	for b := q.ctr.take(); b >= 0; b = q.ctr.take() {
		for st, count := 0, int(q.lPartkey.dir[b].count); st < count; st += VEC {
			n := min(count-st, VEC)
			unpack(&q.lPartkey, b, st, n, s.a[:])
			k := semi(&q.part, &q.fpart, s.a[:n], st, s.pos[:], s.b[:])
			if k == 0 {
				continue
			}
			unpackSel(&q.lSuppkey, b, s.pos[:k], s.c[:])
			unpackSel(&q.lOrderkey, b, s.pos[:k], s.d[:])
			unpackSel(&q.lQty, b, s.pos[:k], s.e[:])
			unpackSel(&q.lExt, b, s.pos[:k], s.f[:])
			unpackSel(&q.lDisc, b, s.pos[:k], s.g[:])
			for i := range k {
				cost := q.ps.find(int64(s.b[i])<<32 | int64(s.c[i])).val
				nation := q.supp.find(int64(s.c[i])).val
				t := push[T9Tuple](p, partOf(hash64(uint64(s.d[i]))))
				t.okey, t.nation = s.d[i], int32(nation)
				t.amount = int64(s.f[i])*int64(100-s.g[i]) - cost*int64(s.e[i])
			}
		}
	}
	p.close()
}
func (q *T9) ordersTask(tid int) {
	s := scratch[tid]
	p := parts2[tid]
	p.init(&arena[tid], unsafe.Sizeof(T9Order{}))
	for b := q.ctr.take(); b >= 0; b = q.ctr.take() {
		for st, count := 0, int(q.oOrderkey.dir[b].count); st < count; st += VEC {
			n := min(count-st, VEC)
			unpack(&q.oOrderkey, b, st, n, s.a[:])
			unpack(&q.oOrderdate, b, st, n, s.b[:])
			key, date, h := s.a[:n], s.b[:n], s.h[:n]
			hashKeys(key, h)
			for i := range h {
				*push[T9Order](p, partOf(h[i])) = T9Order{key[i], date[i]}
			}
		}
	}
	p.close()
}
func (q *T9) joinTask(tid int) {
	a := &arena[tid]
	agg := newMap(a, 1024)
	for k := q.ctr.take(); k >= 0; k = q.ctr.take() {
		n := partsCount(parts, k)
		if n == 0 {
			continue
		}
		tu, next := array[T9Tuple](a, n), array[int32](a, n)
		m := newMap(a, pow2For(n)) // commande -> rang de son dernier tuple ; next chaîne les tuples d'une même commande
		i := 0
		for _, p := range parts {
			for c := p.head[k]; c != nil; c = c.next {
				for _, t := range tuples[T9Tuple](c) {
					cell, fresh := m.upsertFresh(int64(t.okey))
					tu[i], next[i] = t, -1
					if !fresh {
						next[i] = int32(cell.val)
					}
					cell.val = int64(i)
					i++
				}
			}
		}
		for _, p := range parts2 {
			for c := p.head[k]; c != nil; c = c.next {
				for _, o := range tuples[T9Order](c) {
					cell := m.find(int64(o.okey))
					if cell == nil {
						continue
					}
					year := yearOf(o.date)
					for j := int32(cell.val); j >= 0; j = next[j] {
						agg.upsert(int64(tu[j].nation)<<16 | year).val += tu[j].amount
					}
				}
			}
		}
	}
	q.agg[tid] = agg
}
func (q *T9) run() {
	a0, s := &arena[0], scratch[0]
	q.ctr.set(q.pName.nblocks)
	pool.run(q.partTask)
	n := 0
	for t := range NT {
		n += len(q.l1[t].v)
	}
	q.part, q.fpart = newMap(a0, pow2For(uint64(n))), newBloom(a0, uint64(n))
	for t := range NT {
		for _, key := range q.l1[t].v {
			q.part.upsert(key)
			q.fpart.add(hash64(uint64(key)))
		}
	}
	q.ctr.set(q.psPartkey.nblocks)
	pool.run(q.psTask)
	n = 0
	for t := range NT {
		n += len(q.l1[t].v)
	}
	q.ps = newMap(a0, pow2For(uint64(n)))
	for t := range NT {
		for i, key := range q.l1[t].v {
			q.ps.upsert(key).val = q.l2[t].v[i]
		}
	}
	q.supp = newMap(a0, pow2For(q.sSuppkey.nrows))
	for b := range int(q.sSuppkey.nblocks) {
		for st, count := 0, int(q.sSuppkey.dir[b].count); st < count; st += VEC {
			m := min(count-st, VEC)
			unpack(&q.sSuppkey, b, st, m, s.a[:])
			unpack(&q.sNationkey, b, st, m, s.b[:])
			for i := range m {
				q.supp.upsert(int64(s.a[i])).val = int64(s.b[i])
			}
		}
	}
	q.ctr.set(q.lPartkey.nblocks)
	pool.run(q.lineTask)
	q.ctr.set(q.oOrderkey.nblocks)
	pool.run(q.ordersTask)
	q.ctr.set(NPART)
	pool.run(q.joinTask)
	// fusion ; nation -> nom ; tri par nom puis année décroissante
	total := newMap(a0, 1024)
	for t := range NT {
		for _, c := range q.agg[t].all() {
			if c.key != -1 {
				total.upsert(c.key).val += c.val
			}
		}
	}
	nat := newMap(a0, 64)
	nn := int(q.nNationkey.nrows)
	unpack(&q.nNationkey, 0, 0, nn, s.a[:])
	unpack(&q.nName, 0, 0, nn, s.b[:])
	for i := range nn {
		nat.upsert(int64(s.a[i])).val = int64(s.b[i])
	}
	type row struct {
		name      []byte
		year, sum int64
	}
	rows := make([]row, 0, total.count)
	for _, c := range total.all() {
		if c.key != -1 {
			rows = append(rows, row{q.nName.dict(uint32(nat.find(c.key >> 16).val)), c.key & 0xFFFF, c.val})
		}
	}
	slices.SortFunc(rows, func(a, b row) int {
		return cmp.Or(bytes.Compare(a.name, b.name), cmp.Compare(b.year, a.year))
	})
	for _, r := range rows {
		emit(r.name, "|", r.year, "|", r.sum, "\n")
	}
}

// ================================================================================================ T18 (TPC-H Q18)

type KQ struct{ key, qty int32 }
type T18 struct {
	lOrderkey, lQty, oOrderkey, oCustkey, oOrderdate, oTotalprice, cCustkey, cName Col
	ctr                                                                            Counter
	l1, l2, l3, l4                                                                 [MAXT]List
	big, cust                                                                      Map
	sums                                                                           [MAXT]Map
	fbig, fcust                                                                    Bloom
}

func (q *T18) open() {
	q.lOrderkey, q.lQty = colOpen("lineitem", "l_orderkey"), colOpen("lineitem", "l_quantity")
	q.oOrderkey, q.oCustkey = colOpen("orders", "o_orderkey"), colOpen("orders", "o_custkey")
	q.oOrderdate, q.oTotalprice = colOpen("orders", "o_orderdate"), colOpen("orders", "o_totalprice")
	q.cCustkey, q.cName = colOpen("customer", "c_custkey"), colOpen("customer", "c_name")
}
func (q *T18) scatterTask(tid int) { // lineitem réparti par commande
	s := scratch[tid]
	p := parts[tid]
	p.init(&arena[tid], unsafe.Sizeof(KQ{}))
	for b := q.ctr.take(); b >= 0; b = q.ctr.take() {
		for st, count := 0, int(q.lOrderkey.dir[b].count); st < count; st += VEC {
			n := min(count-st, VEC)
			unpack(&q.lOrderkey, b, st, n, s.a[:])
			unpack(&q.lQty, b, st, n, s.b[:])
			key, qty, h := s.a[:n], s.b[:n], s.h[:n]
			hashKeys(key, h)
			for i := range h {
				*push[KQ](p, partOf(h[i])) = KQ{key[i], qty[i]}
			}
		}
	}
	p.close()
}
func (q *T18) aggTask(tid int) { // une partition : somme par commande ; garde celles de plus de 300 unités
	a := &arena[tid]
	l := &q.l1[tid]
	l.init(a)
	for k := q.ctr.take(); k >= 0; k = q.ctr.take() {
		m := newMap(a, pow2Start(partsCount(parts, k)))
		for _, p := range parts {
			for c := p.head[k]; c != nil; c = c.next {
				for _, t := range tuples[KQ](c) {
					m.upsert(int64(t.key)).val += int64(t.qty)
				}
			}
		}
		for _, c := range m.all() {
			if c.key != -1 && c.val > 30000 {
				l.push(c.key)
			}
		}
	}
}
func (q *T18) ordersTask(tid int) { // commandes retenues : client, date, prix
	s := scratch[tid]
	l1, l2, l3, l4 := &q.l1[tid], &q.l2[tid], &q.l3[tid], &q.l4[tid]
	for _, l := range []*List{l1, l2, l3, l4} {
		l.init(&arena[tid])
	}
	for b := q.ctr.take(); b >= 0; b = q.ctr.take() {
		for st, count := 0, int(q.oOrderkey.dir[b].count); st < count; st += VEC {
			n := min(count-st, VEC)
			unpack(&q.oOrderkey, b, st, n, s.a[:])
			k := semi(&q.big, &q.fbig, s.a[:n], st, s.pos[:], s.b[:])
			if k == 0 {
				continue
			}
			unpackSel(&q.oCustkey, b, s.pos[:k], s.c[:])
			unpackSel(&q.oOrderdate, b, s.pos[:k], s.d[:])
			unpackSel(&q.oTotalprice, b, s.pos[:k], s.e[:])
			for i := range k {
				l1.push(int64(s.b[i]))
				l2.push(int64(s.c[i]))
				l3.push(int64(s.d[i]))
				l4.push(int64(s.e[i]))
			}
		}
	}
}
func (q *T18) custTask(tid int) { // clients de ces commandes : position et longueur de leur nom
	s := scratch[tid]
	l1, l2, l3 := &q.l1[tid], &q.l2[tid], &q.l3[tid]
	for _, l := range []*List{l1, l2, l3} {
		l.init(&arena[tid])
	}
	for b := q.ctr.take(); b >= 0; b = q.ctr.take() {
		pos := q.cName.dir[b].auxOff
		for st, count := 0, int(q.cCustkey.dir[b].count); st < count; st += VEC {
			n := min(count-st, VEC)
			unpack(&q.cCustkey, b, st, n, s.a[:])
			unpack(&q.cName, b, st, n, s.b[:])
			for i := range n {
				h := hash64(uint64(s.a[i]))
				if q.fcust.test(h) && q.cust.findH(int64(s.a[i]), h) != nil {
					l1.push(int64(s.a[i]))
					l2.push(int64(pos))
					l3.push(int64(s.b[i]))
				}
				pos += uint64(s.b[i])
			}
		}
	}
}
func (q *T18) sumTask(tid int) { // lineitem des commandes retenues : somme des quantités
	s := scratch[tid]
	m := newMap(&arena[tid], 1024)
	for b := q.ctr.take(); b >= 0; b = q.ctr.take() {
		for st, count := 0, int(q.lOrderkey.dir[b].count); st < count; st += VEC {
			n := min(count-st, VEC)
			unpack(&q.lOrderkey, b, st, n, s.a[:])
			k := semi(&q.big, &q.fbig, s.a[:n], st, s.pos[:], s.b[:])
			if k == 0 {
				continue
			}
			unpackSel(&q.lQty, b, s.pos[:k], s.c[:])
			for i := range k {
				m.upsert(int64(s.b[i])).val += int64(s.c[i])
			}
		}
	}
	q.sums[tid] = m
}
func (q *T18) run() {
	a0 := &arena[0]
	// 1. et 2. agrégation de lineitem par commande ; 3. commandes de plus de 300 unités
	q.ctr.set(q.lOrderkey.nblocks)
	pool.run(q.scatterTask)
	q.ctr.set(NPART)
	pool.run(q.aggTask)
	n := 0
	for t := range NT {
		n += len(q.l1[t].v)
	}
	q.big, q.fbig = newMap(a0, pow2For(uint64(n))), newBloom(a0, uint64(n))
	for t := range NT {
		for _, key := range q.l1[t].v {
			q.big.upsert(key)
			q.fbig.add(hash64(uint64(key)))
		}
	}
	// 4. leurs lignes dans orders
	q.ctr.set(q.oOrderkey.nblocks)
	pool.run(q.ordersTask)
	type row struct {
		okey, cust, date, price, sum int64
		name                         []byte
	}
	rows := make([]row, 0, n)
	q.cust, q.fcust = newMap(a0, pow2For(uint64(n))), newBloom(a0, uint64(n))
	for t := range NT {
		for i, okey := range q.l1[t].v {
			c := q.l2[t].v[i]
			rows = append(rows, row{okey: okey, cust: c, date: q.l3[t].v[i], price: q.l4[t].v[i]})
			q.cust.upsert(c)
			q.fcust.add(hash64(uint64(c)))
		}
	}
	// 5. leurs clients ; 6. leurs lignes dans lineitem
	q.ctr.set(q.cCustkey.nblocks)
	pool.run(q.custTask)
	name := newMap(a0, pow2For(uint64(n))) // client -> rang dans les listes
	names := make([][]byte, 0, n)
	for t := range NT {
		for i, c := range q.l1[t].v {
			name.upsert(c).val = int64(len(names))
			pos := uint64(q.l2[t].v[i])
			names = append(names, q.cName.aux[pos:pos+uint64(q.l3[t].v[i])])
		}
	}
	q.ctr.set(q.lOrderkey.nblocks)
	pool.run(q.sumTask)
	for i := range rows {
		r := &rows[i]
		for t := range NT {
			if c := q.sums[t].find(r.okey); c != nil {
				r.sum += c.val
			}
		}
		r.name = names[name.find(r.cust).val]
	}
	slices.SortFunc(rows, func(a, b row) int { // prix décroissant, date, commande
		return cmp.Or(cmp.Compare(b.price, a.price), cmp.Compare(a.date, b.date), cmp.Compare(a.okey, b.okey))
	})
	for _, r := range rows[:min(len(rows), 100)] {
		emit(r.name, "|", r.cust, "|", r.okey, "|", r.date, "|", r.price, "|", r.sum, "\n")
	}
}

// ================================================================================================ C4

type C4 struct {
	uid Col
	ctr Counter
}

func (q *C4) open() { q.uid = colOpen("hits", "UserID") }
func (q *C4) run() {
	var counts [MAXT][8]uint64
	var minus1 [MAXT][8]bool
	q.ctr.set(q.uid.nblocks)
	pool.run(func(tid int) {
		s := scratch[tid]
		p := parts[tid]
		p.init(&arena[tid], 8)
		for b := q.ctr.take(); b >= 0; b = q.ctr.take() {
			// 64 bits : valeurs telles quelles
			v := unsafe.Slice((*int64)(unsafe.Pointer(&q.uid.words(b)[0])), q.uid.dir[b].count)
			for st := 0; st < len(v); st += VEC {
				vv := v[st:min(st+VEC, len(v))]
				h := s.h[:len(vv)]
				hashLongs(vv, h)
				for i := range h {
					*push[int64](p, partOf(h[i])) = vv[i]
				}
			}
		}
		p.close()
	})
	q.ctr.set(NPART)
	pool.run(func(tid int) {
		count := uint64(0)
		for k := q.ctr.take(); k >= 0; k = q.ctr.take() {
			m := newMap(&arena[tid], pow2Start(partsCount(parts, k)))
			for _, p := range parts {
				for c := p.head[k]; c != nil; c = c.next {
					for _, t := range tuples[int64](c) {
						if t == -1 {
							minus1[tid][0] = true // la valeur qui marque les cases vides est comptée à part
						} else {
							m.upsert(t)
						}
					}
				}
			}
			count += m.count
		}
		counts[tid][0] = count
	})
	count := uint64(0)
	for t := range NT {
		count += counts[t][0]
	}
	for t := range NT {
		if minus1[t][0] {
			count++
			break
		}
	}
	emit(count, "\n")
}

// ================================================================================================ agrégations par chaîne

// C12, C16, C33, C36 : les lignes retenues sont hachées, réparties, puis agrégées partition par partition ; chaque
// fil garde ses dix premiers groupes.
type STuple struct {
	hash     uint64
	ikey     int64
	pos      uint64
	len, pad uint32
}
type CS struct {
	str, uid, counter, date, dch, refresh Col
	ctr                                   Counter
	mode                                  int // 12, 16, 33, 36
	lo, hi                                int32
	top                                   [MAXT]Top10
}

func (q *CS) open(mode int) {
	q.mode = mode
	if mode == 12 || mode == 16 {
		q.str = colOpen("hits", "SearchPhrase")
	} else {
		q.str = colOpen("hits", "URL")
	}
	if mode == 16 {
		q.uid = colOpen("hits", "UserID")
	}
	if mode == 36 {
		q.counter, q.date = colOpen("hits", "CounterID"), colOpen("hits", "EventDate")
		q.dch, q.refresh = colOpen("hits", "DontCountHits"), colOpen("hits", "IsRefresh")
		q.lo, q.hi = daysFromCivil(2013, 7, 1), daysFromCivil(2013, 7, 31)
	}
}
func b2i(b bool) int { // 0 ou 1, sans branchement
	if b {
		return 1
	}
	return 0
}
func (q *CS) scatterTask(tid int) {
	s := scratch[tid]
	p := parts[tid]
	p.init(&arena[tid], unsafe.Sizeof(STuple{}))
	bytes := unsafe.Pointer(&q.str.aux[0])
	for b := q.ctr.take(); b >= 0; b = q.ctr.take() {
		if q.mode == 36 { // cartes de zones : compteur et date
			ec, ed := &q.counter.dir[b], &q.date.dir[b]
			if ec.min > 62 || ec.max < 62 || ed.max < int64(q.lo) || ed.min > int64(q.hi) {
				continue
			}
		}
		count := int(q.str.dir[b].count)
		var uid []int64
		if q.mode == 16 {
			uid = unsafe.Slice((*int64)(unsafe.Pointer(&q.uid.words(b)[0])), count)
		}
		pos := q.str.dir[b].auxOff
		for st := 0; st < count; st += VEC {
			n := min(count-st, VEC)
			unpack(&q.str, b, st, n, s.a[:]) // longueurs
			length, x := s.a[:n], s.x[:n]
			for i := range x {
				x[i] = int64(pos)
				pos += uint64(length[i])
			}
			k := 0
			switch q.mode {
			case 36:
				unpack(&q.counter, b, st, n, s.b[:])
				k = selBetween(s.b[:n], 62, 62, uint32(st), s.pos[:])
				if k == 0 {
					continue
				}
				unpackSel(&q.date, b, s.pos[:k], s.c[:])
				unpackSel(&q.dch, b, s.pos[:k], s.d[:])
				unpackSel(&q.refresh, b, s.pos[:k], s.e[:])
				k2 := 0
				for i := range k {
					j := int(s.pos[i]) - st
					s.sel[k2] = int32(j)
					k2 += b2i(s.c[i] >= q.lo) & b2i(s.c[i] <= q.hi) & b2i(s.d[i] == 0) & b2i(s.e[i] == 0) & b2i(length[j] > 0)
				}
				k = k2
			case 12:
				k = selBetween(length, 1, math.MaxInt32, 0, s.sel[:])
			default:
				for i := range n {
					s.sel[i] = int32(i)
				}
				k = n
			}
			sel, h := s.sel[:k], s.h[:k]
			for j, i := range sel {
				h[j] = hashBytes(unsafe.Add(bytes, x[i]), uint64(length[i]))
			}
			if uid != nil {
				for j, i := range sel {
					if h[j] = hash64(h[j] ^ uint64(uid[st+int(i)])*K2); h[j] == 0 {
						h[j] = 1
					}
				}
			}
			for j, i := range sel {
				t := push[STuple](p, partOf(h[j]))
				t.hash, t.pos, t.len = h[j], uint64(x[i]), uint32(length[i])
				if uid != nil {
					t.ikey = uid[st+int(i)]
				} else {
					t.ikey = 0
				}
			}
		}
	}
	p.close()
}
func (q *CS) aggTask(tid int) {
	top := &q.top[tid]
	top.n, top.bytes = 0, q.str.aux
	for k := q.ctr.take(); k >= 0; k = q.ctr.take() {
		m := newSMap(&arena[tid], pow2Start(partsCount(parts, k)), q.str.aux)
		for _, p := range parts {
			for c := p.head[k]; c != nil; c = c.next {
				for _, t := range tuples[STuple](c) {
					m.add(t.hash, t.ikey, t.pos, t.len)
				}
			}
		}
		for _, c := range unsafe.Slice((*SCell)(m.cells), m.mask+1) {
			if c.hash != 0 {
				top.add(Top{c.count, c.len, c.ikey, c.pos})
			}
		}
	}
}
func (q *CS) run() {
	q.ctr.set(q.str.nblocks)
	pool.run(q.scatterTask)
	q.ctr.set(NPART)
	pool.run(q.aggTask)
	all := Top10{bytes: q.str.aux}
	for t := range NT {
		for _, x := range q.top[t].t[:q.top[t].n] {
			all.add(x)
		}
	}
	for _, t := range all.t[:all.n] {
		if q.mode == 16 {
			emit(t.ikey, "|")
		}
		emit(q.str.aux[t.pos:t.pos+uint64(t.len)], "|", t.count, "\n")
	}
}

// ================================================================================================ C20

type C20 struct {
	url Col
	ctr Counter
}

func (q *C20) open() { q.url = colOpen("hits", "URL") }
func (q *C20) run() {
	var counts [MAXT][8]uint64
	q.ctr.set(q.url.nblocks)
	pool.run(func(tid int) {
		s := scratch[tid]
		count := 0
		for b := q.ctr.take(); b >= 0; b = q.ctr.take() {
			nbytes := blockLengths(&q.url, b, s.len[:])
			count += searchBlock(q.url.aux[q.url.dir[b].auxOff:], nbytes, s.len[:], "google", s.rows[:])
		}
		counts[tid][0] = uint64(count)
	})
	count := uint64(0)
	for t := range NT {
		count += counts[t][0]
	}
	emit(count, "\n")
}

// ================================================================================================ principal

func main() {
	if len(os.Args) < 5 {
		die("usage : olap <requête> <fils> <répétitions> <répertoire des données> [--print]")
	}
	q := os.Args[1]
	NT, _ = strconv.Atoi(os.Args[2])
	reps, _ := strconv.Atoi(os.Args[3])
	dataDir = os.Args[4]
	doPrint := len(os.Args) > 5 && os.Args[5] == "--print"
	if NT < 1 || NT > MAXT {
		die("nombre de fils")
	}
	runtime.GOMAXPROCS(NT)
	for y := range yearStart {
		yearStart[y] = daysFromCivil(1970+y, 1, 1)
	}
	for t := range NT {
		scratch[t] = (*Scratch)(hugeAlloc(unsafe.Sizeof(Scratch{})))
		parts = append(parts, (*Parts)(hugeAlloc(unsafe.Sizeof(Parts{}))))
		parts2 = append(parts2, (*Parts)(hugeAlloc(unsafe.Sizeof(Parts{}))))
	}
	var run func()
	switch q {
	case "t1":
		x := new(T1)
		x.open()
		run = x.run
	case "t6":
		x := new(T6)
		x.open()
		run = x.run
	case "t9":
		x := new(T9)
		x.open()
		run = x.run
	case "t18":
		x := new(T18)
		x.open()
		run = x.run
	case "c4":
		x := new(C4)
		x.open()
		run = x.run
	case "c12", "c16", "c33", "c36":
		x := new(CS)
		mode, _ := strconv.Atoi(q[1:])
		x.open(mode)
		run = x.run
	case "c20":
		x := new(C20)
		x.open()
		run = x.run
	default:
		die("requête inconnue")
	}
	pool.start(NT)
	for r := range reps {
		for t := range NT {
			arena[t].reset()
		}
		res = res[:0]
		t0 := time.Now()
		run()
		dt := time.Since(t0).Seconds()
		fmt.Printf("RESULT;%s;%s;%d;%d;%.6f;%016x\n", q, level, NT, r, dt, fnv1a(res))
		if doPrint && r == reps-1 {
			os.Stdout.Write(res)
		}
	}
}
