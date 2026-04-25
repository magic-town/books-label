# Catálogo de prompt para publicaciones en redes sociales (Fb, Whatsapp, IG).

> Este fichero Markdown es para crear publicaciones en estados de WhatsApp, Facebook, IG.

Para usarlo ocuparemos un contenedor 📦 para archivar las prendas antes y después de la edición.

```
~/boutique_zepeda/pto_montaje/social_media/
```

Guarda las fotos o toma capturas con `flameshot` para usar como inputo o archivo adjunto en: ChatGPT, Gemmini Nano Banana.


Elige el prompt según el público al que esté dirigido el producto:

* [Catálogo](#Catálogo)
* [Dama](#Dama)
* [Caballero](#Caballero)
* [Infantil](#Infantil)
* [Accesorios](#Accesorios)

Una vez seleccionado el prompt adecuado, utilízalo junto con la imagen de la prenda, logo (opcional) para generar una publicación visual atractiva y enfocada en la venta.

## Catálogo

```text
Genera una composición visual profesional para promoción de catálogo de ropa.

INPUT:
{
  "mensaje": "Te invitamos a ver nuestro nuevo catálogo de temporada",
  "tono": "elegante",
  "publico": "general",
  "estilo_marca": "moda contemporánea"
}

INSTRUCCIONES:

- Utiliza la imagen proporcionada como portada principal del catálogo (no modificar su contenido).
- Agrega un background adicional fuera de la portada (como marco o extensión del lienzo), con un diseño profesional, limpio y coherente con el estilo de moda contemporánea.
- El background NO debe ser editable ni contener placeholders visibles, debe ser una composición final estética (colores suaves, degradados, formas orgánicas o geométricas sutiles).
- Integra el mensaje del JSON de forma destacada en el background, fuera de la portada, con tipografía moderna, legible y elegante.
- El mensaje debe respetar jerarquía visual (frase principal clara, posible énfasis en palabras clave).
- Mantener equilibrio visual entre portada y fondo.
- Iluminación suave, sombras sutiles, estilo premium.
- Evitar saturación visual, mantener estética minimalista.

OUTPUT:
- Imagen en alta resolución
- Estilo publicitario de marca de ropa
- Composición lista para uso en redes sociales o impresión
```

Ejemplos de mensaje:

+ "mensaje": "Descubre la nueva colección primavera-verano"
+ "mensaje": "Renueva tu estilo con nuestra línea exclusiva"
+ "mensaje": "Lo último en moda ya está disponible"

## Dama

```text
Visualización de producto en ultra alta calidad de una prenda de dama (moda femenina), centrada y dominante en la composición.

La prenda se muestra con un estilo 3D realista o fotografía hiperrealista, con textura de tela visible, caída natural, detalles finos y pliegues suaves que transmitan elegancia, feminidad y una sensación premium y táctil.

Fondo: minimalista, con degradado suave o color sólido inspirado en e-commerce de moda femenina de alta gama (tonos neutros como beige, nude, gris suave, pastel o tonos oscuros elegantes, eligiendo el que mejor contraste con la prenda). Añadir un sutil resplandor de luz detrás del producto para reforzar el enfoque.

Composición: limpia, estética y balanceada, con espacio negativo alrededor de la prenda para colocar elementos comerciales definidos por la siguiente configuración JSON:

{
  "label": {
    "show_precio": true,
    "precio": "00.00",

    "show_marca": false,
    "marca": "NOMBRE_MARCA",

    "show_talla": false,
    "talla": "XG",

    "show_descripcion": false,
    "descripcion": "tela algodón",

    "mostrar_logo": false,
    "show_logo": "usa el logo que te comparto de manera armónica y bien distribuida en la publicación",

    "estilo": "minimalista_premium"
  }
}

La etiqueta debe ser altamente estilizada según el campo "estilo", con diseño limpio, moderno, femenino y elegante. Debe integrarse de forma natural en la composición (por ejemplo: esquina inferior, tipo badge, o etiqueta flotante), sin distraer del producto pero siendo claramente visible para fines de venta.

Para los campos en false, no se deben mostrar. Si están en true, integrar la información de manera natural, evitando recuadros tradicionales; distribuir los datos con tipografía elegante y alineada a una publicación de tienda online dinámica y de alta gama.

Agregar elementos de diseño modernos y sutiles: formas orgánicas suaves, sombras ligeras, brillos delicados o reflejos de luz que aporten profundidad sin distraer del producto.

Iluminación: tipo estudio, suave pero direccional, resaltando texturas y volumen.

Estilo general: premium, elegante, femenino, moderno, visualmente atractivo, sin saturación pero con presencia comercial clara.

Formato vertical 9:16, ideal para estados de WhatsApp.

Alta resolución, enfoque nítido, estilo fotografía comercial de producto.
```

## Caballero

```text
Visualización de producto en ultra alta calidad de una prenda de caballero (moda masculina), centrada y dominante en la composición.

La prenda se muestra con un estilo 3D realista o fotografía hiperrealista, con textura de tela visible, estructura definida, cortes precisos y pliegues naturales que transmitan elegancia, carácter y una sensación premium y táctil.

Fondo: minimalista, con degradado suave o color sólido inspirado en e-commerce de moda masculina de alta gama (tonos neutros como gris, negro, azul marino, beige oscuro o tonos sobrios elegantes, eligiendo el que mejor contraste con la prenda). Añadir un sutil resplandor de luz detrás del producto para reforzar el enfoque.

Composición: limpia, sólida y balanceada, con espacio negativo alrededor de la prenda para colocar elementos comerciales definidos por la siguiente configuración JSON:

{
  "label": {
    "show_precio": true,
    "precio": "00.00",

    "show_marca": false,
    "marca": "NOMBRE_MARCA",

    "show_talla": false,
    "talla": "XG",

    "show_descripcion": false,
    "descripcion": "tela algodón",

    "mostrar_logo": false,
    "show_logo": "usa el logo que te comparto de manera armónica y bien distribuida en la publicación",

    "estilo": "minimalista_premium"
  }
}

La etiqueta debe ser altamente estilizada según el campo "estilo", con diseño limpio, moderno y elegante con estética masculina. Debe integrarse de forma natural en la composición (por ejemplo: esquina inferior, tipo badge, o etiqueta flotante), sin distraer del producto pero siendo claramente visible para fines de venta.

Para los campos en false, no se deben mostrar. Si están en true, integrar la información de manera natural, evitando recuadros tradicionales; distribuir los datos con tipografía sobria, fuerte y alineada a una publicación de tienda online dinámica y de alta gama.

Agregar elementos de diseño modernos y sutiles: líneas geométricas discretas, sombras suaves, reflejos controlados o acentos visuales que aporten profundidad sin distraer del producto.

Iluminación: tipo estudio, suave pero direccional, resaltando estructura, textura y volumen.

Estilo general: premium, elegante, masculino, moderno, visualmente atractivo, con presencia sólida sin saturación.

Formato vertical 9:16, ideal para estados de WhatsApp.

Alta resolución, enfoque nítido, estilo fotografía comercial de producto.
```

## Infantil

```text
Visualización de producto en ultra alta calidad de una prenda infantil (moda para niños/niñas), centrada y dominante en la composición.

La prenda se muestra con un estilo 3D realista o fotografía hiperrealista, con textura de tela visible, acabados suaves, formas ligeras y pliegues naturales que transmitan comodidad, frescura y una sensación de calidad.

Fondo: minimalista con un toque alegre, utilizando degradados suaves o colores sólidos inspirados en e-commerce infantil moderno (tonos pastel, colores claros o combinaciones suaves como azul cielo, rosa, menta, beige claro o lavanda). Elegir el fondo que mejor contraste con la prenda. Añadir un sutil resplandor de luz detrás del producto para reforzar el enfoque.

Composición: limpia, equilibrada y amigable, con espacio negativo alrededor de la prenda para colocar elementos comerciales definidos por la siguiente configuración JSON:

{
  "label": {
    "show_precio": true,
    "precio": "00.00",

    "show_marca": false,
    "marca": "NOMBRE_MARCA",

    "show_talla": false,
    "talla": "XG",

    "show_descripcion": false,
    "descripcion": "tela algodón",

    "mostrar_logo": false,
    "show_logo": "usa el logo que te comparto de manera armónica y bien distribuida en la publicación",

    "estilo": "minimalista_premium"
  }
}

La etiqueta debe ser altamente estilizada según el campo "estilo", con diseño limpio, moderno y con un toque amigable y ligero. Debe integrarse de forma natural en la composición (por ejemplo: esquina inferior, tipo badge, o etiqueta flotante), sin distraer del producto pero siendo claramente visible para fines de venta.

Para los campos en false, no se deben mostrar. Si están en true, integrar la información de manera natural, evitando recuadros tradicionales; distribuir los datos con tipografía clara, amigable y legible, alineada a una publicación de tienda online dinámica.

Agregar elementos de diseño modernos y sutiles: formas suaves u orgánicas, ligeros acentos gráficos (curvas, burbujas, brillos suaves) que aporten dinamismo sin saturar la imagen.

Iluminación: tipo estudio, suave y uniforme, resaltando colores y textura sin generar sombras duras.

Estilo general: limpio, moderno, amigable, alegre pero equilibrado, visualmente atractivo sin saturación.

Formato vertical 9:16, ideal para estados de WhatsApp.

Alta resolución, enfoque nítido, estilo fotografía comercial de producto.
```

## Accesrios

```text
Visualización de producto en ultra alta calidad de un accesorio de moda, centrado y dominante en la composición.

El accesorio se muestra con un estilo 3D realista o fotografía hiperrealista, con alto nivel de detalle en materiales (metal, piel, tela, plástico, etc.), acabados finos, reflejos controlados y texturas visibles que transmitan calidad, precisión y una sensación premium.

Fondo: minimalista, con degradado suave o color sólido inspirado en e-commerce de accesorios de alta gama (tonos neutros como negro, gris, beige, blanco o colores elegantes según el producto). Elegir el fondo que mejor contraste con el accesorio. Añadir un sutil resplandor de luz detrás del producto para reforzar el enfoque.

Composición: limpia, precisa y balanceada, con el accesorio perfectamente centrado y con suficiente espacio negativo alrededor para colocar elementos comerciales definidos por la siguiente configuración JSON:

{
  "label": {
    "show_precio": true,
    "precio": "00.00",

    "show_marca": false,
    "marca": "NOMBRE_MARCA",

    "show_talla": false,
    "talla": "XG",

    "show_descripcion": false,
    "descripcion": "material premium",

    "mostrar_logo": false,
    "show_logo": "usa el logo que te comparto de manera armónica y bien distribuida en la publicación",

    "estilo": "minimalista_premium"
  }
}

La etiqueta debe ser altamente estilizada según el campo "estilo", con diseño limpio, moderno y elegante. Debe integrarse de forma natural en la composición (por ejemplo: esquina inferior, tipo badge o elemento flotante), sin distraer del accesorio pero siendo claramente visible para fines de venta.

Para los campos en false, no se deben mostrar. Si están en true, integrar la información de manera natural, evitando recuadros tradicionales; distribuir los datos con tipografía elegante y acorde al tipo de accesorio (lujoso, casual, deportivo, etc.), alineada a una publicación de tienda online dinámica y de alta gama.

Agregar elementos de diseño modernos y sutiles: líneas finas, reflejos suaves, sombras ligeras o acentos visuales que aporten profundidad sin saturar la escena.

Iluminación: tipo estudio, precisa y controlada, resaltando brillos, bordes y textura del accesorio.

Estilo general: premium, limpio, moderno, detallado, visualmente atractivo con enfoque en el producto.

Formato vertical 9:16, ideal para estados de WhatsApp.

Alta resolución, enfoque nítido, estilo fotografía comercial de producto.
```