<img src="../imagenes/asset_repo/cover00.png" alt="Boutique Zepeda — Taller de Etiquetado" width="100%"/>

# ✨ Guía de Etiquetado — Boutique Zepeda

> Cada catálogo que etiquetas representa tiempo liberado y calidad entregada.
> Sigue los pasos en orden — el proceso está diseñado para cuidarse solo.

---

## 🗺️ ¿En qué etapa estoy?

```
FASE 1          FASE 2          FASE 3
Preparar   →   Etiquetar   →   Publicar
precios         catálogo        en WA
```

---

## 📋 FASE 1 — Preparar los precios

> **Objetivo:** contar con el archivo Excel validado antes de ejecutar cualquier script.

### Descargar y verificar

- [ ] Descargar el catálogo PDF y la lista de precios del proveedor.
- [ ] Validar visualmente que ambos archivos correspondan al mismo proveedor y temporada: número de páginas, IDs y precios sugeridos deben coincidir.
- [ ] Mover los archivos a sus directorios:
  - Catálogo PDF → `~/boutique_zepeda/<proveedor>/catalogos`
  - Lista de precios → `~/boutique_zepeda/<proveedor>/lista_precios`

### Extracción de precios con asistente de IA *(solución vigente — se evalúa automatización con script)*

- [ ] Abrir el prompt de extracción: 👉 [extraer_columnas_listas.md](../prompts/extraer_columnas_listas.md)
- [ ] Seleccionar un modelo de lenguaje — NotebookLM, Claude, o ambos en paralelo — y adjuntar la lista cruda del proveedor.
- [ ] Ejecutar el prompt y obtener la tabla extraída.
- [ ] Validar el resultado: comparar la **lista cruda del proveedor** contra la **tabla extraída por el modelo**, verificando que no haya registros faltantes, precios en cero ni IDs con formato incorrecto.

### Construcción de la tabla de precios en LibreOffice Calc

> Se trabaja con LibreOffice Calc. Algunas fórmulas y atajos dependen de extensiones instaladas — si algo no responde como se describe, verifica que estén activas.

- [ ] Abrir `~/books-label/precios/tabla_precios.ods`.
- [ ] Agregar una hoja nueva y renombrarla como `<proveedor_categoria>`.
- [ ] Pegar la tabla extraída en formato numérico.
- [ ] Verificar la columna de redondeo — si no existe, agregarla:
  ```
  =ROUND(C2, -1)
  ```
- [ ] Agregar la columna `precio_venta` con fórmula VLOOKUP *(consultar hojas anteriores como referencia)*.
- [ ] Agregar la columna de longitud `len`:
  ```
  =LEN(A2)
  ```
- [ ] Completar la tabla en su totalidad.

### 🔎 Validación — paso obligatorio

- [ ] Fijar encabezados: `Ver > Fijar filas y columnas > Fijar primera fila`
- [ ] Activar filtros: `Datos > AutoFiltro` o `Ctrl+Shift+L`
- [ ] Filtrar por la columna `len` y comparar los largos de ID contra el catálogo del proveedor.
- [ ] Confirmar que no existan IDs con longitud incorrecta ni precios en cero.

### ⚠️ Generación del archivo final — paso crítico

- [ ] Retirar todos los filtros activos antes de copiar.
- [ ] Copiar la columna `ID` y pegarla de forma normal.
- [ ] Copiar la columna `precio_venta` y pegarla usando **Pegado especial > Solo números** (clic derecho).
- [ ] La hoja debe contener dos tablas claramente diferenciadas:
  - Tabla completa con todos los campos de trabajo.
  - Tabla simplificada con únicamente `ID` y `precio_venta`.
- [ ] Copiar la tabla simplificada a un archivo nuevo:
  `Archivo > Nueva hoja de cálculo > Pegar`
  *(En inglés: `File > New spreadsheet > Paste`)*
- [ ] Guardar el archivo como:
  ```
  ~/books-label/precios/<lista_catalogo.xlsx>
  ```
  Si el sistema solicita confirmar el formato Excel, seleccionar **Aceptar**.

---

## 🏷️ FASE 2 — Etiquetar el catálogo

> **Objetivo:** ejecutar el script y obtener semáforo verde en el catálogo completo.

### Preparar la configuración

- [ ] Crear una copia de `configs/config_base.json`. Desde **VSC** o **Dolphin**: seleccionar el archivo, `Ctrl+C` seguido de `Ctrl+V` — el sistema genera la copia automáticamente.
- [ ] Renombrar la copia con `F12` siguiendo la convención: `config_<proveedor>_<temporada>.json`
  — Ejemplo: `config_importados_26.json`
- [ ] Abrir el configurador visual por cualquiera de estas vías:

  - Desde terminal:
    ```bash
    source venv_catalogo/bin/activate
    ```
    ```bash
    python3 abrir_configurador.py
    ```
  - Desde Dolphin: doble clic sobre `configurador.html`.
  - Si ya está abierto en el navegador, no es necesario volver a lanzarlo.

- [ ] Actualizar los tres campos de archivos en el configurador, o editarlos directamente en el JSON desde VSC:

<img src="../imagenes/asset_repo/configurador.png" alt="Boutique Zepeda — Taller de Etiquetado" width="85%"/>

---

### Etapa 1 de pruebas — Posicionamiento visual

> **Objetivo:** definir la posición correcta de la etiqueta de precio y del logo antes de iterar parámetros de lectura.

- [ ] Activar el modo prueba con un valor de **20 páginas** para agilizar el ciclo de validación.
- [ ] Mantener las páginas insertadas (carátulas) en `false` durante esta etapa — no afectan el resultado de las etiquetas y pueden ajustarse al final.
- [ ] Ejecutar el script y abrir el PDF generado en `salidas/`.
- [ ] Validar visualmente que la etiqueta de precio y el logo aparezcan en la posición esperada:
  - ¿El precio se ubica junto al ID del producto?
  - ¿El logo aparece en el cuadrante correcto de la portada?
- [ ] Ajustar los controles de posición en el configurador hasta obtener el resultado deseado. Copiar el JSON y pegarlo en el archivo de configuración.

---

### Etapa 2 de pruebas — Optimización de parámetros de lectura

> **Objetivo:** identificar la combinación de parámetros que maximiza el número de etiquetas insertadas.

- [ ] Mantener el modo prueba activo. Usar entre **30 y 40 páginas** — esta muestra es suficiente para evaluar el comportamiento del catálogo sin extender el tiempo de cada corrida.
- [ ] Desactivar la doble pasada (`ocr_doble_pasada: false`) durante esta etapa. La doble pasada se reserva para la corrida final.
- [ ] Ejecutar entre **4 y 8 combinaciones** de parámetros. La siguiente tabla presenta las combinaciones estándar de referencia:

| # | 📸 DPI | 🔍 PSM | 🔄 Doble pasada | 🔃 Invertir | Cuándo usarla |
|---|:------:|:------:|:--------------:|:-----------:|---------------|
| 1 | 200 | 6 | ❌ | ❌ | Punto de partida — catálogo limpio, texto negro sobre blanco |
| 2 | 200 | 11 | ❌ | ❌ | IDs dispersos o con fotos de página completa |
| 3 | 200 | 4 | ❌ | ❌ | Catálogo organizado en columnas de texto bien definidas |
| 4 | 200 | 6 | ❌ | ❌ | Repetir combinación 1 con nitidez o contraste ajustados |
| 5 | 250 | 6 | ❌ | ❌ | PDF de baja resolución o IDs pequeños |
| 6 | 250 | 11 | ❌ | ❌ | IDs dispersos con mayor resolución |
| 7 | 300 | 11 | ❌ | ❌ | Máxima resolución — catálogos complejos sin mejora previa |
| 8 | 250 | 11 | ❌ | ✅ | IDs en texto blanco sobre fondo oscuro en todo el catálogo |

- [ ] El dato crítico de cada corrida es **Etiquetas** — no la tasa porcentual, que es relativa al Excel completo. Con el mismo número de páginas de prueba, la combinación que produce el mayor número de etiquetas es la ganadora.

<img src="../imagenes/asset_repo/modo_prueba.png" alt="Boutique Zepeda — Taller de Etiquetado" width="100"/>

- [ ] Registrar los resultados de cada corrida para comparar. Los outputs se conservan en `diagnosticos/` con nombre y timestamp.

<img src="../imagenes/asset_repo/copy_json.png" alt="Boutique Zepeda — Taller de Etiquetado" width="65%"/>

---

### Etiquetado final

> **Objetivo:** procesar el catálogo completo con la configuración ganadora y las páginas institucionales insertadas.

- [ ] Seleccionar la combinación de parámetros con mayor número de etiquetas de la etapa anterior.
- [ ] Configurar las páginas insertadas con sus posiciones definitivas:

```json
"presentaciones": [
    {"path": "imagenes/logos/portada_01.pdf", "posicion": 2},
    {"path": "imagenes/logos/portada_02.pdf", "posicion": 25},
    {"path": "imagenes/logos/portada_03.pdf", "posicion": 150},
    {"path": "imagenes/logos/portada_04.pdf", "posicion": false},
    {"path": "imagenes/logos/portada_05.pdf", "posicion": -1}
]
```

> Las posiciones `2` y `-1` son fijas — corresponden a la segunda y última página del PDF final. Las posiciones intermedias pueden ajustarse libremente; `false` desactiva una carátula sin eliminarla del archivo.

- [ ] Activar la doble pasada y desactivar el modo prueba:
  ```json
  "paginas_prueba": false,
  "ocr_doble_pasada": true
  ```
- [ ] Copiar el JSON generado por el configurador y pegarlo en el archivo de configuración.
- [ ] Ejecutar el script:
  ```bash
  python3 scripts/catalogo_base.py --config configs/<nombre_config>.json
  ```

### Leer el semáforo

Al concluir el proceso, el sistema mostrará el resultado en consola:

| Resultado | Acción |
|-----------|--------|
| 🟢 **VERDE** — 85% o más | Revisar el PDF visualmente y continuar a Fase 3 |
| 🟡 **AMARILLO** — 65% a 84% | Revisar el PDF y evaluar si se requiere un ajuste adicional |
| 🔴 **ROJO** — menos de 65% | No publicar — consultar la sección siguiente |

- [ ] Independientemente del semáforo, ejecutar el diagnóstico al finalizar el etiquetado completo:
  ```bash
  python3 scripts/diagnostico.py
  ```
  Copiar el output y compartirlo con el colaborador del proyecto para obtener el visto bueno final antes de publicar. Este paso no es bloqueante, pero es parte del proceso de calidad.

### Si el semáforo no es verde

Seleccionar el camino según lo que se observa en el PDF:

**Camino A — Ajuste autónomo de parámetros**
- [ ] Abrir el configurador, revisar los sliders, ajustar la combinación de parámetros y copiar el JSON actualizado al archivo de configuración.
- [ ] Ejecutar nuevamente el script y comparar el resultado.

**Camino B — Diagnóstico automático con soporte de Claude**
- [ ] Ejecutar el diagnóstico:
  ```bash
  python3 scripts/diagnostico.py
  ```
- [ ] Copiar el output completo y pegarlo en Claude con la consulta: *"Este es el diagnóstico de mi script de etiquetado, ¿qué parámetros recomiendas ajustar?"*

**Camino C — Escalamiento al colaborador del proyecto**
- [ ] Este camino aplica cuando los caminos A y B no logran superar el 70% de efectividad.
- [ ] Capturar el PDF con el problema y el output de consola.
- [ ] Compartir con el colaborador describiendo el contexto: tipo de catálogo, combinaciones ya probadas y resultado obtenido.

> Tu responsabilidad como analista concluye al ejecutar el diagnóstico y completar las iteraciones de parámetros. Si después de ese proceso la tasa permanece por debajo del 70%, el caso se escala al colaborador técnico del proyecto.

---

## 📲 FASE 3 — Publicar en WhatsApp Business

> **Objetivo:** entregar el catálogo etiquetado al cliente a través del canal oficial.

### Mover el archivo

- [ ] Copiar el PDF final desde `salidas/` al directorio correspondiente:
  ```
  ~/boutique_zepeda/<marca>/catalogos_etiquetados/
  ```

### Subir a Dropbox

- [ ] Subir a 🗳️ Dropbox: `Inicio > <marca> > catalogos`
- [ ] Copiar el enlace generado por Dropbox.
- [ ] Pegar el enlace en VSC, en el archivo `~/books-label/prompts/notas_operativas.md`.
- [ ] Cambiar el último carácter del enlace: `0` → `1` *(esto convierte el enlace de previsualización en enlace de descarga directa)*.

<img src="../imagenes/asset_repo/link.png" alt="Boutique Zepeda — Taller de Etiquetado" width="95%"/>

### Comprimir el enlace

- [ ] Acceder a [bitly.com](https://bitly.com) → `Create new` → pegar el enlace modificado desde VSC.

<img src="../imagenes/asset_repo/bitly.png" alt="Boutique Zepeda — Taller de Etiquetado" width="85%"/>

> 🥺 Bitly tiene un límite mensual de enlaces. Contamos con 3 cuentas para distribuir la carga — si se agotan, se utiliza el enlace largo directamente en WhatsApp Business.

- [ ] Copiar el enlace corto generado por Bitly.
- [ ] Pegarlo en el mismo bloque de VSC: `~/books-label/prompts/notas_operativas.md`.

### Crear el artículo en WhatsApp Business

- [ ] Utilizando 🔥 **Flameshot**, capturar 10 recortes representativos del catálogo etiquetado, incluyendo la portada. Guardar en `~/boutique_zepeda/<marca>/carrusel` con nombres secuenciales — ejemplo: `1.png, 2.png, ..., 10.png`.

- [ ] Desde **WhatsApp Business Desktop** navegar a `Herramientas` > `Catálogo` > `Añadir un artículo nuevo`:

<img src="../imagenes/asset_repo/WB.png" alt="Boutique Zepeda — Taller de Etiquetado" width="85%"/>

---

> **Nota — cuando la aplicación de escritorio no está disponible**
>
> En caso de fallo en la funcionalidad de catálogo en la versión de escritorio, utilizar el dispositivo móvil Android. Las imágenes compartidas por WhatsApp se almacenan en:
> ```
> Almacenamiento interno > Android > media > com.whatsapp > WhatsApp > Media > WhatsApp Images > Sent
> ```
> Mover las imágenes a una carpeta accesible — por ejemplo `Pictures > carrusel` — para que WhatsApp las detecte al momento de seleccionarlas.

---

- [ ] En `Añadir imágenes`, cargar las 10 capturas desde `~/boutique_zepeda/<marca>/carrusel`.
- [ ] Completar los campos requeridos:
  - **Nombre:** nombre del catálogo o proveedor.
  - **Descripción:** pegar el siguiente texto:
    ```
    Da clic en el enlace 👇 para descargar el catálogo, espera o confirma la descarga. ✅️ Revisa tu carpeta de descargas.
    ```
- [ ] En el campo **Enlace**: pegar el link de Bitly → **Guardar**.

---

## 🆘 Árbol de decisión ante resultados adversos

```
¿El semáforo fue amarillo o rojo?
        ↓
Revisar el PDF — ¿el problema es visible?
   ↙                      ↘
  Sí                        No
  ↓                          ↓
Ajustar parámetros       Ejecutar diagnostico.py
en el configurador       y compartir output con Claude
```

> El proceso está diseñado para acompañarte en cada paso. Cualquier duda es válida — consultar siempre es la decisión correcta.

---

*Última revisión: 03-2026 · books-label*
