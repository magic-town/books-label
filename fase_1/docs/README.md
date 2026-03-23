# Fase 1 — Extracción de campos

**books-label · Boutique Zepeda**

---

## Qué hace este módulo

Extrae automáticamente tres campos de las listas de precios PDF que envían los proveedores — página, ID de producto y precio base — y los entrega como un Excel limpio y estructurado.

Ese Excel es el input de Fase 2. También es el primer activo de datos del negocio.

---

## Por qué importa

Las listas de precios del proveedor llegan en PDF. Son documentos diseñados para imprimirse, no para trabajar con ellos. Extraer los datos manualmente es lento, propenso a errores y no escala.

Pero hay algo más importante que la velocidad: **un dato extraído correctamente vale mucho más que un PDF bien impreso**.

El precio de cada artículo, vinculado a su ID y a la página donde aparece, es la unidad mínima de información estructurada del negocio. Con eso se pueden construir cosas que hoy no existen: historial de precios por temporada, análisis de márgenes por proveedor, catálogos personalizados por segmento de cliente, campañas de marketing basadas en datos reales. Nada de eso es posible sin esta extracción — o toma semanas hacerla a mano.

Este módulo convierte un PDF opaco en una tabla de datos limpia. Eso es el punto de partida de cualquier decisión informada.

---

## Proveedores soportados

| Proveedor | Tipo de PDF | Estrategia |
|-----------|-------------|------------|
| **Price Shoes** | Encoding propietario — texto desplazado | Decodificador + extracción espacial por coordenadas |
| **Pakar** | Texto limpio — estructura tabular | Extracción directa por encabezado de columna |
| **Cklass** | Texto limpio — precios con `$` y decimales | Extracción directa con normalización de precio |
| **Otro** | Configurable | Extracción directa — offset configurable |

---

## Archivos del módulo

```
fase_1/
├── extractor.py              ← script principal
├── lista_cruda/              ← PDFs de entrada (listas del proveedor)
├── salida/                   ← Excels generados
├── diagnosticos/             ← logs de cada corrida
├── archivo/                  ← corridas anteriores
└── config/
    ├── config_base_extractor.json    ← plantilla de configuración
    └── panel_extraer_campos.html     ← panel visual para generar configs
```

---

## Cómo usar

**1. Abrir el panel visual**
```
fase_1/config/panel_extraer_campos.html
```
Seleccionar el proveedor, completar los nombres de archivo, copiar el JSON.

**2. Pegar el JSON en una copia de la plantilla**
```
fase_1/config/config_ps_pv26.json
```

**3. Ejecutar**
```bash
python3 fase_1/extractor.py --config fase_1/config/config_ps_pv26.json
```

**4. Revisar el Excel en `fase_1/salida/`**
Columnas: `pag` · `id` · `precio_base` · `len`

---

## Formato de salida

El Excel generado tiene cuatro columnas:

| Columna | Contenido | Ejemplo |
|---------|-----------|---------|
| `pag` | Página del catálogo donde aparece el artículo | `4` |
| `id` | ID o código del producto | `142-530` |
| `precio_base` | Precio extraído, limpio y sin símbolo | `1399` |
| `len` | Longitud del ID — para auditoría | `7` |

El precio siempre se normaliza a entero sin decimales ni símbolo de moneda, independientemente del formato que use el proveedor.

---

## Semáforo de extracción

| Indicador | Registros | Acción |
|-----------|-----------|--------|
| 🟢 Exitosa | ≥ 100 | Validar y pasar a Fase 2 |
| 🟡 Parcial | 20 – 99 | Revisar columnas en el config |
| 🔴 Fallida | < 20 | Revisar PDF y configuración |

---

## Dependencias

Solo `pdfplumber`, `pandas` y `openpyxl` — ya incluidas en `requirements.txt`.
No requiere OCR ni librerías externas adicionales.

---

## Pendiente

- [ ] Validación automática del Excel contra umbrales configurables
- [ ] Pipeline Fase 1 → Fase 2 sin paso manual cuando la extracción esté validada en producción

---

*books-label · Fase 1 · 03-2026*
