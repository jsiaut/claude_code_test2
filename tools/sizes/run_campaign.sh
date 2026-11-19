#!/bin/sh
# v4, point 2 : lance la campagne des tailles détachée du terminal (plusieurs heures ; reprise possible : un processus
# déjà enregistré n'est pas refait). Journal : results/sizes/work/campaign.out ; état : results/sizes/work/campaign.log
# (recopiés dans results/sizes par tools/sizes/save_progress.sh).
cd "$(dirname "$0")/../.."
setsid nohup python3 tools/sizes/campaign.py "$@" >> results/sizes/work/campaign.out 2>&1 < /dev/null &
echo "campagne lancée (pid $!)"
