#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
diagnostico.py — Lector de logs para Boutique Zepeda
Analiza el último log generado en diagnosticos/ y produce un reporte accionable.

Uso:
    python3 scripts/diagnostico.py
"""

import os
import re
import sys
import glob
from datetime import datetime


# ─────────────────────────────────────────────
#  Localizar el log más reciente
# ─────────────────────────────────────────────

def encontrar_ultimo_log(base_dir: str) -> str:
    patron = os.path.join(base_dir, "diagnosticos", "*.log")
    logs   = sorted(glob.glob(patron), key=os.path.getmtime, reverse=True)

    if not logs:
        print("❌ No se encontró ningún log en diagnosticos/")
        print("   Asegúrate de haber ejecutado catalogo_base.py al menos una vez.")
        sys.exit(1)

    return logs[0]


# ─────────────────────────────────────────────
#  Parsear el log
# ─────────────────────────────────────────────

def parsear_log(log_path: str) -> dict:
    with open(log_path, "r", encoding="utf-8") as f:
        contenido = f.read()

    datos = {}

    # Métricas principales
    for patron, clave in [
        (r"Páginas procesadas\s*:\s*(\d+)",      "paginas"),
        (r"Registros en Excel\s*:\s*(\d+)",      "total_excel"),
        (r"IDs únicos marcados\s*:\s*(\d+)",     "ids_unicos"),
        (r"Etiquetas insertadas\s*:\s*(\d+)",    "etiquetas"),
        (r"Fuzzy matches\s*:\s*(\d+)",           "fuzzy"),
        (r"Efectividad\s*:\s*([\d.]+)%",         "efectividad"),
    ]:
        m = re.search(patron, contenido)
        datos[clave] = float(m.group(1)) if m else None

    # Semáforo
    if "🟢 VERDE"    in contenido: datos["semaforo"] = "verde"
    elif "🟡 AMARILLO" in contenido: datos["semaforo"] = "amarillo"
    elif "🔴 ROJO"    in contenido: datos["semaforo"] = "rojo"
    else:                            datos["semaforo"] = "desconocido"

    # Config usada
    m = re.search(r"Config cargada:\s*(.+)", contenido)
    datos["config"] = m.group(1).strip() if m else "no registrada"

    # Parámetros OCR registrados al inicio
    m = re.search(r"DPI=(\d+).*PSM=(\d+).*Fuzzy=(ON|OFF)\s*\((\d+)%\).*IDs:\s*(\d+)–(\d+)", contenido)
    if m:
        datos["dpi"]        = int(m.group(1))
        datos["psm"]        = int(m.group(2))
        datos["fuzzy_on"]   = m.group(3) == "ON"
        datos["fuzzy_umbral"] = int(m.group(4))
        datos["id_min"]     = int(m.group(5))
        datos["id_max"]     = int(m.group(6))
    else:
        datos["dpi"] = datos["psm"] = datos["fuzzy_umbral"] = None
        datos["fuzzy_on"] = None
        datos["id_min"] = datos["id_max"] = None

    # Errores por página
    errores = re.findall(r"Error en página (\d+): (.+)", contenido)
    datos["errores"] = errores

    return datos


# ─────────────────────────────────────────────
#  Generar recomendaciones
# ─────────────────────────────────────────────

def generar_recomendaciones(datos: dict) -> list:
    recs = []
    ef   = datos.get("efectividad")

    if ef is None:
        recs.append("⚠️  No se pudo leer la efectividad. El log puede estar incompleto.")
        return recs

    # Fuzzy matches altos respecto al total → OCR con errores frecuentes
    fuzzy    = datos.get("fuzzy") or 0
    etiquetas = datos.get("etiquetas") or 0
    if etiquetas > 0 and (fuzzy / etiquetas) > 0.3:
        recs.append(
            f"🔍 El {fuzzy/etiquetas*100:.0f}% de las etiquetas son fuzzy matches. "
            "El OCR tiene dificultades con este catálogo. "
            "Prueba subir el DPI a 250 o ajustar contraste/nitidez en el config."
        )

    # Efectividad baja con fuzzy activo → bajar umbral o revisar IDs
    if ef < 85 and datos.get("fuzzy_on"):
        if (datos.get("fuzzy_umbral") or 85) >= 85:
            recs.append(
                f"📉 Efectividad {ef:.1f}% con fuzzy activo al {datos.get('fuzzy_umbral')}%. "
                "Prueba bajar fuzzy_umbral a 80 en el config. "
                "Si baja más de 5 puntos al hacerlo, el problema es otro."
            )

    # Efectividad baja con fuzzy inactivo
    if ef < 85 and not datos.get("fuzzy_on"):
        recs.append(
            f"📉 Efectividad {ef:.1f}% con fuzzy desactivado. "
            "Activa fuzzy_activo: true en el config como primer paso."
        )

    # Rango de IDs — puede estar descartando IDs válidos
    if datos.get("id_max") and datos["id_max"] <= 8:
        recs.append(
            f"📏 El filtro de longitud de IDs está en {datos['id_min']}–{datos['id_max']} dígitos. "
            "Si el proveedor usa IDs de 9 o 10 caracteres los está descartando. "
            "Revisa la columna 'len' en el Excel para confirmar."
        )

    # PSM 6 — no siempre es el mejor
    if datos.get("psm") == 6 and ef < 75:
        recs.append(
            "🔧 El modo PSM 6 asume texto en bloque uniforme. "
            "Si el catálogo tiene columnas o layout irregular, prueba PSM 4 o PSM 11 en el config."
        )

    # Errores por página
    if datos.get("errores"):
        n = len(datos["errores"])
        recs.append(
            f"❌ Se registraron {n} error(es) en páginas específicas. "
            "Ver detalle de errores abajo. Si son páginas con imágenes complejas es normal en baja proporción."
        )

    # Sin recomendaciones
    if not recs:
        if ef >= 85:
            recs.append("✅ Sin observaciones. La ejecución fue limpia.")
        else:
            recs.append(
                "⚠️  Efectividad baja sin causa clara en el log. "
                "Comparte este reporte con el coach para revisión."
            )

    return recs


# ─────────────────────────────────────────────
#  Imprimir reporte
# ─────────────────────────────────────────────

def imprimir_reporte(log_path: str, datos: dict, recomendaciones: list):
    timestamp_log = datetime.fromtimestamp(os.path.getmtime(log_path)).strftime("%d/%m/%Y %H:%M")
    nombre_log    = os.path.basename(log_path)

    semaforos = {
        "verde":       "🟢 VERDE",
        "amarillo":    "🟡 AMARILLO",
        "rojo":        "🔴 ROJO",
        "desconocido": "⚪ DESCONOCIDO"
    }

    print()
    print("=" * 62)
    print("  DIAGNÓSTICO — Boutique Zepeda · Taller de Etiquetado")
    print("=" * 62)
    print(f"  Log analizado : {nombre_log}")
    print(f"  Ejecutado el  : {timestamp_log}")
    print(f"  Config usada  : {datos.get('config', 'no registrada')}")
    print("-" * 62)

    # Métricas
    print("  MÉTRICAS")
    print(f"  {'Páginas procesadas':<30} {int(datos['paginas']) if datos['paginas'] else '—'}")
    print(f"  {'Registros en Excel':<30} {int(datos['total_excel']) if datos['total_excel'] else '—'}")
    print(f"  {'IDs únicos marcados':<30} {int(datos['ids_unicos']) if datos['ids_unicos'] else '—'}")
    print(f"  {'Etiquetas insertadas':<30} {int(datos['etiquetas']) if datos['etiquetas'] else '—'}")
    print(f"  {'Fuzzy matches':<30} {int(datos['fuzzy']) if datos['fuzzy'] else '—'}")
    print(f"  {'Efectividad':<30} {datos['efectividad']:.1f}%" if datos['efectividad'] else f"  {'Efectividad':<30} —")
    print(f"  {'Resultado':<30} {semaforos.get(datos['semaforo'], '⚪')}")
    print("-" * 62)

    # Parámetros usados
    print("  PARÁMETROS OCR USADOS")
    if datos.get("dpi"):
        fuzzy_str = f"{'ON' if datos['fuzzy_on'] else 'OFF'} ({datos['fuzzy_umbral']}%)"
        id_str    = f"{datos['id_min']}–{datos['id_max']} dígitos"
        print(f"  {'DPI':<30} {datos['dpi']}")
        print(f"  {'PSM':<30} {datos['psm']}")
        print(f"  {'Fuzzy matching':<30} {fuzzy_str}")
        print(f"  {'Rango IDs':<30} {id_str}")
    else:
        print("  No disponibles en este log.")
    print("-" * 62)

    # Recomendaciones
    print("  RECOMENDACIONES")
    for r in recomendaciones:
        print(f"  {r}")
    print("-" * 62)

    # Errores por página
    if datos.get("errores"):
        print("  ERRORES POR PÁGINA")
        for pagina, mensaje in datos["errores"]:
            print(f"  Página {pagina}: {mensaje}")
        print("-" * 62)

    print()


# ─────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────

if __name__ == "__main__":
    BASE    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_path = encontrar_ultimo_log(BASE)
    datos    = parsear_log(log_path)
    recs     = generar_recomendaciones(datos)
    imprimir_reporte(log_path, datos, recs)
