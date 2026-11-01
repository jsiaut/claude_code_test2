"""Boucles d'une fonction dans un .s (AT&T) : taille, vidages sur la pile, popcounts."""
import os, re, sys
def func(path, name):
    L, on = [], False
    for line in open(path):
        if re.match(r"^\S*%s\S*:(\s|$)" % name, line) and not line.startswith("."):
            on = True; L = []; continue
        if on:
            if ".cfi_endproc" in line:
                break
            L.append(line.rstrip("\n"))
    return L
def loops(L):
    labels = {}
    for k, l in enumerate(L):
        m = re.match(r"^(\.\w+):", l)
        if m: labels[m.group(1)] = k
    out = []
    for k, l in enumerate(L):
        m = re.match(r"^\s+j\w+\s+(\.\w+)", l)
        if m and m.group(1) in labels and labels[m.group(1)] < k:
            body = [x for x in L[labels[m.group(1)]:k + 1] if re.match(r"^\s+[a-z]", x)]
            out.append((m.group(1), len(body),
                        sum(1 for x in body if re.search(r"^\s+v?mov\S*\s+%[xyz]?mm\d+,\s*-?\d*\(%rsp\)|^\s+v?mov\S*\s+%[xyz]?mm\d+,\s*-?\d+\(%rsp\)|^\s+k?mov\S*\s+%\w+,\s*-?\d*\(%rsp\)", x)),
                        sum(1 for x in body if re.search(r"\(%rsp\)", x)),
                        sum(1 for x in body if re.search(r"\bpopcnt", x)),
                        sum(1 for x in body if re.search(r"vpopcnt", x)),
                        sum(1 for x in body if re.search(r"vpshufb", x))))
    return out
for path in sys.argv[2:]:
    L = func(path, sys.argv[1])
    print(os.path.basename(path), "instructions dans la fonction :", sum(1 for x in L if re.match(r"^\s+[a-z]", x)))
    for lab, n, sp, rsp, pc, vpc, shuf in sorted(loops(L), key=lambda t: -t[1])[:3]:
        print(f"   boucle {lab}: {n} instr., écritures pile {sp}, accès pile {rsp}, popcnt {pc}, vpopcnt {vpc}, vpshufb {shuf}")
