int f(int x) { if (x > 0) [[likely]] { return 1; } return 2; }
