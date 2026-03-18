#!/bin/bash

# ── Quién ejecuta este sync ───────────────────────────────────────────────────
# Detecta automáticamente el usuario de git configurado en esta máquina.
# Si no está configurado, usa el hostname.
QUIEN=$(git config user.name 2>/dev/null || hostname)

# ── Bajar cambios ─────────────────────────────────────────────────────────────
echo "⬇️  Bajando cambios..."
git pull --rebase=false --no-edit

if [ $? -ne 0 ]; then
  # Verificar si hay conflictos de merge sin resolver
  if git diff --name-only --diff-filter=U | grep -q .; then
    echo ""
    echo "❌  Hay conflictos sin resolver en estos archivos:"
    git diff --name-only --diff-filter=U | sed 's/^/   · /'
    echo ""
    echo "   Abre cada archivo, busca las marcas <<<<<< y >>>>>> y elige qué conservar."
    echo "   Cuando termines: git add <archivo> y vuelve a ejecutar sync.sh"
  else
    echo ""
    echo "⚠️  No se pudo bajar. Revisa tu conexión o el estado del repo con: git status"
  fi
  exit 1
fi

# Verificar que no quedaron conflictos sin resolver después del pull
if git diff --name-only --diff-filter=U | grep -q .; then
  echo ""
  echo "❌  Quedaron conflictos sin resolver. No se puede continuar."
  git diff --name-only --diff-filter=U | sed 's/^/   · /'
  exit 1
fi

# ── Subir cambios locales ─────────────────────────────────────────────────────
git add -A

if git diff --cached --quiet; then
  echo "✅ Sin cambios locales — todo al día."
  exit 0
fi

# Construir mensaje con quién y qué archivos
ARCHIVOS=$(git diff --cached --name-only | head -5 | tr '\n' ', ' | sed 's/,$//')
MSG="sync $(date '+%Y-%m-%d %H:%M') | $QUIEN | $ARCHIVOS"

git commit -m "$MSG"

echo "⬆️  Subiendo cambios..."
git push

if [ $? -ne 0 ]; then
  echo ""
  echo "⚠️  El push falló — probablemente la otra máquina subió algo mientras tanto."
  echo "   Ejecuta sync.sh de nuevo para bajar esos cambios y reintentar."
  exit 1
fi

echo "✅ Cambios subidos: $ARCHIVOS"
