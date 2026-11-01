// Sonde réflexion C++26 (P2996), syntaxe seule, sans en-tête : l'opérateur ^^ est-il reconnu ?
struct P { int a; };
constexpr auto r = ^^P;
int main() {}
