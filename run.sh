#!/bin/sh
# Lance l'affichage météo : se place dans le dossier du script,
# charge .env et le venv s'ils existent, puis exécute weather_display.py.
# Usage : ./run.sh [--preview [fichier.png]]

cd "$(dirname "$0")" || exit 1

if [ -f .env ]; then
    set -a
    . ./.env
    set +a
fi

if [ -f venv/bin/activate ]; then
    . venv/bin/activate
fi

exec python3 weather_display.py "$@"
