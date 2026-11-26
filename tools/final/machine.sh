#!/bin/sh
# Campagne (docs/METHOD.md, 6) : enregistrement d'une machine avant ses premières mesures, à son arrivée (début de la
# campagne, ou après un redémarrage). Usage : tools/final/machine.sh <numéro>
# 1. caractérisation au repos (tools/sizes/hwchar.sh -> results/hw/machine<numéro>), si elle n'est pas déjà faite ;
# 2. numéro inscrit dans /dev/shm/ms_final_machine (lu par le pilote ; un redémarrage l'efface) ;
# 3. versions des chaînes de la machine (tools/versions.sh -> toolchains.txt du répertoire de la campagne) ;
# 4. b3 à l'arrivée, machine au repos ;
# 5. toutes les constructions (tools/final/build.py), puis comparaison de leurs empreintes avec celles des machines
#    précédentes (tools/final/compare_builds.py -> builds_compare.txt).
# Répertoire de la campagne : results/final, ou celui de MS_CAMPAIGN_DIR. Refuse une machine d'un autre modèle que
# celui de la campagne. MS_LANGS=a,b : ne construit que ces langages (remesure d'un langage : docs/V5_2.md, 3).
set -e
cd "$(dirname "$0")/../.."
N=$1
[ -n "$N" ] || { echo "usage : $0 <numéro de machine>" >&2; exit 2; }
R=${MS_CAMPAIGN_DIR:-results/final}
# une campagne se mesure sur un seul modèle de processeur : celui de model.txt dans son répertoire (6/207/2 sans lui)
M=$(cat "$R/model.txt" 2>/dev/null || echo 6/207/2)
CUR=$(awk -F': ' '/^cpu family/ {f = $2} /^model\t/ {m = $2} /^stepping/ {print f "/" m "/" $2; exit}' /proc/cpuinfo)
[ "$CUR" = "$M" ] || { echo "machine.sh : processeur $CUR, la campagne de $R se mesure sur $M" >&2; exit 1; }
[ -f results/hw/machine$N/stream.txt ] || sh tools/sizes/hwchar.sh results/hw/machine$N
echo "$N" > /dev/shm/ms_final_machine
mkdir -p "$R"
sh tools/versions.sh > "$R/toolchains.txt"
python3 tools/final/campaign.py b3 "arrivée de la machine $N"
python3 tools/final/build.py --jobs 3 --footprint ${MS_LANGS:+--langs "$MS_LANGS"}
python3 tools/final/compare_builds.py
sh tools/final/save_progress.sh
