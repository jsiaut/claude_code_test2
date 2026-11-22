#!/bin/sh
# v4, point 6 : enregistre l'état de la campagne de la piste ouverte (mesures brutes, calibration, journaux, b3) dans le
# dépôt et le pousse, pour qu'une interruption ne perde rien ; la campagne reprend où elle s'est arrêtée.
cd "$(dirname "$0")/../.."
W=results/open/work
mkdir -p results/open/raw
[ -d $W/raw ] && cp $W/raw/*.jsonl results/open/raw/ 2>/dev/null
for f in calib.json campaign.log campaign.out; do [ -f $W/$f ] && cp $W/$f results/open/$f; done
git add results/open/raw results/open/calib.json results/open/campaign.log results/open/campaign.out \
  results/open/k3_ref_start.txt results/open/k3_ref_end.txt 2>/dev/null
git diff --cached --quiet && exit 0
n=$(cat results/open/raw/*.jsonl 2>/dev/null | wc -l)
git commit -q -m "v4, point 6 : campagne de la piste ouverte en cours ($n processus enregistrés)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_014nP7V1QZuSobEutVGCERvp"
for i in 2 4 8 16; do git push -q -u origin claude/great-goodall-49iwdz && break || sleep $i; done
git log --oneline -1
