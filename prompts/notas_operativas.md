# Notas operativas — Boutique Zepeda

Referencia rápida para el día a día. Sin formalidades.

---

## 📌 Git push

En este equipo el push siempre va con la URL completa:

```bash
git push https://magic-town@github.com/magic-town/books-label.git main
```

---

## 🏷️ Mover la etiqueta de precio

Cuando el precio aparece desplazado, los dos parámetros a ajustar en el archivo
de configuración `configs/<nombre>.json` son:

```json
"etiqueta_offset_x_pt": 4.0,
"etiqueta_offset_y_pt": 5.67
```

La unidad es puntos PDF. Referencia rápida: **1 mm = 2.835 puntos**.

### ¿Hacia dónde muevo?

| Quiero mover el precio... | Qué hacer |
|---------------------------|-----------|
| Más a la derecha ▶ | Subir `offset_x` |
| Más a la izquierda ◀ | Bajar `offset_x` |
| Más arriba ▲ | Subir `offset_y` |
| Más abajo ▼ | Bajar `offset_y` |

### Situaciones comunes

**Precio bien posicionado — 2mm a la derecha del ID:**
```
1234   $150.00
↑      ↑
ID     precio empieza aquí
```
Config: `offset_x` en valores positivos pequeños (2–6 pt), `offset_y` cerca de 5.

**Precio encimado sobre el ID:**
```
$150.00
↑
tapando el 1234
```
Config: `offset_x` está demasiado bajo o negativo — subir hasta que se separe.

**Precio muy lejos o fuera de la página:**
Config: `offset_x` o `offset_y` demasiado alto — bajar de a 5 puntos (~2mm) hasta acomodar.

> 💡 Hacer siempre prueba con las primeras 10 páginas antes de procesar el catálogo completo.
> Ver `docs/DIAGNOSTICO.md` sección 5 para referencia técnica completa.

---

## 🔗 Historial de links publicados

### Caballeros (01-mar)
- Dropbox: `https://www.dropbox.com/scl/fi/mmb1wrvnv8bxk8t9m5h8r/caballeros_25_26.pdf?rlkey=wjlv7oc1cdv2a0vt6u8ow0arx&st=6qjhys93&dl=1`
- Bitly: `https://bit.ly/PS_Caballeros_25_26`

### Importados
- Dropbox: `https://www.dropbox.com/scl/fi/s7qq1u0qn9vhvfgjt37y8/imp_spring_26_final.pdf?rlkey=u1l8s9jh77jw8uk8j4dhgv39r&st=q5fjrh1b&dl=1`
- Bitly: `https://bit.ly/ps_importados`

### Confort
- Dropbox: `https://www.dropbox.com/scl/fi/yw749zjadujsxu6g6z47y/confort_26_final.pdf?rlkey=ugcjoeefefc9zw49p3st=sspuri6k&dl=1`
- Bitly: `https://bit.ly/ps_confort`

### Sandalias
- Dropbox: `https://www.dropbox.com/scl/fi/p681fiurjxutp9bw2hfnk/sandalias_final.pdf?rlkey=jxudboz7nmi9ohif3tjnypo3d&st=8kg1i7pz&dl=1`
- Bitly: `https://bit.ly/PS_Sandalias`
