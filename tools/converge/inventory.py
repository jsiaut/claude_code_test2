#!/usr/bin/env python3
"""v4, point 4 (docs/V4_CONVERGE.md, 3.4) : relevé des formes, langage par langage et forme par forme. Les données sont
ici (INV) ; le script écrit results/converge/inventory.md (lecture) et results/converge/forms.json (lu par le pilote et
par l'analyse), et vérifie que les cellules des formes écrites sont exactement celles de bench/<langage>/cv_variants
(hors K9 natural_flat, variante R2 du point 3, que le calcul du point 4 n'emploie pas).

États : « présente » (une variante publiée répond à la définition ; ses cellules sont les siennes), « écrite »
(variante ajoutée pour le catalogue, listée dans cv_variants), « non écrivible » (capacité absente, preuve dans la note), « sans
objet » (forme de repli quand la forme principale est présente ou écrite ; mt_pool_* sans forme à un fil nouvelle).
« remarque » : forme trouvée par la remarque du langage lui-même (calcul 4 de la section 8)."""
import json, os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
LANGS = ["c", "odin", "cpp", "c3", "zig", "rust", "nim", "d", "ada", "chapel", "fortran", "swift", "julia", "mojo",
         "csharp", "fpc", "java", "go", "haskell", "ocaml"]
NAMES = {"c": "C", "odin": "Odin", "cpp": "C++", "c3": "C3", "zig": "Zig", "rust": "Rust", "nim": "Nim", "d": "D",
         "ada": "Ada", "chapel": "Chapel", "fortran": "Fortran", "swift": "Swift", "julia": "Julia", "mojo": "Mojo",
         "csharp": "C#", "fpc": "FreePascal", "java": "Java", "go": "Go", "haskell": "Haskell", "ocaml": "OCaml"}
# Formes du catalogue (3.3), dans l'ordre du relevé : clé, cellule du plafond, forme principale dont c'est le repli
FORMS = [
    ("k4 tuned", "K4", None), ("k4 swar", "K4", None), ("k5 tuned_v", "K5", None),
    ("q6 tuned_v", "Q6", None), ("q6 tuned_s", "Q6", "q6 tuned_v"),
    ("q1 tuned_v", "Q1", None), ("q1 tuned_s", "Q1", "q1 tuned_v"),
    ("q6 mt_pool", "Q6 mt", None), ("q6 mt_pool_v", "Q6 mt", None), ("q6 mt_pool_s", "Q6 mt", None),
    ("q1 mt_pool", "Q1 mt", None), ("q1 mt_pool_v", "Q1 mt", None), ("q1 mt_pool_s", "Q1 mt", None),
    ("k7 tuned_pf", "K7", None), ("k7 tuned_oa", "K7", "k7 tuned_pf"),
    ("k8 tuned_val", "K8", None), ("k8 tuned_it", "K8", None),
    ("k9 tuned_v", "K9", None), ("k9 mt_pool", "K9 mt", None), ("k9 mt_pool_v", "K9 mt", None),
]
FORM_KEYS = [f for f, _, _ in FORMS]
CEILING = {f: c for f, c, _ in FORMS}

P, E, N, S = "présente", "écrite", "non écrivible", "sans objet"


def e(status, cells=(), note="", remarque=False):
    """Une entrée : état, cellules (noyau, variante, paramètre), note, forme de la remarque du langage."""
    return {"status": status, "cells": [list(c) for c in cells], "note": note, "remarque": remarque}


SANS_REPLI = e(S, note="forme principale présente ou écrite")
INV = {
    "c": {
        "k4 tuned": e(E, [("k4", "tuned", "")], "point 3 (R3) : intrinsèques AVX-512BW, vpsadbw"),
        "k4 swar": e(E, [("k4", "swar", "")], "mots de 64 bits ; clang vectorise la boucle (registres ymm)"),
        "k5 tuned_v": e(P, [("k5", "tuned", "")], "AVX-512 : 16 f32, quatre accumulateurs, 64 éléments par tour, FMA"),
        "q6 tuned_v": e(E, [("k6", "tuned_v", "q6")], "AVX-512 ; la variante tuned publiée est scalaire sans branchement"),
        "q6 tuned_s": SANS_REPLI,
        "q1 tuned_v": e(P, [("k6", "tuned", "q1")], "la référence de la forme"),
        "q1 tuned_s": SANS_REPLI,
        "q6 mt_pool": e(E, [("k6", "mt_pool", "q6")], "barrières POSIX ; chaque quart : q6_tuned publiée"),
        "q6 mt_pool_v": e(E, [("k6", "mt_pool_v", "q6")], "chaque quart : tuned_v"),
        "q6 mt_pool_s": e(S, note="pas de forme scalaire nouvelle"),
        "q1 mt_pool": e(E, [("k6", "mt_pool", "q1")], "chaque quart : q1_tuned publiée (déjà tuned_v)"),
        "q1 mt_pool_v": e(S, note="tuned_v de Q1 présente : mt_pool l'exécute"),
        "q1 mt_pool_s": e(S, note="pas de forme scalaire nouvelle"),
        "k7 tuned_pf": e(P, [("k7", "tuned", "")], "capacité 2^(LOG2+1), cases de 16 octets, Fibonacci, lots de 16, "
                                                    "__builtin_prefetch en écriture"),
        "k7 tuned_oa": SANS_REPLI,
        "k8 tuned_val": e(E, [("k8", "tuned_val", "")], "copie bench/c_k8val (remarque sur C)", True),
        "k8 tuned_it": e(E, [("k8", "tuned_it", "")], "copie bench/c_k8it (remarque sur C)", True),
        "k9 tuned_v": e(E, [("k9", "tuned_v", "")], "AVX-512, 8 f64 ; boucle de Swift (j depuis 1, accès non alignés)"),
        "k9 mt_pool": e(E, [("k9", "mt_pool", "")], "chaque quart : k9_rows publiée"),
        "k9 mt_pool_v": e(E, [("k9", "mt_pool_v", "")], "chaque quart : tuned_v"),
    },
    "odin": {
        "k4 tuned": e(E, [("k4", "tuned", "")], "point 3 (R3) : #simd[64]u8, core:simd"),
        "k4 swar": e(E, [("k4", "swar", "")], "mots de 64 bits (intrinsics.unaligned_load)"),
        "k5 tuned_v": e(P, [("k5", "tuned", "")], "#simd[16]f32, quatre accumulateurs, simd.fma"),
        "q6 tuned_v": e(P, [("k6", "tuned", "q6")], "#simd[16]i32, simd.select, accumulation en #simd[16]i64"),
        "q6 tuned_s": SANS_REPLI,
        "q1 tuned_v": e(E, [("k6", "tuned_v", "q1")], "forme de bench/odin_q1 (remarque sur Odin, × 0,55) : compte par "
                        "card(simd.extract_msbs) ; la variante tuned publiée compte par somme des voies du masque", True),
        "q1 tuned_s": SANS_REPLI,
        "q6 mt_pool": e(E, [("k6", "mt_pool", "q6")], "barrières de core:sync ; chaque quart : q6_tuned publiée (tuned_v)"),
        "q6 mt_pool_v": e(S, note="tuned_v de Q6 présente : mt_pool l'exécute"),
        "q6 mt_pool_s": e(S, note="pas de forme scalaire nouvelle"),
        "q1 mt_pool": e(E, [("k6", "mt_pool", "q1")], "chaque quart : q1_tuned publiée"),
        "q1 mt_pool_v": e(E, [("k6", "mt_pool_v", "q1")], "chaque quart : tuned_v (le Q1 mt de la remarque, fils créés à "
                          "chaque appel, n'est pas écrit : 3.6)"),
        "q1 mt_pool_s": e(S, note="pas de forme scalaire nouvelle"),
        "k7 tuned_pf": e(P, [("k7", "tuned", "")], "lots de 16, intrinsics.prefetch_write_data"),
        "k7 tuned_oa": SANS_REPLI,
        "k8 tuned_val": e(E, [("k8", "tuned_val", "")], "procédure récursive, état en paramètres et en retour"),
        "k8 tuned_it": e(E, [("k8", "tuned_it", "")], "piles en tableaux fixes ([64])"),
        "k9 tuned_v": e(P, [("k9", "tuned", "")], "#simd[8]f64, chargements et écriture non alignés, j depuis 1"),
        "k9 mt_pool": e(E, [("k9", "mt_pool", "")], "chaque quart : k9_rows publiée (tuned_v)"),
        "k9 mt_pool_v": e(S, note="tuned_v de K9 présente : mt_pool l'exécute"),
    },
    "cpp": {
        "k4 tuned": e(E, [("k4", "tuned", "")], "point 3 (R3) : intrinsèques AVX-512BW, comme C"),
        "k4 swar": e(E, [("k4", "swar", "")], "mots de 64 bits (std::memcpy)"),
        "k5 tuned_v": e(P, [("k5", "tuned", "")], "std::simd vec<float, 16>, quatre accumulateurs, chargements alignés"),
        "q6 tuned_v": e(E, [("k6", "tuned_v", "q6")], "std::simd, accumulation en vec<int64_t, 16> ; la variante tuned "
                        "publiée accumule en i32, vidé tous les 256 pas"),
        "q6 tuned_s": SANS_REPLI,
        "q1 tuned_v": e(P, [("k6", "tuned", "q1")], "std::simd : compte par reduce_count, charge en vec<int64_t, 16>"),
        "q1 tuned_s": SANS_REPLI,
        "q6 mt_pool": e(E, [("k6", "mt_pool", "q6")], "std::barrier et std::jthread ; chaque quart : q6_tuned publiée"),
        "q6 mt_pool_v": e(E, [("k6", "mt_pool_v", "q6")], "chaque quart : tuned_v"),
        "q6 mt_pool_s": e(S, note="pas de forme scalaire nouvelle"),
        "q1 mt_pool": e(E, [("k6", "mt_pool", "q1")], "chaque quart : q1_tuned publiée (tuned_v)"),
        "q1 mt_pool_v": e(S, note="tuned_v de Q1 présente : mt_pool l'exécute"),
        "q1 mt_pool_s": e(S, note="pas de forme scalaire nouvelle"),
        "k7 tuned_pf": e(P, [("k7", "tuned", "")], "lots de 16, __builtin_prefetch en écriture"),
        "k7 tuned_oa": SANS_REPLI,
        "k8 tuned_val": e(E, [("k8", "tuned_val", "")], "arène passée par pointeur"),
        "k8 tuned_it": e(E, [("k8", "tuned_it", "")], "piles en std::array<.., 64>"),
        "k9 tuned_v": e(E, [("k9", "tuned_v", "")], "std::simd vec<double, 8>, j depuis 1 ; la variante tuned publiée est "
                        "une boucle scalaire vectorisée par g++"),
        "k9 mt_pool": e(E, [("k9", "mt_pool", "")], "chaque quart : k9_rows publiée"),
        "k9 mt_pool_v": e(E, [("k9", "mt_pool_v", "")], "chaque quart : tuned_v"),
    },
    "c3": {
        "k4 tuned": e(E, [("k4", "tuned", "")], "point 3 (R3) : char[<64>], comp_ge, math::select"),
        "k4 swar": e(E, [("k4", "swar", "")], "mots de 64 bits (mem::load non aligné)"),
        "k5 tuned_v": e(P, [("k5", "tuned", "")], "float[<16>], quatre accumulateurs, math::fma"),
        "q6 tuned_v": e(P, [("k6", "tuned", "q6")], "int[<16>], math::select, accumulation en long[<16>]"),
        "q6 tuned_s": SANS_REPLI,
        "q1 tuned_v": e(E, [("k6", "tuned_v", "q1")], "compte par mask_to_int puis popcount ; la variante tuned publiée "
                        "compte par somme des voies d'une sélection"),
        "q1 tuned_s": SANS_REPLI,
        "q6 mt_pool": e(E, [("k6", "mt_pool", "q6")], "barrière faite du Mutex et de la ConditionVariable de std::thread ; "
                        "chaque quart : q6_tuned publiée (tuned_v)"),
        "q6 mt_pool_v": e(S, note="tuned_v de Q6 présente : mt_pool l'exécute"),
        "q6 mt_pool_s": e(S, note="pas de forme scalaire nouvelle"),
        "q1 mt_pool": e(E, [("k6", "mt_pool", "q1")], "chaque quart : q1_tuned publiée"),
        "q1 mt_pool_v": e(E, [("k6", "mt_pool_v", "q1")], "chaque quart : tuned_v"),
        "q1 mt_pool_s": e(S, note="pas de forme scalaire nouvelle"),
        "k7 tuned_pf": e(P, [("k7", "tuned", "")], "lots de 16, @prefetch(…, VERY_NEAR, true) (écriture)"),
        "k7 tuned_oa": SANS_REPLI,
        "k8 tuned_val": e(E, [("k8", "tuned_val", "")], "fonction récursive, état en paramètres et en retour"),
        "k8 tuned_it": e(E, [("k8", "tuned_it", "")], "piles en tableaux fixes ([64])"),
        "k9 tuned_v": e(P, [("k9", "tuned", "")], "double[<8>], mem::load et mem::store non alignés, j depuis 1"),
        "k9 mt_pool": e(E, [("k9", "mt_pool", "")], "chaque quart : k9_rows publiée (tuned_v)"),
        "k9 mt_pool_v": e(S, note="tuned_v de K9 présente : mt_pool l'exécute"),
    },
    "zig": {
        "k4 tuned": e(E, [("k4", "tuned", "")], "point 3 (R3) : @Vector(64, u8), @select"),
        "k4 swar": e(E, [("k4", "swar", "")], "mots de 64 bits (std.mem.readInt)"),
        "k5 tuned_v": e(P, [("k5", "tuned", "")], "@Vector(16, f32), quatre accumulateurs, @mulAdd"),
        "q6 tuned_v": e(P, [("k6", "tuned", "q6")], "la forme de la frontière : @Vector(16, i32), @select, accumulation en "
                        "@Vector(16, i64)"),
        "q6 tuned_s": SANS_REPLI,
        "q1 tuned_v": e(P, [("k6", "tuned", "q1")], "compte par @popCount(@bitCast(masque)), charge en @Vector(16, i64)"),
        "q1 tuned_s": SANS_REPLI,
        "q6 mt_pool": e(E, [("k6", "mt_pool", "q6")], "barrière faite de std.Io.Mutex et std.Io.Condition ; chaque quart : "
                        "q6Tuned publiée (tuned_v)"),
        "q6 mt_pool_v": e(S, note="tuned_v de Q6 présente : mt_pool l'exécute"),
        "q6 mt_pool_s": e(S, note="pas de forme scalaire nouvelle"),
        "q1 mt_pool": e(E, [("k6", "mt_pool", "q1")], "chaque quart : q1Tuned publiée (tuned_v)"),
        "q1 mt_pool_v": e(S, note="tuned_v de Q1 présente : mt_pool l'exécute"),
        "q1 mt_pool_s": e(S, note="pas de forme scalaire nouvelle"),
        "k7 tuned_pf": e(P, [("k7", "tuned", "")], "lots de 16, @prefetch(.write)"),
        "k7 tuned_oa": SANS_REPLI,
        "k8 tuned_val": e(E, [("k8", "tuned_val", "")], "fonction récursive, état en paramètres et en retour"),
        "k8 tuned_it": e(E, [("k8", "tuned_it", "")], "piles en tableaux fixes ([64])"),
        "k9 tuned_v": e(P, [("k9", "tuned", "")], "@Vector(8, f64), tranches non alignées, j depuis 1"),
        "k9 mt_pool": e(E, [("k9", "mt_pool", "")], "chaque quart : k9Rows publiée (tuned_v)"),
        "k9 mt_pool_v": e(S, note="tuned_v de K9 présente : mt_pool l'exécute"),
    },
    "rust": {
        "k4 tuned": e(E, [("k4", "tuned", "")], "point 3 (R3) : std::arch AVX-512BW, vpsadbw"),
        "k4 swar": e(E, [("k4", "swar", "")], "mots de 64 bits (chunks_exact, u64::from_le_bytes)"),
        "k5 tuned_v": e(P, [("k5", "tuned", "")], "std::arch AVX-512 : 16 f32, quatre accumulateurs, FMA"),
        "q6 tuned_v": e(E, [("k6", "tuned_v", "q6")], "std::arch AVX-512 ; la variante tuned publiée est scalaire sans "
                        "branchement (std::simd n'est pas stable)"),
        "q6 tuned_s": SANS_REPLI,
        "q1 tuned_v": e(P, [("k6", "tuned", "q1")], "std::arch, la référence ; count_ones compilé en popcnt sous "
                        "target-cpu=native : la forme de la remarque (_popcnt32, bench/rust_clpop, × 0,83 sur le code "
                        "de Cascade Lake) n'en diffère pas sur cet hôte"),
        "q1 tuned_s": SANS_REPLI,
        "q6 mt_pool": e(E, [("k6", "mt_pool", "q6")], "std::sync::Barrier, fils de std::thread::scope ; chaque quart : "
                        "q6_tuned publiée"),
        "q6 mt_pool_v": e(E, [("k6", "mt_pool_v", "q6")], "chaque quart : tuned_v"),
        "q6 mt_pool_s": e(S, note="pas de forme scalaire nouvelle"),
        "q1 mt_pool": e(E, [("k6", "mt_pool", "q1")], "chaque quart : q1_tuned publiée (tuned_v)"),
        "q1 mt_pool_v": e(S, note="tuned_v de Q1 présente : mt_pool l'exécute"),
        "q1 mt_pool_s": e(S, note="pas de forme scalaire nouvelle"),
        "k7 tuned_pf": e(P, [("k7", "tuned", "")], "lots de 16, _mm_prefetch::<_MM_HINT_ET0> (écriture)"),
        "k7 tuned_oa": SANS_REPLI,
        "k8 tuned_val": e(E, [("k8", "tuned_val", "")], "arène préallouée, get_unchecked (sûreté : indices < longueur "
                          "par construction)"),
        "k8 tuned_it": e(E, [("k8", "tuned_it", "")], "piles en tableaux fixes ([_; 64])"),
        "k9 tuned_v": e(E, [("k9", "tuned_v", "")], "std::arch AVX-512, grilles ABuf alignées sur 64 octets, j depuis 1 ; "
                        "la variante tuned publiée est une boucle scalaire vectorisée par rustc"),
        "k9 mt_pool": e(E, [("k9", "mt_pool", "")], "chaque quart : k9_rows publiée (grilles ABuf)"),
        "k9 mt_pool_v": e(E, [("k9", "mt_pool_v", "")], "chaque quart : tuned_v"),
    },
    "nim": {
        "k4 tuned": e(E, [("k4", "tuned", "")], "point 3 (R3) : intrinsèques AVX-512BW importées de immintrin.h"),
        "k4 swar": e(E, [("k4", "swar", "")], "mots de 64 bits (copyMem)"),
        "k5 tuned_v": e(P, [("k5", "tuned", "")], "intrinsèques AVX-512 importées : quatre accumulateurs, FMA"),
        "q6 tuned_v": e(E, [("k6", "tuned_v", "q6")], "intrinsèques AVX-512 importées ; la variante tuned publiée est "
                        "scalaire sans branchement"),
        "q6 tuned_s": SANS_REPLI,
        "q1 tuned_v": e(E, [("k6", "tuned_v", "q1")], "forme de bench/nim_q1 (remarque sur Nim, × 0,30), recopiée : la "
                        "référence C en intrinsèques importées ; la variante tuned publiée agrège par blocs et par groupe "
                        "en scalaire", True),
        "q1 tuned_s": SANS_REPLI,
        "q6 mt_pool": e(E, [("k6", "mt_pool", "q6")], "barrière faite du Lock et du Cond de std/locks ; chaque quart : "
                        "q6Tuned publiée"),
        "q6 mt_pool_v": e(E, [("k6", "mt_pool_v", "q6")], "chaque quart : tuned_v"),
        "q6 mt_pool_s": e(S, note="pas de forme scalaire nouvelle"),
        "q1 mt_pool": e(E, [("k6", "mt_pool", "q1")], "chaque quart : q1Tuned publiée"),
        "q1 mt_pool_v": e(E, [("k6", "mt_pool_v", "q1")], "chaque quart : tuned_v (le Q1 mt de la remarque, fils créés à "
                          "chaque appel, n'est pas écrit : 3.6)"),
        "q1 mt_pool_s": e(S, note="pas de forme scalaire nouvelle"),
        "k7 tuned_pf": e(P, [("k7", "tuned", "")], "lots de 16, __builtin_prefetch(p, 1, 3) importé (écriture)"),
        "k7 tuned_oa": SANS_REPLI,
        "k8 tuned_val": e(E, [("k8", "tuned_val", "")], "sous boundChecks et overflowChecks désactivés, comme les autres "
                          "noyaux optimisés"),
        "k8 tuned_it": e(E, [("k8", "tuned_it", "")], "piles en tableaux fixes (array[64, …])"),
        "k9 tuned_v": e(E, [("k9", "tuned_v", "")], "intrinsèques AVX-512 importées, j depuis 1 ; la variante tuned "
                        "publiée est une boucle scalaire que clang vectorise"),
        "k9 mt_pool": e(E, [("k9", "mt_pool", "")], "chaque quart : k9Rows publiée"),
        "k9 mt_pool_v": e(E, [("k9", "mt_pool_v", "")], "chaque quart : tuned_v"),
    },
    "d": {
        "k4 tuned": e(E, [("k4", "tuned", "")], "point 3 (R3) : vecteurs de core.simd, masque de ldc.simd, psadbw de "
                      "ldc.gccbuiltins_x86"),
        "k4 swar": e(E, [("k4", "swar", "")], "mots de 64 bits (memcpy)"),
        "k5 tuned_v": e(P, [("k5", "tuned", "")], "float16 de core.simd, quatre accumulateurs, contraction permise "
                        "(@llvmFastMathFlag(\"contract\"))"),
        "q6 tuned_v": e(E, [("k6", "tuned_v", "q6")], "int16 de core.simd, accumulation en long8 (voies paires et "
                        "impaires) ; la variante tuned publiée est scalaire sans branchement. La préférence 512 bits de "
                        "la remarque (bench/d_512, -mattr=-prefer-256-bit) n'est pas admise : option de construction "
                        "propre à une variante (3.2, 4)"),
        "q6 tuned_s": SANS_REPLI,
        "q1 tuned_v": e(P, [("k6", "tuned", "q1")], "core.simd (la correction de la remarque, reportée en base) : compte "
                        "par accumulation des voies du masque, réduite toutes les 4 096 lignes (la population du masque "
                        "sans réduction à chaque tour ; LDC n'expose pas de comparaison vers un masque en bits), charge "
                        "en 64 bits par voies paires et impaires"),
        "q1 tuned_s": SANS_REPLI,
        "q6 mt_pool": e(E, [("k6", "mt_pool", "q6")], "core.sync.barrier, fils de core.thread ; chaque quart : q6Tuned "
                        "publiée"),
        "q6 mt_pool_v": e(E, [("k6", "mt_pool_v", "q6")], "chaque quart : tuned_v"),
        "q6 mt_pool_s": e(S, note="pas de forme scalaire nouvelle"),
        "q1 mt_pool": e(E, [("k6", "mt_pool", "q1")], "chaque quart : q1Tuned publiée (tuned_v)"),
        "q1 mt_pool_v": e(S, note="tuned_v de Q1 présente : mt_pool l'exécute"),
        "q1 mt_pool_s": e(S, note="pas de forme scalaire nouvelle"),
        "k7 tuned_pf": e(P, [("k7", "tuned", "")], "lots de 16, llvm_prefetch(p, 1, 3, 1) (écriture)"),
        "k7 tuned_oa": SANS_REPLI,
        "k8 tuned_val": e(E, [("k8", "tuned_val", "")], "fonction récursive, état en paramètres et en retour"),
        "k8 tuned_it": e(E, [("k8", "tuned_it", "")], "piles en tableaux fixes ([64])"),
        "k9 tuned_v": e(P, [("k9", "tuned", "")], "double8 de core.simd, loadUnaligned et storeUnaligned, j depuis 1"),
        "k9 mt_pool": e(E, [("k9", "mt_pool", "")], "chaque quart : k9Rows publiée (tuned_v)"),
        "k9 mt_pool_v": e(S, note="tuned_v de K9 présente : mt_pool l'exécute"),
    },
    "ada": {
        "k4 tuned": e(E, [("k4", "tuned", "")], "point 3 (R3) : type vectoriel GCC et builtins importés (vpmovb2m, "
                      "vmovdqu8 masqué, vpsadbw)"),
        "k4 swar": e(E, [("k4", "swar", "")], "mots de 64 bits lus par superposition d'adresse"),
        "k5 tuned_v": e(P, [("k5", "tuned", "")], "type vectoriel GCC de 16 Float, builtin FMA, quatre accumulateurs"),
        "q6 tuned_v": e(E, [("k6", "tuned_v", "q6")], "type vectoriel GCC et builtins AVX-512 importés (pmovzxbd, "
                        "comparaisons vers masque, pmulld masqué) ; la variante tuned publiée est scalaire, vectorisée "
                        "par GCC"),
        "q6 tuned_s": SANS_REPLI,
        "q1 tuned_v": e(E, [("k6", "tuned_v", "q1")], "la référence C en builtins importés (popcount, pext, pmuldq) ; "
                        "boucle des six groupes déroulée (pragma Loop_Optimize (Unroll) : 70 → 22 ms) ; la variante "
                        "tuned publiée agrège par blocs et par groupe en scalaire"),
        "q1 tuned_s": SANS_REPLI,
        "q6 mt_pool": e(E, [("k6", "mt_pool", "q6")], "trois tâches Ada créées une fois, rendez-vous Go et Done ; chaque "
                        "quart : Q6_Tuned publiée"),
        "q6 mt_pool_v": e(E, [("k6", "mt_pool_v", "q6")], "chaque quart : tuned_v"),
        "q6 mt_pool_s": e(S, note="pas de forme scalaire nouvelle"),
        "q1 mt_pool": e(E, [("k6", "mt_pool", "q1")], "chaque quart : Q1_Tuned publiée"),
        "q1 mt_pool_v": e(E, [("k6", "mt_pool_v", "q1")], "chaque quart : tuned_v"),
        "q1 mt_pool_s": e(S, note="pas de forme scalaire nouvelle"),
        "k7 tuned_pf": e(P, [("k7", "tuned", "")], "lots de 16, __builtin_prefetch(p, 1, 0) importé (écriture)"),
        "k7 tuned_oa": SANS_REPLI,
        "k8 tuned_val": e(P, [("k8", "tuned", "")], "la forme de la frontière : paramètres in out de types élémentaires, "
                          "passés par copie (RM 6.2)"),
        "k8 tuned_it": e(E, [("k8", "tuned_it", "")], "piles en tableaux fixes (0 .. 63)"),
        "k9 tuned_v": e(E, [("k9", "tuned_v", "")], "type vectoriel GCC de 8 Long_Float, builtins loadupd, addpd, "
                        "mulpd, storeupd, j depuis 1 ; la variante tuned publiée est une boucle scalaire vectorisée par "
                        "GCC"),
        "k9 mt_pool": e(E, [("k9", "mt_pool", "")], "chaque quart : K9_Rows publiée"),
        "k9 mt_pool_v": e(E, [("k9", "mt_pool_v", "")], "chaque quart : tuned_v"),
    },
    "chapel": {
        "k4 tuned": e(E, [("k4", "tuned", "")], "point 3 (R3) : intrinsèques AVX-512BW importées par extern proc"),
        "k4 swar": e(E, [("k4", "swar", "")], "mots de 64 bits (OS.POSIX.memcpy)"),
        "k5 tuned_v": e(E, [("k5", "tuned_v", "")], "intrinsèques AVX-512 importées (FMA, quatre accumulateurs), "
                        "binaire ms_tuned ; la variante tuned publiée est une boucle simple vectorisée par LLVM sous "
                        "--no-ieee-float"),
        "q6 tuned_v": e(E, [("k6", "tuned_v", "q6")], "intrinsèques importées ; comparaisons par le bit de signe d'une "
                        "différence (les comparaisons à immédiat sont des macros, non importables) ; la variante tuned "
                        "publiée est scalaire, vectorisée par LLVM"),
        "q6 tuned_s": SANS_REPLI,
        "q1 tuned_v": e(E, [("k6", "tuned_v", "q1")], "forme de bench/chapel_exp (remarque sur Chapel, × 0,84), recopiée : "
                        "la référence C en intrinsèques importées ; la variante tuned publiée agrège par blocs et par "
                        "groupe", True),
        "q1 tuned_s": SANS_REPLI,
        "q6 mt_pool": e(P, [("k6", "mt", "q6")], "coforall : tâches sur les fils gardés par le runtime (créés une fois)"),
        "q6 mt_pool_v": e(E, [("k6", "mt_pool_v", "q6")], "coforall, chaque quart : tuned_v"),
        "q6 mt_pool_s": e(S, note="pas de forme scalaire nouvelle"),
        "q1 mt_pool": e(P, [("k6", "mt", "q1")], "coforall (fils du runtime)"),
        "q1 mt_pool_v": e(E, [("k6", "mt_pool_v", "q1")], "coforall, chaque quart : tuned_v"),
        "q1 mt_pool_s": e(S, note="pas de forme scalaire nouvelle"),
        "k7 tuned_pf": e(P, [("k7", "tuned", "")], "la forme de la frontière ; le module Prefetch n'expose que "
                         "__builtin_prefetch(addr), un préchargement en lecture"),
        "k7 tuned_oa": SANS_REPLI,
        "k8 tuned_val": e(E, [("k8", "tuned_val", "")], "procédure récursive, état en paramètres et en retour"),
        "k8 tuned_it": e(E, [("k8", "tuned_it", "")], "piles en tuples (64 * int(32)) : aucune allocation"),
        "k9 tuned_v": e(E, [("k9", "tuned_v", "")], "intrinsèques importées sur les tableaux 2D de Chapel lus par "
                        "pointeur, j depuis 1 ; la variante tuned publiée est une boucle foreach vectorisée par LLVM"),
        "k9 mt_pool": e(P, [("k9", "mt", "")], "forall (fils du runtime), quatre blocs de lignes"),
        "k9 mt_pool_v": e(E, [("k9", "mt_pool_v", "")], "coforall, quatre quarts : tuned_v"),
    },
    "fortran": {
        "k4 tuned": e(E, [("k4", "tuned", "")], "point 3 (R3) : sans SIMD explicite, la meilleure boucle scalaire "
                      "(vectorisée par gfortran)"),
        "k4 swar": e(E, [("k4", "swar", "")], "tableau d'octets vu en entiers de 64 bits (c_f_pointer) ; masque par "
                     "ishft(m, 8) - m (entiers signés) ; gfortran vectorise la boucle"),
        "k5 tuned_v": e(N, note="pas de vecteurs explicites : grille C1 = 0 (« aucun type vectoriel ») et C2 = 0 (aucun intrinsèque), sondes results/probes/fortran.txt ; la forme de la remarque (rq_acc16) en tient "
                        "lieu"),
        "q6 tuned_v": e(N, note="grille C1 = 0 (« aucun type vectoriel ») et C2 = 0 (aucun intrinsèque), sondes results/probes/fortran.txt"),
        "q6 tuned_s": e(P, [("k6", "tuned", "q6")], "prédicat en 0/1 par merge (pas d'entiers non signés), "
                        "s += prix × remise × m en 64 bits, !$omp simd"),
        "q1 tuned_v": e(N, note="grille C1 = 0 (« aucun type vectoriel ») et C2 = 0 (aucun intrinsèque), sondes results/probes/fortran.txt"),
        "q1 tuned_s": e(E, [("k6", "tuned_s", "q1")], "une passe, 30 accumulateurs locaux de 64 bits, masques par merge ; "
                        "la variante tuned publiée agrège par blocs et par groupe"),
        "q6 mt_pool": e(P, [("k6", "mt", "q6")], "équipe OpenMP (fils gardés par le runtime)"),
        "q6 mt_pool_v": e(S, note="tuned_v de Q6 non écrivible"),
        "q6 mt_pool_s": e(S, note="tuned_s de Q6 présente : mt_pool l'exécute"),
        "q1 mt_pool": e(P, [("k6", "mt", "q1")], "équipe OpenMP"),
        "q1 mt_pool_v": e(S, note="tuned_v de Q1 non écrivible"),
        "q1 mt_pool_s": e(E, [("k6", "mt_pool_s", "q1")], "équipe OpenMP, chaque quart : tuned_s"),
        "k7 tuned_pf": e(N, note="pas d'instruction de préchargement : grille E4 = 0 ; la variante tuned publiée lit "
                         "par lots les cases (chargements anticipés) avec un autre hachage"),
        "k7 tuned_oa": e(E, [("k7", "tuned_oa", "")], "la table de tuned_pf sans préchargement ni lots ; produit de "
                         "Fibonacci modulo 2^32 par moitiés de 16 bits (entiers signés de 64 bits)"),
        "k8 tuned_val": e(E, [("k8", "tuned_val", "")], "arguments value, arène de nœuds de 16 octets"),
        "k8 tuned_it": e(E, [("k8", "tuned_it", "")], "piles en tableaux fixes (64)"),
        "k9 tuned_v": e(N, note="grille C1 = 0 (« aucun type vectoriel ») et C2 = 0 (aucun intrinsèque), sondes results/probes/fortran.txt"),
        "k9 mt_pool": e(P, [("k9", "mt", "")], "équipe OpenMP, quatre blocs de colonnes"),
        "k9 mt_pool_v": e(S, note="tuned_v de K9 non écrivible"),
    },
    "swift": {
        "k4 tuned": e(E, [("k4", "tuned", "")], "point 3 (R3) : SIMD8<UInt64>, masque par le bit de poids fort, somme "
                      "par voies"),
        "k4 swar": e(E, [("k4", "swar", "")], "mots de 64 bits scalaires (loadUnaligned)"),
        "k5 tuned_v": e(P, [("k5", "tuned", "")], "SIMD16<Float>, quatre accumulateurs, addProduct (FMA), réduction en "
                        "arbre une fois par appel"),
        "q6 tuned_v": e(P, [("k6", "tuned", "q6")], "SIMD16<Int32>, masques, replacing(with:where:), accumulation en "
                        "SIMD16<Int64>"),
        "q6 tuned_s": SANS_REPLI,
        "q1 tuned_v": e(P, [("k6", "tuned", "q1")], "l'algorithme de la référence, groupes déroulés à la main ; compte par "
                        "accumulation des voies du masque, réduite toutes les 4 096 lignes ; charge en SIMD16<Int64>"),
        "q1 tuned_s": SANS_REPLI,
        "q6 mt_pool": e(E, [("k6", "mt_pool", "q6")], "trois Foundation.Thread créés une fois, DispatchSemaphore ; chaque "
                        "quart : q6Tuned publiée (tuned_v)"),
        "q6 mt_pool_v": e(S, note="tuned_v de Q6 présente : mt_pool l'exécute"),
        "q6 mt_pool_s": e(S, note="pas de forme scalaire nouvelle"),
        "q1 mt_pool": e(E, [("k6", "mt_pool", "q1")], "chaque quart : q1Tuned publiée (tuned_v)"),
        "q1 mt_pool_v": e(S, note="tuned_v de Q1 présente : mt_pool l'exécute"),
        "q1 mt_pool_s": e(S, note="pas de forme scalaire nouvelle"),
        "k7 tuned_pf": e(E, [("k7", "tuned_pf", "")], "lots de 16, préchargement en écriture par "
                         "@_silgen_name(\"llvm.prefetch.p0\") (attribut souligné, grille E4 = ½ ; 16 prefetchw dans le "
                         "binaire)"),
        "k7 tuned_oa": e(P, [("k7", "tuned", "")], "la variante tuned publiée : la même table, sans préchargement"),
        "k8 tuned_val": e(E, [("k8", "tuned_val", "")], "fonction récursive, état en paramètres et en retour"),
        "k8 tuned_it": e(E, [("k8", "tuned_it", "")], "piles en InlineArray<64, Int32> (sur la pile)"),
        "k9 tuned_v": e(P, [("k9", "tuned", "")], "la forme de la frontière : SIMD8<Double>, j depuis 1"),
        "k9 mt_pool": e(E, [("k9", "mt_pool", "")], "chaque quart : k9Rows publiée (tuned_v)"),
        "k9 mt_pool_v": e(S, note="tuned_v de K9 présente : mt_pool l'exécute"),
    },
    "julia": {
        "k4 tuned": e(E, [("k4", "tuned", "")], "point 3 (R3) : llvmcall (VecElement et IR de LLVM, la seule voie de Base)"),
        "k4 swar": e(E, [("k4", "swar", "")], "mots de 64 bits (unsafe_load)"),
        "k5 tuned_v": e(E, [("k5", "tuned_v", "")], "llvmcall : <16 x float>, quatre accumulateurs, llvm.fmuladd ; la "
                        "variante tuned publiée est une boucle @simd à un accumulateur"),
        "q6 tuned_v": e(E, [("k6", "tuned_v", "q6")], "llvmcall (IR de tools/converge/gen_julia_ir.py)"),
        "q6 tuned_s": e(P, [("k6", "tuned", "q6")], "la variante tuned publiée : prédicat sans branchement par "
                        "soustractions non signées et comparaisons, ifelse, @simd"),
        "q1 tuned_v": e(E, [("k6", "tuned_v", "q1")], "llvmcall : la référence C, compte par llvm.ctpop du masque "
                        "(IR de tools/converge/gen_julia_ir.py) ; la variante tuned publiée agrège par blocs et par groupe"),
        "q1 tuned_s": e(E, [("k6", "tuned_s", "q1")], "forme de bench/julia_exp (remarque sur Julia, × 0,53), recopiée pour "
                        "le calcul 4 bien que tuned_v soit écrite", True),
        "q6 mt_pool": e(P, [("k6", "mt", "q6")], "Threads.@spawn : tâches sur les fils gardés par le runtime (-t 4)"),
        "q6 mt_pool_v": e(E, [("k6", "mt_pool_v", "q6")], "Threads.@spawn, chaque quart : tuned_v"),
        "q6 mt_pool_s": e(S, note="tuned_s de Q6 présente : mt_pool l'exécute"),
        "q1 mt_pool": e(P, [("k6", "mt", "q1")], "Threads.@spawn"),
        "q1 mt_pool_v": e(E, [("k6", "mt_pool_v", "q1")], "Threads.@spawn, chaque quart : tuned_v"),
        "q1 mt_pool_s": e(S, note="tuned_s n'est écrite que comme forme de la remarque (calcul 4)"),
        "k7 tuned_pf": e(E, [("k7", "tuned_pf", "")], "forme de bench/julia_exp (remarque sur Julia, × 0,69), recopiée : "
                         "lots de 16, llvm.prefetch par ccall llvmcall (écriture)", True),
        "k7 tuned_oa": e(P, [("k7", "tuned", "")], "la variante tuned publiée : la même table, sans préchargement"),
        "k8 tuned_val": e(E, [("k8", "tuned_val", "")], "fonction récursive, état en paramètres et en retour (indices de base 1)"),
        "k8 tuned_it": e(E, [("k8", "tuned_it", "")], "piles en vecteurs de 64 entrées alloués une fois, hors chrono"),
        "k9 tuned_v": e(E, [("k9", "tuned_v", "")], "llvmcall : <8 x double> le long de la dimension contiguë de la Matrix "
                        "(colonnes), reste scalaire dans l'IR"),
        "k9 mt_pool": e(P, [("k9", "mt", "")], "Threads.@spawn, quatre blocs de colonnes"),
        "k9 mt_pool_v": e(E, [("k9", "mt_pool_v", "")], "Threads.@spawn, chaque quart : tuned_v"),
    },
    "mojo": {
        "k4 tuned": e(E, [("k4", "tuned", "")], "point 3 (R3) : SIMD[DType.uint8, 64], la forme de bench/mojo_exp"),
        "k4 swar": e(E, [("k4", "swar", "")], "mots de 64 bits (chargement non aligné par pointeur)"),
        "k5 tuned_v": e(P, [("k5", "tuned", "")], "SIMD[float32, 16], quatre accumulateurs, fma"),
        "q6 tuned_v": e(P, [("k6", "tuned", "q6")], "SIMD[int32, 16], select, accumulation en SIMD[int64, 16]"),
        "q6 tuned_s": SANS_REPLI,
        "q1 tuned_v": e(E, [("k6", "tuned_v", "q1")], "compte par reduce_bit_count du masque ; la variante tuned publiée "
                        "réduit les voies d'une sélection à chaque tour"),
        "q1 tuned_s": SANS_REPLI,
        "q6 mt_pool": e(P, [("k6", "mt", "q6")], "create_task : tâches sur les fils gardés par le runtime asynchrone"),
        "q6 mt_pool_v": e(S, note="tuned_v de Q6 présente : mt_pool l'exécute"),
        "q6 mt_pool_s": e(S, note="pas de forme scalaire nouvelle"),
        "q1 mt_pool": e(P, [("k6", "mt", "q1")], "create_task (runtime asynchrone)"),
        "q1 mt_pool_v": e(E, [("k6", "mt_pool_v", "q1")], "create_task, chaque quart : tuned_v"),
        "q1 mt_pool_s": e(S, note="pas de forme scalaire nouvelle"),
        "k7 tuned_pf": e(P, [("k7", "tuned", "")], "lots de 16, prefetch[PrefetchOptions().for_write()]"),
        "k7 tuned_oa": SANS_REPLI,
        "k8 tuned_val": e(E, [("k8", "tuned_val", "")], "fonction récursive, état en paramètres et en retour"),
        "k8 tuned_it": e(E, [("k8", "tuned_it", "")], "piles en Array[.., 64] (sur la pile)"),
        "k9 tuned_v": e(P, [("k9", "tuned", "")], "SIMD[float64, 8], chargements et écriture non alignés, j depuis 1"),
        "k9 mt_pool": e(P, [("k9", "mt", "")], "create_task (runtime asynchrone), quatre quarts"),
        "k9 mt_pool_v": e(S, note="tuned_v de K9 présente : mt_pool l'exécute"),
    },
    "csharp": {
        "k4 tuned": e(E, [("k4", "tuned", "")], "point 3 (R3) : Vector512 et vpsadbw d'Avx512BW, la forme de bench/csharp_exp"),
        "k4 swar": e(E, [("k4", "swar", "")], "mots de 64 bits (Unsafe.ReadUnaligned)"),
        "k5 tuned_v": e(P, [("k5", "tuned", "")], "Vector512<float>, quatre accumulateurs, FusedMultiplyAdd"),
        "q6 tuned_v": e(P, [("k6", "tuned", "q6")], "Vector512<int>, sélection par masque, Widen en Vector512<long>"),
        "q6 tuned_s": SANS_REPLI,
        "q1 tuned_v": e(P, [("k6", "tuned", "q1")], "Vector512 et intrinsèques AVX-512, compte par PopCount de "
                        "ExtractMostSignificantBits ; la forme de la remarque (accumulateurs en variables locales) "
                        "n'est pas reprise : × 4,05 sous le protocole publié, son gain ne venait qu'avec FullOpts, option "
                        "non admise (3.2, 4)"),
        "q1 tuned_s": SANS_REPLI,
        "q6 mt_pool": e(E, [("k6", "mt_pool", "q6")], "forme de bench/csharp_exp (remarque sur C#, × 0,71) : Parallel.For "
                        "sur les fils du ThreadPool, le fil appelant compris ; chaque quart : Q6Tuned publiée", True),
        "q6 mt_pool_v": e(S, note="tuned_v de Q6 présente : mt_pool l'exécute"),
        "q6 mt_pool_s": e(S, note="pas de forme scalaire nouvelle"),
        "q1 mt_pool": e(E, [("k6", "mt_pool", "q1")], "Parallel.For (forme de la remarque) ; chaque quart : Q1Tuned "
                        "publiée", True),
        "q1 mt_pool_v": e(S, note="tuned_v de Q1 présente : mt_pool l'exécute"),
        "q1 mt_pool_s": e(S, note="pas de forme scalaire nouvelle"),
        "k7 tuned_pf": e(P, [("k7", "tuned", "")], "lots de 16, Sse.Prefetch0 (préchargement en lecture : .NET n'expose pas "
                         "prefetchw)"),
        "k7 tuned_oa": SANS_REPLI,
        "k8 tuned_val": e(E, [("k8", "tuned_val", "")], "fonction récursive, état en paramètres et en retour, arène statique"),
        "k8 tuned_it": e(E, [("k8", "tuned_it", "")], "forme de bench/csharp_exp (remarque sur C#, × 0,51), piles portées à "
                         "64 entrées (stackalloc)", True),
        "k9 tuned_v": e(P, [("k9", "tuned", "")], "Vector512<double>, Load et Store non alignés, j depuis 1"),
        "k9 mt_pool": e(E, [("k9", "mt_pool", "")], "Parallel.For (forme de la remarque, × 0,63) ; chaque quart : K9Rows "
                        "publiée (tuned_v)", True),
        "k9 mt_pool_v": e(S, note="tuned_v de K9 présente : mt_pool l'exécute"),
    },
    "fpc": {
        "k4 tuned": e(E, [("k4", "tuned", "")], "sans assembleur (erratum du point 3, docs/V4_EQUAL.md 11.8) : forme de "
                      "bench/fpc_rq (remarque sur FreePascal, K4BranchlessPtr) : masque -(x shr 7), pointeur avancé "
                      "par Inc ; -Sv n'a ni octets ni masques (grille C1 = ½, sonde results/probes/fpc.txt)", True),
        "k4 swar": e(E, [("k4", "swar", "")], "mots de 64 bits (unaligned), masque par (m * $FF)"),
        "k5 tuned_v": e(E, [("k5", "tuned_v", "")], "forme de bench/fpc_rq (remarque sur FreePascal, × 0,68) : -Sv, "
                        "4 Single (la plus grande largeur admise : 8 Single = erreur interne 200610072), huit "
                        "accumulateurs, pas de FMA vectorielle, pointeurs avancés par Inc ; la variante tuned publiée "
                        "indexe", True),
        "q6 tuned_v": e(N, note="-Sv n'accepte que des tableaux de Single ou de Double (sonde du 21 novembre : "
                        "« Operator is not overloaded » sur array[0..3] of LongInt), sans masque ni comparaison ; "
                        "aucun intrinsèque SSE/AVX (grille C1 = ½, C2 = ½ par l'assembleur seul, non admis)"),
        "q6 tuned_s": e(P, [("k6", "tuned", "q6")], "la variante tuned publiée : prédicat en 0/1 par soustractions non "
                        "signées et bit de signe (shr 63), produit en 32 bits, s += produit and -m en 64 bits"),
        "q1 tuned_v": e(N, note="comme Q6 : pas d'entiers en -Sv, aucun intrinsèque"),
        "q1 tuned_s": e(E, [("k6", "tuned_s", "q1")], "une passe, 30 accumulateurs locaux de 64 bits, masques par bit "
                        "de signe ; plus lente que la variante tuned publiée (deux tables en mémoire entrelacées) à "
                        "l'essai : FPC garde les accumulateurs en mémoire"),
        "q6 mt_pool": e(E, [("k6", "mt_pool", "q6")], "événements de la RTL (RTLEventSetEvent / RTLEventWaitFor : la "
                        "RTL n'a pas de barrière), fils créés une fois par BeginThread ; chaque quart : Q6Tuned publiée "
                        "(tuned_s)"),
        "q6 mt_pool_v": e(S, note="tuned_v de Q6 non écrivible"),
        "q6 mt_pool_s": e(S, note="tuned_s de Q6 présente : mt_pool l'exécute"),
        "q1 mt_pool": e(E, [("k6", "mt_pool", "q1")], "chaque quart : Q1Tuned publiée"),
        "q1 mt_pool_v": e(S, note="tuned_v de Q1 non écrivible"),
        "q1 mt_pool_s": e(E, [("k6", "mt_pool_s", "q1")], "chaque quart : tuned_s"),
        "k7 tuned_pf": e(P, [("k7", "tuned", "")], "lots de 16, Prefetch du System : prefetchnta, la seule instruction "
                         "de préchargement de la chaîne (sans écriture ni localité ; grille E4 = ½)"),
        "k7 tuned_oa": SANS_REPLI,
        "k8 tuned_val": e(E, [("k8", "tuned_val", "")], "fonction récursive, état en paramètres et en retour"),
        "k8 tuned_it": e(E, [("k8", "tuned_it", "")], "forme de bench/fpc_rq (remarque sur FreePascal, × 0,38), "
                         "recopiée : piles de 64 entrées ({$if} sur MS_K8_REQ à la compilation)", True),
        "k9 tuned_v": e(N, note="-Sv : 2 Double au plus, opérandes mémoire alignés sur 16 octets exigés (erreur 216 "
                        "sinon, sonde results/probes/fpc.txt) : les voisins j - 1 et j + 1 ne peuvent pas l'être en "
                        "même temps que j ; l'essai en -Sv sur 2 Double est plus lent que le scalaire (docs/FPC.md, 2.4)"),
        "k9 mt_pool": e(E, [("k9", "mt_pool", "")], "chaque quart : K9Rows publiée"),
        "k9 mt_pool_v": e(S, note="tuned_v de K9 non écrivible"),
    },
    "java": {
        "k4 tuned": e(E, [("k4", "tuned", "")], "point 3 (R3) : Vector API (ByteVector de 64 octets), blend, voies de "
                      "16 bits"),
        "k4 swar": e(E, [("k4", "swar", "")], "mots de 64 bits lus par la vue VarHandle du tableau d'octets "
                     "(byteArrayViewVarHandle)"),
        "k5 tuned_v": e(P, [("k5", "tuned", "")], "FloatVector de 16 f32 (Vector API), quatre accumulateurs, fma, 64 "
                        "éléments par tour, copies hors tas alignées sur 64 octets"),
        "q6 tuned_v": e(P, [("k6", "tuned", "q6")], "IntVector de 16 voies, comparaisons, produit en i32, blend, "
                        "accumulation en LongVector"),
        "q6 tuned_s": SANS_REPLI,
        "q1 tuned_v": e(E, [("k6", "tuned_v", "q1")], "forme de bench/java_exp (remarque sur Java, × 0,40), recopiée : "
                        "une passe, algorithme de la référence C, compte par Long.bitCount du masque, accumulateurs en "
                        "variables locales ; la variante tuned publiée fait une passe par groupe sur des blocs de 2 048 "
                        "lignes", True),
        "q1 tuned_s": SANS_REPLI,
        "q6 mt_pool": e(E, [("k6", "mt_pool", "q6")], "forme de bench/java_exp (remarque sur Java) ramenée à la "
                        "définition : ThreadPoolExecutor de trois fils démarrés avant l'échauffement, le fil principal "
                        "traite le quart 0 (la remarque : quatre fils de réserve, le fil principal en attente) ; chaque "
                        "quart : q6Tuned publiée (tuned_v)", True),
        "q6 mt_pool_v": e(S, note="tuned_v de Q6 présente : mt_pool l'exécute"),
        "q6 mt_pool_s": e(S, note="pas de forme scalaire nouvelle"),
        "q1 mt_pool": e(E, [("k6", "mt_pool", "q1")], "chaque quart : q1Tuned publiée", True),
        "q1 mt_pool_v": e(E, [("k6", "mt_pool_v", "q1")], "chaque quart : tuned_v (mt_pool_1p de la remarque)", True),
        "q1 mt_pool_s": e(S, note="pas de forme scalaire nouvelle"),
        "k7 tuned_pf": e(N, note="aucun préchargement dans le JDK (grille E4 = 0, results/probes/java.txt : "
                         "Unsafe.prefetch* retirées au JDK 9)"),
        "k7 tuned_oa": e(P, [("k7", "tuned", "")], "la variante tuned publiée : la même table (cases de 16 octets dans "
                         "un long[] : clé et compte dans un mot, somme dans l'autre), sans préchargement ni lots"),
        "k8 tuned_val": e(E, [("k8", "tuned_val", "")], "fonction récursive, état en paramètres et en retour (la "
                          "variante tuned publiée passe l'état par des champs statiques)"),
        "k8 tuned_it": e(E, [("k8", "tuned_it", "")], "forme de bench/java_exp (remarque sur Java, × 0,64), recopiée : "
                         "piles de 64 entrées (K8_REQ contrôlée)", True),
        "k9 tuned_v": e(E, [("k9", "tuned_v", "")], "forme de bench/java_exp (remarque sur Java, tuned_vec, × 0,96) : "
                        "DoubleVector de 8, j depuis 1, accès non alignés (tableaux du tas)", True),
        "k9 mt_pool": e(E, [("k9", "mt_pool", "")], "chaque quart : k9Rows publiée (la remarque : × 0,81)", True),
        "k9 mt_pool_v": e(E, [("k9", "mt_pool_v", "")], "chaque quart : tuned_v (la remarque : × 0,77)", True),
    },
    "go": {
        "k4 tuned": e(E, [("k4", "tuned", "")], "point 3 (R3) : simd/archsimd (Uint8x64), masque, SumOf8AbsDiff"),
        "k4 swar": e(E, [("k4", "swar", "")], "mots de 64 bits (binary.LittleEndian.Uint64)"),
        "k5 tuned_v": e(E, [("k5", "tuned_v", "")], "forme de bench/go_exp (remarque sur Go, tuned_r, × 0,75), recopiée : "
                        "Float32x16, quatre accumulateurs, MulAdd, la réduction finale dans les registres ; la variante "
                        "tuned publiée réduit par un tableau en mémoire", True),
        "q6 tuned_v": e(P, [("k6", "tuned", "q6")], "Int32x16 (archsimd), masques, produit en i32, Masked, "
                        "accumulation en Int64x8"),
        "q6 tuned_s": SANS_REPLI,
        "q1 tuned_v": e(E, [("k6", "tuned_v", "q1")], "forme de bench/go_exp (remarque sur Go, tuned_1p), recopiée : une "
                        "passe, compte par bits.OnesCount16 du masque, additions masquées par IfElse, accumulateurs en "
                        "variables locales ; plus lente que la variante tuned publiée (scalaire) dans la remarque "
                        "(× 1,36) et à l'essai", True),
        "q1 tuned_s": SANS_REPLI,
        "q6 mt_pool": e(P, [("k6", "mt", "q6")], "goroutines : fils du runtime (GOMAXPROCS), créés une fois"),
        "q6 mt_pool_v": e(S, note="tuned_v de Q6 présente : mt_pool l'exécute"),
        "q6 mt_pool_s": e(S, note="pas de forme scalaire nouvelle"),
        "q1 mt_pool": e(P, [("k6", "mt", "q1")], "goroutines (fils du runtime)"),
        "q1 mt_pool_v": e(E, [("k6", "mt_pool_v", "q1")], "goroutines, chaque quart : tuned_v (mt_1p de la remarque)", True),
        "q1 mt_pool_s": e(S, note="pas de forme scalaire nouvelle"),
        "k7 tuned_pf": e(N, note="aucun préchargement exporté (grille E4 = 0, results/probes/go.txt : "
                         "internal/runtime/sys.Prefetch interdit hors de la bibliothèque)"),
        "k7 tuned_oa": e(P, [("k7", "tuned", "")], "la variante tuned publiée : la même table (cases de 16 octets), "
                         "sans préchargement ni lots"),
        "k8 tuned_val": e(E, [("k8", "tuned_val", "")], "fonction récursive, état en paramètres et en retour, tranche de "
                          "longueur fixe (la variante tuned publiée passe un compteur et la tranche par pointeur, et "
                          "ajoute par append)"),
        "k8 tuned_it": e(E, [("k8", "tuned_it", "")], "forme de bench/go_noexp (remarque sur Go, × 0,62), recopiée : piles "
                         "de 64 entrées (profondeur contrôlée à la compilation)", True),
        "k9 tuned_v": e(E, [("k9", "tuned_v", "")], "forme de bench/go_exp (remarque sur Go, tuned_vec, × 0,78) : "
                        "Float64x8, j depuis 1, accès non alignés, fin par chargements partiels", True),
        "k9 mt_pool": e(P, [("k9", "mt", "")], "goroutines (fils du runtime)"),
        "k9 mt_pool_v": e(E, [("k9", "mt_pool_v", "")], "goroutines, chaque quart : tuned_v (mt_vec de la remarque, "
                          "× 0,73)", True),
    },
    "haskell": {
        "k4 tuned": e(E, [("k4", "tuned", "")], "point 3 (R3) : primitives SIMD de GHC (Word16X32#), sans comparaison "
                      "ni « et » : reste et quotient par 256 et par 128"),
        "k4 swar": e(E, [("k4", "swar", "")], "mots de 64 bits (indexWord8OffAddrAsWord64#, lecture non alignée)"),
        "k5 tuned_v": e(P, [("k5", "tuned", "")], "FloatX16#, quatre accumulateurs, fmaddFloatX16#, 64 éléments par tour"),
        "q6 tuned_v": e(N, note="GHC 9.14.1 n'offre sur les vecteurs d'entiers (Int32X16#…) ni comparaison, ni masque, "
                        "ni sélection, ni « et » (GHC.Exts : broadcast, pack/unpack, insert, plus, minus, times, quot, "
                        "rem, negate, lectures et écritures ; « :browse GHC.Exts », 21 novembre) : le prédicat ne s'écrit "
                        "pas par comparaisons"),
        "q6 tuned_s": e(P, [("k6", "tuned", "q6")], "la variante tuned publiée : prédicat en 0/1 par comparaisons non "
                        "signées (fromEnum), s += prix × remise × m en 64 bits"),
        "q1 tuned_v": e(N, note="comme Q6 : ni comparaison ni masque sur les vecteurs d'entiers de GHC"),
        "q1 tuned_s": e(E, [("k6", "tuned_s", "q1")], "une passe, 30 accumulateurs en arguments stricts de la boucle, "
                        "masques par décalage arithmétique ; bien plus lente que la variante tuned publiée à l'essai "
                        "(342 contre 46 ms : GHC passe les 31 arguments par sa pile)"),
        "q6 mt_pool": e(P, [("k6", "mt", "q6")], "forkOn : fils légers sur les capacités du runtime (-N4, fils gardés "
                        "par le RTS)"),
        "q6 mt_pool_v": e(S, note="tuned_v de Q6 non écrivible"),
        "q6 mt_pool_s": e(S, note="tuned_s de Q6 présente : mt_pool l'exécute"),
        "q1 mt_pool": e(P, [("k6", "mt", "q1")], "forkOn (capacités du runtime)"),
        "q1 mt_pool_v": e(S, note="tuned_v de Q1 non écrivible"),
        "q1 mt_pool_s": e(E, [("k6", "mt_pool_s", "q1")], "forkOn, chaque quart : tuned_s"),
        "k7 tuned_pf": e(E, [("k7", "tuned_pf", "")], "la table de la variante tuned, lots de 16, prefetchAddr3# "
                         "(préchargement en lecture : GHC n'en a pas en écriture)"),
        "k7 tuned_oa": SANS_REPLI,
        "k8 tuned_val": e(E, [("k8", "tuned_val", "")], "fonction récursive dans IO, état en arguments et en retour (la "
                          "variante tuned publiée garde l'indice libre et le compteur en mémoire brute)"),
        "k8 tuned_it": e(E, [("k8", "tuned_it", "")], "piles de 64 entrées en mémoire brute allouée une fois "
                         "(profondeur contrôlée à la compilation, #error)"),
        "k9 tuned_v": e(P, [("k9", "tuned", "")], "DoubleX8#, j depuis 1, chargements et écritures non alignés, reste "
                        "scalaire"),
        "k9 mt_pool": e(P, [("k9", "mt", "")], "forkOn (capacités du runtime)"),
        "k9 mt_pool_v": e(S, note="tuned_v de K9 présente : mt_pool l'exécute"),
    },
    "ocaml": {
        "k4 tuned": e(E, [("k4", "tuned", "")], "point 3 (R3) : sans SIMD (aucun type vectoriel), huit octets par mot "
                      "Int64, somme des voies par multiplication à chaque mot"),
        "k4 swar": e(E, [("k4", "swar", "")], "voies de 16 bits en Int64 (le int de 63 bits ne tient pas quatre voies), "
                     "vidées toutes les 128 mots"),
        "k5 tuned_v": e(N, note="aucun type vectoriel ni intrinsèque (grille C1 = 0, C2 = 0, results/probes/ocaml.txt) ; "
                        "la forme à huit accumulateurs de la remarque (× 0,97, dans le bruit) n'est pas reprise"),
        "q6 tuned_v": e(N, note="aucun type vectoriel (grille C1 = 0)"),
        "q6 tuned_s": e(E, [("k6", "tuned_s", "q6")], "forme de bench/ocaml_exp (remarque sur OCaml, tuned_m, × 0,86), "
                        "recopiée : masque tiré des bits de signe des cinq bornes, s += prix × remise × m ; la variante "
                        "tuned publiée fait cinq comparaisons (Bool.to_int)", True),
        "q1 tuned_v": e(N, note="aucun type vectoriel (grille C1 = 0)"),
        "q1 tuned_s": e(E, [("k6", "tuned_s", "q1")], "une passe, 30 références locales, masques par décalage arithmétique ; "
                        "plus lente que la variante tuned publiée à l'essai (379 contre 115 ms)"),
        "q6 mt_pool": e(E, [("k6", "mt_pool", "q6")], "trois domaines créés une fois, barrière par Mutex et Condition "
                        "(la bibliothèque standard n'en a pas), le domaine principal traite le quart 0 ; la variante mt "
                        "publiée crée ses domaines à chaque appel ; chaque quart : q6_tuned publiée"),
        "q6 mt_pool_v": e(S, note="tuned_v de Q6 non écrivible"),
        "q6 mt_pool_s": e(E, [("k6", "mt_pool_s", "q6")], "chaque quart : tuned_s (mt_m de la remarque, ici par la "
                          "réserve)", True),
        "q1 mt_pool": e(E, [("k6", "mt_pool", "q1")], "chaque quart : q1_tuned publiée"),
        "q1 mt_pool_v": e(S, note="tuned_v de Q1 non écrivible"),
        "q1 mt_pool_s": e(E, [("k6", "mt_pool_s", "q1")], "chaque quart : tuned_s"),
        "k7 tuned_pf": e(N, note="aucun préchargement (grille E4 = 0, results/probes/ocaml.txt)"),
        "k7 tuned_oa": e(E, [("k7", "tuned_oa", "")], "forme de bench/ocaml_exp (remarque sur OCaml, tuned_p, × 0,875), "
                         "recopiée : cases de deux mots (clé et compteur de 30 bits dans un entier, somme dans l'autre), "
                         "c'est-à-dire la table de tuned_pf sans préchargement ; la variante tuned publiée prend trois "
                         "mots par case. Le plan (section 2) la range parmi les formes propres au runtime (champs de "
                         "deux mots d'OCaml) : comptée ici comme repli, la cellule du plafond est la même (K7)", True),
        "k8 tuned_val": e(E, [("k8", "tuned_val", "")], "forme de bench/ocaml_exp (remarque sur OCaml, × 0,77), "
                          "recopiée", True),
        "k8 tuned_it": e(E, [("k8", "tuned_it", "")], "piles de 64 entrées (tableaux alloués une fois ; profondeur "
                         "vérifiée au lancement)"),
        "k9 tuned_v": e(N, note="aucun type vectoriel (grille C1 = 0) ; la forme floatarray de la remarque (× 0,945) "
                        "n'est pas reprise : gain sous 10 %, et ce n'est pas une forme du catalogue"),
        "k9 mt_pool": e(E, [("k9", "mt_pool", "")], "réserve de domaines, chaque quart : k9_rows publiée"),
        "k9 mt_pool_v": e(S, note="tuned_v de K9 non écrivible"),
    },
}
RQ = {  # formes propres à un langage ou à son runtime (3.5), par langage : {nom: entrée, avec sa cellule du plafond}
    "java": {
        "k7 rq_iso": {**e(E, [("k7", "rq_iso", "")], "forme de bench/java_exp (remarque sur Java, tuned_iso, × 0,72) : "
                          "la boucle de la variante tuned dans sa propre méthode ; son gain tient à l'unité de "
                          "compilation du JIT (runK7, appelée une fois, est compilée sur place), coût propre au runtime "
                          "(plan, 3.5). Les lots lus d'avance de la remarque (tuned_batch, × 0,80) ne sont pas repris : "
                          "sans préchargement, ils perdent sur la forme isolée seule", True), "ceiling": "K7"},
    },
    "julia": {
        "k8 rq_spec": {**e(E, [("k8", "rq_spec", "")], "forme de bench/julia_exp (remarque sur Julia, × 0,83) : la "
                           "variante tuned spécialisée sur la profondeur (Val) ; classée propre au runtime par le plan "
                           "(2 : spécialisation de Julia)", True), "ceiling": "K8"},
    },
    "fortran": {
        "k5 rq_acc16": {**e(E, [("k5", "rq_acc16", "")], "forme de bench/fortran_exp (remarque sur Fortran) : quatre "
                            "accumulateurs écrits comme des tableaux de 16 valeurs, une réduction finale ; propre à "
                            "Fortran, qui n'a pas de type vectoriel (K5 tuned_v non écrivible)", True), "ceiling": "K5"},
        "k8 rq_aos": {**e(E, [("k8", "rq_aos", "")], "forme de bench/fortran_exp (remarque sur Fortran) : la variante "
                          "tuned (état par référence) sur une arène de nœuds de 16 octets au lieu de trois tableaux",
                          True), "ceiling": "K8"},
    },
    "nim": {
        "k8 rq_noovf": {**e(E, [("k8", "rq_noovf", "")], "forme de bench/nim_k8 (remarque sur Nim, × 0,91) : la variante "
                            "tuned sans vérification de débordement ; son gain tient aux vérifications de débordement "
                            "de Nim (classée propre au runtime par le plan, 2)", True), "ceiling": "K8"},
    },
    "rust": {
        "k8 rq_arena": {**e(E, [("k8", "rq_arena", "")], "forme de bench/rust_k8 (remarque sur Rust, × 0,74) : l'arène "
                            "écrite comme en C (tranche préallouée, indice libre et compteur par référence, get_unchecked) ; "
                            "son gain tient à Vec::push (test de capacité, longueur mise à jour) et aux vérifications de "
                            "bornes de la variante tuned publiée, des coûts de l'idiome de Rust", True), "ceiling": "K8"},
    },
    "cpp": {
        "k8 rq_ptr": {**e(E, [("k8", "rq_ptr", "")], "forme de bench/cpp_k8 (remarque sur C++, × 0,77) : la variante tuned, "
                          "l'arène passée par pointeur brut ; son gain tient au std::vector passé par référence avec un "
                          "état lui aussi par référence (rechargements imposés par l'aliasing), un coût de l'idiome de "
                          "C++ ; les formes du catalogue reçoivent l'arène par pointeur", True), "ceiling": "K8"},
    },
}


def cv_cells(lang):
    path = os.path.join(ROOT, "bench", lang, "cv_variants")
    out = set()
    for line in open(path):
        f = line.split()
        if len(f) >= 2:
            out.add((f[0], f[1], f[2] if len(f) > 2 else ""))
    return out


def check(lang):
    inv = {**INV[lang], **RQ.get(lang, {})}
    missing = [f for f in FORM_KEYS if f not in INV[lang]]
    if missing:
        raise SystemExit(f"{lang} : formes sans état {missing}")
    written = {tuple(c) for x in inv.values() if x["status"] == E for c in x["cells"]}
    have = cv_cells(lang) - {("k9", "natural_flat", "")}
    if written != have:
        raise SystemExit(f"{lang} : écrites {sorted(written - have)} absentes de cv_variants ; "
                         f"cv_variants {sorted(have - written)} sans forme")


def main():
    done = [l for l in LANGS if l in INV]
    for lang in done:
        check(lang)
    js = {"note": "v4, point 4 : relevé des formes (tools/converge/inventory.py, docs/V4_CONVERGE.md 3.4)",
          "langs": {l: {**{f: {**INV[l][f], "ceiling": CEILING[f]} for f in FORM_KEYS},
                        **{k: {**v, "ceiling": v["ceiling"]} for k, v in RQ.get(l, {}).items()}} for l in done}}
    open(os.path.join(ROOT, "results", "converge", "forms.json"), "w").write(
        json.dumps(js, ensure_ascii=False, indent=1) + "\n")
    md = ["# Relevé des formes du point 4 (v4)", "",
          "Écrit par `tools/converge/inventory.py` (données dans le script) ; plan : `docs/V4_CONVERGE.md`, 3.3 à 3.5.",
          "États : **présente** (variante publiée conforme à la définition), **écrite** (variante ajoutée pour le "
          "catalogue, listée dans `cv_variants`), **non écrivible** (preuve dans la note), **sans objet** (repli d'une forme "
          "principale présente ou écrite ; réserve de fils sans forme à un fil nouvelle). « R » : forme trouvée par "
          "la remarque du langage (calcul 4).", "",
          f"Langages relevés : {len(done)} sur 25 ({', '.join(NAMES[l] for l in done)}).", "",
          "## Règles de lecture appliquées au relevé (fixées au fil du portage, 21 novembre)", "",
          "1. **Q1 `tuned_v`, « compte par population du masque ».** Sont lus comme conformes : le compte des bits "
          "d'un masque en bits à chaque tour (popcount ; C, Zig, C++, Rust) et l'accumulation des voies du masque "
          "dans un vecteur réduit une fois par bloc de 4 096 lignes (D). Une variante qui réduit horizontalement "
          "les voies du masque à chaque tour (Odin, C3) n'est pas la forme : `tuned_v` est écrite avec un popcount "
          "quand le langage peut tirer un masque en bits (la remarque sur Odin a mesuré × 0,55 pour ce seul "
          "changement).",
          "2. **K9 `tuned_v`.** La forme de la frontière (Swift) part de j = 1 : haut et bas sont lus à 8 octets "
          "d'une frontière de 64 octets, droite à 16, gauche alignée, et l'écriture se fait à 8. Les "
          "variantes écrites reprennent cette boucle avec des chargements et écritures non alignés ; "
          "l'alignement ne change rien de mesurable (4.1).",
          "3. **Formes propres à un langage (3.5).** S'ajoutent à la liste du plan les formes trouvées par une "
          "remarque dont le gain tient à un idiome du langage plutôt qu'à l'algorithme : arène passée par "
          "pointeur brut en C++ (`std::vector` et état par référence) et arène écrite comme en C en Rust "
          "(`Vec::push` et vérifications de bornes). Elles entrent dans le plafond de leur langage, sans portage.",
          "4. **Options de construction.** Une forme dont le gain venait d'une option de construction (D, "
          "`-mattr=-prefer-256-bit`) n'est pas admise (3.2, 4). Une correction déjà reportée en base (4.1) n'est "
          "pas une forme nouvelle.",
          "5. **Réserve de fils (3.6).** `mt_pool` exécute dans chaque quart la forme de la variante `mt` publiée ; "
          "`mt_pool_v` (ou `_s`) n'est écrite que si la forme à un fil correspondante est nouvelle dans le langage. "
          "Sans barrière dans la bibliothèque standard, elle est faite du mutex et de la variable de condition du "
          "langage (numéro de génération).", ""]
    for lang in done:
        md += [f"## {NAMES[lang]}", "", "| Forme | Cellule | État | Variante | Note |", "|---|---|---|---|---|"]
        rows = [(f, INV[lang][f]) for f in FORM_KEYS] + sorted(RQ.get(lang, {}).items())
        for f, x in rows:
            cells = ", ".join(f"`{c[0]} {c[1]}{' ' + c[2] if c[2] else ''}`" for c in x["cells"]) or "—"
            ceil = CEILING.get(f) or x.get("ceiling", "")
            md.append(f"| `{f}`{' (R)' if x['remarque'] else ''} | {ceil} | {x['status']} | {cells} | {x['note']} |")
        md.append("")
    open(os.path.join(ROOT, "results", "converge", "inventory.md"), "w").write("\n".join(md))
    print(f"relevé : {len(done)} langages")


if __name__ == "__main__":
    main()
