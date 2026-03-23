# books-label — Alcance y visión del proyecto

**Versión 1.2 — Marzo 2026**

---

## 1. Propósito

`books-label` nace como una herramienta de automatización para Novedades Zepeda, una boutique familiar en Mineral de Angangueo, Michoacán. El negocio opera con catálogos físicos y digitales de múltiples proveedores, y el proceso de etiquetado de precios propios sobre esos catálogos consumía horas de trabajo manual cada temporada.

El primer objetivo del proyecto fue claro: automatizar ese proceso. El segundo, más ambicioso, es convertir ese esfuerzo en la base de una transformación digital completa — llevando los productos al canal en línea y construyendo una presencia comercial moderna.

---

## 2. Alcance actual

El proyecto está estructurado en tres fases en distintos estados de madurez:

**Fase 1 — Extracción de datos del proveedor**
Módulo en desarrollo. Toma las listas de precios crudas de cada proveedor (PDF con encoding propietario, estructura tabular inconsistente) y extrae automáticamente los campos `ID` y `precio_sugerido` en un Excel limpio. Elimina la extracción manual que hoy depende de asistentes de IA y validación visual.

**Fase 2 — Etiquetado del catálogo**
Módulo funcional en producción. Toma el catálogo PDF del proveedor y la lista de precios validada, detecta los IDs de producto mediante OCR y estampa el precio de venta de la boutique sobre cada artículo. El resultado es un PDF listo para distribuir. Soporta actualmente Price Shoes, con Pakar y Cklass en integración.

**Fase 3 — Distribución y canal de venta**
Módulo en definición. Hoy la distribución opera a través de Dropbox y WhatsApp Business mediante enlaces de descarga. El objetivo es reemplazar ese flujo por una plataforma web donde el cliente navegue los catálogos directamente — sin descargas, sin fricción. Las opciones evaluadas son GitHub Pages para una solución inmediata y Vercel para un portal con mayor alcance y presencia a largo plazo.

---

## 3. Hacia dónde va

La automatización que construye `books-label` no es un fin en sí mismo — es el primer paso de una transformación más amplia.

El pipeline completo, cuando esté validado, elimina la intervención manual en la preparación de catálogos y los pone disponibles en línea de forma inmediata. Eso libera tiempo del equipo, reduce errores y abre un canal de venta que no existía.

La plataforma web que se construya en Fase 3 no es una tienda en línea convencional — es un portal de presentación elegante que pone los productos frente al cliente con contexto, navegabilidad y una imagen de marca coherente. Para un negocio que hoy distribuye por mensajería instantánea, eso representa un salto cualitativo real.

La visión de largo plazo es que este modelo — automatización de catálogos más canal web — sea replicable. Lo que se construye para Novedades Zepeda es, en esencia, una plataforma que cualquier negocio con catálogos de proveedores podría adoptar. La transformación digital no requiere grandes presupuestos ni infraestructura compleja: requiere procesos bien diseñados, automatización progresiva y un equipo dispuesto a aprender.

---

## 4. Principios de construcción

El proyecto se construye con criterios deliberados:

**Automatización correcta antes que automatización rápida.** Cada módulo se valida con pruebas reales antes de escalar. La tasa de etiquetado, el formato de extracción y la experiencia del usuario en el canal final son métricas concretas, no supuestos.

**El analista como usuario real.** Sonia opera el sistema sin tocar código. Todo panel, configurador y guía está diseñado para que una persona sin perfil técnico pueda ejecutar el proceso completo de forma autónoma. Si algo requiere intervención de desarrollo, es una deficiencia del diseño, no del usuario.

**Arquitectura modular.** Cada fase es un módulo independiente con su propia configuración, inputs, outputs y documentación. Un nuevo proveedor, un nuevo canal de distribución o un nuevo colaborador pueden incorporarse sin reescribir lo que ya funciona.

**Documentación como parte del producto.** `CHECKLIST.md`, `README.md` y los paneles HTML no son complementos — son parte del sistema. Un proceso que no puede documentarse no puede mantenerse.

---

## 5. Estado del equipo

El proyecto lo desarrollan dos personas:

| Persona | Rol |
|---------|-----|
| Gabriel | Desarrollo, arquitectura y mantenimiento técnico |
| Sonia | Operación: extracción, etiquetado y distribución |

La escala del equipo es una restricción consciente, no una limitación. La arquitectura modular y la documentación operativa están diseñadas precisamente para que el sistema funcione con este equipo y pueda crecer sin depender de ninguna persona en particular.

---

## 6. Decisiones pendientes

| Tema | Estado |
|------|--------|
| Validación del pipeline Fase 1 → Fase 2 | En pruebas — n corridas necesarias antes de automatizar |
| Canal de distribución Fase 3 | En definición — GitHub Pages vs. Vercel |
| Soporte Pakar y Cklass en Fase 2 | En integración |
| Nuevos proveedores | Declarables en `config_base.json` sin modificar el script |

---

*books-label · Novedades Zepeda · Angangueo, Michoacán · 2026*
