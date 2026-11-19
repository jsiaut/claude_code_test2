#!/bin/sh
# v4, point 2 : enregistre l'état de la campagne en cours (mesures brutes, calibration, journaux) dans le dépôt et le
# pousse, pour qu'une interruption de la machine ne perde rien ; la campagne reprend où elle s'est arrêtée.
cd "$(dirname "$0")/../.."
W=results/sizes/work
mkdir -p results/sizes/raw
[ -d $W/raw ] && cp $W/raw/*.jsonl results/sizes/raw/ 2>/dev/null
for f in calib.json campaign.log campaign.out; do [ -f $W/$f ] && cp $W/$f results/sizes/$f; done
git add results/sizes
git diff --cached --quiet && exit 0
n=$(cat results/sizes/raw/*.jsonl 2>/dev/null | wc -l)
git commit -q -m "v4, point 2 : campagne des tailles en cours ($n processus enregistrés)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_014nP7V1QZuSobEutVGCERvp"
for i in 2 4 8 16; do git push -q -u origin claude/great-goodall-49iwdz && break || sleep $i; done
git log --oneline -1
