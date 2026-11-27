#!/usr/bin/env python3
"""Définition des trois tailles de chaque noyau (docs/METHOD.md, 3), données et environnement.

Chaque taille d'un noyau est un jeu de variables d'environnement lues par les implémentations (valeurs publiées par
défaut) et, pour les noyaux à données, un répertoire de données propre dans /dev/shm, produit par tools/gendata.c
(mêmes graines et mêmes lois qu'à la taille publiée, dont les fichiers restent ceux de /opt/msdata)."""
import os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SHM = "/dev/shm"
GENDATA = os.path.join(ROOT, "tools", "sizes", "gendata")

# taille -> (paramètres de taille, arguments de gendata) ; "pub" = taille publiée. Les paramètres sont des constantes
# de compilation redéfinies à la construction pour les langages compilés (MS_N1=…), des constantes substituées dans
# une copie du source pour Julia (tools/sizes/patches.py) ; sans elles, les valeurs publiées.
SIZES = {
    "k1": {"small": ({"MS_N1": 1 << 14}, ["--n1", 1 << 14]), "pub": ({}, None),
           "large": ({"MS_N1": 1 << 24}, ["--n1", 1 << 24])},
    "k4": {"small": ({"MS_N4": 1 << 20}, ["--n4", 1 << 20]), "pub": ({}, None),
           "large": ({"MS_N4": 1 << 28}, ["--n4", 1 << 28])},
    "k5": {"pub": ({}, None), "l2": ({"MS_N5": 1 << 15, "MS_INNER5": 1 << 12}, ["--n5", 1 << 15]),
           "l3": ({"MS_N5": 1 << 21, "MS_INNER5": 1 << 6}, ["--n5", 1 << 21])},
    "k6": {"small": ({"MS_N6": 1 << 16}, ["--n6", 1 << 16]), "pub": ({}, None),
           "large": ({"MS_N6": 1 << 26}, ["--n6", 1 << 26])},
    "k7": {"small": ({"MS_N7": 1 << 16, "MS_K7_LOG2": 12, "MS_K7_NB": 4093}, ["--n7", 1 << 16, "--keys7", 1 << 12]),
           "pub": ({}, None),
           "large": ({"MS_N7": 1 << 27, "MS_K7_LOG2": 23, "MS_K7_NB": 8388593}, ["--n7", 1 << 27, "--keys7", 1 << 23])},
    "k8": {"small": ({"MS_K8_LONG": 16, "MS_K8_REQ": 8}, None), "pub": ({}, None),
           "large": ({"MS_K8_LONG": 23, "MS_K8_REQ": 12}, None)},
    "k9": {"small": ({"MS_M9": 1 << 8}, None), "pub": ({}, None), "large": ({"MS_M9": 1 << 13}, None)},
}
ORDER = {k: list(v) for k, v in SIZES.items()}
PUBLISHED = {"MS_N1": 1 << 22, "MS_N4": 1 << 24, "MS_N5": 2048, "MS_INNER5": 1 << 16, "MS_N6": 1 << 24, "MS_N7": 1 << 24,
             "MS_K7_LOG2": 20, "MS_K7_NB": 1048573, "MS_K8_LONG": 20, "MS_K8_REQ": 10, "MS_M9": 2048}
# jeux de constructions des langages compilés : une construction par jeu, qui fixe la taille de chaque noyau
SETS = {"small": {"k1": "small", "k4": "small", "k5": "l2", "k6": "small", "k7": "small", "k8": "small", "k9": "small"},
        "large": {"k1": "large", "k4": "large", "k5": "l3", "k6": "large", "k7": "large", "k8": "large", "k9": "large"}}


def set_of(kernel, size):
    """Jeu de construction qui porte la taille size du noyau kernel (None : la construction publiée)."""
    for name, m in SETS.items():
        if m.get(kernel) == size:
            return name
    return None


def set_params(name):
    """Paramètres de taille d'un jeu de construction (les valeurs publiées complétées par celles du jeu)."""
    out = dict(PUBLISHED)
    for k, size in SETS[name].items():
        out.update(SIZES[k][size][0])
    return out


def data_dir(kernel, size):
    env, gen = SIZES[kernel][size]
    return "/opt/msdata" if gen is None else os.path.join(SHM, f"ms_{kernel}_{size}")


def ensure_gendata():
    if not os.path.exists(GENDATA) or os.path.getmtime(GENDATA) < os.path.getmtime(os.path.join(ROOT, "tools", "gendata.c")):
        subprocess.run(["gcc", "-O2", "-o", GENDATA, os.path.join(ROOT, "tools", "gendata.c")], check=True)


def ensure_data(kernel, size):
    env, gen = SIZES[kernel][size]
    d = data_dir(kernel, size)
    if gen is None:
        return d
    stamp = os.path.join(d, ".complete")
    if not os.path.exists(stamp):
        ensure_gendata()
        os.makedirs(d, exist_ok=True)
        subprocess.run([GENDATA, d, "--only", kernel] + [str(x) for x in gen], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        open(stamp, "w").close()
    return d


def drop_data(kernel, size):
    env, gen = SIZES[kernel][size]
    if gen is not None:
        subprocess.run(["rm", "-rf", data_dir(kernel, size)], check=True)


def view_dir(name):
    """Répertoire de liens vers les données d'un jeu de construction (/dev/shm/ms_view_<jeu>), pour les langages qui
    fixent le répertoire des données à la compilation (Mojo) : chaque fichier de /opt/msdata, sauf ceux des noyaux du
    jeu, remplacés par ceux de leur taille (produits à la demande par ensure_data)."""
    d = os.path.join(SHM, f"ms_view_{name}")
    os.makedirs(d, exist_ok=True)
    for f in sorted(os.listdir("/opt/msdata")):
        k = f.split("_")[0]
        target = os.path.join("/opt/msdata", f)
        if k in SETS[name]:
            target = os.path.join(data_dir(k, SETS[name][k]), f)
        link = os.path.join(d, f)
        if os.path.islink(link) and os.readlink(link) == target:
            continue
        if os.path.lexists(link):
            os.remove(link)
        os.symlink(target, link)
    return d + "/"


def environ(kernel, size, base=None):
    env = dict(base if base is not None else os.environ)
    for k in PUBLISHED:
        env.pop(k, None)
    env.update({k: str(v) for k, v in SIZES[kernel][size][0].items()})
    env["MS_DATA"] = data_dir(kernel, size)
    return env


if __name__ == "__main__":
    for k, d in SIZES.items():
        print(k, ", ".join(f"{s}: {e or 'publiée'}" for s, (e, g) in d.items()))
