python3 << 'EOF'
# ══════════════════════════════════════════════════════════════
#  OCR DIAGNÓSTICO — autopsia de IDs no encontrados
#  Edita la sección CONFIGURACIÓN y ejecuta en terminal.
# ══════════════════════════════════════════════════════════════

# ── CONFIGURACIÓN ──────────────────────────────────────────────
PDF       = "fase_2/libros/catalogo_kids_pk.pdf"
EXCEL     = "fase_2/precios/lista_kids_pk.xlsx"   # columnas: ID, precio_venta
PAGINAS   = [249]                               # páginas a revisar
PROVEEDOR = "Pakar"       # PS | Pakar | Cklass | Otro
ID_MIN    = 4
ID_MAX    = 8
DPI       = 200
CONTRASTE = 2.5
NITIDEZ   = 2.0
# ──────────────────────────────────────────────────────────────

import re
import pandas as pd
from pdf2image import convert_from_path
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract

S1 = "═" * 64
S2 = "─" * 64

# ── Helpers de extracción por proveedor ───────────────────────

def extraer_candidato(texto, proveedor, id_min, id_max):
    p = proveedor.upper()
    if p == "PAKAR":
        m = re.search(r'\d{3}-\d{3}', texto)
        return m.group() if m else None
    if p == "CKLASS":
        m = re.search(r'\d{3}-\d{2}', texto)
        return m.group() if m else None
    if p == "PS":
        fuente = re.sub(r"^[I1][Dd]\D*", "", texto, flags=re.IGNORECASE).strip() or texto
        c = re.sub(r"\D", "", fuente)
    else:
        c = re.sub(r"[^A-Za-z0-9]", "", texto)
    if len(c) < id_min or len(c) > id_max * 2:
        return None
    return c

def confusiones_ocr(id_str):
    """Genera variantes con sustituciones típicas de OCR."""
    mapas = [
        {"0": "O", "O": "0"},
        {"1": "I", "I": "1", "l": "1"},
        {"8": "B", "B": "8"},
        {"5": "S", "S": "5"},
        {"6": "G", "G": "6"},
        {"2": "Z", "Z": "2"},
    ]
    variantes = set()
    for mapa in mapas:
        v = ""
        cambio = False
        for c in id_str:
            if c in mapa:
                v += mapa[c]
                cambio = True
            else:
                v += c
        if cambio:
            variantes.add(v)
    return variantes

def tokens_cercanos(tokens, idx, radio=100):
    """Devuelve tokens dentro de radio px en cualquier dirección."""
    x0, y0 = tokens["left"][idx], tokens["top"][idx]
    vecinos = []
    for k, t in enumerate(tokens["text"]):
        if k == idx or not t.strip():
            continue
        if abs(tokens["left"][k] - x0) < radio and abs(tokens["top"][k] - y0) < radio:
            vecinos.append(t)
    return vecinos

# ── Preprocesado ──────────────────────────────────────────────

def mejorar(img):
    img = ImageEnhance.Contrast(img).enhance(CONTRASTE)
    img = ImageEnhance.Sharpness(img).enhance(NITIDEZ)
    img = img.filter(ImageFilter.MedianFilter(size=3))
    return img

def ocr_tokens(img):
    return pytesseract.image_to_data(
        img, lang="spa",
        config="--oem 3 --psm 6",
        output_type=pytesseract.Output.DICT
    )

def ocr_con_rotaciones(img):
    W, H = img.size
    d0 = ocr_tokens(img)

    img90  = img.rotate(90, expand=True)
    d90    = ocr_tokens(img90)
    left90 = list(d90["top"])
    top90  = [H - 1 - rx for rx in d90["left"]]
    d90["left"], d90["top"] = left90, top90

    img270  = img.rotate(270, expand=True)
    d270    = ocr_tokens(img270)
    left270 = [W - 1 - ry for ry in d270["top"]]
    top270  = list(d270["left"])
    d270["left"], d270["top"] = left270, top270

    merged = {k: list(d0[k]) for k in ("text","conf","left","top")}
    for d in (d90, d270):
        for j, t in enumerate(d["text"]):
            if not t.strip():
                continue
            x2, y2 = d["left"][j], d["top"][j]
            if not any(
                abs(merged["left"][k] - x2) < 20 and abs(merged["top"][k] - y2) < 20
                for k in range(len(merged["text"]))
            ):
                for key in ("text","conf","left","top"):
                    merged[key].append(d[key][j])
    return merged

# ── Cargar Excel ──────────────────────────────────────────────

try:
    df = pd.read_excel(EXCEL)
    df.columns = [str(c).strip() for c in df.columns]
    ids_excel = set(df["ID"].astype(str).str.strip().tolist())
    print(f"\n  📊  Excel cargado — {len(ids_excel)} IDs")
except Exception as e:
    print(f"\n  ❌  No se pudo leer el Excel: {e}")
    ids_excel = set()

# ══════════════════════════════════════════════════════════════
#  LOOP DE PÁGINAS
# ══════════════════════════════════════════════════════════════

for n_pag in PAGINAS:
    print(f"\n{S1}")
    print(f"  PÁGINA {n_pag}  —  {PROVEEDOR}  |  DPI={DPI}")
    print(S1)

    imgs = convert_from_path(PDF, dpi=DPI, first_page=n_pag, last_page=n_pag)
    img  = mejorar(imgs[0].convert("L"))
    data = ocr_con_rotaciones(img)

    # ── 1. Tokens y candidatos ────────────────────────────────
    todos_tokens   = [t for t in data["text"] if t.strip()]
    ids_aceptados  = {}   # candidato → (token_orig, conf, idx)
    ids_rechazados = []   # (token_orig, razon)

    for j, texto in enumerate(data["text"]):
        if not texto.strip():
            continue
        c = extraer_candidato(texto, PROVEEDOR, ID_MIN, ID_MAX)
        if c:
            if c not in ids_aceptados:
                ids_aceptados[c] = (texto, data["conf"][j], j)
        else:
            # ¿Por qué fue rechazado?
            p = PROVEEDOR.upper()
            if p == "PS":
                fuente = re.sub(r"^[I1][Dd]\D*", "", texto, flags=re.IGNORECASE).strip() or texto
                solo_num = re.sub(r"\D", "", fuente)
                n = len(solo_num)
                if n > 0 and n < ID_MIN:
                    ids_rechazados.append((texto, f"muy corto ({n} dígitos, mín {ID_MIN})"))
                elif n > ID_MAX * 2:
                    ids_rechazados.append((texto, f"muy largo ({n} dígitos, máx {ID_MAX*2})"))
                elif n == 0:
                    ids_rechazados.append((texto, "sin dígitos"))
            elif p in ("PAKAR", "CKLASS"):
                ids_rechazados.append((texto, "no coincide patrón regex del proveedor"))

    # ── 2. Cruce con Excel ────────────────────────────────────
    encontrados   = {c for c in ids_aceptados if c in ids_excel}
    no_en_excel   = {c for c in ids_aceptados if c not in ids_excel}

    print(f"\n  TOKENS OCR: {len(todos_tokens)} palabras")
    print(f"  Candidatos extraídos: {len(ids_aceptados)}  |  En Excel: {len(encontrados)}  |  Fuera de Excel: {len(no_en_excel)}")

    # ── 3. IDs encontrados ────────────────────────────────────
    print(f"\n{S2}")
    print(f"  ✅  ENCONTRADOS EN EXCEL ({len(encontrados)})")
    print(S2)
    for c in sorted(encontrados):
        tok_orig, conf, _ = ids_aceptados[c]
        sufijo = f"  ← token: '{tok_orig}'" if tok_orig != c else ""
        print(f"    {c:<14}{sufijo}  (conf {conf})")

    # ── 4. Candidatos fuera del Excel ─────────────────────────
    if no_en_excel:
        print(f"\n{S2}")
        print(f"  ⚠️   CANDIDATOS NO EN EXCEL ({len(no_en_excel)})  — posibles falsos positivos o IDs extra")
        print(S2)
        for c in sorted(no_en_excel):
            tok_orig, conf, _ = ids_aceptados[c]
            print(f"    {c:<14}  token: '{tok_orig}'  (conf {conf})")

    # ── 5. Tokens rechazados por regex/longitud ───────────────
    if ids_rechazados:
        print(f"\n{S2}")
        print(f"  🔴  RECHAZADOS POR FILTRO ({len(ids_rechazados)})  — ajustar ID_MIN / ID_MAX / proveedor")
        print(S2)
        for tok, razon in ids_rechazados[:20]:   # máx 20 para no saturar
            print(f"    '{tok}'  →  {razon}")

    # ── 6. Autopsia: tokens cercanos a IDs no encontrados ─────
    #       ¿Hay pares "id" + número que no se fusionaron?
    PREFIJO_RE = re.compile(r'^[I1][Dd]$', re.IGNORECASE)
    pares_sueltos = []
    usados_par = set()
    for j, tok in enumerate(data["text"]):
        if not tok.strip() or not PREFIJO_RE.match(tok.strip()):
            continue
        x0, y0 = data["left"][j], data["top"][j]
        for k, tok2 in enumerate(data["text"]):
            if k == j or k in usados_par or not tok2.strip():
                continue
            solo_num = re.sub(r"\D", "", tok2)
            if len(solo_num) < ID_MIN or len(solo_num) > ID_MAX * 2:
                continue
            dist = abs(data["left"][k] - x0) + abs(data["top"][k] - y0)
            if dist < 150:
                pares_sueltos.append((tok, tok2, solo_num, dist))
                usados_par.add(j)
                usados_par.add(k)
                break

    if pares_sueltos:
        print(f"\n{S2}")
        print(f"  🔗  PARES 'id + número' SUELTOS ({len(pares_sueltos)})  — token partido, necesita fusión")
        print(S2)
        for pre, num_tok, num, dist in pares_sueltos:
            en_excel = "✅ en Excel" if num in ids_excel else "❌ no en Excel"
            print(f"    '{pre}' + '{num_tok}'  →  {num}  ({en_excel}, dist {dist}px)")

    # ── 7. Detección de confusiones OCR ──────────────────────
    #       Para cada candidato fuera del Excel, probar variantes
    confusiones_encontradas = []
    for c in no_en_excel:
        for var in confusiones_ocr(c):
            if var in ids_excel:
                confusiones_encontradas.append((c, var))

    if confusiones_encontradas:
        print(f"\n{S2}")
        print(f"  🔁  CONFUSIONES OCR DETECTADAS ({len(confusiones_encontradas)})  — dígito mal leído")
        print(S2)
        for leido, real in confusiones_encontradas:
            print(f"    OCR leyó '{leido}'  →  en Excel existe '{real}'")

print(f"\n{S1}\n")
EOF
