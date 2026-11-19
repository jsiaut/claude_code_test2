# Noms publics des modules de la bibliothèque standard écrits en C (intégrés à l'interpréteur ou dans lib-dynload),
# un par ligne, avec les membres de leurs classes ; complète la fouille des sources .py (tools/grid_audit/search.py).
import importlib, os, sys, sysconfig
dyn = os.path.join(sysconfig.get_paths()['stdlib'], 'lib-dynload')
names = set(sys.builtin_module_names)
for f in os.listdir(dyn) if os.path.isdir(dyn) else []:
    if f.endswith('.so'):
        names.add(f.split('.')[0])
skip = {'_tkinter', 'antigravity', 'this'}
names = {m for m in names if not m.startswith('_test') and not m.startswith('xx')}   # modules de test de CPython, pas l'API
out = set()
for m in sorted(names - skip):
    try:
        mod = importlib.import_module(m)
    except Exception:
        continue
    for k in dir(mod):
        if k.startswith('__'):
            continue
        out.add(f'{m}.{k}')
        v = getattr(mod, k, None)
        if isinstance(v, type):
            for a in dir(v):
                if not a.startswith('__'):
                    out.add(f'{m}.{k}.{a}')
print('\n'.join(sorted(out)))
