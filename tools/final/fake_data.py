"""v4, campagne finale : données fictives au format de tools/final/campaign.py, pour essayer analysis/final_v4.py avant
la campagne (docs/V4_FINAL.md, 8). Temps : médianes des points 2 et 4, bruit de 5 % ; deux machines simulées
(passes 0 et 1, passe 2), dont la seconde a un b3 et des temps de K3 1,2 fois plus longs ; K1 naturel de Python à la
grande taille « hors mémoire ».
Usage : fake_data.py <répertoire> ; puis FINAL_RAW=<répertoire>/raw FINAL_OUT=<répertoire>/out UA=200 BOOT=40
python3 analysis/final_v4.py"""
import json, os, sys, glob, random, math, collections, importlib.util
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
OUT = sys.argv[1] if len(sys.argv) > 1 else '/dev/shm/final_fake'
ARGS = list(sys.argv); sys.argv = ['x']
spec = importlib.util.spec_from_file_location("camp", ROOT + "/tools/final/campaign.py")
C = importlib.util.module_from_spec(spec); spec.loader.exec_module(C)
rnd = random.Random(7)
# temps de référence : point 2 (base, trois tailles), point 4 (cv, taille publiée)
base = {}
lat2 = {}
for f in glob.glob(ROOT + '/results/sizes/raw/*.jsonl'):
    for line in open(f):
        r = json.loads(line)
        if r.get('build') != 'new' or not r.get('median'): continue
        base[(r['lang'], r['kernel'], r['size'], r['variant'], r['param'])] = r['median']
        if r['kernel'] == 'k8' and r['variant'] == 'natural' and r.get('lat'):
            lat2[(r['lang'], r['size'])] = r['lat']
cv4 = {}
for f in glob.glob(ROOT + '/results/converge/raw/*.jsonl'):
    for line in open(f):
        r = json.loads(line)
        if r.get('median'): cv4[(r['lang'], r['build'], r['kernel'], r['variant'], r['param'])] = r['median']
fac = {'small': 0.3, 'large': 4.0, 'l2': 1.0, 'l3': 1.2, 'pub': 1.0}
def t0(l, cons, k, s, v, q):
    if (l, k, s, v, q) in base and cons in ('pub', 'chk', 'unc'):
        return base[(l, k, s, v, q)] * (1.1 if cons == 'chk' else 1.0)
    for b in ('cv', 'pub'):
        if (l, b, k, v, q) in cv4: return cv4[(l, b, k, v, q)] * fac[s]
    return 0.01 * fac[s]
os.makedirs(OUT + '/raw', exist_ok=True)
for f in glob.glob(OUT + '/raw/*'): os.remove(f)
recs = collections.defaultdict(list)
boots = {0: 'boot-A', 1: 'boot-A', 2: 'boot-B'}
mach = {0: '34', 1: '34', 2: '35'}
for p in (0, 1, 2):
    for k, s in C.pass_order(p, None):
        for l, cons, j in C.blocks_of(C.LANGS, k, s, p):
            for v, q in C.cells(l, cons, k):
                if j >= C.copies(k, v, p): continue
                m = t0(l, cons, k, s, v, q) * math.exp(rnd.gauss(0, 0.05))
                if k == 'k3': m *= (1.2 if p == 2 else 1.0)  # machine B plus lente : b3 aussi
                rec = {'lang': l, 'construction': cons, 'kernel': k, 'size': s, 'variant': v, 'param': q, 'reps': [],
                       'n': 5, 'oks': ['True'], 'median': m, 'returncode': 0, 'oom': False, 'timeout': False,
                       'steal_frac': 0.01, 'pass': p, 'copy': j, 'machine': mach[p], 'boot_id': boots[p],
                       'cpu_model': '6/207/2 Intel(R) Xeon(R) Processor @ 2.10GHz', 'lat': []}
                if k == 'k8' and v == 'natural':
                    rec['lat'] = lat2.get((l, s)) or lat2.get((l, 'pub')) or [[1000, 1000, 1000, 2000, 3000]] * 10
                if l == 'python' and cons == 'pub' and k == 'k1' and s == 'large' and v.startswith('natural'):
                    keep = ('lang', 'construction', 'kernel', 'size', 'variant', 'param', 'pass', 'copy', 'machine',
                            'boot_id', 'cpu_model')
                    rec = {k_: rec[k_] for k_ in keep} | {'skipped': 'oom', 'reps': [], 'n': 0}
                recs[l].append(rec)
for l, rs in recs.items():
    with open(f'{OUT}/raw/{l}.jsonl', 'w') as g:
        for r in rs: g.write(json.dumps(r) + '\n')
with open(OUT + '/b3.jsonl', 'w') as g:
    for p in (0, 1, 2):
        for lab in ('avant le groupe K3', 'après le groupe K3'):
            b = 70.0 * (1.2 if p == 2 else 1.0)
            g.write(json.dumps({'label': lab, 'pass': p, 'machine': mach[p], 'boot_id': boots[p], 'b3_ms': b,
                                'medians_ms': [b, b]}) + '\n')
print(sum(len(v) for v in recs.values()), 'enregistrements fictifs')
