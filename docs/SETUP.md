# SETUP — Configuración del Entorno

**Autor:** Sonia  
**Fecha:** Febrero 2026  
**Sistema:** Ubuntu 24.04  
**CPU:** Intel Core i5-3317U @ 1.70GHz (Ivy Bridge 2012 — solo SSE4.2, sin AVX2)

---

## ⚠️ Nota de hardware

Este setup está optimizado para CPUs antiguos sin instrucciones AVX2.  
**No uses PyTorch ni EasyOCR** — causan `Illegal instruction (core dumped)`.  
El motor OCR es **Tesseract**, compatible con este hardware.

---

## 1. Dependencias del sistema

Desde la terminal ejecuta posicionado en el `/home/user/`, es decir:

```bash
┌─[user@hostname]─[~]
└─$ 
```

Los siguietes comandos, basta con hacer copy-paste:

```bash
sudo apt update
sudo apt install -y \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-spa \
    libgl1-mesa-glx \
    libglib2.0-0 \
    python3-pip \
    python3-venv
```

Verificar:

```bash
tesseract --version     # debe mostrar 5.3.x o superior
python3 --version       # debe mostrar 3.10 o superior
```

---

## 2. Estructura del proyecto

Usa `tree -L 2 ~/books-label`desde `/home/user/` ¿para visualizar tu estructura:


```
/home/user/books-label
├── diagnosticos
├── docs
│   ├── CHECKLIST.md
│   ├── DIAGNOSTICO.md
│   ├── git-esencial.txt
│   └── SETUP.md
├── libros
├── precios
├── prompts
├── README.md
├── requirements.txt
├── salidas
└── scripts
```

---

## 3. Entorno virtual Python

Ahora encapsulemos nuestro laboratorio:

```bash
cd ~/books-label
python3 -m venv venv_catalogo
source venv_catalogo/bin/activate
pip install --upgrade pip
```

El prompt debe cambiar a:

```
(venv_catalogo) gabriel@actuary:~/books-label$
```

---

## 4. Librerías Python

Con el entorno virtual activo:

```bash
pip install \
    pytesseract==0.3.10 \
    pillow==10.2.0 \
    pandas==2.2.0 \
    openpyxl==3.1.2 \
    pdf2image==1.17.0 \
    PyPDF2==3.0.1 \
    reportlab==4.1.0 \
    "numpy<2"
```

> `numpy<2` es crítico para compatibilidad con este CPU. No actualizar.

Verificar:

```bash
pip list | grep -E "pytesseract|pillow|pandas|openpyxl|pdf2image|PyPDF2|reportlab|numpy"
```

---

## 5. Verificación completa

```bash
python3 << 'EOF'
import pytesseract
import pandas as pd
import PIL
from pdf2image import convert_from_path
from PyPDF2 import PdfReader
from reportlab.pdfgen import canvas
print("✅ Todas las librerías importadas correctamente")
print(f"   Tesseract: {pytesseract.get_tesseract_version()}")
print(f"   Pandas:    {pd.__version__}")
print(f"   PIL:       {PIL.__version__}")
EOF
```

---

## 6. Uso del sistema

```bash
# 1. Posicionarse en el proyecto
cd ~/books-label

# 2. Activar entorno virtual
source venv_catalogo/bin/activate

# 3. Editar inputs/outputs en el script
#    Catálogo PDF  → libros/
#    Lista precios → precios/
#    Salida        → salidas/

# 4. Prueba (páginas 1-10)
python3 scripts/catalogo_pag.py

# 5. Catálogo completo
python3 scripts/catalogo_fecha.py

# 6. Ver log en tiempo real
tail -f diagnosticos/procesamiento_mejorado.log
```

---

## 7. Solución de problemas

| Error | Causa | Solución |
|-------|-------|---------|
| `tesseract not found` | No instalado | `sudo apt install tesseract-ocr tesseract-ocr-spa` |
| `No module named X` | Entorno no activo | `source venv_catalogo/bin/activate` |
| `Illegal instruction` | PyTorch/EasyOCR en CPU antiguo | Usar solo Tesseract |
| `numpy error` | Versión incompatible | `pip install "numpy<2"` |
| `PDF no encontrado` | Ruta o nombre incorrecto | Verificar nombre exacto en `libros/` |
| Baja precisión OCR | DPI bajo o PDF borroso | Cambiar `dpi=150` a `dpi=200` en el script |
| `PermissionError` | Sin permisos | `python3 scripts/catalogo_fecha.py` |

---

## 8. Backup

```bash
cd ~
tar -czf books-label_backup_$(date +%Y%m%d).tar.gz \
    --exclude='books-label/venv_catalogo' \
    --exclude='books-label/__pycache__' \
    --exclude='books-label/*.pyc' \
    books-label/
```

---

## 9. Comandos rápidos

```bash
# Activar entorno
cd ~/books-label && source venv_catalogo/bin/activate

# Ejecutar catálogo completo
python3 scripts/catalogo_fecha.py

# Ver log en tiempo real
tail -f diagnosticos/procesamiento_mejorado.log

# Desactivar entorno
deactivate

# Verificar espacio en disco
df -h ~/books-label

# Últimos archivos generados
ls -lht salidas/ | head -10

# Limpiar caché Python
find ~/books-label -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
```

---

## Historial

| Versión | Fecha | Cambios |
|---------|-------|---------|
| 1.0 | Feb 2026 | Setup inicial — migración de EasyOCR a Tesseract |
| 1.1 | Feb 2026 | Migración de `taller_etiquetado` a `books-label` |
