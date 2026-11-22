#!/usr/bin/env python3
"""v4, point 6 : campagne de la piste ouverte (docs/V4_OPEN.md, section 6 ; écart 7 de la section 10).

Le pilote du point 4 (tools/converge/campaign.py), adapté. Processus, d'après results/open/forms.json
(tools/open/forms.py) : pour chaque (langage, cellule) touché, chaque forme op_* (construction op), la forme d'accès de
la cellule dans les constructions op et cv (témoin de construction, 5.2) ; pour chaque cellule touchée, la forme de C
de la cellule (témoin d'hôte, calcul 6), dans la construction qui la porte (pub ou cv). Constructions
(tools/open/build.py, /dev/shm/msbuild/<langage>/<construction>), toutes faites avant la première mesure.
Trois passes ; dans chaque passe, l'ordre des groupes (un par noyau) est tiré au hasard (graine 20261122 + 6000 +
passe), puis celui des blocs (langage, construction) de chaque groupe ; un bloc exécute un processus par cellule.
Comme aux points 2 à 4 : répétitions fixées par une exécution de calibration avant le premier processus de la cellule
(environ 3 s par processus, au moins 3 et au plus 10 000 ; une seule au-delà de 300 s), échauffement d'une répétition
(langages à JIT : au moins 3 et au moins une seconde), processus refait une fois si le vol de temps dépasse 5 %,
sentinelle de mémoire (plus grand VmRSS du groupe de processus, 13 Gio), modèle du processeur vérifié avant chaque
processus (s'il change, arrêt). b3 (tools/open/k3_ref.sh) est mesuré avant la première passe et après la dernière.
Sortie : results/open/work/raw/<langage>.jsonl (une ligne par processus), calib.json, campaign.log ;
tools/open/save_progress.sh les recopie dans results/open et les pousse à la fin de chaque groupe. Reprise : un
processus déjà enregistré (passe, langage, construction, noyau, variante, paramètre) n'est pas refait.

Usage : campaign.py [--passes 0,1,2] [--langs python,rust,...] [--kernels k1,...] [--dry]"""
import argparse, json, os, random, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "converge"))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "analysis"))
import importlib.util  # noqa: E402


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


B = _load("openbuild", os.path.join(HERE, "build.py"))               # constructions pub, cv, op
C = _load("cvcampaign", os.path.join(ROOT, "tools", "converge", "campaign.py"))  # exécution, calibration, contrôles

FORMS = json.load(open(os.path.join(ROOT, "results", "open", "forms.json")))
SEED = 20261122 + 6000
WORK = os.path.join(ROOT, "results", "open", "work")
RAW = os.path.join(WORK, "raw")
CALIB = os.path.join(WORK, "calib.json")
LOG = os.path.join(WORK, "campaign.log")
# le pilote du point 4 écrit dans ses propres fichiers : on lui donne ceux de cette campagne
C.WORK, C.RAW, C.CALIB, C.LOG, C.B = WORK, RAW, CALIB, LOG, B


def k(key):
    f = key.split("|")
    return f[0], f[1], f[2]


def plan():
    """{(langage, construction): {noyau: [(variante, paramètre)]}}, dans l'ordre du relevé, sans doublon."""
    out = {}

    def add(lang, build, key):
        kern, v, p = k(key)
        lst = out.setdefault((lang, build), {}).setdefault(kern, [])
        if (v, p) not in lst:
            lst.append((v, p))
    for f in FORMS["forms"]:
        add(f["lang"], "op", f["key"])
    for lang, cells in FORMS["access"].items():
        for cell, key in cells.items():
            add(lang, "op", key)
            add(lang, "cv", key)
    for cell, w in FORMS["c_witness"].items():
        add("c", w["build"], w["key"])
    return out


PLAN = plan()
LANGS = sorted({l for l, b in PLAN})
KERNELS = sorted({kern for x in PLAN.values() for kern in x})


def builds_of(lang):
    return [b for b in ("pub", "cv", "op") if (lang, b) in PLAN]


def cells(lang, build, kernel):
    return list(PLAN.get((lang, build), {}).get(kernel, []))


def b3(which):
    p = os.path.join(ROOT, "results", "open", f"k3_ref_{which}.txt")
    if os.path.exists(p):
        return
    moment = "avant la première passe" if which == "start" else "après la dernière passe"
    r = subprocess.run(["sh", os.path.join(HERE, "k3_ref.sh"), which, "machine 34", moment], capture_output=True,
                       text=True)
    C.log(f"b3 ({which}) : code {r.returncode}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--passes", default="0,1,2")
    ap.add_argument("--langs", default=",".join(LANGS))
    ap.add_argument("--kernels", default=",".join(KERNELS))
    ap.add_argument("--dry", action="store_true", help="liste les groupes sans rien construire ni exécuter")
    a = ap.parse_args()
    langs = a.langs.split(",")
    kernels = a.kernels.split(",")
    passes = [int(x) for x in a.passes.split(",")]
    if not a.dry:
        os.makedirs(RAW, exist_ok=True)
    model = C.cpu_model()
    try:  # le pilote, pas la victime
        with open("/proc/self/oom_score_adj", "w") as f:
            f.write("-900")
    except OSError:
        pass
    if not a.dry:  # toutes les constructions avant la première mesure (aucune compilation pendant un groupe)
        for lang in langs:
            for b in builds_of(lang):
                B.ensure(lang, b)
        C.log(f"constructions prêtes ; processeur : {model}")
        if 0 in passes:
            b3("start")
    for p in passes:
        gl = list(kernels)
        rnd = random.Random(SEED + p)
        rnd.shuffle(gl)
        (print if a.dry else C.log)(f"passe {p} : {len(gl)} groupes ; processeur : {model}")
        for gi, kernel in enumerate(gl):
            blocks = [(l, b) for l in langs for b in builds_of(l) if cells(l, b, kernel)]
            rnd.shuffle(blocks)
            done = C.done_set()
            todo = [(l, b, v, q) for l, b in blocks for v, q in cells(l, b, kernel)
                    if (p, l, b, kernel, v, q) not in done]
            if a.dry:
                print(p, kernel, len(blocks), "blocs", len(todo), "processus")
                continue
            if not todo:
                continue
            t_g = time.time()
            for lang, build, variant, param in todo:
                if C.cpu_model() != model:
                    C.log(f"le modèle du processeur a changé ({C.cpu_model()} au lieu de {model}) : arrêt")
                    C.save_progress()
                    sys.exit(3)
                c = C.calibrate(lang, build, kernel, variant, param)
                if c.get("failed"):
                    rec = {"lang": lang, "build": build, "kernel": kernel, "size": "pub", "variant": variant,
                           "param": param, "reps": [], "failed_calibration": c}
                else:
                    timeout = min(4 * 3600, 600 + 3 * (c["reps"] + c["warmup"]) * c["t_cal"])
                    for attempt in range(2):
                        rec = C.run_one(lang, build, kernel, variant, param, c["reps"], c["warmup"], timeout)
                        rec["attempt"] = attempt
                        if rec["steal_frac"] <= 0.05:
                            break
                rec.update({"pass": p, "ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "cpu_model": C.cpu_model()})
                with open(os.path.join(RAW, f"{lang}.jsonl"), "a") as f:
                    f.write(json.dumps(rec) + "\n")
                print(f"p{p} {kernel} {lang}/{build} {variant} {param} n={rec.get('n', 0)}"
                      f" med={rec.get('median', float('nan')):.6g}s ok={rec.get('oks')}"
                      f" oom={rec.get('oom')} rc={rec.get('returncode')}", flush=True)
            C.log(f"passe {p} groupe {gi + 1}/{len(gl)} {kernel} {len(todo)} processus {time.time() - t_g:.0f}s")
            save_progress()
    if not a.dry and 2 in passes:
        b3("end")
        save_progress()
    (print if a.dry else C.log)("campagne finie")


def save_progress():
    r = subprocess.run(["sh", os.path.join(HERE, "save_progress.sh")], capture_output=True, text=True)
    if r.returncode:
        C.log(f"enregistrement : code {r.returncode} {r.stderr[-300:]}")


C.save_progress = save_progress  # arrêt sur changement de processeur : l'enregistrement de cette campagne

if __name__ == "__main__":
    main()
