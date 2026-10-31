// D5 / C2 : _mm_pause s'importe-t-il ?
require "immintrin.h";
extern proc _mm_pause();
proc main() { _mm_pause(); writeln("pause exécutée"); }
