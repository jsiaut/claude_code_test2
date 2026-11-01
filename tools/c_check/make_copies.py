#!/usr/bin/env python3
"""Remarque sur C (docs/C.md, section 3) : copies du banc C pour K8 tuned, par remplacements exacts (chaque motif
doit apparaître une seule fois) à partir de la source de la campagne (bench/c/ms.c), et leurs scripts.

Même algorithme que le banc (arbre complet de profondeur 10 construit en ordre préfixe dans l'arène, valeur du nœud =
numéro de la requête + numéro du nœud en ordre préfixe, puis parcours en profondeur qui somme les valeurs) ; même
arène, mêmes valeurs, même somme de contrôle. Seule change l'écriture :
* c_k8val   : construction récursive à un seul état passé par valeur (l'indice du nœud ; v = q + indice), qui rend
              l'indice suivant, au lieu de deux compteurs passés par pointeur (int32_t *top, int64_t *counter) ;
* c_k8it    : construction et somme itératives, piles explicites ;
* c_gcc_ref, c_gcc_k8val, c_gcc_k8it : les mêmes sources (campagne, c_k8val, c_k8it) compilées par gcc 16 avec les
              options de l'annexe c_gcc ; c_ref (clang 23, source de la campagne) vient de la remarque sur C++."""
import os, stat

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CLANG = "clang-23 -std=c23 -O3 -march=native -Wall -Wextra -pthread"
GCC = "/opt/gcc-16/bin/gcc-16 -std=c23 -O3 -march=native -pthread"

OLD_BUILD = """static int32_t a8_build(ANode *a, int32_t *top, int depth, int64_t *counter) {
    int32_t i = (*top)++;
    a[i].v = (*counter)++;
    if (depth > 0) { int32_t l = a8_build(a, top, depth - 1, counter); a[i].l = l; a[i].r = a8_build(a, top, depth - 1, counter); }
    else a[i].l = a[i].r = -1;
    return i;
}
static int64_t a8_sum(const ANode *a, int32_t i) { return i < 0 ? 0 : a[i].v + a8_sum(a, a[i].l) + a8_sum(a, a[i].r); }
"""
OLD_CALL = "if (tuned) { int32_t top = 0; int32_t root = a8_build(arena, &top, D, &c); s = a8_sum(arena, root); }"

VAL_BUILD = """// copie c_k8val (remarque sur C) : un seul état passé par valeur, l'indice du nœud en ordre préfixe (v = q + indice) ;
// la fonction rend l'indice libre suivant. Même arène et mêmes valeurs que a8_build du banc.
static int32_t a8_build(ANode *a, int32_t i, int depth, int64_t q) {
    a[i].v = q + i;
    if (depth > 0) {
        int32_t l = i + 1, r = a8_build(a, l, depth - 1, q);
        a[i].l = l;
        a[i].r = r;
        return a8_build(a, r, depth - 1, q);
    }
    a[i].l = a[i].r = -1;
    return i + 1;
}
static int64_t a8_sum(const ANode *a, int32_t i) { return i < 0 ? 0 : a[i].v + a8_sum(a, a[i].l) + a8_sum(a, a[i].r); }
"""
VAL_CALL = "if (tuned) { a8_build(arena, 0, D, c); s = a8_sum(arena, 0); }"

IT_BUILD = """// copie c_k8it (remarque sur C) : construction et somme itératives, piles explicites. La construction descend à gauche
// en empilant le sous-arbre droit de chaque nœud interne, puis le reprend à la feuille suivante : même ordre préfixe,
// même arène et mêmes valeurs que a8_build et a8_sum du banc.
static int32_t a8_build(ANode *a, int depth, int64_t q) {
    struct { int32_t parent, depth; } stk[64];
    int sp = 0;
    int32_t top = 0, parent = -1;
    int right = 0, d = depth;
    for (;;) {
        int32_t i = top++;
        a[i].v = q + i;
        if (parent >= 0) {
            if (right) a[parent].r = i;
            else a[parent].l = i;
        }
        if (d > 0) {
            stk[sp].parent = i; stk[sp].depth = d - 1; sp++;
            parent = i; right = 0; d = d - 1;
        } else {
            a[i].l = a[i].r = -1;
            if (!sp) break;
            sp--;
            parent = stk[sp].parent; d = stk[sp].depth; right = 1;
        }
    }
    return 0;
}
static int64_t a8_sum(const ANode *a, int32_t root) {
    int32_t stk[64];
    int sp = 0;
    int64_t s = 0;
    stk[sp++] = root;
    while (sp) {
        int32_t i = stk[--sp];
        s += a[i].v;
        if (a[i].l >= 0) { stk[sp++] = a[i].r; stk[sp++] = a[i].l; }
    }
    return s;
}
"""
IT_CALL = "if (tuned) { int32_t root = a8_build(arena, D, c); s = a8_sum(arena, root); }"


def sub(s, old, new):
    assert s.count(old) == 1, f"motif absent ou multiple : {old[:80]!r}"
    return s.replace(old, new)


def write(path, text, exe=False):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").write(text)
    if exe:
        os.chmod(path, os.stat(path).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def impl(name, comment, cmd, source=None):
    d = os.path.join(ROOT, "bench", name)
    if source is not None:
        write(os.path.join(d, "ms.c"), source)
    write(os.path.join(d, "build.sh"), f"#!/bin/sh\n# {comment}\nset -e\ncd \"$(dirname \"$0\")\"\n{cmd}\n", exe=True)
    write(os.path.join(d, "run"), "#!/bin/sh\nexec \"$(dirname \"$0\")/ms\" \"$@\"\n", exe=True)


def main():
    c = open(os.path.join(ROOT, "bench", "c", "ms.c")).read()
    val = sub(sub(c, OLD_BUILD, VAL_BUILD), OLD_CALL, VAL_CALL)
    it = sub(sub(c, OLD_BUILD, IT_BUILD), OLD_CALL, IT_CALL)
    impl("c_k8val", "Remarque sur C : arène de K8 construite par une récursion à un seul état passé par valeur, clang 23",
         f"{CLANG} -o ms ms.c", val)
    impl("c_k8it", "Remarque sur C : arène de K8 construite et sommée par itération (piles explicites), clang 23",
         f"{CLANG} -o ms ms.c", it)
    impl("c_gcc_ref", "Remarque sur C : source C de la campagne, gcc 16, options de l'annexe c_gcc",
         f"{GCC} -o ms ../c/ms.c")
    impl("c_gcc_k8val", "Remarque sur C : source de c_k8val, gcc 16", f"{GCC} -o ms ../c_k8val/ms.c")
    impl("c_gcc_k8it", "Remarque sur C : source de c_k8it, gcc 16", f"{GCC} -o ms ../c_k8it/ms.c")
    print("copies écrites : c_k8val, c_k8it, c_gcc_ref, c_gcc_k8val, c_gcc_k8it")


if __name__ == "__main__":
    main()
