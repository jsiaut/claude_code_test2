#!/bin/sh
# v4, point 2 : lance la campagne des tailles détachée du terminal (plusieurs heures ; reprise possible : un processus
# déjà enregistré n'est pas refait). Journal : results/sizes/campaign.out ; état : results/sizes/campaign.log.
cd "$(dirname "$0")/../.."
setsid nohup python3 tools/sizes/campaign.py "$@" >> results/sizes/campaign.out 2>&1 < /dev/null &
echo "campagne lancée (pid $!)"
