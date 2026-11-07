#!/bin/bash
# Remarque sur PHP (docs/PHP.md, 5) : faits vérifiés dans les listes officielles de php.net et les sources des
# archives (SHA-256 des listes), puis reproductions sur 8.3.36, 8.4.27, 8.5.12 (publié), 8.5.13RC1 et 8.6.0RC5, toutes
# construites avec les options du banc (tools/php_remark/build.sh). Sortie : results/php_remark/facts.txt.
# Les temps sont ceux d'exécutions de mise au point (une à quatre répétitions), sur une machine au repos.
D=$(cd "$(dirname "$0")" && pwd)
DL=/opt/dl/php_rq
SRC=$D/src
T=$(mktemp -d)
cp $SRC/*.php $D/../php_check/src/jit_stack_bug.php $T/ && touch -d '-1 min' $T/*.php
VERS="8.3.36:php83 8.4.27:php84 8.5.12:php85 8.5.13RC1:php8513rc1 8.6.0RC5:php86rc5"
tarball() { if [ "$1" = 8.5.12 ]; then echo /opt/dl/php/php-8.5.12.tar.xz; else echo $DL/php-$1.tar.xz; fi; }
flags() { # 8.3 et 8.4 : OPcache est une extension partagée ; 8.3 : tampon du JIT nul par défaut
  local f="-d memory_limit=-1 -d opcache.enable_cli=1 -d opcache.file_update_protection=0"
  case $1 in 8.3*) f="-d zend_extension=opcache $f -d opcache.jit_buffer_size=64M" ;; 8.4*) f="-d zend_extension=opcache $f" ;; esac
  echo "$f"
}
echo "# tools/php_remark/facts.sh, $(date '+%Y-%m-%d %H:%M:%S'), $(grep -m1 'model name' /proc/cpuinfo | cut -d: -f2), modèle $(grep -m1 -E '^model\s' /proc/cpuinfo | cut -d: -f2)"
echo "== 1. Listes officielles (php.net : /releases/?json&version=…, /pre-release-builds.php?format=json)"
for v in 8.3 8.4 8.5; do python3 -c "import json;d=json.load(open('$DL/rel_$v.json'));print('stable', d['version'], d['date'])"; done
python3 -c "
import json; d=json.load(open('$DL/pre.json'))
for k,v in d.items():
    r=v.get('release',{}) if isinstance(v,dict) else {}
    if r.get('enabled', True) and r.get('version'): print('candidate', r['version'], r['date'])"
(cd $DL && sha256sum -c sums.txt)
python3 -c "import json;d=json.load(open('$DL/rel_8.5.json'));print([s['sha256'] for s in d['source'] if s['filename']=='php-8.5.12.tar.xz'][0]+'  /opt/dl/php/php-8.5.12.tar.xz')" | sha256sum -c
echo "== 2. Sources"
for spec in $VERS; do v=${spec%%:*}; tb=$(tarball $v)
  echo "-- $v : réglages par défaut (ext/opcache/zend_accelerator_module.c, jit/zend_jit.h)"
  tar xOf $tb php-$v/ext/opcache/zend_accelerator_module.c | grep -E 'INI_(ENTRY|BOOLEAN)\("opcache\.(enable_cli|jit|jit_hot_loop|jit_blacklist_root_trace)"' | sed -E 's/^[ \t]*STD_PHP_INI_(ENTRY|BOOLEAN)\("([^"]+)" *, *("[^"]*"|[A-Z_]+).*/\2 = \3/'
  tar xOf $tb php-$v/ext/opcache/jit/zend_jit.h | grep -E 'define ZEND_JIT_DEFAULT_BUFFER_SIZE' | sed 's/^#define //'
  echo "   FFI dans le code du JIT (zend_jit*.c, zend_jit*.h) : $(tar xOf $tb --wildcards "php-$v/ext/opcache/jit/zend_jit*" 2>/dev/null | grep -c -w -i 'ffi\|zend_ffi') occurrence(s)"
done
tb=$(tarball 8.5.12)
echo "-- 8.5.12 : arrêt d'une trace (jit/zend_jit_internal.h) et liste noire (jit/zend_jit_trace.c)"
tar xOf $tb php-8.5.12/ext/opcache/jit/zend_jit_internal.h | grep -E '_\(COMPILER_ERROR' | sed 's/^[ \t]*//'
tar xOf $tb php-8.5.12/ext/opcache/jit/zend_jit_trace.c | grep -E 'cache_count\[i\] >= JIT_G\(blacklist_root_trace\)' | sed 's/^[ \t]*//'
echo "-- 8.5.12 : collecteur de cycles (Zend/zend_gc.c, zend_variables.h)"
tar xOf $tb php-8.5.12/Zend/zend_gc.c | grep -E '^#define GC_THRESHOLD_(DEFAULT|STEP|MAX|TRIGGER)'
tar xOf $tb php-8.5.12/Zend/zend_variables.h | sed -n '/static zend_always_inline void zval_ptr_dtor_nogc/,/^}/p;/static zend_always_inline void i_zval_ptr_dtor/,/^}/p'
echo "-- 8.6.0RC5 : UPGRADING, section « New Features » : mentions de threads, SIMD, struct"
tar xOf $DL/php-8.6.0RC5.tar.xz php-8.6.0RC5/UPGRADING | awk '/^2\. New Features/{n++} n==2' | awk '/^3\. /{exit} {print}' > $T/nf.txt
echo "   $(grep -c -i 'thread' $T/nf.txt) thread, $(grep -c -i 'simd' $T/nf.txt) SIMD, $(grep -c -i -w 'struct\|structs' $T/nf.txt) struct ; RFC du cœur : $(grep -A40 '^- Core:' $T/nf.txt | grep -m6 'RFC:' | sed 's#.*/rfc/##' | tr '\n' ' ')"
echo "== 3. Reproductions (machine au repos)"
for spec in $VERS; do v=${spec%%:*}; PHP=/opt/${spec##*:}/bin/php; F=$(flags $v)
  echo "-- $v ($($PHP -v | head -1 | cut -d' ' -f1-2))"
  for j in tracing function disable; do echo "   pile : $($PHP $F -d opcache.jit=$j $T/jit_stack_bug.php)"; done
  for form in natural byval reads samerow otherrow mixed tworows nomul; do
    $PHP $F -d opcache.jit=tracing -d opcache.jit_debug=212992 $T/k9_jit.php $form 2 > $T/o.txt 2>&1
    echo "   K9 $form : erreurs de compilation $(grep -c 'abort (JIT compilation error)' $T/o.txt), liste noire $(grep -c 'blacklisted$' $T/o.txt), traces compilées $(grep -c ' compiled$' $T/o.txt) ; s par répétition $(grep "^$v;" $T/o.txt | cut -d';' -f4 | tr '\n' ' ')"
  done
  for form in foreach foreach_gcoff index index_var; do
    $PHP $F -d opcache.jit=tracing $T/k1_gc.php $form seq 2 | sed "s/^/   K1 /"
  done
done
rm -rf $T
