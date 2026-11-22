// v4, point 6 (docs/V4_OPEN.md, 4) : sondes de la grille ouverte de D (A6 : soa 0.2.0 ; F1 : mir-algorithm 3.22.5).
import std.stdio : writefln;
import soa;
import mir.ndslice;

struct P { float vx; float vy; float vz; float m; }

void a6()
{
    SOA!P s;
    foreach (i; 0 .. 1000)
        s ~= P(i, 2 * i, 3 * i, 1);
    // énergie par les champs (tableaux séparés) et par les éléments (objet de dispatch)
    double e1 = 0, e2 = 0;
    foreach (i; 0 .. s.length)
        e1 += 0.5 * s.m[i] * (s.vx[i] * s.vx[i] + s.vy[i] * s.vy[i] + s.vz[i] * s.vz[i]);
    foreach (p; s[])
        e2 += 0.5 * p.m * (p.vx * p.vx + p.vy * p.vy + p.vz * p.vz);
    auto dx = cast(size_t)&s.vx[1] - cast(size_t)&s.vx[0];
    auto dm = cast(long)(cast(size_t)&s.m[0]) - cast(long)(cast(size_t)&s.vx[0]);
    writefln("RESULT;A6;soa;SOA!P (4 champs float) : %d éléments par ~= ; écart entre vx[0] et vx[1] = %d octets "
        ~ "(sizeof P = %d) ; m[0] dans un autre tableau, à %d octets de vx[0] ; énergie par les champs = %.1f, "
        ~ "par l'itération des éléments = %.1f ; s[1].vy = %.1f", s.length, dx, P.sizeof, dm, e1, e2, s[1].vy);
}

void f1()
{
    size_t m = 300, n = 500;
    auto t = slice!double(m, n);
    t[] = 0;
    t[2, 3] = 7;
    auto off = (cast(size_t)&t[2, 3] - cast(size_t)&t[0, 0]) / double.sizeof;
    writefln("RESULT;F1;mir-algorithm;slice!double(%d, %d) de dimensions connues à l'exécution : shape %s, strides %s, "
        ~ "t.field.length = %d (tampon contigu), t[2, 3] = %.0f à l'indice %d (2*%d+3)",
        m, n, t.shape, t.strides, t.field.length, t[2, 3], off, n);
}

void main()
{
    a6();
    f1();
}
