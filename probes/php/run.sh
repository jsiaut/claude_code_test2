#!/bin/sh
# sonde de la grille de PHP (docs/PHP.md, 2.3) : mêmes réglages que bench/php/run
exec /opt/php85/bin/php -d memory_limit=-1 -d opcache.enable_cli=1 -d opcache.jit=tracing -d opcache.file_update_protection=0 "$(dirname "$0")/probe.php"
