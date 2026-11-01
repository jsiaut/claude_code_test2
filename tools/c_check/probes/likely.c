/* Sonde : C23 a-t-il des attributs de probabilité de branche ([[likely]]) ? */
int f(int x) {
    if (x > 0) [[likely]] return 1;
    return 0;
}
int main(void) { return f(1) - 1; }
