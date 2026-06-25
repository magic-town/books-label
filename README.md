# books-label

**Herramienta de etiquetado de catálogos — Boutique Zepeda**

---

## ¿Qué hace este proyecto?

`books-label` tiene dos objetivos en secuencia:

1. **Etiquetar catálogos.** Toma los catálogos PDF de los proveedores y les imprime los precios de la Boutique mediante `OCR` auxiliandose con tabla/tabulador de precios en Excel. El resultado es un PDF listo para distribuir al cliente, canales de venta.

2. **Desplegar los catálogos etiquetados a un canal de venta.** Este segundo objetivo está en definición. Las opciones evaluadas son:

  - `GitHub Pages` (visualización directa desde el repositorio).
  - Portal web desplegado en Vercel o equivalente. 
  - Dropbox + WhatsApp Business.

  De los anteriores ya se probo `Dropbox + Whatsapp Business`, se deshabilito ya que se busca que la descarga sea opcional, i.e., que la visualización sin descarga tenga prioridad lo cual no se conciguio por este canal.

---

## Team

| Colaborador | Rol |
|---------|-----|
| Sonia   | Analista operativa |
| Gabriel | Desarrollo y mantenimiento técnico |


**Sonia** trabaja con paneles `HTML`, ficheros de configuración `JSON` ejecución de `script.py` — sin editar código ni montar infraestructura.

**Gabriel** es responsable del mantenimiento, programación, setup.

---

## Flujo de trabajo

<div align="center">
  <img src="./imagenes/asset_repo/cover_fases.png" 
       alt="Boutique Zepeda — Taller de Etiquetado"
       width="85%"/>
</div>

La guía operativa completa para la `analista_operativa` está en [`docs/CHECKLIST.md`](docs/CHECKLIST.md).

---

## Estructura del proyecto

```text
.
├── CLAUDE.md
├── docs
│   ├── CHECKLIST.md
│   ├── EXTRAER_PRECIOS_SIN_SCRIPT.md
│   ├── GIT-ESENCIAL.md
│   ├── MANTENIMIENTO.md
│   └── social_media.md
├── fase_1
│   ├── config
│   │   ├── archivo
│   │   ├── config_pakar.json
│   │   ├── config_price.json
│   │   └── panel_extraer_campos.html
│   ├── diagnosticos
│   ├── docs
│   │   └── README.md
│   ├── extractor.py
│   ├── lista_cruda
│   │   ├── archivo
│   │   ├── lista_accesorios.pdf
│   │   └── tabulador.xlsx
│   └── salida
│       └── base_precios.xlsx
├── fase_2
│   ├── catalogo_base.py
│   ├── config
│   │   ├── archivo
│   │   ├── config_base.json
│   │   └── configurador.html
│   ├── diagnosticos
│   ├── docs
│   │   ├── ARQUITECTURA.md
│   │   ├── DIAGNOSTICO.md
│   │   ├── README.md
│   │   └── SETUP.md
│   ├── libros
│   │   └── perfumes_26.pdf
│   ├── ocr_diagnostico.sh
│   ├── precios
│   │   ├── archivo
│   │   └── lista_perfumes_26.xlsx
│   └── salidas
│       └── mochilas_26_precios.pdf
├── fase_3
│   ├── docs
│   │   └── README.md
│   └── HISTORY_LINKS.md
├── imagenes
│   ├── asset_repo
│   │   ├── A171.png
│   │   └── WB.png
│   └── logos
│       ├── logo_bz.png
│       └── logo_ocean.png
├── README.md
├── requirements.txt
├── sync.sh
└── venv_catalogo
```

> `libros/` y `salidas/` no se versionan — contienen archivos de trabajo locales.
> `venv_catalogo/` tampoco se versiona — cada máquina lo recrea con `SETUP.md`.

---

## Inicio rápido

**Primera vez en esta máquina** — seguir [`docs/SETUP.md`](docs/SETUP.md).

**Uso diario:**

```bash
# 1. Sincronizar antes de trabajar
./sync.sh

# 2. Activar el entorno
source venv_catalogo/bin/activate

# 3. Abrir el configurador visual
xdg-open configs/configurador.html

# 4. Ejecutar el etiquetado
python3 scripts/catalogo_base.py --config configs/<nombre_config>.json

# 5. Sincronizar al terminar
./sync.sh
```

---

## Proveedores soportados

| Proveedor   | Formato de ID    | Estado           |
|-------------|------------------|------------------|
| Price Shoes | `ID xxxxxxx`     | ✅ Activo        |
| Pakar       | `Código xxx-xxx` | 🔧 En desarrollo |
| Cklass      | `xxx-xx`         | 🔧 En desarrollo |

El formato de cada proveedor se declara en `config_base.json`. Agregar un proveedor nuevo no requiere modificar el script.

---

## Sincronización entre máquinas

Gabriel y Sonia trabajan sobre el mismo repositorio desde máquinas distintas. El script `sync.sh` maneja la sincronización con las siguientes reglas:

- `tabla_precios.ods` siempre conserva la versión de Sonia.
- Los conflictos en otros archivos se reportan y deben resolverse manualmente.
- El commit incluye automáticamente quién sincronizó y qué archivos cambió.

```bash
./sync.sh   # bajar cambios + subir los propios
```

---

*books-label · Boutique Zepeda · 2026*
