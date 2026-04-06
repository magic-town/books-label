<img src="../imagenes/asset_repo/cover00.png" alt="Boutique Zepeda — Taller de Etiquetado" width="95%"/>

# ✨ Guía de Etiquetado — Boutique Zepeda

> Cada catálogo que etiquetas representa tiempo liberado y calidad entregada.
> Sigue los pasos en orden — el proceso está diseñado para cuidarse solo.

---

## 🗺️ ¿En qué etapa estoy?

```
FASE 1               FASE 2               FASE 3
Extraer precios  →  Etiquetar       →   Publicar
del proveedor        catálogo            al cliente
```

<img src="../imagenes/asset_repo/cover_modulos.png" alt="Boutique Zepeda — Taller de Etiquetado" width="80%"/>

## Modulo 1 - Fase 1 (🚀 Deploy 06-abril).

El módulo está diseñado para ejecutarse de forma automática, iniciand en la extracción de precios hasta la aplicación de precios de nuestra tienda para cada catálogo. No obstante, se seguirá contemplando un plan de contingencia que incluye la extracción mediante LLMs (como NotebookLM de Google o Claude de Anthropic).

- [Extractor.py](#extractor-py)
- [NotebookLM](#notebook)

Para ambos métodos siempre iniciamos descargando los catálogos de cada proveedor en el directorio 📁 `~/boutique_zepeda/proveedor/`:

+ Price Shoes: 👉 https://www.priceshoes.com/ $\to$ 📥 Download
+ Pakar:  📱 app móvil $\to$ compartir a Whatsapp $\to$ 📥 Download
+ Cklass: Se consiguen por combo con una lista de precios para todos los catálogos.

<img src="../imagenes/asset_repo/download00.png" alt="Boutique Zepeda — Taller de Etiquetado" width="65%"/>

### <a name="extractor-py"></a>Opción I. Extractor.py

- [ ] Validar en patalla 🖥️ que el catálogo y la lista descargados coincidan en `ID`, `páginas`, `precio`.
- [ ] Hacer una copia de `~/boutique_zepeda/proveedor/catalogs` a `~/books-label/fase_1/libros`

```bash
cp ~/boutique_zepeda/proveedor/catalogos ~/books-label/fase_1/libros
cp ~/boutique_zepeda/proveedor/lista_precios ~/books-label/fase_1/lista_cruda
```

<img src="../imagenes/asset_repo/download.png" alt="Boutique Zepeda — Taller de Etiquetado" width="75%"/>

#### Modulo 1 = Extraer precios PDF + aplicar nuestra tabla

- [ ] Ya con el la lista descarga y copiada en `~/books-labels/fase_1/lista_cruda`:


```
Abrimos **VSC** > File > Open Folder > books-label
```

- [ ] Activar el virtual environment `venv`. Para mostraur u oculatar la terminal puedes usar: `Ctrl + J`

```bash
source venv/venv_catalogo/bin/activate
```
El proyeecto se ha vuelto algo robusto, por lo que te sugiero que uses un modulo a la vez, de momento nos encontramos en el modulo_1 - fase_1




### <a name="notebook"></a>Opción II. NotebookLM
{text}

- [ ] Validar en patalla 🖥️ que el catálogo y la lista descargados coincidan en_ID_`, _páginas_.
- [ ] Inserta tu lista cruda de precios en alguno de los 2 LLM que han dado mejor reusltado: `Claude` o `NotebookLM (Google)`
- [ ] Usa uno o varios de los siguietnes prompts:

#### 🛍️ Prompt para Price Shoes

**Paso 1 — Extracción inicial**

```
Del fichero <nombre_archivo> extrae las siguientes columnas de todas las páginas del documento:

{
  "columna_1":  "Pag",
  "columna_4":  "ID",
  "columna_12": "Sug_credito"
}

Preséntala en forma de tabla, lista para copiar y pegar en LibreOffice Calc.
IMPORTANTE: el tipo de datos debe ser número y el formato debe ser una tabla.
```

---

**Paso 2 — Si se equivoca de columna**

```
Del fichero <nombre_archivo> extrae las siguientes columnas de todas las páginas del documento:

{
  "columna_1":  "Pag",
  "columna_4":  "ID",
  "columna_13": "Sug_credito"
}


La columa "Sug_credito" es la siguiete de la que me estas dando en tu último output.
Preséntala en forma de tabla, lista para copiar y pegar en LibreOffice Calc.
IMPORTANTE: el tipo de datos debe ser número y el formato debe ser una tabla.
```

---

**Paso 3 — Si vuelve a equivocarse (este es común para NotebookLM)**

```
La tabla que generaste es correcta en:

{
  "columna_1": "Pag",
  "columna_4": "ID"
}

Es incorrecta la última columna. Corrígela por los datos correctos: "columna_X": "Sug_credito", es la siguiete columna de la que me estas dando en tus últimos outputs.
IMPORTANTE: los datos de toda la tabla deben ser de tipo número.
```

#### 🟣 Extacción de Pakar

```
Del fichero <nombre_archivo> extrae las siguientes columnas de todas las páginas del documento:

{
  "columna_1":  "PÁG.",
  "columna_2":  "CÓDIGO",
  "columna_11": "2 PAGOS"
}

IMPORTANTE: El tipo de datos para "CÓDIGO" debe ser texto, es decir, los valores tienen este formato "xxx-xxx". Para "2 PAGO" el formato debe ser número ya que debo aplicarle fórmula en Calc. Tu output tiene que ser una tabla lista para copiar y pegar.
```

- [ ] Valida que la tabla es la que necesitas Vs tu tabla cruda.
- [ ] Copia tu tabla extraida en `~/books-label/fase_2/precios/precios_tabla.ods`
- [ ] Aplica las transformaciones `REDONDEAR`, `precios_venta`, `LEN`
- [ ] Copia las columnas `ID`, `precio_venta` en una tabla al costado de la transformada con `pegado especial`

---


## 🏷️ FASE 2 — Etiquetar el catálogo

> **Objetivo:** ejecutar el script y obtener semáforo verde en el catálogo completo.

### Antes de empezar

- [ ] Verificar que tienes el catálogo PDF en `fase_2/libros/`
- [ ] Verificar que tienes el Excel validado en `fase_2/precios/`
- [ ] Ejecutar sync.
  Desde **Tilix** o la terminal integrada de VSC:
  ```bash
  cd ~/books-label && ./sync.sh
  ```
- [ ] Activar el entorno:
  ```bash
  source venv_catalogo/bin/activate
  ```

---

### Preparar la configuración

- [ ] Crear una copia de `fase_2/config/config_base.json`. Desde **Dolphin**: `Ctrl+C` → `Ctrl+V`.
- [ ] Renombrar la copia con `F12`:
  `config_<proveedor>_<temporada>.json`

- [ ] Abrir el configurador haciendo doble clic sobre:
  ```
  fase_2/config/configurador.html
  ```

  Elige el **proveedor** primero — determina el patrón de búsqueda del OCR.

- [ ] Completar los tres campos I/O (inputs / outputs).

<img src="../imagenes/asset_repo/configurador.png" alt="Boutique Zepeda — Taller de Etiquetado" width="85%"/>

- [ ] Copiar el JSON del configurador y pegarlo en tu archivo de configuración en VSC.

---

### Etapa 1 de pruebas — Posicionamiento visual

> **Objetivo:** que la etiqueta de precio aparezca junto al ID del producto.

- [ ] Activar modo prueba con **20 páginas**.
- [ ] Mantener las carátulas en `false` durante esta etapa.
- [ ] Ejecutar el script:
  ```bash
  python3 fase_2/catalogo_base.py --config fase_2/config/<nombre_config>.json
  ```
- [ ] Abrir el PDF en `fase_2/salidas/` y verificar visualmente.
- [ ] Ajustar posición en el configurador si es necesario. Copiar JSON y pegar.

---

### Etapa 2 de pruebas — Optimización de lectura

> **Objetivo:** encontrar la combinación de parámetros que detecta más IDs.

- [ ] Mantener modo prueba activo. Usar entre **30 y 40 páginas**.
- [ ] Desactivar doble pasada durante esta etapa.
- [ ] Probar entre 4 y 8 combinaciones. Tabla de referencia:

| # | DPI | PSM | Doble pasada | Invertir | Cuándo usarla |
|---|:---:|:---:|:------------:|:--------:|---------------|
| 1 | 200 | 6 | ❌ | ❌ | Punto de partida — catálogo limpio |
| 2 | 200 | 11 | ❌ | ❌ | IDs dispersos o fotos de página completa |
| 3 | 200 | 4 | ❌ | ❌ | Catálogo en columnas de texto |
| 4 | 250 | 6 | ❌ | ❌ | PDF de baja resolución |
| 5 | 250 | 11 | ❌ | ❌ | IDs dispersos con más resolución |
| 6 | 300 | 11 | ❌ | ❌ | Máxima resolución |
| 7 | 250 | 11 | ❌ | ✅ | IDs en texto blanco sobre fondo oscuro |

- [ ] El dato clave de cada corrida es **Etiquetas** — no el porcentaje.
- [ ] Registrar los resultados. Los logs se guardan en `fase_2/diagnosticos/`.

---

### Etiquetado final

> **Objetivo:** procesar el catálogo completo con la configuración ganadora.

- [ ] Configurar las carátulas con sus posiciones definitivas:

```json
"presentaciones": [
    {"path": "../imagenes/logos/portada_01.pdf", "posicion": 2},
    {"path": "../imagenes/logos/portada_02.pdf", "posicion": 25},
    {"path": "../imagenes/logos/portada_03.pdf", "posicion": 150},
    {"path": "../imagenes/logos/portada_04.pdf", "posicion": false},
    {"path": "../imagenes/logos/portada_05.pdf", "posicion": -1}
]
```

> Posición `2` = segunda página · `-1` = última página · `false` = desactivada

- [ ] Desactivar modo prueba y activar doble pasada:
```json
"paginas_prueba": false,
"ocr_doble_pasada": true
```

- [ ] Copiar JSON del configurador y pegar en el archivo de configuración.
- [ ] Ejecutar el script:
  ```bash
  python3 fase_2/catalogo_base.py --config fase_2/config/<nombre_config>.json
  ```

---

### Leer el semáforo

| Resultado | Acción |
|-----------|--------|
| 🟢 **VERDE** — 85% o más | Revisar el PDF visualmente y continuar a Fase 3 |
| 🟡 **AMARILLO** — 65% a 84% | Revisar el PDF y evaluar si se requiere un ajuste |
| 🔴 **ROJO** — menos de 65% | No publicar — ver sección siguiente |

- [ ] Ejecutar el diagnóstico al terminar:
  ```bash
  python3 fase_2/diagnostico.py
  ```
  Copiar el output y compartirlo con Gabriel si el semáforo no es verde.

---

### Si el semáforo no es verde

**Camino A — Ajuste autónomo**
- [ ] Abrir el configurador, ajustar parámetros, copiar JSON y ejecutar de nuevo.

**Camino B — Diagnóstico con Claude**
- [ ] Ejecutar `python3 fase_2/diagnostico.py`
- [ ] Pegar el output en Claude: *"Este es el diagnóstico de mi script, ¿qué parámetros recomiendas?"*

**Camino C — Escalar a Gabriel**
- [ ] Aplica cuando A y B no superan el 70%.
- [ ] Compartir el PDF, el log de consola y las combinaciones ya probadas.

> Tu responsabilidad concluye al ejecutar el diagnóstico y completar las iteraciones.
> Si después de ese proceso la tasa sigue por debajo del 70%, se escala.

---

## 📲 FASE 3 — Publicar al cliente

> **Estado:** canal actual es Dropbox + WhatsApp Business.
> Se evalúa migrar a GitHub Pages o portal web para visualización directa.

### Mover el archivo

- [ ] Copiar el PDF final desde `fase_2/salidas/` al directorio de la marca:
  ```
  ~/boutique_zepeda/<marca>/catalogos_etiquetados/
  ```

### Subir a Dropbox

- [ ] Subir a 🗳️ Dropbox: `Inicio > <marca> > catalogos`
- [ ] Copiar el enlace generado.
- [ ] Pegar en VSC en el archivo `~/books-label/prompts/notas_operativas.md`
- [ ] Cambiar el último carácter del enlace: `0` → `1`

### Comprimir el enlace

- [ ] Entrar a [bitly.com](https://bitly.com) → `Create new` → pegar el enlace modificado.

> 🥺 Bitly tiene límite mensual. Contamos con 3 cuentas — si se agotan, usar el enlace largo directamente.

- [ ] Copiar el enlace corto y pegarlo en `notas_operativas.md`.

### Crear el artículo en WhatsApp Business

- [ ] Capturar 10 recortes del catálogo con **Flameshot**. Guardar en:
  `~/boutique_zepeda/<marca>/carrusel` con nombres `1.png, 2.png, ..., 10.png`

- [ ] Desde **WhatsApp Business Desktop**: `Herramientas > Catálogo > Añadir artículo nuevo`
- [ ] Cargar las 10 capturas.
- [ ] Completar los campos:
  - **Nombre:** nombre del catálogo o proveedor
  - **Descripción:**
    ```
    Da clic en el enlace 👇 para descargar el catálogo, espera o confirma la descarga. ✅️ Revisa tu carpeta de descargas.
    ```
  - **Enlace:** pegar el link de Bitly → **Guardar**

> **Nota — WhatsApp Business en móvil**
>
> Si la aplicación de escritorio falla, usar el dispositivo Android. Las imágenes están en:
> ```
> Almacenamiento interno > Android > media > com.whatsapp > WhatsApp > Media > WhatsApp Images > Sent
> ```

---

## 🆘 Árbol de decisión ante resultados adversos

```
¿La extracción o el semáforo no son verdes?
              ↓
  Revisar el output en consola — ¿el error es claro?
       ↙                              ↘
      Sí                               No
      ↓                                 ↓
  Ajustar config               Ejecutar diagnostico.py
  y volver a intentar          y compartir con Claude
```

> El proceso está diseñado para acompañarte en cada paso.
> Cualquier duda es válida — consultar siempre es la decisión correcta.

---

## 🔄 Sincronización con Gabriel

Siempre ejecutar sync **antes de empezar** y **al terminar** el trabajo del día.
Desde **Tilix** o la terminal integrada de VSC:

```bash
cd ~/books-label && ./sync.sh
```

El script protege automáticamente tu versión de `tabla_precios.ods` — tu archivo siempre tiene prioridad.

---

*Última revisión: 03-2026 · books-label*
