#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Etiquetador Automático de Catálogos con Tesseract OCR
Compatible con CPUs antiguos (Intel Ivy Bridge 2012+)
"""

import os
import pandas as pd
import numpy as np
from pdf2image import convert_from_path
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from io import BytesIO
import re
import gc
import pytesseract
from PIL import Image, ImageEnhance
import logging

# ============================================
# Configuración de Logging
# ============================================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('procesamiento.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class MarcadorJeansDerecha:
    """
    Procesa catálogos PDF insertando precios desde Excel usando OCR
    """
    
    def __init__(self, pdf_path, excel_path):
        self.pdf_path = pdf_path
        
        logger.info("📊 Cargando y limpiando base de datos...")
        
        # Cargar Excel
        try:
            df = pd.read_excel(excel_path)
            df.columns = [str(c).strip() for c in df.columns]
        except FileNotFoundError:
            logger.error(f"❌ Archivo Excel no encontrado: {excel_path}")
            raise
        except Exception as e:
            logger.error(f"❌ Error al leer Excel: {e}")
            raise
        
        self.col_id = 'ID'
        self.col_precio = 'precio_venta'
        
        # Validar columnas
        if self.col_id not in df.columns or self.col_precio not in df.columns:
            logger.error(f"❌ Columnas requeridas no encontradas. Disponibles: {df.columns.tolist()}")
            raise ValueError(f"El Excel debe tener columnas '{self.col_id}' y '{self.col_precio}'")
        
        # Sanitización de datos
        df[self.col_id] = df[self.col_id].astype(str).str.strip()
        df[self.col_precio] = df[self.col_precio].astype(str).str.replace(r'[^\d.]', '', regex=True)
        df[self.col_precio] = pd.to_numeric(df[self.col_precio], errors='coerce').fillna(0.0)
        
        self.precios_dict = pd.Series(df[self.col_precio].values, index=df[self.col_id]).to_dict()
        
        logger.info(f"✅ Cargados {len(self.precios_dict)} precios desde la base de datos")
        logger.info("🧠 Motor OCR: Tesseract")
        
        # Verificar que Tesseract esté instalado
        try:
            version = pytesseract.get_tesseract_version()
            logger.info(f"✅ Tesseract version: {version}")
        except pytesseract.TesseractNotFoundError:
            logger.error("❌ Tesseract no encontrado. Instala con: sudo apt install tesseract-ocr tesseract-ocr-spa")
            raise

    def _mejorar_imagen(self, img):
        """
        Preprocesa la imagen para mejorar precisión del OCR
        """

        from PIL import ImageFilter
    
        # Aumentar contraste MÁS agresivo
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.5)  # Era 2.0, ahora 2.5
    
        # Aumentar nitidez
        enhancer = ImageEnhance.Sharpness(img)
        img = enhancer.enhance(2.0)  # Era 1.5, ahora 2.0
    
        # Aplicar filtro para reducir ruido
        img = img.filter(ImageFilter.MedianFilter(size=3))
    
        return img

    def marcar(self, output_path):
        """
        Procesa el PDF completo insertando precios
        """
        logger.info(f"🚀 Iniciando procesamiento: {os.path.basename(self.pdf_path)}")
        
        try:
            reader_pdf = PdfReader(self.pdf_path)
        except FileNotFoundError:
            logger.error(f"❌ PDF no encontrado: {self.pdf_path}")
            raise
        except Exception as e:
            logger.error(f"❌ Error al abrir PDF: {e}")
            raise
        
        writer = PdfWriter()
        total_paginas = len(reader_pdf.pages)
        total_encontrados = 0
        ids_detectados = set()

        for i in range(total_paginas):
            # Mostrar progreso sin salto de línea
            print(f"⚡ Procesando página {i+1}/{total_paginas}...", end='\r', flush=True)
            
            try:
                # Convertir página a imagen
                images = convert_from_path(
                    self.pdf_path, 
                    first_page=i+1, 
                    last_page=i+1, 
                    dpi=200,
                    grayscale=True
                )
                img = images[0]
                
                # Mejorar imagen para OCR
                img = self._mejorar_imagen(img)
                
                # Configuración optimizada de Tesseract
                custom_config = r'--oem 3 --psm 6'
                
                # Ejecutar OCR
                data = pytesseract.image_to_data(
                    img, 
                    lang='spa', 
                    config=custom_config,
                    output_type=pytesseract.Output.DICT
                )
                
                # Obtener dimensiones
                p_orig = reader_pdf.pages[i]
                w_pdf, h_pdf = float(p_orig.mediabox.width), float(p_orig.mediabox.height)
                w_img, h_img = img.size
                
                # Crear capa de texto
                packet = BytesIO()
                can = canvas.Canvas(packet, pagesize=(w_pdf, h_pdf))
                can.setFont("Helvetica-Bold", 11)
                can.setFillColorRGB(0.0, 0.0, 1.0)  # Azul fuerte
                
                # Procesar cada texto detectado
                n_boxes = len(data['text'])
                for j in range(n_boxes):
                    text = data['text'][j]
                    
                    # Procesar todo el texto detectado
                    if text.strip():
                        # Extraer solo dígitos
                        id_detectado = re.sub(r'\D', '', text)
                        
                        # Validar ID en base de datos
                        if id_detectado in self.precios_dict and len(id_detectado) >= 4:
                            # Coordenadas del texto detectado
                            x_img = data['left'][j]  # Encima del texto
                            y_img = data['top'][j]  # Base del texto
                            
                            # Conversión de coordenadas imagen → PDF
                            x_pdf = (x_img * (w_pdf / w_img)) + 4  # +4px de separación
                            y_pdf = h_pdf - (y_img * (h_pdf / h_img)) + 5.67  # +0.2 cm (5.67 puntos) encima del ID
                            
                            precio_float = self.precios_dict[id_detectado]
                            
                            if precio_float > 0:
                                can.drawString(x_pdf, y_pdf, f"${precio_float:,.2f}")
                                total_encontrados += 1
                                ids_detectados.add(id_detectado)

                can.save()
                packet.seek(0)
                
                # Fusionar capa de texto con página original
                if packet.getbuffer().nbytes > 0:
                    p_orig.merge_page(PdfReader(packet).pages[0])
                
                writer.add_page(p_orig)
                
            except pytesseract.TesseractNotFoundError:
                logger.error("❌ Tesseract no encontrado. Instala con: sudo apt install tesseract-ocr")
                raise
            except Exception as e:
                logger.error(f"\n❌ Error en página {i+1}: {str(e)}")
                writer.add_page(reader_pdf.pages[i])

            # Limpieza de memoria
            if 'images' in locals(): 
                del images
            if 'img' in locals(): 
                del img
            gc.collect()

        # Limpiar línea de progreso
        print(" " * 80, end='\r')
        
        # Guardar PDF resultante
        logger.info("💾 Guardando archivo final...")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        try:
            with open(output_path, "wb") as f:
                writer.write(f)
        except Exception as e:
            logger.error(f"❌ Error al guardar PDF: {e}")
            raise
        
        # Reporte final
        logger.info("=" * 60)
        logger.info("✅ ¡PROCESO TERMINADO!")
        logger.info(f"🏷️  Etiquetas insertadas: {total_encontrados}")
        logger.info(f"🔢 IDs únicos procesados: {len(ids_detectados)}")
        logger.info(f"📄 Páginas procesadas: {total_paginas}")
        logger.info(f"📂 Archivo generado: {output_path}")
        logger.info("=" * 60)


if __name__ == "__main__":
    # Configuración de rutas
    BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    PDF_INPUT = os.path.join(BASE, "libros", "jeans_PV26.pdf")
    EXCEL_INPUT = os.path.join(BASE, "precios", "lista_jeans.xlsx")
    PDF_OUTPUT = os.path.join(BASE, "salida", "jeans_26_final.pdf")
    
    try:
        app = MarcadorJeansDerecha(PDF_INPUT, EXCEL_INPUT)
        app.marcar(PDF_OUTPUT)
    except KeyboardInterrupt:
        logger.warning("\n⚠️  Proceso interrumpido por el usuario")
    except Exception as e:
        logger.error(f"🔥 Error crítico: {e}", exc_info=True)
        exit(1)

