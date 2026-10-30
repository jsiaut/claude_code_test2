import std.concurrency;
void worker(int[] a) { a[0] = 1; }
void main() { int[] a = [0]; spawn(&worker, a); }
