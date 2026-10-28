#!/usr/bin/env python3
"""Empreinte K1 (D2a), méthode en deux points (écart consigné dans docs/METHODOLOGY.md, journal).

La mesure par pic RSS était invalide : le chargement du fichier crée dans la plupart des
implémentations un tampon transitoire de 256 Mio, et le pic qu'il produit masque la collection
construite ensuite (8 langages mesuraient 0 octet par particule). La variante `footprint` lit donc
la mémoire M dans le processus, en deux points :
  P1 : tampon brut chargé, collection pas encore construite (C, Fortran et Ada lisent le fichier
       directement dans la collection : P1 est alors avant la lecture) ;
  P2 : collection construite, tampon brut toujours vivant (il est relu après P2).
M = octets vivants comptés par le runtime après un GC complet pour les langages à ramasse-miettes
traçant (Java, C#, Go, JavaScript, Julia, Haskell, OCaml, D, Lua) ; RSS courant (/proc/self/statm)
pour les autres. Le RSS courant est relevé partout, comme contrôle. Lignes émises :
  META;mem;<live|rss>;<M(P1)>;<M(P2)>   et   META;rss;<RSS(P1)>;<RSS(P2)>
Corrections appliquées ensuite à la main (le script n'est plus rejouable, ses ancres ont disparu) :
  * Zig, Nim, D : /proc/self/statm annonce une taille nulle ; la lecture « fichier entier » de leur
    bibliothèque rendait une chaîne vide (RSS = 0). Lecture en flux ou ligne à ligne à la place.
  * Nim : son allocateur garde le tampon transitoire libéré et le réutilise pour la collection, donc
    le RSS ne bouge pas entre P1 et P2. M = getOccupiedMem() (octets occupés selon l'allocateur).
"""
import os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
B = os.path.join(ROOT, "bench")
E = []  # (fichier, ancien, nouveau)

# ---------------------------------------------------------------- C (clang et gcc, même source)
E += [("c/ms.c", "static void run_k1(const char *variant, int reps) {\n",
       "// Empreinte K1 (D2a) : RSS courant en octets (/proc/self/statm, 2e champ ; pages de 4 Kio)\n"
       "static long rss_now(void) {\n"
       "    long size = 0, res = 0;\n"
       "    FILE *f = fopen(\"/proc/self/statm\", \"r\");\n"
       "    if (f) {\n"
       "        if (fscanf(f, \"%ld %ld\", &size, &res) != 2) res = 0;\n"
       "        fclose(f);\n"
       "    }\n"
       "    return res * 4096;\n"
       "}\n\n"
       "static void run_k1(const char *variant, int reps) {\n"),
      ("c/ms.c", "    Particle *src = load(\"k1_particles.f32\", &bytes);\n    char chk[64], par[] = \"energy\";\n",
       "    long m1 = !strcmp(variant, \"footprint\") ? rss_now() : 0; // P1 : avant la lecture (la collection naturelle est le tableau lu)\n"
       "    Particle *src = load(\"k1_particles.f32\", &bytes);\n    char chk[64], par[] = \"energy\";\n"),
      ("c/ms.c", "        // la collection naturelle en C est déjà ce tableau de structs\n",
       "        // la collection naturelle en C est déjà ce tableau de structs ; P2 : après la lecture\n"
       "        long m2 = rss_now();\n"
       "        printf(\"META;mem;rss;%ld;%ld\\nMETA;rss;%ld;%ld\\n\", m1, m2, m1, m2);\n")]

# ---------------------------------------------------------------- C++
E += [("cpp/ms.cpp", "static void run_k1(std::string_view v, int reps) {\n",
       "// Empreinte K1 (D2a) : RSS courant en octets (/proc/self/statm, 2e champ ; pages de 4 Kio)\n"
       "static long rss_now() {\n"
       "    long size = 0, res = 0;\n"
       "    if (std::FILE *f = std::fopen(\"/proc/self/statm\", \"r\")) {\n"
       "        if (std::fscanf(f, \"%ld %ld\", &size, &res) != 2) res = 0;\n"
       "        std::fclose(f);\n"
       "    }\n"
       "    return res * 4096;\n"
       "}\n\n"
       "static void run_k1(std::string_view v, int reps) {\n"),
      ("cpp/ms.cpp", "    if (v == \"footprint_raw\") return result(\"k1\", v, \"energy\", 0, 0, \"0\");\n",
       "    if (v == \"footprint_raw\") return result(\"k1\", v, \"energy\", 0, 0, \"0\");\n"
       "    const long m1 = v == \"footprint\" ? rss_now() : 0; // P1 : tampon brut chargé\n"),
      ("cpp/ms.cpp", "    std::vector<Particle> ps(raw.begin(), raw.end());\n    raw = {};\n"
                     "    if (v == \"footprint\") return result(\"k1\", v, \"energy\", 0, 0, fmt(\"%.6f\", k1_natural(ps)));\n",
       "    std::vector<Particle> ps(raw.begin(), raw.end());\n"
       "    if (v == \"footprint\") { // P2 : collection construite, tampon brut encore vivant\n"
       "        const long m2 = rss_now();\n"
       "        std::printf(\"META;mem;rss;%ld;%ld\\nMETA;rss;%ld;%ld\\nMETA;raw0;%g\\n\", m1, m2, m1, m2, (double)raw[0].x);\n"
       "        return result(\"k1\", v, \"energy\", 0, 0, fmt(\"%.6f\", k1_natural(ps)));\n"
       "    }\n"
       "    raw = {};\n")]

# ---------------------------------------------------------------- Rust
E += [("rust/ms.rs", "fn run_k1(v: &str, reps: i32) {\n",
       "/// Empreinte K1 (D2a) : RSS courant en octets (/proc/self/statm, 2e champ ; pages de 4 Kio)\n"
       "fn rss_now() -> i64 {\n"
       "    std::fs::read_to_string(\"/proc/self/statm\")\n"
       "        .ok()\n"
       "        .and_then(|s| s.split_whitespace().nth(1).and_then(|x| x.parse::<i64>().ok()))\n"
       "        .unwrap_or(0)\n"
       "        * 4096\n"
       "}\n\n"
       "fn run_k1(v: &str, reps: i32) {\n"),
      ("rust/ms.rs", "    let mut ps: Vec<Particle> = raw.chunks_exact(16).map(Particle::from).collect();\n"
                     "    if v == \"footprint\" {\n        drop(raw);\n",
       "    let m1 = if v == \"footprint\" { rss_now() } else { 0 }; // P1 : tampon brut chargé\n"
       "    let mut ps: Vec<Particle> = raw.chunks_exact(16).map(Particle::from).collect();\n"
       "    if v == \"footprint\" {\n"
       "        let m2 = rss_now(); // P2 : collection construite, tampon brut encore vivant\n"
       "        println!(\"META;mem;rss;{m1};{m2}\\nMETA;rss;{m1};{m2}\\nMETA;raw0;{}\", raw[0]);\n"
       "        drop(raw);\n")]

# ---------------------------------------------------------------- Zig
E += [("zig/ms.zig", "fn runK1(v: []const u8, reps: i32) void {\n",
       "/// Empreinte K1 (D2a) : RSS courant en octets (/proc/self/statm, 2e champ ; pages de 4 Kio)\n"
       "fn rssNow() i64 {\n"
       "    const s = Io.Dir.cwd().readFileAlloc(io, \"/proc/self/statm\", gpa, .unlimited) catch return 0;\n"
       "    defer gpa.free(s);\n"
       "    var it = std.mem.tokenizeScalar(u8, s, ' ');\n"
       "    _ = it.next();\n"
       "    const res = std.fmt.parseInt(i64, it.next() orelse return 0, 10) catch return 0;\n"
       "    return res * 4096;\n"
       "}\n"
       "fn runK1(v: []const u8, reps: i32) void {\n"),
      ("zig/ms.zig", "    var ps: std.ArrayList(Particle) = .empty;\n    ps.ensureTotalCapacity(gpa, N1) catch @panic(\"oom\");\n"
                     "    for (0..N1) |i| ps.appendAssumeCapacity(Particle.from(raw[16 * i ..][0..16]));\n"
                     "    gpa.free(std.mem.sliceAsBytes(raw));\n"
                     "    if (std.mem.eql(u8, v, \"footprint\")) return result(\"k1\", v, \"energy\", 0, 0, fmt(\"{d:.6}\", .{k1Natural(ps.items)}));\n",
       "    const fp = std.mem.eql(u8, v, \"footprint\");\n"
       "    const m1: i64 = if (fp) rssNow() else 0; // P1 : tampon brut chargé\n"
       "    var ps: std.ArrayList(Particle) = .empty;\n    ps.ensureTotalCapacity(gpa, N1) catch @panic(\"oom\");\n"
       "    for (0..N1) |i| ps.appendAssumeCapacity(Particle.from(raw[16 * i ..][0..16]));\n"
       "    if (fp) { // P2 : collection construite, tampon brut encore vivant\n"
       "        const m2 = rssNow();\n"
       "        out.print(\"META;mem;rss;{d};{d}\\nMETA;rss;{d};{d}\\nMETA;raw0;{d}\\n\", .{ m1, m2, m1, m2, raw[0] }) catch {};\n"
       "        gpa.free(std.mem.sliceAsBytes(raw));\n"
       "        return result(\"k1\", v, \"energy\", 0, 0, fmt(\"{d:.6}\", .{k1Natural(ps.items)}));\n"
       "    }\n"
       "    gpa.free(std.mem.sliceAsBytes(raw));\n")]

# ---------------------------------------------------------------- Odin
E += [("odin/ms.odin", "run_k1 :: proc(v: string, reps: int) {\n",
       "// Empreinte K1 (D2a) : RSS courant en octets (/proc/self/statm, 2e champ ; pages de 4 Kio)\n"
       "rss_now :: proc() -> int {\n"
       "\tdata, err := os.read_entire_file(\"/proc/self/statm\", context.temp_allocator)\n"
       "\tif err != nil {return 0}\n"
       "\ts := string(data)\n"
       "\ti := 0\n"
       "\tfor i < len(s) && s[i] != ' ' do i += 1\n"
       "\tj := i + 1\n"
       "\tfor j < len(s) && s[j] != ' ' do j += 1\n"
       "\tif j > len(s) {return 0}\n"
       "\tres, _ := strconv.parse_int(s[i + 1:j])\n"
       "\treturn res * 4096\n"
       "}\n"
       "run_k1 :: proc(v: string, reps: int) {\n"),
      ("odin/ms.odin", "\tps := make([dynamic]Particle, 0, N1)\n\tfor i in 0 ..< N1 do append(&ps, (cast(^Particle)&raw[16 * i])^)\n"
                       "\tdelete(slice.reinterpret([]byte, raw))\n",
       "\tm1 := v == \"footprint\" ? rss_now() : 0 // P1 : tampon brut chargé\n"
       "\tps := make([dynamic]Particle, 0, N1)\n\tfor i in 0 ..< N1 do append(&ps, (cast(^Particle)&raw[16 * i])^)\n"
       "\tif v == \"footprint\" { // P2 : collection construite, tampon brut encore vivant\n"
       "\t\tm2 := rss_now()\n"
       "\t\tfmt.printf(\"META;mem;rss;%d;%d\\nMETA;rss;%d;%d\\nMETA;raw0;%v\\n\", m1, m2, m1, m2, raw[0])\n"
       "\t}\n"
       "\tdelete(slice.reinterpret([]byte, raw))\n")]

# ---------------------------------------------------------------- C3
E += [("c3/ms.c3", "import std::atomic, std::math, std::os::env, std::sort, std::core::mem;\n",
       "import std::atomic, std::math, std::os::env, std::sort, std::core::mem;\nimport libc;\n"),
      ("c3/ms.c3", "fn void run_k1(String v, int reps)\n",
       "// Empreinte K1 (D2a) : RSS courant en octets (/proc/self/statm, 2e champ ; pages de 4 Kio)\n"
       "fn long rss_now()\n"
       "{\n"
       "\tCFile f = libc::fopen(\"/proc/self/statm\", \"r\");\n"
       "\tif (!f) return 0;\n"
       "\tlong size, res;\n"
       "\tif (libc::fscanf(f, \"%ld %ld\", &size, &res) != 2) res = 0;\n"
       "\tlibc::fclose(f);\n"
       "\treturn res * 4096;\n"
       "}\n"
       "fn void run_k1(String v, int reps)\n"),
      ("c3/ms.c3", "\tParticle[] ps = mem::new_array(Particle, N1);\n\tfor (usz i = 0; i < N1; i++) ps[i] = *(Particle*)&raw[16 * i];\n"
                   "\tif (v == \"footprint\") { free(raw.ptr); result(",
       "\tlong m1 = v == \"footprint\" ? rss_now() : 0; // P1 : tampon brut chargé\n"
       "\tParticle[] ps = mem::new_array(Particle, N1);\n\tfor (usz i = 0; i < N1; i++) ps[i] = *(Particle*)&raw[16 * i];\n"
       "\tif (v == \"footprint\")\n"
       "\t{\n"
       "\t\tlong m2 = rss_now(); // P2 : collection construite, tampon brut encore vivant\n"
       "\t\tio::printfn(\"META;mem;rss;%d;%d\", m1, m2);\n"
       "\t\tio::printfn(\"META;rss;%d;%d\", m1, m2);\n"
       "\t\tio::printfn(\"META;raw0;%s\", raw[0]);\n"
       "\t}\n"
       "\tif (v == \"footprint\") { free(raw.ptr); result(")]

# ---------------------------------------------------------------- D
E += [("d/ms.d", "import std.stdio : writefln, writeln, stdout;\n",
       "import std.stdio : writefln, writeln, stdout;\nimport std.file : readText;\nimport std.array : split;\n"),
      ("d/ms.d", "void runK1(string v, int reps) {\n",
       "// Empreinte K1 (D2a) : octets vivants du tas du GC après une collecte complète, et RSS courant\n"
       "long liveNow() {\n"
       "    GC.collect();\n"
       "    return cast(long) GC.stats().usedSize;\n"
       "}\n"
       "long rssNow() {\n"
       "    try return readText(\"/proc/self/statm\").split()[1].to!long * 4096;\n"
       "    catch (Exception) return 0;\n"
       "}\n\n"
       "void runK1(string v, int reps) {\n"),
      ("d/ms.d", "    auto ps = new Particle[N1]; // tableau dynamique géré par le GC (valeurs contiguës)\n"
                 "    foreach (i; 0 .. N1) ps[i] = *cast(Particle*)&raw[16 * i];\n"
                 "    if (v == \"footprint\") { free(raw.ptr);",
       "    long m1, r1;\n"
       "    if (v == \"footprint\") { m1 = liveNow(); r1 = rssNow(); } // P1 : tampon brut chargé\n"
       "    auto ps = new Particle[N1]; // tableau dynamique géré par le GC (valeurs contiguës)\n"
       "    foreach (i; 0 .. N1) ps[i] = *cast(Particle*)&raw[16 * i];\n"
       "    if (v == \"footprint\") { // P2 : collection construite, tampon brut encore vivant\n"
       "        const m2 = liveNow(), r2 = rssNow();\n"
       "        writefln(\"META;mem;live;%d;%d\\nMETA;rss;%d;%d\\nMETA;raw0;%s\", m1, m2, r1, r2, raw[0]);\n"
       "    }\n"
       "    if (v == \"footprint\") { free(raw.ptr);")]

# ---------------------------------------------------------------- Nim (ORC, allocateur de Nim : RSS, et getOccupiedMem en contrôle)
E += [("nim/ms.nim", "proc runK1(v: string, reps: int) =\n",
       "proc rssNow(): int =\n"
       "  ## Empreinte K1 (D2a) : RSS courant en octets (/proc/self/statm, 2e champ ; pages de 4 Kio)\n"
       "  try: readFile(\"/proc/self/statm\").splitWhitespace()[1].parseInt * 4096\n"
       "  except CatchableError: 0\n\n"
       "proc runK1(v: string, reps: int) =\n"),
      ("nim/ms.nim", "  var ps = newSeq[Particle](N1)\n  for i in 0 ..< N1: copyMem(ps[i].addr, raw.p[16 * i].addr, sizeof(Particle))\n"
                     "  if v == \"footprint\":\n    cfree(raw.p);",
       "  let m1 = if v == \"footprint\": rssNow() else: 0  # P1 : tampon brut chargé\n"
       "  let o1 = getOccupiedMem()\n"
       "  var ps = newSeq[Particle](N1)\n  for i in 0 ..< N1: copyMem(ps[i].addr, raw.p[16 * i].addr, sizeof(Particle))\n"
       "  if v == \"footprint\":\n"
       "    let m2 = rssNow()  # P2 : collection construite, tampon brut encore vivant\n"
       "    echo &\"META;mem;rss;{m1};{m2}\\nMETA;rss;{m1};{m2}\\nMETA;nim_occupied;{o1};{getOccupiedMem()}\\nMETA;raw0;{raw.p[0]}\"\n"
       "    cfree(raw.p);")]

# ---------------------------------------------------------------- Mojo
E += [("mojo/ms.mojo", "def run_k1(v: String, reps: Int, warmup: Int) raises:\n",
       "def rss_now() raises -> Int:\n"
       "    \"\"\"Empreinte K1 (D2a) : RSS courant en octets (/proc/self/statm, 2e champ ; pages de 4 Kio).\"\"\"\n"
       "    with open(\"/proc/self/statm\", \"r\") as f:\n"
       "        var parts = f.read().split(\" \")\n"
       "        return atol(parts[1]) * 4096\n\n\n"
       "def run_k1(v: String, reps: Int, warmup: Int) raises:\n"),
      ("mojo/ms.mojo", "    var ps = List[Particle](capacity=N1)\n",
       "    var m1 = rss_now() if v == \"footprint\" else 0  # P1 : tampon brut chargé\n"
       "    var ps = List[Particle](capacity=N1)\n"),
      ("mojo/ms.mojo", "    if v == \"footprint\":\n        raw.p.free()\n",
       "    if v == \"footprint\":\n"
       "        var m2 = rss_now()  # P2 : collection construite, tampon brut encore vivant\n"
       "        print(\"META;mem;rss;\" + String(m1) + \";\" + String(m2))\n"
       "        print(\"META;rss;\" + String(m1) + \";\" + String(m2))\n"
       "        print(\"META;raw0;\" + String(raw.p[0]))\n"
       "        raw.p.free()\n")]

# ---------------------------------------------------------------- Chapel
E += [("chapel/ms.chpl", "proc runK1(v: string, reps: int) {\n",
       "// Empreinte K1 (D2a) : RSS courant en octets (/proc/self/statm, 2e champ ; pages de 4 Kio)\n"
       "proc rssNow(): int {\n"
       "  try {\n"
       "    var r = openReader(\"/proc/self/statm\");\n"
       "    var size, res: int;\n"
       "    r.read(size, res);\n"
       "    r.close();\n"
       "    return res * 4096;\n"
       "  } catch { return 0; }\n"
       "}\n"
       "proc runK1(v: string, reps: int) {\n"),
      ("chapel/ms.chpl", "  if v == \"footprint_raw\" { result(\"k1\", v, \"energy\", 0, 0.0, \"0\"); return; }\n",
       "  if v == \"footprint_raw\" { result(\"k1\", v, \"energy\", 0, 0.0, \"0\"); return; }\n"
       "  const m1 = if v == \"footprint\" then rssNow() else 0;  // P1 : tampon brut chargé\n"),
      ("chapel/ms.chpl", "  if v == \"footprint\" { result(\"k1\", v, \"energy\", 0, 0.0, \"%.6dr\".format(k1Natural(ps))); return; }\n",
       "  if v == \"footprint\" {\n"
       "    const m2 = rssNow();  // P2 : collection construite, tampon brut encore vivant\n"
       "    writeln(\"META;mem;rss;\", m1, \";\", m2);\n"
       "    writeln(\"META;rss;\", m1, \";\", m2);\n"
       "    writeln(\"META;raw0;\", raw[0]);\n"
       "    result(\"k1\", v, \"energy\", 0, 0.0, \"%.6dr\".format(k1Natural(ps))); return;\n"
       "  }\n")]

# ---------------------------------------------------------------- Go
E += [("go/ms.go", "\t\"strconv\"\n", "\t\"strconv\"\n\t\"strings\"\n"),
      ("go/ms.go", "func runK1(v string, reps int) {\n",
       "// Empreinte K1 (D2a) : octets vivants du tas après un GC complet, et RSS courant (pages de 4 Kio)\n"
       "func liveNow() uint64 {\n"
       "\truntime.GC()\n"
       "\tvar m runtime.MemStats\n"
       "\truntime.ReadMemStats(&m)\n"
       "\treturn m.HeapAlloc\n"
       "}\n\n"
       "func rssNow() uint64 {\n"
       "\tb, err := os.ReadFile(\"/proc/self/statm\")\n"
       "\tif err != nil {\n"
       "\t\treturn 0\n"
       "\t}\n"
       "\tf := strings.Fields(string(b))\n"
       "\tif len(f) < 2 {\n"
       "\t\treturn 0\n"
       "\t}\n"
       "\tn, _ := strconv.ParseUint(f[1], 10, 64)\n"
       "\treturn n * 4096\n"
       "}\n\n"
       "func runK1(v string, reps int) {\n"),
      ("go/ms.go", "\tps := make([]Particle, N1)\n\tfor i := range ps {\n",
       "\tvar m1, r1 uint64\n"
       "\tif v == \"footprint\" { // P1 : tampon brut chargé\n"
       "\t\tm1, r1 = liveNow(), rssNow()\n"
       "\t}\n"
       "\tps := make([]Particle, N1)\n\tfor i := range ps {\n"),
      ("go/ms.go", "\tcase \"footprint\":\n\t\traw = nil\n",
       "\tcase \"footprint\":\n"
       "\t\tm2, r2 := liveNow(), rssNow() // P2 : collection construite, tampon brut encore vivant\n"
       "\t\tfmt.Printf(\"META;mem;live;%d;%d\\nMETA;rss;%d;%d\\nMETA;raw0;%v\\n\", m1, m2, r1, r2, raw[0])\n"
       "\t\traw = nil\n")]

# ---------------------------------------------------------------- Java
E += [("java/Ms.java", "    static void runK1(String v, int reps) {\n",
       "    // Empreinte K1 (D2a) : octets vivants du tas après GC complet, et RSS courant (pages de 4 Kio)\n"
       "    static long liveNow() {\n"
       "        Runtime rt = Runtime.getRuntime();\n"
       "        System.gc();\n"
       "        System.gc();\n"
       "        return rt.totalMemory() - rt.freeMemory();\n"
       "    }\n"
       "    static long rssNow() {\n"
       "        try {\n"
       "            return Long.parseLong(java.nio.file.Files.readString(java.nio.file.Path.of(\"/proc/self/statm\")).trim().split(\"\\\\s+\")[1]) * 4096;\n"
       "        } catch (Exception e) {\n"
       "            return 0;\n"
       "        }\n"
       "    }\n"
       "    static void runK1(String v, int reps) {\n"),
      ("java/Ms.java", "        List<Particle> ps = new ArrayList<>();\n        for (int i = 0; i < N1; i++) {\n",
       "        long m1 = 0, r1 = 0;\n"
       "        if (v.equals(\"footprint\")) { m1 = liveNow(); r1 = rssNow(); } // P1 : tampon brut chargé\n"
       "        List<Particle> ps = new ArrayList<>();\n        for (int i = 0; i < N1; i++) {\n"),
      ("java/Ms.java", "            System.gc();\n            Runtime rt = Runtime.getRuntime();\n"
                       "            System.out.println(\"META;live_bytes_after_gc;\" + (rt.totalMemory() - rt.freeMemory()));\n",
       "            long m2 = liveNow(), r2 = rssNow(); // P2 : collection construite, tampon brut encore vivant\n"
       "            System.out.println(\"META;mem;live;\" + m1 + \";\" + m2);\n"
       "            System.out.println(\"META;rss;\" + r1 + \";\" + r2);\n"
       "            System.out.println(\"META;raw0;\" + raw[0]);\n")]

# ---------------------------------------------------------------- C#
E += [("csharp/Program.cs", "    static void RunK1(string v, int reps)\n",
       "    // Empreinte K1 (D2a) : octets vivants du tas après GC complet, et RSS courant (pages de 4 Kio)\n"
       "    static long LiveNow()\n"
       "    {\n"
       "        GC.Collect(); GC.WaitForPendingFinalizers(); GC.Collect();\n"
       "        return GC.GetTotalMemory(true);\n"
       "    }\n"
       "    static long RssNow()\n"
       "    {\n"
       "        try { return long.Parse(System.IO.File.ReadAllText(\"/proc/self/statm\").Split(' ')[1]) * 4096; }\n"
       "        catch { return 0; }\n"
       "    }\n"
       "    static void RunK1(string v, int reps)\n"),
      ("csharp/Program.cs", "        var list = new List<Particle>();\n",
       "        long m1 = 0, r1 = 0;\n"
       "        if (v == \"footprint\") { m1 = LiveNow(); r1 = RssNow(); } // P1 : tampon brut chargé\n"
       "        var list = new List<Particle>();\n"),
      ("csharp/Program.cs", "        raw = null!;\n        if (v == \"footprint\")\n        {\n"
                            "            GC.Collect(); GC.WaitForPendingFinalizers(); GC.Collect();\n"
                            "            Console.WriteLine($\"META;live_bytes_after_gc;{GC.GetTotalMemory(true)}\");\n",
       "        if (v == \"footprint\")\n        {\n"
       "            long m2 = LiveNow(), r2 = RssNow(); // P2 : collection construite, tampon brut encore vivant\n"
       "            Console.WriteLine($\"META;mem;live;{m1};{m2}\");\n"
       "            Console.WriteLine($\"META;rss;{r1};{r2}\");\n"
       "            Console.WriteLine($\"META;raw0;{raw[0].ToString(Inv)}\");\n"),
      ("csharp/Program.cs", "            Result(\"k1\", v, \"energy\", 0, 0, K1Natural(list).ToString(\"F6\", Inv));\n            return;\n        }\n"
                            "        if (v == \"natural_shuffled\")\n",
       "            Result(\"k1\", v, \"energy\", 0, 0, K1Natural(list).ToString(\"F6\", Inv));\n            return;\n        }\n"
       "        raw = null!;\n"
       "        if (v == \"natural_shuffled\")\n")]

# ---------------------------------------------------------------- JavaScript (Node et Bun, même source)
E += [("js/ms.js", "function runK1(v, reps) {\n",
       "// Empreinte K1 (D2a) : octets vivants (tas JS + mémoire externe) après GC complet, et RSS courant\n"
       "function liveNow() {\n"
       "  if (typeof Bun !== 'undefined') Bun.gc(true); else if (global.gc) global.gc();\n"
       "  const m = process.memoryUsage();\n"
       "  return m.heapUsed + m.external;\n"
       "}\n"
       "function rssNow() { return process.memoryUsage().rss; }\n"
       "function runK1(v, reps) {\n"),
      ("js/ms.js", "  let ps = [];\n  for (let i = 0; i < N1; i++) {\n",
       "  const [m1, r1] = v === 'footprint' ? [liveNow(), rssNow()] : [0, 0]; // P1 : tampon brut chargé\n"
       "  let ps = [];\n  for (let i = 0; i < N1; i++) {\n"),
      ("js/ms.js", "    if (global.gc) global.gc();\n    console.log(`META;live_bytes_after_gc;${process.memoryUsage().heapUsed}`);\n",
       "    const m2 = liveNow(), r2 = rssNow(); // P2 : collection construite, tampon brut encore vivant\n"
       "    console.log(`META;mem;live;${m1};${m2}\\nMETA;rss;${r1};${r2}\\nMETA;raw0;${raw[0]}`);\n")]

# ---------------------------------------------------------------- Julia
E += [("julia/ms.jl", "function run_k1(v, reps)\n",
       "# Empreinte K1 (D2a) : octets vivants du tas après GC complet, et RSS courant (pages de 4 Kio)\n"
       "live_now() = (GC.gc(true); Int(Base.gc_live_bytes()))\n"
       "rss_now() = parse(Int, split(read(\"/proc/self/statm\", String))[2]) * 4096\n"
       "function run_k1(v, reps)\n"),
      ("julia/ms.jl", "    ps = copy(reinterpret(Particle, raw))\n    if v == \"footprint\"\n        raw = nothing; GC.gc()\n",
       "    m1, r1 = v == \"footprint\" ? (live_now(), rss_now()) : (0, 0)  # P1 : tampon brut chargé\n"
       "    ps = copy(reinterpret(Particle, raw))\n    if v == \"footprint\"\n"
       "        m2, r2 = live_now(), rss_now()  # P2 : collection construite, tampon brut encore vivant\n"
       "        println(\"META;mem;live;$m1;$m2\\nMETA;rss;$r1;$r2\\nMETA;raw0;$(raw[1])\")\n")]

# ---------------------------------------------------------------- Haskell (RTS lancé avec -T pour cette variante : bench/haskell/run)
E += [("haskell/Ms.hs", "import System.Environment\n",
       "import System.Environment\nimport System.Mem (performMajorGC)\nimport GHC.Stats (getRTSStats, gc, gcdetails_live_bytes)\n"),
      ("haskell/Ms.hs", "runK1 :: String -> Int -> Int -> IO ()\n",
       "-- Empreinte K1 (D2a) : octets vivants du tas après un GC majeur (RTS lancé avec -T), et RSS courant\n"
       "liveNow :: IO Int\n"
       "liveNow = do\n"
       "  performMajorGC\n"
       "  s <- getRTSStats\n"
       "  return (fromIntegral (gcdetails_live_bytes (gc s)))\n\n"
       "rssNow :: IO Int\n"
       "rssNow = do\n"
       "  s <- readFile \"/proc/self/statm\"\n"
       "  let r = read (words s !! 1) :: Int\n"
       "  r `seq` return (r * 4096)\n\n"
       "runK1 :: String -> Int -> Int -> IO ()\n"),
      ("haskell/Ms.hs", "        _ -> do\n          ps0 <- withBuf raw $ \\p -> forM [0 .. n1 - 1] $ \\i -> do\n",
       "        _ -> do\n"
       "          (m1, r1) <- if v == \"footprint\" then (,) <$> liveNow <*> rssNow else return (0, 0)  -- P1 : tampon brut chargé\n"
       "          ps0 <- withBuf raw $ \\p -> forM [0 .. n1 - 1] $ \\i -> do\n"),
      ("haskell/Ms.hs", "          if v == \"footprint\"\n            then result \"k1\" v \"energy\" 0 0 (printf \"%.6f\" (k1Natural ps))\n",
       "          if v == \"footprint\"\n"
       "            then do\n"
       "              m2 <- liveNow  -- P2 : collection construite, tampon brut encore vivant\n"
       "              r2 <- rssNow\n"
       "              raw0 <- withBuf raw $ \\p -> peekElemOff p 0\n"
       "              putStrLn (\"META;mem;live;\" ++ show m1 ++ \";\" ++ show m2 ++ \"\\nMETA;rss;\" ++ show r1 ++ \";\" ++ show r2 ++ \"\\nMETA;raw0;\" ++ show raw0)\n"
       "              result \"k1\" v \"energy\" 0 0 (printf \"%.6f\" (k1Natural ps))\n")]

# ---------------------------------------------------------------- OCaml
E += [("ocaml/ms.ml", "let run_k1 v reps =\n",
       "(* Empreinte K1 (D2a) : octets vivants du tas après GC complet, et RSS courant (pages de 4 Kio) *)\n"
       "let live_now () = Gc.full_major (); (Gc.stat ()).Gc.live_words * (Sys.word_size / 8)\n"
       "let rss_now () =\n"
       "  try\n"
       "    let ic = open_in \"/proc/self/statm\" in\n"
       "    let l = input_line ic in\n"
       "    close_in ic;\n"
       "    int_of_string (List.nth (String.split_on_char ' ' l) 1) * 4096\n"
       "  with _ -> 0\n\n"
       "let run_k1 v reps =\n"),
      ("ocaml/ms.ml", "        let g i k = Array1.get raw ((16 * i) + k) in\n        let ps = Array.init n1 (fun i ->\n",
       "        let g i k = Array1.get raw ((16 * i) + k) in\n"
       "        let m1, r1 = if v = \"footprint\" then (live_now (), rss_now ()) else (0, 0) in (* P1 : tampon brut chargé *)\n"
       "        let ps = Array.init n1 (fun i ->\n"),
      ("ocaml/ms.ml", "        if v = \"footprint\" then (Gc.compact (); result \"k1\" v \"energy\" 0 0. (f6 (k1_natural ps)))\n",
       "        if v = \"footprint\" then begin\n"
       "          let m2 = live_now () in (* P2 : collection construite, tampon brut encore vivant *)\n"
       "          let r2 = rss_now () in\n"
       "          Printf.printf \"META;mem;live;%d;%d\\nMETA;rss;%d;%d\\nMETA;raw0;%g\\n%!\" m1 m2 r1 r2 (Array1.get raw 0);\n"
       "          result \"k1\" v \"energy\" 0 0. (f6 (k1_natural ps))\n"
       "        end\n")]

# ---------------------------------------------------------------- Lua 5.5
E += [("lua/ms.lua", "local function run_k1(v, reps)\n",
       "-- Empreinte K1 (D2a) : octets alloués par Lua après un GC complet, et RSS courant (pages de 4 Kio)\n"
       "local function live_now() collectgarbage(\"collect\"); collectgarbage(\"collect\"); return math.floor(collectgarbage(\"count\") * 1024) end\n"
       "local function rss_now()\n"
       "  local f = io.open(\"/proc/self/statm\", \"r\")\n"
       "  if not f then return 0 end\n"
       "  local _, res = f:read(\"n\", \"n\")\n"
       "  f:close()\n"
       "  return math.floor(res * 4096)\n"
       "end\n"
       "local function run_k1(v, reps)\n"),
      ("lua/ms.lua", "  local ps = {}\n  for i = 1, N1 do\n    local o = 16 * (i - 1)\n    ps[i] = { x = raw[o + 1],",
       "  local m1, r1 = 0, 0\n"
       "  if v == \"footprint\" then m1, r1 = live_now(), rss_now() end -- P1 : tampon brut chargé\n"
       "  local ps = {}\n  for i = 1, N1 do\n    local o = 16 * (i - 1)\n    ps[i] = { x = raw[o + 1],"),
      ("lua/ms.lua", "  raw = nil; collectgarbage()\n  if v == \"footprint\" then\n"
                     "    print(\"META;live_bytes_after_gc;\" .. math.floor(collectgarbage(\"count\") * 1024))\n"
                     "    return result(\"k1\", v, \"energy\", 0, 0, f6(k1_natural(ps)))\n  end\n",
       "  if v == \"footprint\" then\n"
       "    local m2, r2 = live_now(), rss_now() -- P2 : collection construite, tampon brut encore vivant\n"
       "    print(string.format(\"META;mem;live;%d;%d\\nMETA;rss;%d;%d\\nMETA;raw0;%s\", m1, m2, r1, r2, tostring(raw[1])))\n"
       "    return result(\"k1\", v, \"energy\", 0, 0, f6(k1_natural(ps)))\n  end\n"
       "  raw = nil; collectgarbage()\n")]

# ---------------------------------------------------------------- LuaJIT (annexe)
E += [("luajit/ms.lua", "local function run_k1(v, reps)\n",
       "-- Empreinte K1 (D2a) : octets alloués par LuaJIT après un GC complet, et RSS courant (pages de 4 Kio)\n"
       "local function live_now() collectgarbage(\"collect\"); collectgarbage(\"collect\"); return math.floor(collectgarbage(\"count\") * 1024) end\n"
       "local function rss_now()\n"
       "  local f = io.open(\"/proc/self/statm\", \"r\")\n"
       "  if not f then return 0 end\n"
       "  local _, res = f:read(\"*n\", \"*n\")\n"
       "  f:close()\n"
       "  return math.floor(res * 4096)\n"
       "end\n"
       "local function run_k1(v, reps)\n"),
      ("luajit/ms.lua", "  local ps = {}\n  for i = 1, N1 do\n    local o = 16 * (i - 1)\n    ps[i] = { x = raw[o],",
       "  local m1, r1 = 0, 0\n"
       "  if v == \"footprint\" then m1, r1 = live_now(), rss_now() end -- P1 : tampon brut chargé\n"
       "  local ps = {}\n  for i = 1, N1 do\n    local o = 16 * (i - 1)\n    ps[i] = { x = raw[o],"),
      ("luajit/ms.lua", "  raw = nil; collectgarbage()\n  if v == \"footprint\" then return result(\"k1\", v, \"energy\", 0, 0, f6(k1_natural(ps))) end\n",
       "  if v == \"footprint\" then\n"
       "    local m2, r2 = live_now(), rss_now() -- P2 : collection construite, tampon brut encore vivant\n"
       "    print(string.format(\"META;mem;live;%d;%d\\nMETA;rss;%d;%d\\nMETA;raw0;%s\", m1, m2, r1, r2, tostring(raw[0])))\n"
       "    return result(\"k1\", v, \"energy\", 0, 0, f6(k1_natural(ps)))\n"
       "  end\n"
       "  raw = nil; collectgarbage()\n")]

# ---------------------------------------------------------------- Python (comptage de références : RSS)
E += [("python/ms.py", "def run_k1(v, reps):\n",
       "def rss_now():\n"
       "    \"\"\"Empreinte K1 (D2a) : RSS courant en octets (/proc/self/statm, 2e champ ; pages de 4 Kio).\"\"\"\n"
       "    with open(\"/proc/self/statm\") as f:\n"
       "        return int(f.read().split()[1]) * 4096\n\n\n"
       "def run_k1(v, reps):\n"),
      ("python/ms.py", "    ps = [Particle(*raw[16 * i:16 * i + 16]) for i in range(N1)]\n    del raw\n"
                       "    if v == \"footprint\":\n        result(\"k1\", v, \"energy\", 0, 0, f\"{k1_natural(ps):.6f}\")\n        return\n",
       "    m1 = rss_now() if v == \"footprint\" else 0  # P1 : tampon brut chargé\n"
       "    ps = [Particle(*raw[16 * i:16 * i + 16]) for i in range(N1)]\n"
       "    if v == \"footprint\":\n"
       "        m2 = rss_now()  # P2 : collection construite, tampon brut encore vivant\n"
       "        print(f\"META;mem;rss;{m1};{m2}\\nMETA;rss;{m1};{m2}\\nMETA;raw0;{raw[0]}\", flush=True)\n"
       "        result(\"k1\", v, \"energy\", 0, 0, f\"{k1_natural(ps):.6f}\")\n"
       "        return\n"
       "    del raw\n")]

# ---------------------------------------------------------------- Ada
E += [("ada/ms.adb", "   procedure Run_K1 (V : String; Reps : Integer) is\n      Ps : Particle_Acc;\n",
       "   --  Empreinte K1 (D2a) : RSS courant en octets (/proc/self/statm, 2e champ ; pages de 4 Kio)\n"
       "   function Rss_Now return Long_Long_Integer is\n"
       "      F    : File_Type;\n"
       "      Line : String (1 .. 256);\n"
       "      Last : Natural;\n"
       "      P, Q : Natural;\n"
       "   begin\n"
       "      Open (F, In_File, \"/proc/self/statm\");\n"
       "      Get_Line (F, Line, Last);\n"
       "      Close (F);\n"
       "      P := Index (Line (1 .. Last), \" \");\n"
       "      Q := Index (Line (P + 1 .. Last), \" \");\n"
       "      return Long_Long_Integer'Value (Line (P + 1 .. Q - 1)) * 4096;\n"
       "   exception\n"
       "      when others => return 0;\n"
       "   end Rss_Now;\n\n"
       "   function Img (X : Long_Long_Integer) return String is (Trim (Long_Long_Integer'Image (X), Left));\n\n"
       "   procedure Run_K1 (V : String; Reps : Integer) is\n      Ps : Particle_Acc;\n      M1 : Long_Long_Integer := 0;\n"),
      ("ada/ms.adb", "      Ps := Load_P (\"k1_particles.f32\");\n      if V = \"soa\" then\n",
       "      if V = \"footprint\" then\n"
       "         M1 := Rss_Now;  --  P1 : avant la lecture (la collection naturelle est le tableau lu)\n"
       "      end if;\n"
       "      Ps := Load_P (\"k1_particles.f32\");\n      if V = \"soa\" then\n"),
      ("ada/ms.adb", "      if V = \"footprint\" then\n         Result (\"k1\", V, \"energy\", 0, 0.0, Fix (K1_Natural (Ps.all), 6));\n",
       "      if V = \"footprint\" then\n"
       "         declare\n"
       "            M2 : constant Long_Long_Integer := Rss_Now;  --  P2 : après la lecture\n"
       "         begin\n"
       "            Put_Line (\"META;mem;rss;\" & Img (M1) & \";\" & Img (M2));\n"
       "            Put_Line (\"META;rss;\" & Img (M1) & \";\" & Img (M2));\n"
       "         end;\n"
       "         Result (\"k1\", V, \"energy\", 0, 0.0, Fix (K1_Natural (Ps.all), 6));\n")]

# ---------------------------------------------------------------- Fortran (gfortran et flang, même source)
E += [("fortran/ms.f90", "  subroutine result(k, v, p, rep, sec, chk)\n",
       "  ! Empreinte K1 (D2a) : RSS courant en octets (/proc/self/statm, 2e champ ; pages de 4 Kio)\n"
       "  integer(int64) function rss_now()\n"
       "    integer(int64) :: sz, res\n"
       "    integer :: u, ios\n"
       "    rss_now = 0\n"
       "    open (newunit=u, file='/proc/self/statm', action='read', iostat=ios)\n"
       "    if (ios /= 0) return\n"
       "    read (u, *, iostat=ios) sz, res\n"
       "    close (u)\n"
       "    if (ios == 0) rss_now = res * 4096_int64\n"
       "  end function\n"
       "  subroutine result(k, v, p, rep, sec, chk)\n"),
      ("fortran/ms.f90", "    character(64) :: s\n    if (v == \"footprint0\" .or. v == \"footprint_raw\") then\n",
       "    character(64) :: s\n    integer(int64) :: m1, m2\n    if (v == \"footprint0\" .or. v == \"footprint_raw\") then\n"),
      ("fortran/ms.f90", "    allocate (ps(N1))\n    open (newunit=u, file=path(\"k1_particles.f32\")",
       "    m1 = 0\n"
       "    if (v == \"footprint\") m1 = rss_now()  ! P1 : avant la lecture (la collection naturelle est le tableau lu)\n"
       "    allocate (ps(N1))\n    open (newunit=u, file=path(\"k1_particles.f32\")"),
      ("fortran/ms.f90", "    if (v == \"footprint\") then\n      write (s, '(f0.6)') k1_natural(ps)\n",
       "    if (v == \"footprint\") then\n"
       "      m2 = rss_now()  ! P2 : après la lecture\n"
       "      write (output_unit, '(a)') 'META;mem;rss;' // itoa(m1) // ';' // itoa(m2)\n"
       "      write (output_unit, '(a)') 'META;rss;' // itoa(m1) // ';' // itoa(m2)\n"
       "      write (s, '(f0.6)') k1_natural(ps)\n")]


def main():
    dry = "--dry" in sys.argv
    texts = {}
    for f, old, new in E:
        p = os.path.join(B, f)
        t = texts.get(p) or open(p).read()
        n = t.count(old)
        if n != 1:
            sys.exit(f"{f}: ancre trouvée {n} fois :\n{old}")
        texts[p] = t.replace(old, new)
    if dry:
        print("ancres toutes uniques :", len(E), "modifications dans", len(texts), "fichiers")
        return
    for p, t in texts.items():
        open(p, "w").write(t)
    print("appliqué :", len(E), "modifications dans", len(texts), "fichiers")


if __name__ == "__main__":
    main()
