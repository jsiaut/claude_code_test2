#!/bin/sh
# Campagne (docs/METHOD.md, 6) : enregistre l'état de la campagne (mesures brutes, étalonnage, b3, constructions,
# journaux, enregistrements mis à part) dans le dépôt et le pousse sur la branche courante, pour qu'une interruption
# ne perde rien ; la campagne reprend où elle s'est arrêtée (un processus enregistré n'est pas refait). Répertoire de
# la campagne : results/final, ou celui de MS_CAMPAIGN_DIR. Le message de commit se termine par les lignes de
# MS_COMMIT_TRAILERS, si la variable est donnée (attribution de la session qui mesure).
cd "$(dirname "$0")/../.."
R=${MS_CAMPAIGN_DIR:-results/final}
W=$R/work
mkdir -p $R/raw $R/discarded
[ -d $W/raw ] && cp $W/raw/*.jsonl $R/raw/ 2>/dev/null
[ -d $W/discarded ] && cp $W/discarded/*.jsonl $R/discarded/ 2>/dev/null
for f in calib.json calib.jsonl b3.jsonl builds.jsonl campaign.log campaign.out; do [ -f $W/$f ] && cp $W/$f $R/$f; done
for f in $R/raw $R/discarded $R/calib.json $R/calib.jsonl $R/b3.jsonl $R/builds.jsonl $R/campaign.log \
  $R/campaign.out $R/builds_compare.txt $R/k4_extreme.txt $R/toolchains.txt; do  # un à un : un fichier absent n'arrête pas les autres
  [ -e "$f" ] && git add "$f" 2>/dev/null
done
git diff --cached --quiet && exit 0
n=$(cat $R/raw/*.jsonl 2>/dev/null | wc -l)
c=$(grep -c . $R/calib.jsonl 2>/dev/null || echo 0)
msg="Campagne en cours dans $R ($c étalonnages, $n processus enregistrés)"
[ -n "${MS_COMMIT_TRAILERS:-}" ] && msg="$msg

$MS_COMMIT_TRAILERS"
git commit -q -m "$msg"
branch=$(git rev-parse --abbrev-ref HEAD)
if [ "$branch" = HEAD ]; then
  echo "save_progress : pas de branche courante (HEAD détachée), commit non poussé" >&2
else
  for i in 2 4 8 16; do git push -q -u origin "$branch" && break || sleep $i; done
fi
git log --oneline -1
