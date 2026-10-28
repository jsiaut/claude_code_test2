# Fiches chiffrées (générées par analysis/facts.py)

## 1. odin
* MS 72.3 ; C 81.8 (rang 3) ; E 77.7 (rang 2) ; D 50.4 (rang 7) ; rang Dirichlet 2 [1, 4] ; cellules 0,5 [1, 2] ; noyau retiré [1, 3]
* E par noyau (t*/t) : k1 0.95, k3 0.95, k4 0.94, k5 0.99, k6 0.71, k7 0.87, k8 0.37, k9 0.74, k10 0.72
* D : D1 0.13, D2 0.99, D3 0.64, D4 0.96
* K1 natural 42.6 ms, shuffled 43.1 ms (×1), aos 40.2 ms, soa 7.62 ms ; empreinte 64.0 o/particule
* K3 rmw_packed 2.28e+03 ms, rmw_padded 206 ms, sw_packed 150 ms, sw_padded 61.3 ms (faux partage ×11)
* K4 natural non trié 3.02 ms, trié 3.05 ms, sans branchement 3.28 ms ; vectorisation mesurée C3 = 1.0
* K5 natural 177 ms, tuned 4.78 ms (×37)
* K6 Q6 natural/tuned/mt 63.3 ms / 21.6 ms / 8.14 ms ; Q1 121 ms / 46.2 ms / 20.8 ms
* K7 natural 2.43e+03 ms, tuned 498 ms (×4.9)
* K8 natural 1.88e+03 ms, tuned 291 ms, tuned_alloc 1.07e+03 ms ; latence p50 97.3 µs, p99.9 668 µs, max 3.22e+03 µs (p99.9/p50 6.9)
* K9 natural 36.3 ms, tuned 36.8 ms, mt 19.7 ms
* K10 natural 1.67e+03 ms, tuned 17.6 ms (×95)
* K2 ns/saut 16K/256K/8M/256M : 1.58 / 4.9 / 147 / 394
* (CPU utilisateur + système) / mural, noyaux mono-thread : 0.98

## 2. cpp
* MS 71.9 ; C 84.7 (rang 1) ; E 72.4 (rang 3) ; D 53.3 (rang 2) ; rang Dirichlet 1 [1, 4] ; cellules 0,5 [1, 3] ; noyau retiré [1, 2]
* E par noyau (t*/t) : k1 0.96, k3 0.96, k4 0.44, k5 1.00, k6 0.90, k7 0.90, k8 0.59, k9 0.74, k10 0.38
* D : D1 0.12, D2 0.95, D3 0.98, D4 0.92
* K1 natural 37.5 ms, shuffled 41.2 ms (×1.1), aos 40.3 ms, soa 7.55 ms ; empreinte 64.02 o/particule
* K3 rmw_packed 2.18e+03 ms, rmw_padded 216 ms, sw_packed 123 ms, sw_padded 60.3 ms (faux partage ×10)
* K4 natural non trié 6.48 ms, trié 6.23 ms, sans branchement 6.51 ms ; vectorisation mesurée C3 = 1.0
* K5 natural 164 ms, tuned 4.75 ms (×35)
* K6 Q6 natural/tuned/mt 62.1 ms / 18.5 ms / 6.76 ms ; Q1 73.4 ms / 36.5 ms / 13.9 ms
* K7 natural 10.6 s, tuned 484 ms (×22)
* K8 natural 1.05e+03 ms, tuned 181 ms, tuned_alloc 281 ms ; latence p50 56.1 µs, p99.9 231 µs, max 1.33e+03 µs (p99.9/p50 4.1)
* K9 natural 36.3 ms, tuned 36.2 ms, mt 19.6 ms
* K10 natural 1.1e+03 ms, tuned 33.8 ms (×32)
* K2 ns/saut 16K/256K/8M/256M : 1.58 / 5.67 / 148 / 352
* (CPU utilisateur + système) / mural, noyaux mono-thread : 0.99

## 3. c
* MS 69.3 ; C 76.3 (rang 4) ; E 71.6 (rang 4) ; D 55.8 (rang 1) ; rang Dirichlet 3 [1, 4] ; cellules 0,5 [2, 5] ; noyau retiré [1, 4]
* E par noyau (t*/t) : k1 0.94, k3 0.98, k4 1.00, k5 0.98, k6 0.87, k7 1.00, k8 0.44, k9 0.90, k10 0.16
* D : D1 0.14, D2 1.00, D3 0.91, D4 1.00
* K1 natural 41.8 ms, shuffled 38.6 ms (×0.92), aos 37.9 ms, soa 7.72 ms ; empreinte 64.02 o/particule
* K3 rmw_packed 2.54e+03 ms, rmw_padded 222 ms, sw_packed 156 ms, sw_padded 59.5 ms (faux partage ×11)
* K4 natural non trié 4.05 ms, trié 3.67 ms, sans branchement 2.85 ms ; vectorisation mesurée C3 = 1.0
* K5 natural 169 ms, tuned 4.84 ms (×35)
* K6 Q6 natural/tuned/mt 60.9 ms / 21.4 ms / 8.34 ms ; Q1 82.1 ms / 32.1 ms / 13.2 ms
* K7 natural 5.11e+03 ms, tuned 436 ms (×12)
* K8 natural 980 ms, tuned 243 ms, tuned_alloc — ; latence p50 51.5 µs, p99.9 218 µs, max 1.37e+03 µs (p99.9/p50 4.2)
* K9 natural 37.9 ms, tuned 37.8 ms, mt 12.8 ms
* K10 natural 836 ms, tuned 80 ms (×10)
* K2 ns/saut 16K/256K/8M/256M : 1.62 / 4.35 / 149 / 348
* (CPU utilisateur + système) / mural, noyaux mono-thread : 0.98

## 4. c3
* MS 66.8 ; C 74.4 (rang 6) ; E 68.9 (rang 7) ; D 52.9 (rang 3) ; rang Dirichlet 5 [4, 8] ; cellules 0,5 [3, 7] ; noyau retiré [4, 5]
* E par noyau (t*/t) : k1 0.99, k3 0.96, k4 0.86, k5 0.77, k6 0.90, k7 0.92, k8 0.45, k9 0.76, k10 0.20
* D : D1 0.13, D2 1.00, D3 0.91, D4 0.90
* K1 natural 42.5 ms, shuffled 41.8 ms (×0.98), aos 37.9 ms, soa 7.3 ms ; empreinte 64.03 o/particule
* K3 rmw_packed 2.79e+03 ms, rmw_padded 222 ms, sw_packed 136 ms, sw_padded 60.4 ms (faux partage ×13)
* K4 natural non trié 3.42 ms, trié 3.46 ms, sans branchement 3.32 ms ; vectorisation mesurée C3 = 1.0
* K5 natural 166 ms, tuned 6.14 ms (×27)
* K6 Q6 natural/tuned/mt 63.4 ms / 19.9 ms / 7.82 ms ; Q1 112 ms / 33.7 ms / 12.4 ms
* K7 natural 7.1e+03 ms, tuned 476 ms (×15)
* K8 natural 1.49e+03 ms, tuned 242 ms, tuned_alloc 535 ms ; latence p50 76.7 µs, p99.9 303 µs, max 2.21e+03 µs (p99.9/p50 4.0)
* K9 natural 37.4 ms, tuned 36.4 ms, mt 18.6 ms
* K10 natural 971 ms, tuned 64.4 ms (×15)
* K2 ns/saut 16K/256K/8M/256M : 2.19 / 4.43 / 149 / 354
* (CPU utilisateur + système) / mural, noyaux mono-thread : 0.99

## 5. zig
* MS 66.7 ; C 82.0 (rang 2) ; E 64.3 (rang 11) ; D 49.2 (rang 8) ; rang Dirichlet 5 [3, 10] ; cellules 0,5 [3, 8] ; noyau retiré [3, 6]
* E par noyau (t*/t) : k1 0.99, k3 0.97, k4 0.33, k5 0.85, k6 0.87, k7 0.90, k8 0.42, k9 0.70, k10 0.31
* D : D1 0.15, D2 0.94, D3 0.57, D4 0.96
* K1 natural 38.6 ms, shuffled 43.3 ms (×1.1), aos 42.4 ms, soa 7.3 ms ; empreinte 64.0 o/particule
* K3 rmw_packed 2.32e+03 ms, rmw_padded 210 ms, sw_packed 143 ms, sw_padded 60.2 ms (faux partage ×11)
* K4 natural non trié 8.7 ms, trié 8.98 ms, sans branchement 9.97 ms ; vectorisation mesurée C3 = 0.0
* K5 natural 166 ms, tuned 5.63 ms (×29)
* K6 Q6 natural/tuned/mt 67.5 ms / 17.7 ms / 8.05 ms ; Q1 77.7 ms / 34.6 ms / 14.7 ms
* K7 natural 1.66e+03 ms, tuned 483 ms (×3.4)
* K8 natural 1.05e+03 ms, tuned 256 ms, tuned_alloc 899 ms ; latence p50 56.1 µs, p99.9 298 µs, max 3.07e+03 µs (p99.9/p50 5.3)
* K9 natural 40.4 ms, tuned 36.4 ms, mt 22 ms
* K10 natural 784 ms, tuned 41.6 ms (×19)
* K2 ns/saut 16K/256K/8M/256M : 1.57 / 4.83 / 153 / 364
* (CPU utilisateur + système) / mural, noyaux mono-thread : 0.99

## 6. chapel
* MS 65.5 ; C 59.1 (rang 12) ; E 79.4 (rang 1) ; D 52.2 (rang 4) ; rang Dirichlet 6 [1, 11] ; cellules 0,5 [4, 10] ; noyau retiré [4, 8]
* E par noyau (t*/t) : k1 0.93, k3 1.00, k4 0.91, k5 0.88, k6 0.71, k7 0.92, k8 0.39, k9 0.96, k10 0.68
* D : D1 0.11, D2 1.00, D3 0.80, D4 0.97
* K1 natural 40.4 ms, shuffled 38.7 ms (×0.96), aos 50.8 ms, soa 7.75 ms ; empreinte 64.02 o/particule
* K3 rmw_packed 2.53e+03 ms, rmw_padded 208 ms, sw_packed 122 ms, sw_padded 58.1 ms (faux partage ×12)
* K4 natural non trié 3.12 ms, trié 3.44 ms, sans branchement 3.29 ms ; vectorisation mesurée C3 = 1.0
* K5 natural 176 ms, tuned 5.41 ms (×32)
* K6 Q6 natural/tuned/mt 63.5 ms / 22.8 ms / 6.49 ms ; Q1 117 ms / 48.6 ms / 22.9 ms
* K7 natural 3.52e+03 ms, tuned 475 ms (×7.4)
* K8 natural 1.92e+03 ms, tuned 278 ms, tuned_alloc — ; latence p50 94 µs, p99.9 495 µs, max 2.61e+03 µs (p99.9/p50 5.3)
* K9 natural 38.9 ms, tuned 43.1 ms, mt 10.8 ms
* K10 natural 3.3e+03 ms, tuned 18.6 ms (×1.8e+02)
* K2 ns/saut 16K/256K/8M/256M : 1.72 / 4.49 / 148 / 386
* (CPU utilisateur + système) / mural, noyaux mono-thread : 1.23

## 7. nim
* MS 64.6 ; C 73.4 (rang 7) ; E 65.2 (rang 10) ; D 51.2 (rang 5) ; rang Dirichlet 6 [5, 10] ; cellules 0,5 [4, 10] ; noyau retiré [7, 9]
* E par noyau (t*/t) : k1 1.00, k3 0.97, k4 0.79, k5 0.77, k6 0.50, k7 0.85, k8 0.34, k9 0.80, k10 0.32
* D : D1 0.14, D2 1.00, D3 0.66, D4 0.98
* K1 natural 44 ms, shuffled 38.5 ms (×0.87), aos 39.8 ms, soa 7.24 ms ; empreinte 64.0 o/particule
* K3 rmw_packed 2.67e+03 ms, rmw_padded 207 ms, sw_packed 160 ms, sw_padded 59.6 ms (faux partage ×13)
* K4 natural non trié 4.01 ms, trié 3.4 ms, sans branchement 3.63 ms ; vectorisation mesurée C3 = 0.5
* K5 natural 184 ms, tuned 6.15 ms (×30)
* K6 Q6 natural/tuned/mt 65 ms / 22.1 ms / 8.74 ms ; Q1 94.9 ms / 98.1 ms / 37.8 ms
* K7 natural 2.09e+03 ms, tuned 515 ms (×4.1)
* K8 natural 899 ms, tuned 320 ms, tuned_alloc — ; latence p50 44.9 µs, p99.9 234 µs, max 1.86e+03 µs (p99.9/p50 5.2)
* K9 natural 71.1 ms, tuned 36.6 ms, mt 16.6 ms
* K10 natural 1.22e+03 ms, tuned 39.9 ms (×31)
* K2 ns/saut 16K/256K/8M/256M : 1.58 / 4.69 / 142 / 327
* (CPU utilisateur + système) / mural, noyaux mono-thread : 0.99

## 8. d
* MS 64.4 ; C 74.5 (rang 5) ; E 70.8 (rang 5) ; D 40.2 (rang 14) ; rang Dirichlet 9 [5, 12] ; cellules 0,5 [4, 10] ; noyau retiré [7, 10]
* E par noyau (t*/t) : k1 0.99, k3 0.85, k4 0.91, k5 0.83, k6 0.53, k7 0.89, k8 0.40, k9 0.76, k10 0.48
* D : D1 0.10, D2 1.00, D3 0.06, D4 0.96
* K1 natural 43 ms, shuffled 41.3 ms (×0.96), aos 45.9 ms, soa 7.29 ms ; empreinte 64.0 o/particule
* K3 rmw_packed 2.43e+03 ms, rmw_padded 213 ms, sw_packed 135 ms, sw_padded 68.1 ms (faux partage ×11)
* K4 natural non trié 3.12 ms, trié 3.47 ms, sans branchement 3.53 ms ; vectorisation mesurée C3 = 0.5
* K5 natural 170 ms, tuned 5.7 ms (×30)
* K6 Q6 natural/tuned/mt 57.7 ms / 20.1 ms / 7.57 ms ; Q1 79.3 ms / 110 ms / 43.3 ms
* K7 natural 6.03e+03 ms, tuned 491 ms (×12)
* K8 natural 2.99e+03 ms, tuned 272 ms, tuned_alloc — ; latence p50 82.2 µs, p99.9 1.25e+03 µs, max 1.27e+05 µs (p99.9/p50 15.2)
* K9 natural 55.6 ms, tuned 37.1 ms, mt 18.3 ms
* K10 natural 2.72e+03 ms, tuned 26.2 ms (×1e+02)
* K2 ns/saut 16K/256K/8M/256M : 1.59 / 4.95 / 148 / 331
* (CPU utilisateur + système) / mural, noyaux mono-thread : 0.99

## 9. rust
* MS 64.4 ; C 73.1 (rang 8) ; E 67.2 (rang 8) ; D 47.8 (rang 10) ; rang Dirichlet 7 [5, 9] ; cellules 0,5 [5, 10] ; noyau retiré [6, 10]
* E par noyau (t*/t) : k1 0.99, k3 0.96, k4 0.87, k5 0.71, k6 0.77, k7 0.88, k8 0.40, k9 0.79, k10 0.23
* D : D1 0.18, D2 1.00, D3 0.34, D4 0.95
* K1 natural 44.3 ms, shuffled 38.6 ms (×0.87), aos 40.2 ms, soa 7.29 ms ; empreinte 64.01 o/particule
* K3 rmw_packed 2.39e+03 ms, rmw_padded 220 ms, sw_packed 152 ms, sw_padded 60.5 ms (faux partage ×11)
* K4 natural non trié 3.27 ms, trié 3.8 ms, sans branchement 3.58 ms ; vectorisation mesurée C3 = 0.5
* K5 natural 167 ms, tuned 6.67 ms (×25)
* K6 Q6 natural/tuned/mt 63.7 ms / 21.7 ms / 8.03 ms ; Q1 116 ms / 38 ms / 18.6 ms
* K7 natural 3.77e+03 ms, tuned 498 ms (×7.6)
* K8 natural 1.13e+03 ms, tuned 270 ms, tuned_alloc — ; latence p50 54.3 µs, p99.9 538 µs, max 4.5e+03 µs (p99.9/p50 9.9)
* K9 natural 72.7 ms, tuned 36.2 ms, mt 17.3 ms
* K10 natural 86.6 ms, tuned 56.4 ms (×1.5)
* K2 ns/saut 16K/256K/8M/256M : 1.63 / 4.98 / 153 / 360
* (CPU utilisateur + système) / mural, noyaux mono-thread : 0.98

## 10. ada
* MS 63.7 ; C 70.3 (rang 9) ; E 69.0 (rang 6) ; D 46.1 (rang 11) ; rang Dirichlet 9 [6, 10] ; cellules 0,5 [6, 10] ; noyau retiré [7, 10]
* E par noyau (t*/t) : k1 0.95, k3 0.96, k4 0.52, k5 0.90, k6 0.50, k7 0.82, k8 1.00, k9 0.52, k10 0.39
* D : D1 0.08, D2 1.00, D3 0.66, D4 0.86
* K1 natural 43.1 ms, shuffled 42.1 ms (×0.98), aos 40.6 ms, soa 7.66 ms ; empreinte 64.0 o/particule
* K3 rmw_packed 2.77e+03 ms, rmw_padded 264 ms, sw_packed 144 ms, sw_padded 60.5 ms (faux partage ×11)
* K4 natural non trié 7.62 ms, trié 8.26 ms, sans branchement 5.43 ms ; vectorisation mesurée C3 = 0.5
* K5 natural 169 ms, tuned 5.29 ms (×32)
* K6 Q6 natural/tuned/mt 80.9 ms / 19.6 ms / 19.2 ms ; Q1 194 ms / 57.1 ms / 31.1 ms
* K7 natural 11.1 s, tuned 533 ms (×21)
* K8 natural 1.03e+03 ms, tuned 108 ms, tuned_alloc 187 ms ; latence p50 52 µs, p99.9 284 µs, max 2.07e+03 µs (p99.9/p50 5.5)
* K9 natural 70.7 ms, tuned 52.3 ms, mt 27.5 ms
* K10 natural 4.55e+03 ms, tuned 32.9 ms (×1.4e+02)
* K2 ns/saut 16K/256K/8M/256M : 2.19 / 5 / 151 / 340
* (CPU utilisateur + système) / mural, noyaux mono-thread : 0.98

## 11. fortran
* MS 58.1 ; C 53.6 (rang 14) ; E 66.5 (rang 9) ; D 50.9 (rang 6) ; rang Dirichlet 11 [8, 14] ; cellules 0,5 [11, 12] ; noyau retiré [11, 13]
* E par noyau (t*/t) : k1 0.97, k3 0.83, k4 0.25, k5 0.61, k6 0.77, k7 0.73, k8 0.56, k9 0.96, k10 0.66
* D : D1 0.12, D2 1.00, D3 0.77, D4 0.91
* K1 natural 39.5 ms, shuffled 39.2 ms (×0.99), aos 41.3 ms, soa 7.47 ms ; empreinte 64.0 o/particule
* K3 rmw_packed 2.39e+03 ms, rmw_padded 229 ms, sw_packed 155 ms, sw_padded 69.6 ms (faux partage ×10)
* K4 natural non trié 11.2 ms, trié 11.2 ms, sans branchement 12.4 ms ; vectorisation mesurée C3 = 0.5
* K5 natural 172 ms, tuned 7.76 ms (×22)
* K6 Q6 natural/tuned/mt 74.5 ms / 20.8 ms / 5.98 ms ; Q1 93.7 ms / 47.9 ms / 19.8 ms
* K7 natural 5.2e+03 ms, tuned 593 ms (×8.8)
* K8 natural 906 ms, tuned 193 ms, tuned_alloc — ; latence p50 48.1 µs, p99.9 263 µs, max 1.39e+03 µs (p99.9/p50 5.5)
* K9 natural 36.5 ms, tuned 37.2 ms, mt 11.7 ms
* K10 natural 888 ms, tuned 19.3 ms (×46)
* K2 ns/saut 16K/256K/8M/256M : 1.85 / 4.92 / 154 / 341
* (CPU utilisateur + système) / mural, noyaux mono-thread : 0.99

## 12. mojo
* MS 56.9 ; C 58.7 (rang 13) ; E 61.0 (rang 12) ; D 48.1 (rang 9) ; rang Dirichlet 12 [11, 13] ; cellules 0,5 [11, 12] ; noyau retiré [11, 12]
* E par noyau (t*/t) : k1 0.95, k3 0.93, k4 0.26, k5 0.90, k6 0.77, k7 0.87, k8 0.51, k9 0.84, k10 0.20
* D : D1 0.08, D2 1.00, D3 0.78, D4 0.87
* K1 natural 40.6 ms, shuffled 38.1 ms (×0.94), aos 38 ms, soa 7.61 ms ; empreinte 64.0 o/particule
* K3 rmw_packed 2.22e+03 ms, rmw_padded 212 ms, sw_packed 123 ms, sw_padded 62.8 ms (faux partage ×10)
* K4 natural non trié 11 ms, trié 11.4 ms, sans branchement 11.1 ms ; vectorisation mesurée C3 = 0.0
* K5 natural 173 ms, tuned 5.31 ms (×33)
* K6 Q6 natural/tuned/mt 56.9 ms / 19.7 ms / 8.47 ms ; Q1 229 ms / 43.9 ms / 16.2 ms
* K7 natural 4.82e+03 ms, tuned 499 ms (×9.7)
* K8 natural 1.7e+03 ms, tuned 211 ms, tuned_alloc — ; latence p50 80.9 µs, p99.9 444 µs, max 2.25e+03 µs (p99.9/p50 5.5)
* K9 natural 262 ms, tuned 38.2 ms, mt 14.6 ms
* K10 natural 1.99e+03 ms, tuned 64.2 ms (×31)
* K2 ns/saut 16K/256K/8M/256M : 1.95 / 5.19 / 158 / 366
* (CPU utilisateur + système) / mural, noyaux mono-thread : 0.98

## 13. julia
* MS 52.6 ; C 65.4 (rang 11) ; E 47.3 (rang 14) ; D 43.1 (rang 13) ; rang Dirichlet 13 [10, 14] ; cellules 0,5 [12, 14] ; noyau retiré [12, 13]
* E par noyau (t*/t) : k1 0.91, k3 0.91, k4 0.95, k5 0.68, k6 0.52, k7 0.60, k8 0.31, k9 0.81, k10 0.03
* D : D1 0.14, D2 1.00, D3 0.09, D4 0.98
* K1 natural 40.6 ms, shuffled 38.1 ms (×0.94), aos 60 ms, soa 7.92 ms ; empreinte 64.0 o/particule
* K3 rmw_packed 2.23e+03 ms, rmw_padded 219 ms, sw_packed 129 ms, sw_padded 64.1 ms (faux partage ×10)
* K4 natural non trié 2.99 ms, trié 3.91 ms, sans branchement 3.45 ms ; vectorisation mesurée C3 = 1.0
* K5 natural 179 ms, tuned 6.98 ms (×26)
* K6 Q6 natural/tuned/mt 78.3 ms / 20.2 ms / 8.6 ms ; Q1 132 ms / 95 ms / 35.1 ms
* K7 natural 3.27e+03 ms, tuned 731 ms (×4.5)
* K8 natural 986 ms, tuned 345 ms, tuned_alloc — ; latence p50 40.5 µs, p99.9 2.84e+03 µs, max 6.94e+03 µs (p99.9/p50 70.0)
* K9 natural 37.9 ms, tuned 38.1 ms, mt 15.8 ms
* K10 natural 1.09e+03 ms, tuned 448 ms (×2.4)
* K2 ns/saut 16K/256K/8M/256M : 1.61 / 4.46 / 153 / 334
* (CPU utilisateur + système) / mural, noyaux mono-thread : 1.04

## 14. csharp
* MS 48.6 ; C 65.8 (rang 10) ; E 44.3 (rang 15) ; D 31.6 (rang 17) ; rang Dirichlet 14 [12, 16] ; cellules 0,5 [14, 15] ; noyau retiré [14, 15]
* E par noyau (t*/t) : k1 0.91, k3 0.88, k4 0.17, k5 0.28, k6 0.60, k7 0.63, k8 0.31, k9 0.64, k10 0.22
* D : D1 0.06, D2 0.39, D3 0.35, D4 0.87
* K1 natural 55.1 ms, shuffled 259 ms (×4.7), aos 39 ms, soa 7.93 ms ; empreinte 88.0 o/particule
* K3 rmw_packed 2.55e+03 ms, rmw_padded 272 ms, sw_packed 116 ms, sw_padded 65.9 ms (faux partage ×9.4)
* K4 natural non trié 83.2 ms, trié 11.3 ms, sans branchement 16.3 ms ; vectorisation mesurée C3 = 0.0
* K5 natural 168 ms, tuned 17.3 ms (×9.7)
* K6 Q6 natural/tuned/mt 159 ms / 20.7 ms / 8.76 ms ; Q1 186 ms / 68.4 ms / 26.1 ms
* K7 natural 5.65e+03 ms, tuned 687 ms (×8.2)
* K8 natural 880 ms, tuned 347 ms, tuned_alloc — ; latence p50 43.7 µs, p99.9 776 µs, max 1.85e+03 µs (p99.9/p50 17.8)
* K9 natural 123 ms, tuned 39.2 ms, mt 24.3 ms
* K10 natural 2.9e+03 ms, tuned 56.8 ms (×51)
* K2 ns/saut 16K/256K/8M/256M : 1.92 / 5.58 / 151 / 353
* (CPU utilisateur + système) / mural, noyaux mono-thread : 0.99

## 15. java
* MS 46.7 ; C 41.5 (rang 16) ; E 60.5 (rang 13) ; D 32.1 (rang 16) ; rang Dirichlet 15 [13, 16] ; cellules 0,5 [14, 15] ; noyau retiré [14, 15]
* E par noyau (t*/t) : k1 0.83, k3 0.93, k4 0.42, k5 0.56, k6 0.50, k7 0.37, k8 0.45, k9 0.71, k10 1.00
* D : D1 0.09, D2 0.41, D3 0.20, D4 0.91
* K1 natural 56.3 ms, shuffled 276 ms (×4.9), aos 42.5 ms, soa 8.74 ms ; empreinte 78.01 o/particule
* K3 rmw_packed 2.32e+03 ms, rmw_padded 223 ms, sw_packed 142 ms, sw_padded 62.8 ms (faux partage ×10)
* K4 natural non trié 79.1 ms, trié 8.37 ms, sans branchement 6.74 ms ; vectorisation mesurée C3 = 0.5
* K5 natural 179 ms, tuned 8.5 ms (×21)
* K6 Q6 natural/tuned/mt 111 ms / 25.8 ms / 9.65 ms ; Q1 112 ms / 89.3 ms / 30.7 ms
* K7 natural 9.16e+03 ms, tuned 1.17e+03 ms (×7.8)
* K8 natural 301 ms, tuned 239 ms, tuned_alloc — ; latence p50 14.7 µs, p99.9 134 µs, max 3.6e+03 µs (p99.9/p50 9.1)
* K9 natural 39.5 ms, tuned 41 ms, mt 19.4 ms
* K10 natural 815 ms, tuned 12.7 ms (×64)
* K2 ns/saut 16K/256K/8M/256M : 1.75 / 5.35 / 146 / 365
* (CPU utilisateur + système) / mural, noyaux mono-thread : 1.14

## 16. go
* MS 39.6 ; C 44.9 (rang 15) ; E 32.3 (rang 17) ; D 43.7 (rang 12) ; rang Dirichlet 16 [14, 16] ; cellules 0,5 [16, 16] ; noyau retiré [16, 16]
* E par noyau (t*/t) : k1 0.96, k3 0.27, k4 0.25, k5 0.39, k6 0.54, k7 0.62, k8 0.26, k9 0.47, k10 0.04
* D : D1 0.09, D2 1.00, D3 0.35, D4 0.94
* K1 natural 50.7 ms, shuffled 47.8 ms (×0.94), aos 47.2 ms, soa 7.55 ms ; empreinte 64.0 o/particule
* K3 rmw_packed 2.38e+03 ms, rmw_padded 216 ms, sw_packed 4.18e+03 ms, sw_padded 358 ms (faux partage ×11)
* K4 natural non trié 11.6 ms, trié 11.1 ms, sans branchement 14.2 ms ; vectorisation mesurée C3 = 0.0
* K5 natural 260 ms, tuned 12.2 ms (×21)
* K6 Q6 natural/tuned/mt 138 ms / 20.1 ms / 7.81 ms ; Q1 121 ms / 86.4 ms / 37.9 ms
* K7 natural 5.8e+03 ms, tuned 706 ms (×8.2)
* K8 natural 1.59e+03 ms, tuned 411 ms, tuned_alloc — ; latence p50 73 µs, p99.9 1.13e+03 µs, max 3.59e+03 µs (p99.9/p50 15.5)
* K9 natural 114 ms, tuned 116 ms, mt 15.3 ms
* K10 natural 571 ms, tuned 332 ms (×1.7)
* K2 ns/saut 16K/256K/8M/256M : 1.67 / 4.9 / 152 / 374
* (CPU utilisateur + système) / mural, noyaux mono-thread : 1.00

## 17. haskell
* MS 33.6 ; C 33.4 (rang 17) ; E 32.6 (rang 16) ; D 35.7 (rang 15) ; rang Dirichlet 17 [17, 17] ; cellules 0,5 [17, 17] ; noyau retiré [17, 17]
* E par noyau (t*/t) : k1 0.78, k3 0.21, k4 0.26, k5 0.58, k6 0.35, k7 0.60, k8 0.09, k9 0.70, k10 0.13
* D : D1 0.03, D2 0.82, D3 0.21, D4 0.92
* K1 natural 71 ms, shuffled 66.1 ms (×0.93), aos 40 ms, soa 9.28 ms ; empreinte 96.0 o/particule
* K3 rmw_packed 2.45e+03 ms, rmw_padded 282 ms, sw_packed 4.11e+03 ms, sw_padded 337 ms (faux partage ×8.7)
* K4 natural non trié 72.5 ms, trié 8.93 ms, sans branchement 11 ms ; vectorisation mesurée C3 = 0.0
* K5 natural 639 ms, tuned 8.19 ms (×78)
* K6 Q6 natural/tuned/mt 76.7 ms / 70.6 ms / 17.4 ms ; Q1 103 ms / 70.2 ms / 32 ms
* K7 natural 87.7 s, tuned 725 ms (×1.2e+02)
* K8 natural 2.6e+03 ms, tuned 1.18e+03 ms, tuned_alloc — ; latence p50 97.7 µs, p99.9 2.22e+03 µs, max 8.74e+03 µs (p99.9/p50 22.7)
* K9 natural 402 ms, tuned 40.3 ms, mt 19.5 ms
* K10 natural 1e+03 ms, tuned 101 ms (×9.9)
* K2 ns/saut 16K/256K/8M/256M : 1.88 / 4.76 / 139 / 367
* (CPU utilisateur + système) / mural, noyaux mono-thread : 1.00

## 18. ocaml
* MS 21.8 ; C 24.7 (rang 18) ; E 16.8 (rang 18) ; D 25.5 (rang 18) ; rang Dirichlet 18 [18, 18] ; cellules 0,5 [18, 18] ; noyau retiré [18, 18]
* E par noyau (t*/t) : k1 0.68, k3 0.19, k4 0.08, k5 0.04, k6 0.11, k7 0.32, k8 0.40, k9 0.38, k10 0.06
* D : D1 0.05, D2 0.25, D3 0.22, D4 0.78
* K1 natural 110 ms, shuffled 761 ms (×6.9), aos 308 ms, soa 10.7 ms ; empreinte 144.0 o/particule
* K3 rmw_packed 582 ms, rmw_padded 309 ms, sw_packed 946 ms, sw_padded 429 ms (faux partage ×1.9)
* K4 natural non trié 94.3 ms, trié 18.3 ms, sans branchement 37.5 ms ; vectorisation mesurée C3 = 0.0
* K5 natural 385 ms, tuned 132 ms (×2.9)
* K6 Q6 natural/tuned/mt 204 ms / 251 ms / 80.3 ms ; Q1 232 ms / 208 ms / 78.1 ms
* K7 natural 12.4 s, tuned 1.36e+03 ms (×9.1)
* K8 natural 319 ms, tuned 268 ms, tuned_alloc — ; latence p50 15 µs, p99.9 191 µs, max 2.2e+03 µs (p99.9/p50 12.7)
* K9 natural 112 ms, tuned 62.6 ms, mt 42.2 ms
* K10 natural 1.96e+03 ms, tuned 229 ms (×8.6)
* K2 ns/saut 16K/256K/8M/256M : 2.55 / 5.67 / 152 / 186
* (CPU utilisateur + système) / mural, noyaux mono-thread : 0.99

## 19. js
* MS 14.1 ; C 11.6 (rang 20) ; E 11.1 (rang 19) ; D 22.3 (rang 19) ; rang Dirichlet 19 [19, 20] ; cellules 0,5 [19, 19] ; noyau retiré [19, 19]
* E par noyau (t*/t) : k1 0.37, k3 0.06, k4 0.11, k5 0.02, k6 0.11, k7 0.16, k8 0.15, k9 0.33, k10 0.05
* D : D1 0.03, D2 0.16, D3 0.04, D4 0.89
* K1 natural 353 ms, shuffled 2.08e+03 ms (×5.9), aos 49.7 ms, soa 19.4 ms ; empreinte 416.4 o/particule
* K3 rmw_packed 7.78e+03 ms, rmw_padded 924 ms, sw_packed 10.8 s, sw_padded 1.59e+03 ms (faux partage ×8.4)
* K4 natural non trié 87.3 ms, trié 23.4 ms, sans branchement 25.3 ms ; vectorisation mesurée C3 = 0.0
* K5 natural 212 ms, tuned 209 ms (×1)
* K6 Q6 natural/tuned/mt 143 ms / 123 ms / 45.6 ms ; Q1 395 ms / 421 ms / 134 ms
* K7 natural 14.3 s, tuned 2.72e+03 ms (×5.2)
* K8 natural 1.79e+03 ms, tuned 717 ms, tuned_alloc — ; latence p50 54.4 µs, p99.9 881 µs, max 1.7e+05 µs (p99.9/p50 16.2)
* K9 natural 165 ms, tuned 94.8 ms, mt 38.8 ms
* K10 natural 10.5 s, tuned 248 ms (×42)
* K2 ns/saut 16K/256K/8M/256M : 1.66 / 5.73 / 159 / 371
* (CPU utilisateur + système) / mural, noyaux mono-thread : 1.00

## 20. python
* MS 9.8 ; C 22.4 (rang 19) ; E 0.5 (rang 21) ; D 7.0 (rang 21) ; rang Dirichlet 20 [19, 21] ; cellules 0,5 [20, 20] ; noyau retiré [20, 20]
* E par noyau (t*/t) : k1 0.01, k3 0.00, k4 0.00, k5 0.00, k6 0.00, k7 0.02, k8 0.01, k9 0.01, k10 0.00
* D : D1 0.00, D2 0.13, D3 0.14, D4 0.14
* K1 natural 924 ms, shuffled 4.93e+03 ms (×5.3), aos 1.09e+03 ms, soa 938 ms ; empreinte 749.65 o/particule
* K3 rmw_packed 33.9 s, rmw_padded 33.1 s, sw_packed 18.1 s, sw_padded 17.5 s (faux partage ×1)
* K4 natural non trié 668 ms, trié 540 ms, sans branchement 995 ms ; vectorisation mesurée C3 = 0.0
* K5 natural 11.2 s, tuned 4.41e+03 ms (×2.5)
* K6 Q6 natural/tuned/mt 1.76e+03 ms / 1.95e+03 ms / 2.38e+03 ms ; Q1 10.8 s / 7.95e+03 ms / 9.03e+03 ms
* K7 natural 28.3 s, tuned 28.4 s (×0.99)
* K8 natural 25.7 s, tuned 17 s, tuned_alloc — ; latence p50 1.05e+03 µs, p99.9 4.58e+03 µs, max 1.08e+06 µs (p99.9/p50 4.4)
* K9 natural 1.98e+03 ms, tuned 2.28e+03 ms, mt 2.55e+03 ms
* K10 natural 7.99e+03 ms, tuned 2.73e+03 ms (×2.9)
* K2 ns/saut 16K/256K/8M/256M : 48.8 / 46.7 / 187 / 395
* (CPU utilisateur + système) / mural, noyaux mono-thread : 0.99

## 21. lua
* MS 4.5 ; C 2.8 (rang 21) ; E 1.3 (rang 20) ; D 11.8 (rang 20) ; rang Dirichlet 21 [20, 21] ; cellules 0,5 [21, 21] ; noyau retiré [21, 21]
* E par noyau (t*/t) : k1 0.02, k3 0.01, k4 0.00, k5 0.00, k6 0.01, k7 0.04, k8 0.02, k9 0.02, k10 0.04
* D : D1 0.01, D2 0.15, D3 0.10, D4 0.37
* K1 natural 679 ms, shuffled 4.1e+03 ms (×6), aos 427 ms, soa 291 ms ; empreinte 449.0 o/particule
* K3 rmw_packed 2.47e+03 ms, rmw_padded 3.94e+03 ms, sw_packed 2.69e+03 ms, sw_padded 4.27e+03 ms (faux partage ×0.63)
* K4 natural non trié 1.04e+03 ms, trié 875 ms, sans branchement 991 ms ; vectorisation mesurée C3 = 0.0
* K5 natural 2.86e+03 ms, tuned 2.93e+03 ms (×0.98)
* K6 Q6 natural/tuned/mt 627 ms / 1.65e+03 ms / 1.6e+03 ms ; Q1 3.14e+03 ms / 2.22e+03 ms / 2.29e+03 ms
* K7 natural 11.3 s, tuned 10.1 s (×1.1)
* K8 natural 10.9 s, tuned 5.01e+03 ms, tuned_alloc — ; latence p50 472 µs, p99.9 3.78e+04 µs, max 5.03e+04 µs (p99.9/p50 80.0)
* K9 natural 822 ms, tuned 1.3e+03 ms, mt 1.25e+03 ms
* K10 natural 598 ms, tuned 294 ms (×2)
* K2 ns/saut 16K/256K/8M/256M : 9.14 / 12.7 / 183 / 444
* (CPU utilisateur + système) / mural, noyaux mono-thread : 0.98

## annexe. c_gcc
* MS 69.3 ; C 76.3 (rang —) ; E 73.8 (rang —) ; D 52.4 (rang —) ; rang Dirichlet —  ; cellules 0,5  ; noyau retiré 
* E par noyau (t*/t) : k1 0.98, k3 0.93, k4 0.55, k5 1.03, k6 0.88, k7 0.86, k8 0.70, k9 0.95, k10 0.25
* D : D1 0.13, D2 1.00, D3 0.74, D4 0.99
* K1 natural 52.1 ms, shuffled 41.3 ms (×0.79), aos 39.9 ms, soa 7.42 ms ; empreinte 64.02 o/particule
* K3 rmw_packed 2.43e+03 ms, rmw_padded 227 ms, sw_packed 136 ms, sw_padded 62.8 ms (faux partage ×11)
* K4 natural non trié 6.06 ms, trié 6.3 ms, sans branchement 5.22 ms ; vectorisation mesurée C3 = 1.0
* K5 natural 163 ms, tuned 4.64 ms (×35)
* K6 Q6 natural/tuned/mt 64.8 ms / 19.8 ms / 7.91 ms ; Q1 80 ms / 33.7 ms / 13.4 ms
* K7 natural 5.35e+03 ms, tuned 506 ms (×11)
* K8 natural 1.01e+03 ms, tuned 155 ms, tuned_alloc — ; latence p50 45.4 µs, p99.9 209 µs, max 1.71e+03 µs (p99.9/p50 4.6)
* K9 natural 36.6 ms, tuned 35.3 ms, mt 12.2 ms
* K10 natural 885 ms, tuned 50 ms (×18)
* K2 ns/saut 16K/256K/8M/256M : 1.56 / 4.43 / 148 / 363
* (CPU utilisateur + système) / mural, noyaux mono-thread : 0.98

## annexe. fortran_flang
* MS 52.3 ; C 53.6 (rang —) ; E 51.9 (rang —) ; D 51.0 (rang —) ; rang Dirichlet —  ; cellules 0,5  ; noyau retiré 
* E par noyau (t*/t) : k1 0.95, k3 1.03, k4 0.72, k5 0.55, k6 0.66, k7 0.60, k8 0.33, k9 0.98, k10 0.05
* D : D1 0.10, D2 0.98, D3 0.84, D4 0.93
* K1 natural 40.3 ms, shuffled 41.5 ms (×1), aos 40.5 ms, soa 7.63 ms ; empreinte 64.03 o/particule
* K3 rmw_packed 2.29e+03 ms, rmw_padded 209 ms, sw_packed 105 ms, sw_padded 56.2 ms (faux partage ×11)
* K4 natural non trié 3.93 ms, trié 4.03 ms, sans branchement 4.86 ms ; vectorisation mesurée C3 = 1.0
* K5 natural 171 ms, tuned 8.71 ms (×20)
* K6 Q6 natural/tuned/mt 19.7 ms / 19 ms / 7.14 ms ; Q1 56.4 ms / 75.5 ms / 29.8 ms
* K7 natural 9.49e+03 ms, tuned 722 ms (×13)
* K8 natural 4.11e+03 ms, tuned 323 ms, tuned_alloc — ; latence p50 208 µs, p99.9 1.07e+03 µs, max 5.39e+03 µs (p99.9/p50 5.1)
* K9 natural 36.1 ms, tuned 38 ms, mt 11.3 ms
* K10 natural 3.68e+03 ms, tuned 234 ms (×16)
* K2 ns/saut 16K/256K/8M/256M : 1.67 / 5.26 / 141 / 348
* (CPU utilisateur + système) / mural, noyaux mono-thread : 0.99

## annexe. luajit
* C 2.8125, E None, D 25.70300735225532
* E par noyau (t*/t) : k1 0.71, k4 0.13, k5 0.06, k6 0.16, k7 0.23, k8 0.03, k9 0.48, k10 0.58
* D : D1 0.05, D2 0.21, D3 0.65, D4 0.51
* K1 natural 240 ms, shuffled 850 ms (×3.5), aos 44.9 ms, soa 10.3 ms ; empreinte 428.0 o/particule
* K3 rmw_packed —, rmw_padded —, sw_packed —, sw_padded — (faux partage ×—)
* K4 natural non trié 140 ms, trié 58.4 ms, sans branchement 21.4 ms ; vectorisation mesurée C3 = 0.0
* K5 natural 174 ms, tuned 85.7 ms (×2)
* K6 Q6 natural/tuned/mt 275 ms / 72 ms / 72 ms ; Q1 107 ms / 119 ms / 118 ms
* K7 natural 11.2 s, tuned 1.92e+03 ms (×5.8)
* K8 natural 6.08e+03 ms, tuned 3.62e+03 ms, tuned_alloc — ; latence p50 188 µs, p99.9 2.14e+03 µs, max 3.65e+03 µs (p99.9/p50 11.4)
* K9 natural 58.1 ms, tuned 42.3 ms, mt 40.4 ms
* K10 natural 197 ms, tuned 22 ms (×9)
* K2 ns/saut 16K/256K/8M/256M : 6.13 / 8.45 / 154 / 342
* (CPU utilisateur + système) / mural, noyaux mono-thread : 0.99

## annexe. js_bun
* MS 17.2 ; C 11.6 (rang —) ; E 14.7 (rang —) ; D 29.0 (rang —) ; rang Dirichlet —  ; cellules 0,5  ; noyau retiré 
* E par noyau (t*/t) : k1 0.53, k3 0.20, k4 0.03, k5 0.03, k6 0.14, k7 0.32, k8 0.22, k9 0.38, k10 0.08
* D : D1 0.04, D2 0.25, D3 0.24, D4 0.98
* K1 natural 104 ms, shuffled 605 ms (×5.8), aos 43.3 ms, soa 13.6 ms ; empreinte 169.58 o/particule
* K3 rmw_packed 2.41e+03 ms, rmw_padded 287 ms, sw_packed 4.42e+03 ms, sw_padded 512 ms (faux partage ×8.4)
* K4 natural non trié 91.8 ms, trié 21.1 ms, sans branchement 114 ms ; vectorisation mesurée C3 = 0.0
* K5 natural 349 ms, tuned 142 ms (×2.5)
* K6 Q6 natural/tuned/mt 146 ms / 121 ms / 46.3 ms ; Q1 260 ms / 255 ms / 87.4 ms
* K7 natural 11 s, tuned 1.37e+03 ms (×8)
* K8 natural 880 ms, tuned 497 ms, tuned_alloc — ; latence p50 43.5 µs, p99.9 901 µs, max 3.29e+03 µs (p99.9/p50 20.7)
* K9 natural 284 ms, tuned 83.1 ms, mt 32.1 ms
* K10 natural 7.41e+03 ms, tuned 157 ms (×47)
* K2 ns/saut 16K/256K/8M/256M : 1.56 / 4.44 / 154 / 365
* (CPU utilisateur + système) / mural, noyaux mono-thread : 1.00

## annexe. python_ft
* C 22.40178571428571, E None, D None
* E par noyau (t*/t) : k3 0.00, k6 0.01, k9 0.01, k10 0.00
* D : 
* K1 natural —, shuffled — (×—), aos —, soa — ; empreinte — o/particule
* K3 rmw_packed 71.1 s, rmw_padded 64.4 s, sw_packed 73.4 s, sw_padded 61.8 s (faux partage ×1.1)
* K4 natural non trié —, trié —, sans branchement — ; vectorisation mesurée C3 = 0.0
* K5 natural —, tuned — (×—)
* K6 Q6 natural/tuned/mt 2.5e+03 ms / 2.43e+03 ms / 733 ms ; Q1 13.7 s / 10.6 s / 3.54e+03 ms
* K7 natural —, tuned — (×—)
* K8 natural —, tuned —, tuned_alloc —
* K9 natural 3.93e+03 ms, tuned 4.08e+03 ms, mt 2.01e+03 ms
* K10 natural 27.7 s, tuned 2.92e+03 ms (×9.5)
* K2 ns/saut 16K/256K/8M/256M : — / — / — / —
* (CPU utilisateur + système) / mural, noyaux mono-thread : 0.99
