#!/usr/bin/env python3
"""v4, point 2 : validation des sommes de contrôle d'un langage à chaque taille (une exécution par cellule, une
répétition) contre results/sizes/expected.json (calculées par le C).
Usage : validate.py <langage>[,<langage>...] [k1,k4,...] [small,pub,large,l2,l3]
Les données d'une taille sont produites une fois pour tous les langages demandés, puis effacées (/dev/shm) : une seule
validation à la fois."""
import json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sizes as S  # noqa: E402
import build as B  # noqa: E402
from expected import PLAN, TOL  # noqa: E402

EXP = json.load(open(os.path.join(S.ROOT, "results", "sizes", "expected.json")))


def runner(lang, kernel, size):
    name = S.set_of(kernel, size)
    if name is None:
        return os.path.join(S.ROOT, "bench", lang, "run")
    return os.path.join(B.ensure_build(lang, name), "run")


def env_for(lang, kernel, size):
    env = S.environ(kernel, size)
    for k in S.PUBLISHED:  # la taille est dans la construction (ou la copie), pas dans l'environnement
        env.pop(k, None)
    env["WARMUP"] = "0"
    return env


def checksum_ok(kernel, got, exp):
    """Tolérance de la spécification (TOL), égalité exacte sinon ; une somme de contrôle entière au-delà de 2^53 se
    compare à l'arrondi d'un double près (écart relatif d'au plus 1e-15) : un langage dont les nombres sont des doubles
    (BQN) ne la représente pas exactement."""
    try:
        if kernel in TOL:
            return abs(float(got) - float(exp)) <= TOL[kernel] * abs(float(exp))
        if got.strip() == exp:
            return True
        if ":" not in exp and abs(float(exp)) > 2.0 ** 53:
            return abs(float(got) - float(exp)) <= 1e-15 * abs(float(exp))
        return False
    except ValueError:
        return False


def extra_variants(lang):
    """Variantes propres à un langage (bench/<langage>/extra_variants, comme tools/driver.py)."""
    extra = {}
    ef = os.path.join(S.ROOT, "bench", lang, "extra_variants")
    if os.path.exists(ef):
        for line in open(ef):
            f = line.split()
            if len(f) >= 2:
                extra.setdefault(f[0], []).append((f[1], f[2] if len(f) > 2 else ""))
    return extra


def main():
    langs = sys.argv[1].split(",")
    kernels = sys.argv[2].split(",") if len(sys.argv) > 2 else list(PLAN)
    only = sys.argv[3].split(",") if len(sys.argv) > 3 else None
    bad = {lang: 0 for lang in langs}
    for k in kernels:
        for size in S.ORDER[k]:
            if only and size not in only:
                continue
            S.ensure_data(k, size)
            for lang in langs:
                for v, p in PLAN[k] + extra_variants(lang).get(k, []):
                    key = f"{k}:{size}" + (f":{p}" if k == "k6" else "")
                    err = ""
                    try:
                        out = subprocess.run([runner(lang, k, size), k, v, "1"] + ([p] if p else []), capture_output=True,
                                             text=True, env=env_for(lang, k, size), timeout=1800)
                        err = out.stderr[-200:]
                        got = [l for l in out.stdout.splitlines() if l.startswith("RESULT;")][-1].split(";")[6]
                    except Exception as e:  # noqa: BLE001
                        got = f"ERREUR {type(e).__name__} {err}"
                    e = EXP[key]
                    ok = checksum_ok(k, got, e)
                    bad[lang] += not ok
                    print(f"{lang} {key} {v} {got} {'OK' if ok else 'ATTENDU ' + e}", flush=True)
            if size not in ("pub",):
                S.drop_data(k, size)
    for lang in langs:
        print(f"{lang} : {bad[lang]} échec(s)")
    return sum(bad.values())


if __name__ == "__main__":
    sys.exit(1 if main() else 0)
