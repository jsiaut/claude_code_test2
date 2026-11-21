#!/bin/sh
# PHP 8.5.12 (étiquette php-8.5.12 de php-src, archive php-8.5.12.tar.xz de php.net, SHA-256 08bc2eba…1209) :
# ./configure --prefix=/opt/php85 --enable-pcntl --enable-shmop --enable-sysvsem --enable-sysvshm --with-ffi
# --disable-cgi --disable-phpdbg, gcc 13.3 (le cc du système), options par défaut (-g -O2), puis make et make install ;
# php.ini-production copié en /opt/php85/lib/php.ini (docs/PHP.md, 2.1). Le banc est interprété (avec le JIT
# d'OPcache) : vérification syntaxique seulement.
set -e
cd "$(dirname "$0")"
/opt/php85/bin/php -l ms.php > /dev/null
