// Sonde réflexion C++26 (P2996) : nombre de membres non statiques d'une structure, à la compilation.
#include <meta>
struct P { float x, y, z, m; };
consteval int nmem() { return std::meta::nonstatic_data_members_of(^^P, std::meta::access_context::unchecked()).size(); }
static_assert(nmem() == 4);
int main() { return nmem(); }
