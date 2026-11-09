# RADAR 360

Buscador gratuito de ayudas y subvenciones en España, alimentado con la API pública de la BDNS.
Prototipo en validación: sin cuentas, sin pagos, sin datos inventados.

## Estructura
- `index.html`, `assets/` — web estática (HTML + CSS + JS, sin dependencias).
- `data/convocatorias.json` — datos normalizados que lee la web.
- `scripts/radar.py` — normalización y clasificación por tema (palabras clave).
- `scripts/import_bdns.py` — descarga de BDNS; no toca el fichero si falla.
- `.github/workflows/actualizar.yml` — cron 2 veces al día que actualiza los datos.
- `render.yaml` — Static Site en Render (0 €).

## Límites conocidos
- El listado de BDNS no trae plazo, cuantía ni beneficiarios: la web no los muestra.
- Tema y perfil son orientativos (palabras clave del título).
- `import_bdns.py` no se ha podido probar contra la API real desde el entorno de desarrollo; verificar con el primer
  `workflow_dispatch` y revisar condiciones de uso y límites de BDNS.
- Los datos iniciales son una foto de 100 convocatorias del 09/11/2026.

## Probar en local
```
python3 -m http.server 8000   # y abrir http://localhost:8000
```
