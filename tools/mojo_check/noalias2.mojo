# Sonde E5, second essai : transfert d'une écriture à une lecture à travers une écriture par un autre pointeur.
from std.memory.alloc import unsafe_alloc

@inline(.never)
def fwd_plain(a: Pointer[Int64, MutUntrackedOrigin], b: Pointer[Int64, MutUntrackedOrigin]) -> Int64:
    a[unsafe_offset=0] = 1
    b[unsafe_offset=0] = 2
    return a[unsafe_offset=0]

@inline(.never)
def fwd_noalias(a0: Pointer[Int64, MutUntrackedOrigin], b0: Pointer[Int64, MutUntrackedOrigin]) -> Int64:
    var a = a0.unsafe_as_noalias()
    var b = b0.unsafe_as_noalias()
    a[unsafe_offset=0] = 1
    b[unsafe_offset=0] = 2
    return a[unsafe_offset=0]

def main():
    var a = unsafe_alloc[Int64](1)
    var b = unsafe_alloc[Int64](1)
    print(fwd_plain(a, b), fwd_noalias(a, b))
