"""v4, point 6 (docs/V4_OPEN.md, 7, calcul 7) : relevé des régions des formes op_*, délimitées à la lecture des copies
bench/<langage>_op, avec les règles de lecture du point 5 (tools/cost/regions.py ; docs/V4_COST.md, 3.2 et 8).

LANGS[langage] = {
  "dir": répertoire de la copie,
  "files": {fichier: empreinte git ; tools/open/count_op.py refuse de compter si un fichier a changé},
  "regions": {nom: [(fichier, première ligne, dernière ligne), …]} (lignes de la copie _op, bornes comprises),
  "forms": {"noyau|variante|paramètre": (fonction d'entrée, [régions])},
}
Une région « cv:<nom> » est la région <nom> du relevé du point 5 (copie bench/<langage>_cv, à l'empreinte qu'il
nomme), transposée dans la copie _op par correspondance des lignes (les copies _op sont les copies _cv plus des
lignes) : une forme op_* qui réemploie une fonction de la forme d'accès la compte comme le point 5 l'a comptée.
Règles appliquées en plus de celles du point 5 : le chargement des données reste au harnais, y compris dans les
processus d'amphp (op_load, op_k6_cols) ; l'horloge murale des fils de Lua (wall) relève de la mesure du temps ; la
conversion des données dans la représentation que la bibliothèque demande (tableaux NumPy en colonnes SoA, conteneur
SOA de D, vecteurs et matrices de vmsl, chaînes des fils llthreads2 et des tâches d'amphp, mat.Dense de gonum) et les
réserves de fils ou de processus appartiennent à la forme ; les directives d'import n'appartiennent à aucune forme."""


def _r(f, *spans):
    out = []
    for s in spans:
        a, _, b = str(s).partition("-")
        out.append((f, int(a), int(b or a)))
    return out


def _f(entry, *regions):
    return (entry, list(regions))


LANGS = {}

LANGS["python"] = {
    "dir": "bench/python_op",
    "files": {"ms.py": "9151ad553930499ab45e41dcc926539ae4b63528"},
    "regions": {
        "pool4": _r("ms.py", "863-891"),
        "k1_np": _r("ms.py", "897", "902-903"),
        "k4_np": _r("ms.py", "911"),
        "k5_np": _r("ms.py", "921"),
        "q6_np": _r("ms.py", "934-938"),
        "q1_np": _r("ms.py", "941-955"),
        "k6_np_mt": _r("ms.py", "966-967", "969-970", "973-974", "976"),
        "k6_dask": _r("ms.py", "982-983", "993"),
        "q6_dask": _r("ms.py", "985-986"),
        "q1_dask": _r("ms.py", "988-992"),
        "k9_np_rows": _r("ms.py", "1006-1013"),
        "k9_np": _r("ms.py", "1020"),
        "k9_np_mt": _r("ms.py", "1021-1023", "1040", "1052-1053"),
        "k9_dask": _r("ms.py", "1027-1030", "1042-1044"),
        "k3_dask": _r("ms.py", "1061", "1063-1067", "1072"),
    },
    "forms": {
        "k1|op_numpy|energy": _f("dot", "k1_np"),
        "k4|op_numpy|": _f("sum", "k4_np"),
        "k5|op_numpy|": _f("dot", "k5_np"),
        "k6|op_numpy|q6": _f("q6_np", "q6_np"),
        "k6|op_numpy|q1": _f("q1_np", "q1_np"),
        "k6|op_numpy_mt|q6": _f("ThreadPool4", "k6_np_mt", "pool4", "q6_np"),
        "k6|op_numpy_mt|q1": _f("ThreadPool4", "k6_np_mt", "pool4", "q1_np"),
        "k6|op_dask_mt|q6": _f("from_array", "k6_dask", "q6_dask"),
        "k6|op_dask_mt|q1": _f("map_blocks", "k6_dask", "q1_dask", "q1_np"),
        "k9|op_numpy|": _f("k9_np_rows", "k9_np_rows", "k9_np"),
        "k9|op_numpy_mt|": _f("ThreadPool4", "k9_np_mt", "pool4", "k9_np_rows"),
        "k9|op_dask_mt|": _f("map_overlap", "k9_dask"),
        "k3|op_dask|": _f("delayed", "k3_dask"),
    },
}

LANGS["rust"] = {
    "dir": "bench/rust_op",
    "files": {"ms.rs": "05a687f1778d9b98cf339c310a2c1dde93f1a83b"},
    "regions": {
        "op_k3_threads": _r("ms.rs", "1071-1079"),
        "op_cache_padded": _r("ms.rs", "1083", "1087-1088"),
        "op_crossbeam": _r("ms.rs", "1091-1092"),
        "op_libc": _r("ms.rs", "1095-1101"),
        "op_bumpalo": _r("ms.rs", "1110-1163", "1171", "1179"),
    },
    "forms": {
        "k3|op_cache_padded|": _f("cache_padded", "op_cache_padded", "op_k3_threads"),
        "k3|op_crossbeam|": _f("crossbeam", "op_crossbeam", "op_k3_threads"),
        "k3|op_libc|": _f("sysconf", "op_libc", "op_k3_threads"),
        "k8|op_bumpalo|": _f("bb_build", "op_bumpalo"),
    },
}

LANGS["mojo"] = {
    "dir": "bench/mojo_op",
    "files": {"ms.mojo": "5c40b940cab3c501d8208cd739b1d2123456d2cb"},
    "regions": {
        "op_k3": _r("ms.mojo", "949", "954-958"),
        "op_k6": _r("ms.mojo", "972", "975-977", "984-985"),
        "op_k6_q6": _r("ms.mojo", "982-983"),
        "op_k6_q1": _r("ms.mojo", "978-981"),
        "op_k9": _r("ms.mojo", "1001-1003"),
    },
    "forms": {
        "k3|op_max|": _f("sync_parallelize", "op_k3"),
        "k6|op_max|q6": _f("sync_parallelize", "op_k6", "op_k6_q6", "cv:q6_tuned", "cv:simd_i", "cv:q6_natural"),
        "k6|op_max|q1": _f("sync_parallelize", "op_k6", "op_k6_q1", "cv:fold", "cv:q1_tuned_v", "cv:simd_i",
                           "cv:q1_natural"),
        "k9|op_max|": _f("sync_parallelize", "op_k9", "cv:k9_rows"),
    },
}

LANGS["d"] = {
    "dir": "bench/d_op",
    "files": {"ms.d": "2989abdbeb7963d9d740c116e4958ffb738f83a4"},
    "regions": {
        "vec_aliases": _r("ms.d", "26-27"),
        "k1_soau": _r("ms.d", "89-107"),
        "op_soa": _r("ms.d", "152-155"),
    },
    "forms": {"k1|op_soa|energy": _f("SOA", "op_soa", "k1_soau", "vec_aliases")},
}

LANGS["ada"] = {
    "dir": "bench/ada_op",
    "files": {"ms.adb": "083a3f54a6b7321a2408edd9cf0032f29b24f196"},
    "regions": {"op_k3": _r("ms.adb", "375-396", "405-411")},
    "forms": {"k3|op_cachelines|": _f("Worker", "op_k3")},
}

LANGS["swift"] = {
    "dir": "bench/swift_op",
    "files": {"ms.swift": "ddd82e66b9dbc87703a1325d9bd3210daa66f4fc"},
    "regions": {"op_arena": _r("ms.swift", "864-918", "922", "927-932", "940", "951-953")},
    "forms": {"k8|op_arena|": _f("opBuild", "op_arena")},
}

LANGS["julia"] = {
    "dir": "bench/julia_op",
    "files": {"ms.jl": "61719239f2f19c45741d9b876d3cd18ed1401968"},
    "regions": {"anode": _r("ms.jl", "903-905"),
                "op_bumper": _r("ms.jl", "1023-1051", "1057-1060", "1066-1067", "1070")},
    "forms": {"k8|op_bumper|": _f("ob_build_it", "op_bumper", "anode")},
}

LANGS["go"] = {
    "dir": "bench/go_op",
    "files": {"ms.go": "78b859d2054c3fad99cb495a15b96ce21bba48e9"},
    "regions": {
        "op_k3": _r("ms.go", "1105-1108", "1115-1119", "1121-1122", "1124-1132"),
        "k9_gonum": _r("ms.go", "1145-1151", "1160"),
        "k9_gonum_mt": _r("ms.go", "1173-1181"),
    },
    "forms": {
        "k3|op_cpu|": _f("opPadded", "op_k3"),
        "k9|op_gonum|": _f("k9Gonum", "k9_gonum"),
        "k9|op_gonum_mt|": _f("k9Gonum", "k9_gonum", "k9_gonum_mt"),
    },
}

LANGS["ocaml"] = {
    "dir": "bench/ocaml_op",
    "files": {"ms.ml": "60921df0e44d399265ceed98f3096d44e0912175"},
    "regions": {
        "ci": _r("ms.ml", "764"),
        "k4_op": _r("ms.ml", "769-775"),
        "q6_op": _r("ms.ml", "788-795"),
        "k6_pool_op": _r("ms.ml", "803", "806-811", "813"),
    },
    "forms": {
        "k4|op_intrinsics|": _f("k4_op", "k4_op", "ci"),
        "k6|op_intrinsics|q6": _f("q6_op", "q6_op", "ci"),
        "k6|op_intrinsics_mt|q6": _f("pool_run", "k6_pool_op", "cv:pool", "q6_op", "ci"),
    },
}

LANGS["js"] = {
    "dir": "bench/js_op",
    "files": {"ms.js": "d132a9fcee3e692434cbc742a553992ca6e4cb37"},
    "regions": {"op_pool": _r("ms.js", "355", "405-422", "426", "429", "434-436")},
    "forms": {"k8|op_pool|": _f("opBuildIt", "op_pool")},
}

LANGS["php"] = {
    "dir": "bench/php_op",
    "files": {"ms.php": "c6985c7d8b567d372ce1da028bac2c6a2199d554",
              "op_worker.php": "e8c16f7408c201499fe561d6b3b40b3107143302"},
    "regions": {
        "op_pool": _r("ms.php", "1160-1168"),
        "k6_amphp": _r("ms.php", "1173-1178", "1185", "1187"),
        "q6_worker": _r("op_worker.php", "33-42", "65-69"),
        "q1_worker": _r("op_worker.php", "44-61", "71-74"),
        "k9_amphp": _r("ms.php", "1199-1200", "1208", "1212-1219", "1230"),
        "k9_worker": _r("op_worker.php", "78-94"),
    },
    "forms": {
        "k6|op_amphp|q6": _f("parallelMap", "k6_amphp", "op_pool", "q6_worker"),
        "k6|op_amphp|q1": _f("parallelMap", "k6_amphp", "op_pool", "q1_worker"),
        "k9|op_amphp|": _f("parallelMap", "k9_amphp", "op_pool", "k9_worker"),
    },
}

LANGS["lua"] = {
    "dir": "bench/lua_op",
    "files": {"ms.lua": "32e072ef0bd007d2e870bbbcc81f1280d1efce17"},
    "regions": {
        "k5_vmsl": _r("ms.lua", "659", "662"),
        "k9_vmsl": _r("ms.lua", "671-683", "685"),
        "dec": _r("ms.lua", "703-727"),
        "pack": _r("ms.lua", "729-736"),
        "bytes_range": _r("ms.lua", "737-741"),
        "q6_thread": _r("ms.lua", "743-754"),
        "q1_thread": _r("ms.lua", "756-773"),
        "k6_threads": _r("ms.lua", "779-785", "790-791"),
        "k6_join_q6": _r("ms.lua", "802"),
        "k6_join_q1": _r("ms.lua", "793-800"),
        "k9_thread": _r("ms.lua", "812-830"),
        "k9_threads": _r("ms.lua", "832", "836", "839-848"),
    },
    "forms": {
        "k5|op_vmsl|": _f("CreateVector", "k5_vmsl"),
        "k9|op_vmsl|": _f("submatrix", "k9_vmsl"),
        "k6|op_llthreads2|q6": _f("llthreads", "k6_threads", "k6_join_q6", "q6_thread", "dec", "pack",
                                  "bytes_range"),
        "k6|op_llthreads2|q1": _f("llthreads", "k6_threads", "k6_join_q1", "q1_thread", "dec", "pack",
                                  "bytes_range"),
        "k9|op_llthreads2|": _f("llthreads", "k9_threads", "k9_thread", "dec", "pack"),
    },
}
