<?php
// v4, point 6 (docs/V4_OPEN.md, 5.1 et 5.2) : fichier d'amorce des processus d'amphp/parallel (ContextWorkerFactory,
// bootstrapPath) pour les formes op_amphp de ms.php. Les processus d'amphp ne chargent pas ms.php : les fonctions
// qu'appellent les tâches sont ici, recopiées de ms.php (q6_tuned_s, q1_tuned, k9_rows ; mêmes opérations, même ordre).
// Fichier ordinaire : OPcache le garde et le JIT tracing le compile dans chaque processus (options du banc passées au
// binaire, ms.php : op_pool). Tailles publiées seulement.

const OP_N6 = 1 << 24;
const OP_M9 = 2048;

function op_load(string $name, string $code): array
{
    $dir = getenv('MS_DATA') ?: '/opt/msdata';
    return array_values(unpack("$code*", file_get_contents("$dir/$name")));
}

// Colonnes de K6 lues une fois par processus (au premier appel : la répétition d'échauffement), gardées entre les
// tâches. Un processus d'amphp peut recevoir n'importe quel quart : chacun lit toutes les lignes des colonnes utiles.
function op_k6_cols(bool $q1): array
{
    static $c = null;
    if ($c === null) {
        $c = $q1
            ? [op_load('k6_shipdate.i32', 'l'), op_load('k6_extendedprice.i32', 'l'), op_load('k6_quantity.u8', 'C'),
                op_load('k6_discount.u8', 'C'), op_load('k6_tax.u8', 'C'), op_load('k6_returnflag.u8', 'C'),
                op_load('k6_linestatus.u8', 'C')]
            : [op_load('k6_shipdate.i32', 'l'), op_load('k6_extendedprice.i32', 'l'), op_load('k6_quantity.u8', 'C'),
                op_load('k6_discount.u8', 'C')];
    }
    return $c;
}

function op_q6_tuned_s(array $sd, array $d, array $q, array $pr, int $lo, int $hi): int
{
    $s = 0;
    for ($i = $lo; $i < $hi; $i++) {
        $dd = $d[$i];
        $m = (((($sd[$i] - 8766) & 0xFFFFFFFF) - 365) & ((($dd - 5) & 0xFF) - 3) & ($q[$i] - 24)) >> 63;
        $s += $pr[$i] * $dd * ($m & 1);
    }
    return $s;
}

function op_q1_tuned(array $c, int $lo, int $hi): int
{
    [$sd, $pr, $q, $d, $t, $rf, $ls] = $c;
    $cnt = $sq = $sp = $sdp = $sdt = [0, 0, 0, 0, 0, 0];
    for ($i = $lo; $i < $hi; $i++) {
        if ($sd[$i] <= 10471) {
            $g = $rf[$i] * 2 + $ls[$i];
            $p = $pr[$i];
            $dp = $p * (100 - $d[$i]);
            $cnt[$g]++;
            $sq[$g] += $q[$i];
            $sp[$g] += $p;
            $sdp[$g] += $dp;
            $sdt[$g] += $dp * (100 + $t[$i]);
        }
    }
    return array_sum($cnt) + array_sum($sq) + array_sum($sp) + array_sum($sdp) + array_sum($sdt);
}

// Tâches de K6 : le quart t des lignes (découpage de mt), Q6 par tuned_s, Q1 par tuned (les formes de mt_pool_s et de
// mt) ; chacune rend sa somme partielle.
function op_q6_part(int $t): int
{
    $c = op_k6_cols(false);
    return op_q6_tuned_s($c[0], $c[3], $c[2], $c[1], intdiv(OP_N6, 4) * $t, intdiv(OP_N6, 4) * ($t + 1));
}

function op_q1_part(int $t): int
{
    return op_q1_tuned(op_k6_cols(true), intdiv(OP_N6, 4) * $t, intdiv(OP_N6, 4) * ($t + 1));
}

// Tâche de K9 : une bande de lignes avec une ligne voisine de part et d'autre, en chaîne de float64 (pack 'd*') ; rend
// ses lignes intérieures calculées (colonnes de bord recopiées), en chaîne. Calcul de k9_rows.
function op_k9_band(string $band): string
{
    $a = array_values(unpack('d*', $band));
    $nl = intdiv(count($a), OP_M9);
    $b = $a;
    for ($i = 1; $i < $nl - 1; $i++) {
        $o = $i * OP_M9;
        for ($k = $o + 1, $e = $o + OP_M9 - 1; $k < $e; $k++) {
            $b[$k] = 0.25 * ((($a[$k - OP_M9] + $a[$k + OP_M9]) + $a[$k - 1]) + $a[$k + 1]);
        }
    }
    $out = '';
    for ($i = 1; $i < $nl - 1; $i++) {
        $out .= pack('d*', ...array_slice($b, $i * OP_M9, OP_M9));
    }
    return $out;
}
