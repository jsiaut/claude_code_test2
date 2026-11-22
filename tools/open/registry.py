#!/usr/bin/env python3
"""v4, point 6 (docs/V4_OPEN.md, 3.2 à 3.4 et 10) : recherche dans le registre de chaque langage.

Pour chaque couple (langage, case) où l'une des 15 cases « d'API » vaut moins de 1 dans la grille du score central
(analysis/capabilities.py et capabilities_v2.py, celle que le score lit), le registre du langage est interrogé avec
chacun des mots de la case (table de 3.2) : par son API de recherche quand il en a une publique (crates.io, npm, NuGet,
Packagist, dub, Maven Central, pkg.go.dev, LuaRocks), sinon par la recherche des mots (mot entier, sans distinction de
casse) dans le nom, la description et les mots-clés de son index (écart 1 de la section 10 : ecosyste.ms pour PyPI,
Hackage, opam, General, Swift Package Index et Ubuntu 24.04 ; fichiers ou clones Git pour nimble, Alire, Mason,
fortran-lang.org, le dépôt vendor de C3, fppkg et le canal modular-community). Les réponses sont réunies, la
statistique d'usage de 3.1 est relevée pour chaque bibliothèque trouvée, et les bibliothèques sont classées par cette
statistique (registre sans statistique : par ancienneté de la première version, 3.3 b). Écrit
results/open/registry/<langage>.json. Usage : tools/open/registry.py <langage>... | all
Le choix (3.3) se fait à la lecture de ces fichiers et va dans results/open/list.md : cet outil ne choisit rien.
"""
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
UA = "ms-bench-registry-survey/1.0 (research)"
MAINTAINED = "2024-11-22"  # 3.3 b : une version publiée depuis cette date

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


def kw_re(kw):
    """Mot (ou suite de mots) entier, sans casse ; espaces, « - » et « _ » interchangeables."""
    parts = [re.escape(p) for p in kw.split()]
    return re.compile(r"(?<![A-Za-z0-9])" + r"[ _\-]?".join(parts) + r"(?![A-Za-z0-9])", re.I)


# ------------------------------------------------------------------ réseau (cache local, reprises, politesse)
def fetch(url, binary=False, tries=4, delay=0.3):
    os.makedirs(CACHE, exist_ok=True)
    key = re.sub(r"[^A-Za-z0-9]+", "_", url)[:180] + "_" + str(abs(hash(url)) % 10**8)
    path = os.path.join(CACHE, key)
    if os.path.exists(path):
        with open(path, "rb") as f:
            raw = f.read()
        return raw if binary else raw.decode("utf-8", "replace")
    err = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
            with urllib.request.urlopen(req, timeout=90) as r:
                raw = r.read()
            with open(path, "wb") as f:
                f.write(raw)
            time.sleep(delay)
            return raw if binary else raw.decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code in (404, 410):
                return None
            err = e
        except Exception as e:  # noqa: BLE001
            err = e
        time.sleep(3 * (i + 1))
    raise RuntimeError(f"{url}: {err}")


def jget(url, **kw):
    raw = fetch(url, **kw)
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def qq(s):
    return urllib.parse.quote(s, safe="")


def git(url, name):
    d = os.path.join(CACHE, "git", name)
    if not os.path.isdir(d):
        os.makedirs(os.path.dirname(d), exist_ok=True)
        subprocess.run(["git", "clone", "-q", "--filter=blob:none", url, d], check=True, timeout=900)
    return d


def git_dates(url, name):
    """Première et dernière date de commit d'un dépôt (clone sans blobs) ; (None, None) si injoignable."""
    try:
        d = os.path.join(CACHE, "gitrepos", re.sub(r"[^A-Za-z0-9]+", "_", name))
        if not os.path.isdir(d):
            os.makedirs(os.path.dirname(d), exist_ok=True)
            subprocess.run(["git", "clone", "-q", "--bare", "--filter=tree:0", url, d], check=True, timeout=600,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        out = subprocess.run(["git", "-C", d, "log", "--all", "--format=%cs"], capture_output=True, text=True,
                             timeout=120).stdout.split()
        return (min(out), max(out)) if out else (None, None)
    except Exception:  # noqa: BLE001
        return (None, None)


# ------------------------------------------------------------------ registres à API de recherche
class Search:
    """search(mot) -> [{name, desc}] ; stat(noms) -> {nom: valeur} (plus grand = plus utilisé)."""
    order = "stat"

    def candidates(self, kws):
        found = {}
        for kw in kws:
            for r in self.search(kw):
                e = found.setdefault(r["name"], {"name": r["name"], "desc": r["desc"][:300], "mots": []})
                e["mots"].append(kw)
        return found


class CratesIo(Search):
    stat_name = "téléchargements des 90 derniers jours (crates.io, recent_downloads)"

    def __init__(self):
        self._s = {}

    def search(self, kw):
        d = jget(f"https://crates.io/api/v1/crates?q={qq(kw)}&per_page=20") or {}
        out = []
        for c in d.get("crates", []):
            self._s[c["name"]] = c.get("recent_downloads") or 0
            out.append({"name": c["name"], "desc": (c.get("description") or "").strip()})
        return out

    def stat(self, names):
        return {n: self._s.get(n, 0) for n in names}


class Npm(Search):
    stat_name = "téléchargements du dernier mois (api.npmjs.org)"

    def search(self, kw):
        d = jget(f"https://registry.npmjs.org/-/v1/search?text={qq(kw)}&size=20") or {}
        return [{"name": o["package"]["name"], "desc": (o["package"].get("description") or "").strip()}
                for o in d.get("objects", [])]

    def stat(self, names):
        return {n: (jget(f"https://api.npmjs.org/downloads/point/last-month/{n}") or {}).get("downloads", 0) or 0
                for n in names}


class NuGet(Search):
    stat_name = "téléchargements totaux (NuGet)"

    def __init__(self):
        self._s = {}

    def search(self, kw):
        d = jget(f"https://azuresearch-usnc.nuget.org/query?q={qq(kw)}&take=20&prerelease=false"
                 f"&semVerLevel=2.0.0") or {}
        out = []
        for p in d.get("data", []):
            self._s[p["id"]] = p.get("totalDownloads", 0)
            out.append({"name": p["id"], "desc": (p.get("description") or "").strip()})
        return out

    def stat(self, names):
        return {n: self._s.get(n, 0) for n in names}


class Packagist(Search):
    stat_name = "téléchargements du dernier mois (Packagist)"

    def search(self, kw):
        d = jget(f"https://packagist.org/search.json?q={qq(kw)}&per_page=20") or {}
        return [{"name": p["name"], "desc": (p.get("description") or "").strip()} for p in d.get("results", [])]

    def stat(self, names):
        return {n: ((jget(f"https://packagist.org/packages/{n}.json") or {}).get("package", {})
                    .get("downloads", {}).get("monthly", 0)) for n in names}


class Dub(Search):
    stat_name = "téléchargements du dernier mois (dub)"

    def search(self, kw):
        d = jget(f"https://code.dlang.org/api/packages/search?q={qq(kw)}") or []
        return [{"name": p["name"], "desc": (p.get("description") or "").strip()} for p in d[:20]]

    def stat(self, names):
        return {n: ((jget(f"https://code.dlang.org/api/packages/{qq(n)}/stats") or {}).get("downloads", {})
                    .get("monthly", 0)) for n in names}


class Maven(Search):
    stat_name = "dépendants de la version par défaut (deps.dev)"

    def search(self, kw):
        d = jget(f"https://search.maven.org/solrsearch/select?q={qq(kw)}&rows=20&wt=json") or {}
        return [{"name": f'{x["g"]}:{x["a"]}', "desc": ""} for x in d.get("response", {}).get("docs", [])]

    def stat(self, names):
        res = {}
        for n in names:
            p = jget(f"https://api.deps.dev/v3/systems/maven/packages/{qq(n)}") or {}
            v = [x["versionKey"]["version"] for x in p.get("versions", []) if x.get("isDefault")]
            if not v:
                res[n] = 0
                continue
            d = jget(f"https://api.deps.dev/v3alpha/systems/maven/packages/{qq(n)}/versions/{qq(v[0])}:dependents")
            res[n] = (d or {}).get("dependentCount", 0)
        return res


class GoPkg(Search):
    stat_name = "« imported by » (pkg.go.dev)"

    def __init__(self):
        self._s = {}

    def search(self, kw):
        raw = fetch(f"https://pkg.go.dev/search?q={qq(kw)}&m=package&limit=25") or ""
        out = []
        for blk in re.split(r'<div class="SearchSnippet"\s*>', raw)[1:]:
            m = re.search(r'<a href="/([^"?#]+)"[^>]*?data-test-id="snippet-title"', blk, re.S)
            if not m:
                continue
            name = m.group(1)
            dm = re.search(r'data-test-id="snippet-synopsis"[^>]*>\s*(.*?)\s*</p>', blk, re.S)
            im = re.search(r"Imported by </span><strong>([\d,]+)</strong>", blk)
            self._s[name] = int(im.group(1).replace(",", "")) if im else 0
            out.append({"name": name, "desc": html.unescape(re.sub("<[^>]+>", "", dm.group(1))).strip() if dm else ""})
        return out[:20]

    def stat(self, names):
        return {n: self._s.get(n, 0) for n in names}


class LuaRocks(Search):
    stat_name = "téléchargements (LuaRocks)"

    def __init__(self):
        self._s = {}

    def search(self, kw):
        raw = fetch(f"https://luarocks.org/search?q={qq(kw)}") or ""
        out = []
        for blk in raw.split('<li class="module_row">')[1:]:
            m = re.search(r'<a href="/modules/([^/"]+)/([^"/]+)" class="title">', blk)
            if not m:
                continue
            name = f"{m.group(1)}/{m.group(2)}"
            dm = re.search(r'<div class="summary">(.*?)</div>', blk, re.S)
            out.append({"name": name, "desc": html.unescape(dm.group(1)).strip() if dm else ""})
        return out[:20]

    def stat(self, names):
        """Téléchargements lus sur la page du module : la page de recherche ne les donne pas pour tous."""
        res = {}
        for n in names:
            raw = fetch(f"https://luarocks.org/modules/{n}") or ""
            m = re.search(r"Downloads</h3>([\d,]+)", raw)
            res[n] = int(m.group(1).replace(",", "")) if m else 0
        return res


# ------------------------------------------------------------------ registres lus dans leur index
class Index:
    """items() -> [{name, desc, keywords, ...}] ; les candidates sont les paquets dont le nom, la description ou les
    mots-clés contiennent un mot de la case (mot entier)."""

    def candidates(self, kws):
        found = {}
        for it in self.items():
            text = " ".join([it["name"], it.get("desc", ""), " ".join(it.get("keywords") or [])])
            hit = [kw for kw in kws if kw_re(kw).search(text)]
            if hit:
                found[it["name"]] = {"name": it["name"], "desc": (it.get("desc") or "")[:300], "mots": hit}
        return found


class Eco(Index):
    """Index d'un registre tel que le publie ecosyste.ms, trié par téléchargements (pages de 1000)."""

    def __init__(self, registry, top=None, sort="downloads"):
        self.registry, self.top, self.sort = registry, top, sort
        self._items = None

    def items(self):
        if self._items is None:
            self._items, page = [], 1
            while True:
                d = jget(f"https://packages.ecosyste.ms/api/v1/registries/{self.registry}/packages"
                         f"?sort={self.sort}&order=desc&per_page=1000&page={page}", delay=1.0)
                if not d:
                    break
                for x in d:
                    self._items.append({"name": x["name"], "desc": (x.get("description") or "").strip(),
                                        "keywords": x.get("keywords_array") or [], "downloads": x.get("downloads"),
                                        "period": x.get("downloads_period"),
                                        "dependents": x.get("dependent_packages_count"),
                                        "first": (x.get("first_release_published_at") or "")[:10],
                                        "latest": (x.get("latest_release_published_at") or "")[:10]})
                page += 1
                if len(d) < 1000 or (self.top and len(self._items) >= self.top):
                    break
            if self.top:
                self._items = self._items[:self.top]
            self._by = {x["name"]: x for x in self._items}
        return self._items


class PyPIEco(Eco):
    stat_name = "téléchargements du dernier mois (pypistats)"

    def __init__(self):
        super().__init__("pypi.org", top=20000)

    def stat(self, names):
        return {n: (jget(f"https://pypistats.org/api/packages/{n.lower()}/recent", delay=1.5) or {})
                .get("data", {}).get("last_month", 0) for n in names}


class HackageEco(Eco):
    stat_name = "téléchargements (page « top » de Hackage)"

    def __init__(self):
        super().__init__("hackage.haskell.org")
        self._top = None

    def stat(self, names):
        if self._top is None:
            raw = fetch("https://hackage.haskell.org/packages/top") or ""
            self._top = {m.group(1): int(m.group(2)) for m in
                         re.finditer(r'<td><a href="/package/[^"]*">([^<]*)</a></td><td>(\d+)', raw)}
        return {n: self._top.get(n, 0) for n in names}


class EcoStat(Eco):
    def __init__(self, registry, field, stat_name):
        super().__init__(registry)
        self.field, self.stat_name = field, stat_name

    def stat(self, names):
        self.items()
        return {n: (self._by.get(n, {}).get(self.field) or 0) for n in names}


class EcoAge(Eco):
    """Registre sans statistique (3.3 b) : ancienneté de la première version, parmi les paquets maintenus."""
    order = "age"
    stat_name = "aucune : ancienneté de la première version (versions depuis le 22 novembre 2024)"

    def stat(self, names):
        self.items()
        return {n: {"first": self._by[n]["first"], "latest": self._by[n]["latest"]} for n in names}


class DebianPopcon(Eco):
    stat_name = "installations (popcon de Debian ; celui d'Ubuntu n'est plus publié : écart 2)"

    def __init__(self):
        super().__init__("ubuntu-24.04")
        self._pc = None

    def stat(self, names):
        if self._pc is None:
            raw = fetch("https://popcon.debian.org/by_inst") or ""
            self._pc = {}
            for line in raw.splitlines():
                p = line.split()
                if len(p) > 3 and p[0].isdigit():
                    self._pc[p[1]] = int(p[2])
        return {n: self._pc.get(n, 0) for n in names}


class Nimble(Index):
    order = "age"
    stat_name = "aucune : ancienneté du premier commit (dépôt maintenu depuis le 22 novembre 2024)"

    def items(self):
        d = jget("https://raw.githubusercontent.com/nim-lang/packages/master/packages.json") or []
        self._url = {p["name"]: p.get("url") for p in d if "name" in p}
        return [{"name": p["name"], "desc": p.get("description", ""), "keywords": p.get("tags", [])}
                for p in d if "name" in p and "url" in p]

    def stat(self, names):
        out = {}
        for n in names:
            f, l = git_dates(self._url[n], "nimble_" + n)
            out[n] = {"first": f, "latest": l, "url": self._url[n]}
        return out


class GitIndexDeps(Index):
    """Alire et Mason : manifestes TOML d'un clone ; statistique : dépendants dans l'index."""
    order = "stat"
    stat_name = "dépendants dans l'index"

    def __init__(self, url, name, root):
        self.url, self.name, self.root = url, name, root

    def items(self):
        if hasattr(self, "_items"):
            return self._items
        d = os.path.join(git(self.url, self.name), self.root)
        subprocess.run(["git", "-C", os.path.dirname(d) if self.root else d, "checkout", "-q"], check=False)
        pk, deps = {}, {}
        for dirpath, _, files in os.walk(d):
            for fn in files:
                if not fn.endswith(".toml"):
                    continue
                txt = open(os.path.join(dirpath, fn), encoding="utf-8", errors="replace").read()
                nm = re.search(r'^name\s*=\s*"([^"]+)"', txt, re.M)
                if not nm:
                    continue
                n = nm.group(1)
                ds = re.search(r'^description\s*=\s*"([^"]*)"', txt, re.M)
                tg = re.search(r"^tags\s*=\s*\[([^\]]*)\]", txt, re.M)
                pk[n] = {"name": n, "desc": ds.group(1) if ds else "",
                         "keywords": re.findall(r'"([^"]+)"', tg.group(1)) if tg else []}
                for blk in re.findall(r"^\[\[?depends-on\]?\]\s*\n((?:[^\[\n].*\n?)*)", txt, re.M) + \
                        re.findall(r"^\[dependencies\]\s*\n((?:[^\[\n].*\n?)*)", txt, re.M):
                    for dn in re.findall(r"^\s*([A-Za-z0-9_\-]+)\s*=", blk, re.M):
                        deps.setdefault(dn, set()).add(n)
        self._deps = {k: len(v) for k, v in deps.items()}
        self._items = list(pk.values())
        return self._items

    def stat(self, names):
        return {n: self._deps.get(n, 0) for n in names}


class FortranLang(Index):
    order = "age"
    stat_name = "aucune : ancienneté du premier commit (dépôt maintenu depuis le 22 novembre 2024)"
    CATS = ["data-types", "examples", "graphics", "interfaces", "io", "libraries", "numerical", "programming",
            "scientific", "strings"]

    def items(self):
        if hasattr(self, "_items"):
            return self._items
        self._items, self._url = [], {}
        for c in self.CATS:
            raw = fetch(f"https://fortran-lang.org/categories/{c}/") or ""
            for m in re.finditer(r'<a[^>]+href="(https://github\.com/[^"]+|https://gitlab\.com/[^"]+)"[^>]*>'
                                 r'\s*(?:<[^>]+>\s*)*([^<]+)</', raw):
                url, name = m.group(1), html.unescape(m.group(2)).strip()
                tail = raw[m.end():m.end() + 600]
                desc = html.unescape(re.sub(r"<[^>]+>", " ", tail.split("<a ")[0])).strip()
                if name and name not in self._url:
                    self._url[name] = url
                    self._items.append({"name": name, "desc": " ".join(desc.split())[:300], "keywords": [c]})
        return self._items

    def stat(self, names):
        out = {}
        for n in names:
            f, l = git_dates(self._url[n], "fortran_" + n)
            out[n] = {"first": f, "latest": l, "url": self._url[n]}
        return out


class C3Vendor(Index):
    order = "age"
    stat_name = "aucune : ancienneté de l'entrée dans le dépôt vendor (dépôt maintenu depuis le 22 novembre 2024)"

    def items(self):
        self._d = git("https://github.com/c3lang/vendor", "c3vendor")
        subprocess.run(["git", "-C", self._d, "checkout", "-q"], check=False)
        lib = os.path.join(self._d, "libraries")
        out = []
        for n in sorted(os.listdir(lib)) if os.path.isdir(lib) else []:
            desc = ""
            mf = os.path.join(lib, n, "manifest.json")
            if os.path.exists(mf):
                try:
                    desc = json.load(open(mf)).get("description", "") or ""
                except Exception:  # noqa: BLE001
                    pass
            out.append({"name": n, "desc": desc, "keywords": []})
        return out

    def stat(self, names):
        out = {}
        for n in names:
            dates = subprocess.run(["git", "-C", self._d, "log", "--format=%cs", "--", f"libraries/{n}"],
                                   capture_output=True, text=True).stdout.split()
            out[n] = {"first": min(dates) if dates else None, "latest": max(dates) if dates else None}
        return out


class Fppkg(Index):
    order = "age"
    stat_name = "aucune (fppkg ne publie ni téléchargements ni dates)"

    def items(self):
        raw = fetch("https://www.freepascal.org/repository/3.2.2/packages.xml") or ""
        out = []
        for m in re.finditer(r'<package name="([^"]+)">(.*?)</package>', raw, re.S):
            d = re.search(r"<description>(.*?)</description>", m.group(2), re.S)
            out.append({"name": m.group(1), "desc": html.unescape(d.group(1)).strip() if d else "", "keywords": []})
        return out

    def stat(self, names):
        return {n: {"first": None, "latest": None} for n in names}


class Modular(Index):
    order = "age"
    stat_name = "aucune : ancienneté de la première version (canal modular-community ; MAX : paquet de Modular)"

    def items(self):
        d = jget("https://repo.prefix.dev/modular-community/linux-64/repodata.json") or {}
        self._ts = {}
        for fn, p in list(d.get("packages", {}).items()) + list(d.get("packages.conda", {}).items()):
            n = p.get("name")
            ts = p.get("timestamp")
            if n and ts:
                self._ts.setdefault(n, []).append(time.strftime("%Y-%m-%d", time.gmtime(ts / 1000)))
        out = [{"name": n, "desc": "", "keywords": []} for n in sorted(self._ts)]
        mx = jget("https://pypi.org/pypi/max/json") or {}
        self._max = mx.get("info", {})
        out.append({"name": "max", "desc": (self._max.get("summary") or "") + " " +
                    (self._max.get("description") or "")[:2000], "keywords": []})
        return out

    def stat(self, names):
        out = {}
        for n in names:
            if n == "max":
                up = [f["upload_time"][:10] for r in (jget("https://pypi.org/pypi/max/json") or {})
                      .get("releases", {}).values() for f in r]
                out[n] = {"first": min(up) if up else None, "latest": max(up) if up else None,
                          "note": "paquet de Modular (PyPI)"}
            else:
                out[n] = {"first": min(self._ts[n]), "latest": max(self._ts[n])}
        return out


ADAPTERS = {
    "c": DebianPopcon, "cpp": DebianPopcon,
    "rust": CratesIo, "d": Dub, "nim": Nimble,
    "ada": lambda: GitIndexDeps("https://github.com/alire-project/alire-index", "alire", "index"),
    "fortran": FortranLang,
    "chapel": lambda: GitIndexDeps("https://github.com/chapel-lang/mason-registry", "mason", "Bricks"),
    "mojo": Modular, "swift": lambda: EcoAge("swiftpackageindex.com"), "c3": C3Vendor, "fpc": Fppkg,
    "go": GoPkg, "csharp": NuGet, "java": Maven,
    "julia": lambda: EcoStat("juliahub.com", "downloads", "téléchargements du dernier mois (ecosyste.ms, JuliaHub)"),
    "haskell": HackageEco,
    "ocaml": lambda: EcoStat("opam.ocaml.org", "dependents", "dépendants inverses (ecosyste.ms, opam)"),
    "js": Npm, "python": PyPIEco, "lua": LuaRocks, "php": Packagist,
}
NO_REGISTRY = {"zig": "paquets par URL, sans registre", "odin": "aucun gestionnaire (collection vendor livrée)",
               "bqn": "aucun gestionnaire de paquets"}


def rank(cands, st, order):
    if order == "age":
        def key(e):
            s = st.get(e["name"]) or {}
            maint = bool(s.get("latest")) and s["latest"] >= MAINTAINED
            return (0 if maint else 1, s.get("first") or "9999")
        return sorted(cands, key=key)
    return sorted(cands, key=lambda e: -(st.get(e["name"]) or 0))


def survey(lang):
    res = {"langage": lang, "date": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()), "cases": {}}
    if lang in NO_REGISTRY:
        res["registre"] = "aucun : " + NO_REGISTRY[lang]
        for case, val in holes(lang):
            res["cases"][case] = {"note": val, "mots": KEYWORDS[case], "candidates": []}
    else:
        ad = ADAPTERS[lang]()
        res["statistique"] = ad.stat_name
        res["ordre"] = getattr(ad, "order", "stat")
        for case, val in holes(lang):
            found = ad.candidates(KEYWORDS[case])
            st = ad.stat(list(found))
            cands = rank(list(found.values()), st, res["ordre"])
            for e in cands:
                e["stat"] = st.get(e["name"])
            res["cases"][case] = {"note": val, "mots": KEYWORDS[case], "candidates": cands}
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, f"{lang}.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    return res


if __name__ == "__main__":
    langs = sys.argv[1:] or ["all"]
    if langs == ["all"]:
        langs = list(MATRIX)
    for l in langs:
        try:
            r = survey(l)
            print(l, {c: len(v["candidates"]) for c, v in r["cases"].items()}, flush=True)
        except Exception as e:  # noqa: BLE001
            print(l, "ÉCHEC", repr(e)[:300], flush=True)
