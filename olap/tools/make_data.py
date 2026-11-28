#!/usr/bin/env python3
"""Données de la v7 dans le format commun (docs/V7.md, 5) : TPC-H et le sous-ensemble de ClickBench.

Usage : make_data.py tpch <échelle> <répertoire>     ex. tpch 10 /opt/olap/data/sf10
        make_data.py hits <partitions> <répertoire>  ex. hits 0,5,...,95 /opt/olap/data/hits20 ; « small » : 20 000
                                                     lignes de chacune des vingt partitions, à partir de la 600 000e
                                                     (la partition 0 y a des lignes du compteur 62, que lit C36)

TPC-H vient du générateur de DuckDB (extension tpch), dans une base gardée à côté des colonnes (tpch.duckdb : c'est
aussi le stockage du repère DuckDB). ClickBench vient de ses partitions Parquet, téléchargées dans
<répertoire>/parquet et vérifiées par leur empreinte (olap/data/hits.sha256). Seules les colonnes que lisent les dix
requêtes sont écrites. Chaque répertoire reçoit un manifeste (manifest.json) : lignes, genre, taille et empreinte de
chaque colonne. Demande l'environnement Python de olap/tools/requirements.txt (duckdb, pyarrow, numpy)."""
import hashlib, json, os, sys, time, urllib.request
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
    for table, cols in TPCH.items():
        t = time.time()
        kinds, dicts = {}, {}
        typ = dict((r[0], r[1]) for r in con.execute(f"DESCRIBE {table}").fetchall())
        for c in cols:
            if c in DICT_COLS:
                kinds[c] = msc.DICT
                dicts[c] = sorted(r[0].encode() for r in con.execute(f"SELECT DISTINCT {c} FROM {table}").fetchall())
            else:
                kinds[c] = msc.STR if typ[c] == "VARCHAR" else msc.INT
        sel = ", ".join(f"{e} AS {c}" for c, e in cols.items())
        con.execute("SET preserve_insertion_order=true")
        reader = con.sql(f"SELECT {sel} FROM {table}").to_arrow_reader(BATCH)
        manifest["tables"][table] = write_table(reader, list(cols), os.path.join(out, table), kinds, dicts)
        rows = next(iter(manifest["tables"][table].values()))["rows"]
        print(f"{table} : {rows} lignes, {len(cols)} colonnes, {time.time() - t:.0f} s", flush=True)
    json.dump(manifest, open(os.path.join(out, "manifest.json"), "w"), indent=1, sort_keys=True)
    con.close()


def hits(parts, out, small=False):
    os.makedirs(os.path.join(out, "parquet"), exist_ok=True)
    want = dict(line.split()[::-1] for line in open(os.path.join(HERE, "..", "data", "hits.sha256")))

    def batches():
        for p in parts:
            name = f"hits_{p}.parquet"
            path = os.path.join(out, "parquet", name)
            if not os.path.exists(path):
                urllib.request.urlretrieve(URL.format(p), path + ".part")
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

    kinds = {c: msc.STR if c in ("SearchPhrase", "URL") else msc.INT for c in HITS}
    man = write_table(batches(), HITS, os.path.join(out, "hits"), kinds, {})
    manifest = {"source": "ClickBench, hits_compatible/athena_partitioned, partitions " + ",".join(map(str, parts))
                          + (f" ({SMALL_ROWS} lignes de chacune à partir de la ligne {SMALL_FROM})" if small else ""),
                "tables": {"hits": man}}
    json.dump(manifest, open(os.path.join(out, "manifest.json"), "w"), indent=1, sort_keys=True)


if __name__ == "__main__":
    what, arg, out = sys.argv[1:4]
    if what == "tpch":
        tpch(float(arg), out)
    elif what == "hits":
        hits(PARTS, out, small=True) if arg == "small" else hits([int(x) for x in arg.split(",")], out)
    else:
        raise SystemExit(__doc__)
