#!/bin/bash
# sync.sh — Boutique Zepeda
# Uso: bash ~/books-label/sync.sh
#
# - Protege lista_precios.xlsx (remoto siempre gana en conflicto)
# - Backup automático del xlsx antes de cada sync
# - Todo lo demás se alinea solo

set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
XLSX_REL="fase_1/salidas/lista_precios.xlsx"
XLSX_BAK="fase_1/salidas/lista_precios.bak.xlsx"

cd "$REPO_DIR"

echo "🔄 Sincronizando desde $(hostname)..."

# ── Backup del xlsx antes de tocar nada ──────────────────────────────────
if [[ -f "$XLSX_REL" ]]; then
    cp "$XLSX_REL" "$XLSX_BAK"
    echo "💾 Backup: $XLSX_BAK"
fi

# ── Traer cambios del remoto ──────────────────────────────────────────────
git fetch origin

# ── Merge: en conflicto de xlsx, el remoto gana ──────────────────────────
git merge origin/main -X theirs --no-edit 2>/dev/null || true

# ── Commit de cambios locales ─────────────────────────────────────────────
git add .

if git diff --cached --quiet; then
    echo "ℹ️  Sin cambios locales nuevos."
else
    git commit -m "sync: $(hostname) · $(date '+%Y-%m-%d %H:%M:%S')"
fi

# ── Push ─────────────────────────────────────────────────────────────────
git push origin main

echo "✅ Sync completado."
