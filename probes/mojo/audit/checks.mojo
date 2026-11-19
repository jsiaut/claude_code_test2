# E6 : List[i] (assertions actives par défaut) contre unsafe_get et pointeur.
from std.collections import List
from std.sys import argv

@no_inline
def idx_checked(ref l: List[Float32], i: Int) -> Float32:
    return l[i]

@no_inline
def idx_unchecked(ref l: List[Float32], i: Int) -> Float32:
    return l.unsafe_get(i)

def main():
    var l = List[Float32](capacity=8)
    for i in range(8):
        l.append(Float32(i))
    print(idx_checked(l, len(argv())), idx_unchecked(l, len(argv())))
