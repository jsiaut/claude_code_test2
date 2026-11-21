#!/bin/sh
# v4, point 3 : enregistre l'état de la campagne en cours (mesures brutes, calibration, journaux) dans le dépôt et le
# pousse, pour qu'une interruption de la machine ne perde rien ; la campagne reprend où elle s'est arrêtée.
cd "$(dirname "$0")/../.."
W=results/equal/work
mkdir -p results/equal/raw
[ -d $W/raw ] && cp $W/raw/*.jsonl results/equal/raw/ 2>/dev/null
for f in calib.json campaign.log campaign.out; do [ -f $W/$f ] && cp $W/$f results/equal/$f; done
git add results/equal/raw results/equal/calib.json results/equal/campaign.log results/equal/campaign.out 2>/dev/null
git diff --cached --quiet && exit 0
n=$(cat results/equal/raw/*.jsonl 2>/dev/null | wc -l)
git commit -q -m "v4, point 3 : campagne des conditions égales en cours ($n processus enregistrés)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_014nP7V1QZuSobEutVGCERvp"
for i in 2 4 8 16; do git push -q -u origin claude/great-goodall-49iwdz && break || sleep $i; done
git log --oneline -1
