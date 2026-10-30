import std/typedthreads
var shared_data: seq[int] = @[1, 2, 3]
proc worker() {.thread.} =
  shared_data.add 4
var t: Thread[void]
createThread(t, worker)
joinThread(t)
