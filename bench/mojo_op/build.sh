#!/bin/sh
# v4, point 6 (docs/V4_OPEN.md, 5.2) : la commande publiée (mojo build par défaut, Mojo 1.2.0), plus les paquets Mojo et
# la bibliothèque d'exécution de max-core 26.7.0 (archive conda, /opt/open/mojo/maxcore).
set -e
cd "$(dirname "$0")"
case "${MS_MODE:-}" in
  "") MODE="" ;;
  unc) MODE="-D ASSERT=none" ;;
  *) echo "MS_MODE=$MS_MODE : mode inconnu pour ce langage" >&2; exit 2 ;;
esac
DEFS=$(env | grep -E '^MS_(N1|INNER5|N6|K7_LOG2|K8_LONG|K8_REQ|M9|DATA_DIR)=' | sed 's/^/-D /' | tr '\n' ' ')
M=/opt/open/mojo/maxcore/lib
/opt/mojo-venv/bin/mojo build $MODE $DEFS -I $M/mojo -Xlinker -L$M -Xlinker -lAsyncRTMojoBindings -Xlinker -rpath -Xlinker $M \
  ms.mojo -o ms 2>&1 | grep -v Crashpad | grep -v "warning\|^ *[|^~]\|note:" || true
