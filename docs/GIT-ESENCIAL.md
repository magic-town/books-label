# Git Esencial — books-label

**Angangueo Point of Sale | Febrero 2026**

Comandos ordenados de mayor a menor frecuencia de uso.
Ver también: [Documentación oficial de Git](https://git-scm.com/doc)

---

## Configuración inicial (solo una vez)

```bash
git config --global user.name "magic-town"
git config --global user.email "brillantehogar2024@gmail.com"
```

---

## 0. SYNC — Flujo diario simplificado (recomendado)

Un solo comando reemplaza el pull de inicio y el push de cierre.

### Instalación (una sola vez, desde el repo)

```bash
cd ~/books-label

cat > sync.sh << 'EOF'
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
EOF

chmod +x sync.sh
git add sync.sh
git commit -m "agrega script de sincronización"
git push https://magic-town@github.com/magic-town/books-label.git main
```

> La otra máquina recibe el script la próxima vez que haga pull.

### Uso diario

```bash
cd ~/books-label && bash sync.sh
```

Ejecutar **al iniciar** y **al terminar** cada sesión de trabajo.
El commit generado muestra fecha, hora y archivos modificados. Por ejemplo:

```
sync 2026-03-09 14:32 | docs/CHECKLIST.md, scripts/etiquetas.py
```

---

## 1. PULL — Antes de trabajar, siempre

Descarga los cambios más recientes del repo.
Ejecutar **siempre** antes de empezar a trabajar.

```bash
git pull https://magic-town@github.com/magic-town/books-label.git main
```

---

## 2. STATUS — ¿Qué cambió?

Muestra qué archivos fueron modificados.

```bash
git status
```

---

## 3. ADD — Preparar cambios para guardar

Agregar todos los cambios:

```bash
git add .
```

Agregar un archivo específico:

```bash
git add docs/CHECKLIST.md
```

---

## 4. COMMIT — Guardar cambios con mensaje

Siempre con un mensaje claro de qué se hizo.

```bash
git commit -m "descripción corta de lo que hiciste"
```

Ejemplos de buenos mensajes:

```bash
git commit -m "fix: corregir posición de etiqueta en sandalias"
git commit -m "docs: actualizar checklist fase 1"
git commit -m "feat: agregar script para proveedor nuevo"
```

---

## 5. PUSH — Subir cambios al repo

```bash
git push https://magic-town@github.com/magic-town/books-label.git main
```

---

## 6. LOG — Ver historial de cambios

```bash
git log --oneline -5
```

---

## 7. DIFF — Ver exactamente qué cambió

Antes de hacer commit, ver línea por línea qué se modificó:

```bash
git diff
```

---

## 8. RESTORE — Deshacer cambios no guardados

Si algo salió mal y quieres regresar al estado anterior:

```bash
git restore nombre_del_archivo.py
```

> Solo funciona si aún **no** hiciste commit.

---

## Flujo diario completo (manual)

Si prefieres no usar `sync.sh`, el flujo manual es:

```bash
# 1. Antes de empezar
cd ~/books-label
git pull https://magic-town@github.com/magic-town/books-label.git main

# 2. Trabajar: editar scripts, mover archivos, actualizar docs, etc.

# 3. Al terminar
git status
git add .
git commit -m "descripción de lo que hiciste"
git push https://magic-town@github.com/magic-town/books-label.git main
```

---

## Regla de oro

> Pull antes de trabajar.
> Commit seguido con mensajes claros.
> Push al terminar.
>
> Si algo se rompe, Git lo tiene guardado.
