# Régions des formes op_* (v4, point 6, calcul 7)

*Écrit par `tools/open/count_op.py` à partir du relevé `tools/open/regions_op.py` (règles de lecture du point 5). Intervalles de lignes (bornes comprises) dans les copies `bench/<langage>_op` ; « cv: » : région du relevé du point 5, transposée.*

## python

* `k1|op_numpy|energy` (entrée `dot`) : k1_np ms.py:897-897, ms.py:902-903 — L 3, T 116, U 0, X 0
* `k3|op_dask|` (entrée `delayed`) : k3_dask ms.py:1061-1061, ms.py:1063-1067, ms.py:1072-1072 — L 7, T 82, U 0, X 0
* `k4|op_numpy|` (entrée `sum`) : k4_np ms.py:911-911 — L 1, T 37, U 0, X 0
* `k5|op_numpy|` (entrée `dot`) : k5_np ms.py:921-921 — L 1, T 10, U 0, X 0
* `k6|op_dask_mt|q1` (entrée `map_blocks`) : k6_dask ms.py:982-983, ms.py:993-993 ; q1_dask ms.py:988-992 ; q1_np ms.py:941-955 — L 21, T 407, U 0, X 0
* `k6|op_dask_mt|q6` (entrée `from_array`) : k6_dask ms.py:982-983, ms.py:993-993 ; q6_dask ms.py:985-986 — L 5, T 146, U 0, X 0
* `k6|op_numpy_mt|q1` (entrée `ThreadPool4`) : k6_np_mt ms.py:966-967, ms.py:969-970, ms.py:973-974, ms.py:976-976 ; pool4 ms.py:863-891 ; q1_np ms.py:941-955 — L 44, T 461, U 0, X 0
* `k6|op_numpy_mt|q6` (entrée `ThreadPool4`) : k6_np_mt ms.py:966-967, ms.py:969-970, ms.py:973-974, ms.py:976-976 ; pool4 ms.py:863-891 ; q6_np ms.py:934-938 — L 36, T 375, U 0, X 0
* `k6|op_numpy|q1` (entrée `q1_np`) : q1_np ms.py:941-955 — L 13, T 211, U 0, X 0
* `k6|op_numpy|q6` (entrée `q6_np`) : q6_np ms.py:934-938 — L 5, T 125, U 0, X 0
* `k9|op_dask_mt|` (entrée `map_overlap`) : k9_dask ms.py:1027-1030, ms.py:1042-1044 — L 7, T 143, U 0, X 0
* `k9|op_numpy_mt|` (entrée `ThreadPool4`) : k9_np_mt ms.py:1021-1023, ms.py:1040-1040, ms.py:1052-1053 ; pool4 ms.py:863-891 ; k9_np_rows ms.py:1006-1013 — L 37, T 444, U 0, X 0
* `k9|op_numpy|` (entrée `k9_np_rows`) : k9_np_rows ms.py:1006-1013 ; k9_np ms.py:1020-1020 — L 8, T 143, U 0, X 0

## rust

* `k3|op_cache_padded|` (entrée `cache_padded`) : op_cache_padded ms.rs:1083-1083, ms.rs:1087-1088 ; op_k3_threads ms.rs:1071-1079 — L 12, T 108, U 0, X 0
* `k3|op_crossbeam|` (entrée `crossbeam`) : op_crossbeam ms.rs:1091-1092 ; op_k3_threads ms.rs:1071-1079 — L 11, T 103, U 0, X 0
* `k3|op_libc|` (entrée `sysconf`) : op_libc ms.rs:1095-1101 ; op_k3_threads ms.rs:1071-1079 — L 15, T 195, U 1, X 0
* `k8|op_bumpalo|` (entrée `bb_build`) : op_bumpalo ms.rs:1110-1163, ms.rs:1171-1171, ms.rs:1179-1179 — L 56, T 440, U 11, X 0

## mojo

* `k3|op_max|` (entrée `sync_parallelize`) : op_k3 ms.mojo:949-949, ms.mojo:954-958 — L 6, T 88, U 1, X 0
* `k6|op_max|q1` (entrée `sync_parallelize`) : op_k6 ms.mojo:972-972, ms.mojo:975-977, ms.mojo:984-985 ; op_k6_q1 ms.mojo:978-981 ; cv:fold ms.mojo:454-458 ; cv:q1_tuned_v ms.mojo:417-452 ; cv:simd_i ms.mojo:344-344, ms.mojo:346-348 ; cv:q1_natural ms.mojo:363-374 — L 67, T 921, U 6, X 0
* `k6|op_max|q6` (entrée `sync_parallelize`) : op_k6 ms.mojo:972-972, ms.mojo:975-977, ms.mojo:984-985 ; op_k6_q6 ms.mojo:982-983 ; cv:q6_tuned ms.mojo:350-361 ; cv:simd_i ms.mojo:344-344, ms.mojo:346-348 ; cv:q6_natural ms.mojo:336-342 — L 31, T 491, U 6, X 0
* `k9|op_max|` (entrée `sync_parallelize`) : op_k9 ms.mojo:1001-1003 ; cv:k9_rows ms.mojo:755-770, ms.mojo:829-830 — L 21, T 353, U 6, X 0

## d

* `k1|op_soa|energy` (entrée `SOA`) : op_soa ms.d:152-155 ; k1_soau ms.d:89-107 ; vec_aliases ms.d:26-27 — L 25, T 334, U 3, X 0

## ada

* `k3|op_cachelines|` (entrée `Worker`) : op_k3 ms.adb:375-396, ms.adb:405-411 — L 28, T 171, U 28, X 0

## swift

* `k8|op_arena|` (entrée `opBuild`) : op_arena ms.swift:864-918, ms.swift:922-922, ms.swift:927-932, ms.swift:940-940, ms.swift:951-953 — L 66, T 543, U 17, X 0

## julia

* `k8|op_bumper|` (entrée `ob_build_it`) : op_bumper ms.jl:1023-1051, ms.jl:1057-1060, ms.jl:1066-1067, ms.jl:1070-1070 ; anode ms.jl:903-905 — L 39, T 382, U 22, X 0

## go

* `k3|op_cpu|` (entrée `opPadded`) : op_k3 ms.go:1105-1108, ms.go:1115-1119, ms.go:1121-1122, ms.go:1124-1132 — L 20, T 106, U 0, X 0
* `k9|op_gonum_mt|` (entrée `k9Gonum`) : k9_gonum ms.go:1145-1151, ms.go:1160-1160 ; k9_gonum_mt ms.go:1173-1181 — L 17, T 227, U 0, X 0
* `k9|op_gonum|` (entrée `k9Gonum`) : k9_gonum ms.go:1145-1151, ms.go:1160-1160 — L 8, T 156, U 0, X 0

## ocaml

* `k4|op_intrinsics|` (entrée `k4_op`) : k4_op ms.ml:769-775 ; ci ms.ml:764-764 — L 8, T 72, U 1, X 0
* `k6|op_intrinsics_mt|q6` (entrée `pool_run`) : k6_pool_op ms.ml:803-803, ms.ml:806-811, ms.ml:813-813 ; cv:pool ms.ml:263-263, ms.ml:265-265, ms.ml:267-277, ms.ml:279-279, ms.ml:281-281, ms.ml:283-306 ; q6_op ms.ml:788-795 ; ci ms.ml:764-764 — L 54, T 543, U 2, X 0
* `k6|op_intrinsics|q6` (entrée `q6_op`) : q6_op ms.ml:788-795 ; ci ms.ml:764-764 — L 9, T 135, U 2, X 0

## js

* `k8|op_pool|` (entrée `opBuildIt`) : op_pool ms.js:355-355, ms.js:405-422, ms.js:426-426, ms.js:429-429, ms.js:434-436 — L 24, T 446, U 0, X 0

## php

* `k6|op_amphp|q1` (entrée `parallelMap`) : k6_amphp ms.php:1173-1178, ms.php:1185-1185, ms.php:1187-1187 ; op_pool ms.php:1160-1168 ; q1_worker op_worker.php:44-61, op_worker.php:71-74 — L 37, T 449, U 0, X 0
* `k6|op_amphp|q6` (entrée `parallelMap`) : k6_amphp ms.php:1173-1178, ms.php:1185-1185, ms.php:1187-1187 ; op_pool ms.php:1160-1168 ; q6_worker op_worker.php:33-42, op_worker.php:65-69 — L 30, T 372, U 0, X 0
* `k9|op_amphp|` (entrée `parallelMap`) : k9_amphp ms.php:1199-1200, ms.php:1208-1208, ms.php:1212-1219, ms.php:1230-1230 ; op_pool ms.php:1160-1168 ; k9_worker op_worker.php:78-94 — L 36, T 460, U 0, X 0

## lua

* `k5|op_vmsl|` (entrée `CreateVector`) : k5_vmsl ms.lua:659-659, ms.lua:662-662 — L 2, T 41, U 0, X 0
* `k6|op_llthreads2|q1` (entrée `llthreads`) : k6_threads ms.lua:779-785, ms.lua:790-791 ; k6_join_q1 ms.lua:793-800 ; q1_thread ms.lua:756-773 ; dec ms.lua:703-727 ; pack ms.lua:729-736 ; bytes_range ms.lua:737-741 — L 73, T 1018, U 0, X 0
* `k6|op_llthreads2|q6` (entrée `llthreads`) : k6_threads ms.lua:779-785, ms.lua:790-791 ; k6_join_q6 ms.lua:802-802 ; q6_thread ms.lua:743-754 ; dec ms.lua:703-727 ; pack ms.lua:729-736 ; bytes_range ms.lua:737-741 — L 60, T 797, U 0, X 0
* `k9|op_llthreads2|` (entrée `llthreads`) : k9_threads ms.lua:832-832, ms.lua:836-836, ms.lua:839-848 ; k9_thread ms.lua:812-830 ; dec ms.lua:703-727 ; pack ms.lua:729-736 — L 64, T 756, U 0, X 0
* `k9|op_vmsl|` (entrée `submatrix`) : k9_vmsl ms.lua:671-683, ms.lua:685-685 — L 14, T 190, U 0, X 0

