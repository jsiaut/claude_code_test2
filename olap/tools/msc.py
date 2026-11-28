"""Format binaire commun des colonnes de la v7 (docs/V7.md, 5 ; olap/SPEC.md, 2) : écrivain et relecteur.

Un fichier par colonne, petit-boutiste, en blocs de BLOCK lignes décodables séparément :

  en-tête, 64 octets :
     0  char[4]  « MSC1 »
     4  u32      genre : 0 entiers, 1 chaînes en dictionnaire, 2 chaînes en clair
     8  u32      type décodé : 0 les valeurs tiennent sur 32 bits signés, 1 sur 64 bits
    12  u32      lignes par bloc (65 536)
    16  u64      nombre de lignes
    24  u64      nombre de blocs
    32  u64      position du répertoire des blocs
    40  u64      position de la zone des valeurs compactées
    48  u64      position de la zone annexe (genre 1 : dictionnaire ; genre 2 : octets des chaînes)
    56  u64      genre 1 : nombre d'entrées du dictionnaire ; genre 2 : nombre d'octets des chaînes
  répertoire, 40 octets par bloc :
     i64 minimum, i64 maximum, u64 position des valeurs du bloc dans leur zone, u64 position des octets du bloc dans
     la zone annexe (genre 2 ; sinon 0), u32 largeur en bits, u32 nombre de lignes du bloc
  zone des valeurs : pour chaque bloc, ses valeurs moins son minimum, sur « largeur » bits chacune (0 à 32), mises
     bout à bout bit de poids faible d'abord dans des mots de 64 bits ; largeur 64 : les valeurs telles quelles. Le
     dernier groupe de 64 valeurs d'un bloc est complété par des zéros. La zone est suivie de 8 octets nuls.
  genre 1 : les valeurs sont les codes ; zone annexe : u32 positions[entrées + 1], puis les octets des entrées, triées.
  genre 2 : les valeurs sont les longueurs ; zone annexe : les octets des chaînes dans l'ordre des lignes, suivis de
     8 octets nuls.

Le minimum et le maximum d'un bloc (des valeurs, des codes ou des longueurs) servent de carte de zones."""
import os, struct
import numpy as np

BLOCK = 65536
MAGIC = b"MSC1"
INT, DICT, STR = 0, 1, 2
HEADER = struct.Struct("<4sIIIQQQQQQ")
ENTRY = struct.Struct("<qqQQII")


def width_of(span):
    """Largeur d'un bloc dont les valeurs moins le minimum vont de 0 à span : 0 à 32 bits, sinon 64."""
    w = int(span).bit_length()
    return w if w <= 32 else 64


def pack(vals, width):
    """Compacte des valeurs non signées (np.uint64, < 2**width) : mots de 64 bits, groupes de 64 valeurs."""
    n = len(vals)
    if width == 0:
        return np.zeros(0, np.uint64)
    if width == 64:
        return np.ascontiguousarray(vals, np.uint64)
    groups = (n + 63) // 64
    g = np.zeros(groups * 64, np.uint64)
    g[:n] = vals
    g = g.reshape(groups, 64)
    words = np.zeros((groups, width), np.uint64)  # 64 valeurs de « width » bits font « width » mots
    for j in range(64):
        bit = j * width
        idx, sh = bit >> 6, bit & 63
        words[:, idx] |= g[:, j] << np.uint64(sh)
        if sh + width > 64:
            words[:, idx + 1] |= g[:, j] >> np.uint64(64 - sh)
    return words.reshape(-1)


def unpack(words, width, n):
    """Inverse de pack : n valeurs (np.uint64)."""
    if width == 0:
        return np.zeros(n, np.uint64)
    if width == 64:
        return np.array(words[:n], np.uint64)
    groups = (n + 63) // 64
    w = np.asarray(words[:groups * width], np.uint64).reshape(groups, width)
    out = np.zeros((groups, 64), np.uint64)
    mask = np.uint64((1 << width) - 1)
    for j in range(64):
        bit = j * width
        idx, sh = bit >> 6, bit & 63
        v = w[:, idx] >> np.uint64(sh)
        if sh + width > 64:
            v = v | (w[:, idx + 1] << np.uint64(64 - sh))
        out[:, j] = v & mask
    return out.reshape(-1)[:n]


class Writer:
    """Écrit une colonne au fil de l'eau : append() autant de fois qu'il faut, puis close()."""

    def __init__(self, path, kind, dictionary=None):
        self.path, self.kind = path, kind
        self.data = open(path + ".data", "wb")
        self.aux = open(path + ".aux", "wb") if kind == STR else None
        self.entries, self.nrows, self.data_off, self.aux_off = [], 0, 0, 0
        self.pending = np.zeros(0, np.int64)       # valeurs en attente d'un bloc complet
        self.pending_bytes = []                   # genre 2 : octets en attente, dans l'ordre
        self.wide = False
        self.dictionary = dictionary              # genre 1 : liste triée d'octets

    def append(self, values, data=None):
        """values : entiers (genre 0), codes (genre 1) ou longueurs (genre 2) ; data : octets des chaînes (genre 2)."""
        v = np.concatenate([self.pending, np.asarray(values, np.int64)])
        if self.kind == STR:
            self.pending_bytes.append(bytes(data))
        full = len(v) // BLOCK * BLOCK
        self._blocks(v[:full])
        self.pending = v[full:]

    def _blocks(self, v):
        if self.kind == STR and len(v):
            buf = b"".join(self.pending_bytes)
            used = int(v.sum())
            self.aux.write(buf[:used])
            self.pending_bytes = [buf[used:]]
        lens = v
        for a in range(0, len(v), BLOCK):
            b = v[a:a + BLOCK]
            lo, hi = int(b.min()), int(b.max())
            w = width_of(hi - lo)
            if w == 64 or not (-2**31 <= lo and hi < 2**31):
                self.wide = True
            words = pack(b.astype(np.uint64) if w == 64 else (b - lo).astype(np.uint64), w)
            self.data.write(words.tobytes())
            self.entries.append((lo, hi, self.data_off, self.aux_off, w, len(b)))
            self.data_off += words.nbytes
            self.nrows += len(b)
            if self.kind == STR:
                self.aux_off += int(lens[a:a + BLOCK].sum())

    def close(self):
        if len(self.pending):
            last = self.pending
            self.pending = np.zeros(0, np.int64)
            if self.kind == STR:
                buf = b"".join(self.pending_bytes)
                assert len(buf) == int(last.sum()), (len(buf), int(last.sum()))
                self.aux.write(buf)
                self.pending_bytes = []
            lo, hi = int(last.min()), int(last.max())
            w = width_of(hi - lo)
            if w == 64 or not (-2**31 <= lo and hi < 2**31):
                self.wide = True
            words = pack(last.astype(np.uint64) if w == 64 else (last - lo).astype(np.uint64), w)
            self.data.write(words.tobytes())
            self.entries.append((lo, hi, self.data_off, self.aux_off, w, len(last)))
            self.data_off += words.nbytes
            self.nrows += len(last)
            if self.kind == STR:
                self.aux_off += int(last.sum())
        self.data.close()
        aux_count = 0
        if self.kind == STR:
            self.aux.close()
            aux_count = self.aux_off
        off_dir = HEADER.size
        off_data = off_dir + ENTRY.size * len(self.entries)
        off_aux = off_data + self.data_off + 8
        with open(self.path, "wb") as f:
            if self.kind == DICT:
                aux_count = len(self.dictionary)
            f.write(HEADER.pack(MAGIC, self.kind, int(self.wide), BLOCK, self.nrows, len(self.entries), off_dir, off_data,
                                off_aux, aux_count))
            for e in self.entries:
                f.write(ENTRY.pack(*e))
            with open(self.path + ".data", "rb") as d:
                while chunk := d.read(1 << 24):
                    f.write(chunk)
            f.write(b"\0" * 8)
            if self.kind == DICT:
                pos = np.zeros(len(self.dictionary) + 1, np.uint32)
                pos[1:] = np.cumsum([len(x) for x in self.dictionary])
                f.write(pos.tobytes())
                f.write(b"".join(self.dictionary))
                f.write(b"\0" * 8)
            elif self.kind == STR:
                with open(self.path + ".aux", "rb") as d:
                    while chunk := d.read(1 << 24):
                        f.write(chunk)
                f.write(b"\0" * 8)
                os.remove(self.path + ".aux")
        os.remove(self.path + ".data")
        return self.nrows


class Reader:
    """Relecteur d'une colonne (contrôles et essais ; les implémentations du banc ont le leur)."""

    def __init__(self, path):
        self.m = np.memmap(path, dtype=np.uint8, mode="r")
        (magic, self.kind, self.vtype, self.block, self.nrows, self.nblocks, self.off_dir, self.off_data, self.off_aux,
         self.aux_count) = HEADER.unpack(self.m[:HEADER.size].tobytes())
        assert magic == MAGIC and self.block == BLOCK
        raw = self.m[self.off_dir:self.off_dir + ENTRY.size * self.nblocks].tobytes()
        self.entries = [ENTRY.unpack_from(raw, i * ENTRY.size) for i in range(self.nblocks)]

    def block_values(self, b):
        """Valeurs décodées du bloc b (entiers, codes ou longueurs) : np.int64."""
        lo, hi, off, aux, w, n = self.entries[b]
        nwords = n if w == 64 else (n + 63) // 64 * w
        words = np.frombuffer(self.m[self.off_data + off:self.off_data + off + 8 * nwords].tobytes(), np.uint64)
        v = unpack(words, w, n)
        return v.astype(np.int64) if w == 64 else v.astype(np.int64) + lo

    def values(self):
        return np.concatenate([self.block_values(b) for b in range(self.nblocks)]) if self.nblocks else np.zeros(0, np.int64)

    def dictionary(self):
        assert self.kind == DICT
        pos = np.frombuffer(self.m[self.off_aux:self.off_aux + 4 * (self.aux_count + 1)].tobytes(), np.uint32)
        base = self.off_aux + 4 * (self.aux_count + 1)
        return [self.m[base + int(pos[i]):base + int(pos[i + 1])].tobytes() for i in range(self.aux_count)]

    def block_strings(self, b):
        """Chaînes du bloc b (genre 2) : liste d'octets."""
        assert self.kind == STR
        lens = self.block_values(b)
        base = self.off_aux + self.entries[b][3]
        ends = np.cumsum(lens)
        buf = self.m[base:base + int(ends[-1])].tobytes() if len(ends) else b""
        return [buf[int(e - l):int(e)] for l, e in zip(lens, ends)]
