# Audit de la grille : une sonde par case (v4, point 1)

*Plan : `docs/V4_PLAN.md`, section 2, poussé avant tout travail. Outils : `tools/grid_audit/` (motifs de recherche fixés
d'avance, `search.py`), `analysis/grid_audit.py` (confrontation des sondes à la matrice v1 et v2, classes de preuve).
Sorties : `results/probes/<langage>.txt`, `results/grid_audit/summary.md`, `results/grid_audit/search/` (détail de chaque
recherche d'absence). Ce document est rempli langage par langage ; les errata sont appliqués ensemble à la fin.*

## 1. Méthode

* **Classes de preuve.** [exécutée] : un programme se sert de la capacité et imprime un fait observable (taille,
  décalage, adresse modulo, valeur, fil, instruction du code produit, attribut de l'IR) ; pour ½, la limite est montrée
  aussi. [échec] : la forme canonique est tentée et le refus du compilateur est imprimé. [recherche] : les sources livrées
  de la bibliothèque standard (ou la liste de ses API publiques) sont fouillées avec le motif de la case
  (`tools/grid_audit/patterns.json`) ; chaque déclaration publique trouvée est examinée, et l'examen est écrit dans la
  ligne de la sonde. C3 reste [mesurée].
* **Note.** La sonde imprime la note de la règle v2 (score central) ; quand v1 diffère, la ligne le dit.
  `analysis/grid_audit.py` compare chaque ligne à la matrice et liste les divergences.
* **Contre-épreuves.** Quand une capacité notée ½ ou 0 existe sous une forme exclue par la règle (canal instable,
  unité interne, FFI), la sonde l'exécute aussi et l'imprime en ligne NOTE : le fait est établi, la note suit la règle.
  Une case où la règle elle-même hésite est listée en section 3 avec l'effet des deux notes.
* **Écarts au plan.** (1) Après la première recherche (Rust), les fichiers `tests.rs` ont été ajoutés aux exclusions de
  Rust (modules de test, pas des API publiques) et le détail des recherches liste désormais les lignes de mention ; les
  motifs des cases n'ont pas changé.

## 2. Résultats par langage

### Rust (rustc 1.99.1 stable ; nightly 1.101.0 du 27 octobre pour les contre-épreuves)

33 cases sondées (C3 mesurée), aucune divergence avec la matrice. Sondes : `probes/rust/probe.rs` (A5, E2) et
`probes/rust/audit/` (`audit.rs` exécuté, `codegen.rs` lu en assembleur et en IR, trois échecs sur le canal stable,
`nightly.rs` pour les contre-épreuves, sept recherches dans `std`, `core` et `alloc` de rust-src 1.99.1).
* Faits notables : `repr(Rust)` réordonne (u8, f64, u8) en 16 octets, `repr(C)` garde 24 ; `cold_path` pose des
  poids de branchement dans l'IR ; `algebraic_add` vectorise une somme (7 `vaddps` sur ymm/zmm contre 9 `vaddss` en
  chaîne) ; `get_unchecked` retire l'appel à `panic_bounds_check` ; `slice::sort` alloue un tampon pour 100 000
  éléments (tri stable, allocation documentée : B4 reste 1).
* Contre-épreuves (nightly) : `Vec::with_capacity_in` dans une arène (B2), `std::simd::f32x8` (C1), et, par le crate
  `libc` du sysroot (`#![feature(rustc_private)]`), `sched_setaffinity` (fil épinglé sur le CPU 1) et `mmap` d'un
  fichier relu comme `&[f32]` sans copie (D4, F4).

## 3. Cases discutables

| Langage | Case | Note | Fait établi | Lecture de la règle | Autre note possible |
|---|---|---|---|---|---|
| Rust | D4, F4 | 0 | `sched_setaffinity` et `mmap` marchent par le crate `libc` du sysroot, sur nightly avec `#![feature(rustc_private)]` | Le crate n'est pas dans l'API publique de `std` : c'est une FFI vers la glibc, du code non intrinsèque (0) | ½ si on le lit comme une unité interne livrée, accessible sur le canal instable |
