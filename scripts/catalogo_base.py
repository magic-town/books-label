#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
catalogo_base.py — Etiquetador Automático de Catálogos
Boutique Zepeda · books-label

Uso:
    python3 scripts/catalogo_base.py --config configs/config_jeans_PV26.json

Dependencias del sistema:
    sudo apt install tesseract-ocr tesseract-ocr-spa poppler-utils

Dependencias Python (requirements.txt):
    rapidfuzz, pandas, pdf2image, PyPDF2, reportlab, Pillow, openpyxl
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime
from io import BytesIO

import pandas as pd
import pytesseract
import re
import gc
import subprocess

from pdf2image import convert_from_path
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image, ImageEnhance, ImageFilter
from rapidfuzz import process, fuzz


# ─────────────────────────────────────────────
#  Argumentos de entrada
# ─────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(
        description="Etiquetador automático de catálogos PDF — Boutique Zepeda"
    )
    parser.add_argument(
        "--config",
        required=True,
        help="Ruta al archivo de configuración JSON (ej: configs/config_jeans_PV26.json)"
    )
    return parser.parse_args()


# ─────────────────────────────────────────────
#  Configuración de logging
# ─────────────────────────────────────────────

def setup_logging(base_dir: str, nombre_catalogo: str) -> str:
    """
    Crea el archivo de log con timestamp en diagnosticos/.
    Retorna la ruta del log generado.
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"{nombre_catalogo}_{timestamp}.log"
    log_path = os.path.join(base_dir, "diagnosticos", log_filename)
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return log_path


# ─────────────────────────────────────────────
#  Clase principal
# ─────────────────────────────────────────────

class EtiquetadorCatalogo:
    """
    Procesa catálogos PDF insertando precios desde Excel usando OCR + fuzzy matching.
    Todos los parámetros ajustables vienen del archivo de configuración JSON.
    """

    def __init__(self, config: dict, base_dir: str):
        self.config     = config
        self.base_dir   = base_dir
        self.logger     = logging.getLogger(__name__)

        # Rutas desde config
        self.pdf_path    = os.path.join(base_dir, config["pdf_input"])
        self.excel_path  = os.path.join(base_dir, config["excel_input"])
        self.output_path = os.path.join(base_dir, config["pdf_output"])

        # Parámetros OCR
        self.dpi            = config.get("dpi", 200)
        self.contraste      = config.get("contraste", 2.5)
        self.nitidez        = config.get("nitidez", 2.0)
        self.psm            = config.get("psm", 6)
        self.id_len_min     = config.get("id_longitud_min", 4)
        self.id_len_max     = config.get("id_longitud_max", 8)
        self.ocr_grayscale  = config.get("ocr_grayscale", True)
        self.ocr_invertir   = config.get("ocr_invertir", False)

        # Doble pasada OCR — resuelve catálogos con fondo mixto
        # (IDs negros sobre blanco + IDs blancos sobre fondo oscuro)
        self.ocr_doble_pasada = config.get("ocr_doble_pasada", False)

        # Parámetros fuzzy matching
        self.fuzzy_activo   = config.get("fuzzy_activo", True)
        self.fuzzy_umbral   = config.get("fuzzy_umbral", 85)

        # Parámetros etiqueta
        self.etiqueta_font      = config.get("etiqueta_font", "Helvetica-Bold")
        self.etiqueta_font_size = config.get("etiqueta_font_size", 11)
        self.etiqueta_color     = config.get("etiqueta_color_rgb", [0.0, 0.0, 1.0])
        self.etiqueta_offset_x  = config.get("etiqueta_offset_x_pt", 4.0)
        self.etiqueta_offset_y  = config.get("etiqueta_offset_y_pt", 5.67)

        # Parámetros logo
        self.logo_activo        = config.get("logo_activo", False)
        self.logo_path          = os.path.join(base_dir, config.get("logo_path", "")) if config.get("logo_path") else None
        self.logo_x             = config.get("logo_x_pt", 20.0)
        self.logo_y             = config.get("logo_y_pt", 750.0)
        self.logo_ancho         = config.get("logo_ancho_pt", 80.0)
        self.logo_alto          = config.get("logo_alto_pt", 40.0)
        self.logo_transparencia = config.get("logo_transparencia", 1.0)

        # Páginas de presentación — lista de {path, posicion}
        # posicion: 1=primera, 2=segunda, -1=última, N=posición exacta
        # Se procesan todas en orden antes de guardar el PDF final.
        raw_pres = config.get("presentaciones", [])
        self.presentaciones = [
            {
                "path":     os.path.join(base_dir, p["path"]),
                "posicion": p.get("posicion", 1)
            }
            for p in raw_pres
            if isinstance(p, dict) and p.get("path")
        ]

        # Modo prueba — false = catálogo completo, n >= 1 = solo primeras n páginas
        paginas_prueba_raw  = config.get("paginas_prueba", False)
        self.paginas_prueba = False if paginas_prueba_raw is False else int(paginas_prueba_raw)

        self._cargar_precios()
        self._verificar_tesseract()

    # ── Normalización PDF — compatibilidad universal ─────────────────────────────

    def _normalizar_pdf(self, path: str) -> None:
        """
        Re-renderiza el PDF con Ghostscript para garantizar compatibilidad
        universal: Android, lectores básicos, dispositivos legacy.

        PyPDF2 puede producir estructuras no estándar que Adobe tolera
        pero otros lectores rechazan. Ghostscript normaliza a PDF 1.4 limpio.

        Si Ghostscript no está disponible el PDF original se conserva intacto
        — el proceso no falla, solo avisa.
        """
        import tempfile, shutil
        tmp = path + ".gs_tmp.pdf"
        try:
            result = subprocess.run(
                [
                    "gs",
                    "-dBATCH", "-dNOPAUSE", "-dQUIET",
                    "-sDEVICE=pdfwrite",
                    "-dCompatibilityLevel=1.4",
                    "-dPDFSETTINGS=/default",
                    "-dEmbedAllFonts=true",
                    "-dSubsetFonts=true",
                    f"-sOutputFile={tmp}",
                    path
                ],
                capture_output=True, text=True, timeout=300
            )
            if result.returncode == 0 and os.path.exists(tmp):
                shutil.move(tmp, path)
                self.logger.info("  ✅  PDF normalizado con Ghostscript — compatible con todos los dispositivos")
            else:
                if os.path.exists(tmp):
                    os.remove(tmp)
                self.logger.warning(f"  ⚠️  Ghostscript falló (código {result.returncode}) — se conserva el PDF original")
                if result.stderr:
                    self.logger.debug(f"      GS stderr: {result.stderr[:200]}")
        except FileNotFoundError:
            self.logger.warning("  ⚠️  Ghostscript no encontrado — instalar con: sudo apt install ghostscript")
            self.logger.warning("      El PDF puede no abrirse en todos los dispositivos.")
        except subprocess.TimeoutExpired:
            self.logger.warning("  ⚠️  Ghostscript tardó demasiado — se conserva el PDF original")
            if os.path.exists(tmp):
                os.remove(tmp)
        except Exception as e:
            self.logger.warning(f"  ⚠️  Error en normalización: {e} — se conserva el PDF original")
            if os.path.exists(tmp):
                os.remove(tmp)

    # ── Insertar páginas de presentación ────────────────────────────────────────

    def _insertar_presentaciones(self, paginas: list, total_real: int = None) -> list:
        """
        Inserta carátulas en posiciones absolutas del documento final.

        Reglas de posición:
          posicion false  → desactivada, se omite
          posicion N >= 1 → página N absoluta en el PDF final
                            las portadas previas ya cuentan en el índice
                            si N > páginas disponibles, se omite
          posicion -1     → última página del PDF final
          posicion -N     → N páginas desde el final

        Las positivas se insertan en orden ascendente sobre el resultado
        creciente — así la posición es absoluta en el documento final.
        Las negativas se insertan al final sobre el resultado completo.
        El recorte a paginas_prueba ya ocurre en marcar() antes de llamar
        este método — aquí NO se recorta.
        """
        n_catalogo = len(paginas)  # páginas disponibles (ya recortadas si hay prueba)

        # ── Paso 1: clasificar carátulas ──────────────────────────────────────
        positivas = []  # (pos_final, paginas_pres, ruta)  — orden ascendente
        negativas = []  # (pos_negativa, paginas_pres, ruta)

        for pres in self.presentaciones:
            ruta = pres["path"]
            pos  = pres["posicion"]

            if not os.path.exists(ruta):
                self.logger.warning(f"⚠️  Presentación no encontrada: {ruta} — se omite.")
                continue
            try:
                paginas_pres = list(PdfReader(ruta).pages)
            except Exception as e:
                self.logger.warning(f"⚠️  Error al leer {os.path.basename(ruta)}: {e} — se omite.")
                continue

            if pos is False:
                self.logger.info(f"  ⏭️  {os.path.basename(ruta)} — desactivada, se omite.")
                continue

            if pos >= 1:
                if pos > n_catalogo:
                    self.logger.info(
                        f"  ⏭️  {os.path.basename(ruta)} — posición {pos} supera "
                        f"las {n_catalogo} págs. disponibles, se omite en esta corrida."
                    )
                    continue
                positivas.append((pos, paginas_pres, ruta))

            elif pos < 0:
                negativas.append((pos, paginas_pres, ruta))

        # ── Paso 2: insertar positivas en orden ascendente ────────────────────
        # Insertar de menor a mayor posición sobre el resultado creciente.
        # Cada inserción desplaza el índice siguiente en +1 por cada
        # portada ya insertada antes de ese punto.
        resultado = list(paginas)

        for pos, paginas_pres, ruta in sorted(positivas, key=lambda x: x[0]):
            # pos es absoluta en el documento final — insertar en idx=pos-1
            # del resultado creciente garantiza la posición exacta
            idx = pos - 1
            resultado = resultado[:idx] + paginas_pres + resultado[idx:]
            self.logger.info(
                f"  📎  {os.path.basename(ruta):<30} → página {idx + 1}"
            )

        # ── Paso 3: insertar negativas al final ───────────────────────────────
        total_actual = len(resultado)
        for pos, paginas_pres, ruta in sorted(negativas, key=lambda x: x[0]):
            # pos=-1 → última (idx=total), pos=-2 → penúltima, etc.
            idx = max(0, total_actual + pos + 1)
            resultado    = resultado[:idx] + paginas_pres + resultado[idx:]
            total_actual = len(resultado)
            pos_label = "última" if idx >= total_actual - 1 else f"página {idx + 1}"
            self.logger.info(
                f"  📎  {os.path.basename(ruta):<30} → {pos_label}"
            )

        return resultado

    # ── Carga de precios ──────────────────────────────────────────────────────

    def _cargar_precios(self):
        self.logger.info("📊 Cargando base de precios...")

        try:
            df = pd.read_excel(self.excel_path)
            df.columns = [str(c).strip() for c in df.columns]
        except FileNotFoundError:
            self.logger.error(f"❌ Excel no encontrado: {self.excel_path}")
            raise
        except Exception as e:
            self.logger.error(f"❌ Error al leer Excel: {e}")
            raise

        col_id     = "ID"
        col_precio = "precio_venta"

        if col_id not in df.columns or col_precio not in df.columns:
            self.logger.error(f"❌ Columnas requeridas no encontradas. Disponibles: {df.columns.tolist()}")
            raise ValueError(f"El Excel debe tener columnas '{col_id}' y '{col_precio}'")

        df[col_id]     = df[col_id].astype(str).str.strip()
        df[col_precio] = df[col_precio].astype(str).str.replace(r"[^\d.]", "", regex=True)
        df[col_precio] = pd.to_numeric(df[col_precio], errors="coerce").fillna(0.0)

        self.precios_dict   = pd.Series(df[col_precio].values, index=df[col_id]).to_dict()
        self.total_en_excel = len(self.precios_dict)
        self.ids_excel_keys = list(self.precios_dict.keys())

        self.logger.info(f"✅ {self.total_en_excel} registros cargados desde Excel")

    # ── Verificación Tesseract ────────────────────────────────────────────────

    def _verificar_tesseract(self):
        try:
            version = pytesseract.get_tesseract_version()
            self.logger.info(f"✅ Tesseract {version} detectado")
        except pytesseract.TesseractNotFoundError:
            self.logger.error("❌ Tesseract no encontrado. Instala con: sudo apt install tesseract-ocr tesseract-ocr-spa")
            raise

    # ── Preprocesado de imagen ────────────────────────────────────────────────

    def _mejorar_imagen(self, img: Image.Image) -> Image.Image:
        """
        Preprocesado estándar — pasada normal.
        Contraste + nitidez + mediana. Inversión si ocr_invertir está activo.
        """
        img = ImageEnhance.Contrast(img).enhance(self.contraste)
        img = ImageEnhance.Sharpness(img).enhance(self.nitidez)
        img = img.filter(ImageFilter.MedianFilter(size=3))
        if self.ocr_invertir:
            img = Image.eval(img, lambda px: 255 - px)
        return img

    def _mejorar_imagen_invertida(self, img: Image.Image) -> Image.Image:
        """
        Preprocesado optimizado — segunda pasada (doble pasada).
        Diseñado para IDs en fondo oscuro con texto claro.
        Solo contraste + inversión directa: la mediana y la nitidez
        destruyen los bordes del texto blanco sobre gris antes de invertir.
        Preprocesado fijo — no usa parámetros del config.
        """
        img = ImageEnhance.Contrast(img).enhance(2.5)
        img = Image.eval(img, lambda px: 255 - px)
        return img

    # ── OCR sobre una imagen preparada ───────────────────────────────────────

    def _ocr_tokens(self, img: Image.Image) -> dict:
        """
        Ejecuta Tesseract y retorna el dict de image_to_data.
        """
        return pytesseract.image_to_data(
            img,
            lang="spa",
            config=f"--oem 3 --psm {self.psm}",
            output_type=pytesseract.Output.DICT
        )

    # ── Fusión de resultados de doble pasada ─────────────────────────────────

    def _fusionar_tokens(self, data_normal: dict, data_invertido: dict) -> dict:
        """
        Combina los tokens de dos pasadas OCR.
        Estrategia: toma todos los tokens de la pasada normal y agrega
        los tokens de la pasada invertida que no tengan un token existente
        en una posición cercana (tolerancia: 20px). Esto evita duplicados
        cuando ambas pasadas leen el mismo ID correctamente.
        """
        TOLERANCIA_PX = 20

        # Construir lista base desde pasada normal
        n = len(data_normal["text"])
        tokens = {
            "text": list(data_normal["text"]),
            "conf": list(data_normal["conf"]),
            "left": list(data_normal["left"]),
            "top":  list(data_normal["top"]),
        }

        # Agregar tokens de pasada invertida si no hay solapamiento
        for j in range(len(data_invertido["text"])):
            t = data_invertido["text"][j]
            if not t.strip():
                continue
            x2 = data_invertido["left"][j]
            y2 = data_invertido["top"][j]

            # Buscar si ya existe un token cercano en la pasada normal
            duplicado = False
            for k in range(len(tokens["text"])):
                if abs(tokens["left"][k] - x2) < TOLERANCIA_PX and \
                   abs(tokens["top"][k]  - y2) < TOLERANCIA_PX:
                    duplicado = True
                    break

            if not duplicado:
                tokens["text"].append(t)
                tokens["conf"].append(data_invertido["conf"][j])
                tokens["left"].append(x2)
                tokens["top"].append(y2)

        return tokens

    # ── Fuzzy matching ────────────────────────────────────────────────────────

    def _buscar_id(self, id_detectado: str):
        """
        Busca el ID con tres estrategias en orden:
          1. Exacto
          2. Recorte por la derecha (token con texto adyacente fusionado)
          3. Fuzzy (solo si fuzzy_activo)

        Retorna (precio, tipo_match) donde tipo_match es:
          'exacto' | 'recorte' | 'fuzzy' | None
        """
        # 1. Exacto
        if id_detectado in self.precios_dict:
            return self.precios_dict[id_detectado], "exacto", None, None

        # 2. Recorte por la derecha
        if len(id_detectado) > self.id_len_max:
            for n in range(self.id_len_max, self.id_len_min - 1, -1):
                sufijo = id_detectado[-n:]
                if sufijo in self.precios_dict:
                    self.logger.debug(f"   ✂️  Recorte: '{id_detectado}' → '{sufijo}'")
                    return self.precios_dict[sufijo], "recorte", None, None

        # 3. Fuzzy
        if self.fuzzy_activo:
            resultado = process.extractOne(
                id_detectado,
                self.ids_excel_keys,
                scorer=fuzz.ratio,
                score_cutoff=self.fuzzy_umbral
            )
            if resultado:
                id_match, score, _ = resultado
                return self.precios_dict[id_match], "fuzzy", id_match, score

        return None, None, None, None

    # ── CSV de validación fuzzy ──────────────────────────────────────────────

    def _generar_csv_fuzzy(self, detalle: list) -> str:
        """
        Genera un CSV con los IDs recuperados por fuzzy matching para
        que el analista los verifique manualmente en LibreOffice Calc.
        El archivo queda pareado con el log: mismo nombre base + _fuzzy.csv
        """
        import csv
        log_handlers = [h for h in logging.getLogger().handlers if hasattr(h, 'baseFilename')]
        if log_handlers:
            log_base = os.path.splitext(log_handlers[0].baseFilename)[0]
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre    = os.path.splitext(os.path.basename(self.output_path))[0]
            log_base  = os.path.join(self.base_dir, "diagnosticos", f"{nombre}_{timestamp}")

        csv_path = log_base + "_fuzzy.csv"
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)

        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["pagina", "ocr_leyo", "excel_matcheo", "precio_insertado", "similitud_%"])
            for ocr, matcheo, precio, score, pagina in detalle:
                writer.writerow([pagina, ocr, matcheo, f"${precio:,.0f}", f"{score:.0f}"])

        return csv_path

    # ── Insertar logo en portada ──────────────────────────────────────────────

    def _capa_logo(self, w_pdf: float, h_pdf: float) -> BytesIO:
        """
        Genera una capa PDF con el logo para fusionar en la portada.
        La transparencia se aplica sobre el canal alpha de la imagen PIL
        antes de pasarla a ReportLab.
        """
        logo_img_pil = Image.open(self.logo_path).convert("RGBA")

        if self.logo_transparencia < 1.0:
            r, g, b, a = logo_img_pil.split()
            a = a.point(lambda px: int(px * self.logo_transparencia))
            logo_img_pil = Image.merge("RGBA", (r, g, b, a))

        logo_buffer = BytesIO()
        logo_img_pil.save(logo_buffer, format="PNG")
        logo_buffer.seek(0)

        packet = BytesIO()
        can = canvas.Canvas(packet, pagesize=(w_pdf, h_pdf))
        can.drawImage(
            ImageReader(logo_buffer),
            self.logo_x,
            self.logo_y,
            width=self.logo_ancho,
            height=self.logo_alto,
            mask="auto"
        )
        can.save()
        packet.seek(0)
        return packet

    # ── Proceso principal ─────────────────────────────────────────────────────

    def marcar(self):
        modo = "DOBLE PASADA" if self.ocr_doble_pasada else "PASADA ÚNICA"
        self.logger.info(f"🚀 Iniciando: {os.path.basename(self.pdf_path)}")
        self.logger.info(
            f"   DPI={self.dpi} | PSM={self.psm} | "
            f"Fuzzy={'ON' if self.fuzzy_activo else 'OFF'} ({self.fuzzy_umbral}%) | "
            f"IDs: {self.id_len_min}–{self.id_len_max} dígitos | "
            f"Grayscale={self.ocr_grayscale} | Invertir={self.ocr_invertir} | "
            f"Modo OCR={modo}"
        )
        self.logger.info(f"   📸  DPI            {self.dpi}")
        self.logger.info(f"   🔍  PSM            {self.psm}")

        try:
            reader_pdf = PdfReader(self.pdf_path)
        except FileNotFoundError:
            self.logger.error(f"❌ PDF no encontrado: {self.pdf_path}")
            raise
        except Exception as e:
            self.logger.error(f"❌ Error al abrir PDF: {e}")
            raise

        writer           = PdfWriter()
        total_paginas    = len(reader_pdf.pages)

        # Modo prueba
        if self.paginas_prueba is not False and self.paginas_prueba >= 1:
            total_paginas = min(self.paginas_prueba, total_paginas)
            self.logger.info(f"🧪 MODO PRUEBA — procesando solo {total_paginas} página(s)")

        total_etiquetado = 0
        ids_detectados   = set()
        fuzzy_matches    = 0
        recorte_matches  = 0  # IDs recuperados por recorte por la derecha
        fuzzy_detalle    = []  # (ocr_leyo, excel_matcheo, precio, similitud)

        ancho_barra = 28
        for i in range(total_paginas):
            pct     = (i + 1) / total_paginas
            bloques = int(pct * ancho_barra)
            barra_p = "█" * bloques + "░" * (ancho_barra - bloques)
            print(f"  [{barra_p}] pág {i+1}/{total_paginas}", end="\r", flush=True)

            images = None
            img_base = None

            try:
                images = convert_from_path(
                    self.pdf_path,
                    first_page=i + 1,
                    last_page=i + 1,
                    dpi=self.dpi,
                    grayscale=self.ocr_grayscale
                )

                img_base = images[0].convert("L")

                # ── Pasada normal ──────────────────────────────────────────
                img_normal  = self._mejorar_imagen(img_base.copy())
                data_normal = self._ocr_tokens(img_normal)

                # ── Pasada invertida (preprocesado suave para fondo oscuro) ──
                if self.ocr_doble_pasada:
                    img_inv  = self._mejorar_imagen_invertida(img_base.copy())
                    data_inv = self._ocr_tokens(img_inv)
                    data     = self._fusionar_tokens(data_normal, data_inv)
                else:
                    data = data_normal

                p_orig       = reader_pdf.pages[i]
                w_pdf, h_pdf = float(p_orig.mediabox.width), float(p_orig.mediabox.height)
                w_img, h_img = img_normal.size
                scale_x      = w_pdf / w_img
                scale_y      = h_pdf / h_img

                packet = BytesIO()
                can    = canvas.Canvas(packet, pagesize=(w_pdf, h_pdf))
                can.setFont(self.etiqueta_font, self.etiqueta_font_size)
                can.setFillColorRGB(*self.etiqueta_color)

                # IDs detectados en esta página antes de procesar
                ids_pagina_antes = len(ids_detectados)

                for j in range(len(data["text"])):
                    texto = data["text"][j]
                    if not texto.strip():
                        continue

                    id_detectado = re.sub(r"\D", "", texto)

                    # Permitir hasta el doble del máximo para que tokens con
                    # texto adyacente fusionado lleguen a _buscar_id y sean
                    # recuperados por recorte por la derecha.
                    if len(id_detectado) < self.id_len_min:
                        continue
                    if len(id_detectado) > self.id_len_max * 2:
                        continue

                    precio, tipo_match, id_match, score = self._buscar_id(id_detectado)

                    if precio and precio > 0:
                        x_pdf = (data["left"][j] * scale_x) + self.etiqueta_offset_x
                        y_pdf = h_pdf - (data["top"][j] * scale_y) + self.etiqueta_offset_y

                        can.drawString(x_pdf, y_pdf, f"${precio:,.0f}")
                        total_etiquetado += 1
                        ids_detectados.add(id_detectado)
                        if tipo_match == "fuzzy":
                            fuzzy_matches += 1
                            fuzzy_detalle.append((id_detectado, id_match, precio, score, i + 1))
                        elif tipo_match == "recorte":
                            recorte_matches += 1

                can.save()
                packet.seek(0)

                if packet.getbuffer().nbytes > 0:
                    p_orig.merge_page(PdfReader(packet).pages[0])

                # Logo en portada
                if i == 0 and self.logo_activo and self.logo_path and os.path.exists(self.logo_path):
                    capa_logo = self._capa_logo(w_pdf, h_pdf)
                    p_orig.merge_page(PdfReader(capa_logo).pages[0])

                writer.add_page(p_orig)

            except pytesseract.TesseractNotFoundError:
                self.logger.error("❌ Tesseract no encontrado.")
                raise
            except Exception as e:
                self.logger.error(f"\n❌ Error en página {i+1}: {e}")
                writer.add_page(reader_pdf.pages[i])

            finally:
                del images
                del img_base
                gc.collect()

        print(" " * 60, end="\r")

        # ── Insertar páginas de presentación ─────────────────────────────────────
        if self.presentaciones:
            self.logger.info("📎 Insertando páginas de presentación...")
            total_real_pdf   = len(reader_pdf.pages)
            paginas_catalogo = list(writer.pages)
            paginas_final    = self._insertar_presentaciones(
                                   paginas_catalogo, total_real_pdf)
            writer_final = PdfWriter()
            for p in paginas_final:
                writer_final.add_page(p)
            writer = writer_final

        # Guardar PDF
        self.logger.info("💾 Guardando PDF final...")
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)

        try:
            with open(self.output_path, "wb") as f:
                writer.write(f)
        except Exception as e:
            self.logger.error(f"❌ Error al guardar PDF: {e}")
            raise

        # ── Normalizar PDF — compatibilidad universal ──────────────────────────────
        self._normalizar_pdf(self.output_path)

        # ── Reporte final ─────────────────────────────────────────────────────
        ids_unicos    = len(ids_detectados)
        ids_falta     = max(0, self.total_en_excel - ids_unicos)
        tasa          = (ids_unicos / self.total_en_excel * 100) if self.total_en_excel > 0 else 0.0
        bloques       = int(tasa / 5)
        barra         = "█" * bloques + "░" * (20 - bloques)
        semaforo_key  = "VERDE" if tasa >= 85 else ("AMARILLO" if tasa >= 65 else "ROJO")
        prueba_activa = self.paginas_prueba is not False and self.paginas_prueba >= 1

        SEP  = "─" * 54
        SEP2 = "═" * 54

        self.logger.info("")
        self.logger.info(SEP2)
        self.logger.info("  ✅  PROCESO TERMINADO")
        self.logger.info(SEP)
        self.logger.info(f"  📄  Páginas          {total_paginas}")
        self.logger.info(f"  📋  En Excel         {self.total_en_excel}")
        self.logger.info(f"  🔢  IDs marcados     {ids_unicos} / {self.total_en_excel}  (faltan {ids_falta})")
        self.logger.info(f"  🏷️   Etiquetas        {total_etiquetado}")
        if recorte_matches:
            self.logger.info(f"  ✂️   Recortes auto    {recorte_matches}")
        if fuzzy_matches:
            self.logger.info(f"  ·   Fuzzy            {fuzzy_matches} IDs recuperados")
        if self.ocr_doble_pasada:
            self.logger.info(f"  🔄  Doble pasada     activa")
        if self.presentaciones:
            posiciones = ", ".join(
                str(p["posicion"]) if p["posicion"] != -1 else "última"
                for p in self.presentaciones
            )
            self.logger.info(f"  📎  Portadas         insertadas en pág. {posiciones}")
        self.logger.info(SEP)
        self.logger.info(f"  📊  [{barra}]  {tasa:.1f}%")
        self.logger.info("")

        # ── Semáforo o aviso de prueba ──
        if prueba_activa:
            self.logger.info(f"  🧪  MODO PRUEBA — {total_paginas} páginas procesadas")
            self.logger.info(f"      Esta efectividad no es el semáforo real del catálogo.")
            self.logger.info(f"      Abre el PDF en salidas/ y revisa visualmente:")
            self.logger.info(f"      · ¿Los precios aparecen junto a los productos?")
            self.logger.info(f"      · ¿El logo y las portadas quedan bien posicionados?")
            self.logger.info(f"      Cuando estés lista → cambia paginas_prueba: false")
            self.logger.info(f"      y ejecuta el catálogo completo.")
        elif tasa >= 85:
            self.logger.info(f"  🟢  VERDE — listo para publicar")
            self.logger.info(f"      Abre el PDF en salidas/ y revisa visualmente.")
            self.logger.info(f"      Si todo se ve bien, continúa con la Fase 3 del checklist.")
            if fuzzy_matches:
                self.logger.info(f"      ⚠️  Hay {fuzzy_matches} IDs por fuzzy — revisa el CSV antes de publicar.")
        elif tasa >= 65:
            self.logger.info(f"  🟡  AMARILLO — revisar antes de publicar")
            self.logger.info(f"      python3 scripts/diagnostico.py")
        else:
            self.logger.info(f"  🔴  ROJO — no publicar")
            self.logger.info(f"      python3 scripts/diagnostico.py")

        self.logger.info(SEP)
        self.logger.info(f"  📂  {os.path.basename(self.output_path)}")

        # ── CSV fuzzy — solo si hubo matches ────────────────────────────────
        if fuzzy_detalle:
            csv_path = self._generar_csv_fuzzy(fuzzy_detalle)
            self.logger.info(f"  📋  Fuzzy CSV        {os.path.basename(csv_path)}")
            self.logger.info(f"      Abre ese archivo en LibreOffice Calc y verifica")
            self.logger.info(f"      que cada precio corresponda al producto correcto.")

        self.logger.info(SEP2)
        self.logger.info("")

        # Métricas parseables por diagnostico.py — no modificar formato
        self.logger.info(f"[STAT] paginas={total_paginas}")
        self.logger.info(f"[STAT] total_excel={self.total_en_excel}")
        self.logger.info(f"[STAT] ids_unicos={ids_unicos}")
        self.logger.info(f"[STAT] etiquetas={total_etiquetado}")
        self.logger.info(f"[STAT] fuzzy_matches={fuzzy_matches}")
        self.logger.info(f"[STAT] recorte_matches={recorte_matches}")
        self.logger.info(f"[STAT] doble_pasada={self.ocr_doble_pasada}")
        self.logger.info(f"[STAT] paginas_prueba={self.paginas_prueba}")
        self.logger.info(f"[STAT] tasa={tasa:.2f}")
        self.logger.info(f"[STAT] semaforo={semaforo_key}")


# ─────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────

if __name__ == "__main__":
    args = parse_args()
    BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    config_path = os.path.join(BASE, args.config)
    if not os.path.exists(config_path):
        print(f"❌ Archivo de configuración no encontrado: {config_path}")
        sys.exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    nombre_catalogo = os.path.splitext(os.path.basename(config_path))[0]
    log_path = setup_logging(BASE, nombre_catalogo)
    logger   = logging.getLogger(__name__)
    logger.info(f"📁 Config cargada: {args.config}")
    logger.info(f"📝 Log guardado en: {log_path}")

    try:
        app = EtiquetadorCatalogo(config, BASE)
        app.marcar()
    except KeyboardInterrupt:
        logger.warning("\n⚠️  Proceso interrumpido por el usuario")
    except Exception as e:
        logger.error(f"🔥 Error crítico: {e}", exc_info=True)
        sys.exit(1)
