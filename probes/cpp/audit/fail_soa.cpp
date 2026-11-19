struct __attribute__((soa)) P { float x, y; };
struct P ps[16];
int main(void) { return (int)ps[0].x; }
