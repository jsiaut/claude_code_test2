# E3 : likely/unlikely sous les deux compilateurs C (clang 23, celui du banc ; gcc 16, celui de Nim par défaut).
proc ext(x: uint64) {.importc: "ext_hook", nodecl.}
{.emit: """__attribute__((noinline)) void ext_hook(unsigned long long x) { __asm__ volatile("" :: "r"(x)); }""".}
proc h_lik(x: uint64): uint64 {.exportc: "h_lik", noinline.} =
  var r = x
  if likely(x == 7):
    ext(x)
    r = x * 5
  r + 1
proc h_unl(x: uint64): uint64 {.exportc: "h_unl", noinline.} =
  var r = x
  if unlikely(x == 8):
    ext(x)
    r = x * 6
  r + 2
proc h_non(x: uint64): uint64 {.exportc: "h_non", noinline.} =
  var r = x
  if x == 9:
    ext(x)
    r = x * 7
  r + 3
echo h_lik(1) + h_unl(1) + h_non(1)
