#!/usr/bin/env python3
"""Taille du code et échappatoires de chaque implémentation du banc OLAP (docs/V7.md, 10).

Usage : count.py [implémentation...]

Pour chaque répertoire de olap/ qui a un build.sh, sur ses fichiers suivis par git (hors CHECKLIST.md, build.sh et
fichiers de projet) :
  * lignes de code : lignes non vides une fois les commentaires retirés ; à part, celles des fichiers du niveau
    spécialisé et celles des fichiers engendrés (première ligne « Code engendré par ») ;
  * octets compressés : le même texte, espaces de début et de fin de ligne retirés, compressé par zlib (niveau 9) ;
    hors fichiers engendrés ;
  * échappatoires : occurrences, dans le code écrit à la main, des constructions par lesquelles l'implémentation sort
    de ce que le langage vérifie ou gère (code non vérifié, mémoire hors tas, appels du système ou natifs, assembleur),
    et des primitives vectorielles explicites.
La mesure est grossière : elle compare des ordres de grandeur, pas des lignes."""
import os, re, subprocess, sys, zlib

OLAP = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = re.compile(r"(CHECKLIST\.md|build\.sh|go\.mod|\.csproj)$")
SPECIAL = re.compile(r"(olap_special\.h(pp)?|special\.(rs|go)|Special\.(java|cs)|olap_s\.zig)$")
# commentaires : tous les langages portés jusqu'ici écrivent « // » jusqu'à la fin de la ligne, et « /* ... */ » pour C, C++,
# Rust, Go, Java et C#
LINE_COMMENT = re.compile(r"//.*")
BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.S)
ESCAPES = {
    "c": [],  # le langage entier est sans vérification : rien à compter
    "cpp": [("reinterpret_cast", r"\breinterpret_cast\b")],
    "rust": [("unsafe", r"\bunsafe\b"), ("accès sans borne", r"get_unchecked"), ("fonctions du système", r'extern "C"')],
    "go": [("unsafe", r"\bunsafe\.\w+"), ("mémoire hors tas, système", r"\bsyscall\.\w+\(")],
    "java": [("accès par adresse", r"\b(getLong|getInt|getByte|putLong|putInt)\(|\bMEM\b"),
             ("fonctions natives", r"downcallHandle|\.reinterpret\(")],
    "csharp": [("unsafe", r"\bunsafe\b"), ("stackalloc, fixed", r"\bstackalloc\b|\bfixed\b"),
               ("mémoire native, système", r"NativeMemory\.|DllImport")],
    "zig": [("conversions de pointeurs", r"@ptrCast|@ptrFromInt|@intFromPtr|@alignCast"), ("appels du système", r"\blinux\.\w+\("),
            ("assembleur", r"\basm\b")],
}
SIMD = {
    "c": r"_mm\d*_\w+", "cpp": r"_mm\d*_\w+", "rust": r"_mm\d*_\w+", "go": r"\barchsimd\.\w+",
    "java": r"\b(IntVector|LongVector|ByteVector|VectorMask|VectorShuffle)\b", "csharp": r"\b(Avx512\w*|Avx2|Sse)\.\w+|\bVector(256|512)\b",
    "zig": r"@Vector|@shuffle|@select|@reduce|@prefetch",
}


def code_of(text):
    text = BLOCK_COMMENT.sub("", text)
    lines = [LINE_COMMENT.sub("", line).strip() for line in text.split("\n")]
    return [line for line in lines if line]


def count(impl):
    d = os.path.join(OLAP, impl)
    files = subprocess.run(["git", "-C", d, "ls-files"], capture_output=True, text=True, check=True).stdout.split()
    r = {"impl": impl, "common": 0, "special": 0, "generated": 0, "hand": [], "escapes": {}, "simd": 0}
    for f in sorted(files):
        if SKIP.search(f):
            continue
        text = open(os.path.join(d, f), encoding="utf-8").read()
        lines = code_of(text)
        if "Code engendré par" in text[:200]:
            r["generated"] += len(lines)
            continue
        r["special" if SPECIAL.search(f) else "common"] += len(lines)
        r["hand"] += lines
    hand = "\n".join(r["hand"])
    r["zlib"] = len(zlib.compress(hand.encode(), 9))
    for name, pattern in ESCAPES.get(impl, []):
        r["escapes"][name] = len(re.findall(pattern, hand))
    r["simd"] = len(re.findall(SIMD[impl], hand)) if impl in SIMD else 0
    return r


def main():
    impls = sys.argv[1:] or sorted(d for d in os.listdir(OLAP) if os.path.exists(os.path.join(OLAP, d, "build.sh")))
    print("| Implémentation | Lignes de code, écrites à la main | dont niveau spécialisé (fichiers à part) | Lignes engendrées | "
          "Octets compressés | Échappatoires (occurrences) | Primitives vectorielles explicites |")
    print("|---|---:|---:|---:|---:|---|---:|")
    for impl in impls:
        r = count(impl)
        esc = " ; ".join(f"{k} : {v}" for k, v in r["escapes"].items()) or "sans objet : le langage ne vérifie rien"
        print(f"| {impl} | {r['common'] + r['special']} | {r['special']} | {r['generated']} | {r['zlib']} | {esc} | {r['simd']} |")


if __name__ == "__main__":
    main()
