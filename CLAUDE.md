# books-label — Guía del MVP

**Versión 1.1 — Marzo 2026**

---

## 1. Contexto general

`books-label` es un proyecto de etiquetado de catálogos de proveedores con precios propios de Novedades Zepeda. El sistema cuenta con un borrador funcional que cubre el flujo completo, pero presenta inconsistencias críticas que deben corregirse antes de escalar. Este documento define las tres fases del proyecto, sus deficiencias actuales y las soluciones planteadas, con el objetivo de establecer un MVP real y sostenible.

El equipo está formado por dos personas: Gabriel (desarrollador principal) y Sonia (analista sin perfil técnico en TI). La arquitectura y los flujos de trabajo deben reflejar esta realidad: Sonia opera exclusivamente mediante paneles HTML que escriben archivos JSON ejecutables desde consola.

---

## 2. Fases del proyecto

### 2.1 Fase 1 — Extracción de datos del proveedor

**Estado actual**

La extracción de datos crudos desde los catálogos del proveedor se realiza mediante LLM con resultados inconsistentes y alejados de la precisión requerida en producción.

**Solución propuesta**

Crear un módulo dedicado compuesto por tres archivos:

- `script.py` — lógica de extracción precisa y reproducible.
- `configurador.html` — panel de configuración para uso por parte de Sonia.
- `config_lista_proveedor.json` — parámetros de extracción; sustituye el método actual.

La interacción entre el panel y el archivo de configuración sigue el mismo patrón de Fase 2: no existe servidor, el panel incluye un botón `Copiar JSON` que transfiere los valores al archivo `config_lista_proveedor.json`. Este patrón debe mantenerse consistente en todas las fases.

---

### 2.2 Fase 2 — Etiquetado del catálogo

**Estado actual**

Esta fase funciona, aunque de forma incompleta. Solo se han realizado pruebas con un proveedor (Price Shoes), con una tasa de etiquetado de entre 70% y 95%, suficiente para salir a producción. El problema principal es que el crecimiento del proyecto sin una arquitectura definida lo convierte en un sistema difícil de mantener.

**Solución propuesta**

Actualmente se detectan tres formatos de identificador según el proveedor:

| Proveedor   | Formato          | Descripción                                         |
|-------------|------------------|-----------------------------------------------------|
| Price Shoes | `ID xxxxxxx`     | Prefijo fijo `ID`, seguido de 4 a 8 dígitos         |
| Pakar       | `Código xxx-xxx` | Prefijo fijo `Código`, dígitos separados por guion  |
| Cklass      | `xxx-xx`         | Dígitos separados por guion, sin prefijo            |

La solución óptima es declarar el formato de cada proveedor directamente en `config_base.json`, de modo que `catalogo_base.py` seleccione el patrón de detección sin lógica condicional dispersa en el código. Agregar un proveedor nuevo implicaría únicamente añadir su entrada en el JSON, sin tocar el script.

---

### 2.3 Fase 3 — Distribución y visualización de catálogos

**Estado actual**

Se utilizan Dropbox y WhatsApp Business como canal de distribución mediante enlaces de descarga. El flujo es deficiente: el enlace no siempre se abre correctamente y, cuando funciona, el usuario no sabe qué hacer con el archivo descargado.

**Opción A — GitHub Pages**

Publicar los catálogos directamente desde el repositorio mediante GitHub Pages. El usuario haría clic en un índice dentro de WhatsApp Business y visualizaría el catálogo PDF de inmediato, sin descargar ningún archivo. Esta solución reutiliza el flujo de sincronización existente (`sync.sh`), que ya contiene el `push` necesario.

**Opción B — Portal web en Vercel**

Crear un portal web sin costo, desplegado en Vercel, que permita navegar entre catálogos con una experiencia elegante. No es una tienda en línea, sino un espacio de presentación de productos diseñable con Lovable o con HTML/CSS propio. Tiene mayor alcance que la Opción A: permite agregar contexto, mejorar la navegación y construir una presencia web más sólida a futuro.

---

## 3. Archivos núcleo

| Archivo                      | Fase | Función                                          |
|------------------------------|------|--------------------------------------------------|
| `catalogo_base.py`           | 2    | Script principal; todo el sistema depende de él  |
| `config_base.json`           | 2    | Configuración de proveedores y formatos          |
| `configurador.html`          | 2    | Panel de control para Sonia                      |
| `config_lista_proveedor.json`| 1    | Parámetros de extracción por proveedor           |
| `CHECKLIST.md`               | —    | Bitácora del proyecto y tutorial de operación    |
| `sync.sh`                    | —    | Sincronización Git entre Gabriel y Sonia         |

---

## 4. Sincronización y trabajo en equipo

Sonia y Gabriel comparten una misma cuenta de GitHub y se sincronizan mediante convenciones que evitan conflictos de versiones. Este flujo está construido en `~/books-label/sync.sh`. Cualquier cambio en la arquitectura debe preservar este mecanismo.

---

## 5. Estructura de directorios

La estructura actual fue construida de forma improvisada. El primer paso antes de continuar con cualquier fase es establecer una organización lógica, limpia y estable. La estructura propuesta separa los módulos por fase, aísla la configuración de la ejecución y mantiene rutas predecibles para Sonia.

Cada fase tendrá su propia carpeta con un `README.md` breve: no una enciclopedia, sino una referencia operativa de tres secciones fijas — *qué hace*, *cómo se ejecuta* y *qué archivos toca*.

---

## 6. Alcance del MVP

El MVP real de `books-label` se considera completo cuando:

- La extracción de datos del proveedor es precisa y reproducible (Fase 1 corregida).
- El etiquetado soporta los tres formatos de identificador actuales y permite agregar nuevos desde `config_base.json` sin modificar el script (Fase 2 extendida).
- El catálogo es visualizable de inmediato por el usuario final, sin descargas (Fase 3, vía GitHub Pages o Vercel).
- La estructura de directorios está organizada y cada fase cuenta con su documentación operativa mínima.
- El flujo completo es operable por Sonia sin intervención en el código.
