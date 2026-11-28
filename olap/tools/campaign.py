#!/usr/bin/env python3
"""Mesure du banc OLAP (docs/V7.md, 9 et 11) : étalonnage, puis passes ; un processus par cellule, ordre tiré au hasard.

Usage : campaign.py run <répertoire de la campagne> [--passes=3] [--impls=c,duckdb,clickhouse] [--threads=1,4]
                        [--queries=t1,...] [--machine=<numéro>]
        campaign.py summary <répertoire de la campagne>

Une cellule est une implémentation, un niveau, un nombre de fils et une requête. Les implémentations sont les
répertoires de olap/ qui ont un build.sh ; chacune est construite, depuis les fichiers suivis par git, avant de
mesurer. Les moteurs de référence (duckdb, clickhouse) sont des cellules comme les autres, sans niveau, mesurées par
engines.py ; leurs résultats sont vérifiés à part (engines.py expected).

Étalonnage : chaque cellule est exécutée une fois (après un échauffement) ; son résultat est vérifié et sa durée fixe
le nombre de répétitions (environ 3 s par processus, de 5 à 100) et l'échauffement (une exécution ; au moins trois et
au moins une seconde pour les implémentations à compilation en cours d'exécution et pour les moteurs). Un processus
sans exécution (zéro répétition : il charge les colonnes, crée ses fils et s'arrête) donne la mémoire de départ de
la cellule ; la mémoire de travail est la mémoire de pointe moins celle-là.
Passe : toutes les cellules, groupe par groupe ; un groupe est une requête à un nombre de fils ; l'ordre des groupes,
puis celui des cellules du groupe, sont tirés au hasard (graine : le numéro de la passe). Chaque cellule est un
processus : échauffement, répétitions ; son temps est la médiane des répétitions, son résultat doit être celui de
olap/expected à chaque exécution. Un processus dont le vol de temps de l'hyperviseur dépasse 5 % est refait une fois.
« run » complète la campagne jusqu'au nombre de passes demandé : relancé, il reprend où il s'était arrêté.

Sorties dans le répertoire de la campagne : raw.jsonl (une ligne par processus : temps, empreinte du résultat,
mémoire de pointe, machine), calib.json (étalonnage), builds.jsonl (empreinte des binaires), model.txt (modèle du
processeur : une campagne n'en a qu'un). Répertoire des données : variable OLAP_DATA (/opt/olap/data par défaut)."""
import hashlib, json, math, os, random, statistics, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
OLAP = os.path.dirname(HERE)
ROOT = os.path.dirname(OLAP)
DATA = os.environ.get("OLAP_DATA", "/opt/olap/data")
PY = os.environ.get("OLAP_PYTHON", "/opt/olap-venv/bin/python")
DIRS = {"t": "sf10", "c": "hits20"}
QUERIES = ["t1", "t6", "t9", "t18", "c4", "c12", "c16", "c20", "c33", "c36"]
ROWS = {"t": 59986052, "c": 20000000}  # lignes de la table de faits : le débit est en lignes par seconde
LEVELS = {"p": "portable", "s": "spécialisé"}
ENGINES = ("duckdb", "clickhouse")
JIT = ("java", "csharp", "julia")  # compilation en cours d'exécution : échauffement plus long
TARGET, STEAL_MAX = 3.0, 0.05


def fnv1a(b):
    h = 0xCBF29CE484222325
    for x in b:
        h = ((h ^ x) * 0x100000001B3) & 0xFFFFFFFFFFFFFFFF
    return f"{h:016x}"


def cpu_model():
    f = {}
    for line in open("/proc/cpuinfo"):
        k, _, v = line.partition(":")
        f.setdefault(k.strip(), v.strip())
        if k.strip() == "stepping":
            break
    return f"{f['cpu family']}/{f['model']}/{f['stepping']}"


def steal():
    f = open("/proc/stat").readline().split()  # cpu user nice system idle iowait irq softirq steal
    return int(f[8]), sum(int(x) for x in f[1:9])


def impl_dirs():
    return sorted(d for d in os.listdir(OLAP) if os.path.exists(os.path.join(OLAP, d, "build.sh")))


def launch(cmd):
    """Exécute un processus ; rend son code de retour, ses sorties et sa mémoire de pointe (ko), enfants compris."""
    with tempfile.TemporaryFile() as fo, tempfile.TemporaryFile() as fe:
        p = subprocess.Popen(cmd, stdout=fo, stderr=fe)
        _, status, ru = os.wait4(p.pid, 0)
        p.returncode = os.waitstatus_to_exitcode(status)
        fo.seek(0), fe.seek(0)
        return p.returncode, fo.read().decode(errors="replace"), fe.read().decode(errors="replace"), ru.ru_maxrss


def run_cell(impl, level, nt, q, warm, reps, want):
    """Le processus d'une cellule : temps des répétitions (échauffement écarté), validité du résultat, mémoire de pointe."""
    d = os.path.join(DATA, DIRS[q[0]])
    if impl in ENGINES:
        cmd = [PY, os.path.join(HERE, "engines.py"), "time", "tpch" if q[0] == "t" else "hits", d, str(nt), str(reps), q,
               f"--engine={impl}", f"--warmup={warm}"]
    else:
        cmd = [os.path.join(OLAP, impl, "olap_" + level), q, str(nt), str(warm + reps), d]
    s0 = steal()
    code, out, err, rss = launch(cmd)
    s1 = steal()
    rec = {"impl": impl, "level": level, "threads": nt, "query": q, "warmups": warm, "returncode": code, "maxrss_kb": rss,
           "steal": round((s1[0] - s0[0]) / max(1, s1[1] - s0[1]), 4), "times": [], "ok": False}
    if code != 0:
        rec["error"] = err[-500:]
    elif impl in ENGINES:
        r = json.loads(out.strip().splitlines()[-1])
        rec.update(times=r["times"], version=r["version"], ok=len(r["times"]) == reps)
    else:
        lines = [x.split(";") for x in out.splitlines() if x.startswith("RESULT;")]
        sums = sorted({x[6] for x in lines})
        rec.update(times=[float(x[5]) for x in lines[warm:]], sums=sums,
                   ok=len(lines) == warm + reps and sums == [want] and all(x[2] == level for x in lines))
    rec["median"] = statistics.median(rec["times"]) if rec["times"] else None
    return rec


def build(out, impls):
    """Construit chaque implémentation depuis les fichiers suivis ; rend ses niveaux."""
    levels = {}
    commit = subprocess.run(["git", "-C", ROOT, "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    for name in impls:
        if name in ENGINES:
            levels[name] = ["-"]
            continue
        d = os.path.join(OLAP, name)
        dirty = subprocess.run(["git", "-C", ROOT, "status", "--porcelain", "--", d], capture_output=True, text=True).stdout
        if dirty.strip():
            raise SystemExit(f"olap/{name} : fichiers modifiés ou non suivis ; une campagne part des fichiers suivis par git")
        subprocess.run(["sh", "build.sh"], cwd=d, check=True)
        levels[name] = [lv for lv in LEVELS if os.path.exists(os.path.join(d, "olap_" + lv))]
        rec = {"impl": name, "commit": commit, "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "sha256": {lv: hashlib.sha256(open(os.path.join(d, "olap_" + lv), "rb").read()).hexdigest() for lv in levels[name]}}
        with open(os.path.join(out, "builds.jsonl"), "a") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return levels


def opt(name, default):
    for a in sys.argv[3:]:
        if a.startswith(f"--{name}="):
            return a.split("=", 1)[1]
    return default


def run(out):
    os.makedirs(out, exist_ok=True)
    model, mp = cpu_model(), os.path.join(out, "model.txt")
    if os.path.exists(mp) and open(mp).read().strip() != model:
        raise SystemExit(f"processeur {model} : la campagne de {out} se mesure sur {open(mp).read().strip()}")
    open(mp, "w").write(model + "\n")
    passes = int(opt("passes", "3"))
    impls = opt("impls", ",".join(impl_dirs() + list(ENGINES))).split(",")
    threads = [int(x) for x in opt("threads", "1,4").split(",")]
    queries = opt("queries", ",".join(QUERIES)).split(",")
    stamp = {"machine": opt("machine", "?"), "boot_id": open("/proc/sys/kernel/random/boot_id").read().strip(), "cpu": model}
    levels = build(out, impls)
    want = {q: fnv1a(open(os.path.join(OLAP, "expected", "full", q + ".txt"), "rb").read()) for q in queries}
    cells = [(i, lv, nt, q) for q in queries for nt in threads for i in impls for lv in levels[i]]

    # étalonnage : validation et nombre de répétitions
    cp = os.path.join(out, "calib.json")
    calib = json.load(open(cp)) if os.path.exists(cp) else {}
    for i, lv, nt, q in cells:
        key = f"{i}/{lv}/{nt}/{q}"
        if key in calib:
            continue
        rec = run_cell(i, lv, nt, q, 1, 1, want[q])
        if not rec["ok"]:
            raise SystemExit(f"étalonnage : {key} en échec : {rec.get('error', rec.get('sums'))}")
        t = rec["median"]
        slow_start = i in ENGINES or i in JIT
        calib[key] = {"seconds": t, "reps": min(100, max(5, round(TARGET / t))),
                      "warmups": max(3, math.ceil(1.0 / t)) if slow_start else 1}
        if i not in ENGINES:
            code, _, err, calib[key]["base_rss_kb"] = launch([os.path.join(OLAP, i, "olap_" + lv), q, str(nt), "0",
                                                              os.path.join(DATA, DIRS[q[0]])])
            if code != 0:
                raise SystemExit(f"étalonnage : {key} sans exécution : {err[-300:]}")
        json.dump(calib, open(cp, "w"), indent=0, sort_keys=True)
        print(f"étalonnage {key} : {1e3 * t:.1f} ms, {calib[key]['reps']} répétitions, {calib[key]['warmups']} échauffement(s)", flush=True)

    raw = os.path.join(out, "raw.jsonl")
    done = {(r["pass"], r["impl"], r["level"], r["threads"], r["query"]) for r in map(json.loads, open(raw))
            if r["ok"]} if os.path.exists(raw) else set()
    for ps in range(passes):
        rng = random.Random(7000 + ps)
        groups = [(q, nt) for q in queries for nt in threads]
        rng.shuffle(groups)
        t_pass = time.time()
        for gi, (q, nt) in enumerate(groups):
            group = [(i, lv) for i in impls for lv in levels[i]]
            rng.shuffle(group)
            for i, lv in group:
                if (ps, i, lv, nt, q) in done:
                    continue
                c = calib[f"{i}/{lv}/{nt}/{q}"]
                for attempt in (0, 1):
                    rec = run_cell(i, lv, nt, q, c["warmups"], c["reps"], want[q])
                    rec.update(stamp, **{"pass": ps, "group": gi, "attempt": attempt, "base_rss_kb": c.get("base_rss_kb"),
                                         "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
                    if attempt == 0 and rec["ok"] and rec["steal"] > STEAL_MAX:
                        rec["ok"], rec["error"] = False, "vol de temps"
                    with open(raw, "a") as f:
                        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    if rec["ok"]:
                        break
                    print(f"passe {ps} {i}/{lv}/{nt}/{q} : {rec.get('error', rec.get('sums'))}", flush=True)
                    if rec.get("error") != "vol de temps":
                        break
            print(f"{time.strftime('%H:%M:%S', time.gmtime())} passe {ps}, groupe {gi + 1}/{len(groups)} : {q} à {nt} fil(s)", flush=True)
        print(f"passe {ps} : {time.time() - t_pass:.0f} s", flush=True)


def load(out):
    """Cellule -> liste, par passe, du temps médian de son processus valide ; mémoire (pointe, départ) ; échecs."""
    cells, rss, bad, stamps = {}, {}, 0, set()
    for r in map(json.loads, open(os.path.join(out, "raw.jsonl"))):
        if not r["ok"]:
            bad += r.get("error") != "vol de temps"
            continue
        k = (r["impl"], r["level"], r["threads"], r["query"])
        cells.setdefault(k, []).append(r["median"])
        rss[k] = (max(rss.get(k, (0, 0))[0], r["maxrss_kb"]), r.get("base_rss_kb") or 0)
        stamps.add((r["machine"], r["cpu"], r["boot_id"]))
    return cells, rss, bad, stamps


def ranking(cells, hand, threads):
    """Débit par implémentation : moyenne géométrique, sur les requêtes, des lignes par seconde ; ordre : niveau
    portable, tous cœurs (docs/V7.md, 10). Entre parenthèses : la même grandeur calculée sur chaque passe seule."""
    def rate(impl, level, nt, pick):
        v = [ROWS[q[0]] / pick(cells[(impl, level, nt, q)]) for q in QUERIES if (impl, level, nt, q) in cells]
        return statistics.geometric_mean(v) / 1e6 if len(v) == len(QUERIES) else None

    def cell(impl, level, nt):
        r = rate(impl, level, nt, statistics.median)
        if r is None:
            return "—"
        n = min(len(cells[(impl, level, nt, q)]) for q in QUERIES)
        per_pass = [rate(impl, level, nt, lambda v, k=k: v[k]) for k in range(n)]
        return f"{r:.0f} ({min(per_pass):.0f} à {max(per_pass):.0f})" if n > 1 else f"{r:.0f}"

    top = max(threads)
    impls = sorted({c[0] for c in hand}, key=lambda i: -(rate(i, "p", top, statistics.median) or 0))
    best = rate(impls[0], "p", top, statistics.median)
    print(f"\nDébit en millions de lignes par seconde (moyenne géométrique des dix requêtes) ; ordre : portable, {top} fils\n")
    print("| Rang | Implémentation | " + " | ".join(f"{LEVELS[lv]}, {nt} fil(s)" for nt in sorted(threads, reverse=True) for lv in LEVELS)
          + f" | portable, {top} fils, rapporté au premier |")
    print("|---:|---|" + "---:|" * (2 * len(threads) + 1))
    for k, i in enumerate(impls):
        r = rate(i, "p", top, statistics.median)
        print(f"| {k + 1} | {i} | " + " | ".join(cell(i, lv, nt) for nt in sorted(threads, reverse=True) for lv in LEVELS)
              + f" | {r / best:.2f} |")


def summary(out):
    cells, rss, bad, stamps = load(out)
    med = {k: statistics.median(v) for k, v in cells.items()}
    cols = sorted({k[:2] for k in med}, key=lambda c: (c[0] in ENGINES, c))
    hand = [c for c in cols if c[0] not in ENGINES]
    engines = [c for c in cols if c[0] in ENGINES]
    threads = sorted({k[2] for k in med})
    name = lambda c: c[0] if c[1] == "-" else f"{c[0]}, {LEVELS[c[1]]}"  # noqa: E731
    worst = 0.0
    for nt in threads:
        print(f"\n{nt} fil(s) : temps en ms (médiane, sur les passes, du temps médian de chaque processus)\n")
        print("| Requête | " + " | ".join(name(c) for c in cols) + " | meilleur écrit à la main / meilleur moteur |")
        print("|---|" + "---:|" * (len(cols) + 1))
        rate = {c: [] for c in cols}
        for q in QUERIES:
            row = {c: med.get((*c, nt, q)) for c in cols}
            if None in row.values():
                continue
            for c in cols:
                rate[c].append(ROWS[q[0]] / row[c])
            ratio = min(row[c] for c in hand) / min(row[c] for c in engines) if hand and engines else float("nan")
            worst = max(worst, ratio)
            print(f"| {q.upper()} | " + " | ".join(f"{1e3 * row[c]:.1f}" for c in cols) + f" | {ratio:.2f} |")
        print("| débit, moyenne géométrique (millions de lignes par seconde) | "
              + " | ".join(f"{statistics.geometric_mean(rate[c]) / 1e6:.0f}" if rate[c] else "" for c in cols) + " | |")
    if hand and engines:
        print(f"\nCritère (docs/V7.md, 11) : le pire rapport est {worst:.2f} ; "
              + ("satisfait" if worst <= 2 else "NON SATISFAIT") + " (au plus 2).")
    if len({c[0] for c in hand}) > 1:
        ranking(cells, hand, threads)
    if hand:
        print("\nMémoire de travail en Mio : mémoire de pointe du processus moins sa mémoire de départ (colonnes chargées, "
              "fils créés), donnée entre parenthèses\n")
        print("| Requête | " + " | ".join(f"{name(c)}, {nt} fil(s)" for c in hand for nt in threads) + " |")
        print("|---|" + "---:|" * (len(hand) * len(threads)))
        for q in QUERIES:
            row = [rss.get((*c, nt, q)) for c in hand for nt in threads]
            if None not in row:
                print(f"| {q.upper()} | " + " | ".join(f"{(a - b) / 1024:.0f} ({b / 1024:.0f})" for a, b in row) + " |")
    spread = [(max(v) - min(v)) / statistics.median(v) for v in cells.values() if len(v) > 1]
    print(f"\n{sum(len(v) for v in cells.values())} processus retenus, {max(len(v) for v in cells.values())} passes, {bad} en échec ; "
          + (f"écart entre passes (étendue / médiane) : médiane {100 * statistics.median(spread):.1f} %, "
             f"maximum {100 * max(spread):.1f} % ; " if spread else "")
          + f"machine(s) : {', '.join(sorted(f'{m} ({c})' for m, c, _ in stamps))}.")


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "run":
        run(sys.argv[2])
    elif len(sys.argv) >= 3 and sys.argv[1] == "summary":
        summary(sys.argv[2])
    else:
        raise SystemExit(__doc__)
