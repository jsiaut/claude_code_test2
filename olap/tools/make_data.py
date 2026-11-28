#!/usr/bin/env python3
"""Données de la v7 dans le format commun (docs/V7.md, 5) : TPC-H et le sous-ensemble de ClickBench.

Usage : make_data.py tpch <échelle> <répertoire>     ex. tpch 10 /opt/olap/data/sf10
        make_data.py hits <partitions> <répertoire>  ex. hits 0,5,...,95 /opt/olap/data/hits20 ; « small » : 20 000
                                                     lignes de chacune des vingt partitions, à partir de la 600 000e
                                                     (la partition 0 y a des lignes du compteur 62, que lit C36)
        make_data.py verify <répertoire>             relit chaque colonne par le relecteur de msc.py et la compare,
                                                     ligne à ligne, à sa source (base DuckDB ou partitions Parquet)

TPC-H vient du générateur de DuckDB (extension tpch), dans une base gardée à côté des colonnes (tpch.duckdb : c'est
aussi le stockage du repère DuckDB). ClickBench vient de ses partitions Parquet, téléchargées dans
<répertoire>/parquet et vérifiées par leur empreinte (olap/data/hits.sha256). Seules les colonnes que lisent les dix
requêtes sont écrites. Chaque répertoire reçoit un manifeste (manifest.json) : lignes, genre, taille et empreinte de
chaque colonne. Demande l'environnement Python de olap/tools/requirements.txt (duckdb, pyarrow, numpy)."""
import hashlib, json, os, subprocess, sys, time
import numpy as np
import duckdb
import pyarrow as pa
import pyarrow.parquet as pq

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import msc  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
BATCH = 16 * msc.BLOCK
URL = "https://datasets.clickhouse.com/hits_compatible/athena_partitioned/hits_{}.parquet"
PARTS = list(range(0, 100, 5))
SMALL_ROWS, SMALL_FROM = 20000, 600000

# colonne -> expression SQL (entiers : valeur exacte ; montants en centièmes ; dates en jours depuis 1970-01-01)
cents = lambda c: f"({c} * 100)::BIGINT"  # noqa: E731
days = lambda c: f"({c} - DATE '1970-01-01')::BIGINT"  # noqa: E731
TPCH = {
    "lineitem": {"l_orderkey": "l_orderkey", "l_partkey": "l_partkey", "l_suppkey": "l_suppkey",
                 "l_quantity": cents("l_quantity"), "l_extendedprice": cents("l_extendedprice"),
                 "l_discount": cents("l_discount"), "l_tax": cents("l_tax"), "l_returnflag": "l_returnflag",
                 "l_linestatus": "l_linestatus", "l_shipdate": days("l_shipdate")},
    "orders": {"o_orderkey": "o_orderkey", "o_custkey": "o_custkey", "o_orderdate": days("o_orderdate"),
               "o_totalprice": cents("o_totalprice")},
    "part": {"p_partkey": "p_partkey", "p_name": "p_name"},
    "partsupp": {"ps_partkey": "ps_partkey", "ps_suppkey": "ps_suppkey", "ps_supplycost": cents("ps_supplycost")},
    "supplier": {"s_suppkey": "s_suppkey", "s_nationkey": "s_nationkey"},
    "nation": {"n_nationkey": "n_nationkey", "n_name": "n_name"},
    "customer": {"c_custkey": "c_custkey", "c_name": "c_name"},
}
# Chaînes en dictionnaire : celles qui ont 65 536 valeurs distinctes au plus à l'échelle de la mesure ; les autres
# sont en clair. Le genre d'une colonne est le même à toutes les échelles.
DICT_COLS = {"l_returnflag", "l_linestatus", "n_name"}
HITS = ["UserID", "SearchPhrase", "URL", "CounterID", "EventDate", "DontCountHits", "IsRefresh"]


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(1 << 24):
            h.update(chunk)
    return h.hexdigest()


def string_parts(arr):
    """Longueurs (np.int64) et octets d'un tableau Arrow de chaînes ou d'octets."""
    arr = arr.cast(pa.large_binary()) if not pa.types.is_large_binary(arr.type) else arr
    off = np.frombuffer(arr.buffers()[1], np.int64, len(arr) + 1, arr.offset * 8)
    data = arr.buffers()[2]
    return np.diff(off), (memoryview(data)[int(off[0]):int(off[-1])] if data is not None else b"")


def write_table(batches, columns, out, kinds, dictionaries):
    """Écrit les colonnes d'une table à partir de lots Arrow ; rend le manifeste de la table."""
    os.makedirs(out, exist_ok=True)
    ws = {c: msc.Writer(os.path.join(out, c + ".msc"), kinds[c], dictionaries.get(c)) for c in columns}
    for batch in batches:
        for i, c in enumerate(columns):
            col = batch.column(i)
            if kinds[c] == msc.INT:
                ws[c].append(col.to_numpy(zero_copy_only=False).astype(np.int64))
            elif kinds[c] == msc.DICT:
                codes = {v: k for k, v in enumerate(dictionaries[c])}
                lens, data = string_parts(col)
                raw, ends = bytes(data), np.cumsum(lens)
                ws[c].append(np.array([codes[raw[int(e - n):int(e)]] for n, e in zip(lens, ends)], np.int64))
            else:
                lens, data = string_parts(col)
                ws[c].append(lens, data)
    man = {}
    for c in columns:
        rows = ws[c].close()
        p = os.path.join(out, c + ".msc")
        r = msc.Reader(p)
        man[c] = {"kind": ("int", "dict", "str")[kinds[c]], "type": ("i32", "i64")[r.vtype], "rows": rows,
                  "blocks": r.nblocks, "bytes": os.path.getsize(p), "widths": sorted({e[4] for e in r.entries}),
                  "sha256": sha256(p)}
        if kinds[c] != msc.INT:
            man[c]["string_bytes" if kinds[c] == msc.STR else "dict_entries"] = r.aux_count
    return man


def tpch_tables(con):
    """Pour chaque table de TPC-H : ses colonnes, leurs genres, leurs dictionnaires et les lots Arrow de la source."""
    con.execute("SET preserve_insertion_order=true")
    for table, cols in TPCH.items():
        kinds, dicts = {}, {}
        typ = dict((r[0], r[1]) for r in con.execute(f"DESCRIBE {table}").fetchall())
        for c in cols:
            if c in DICT_COLS:
                kinds[c] = msc.DICT
                dicts[c] = sorted(r[0].encode() for r in con.execute(f"SELECT DISTINCT {c} FROM {table}").fetchall())
            else:
                kinds[c] = msc.STR if typ[c] == "VARCHAR" else msc.INT
        sel = ", ".join(f"{e} AS {c}" for c, e in cols.items())
        yield table, list(cols), kinds, dicts, con.sql(f"SELECT {sel} FROM {table}").to_arrow_reader(BATCH)


def tpch(scale, out):
    os.makedirs(out, exist_ok=True)
    db = os.path.join(out, "tpch.duckdb")
    fresh = not os.path.exists(db)
    con = duckdb.connect(db)
    con.execute("SET threads=4")
    if fresh:
        t = time.time()
        con.execute(f"CALL dbgen(sf={scale})")
        con.execute("CHECKPOINT")
        print(f"dbgen, échelle {scale} : {time.time() - t:.0f} s", flush=True)
    manifest = {"source": f"dbgen de DuckDB {duckdb.__version__}, échelle {scale}", "tables": {}}
    for table, cols, kinds, dicts, reader in tpch_tables(con):
        t = time.time()
        manifest["tables"][table] = write_table(reader, cols, os.path.join(out, table), kinds, dicts)
        rows = next(iter(manifest["tables"][table].values()))["rows"]
        print(f"{table} : {rows} lignes, {len(cols)} colonnes, {time.time() - t:.0f} s", flush=True)
    json.dump(manifest, open(os.path.join(out, "manifest.json"), "w"), indent=1, sort_keys=True)
    con.close()


HITS_KINDS = {c: msc.STR if c in ("SearchPhrase", "URL") else msc.INT for c in HITS}


def hits_batches(parts, out, small):
    """Lots Arrow des partitions de ClickBench, téléchargées au besoin et vérifiées par leur empreinte."""
    os.makedirs(os.path.join(out, "parquet"), exist_ok=True)
    want = dict(line.split()[::-1] for line in open(os.path.join(HERE, "..", "data", "hits.sha256")))
    for p in parts:
        name = f"hits_{p}.parquet"
        path = os.path.join(out, "parquet", name)
        if not os.path.exists(path):  # par curl, comme le documente ClickBench
            subprocess.run(["curl", "-fsSL", "--retry", "3", "-o", path + ".part", URL.format(p)], check=True)
            os.replace(path + ".part", path)
        got = sha256(path)
        if got != want[name]:
            raise SystemExit(f"{name} : empreinte {got}, attendue {want[name]}")
        t = pq.read_table(path, columns=HITS)
        if small:
            t = t.slice(SMALL_FROM, SMALL_ROWS)
        for b in t.to_batches(max_chunksize=BATCH):
            yield b
        print(f"partition {p} : {t.num_rows} lignes", flush=True)


def hits(parts, out, small=False):
    man = write_table(hits_batches(parts, out, small), HITS, os.path.join(out, "hits"), HITS_KINDS, {})
    manifest = {"source": "ClickBench, hits_compatible/athena_partitioned, partitions " + ",".join(map(str, parts))
                          + (f" ({SMALL_ROWS} lignes de chacune à partir de la ligne {SMALL_FROM})" if small else ""),
                "tables": {"hits": man}}
    json.dump(manifest, open(os.path.join(out, "manifest.json"), "w"), indent=1, sort_keys=True)


class Stream:
    """Une colonne relue par msc.Reader, servie dans l'ordre des lignes."""

    def __init__(self, path):
        self.r, self.b, self.vals, self.data = msc.Reader(path), 0, np.zeros(0, np.int64), b""

    def take(self, n):
        """Les n valeurs suivantes (entiers, codes ou longueurs) et, pour des chaînes en clair, leurs octets."""
        while len(self.vals) < n and self.b < self.r.nblocks:
            v = self.r.block_values(self.b)
            if self.r.kind == msc.STR:
                base = self.r.off_aux + self.r.entries[self.b][3]
                self.data += self.r.m[base:base + int(v.sum())].tobytes()
            self.vals = np.concatenate([self.vals, v])
            self.b += 1
        vals, self.vals = self.vals[:n], self.vals[n:]
        if self.r.kind != msc.STR:
            return vals, None
        k = int(vals.sum())
        data, self.data = self.data[:k], self.data[k:]
        return vals, data


def verify_table(batches, columns, out, kinds):
    """Compare chaque colonne relue aux lots de sa source ; rend le nombre de lignes, ou échoue."""
    st = {c: Stream(os.path.join(out, c + ".msc")) for c in columns}
    entries = {c: st[c].r.dictionary() for c in columns if kinds[c] == msc.DICT}
    rows = 0
    for batch in batches:
        for i, c in enumerate(columns):
            col = batch.column(i)
            vals, data = st[c].take(len(col))
            if kinds[c] == msc.INT:
                same = np.array_equal(vals, col.to_numpy(zero_copy_only=False).astype(np.int64))
            else:
                lens, src = string_parts(col)
                if kinds[c] == msc.DICT:  # les codes relus, traduits par le dictionnaire relu
                    d = entries[c]
                    width = {len(e) for e in d}
                    data = (np.frombuffer(b"".join(d), f"S{width.pop()}")[vals].tobytes() if len(width) == 1
                            else b"".join(d[int(k)] for k in vals))
                    vals = np.array([len(e) for e in d], np.int64)[vals]
                same = np.array_equal(vals, lens) and data == bytes(src)
            if not same:
                raise SystemExit(f"{out}/{c} : la colonne relue diffère de sa source vers la ligne {rows}")
        rows += batch.num_rows
    for c in columns:
        if st[c].r.nrows != rows or len(st[c].vals) or st[c].b != st[c].r.nblocks:
            raise SystemExit(f"{out}/{c} : {st[c].r.nrows} lignes écrites, {rows} dans la source")
    return rows


def verify(out):
    src = json.load(open(os.path.join(out, "manifest.json")))["source"]
    if src.startswith("dbgen"):
        con = duckdb.connect(os.path.join(out, "tpch.duckdb"), read_only=True)
        for table, cols, kinds, _, reader in tpch_tables(con):
            print(f"{table} : {len(cols)} colonnes, {verify_table(reader, cols, os.path.join(out, table), kinds)} lignes "
                  "identiques à la source", flush=True)
    else:
        parts = [int(x) for x in src.split("partitions ")[1].split(" ")[0].split(",")]
        rows = verify_table(hits_batches(parts, out, "lignes de chacune" in src), HITS, os.path.join(out, "hits"), HITS_KINDS)
        print(f"hits : {len(HITS)} colonnes, {rows} lignes identiques à la source", flush=True)


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "verify":
        verify(sys.argv[2])
    elif len(sys.argv) == 4 and sys.argv[1] == "tpch":
        tpch(float(sys.argv[2]), sys.argv[3])
    elif len(sys.argv) == 4 and sys.argv[1] == "hits":
        out = sys.argv[3]
        hits(PARTS, out, small=True) if sys.argv[2] == "small" else hits([int(x) for x in sys.argv[2].split(",")], out)
    else:
        raise SystemExit(__doc__)
