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
        self.pdf_path   = os.path.join(base_dir, config["pdf_input"])
        self.excel_path = os.path.join(base_dir, config["excel_input"])
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

        # Parámetros fuzzy matching
        self.fuzzy_activo   = config.get("fuzzy_activo", True)
        self.fuzzy_umbral   = config.get("fuzzy_umbral", 85)

        # Parámetros etiqueta
        self.etiqueta_font_size  = config.get("etiqueta_font_size", 11)
        self.etiqueta_color      = config.get("etiqueta_color_rgb", [0.0, 0.0, 1.0])
        self.etiqueta_offset_x   = config.get("etiqueta_offset_x_pt", 4.0)
        self.etiqueta_offset_y   = config.get("etiqueta_offset_y_pt", 5.67)

        # Parámetros logo
        self.logo_activo        = config.get("logo_activo", False)
        self.logo_path          = os.path.join(base_dir, config.get("logo_path", "")) if config.get("logo_path") else None
        self.logo_x             = config.get("logo_x_pt", 20.0)
        self.logo_y             = config.get("logo_y_pt", 20.0)
        self.logo_ancho         = config.get("logo_ancho_pt", 80.0)
        self.logo_alto          = config.get("logo_alto_pt", 40.0)
        self.logo_transparencia = config.get("logo_transparencia", 1.0)  # 1.0 = opaco, 0.0 = invisible

        self._cargar_precios()
        self._verificar_tesseract()

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

        self.precios_dict  = pd.Series(df[col_precio].values, index=df[col_id]).to_dict()
        self.total_en_excel = len(self.precios_dict)
        self.ids_excel_keys = list(self.precios_dict.keys())  # Para fuzzy matching

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
        img = ImageEnhance.Contrast(img).enhance(self.contraste)
        img = ImageEnhance.Sharpness(img).enhance(self.nitidez)
        img = img.filter(ImageFilter.MedianFilter(size=3))
        return img

    # ── Fuzzy matching ────────────────────────────────────────────────────────

    def _buscar_id(self, id_detectado: str):
        """
        Busca el ID en el diccionario de precios.
        - Primero intenta matching exacto (rápido).
        - Si falla y fuzzy está activo, busca la coincidencia más cercana.
        Retorna (precio, es_fuzzy) o (None, False) si no encuentra.
        """
        # Matching exacto
        if id_detectado in self.precios_dict:
            return self.precios_dict[id_detectado], False

        # Fuzzy matching
        if self.fuzzy_activo:
            resultado = process.extractOne(
                id_detectado,
                self.ids_excel_keys,
                scorer=fuzz.ratio,
                score_cutoff=self.fuzzy_umbral
            )
            if resultado:
                id_match, score, _ = resultado
                return self.precios_dict[id_match], True

        return None, False

    # ── Insertar logo en portada ──────────────────────────────────────────────

    def _capa_logo(self, w_pdf: float, h_pdf: float) -> BytesIO:
        """
        Genera una capa PDF con el logo para fusionar en la portada.
        """
        packet = BytesIO()
        can = canvas.Canvas(packet, pagesize=(w_pdf, h_pdf))
        can.saveState()
        can.setFillAlpha(self.logo_transparencia)

        logo_img = ImageReader(self.logo_path)
        can.drawImage(
            logo_img,
            self.logo_x,
            self.logo_y,
            width=self.logo_ancho,
            height=self.logo_alto,
            mask="auto"
        )

        can.restoreState()
        can.save()
        packet.seek(0)
        return packet

    # ── Proceso principal ─────────────────────────────────────────────────────

    def marcar(self):
        self.logger.info(f"🚀 Iniciando: {os.path.basename(self.pdf_path)}")
        self.logger.info(f"   DPI={self.dpi} | PSM={self.psm} | Fuzzy={'ON' if self.fuzzy_activo else 'OFF'} ({self.fuzzy_umbral}%) | IDs: {self.id_len_min}–{self.id_len_max} dígitos | Grayscale={self.ocr_grayscale} | Invertir={self.ocr_invertir}")

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
        total_etiquetado = 0
        ids_detectados   = set()
        fuzzy_matches    = 0

        for i in range(total_paginas):
            print(f"⚡ Procesando página {i+1}/{total_paginas}...", end="\r", flush=True)

            try:
                images = convert_from_path(
                    self.pdf_path,
                    first_page=i + 1,
                    last_page=i + 1,
                    dpi=self.dpi,
                    grayscale=self.ocr_grayscale
                )
                img = self._mejorar_imagen(images[0].convert("L"))

                data = pytesseract.image_to_data(
                    img,
                    lang="spa",
                    config=f"--oem 3 --psm {self.psm}",
                    output_type=pytesseract.Output.DICT
                )

                p_orig           = reader_pdf.pages[i]
                w_pdf, h_pdf     = float(p_orig.mediabox.width), float(p_orig.mediabox.height)
                w_img, h_img     = img.size
                scale_x          = w_pdf / w_img
                scale_y          = h_pdf / h_img

                packet = BytesIO()
                can    = canvas.Canvas(packet, pagesize=(w_pdf, h_pdf))
                can.setFont("Helvetica-Bold", self.etiqueta_font_size)
                can.setFillColorRGB(*self.etiqueta_color)

                for j in range(len(data["text"])):
                    texto = data["text"][j]
                    if not texto.strip():
                        continue

                    id_detectado = re.sub(r"\D", "", texto)

                    if not (self.id_len_min <= len(id_detectado) <= self.id_len_max):
                        continue

                    precio, es_fuzzy = self._buscar_id(id_detectado)

                    if precio and precio > 0:
                        x_pdf = (data["left"][j] * scale_x) + self.etiqueta_offset_x
                        y_pdf = h_pdf - (data["top"][j] * scale_y) + self.etiqueta_offset_y

                        can.drawString(x_pdf, y_pdf, f"${precio:,.2f}")
                        total_etiquetado += 1
                        ids_detectados.add(id_detectado)
                        if es_fuzzy:
                            fuzzy_matches += 1

                can.save()
                packet.seek(0)

                # Fusionar etiquetas
                if packet.getbuffer().nbytes > 0:
                    p_orig.merge_page(PdfReader(packet).pages[0])

                # Insertar logo en portada
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

            # Liberar memoria
            if "images" in locals():
                del images
            if "img" in locals():
                del img
            gc.collect()

        print(" " * 80, end="\r")

        # Guardar PDF
        self.logger.info("💾 Guardando PDF final...")
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)

        try:
            with open(self.output_path, "wb") as f:
                writer.write(f)
        except Exception as e:
            self.logger.error(f"❌ Error al guardar PDF: {e}")
            raise

        # ── Reporte final con semáforo ────────────────────────────────────────
        ids_unicos     = len(ids_detectados)
        tasa           = (ids_unicos / self.total_en_excel * 100) if self.total_en_excel > 0 else 0.0

        if tasa >= 85:
            semaforo = "🟢 VERDE"
            accion   = "Resultado óptimo. Puedes publicar en WhatsApp Business."
        elif tasa >= 65:
            semaforo = "🟡 AMARILLO"
            accion   = "Resultado aceptable pero revisar. Ejecuta diagnostico.py antes de publicar."
        else:
            semaforo = "🔴 ROJO"
            accion   = "Efectividad baja. No publicar. Ejecuta diagnostico.py y contacta al coach."

        self.logger.info("=" * 60)
        self.logger.info("✅ PROCESO TERMINADO")
        self.logger.info(f"📄 Páginas procesadas  : {total_paginas}")
        self.logger.info(f"📋 Registros en Excel  : {self.total_en_excel}")
        self.logger.info(f"🔢 IDs únicos marcados : {ids_unicos}")
        self.logger.info(f"🏷️  Etiquetas insertadas: {total_etiquetado}")
        self.logger.info(f"🔍 Fuzzy matches        : {fuzzy_matches}")
        self.logger.info(f"📊 Efectividad          : {tasa:.1f}%")
        self.logger.info(f"   {semaforo}")
        self.logger.info(f"   → {accion}")
        self.logger.info(f"📂 Archivo generado     : {self.output_path}")
        self.logger.info("=" * 60)


# ─────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────

if __name__ == "__main__":
    args    = parse_args()
    BASE    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Cargar configuración
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
