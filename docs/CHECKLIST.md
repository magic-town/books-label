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

- [ ] Descargar el catálogo PDF y la lista de precios del proveedor
- [ ] Confirmar que son del mismo proveedor y la misma temporada
- [ ] Mover ambos archivos a `~/boutique_zepeda/<proveedor>/`

### Extraer los precios

- [ ] Abrir el prompt en `prompts/extraer_columnas_listas.txt`
- [ ] Usar el prompt con Claude o Gemini para extraer los campos `Pag`, `ID`, `Sug_credito`
- [ ] Revisar rápidamente que los datos se vean bien — sin huecos raros ni precios en cero

### Armar la tabla en LibreOffice

- [ ] Abrir `~/books-label/precios/tabla_precios.ods` en LibreOffice Calc
- [ ] Agregar hoja nueva → renombrar como `<proveedor_categoria>`
- [ ] Pegar la tabla extraída en formato de número
- [ ] Verificar columna de redondeo — si no existe, agregarla:
  ```
  =ROUND(C2, -1)
  ```
- [ ] Agregar columna `precio_venta` con fórmula VLOOKUP *(ver hojas anteriores)*
- [ ] Agregar columna `len`:
  ```
  =LEN(A2)
  ```
- [ ] Llenar la tabla completa

### 🔎 Validación — no saltar este paso

- [ ] Fijar encabezados: `View > Freeze Cells > Freeze First Row`
- [ ] Activar filtros: `Data > AutoFilter` o `Ctrl+Shift+L`
- [ ] Filtrar columna `len` → comparar largos contra la lista del proveedor
- [ ] Confirmar que no haya IDs con largo incorrecto ni precios en cero

### ⚠️ Preparar el archivo final — paso crítico

- [ ] Quitar filtros antes de copiar
- [ ] Copiar columna `ID` → pegar normal
- [ ] Copiar columna `precio_venta` → **pegar especial > Número** (clic derecho)
- [ ] La hoja debe quedar con dos tablas:
  - Tabla completa con todos los campos
  - Tabla simplificada solo con `ID` y `precio_venta`
- [ ] Copiar la tabla simplificada a un archivo nuevo en
- [ ] file > new spreedsheet > paste
- [ ] File > save as:
  ```
  ~/books-label/precios/<lista_catalogo.xlsx>
  ```
  Si aparece ventana de formato Excel → confirmar con **Aceptar**

---

## 🏷️ FASE 2 — Etiquetar el catálogo

> Objetivo: ejecutar el script y obtener semáforo verde.

### Preparar el config

- [ ] Hacer una copia de `configs/config_base.json`
- [ ] Renombrarla como `config_<proveedor>_<temporada>.json` — ejemplo: `config_jeans_PV26.json`
- [ ] Abrirla en VSC y actualizar los tres campos de archivos:

  | Campo | Qué escribir |
  |-------|--------------|
  | `pdf_input` | `"libros/<nombre_del_pdf>.pdf"` |
  | `excel_input` | `"precios/<nombre_del_excel>.xlsx"` |
  | `pdf_output` | `"salidas/<nombre_que_quieras>.pdf"` |

- [ ] Guardar el archivo (`Ctrl+S`)

### Entender y ajustar parámetros — usar el configurador

- [ ] Abrir terminal en VSC: `View > Terminal`
- [ ] Activar el entorno virtual:
  ```bash
  source venv_catalogo/bin/activate
  ```
- [ ] Abrir el configurador visual:
  ```bash
  python3 abrir_configurador.py
  ```
- [ ] Mover los sliders para entender qué hace cada parámetro
- [ ] Anotar los valores que quieres probar
- [ ] Escribir esos valores en tu config en VSC y guardar

### Ejecutar

- [ ] En la terminal de VSC, ejecutar el script:
  ```bash
  python3 scripts/catalogo_base.py --config configs/<nombre_config>.json
  ```

### Leer el semáforo

Al terminar verás el resultado en consola:

| Resultado | Qué hacer |
|-----------|-----------|
| 🟢 **VERDE** — 85% o más | Abrir el PDF en `salidas/` y revisar visualmente, luego ir a Fase 3 |
| 🟡 **AMARILLO** — 65% a 84% | Revisar el PDF y decidir si ajustar antes de continuar |
| 🔴 **ROJO** — menos de 65% | No publicar — ver sección siguiente |

### Revisar el PDF visualmente

Antes de publicar, abrir el archivo en `salidas/` y confirmar:

- [ ] ¿Los precios aparecen junto a cada producto?
- [ ] ¿Están en la posición correcta, sin encimarse con otro texto?
- [ ] ¿El formato del precio se ve bien? — ejemplo: `$250.00`
- [ ] ¿Hay páginas completas sin ningún precio?

### Si el semáforo no es verde

Tienes tres caminos — elige según lo que observas en el PDF y en consola:

**Camino A — Ajustar parámetros tú misma**
- [ ] Abre el configurador (`python3 abrir_configurador.py`) y mueve los sliders
- [ ] Edita el config en VSC con los nuevos valores
- [ ] Vuelve a ejecutar el script y compara el semáforo

**Camino B — Diagnóstico automático + consulta a Claude**
- [ ] Ejecutar el diagnóstico:
  ```bash
  python3 scripts/diagnostico.py
  ```
- [ ] Copiar todo el output de la terminal
- [ ] Abrirlo en Claude y preguntar: *"Este es el diagnóstico de mi script de etiquetado, ¿qué parámetros ajusto?"*

**Camino C — Consulta directa a Claude**
- [ ] Tomar captura de pantalla del PDF con el problema
- [ ] Tomar captura de pantalla del output de consola
- [ ] Abrir Claude y describir lo que ves: *"El precio aparece encimado / no aparece / está muy lejos del ID"*

> 💡 Los tres caminos funcionan. El criterio para elegir: si sabes dónde está el problema, usa A. Si no tienes idea, usa B o C.
> Nunca publiques con semáforo rojo.

---

## 📲 FASE 3 — Publicar en WhatsApp Business

> Objetivo: el catálogo en manos del cliente.

### Mover el archivo

- [ ] Copiar el PDF final desde `salidas/` a:
  ```
  ~/boutique_zepeda/<marca>/catalogos_etiquetados/
  ```

### Subir a Dropbox

- [ ] Subir a 🗳️​ Dropbox: `Inicio > <marca> > catalogos`
- [ ] Copiar el enlace de Dropbox
- [ ] Pegar el enlace en **VSC**: `~/books-label/prompts/notas_operativas.md`
- [ ] Cambiar el último carácter del enlace: `0` → `1`

<img src="../imagenes/asset_repo/link.png" alt="Boutique Zepeda — Taller de Etiquetado" width="75%"/>

### Comprimir el enlace

- [ ] Ir a [bitly.com](https://bitly.com) → `Create new` → pegar el enlace de **VSC** `../notas_operativas` que anteriormente se genero en Dropbox.

<img src="../imagenes/asset_repo/bitly.png" alt="Boutique Zepeda — Taller de Etiquetado" width="75%"/>

- [ ] Copiar el enlace comprimido que genera bitly
- [ ] Pegar el enlace en el mismo bloque de **VSC**: `~/books-label/prompts/notas_operativas.md`

### Crear el artículo en WhatsApp Business

- [ ] Con tu herramienta 🔥 **Flameshot** hacer 10 recortes del catalogo recién etiquetado incluyendo la página de portada del catálogo, guardar una por una en `~/boutique_zepeda/<marca>/carrusel` con nombres descriptivos. Ejemplo: `jeans_1.png, jeans_2.png, ..., jeans_10.png` 

- [ ] Desde **WhatsApp Bussines Desktop** abrir calatalogo:

<img src="../imagenes/asset_repo/WB.png" alt="Boutique Zepeda — Taller de Etiquetado" width="75%"/>

- [ ] `Herramientas > Catálogos > Nuevo artículo`
  - **Imagen:** portada capturada
  - **Enlace:** link de Bitly

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

> El colaborador está para acompañar, no para juzgar. Cualquier duda es válida.

---

*Última revisión: 03-2026 · books-label*
