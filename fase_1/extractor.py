#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extractor.py — Fase 1: Extracción de lista de precios desde PDF de proveedor
Boutique Zepeda · books-label

Uso:
    python3 scripts/extractor.py --config configs/fase1/config_ella_spring26.json

Dependencias Python (requirements.txt):
    pdfplumber, pandas, openpyxl, odfpy
"""

import argparse
import json
import logging
import os
import re
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import pdfplumber


# ─────────────────────────────────────────────
#  Argumentos de entrada
# ─────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(
        description="Extractor Fase 1 — books-label · Boutique Zepeda"
    )
    parser.add_argument(
        "--config",
        required=True,
        help="Ruta al archivo de configuración JSON (ej: configs/fase1/config_ella_spring26.json)"
    )
    return parser.parse_args()


# ─────────────────────────────────────────────
#  Logging
# ─────────────────────────────────────────────

def setup_logging(base_dir: str, nombre_config: str) -> str:
    timestamp    = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"{nombre_config}_{timestamp}.log"
    log_path     = os.path.join(base_dir, "diagnosticos", log_filename)
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

class ExtractorLista:
    """
    Extrae ID y precio sugerido desde el PDF crudo de un proveedor.
    Todos los parámetros ajustables vienen del archivo de configuración JSON.
    Salida: Excel con columnas id, precio, pag (si está configurada), len.
    """

    def __init__(self, config: dict, base_dir: str):
        self.config   = config
        self.base_dir = base_dir
        self.logger   = logging.getLogger(__name__)

        # Rutas
        self.pdf_path    = os.path.join(base_dir, config["pdf_input"])
        self.excel_output = os.path.join(base_dir, config["excel_output"])

        # Encoding — offset de desplazamiento ASCII del PDF
        # Price Shoes usa 29. PDFs sin encoding roto usan 0.
        self.encoding_offset = config.get("encoding_offset", 0)

        # Nombres de columnas en el PDF (tal como aparecen en el encabezado)
        self.col_id     = config.get("col_id",     "ID")
        self.col_precio = config.get("col_precio",  "Precio")
        self.col_pag    = config.get("col_pag",     None)   # None = no extraer

        # Tolerancia en puntos para asignar palabras a su columna
        self.tolerancia_x = config.get("tolerancia_x", 20.0)

        # Modo prueba
        paginas_prueba_raw  = config.get("paginas_prueba", False)
        self.paginas_prueba = False if paginas_prueba_raw is False else int(paginas_prueba_raw)

    # ── Decodificador de encoding propietario ─────────────────────────────────

    def _decode_cid(self, texto: str) -> str:
        """Reemplaza secuencias (cid:N) por el carácter Unicode correspondiente."""
        return re.sub(r'\(cid:(\d+)\)', lambda m: chr(int(m.group(1))), texto)

    def _decode_offset(self, texto: str) -> str:
        """Aplica desplazamiento ASCII fijo. offset=0 devuelve el texto sin cambios."""
        if self.encoding_offset == 0:
            return texto
        resultado = []
        for c in texto:
            code = ord(c)
            if 32 < code < 127:
                nuevo = code + self.encoding_offset
                resultado.append(chr(nuevo) if 32 <= nuevo < 127 else c)
            else:
                resultado.append(c)
        return ''.join(resultado)

    def decodificar(self, texto: str) -> str:
        if not texto:
            return ''
        return self._decode_offset(self._decode_cid(texto))

    # ── Reconstrucción espacial de tabla ──────────────────────────────────────

    def _agrupar_filas(self, palabras: list, tolerancia_y: float = 3.0) -> list:
        """Agrupa palabras en filas por proximidad vertical."""
        if not palabras:
            return []
        filas      = []
        fila_actual = [palabras[0]]
        y_actual    = palabras[0]['top']

        for palabra in palabras[1:]:
            if abs(palabra['top'] - y_actual) <= tolerancia_y:
                fila_actual.append(palabra)
            else:
                filas.append(sorted(fila_actual, key=lambda w: w['x0']))
                fila_actual = [palabra]
                y_actual    = palabra['top']

        filas.append(sorted(fila_actual, key=lambda w: w['x0']))
        return filas

    def _detectar_mapa_columnas(self, filas: list) -> dict | None:
        """
        Busca la fila de encabezado y retorna {campo: x0} para cada columna configurada.
        Retorna None si no se encuentra el encabezado.
        """
        columnas_buscar = {
            "id":     self.col_id,
            "precio": self.col_precio,
        }
        if self.col_pag:
            columnas_buscar["pag"] = self.col_pag

        for fila in filas:
            textos = {self.decodificar(w['text']): w['x0'] for w in fila}
            fila_str = ' '.join(textos.keys())

            if self.col_id in fila_str:
                mapa = {}
                for campo, nombre_col in columnas_buscar.items():
                    for texto, x0 in textos.items():
                        if nombre_col.lower() in texto.lower():
                            mapa[campo] = x0
                            break
                if "id" in mapa and "precio" in mapa:
                    return mapa

        return None

    def _celda_mas_cercana(self, fila: list, x0_objetivo: float) -> str:
        """Devuelve el texto decodificado de la palabra más cercana a x0_objetivo."""
        candidatos = [
            w for w in fila
            if abs(w['x0'] - x0_objetivo) <= self.tolerancia_x
        ]
        if not candidatos:
            return ''
        mejor = min(candidatos, key=lambda w: abs(w['x0'] - x0_objetivo))
        return self.decodificar(mejor['text'])

    # ── Líneas a saltar ───────────────────────────────────────────────────────

    _SKIP_PATTERNS = [
        'PRECIOS SUJETOS', 'Estimado Socio', 'Lista de Precios',
        'Listas Vigentes', 'SUCURSAL', 'TELEMARKETING'
    ]

    def _es_fila_datos(self, fila: list) -> bool:
        """True si la fila contiene datos de producto (no es encabezado ni pie)."""
        texto = ' '.join(self.decodificar(w['text']) for w in fila)
        if not texto.strip():
            return False
        for patron in self._SKIP_PATTERNS:
            if patron in texto:
                return False
        return True

    # ── Extracción ────────────────────────────────────────────────────────────

    def extraer(self) -> pd.DataFrame:
        if not os.path.exists(self.pdf_path):
            self.logger.error(f"❌ PDF no encontrado: {self.pdf_path}")
            sys.exit(1)

        mapa_columnas  = None
        todos_registros = []

        with pdfplumber.open(self.pdf_path) as pdf:
            paginas = pdf.pages
            if self.paginas_prueba:
                paginas = paginas[:self.paginas_prueba]
                self.logger.info(f"🧪 MODO PRUEBA — {self.paginas_prueba} páginas")

            total = len(paginas)
            for i, page in enumerate(paginas):
                print(f"  Procesando página {i+1}/{total}", end="\r", flush=True)

                palabras_raw = page.extract_words()
                filas        = self._agrupar_filas(palabras_raw)

                # Detectar encabezado (puede aparecer en cada página)
                mapa_pagina = self._detectar_mapa_columnas(filas)
                if mapa_pagina:
                    mapa_columnas = mapa_pagina
                    self.logger.info(f"  ✅ Header en pág {i+1}: {mapa_columnas}")

                if not mapa_columnas:
                    continue

                registros_pagina = 0
                for fila in filas:
                    if not self._es_fila_datos(fila):
                        continue

                    id_val = self._celda_mas_cercana(fila, mapa_columnas["id"])
                    if not id_val.strip():
                        continue

                    precio_val = self._celda_mas_cercana(fila, mapa_columnas["precio"])

                    registro = {"id": id_val.strip(), "precio": precio_val.strip()}

                    if "pag" in mapa_columnas:
                        registro["pag"] = self._celda_mas_cercana(fila, mapa_columnas["pag"])

                    todos_registros.append(registro)
                    registros_pagina += 1

                self.logger.info(f"  Página {i+1}: {registros_pagina} registros")

        print(" " * 50, end="\r")

        if not todos_registros:
            self.logger.warning("⚠️  No se extrajeron registros. Revisa col_id, col_precio y encoding_offset.")
            sys.exit(1)

        df = pd.DataFrame(todos_registros)

        # Limpiar precio → float
        df['precio'] = (
            df['precio']
            .str.replace(r'[\$,\s]', '', regex=True)
            .pipe(pd.to_numeric, errors='coerce')
        )

        # Columna de auditoría: longitud del ID
        df['len'] = df['id'].str.len()

        return df

    # ── Exportación ───────────────────────────────────────────────────────────

    def exportar(self, df: pd.DataFrame):
        Path(self.excel_output).parent.mkdir(parents=True, exist_ok=True)

        # Orden de columnas
        cols = [c for c in ['pag', 'id', 'precio', 'len'] if c in df.columns]
        df   = df[cols]

        engine = 'odf' if self.excel_output.endswith('.ods') else 'openpyxl'
        df.to_excel(self.excel_output, index=False, engine=engine)

        SEP  = "─" * 50
        SEP2 = "═" * 50
        sin_precio = df['precio'].isna().sum()
        longitudes = sorted(df['len'].unique().tolist())

        self.logger.info("")
        self.logger.info(SEP2)
        self.logger.info("  ✅  EXTRACCIÓN TERMINADA")
        self.logger.info(SEP)
        self.logger.info(f"  📋  Total registros : {len(df)}")
        self.logger.info(f"  🔑  IDs únicos      : {df['id'].nunique()}")
        self.logger.info(f"  ⚠️   Sin precio       : {sin_precio}")
        self.logger.info(f"  📏  Longitudes de ID : {longitudes}")
        self.logger.info(SEP)
        self.logger.info(f"  📂  {self.excel_output}")
        self.logger.info(SEP2)

        # Métricas parseables
        self.logger.info(f"[STAT] total={len(df)}")
        self.logger.info(f"[STAT] ids_unicos={df['id'].nunique()}")
        self.logger.info(f"[STAT] sin_precio={sin_precio}")
        self.logger.info(f"[STAT] longitudes={longitudes}")
        self.logger.info(f"[STAT] paginas_prueba={self.paginas_prueba}")


# ─────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────

if __name__ == "__main__":
    args = parse_args()
    BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    config_path = os.path.join(BASE, args.config)
    if not os.path.exists(config_path):
        print(f"❌ Config no encontrado: {config_path}")
        sys.exit(1)

    with open(config_path, encoding="utf-8") as f:
        config = json.load(f)

    nombre_config = os.path.splitext(os.path.basename(config_path))[0]
    log_path      = setup_logging(BASE, nombre_config)
    logger        = logging.getLogger(__name__)
    logger.info(f"📁 Config : {args.config}")
    logger.info(f"📄 PDF    : {config['pdf_input']}")
    logger.info(f"📊 Output : {config['excel_output']}")
    logger.info(f"📝 Log    : {log_path}")

    try:
        app = ExtractorLista(config, BASE)
        df  = app.extraer()
        app.exportar(df)
    except KeyboardInterrupt:
        logger.warning("\n⚠️  Interrumpido por el usuario")
    except Exception as e:
        logger.error(f"🔥 Error crítico: {e}", exc_info=True)
        sys.exit(1)
