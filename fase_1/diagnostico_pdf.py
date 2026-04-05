#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
diagnostico_pdf.py — Ve exactamente qué texto lee pdfplumber antes de cualquier extracción.

Uso:
    python3 diagnostico_pdf.py --pdf ruta/al/archivo.pdf
    python3 diagnostico_pdf.py --pdf ruta/al/archivo.pdf --offset 29   # para Price Shoes
    python3 diagnostico_pdf.py --pdf ruta/al/archivo.pdf --paginas 3   # primeras N páginas

Qué hace:
    1. Imprime los primeros 30 tokens de cada página (texto crudo que ve pdfplumber).
    2. Si se da --offset, también imprime el texto decodificado.
    3. Marca con >>> las líneas que podrían ser encabezado de tabla.
    4. Genera un archivo diagnostico_NOMBRE.txt con todo el output.

NO modifica ni extrae nada. Solo lee y reporta.
"""

import re
import sys
import argparse
from pathlib import Path

try:
    import pdfplumber
except ImportError:
    print("❌ Falta pdfplumber. Instala con: pip install pdfplumber")
    sys.exit(1)


# ── Decodificador (igual que extractor.py) ──────────────────────────────────

def _limpiar_cid(txt):
    return re.sub(r'\(cid:\d+\)', '', txt)

def _aplicar_offset(txt, offset):
    if offset == 0:
        return txt
    res = []
    for c in txt:
        o = ord(c)
        if 32 <= o <= 126:
            n = o + offset
            res.append(chr(n) if 32 <= n <= 126 else c)
        else:
            res.append(c)
    return ''.join(res)

def _decodificar(txt, offset):
    return _aplicar_offset(_limpiar_cid(txt), offset)


# ── Diagnóstico ──────────────────────────────────────────────────────────────

def diagnosticar(pdf_path: str, offset: int, paginas: int):
    path   = Path(pdf_path)
    outfile = Path(f"diagnostico_{path.stem}.txt")
    lineas  = []

    def log(msg=""):
        print(msg)
        lineas.append(msg)

    log(f"{'='*60}")
    log(f"  DIAGNÓSTICO PDF — {path.name}")
    log(f"  Offset aplicado: {offset}   |   Primeras páginas: {paginas}")
    log(f"{'='*60}")

    with pdfplumber.open(pdf_path) as pdf:
        total = len(pdf.pages)
        log(f"\n📄 Total de páginas en el PDF: {total}")

        for i, page in enumerate(pdf.pages[:paginas], 1):
            log(f"\n{'─'*50}")
            log(f"  PÁGINA {i}")
            log(f"{'─'*50}")

            # Extraer con tolerancia estrecha para separar tokens (como ExtractorPS)
            words = page.extract_words(x_tolerance=3, y_tolerance=5, keep_blank_chars=False)

            if not words:
                log("  ⚠️  pdfplumber no encontró ningún token en esta página.")
                log("      El PDF podría ser imagen escaneada (necesitaría OCR).")
                continue

            log(f"\n  [CRUDO — sin offset]  primeros {min(30, len(words))} tokens:\n")
            filas_y = {}
            for w in words:
                y = round(w["top"])
                filas_y.setdefault(y, []).append(w["text"])

            for y, tokens in list(sorted(filas_y.items()))[:15]:
                linea = "  ".join(tokens)
                marca = "  >>>" if any(len(t) > 2 and t.isupper() for t in tokens) else "     "
                log(f"{marca} y={y:4d}  |  {linea}")

            if offset != 0:
                log(f"\n  [DECODIFICADO — offset={offset}]  primeros tokens:\n")
                decoded = [{**w, "text": _decodificar(w["text"], offset)} for w in words]
                filas_d = {}
                for w in decoded:
                    y = round(w["top"])
                    filas_d.setdefault(y, []).append(w["text"])

                for y, tokens in list(sorted(filas_d.items()))[:15]:
                    linea = "  ".join(tokens)
                    marca = "  >>>" if any(len(t) > 2 and t.isupper() for t in tokens) else "     "
                    log(f"{marca} y={y:4d}  |  {linea}")

            # Buscar posibles encabezados (líneas con ≥3 tokens cortos en mayúsculas)
            candidatos = []
            for y, tokens in sorted(filas_y.items()):
                mayus = [t for t in tokens if t.isupper() and len(t) >= 2]
                if len(mayus) >= 2:
                    candidatos.append((y, tokens))

            if candidatos:
                log(f"\n  [CANDIDATOS A ENCABEZADO — texto crudo]\n")
                for y, tokens in candidatos[:5]:
                    log(f"       y={y:4d}  |  {'  '.join(tokens)}")

                if offset != 0:
                    log(f"\n  [CANDIDATOS A ENCABEZADO — decodificados]\n")
                    decoded_map = {}
                    for w in words:
                        y = round(w["top"])
                        decoded_map.setdefault(y, []).append(_decodificar(w["text"], offset))
                    for y, _ in candidatos[:5]:
                        tokens_dec = decoded_map.get(y, [])
                        log(f"       y={y:4d}  |  {'  '.join(tokens_dec)}")
            else:
                log(f"\n  ⚠️  No se encontraron líneas con ≥2 tokens en mayúsculas.")
                log(f"      Posible causa: texto no seleccionable o encoding diferente.")

    # Guardar txt
    outfile.write_text("\n".join(lineas), encoding="utf-8")
    print(f"\n✅ Diagnóstico guardado en: {outfile.resolve()}")
    print(f"   Copia y pega su contenido para calibrar el config.")


# ── Punto de entrada ─────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Diagnóstico de PDF — ve exactamente qué lee pdfplumber"
    )
    parser.add_argument("--pdf",     required=True, help="Ruta al PDF a diagnosticar")
    parser.add_argument("--offset",  type=int, default=0,
                        help="Offset de decodificación (29 para Price Shoes, 0 para los demás)")
    parser.add_argument("--paginas", type=int, default=3,
                        help="Número de páginas a inspeccionar (default: 3)")
    args = parser.parse_args()

    if not Path(args.pdf).is_file():
        print(f"❌ No se encontró el archivo: {args.pdf}")
        sys.exit(1)

    diagnosticar(args.pdf, args.offset, args.paginas)


if __name__ == "__main__":
    main()
