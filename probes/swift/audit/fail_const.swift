func fib(_ n: Int) -> Int { n < 2 ? n : fib(n - 1) + fib(n - 2) }
@const let f20 = fib(20)
print(f20)
