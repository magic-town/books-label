## Opciones de prompt para publicar o postear en redes sociales (Fb, Whatsapp)

Este fichero Markdown es para crear publicaciones en estados de WhatsApp, Facebook, IG.

Para usarlo ocuparemos un contenedor 📦 para archivar las prendas antes y después de la edición. 

Elige el prompt según el público al que esté dirigido el producto:

* Infantil
* Dama
* Caballero
* Accesorios

Una vez seleccionado el prompt adecuado, utilízalo junto con la imagen de la prenda, logo (opcional) para generar una publicación visual atractiva y enfocada en la venta.

```text
Visualización de producto en ultra alta calidad de la prenda que te comparto, centrada y dominante en la composición.

La prenda se muestra con un estilo 3D realista, con textura de tela visible, sombras suaves y pliegues naturales, transmitiendo una sensación premium y táctil.

Fondo: minimalista, con degradado suave o color sólido inspirado en e-commerce de moda de alta gama (tonos neutros como beige, gris suave, pastel o tonos oscuros elegantes, eligiendo el que mejor contraste con la prenda). Añadir un sutil resplandor de luz detrás del producto para reforzar el enfoque.

Composición: limpia y balanceada, con espacio negativo alrededor de la prenda para colocar elementos comerciales definidos por la siguiente configuración JSON:

{
  "etiqueta": {
    "mostrar_precio": true,
    "precio": "00.00",

    "mostrar_marca": false,
    "marca": "NOMBRE_MARCA",
    "talla": "false",
    "descripción": "false",

    "mostrar_logo": false,

    "estilo": "minimalista_premium"
  }
}

La etiqueta debe ser altamente estilizada según el campo "estilo", con diseño limpio, moderno y elegante. Debe integrarse de forma natural en la composición (por ejemplo: esquina inferior, tipo badge, o etiqueta flotante), sin distraer del producto pero siendo claramente visible para fines de venta. Para los campos en false, no se toman en cuenta para la publicación, de tener valor debes agregarlos de maanera natural y alineado a una publicación de tienda online dinamica y de alta gamma, la etiqueta no debe ser el tipico recuadro con datos, debes distribuir la ifno de manera armonica y elegir la tipografía correcta.

Agregar elementos de diseño modernos y sutiles: formas geométricas suaves, sombras ligeras o reflejos de luz que aporten profundidad sin distraer del producto.

Iluminación: tipo estudio, suave pero direccional, generando profundidad y realismo.

Estilo: premium, elegante, moderno, sin saturación visual, pero tampoco demasiado simple — visualmente atractivo y limpio.

Alta resolución, enfoque nítido, estilo fotografía comercial de producto.
```
