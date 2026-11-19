<?php
// Audit de la grille, PHP : compléments exécutés (docs/V4_PLAN.md 2.1), mêmes réglages que le banc (OPcache, JIT
// tracing). Imprime des lignes FACT;<case>;<texte>, reprises par probes/php/run.sh.

// B3 : un petit agrégat de trois flottants n'est jamais une valeur en place : tableau ou objet, il vit sur le tas.
final class P3 { public function __construct(public float $x, public float $y, public float $z) {} }
$n = 100000;
$x = (float)$argc;                       // connu à l'exécution seulement (pas de tableau constant partagé)
$keep = array_fill(0, $n, null);         // conteneur alloué d'avance : seule la mémoire des agrégats est comptée
$m0 = memory_get_usage();
for ($i = 0; $i < $n; $i++) $keep[$i] = [$x + $i, $x, $x];
$arr = (memory_get_usage() - $m0) / $n;
$keep = array_fill(0, $n, null);
$m0 = memory_get_usage();
for ($i = 0; $i < $n; $i++) $keep[$i] = new P3($x + $i, $x, $x);
$obj = (memory_get_usage() - $m0) / $n;
$keep = null;
printf("FACT;B3;%d agrégats de trois flottants gardés vivants : %.0f octets de tas chacun en tableau [x, y, z], %.0f en objet d'une classe à trois propriétés typées float\n", $n, $arr, $obj);

// C4 : la somme garde l'ordre des opérations, dans le code compilé par le JIT comme dans array_sum.
mt_srand(42);
$v = [];
for ($i = 0; $i < 1000000; $i++) $v[] = mt_rand() / mt_getrandmax() - 0.5;
$s = 0.0;
foreach ($v as $e) $s += $e;
$t = array_sum($v);
function pw(array $a, int $lo, int $hi): float
{
    if ($hi - $lo <= 8) { $s = 0.0; for ($i = $lo; $i < $hi; $i++) $s += $a[$i]; return $s; }
    $m = intdiv($lo + $hi, 2);
    return pw($a, $lo, $m) + pw($a, $m, $hi);
}
$p = pw($v, 0, count($v));
printf("FACT;C4;un million de flottants : boucle foreach (JIT) %.17g, array_sum %.17g (%s) ; somme par paires écrite à la main %.17g (écart %.3g)\n",
    $s, $t, $s === $t ? 'identiques, ordre gardé' : 'différentes', $p, abs($p - $s));
$st = opcache_get_status(false);
printf("FACT;JIT;JIT actif pendant l'audit : %s\n", ($st['jit']['on'] ?? false) ? 'oui' : 'non');
