<?php
// Sonde de la grille de capacités de PHP 8.5.12 (docs/PHP.md, 2.3) : chaque ligne CAP;<case>;<valeur>;<preuve>
// est confrontée à analysis/capabilities.py par analysis/check_probes.py. Exécutée par probes/php/run.sh (mêmes
// réglages que le banc : OPcache et JIT tracing). C3 est mesurée à part (tools/c3_measure.py).

function cap(string $id, float $v, string $ev): void
{
    echo "CAP;$id;" . ($v == (int)$v ? (int)$v : $v) . ";$ev\n";
}

$ffi = FFI::cdef('
typedef struct { float x, y, z, vx, vy, vz, ax, ay, az, mass, charge, radius, temp, pressure, energy, density; } particle;
typedef struct { char c; double d; int i; } S;
typedef struct __attribute__((packed)) { char c; int i; unsigned int f : 3; } P;
typedef struct { char c; int v __attribute__((aligned(64))); } A64;
typedef union { double d; unsigned int u[2]; } U;
typedef struct { float f[16]; int n; } R;
');

// --- A : disposition
$ps = $ffi->new('particle[1000]');
$ps[1]->vx = 2.5;
$gap = FFI::sizeof($ps[0]);
cap('A1', 0.5, "FFI (extension livrée avec php-src, --with-ffi) : particle[1000] de $gap o par élément, en ligne ; les objets et les tableaux de PHP sont des références (zval de 16 o vers le tas)");
$t = $ffi->type('S');
cap('A2', 0.5, 'FFI : struct S {char; double; int} : sizeof ' . FFI::sizeof($t) . ', offsets c=' . $t->getStructFieldOffset('c')
    . ' d=' . $t->getStructFieldOffset('d') . ' i=' . $t->getStructFieldOffset('i') . ' (FFI\CType::getStructFieldOffset) ; rien pour les classes de PHP');
cap('A3', 0.5, 'FFI : struct __attribute__((packed)) {char; int; champ de 3 bits} : sizeof ' . FFI::sizeof($ffi->type('P')) . ' ; pack/unpack sur des chaînes');
$a = $ffi->new('A64[2]');
$al = FFI::alignof($ffi->type('A64'));
cap('A4', 0.5, "FFI : champ __attribute__((aligned(64))) : alignof(A64) = $al, adresse de a[1].v mod 64 = "
    . ((FFI::cast('uintptr_t', FFI::addr($a[1]->v))->cdata) % 64) . ' (dépend de l\'allocation ; FFI::new aligne sur le type)');
$u = $ffi->new('U');
$u->d = 1.0;
$w = unpack('V2', pack('e', 1.0));
cap('A5', 0.5, "pack('e', 1.0) / unpack('V2') : $w[1], $w[2] ; union FFI double/uint32[2] : {$u->u[0]}, {$u->u[1]}");
cap('A6', 0, 'aucun conteneur SoA (tableaux séparés écrits à la main)');
$r = $ffi->new('R');
cap('A7', 0.5, 'FFI : struct {float f[16]; int n;} : sizeof ' . FFI::sizeof($r) . ' (tableau fixe en ligne)');
$x = $ffi->new('uint8_t[4]');
$x[0] = 300;
cap('A8', 0.5, "FFI : uint8_t, int16_t, float pour le stockage (uint8_t ← 300 donne {$x[0]}) ; les valeurs de PHP sont des int de 64 bits et des float de 64 bits");

// --- B : mémoire
cap('B1', 1, 'comptage de références (libération immédiate) ; le collecteur de cycles se désactive : gc_disable() → gc_enabled() = '
    . (gc_disable() || true ? var_export(gc_enabled(), true) : '') . ', comme gc.disable de Python');
gc_enable();
cap('B2', 0, 'aucun allocateur à choisir ni arène (le gestionnaire de mémoire de Zend est interne)');
$m0 = memory_get_usage();
$s = 0.0;
for ($i = 0; $i < 1000000; $i++) {
    $s += $i * 0.5;
}
$m1 = memory_get_usage();
cap('B3', 0, 'entiers et flottants jamais boxés (dans le zval : un million d\'opérations, ' . ($m1 - $m0) . ' octets de plus) ; tableaux, objets et chaînes toujours sur le tas, pas de retour multiple sans tableau');
function f3(int $a): int { return $a + 1; }
$m0 = memory_get_usage();
for ($i = 0; $i < 1000000; $i++) {
    $s = f3($i);
}
$m1 = memory_get_usage();
$arr = range(1, 100000);
$m2 = memory_get_usage();
$cp = $arr;
$cp[0] = 0; // séparation : copie cachée
$m3 = memory_get_usage();
cap('B4', 0.5, 'arithmétique et appels n\'allouent pas (un million d\'appels : ' . ($m1 - $m0) . ' octets) ; la copie sur écriture copie un tableau partagé à la première écriture (' . ($m3 - $m2) . ' octets pour 100 000 entiers), comme la croissance des tables de Lua');
$p = FFI::addr($ps[0]);
$q = $p + 1;
cap('B5', 0.5, 'pointeurs par la FFI : FFI::addr, arithmétique (p + 1 pointe la particule suivante : vx = ' . $q[0]->vx . ')');

// --- C : SIMD
cap('C1', 0, 'aucun type vectoriel');
cap('C2', 0, 'aucune intrinsèque');
cap('C4', 0, 'aucun contrôle de la réassociation (le JIT garde l\'ordre ; aucune somme réassociée dans la bibliothèque : array_sum est séquentielle)');
cap('C5', 0, 'aucune construction de parallélisme de données ; seulement des processus (pcntl_fork) à écrire à la main');

// --- D : concurrence
$shm = shmop_open(0, 'c', 0600, 64);
shmop_delete($shm);
$pid = pcntl_fork();
if ($pid === 0) {
    shmop_write($shm, pack('q', 42), 0);
    exit(0);
}
pcntl_waitpid($pid, $st);
cap('D1', 0.5, 'pas de threads : processus (pcntl_fork, extension livrée, CLI) et segment System V partagé (shmop) lu et écrit par copie : le fils écrit '
    . unpack('q', shmop_read($shm, 0, 8))[1] . ', le parent le lit ; Fibers sans parallélisme');
cap('D2', 0, 'aucun atomique (sysvsem : sémaphores, des verrous)');
cap('D3', 0, 'aucune aide de ligne de cache');
$cpus = pcntl_getcpuaffinity();
$ok = pcntl_setcpuaffinity(null, [0]);
cap('D4', 0.5, 'pcntl_setcpuaffinity (PHP 8.4, processus entier) : ' . var_export($ok, true) . ' → ' . json_encode(pcntl_getcpuaffinity()) . ' (avant : ' . json_encode($cpus) . ')');
pcntl_setcpuaffinity(null, $cpus);
cap('D5', 0, 'ni barrière ni pause');

// --- E : contrôle du code
$jit = opcache_get_status(false)['jit'] ?? [];
cap('E1', 0.5, 'JIT d\'OPcache (moteur IR) inactif par défaut (opcache.jit=disable, opcache.enable_cli=0) ; ici on=' . var_export($jit['on'] ?? false, true)
    . ', kind=' . ($jit['kind'] ?? '?') . ' ; le listage du code machine (opcache.jit_debug=1) exige une construction --with-capstone ; interfaces gdb et perf sans reconstruire');
cap('E2', 0, 'aucun');
cap('E3', 0, 'aucun');
cap('E4', 0, 'aucun');
cap('E5', 0, 'aucune annotation');
$c = $ffi->new('int[4]');
try {
    $c[4] = 1;
    $chk = 'pas d\'exception';
} catch (Throwable $e) {
    $chk = get_class($e) . ' : ' . $e->getMessage();
}
$c8 = $ffi->new('int[8]');
$pi = FFI::cast('int*', FFI::addr($c8[0]));
$pi[6] = 7; // pointeur : aucune vérification d'indice (ici dans l'allocation de 8 int, sans comportement indéfini)
cap('E6', 0.5, "seulement par les pointeurs de la FFI (non vérifiés) : int[4], indice 4 → $chk ; par un pointeur int*, aucun contrôle (p[6] = {$c8[6]}) ; les tableaux de PHP rendent null et un avertissement hors des clés");
cap('E7', 0, 'ni génériques ni calcul à la compilation (constantes seulement)');

// --- F : divers
$g = $ffi->new('double[3][4]');
$g[2][3] = 5.0;
$flat = FFI::cast('double*', FFI::addr($g[0][0]));
cap('F1', 0.5, 'tableaux multidimensionnels contigus par la FFI : double[3][4], g[2][3] = élément 11 du tableau aplati (' . $flat[11] . ') ; les tableaux de PHP sont des tables de hachage imbriquées');
cap('F2', 0, 'aucun');
$o = PHP_INT_MAX + 1;
$y = $ffi->new('uint32_t');
$y->cdata = 4294967296 + 5;
cap('F3', 0.5, 'int de 64 bits signé : le dépassement passe en float (PHP_INT_MAX + 1 = ' . var_export($o, true) . ', ' . gettype($o) . ') ; masques & 0xFFFFFFFF ; uint32_t de la FFI enveloppe (2^32 + 5 → ' . $y->cdata . '), comme ctypes en Python');
cap('F4', 0, 'pas de projection de fichier (file_get_contents copie ; mmap seulement par la FFI vers la libc)');
