<?php
// Remarque sur PHP (docs/PHP.md, 5) : le K9 naturel du banc (bench/php/ms.php, k9_natural, à l'identique) et des
// formes réduites, pour localiser l'échec de compilation du JIT tracing. Usage : php [-d ...] k9_jit.php <forme> [reps]
// Formes : natural (le noyau publié : $b par référence), byval ($b par valeur, rendu), reads (lectures seules, somme
// dans un scalaire), samerow (écriture après lecture de la même ligne), otherrow (écriture après lecture d'une autre
// ligne), tworows (deux autres lignes), mixed (une autre ligne et la même), nomul (le noyau sans le facteur 0,25).
// Chaque répétition : 4 itérations, comme le banc ; grilles allouées une fois et réinitialisées hors chrono.
const M9 = 2048;

function k9_init(int $i, int $j): float
{
    return (($i * 37 + $j * 101) % 1000) / 1000.0; // valeurs de test (pas celles du banc, sans effet sur le JIT)
}

function k9_natural(array $a, array &$b): void
{
    for ($i = 1; $i < M9 - 1; $i++) {
        for ($j = 1; $j < M9 - 1; $j++) {
            $b[$i][$j] = 0.25 * ((($a[$i - 1][$j] + $a[$i + 1][$j]) + $a[$i][$j - 1]) + $a[$i][$j + 1]);
        }
    }
}

function k9_byval(array $a, array $b): array
{
    for ($i = 1; $i < M9 - 1; $i++) {
        for ($j = 1; $j < M9 - 1; $j++) {
            $b[$i][$j] = 0.25 * ((($a[$i - 1][$j] + $a[$i + 1][$j]) + $a[$i][$j - 1]) + $a[$i][$j + 1]);
        }
    }
    return $b;
}

function k9_reads(array $a): float
{
    $s = 0.0;
    for ($i = 1; $i < M9 - 1; $i++) {
        for ($j = 1; $j < M9 - 1; $j++) {
            $s += 0.25 * ((($a[$i - 1][$j] + $a[$i + 1][$j]) + $a[$i][$j - 1]) + $a[$i][$j + 1]);
        }
    }
    return $s;
}

function k9_samerow(array $a, array &$b): void
{
    for ($i = 1; $i < M9 - 1; $i++) {
        for ($j = 1; $j < M9 - 1; $j++) {
            $b[$i][$j] = 0.5 * ($a[$i][$j - 1] + $a[$i][$j + 1]);
        }
    }
}

function k9_otherrow(array $a, array &$b): void
{
    for ($i = 1; $i < M9 - 1; $i++) {
        for ($j = 1; $j < M9 - 1; $j++) {
            $b[$i][$j] = $a[$i - 1][$j];
        }
    }
}

function k9_tworows(array $a, array &$b): void
{
    for ($i = 1; $i < M9 - 1; $i++) {
        for ($j = 1; $j < M9 - 1; $j++) {
            $b[$i][$j] = $a[$i - 1][$j] + $a[$i + 1][$j];
        }
    }
}

function k9_mixed(array $a, array &$b): void
{
    for ($i = 1; $i < M9 - 1; $i++) {
        for ($j = 1; $j < M9 - 1; $j++) {
            $b[$i][$j] = $a[$i - 1][$j] + $a[$i][$j - 1];
        }
    }
}

function k9_nomul(array $a, array &$b): void
{
    for ($i = 1; $i < M9 - 1; $i++) {
        for ($j = 1; $j < M9 - 1; $j++) {
            $b[$i][$j] = (($a[$i - 1][$j] + $a[$i + 1][$j]) + $a[$i][$j - 1]) + $a[$i][$j + 1];
        }
    }
}

$form = $argv[1] ?? 'natural';
$reps = (int)($argv[2] ?? 3);
$a = [];
for ($i = 0; $i < M9; $i++) {
    $row = [];
    for ($j = 0; $j < M9; $j++) {
        $row[] = k9_init($i, $j);
    }
    $a[] = $row;
}
$b = $a;
for ($i = 0; $i < M9; $i++) {
    $b[$i][0] = $a[$i][0];
}
for ($r = -1; $r < $reps; $r++) {
    for ($i = 0; $i < M9; $i++) {
        for ($j = 0; $j < M9; $j++) {
            $a[$i][$j] = $b[$i][$j] = k9_init($i, $j);
        }
    }
    $t0 = hrtime(true);
    $x = 0.0;
    for ($it = 0; $it < 4; $it++) {
        switch ($form) {
            case 'natural': k9_natural($a, $b); [$a, $b] = [$b, $a]; break;
            case 'byval': $b = k9_byval($a, $b); [$a, $b] = [$b, $a]; break;
            case 'reads': $x += k9_reads($a); break;
            case 'samerow': k9_samerow($a, $b); [$a, $b] = [$b, $a]; break;
            case 'otherrow': k9_otherrow($a, $b); [$a, $b] = [$b, $a]; break;
            case 'tworows': k9_tworows($a, $b); [$a, $b] = [$b, $a]; break;
            case 'mixed': k9_mixed($a, $b); [$a, $b] = [$b, $a]; break;
            case 'nomul': k9_nomul($a, $b); [$a, $b] = [$b, $a]; break;
            default: fwrite(STDERR, "forme inconnue : $form\n"); exit(2);
        }
    }
    $dt = (hrtime(true) - $t0) / 1e9;
    $s = $x;
    foreach ($a as $row) {
        foreach ($row as $val) {
            $s += $val;
        }
    }
    if ($r >= 0) {
        printf("%s;%s;%d;%.4f;%.6e\n", PHP_VERSION, $form, $r, $dt, $s);
    }
}
