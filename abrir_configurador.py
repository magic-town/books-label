#!/usr/bin/env python3
"""
abrir_configurador.py — Abre el configurador visual en el navegador.

Uso:
    python3 abrir_configurador.py
"""
import os
import webbrowser

BASE = os.path.dirname(os.path.abspath(__file__))
ruta = os.path.join(BASE, "configurador.html")

if not os.path.exists(ruta):
    print("❌ No se encontró configurador.html en la raíz del proyecto.")
else:
    webbrowser.open(f"file://{ruta}")
    print("✅ Configurador abierto en el navegador.")
    print("   Cuando termines de revisar los parámetros, edita tu config en VSC.")
