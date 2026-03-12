#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
diagnostico.py — Análisis de logs del Etiquetador
Boutique Zepeda · books-label

Lee el log más reciente en diagnosticos/ y genera un reporte
con causas detectadas y pasos a seguir en orden de prioridad.

  ─ Sonia: ejecuta este script después de cada corrida con
    semáforo amarillo o rojo. Lee los pasos en orden y prueba
    cada uno antes de avanzar al siguiente.
    Solo comparte el output con tu colaborador (Gabriel) cuando el diagnóstico
    lo indique explícitamente (aparecerá destacado al final).

Uso:
    python3 scripts/diagnostico.py
    python3 scripts/diagnostico.py --log diagnosticos/mi_log.log
"""

import os, re, sys, argparse, glob

# ── Colores ANSI ─────────────────────────────────────────────
R  = "\033[91m";  Y  = "\033[93m";  G  = "\033[92m"
B  = "\033[94m";  DM = "\033[2m";   BD = "\033[1m";  RS = "\033[0m"

NIVEL_COLOR = {"CRITICO": R, "ADVERTENCIA": Y, "INFO": B, "OK": G}
NIVEL_ICONO = {"CRITICO": "🔴", "ADVERTENCIA": "🟡", "INFO": "🔵", "OK": "🟢"}


# ─────────────────────────────────────────────
#  Argumentos
# ─────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description="Diagnóstico de logs — Boutique Zepeda")
    p.add_argument("--log", default=None,
                   help="Log a analizar. Si se omite, usa el más reciente.")
    return p.parse_args()


# ─────────────────────────────────────────────
#  Localizar log
# ─────────────────────────────────────────────

def encontrar_log(base_dir, log_path=None):
    if log_path:
        if not os.path.exists(log_path):
            print(f"\n{R}❌  Log no encontrado:{RS} {log_path}")
            sys.exit(1)
        return log_path
    logs = sorted(glob.glob(os.path.join(base_dir, "diagnosticos", "*.log")))
    if not logs:
        print(f"\n{R}❌  No hay logs en diagnosticos/{RS}")
        print(f"    Ejecuta primero el script con tu config.\n")
        sys.exit(1)
    return logs[-1]


# ─────────────────────────────────────────────
#  Parser de log
# ─────────────────────────────────────────────

def parsear_log(ruta):
    d = {
        "ruta": ruta, "config": None,
        "dpi": None, "psm": None,
        "fuzzy_activo": None, "fuzzy_umbral": None,
        "id_min": None, "id_max": None,
        "ocr_invertir": False, "doble_pasada": False,
        "paginas": None, "total_excel": None,
        "ids_unicos": None, "etiquetas": None,
        "fuzzy_matches": 0, "recorte_matches": 0,
        "tasa": None, "semaforo": None,
        "errores_pagina": [],
        "tesseract_ok": True, "excel_ok": True, "pdf_ok": True,
        "proceso_completo": False,
    }

    with open(ruta, encoding="utf-8") as f:
        lineas = f.readlines()

    for linea in lineas:
        l = linea.strip()

        # Métricas exactas — líneas [STAT] emitidas por catalogo_base.py
        m = re.search(r"\[STAT\] (\w+)=(.+)", l)
        if m:
            k, v = m.group(1), m.group(2).strip()
            if   k == "paginas":          d["paginas"]          = int(v)
            elif k == "total_excel":      d["total_excel"]      = int(v)
            elif k == "ids_unicos":       d["ids_unicos"]       = int(v)
            elif k == "etiquetas":        d["etiquetas"]        = int(v)
            elif k == "fuzzy_matches":    d["fuzzy_matches"]    = int(v)
            elif k == "recorte_matches":  d["recorte_matches"]  = int(v)
            elif k == "doble_pasada":     d["doble_pasada"]     = v == "True"
            elif k == "tasa":             d["tasa"]             = float(v)
            elif k == "semaforo":         d["semaforo"]         = v
            d["proceso_completo"] = True
            continue

        # Parámetros de ejecución
        m = re.search(r"Config cargada: (.+)", l)
        if m: d["config"] = m.group(1).strip()

        m = re.search(r"DPI=(\d+)", l)
        if m: d["dpi"] = int(m.group(1))

        m = re.search(r"PSM=(\d+)", l)
        if m: d["psm"] = int(m.group(1))

        m = re.search(r"Fuzzy=(ON|OFF)", l)
        if m: d["fuzzy_activo"] = m.group(1) == "ON"

        m = re.search(r"Fuzzy=(?:ON|OFF) \((\d+)%\)", l)
        if m: d["fuzzy_umbral"] = int(m.group(1))

        m = re.search(r"IDs: (\d+).(\d+)", l)
        if m: d["id_min"], d["id_max"] = int(m.group(1)), int(m.group(2))

        m = re.search(r"Invertir=(True|False)", l)
        if m: d["ocr_invertir"] = m.group(1) == "True"

        m = re.search(r"Error en p.gina (\d+):", l)
        if m: d["errores_pagina"].append(int(m.group(1)))

        if "Tesseract no encontrado" in l: d["tesseract_ok"] = False
        if "Excel no encontrado"     in l: d["excel_ok"]     = False
        if "Error al leer Excel"     in l: d["excel_ok"]     = False
        if "PDF no encontrado"       in l: d["pdf_ok"]       = False
        if "Error al abrir PDF"      in l: d["pdf_ok"]       = False

    return d


# ─────────────────────────────────────────────
#  Motor de diagnóstico
# ─────────────────────────────────────────────

def diagnosticar(d):
    """
    Genera hallazgos en orden estricto de prioridad y escalada:

      Nivel 1 — infraestructura rota         → bloquea todo, no hay más que hacer
      Nivel 2 — proceso no terminó           → revisar log, posible escalar
      Nivel 3 — errores en páginas puntuales → informativo
      Nivel 4 — semáforo verde               → ok + notas informativas
      Nivel 5 — tasa baja                    → pasos en orden de impacto:
                                               1 longitud IDs
                                               2 DPI
                                               3 PSM
                                               4 fuzzy umbral
                                               5 doble pasada (último recurso)
    """
    hallazgos = []

    def add(nivel, titulo, detalle, config_key=None, escalar=False):
        hallazgos.append(dict(nivel=nivel, titulo=titulo, detalle=detalle,
                               config_key=config_key, escalar=escalar))

    tasa      = d["tasa"]
    ids_u     = d["ids_unicos"] or 0
    total     = d["total_excel"] or 0
    ids_falta = max(0, total - ids_u)

    # ══════════════════════════════════════════
    # NIVEL 1 — infraestructura
    # ══════════════════════════════════════════

    if not d["tesseract_ok"]:
        add("CRITICO", "Tesseract no está instalado",
            "Ejecuta en la terminal y vuelve a correr el script:\n"
            "\n"
            "  sudo apt install tesseract-ocr tesseract-ocr-spa")
        return hallazgos

    if not d["excel_ok"]:
        add("CRITICO", "No se encontró el archivo Excel de precios",
            "Verifica que el campo excel_input en tu config apunte\n"
            "al archivo correcto dentro de la carpeta precios/\n"
            "El archivo debe ser .xlsx  (no .ods ni .xls)",
            config_key="excel_input")
        return hallazgos

    if not d["pdf_ok"]:
        add("CRITICO", "No se encontró el PDF del catálogo",
            "Verifica que el campo pdf_input en tu config apunte\n"
            "al archivo correcto dentro de la carpeta libros/",
            config_key="pdf_input")
        return hallazgos

    # ══════════════════════════════════════════
    # NIVEL 2 — proceso no terminó
    # ══════════════════════════════════════════

    if not d["proceso_completo"]:
        add("CRITICO", "El proceso se interrumpió antes de terminar",
            "El script no generó el PDF final.\n"
            "Revisa el log en diagnosticos/ — busca la línea con el error.\n"
            "Si no puedes identificarlo, comparte el output con el colaborador.",
            escalar=True)
        return hallazgos

    if tasa is None:
        return hallazgos

    # ══════════════════════════════════════════
    # NIVEL 3 — errores en páginas puntuales
    # ══════════════════════════════════════════

    if d["errores_pagina"]:
        pp = ", ".join(str(p) for p in d["errores_pagina"][:6])
        sufijo = "..." if len(d["errores_pagina"]) > 6 else ""
        add("ADVERTENCIA",
            f"Errores en {len(d['errores_pagina'])} páginas  ({pp}{sufijo})",
            "Esas páginas se incluyeron en el PDF sin etiquetas.\n"
            "Si la tasa está en verde, no es urgente.\n"
            "Si son muchas páginas o son páginas clave, comparte el log.")

    # ══════════════════════════════════════════
    # NIVEL 4 — semáforo verde
    # ══════════════════════════════════════════

    if tasa >= 85:
        add("OK", f"Efectividad {tasa:.1f}% — listo para publicar",
            "Abre el PDF en salidas/ y revisa visualmente que los precios\n"
            "aparezcan junto a los productos correctos.\n"
            "Si todo se ve bien, continúa con la Fase 3 del checklist.")

        if d["recorte_matches"] > 0:
            add("INFO", f"Recorte automático recuperó {d['recorte_matches']} IDs",
                "El OCR leyó texto extra pegado a algunos IDs y el script\n"
                "los recuperó automáticamente. No requiere ninguna acción.")

        if ids_u > 0 and d["fuzzy_matches"] / ids_u > 0.25:
            add("INFO",
                f"Fuzzy recuperó {d['fuzzy_matches']} IDs  "
                f"({d['fuzzy_matches']/ids_u*100:.0f}% del total)",
                "Alta dependencia de fuzzy. Está bien por ahora, pero si\n"
                "en corridas futuras la tasa baja, sube el DPI a 250.")
        return hallazgos

    # ══════════════════════════════════════════
    # NIVEL 5 — tasa baja: pasos en orden
    # ══════════════════════════════════════════

    # Diagnóstico base — ¿el OCR no detecta, o detecta pero no matchea?
    ocr_no_detecta = ids_u < total * 0.4 and d["fuzzy_matches"] < 5
    fuzzy_alto     = (d["fuzzy_activo"] and ids_u > 0
                      and d["fuzzy_matches"] > ids_u * 0.3)

    # ─── Paso 1 — longitud de IDs ───────────────────────────────────
    # El error más común y el más rápido de verificar
    if d["id_min"] and d["id_max"]:
        add("ADVERTENCIA" if ocr_no_detecta else "INFO",
            f"Paso 1  —  Verifica el rango de IDs del proveedor",
            f"Tu config acepta IDs de {d['id_min']} a {d['id_max']} dígitos.\n"
            f"Confirma que ese rango cubre todos los IDs del Excel:\n"
            "\n"
            "  python3 -c \"\n"
            "  import pandas as pd\n"
            "  df = pd.read_excel('precios/tu_lista.xlsx')\n"
            "  df['n'] = df['ID'].astype(str).str.len()\n"
            "  print(df.groupby('n')['ID'].count())\n"
            "  \"\n"
            "\n"
            f"Si hay IDs más largos que {d['id_max']}, actualiza\n"
            "id_longitud_max y vuelve a ejecutar.",
            config_key="id_longitud_max  /  id_longitud_min")

    # ─── Paso 2 — DPI ───────────────────────────────────────────────
    if ocr_no_detecta:
        dpi_actual = d["dpi"] or 200
        dpi_sug    = 250 if dpi_actual < 250 else 300
        add("ADVERTENCIA",
            f"Paso 2  —  Sube el DPI  ({dpi_actual} → {dpi_sug})",
            f"Con efectividad {tasa:.0f}% y pocos IDs detectados,\n"
            f"el OCR no está leyendo bien las imágenes a DPI {dpi_actual}.\n"
            "\n"
            f"En tu config cambia:   \"dpi\": {dpi_sug}\n"
            "Vuelve a ejecutar y compara la efectividad.",
            config_key="dpi")

    # ─── Paso 3 — PSM ───────────────────────────────────────────────
    if ocr_no_detecta and d["psm"] == 6:
        add("INFO",
            "Paso 3  —  Prueba un PSM diferente",
            "PSM 6 funciona bien con texto en bloques uniformes.\n"
            "Si el catálogo tiene fotos de página completa o IDs dispersos:\n"
            "\n"
            "  \"psm\": 11   ← texto disperso  (prueba primero)\n"
            "  \"psm\": 4    ← columnas de texto\n"
            "\n"
            "Vuelve a ejecutar con cada opción y compara.",
            config_key="psm")

    # ─── Paso 4 — fuzzy umbral ──────────────────────────────────────
    if fuzzy_alto:
        add("ADVERTENCIA",
            f"Paso 4  —  Revisa los precios marcados con fuzzy  "
            f"({d['fuzzy_matches']} IDs, umbral {d['fuzzy_umbral']}%)",
            "Con tasa baja y muchos fuzzy hay riesgo de que algunos\n"
            "precios no correspondan al producto correcto.\n"
            "\n"
            "Antes de publicar: abre el PDF y revisa visualmente\n"
            "que los precios coincidan con los productos.\n"
            "\n"
            "Si encuentras errores, sube el umbral o desactiva fuzzy:\n"
            f"  \"fuzzy_umbral\": 90\n"
            "  \"fuzzy_activo\": false",
            config_key="fuzzy_umbral  /  fuzzy_activo")

    # ─── Paso 5 — doble pasada (último recurso) ─────────────────────
    if not d["doble_pasada"] and ocr_no_detecta:
        add("INFO",
            "Paso 5  —  ¿Hay IDs en recuadros oscuros?",
            "Si en el PDF hay números con texto claro sobre fondo gris\n"
            "o negro (no solo negro sobre blanco), activa la doble pasada:\n"
            "\n"
            "  \"ocr_doble_pasada\": true\n"
            "\n"
            "Cómo verificar: abre el PDF original y busca si los IDs\n"
            "aparecen dentro de recuadros de color.\n"
            "Si no los hay, este paso no aplica.\n"
            "Duplica el tiempo de proceso.",
            config_key="ocr_doble_pasada")

    elif d["doble_pasada"] and tasa < 65:
        add("INFO",
            "Paso 5  —  Doble pasada activa pero la tasa sigue baja",
            "Ya tienes la doble pasada activa. Si persiste el problema:\n"
            "\n"
            "  · ¿El Excel y el catálogo son del mismo proveedor\n"
            "    y la misma temporada?\n"
            "  · ¿El PDF tiene buena calidad de imagen?\n"
            "\n"
            "Si revisaste todo lo anterior, comparte el output con el colaborador del proyecto.",
            escalar=True)

    # ─── Amarillo — revisión visual ─────────────────────────────────
    if 65 <= tasa < 85:
        add("ADVERTENCIA",
            f"Efectividad {tasa:.1f}%  —  faltan {ids_falta} IDs",
            "Abre el PDF y responde estas preguntas:\n"
            "\n"
            "  ¿Hay páginas completas sin ningún precio?\n"
            "  → Prueba el Paso 2 (DPI)\n"
            "\n"
            "  ¿Los precios aparecen pero en posición incorrecta?\n"
            "  → Ajusta los offsets en el configurador visual\n"
            "\n"
            "  ¿Los precios se ven bien en casi todas las páginas?\n"
            "  → Puede ser aceptable según el proveedor",
            config_key="dpi  /  etiqueta_offset_x_pt  /  etiqueta_offset_y_pt")

    return hallazgos


# ─────────────────────────────────────────────
#  Imprimir reporte
# ─────────────────────────────────────────────

def imprimir_reporte(d, hallazgos):
    SEP  = "─" * 56
    SEP2 = "═" * 56

    # ── Encabezado ────────────────────────────────────────────
    print(f"\n{BD}{SEP2}{RS}")
    print(f"{BD}  DIAGNÓSTICO  ·  Boutique Zepeda  ·  books-label{RS}")
    print(f"{BD}{SEP2}{RS}")
    print(f"\n{DM}  Log    : {os.path.basename(d['ruta'])}{RS}")
    if d["config"]:
        print(f"{DM}  Config : {d['config']}{RS}")

    # ── Resumen ───────────────────────────────────────────────
    print(f"\n{BD}  Resumen{RS}")
    print(f"  {SEP}")

    if d["proceso_completo"] and d["tasa"] is not None:
        tasa    = d["tasa"]
        total   = d["total_excel"] or 0
        ids_u   = d["ids_unicos"]  or 0
        falta   = max(0, total - ids_u)
        bloques = int(tasa / 5)
        barra   = "█" * bloques + "░" * (20 - bloques)
        ct = G if tasa >= 85 else (Y if tasa >= 65 else R)
        sem = {"VERDE":    f"{G}🟢  VERDE — listo para publicar{RS}",
               "AMARILLO": f"{Y}🟡  AMARILLO — revisar antes de publicar{RS}",
               "ROJO":     f"{R}🔴  ROJO — no publicar{RS}"}.get(d["semaforo"], "—")

        def fila(lbl, val, c=""):
            print(f"  {DM}{lbl:<22}{RS}{c}{val}{RS}")

        fila("Páginas",              d["paginas"] or "—")
        fila("En Excel",             total)
        fila("IDs marcados",
             f"{ids_u} / {total}   (faltan {falta})",
             Y if falta > 0 else G)
        fila("Etiquetas",            d["etiquetas"] or "—")
        if d["recorte_matches"]:
            fila("Recortes auto",    d["recorte_matches"])
        if d["fuzzy_matches"]:
            fila("Fuzzy matches",    d["fuzzy_matches"])
        fila("Doble pasada",         "Sí" if d["doble_pasada"] else "No")
        print()
        print(f"  {DM}Efectividad{RS}   {ct}[{barra}] {tasa:.1f}%{RS}")
        print(f"  {DM}Resultado  {RS}   {sem}")
    else:
        print(f"  {R}Proceso incompleto — no hay métricas disponibles.{RS}")

    # ── Parámetros ────────────────────────────────────────────
    print(f"\n{BD}  Parámetros usados{RS}")
    print(f"  {SEP}")
    for lbl, val in [
        ("DPI",            d["dpi"]),
        ("PSM",            d["psm"]),
        ("IDs",            f"{d['id_min']}–{d['id_max']} dígitos" if d["id_min"] else "—"),
        ("Fuzzy",          f"{'ON' if d['fuzzy_activo'] else 'OFF'}  umbral {d['fuzzy_umbral']}%"
                           if d["fuzzy_activo"] is not None else "—"),
        ("OCR invertido",  "Sí" if d["ocr_invertir"] else "No"),
        ("Doble pasada",   "Sí" if d["doble_pasada"] else "No"),
    ]:
        print(f"  {DM}{lbl:<18}{RS}{val}")

    # ── Hallazgos ─────────────────────────────────────────────
    hay_escalar = any(h["escalar"] for h in hallazgos)

    print(f"\n{BD}  Pasos a seguir{RS}")
    print(f"  {SEP}")

    if not hallazgos:
        print(f"\n  {G}Sin problemas detectados.{RS}")
    else:
        for h in hallazgos:
            color = NIVEL_COLOR.get(h["nivel"], "")
            icono = NIVEL_ICONO.get(h["nivel"], "·")
            print()
            print(f"  {icono}  {color}{BD}{h['titulo']}{RS}")
            for linea in h["detalle"].split("\n"):
                print(f"       {DM}{linea}{RS}")
            if h["config_key"]:
                print(f"       {BD}Config:{RS} {h['config_key']}")

    # ── Pie ───────────────────────────────────────────────────
    print(f"\n  {SEP}")
    if hay_escalar:
        print(f"\n  {R}{BD}⚠️   Comparte este output con tu colaborador{RS}")
        print(f"  {DM}Copia todo el texto de esta pantalla y pégalo en el chat.{RS}")
    else:
        print(f"  {DM}Prueba los pasos en orden — empieza por el Paso 1.{RS}")
        print(f"  {DM}Si la tasa sube a verde, no necesitas compartir esto.{RS}")

    print(f"\n{BD}{SEP2}{RS}\n")


# ─────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────

if __name__ == "__main__":
    args     = parse_args()
    BASE     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ruta_log = encontrar_log(BASE, args.log)
    print(f"\n{DM}Analizando: {os.path.basename(ruta_log)}{RS}")
    datos     = parsear_log(ruta_log)
    hallazgos = diagnosticar(datos)
    imprimir_reporte(datos, hallazgos)
