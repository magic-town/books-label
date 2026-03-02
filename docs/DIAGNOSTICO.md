# DIAGNÓSTICO — Guía de resultados y resolución de problemas

**Propósito:** Evaluar si el catálogo quedó bien, entender qué salió mal
y tener la información correcta para resolver o escalar sin adivinanzas.

---

## 1. Regla de oro

> Si el PDF se ve bien pero la efectividad es baja → hay un problema.
> Si la efectividad es alta pero el PDF se ve mal → también hay un problema.
> Ambas fuentes deben coincidir antes de publicar.

---

## 2. El semáforo

Al terminar cada ejecución el script muestra el resultado en consola:

| Resultado | Acción inmediata |
|-----------|-----------------|
| 🟢 VERDE — 85% o más | Publicar en WhatsApp Business |
| 🟡 AMARILLO — 65% a 84% | Ejecutar `diagnostico.py` antes de publicar |
| 🔴 ROJO — menos de 65% | No publicar — ejecutar `diagnostico.py` y escalar al coach |

La efectividad se calcula automáticamente:
```
IDs únicos marcados ÷ total de registros en Excel × 100
```

---

## 3. Primer paso ante amarillo o rojo

Ejecutar desde VSC o terminal:

```bash
python3 scripts/diagnostico.py
```

El script lee el log de la última ejecución y produce un reporte como este:

```
==============================================================
  DIAGNÓSTICO — Boutique Zepeda · Taller de Etiquetado
==============================================================
  Log analizado : config_jeans_PV26_20260215_143022.log
  Ejecutado el  : 15/02/2026 14:30
  Config usada  : configs/config_jeans_PV26.json
--------------------------------------------------------------
  MÉTRICAS
  Páginas procesadas             42
  Registros en Excel             318
  IDs únicos marcados            198
  Etiquetas insertadas           210
  Fuzzy matches                  42
  Efectividad                    62.3%
  Resultado                      🔴 ROJO
--------------------------------------------------------------
  PARÁMETROS OCR USADOS
  DPI                            200
  PSM                            6
  Fuzzy matching                 ON (85%)
  Rango IDs                      4–8 dígitos
--------------------------------------------------------------
  RECOMENDACIONES
  🔍 El 20% de las etiquetas son fuzzy matches. El OCR tiene
     dificultades con este catálogo. Prueba subir DPI a 250.
  📏 El filtro de longitud está en 4–8 dígitos. Si el proveedor
     usa IDs de 9 o 10 caracteres los está descartando.
     Revisa la columna 'len' en el Excel para confirmar.
--------------------------------------------------------------
```

El reporte indica exactamente qué revisar. No es necesario interpretar el log manualmente.

---

## 4. Dónde están los logs

Cada ejecución genera un archivo de log con timestamp en:

```
~/books-label/diagnosticos/
```

El nombre del archivo incluye el catálogo y la hora exacta, por ejemplo:
```
config_jeans_PV26_20260215_143022.log
```

Esto permite comparar dos ejecuciones del mismo catálogo con distintos parámetros.

---

## 5. Qué significa cada parámetro del config

Cuando el reporte de `diagnostico.py` sugiere cambiar algo, aquí está el contexto:

### DPI
Resolución a la que se convierte cada página del PDF antes de leerla.
- Valor actual típico: `200`
- Si el OCR no detecta bien los IDs → subir a `250`
- Subir el DPI aumenta el tiempo de procesamiento

### PSM — Modo de segmentación de Tesseract
Le dice al OCR cómo espera que esté organizado el texto en la página.
- `6` → texto en bloque uniforme (el más común)
- `4` → texto en columna única con posible layout variable
- `11` → texto disperso sin estructura fija
- Cambiar PSM cuando las páginas tienen un layout muy irregular o columnas

### Contraste y nitidez
Preprocesado de la imagen antes del OCR.
- Valores actuales: contraste `2.5`, nitidez `2.0`
- Si el PDF es de baja calidad o los IDs tienen fondo oscuro → subir contraste
- Cambiar con moderación, valores muy altos pueden degradar la lectura

### id_longitud_min / id_longitud_max
Filtra los números detectados por cantidad de dígitos.
- Valor actual: `4` a `8`
- Si el proveedor usa IDs de 9 o 10 dígitos → ajustar `id_longitud_max`
- Verificar la columna `len` en el Excel antes de cambiar

### fuzzy_umbral
Tolerancia para aceptar IDs con errores de OCR.
- Valor actual: `85` (un carácter diferente en un ID de 7 dígitos equivale al 14%)
- Si hay muchos IDs sin reconocer → bajar a `80`
- No bajar de `75` sin revisar el resultado visualmente, puede generar precios incorrectos

### etiqueta_offset_x_pt / etiqueta_offset_y_pt
Posición del precio respecto al ID detectado, en puntos PDF (1mm ≈ 2.835 puntos).
- Si los precios aparecen desplazados → ajustar estos valores
- Hacer prueba con las primeras 10 páginas antes de procesar el catálogo completo

---

## 6. Revisión visual del PDF

Independientemente del semáforo, abrir el PDF de salida en `salidas/` y verificar:

- [ ] ¿Los precios aparecen junto a los productos?
- [ ] ¿Están en la posición correcta, sin encimarse con texto?
- [ ] ¿El formato es correcto? (ej. `$250.00`)
- [ ] ¿Hay páginas completas sin ningún precio?

---

## 7. Errores comunes

| Lo que se ve | Causa probable | Qué revisar en el config |
|--------------|---------------|--------------------------|
| Muy pocas etiquetas en todo el catálogo | DPI bajo o imagen muy oscura | Subir `dpi` a 250 |
| Precios desplazados o fuera de lugar | Offsets desajustados para este PDF | Ajustar `etiqueta_offset_x_pt` y `etiqueta_offset_y_pt` |
| IDs detectados pero precio $0.00 | ID no está en el Excel | Revisar Fase 1 del CHECKLIST |
| Páginas sin ningún precio | Layout diferente al resto del catálogo | Probar `psm` 4 u 11 |
| Fuzzy matches mayor al 30% | OCR con baja calidad | Subir `dpi`, revisar contraste |
| IDs de 9+ dígitos no marcados | Rango de longitud muy corto | Ajustar `id_longitud_max` |

---

## 8. Cuándo escalar al coach

Escalar con el reporte de `diagnostico.py` en mano cuando:

- La efectividad es roja después de dos iteraciones con distintos parámetros
- Los precios aparecen en posiciones incorrectas y ajustar los offsets no resuelve
- El reporte muestra errores en múltiples páginas sin causa clara
- Es un proveedor completamente nuevo con formato distinto a los anteriores
