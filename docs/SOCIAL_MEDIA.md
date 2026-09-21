# Catálogo de prompt para publicaciones en redes sociales (Fb, Whatsapp, IG).

<div align="center">
  <img src="../imagenes/asset_repo/cover_estados.png" 
       alt="Cover - Estados"
       width="75%"/>
</div>

<br>

## Guardar la foto cruda, 📸 la que tomas con tu celular.

Una vez que tengas la foto de la prenda con sus respectivo:

- marca
- talla
- precio

**Guarda la imagen original en**:

```
~/boutique_zepeda/pto_montaje/social_media/estados_piso_venta/<categoria>/originales/
```

**Guarda la imagen editada en**:

```
~/boutique_zepeda/pto_montaje/social_media/estados_piso_venta/<categoria>/editadas/
```


Elige el prompt según el público al que esté dirigido el producto:

* [Dama](#Dama)
* [Caballero](#Caballero)
* [Infantil](#Infantil)
* [Accesorios](#Accesorios)

Una vez seleccionado el prompt adecuado, utilízalo junto con la imagen de la prenda, logo (opcional) para generar una publicación visual atractiva y enfocada en la venta.


## Dama

```text
Crea una publicación con la imagen que te comparto y el siguiente schema JSON:

{
  "dimensiones": "9:16",
  "renderizado": "3D",
  "resolucion": "4K",
  "zona_segura": true,
  "estilo": "dama",
  "presentacion": "tienda_online_minimalista_premium",
  "etiqueta": {
    "label": true,
    "posicion": "esquina_inferior_derecha",
    "estilo": "recuadro_minimalista_premium",
    "informacion_producto": {
      "marca": "NOMBRE_MARCA",
      "talla": "XG",
      "precio": "00.00"
    }
  }
}
```

> [!NOTE]
> Si no quieres incluir la marca, puedes dejar el espacio en blanco de la siguinte manera:
> "marca": "",

## Caballero

```text

Crea una publicación con la imagen que te comparto y el siguiente schema JSON:

{
  "dimensiones": "9:16",
  "renderizado": "3D",
  "resolucion": "4K",
  "zona_segura": true,
  "estilo": "caballero",
  "presentacion": "tienda_online_minimalista_premium",
  "etiqueta": {
    "label": true,
    "posicion": "esquina_inferior_derecha",
    "estilo": "recuadro_minimalista_premium",
    "informacion_producto": {
      "marca": "NOMBRE_MARCA",
      "talla": "XG",
      "precio": "00.00"
    }
  }
}
```

## Infantil

```text
Crea una publicación con la imagen que te comparto y el siguiente schema JSON:

{
  "dimensiones": "9:16",
  "renderizado": "3D",
  "resolucion": "4K",
  "zona_segura": true,
  "estilo": "infantil",
  "presentacion": "tienda_online_minimalista_premium",
  "etiqueta": {
    "label": true,
    "posicion": "esquina_inferior_derecha",
    "estilo": "recuadro_minimalista_premium",
    "informacion_producto": {
      "marca": "NOMBRE_MARCA",
      "talla": "XG",
      "precio": "00.00"
    }
  }
}
```

## Accesorios

```text
Crea una publicación con la imagen que te comparto y el siguiente schema JSON:

{
  "dimensiones": "9:16",
  "zona_segura": true,
  "estilo": "accesorios",
  "presentacion": "tienda_online_minimalista_premium",
  "etiqueta": {
    "label": true,
    "posicion": "esquina_inferior_derecha",
    "estilo": "recuadro_minimalista_premium",
    "informacion_producto": {
      "marca": "NOMBRE_MARCA",
      "talla": "XG",
      "precio": "00.00"
    }
  }
}
```