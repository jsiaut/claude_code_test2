#!/usr/bin/env python3
"""Ajoute la variante K1 `footprint_raw` (écart consigné dans docs/METHODOLOGY.md) : charger le tampon
brut exactement comme le chemin naturel, puis s'arrêter. À appliquer APRÈS la campagne, car les
langages interprétés lisent leur source à chaque exécution."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = '"k1", v, "energy", 0, 0, "0"'
EDITS = [
    # (fichier, ligne d'ancrage exacte, texte inséré APRÈS l'ancre)
    ("c3/ms.c3", '\tfloat[] raw = load(float, "k1_particles.f32");\n',
     '\tif (v == "footprint_raw") { result(' + R + '); return; }\n'),
    ("d/ms.d", '    auto raw = load!float("k1_particles.f32");\n',
     '    if (v == "footprint_raw") { result(' + R + '); return; }\n'),
    ("go/ms.go", '\traw := loadAs[float32]("k1_particles.f32")\n',
     '\tif v == "footprint_raw" {\n\t\tresult(' + R + ')\n\t\treturn\n\t}\n'),
    ("js/ms.js", "  const raw = load('k1_particles.f32', Float32Array);\n",
     "  if (v === 'footprint_raw') { result('k1', v, 'energy', 0, 0, '0'); return; }\n"),
    ("julia/ms.jl", '    raw = load(Float32, "k1_particles.f32")\n',
     '    v == "footprint_raw" && return result(' + R + ')\n'),
    ("mojo/ms.mojo", '    var raw = load[DType.float32]("k1_particles.f32")\n',
     '    if v == "footprint_raw":\n        result(' + R + ')\n        return\n'),
    ("nim/ms.nim", '  let raw = load[float32]("k1_particles.f32")\n',
     '  if v == "footprint_raw":\n    result(' + R + '); return\n'),
    ("odin/ms.odin", '\traw := load(f32, "k1_particles.f32")\n',
     '\tif v == "footprint_raw" {result(' + R + '); return}\n'),
    ("python/ms.py", '    raw = load("k1_particles.f32", "f")\n',
     '    if v == "footprint_raw":\n        result(' + R + ')\n        return\n'),
    ("rust/ms.rs", '    let raw = load_f32("k1_particles.f32");\n',
     '    if v == "footprint_raw" {\n        result("k1", v, "energy", 0, 0.0, "0");\n        return;\n    }\n'),
    ("zig/ms.zig", '    const raw = load(f32, "k1_particles.f32");\n',
     '    if (std.mem.eql(u8, v, "footprint_raw")) return result(' + R + ');\n'),
    ("java/Ms.java", '        float[] raw = loadF32("k1_particles.f32");\n',
     '        if (v.equals("footprint_raw")) { result(' + R + '); return; }\n'),
    ("csharp/Program.cs", '        float[] raw = Load<float>("k1_particles.f32");\n',
     '        if (v == "footprint_raw") { Result(' + R + '); return; }\n'),
    ("lua/ms.lua", '  local raw = load("k1_particles.f32", "<f", 4)\n',
     '  if v == "footprint_raw" then return result(' + R + ') end\n'),
    ("luajit/ms.lua", '  local raw = cload("k1_particles.f32", "float")\n',
     '  if v == "footprint_raw" then return result(' + R + ') end\n'),
    ("haskell/Ms.hs", '      raw <- loadBuf "k1_particles.f32" :: IO (Buf Float)\n      case v of\n',
     '        "footprint_raw" -> result "k1" v "energy" 0 0 "0"\n'),
    # OCaml : le tampon est projeté (mmap) ; on touche chaque page comme le ferait le chemin naturel
    ("ocaml/ms.ml", '    match v with\n',
     '    | "footprint_raw" -> (let s = ref 0. in for i = 0 to Bigarray.Array1.dim raw - 1 do s := !s +. raw.{i} done;\n'
     '                          result "k1" v "energy" 0 0. (if !s = 0. then "0" else "0"))\n'),
    ("cpp/ms.cpp", '    auto raw = load<Particle>("k1_particles.f32");\n',
     '    if (v == "footprint_raw") return result(' + R + ');\n'),
    ("chapel/ms.chpl", '  const raw = loadArr("k1_particles.f32", real(32));\n',
     '  if v == "footprint_raw" { result("k1", v, "energy", 0, 0.0, "0"); return; }\n'),
]
# collection naturelle chargée directement depuis le fichier : footprint_raw = footprint0
SAME_AS_FP0 = [
    ("c/ms.c", 'if (!strcmp(variant, "footprint0"))', 'if (!strcmp(variant, "footprint0") || !strcmp(variant, "footprint_raw"))'),
    ("fortran/ms.f90", 'if (v == "footprint0") then', 'if (v == "footprint0" .or. v == "footprint_raw") then'),
    ("ada/ms.adb", 'if V = "footprint0" then', 'if V = "footprint0" or else V = "footprint_raw" then'),
]

for f, anchor, text in EDITS:
    p = os.path.join(ROOT, "bench", f)
    s = open(p).read()
    if "footprint_raw" in s:
        continue
    assert s.count(anchor) == 1, (f, s.count(anchor))
    s = s.replace(anchor, anchor + text)
    open(p, "w").write(s)
    print("ok", f)
for f, old, new in SAME_AS_FP0:
    p = os.path.join(ROOT, "bench", f)
    s = open(p).read()
    if "footprint_raw" in s:
        continue
    assert s.count(old) == 1, (f, s.count(old))
    open(p, "w").write(s.replace(old, new))
    print("ok", f)
