# CHECKLIST — Etiquetado de Catálogos de Ropa

**Uso:** Proceso estándar de etiquetado y preparación de catálogos para impresión.  
**Última revisión:** 02-2026

---

## ⚡ Ejecución imediata

1. Extraer y validar precios → guardar como `precios_cat.xlsx`
2. Activar entorno virtual `venv_catalogo`
3. *(Opcional)* Testear páginas 1–10 → `catalogo_pag.py`
4. Generar catálogo final → `catalogo_fecha.py`
5. Revisar métricas en log → `diagnosticos/`
6. Si eficiencia < 80% → seguir `docs/DIAGNOSTICO.md` antes de publicar

---

## FASE 1 — Preparación de insumos y precios

**Objetivo:** Obtener, validar y preparar los datos de precios antes del etiquetado.

- [ ] Descargar catálogo y lista de precios del proveedor en PDF.
- [ ] Verificar que coincidan: catálogo vs. lista de precios (mismo proveedor, misma temporada).
- [ ] Mover ambos archivos a:
  ```
  ~/boutique_zepeda/<proveedor>/
  ```
- [ ] Extraer de la lista de precios los campos `Pag`, `ID`, `Sug_credito` usando el prompt en:
  ```
  ~/taller_etiquetado/prompts/extraer_columnas_listas.txt
  ```
- [ ] Revisión rápida de los datos extraídos: consistencia, formato, valores atípicos.
- [ ] Abrir `~/taller_etiquetado/tabla_precios.ods` en LibreOffice Calc:
  - Agregar hoja nueva → renombrar como `<proveedor_categoria>`
  - Pegar tabla extraída en formato de número
- [ ] Verificar columna de redondeo. Si no existe, agregarla:
  ```
  =ROUND(C2, -1)
  ```
- [ ] Agregar columna `precio_venta` con fórmula VLOOKUP (ver hojas anteriores del mismo archivo).
- [ ] Agregar columna `len`:
  ```
  =LEN(A2)
  ```
- [ ] Llenar tabla completa con redondeo y precio_venta.

### 🔎 Validación tipo analista

- [ ] Fijar encabezados: seleccionar fila 1 → `View > Freeze Cells > Freeze First Row`
- [ ] Insertar filtros: seleccionar fila 1 → `Data > AutoFilter` (`Ctrl+Shift+L`)
- [ ] Filtrar columna `len` y comparar contra lista cruda del proveedor
- [ ] Validar que no haya IDs con largo incorrecto o precios en cero

### 👀 CRÍTICO — Preparar archivo final

- [ ] Quitar filtros antes de copiar
- [ ] Copiar columna `ID` → pegar normal
- [ ] Copiar columna `precio_venta` → **pegar especial > Número** (clic derecho)
- [ ] La hoja debe quedar con **dos tablas**:
  - Tabla completa (todos los campos)
  - Tabla simplificada solo con `[ID, precio_venta]`
- [ ] Copiar tabla simplificada a archivo nuevo:
  ```
  ~/taller_etiquetado/precios/<nombre_archivo.xlsx>
  ```
  Si aparece ventana de formato Excel 1997-2000 → confirmar con Aceptar.

---

## FASE 2 — Taller de etiquetado automático

**Objetivo:** Ejecutar el proceso de etiquetado sobre el catálogo.

### Opción A — Desde VSC

- [ ] `File > Open Folder > taller_etiquetado`
- [ ] Abrir el script en `scripts/`
- [ ] Verificar y actualizar inputs/outputs:
  - PDF del catálogo → directorio `libros/`
  - Lista de precios → directorio `precios/`
  - Nombre del archivo de salida → directorio `salidas/`
- [ ] Verificar que los nombres en el script coincidan exactamente con los archivos en disco
- [ ] Ejecutar con `Play` o `F5`

### Opción B — Desde terminal

```bash
cd ~/taller_etiquetado
source venv_catalogo/bin/activate
python3 scripts/catalogo_fecha.py
```

---

## FASE 2.1 — Validación previa / Testeo

**Usar cuando:** proveedor nuevo, temporada nueva, o formato distinto al habitual.

- [ ] ¿Se puede seleccionar texto en el PDF?
  - **NO** → apto para etiquetar completo
  - **SÍ** → revisar posicionamiento antes de continuar
- [ ] ¿Es difícil posicionar el precio cerca del ID?
- [ ] Si hay dudas → testear con `catalogo_pag.py` (páginas 1–10)
- [ ] Revisar en el script: rutas, nombres, tamaño/color/posición de etiqueta
- [ ] Ajustar con GitHub Copilot si es necesario
- [ ] Ejecutar prueba:
  ```bash
  python3 scripts/catalogo_pag.py
  ```
- [ ] Revisar log en `diagnosticos/` → ver `docs/DIAGNOSTICO.md`

---

## FASE 3 — Compartir en WhatsApp Business

**Objetivo:** Publicar el catálogo etiquetado para clientes.

- [ ] Copiar PDF final desde `salidas/` a:
  ```
  ~/boutique_zepeda/<marca>/catalogos_etiquetados/
  ```
- [ ] Subir a Dropbox: `Inicio > <marca> > catalogos`
- [ ] Copiar enlace de Dropbox → pegar en `~/taller_etiquetado/test_Whatsapp.txt`
- [ ] Editar el último caracter del enlace (cambiar `0` por `1`)
- [ ] Comprimir enlace en [bitly.com](https://bitly.com): `Create new > pegar enlace`
- [ ] Copiar enlace comprimido

### Crear artículo en WhatsApp Business

- [ ] Tomar captura de pantalla de la portada del catálogo
- [ ] Enviarte a la cuenta **Boutique Zepeda** la portada y el link de Bitly
- [ ] `Herramientas > Catálogos > Nuevo artículo`
  - Imagen: portada capturada
  - Enlace: link de Bitly
