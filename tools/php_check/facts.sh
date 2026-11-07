#!/bin/sh
# Faits de l'ajout de PHP (docs/PHP.md, 2) : chaîne, réglages par défaut, documentation officielle (dépôt php/doc-en,
# extraction partielle dans $DOC), et reproductions (tools/php_check/src). Sortie : results/php_check/facts.txt.
# Usage : tools/php_check/facts.sh [chemin de doc-en] [chemin des sources de php-src]
DOC=${1:-/home/user/php/doc-en}
SRC=${2:-/opt/src/php-8.5.12}
PHP=/opt/php85/bin/php
JIT="-d memory_limit=-1 -d opcache.enable_cli=1 -d opcache.jit=tracing"
D=$(cd "$(dirname "$0")" && pwd)
T=$(mktemp -d)  # copies vieillies des reproductions (OPcache ne met pas en cache un script de moins de 2 s)
echo "== version et construction"
$PHP -v | head -1
$PHP -i | grep -E '^(Configure Command|Compiler|Build System|Thread Safety|Loaded Configuration File)' | sed 's/  */ /g'
sha256sum $PHP /opt/dl/php/php-8.5.12.tar.xz
echo "== liste officielle (php.net, releases/index.php?json, copiée dans /opt/dl/php/releases.json)"
python3 -c "import json; d=json.load(open('/opt/dl/php/releases.json')); [print(k, v['date'], v['tags'], [s['sha256'] for s in v['source'] if s['filename'].endswith('.tar.xz')]) for k, v in d.items()]"
echo "== réglages par défaut d'OPcache et de la FFI (sources)"
grep -n -E '"opcache\.(enable|enable_cli|jit|jit_buffer_size|file_update_protection)"' $SRC/ext/opcache/zend_accelerator_module.c | sed 's/\t/ /g'
grep -n 'define ZEND_JIT_DEFAULT_BUFFER_SIZE' $SRC/ext/opcache/jit/zend_jit.h
grep -n '"ffi.enable"' $SRC/ext/ffi/ffi.c | sed 's/\t/ /g'
sed -n '/^- Opcache:/,/^$/p' $SRC/UPGRADING | head -8
echo "== documentation (php/doc-en, $(git -C $DOC log -1 --format='%h %ci' 2>/dev/null))"
grep -n -A2 '<literal>tracing</literal>/<literal>on</literal>' $DOC/reference/opcache/ini.xml
grep -n -A4 'xml:id="language.types.integer.overflow"' $DOC/language/types/integer.xml | tail -4
grep -n 'is actually an ordered map' $DOC/language/types/array.xml
echo "== drapeaux du JIT (IR) : extensions x86 reconnues"
grep -n 'define IR_X86_' $SRC/ext/opcache/jit/ir/ir.h
echo "== fonctions de la grille (stubs)"
grep -n -E 'function (pcntl_setcpuaffinity|pcntl_getcpuaffinity|gc_disable|gc_enable)\(' $SRC/ext/pcntl/pcntl.stub.php $SRC/Zend/zend_builtin_functions.stub.php
echo "== dépassement d'entier"
$PHP -r 'var_dump(PHP_INT_MAX + 1, 4294967295 * 4294967295);'
echo "== bogue du JIT tracing (src/jit_stack_bug.php)"
cp $D/src/jit_stack_bug.php $T/jit_stack_bug.php && touch -d '-1 min' $T/jit_stack_bug.php
for j in tracing function disable; do $PHP -d opcache.enable_cli=1 -d opcache.jit=$j $T/jit_stack_bug.php; done
echo "== script récent et OPcache (src/fichier_recent.php)"
cp $D/src/fichier_recent.php $T/fichier_recent.php && $PHP $JIT $T/fichier_recent.php
touch -d '-1 min' $T/fichier_recent.php && $PHP $JIT $T/fichier_recent.php
echo "== fermeture et collecteur de cycles (src/fermeture_gc.php, 2^22 particules)"
cp $D/src/fermeture_gc.php $T/fermeture_gc.php && touch -d '-1 min' $T/fermeture_gc.php
for m in direct fermeture; do $PHP $JIT $T/fermeture_gc.php $m; done
rm -rf "$T"
