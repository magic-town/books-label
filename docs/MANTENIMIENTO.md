# Mantenimiento

## Descripción general

Nuestra oficina de edición de catálogos, vista desde inmuebles o hardware, se compone de:

- **2 computadoras físicas** que trabajan en local de forma independiente y en remoto como una sola:
  - `sonia@envy`
  - `gabriel@actuary`

Las dos computadoras están conectadas por VPN **Tailscale**, por lo que para trabajar en red lo único que necesitan es conexión a `internet`, independientemente del `SSID`.

Comparten cuenta y credenciales de GitHub, por lo que todas las subidas o actualizaciones las toma como si fueran de la misma persona/máquina.

---

Sin embargo, no todo lo que comparten necesita guardarse en Git. Por ejemplo, hay respaldos como el directorio `~/boutique_zepeda` que puede contener ficheros o directorios que no son propios a la oficina de edición de catálogos. Un fichero `inventario` o un directorio `FOLEYS` son ejemplos de assets que no necesitamos en Git.

Para ello se creó el directorio `pto_montaje`:

```
┌─[sonia@envy]─[~/boutique_zepeda/pto_montaje]
└─$ tree -L 2
.
├── books_label_backup
│   ├── docs
│   ├── fase1
│   └── fase2
├── inventario
│   └── inventario_bz.ods
├── lista_precios_proveedores.ods
├── setup
│   ├── git_nvim_vsc_md_ssh.txt
│   ├── prompt_diseno.txt
│   └── test_tesseract.txt
└── social_media
    ├── portada_catalogos
    ├── ropa_tienda
    └── videos
```

---

## Descripción de cada directorio

### `books_label_backup`

```
├── books_label_backup
    ├── docs
    ├── fase1
    └── fase2
```

Respaldo de ficheros que pertenecen a versiones anteriores o que ya fueron utilizados.

#### Tarea de Mantenimiento

**Ejemplo 1 — `fase_2/precios/lista_ella.xlsx`**

Este fichero ya fue usado, por lo que se cortó y pegó en este directorio:

```bash
mv ~/books-label/fase_2/precios/lista_ella.xlsx \
   ~/boutique_zepeda/pto_montaje/price/
```

Tareas similares se realizan entre `/books-label/fase_2/` y `boutique_zepeda/pto_montaje/books_label_backup/`.

---

**Ejemplo 2 — `fase_1/lista_cruda/importados_pv26.pdf`**

```bash
# Se elimina porque ya existe un respaldo en:
# ~/boutique_zepeda/Price_Shoes/catalogos/importados_pv26.pdf
rm ~/books-label/fase_1/lista_cruda/importados_pv26.pdf
```

---

**Ejemplo 3 — `fase_2/config/config_kids_todoen1.json`**

El fichero ya fue utilizado, pero se conserva porque contiene la posición de la etiqueta, el logo y la configuración óptima de impresión:

```bash
mv ~/books-label/fase_2/config/config_kids_todoen1.json \
   ~/boutique_zepeda/pto_montaje/fase_2/config/
```

Lo mismo aplica para la lista de precios correspondiente:

```bash
mv ~/books-label/fase_2/precios/lista_kids_todoen1.xlsx \
   ~/boutique_zepeda/pto_montaje/fase_2/precios/price/
```

---

### `inventario`

Contiene el fichero `inventario_bz.ods`. Además de ser el primer inventario digital, es también el primer ejercicio de control de ventas.

---

### `lista_precios_proveedores.ods`

#### Tarea de Mantenimiento

**Contexto:** Al ejecutar el extractor de fase 1:

```bash
python3 fase_1/extractor.py --config fase_1/config/<config_proveedor.json>
```

Se generan 2 ficheros. El primero es `~/books-label/fase_1/salida/base_precios.xlsx`, que se autocompleta cada vez que se ejecuta `extractor.py`.

Para contar con un respaldo editable con mayor flexibilidad, los registros se cortan y pegan en:

```
~/boutique_zepeda/pto_montaje/lista_precios_proveedores.ods
```

---

### `setup`

Directorio con ficheros `.txt` que contiene comandos bash y prompts tipo plantilla con el diseño del proyecto.

---

### `social_media`

Directorio orientado hacia la **fase 3**, relativa a publicaciones en plataformas digitales.
