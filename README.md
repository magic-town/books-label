# 🏷️ Taller de Etiquetado Automático — Boutique Zepeda

Pipeline de automatización para etiquetado de catálogos de ropa en PDF.
Convierte catálogos sin precios en catálogos listos para cliente en minutos.

---

## ¿Qué hace este proyecto?

1. Toma un catálogo PDF del proveedor (sin precios visibles)
2. Cruza los IDs de producto contra una lista de precios validada
3. Inserta automáticamente el precio junto a cada producto
4. Genera un PDF listo para compartir por WhatsApp Business

---

## Estructura del proyecto

Una vez clonado el repositorio, revisemos la arquitectura de directorios, desde tu teminal ejecuta:

```
┌─[user@hostname]─[~]
└─$ tree -L 2 ~/books-label
```

o copia y pega:

```
tree -L 2 ~/books-label
```
debes de ver una estuctura similar a la siguiete 👇



```
/home/user/books-label
├── diagnosticos
├── docs
│   ├── CHECKLIST.md
│   ├── DIAGNOSTICO.md
│   ├── git-esencial.md
│   └── SETUP.md
├── libros
├── precios
├── prompts
├── README.md
├── requirements.txt
├── salida
└── scripts
```

## Flujo de trabajo

```
PDF proveedor → Extracción LLM → Validación → Script Python → PDF etiquetado → WhatsApp
                                                    ↑                ↓
                                                    └── Diagnóstico ─┘
```

---

## Fases del proceso

| Fase | Responsable | Herramienta |
|------|-------------|-------------|
| 1. Descarga y validación de precios | Analista | Claude / Gemini + LibreOffice |
| 2. Ejecución del script | Analista | VSC o terminal |
| 3. Revisión del output | Analista | PDF viewer |
| 4. Diagnóstico si falla | Analista → Dev | `diagnosticos/` + reporte |
| 5. Publicación | Analista | Dropbox + WhatsApp Business |

---

## Requisitos

### Dependencias del sistema
```bash
sudo apt install -y \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-spa \
    libgl1-mesa-glx \
    libglib2.0-0 \
    python3-pip \
    python3-venv
```

### Entorno virtual y librerías Python
```bash
cd ~/books-label
python3 -m venv venv_catalogo
source venv_catalogo/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

> Ver `docs/SETUP.md` para instrucciones detalladas y solución de problemas.

---

## Ejecución rápida

```bash
cd ~/books-label
source venv_catalogo/bin/activate

# Prueba (páginas 1-10)
python3 scripts/catalogo_pag.py

# Catálogo completo
python3 scripts/catalogo_temprada.py
```

Antes de ejecutar, verificar en el script:
- Nombre del PDF en `libros/`
- Nombre del Excel en `precios/`
- Nombre del libro PDF etiquetado en `salida/`

---

## Diagnóstico

Cada ejecución genera un log en `diagnosticos/`.  
Ver `docs/DIAGNOSTICO.md` para saber cómo interpretar los resultados y qué reportar cuando algo no sale bien.

---

## Métricas clave

| Métrica | Qué significa |
|---------|---------------|
| Etiquetas insertadas | Precios colocados correctamente en el PDF |
| IDs únicos encontrados | Productos distintos detectados |
| Fuzzy matches | IDs con corrección automática de OCR |
| Eficiencia | `(IDs encontrados / IDs en lista) × 100` |

Una eficiencia menor al 80% requiere diagnóstico antes de publicar.

---

## Proveedores activos

| Proveedor | Categoría | Estado |
|-----------|-----------|--------|
| — | — | — |

*(Actualizar con cada proveedor nuevo)*

---

## Notas importantes

- El script **nunca será 100% estable** porque depende del formato del PDF del proveedor. Cada proveedor nuevo o temporada nueva puede requerir ajuste.
- El log es la fuente de verdad. Si el PDF se ve bien pero el log muestra baja eficiencia, hay un problema.
- Hacer **siempre** la prueba de 10-20 páginas con proveedor nuevo o temporada nueva.
- Los archivos en `salidas/` son el producto final. Nunca modificar manualmente.
