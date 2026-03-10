<img src="imagenes/asset_repo/cover.png" alt="Boutique Zepeda — Taller de Etiquetado" width="100%"/>

# 🪡 Taller de Etiquetado Automático — Boutique Zepeda

Pipeline de automatización para etiquetado de catálogos de ropa en PDF.
Convierte catálogos sin precios en catálogos listos para cliente en minutos.

---

## ¿Qué hace este proyecto?

Toma el catálogo PDF de un proveedor, cruza los IDs de producto contra una lista de precios validada, inserta automáticamente el precio junto a cada producto y genera un PDF listo para compartir por WhatsApp Business.

---

## Estructura del proyecto

```
~/books-label
├── configs/                   # Un archivo de configuración por proveedor o temporada
├── diagnosticos/              # Logs generados automáticamente en cada ejecución
├── docs/
│   ├── CHECKLIST.md           # Guía paso a paso del proceso completo
│   ├── DIAGNOSTICO.md         # Cómo interpretar logs y resolver problemas
│   ├── GIT-ESENCIAL.md        # Comandos git para el día a día
│   └── SETUP.md               # Instalación y configuración del entorno
├── imagenes/
│   ├── asset_repo/            # Imágenes para documentación y README
│   └── logos/                 # Logos operativos para insertar en catálogos
├── libros/                    # PDFs de catálogos del proveedor (input)
├── precios/                   # Archivos Excel (.xlsx) con IDs y precios validados
├── prompts/                   # Prompts para extracción de datos con LLM
├── salidas/                   # PDFs etiquetados listos para publicar (output)
├── scripts/
│   ├── catalogo_base.py       # Script principal — no editar directamente
│   └── archivo/               # Scripts anteriores conservados como referencia
├── requirements.txt
└── README.md
```

---

## Flujo de trabajo

```
Descarga → Precios Excel → Validar Config → Ejecutar Script → Publicar
                                  ↑                  ↓
                                  └──── 🟡 🔴 ───────┘
```

---

## Ejecución

### Antes de cada catálogo, verificar en el archivo de configuración:
- Nombre del PDF en `libros/`
- Nombre del Excel en `precios/`
- Nombre del archivo de salida en `salidas/`

### Desde VSC
1. `File > Open Folder > books-label`
2. Abrir terminal integrada
3. Activar entorno virtual y ejecutar:

```bash
source venv_catalogo/bin/activate
python3 scripts/catalogo_base.py --config configs/config_jeans_PV26.json
```

### Desde terminal

```bash
cd ~/books-label
source venv_catalogo/bin/activate
python3 scripts/catalogo_base.py --config configs/config_jeans_PV26.json
```

> Sustituir `config_jeans_PV26.json` por el archivo de configuración del proveedor correspondiente.

---

## Resultado al terminar

Al finalizar cada ejecución el script muestra un resumen en consola:

```
============================================================
✅ PROCESO TERMINADO
📄 Páginas procesadas  : 42
📋 Registros en Excel  : 318
🔢 IDs únicos marcados : 287
🏷️  Etiquetas insertadas: 301
🔍 Fuzzy matches        : 14
📊 Efectividad          : 90.3%
   🟢 VERDE
   → Resultado óptimo. Puedes publicar en WhatsApp Business.
============================================================
```

### Semáforo de efectividad

| Resultado | Acción |
|-----------|--------|
| 🟢 85% o más | Publicar en WhatsApp Business |
| 🟡 65% – 84% | Revisar antes de publicar — ejecutar `diagnostico.py` |
| 🔴 menos de 65% | No publicar — ejecutar `diagnostico.py` y escalar al coach |

La efectividad se calcula como: `IDs únicos marcados / total de registros en Excel × 100`

---

## Configuración por proveedor

Cada proveedor o temporada tiene su propio archivo JSON en `configs/`. El script base nunca se edita directamente. Todos los parámetros ajustables viven en el config:

```json
{
    "pdf_input":   "libros/jeans_PV26.pdf",
    "excel_input": "precios/lista_jeans.xlsx",
    "pdf_output":  "salidas/jeans_PV26_etiquetado.pdf",

    "dpi": 200,
    "psm": 6,
    "contraste": 2.5,
    "nitidez": 2.0,
    "ocr_grayscale": true,
    "ocr_invertir": false,
    "ocr_doble_pasada": false,

    "id_longitud_min": 4,
    "id_longitud_max": 8,

    "fuzzy_activo": true,
    "fuzzy_umbral": 85,

    "etiqueta_font_size": 11,
    "etiqueta_color_rgb": [0.0, 0.0, 1.0],
    "etiqueta_offset_x_pt": 4.0,
    "etiqueta_offset_y_pt": 5.67,

    "logo_activo": false,
    "logo_path": "imagenes/logos/logo_bz.png",
    "logo_x_pt": 20.0,
    "logo_y_pt": 750.0,
    "logo_ancho_pt": 80.0,
    "logo_alto_pt": 40.0,
    "logo_transparencia": 0.85
}
```

### Parámetros clave

| Parámetro | Qué hace | Cuándo ajustar |
|-----------|----------|----------------|
| `dpi` | Resolución del OCR | Si el OCR no detecta bien los IDs |
| `psm` | Modo de lectura de Tesseract | Si el layout del catálogo es inusual |
| `contraste` / `nitidez` | Preprocesado de imagen | Si el PDF es de baja calidad |
| `ocr_grayscale` | Convierte la imagen a escala de grises antes del OCR | Desactivar solo si el OCR performa mejor en color |
| `ocr_invertir` | Invierte los colores de la imagen antes del OCR | Activar si el catálogo tiene texto blanco sobre fondo oscuro en todas las páginas |
| `ocr_doble_pasada` | Ejecuta OCR dos veces: una normal y una invertida, luego fusiona los resultados | Activar en catálogos con IDs en fondo oscuro y fondo claro en la misma página. Duplica el tiempo de proceso. |
| `id_longitud_min/max` | Filtro de longitud de IDs | Si el proveedor usa IDs más largos o cortos |
| `fuzzy_umbral` | Tolerancia a errores de OCR | Bajar si hay muchos IDs sin reconocer |
| `etiqueta_offset_x/y_pt` | Posición del precio respecto al ID | Si los precios aparecen desplazados |
| `logo_activo` | Activa o desactiva el logo en portada | Al activar por primera vez |
| `logo_path` | Ruta al archivo de logo | Debe apuntar a un archivo en `imagenes/logos/` |
| `logo_transparencia` | Opacidad del logo (1.0 = opaco, 0.0 = invisible) | Al insertar logo por primera vez — probar con 0.85 |

> **Logos disponibles:** `imagenes/logos/logo_bz.png` y `imagenes/logos/logo_ocean.png`

> **Archivos de precios:** solo se aceptan archivos `.xlsx`. Si recibes un archivo `.ods` o `.xls`, conviértelo antes de ejecutar el script.

---

## Diagnóstico

Cada ejecución genera un log con timestamp en `diagnosticos/`. El nombre del archivo indica el catálogo y la hora exacta de la corrida, por lo que cada ejecución queda registrada de forma independiente.

Si el semáforo es amarillo o rojo, ejecutar:

```bash
python3 scripts/diagnostico.py
```

Ver `docs/DIAGNOSTICO.md` para interpretar resultados y saber qué escalar al coach.

---

## Instalación del entorno

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

## Métricas clave

| Métrica | Qué significa |
|---------|---------------|
| Efectividad | `IDs únicos marcados / registros en Excel × 100` |
| Etiquetas insertadas | Total de precios colocados en el PDF (puede superar IDs únicos si un ID aparece en varias páginas) |
| IDs únicos marcados | Productos distintos etiquetados al menos una vez |
| Fuzzy matches | IDs recuperados por corrección automática de errores de OCR |

Una efectividad menor al 65% requiere diagnóstico obligatorio antes de cualquier acción.

---

## Notas importantes

- El script base **nunca se edita directamente**. Todos los ajustes van en el archivo de configuración del proveedor.
- Cada proveedor nuevo o temporada nueva puede requerir un config nuevo. Usar como base el de un proveedor similar.
- Siempre probar con las primeras 10 páginas antes de procesar el catálogo completo cuando el proveedor es nuevo.
- Los archivos en `salidas/` son el producto final. Nunca modificar manualmente.
- El log es la fuente de verdad. Si el PDF se ve bien pero la efectividad es baja, hay un problema real.
- Los archivos de precios deben estar en formato `.xlsx`. Si recibes un archivo `.ods` o `.xls`, conviértelo antes de ejecutar el script.
