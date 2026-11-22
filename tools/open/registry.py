#!/usr/bin/env python3
"""v4, point 6 (docs/V4_OPEN.md, 3.2 à 3.4) : recherche dans le registre de chaque langage.

Pour chaque couple (langage, case) où l'une des 15 cases « d'API » vaut moins de 1 dans la grille du score central
(analysis/capabilities.py et capabilities_v2.py, celle que le score lit), le registre du langage est interrogé avec
chacun des mots de la case (table de 3.2) ; les réponses sont réunies, la statistique d'usage du registre (3.1) est
relevée pour chaque bibliothèque trouvée, et les bibliothèques sont classées par cette statistique (les dix premières
sont à examiner, toutes pour un registre sans statistique). Écrit results/open/registry/<langage>.json : réponses
brutes résumées (nom, description, statistique, mots qui l'ont trouvée), par case. Usage :
  tools/open/registry.py <langage> [...]      (ou « all »)
Le choix (3.3) se fait à la lecture de ces fichiers et va dans results/open/list.md ; cet outil ne choisit rien.
"""
import gzip
import html
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "analysis"))
from capabilities import MATRIX  # noqa: E402
from capabilities_v2 import V2_OVERRIDES  # noqa: E402

OUT = os.path.join(ROOT, "results", "open", "registry")
CACHE = os.environ.get("OPEN_CACHE", "/tmp/open_registry_cache")
UA = "ms-bench-registry-survey/1.0 (research; contact via repository)"

API = ["A6", "B2", "B5", "C1", "C2", "C5", "D1", "D2", "D3", "D4", "D5", "E4", "F1", "F2", "F4"]
KEYWORDS = {
    "A6": ["soa", "struct of arrays", "structure of arrays"],
    "B2": ["arena", "bump allocator", "memory pool"],
    "B5": ["raw memory", "pointer", "unsafe memory"],
    "C1": ["simd", "vector types"],
    "C2": ["intrinsics", "avx"],
    "C5": ["parallel", "parallel for", "data parallel"],
    "D1": ["threads", "multithreading"],
    "D2": ["atomic", "atomics"],
    "D3": ["cache line", "cache padded", "false sharing"],
    "D4": ["affinity", "cpu affinity", "thread pinning"],
    "D5": ["spin", "spin wait", "barrier"],
    "E4": ["prefetch"],
    "F1": ["ndarray", "multidimensional array", "matrix"],
    "F2": ["numa", "hwloc"],
    "F4": ["mmap", "memory map"],
}


def holes(lang):
    out = []
    for c in API:
        v = MATRIX[lang][c]
        v = V2_OVERRIDES[(lang, c)][0] if (lang, c) in V2_OVERRIDES else v[0]
        if v < 1:
            out.append((c, v))
    return out


# ------------------------------------------------------------------ accès réseau (avec cache local et reprises)
def fetch(url, data=None, headers=None, binary=False, tries=4):
    os.makedirs(CACHE, exist_ok=True)
    key = re.sub(r"[^A-Za-z0-9]+", "_", url + (json.dumps(data) if data else ""))[:200]
    path = os.path.join(CACHE, key)
    if os.path.exists(path):
        with open(path, "rb") as f:
            raw = f.read()
        return raw if binary else raw.decode("utf-8", "replace")
    h = {"User-Agent": UA, "Accept": "*/*"}
    h.update(headers or {})
    body = None
    if data is not None:
        body = json.dumps(data).encode()
        h["Content-Type"] = "application/json"
    err = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, data=body, headers=h)
            with urllib.request.urlopen(req, timeout=60) as r:
                raw = r.read()
            with open(path, "wb") as f:
                f.write(raw)
            time.sleep(0.2)
            return raw if binary else raw.decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            err = e
        except Exception as e:  # noqa: BLE001
            err = e
        time.sleep(2 * (i + 1))
    raise RuntimeError(f"{url}: {err}")


def jget(url, **kw):
    raw = fetch(url, **kw)
    return None if raw is None else json.loads(raw)


def q(s):
    return urllib.parse.quote(s)


# ------------------------------------------------------------------ adaptateurs : search(mot) -> [{name, desc}]
#                                                                       stat(noms) -> {nom: valeur}
class CratesIo:
    stat_name = "téléchargements des 90 derniers jours (crates.io, recent_downloads)"

    def search(self, kw):
        d = jget(f"https://crates.io/api/v1/crates?q={q(kw)}&per_page=20&sort=relevance")
        self._s = getattr(self, "_s", {})
        out = []
        for c in d.get("crates", []):
            self._s[c["name"]] = c.get("recent_downloads") or 0
            out.append({"name": c["name"], "desc": (c.get("description") or "").strip()})
        return out

    def stat(self, names):
        res = {}
        for n in names:
            if n in self._s:
                res[n] = self._s[n]
            else:
                d = jget(f"https://crates.io/api/v1/crates/{q(n)}")
                res[n] = (d or {}).get("crate", {}).get("recent_downloads") or 0
        return res


class Npm:
    stat_name = "téléchargements du dernier mois (api.npmjs.org)"

    def search(self, kw):
        d = jget(f"https://registry.npmjs.org/-/v1/search?text={q(kw)}&size=20")
        return [{"name": o["package"]["name"], "desc": (o["package"].get("description") or "").strip()}
                for o in d.get("objects", [])]

    def stat(self, names):
        res = {}
        for n in names:
            d = jget(f"https://api.npmjs.org/downloads/point/last-month/{n}")
            res[n] = (d or {}).get("downloads", 0) or 0
        return res


class NuGet:
    stat_name = "téléchargements totaux (NuGet)"

    def search(self, kw):
        d = jget(f"https://azuresearch-usnc.nuget.org/query?q={q(kw)}&take=20&prerelease=false&semVerLevel=2.0.0")
        self._s = getattr(self, "_s", {})
        out = []
        for p in d.get("data", []):
            self._s[p["id"]] = p.get("totalDownloads", 0)
            out.append({"name": p["id"], "desc": (p.get("description") or "").strip()})
        return out

    def stat(self, names):
        return {n: self._s.get(n, 0) for n in names}


class Packagist:
    stat_name = "téléchargements du dernier mois (Packagist)"

    def search(self, kw):
        d = jget(f"https://packagist.org/search.json?q={q(kw)}&per_page=20")
        return [{"name": p["name"], "desc": (p.get("description") or "").strip()} for p in d.get("results", [])]

    def stat(self, names):
        res = {}
        for n in names:
            d = jget(f"https://packagist.org/packages/{n}.json")
            res[n] = (d or {}).get("package", {}).get("downloads", {}).get("monthly", 0)
        return res


class Dub:
    stat_name = "téléchargements du dernier mois (dub)"

    def search(self, kw):
        d = jget(f"https://code.dlang.org/api/packages/search?q={q(kw)}")
        return [{"name": p["name"], "desc": (p.get("description") or "").strip()} for p in (d or [])[:20]]

    def stat(self, names):
        res = {}
        for n in names:
            d = jget(f"https://code.dlang.org/api/packages/{q(n)}/stats")
            res[n] = (d or {}).get("downloads", {}).get("monthly", 0)
        return res


class PyPI:
    stat_name = "téléchargements du dernier mois (pypistats)"

    def search(self, kw):
        raw = fetch(f"https://pypi.org/search/?q={q(kw)}")
        out = []
        for m in re.finditer(r'<span class="package-snippet__name">([^<]+)</span>.*?'
                             r'<p class="package-snippet__description">([^<]*)</p>', raw or "", re.S):
            out.append({"name": html.unescape(m.group(1)).strip(), "desc": html.unescape(m.group(2)).strip()})
        return out[:20]

    def stat(self, names):
        res = {}
        for n in names:
            d = jget(f"https://pypistats.org/api/packages/{n.lower()}/recent")
            res[n] = (d or {}).get("data", {}).get("last_month", 0)
        return res


class Hackage:
    stat_name = "téléchargements des 30 derniers jours (Hackage)"

    def search(self, kw):
        d = jget("https://hackage.haskell.org/packages/search",
                 data={"page": 0, "sortColumn": "default", "sortDirection": "ascending", "searchQuery": kw},
                 headers={"Accept": "application/json"})
        self._s = getattr(self, "_s", {})
        out = []
        for p in (d or {}).get("pageContents", [])[:20]:
            name = p["name"]["display"] if isinstance(p.get("name"), dict) else p.get("name")
            self._s[name] = p.get("downloads", 0)
            out.append({"name": name, "desc": (p.get("description") or "").strip()})
        return out

    def stat(self, names):
        return {n: self._s.get(n, 0) for n in names}


ADAPTERS = {"rust": CratesIo, "js": Npm, "csharp": NuGet, "php": Packagist, "d": Dub, "python": PyPI,
            "haskell": Hackage}


def survey(lang):
    ad = ADAPTERS[lang]()
    res = {"langage": lang, "statistique": ad.stat_name, "date": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()),
           "cases": {}}
    for case, val in holes(lang):
        found = {}
        for kw in KEYWORDS[case]:
            for r in ad.search(kw):
                e = found.setdefault(r["name"], {"name": r["name"], "desc": r["desc"][:300], "mots": []})
                e["mots"].append(kw)
        st = ad.stat(list(found))
        cands = sorted(found.values(), key=lambda e: -(st.get(e["name"]) or 0))
        for e in cands:
            e["stat"] = st.get(e["name"]) or 0
        res["cases"][case] = {"note": val, "mots": KEYWORDS[case], "candidates": cands}
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, f"{lang}.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    return res


if __name__ == "__main__":
    langs = sys.argv[1:] or ["all"]
    if langs == ["all"]:
        langs = list(ADAPTERS)
    for l in langs:
        r = survey(l)
        print(l, {c: len(v["candidates"]) for c, v in r["cases"].items()})
