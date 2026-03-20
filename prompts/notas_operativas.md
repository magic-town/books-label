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
- Dropbox: `https://www.dropbox.com/scl/fi/d98t61pp6c39yr9frw4kd/importados_precios.pdf?rlkey=ku6y7ahxdt1jnysi4yjv320ix&st=swmhcqhl&dl=1`
- Bitly: `https://bit.ly/ps_importados`

**Confort**
- Dropbox: `https://www.dropbox.com/scl/fi/od9gsqxm1oul94xt4hx8n/confort_precios.pdf?rlkey=47f1i9e0bi2x2xwiw9nsq8kul&st=enbv5qiz&dl=1`
- Bitly: `https://bit.ly/confort_26`

**Sandalias**
- Dropbox: `https://www.dropbox.com/scl/fi/9il6j33plgpq6qyqi42bm/sandalias_precios.pdf?rlkey=8vytadcsjbn8781k19a1h3gux&st=50nj9g27&dl=1`
- Bitly: `https://bit.ly/PS_Sandalias`

**Jeans**
- Dropbox: `https://www.dropbox.com/scl/fi/1mn1kdtaos8mx9rsv08e4/jeans_precios.pdf?rlkey=o0zxog7s4p95wjgtqyz72ayj1&st=69a7d9q2&dl=1`
- Bitly: `https://bit.ly/sandalias_26`

**Urbano**
- Dropbox: `https://www.dropbox.com/scl/fi/zyc29sqbo9l1nidzj6uhs/urbano_precios.pdf?rlkey=27qtxbz83dhh13655efygk8lo&st=k94575uc&dl=1`
- Bitly: `https://bit.ly/urbano_26`


**Basicos**
- Dropbox: `https://www.dropbox.com/scl/fi/31kpn7b3bmmx6ye4vli0m/basicos_precios.pdf?rlkey=p5xl7ncnj6uram6jnebdrta6l&st=k3rb4bqb&dl=1`
- Bitly: `https://bit.ly/3NMr1c6`

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
