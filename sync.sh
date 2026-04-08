#!/bin/bash

# ══════════════════════════════════════════════════════════════════════════════
#  sync.sh — books-label
#  Dos máquinas, una cuenta GitHub. Identidad por hostname.
#  Sonia tiene prioridad sobre precios_tabla.ods (archivo maestro de precios).
#  Gabriel sincroniza sin tocar ese archivo; si necesita ir adelante,
#  copia el archivo vía SSH desde Sonia antes de correr este script.
# ══════════════════════════════════════════════════════════════════════════════

# ── Identidad de esta máquina ─────────────────────────────────────────────────
# Fuente de verdad: ~/books-label/.quien  (un archivo de texto con el nombre)
# Si no existe, se usa el hostname del sistema.
# Para crearlo la primera vez en cada máquina:
#   echo "Sonia" > ~/books-label/.quien
#   echo "Gabriel" > ~/books-label/.quien
QUIEN=$(cat "$(dirname "$0")/.quien" 2>/dev/null | tr -d '[:space:]' || hostname)

# ── Archivos con dueño definido ───────────────────────────────────────────────
# Formato: "NombreOwner:ruta/al/archivo"
# Para agregar mas archivos con owner distinto, añade lineas aqui.
ARCHIVOS_OWNER=(
  "Sonia:fase_2/precios/precios_tabla.ods"
)

# ── Función: ¿soy el owner de este archivo? ───────────────────────────────────
es_owner() {
  local owner="$1"
  [[ "$QUIEN" == *"$owner"* ]]
}

# ── Guardar versión local de archivos donde soy owner ────────────────────────
declare -A BACKUP_HASH
for entrada in "${ARCHIVOS_OWNER[@]}"; do
  owner="${entrada%%:*}"
  archivo="${entrada#*:}"
  if es_owner "$owner" && [ -f "$archivo" ]; then
    cp "$archivo" "${archivo}.owner_backup"
    BACKUP_HASH["$archivo"]=$(md5sum "$archivo" | cut -d' ' -f1)
  fi
done

# ── Preparar working tree para pull limpio ───────────────────────────────────
# Problema: git pull aborta si hay cambios sin commitear en archivos que el
# remoto quiere modificar, incluso antes de que corra cualquier lógica nuestra.
#
# Solución en dos pasos:
#   1. Archivos donde soy owner → git checkout (descarta working copy; ya
#      tenemos el backup, la lógica de restauración lo devuelve después).
#   2. Resto de archivos sucios → stash temporal, se recupera tras el pull.

for entrada in "${ARCHIVOS_OWNER[@]}"; do
  owner="${entrada%%:*}"
  archivo="${entrada#*:}"
  if es_owner "$owner" && [ -f "$archivo" ]; then
    if ! git diff --quiet -- "$archivo" 2>/dev/null; then
      git checkout -- "$archivo"
      echo "🧹  $archivo — copia de trabajo descartada antes del pull (owner: $owner, backup guardado)"
    fi
  fi
done

STASHED=false
if ! git diff --quiet || ! git diff --cached --quiet; then
  STASH_MSG="sync-auto-$(date +%Y%m%d-%H%M%S)"
  git stash push -m "$STASH_MSG"
  STASHED=true
  echo "📦  Cambios locales (no-owner) guardados en stash: $STASH_MSG"
fi

# ── Bajar cambios ─────────────────────────────────────────────────────────────
echo "⬇️  Bajando cambios... (máquina: $QUIEN)"
git pull --rebase=false --no-edit

PULL_STATUS=$?

# ── Restaurar archivos propios si el pull los sobreescribió ──────────────────
for entrada in "${ARCHIVOS_OWNER[@]}"; do
  owner="${entrada%%:*}"
  archivo="${entrada#*:}"
  BACKUP="${archivo}.owner_backup"

  if es_owner "$owner" && [ -f "$BACKUP" ]; then
    HASH_ANTES="${BACKUP_HASH[$archivo]}"
    HASH_REMOTO=$(md5sum "$archivo" 2>/dev/null | cut -d' ' -f1)
    if [ "$HASH_ANTES" != "$HASH_REMOTO" ]; then
      cp "$BACKUP" "$archivo"
      echo "📌  $archivo — restaurado (owner: $owner)"
    fi
    rm -f "$BACKUP"
  fi
done

# ── Resolver conflictos de merge ──────────────────────────────────────────────
if [ $PULL_STATUS -ne 0 ]; then
  if git diff --name-only --diff-filter=U | grep -q .; then

    # Resolver automáticamente conflictos en archivos donde soy owner
    for entrada in "${ARCHIVOS_OWNER[@]}"; do
      owner="${entrada%%:*}"
      archivo="${entrada#*:}"
      if es_owner "$owner" && git diff --name-only --diff-filter=U | grep -q "^${archivo}$"; then
        git checkout --ours "$archivo"
        git add "$archivo"
        echo "📌  Conflicto en $archivo resuelto — se conserva versión de $owner"
      fi
    done

    # ¿Quedan conflictos en otros archivos?
    if git diff --name-only --diff-filter=U | grep -q .; then
      echo ""
      echo "❌  Conflictos sin resolver:"
      git diff --name-only --diff-filter=U | sed 's/^/   · /'
      echo ""
      echo "   Abre cada archivo, resuelve las marcas <<<<<< / >>>>>>"
      echo "   Luego: git add <archivo> && ./sync.sh"
      exit 1
    fi

  else
    echo ""
    echo "⚠️  No se pudo bajar. Revisa tu conexión o ejecuta: git status"
    exit 1
  fi
fi

# Guardia final — no debería llegar aquí con conflictos, pero por si acaso
if git diff --name-only --diff-filter=U | grep -q .; then
  echo ""
  echo "❌  Quedaron conflictos sin resolver. No se puede continuar."
  git diff --name-only --diff-filter=U | sed 's/^/   · /'
  exit 1
fi

# ── Restaurar stash (archivos no-owner) ──────────────────────────────────────
if [ "$STASHED" = true ]; then
  git stash pop
  if [ $? -ne 0 ]; then
    echo ""
    echo "⚠️  Conflicto al restaurar cambios locales del stash."
    echo "   Revisa con: git stash show -p"
    echo "   Resuelve los conflictos y vuelve a ejecutar ./sync.sh"
    exit 1
  fi
  echo "📤  Cambios locales (no-owner) restaurados desde stash."
fi

# ── Subir cambios locales ─────────────────────────────────────────────────────
git add -A

if git diff --cached --quiet; then
  # No hay nada nuevo que commitear, pero puede haber commits pendientes de push
  PENDING=$(git log --oneline origin/main..main 2>/dev/null | wc -l)
  if [ "$PENDING" -gt 0 ]; then
    echo "⬆️  Sin cambios nuevos pero hay $PENDING commit(s) pendiente(s) de subir..."
  else
    echo "✅ Sin cambios locales — todo al día."
    exit 0
  fi
else
  ARCHIVOS_CAMBIADOS=$(git diff --cached --name-only | head -5 | tr '\n' ', ' | sed 's/,$//')
  MSG="sync $(date '+%Y-%m-%d %H:%M') | $QUIEN | $ARCHIVOS_CAMBIADOS"
  git commit -m "$MSG"
fi

echo "⬆️  Subiendo cambios..."
git push

if [ $? -ne 0 ]; then
  echo ""
  echo "⚠️  Push reportó error — verificando si los cambios llegaron..."
  git fetch origin
  PENDING=$(git log --oneline origin/main..main 2>/dev/null | wc -l)
  if [ "$PENDING" -eq 0 ]; then
    echo "✅ El push llegó correctamente a pesar del error reportado."
    exit 0
  fi
  echo "⚠️  Hay $PENDING commit(s) que no llegaron al remoto."
  echo "   Ejecuta ./sync.sh de nuevo para reintentar."
  exit 1
fi

echo "✅ Subido: $ARCHIVOS_CAMBIADOS"
