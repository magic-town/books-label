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

### 👀 Preparar el archivo final — paso crítico

- [ ] Quitar filtros antes de copiar
- [ ] Copiar columna `ID` → pegar normal
- [ ] Copiar columna `precio_venta` → **pegar especial > Número** (clic derecho)
- [ ] La hoja debe quedar con dos tablas:
  - Tabla completa con todos los campos
  - Tabla simplificada solo con `ID` y `precio_venta`
- [ ] Copiar la tabla simplificada a un archivo nuevo en:
  ```
  ~/books-label/precios/<nombre_archivo.xlsx>
  ```
  Si aparece ventana de formato Excel → confirmar con **Aceptar**

---

## 🏷️ FASE 2 — Etiquetar el catálogo

> Objetivo: ejecutar el script y obtener semáforo verde.

### Antes de ejecutar

- [ ] Abrir VSC → `File > Open Folder > books-label`
- [ ] Abrir el archivo de configuración en `configs/` que corresponde al proveedor
- [ ] Verificar que los nombres coincidan exactamente con los archivos en disco:

  | Campo en el config | Archivo que debe existir |
  |--------------------|--------------------------|
  | `pdf_input` | en `libros/` |
  | `excel_input` | en `precios/` |
  | `pdf_output` | nombre del archivo que se va a generar en `salidas/` |

### Ejecutar

- [ ] Abrir terminal en VSC
- [ ] Activar el entorno virtual:
  ```bash
  source venv_catalogo/bin/activate
  ```
- [ ] Ejecutar el script:
  ```bash
  python3 scripts/catalogo_base.py --config configs/<nombre_config>.json
  ```

### Leer el semáforo

Al terminar verás el resultado en consola:

| Resultado | Qué hacer |
|-----------|-----------|
| 🟢 **VERDE** — 85% o más | Continuar a Fase 3 |
| 🟡 **AMARILLO** — 65% a 84% | Ejecutar diagnóstico antes de continuar |
| 🔴 **ROJO** — menos de 65% | Ejecutar diagnóstico y avisar al coach |

### Si el semáforo no es verde

- [ ] Ejecutar el diagnóstico:
  ```bash
  python3 scripts/diagnostico.py
  ```
- [ ] Leer las recomendaciones que aparecen
- [ ] Si puedes aplicarlas sola → ajustar el config y volver a ejecutar
- [ ] Si no es claro qué hacer → captura el reporte y mándalo al coach

### Revisar el PDF visualmente

Antes de publicar, abrir el archivo de salida en `salidas/` y confirmar:

- [ ] ¿Los precios aparecen junto a cada producto?
- [ ] ¿Están en la posición correcta, sin encimarse con otro texto?
- [ ] ¿El formato del precio se ve bien? — ejemplo: `$250.00`
- [ ] ¿Hay páginas completas sin ningún precio?

---

## 📲 FASE 3 — Publicar en WhatsApp Business

> Objetivo: el catálogo en manos del cliente.

### Mover el archivo

- [ ] Copiar el PDF final desde `salidas/` a:
  ```
  ~/boutique_zepeda/<marca>/catalogos_etiquetados/
  ```

### Subir a Dropbox

- [ ] Subir a Dropbox: `Inicio > <marca> > catalogos`
- [ ] Copiar el enlace de Dropbox
- [ ] Pegar el enlace en `~/books-label/test_Whatsapp.txt`
- [ ] Cambiar el último carácter del enlace: `0` → `1`

### Comprimir el enlace

- [ ] Ir a [bitly.com](https://bitly.com) → `Create new` → pegar el enlace
- [ ] Copiar el enlace comprimido

### Crear el artículo en WhatsApp Business

- [ ] Tomar captura de pantalla de la portada del catálogo
- [ ] Enviarte a la cuenta **Boutique Zepeda** la portada y el link de Bitly
- [ ] `Herramientas > Catálogos > Nuevo artículo`
  - **Imagen:** portada capturada
  - **Enlace:** link de Bitly

---

## 🆘 ¿Algo no salió bien?

```
¿El semáforo fue amarillo o rojo?
        ↓
Ejecuta diagnostico.py
        ↓
¿Las recomendaciones son claras?
   Sí → aplica y vuelve a ejecutar
   No → manda el reporte al coach
```

> 💡 Nunca publiques con semáforo rojo.
> El coach está para acompañar, no para juzgar. Cualquier duda es válida.

---

*Última revisión: 03-2026 · books-label*
