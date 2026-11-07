<?php
// Remarque sur PHP (docs/PHP.md, 5) : K1 naturel du banc (bench/php/ms.php : classe Particle, foreach) et le travail
// du collecteur de cycles. Usage : php [-d ...] k1_gc.php <forme> [ordre] [reps] ; ordre : seq (défaut) ou shuffled.
// Formes : foreach (le noyau publié), foreach_gcoff (le même, après gc_disable()), index ($ps[$i]->vx, sans variable
// intermédiaire), index_var ($p = $ps[$i] dans une boucle for). Pour chaque répétition (une d'échauffement, puis
// reps) : temps, passes du collecteur et leurs durées (gc_status, PHP 8.3 et suivants).
const N1 = 1 << 22;

class Particle
{
    public function __construct(
        public float $x, public float $y, public float $z,
        public float $vx, public float $vy, public float $vz,
        public float $ax, public float $ay, public float $az,
        public float $mass, public float $charge, public float $radius,
        public float $temp, public float $pressure, public float $energy, public float $density,
    ) {
    }
}

function k1_foreach(array $ps): float
{
    $e = 0.0;
    foreach ($ps as $p) {
        $e += 0.5 * $p->mass * ($p->vx * $p->vx + $p->vy * $p->vy + $p->vz * $p->vz);
    }
    return $e;
}

function k1_index(array $ps): float
{
    $e = 0.0;
    $n = count($ps);
    for ($i = 0; $i < $n; $i++) {
        $e += 0.5 * $ps[$i]->mass * ($ps[$i]->vx * $ps[$i]->vx + $ps[$i]->vy * $ps[$i]->vy + $ps[$i]->vz * $ps[$i]->vz);
    }
    return $e;
}

function k1_index_var(array $ps): float
{
    $e = 0.0;
    $n = count($ps);
    for ($i = 0; $i < $n; $i++) {
        $p = $ps[$i];
        $e += 0.5 * $p->mass * ($p->vx * $p->vx + $p->vy * $p->vy + $p->vz * $p->vz);
    }
    return $e;
}

$form = $argv[1] ?? 'foreach';
$order = $argv[2] ?? 'seq';
$reps = (int)($argv[3] ?? 4);
$dir = getenv('MS_DATA') ?: '/opt/msdata';
$raw = file_get_contents("$dir/k1_particles.f32");
$ps = [];
for ($i = 0; $i < N1; $i++) {
    $ps[] = new Particle(...unpack('g16', $raw, 64 * $i));
}
unset($raw);
if ($order === 'shuffled') {
    $perm = array_values(unpack('V*', file_get_contents("$dir/k1_perm.u32")));
    $sh = [];
    foreach ($perm as $j) {
        $sh[] = $ps[$j];
    }
    $ps = $sh;
    unset($sh, $perm);
}
$f = ['foreach' => 'k1_foreach', 'foreach_gcoff' => 'k1_foreach', 'index' => 'k1_index',
    'index_var' => 'k1_index_var'][$form];
if ($form === 'foreach_gcoff') {
    gc_disable();
}
$args = [$ps];
for ($r = -1; $r < $reps; $r++) {
    $g0 = gc_status();
    $t0 = hrtime(true);
    $e = $f(...$args);
    $dt = (hrtime(true) - $t0) / 1e9;
    $g1 = gc_status();
    if ($r >= 0) {
        printf("%s;%s;%s;%d;%.4f;%.6f;runs=%d;collected=%d;collector=%.4f;threshold=%d\n", PHP_VERSION, $form, $order,
            $r, $dt, $e, $g1['runs'] - $g0['runs'], $g1['collected'] - $g0['collected'],
            ($g1['collector_time'] ?? 0) - ($g0['collector_time'] ?? 0), $g1['threshold']);
    }
}
