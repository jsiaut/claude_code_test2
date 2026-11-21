#!/usr/bin/env python3
"""v4, point 4 (docs/V4_CONVERGE.md, 4.1, écart 1) : validation des sources publiées corrigées. Chaque langage corrigé
est reconstruit depuis les sources suivies (tools/equal/build.py, construction « pub »), puis chaque cellule du score
(campagne du point 3 : tools/equal/campaign.py, cells) et les trois variantes de K9 sont exécutées une fois, à la taille
publiée ; la somme de contrôle doit être celle de la taille publiée (tools/driver.py). Sortie :
results/converge/validation_base.txt. Usage : validate_base.py [langage,...]"""
import os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "equal"))
import build as B  # noqa: E402
import campaign as C  # noqa: E402

LANGS = ["ada", "fortran", "d", "rust", "java", "go", "haskell", "ocaml", "js", "python", "lua", "bqn",
         "cpp", "zig", "odin", "c3", "nim", "csharp", "julia", "mojo"]
OUT = os.path.join(ROOT, "results", "converge", "validation_base.txt")


def main():
    langs = sys.argv[1].split(",") if len(sys.argv) > 1 else LANGS
    lines = [f"# Validation des sources publiées corrigées (tools/converge/validate_base.py), "
             f"{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())}, {C.cpu_model()}",
             "# langage noyau variante paramètre : temps (s), somme de contrôle, verdict"]
    bad = 0
    for lang in langs:
        t0 = time.time()
        B.ensure(lang, "pub")
        print(f"construit {lang} en {time.time() - t0:.0f} s", flush=True)
        for k in C.KERNELS:
            cells = list(C.cells(lang, "pub", k))
            if k == "k9":
                cells += [(v, "") for v in ("natural", "tuned", "mt") if (v, "") not in cells]
            for v, q in cells:
                rec = C.run_one(lang, "pub", k, v, q, 1, 3 if lang in C.JIT else 1, 3600)
                ok = rec.get("oks") == ["True"] and rec["returncode"] == 0
                bad += not ok
                t = f"{rec['median']:.4g}" if "median" in rec else "-"
                line = (f"{lang} {k} {v} {q or '-'} : {t} {','.join(rec.get('chks', [])) or '-'} "
                        f"{'juste' if ok else 'FAUX (code ' + str(rec['returncode']) + ') ' + rec['stderr'][-200:]}")
                lines.append(line)
                print(line, flush=True)
    body = [l for l in lines if not l.startswith("#")]
    lines.append(f"# {len(body)} cellules, {len(body) - bad} justes, {bad} fausses")
    open(OUT, "w").write("\n".join(lines) + "\n")
    return bad


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
