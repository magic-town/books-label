#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extractor.py — Extractor de campos de listas de precios
Boutique Zepeda · books-label · Fase 1

Uso:
    python3 fase_1/extractor.py --config fase_1/config/config_ps_pv26.json

Proveedores soportados:
    PS     → Price Shoes  (encoding propietario, extracción por coordenadas X)
    Pakar  → Pakar        (texto limpio, extracción tabular)
    Cklass → Cklass       (texto limpio, precios con $ y decimales)
    Otro   → genérico     (texto limpio, offset configurable)

Dependencias Python (requirements.txt):
    pdfplumber, pandas, openpyxl
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


# ─────────────────────────────────────────────
#  Argumentos
# ─────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(
        description="Extractor de campos de listas de precios — Boutique Zepeda"
    )
    parser.add_argument("--config", required=True, help="Ruta al archivo JSON de configuración")
    return parser.parse_args()


# ─────────────────────────────────────────────
#  Logger
# ─────────────────────────────────────────────

def setup_logger(nombre: str, base_dir: str) -> logging.Logger:
    ts      = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = os.path.join(base_dir, "diagnosticos")
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, f"{nombre}_{ts}.log")

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
    logger.info(f"📝 Log: {log_path}")
    return logger


# ─────────────────────────────────────────────
#  Decodificador Price Shoes
# ─────────────────────────────────────────────

def _decodificar(txt: str, offset: int) -> str:
    """
    Price Shoes usa dos fuentes en el mismo PDF:
    - Letras/simbolos: offset ASCII (ej. offset=29).
    - Numeros: (cid:N) donde N=19->'0', N=20->'1', ..., N=28->'9'.
      No llevan offset; se mapean directamente a digito.

    _limpiar_cid eliminaba TODOS los (cid:N), vaciando Pag, ID y precio.
    Esta funcion los preserva correctamente.
    """
    resultado = []
    i = 0
    while i < len(txt):
        m = re.match(r'\(cid:(\d+)\)', txt[i:])
        if m:
            n = int(m.group(1))
            if 19 <= n <= 28:
                resultado.append(str(n - 19))
            i += len(m.group(0))
        else:
            c = txt[i]
            o = ord(c)
            if offset != 0 and 32 <= o <= 126:
                n2 = o + offset
                resultado.append(chr(n2) if 32 <= n2 <= 126 else c)
            else:
                resultado.append(c)
            i += 1
    return ''.join(resultado)


# ─────────────────────────────────────────────
#  Limpieza de precio
# ─────────────────────────────────────────────

def _limpiar_precio(val: str) -> str | None:
    if not val:
        return None
    limpio = re.sub(r'[$,\s]', '', str(val))
    limpio = re.sub(r'\.0+$', '', limpio)
    if re.match(r'^\d+(\.\d+)?$', limpio):
        return limpio.split('.')[0]
    return None


# ─────────────────────────────────────────────
#  Extractor Price Shoes — coordenadas X fijas
# ─────────────────────────────────────────────

class ExtractorPS:
    """
    Price Shoes: encoding propietario + layout con imagen izquierda y tabla derecha.

    Estrategia final (rangos X fijos):
    - Las columnas Pag, ID y Sug_credito tienen posiciones X estables en todo el PDF.
    - Se detectan desde el encabezado y se aplica una tolerancia estricta (~20px)
      para no capturar columnas adyacentes (Corrida, Pasillo, etc.).
    - Cada producto ocupa un bloque de 3-5 sub-filas con Y ligeramente distintas.
      Se fusionan filas a <=12px de distancia vertical.
    - El decodificador maneja dos fuentes: letras con offset ASCII,
      numeros como (cid:N) donde N-19 = digito.
    """

    def __init__(self, config: dict, logger: logging.Logger):
        self.logger     = logger
        self.offset     = config.get("encoding_offset", 29)
        self.tol_x      = config.get("tolerancia_x", 20.0)   # estricta para separar columnas
        self.col_pag    = config.get("col_pag",    "Pag")
        self.col_id     = config.get("col_id",     "ID")
        self.col_precio = config.get("col_precio", "Sug_credito")

    def extraer(self, pdf_path: str) -> pd.DataFrame:
        registros = []
        col_x     = None

        with pdfplumber.open(pdf_path) as pdf:
            total = len(pdf.pages)
            self.logger.info(f"📄 Total páginas: {total}")

            for i, page in enumerate(pdf.pages, 1):
                # x_tolerance=3 mantiene tokens separados para detectar columnas
                words = page.extract_words(
                    x_tolerance=3,
                    y_tolerance=5,
                    keep_blank_chars=False,
                )
                if not words:
                    continue

                # Decodificar todos los tokens
                decoded = [{**w, "text": _decodificar(w["text"], self.offset)} for w in words]

                # Intentar detectar encabezado
                nuevo_col_x = self._detectar_encabezado(decoded)
                if nuevo_col_x:
                    col_x = nuevo_col_x
                    self.logger.debug(f"  Página {i}: encabezado → {col_x}")

                if not col_x:
                    self.logger.debug(f"  Página {i}: sin columnas detectadas, omitida")
                    continue

                filas = self._extraer_filas(decoded, col_x)
                antes = len(registros)
                for fila in filas:
                    registros.append({
                        "pag":         fila.get("pag", "").strip(),
                        "id":          fila.get("id",  "").strip(),
                        "precio_base": _limpiar_precio(fila.get("precio", "")),
                    })
                self.logger.debug(f"  Página {i}: {len(registros)-antes} registros")

        df = pd.DataFrame(registros) if registros else pd.DataFrame(columns=["pag","id","precio_base"])
        return self._filtrar(df)

    def _detectar_encabezado(self, words: list) -> dict | None:
        """
        Busca la fila con col_pag y col_id. Si col_precio esta en fila adyacente
        (Price Shoes lo pone ~1px abajo), lo busca en un rango de +-5px.
        Devuelve {alias: x0} con las coordenadas X del encabezado.
        """
        filas_y = {}
        for w in words:
            y = round(w["top"])
            filas_y.setdefault(y, []).append(w)

        objetivos = {
            self.col_pag:    "pag",
            self.col_id:     "id",
            self.col_precio: "precio",
        }
        ys_sorted = sorted(filas_y.keys())

        for y, tokens in sorted(filas_y.items()):
            textos = [t["text"].strip() for t in tokens]
            if self.col_pag not in textos or self.col_id not in textos:
                continue

            col_x = {}
            for t in tokens:
                txt = t["text"].strip()
                if txt in objetivos:
                    col_x[objetivos[txt]] = t["x0"]

            if "precio" not in col_x:
                for y2 in ys_sorted:
                    if y2 == y or abs(y2 - y) > 5:
                        continue
                    for t in filas_y[y2]:
                        if t["text"].strip() == self.col_precio:
                            col_x["precio"] = t["x0"]
                            self.logger.debug(f"  col_precio en fila adyacente y={y2}")
                            break

            if "pag" in col_x and "id" in col_x and "precio" in col_x:
                return col_x

        return None

    def _extraer_filas(self, words: list, col_x: dict) -> list:
        """
        Asigna cada token a pag/id/precio usando rangos X estrictos
        (encabezado_X +- tol_x). Evita capturar columnas adyacentes como
        Pasillo (x~40) o Corrida (x~160) que confunden la asignacion.

        Luego fusiona sub-filas del mismo producto (gap Y <= 12px).
        """
        x_pag    = col_x["pag"]
        x_id     = col_x["id"]
        x_precio = col_x["precio"]
        tol      = self.tol_x

        filas_raw = {}
        for w in words:
            x = w["x0"]
            token = w["text"].strip()
            if not token:
                continue

            # Asignar solo si el token cae dentro del rango de la columna
            if abs(x - x_pag) <= tol:
                col = "pag"
            elif abs(x - x_id) <= tol:
                col = "id"
            elif abs(x - x_precio) <= tol:
                col = "precio"
            else:
                continue

            y_key = round(w["top"])
            if y_key not in filas_raw:
                filas_raw[y_key] = {}
            prev = filas_raw[y_key].get(col, "")
            filas_raw[y_key][col] = (prev + " " + token).strip() if prev else token

        # Fusionar sub-filas del mismo producto (gap <= 12px)
        bloques = []
        ys = sorted(filas_raw.keys())
        if not ys:
            return []

        bloque_actual = dict(filas_raw[ys[0]])
        y_inicio = ys[0]

        for y in ys[1:]:
            if y - y_inicio <= 12:
                for col, val in filas_raw[y].items():
                    if col not in bloque_actual:
                        bloque_actual[col] = val
                    elif col in ("pag", "id", "precio") and re.match(r"^\d+$", val) and not re.match(r"^\d+$", bloque_actual[col]):
                        bloque_actual[col] = val  # preferir valor numerico puro
            else:
                bloques.append(bloque_actual)
                bloque_actual = dict(filas_raw[y])
                y_inicio = y

        bloques.append(bloque_actual)
        return bloques

    def _filtrar(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df
        # IDs de Price Shoes: 7 digitos. Rango 6-8 para cubrir variaciones.
        df = df[df["id"].astype(str).str.match(r"^\d{6,8}$")].copy()
        df = df[df["precio_base"].notna()].copy()
        return df.reset_index(drop=True)




# ─────────────────────────────────────────────
#  Extractor texto limpio (Pakar / Cklass / Otro)
# ─────────────────────────────────────────────

class ExtractorTexto:
    """
    Para PDFs con texto seleccionable y estructura tabular clara.
    Detecta encabezado por nombre de columna, mapea X y extrae filas.
    """

    def __init__(self, config: dict, logger: logging.Logger):
        self.logger     = logger
        self.tol_x      = config.get("tolerancia_x", 20.0)
        self.tol_col    = config.get("tol_col", 0)          # 0 = sin filtro de distancia (comportamiento original)
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
                        "pag":         fila.get("pag", "").strip(),
                        "id":          fila.get("id",  "").strip(),
                        "precio_base": _limpiar_precio(fila.get("precio", "")),
                    })
                self.logger.debug(f"  Página {i}: {len(filas)} filas")

        df = pd.DataFrame(registros) if registros else pd.DataFrame(columns=["pag","id","precio_base"])
        return self._filtrar(df)

    def _detectar_encabezado(self, words):
        for w in words:
            txt = w["text"].strip()
            if txt == self.col_pag or self.col_pag in txt:
                return w["top"]
        return None

    def _mapear_columnas(self, words, header_y):
        """
        Mapea columnas objetivo a su coordenada X.
        tol_y=15 para cubrir encabezados partidos en 2 filas (Pakar: y=53 y y=54).
        Une pares de tokens consecutivos para manejar nombres como "2 PAGOS"
        que pdfplumber parte en tokens separados "2" y "PAGOS".
        """
        col_x = {}
        tol_y = 15
        mapa  = {self.col_pag: "pag", self.col_id: "id", self.col_precio: "precio"}

        # Agrupar tokens de la zona del encabezado por fila Y
        zona = [w for w in words if abs(w["top"] - header_y) < tol_y]
        zona_por_fila = {}
        for w in zona:
            y2 = round(w["top"])
            zona_por_fila.setdefault(y2, []).append(w)

        for y2, fila_tokens in zona_por_fila.items():
            for i, w in enumerate(fila_tokens):
                txt = w["text"].strip()
                for nombre, alias in mapa.items():
                    if alias in col_x:
                        continue
                    # Match directo
                    if txt == nombre or nombre in txt:
                        col_x[alias] = w["x0"]
                        break
                    # Match uniendo con token siguiente ("2" + "PAGOS" -> "2 PAGOS")
                    if i + 1 < len(fila_tokens):
                        txt2 = txt + " " + fila_tokens[i + 1]["text"].strip()
                        if txt2 == nombre or nombre in txt2:
                            col_x[alias] = w["x0"]
                            break

        return col_x

    def _agrupar_filas(self, words, header_y, col_x):
        filas   = {}
        aliases = list(col_x.keys())
        xs      = [col_x[a] for a in aliases]

        for w in words:
            if w["top"] <= header_y + 5:
                continue
            y_key = round(w["top"])
            token = w["text"].strip()
            if not token:
                continue

            idx  = min(range(len(xs)), key=lambda k: abs(w["x0"] - xs[k]))
            # tol_col > 0: descartar tokens demasiado lejos de todas las columnas objetivo
            # Esto evita que columnas intermedias (MARCA, COLOR, CLAVE…) ensucien pag/id/precio
            if self.tol_col > 0 and abs(w["x0"] - xs[idx]) > self.tol_col:
                continue
            col = aliases[idx]

            if y_key not in filas:
                filas[y_key] = {}
            prev = filas[y_key].get(col, "")
            filas[y_key][col] = (prev + " " + token).strip() if prev else token

        return list(filas.values())

    def _filtrar(self, df):
        if df.empty:
            return df
        df = df[df["precio_base"].notna()].copy()
        df = df[df["id"].str.strip() != ""].copy()
        df = df[~df["precio_base"].astype(str).str.contains(r'[a-zA-Z]', na=False)].copy()
        return df.reset_index(drop=True)


# ─────────────────────────────────────────────
#  Clase principal
# ─────────────────────────────────────────────

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
            self.logger.info("🔧 Modo: Price Shoes (decodificador + coordenadas X)")
            return ExtractorPS(self.config, self.logger)
        elif p in ("PAKAR", "CKLASS", "OTRO"):
            self.logger.info(f"🔧 Modo: texto limpio ({self.proveedor})")
            return ExtractorTexto(self.config, self.logger)
        else:
            self.logger.warning(f"⚠️  Proveedor '{self.proveedor}' no reconocido — extractor genérico")
            return ExtractorTexto(self.config, self.logger)

    def ejecutar(self):
        if not os.path.isfile(self.pdf_path):
            self.logger.error(f"❌ PDF no encontrado: {self.pdf_path}")
            raise FileNotFoundError(self.pdf_path)

        extractor = self._factory()
        self.logger.info("🚀 Iniciando extracción...")
        df = extractor.extraer(self.pdf_path)

        if df.empty:
            self.logger.warning(
                "⚠️  No se extrajeron registros.\n"
                "   Verifica col_pag y col_id en el config — deben coincidir exactamente\n"
                "   con el encabezado del PDF después de aplicar encoding_offset."
            )
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
                self.logger.info("🟢 EXTRACCIÓN EXITOSA — Validar Excel antes de usar en Fase 2")
            elif n >= 20:
                self.logger.warning("🟡 EXTRACCIÓN PARCIAL — Revisar columnas en el config")
            else:
                self.logger.error("🔴 EXTRACCIÓN INSUFICIENTE — Muy pocos registros")

        self.logger.info(f"[STAT] proveedor={self.proveedor}")
        self.logger.info(f"[STAT] registros={len(df)}")
        self.logger.info(f"[STAT] ids_unicos={df['id'].nunique() if not df.empty else 0}")


# ─────────────────────────────────────────────
#  Punto de entrada
# ─────────────────────────────────────────────

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
