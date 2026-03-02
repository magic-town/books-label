<img src="../images/asset_repo/cover00.png" alt="Boutique Zepeda — Taller de Etiquetado" width="100%"/>

# Prompts — Extracción de columnas desde lista de precios

Usar con NotebookLM, Claude o Gemini. Seguir en orden si el modelo se equivoca de columna.

---

## Paso 1 — Extracción inicial

```
Del fichero <nombre_archivo> extrae las siguientes columnas de todas las páginas del documento:

{
  "columna_1":  "Pag",
  "columna_4":  "ID",
  "columna_12": "Sug_credito"
}

Preséntala en forma de tabla, lista para copiar y pegar en LibreOffice Calc.
IMPORTANTE: el tipo de datos debe ser número y el formato debe ser una tabla.
```

---

## Paso 2 — Si se equivoca de columna

```
Del fichero <nombre_archivo> extrae las siguientes columnas de todas las páginas del documento:

{
  "columna_1":  "Pag",
  "columna_4":  "ID",
  "columna_13": "Sug_credito"
}

Preséntala en forma de tabla, lista para copiar y pegar en LibreOffice Calc.
IMPORTANTE: el tipo de datos debe ser número y el formato debe ser una tabla.
```

---

## Paso 3 — Si vuelve a equivocarse

```
La tabla que generaste es correcta en:

{
  "columna_1": "Pag",
  "columna_4": "ID"
}

Es incorrecta la columna_X. Corrígela por los datos correctos: "columna_X": "Sug_credito".
IMPORTANTE: los datos de toda la tabla deben ser de tipo número.
```

---

## Paso 4 — Si aún no da la tabla correcta

Compartirle los dos primeros registros como referencia:

```
Te comparto los dos primeros registros:

{
  "primer_registro":  { "Pag": <num_pag>, "ID": <id>, "Sug_credito": <precio> },
  "segundo_registro": { "Pag": <num_pag>, "ID": <id>, "Sug_credito": <precio> }
}

Dame la tabla completa con las columnas: Pag, ID, Sug_credito.
```
