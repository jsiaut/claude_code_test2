#!/usr/bin/env python3
"""Moteurs de référence de la v7 (docs/V7.md, 11) : DuckDB et ClickHouse sur les mêmes lignes que le banc.

Usage : engines.py load <tpch|hits> <répertoire des données>     charge les lignes dans le stockage de chaque moteur
        engines.py expected <tpch|hits> <répertoire> <sortie>    résultats de référence de chaque requête, calculés
                                                                 par DuckDB sous leur forme canonique (olap/SPEC.md,
                                                                 5) et recoupés par ClickHouse ; échec s'ils diffèrent
        engines.py time <tpch|hits> <répertoire> <fils> <répétitions> [requête...] [--engine=duckdb|clickhouse]
                        [--warmup=1]                             temps à chaud des requêtes officielles (olap/queries),
                                                                 une ligne JSON par moteur et par requête

Le répertoire est celui de make_data.py : TPC-H y a sa base DuckDB (tpch.duckdb), ClickBench ses partitions Parquet
(parquet/). DuckDB : paquet Python de olap/tools/requirements.txt. ClickHouse : binaire « clickhouse » (variable
CLICKHOUSE, sinon /opt/clickhouse/usr/bin/clickhouse), en mode local, tables MergeTree sous <répertoire>/clickhouse.
Chaque moteur garde ses réglages par défaut, hors le nombre de fils."""
import json, os, re, statistics, subprocess, sys, time
import duckdb

HERE = os.path.dirname(os.path.abspath(__file__))
CH = os.environ.get("CLICKHOUSE", "/opt/clickhouse/usr/bin/clickhouse")
QUERIES = {"tpch": ["t1", "t6", "t9", "t18"], "hits": ["c4", "c12", "c16", "c20", "c33", "c36"]}

# Forme canonique des résultats : entiers exacts (montants en centièmes, produits en 1e-4 et 1e-6, dates en jours),
# ordre total. DuckDB puis ClickHouse.
C = "CAST({} * 100 AS BIGINT)"
CANON = {
    "t1": ("SELECT l_returnflag, l_linestatus, sum(%(q)s), sum(%(e)s), sum(%(e)s * (100 - %(d)s)), "
           "sum(%(e)s * (100 - %(d)s) * (100 + %(t)s)), sum(%(d)s), count(*) FROM lineitem "
           "WHERE l_shipdate <= DATE '1998-09-02' GROUP BY l_returnflag, l_linestatus ORDER BY l_returnflag, l_linestatus"),
    "t6": ("SELECT sum(%(e)s * %(d)s) FROM lineitem WHERE l_shipdate >= DATE '1994-01-01' AND l_shipdate < DATE '1995-01-01' "
           "AND l_discount BETWEEN 0.05 AND 0.07 AND l_quantity < 24"),
    "t9": ("SELECT n_name, %(year)s AS o_year, sum(%(e)s * (100 - %(d)s) - %(c)s * %(q)s) FROM part, supplier, lineitem, "
           "partsupp, orders, nation WHERE s_suppkey = l_suppkey AND ps_suppkey = l_suppkey AND ps_partkey = l_partkey "
           "AND p_partkey = l_partkey AND o_orderkey = l_orderkey AND s_nationkey = n_nationkey AND p_name LIKE '%%green%%' "
           "GROUP BY n_name, o_year ORDER BY n_name, o_year DESC"),
    "t18": ("SELECT c_name, c_custkey, o_orderkey, %(days)s, %(p)s, sum(%(q)s) FROM customer, orders, lineitem "
            "WHERE o_orderkey IN (SELECT l_orderkey FROM lineitem GROUP BY l_orderkey HAVING sum(l_quantity) > 300) "
            "AND c_custkey = o_custkey AND o_orderkey = l_orderkey GROUP BY c_name, c_custkey, o_orderkey, o_orderdate, "
            "o_totalprice ORDER BY o_totalprice DESC, o_orderdate, o_orderkey LIMIT 100"),
    "c4": "SELECT count(DISTINCT UserID) FROM hits",
    "c12": ("SELECT SearchPhrase, count(*) AS c FROM hits WHERE SearchPhrase <> '' GROUP BY SearchPhrase "
            "ORDER BY c DESC, SearchPhrase LIMIT 10"),
    "c16": ("SELECT UserID, SearchPhrase, count(*) AS c FROM hits GROUP BY UserID, SearchPhrase "
            "ORDER BY c DESC, UserID, SearchPhrase LIMIT 10"),
    "c20": "SELECT count(*) FROM hits WHERE URL LIKE '%%google%%'",
    "c33": "SELECT URL, count(*) AS c FROM hits GROUP BY URL ORDER BY c DESC, URL LIMIT 10",
    "c36": ("SELECT URL, count(*) AS c FROM hits WHERE CounterID = 62 AND EventDate >= '2013-07-01' AND EventDate <= "
            "'2013-07-31' AND DontCountHits = 0 AND IsRefresh = 0 AND URL <> '' GROUP BY URL ORDER BY c DESC, URL LIMIT 10"),
}
SUBST = {
    "duckdb": {"q": C.format("l_quantity"), "e": C.format("l_extendedprice"), "d": C.format("l_discount"),
               "t": C.format("l_tax"), "c": C.format("ps_supplycost"), "p": C.format("o_totalprice"),
               "year": "year(o_orderdate)", "days": "CAST(o_orderdate - DATE '1970-01-01' AS BIGINT)"},
    "clickhouse": {"q": "toInt64(l_quantity * 100)", "e": "toInt64(l_extendedprice * 100)", "d": "toInt64(l_discount * 100)",
                   "t": "toInt64(l_tax * 100)", "c": "toInt64(ps_supplycost * 100)", "p": "toInt64(o_totalprice * 100)",
                   "year": "toYear(o_orderdate)", "days": "toInt32(o_orderdate)"},
}
CH_TPCH = {
    "lineitem": ("l_orderkey Int32, l_linenumber Int32, l_partkey Int32, l_suppkey Int32, l_quantity Decimal(15,2), "
                 "l_extendedprice Decimal(15,2), l_discount Decimal(15,2), l_tax Decimal(15,2), l_returnflag String, "
                 "l_linestatus String, l_shipdate Date", "l_orderkey, l_linenumber"),
    "orders": ("o_orderkey Int32, o_custkey Int32, o_orderdate Date, o_totalprice Decimal(15,2)", "o_orderkey"),
    "part": ("p_partkey Int32, p_name String", "p_partkey"),
    "partsupp": ("ps_partkey Int32, ps_suppkey Int32, ps_supplycost Decimal(15,2)", "ps_partkey, ps_suppkey"),
    "supplier": ("s_suppkey Int32, s_nationkey Int32", "s_suppkey"),
    "nation": ("n_nationkey Int32, n_name String", "n_nationkey"),
    "customer": ("c_custkey Int32, c_name String", "c_custkey"),
}
HITS_COLS = "WatchID, UserID, CounterID, EventTime, EventDate, URL, SearchPhrase, DontCountHits, IsRefresh"


def ch(path, sql, *opts):
    r = subprocess.run([CH, "local", "--path", path, "--multiquery", *opts, "--query", sql], capture_output=True)
    if r.returncode:
        raise SystemExit("clickhouse : " + r.stderr.decode(errors="replace")[-2000:])
    return r


def parts_of(d):
    """Partitions Parquet de ClickBench, dans l'ordre de leur numéro, et tranche prise dans chacune (lignes, début)."""
    man = json.load(open(os.path.join(d, "manifest.json")))
    src = man["source"]
    nums = [int(x) for x in re.search(r"partitions ([0-9,]+)", src).group(1).split(",")]
    m = re.search(r"\((\d+) lignes de chacune à partir de la ligne (\d+)\)", src)
    return [os.path.join(d, "parquet", f"hits_{n}.parquet") for n in nums], ((int(m.group(1)), int(m.group(2))) if m else None)


def load(kind, d):
    chp = os.path.join(d, "clickhouse")
    os.makedirs(chp, exist_ok=True)
    if kind == "tpch":
        con = duckdb.connect(os.path.join(d, "tpch.duckdb"), read_only=True)
        for table, (cols, key) in CH_TPCH.items():
            names = ", ".join(c.split()[0] for c in cols.split(", "))
            tmp = os.path.join(d, f"_{table}.parquet")
            con.execute(f"COPY (SELECT {names} FROM {table}) TO '{tmp}' (FORMAT parquet)")
            ch(chp, f"DROP TABLE IF EXISTS {table}; CREATE TABLE {table} ({cols}) ENGINE = MergeTree ORDER BY ({key}); "
                    f"INSERT INTO {table} SELECT {names} FROM file('{tmp}', Parquet); OPTIMIZE TABLE {table} FINAL;")
            os.remove(tmp)
            n = ch(chp, f"SELECT count() FROM {table}").stdout.decode().strip()
            print(f"clickhouse {table} : {n} lignes", flush=True)
        con.close()
    else:
        files, limit = parts_of(d)
        db = os.path.join(d, "hits.duckdb")
        if os.path.exists(db):
            os.remove(db)
        con = duckdb.connect(db)
        con.execute("SET preserve_insertion_order=true")
        sel = ("SELECT WatchID, UserID, CounterID, EventTime, DATE '1970-01-01' + CAST(EventDate AS INTEGER) AS EventDate, "
               "URL, SearchPhrase, DontCountHits, IsRefresh FROM read_parquet('{}', binary_as_string=True)")
        ch(chp, "DROP TABLE IF EXISTS hits; CREATE TABLE hits (WatchID Int64, UserID Int64, CounterID Int32, EventTime "
                "DateTime, EventDate Date, URL String, SearchPhrase String, DontCountHits Int16, IsRefresh Int16) "
                "ENGINE = MergeTree PRIMARY KEY (CounterID, EventDate, UserID, EventTime, WatchID);")
        for i, f in enumerate(files):
            lim = f" LIMIT {limit[0]} OFFSET {limit[1]}" if limit else ""
            con.execute(("INSERT INTO hits " if i else "CREATE TABLE hits AS ") + sel.format(f) + lim)
            ch(chp, f"INSERT INTO hits SELECT {HITS_COLS} FROM file('{f}', Parquet){lim} "
                    "SETTINGS input_format_parquet_preserve_order = 1, max_threads = 1;")
        con.execute("CHECKPOINT")
        ch(chp, "OPTIMIZE TABLE hits FINAL;")
        print("duckdb hits :", con.execute("SELECT count(*) FROM hits").fetchall()[0][0], "lignes ; clickhouse hits :",
              ch(chp, "SELECT count() FROM hits").stdout.decode().strip(), "lignes", flush=True)
        con.close()


def connect(kind, d):
    return duckdb.connect(os.path.join(d, "tpch.duckdb" if kind == "tpch" else "hits.duckdb"), read_only=True)


def canon_duckdb(con, q):
    rows = con.execute(CANON[q] % SUBST["duckdb"]).fetchall()
    return b"".join(b"|".join(v.encode() if isinstance(v, str) else str(v).encode() for v in r) + b"\n" for r in rows)


def canon_clickhouse(d, q):
    out = ch(os.path.join(d, "clickhouse"), CANON[q] % SUBST["clickhouse"] + " FORMAT TSVRaw").stdout
    return out.replace(b"\t", b"|")


def expected(kind, d, out):
    os.makedirs(out, exist_ok=True)
    con = connect(kind, d)
    bad = 0
    for q in QUERIES[kind]:
        a, b = canon_duckdb(con, q), canon_clickhouse(d, q)
        same = a == b
        bad += not same
        open(os.path.join(out, q + ".txt"), "wb").write(a)
        print(f"{q} : {a.count(10)} lignes ; DuckDB et ClickHouse " + ("identiques" if same else "DIFFÈRENT"), flush=True)
        if not same:
            open(os.path.join(out, q + ".clickhouse.txt"), "wb").write(b)
    if bad:
        raise SystemExit(f"{bad} requêtes dont les deux moteurs ne rendent pas le même résultat")


def official(q, engine):
    sql = open(os.path.join(HERE, "..", "queries", q + ".sql")).read().strip().rstrip(";")
    if engine == "clickhouse" and q == "t9":
        sql = sql.replace("extract(year FROM o_orderdate)", "toYear(o_orderdate)")
    return sql


def timing(kind, d, threads, reps, queries, only=None, warm=1):
    """Chaque requête, dans un même processus du moteur : `warm` exécutions d'échauffement, puis `reps` mesurées."""
    con = connect(kind, d) if only != "clickhouse" else None
    if con:
        con.execute(f"SET threads={threads}")
    for q in queries or QUERIES[kind]:
        if con:
            sql = official(q, "duckdb")
            ts = []
            for i in range(warm + reps):
                t = time.perf_counter()
                con.execute(sql).fetchall()
                ts.append(time.perf_counter() - t)
            print(json.dumps({"engine": "duckdb", "version": duckdb.__version__, "query": q, "threads": threads,
                              "warmup": ts[:warm], "times": ts[warm:], "median": statistics.median(ts[warm:])}), flush=True)
        if only == "duckdb":
            continue
        sql = official(q, "clickhouse")
        r = ch(os.path.join(d, "clickhouse"), ";\n".join([sql + " FORMAT Null"] * (warm + reps)), "--time",
               f"--max_threads={threads}")
        ts = [float(x) for x in re.findall(r"^\d+\.\d+$", r.stderr.decode(), re.M)]
        assert len(ts) == warm + reps, r.stderr.decode()[-500:]
        ver = subprocess.run([CH, "local", "--version"], capture_output=True, text=True).stdout.split()[3]
        print(json.dumps({"engine": "clickhouse", "version": ver, "query": q, "threads": threads, "warmup": ts[:warm],
                          "times": ts[warm:], "median": statistics.median(ts[warm:])}), flush=True)


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    flags = dict(x[2:].split("=", 1) for x in sys.argv[1:] if x.startswith("--"))
    if len(a) >= 3 and a[0] == "load":
        load(a[1], a[2])
    elif len(a) >= 4 and a[0] == "expected":
        expected(a[1], a[2], a[3])
    elif len(a) >= 5 and a[0] == "time":
        timing(a[1], a[2], int(a[3]), int(a[4]), a[5:], flags.get("engine"), int(flags.get("warmup", 1)))
    else:
        raise SystemExit(__doc__)
