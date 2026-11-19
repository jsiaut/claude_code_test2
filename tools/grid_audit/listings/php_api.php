<?php
// API publique de la construction PHP du banc : fonctions internes, classes et leurs méthodes, constantes et directives
// ini des extensions chargées, une par ligne. Sert à tools/grid_audit/search.py (introspection, docs/V4_PLAN.md 2.1).
$out = [];
foreach (get_defined_functions()['internal'] as $f) $out[] = "fonction $f";
foreach (array_merge(get_declared_classes(), get_declared_interfaces(), get_declared_traits()) as $c) {
    $r = new ReflectionClass($c);
    if (!$r->isInternal()) continue;
    $out[] = "classe $c";
    foreach ($r->getMethods() as $m) $out[] = "méthode $c::" . $m->getName();
    foreach ($r->getConstants() as $k => $v) $out[] = "constante $c::$k";
}
foreach (get_defined_constants(true) as $ext => $cs) { if ($ext === 'user') continue; foreach ($cs as $k => $v) $out[] = "constante $k ($ext)"; }
foreach (ini_get_all(null, false) as $k => $v) $out[] = "ini $k";
foreach (get_loaded_extensions() as $e) $out[] = "extension $e";
foreach (get_loaded_extensions(true) as $e) $out[] = "extension $e";
sort($out);
echo implode("\n", array_unique($out)), "\n";
