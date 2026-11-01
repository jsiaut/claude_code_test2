#!/bin/sh
# Remarque sur Nim (docs/NIM.md, section 2) : preuves des vérifications faites avant le plan. Écrit results/nim_check/*.txt.
# Prérequis : /opt/nim (Nim 2.2.12, chaîne du banc), /opt/nim240 (paquet officiel nim-2.4.0-linux_x64.tar.xz), clang-23.
set -e
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
T=$ROOT/tools/nim_check
OUT=$ROOT/results/nim_check
W=$ROOT/.work/nim/collect
mkdir -p "$OUT" "$W"
NIMF="-d:release --cc:clang --clang.exe:clang-23 --clang.linkerexe:clang-23 --threads:on --mm:orc --hints:off --warnings:off"

# 1. Chaînes et option d'aliasing imposée par Nim
{ /opt/nim/bin/nim --version | head -1; /opt/nim240/bin/nim --version | head -1
  echo "paquet nim-2.4.0-linux_x64.tar.xz, SHA-256 23c1c83d9031c498a2b3ad0bce153b8905710d04eb5922cf8ebd8f9d12125743 (fichier .sha256 officiel identique)"
  clang-23 --version | head -1; /opt/gcc-16/bin/gcc-16 --version | head -1
  echo; echo "== /opt/nim/config/nim.cfg (2.2.12)"; grep -n -B1 "fno-strict-aliasing" /opt/nim/config/nim.cfg | grep -v "^--$" | grep -v vxworks -i
  echo; echo "== /opt/nim240/config/nim.cfg (2.4.0)"; grep -n "seqs_v2 violates\|clang.options.always = " /opt/nim240/config/nim.cfg; } > "$OUT/versions.txt"

# 2. Q1 optimisé de la campagne : code C généré par Nim, compilé comme dans le banc pour Cascade Lake ; et copie nim_q1
rm -rf "$W/ncq"; /opt/nim/bin/nim c $NIMF --passC:"-march=cascadelake" --nimcache:"$W/ncq" --compileOnly "$ROOT/bench/nim/ms.nim" > /dev/null
clang-23 -S -w -ferror-limit=3 -fno-strict-aliasing -pthread -march=cascadelake -O3 -I/opt/nim/lib -I"$ROOT/bench/nim" -o "$W/q1.s" "$W/ncq/@mms.nim.c"
awk '/^q1Tuned__ms[^:]*:/,/\.Lfunc_end/' "$W/q1.s" > "$W/q1f.s"
{ echo "q1Tuned de la campagne (bench/nim/ms.nim), Nim 2.2.12 -> clang 23 -O3 -march=cascadelake -fno-strict-aliasing :"
  echo "$(grep -c -E '^\s+v\w+\s.*%[xyz]mm' "$W/q1f.s") instructions vectorielles (xmm $(grep -c xmm "$W/q1f.s"), ymm $(grep -c ymm "$W/q1f.s"), zmm $(grep -c zmm "$W/q1f.s"))"
  echo; echo "Boucle interne vectorisée (8 lignes par tour, additions masquées) :"
  awk '/This Inner Loop Header/{n++} n==1' "$W/q1f.s" | awk 'NR<=48'
  echo; echo "Copie nim_q1 (bench/nim_q1, binaire natif) : q1Tuned"
  objdump -d --no-show-raw-insn "$ROOT/bench/nim_q1/ms" | awk '/<q1Tuned.*>:/{p=1;next} p&&/^$/{exit} p' > "$W/q1fix.s"
  echo "zmm $(grep -c zmm "$W/q1fix.s") ; pext $(grep -c pext "$W/q1fix.s") ; vpcmp $(grep -c vpcmp "$W/q1fix.s")"; } > "$OUT/q1_asm.txt"

# 3. Convention de Q1 optimisé : forme et SIMD explicite dans les autres noyaux optimisés, par langage
python3 - "$ROOT" > "$OUT/q1_convention.txt" <<'PY'
import re, sys
sys.path.insert(0, sys.argv[1] + "/analysis")
import capabilities as cap, capabilities_v2 as v2
rows = [("c", "intrinsèques", "une passe (référence)"), ("cpp", "std::simd, intrinsèques", "une passe"), ("zig", "@Vector", "une passe"),
        ("odin", "#simd", "une passe"), ("c3", "vecteurs natifs", "une passe"), ("mojo", "SIMD", "une passe"),
        ("csharp", "Vector512", "une passe"), ("d", "core.simd", "une passe (corrigé le 31/10)"),
        ("rust", "std::arch (intrinsèques)", "une passe"), ("nim", "intrinsèques importées (K1 soa, K5 tuned)", "blocs"),
        ("ada", "vector_type GCC et builtins (K5 tuned)", "blocs"), ("chapel", "aucun (boucles)", "blocs"),
        ("julia", "aucun (@simd)", "blocs"), ("fortran", "aucun", "blocs")]
print("Langage | C1 (v1) | C2 (v1 / v2) | SIMD explicite des autres noyaux optimisés | Q1 tuned")
for l, simd, form in rows:
    m = cap.MATRIX[l]
    c2v2 = v2.V2_OVERRIDES.get((l, "C2"), m["C2"])[0]
    print(f"{l} | {m['C1'][0]} | {m['C2'][0]} / {c2v2} | {simd} | {form}")
print()
print("docs/DLANG.md (section 2, poussée avant les mesures de D) : « parmi les langages à types vectoriels portables standard")
print("(C1 = 1 en règle v1), C++, Zig, Odin, C3, Mojo et C# écrivent Q1 tuned avec l'algorithme de la référence C, en une")
print("passe de 16 lignes ; les blocs servent aux langages qui n'en ont pas (Nim, Fortran, Chapel, Julia ; Ada, dont les")
print("vecteurs sont propres à GNAT). »")
PY

# 4. Formes de K9 naturel : vérifications (-d:release / -d:danger) et aliasing (avec ou sans -fstrict-aliasing)
cd "$W"
{ echo "tools/nim_check/k9forms.nim : k9Seq = seq[seq[float]] (forme du banc) ; k9Arr = ref array[M, array[M, float]]."
  echo "Nim 2.2.12 -> clang 23 -O3 -march=cascadelake ; nombre d'instructions vectorielles sur des doubles (ymm/zmm)."
  for mode in release danger; do for sa in "" "-fstrict-aliasing"; do
    d=k9_${mode}${sa:+_sa}; rm -rf "$d"
    /opt/nim/bin/nim c -d:$mode --cc:clang --clang.exe:clang-23 --clang.linkerexe:clang-23 --passC:"-march=cascadelake $sa" --threads:on --mm:orc --hints:off --warnings:off --nimcache:./$d --compileOnly "$T/k9forms.nim" > /dev/null 2>&1
    clang-23 -S -w -fno-strict-aliasing $sa -pthread -march=cascadelake -O3 -I/opt/nim/lib -o $d.s $(ls $d/*k9forms.nim.c | head -1) 2>/dev/null
    for fn in k9Seq k9Arr; do awk "/^$fn:/,/\.Lfunc_end/" $d.s > f.s
      echo "-d:$mode ${sa:-(-fno-strict-aliasing seul, défaut de Nim)} $fn : $(grep -c -E '\sv\w+pd\s.*%[yz]mm' f.s) vectorielles, $(grep -c -E '\sv\w+sd\s' f.s) scalaires"
    done; done; done; } > "$OUT/k9_forms.txt"

# 5. {.localPassC.} : l'option ne vaut que pour le fichier C du module qui la déclare
rm -rf lp; mkdir lp; cp "$T/lp.nim" lp/; cd lp
/opt/nim/bin/nim c -d:release --cc:clang --clang.exe:clang-23 --clang.linkerexe:clang-23 --hints:off --nimcache:./nc lp.nim > /dev/null 2>&1
python3 -c "
import json; j = json.load(open('nc/lp.json'))
print('sonde tools/nim_check/lp.nim : {.localPassC: \"-ffast-math\".}')
for c in j['compile']: print(c[0].split('/')[-1], '->', 'avec -ffast-math' if '-ffast-math' in c[1] else 'sans')" > "$OUT/localpassc.txt"
cd "$W"

# 6. Nim 2.4.0 contre 2.2.12 : code machine des noyaux, fonction par fonction
for v in 2212:/opt/nim 240:/opt/nim240; do tag=${v%%:*}; dir=${v#*:}; rm -rf v$tag
  $dir/bin/nim c $NIMF --passC:"-march=cascadelake" --nimcache:./v$tag --compileOnly "$ROOT/bench/nim/ms.nim" > /dev/null 2>&1
  clang-23 -S -w -ferror-limit=3 -fno-strict-aliasing -pthread -march=cascadelake -O3 -I$dir/lib -I"$ROOT/bench/nim" -o v$tag.s v$tag/@mms.nim.c
done
python3 "$T/cmpfun.py" v2212.s v240.s > "$OUT/nim240.txt"
echo "écrit : $(ls "$OUT")"
