#!/usr/bin/env python3
"""Remarque sur C++ (docs/CPP.md, section 3) : génère les copies du banc par remplacements exacts (chaque motif doit
apparaître une seule fois), à partir des sources de la campagne (bench/cpp/ms.cpp, bench/c/ms.c), et leurs scripts.

* cpp_ref   : bench/cpp/ms.cpp tel quel, g++ 16 et les options du banc (référence des rapports appariés) ;
* cpp_intr  : les quatre noyaux en std::simd (K1 soa, K5 tuned, Q6 tuned, Q1 tuned) remplacés par la forme de C
              (intrinsèques AVX-512 de bench/c/ms.c ; Q6 en boucle sans branchement vectorisée par le compilateur), g++ 16 ;
* cpp_clang : la source de cpp_intr compilée par clang++ 23 (libstdc++ de GCC 16 ; std::simd n'y est pas disponible) ;
* cpp_k9    : grilles de K9 allouées une seule fois et réinitialisées à chaque répétition (hors chrono), comme C ;
* cpp_k8    : arène de K8 tuned passée par pointeur brut (ANode*) au lieu de std::vector<ANode>&, comme C ;
* cpp_all   : cpp_intr + cpp_k9 + cpp_k8, compilée par clang++ 23 (les corrections 1 à 4 de la remarque ensemble) ;
* c_ref     : bench/c/ms.c tel quel, clang 23 et les options du banc ;
* c_k9      : bench/c/ms.c, grilles de K9 réallouées à chaque répétition (la pratique de la plupart des langages)."""
import os, stat

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GXX = "/opt/gcc-16/bin/g++-16 -std=c++26 -O3 -march=native -pthread -Wall -Wno-interference-size"
CLANGXX = "clang++-23 -std=c++26 -O3 -march=native -pthread -Wall --gcc-toolchain=/opt/gcc-16"
CLANG = "clang-23 -std=c23 -O3 -march=native -Wall -Wextra -pthread"


def sub(s, old, new):
    assert s.count(old) == 1, f"motif absent ou multiple : {old[:80]!r}"
    return s.replace(old, new)


def block(s, start, end):
    """Bloc de s qui commence par start et se termine par end (inclus), unique."""
    assert s.count(start) == 1, start[:80]
    i = s.index(start)
    j = s.index(end, i) + len(end)
    return s[i:j]


INTR_K1 = """// SoA optimisé (copie cpp_intr) : la forme de C, AVX-512 explicite, f32 -> f64 pour l'accumulation
[[gnu::noinline]] static double k1_soa(const float *__restrict vx, const float *__restrict vy, const float *__restrict vz,
                                       const float *__restrict m, size_t n) {
    __m512d a0 = _mm512_setzero_pd(), a1 = a0, a2 = a0, a3 = a0;
    const __m512 h = _mm512_set1_ps(0.5f);
    for (size_t i = 0; i < n; i += 32) {
        for (int u = 0; u < 2; u++) {
            size_t j = i + 16 * (size_t)u;
            __m512 x = _mm512_load_ps(vx + j), y = _mm512_load_ps(vy + j), z = _mm512_load_ps(vz + j), w = _mm512_load_ps(m + j);
            __m512 v2 = _mm512_fmadd_ps(z, z, _mm512_fmadd_ps(y, y, _mm512_mul_ps(x, x)));
            __m512 e = _mm512_mul_ps(_mm512_mul_ps(h, w), v2);
            __m512d lo = _mm512_cvtps_pd(_mm512_castps512_ps256(e));
            __m512d hi = _mm512_cvtps_pd(_mm256_castpd_ps(_mm512_extractf64x4_pd(_mm512_castps_pd(e), 1)));
            if (u == 0) { a0 = _mm512_add_pd(a0, lo); a1 = _mm512_add_pd(a1, hi); }
            else { a2 = _mm512_add_pd(a2, lo); a3 = _mm512_add_pd(a3, hi); }
        }
    }
    return _mm512_reduce_add_pd(_mm512_add_pd(_mm512_add_pd(a0, a1), _mm512_add_pd(a2, a3)));
}
"""
INTR_K5 = """// K5 optimisé (copie cpp_intr) : la forme de C, 4 accumulateurs AVX-512, FMA
[[gnu::noinline]] static float k5_tuned(const float *__restrict a, const float *__restrict b, int n) {
    __m512 s0 = _mm512_setzero_ps(), s1 = s0, s2 = s0, s3 = s0;
    for (int i = 0; i < n; i += 64) {
        s0 = _mm512_fmadd_ps(_mm512_load_ps(a + i), _mm512_load_ps(b + i), s0);
        s1 = _mm512_fmadd_ps(_mm512_load_ps(a + i + 16), _mm512_load_ps(b + i + 16), s1);
        s2 = _mm512_fmadd_ps(_mm512_load_ps(a + i + 32), _mm512_load_ps(b + i + 32), s2);
        s3 = _mm512_fmadd_ps(_mm512_load_ps(a + i + 48), _mm512_load_ps(b + i + 48), s3);
    }
    return _mm512_reduce_add_ps(_mm512_add_ps(_mm512_add_ps(s0, s1), _mm512_add_ps(s2, s3)));
}
"""
INTR_Q6 = """// Q6 optimisé (copie cpp_intr) : la forme de C, prédicat sans branchement vectorisé par le compilateur
[[gnu::noinline]] static int64_t q6_tuned_k(const int32_t *__restrict sd, const uint8_t *__restrict d, const uint8_t *__restrict q,
                                           const int32_t *__restrict pr, size_t lo, size_t hi) {
    int64_t s = 0;
    for (size_t i = lo; i < hi; i++) {
        uint32_t m = ((uint32_t)(sd[i] - 8766) < 365u) & ((uint8_t)(d[i] - 5) <= 2) & (q[i] < 24);
        s += (int64_t)(pr[i] * (int32_t)d[i]) & -(int64_t)m;
    }
    return s;
}
static int64_t q6_tuned(const Cols &c, size_t lo, size_t hi) { return q6_tuned_k(c.sd.data(), c.d.data(), c.q.data(), c.pr.data(), lo, hi); }
"""
INTR_Q1 = """// Q1 optimisé (copie cpp_intr) : la forme de C, AVX-512 explicite, 16 lignes par itération, agrégation masquée par
// groupe, accumulateurs 32 bits vidés tous les 4096 lignes, produits 64 bits pairs/impairs (vpmuldq) pour la charge.
[[gnu::noinline]] static void q1_tuned(const Cols &c, size_t lo, size_t hi, Q1Acc &acc) {
    const int32_t *sd = c.sd.data(), *pr = c.pr.data();
    const uint8_t *rf = c.rf.data(), *ls = c.ls.data(), *qq = c.q.data(), *dd = c.d.data(), *tt = c.t.data();
    const __m512i lim = _mm512_set1_epi32(10471), c100 = _mm512_set1_epi32(100);
    size_t i = lo;
    while (i + 16 <= hi) {
        __m512i aq[6], ap[6], adp[6], ace[6], aco[6];
        int64_t cnt[6] = {0};
        for (int g = 0; g < 6; g++) aq[g] = ap[g] = adp[g] = ace[g] = aco[g] = _mm512_setzero_si512();
        size_t end = i + 4096 <= hi ? i + 4096 : hi - (hi - i) % 16;
        for (; i < end; i += 16) {
            __mmask16 pass = _mm512_cmple_epi32_mask(_mm512_loadu_si512(sd + i), lim);
            __m512i vg = _mm512_add_epi32(_mm512_slli_epi32(_mm512_cvtepu8_epi32(_mm_loadu_si128((const __m128i *)(rf + i))), 1),
                                          _mm512_cvtepu8_epi32(_mm_loadu_si128((const __m128i *)(ls + i))));
            __m512i vq = _mm512_cvtepu8_epi32(_mm_loadu_si128((const __m128i *)(qq + i)));
            __m512i vd = _mm512_cvtepu8_epi32(_mm_loadu_si128((const __m128i *)(dd + i)));
            __m512i vt = _mm512_add_epi32(_mm512_cvtepu8_epi32(_mm_loadu_si128((const __m128i *)(tt + i))), c100);
            __m512i vp = _mm512_loadu_si512(pr + i);
            __m512i vdp = _mm512_mullo_epi32(vp, _mm512_sub_epi32(c100, vd));
            __m512i che = _mm512_mul_epi32(vdp, vt);                                              // lignes paires
            __m512i cho = _mm512_mul_epi32(_mm512_srli_epi64(vdp, 32), _mm512_srli_epi64(vt, 32));  // lignes impaires
            for (int g = 0; g < 6; g++) {
                __mmask16 m = _mm512_mask_cmpeq_epi32_mask(pass, vg, _mm512_set1_epi32(g));
                cnt[g] += __builtin_popcount(m);
                aq[g] = _mm512_mask_add_epi32(aq[g], m, aq[g], vq);
                ap[g] = _mm512_mask_add_epi32(ap[g], m, ap[g], vp);
                adp[g] = _mm512_mask_add_epi32(adp[g], m, adp[g], vdp);
                ace[g] = _mm512_mask_add_epi64(ace[g], (__mmask8)_pext_u32(m, 0x5555), ace[g], che);
                aco[g] = _mm512_mask_add_epi64(aco[g], (__mmask8)_pext_u32(m, 0xAAAA), aco[g], cho);
            }
        }
        for (int g = 0; g < 6; g++) {
            acc[g][0] += cnt[g];
            acc[g][1] += _mm512_reduce_add_epi32(aq[g]);
            acc[g][2] += _mm512_reduce_add_epi32(ap[g]);
            acc[g][3] += (int64_t)_mm512_reduce_add_epi64(_mm512_add_epi64(_mm512_cvtepi32_epi64(_mm512_castsi512_si256(adp[g])),
                                                                           _mm512_cvtepi32_epi64(_mm512_extracti64x4_epi64(adp[g], 1))));
            acc[g][4] += _mm512_reduce_add_epi64(_mm512_add_epi64(ace[g], aco[g]));
        }
    }
    if (i < hi) q1_natural(c, i, hi, acc);  // reste éventuel (< 16 lignes)
}
"""
K9_ONCE = """static void run_k9(std::string_view v, int reps) {
    // copie cpp_k9 : grilles allouées une seule fois, réinitialisées à chaque répétition (hors chrono), comme C
    std::vector<std::vector<double>> na, nb;
    avec<double> fa, fb;
    if (v == "natural") { na.assign(M9, std::vector<double>(M9)); nb = na; }
    else { fa.resize((size_t)M9 * M9); fb.resize((size_t)M9 * M9); }
    for (int r = -warmup_count(); r < reps; r++) {
        double s = 0, t0, t1;
        if (v == "natural") {
            for (int i = 0; i < M9; i++) for (int j = 0; j < M9; j++) na[i][j] = k9_init(i, j);
            for (int i = 0; i < M9; i++) std::copy(na[i].begin(), na[i].end(), nb[i].begin());
            auto &a = na;
            auto &b = nb;
            t0 = now();
            for (int it = 0; it < IT9; it++) { k9_natural(a, b); std::swap(a, b); }
            t1 = now();
            for (const auto &row : a) for (double x : row) s += x;
        } else {
            for (int i = 0; i < M9; i++) for (int j = 0; j < M9; j++) fa[(size_t)i * M9 + j] = k9_init(i, j);
            std::copy(fa.begin(), fa.end(), fb.begin());
            double *in = fa.data(), *out = fb.data();
            t0 = now();
            for (int it = 0; it < IT9; it++) {
                if (v == "tuned") k9_rows(in, out, 1, M9 - 1);
                else {
                    std::array<std::jthread, 4> th;
                    for (int t = 0; t < 4; t++) th[t] = std::jthread(k9_rows, in, out, 1 + (M9 - 2) * t / 4, 1 + (M9 - 2) * (t + 1) / 4);
                }
                std::swap(in, out);
            }
            t1 = now();
            for (size_t k = 0; k < (size_t)M9 * M9; k++) s += in[k];
        }
        if (r >= 0) result("k9", v, "2048^2x4", r, t1 - t0, fmt("%.15e", s));
    }
}
"""
K8_OLD_BUILD = """static int32_t a8_build(std::vector<ANode> &a, int32_t &top, int depth, int64_t &counter) {"""
K8_NEW_BUILD = """// copie cpp_k8 : arène passée par pointeur brut, comme C
static int32_t a8_build(ANode *a, int32_t &top, int depth, int64_t &counter) {"""
K8_OLD_SUM = """static int64_t a8_sum(const std::vector<ANode> &a, int32_t i) {"""
K8_NEW_SUM = """static int64_t a8_sum(const ANode *a, int32_t i) {"""
K8_OLD_CALL = """int32_t root = a8_build(arena, top, D, c); s = a8_sum(arena, root);"""
K8_NEW_CALL = """int32_t root = a8_build(arena.data(), top, D, c); s = a8_sum(arena.data(), root);"""


def patch_intr(s):
    s = sub(s, "#include <simd>\n", "#include <immintrin.h>\n")
    s = sub(s, "namespace ss = std::simd;\n", "")
    s = sub(s, "// Implémentation C++26 (GCC 16 / libstdc++) des noyaux de docs/SPEC.md.\n",
            "// Implémentation C++26 (GCC 16 / libstdc++) des noyaux de docs/SPEC.md.\n"
            "// Copie de la remarque sur C++ (docs/CPP.md) : K1 soa, K5 tuned, Q6 tuned et Q1 tuned prennent la forme de C\n"
            "// (intrinsèques AVX-512, Q6 sans branchement), pour compiler aussi avec clang++ 23 (sans std::simd).\n")
    s = s.replace(block(s, "// SoA optimisé : std::simd (16 × f32)", "    return ss::reduce((a0 + a1) + (a2 + a3));\n}\n"), INTR_K1)
    s = s.replace(block(s, "// std::simd : 4 accumulateurs de 16 f32", "    return ss::reduce((s0 + s1) + (s2 + s3));\n}\n"), INTR_K5)
    s = s.replace(block(s, "using I16 = ss::vec<int32_t, 16>;\n", "    return s + q6_natural(c, i, hi);\n}\n"), INTR_Q6)
    s = s.replace(block(s, "// Q1 std::simd : 16 lignes par pas", "    if (i < hi) q1_natural(c, i, hi, acc);\n}\n"), INTR_Q1)
    assert "ss::" not in s
    return s


def patch_k9(s):
    return s.replace(block(s, "static void run_k9(std::string_view v, int reps) {\n",
                           '        if (r >= 0) result("k9", v, "2048^2x4", r, t1 - t0, fmt("%.15e", s));\n    }\n}\n'), K9_ONCE)


def patch_k8(s):
    s = sub(s, K8_OLD_BUILD, K8_NEW_BUILD)
    s = sub(s, K8_OLD_SUM, K8_NEW_SUM)
    return sub(s, K8_OLD_CALL, K8_NEW_CALL)


def patch_c_k9(s):
    s = sub(s, """    double *a = aligned_alloc(64, n * 8), *b = aligned_alloc(64, n * 8);
    char chk[64];
    for (int r = -warmup_count(); r < reps; r++) {
        k9_init(a);""", """    char chk[64];
    for (int r = -warmup_count(); r < reps; r++) {
        double *a = aligned_alloc(64, n * 8), *b = aligned_alloc(64, n * 8);  // copie c_k9 : grilles réallouées à chaque répétition
        k9_init(a);""")
    return sub(s, """        if (r >= 0) result("k9", variant, "2048^2x4", r, t1 - t0, chk);
    }""", """        if (r >= 0) result("k9", variant, "2048^2x4", r, t1 - t0, chk);
        free(a); free(b);
    }""")


def write(path, text, exe=False):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").write(text)
    if exe:
        os.chmod(path, os.stat(path).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def impl(name, comment, cmd, source=None, extra=True):
    d = os.path.join(ROOT, "bench", name)
    if source is not None:
        write(os.path.join(d, "ms.cpp" if not name.startswith("c_") else "ms.c"), source)
    write(os.path.join(d, "build.sh"), f"#!/bin/sh\n# {comment}\nset -e\ncd \"$(dirname \"$0\")\"\n{cmd}\n", exe=True)
    write(os.path.join(d, "run"), "#!/bin/sh\nexec \"$(dirname \"$0\")/ms\" \"$@\"\n", exe=True)
    if extra:
        write(os.path.join(d, "extra_variants"), "k8 tuned_alloc\n")


def main():
    cpp = open(os.path.join(ROOT, "bench", "cpp", "ms.cpp")).read()
    c = open(os.path.join(ROOT, "bench", "c", "ms.c")).read()
    intr = patch_intr(cpp)
    impl("cpp_ref", "Remarque sur C++ (docs/CPP.md) : source de la campagne, g++ 16, options du banc (référence des rapports)",
         f"{GXX} -o ms ../cpp/ms.cpp")
    impl("cpp_intr", "Remarque sur C++ : noyaux std::simd remplacés par la forme de C (intrinsèques), g++ 16", f"{GXX} -o ms ms.cpp", intr)
    impl("cpp_clang", "Remarque sur C++ : source de cpp_intr compilée par clang++ 23 (libstdc++ de GCC 16)",
         f"{CLANGXX} -o ms ../cpp_intr/ms.cpp")
    impl("cpp_k9", "Remarque sur C++ : grilles de K9 allouées une seule fois (comme C), g++ 16", f"{GXX} -o ms ms.cpp", patch_k9(cpp))
    impl("cpp_k8", "Remarque sur C++ : arène de K8 tuned par pointeur brut (comme C), g++ 16", f"{GXX} -o ms ms.cpp", patch_k8(cpp))
    impl("cpp_all", "Remarque sur C++ : cpp_intr + cpp_k9 + cpp_k8, compilée par clang++ 23", f"{CLANGXX} -o ms ms.cpp",
         patch_k8(patch_k9(intr)))
    impl("c_ref", "Remarque sur C++ : source C de la campagne, clang 23, options du banc (témoin du même hôte)",
         f"{CLANG} -o ms ../c/ms.c", extra=False)
    impl("c_k9", "Remarque sur C++ : source C, grilles de K9 réallouées à chaque répétition, clang 23", f"{CLANG} -o ms ms.c",
         patch_c_k9(c), extra=False)
    print("copies écrites : cpp_ref, cpp_intr, cpp_clang, cpp_k9, cpp_k8, cpp_all, c_ref, c_k9")


if __name__ == "__main__":
    main()
