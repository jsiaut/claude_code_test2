#!/bin/bash
# Remarque sur PHP : construit 8.3.36, 8.4.27, 8.5.13RC1 et 8.6.0RC5 avec les options du banc (8.5.12, /opt/php85).
# Archives : listes officielles de php.net (stables : /releases/?json ; candidates : /pre-release-builds.php?format=json),
# SHA-256 vérifiés (sums.txt). Une construction à la fois ; l'arbre de construction est supprimé après l'installation.
set -e
DL=/opt/dl/php_rq
cd $DL && sha256sum -c sums.txt
for spec in "8.3.36:php83" "8.4.27:php84" "8.5.13RC1:php8513rc1" "8.6.0RC5:php86rc5"; do
  v=${spec%%:*}; p=/opt/${spec##*:}
  if [ -x $p/bin/php ]; then echo "$v déjà installé ($p)"; continue; fi
  t0=$(date +%s); cd /opt/src && rm -rf php-$v && tar xf $DL/php-$v.tar.xz && cd php-$v
  ./configure --prefix=$p --enable-pcntl --enable-shmop --enable-sysvsem --enable-sysvshm --with-ffi \
    --disable-cgi --disable-phpdbg > $DL/configure-$v.log 2>&1
  make -j4 > $DL/make-$v.log 2>&1
  make install > $DL/install-$v.log 2>&1
  cp php.ini-production $p/lib/php.ini
  cd /opt/src && rm -rf php-$v
  echo "$v -> $p ($(( $(date +%s) - t0 )) s) : $($p/bin/php -v | head -1) ; sha256 $(sha256sum $p/bin/php | cut -c1-16)"
done
