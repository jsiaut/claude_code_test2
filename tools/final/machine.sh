#!/bin/sh
# v4, campagne finale (docs/V4_FINAL.md, 6) : enregistrement d'une machine avant ses premières mesures, à son arrivée
# (début de la campagne, ou après un redémarrage). Usage : tools/final/machine.sh <numéro>
# 1. caractérisation au repos (tools/sizes/hwchar.sh -> results/hw/machine<numéro>), si elle n'est pas déjà faite ;
# 2. numéro inscrit dans /dev/shm/ms_final_machine (lu par le pilote ; un redémarrage l'efface) ;
# 3. b3 à l'arrivée, machine au repos ;
# 4. toutes les constructions (tools/final/build.py), puis comparaison de leurs empreintes avec celles des machines
#    précédentes (tools/final/compare_builds.py -> results/final/builds_compare.txt).
set -e
cd "$(dirname "$0")/../.."
N=$1
[ -n "$N" ] || { echo "usage : $0 <numéro de machine>" >&2; exit 2; }
grep -q "^model[[:space:]]*: 207$" /proc/cpuinfo || echo "ATTENTION : modèle de processeur différent de 207" >&2
[ -f results/hw/machine$N/stream.txt ] || sh tools/sizes/hwchar.sh results/hw/machine$N
echo "$N" > /dev/shm/ms_final_machine
python3 tools/final/campaign.py b3 "arrivée de la machine $N"
python3 tools/final/build.py --jobs 3 --footprint
python3 tools/final/compare_builds.py
sh tools/final/save_progress.sh
