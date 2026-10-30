#!/bin/sh
# Copie de la remarque sur Mojo (docs/MOJO.md) : même source que bench/mojo (../mojo/ms.mojo), même compilateur,
# compilée avec -D ASSERT=none (debug_assert retirés, dont les vérifications de bornes de List). Diagnostic
# seulement : la règle du classement garde les réglages par défaut (ASSERT=safe).
set -e
cd "$(dirname "$0")"
/opt/mojo-venv/bin/mojo build -D ASSERT=none ../mojo/ms.mojo -o ms 2>&1 | grep -v Crashpad
