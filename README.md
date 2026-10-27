# Recetario de Li You

Web para el móvil que acompaña al libro impreso de recetas de Li You. Cada receta del libro lleva un código QR que abre su página aquí.

Dirección: https://ragonzalezram83.github.io/recetas-li-you/

## Qué hay en cada receta

- **Receta**: la versión editada, con ingredientes para ir marcando y el modo «Cocinar paso a paso» (pantalla encendida y temporizadores solo donde el cuaderno da un tiempo).
- **Cuaderno**: las páginas manuscritas originales y la transcripción fiel, con su ortografía.
- **Fotos**: fotos de los platos y del proceso.

Las dudas se muestran como `POR CONFIRMAR`. No se añade ningún ingrediente, cantidad, tiempo ni temperatura que no esté en el cuaderno.

## Cómo se actualiza

1. `data/transcripciones.md` es la copia del documento de trabajo. `tools/parse_doc.py data/transcripciones.md data/recetas.json` la convierte en datos.
2. `data/fotos.json` dice qué foto va de portada en cada receta.
3. `python3 tools/build.py` genera `index.html`, una carpeta por receta y los QR en `qr/` (necesita `pip install segno jinja2`).

Las fotos en las que sale gente no están publicadas.
