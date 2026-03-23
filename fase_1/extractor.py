#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extractor.py — Extractor de campos de listas de precios
Boutique Zepeda · books-label · Fase 1

Notas de implementación:
    - El PDF de Price Shoes tiene cada carácter desplazado +29 en ASCII.
      El extractor resta 29 para recuperar el texto real.
    - col_pag / col_id / col_precio se escriben con los nombres reales
      del encabezado (ej. "Pag", "ID", "Sug_credito").
    - _detectar_encabezado y _mapear_columnas usan startswith para tolerar
      tokens fusionados cuando dos columnas están muy próximas en el PDF.
    - tolerancia_asign controla el margen máximo (px) para asignar un token
      de datos a una columna. Permite separar tokenización (tolerancia_x baja)
      de asignación (tolerancia_asign más generosa).
"""

import os
import re
import sys
import json
import logging
import argparse
from datetime import datetime

import pandas as pd
import pdfplumber


def parse_args():
    parser = argparse.ArgumentParser(
        description="Extractor de campos de listas de precios — Boutique Zepeda"
    )
    parser.add_argument("--config", required=True, help="Ruta al archivo de configuración JSON")
    return parser.parse_args()


def setup_logger(nombre_config: str, base_dir: str) -> logging.Logger:
    ts      = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = os.path.join(base_dir, "diagnosticos")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, f"{nombre_config}_{ts}.log")

    logger = logging.getLogger("extractor")
    logger.setLevel(logging.DEBUG)
    fmt = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)

    logger.addHandler(fh)
    logger.addHandler(ch)
    logger.info(f"📝 Log guardado en: {log_path}")
    return logger


def _limpiar_cid(texto: str) -> str:
    return re.sub(r'\(cid:\d+\)', '', texto)


def _aplicar_offset(texto: str, offset: int) -> str:
    """
    Revierte el encoding de Price Shoes restando el offset.
    El PDF almacena cada carácter con +offset; restar recupera el original.
    offset=29 → Price Shoes | offset=0 → PDF limpio
    """
    if offset == 0:
        return texto
    resultado = []
    for c in texto:
        o = ord(c)
        if 32 <= o <= 126:
            nuevo = o - offset
            if 32 <= nuevo <= 126:
                resultado.append(chr(nuevo))
            else:
                resultado.append(c)
        else:
            resultado.append(c)
    return ''.join(resultado)


def _decodificar(texto: str, offset: int) -> str:
    texto = _limpiar_cid(texto)
    return _aplicar_offset(texto, offset)


def _limpiar_precio(valor: str) -> str | None:
    if not valor:
        return None
    limpio = re.sub(r'[$,\s]', '', str(valor))
    limpio = re.sub(r'\.0+$', '', limpio)
    if re.match(r'^\d+(\.\d+)?$', limpio):
        return limpio.split('.')[0]
    return None


class ExtractorPS:
    """
    Price Shoes — encoding propietario (+29 ASCII).
    Tokeniza con tolerancia_x baja para separar columnas,
    asigna datos con tolerancia_asign generosa para cubrir offsets de alineación.
    """

    def __init__(self, config: dict, logger: logging.Logger):
        self.logger     = logger
        self.offset     = config.get("encoding_offset", 29)
        self.tol_x      = config.get("tolerancia_x",    5.0)
        self.tol_asign  = config.get("tolerancia_asign", 20.0)
        self.col_pag    = config.get("col_pag",    "Pag")
        self.col_id     = config.get("col_id",     "ID")
        self.col_precio = config.get("col_precio", "Sug_credito")

    def extraer(self, pdf_path: str) -> pd.DataFrame:
        registros = []

        with pdfplumber.open(pdf_path) as pdf:
            total = len(pdf.pages)
            self.logger.info(f"📄 Total páginas: {total}")

            for i, page in enumerate(pdf.pages, 1):
                words = page.extract_words(
                    x_tolerance=self.tol_x,
                    y_tolerance=5,
                    keep_blank_chars=False,
                )
                if not words:
                    continue

                decoded = [{**w, "text": _decodificar(w["text"], self.offset)} for w in words]

                header_y = self._detectar_encabezado(decoded)
                if header_y is None:
                    self.logger.debug(f"  Página {i}: sin encabezado")
                    continue

                col_x = self._mapear_columnas(decoded, header_y)
                if len(col_x) < 2:
                    self.logger.debug(f"  Página {i}: columnas insuficientes {col_x}")
                    continue

                filas = self._agrupar_filas(decoded, header_y, col_x)
                for fila in filas:
                    registros.append({
                        "pag":         fila.get("pag", ""),
                        "id":          fila.get("id",  ""),
                        "precio_base": _limpiar_precio(fila.get("precio", "")),
                    })

                self.logger.debug(f"  Página {i}: {len(filas)} filas")

        return self._filtrar(pd.DataFrame(registros))

    def _detectar_encabezado(self, words):
        for w in words:
            if w["text"].strip().startswith(self.col_pag):
                return w["top"]
        return None

    def _mapear_columnas(self, words, header_y):
        col_x = {}
        tol_y = 8
        mapa  = {
            self.col_pag:    "pag",
            self.col_id:     "id",
            self.col_precio: "precio",
        }
        for w in words:
            if abs(w["top"] - header_y) < tol_y:
                txt = w["text"].strip()
                for nombre, alias in mapa.items():
                    if txt.startswith(nombre):
                        col_x[alias] = w["x0"]
        return col_x

    def _agrupar_filas(self, words, header_y, col_x):
        filas   = {}
        aliases = list(col_x.keys())
        xs      = list(col_x.values())

        for w in words:
            if w["top"] <= header_y + 5:
                continue
            y_key = round(w["top"])
            token = w["text"].strip()
            if not token:
                continue

            dists = [abs(w["x0"] - xs[k]) for k in range(len(xs))]
            idx   = min(range(len(xs)), key=lambda k: dists[k])
            if dists[idx] > self.tol_asign:
                continue

            col  = aliases[idx]
            if y_key not in filas:
                filas[y_key] = {}
            prev = filas[y_key].get(col, "")
            filas[y_key][col] = (prev + " " + token).strip()

        return list(filas.values())

    def _filtrar(self, df):
        if df.empty:
            return df
        df = df[df["id"].astype(str).str.match(r'^\d{4,8}$')].copy()
        df = df[df["precio_base"].notna()].copy()
        return df.reset_index(drop=True)


class ExtractorTexto:
    """
    Pakar / Cklass / Otro — texto limpio, estructura tabular.
    """

    def __init__(self, config: dict, logger: logging.Logger):
        self.logger     = logger
        self.tol_x      = config.get("tolerancia_x", 20.0)
        self.col_pag    = config.get("col_pag",    "PÁG.")
        self.col_id     = config.get("col_id",     "CÓDIGO")
        self.col_precio = config.get("col_precio", "2 PAGOS")
        self.offset     = config.get("encoding_offset", 0)

    def extraer(self, pdf_path: str) -> pd.DataFrame:
        registros = []
        col_x     = None

        with pdfplumber.open(pdf_path) as pdf:
            total = len(pdf.pages)
            self.logger.info(f"📄 Total páginas: {total}")

            for i, page in enumerate(pdf.pages, 1):
                words = page.extract_words(
                    x_tolerance=self.tol_x,
                    y_tolerance=5,
                    keep_blank_chars=False,
                )
                if not words:
                    continue

                if self.offset:
                    words = [{**w, "text": _decodificar(w["text"], self.offset)} for w in words]

                header_y = self._detectar_encabezado(words)
                if header_y is not None:
                    col_x = self._mapear_columnas(words, header_y)

                if not col_x:
                    continue

                hy = header_y if header_y is not None else -1
                filas = self._agrupar_filas(words, hy, col_x)
                for fila in filas:
                    registros.append({
                        "pag":         fila.get("pag", ""),
                        "id":          fila.get("id",  "").strip(),
                        "precio_base": _limpiar_precio(fila.get("precio", "")),
                    })

                self.logger.debug(f"  Página {i}: {len(filas)} filas")

        return self._filtrar(pd.DataFrame(registros))

    def _detectar_encabezado(self, words):
        for w in words:
            txt = w["text"].strip()
            if txt == self.col_pag or self.col_pag in txt:
                return w["top"]
        return None

    def _mapear_columnas(self, words, header_y):
        col_x  = {}
        tol_y  = 10
        mapa   = {self.col_pag: "pag", self.col_id: "id", self.col_precio: "precio"}
        for w in words:
            if abs(w["top"] - header_y) < tol_y:
                txt = w["text"].strip()
                for nombre, alias in mapa.items():
                    if txt == nombre or nombre in txt:
                        col_x[alias] = w["x0"]
                        if alias == "pag" and self.col_id in txt:
                            col_x["id"] = w["x0"]
        return col_x

    def _agrupar_filas(self, words, header_y, col_x):
        filas   = {}
        aliases = list(col_x.keys())
        xs      = list(col_x.values())

        for w in words:
            if w["top"] <= header_y + 5:
                continue
            y_key = round(w["top"])
            token = w["text"].strip()
            if not token:
                continue

            idx = min(range(len(xs)), key=lambda k: abs(w["x0"] - xs[k]))
            col = aliases[idx]

            if y_key not in filas:
                filas[y_key] = {}
            prev = filas[y_key].get(col, "")
            filas[y_key][col] = (prev + " " + token).strip()

        return list(filas.values())

    def _filtrar(self, df):
        if df.empty:
            return df
        df = df[df["precio_base"].notna()].copy()
        df = df[df["id"].str.strip() != ""].copy()
        df = df[df["id"].str.match(r'^\d{4,8}(-\d+)?$')].copy()
        df = df[~df["precio_base"].astype(str).str.contains(r'[a-zA-Z]', na=False)].copy()
        return df.reset_index(drop=True)


class ExtractorCatalogo:

    def __init__(self, config: dict, base_dir: str):
        nombre = os.path.splitext(
            os.path.basename(config.get("_config_path", "extractor"))
        )[0]
        self.logger    = setup_logger(nombre, base_dir)
        self.config    = config
        self.base_dir  = base_dir
        self.proveedor = config.get("proveedor", "PS").strip()

        self.pdf_path   = os.path.join(base_dir, config.get("pdf_input",    ""))
        self.excel_path = os.path.join(base_dir, config.get("excel_output", ""))

        os.makedirs(os.path.dirname(self.excel_path), exist_ok=True)

        self.logger.info(f"🏭 Proveedor:       {self.proveedor}")
        self.logger.info(f"📄 PDF de entrada:  {self.pdf_path}")
        self.logger.info(f"📊 Excel de salida: {self.excel_path}")

    def _factory(self):
        p = self.proveedor.upper()
        if p == "PS":
            self.logger.info("🔧 Modo: Price Shoes (decodificador + extracción espacial)")
            return ExtractorPS(self.config, self.logger)
        elif p in ("PAKAR", "CKLASS", "OTRO"):
            self.logger.info(f"🔧 Modo: texto limpio ({self.proveedor})")
            return ExtractorTexto(self.config, self.logger)
        else:
            self.logger.warning(f"⚠️  Proveedor '{self.proveedor}' no reconocido — usando extractor genérico")
            return ExtractorTexto(self.config, self.logger)

    def ejecutar(self):
        if not os.path.isfile(self.pdf_path):
            self.logger.error(f"❌ PDF no encontrado: {self.pdf_path}")
            raise FileNotFoundError(self.pdf_path)

        extractor = self._factory()

        self.logger.info("🚀 Iniciando extracción...")
        df = extractor.extraer(self.pdf_path)

        if df.empty:
            self.logger.warning("⚠️  No se extrajeron registros — revisar col_pag / col_id / col_precio en el config")
            self.logger.error("🔴 EXTRACCIÓN FALLIDA")
        else:
            df["len"] = df["id"].astype(str).str.len()
            df.to_excel(self.excel_path, index=False)

            n    = len(df)
            u    = df["id"].nunique()
            pmin = df["precio_base"].min()
            pmax = df["precio_base"].max()

            self.logger.info(f"✅ Excel generado:  {self.excel_path}")
            self.logger.info(f"   Registros:       {n}")
            self.logger.info(f"   IDs únicos:      {u}")
            self.logger.info(f"   Rango precios:   {pmin} – {pmax}")

            if n >= 100:
                self.logger.info("🟢 EXTRACCIÓN EXITOSA — Validar Excel antes de usar como input de Fase 2")
            elif n >= 20:
                self.logger.warning("🟡 EXTRACCIÓN PARCIAL — Revisar columnas en el config")
            else:
                self.logger.error("🔴 EXTRACCIÓN INSUFICIENTE — Muy pocos registros, revisar PDF y config")

        self.logger.info(f"[STAT] proveedor={self.proveedor}")
        self.logger.info(f"[STAT] registros={len(df)}")
        self.logger.info(f"[STAT] ids_unicos={df['id'].nunique() if not df.empty else 0}")


if __name__ == "__main__":
    args        = parse_args()
    config_path = os.path.abspath(args.config)
    BASE        = os.path.dirname(os.path.abspath(__file__))

    if not os.path.isfile(config_path):
        print(f"❌ Archivo de configuración no encontrado: {config_path}")
        sys.exit(1)

    with open(config_path, encoding="utf-8") as f:
        config = json.load(f)

    config["_config_path"] = config_path

    try:
        app = ExtractorCatalogo(config, BASE)
        app.ejecutar()
    except Exception as e:
        logging.getLogger("extractor").error(f"🔥 Error crítico: {e}", exc_info=True)
        sys.exit(1)
