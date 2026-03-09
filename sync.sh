#!/bin/bash
echo "⬇️  Bajando cambios..."
git pull

if [ $? -ne 0 ]; then
  echo "⚠️  Conflicto al bajar. Resuélvelo antes de continuar."
  exit 1
fi

git add -A
git diff --cached --quiet && echo "✅ Sin cambios locales." && exit 0

MSG=$(git diff --cached --name-only | head -5 | tr '\n' ', ' | sed 's/,$//')
git commit -m "sync $(date '+%Y-%m-%d %H:%M') | $MSG"
git push
echo "✅ Cambios subidos."
