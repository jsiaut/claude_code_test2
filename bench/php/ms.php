<?php
// Implémentation PHP 8.5 (docs/PHP.md ; contrat commun : docs/SPEC.md). Exécutée par la CLI de PHP 8.5.12 avec
// php.ini-production, OPcache et le JIT tracing (bench/php/run). Bibliothèque : les extensions livrées avec php-src
// (standard, SPL, FFI, pcntl, shmop, sysvsem), aucune bibliothèque tierce, aucun code C appelé par la FFI.
// PHP n'a pas de fils : K3 et les variantes mt emploient des processus (pcntl_fork) créés avant la mesure, comme les
// Workers de JavaScript, qui partagent avec le parent un segment de mémoire (shmop) ou lui répondent par une paire de
// sockets ; K10 emploie des Fibers (coroutines).

// ------------------------------------------------------------------ harnais
$DATA = getenv('MS_DATA') ?: '/opt/msdata';
$WARMUP = (int)(getenv('WARMUP') ?: '1');

function data_path(string $name): string
{
    global $DATA;
    return "$DATA/$name";
}

function load(string $name, string $code): array
{
    // unpack rend des clés 1..n : array_values les renumérote à partir de 0 (tableau « packed »)
    return array_values(unpack("$code*", file_get_contents(data_path($name))));
}

function result(string $k, string $v, string $p, int $rep, float $sec, string $chk): void
{
    printf("RESULT;%s;%s;%s;%d;%.9f;%s\n", $k, $v, $p, $rep, $sec, $chk);
}

// Section chronométrée : appel du noyau par son nom, sans fermeture. Une fermeture qui capture les données les fait
// parcourir par le collecteur de cycles à chacune de ses passes : K1 naturel y prend 0,9 s au lieu de 0,48 s
// (docs/PHP.md, 2.4).
function bench(string $k, string $v, string $p, int $reps, string $f, array $args, string $fmt = '%d'): void
{
    global $WARMUP;
    for ($r = -$WARMUP; $r < $reps; $r++) {
        $t0 = hrtime(true);
        $chk = sprintf($fmt, $f(...$args));
        $dt = (hrtime(true) - $t0) / 1e9;
        if ($r >= 0) {
            result($k, $v, $p, $r, $dt, $chk);
        }
    }
}

function fmt_e(float $s): string
{
    // même écriture que Python (%.15e, exposant sur deux chiffres)
    return preg_replace('/e([+-])(\d)$/', 'e${1}0$2', sprintf('%.15e', $s));
}

// Processus de travail (pcntl_fork) créés avant la mesure : chacun lit ses commandes, une par ligne, sur sa paire
// de sockets, appelle $job($t, $commande) et répond par une ligne.
function workers(int $n, callable $job): array
{
    $ws = [];
    for ($t = 0; $t < $n; $t++) {
        $pair = stream_socket_pair(STREAM_PF_UNIX, STREAM_SOCK_STREAM, STREAM_IPPROTO_IP);
        $pid = pcntl_fork();
        if ($pid === 0) {
            fclose($pair[0]);
            $sock = $pair[1];
            while (($cmd = fgets($sock)) !== false) {
                $cmd = rtrim($cmd);
                if ($cmd === 'q') {
                    break;
                }
                fwrite($sock, $job($t, $cmd) . "\n");
            }
            exit(0);
        }
        fclose($pair[1]);
        $ws[] = [$pid, $pair[0]];
    }
    return $ws;
}

function run_workers(array $ws, string $cmd): array
{
    foreach ($ws as [$pid, $s]) {
        fwrite($s, "$cmd\n");
    }
    $out = [];
    foreach ($ws as [$pid, $s]) {
        $out[] = rtrim(fgets($s));
    }
    return $out;
}

function stop_workers(array $ws): void
{
    foreach ($ws as [$pid, $s]) {
        fwrite($s, "q\n");
        fclose($s);
        pcntl_waitpid($pid, $status);
    }
}

// ------------------------------------------------------------------ K1
const N1 = 1 << 22;

class Particle // classe à propriétés typées, promues par le constructeur (manuel : « Constructor Promotion »)
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

const FIELDS = ['x', 'y', 'z', 'vx', 'vy', 'vz', 'ax', 'ay', 'az', 'mass', 'charge', 'radius', 'temp', 'pressure',
    'energy', 'density'];

function k1_natural(array $ps): float
{
    $e = 0.0;
    foreach ($ps as $p) {
        $e += 0.5 * $p->mass * ($p->vx * $p->vx + $p->vy * $p->vy + $p->vz * $p->vz);
    }
    return $e;
}

function k1_natural_arr(array $ps): float // sensibilité : tableaux associatifs à clés nommées
{
    $e = 0.0;
    foreach ($ps as $p) {
        $e += 0.5 * $p['mass'] * ($p['vx'] * $p['vx'] + $p['vy'] * $p['vy'] + $p['vz'] * $p['vz']);
    }
    return $e;
}

function k1_soa(array $vx, array $vy, array $vz, array $m): float
{
    $e = 0.0;
    $n = count($m);
    for ($i = 0; $i < $n; $i++) {
        $a = $vx[$i];
        $b = $vy[$i];
        $c = $vz[$i];
        $e += $m[$i] * ($a * $a + $b * $b + $c * $c);
    }
    return 0.5 * $e;
}

function k1_aos($f, int $n): float // $f : vue float[16·n] sur le tableau FFI de struct particle (64 o)
{
    $e = 0.0;
    $end = 16 * $n;
    for ($k = 0; $k < $end; $k += 16) {
        $a = $f[$k + 3];
        $b = $f[$k + 4];
        $c = $f[$k + 5];
        $e += $f[$k + 9] * ($a * $a + $b * $b + $c * $c);
    }
    return 0.5 * $e;
}

function rss_now(): int // RSS courant (/proc/self/statm, 2e champ ; pages de 4 Kio)
{
    return (int)explode(' ', file_get_contents('/proc/self/statm'))[1] * 4096;
}

function run_k1(string $v, int $reps): void
{
    if ($v === 'footprint0' || $v === 'footprint_raw') {
        result('k1', $v, 'energy', 0, 0.0, '0');
        return;
    }
    $raw = file_get_contents(data_path('k1_particles.f32'));
    if ($v === 'aos') {
        $ffi = FFI::cdef('typedef struct { float x, y, z, vx, vy, vz, ax, ay, az, mass, charge, radius, temp, pressure, energy, density; } particle;');
        $ps = $ffi->new('particle[' . N1 . ']');
        FFI::memcpy($ps, $raw, strlen($raw));
        unset($raw);
        $f = $ffi->cast('float[' . (16 * N1) . ']', $ps);
        echo 'META;aos_repr;tableau FFI de ' . N1 . ' struct particle (16 float, ' . FFI::sizeof($ffi->type('particle'))
            . " o, contigus), lu par une vue float[] (cast FFI, même mémoire)\n";
        bench('k1', $v, 'energy', $reps, 'k1_aos', [$f, N1], '%.6f');
        return;
    }
    if ($v === 'soa') {
        $all = array_values(unpack('g*', $raw));
        unset($raw);
        $cols = array_fill(0, 16, []);
        for ($k = 0; $k < 16; $k++) {
            $c = [];
            for ($i = $k; $i < 16 * N1; $i += 16) {
                $c[] = $all[$i];
            }
            $cols[$k] = $c;
        }
        unset($all);
        $vx = $cols[3];
        $vy = $cols[4];
        $vz = $cols[5];
        $m = $cols[9];
        bench('k1', $v, 'energy', $reps, 'k1_soa', [$vx, $vy, $vz, $m], '%.6f');
        return;
    }
    $arr = str_starts_with($v, 'natural_arr');
    if ($v === 'footprint') {
        gc_collect_cycles();
        $m1 = memory_get_usage();
        $r1 = rss_now();
    }
    $ps = [];
    for ($i = 0; $i < N1; $i++) {
        $f = unpack('g16', $raw, 64 * $i);
        $ps[] = $arr ? array_combine(FIELDS, array_values($f)) : new Particle(...$f);
    }
    if ($v === 'footprint') {
        gc_collect_cycles();
        $m2 = memory_get_usage();
        $r2 = rss_now();
        echo "META;mem;live;$m1;$m2\nMETA;rss;$r1;$r2\nMETA;raw0;" . unpack('g', $raw)[1] . "\n";
        result('k1', $v, 'energy', 0, 0.0, sprintf('%.6f', k1_natural($ps)));
        return;
    }
    unset($raw);
    if (str_ends_with($v, 'shuffled')) {
        $perm = load('k1_perm.u32', 'V');
        $sh = [];
        foreach ($perm as $j) {
            $sh[] = $ps[$j];
        }
        $ps = $sh;
        unset($sh, $perm);
    }
    bench('k1', $v, 'energy', $reps, $arr ? 'k1_natural_arr' : 'k1_natural', [$ps], '%.6f');
}

// ------------------------------------------------------------------ K2
function k2_chase($a, int $h): int
{
    $i = 0;
    for ($k = 0; $k < $h; $k++) {
        $i = $a[$i];
    }
    return $i;
}

function run_k2(string $v, int $reps, string $p): void
{
    // le tableau d'entiers le plus compact de la distribution : uint32_t[] de la FFI (4 o par élément ; un tableau
    // PHP prend 16 o par élément)
    $s = file_get_contents(data_path("k2_chase_$p.u32"));
    $a = FFI::cdef('')->new('uint32_t[' . (strlen($s) >> 2) . ']');
    FFI::memcpy($a, $s, strlen($s));
    unset($s);
    echo "META;k2_repr;uint32_t[] de la FFI (4 o par élément)\n";
    bench('k2', $v, $p, $reps, 'k2_chase', [$a, 4200000]);
}

// ------------------------------------------------------------------ K3
const ITER3 = 1 << 25;

function run_k3(string $v, int $reps): void
{
    $rmw = str_starts_with($v, 'rmw');
    $stride = str_ends_with($v, 'padded') ? 128 : 8; // compteurs de 64 bits : 128 o ou 8 o d'écart
    echo 'META;k3_mechanism;' . ($rmw
            ? "PHP n'a pas d'atomiques : sem_acquire/sem_release (sysvsem, un sémaphore par compteur) autour de shmop_read/shmop_write"
            : "c[t] = c[t] + 1 par shmop_read/shmop_write (unpack/pack 'q') sur un segment partagé (shmop), écrivain unique")
        . " ; 4 processus (pcntl_fork) créés avant la mesure\n";
    $shm = shmop_open(0, 'c', 0600, 4096); // IPC_PRIVATE : segment hérité par les processus fils
    shmop_delete($shm); // détruit au dernier détachement, même si le processus meurt
    $sems = [];
    if ($rmw) {
        for ($t = 0; $t < 4; $t++) {
            $sems[] = sem_get(0, 1, 0600, false);
        }
    }
    $off = fn(int $t): int => 64 + $t * $stride;
    $job = function (int $t, string $cmd) use ($shm, $sems, $rmw, $off): string {
        $o = $off($t);
        if ($rmw) {
            $sem = $sems[$t];
            for ($n = 0; $n < ITER3; $n++) {
                sem_acquire($sem);
                shmop_write($shm, pack('q', unpack('q', shmop_read($shm, $o, 8))[1] + 1), $o);
                sem_release($sem);
            }
        } else {
            for ($n = 0; $n < ITER3; $n++) {
                shmop_write($shm, pack('q', unpack('q', shmop_read($shm, $o, 8))[1] + 1), $o);
            }
        }
        return '0';
    };
    global $WARMUP;
    for ($r = -$WARMUP; $r < $reps; $r++) {
        for ($t = 0; $t < 4; $t++) {
            shmop_write($shm, pack('q', 0), $off($t));
        }
        $ws = workers(4, $job);
        $t0 = hrtime(true);
        run_workers($ws, 'go');
        $dt = (hrtime(true) - $t0) / 1e9;
        stop_workers($ws);
        $s = 0;
        for ($t = 0; $t < 4; $t++) {
            $s += unpack('q', shmop_read($shm, $off($t), 8))[1];
        }
        if ($r >= 0) {
            result('k3', $v, '4x2^25', $r, $dt, (string)$s);
        }
    }
    foreach ($sems as $sem) {
        sem_remove($sem);
    }
}

// ------------------------------------------------------------------ K4
function k4_natural(array $v): int
{
    $s = 0;
    foreach ($v as $x) {
        if ($x >= 128) {
            $s += $x;
        }
    }
    return $s;
}

function k4_branchless(array $v): int
{
    $s = 0;
    foreach ($v as $x) {
        $s += $x * ($x >> 7);
    }
    return $s;
}

function run_k4(string $v, int $reps): void
{
    $d = load('k4_bytes.u8', 'C');
    if ($v === 'natural_sorted') {
        sort($d);
    }
    bench('k4', $v, '16M', $reps, $v === 'branchless_unsorted' ? 'k4_branchless' : 'k4_natural', [$d]);
}

// ------------------------------------------------------------------ K5
const INNER5 = 1 << 16;

function k5_natural(array $a, array $b): float
{
    $s = 0.0;
    $n = count($a);
    for ($i = 0; $i < $n; $i++) {
        $s += $a[$i] * $b[$i];
    }
    return $s;
}

function k5_tuned(array $a, array $b): float // 2 accumulateurs, boucle déroulée par 2 (n pair) : la plus rapide
{                                               // des formes essayées (1, 2, 4 et 8 accumulateurs ; foreach)
    $s0 = $s1 = 0.0;
    $n = count($a);
    for ($i = 0; $i < $n; $i += 2) {
        $s0 += $a[$i] * $b[$i];
        $s1 += $a[$i + 1] * $b[$i + 1];
    }
    return $s0 + $s1;
}

// un appel de fonction à chaque itération : rien ne prouve au JIT que les itérations sont égales
function k5_natural_loop(array $a, array $b): float
{
    $d = 0.0;
    for ($k = 0; $k < INNER5; $k++) {
        $d = k5_natural($a, $b);
    }
    return $d;
}

function k5_tuned_loop(array $a, array $b): float
{
    $d = 0.0;
    for ($k = 0; $k < INNER5; $k++) {
        $d = k5_tuned($a, $b);
    }
    return $d;
}

function run_k5(string $v, int $reps): void
{
    $a = load('k5_a.f32', 'g');
    $b = load('k5_b.f32', 'g');
    bench('k5', $v, '2048x65536', $reps, $v === 'tuned' ? 'k5_tuned_loop' : 'k5_natural_loop', [$a, $b], '%.4f');
}

// ------------------------------------------------------------------ K6
const N6 = 1 << 24;

function q6_natural(array $sd, array $d, array $q, array $pr, int $lo, int $hi): int
{
    $s = 0;
    for ($i = $lo; $i < $hi; $i++) {
        if ($sd[$i] >= 8766 && $sd[$i] < 9131 && $d[$i] >= 5 && $d[$i] <= 7 && $q[$i] < 24) {
            $s += $pr[$i] * $d[$i];
        }
    }
    return $s;
}

function q6_tuned(array $sd, array $d, array $q, array $pr, int $lo, int $hi): int
{
    // chaque intervalle en une comparaison : (x - bas) & masque < largeur (les valeurs sous la borne deviennent
    // grandes) ; la date d'abord (la plus sélective)
    $s = 0;
    for ($i = $lo; $i < $hi; $i++) {
        if ((($sd[$i] - 8766) & 0xFFFFFFFF) < 365) {
            $dd = $d[$i];
            if ((($dd - 5) & 0xFF) < 3 && $q[$i] < 24) {
                $s += $pr[$i] * $dd;
            }
        }
    }
    return $s;
}

function q1_natural(array $c, int $lo, int $hi, array &$acc): void
{
    [$sd, $pr, $q, $d, $t, $rf, $ls] = $c;
    for ($i = $lo; $i < $hi; $i++) {
        if ($sd[$i] <= 10471) {
            $g = ($rf[$i] * 2 + $ls[$i]) * 5;
            $p = $pr[$i];
            $dp = $p * (100 - $d[$i]);
            $acc[$g]++;
            $acc[$g + 1] += $q[$i];
            $acc[$g + 2] += $p;
            $acc[$g + 3] += $dp;
            $acc[$g + 4] += $dp * (100 + $t[$i]);
        }
    }
}

function q1_tuned(array $c, int $lo, int $hi): int
{
    // cinq tableaux de 6 agrégats (un par groupe) au lieu d'un tableau de 30 : moins d'arithmétique d'indices
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

function q1_natural_all(array $c): int
{
    $acc = array_fill(0, 30, 0);
    q1_natural($c, 0, N6, $acc);
    return array_sum($acc);
}

function k6_mt(array $ws): int
{
    return array_sum(array_map('intval', run_workers($ws, 'go')));
}

function run_k6(string $v, int $reps, string $p): void
{
    $c = [load('k6_shipdate.i32', 'l'), load('k6_extendedprice.i32', 'l'), load('k6_quantity.u8', 'C'),
        load('k6_discount.u8', 'C'), load('k6_tax.u8', 'C'), load('k6_returnflag.u8', 'C'),
        load('k6_linestatus.u8', 'C')];
    $q1 = $p === 'q1';
    if ($v === 'mt') {
        echo "META;k6_mt;4 processus (pcntl_fork) créés avant la mesure, colonnes partagées en copie sur écriture, code tuned sur un quart des lignes chacun, résultat par paire de sockets\n";
        $ws = workers(4, function (int $t, string $cmd) use ($c, $q1): string {
            $lo = intdiv(N6, 4) * $t;
            $hi = intdiv(N6, 4) * ($t + 1);
            return (string)($q1 ? q1_tuned($c, $lo, $hi) : q6_tuned($c[0], $c[3], $c[2], $c[1], $lo, $hi));
        });
        bench('k6', $v, $p, $reps, 'k6_mt', [$ws]);
        stop_workers($ws);
        return;
    }
    if ($q1) {
        if ($v === 'tuned') {
            bench('k6', $v, $p, $reps, 'q1_tuned', [$c, 0, N6]);
            return;
        }
        bench('k6', $v, $p, $reps, 'q1_natural_all', [$c]);
        return;
    }
    bench('k6', $v, $p, $reps, $v === 'tuned' ? 'q6_tuned' : 'q6_natural', [$c[0], $c[3], $c[2], $c[1], 0, N6]);
}

// ------------------------------------------------------------------ K7
function run_k7(string $v, int $reps): void
{
    global $WARMUP;
    $keys = load('k7_keys.u32', 'V');
    $vals = load('k7_vals.u32', 'V');
    $n = count($keys);
    for ($r = -$WARMUP; $r < $reps; $r++) {
        if ($v === 'natural') { // le tableau de PHP (table de hachage ordonnée), un couple [compte, somme] par clé
            $t0 = hrtime(true);
            $m = [];
            foreach ($keys as $i => $k) {
                if (isset($m[$k])) {
                    $m[$k][0]++;
                    $m[$k][1] += $vals[$i];
                } else {
                    $m[$k] = [1, $vals[$i]];
                }
            }
            $dt = (hrtime(true) - $t0) / 1e9;
            $nk = count($m);
            $ws = 0;
            foreach ($m as $k => $e) {
                $ws += $e[1] * (($k & 1023) + 1);
            }
            unset($m);
        } else { // table maison à adressage ouvert : clés et couples (compte, somme) entrelacés dans deux tableaux
            // « packed » (2^21 cases), sondage linéaire, hachage par les bits bas (les clés sont brouillées ; un
            // hachage multiplicatif sur 32 bits, comme celui du C, passerait en flottant : 2.4)
            $t0 = hrtime(true);
            $cap = 1 << 21;
            $mask = $cap - 1;
            $tk = array_fill(0, $cap, -1);
            $tcs = array_fill(0, 2 * $cap, 0);
            $nk = 0;
            foreach ($keys as $i => $k) {
                $h = $k & $mask;
                while (true) {
                    $x = $tk[$h];
                    if ($x === $k) {
                        $tcs[2 * $h]++;
                        $tcs[2 * $h + 1] += $vals[$i];
                        break;
                    }
                    if ($x < 0) {
                        $tk[$h] = $k;
                        $tcs[2 * $h] = 1;
                        $tcs[2 * $h + 1] = $vals[$i];
                        $nk++;
                        break;
                    }
                    $h = ($h + 1) & $mask;
                }
            }
            $dt = (hrtime(true) - $t0) / 1e9;
            $ws = 0;
            foreach ($tk as $h => $k) {
                if ($k >= 0) {
                    $ws += $tcs[2 * $h + 1] * (($k & 1023) + 1);
                }
            }
            unset($tk, $tcs);
        }
        if ($r >= 0) {
            result('k7', $v, '16M/1M', $r, $dt, "$nk:$ws");
        }
    }
}

// ------------------------------------------------------------------ K8
class Node
{
    public function __construct(public int $v, public ?Node $l = null, public ?Node $r = null)
    {
    }
}

class Counter8
{
    public static int $c = 0;
}

function t_build(int $d): Node
{
    $v = Counter8::$c++;
    if ($d > 0) {
        $l = t_build($d - 1);
        return new Node($v, $l, t_build($d - 1));
    }
    return new Node($v);
}

function t_sum(?Node $n): int
{
    return $n === null ? 0 : $n->v + t_sum($n->l) + t_sum($n->r);
}

// Arène : nœuds indexés dans trois tableaux réutilisés (aucune allocation en régime permanent), construits en ordre
// préfixe et sommés sans récursion (pile explicite, réutilisée). Les piles s'écrivent à indices explicites :
// deux « $st[$sp++] = … » de suite dans la boucle interne font calculer faux le JIT tracing de PHP 8.5.12 (2.4).
function a_build(int $depth, int $c, array &$v, array &$l, array &$r, array &$st): void
{
    $sp = 0;
    $top = 1;
    $i = 0;
    $v[0] = $c;
    $c++;
    $d = $depth;
    while (true) {
        while ($d > 0) { // descente à gauche ; le fils droit attend sur la pile
            $j = $top;
            $top++;
            $v[$j] = $c;
            $c++;
            $l[$i] = $j;
            $st[$sp] = $i;
            $st[$sp + 1] = $d - 1;
            $sp += 2;
            $i = $j;
            $d--;
        }
        $l[$i] = -1;
        $r[$i] = -1;
        if ($sp === 0) {
            return;
        }
        $sp -= 2;
        $d = $st[$sp + 1];
        $p = $st[$sp];
        $j = $top;
        $top++;
        $v[$j] = $c;
        $c++;
        $r[$p] = $j;
        $i = $j;
    }
}

function a_sum(array $v, array $l, array $r, array &$st): int
{
    $st[0] = 0;
    $sp = 1;
    $s = 0;
    while ($sp > 0) {
        $sp--;
        $i = $st[$sp];
        $s += $v[$i];
        $x = $l[$i];
        if ($x >= 0) {
            $st[$sp] = $x;
            $st[$sp + 1] = $r[$i];
            $sp += 2;
        }
    }
    return $s;
}

function run_k8(string $v, int $reps): void
{
    global $WARMUP;
    $Q = 16384;
    Counter8::$c = 0;
    $keep = t_build(20);
    $lsum = t_sum($keep);
    $lat = array_fill(0, $Q, 0);
    $tuned = $v === 'tuned';
    $av = array_fill(0, 2047, 0);
    $al = array_fill(0, 2047, -1);
    $ar = array_fill(0, 2047, -1);
    $st = array_fill(0, 64, 0);
    for ($r = -$WARMUP; $r < $reps; $r++) {
        $total = 0;
        $t0 = hrtime(true);
        for ($q = 0; $q < $Q; $q++) {
            $a = hrtime(true);
            if ($tuned) {
                a_build(10, $q, $av, $al, $ar, $st);
                $s = a_sum($av, $al, $ar, $st);
            } else {
                Counter8::$c = $q;
                $s = t_sum(t_build(10));
            }
            $total += $s;
            $lat[$q] = hrtime(true) - $a;
        }
        $dt = (hrtime(true) - $t0) / 1e9;
        if ($r >= 0) {
            result('k8', $v, '16384x2047', $r, $dt, (string)($total + $lsum));
            $sl = $lat;
            sort($sl);
            printf("LAT;%s;%d;%d;%d;%d;%d\n", $v, $sl[$Q >> 1], $sl[intdiv($Q * 9, 10)], $sl[intdiv($Q * 99, 100)],
                $sl[intdiv($Q * 999, 1000)], $sl[$Q - 1]);
        }
    }
}

// ------------------------------------------------------------------ K9
const M9 = 2048;

function k9_init(int $i, int $j): float
{
    return (($i * 31 + $j * 17) % 1024) / 1024.0;
}

function k9_natural(array $a, array &$b): void
{
    for ($i = 1; $i < M9 - 1; $i++) {
        for ($j = 1; $j < M9 - 1; $j++) {
            $b[$i][$j] = 0.25 * ((($a[$i - 1][$j] + $a[$i + 1][$j]) + $a[$i][$j - 1]) + $a[$i][$j + 1]);
        }
    }
}

function k9_rows(array $a, array &$b, int $r0, int $r1): void // grille plate, lignes r0..r1-1 (indices locaux)
{
    for ($i = $r0; $i < $r1; $i++) {
        $o = $i * M9;
        for ($k = $o + 1, $e = $o + M9 - 1; $k < $e; $k++) {
            $b[$k] = 0.25 * ((($a[$k - M9] + $a[$k + M9]) + $a[$k - 1]) + $a[$k + 1]);
        }
    }
}

function run_k9(string $v, int $reps): void
{
    global $WARMUP;
    if ($v === 'natural') { // tableau de tableaux, deux grilles allouées une fois, réinitialisées hors chrono
        $a = [];
        for ($i = 0; $i < M9; $i++) {
            $row = [];
            for ($j = 0; $j < M9; $j++) {
                $row[] = k9_init($i, $j);
            }
            $a[] = $row;
        }
        $b = $a;
        for ($i = 0; $i < M9; $i++) { // sépare les deux grilles (copie sur écriture), hors chrono
            $b[$i][0] = $a[$i][0];
        }
        for ($r = -$WARMUP; $r < $reps; $r++) {
            for ($i = 0; $i < M9; $i++) {
                for ($j = 0; $j < M9; $j++) {
                    $a[$i][$j] = $b[$i][$j] = k9_init($i, $j);
                }
            }
            $t0 = hrtime(true);
            for ($it = 0; $it < 4; $it++) {
                k9_natural($a, $b);
                [$a, $b] = [$b, $a];
            }
            $dt = (hrtime(true) - $t0) / 1e9;
            $s = 0.0;
            foreach ($a as $row) { // somme naïve séquentielle
                foreach ($row as $val) {
                    $s += $val;
                }
            }
            if ($r >= 0) {
                result('k9', $v, '2048^2x4', $r, $dt, fmt_e($s));
            }
        }
        return;
    }
    if ($v === 'mt') {
        run_k9_mt($reps);
        return;
    }
    $ga = [];
    for ($k = 0; $k < M9 * M9; $k++) {
        $ga[] = k9_init(intdiv($k, M9), $k % M9);
    }
    $gb = $ga;
    $gb[0] = $ga[0]; // sépare les deux grilles, hors chrono
    for ($r = -$WARMUP; $r < $reps; $r++) {
        for ($k = 0; $k < M9 * M9; $k++) {
            $ga[$k] = $gb[$k] = k9_init(intdiv($k, M9), $k % M9);
        }
        $t0 = hrtime(true);
        for ($it = 0; $it < 4; $it++) {
            if ($it % 2 === 0) {
                k9_rows($ga, $gb, 1, M9 - 1);
            } else {
                k9_rows($gb, $ga, 1, M9 - 1);
            }
        }
        $dt = (hrtime(true) - $t0) / 1e9;
        $s = 0.0;
        foreach ($ga as $val) { // 4 itérations : la grille finale est de nouveau $ga
            $s += $val;
        }
        if ($r >= 0) {
            result('k9', $v, '2048^2x4', $r, $dt, fmt_e($s));
        }
    }
}

// K9 mt : 4 processus créés avant la mesure ; chacun garde ses lignes (et une ligne de bord de part et d'autre) dans
// deux grilles plates privées, publie ses deux lignes extrêmes dans un segment partagé à chaque itération (double
// tampon) et lit celles de ses voisins ; à la fin, il écrit ses lignes dans la grille finale du segment.
function run_k9_mt(int $reps): void
{
    global $WARMUP;
    $row = M9 * 8;
    $halo = 0; // 4 processus x 2 lignes x 2 tampons
    $final = 16 * $row; // grille finale
    $shm = shmop_open(0, 'c', 0600, $final + M9 * $row);
    shmop_delete($shm);
    echo "META;k9_mt;4 processus (pcntl_fork) créés avant la mesure, lignes privées, lignes voisines échangées par un segment partagé (shmop, pack/unpack), grille finale écrite dans le segment (dans le chrono)\n";
    $job = function (int $t, string $cmd) use ($shm, $row, $halo, $final): string {
        static $a = null, $b = null, $r0 = 0, $r1 = 0, $nl = 0, $it = 0;
        if ($cmd === 'init') {
            $r0 = 1 + intdiv((M9 - 2) * $t, 4);
            $r1 = 1 + intdiv((M9 - 2) * ($t + 1), 4);
            $nl = $r1 - $r0 + 2; // lignes r0-1 .. r1
            $a = [];
            for ($l = 0; $l < $nl; $l++) {
                for ($j = 0; $j < M9; $j++) {
                    $a[] = k9_init($r0 - 1 + $l, $j);
                }
            }
            $b = $a;
            $b[0] = $a[0];
            $it = 0;
            return 'ok';
        }
        if ($cmd === 'it') {
            if ($it > 0) { // lignes voisines publiées à l'itération précédente
                $par = ($it - 1) % 2;
                if ($t > 0) {
                    $v = unpack('d*', shmop_read($shm, $halo + ((($t - 1) * 2 + 1) * 2 + $par) * $row, $row));
                    for ($j = 0; $j < M9; $j++) {
                        $a[$j] = $v[$j + 1];
                    }
                }
                if ($t < 3) {
                    $v = unpack('d*', shmop_read($shm, $halo + ((($t + 1) * 2) * 2 + $par) * $row, $row));
                    $o = ($nl - 1) * M9;
                    for ($j = 0; $j < M9; $j++) {
                        $a[$o + $j] = $v[$j + 1];
                    }
                }
            }
            k9_rows($a, $b, 1, $nl - 1);
            $par = $it % 2;
            shmop_write($shm, pack('d*', ...array_slice($b, M9, M9)), $halo + (($t * 2) * 2 + $par) * $row);
            shmop_write($shm, pack('d*', ...array_slice($b, ($nl - 2) * M9, M9)), $halo + (($t * 2 + 1) * 2 + $par) * $row);
            [$a, $b] = [$b, $a];
            $it++;
            return 'ok';
        }
        // fin : lignes r0..r1-1 de la grille courante écrites dans la grille finale du segment
        for ($l = 1; $l < $nl - 1; $l++) {
            shmop_write($shm, pack('d*', ...array_slice($a, $l * M9, M9)), $final + ($r0 - 1 + $l) * $row);
        }
        return 'ok';
    };
    $ws = workers(4, $job);
    for ($r = -$WARMUP; $r < $reps; $r++) {
        run_workers($ws, 'init');
        $t0 = hrtime(true);
        for ($it = 0; $it < 4; $it++) {
            run_workers($ws, 'it');
        }
        run_workers($ws, 'fin');
        $dt = (hrtime(true) - $t0) / 1e9;
        $s = 0.0;
        for ($i = 0; $i < M9; $i++) {
            if ($i === 0 || $i === M9 - 1) {
                for ($j = 0; $j < M9; $j++) {
                    $s += k9_init($i, $j);
                }
            } else {
                foreach (unpack('d*', shmop_read($shm, $final + $i * $row, $row)) as $val) {
                    $s += $val;
                }
            }
        }
        if ($r >= 0) {
            result('k9', 'mt', '2048^2x4', $r, $dt, fmt_e($s));
        }
    }
    stop_workers($ws);
}

// ------------------------------------------------------------------ K10
const M10 = 1 << 22;
const CAP10 = 1 << 14;

function k10_natural(): int
{
    $s = 0;
    $prod = new Fiber(function (): void {
        for ($x = 1; $x <= M10; $x++) {
            Fiber::suspend($x);
        }
    });
    $x = $prod->start();
    while (!$prod->isTerminated()) {
        $s += $x;
        $x = $prod->resume();
    }
    return $s;
}

function k10_tuned(): int
{
    $s = 0;
    $buf = array_fill(0, CAP10, 0);
    $w = 0; // écrits
    $rd = 0; // lus
    $prod = new Fiber(function () use (&$buf, &$w, &$rd): void {
        for ($x = 1; $x <= M10; $x++) {
            if ($w - $rd === CAP10) {
                Fiber::suspend();
            }
            $buf[$w & (CAP10 - 1)] = $x;
            $w++;
        }
    });
    $prod->start();
    while (true) {
        while ($rd < $w) {
            $s += $buf[$rd & (CAP10 - 1)];
            $rd++;
        }
        if ($prod->isTerminated()) {
            break;
        }
        $prod->resume();
    }
    return $s;
}

function run_k10(string $v, int $reps): void
{
    echo "META;k10_mechanism;PHP n'a pas de fils : Fibers (coroutines)" . ($v === 'natural'
            ? ', une suspension par valeur' : ', anneau borné rempli par lots') . "\n";
    bench('k10', $v, '2^22', $reps, $v === 'natural' ? 'k10_natural' : 'k10_tuned', []);
}

// ------------------------------------------------------------------ main
[$k, $v, $reps] = [$argv[1], $argv[2], (int)$argv[3]];
$p = $argv[4] ?? '';
match ($k) {
    'k1' => run_k1($v, $reps),
    'k2' => run_k2($v, $reps, $p),
    'k3' => run_k3($v, $reps),
    'k4' => run_k4($v, $reps),
    'k5' => run_k5($v, $reps),
    'k6' => run_k6($v, $reps, $p),
    'k7' => run_k7($v, $reps),
    'k8' => run_k8($v, $reps),
    'k9' => run_k9($v, $reps),
    'k10' => run_k10($v, $reps),
};
