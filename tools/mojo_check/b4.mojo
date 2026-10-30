# Sonde B4 (allocations cachées) : erreurs levées et tâches asynchrones, comptées par malloc_count.so.
# Usage : b4 <lit|fmt|task|none> <N>
from std.sys import argv
from std.runtime._asyncrt import create_task
from std.benchmark import black_box

@inline(.never)
def fail_lit(i: Int) raises -> Int:
    if black_box(i) >= 0:
        raise Error("échec")
    return i

@inline(.never)
def fail_fmt(i: Int) raises -> Int:
    if black_box(i) >= 0:
        raise Error("échec numéro ", i, " dans la boucle de la sonde")
    return i

__async def work(i: Int) -> Int:
    return i + 1

def main() raises:
    var mode = String(argv()[1])
    var n = Int(String(argv()[2]))
    var s = 0
    for i in range(n):
        if mode == "lit":
            try:
                s += fail_lit(i)
            except e:
                s += 1
        elif mode == "fmt":
            try:
                s += fail_fmt(i)
            except e:
                s += 1
        elif mode == "task":
            var t = create_task(work(i))
            s += t.wait()
        else:
            s += black_box(i)
    print(mode, n, s)
