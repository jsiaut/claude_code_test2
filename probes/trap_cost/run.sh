#!/bin/sh
# Coût d'une trappe dans cette microVM : uprobe sur malloc et free, point d'arrêt matériel en écriture.
# Chaque programme mesure son propre temps par opération, sans puis avec l'instrument (/opt/pecount, tools/pecount.c).
cd "$(dirname "$0")" && LIBC=/lib/x86_64-linux-gnu/libc.so.6
off() { readelf -Ws $LIBC | awk -v s="$1@@GLIBC_2.2.5" '$8==s{print "0x"$2; exit}'; }
cc -O2 -o malloc_loop malloc_loop.c && cc -O2 -no-pie -o write_loop write_loop.c
echo "malloc + free, sans sonde : $(./malloc_loop)"
echo "malloc + free, uprobes sur les deux : $(/opt/pecount -o /tmp/tc_m.json -u malloc=$LIBC:$(off malloc) -u free=$LIBC:$(off free) -- ./malloc_loop)"
cat /tmp/tc_m.json
ADDR=$(./write_loop | head -1)
echo "écriture, sans point d'arrêt : $(./write_loop | tail -1)"
echo "écriture, point d'arrêt matériel : $(/opt/pecount -o /tmp/tc_w.json -w target=$ADDR:8 -- ./write_loop | tail -1)"
cat /tmp/tc_w.json
rm -f malloc_loop write_loop /tmp/tc_m.json /tmp/tc_w.json
