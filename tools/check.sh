#!/bin/sh
# Garde-fou du dépôt : régénère chaque sortie dérivée et vérifie qu'elle est identique, à l'octet près, à celle du
# dépôt ; vérifie aussi le plan de la campagne, sans rien mesurer (aucune chaîne de compilation n'est nécessaire).
# À lancer avant et après tout changement du code d'analyse, des outils ou de la grille.
#
# Usage : sh tools/check.sh            tout, y compris le classement complet (20 000 variantes : environ une demi-heure)
#         sh tools/check.sh --rapide   le classement est calculé sur 200 variantes et comparé à son empreinte de
#                                      référence (tools/check.ref) : environ une minute en tout
#         sh tools/check.sh --ref      réécrit tools/check.ref ; seulement après un changement voulu de l'analyse
#
# Les sorties régénérées sur place (grille, relevé des formes, graphique) sont comparées à l'index de git : après un
# échec, « git diff » montre l'écart, « git checkout -- <fichier> » le défait.
set -u
cd "$(dirname "$0")/.."
export PYTHONDONTWRITEBYTECODE=1
MODE=${1:-}
REF=tools/check.ref
fail=0
ok() { echo "  ok     $1"; }
ko() { echo "  ÉCHEC  $1"; fail=1; }
same() { if git diff --quiet -- "$@"; then ok "inchangé : $*"; else ko "diffère du dépôt : $*"; fi; }
is() { if [ "$2" = "$3" ]; then ok "$1 : $2"; else ko "$1 : « $2 », attendu « $3 »"; fi; }
quick() {  # empreintes du classement calculé sur 200 variantes et 40 rééchantillonnages
  UA=200 BOOT=40 FINAL_OUT="$1" python3 analysis/final_v4.py > /dev/null || return 1
  (cd "$1" && sha256sum analysis.json report_final.md)
}

T=$(mktemp -d)
trap 'rm -rf "$T"' EXIT

if [ "$MODE" = "--ref" ]; then
  quick "$T" > "$REF" && cat "$REF" && echo "$REF réécrit"
  exit $?
fi

echo "1. Grille de contrôle et sondes"
is "sondes contre grille" "$(python3 analysis/check_probes.py | head -1)" "660 lignes de sonde, 0 divergences"
same results/probes/summary.md
python3 analysis/capabilities_md.py > /dev/null || ko "analysis/capabilities_md.py"
same docs/CAPABILITIES.md

echo "2. Relevé des formes du plafond"
python3 tools/converge/inventory.py > /dev/null || ko "tools/converge/inventory.py"
same results/converge/forms.json results/converge/inventory.md

echo "3. Plan de la campagne (rien n'est exécuté)"
is "constructions" "$(python3 tools/final/build.py --list | tail -1)" "117 constructions"
is "cellules à étalonner" "$(python3 tools/final/campaign.py calibrate --dry | awk '{n += $(NF - 1)} END {print n}')" "2613"
is "processus des trois passes" "$(python3 tools/final/campaign.py run --dry | tail -1)" "8559 processus"
is "remesure de Zig" "$(MS_DEV=1 python3 tools/final/build.py --langs zig --list | tail -1)" "12 constructions"
is "remesure de Go" "$(MS_GOFIX=1 python3 tools/final/build.py --langs go --list | tail -1)" "12 constructions"

echo "4. Classement"
if [ "$MODE" = "--rapide" ]; then
  if quick "$T" > "$T/sums" && cmp -s "$T/sums" "$REF"; then ok "200 variantes : empreintes de $REF"
  else ko "200 variantes : empreintes différentes de $REF"; fi
else
  if FINAL_OUT="$T" python3 analysis/final_v4.py > /dev/null; then
    if cmp -s "$T/report_final.md" results/report_final.md; then ok "inchangé : results/report_final.md"
    else ko "diffère du dépôt : results/report_final.md"; fi
    if cmp -s "$T/analysis.json" results/final/analysis.json; then ok "inchangé : results/final/analysis.json"
    else ko "diffère du dépôt : results/final/analysis.json"; fi
  else ko "analysis/final_v4.py"; fi
fi
# tri des écarts du code naturel (docs/V5_3.md) : tout couple signalé doit avoir une cause au registre de l'analyse
is "tri des écarts : couples à examiner, causes sans couple" "$(python3 -c "
import json
t = json.load(open('results/final/analysis.json'))['triage']
print(len(t['unexplained']), len(t['stale']))")" "0 0"

echo "5. Graphique"
python3 analysis/charts_final.py > /dev/null || ko "analysis/charts_final.py"
same results/charts/classement_v4.svg

if [ $fail = 0 ]; then echo "Tout est conforme."; else echo "Au moins un contrôle a échoué."; fi
exit $fail
