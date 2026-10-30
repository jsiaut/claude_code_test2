import std/[atomics, typedthreads, cpuinfo]

var flag: Atomic[int]
var data: int

proc consumer() {.thread.} =
  while flag.load(moRelaxed) == 0: cpuRelax()
  fence(moAcquire)
  echo "thread saw ", data

proc slowPath(x: int): int {.noinline.} = x * 3

type Padded = object
  a {.align(64).}: int
  b {.align(64).}: int

proc main() =
  let x = 5
  if likely(x > 0): echo "likely ok" else: echo slowPath(x)
  var t: Thread[void]
  createThread(t, consumer)
  pinToCpu(t, 0)
  data = 42
  fence(moRelease)
  flag.store(1, moRelaxed)
  joinThread(t)
  echo "cpus=", countProcessors(), " sizeof(Padded)=", sizeof(Padded)
main()
