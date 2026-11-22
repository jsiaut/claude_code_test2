#!/bin/sh
# v4, campagne finale (docs/V4_FINAL.md, 7) : enregistre l'état de la campagne (mesures brutes, étalonnage, b3,
# constructions, journaux, enregistrements mis à part) dans le dépôt et le pousse, pour qu'une interruption ne perde
# rien ; la campagne reprend où elle s'est arrêtée (un processus enregistré n'est pas refait).
cd "$(dirname "$0")/../.."
W=results/final/work
R=results/final
mkdir -p $R/raw $R/discarded
[ -d $W/raw ] && cp $W/raw/*.jsonl $R/raw/ 2>/dev/null
[ -d $W/discarded ] && cp $W/discarded/*.jsonl $R/discarded/ 2>/dev/null
for f in calib.json calib.jsonl b3.jsonl builds.jsonl campaign.log campaign.out; do [ -f $W/$f ] && cp $W/$f $R/$f; done
for f in $R/raw $R/discarded $R/calib.json $R/calib.jsonl $R/b3.jsonl $R/builds.jsonl $R/campaign.log \
  $R/campaign.out; do  # un à un : un fichier absent n'arrête pas les autres
  [ -e "$f" ] && git add "$f" 2>/dev/null
done
git diff --cached --quiet && exit 0
n=$(cat $R/raw/*.jsonl 2>/dev/null | wc -l)
c=$(grep -c . $R/calib.jsonl 2>/dev/null || echo 0)
git commit -q -m "v4, campagne finale en cours ($c étalonnages, $n processus enregistrés)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_014nP7V1QZuSobEutVGCERvp"
for i in 2 4 8 16; do git push -q -u origin claude/great-goodall-49iwdz && break || sleep $i; done
git log --oneline -1
