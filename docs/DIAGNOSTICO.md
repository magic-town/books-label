# DIAGNÓSTICO — Cómo leer el resultado y reportar fallas

**Propósito:** Que la analista pueda evaluar si el catálogo quedó bien,
identificar qué salió mal, y reportarlo con la información correcta
para que el desarrollador pueda corregirlo sin adivinanzas.

---

## 1. ¿Dónde está el log?

Cada vez que ejecutas el script, se genera un archivo de log en:

```
~/taller_etiquetado/diagnosticos/procesamiento_mejorado.log
```

También aparece en la terminal o en VSC mientras corre el script.

---

## 2. ¿Qué significan las métricas?

Al terminar la ejecución verás algo como esto:

```
✅ ¡PROCESO MEJORADO TERMINADO!
🏷️  Etiquetas insertadas: 142
🔢 IDs únicos encontrados: 138
🔄 Fuzzy matches aplicados: 4
📄 Páginas procesadas: 48
📂 Archivo generado: salidas/cat_proveedor_2026.pdf
```

| Métrica | Qué significa | ¿Es bueno? |
|--------|--------------|------------|
| Etiquetas insertadas | Precios colocados en el PDF | Cuanto más alto, mejor |
| IDs únicos encontrados | Productos distintos detectados | Debe acercarse al total de la lista |
| Fuzzy matches | IDs corregidos automáticamente por OCR | Normal hasta 10-15% |
| Páginas procesadas | Páginas del catálogo procesadas | Debe ser el total del PDF |

---

## 3. ¿Cómo sé si el resultado es aceptable?

### Paso 1 — Calcular eficiencia

```
Eficiencia = (IDs únicos encontrados ÷ Total de IDs en lista) × 100
```

Ejemplo: 138 encontrados de 180 en lista → 138 ÷ 180 × 100 = **76.6%**

| Eficiencia | Decisión |
|-----------|---------|
| 90% o más | ✅ Publicar |
| 80% – 89% | ⚠️ Revisar páginas con fallas antes de publicar |
| Menos de 80% | ❌ No publicar — reportar diagnóstico |

### Paso 2 — Revisar el PDF visualmente

Abrir el PDF de salida en `salidas/` y revisar:

- [ ] ¿Los precios aparecen junto a los productos?
- [ ] ¿Están en la posición correcta (no encimados, no muy lejos)?
- [ ] ¿Los precios tienen el formato correcto? (ej. `$250.00`)
- [ ] ¿Hay páginas completamente sin precios?

---

## 4. ¿Qué reportar cuando algo falla?

Si la eficiencia es menor al 80% o el PDF no se ve bien, reportar lo siguiente:

```
REPORTE DE FALLA — [fecha] — [proveedor]

1. Eficiencia calculada: ____%
   (IDs encontrados: ___ / Total en lista: ___)

2. ¿Qué se ve mal en el PDF?
   Ejemplo: "Los precios aparecen en la esquina superior, no junto al producto"
   Ejemplo: "Las páginas 12 a 20 no tienen ningún precio"
   Ejemplo: "El precio aparece pero con número incorrecto"

3. ¿El PDF del catálogo tiene texto seleccionable?
   ( ) Sí   ( ) No

4. Largo del ID en la lista de precios: ___ caracteres
   Ejemplo de ID: ___________

5. Últimas líneas del log (copiar desde el archivo .log):
```

---

## 5. Errores comunes y su causa

| Lo que ves | Causa probable |
|-----------|---------------|
| Muy pocas etiquetas en todo el catálogo | DPI bajo o imagen muy oscura |
| Precios fuera de lugar (desplazados) | Coordenadas del script desajustadas para este PDF |
| IDs detectados pero precio = $0.00 | ID no encontrado en la lista de precios — revisar Fase 1 |
| Páginas sin ningún precio | Formato de página diferente al resto del catálogo |
| Fuzzy matches > 20% | OCR con baja calidad — posible ajuste de DPI necesario |

---

## 6. Regla de oro

> Si el PDF se ve bonito pero el log dice eficiencia baja, **hay un problema**.
> Si el log dice eficiencia alta pero el PDF se ve mal, **también hay un problema**.
> Ambas fuentes deben coincidir antes de publicar.
