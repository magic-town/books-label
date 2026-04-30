# Catálogo de prompt para publicaciones en redes sociales (Fb, Whatsapp, IG).

> Este fichero Markdown es para crear publicaciones en estados de WhatsApp, Facebook, IG.

Para usarlo ocuparemos un contenedor 📦 para archivar las prendas antes y después de la edición.

```
~/boutique_zepeda/pto_montaje/social_media/
```

Toma las 📷 fotos con tu celular, guardando el `precio`, `marca (opcional)`, `talla`  o toma capturas con `flameshot` en caso de catálogos, para usar como input o archivo adjunto en: ChatGPT, Gemmini Nano Banana.


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

Composición: limpia, estética y balanceada, con espacio negativo alrededor de la prenda.
IMPORTANTE: solo debe existir una única etiqueta comercial, ubicada exclusivamente en la esquina inferior derecha. No generar etiquetas adicionales en ninguna otra parte de la imagen.

Configuración de etiqueta:

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

Reglas estrictas de la etiqueta:

- Solo una etiqueta visible.
- Ubicación fija: esquina inferior derecha.
- No duplicar información ni crear badges adicionales.
- No colocar precio en ninguna otra zona.
- Diseño limpio, moderno, femenino y elegante.
- Integración natural tipo badge flotante o elemento orgánico, sin recuadros rígidos.
- Tipografía refinada, alineada a estética premium.

Elementos adicionales:
Agregar formas orgánicas suaves, sombras ligeras, brillos delicados o reflejos de luz que aporten profundidad sin distraer del producto.

Iluminación: tipo estudio, suave pero direccional, resaltando texturas y volumen.

Estilo general: premium, elegante, femenino, moderno, visualmente atractivo, sin saturación pero con presencia comercial clara.

Formato: vertical 9:16, ideal para estados de WhatsApp.
Resolución: alta, enfoque nítido, estilo fotografía comercial de producto.
```

## Caballero

```text
Visualización de producto en ultra alta calidad de una prenda de caballero (moda masculina), centrada y dominante en la composición.

La prenda se muestra con un estilo 3D realista o fotografía hiperrealista, con textura de tela visible, caída natural, detalles finos y pliegues suaves que transmitan elegancia, masculinidad y una sensación premium y táctil.

Fondo: minimalista, con degradado suave o color sólido inspirado en e-commerce de moda masculina de alta gama (tonos neutros como beige, nude, gris suave, pastel o tonos oscuros elegantes, eligiendo el que mejor contraste con la prenda). Añadir un sutil resplandor de luz detrás del producto para reforzar el enfoque.

Composición: limpia, estética y balanceada, con espacio negativo alrededor de la prenda.
IMPORTANTE: solo debe existir una única etiqueta comercial, ubicada exclusivamente en la esquina inferior derecha. No generar etiquetas adicionales en ninguna otra parte de la imagen.

Configuración de etiqueta:

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

Reglas estrictas de la etiqueta:

- Solo una etiqueta visible.
- Ubicación fija: esquina inferior derecha.
- No duplicar información ni crear badges adicionales.
- No colocar precio en ninguna otra zona.
- Diseño limpio, moderno, elegante (adaptado a estética masculina).
- Integración natural tipo badge flotante o elemento orgánico, sin recuadros rígidos.
- Tipografía refinada, alineada a estética premium.

Elementos adicionales:
Agregar formas orgánicas suaves, sombras ligeras, brillos delicados o reflejos de luz que aporten profundidad sin distraer del producto.

Iluminación: tipo estudio, suave pero direccional, resaltando texturas y volumen.

Estilo general: premium, elegante, masculino, moderno, visualmente atractivo, sin saturación pero con presencia comercial clara.

Formato: vertical 9:16, ideal para estados de WhatsApp.
Resolución: alta, enfoque nítido, estilo fotografía comercial de producto.
```

## Infantil

```text
PROMPT (INFANTIL – DIVERTIDO / CONTRASTE CON ADULTO):

Visualización de producto en ultra alta calidad de una prenda infantil (moda para niños/niñas), centrada y dominante en la composición.

La prenda se muestra con un estilo 3D realista o fotografía hiperrealista, con textura de tela visible, caída natural, detalles finos y pliegues suaves que transmitan suavidad, ternura y una sensación premium y táctil.

Fondo: minimalista pero más dinámico y alegre, con degradados suaves en tonos pastel más vivos (como azul cielo, durazno, lavanda, menta o amarillo suave), o combinaciones sutiles de color que generen contraste visual con los estilos neutros de adulto. Añadir un resplandor de luz suave detrás del producto para reforzar el enfoque.

Composición: limpia, estética y balanceada, con espacio negativo alrededor de la prenda.
IMPORTANTE: solo debe existir una única etiqueta comercial, ubicada exclusivamente en la esquina inferior derecha. No generar etiquetas adicionales en ninguna otra parte de la imagen.

Configuración de etiqueta:

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

Reglas estrictas de la etiqueta:

- Solo una etiqueta visible.
- Ubicación fija: esquina inferior derecha.
- No duplicar información ni crear badges adicionales.
- No colocar precio en ninguna otra zona.
- Diseño limpio pero con un toque más amigable, suave y ligeramente lúdico.
- Integración tipo badge orgánico, con bordes más redondeados o forma fluida.
- Tipografía elegante pero más cálida y accesible.

Elementos adicionales (clave para contraste infantil):

Incorporar formas orgánicas más visibles y dinámicas (ondas, blobs suaves, curvas).
Añadir pequeños acentos gráficos sutiles (puntitos, brillos, destellos suaves o mini formas flotantes).
Sombras suaves con un toque más ligero y alegre.
Mantener equilibrio: divertido pero sin saturar.

Iluminación: tipo estudio, suave pero ligeramente más brillante y envolvente que en adulto, resaltando textura y volumen.

Estilo general: premium + divertido, tierno, moderno, dinámico, visualmente atractivo, con mayor energía visual que los estilos de adulto pero sin perder elegancia comercial.

Formato: vertical 9:16, ideal para estados de WhatsApp.
Resolución: alta, enfoque nítido, estilo fotografía comercial de producto.
```

## Accesrios

```text
Visualización de producto en ultra alta calidad de un accesorio de moda (bolsas, joyería, sombreros, lentes, cinturones u otros), centrado y dominante en la composición.

El accesorio se muestra con un estilo 3D realista o fotografía hiperrealista, con alto nivel de detalle en materiales (metal, piel, tela, plástico, etc.), acabados finos, reflejos controlados y texturas visibles que transmitan calidad, precisión y una sensación premium.

Fondo: minimalista, con degradado suave o color sólido inspirado en e-commerce de accesorios de alta gama. Utilizar tonos neutros (negro, gris, beige, blanco) o colores elegantes que generen contraste con el accesorio. Ajustar ligeramente el carácter del fondo según el tipo de accesorio (más sobrio para lujo, más fresco para casual, más limpio para joyería). Añadir un sutil resplandor de luz detrás del producto para reforzar el enfoque.

Composición: limpia, precisa y balanceada, con el accesorio perfectamente centrado.
IMPORTANTE: solo debe existir una única etiqueta comercial, ubicada exclusivamente en la esquina inferior derecha. No generar etiquetas adicionales en ninguna otra parte de la imagen.

Configuración de etiqueta:

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

Reglas estrictas de la etiqueta:

- Solo una etiqueta visible.
- Ubicación fija: esquina inferior derecha.
- No duplicar información ni crear badges adicionales.
- No colocar precio en ninguna otra zona.
- Diseño limpio, moderno y elegante.
- Integración tipo badge flotante o forma orgánica sutil.
- Tipografía refinada, adaptable al tipo de accesorio (lujo, casual o contemporáneo).

Elementos adicionales (personalización clave para accesorios):

Incorporar líneas finas, reflejos suaves o destellos controlados que acompañen el material (especialmente en metal o joyería).
Sombras suaves que definan volumen sin endurecer la composición.
Acentos visuales discretos que refuercen el carácter del accesorio (más brillo para joyería, más sobriedad para piel, más ligereza para textiles).
Mantener un balance entre estética premium y protagonismo absoluto del producto.

Iluminación: tipo estudio, precisa y controlada, enfatizando brillos, bordes, texturas y acabados del accesorio.

Estilo general: premium, limpio, moderno, detallado, versátil según categoría, con enfoque total en el producto y estética de e-commerce de alta gama.

Formato: vertical 9:16, ideal para estados de WhatsApp.
Resolución: alta, enfoque nítido, estilo fotografía comercial de producto.
```