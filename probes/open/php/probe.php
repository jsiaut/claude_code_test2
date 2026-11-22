<?php
// v4, point 6 (docs/V4_OPEN.md, 4) : sondes de la grille ouverte de PHP
// (C5 : amphp/parallel-functions 2.0.0 ; F1 : rindow/rindow-math-matrix 2.2.0). Modules de /opt/open/php/vendor.
require '/opt/open/php/vendor/autoload.php';
use Rindow\Math\Matrix\MatrixOperator;
use function Amp\ParallelFunctions\parallelMap;

function c5(): void {
    $chunks = [0, 1, 2, 3];
    $t0 = microtime(true);
    $res = parallelMap($chunks, function (int $c): array {
        $s = 0;
        for ($k = $c * 10000000 + 1; $k <= ($c + 1) * 10000000; $k++) { $s += $k; }
        return [$s, getmypid()];
    });
    $t1 = microtime(true);
    $total = array_sum(array_column($res, 0));
    $pids = array_unique(array_column($res, 1));
    printf("RESULT;C5;amphp/parallel-functions;parallelMap sur 4 tranches : somme = %d (attendu 800000020000000) en %.2f s ; exécutées par %d processus distincts (getmypid), autres que le parent (%d) = %s ; données et résultats sérialisés entre processus\n",
        $total, $t1 - $t0, count($pids), getmypid(), in_array(getmypid(), $pids) ? 'false' : 'true');
}

function f1(): void {
    $mo = new MatrixOperator();
    $m = 300 * (count($_SERVER['argv'])); $n = 500;
    $a = $mo->zeros([$m, $n]);
    $a[2][3] = 7.0;
    $buf = $a->buffer();
    $idx = -1;
    for ($i = 0; $i < count($buf); $i++) { if ($buf[$i] == 7.0) { $idx = $i; break; } }
    printf("RESULT;F1;rindow/rindow-math-matrix;MatrixOperator::zeros([%d, %d]) de dimensions connues à l'exécution : shape %s, tampon linéaire %s de %d éléments, a[2][3] = %g à l'indice %d (2*%d+3) ; service %s\n",
        $m, $n, json_encode($a->shape()), get_class($buf), count($buf), $a[2][3], $idx, $n, get_class($mo->service()));
}

c5();
f1();
