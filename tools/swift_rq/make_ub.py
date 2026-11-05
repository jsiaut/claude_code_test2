#!/usr/bin/env python3
"""Remarque sur Swift (docs/SWIFT.md, section 5) : crée bench/swift_ub/ms.swift depuis bench/swift/ms.swift, en
ajoutant deux variantes de sensibilité et rien d'autre (vérifié : le source d'origine est une sous-suite exacte) :
  * k4 natural_w : la boucle naturelle avec l'addition qui enveloppe (&+=) au lieu de += (vérifiée) ;
  * k8 natural_ub : l'arbre en UniqueBox (Swift 6.4, propriété unique, sans comptage de références), avec un
    deinit {} vide, sans lequel l'optimiseur de 6.4.2 épuise la mémoire (sonde : results/swift_check/facts2.txt)."""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src = open(os.path.join(ROOT, "bench", "swift", "ms.swift"), encoding="utf-8").read()
HEAD = "// Copie de sensibilité de bench/swift (remarque sur Swift, docs/SWIFT.md, section 5) : variantes k4 natural_w et\n// k8 natural_ub en plus ; le reste est identique au source publié.\n"
K4_FN = '''@inline(never) func k4NaturalWrapping(_ v: [UInt8]) -> UInt64 {
    var s: UInt64 = 0
    for x in v {
        if x >= 128 { s &+= UInt64(x) }
    }
    return s
}
'''
K4_RUN_OLD = '''        let s = k4Natural(d)
'''
K4_RUN_NEW = '''        let s = v == "natural_w_unsorted" ? k4NaturalWrapping(d) : k4Natural(d)
'''
K8_TYPES = '''/// Variante natural_ub : arbre à propriété unique (UniqueBox, Swift 6.4), sans comptage de références ; le deinit vide
/// évite l'épuisement de mémoire de l'optimiseur de 6.4.2 sur ce type récursif
struct UNode: ~Copyable {
    var v: Int64
    var l: UniqueBox<UNode>?
    var r: UniqueBox<UNode>?
    deinit {}
}
func uBuild(_ d: Int, _ c: inout Int64) -> UniqueBox<UNode> {
    var n = UNode(v: c, l: nil, r: nil)
    c += 1
    if d > 0 {
        n.l = uBuild(d - 1, &c)
        n.r = uBuild(d - 1, &c)
    }
    return UniqueBox(n)
}
func uSum(_ n: borrowing UNode) -> Int64 {
    var s = n.v
    switch n.l { case .some(let b): s += uSum(b.value); case .none: break }
    switch n.r { case .some(let b): s += uSum(b.value); case .none: break }
    return s
}
'''
K8_RUN_OLD = '''            } else {
                let t = tBuild(10, &c)
                s = tSum(t)
            }'''
K8_RUN_NEW = '''            } else if v == "natural_ub" {
                let t = uBuild(10, &c)
                s = uSum(t.value)
            } else {
                let t = tBuild(10, &c)
                s = tSum(t)
            }'''
ANCHOR_K4 = "@inline(never) func k4Branchless("
ANCHOR_K8 = "/// Arène : nœuds compacts dans un tampon réutilisé, enfants par indice\n"
out = src
for old, new in ((ANCHOR_K4, K4_FN + ANCHOR_K4), (K4_RUN_OLD, K4_RUN_NEW), (ANCHOR_K8, K8_TYPES + ANCHOR_K8),
                 (K8_RUN_OLD, K8_RUN_NEW)):
    assert out.count(old) == 1, old[:60]
    out = out.replace(old, new)
out = HEAD + out
# contrôle : en retirant les ajouts, on retrouve le source publié à l'octet près
back = out[len(HEAD):]
for old, new in ((ANCHOR_K4, K4_FN + ANCHOR_K4), (K4_RUN_OLD, K4_RUN_NEW), (ANCHOR_K8, K8_TYPES + ANCHOR_K8),
                 (K8_RUN_OLD, K8_RUN_NEW)):
    back = back.replace(new, old)
assert back == src
dst = os.path.join(ROOT, "bench", "swift_ub")
open(os.path.join(dst, "ms.swift"), "w", encoding="utf-8").write(out)
open(os.path.join(dst, "extra_variants"), "w").write("k4 natural_w_unsorted\nk8 natural_ub\n")
print("bench/swift_ub/ms.swift écrit ; source publié retrouvé à l'octet près")
