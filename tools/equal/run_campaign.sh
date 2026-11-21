#!/bin/sh
# v4, point 3 : lance la campagne des conditions égales détachée du terminal (plusieurs heures ; reprise possible : un
# processus déjà enregistré n'est pas refait). Journal : results/equal/work/campaign.out ; état :
# results/equal/work/campaign.log (recopiés dans results/equal par tools/equal/save_progress.sh à chaque fin de groupe).
cd "$(dirname "$0")/../.."
mkdir -p results/equal/work
setsid nohup python3 tools/equal/campaign.py "$@" >> results/equal/work/campaign.out 2>&1 < /dev/null &
echo "campagne lancée (pid $!)"
