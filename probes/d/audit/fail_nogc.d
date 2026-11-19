@nogc void f() { auto p = new int[10]; p[0] = 1; }
void main() { f(); }
