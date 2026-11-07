<?php
// PHP 8.5.12, JIT tracing (docs/PHP.md, 2.4) : deux écritures « $st[$sp++] = … » de suite dans une boucle interne,
// relues par « $st[--$sp] », donnent un résultat faux : la construction en ordre préfixe d'un arbre complet de
// profondeur 10 (2047 nœuds) ne s'arrête plus (garde à 5000 tours). Sans JIT, avec le JIT « function » ou avec une
// pile à indices explicites, le résultat est juste.
function pile_postincrement(int $D): int
{
    $st = []; $sp = 0; $top = 1; $i = 0; $d = $D; $garde = 0;
    while (true) {
        while ($d > 0) { $j = $top++; $st[$sp++] = $i; $st[$sp++] = $d - 1; $i = $j; $d--; }
        if ($sp === 0) { return $top; }
        $d = $st[--$sp]; $p = $st[--$sp]; $j = $top++; $i = $j;
        if (++$garde > 5000) { return -$top; }
    }
}
function pile_indices(int $D): int
{
    $st = []; $sp = 0; $top = 1; $i = 0; $d = $D; $garde = 0;
    while (true) {
        while ($d > 0) { $j = $top; $top++; $st[$sp] = $i; $st[$sp + 1] = $d - 1; $sp += 2; $i = $j; $d--; }
        if ($sp === 0) { return $top; }
        $sp -= 2; $d = $st[$sp + 1]; $p = $st[$sp]; $j = $top; $top++; $i = $j;
        if (++$garde > 5000) { return -$top; }
    }
}
$a = @pile_postincrement(10);
$b = pile_indices(10);
printf("jit=%s : \$st[\$sp++] -> %d noeuds ; indices explicites -> %d noeuds (attendu 2047)\n", ini_get('opcache.jit'), $a, $b);
