#!/bin/bash

# ── Quién ejecuta este sync ───────────────────────────────────────────────────
# Detecta automáticamente el usuario de git configurado en esta máquina.
# Si no está configurado, usa el hostname.
QUIEN=$(cat ~/books-label/.quien 2>/dev/null || git config user.name 2>/dev/null || hostname)

# ── Archivos donde esta máquina siempre gana ──────────────────────────────────
# Si eres Sonia, tu versión de tabla_precios.ods siempre tiene prioridad.
# En la máquina de Gabriel este bloque no hace nada (QUIEN no coincide).
ARCHIVOS_PROPIOS=("precios/tabla_precios.ods")
NOMBRE_SONIA="Sonia"   # debe coincidir con: git config user.name

# ── Guardar versión local de archivos prioritarios ────────────────────────────
declare -A BACKUP_HASH
if [[ "$QUIEN" == *"$NOMBRE_SONIA"* ]]; then
  for archivo in "${ARCHIVOS_PROPIOS[@]}"; do
    if [ -f "$archivo" ]; then
      cp "$archivo" "${archivo}.sonia_backup"
      BACKUP_HASH["$archivo"]=$(md5sum "$archivo" | cut -d' ' -f1)
    fi
  done
fi

# ── Bajar cambios ─────────────────────────────────────────────────────────────
echo "⬇️  Bajando cambios..."
git pull --rebase=false --no-edit

PULL_STATUS=$?

# ── Restaurar archivos propios si Sonia tenía cambios ─────────────────────────
if [[ "$QUIEN" == *"$NOMBRE_SONIA"* ]]; then
  for archivo in "${ARCHIVOS_PROPIOS[@]}"; do
    BACKUP="${archivo}.sonia_backup"
    if [ -f "$BACKUP" ]; then
      HASH_ANTES="${BACKUP_HASH[$archivo]}"
      HASH_REMOTO=$(md5sum "$archivo" 2>/dev/null | cut -d' ' -f1)
      if [ "$HASH_ANTES" != "$HASH_REMOTO" ]; then
        # El pull sobreescribió el archivo — restaurar versión de Sonia
        cp "$BACKUP" "$archivo"
        echo "📌  tabla_precios.ods — se conserva tu versión (Sonia tiene prioridad)"
      fi
      rm -f "$BACKUP"
    fi
  done
fi

if [ $PULL_STATUS -ne 0 ]; then
  # Verificar si hay conflictos de merge sin resolver
  if git diff --name-only --diff-filter=U | grep -q .; then
    # Resolver automáticamente conflictos en archivos propios
    if [[ "$QUIEN" == *"$NOMBRE_SONIA"* ]]; then
      for archivo in "${ARCHIVOS_PROPIOS[@]}"; do
        if git diff --name-only --diff-filter=U | grep -q "^${archivo}$"; then
          git checkout --ours "$archivo"
          git add "$archivo"
          echo "📌  Conflicto en $archivo resuelto — se conserva versión de Sonia"
        fi
      done
    fi

    # Ver si quedan otros conflictos
    if git diff --name-only --diff-filter=U | grep -q .; then
      echo ""
      echo "❌  Hay conflictos sin resolver en estos archivos:"
      git diff --name-only --diff-filter=U | sed 's/^/   · /'
      echo ""
      echo "   Abre cada archivo, busca las marcas <<<<<< y >>>>>> y elige qué conservar."
      echo "   Cuando termines: git add <archivo> y vuelve a ejecutar sync.sh"
      exit 1
    fi
  else
    echo ""
    echo "⚠️  No se pudo bajar. Revisa tu conexión o el estado del repo con: git status"
    exit 1
  fi
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
