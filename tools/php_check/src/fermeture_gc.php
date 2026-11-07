<?php
// K1 naturel (objets à 16 propriétés float) appelé directement ou à travers une fermeture qui capture le tableau
// (docs/PHP.md, 2.4) : temps et activité du collecteur de cycles. Argument : nombre de particules (défaut 2^22).
class P { public function __construct(public float $x, public float $y, public float $z, public float $vx, public float $vy, public float $vz,
  public float $ax, public float $ay, public float $az, public float $mass, public float $charge, public float $radius,
  public float $temp, public float $pressure, public float $energy, public float $density) {} }
function k1(array $ps): float { $e = 0.0; foreach ($ps as $p) { $e += 0.5 * $p->mass * ($p->vx * $p->vx + $p->vy * $p->vy + $p->vz * $p->vz); } return $e; }
$n = (int)($argv[2] ?? (1 << 22));
$raw = file_get_contents(($argv[3] ?? '/opt/msdata') . '/k1_particles.f32');
$ps = [];
for ($i = 0; $i < $n; $i++) { $ps[] = new P(...unpack('g16', $raw, 64 * $i)); }
unset($raw);
$mode = $argv[1] ?? 'direct';
$g = $mode === 'fermeture' ? fn() => k1($ps) : null;
$g0 = gc_status();
for ($r = 0; $r < 4; $r++) { $t0 = hrtime(true); $e = $g ? $g() : k1($ps); $dt = (hrtime(true) - $t0) / 1e9; }
$g1 = gc_status();
printf("%s : %.4f s (dernière de 4) ; collecteur de cycles pendant les 4 : %d passes, %.3f s\n", $mode, $dt,
    $g1['runs'] - $g0['runs'], $g1['collector_time'] - $g0['collector_time']);
