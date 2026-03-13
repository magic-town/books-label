# 📝 Notas operativas — Boutique Zepeda

Referencia rápida para el día a día. Sin formalidades.

---
## Guía ⚡ rápida de ejecución diaria para Git

**Al iniciar tu jornada, sincroniza los cambios remotos** que se realizaron desde otro equipo:
```bash
git pull https://magic-town@github.com/magic-town/books-label.git main
```

Cuando realices cambios significativos —como modificar una configuración, agregar una dependencia o crear un directorio— o al finalizar tu día, antes de cerrar tus aplicaciones, sube tus cambios a Git:

### Git add — registra tus cambios en el área de preparación:
```bash
git add .
```

Crea un commit para documentar qué cambiaste y dejar tus cambios listos para subir:
```bash
git commit -m "test de config para catálogo <X>"
```

## 📌 Git push

En este equipo, el push siempre se hace con la URL completa:
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

### 🔵 Price Shoes

**Botas 25-26(01-mar)**
- Dropbox: `https://www.dropbox.com/scl/fi/9cvsgyargxitupg7eswck/botas_25_26_final.pdf?rlkey=dg6a4sr71wk6mc1epc9sehq8v&st=9lbtsp2p&dl=1`
- Bitly: `https://bit.ly/PS_Botas_25-_26`

**Caballeros (01-mar)**
- Dropbox: `https://www.dropbox.com/scl/fi/mmb1wrvnv8bxk8t9m5h8r/caballeros_25_26.pdf?rlkey=wjlv7oc1cdv2a0vt6u8ow0arx&st=6qjhys93&dl=1`
- Bitly: `https://bit.ly/PS_Caballeros_25_26`

**Importados**
- Dropbox: `https://www.dropbox.com/scl/fi/s7qq1u0qn9vhvfgjt37y8/imp_spring_26_final.pdf?rlkey=u1l8s9jh77jw8uk8j4dhgv39r&st=q5fjrh1b&dl=1`
- Bitly: `https://bit.ly/ps_importados`

**Confort**
- Dropbox: `https://www.dropbox.com/scl/fi/yw749zjadujsxu6g6z47y/confort_26_final.pdf?rlkey=ugcjoeefefc9zw49p3st=sspuri6k&dl=1`
- Bitly: `https://bit.ly/ps_confort`

**Sandalias**
- Dropbox: `https://www.dropbox.com/scl/fi/p681fiurjxutp9bw2hfnk/sandalias_final.pdf?rlkey=jxudboz7nmi9ohif3tjnypo3d&st=8kg1i7pz&dl=1`
- Bitly: `https://bit.ly/PS_Sandalias`

**Jeans**
- Dropbox: `https://www.dropbox.com/scl/fi/i4wyg6quq34iumnvpyw7k/jeans_final.pdf?rlkey=8q4c78q2gf5gc3aihkpilaqit&st=ce3cjkfj&dl=1`
- Bitly: `https://bit.ly/PS_Jeans`

**Urbano**
- Dropbox: https://www.dropbox.com/scl/fi/ec77vg2xgzh3ytii8id4l/urbano_26_final.pdf?rlkey=npw7guudx5xt2manymdjshazo&st=psdmrgpt&dl=1
- Bitly: https://bit.ly/PS_Urbano


**Basicos**
- Dropbox: https://www.dropbox.com/scl/fi/vhzsuja9dns1lj45ey4ah/basicos_26_final.pdf?rlkey=17qgtf3gvz1ddnbwezglspsy2&st=e0gxqr6b&dl=1
- Bitly: https://bit.ly/4rxNeIF 

--
## 🔴 Cklass

**HANGBAGS**
- Dropbox: `https://www.dropbox.com/scl/fi/9x747f0ldcvrchsekrclk/CKLASS_BOLSO_LENTES.pdf?rlkey=h0vqv9pu2fe4dx313mjrc19vg&st=gu4gba13&dl=1`
- Bi^y: `https://bit.ly/4aXuvjv`

**Fahion-Dama**
- Dropbox: `https://www.dropbox.com/scl/fi/6jku3cpj3p3avucvvl3b5/CKLASS_FASHION_DAMA.pdf?rlkey=dfc8czvu0xobcxnztsqf2v2xg&st=6isavcka&dl=1`
- Bitly: `https://bit.ly/3OArqyD`

**Secrets**
- Dropbox: `https://www.dropbox.com/scl/fi/vtscwyk2c3fg24ugyy9x8/CKLASS_LENCER-A_PV26.pdf?rlkey=n3bwhovzeqklrsxwh8p3phk69&st=v5ds7jc7&dl=1`
- Bitly: `https://bit.ly/Cklass_Secret`
