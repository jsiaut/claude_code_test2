"""Compare, fonction par fonction, le code machine des noyaux Nim compilés par deux versions (noms normalisés)."""
import re, sys
def funcs(path):
    out, name, body = {}, None, []
    for line in open(path):
        m = re.match(r"^(\w+?)(?:__ms_u\d+|_u\d+__ms):", line)
        if m:
            name, body = m.group(1), []
            continue
        if name and line.startswith(".Lfunc_end"):
            out[name] = body; name = None; continue
        if name and re.match(r"^\s+[a-z]", line):
            ins = line.split("#")[0].strip()
            ins = re.sub(r"\.LBB\d+_\d+", "L", ins)
            ins = re.sub(r"(\w+?)(?:__ms_u\d+|_u\d+__ms)", r"\1", ins)
            ins = re.sub(r"\.LCPI\d+_\d+", "C", ins)
            ins = re.sub(r"\w+__\w+_u\d+|\w+_u\d+__\w+", "SYM", ins)
            body.append(ins)
    return out
a, b = funcs(sys.argv[1]), funcs(sys.argv[2])
kern = sorted(n for n in a if re.match(r"(k\d|q\d|aBuild|aSum|tBuild|tSum)", n) and not n.startswith("k9Init"))
same = [n for n in kern if n in b and a[n] == b[n]]
diff = [n for n in kern if n in b and a[n] != b[n]]
miss = [n for n in kern if n not in b]
print(f"fonctions de noyaux : {len(kern)} ; identiques : {len(same)} ; différentes : {len(diff)} ; absentes : {miss}")
for n in diff:
    print(f"  {n} : {len(a[n])} -> {len(b[n])} instructions")
print("identiques :", ", ".join(same))
