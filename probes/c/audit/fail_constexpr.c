static int fib(int n) { return n < 2 ? n : fib(n - 1) + fib(n - 2); }
constexpr int F = fib(20);
int main(void) { return F; }
