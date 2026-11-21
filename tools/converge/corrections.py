#!/usr/bin/env python3
"""v4, point 4 (docs/V4_CONVERGE.md, 4.1, écart 1) : corrections du classement publié reportées dans les sources
publiées. Pour chaque copie corrigée (copies `_fix` et `bqn_rq` des remarques, dont les rapports entrent dans le
classement publié par results/transfers.json ; copies `_k9h` du harnais commun de K9, docs/K9.md), la correction est la
différence entre la source publiée au commit qui a créé la copie et la copie telle qu'elle est ; elle est écrite dans
results/converge/patches/ et essayée à blanc sur la source actuelle (`patch --dry-run`).
Usage : corrections.py [essai|appliquer] [langage,...]"""
import os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PATCHES = os.path.join(ROOT, "results", "converge", "patches")
# langage -> source, copies corrigées dans l'ordre d'application (corrections d'implémentation, puis harnais de K9)
FIX = {
    # corrections d'implémentation sans le harnais de K9 (remarques antérieures au 1er novembre), puis le harnais
    "d": ("ms.d", ["d_fix", "d_k9h"]),
    "rust": ("ms.rs", ["rust_fix", "rust_k9h"]),
    "java": ("Ms.java", ["java_fix", "java_k9h"]),
    "ada": ("ms.adb", ["ada_fix"]),  # K9 d'Ada déjà au harnais commun (docs/K9.md, 2)
    # copies corrigées qui contiennent déjà le harnais commun de K9
    "fortran": ("ms.f90", ["fortran_fix_k9h"]),
    "go": ("ms.go", ["go_fix"]),
    "haskell": ("Ms.hs", ["haskell_fix"]),
    "ocaml": ("ms.ml", ["ocaml_fix"]),
    "js": ("ms.js", ["js_fix"]),
    "python": ("ms.py", ["python_fix"]),
    "lua": ("ms.lua", ["lua_fix"]),
    # harnais commun de K9 seul
    "cpp": ("ms.cpp", ["cpp_k9h"]),
    "zig": ("ms.zig", ["zig_k9h"]),
    "odin": ("ms.odin", ["odin_k9h"]),
    "c3": ("ms.c3", ["c3_k9h"]),
    "nim": ("ms.nim", ["nim_k9h"]),
    "csharp": ("Program.cs", ["csharp_k9h"]),
    "julia": ("ms.jl", ["julia_k9h"]),
    "mojo": ("ms.mojo", ["mojo_k9h"]),
    # BQN : seuls les errata de bqn_rq (K9 : somme hors chrono ; K7 naturel : l'idiome de la documentation), reportés à
    # la main ; les blocs de bqn_rq sont une forme restée en sensibilité (docs/BQN.md, 5.4)
}


def git(*a):
    return subprocess.run(["git", "-C", ROOT, *a], capture_output=True, text=True, check=True).stdout


def creation_commit(path):
    out = git("log", "--diff-filter=A", "--format=%h", "--", path).split()
    return out[-1] if out else None


def patch_for(lang, src, copy):
    """Différence (source publiée au commit de création de la copie) -> copie actuelle, en chemins de la source."""
    c = creation_commit(f"bench/{copy}/{src}")
    if not c:
        raise SystemExit(f"{copy} : pas de bench/{copy}/{src} dans l'historique")
    # la copie peut avoir été créée au même commit que des changements de la source : prendre le parent
    ref = git("show", f"{c}^:bench/{lang}/{src}")
    tmp = f"/dev/shm/corr_{lang}_{copy}_ref"
    open(tmp, "w").write(ref)
    d = subprocess.run(["diff", "-u", "--label", f"a/bench/{lang}/{src}", "--label", f"b/bench/{lang}/{src}", tmp,
                        os.path.join(ROOT, "bench", copy, src)], capture_output=True, text=True).stdout
    return c, d


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "essai"
    langs = sys.argv[2].split(",") if len(sys.argv) > 2 else list(FIX)
    os.makedirs(PATCHES, exist_ok=True)
    for lang in langs:
        src, copies = FIX[lang]
        for copy in copies:
            c, d = patch_for(lang, src, copy)
            p = os.path.join(PATCHES, f"{copy}.patch")
            open(p, "w").write(d)
            hunks = d.count("\n@@ ")
            args = ["patch", "-p1", "--no-backup-if-mismatch", "-r", "-", "-i", p] + (["--dry-run"] if mode == "essai" else [])
            r = subprocess.run(args, cwd=ROOT, capture_output=True, text=True)
            print(f"{lang} {copy} (créée en {c}) : {hunks} morceaux ; {'appliqué' if r.returncode == 0 else 'ÉCHEC'}"
                  + ("" if r.returncode == 0 else "\n" + r.stdout[-600:]), flush=True)


if __name__ == "__main__":
    main()
