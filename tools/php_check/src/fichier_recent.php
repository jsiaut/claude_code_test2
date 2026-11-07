<?php
// opcache.file_update_protection (2 s par défaut) : un script modifié depuis moins de 2 s n'est pas mis en cache par
// OPcache, et le JIT ne s'y applique pas (docs/PHP.md, 2.4). Produit scalaire de K5, 2048 éléments × 4096 fois.
function dot(array $a, array $b): float { $s = 0.0; $n = count($a); for ($i = 0; $i < $n; $i++) { $s += $a[$i] * $b[$i]; } return $s; }
$a = []; $b = [];
for ($i = 0; $i < 2048; $i++) { $a[] = $i / 2048.0; $b[] = 1.0 - $i / 2048.0; }
$t0 = hrtime(true);
for ($k = 0; $k < 4096; $k++) { $d = dot($a, $b); }
$dt = (hrtime(true) - $t0) / 1e9;
$st = opcache_get_status(false);
printf("âge du script %d s : en cache %s, %.2f ns par élément\n", time() - filemtime(__FILE__),
    var_export(opcache_is_script_cached(__FILE__), true), $dt / (2048 * 4096) * 1e9);
