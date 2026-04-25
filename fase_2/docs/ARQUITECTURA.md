# ARQUITECTURA — `catalogo_base.py`
**Boutique Zepeda · books-label**

---

## El problema que resuelve

Los catálogos de proveedores llegan como PDFs de imágenes —páginas escaneadas o generadas sin texto seleccionable—. Cada producto tiene un código de referencia (ID) impreso junto a la foto. La tarea es leer esos IDs, buscar su precio en un Excel, y escribir el precio encima del PDF en una posión cercana y legible al código/id.

El resultado es un PDF listo para publicar con los precios de Boutique Zepeda superpuestos, sin alterar el diseño original del proveedor.

---

## Visión general del flujo

```
PDF de proveedor  +  Excel de precios
        │
        ▼
  Aplanar AcroForm (si aplica)
        │
        ▼
  Por cada página:
    ├── Convertir página a imagen  (pdf2image)
    ├── Preprocesar imagen         (Pillow)
    ├── OCR en 3 orientaciones     (Tesseract via pytesseract)
    ├── [Doble pasada opcional]    (imagen invertida)
    ├── Fusionar tokens
    ├── Reconstruir tokens rotos
    ├── Por cada token detectado:
    │     ├── Extraer candidato a ID  (según proveedor)
    │     └── Buscar precio           (exacto → recorte → fuzzy)
    └── Dibujar precio en coordenadas  (reportlab)
        │
        ▼
  Ensamblar PDF final              (PyPDF2)
        │
        ▼
  Normalizar con Ghostscript
        │
        ▼
  PDF etiquetado  +  Log  +  CSV fuzzy (si aplica)
```

---

## OCR y Tesseract — qué son y cómo se usan

OCR (Optical Character Recognition) es el proceso de extraer texto a partir de una imagen. **Tesseract** es el motor OCR concreto que usa este proyecto —un programa externo instalado en el sistema (`tesseract-ocr`)—. `pytesseract` es el puente Python que le envía imágenes y recibe los resultados.

Tesseract no devuelve solo texto: devuelve un diccionario con el texto de cada token y sus coordenadas en píxeles (`left`, `top`). Esas coordenadas son las que luego se convierten a puntos PDF para saber exactamente dónde pintar el precio.

`pdfplumber` no se usa en este proyecto. Esa librería extrae texto directamente de la estructura interna del PDF, lo que solo funciona cuando el PDF tiene texto embebido. Los catálogos de proveedores son imágenes, así que el único camino es convertir cada página a imagen y aplicar OCR.

---

## Estructura de código — OOP

El proyecto tiene una sola clase principal: `EtiquetadorCatalogo`. Toda la lógica vive dentro de ella.

**Constructor `__init__`**
Lee el archivo de configuración JSON, inicializa todos los parámetros (rutas, DPI, umbrales, colores, proveedor), precarga el Excel en memoria y verifica que Tesseract esté instalado. Al terminar el constructor el objeto está completamente listo.

**Método público `marcar()`**
Es la única entrada externa. Orquesta el proceso completo página por página y guarda el PDF final.

**Métodos privados (`_`)**
Toda la infraestructura interna usa el prefijo `_` por convención: no forman parte de la API pública y no deben llamarse desde fuera. Cada uno tiene una responsabilidad única y acotada.

No hay herencia ni jerarquía de clases. Para un script de procesamiento por lotes es suficiente y apropiado.

---

## Detección de IDs por proveedor

El formato del código de referencia varía según el proveedor. Tres métodos trabajan en cadena y encapsulan esa variación:

### `_build_id_pattern()` — se ejecuta una vez al inicializar

Construye el regex y la bandera `usa_guion` según el valor de `id_proveedor` en el config.

| Proveedor | Regex | Descripción |
|---|---|---|
| `PS` (Price Shoes) | `\d{min,max}` | Solo dígitos. Longitud configurable. Tolera prefijos `ID`, `id`, `1D`. |
| `Pakar` | `\d{3}-\d{3}` | Tres dígitos, guion, tres dígitos. Ej: `856-954` |
| `Cklass` | `\d{3}-\d{2}` | Tres dígitos, guion, dos dígitos. Ej: `938-47` |
| `Otro` | `[A-Za-z0-9]{min,max}` | Alfanumérico, longitud configurable. |

Pakar y Cklass activan `usa_guion=True`, lo que significa que el patrón se aplica con `.search()` directo sobre el texto OCR. PS y Otro usan `usa_guion=False`: primero se limpia el token (prefijos, caracteres no numéricos) y luego se valida por longitud.

### `_extraer_id_candidato(texto)` — se ejecuta por cada token OCR

Aplica la lógica de extracción sobre un token individual. Para Pakar/Cklass hace `.search()` directo. Para PS normaliza el prefijo con `re.sub(r"^[I1][Dd]\D*", "")` —que cubre la confusión OCR entre `I` y `1`— y luego extrae solo dígitos. Para Otro extrae solo caracteres alfanuméricos.

### `_reconstruir_tokens(data)` — se ejecuta por página, antes de la extracción

Tesseract frecuentemente parte un código en dos tokens separados. Este método los fusiona. Aquí sí hay lógica diferenciada por proveedor:

- **PS / Otro:** busca tokens que sean solo `ID`/`id`/`1D` y los une con el número más cercano dentro de 120px. Resultado: `"ID" + "1234567"` → `"ID1234567"`.
- **Pakar / Cklass:** busca el fragmento izquierdo (`NNN`) y el derecho (`NNN` o `NN`) dentro de 150px, absorbe el guion si aparece como token separado, y arma el código completo. Verifica con el regex del proveedor antes de aceptar la fusión para evitar uniones falsas.

---

## Estrategias de recuperación de IDs

A medida que se procesaron catálogos reales se identificaron distintos tipos de fallo. Se implementaron capas de recuperación apiladas en orden de confianza, la mayoría aplicadas globalmente a todos los proveedores.

### 1. Preprocesado de imagen — global

Antes de pasar la imagen a Tesseract se aplica contraste, nitidez y filtro de mediana (Pillow). Los parámetros son configurables por config (`contraste`, `nitidez`). También hay una opción `ocr_invertir` para catálogos con fondo oscuro y texto claro.

### 2. Lectura en tres orientaciones — global

`_ocr_con_rotaciones()` ejecuta Tesseract tres veces sobre cada página: a 0°, 90° CCW y 270° CCW. Las coordenadas de las pasadas rotadas se mapean de vuelta al espacio original con fórmulas geométricas antes de fusionarlas. Cubre texto impreso verticalmente —el caso motivador fueron etiquetas Pakar con el código en orientación vertical—, pero el método se aplica a todos los proveedores sin condicional.

### 3. Doble pasada OCR — global, opcional

Activada con `ocr_doble_pasada: true` en el config. Cada página se procesa dos veces: una pasada normal y una pasada con imagen invertida (preprocesado distinto: solo contraste fuerte + inversión, sin mediana ni nitidez que destruirían bordes de texto claro). Los tokens de ambas pasadas se fusionan en `_fusionar_tokens()` con tolerancia de 20px para evitar duplicados. Resuelve catálogos con fondo mixto donde hay IDs negros sobre blanco e IDs blancos sobre fondo oscuro en la misma página.

### 4. Match exacto — global

Primera estrategia en `_buscar_id()`. Busca el ID detectado directamente en el diccionario de precios. Si existe, retorna precio inmediatamente.

### 5. Ventana deslizante (recorte) — global

Segunda estrategia. Cuando el OCR fusiona texto adyacente al ID —por ejemplo lee `"1234567A"` cuando el código real es `"1234567"`— prueba todas las subcadenas de largo `id_len_max` hacia abajo hasta `id_len_min`. Solo acepta si la subcadena existe exactamente en el Excel, lo que garantiza que no hay riesgo de asignar un precio incorrecto.

### 6. Fuzzy matching — global, opcional

Tercera y última estrategia. Compara el token detectado contra todos los IDs del Excel usando `fuzz.ratio` de la librería `rapidfuzz`. Si la similitud supera `fuzzy_umbral` (default 85%), acepta el match. Genera un archivo `_fuzzy.csv` en `diagnosticos/` con cada ID recuperado por esta vía para revisión manual antes de publicar.

### Resumen de alcance por proveedor

| Método | PS | Pakar | Cklass | Otro |
|---|:---:|:---:|:---:|:---:|
| Preprocesado imagen | ✅ | ✅ | ✅ | ✅ |
| Lectura vertical (3 orientaciones) | ✅ | ✅ | ✅ | ✅ |
| Doble pasada OCR | ✅ | ✅ | ✅ | ✅ |
| Match exacto | ✅ | ✅ | ✅ | ✅ |
| Ventana deslizante | ✅ | ✅ | ✅ | ✅ |
| Fuzzy matching | ✅ | ✅ | ✅ | ✅ |
| Reconstrucción de tokens | prefijo ID+num | guion NNN-NNN | guion NNN-NN | prefijo ID+num |

---

## Ensamblado del PDF final

Por cada página se genera una capa transparente con ReportLab que contiene solo los precios en sus coordenadas. Esa capa se fusiona (`merge_page`) sobre la página original del PDF usando PyPDF2. El PDF original nunca se modifica directamente.

Al terminar todas las páginas, Ghostscript normaliza el PDF resultante a PDF 1.4 estándar para garantizar compatibilidad con lectores básicos, dispositivos Android e iOS. Si Ghostscript no está disponible, el proceso no falla —solo avisa y conserva el PDF tal como quedó de PyPDF2.

---

## Configuración por archivo JSON

Todos los parámetros del proceso se definen en un archivo JSON externo. El script nunca tiene valores de negocio hardcodeados. Parámetros clave:

| Parámetro | Descripción |
|---|---|
| `id_proveedor` | `PS`, `Pakar`, `Cklass`, `Otro` |
| `dpi` | Resolución de renderizado del PDF (afecta calidad OCR y velocidad) |
| `contraste`, `nitidez` | Preprocesado de imagen |
| `psm` | Page Segmentation Mode de Tesseract |
| `id_longitud_min/max` | Rango de longitud de ID para PS y Otro |
| `fuzzy_activo`, `fuzzy_umbral` | Control del fuzzy matching |
| `ocr_doble_pasada` | Activa la segunda pasada con imagen invertida |
| `paginas_prueba` | Procesa solo N páginas para validación rápida |
| `presentaciones` | Lista de carátulas PDF a insertar en posiciones absolutas |

---

## Dependencias del sistema

| Herramienta | Rol |
|---|---|
| `tesseract-ocr` | Motor OCR — lee texto de imágenes |
| `poppler-utils` | Conversión PDF → imagen (requerido por pdf2image) |
| `ghostscript` | Aplanado de AcroForm + normalización PDF final |

## Dependencias Python

| Librería | Rol |
|---|---|
| `pdf2image` | Convierte páginas PDF a imágenes PIL |
| `pytesseract` | Puente Python hacia Tesseract |
| `Pillow` | Preprocesado de imágenes |
| `PyPDF2` | Lectura y escritura de estructura PDF |
| `reportlab` | Dibuja las etiquetas de precio como capa PDF |
| `rapidfuzz` | Fuzzy matching de IDs |
| `pandas` / `openpyxl` | Carga del Excel de precios |
