package ctfe
import "core:fmt"
fib :: proc "contextless" (n: u64) -> u64 { a, b: u64 = 0, 1; for _ in 0 ..< n { a, b = b, a + b }; return a }
F60 :: fib(60)
main :: proc() { fmt.println(F60) }
