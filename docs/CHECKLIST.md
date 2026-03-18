<img src="../imagenes/asset_repo/cover00.png" alt="Boutique Zepeda — Taller de Etiquetado" width="100%"/>

# ✨ Guía de Etiquetado — Boutique Zepeda

> Cada catálogo que etiquetas aquí es uno menos a mano.
> Sigue los pasos en orden y el proceso se cuida solo.

---

## 🗺️ ¿Dónde estoy en el proceso?

```
FASE 1          FASE 2          FASE 3
Preparar   →   Etiquetar   →   Publicar
precios         catálogo        en WA
```

---

## 📋 FASE 1 — Preparar los precios

> Objetivo: tener el archivo Excel listo antes de tocar el script.

### Descargar y verificar

- [ ] Descargar el catálogo PDF y la lista de precios del proveedor.
- [ ] Validar visualmente que el catálogo y la lista coincidan: número de páginas, IDs y precios sugeridos.
- [ ] Mover ambos archivos a: `~/boutique_zepeda/<proveedor>/catalogos` y `~/boutique_zepeda/<proveedor>/lista_precios` respectivamente.

### Extraer los precios con LLM *(solución temporal — se evalúa script.py como alternativa más precisa)*

- [ ] Elige un LLM: NotebookLM, Claude, o ambos en paralelo. 📎 Adjunta la lista cruda del proveedor.
- [ ] Abrir el prompt de extracción: 👉 [magic-town/books-label](../prompts/extraer_columnas_listas.md)
- [ ] Pegar el prompt en el LLM y ejecutar.
- [ ] Validar visualmente: **lista cruda del proveedor** Vs **lista extraída por el LLM**.

### Crear la tabla en LibreOffice

> Trabajamos con LibreOffice Calc. Algunas fórmulas y atajos dependen de las extensiones instaladas — si algo no responde como se describe, verifica que estén activas.

- [ ] Abrir `~/books-label/precios/tabla_precios.ods` en LibreOffice Calc.
- [ ] Agregar hoja nueva → renombrar como `<proveedor_categoria>`.
- [ ] Pegar la tabla extraída en formato de número.
- [ ] Verificar columna de redondeo — si no existe, agregarla:
  ```
  =ROUND(C2, -1)
  ```
- [ ] Agregar columna `precio_venta` con fórmula VLOOKUP *(ver hojas anteriores)*.
- [ ] Agregar columna `len`:
  ```
  =LEN(A2)
  ```
- [ ] Llenar la tabla completa.

### 🔎 Validación — no saltar este paso

- [ ] Fijar encabezados: `Ver > Fijar filas y columnas > Fijar primera fila`
- [ ] Activar filtros: `Datos > AutoFiltro` o `Ctrl+Shift+L`
- [ ] Filtrar columna `len` → comparar largos contra la lista del proveedor.
- [ ] Confirmar que no haya IDs con largo incorrecto ni precios en cero.

### ⚠️ Preparar el archivo final — paso crítico

- [ ] Quitar filtros antes de copiar.
- [ ] Copiar columna `ID` → pegar normal.
- [ ] Copiar columna `precio_venta` → **pegar especial > Número** (clic derecho).
- [ ] La hoja debe quedar con dos tablas:
  - Tabla completa con todos los campos.
  - Tabla simplificada solo con `ID` y `precio_venta`.
- [ ] Copiar la tabla simplificada a un archivo nuevo: `Archivo > Nueva hoja de cálculo > Pegar`.
- [ ] Guardar como:
  ```
  ~/books-label/precios/<lista_catalogo.xlsx>
  ```
  Si aparece ventana de formato Excel → confirmar con **Aceptar**.

---

## 🏷️ FASE 2 — Etiquetar el catálogo

> Objetivo: ejecutar el script y obtener semáforo verde.

### Preparar el config

- [ ] Hacer una copia de `configs/config_base.json`.
- [ ] Renombrarla como `config_<proveedor>_<temporada>.json` — ejemplo: `config_jeans_PV26.json`.
- [ ] Abrir el configurador visual y actualizar los tres campos de archivos desde ahí (ver sección siguiente). Si prefieres editar el JSON directamente en VSC, los campos son:

  | Campo | Qué escribir |
  |-------|--------------|
  | `pdf_input` | `"libros/<catalogo_temp.pdf>"` |
  | `excel_input` | `"precios/<lista_catalogo.xlsx>"` |
  | `pdf_output` | `"salidas/<catalogo_temp_precios.pdf>"` |

- [ ] Guardar el archivo (`Ctrl+S`).

### Ajustar parámetros con el configurador

- [ ] Abrir el configurador visual. Tienes tres opciones — usa la que tengas a mano:
  - Desde terminal:
    ```bash
    source venv_catalogo/bin/activate

    ```

    ```bash
    python3 abrir_configurador.py
    ```
  - Desde Dolphin: doble clic en `abrir_configurador.py`.
  - Si ya lo tienes abierto en el navegador, no es necesario volver a lanzarlo.

- [ ] Ajusta los parámetros clave. Empieza siempre con `paginas_prueba` activo para no procesar el catálogo completo en cada prueba:

  | Parámetro | Valores a probar |
  |-----------|-----------------|
  | `paginas_prueba` | `1, 5, 10, 40` — usa `false` solo para la corrida final |
  | `dpi` | `200, 250, 300` |
  | `psm` | `6` (normal), `11` (IDs dispersos), `4` (columnas) |
  | `ocr_doble_pasada` | `false` primero — activar solo si el diagnóstico lo sugiere |

- [ ] Copia el JSON generado y pégalo en tu archivo de config.
- [ ] La doble pasada duplica el tiempo de proceso — úsala como último recurso, no como punto de partida.

### Ejecutar

- [ ] En la terminal de VSC, ejecutar el script:
  ```bash
  python3 scripts/catalogo_base.py --config configs/<nombre_config>.json
  ```

### Leer el semáforo

Al terminar verás el resultado en consola:

| Resultado | Qué hacer |
|-----------|-----------|
| 🟢 **VERDE** — 85% o más | Revisar el PDF visualmente y pasar a Fase 3 |
| 🟡 **AMARILLO** — 65% a 84% | Revisar el PDF y decidir si ajustar antes de continuar |
| 🔴 **ROJO** — menos de 65% | No publicar — ver sección siguiente |

### Revisar el PDF visualmente

Abrir el archivo en `salidas/` y confirmar:

- [ ] ¿Los precios aparecen junto a cada producto?
- [ ] ¿Están en la posición correcta, sin encimarse con otro texto?
- [ ] ¿El formato del precio se ve bien? — ejemplo: `$250`
- [ ] ¿Hay páginas completas sin ningún precio?

### Si el semáforo no es verde

Elige el camino según lo que observas:

**Camino A — Ajustar parámetros tú misma**
- [ ] Abre el configurador, mueve los sliders y copia el JSON actualizado al config.
- [ ] Vuelve a ejecutar el script y compara el semáforo.

**Camino B — Diagnóstico automático + consulta a Claude**
- [ ] Ejecutar el diagnóstico:
  ```bash
  python3 scripts/diagnostico.py
  ```
- [ ] Copiar el output completo y pegarlo en Claude: *"Este es el diagnóstico de mi script de etiquetado, ¿qué parámetros ajusto?"*

**Camino C — Consulta directa a Claude**
- [ ] Captura el PDF con el problema y el output de consola.
- [ ] Abre Claude y describe lo que ves: *"El precio aparece encimado / no aparece / está muy lejos del ID"*

> 💡 Si sabes dónde está el problema → Camino A. Si no tienes idea → Camino B o C. Nunca publiques con semáforo rojo.

---

## 📲 FASE 3 — Publicar en WhatsApp Business

> Objetivo: el catálogo en manos del cliente.

### Mover el archivo

- [ ] Copiar el PDF final desde `salidas/` a:
  ```
  ~/boutique_zepeda/<marca>/catalogos_etiquetados/
  ```

### Subir a Dropbox

- [ ] Subir a 🗳️ Dropbox: `Inicio > <marca> > catalogos`
- [ ] Copiar el enlace de Dropbox.
- [ ] Pegar el enlace en **VSC**: `~/books-label/prompts/notas_operativas.md`
- [ ] Cambiar el último carácter del enlace: `0` → `1` *(esto convierte el enlace de previsualización en enlace de descarga directa)*.

<img src="../imagenes/asset_repo/link.png" alt="Boutique Zepeda — Taller de Etiquetado" width="95%"/>

### Comprimir el enlace

- [ ] Ir a [bitly.com](https://bitly.com) → `Create new` → pegar el enlace modificado desde **VSC**.

<img src="../imagenes/asset_repo/bitly.png" alt="Boutique Zepeda — Taller de Etiquetado" width="85%"/>

- [ ] Copiar el enlace corto generado por Bitly.
- [ ] Pegarlo en el mismo bloque de **VSC**: `~/books-label/prompts/notas_operativas.md`

### Crear el artículo en WhatsApp Business

- [ ] Con 🔥 **Flameshot** hacer 10 recortes del catálogo etiquetado, incluyendo la portada. Guardar en `~/boutique_zepeda/<marca>/carrusel` con nombres descriptivos — ejemplo: `jeans_1.png, jeans_2.png, ..., jeans_10.png`

- [ ] Desde **WhatsApp Business Desktop** abrir `Herramientas` > `Catálogo` > `Añadir un artículo nuevo`:

<img src="../imagenes/asset_repo/WB.png" alt="Boutique Zepeda — Taller de Etiquetado" width="85%"/>

- [ ] En `Añadir imágenes` cargar las 10 imágenes desde `~/boutique_zepeda/<marca>/carrusel`. Llenar los campos: **Nombre** y en **Descripción** pegar este bloque:

```
Da clic en el enlace 👇 para descargar el catálogo, espera o confirma la descarga. ✅️ Revisa tu carpeta de descargas.
```

- [ ] En el campo **Enlace**: pegar el link de Bitly → **Guardar**.

---

## 🆘 ¿Algo no salió bien?

```
¿El semáforo fue amarillo o rojo?
        ↓
Observa el PDF — ¿ves el problema?
   ↙              ↘
  Sí               No
  ↓                ↓
Ajusta params   Ejecuta diagnostico.py
en configurador  y pégalo a Claude
```

> Cualquier duda es válida — el proceso está para apoyarte, no para juzgarte.

---

*Última revisión: 03-2026 · books-label*
