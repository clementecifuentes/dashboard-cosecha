# Dashboard Cosecha — John Deere Ceres Tolvas

Dashboard web para visualizar y comparar datos de cosecha entre temporadas
(2025, 2025F y 2026), a partir de datos exportados del John Deere Operations Center.

## Contenido

- **`index.html`** — El dashboard completo, autocontenido (Leaflet + Chart.js).
  Se abre directamente en el navegador. Tiene 5 pestañas:
  - 📍 Mapa & Resumen — mapa de lotes con KPIs comparativos entre temporadas
  - 📊 Comparación — comparativa entre temporadas por cultivo
  - 🗂️ Detalle — tabla detallada de lotes
  - 🚜 Máquinas — área y rendimiento por cosechadora/modelo
  - 💰 Rentabilidad — análisis económico y distribución de rendimientos
- **`limpiar_geojson.py`** — Preprocesa los GeoJSON crudos y genera `data/campos.json`
  (liviano) con solo los campos necesarios. Clasifica cultivos, y filtra outliers
  (lotes < 0.5 ha y rindes > 15 t/ha).
- **`data/campos.json`** — Datos procesados que consume el dashboard.
- **`data/*.qmd`** — Metadatos de QGIS de las capas originales.

> Los GeoJSON crudos (`data/interseccion*.geojson`, ~80–95 MB cada uno) **no están
> en el repositorio** por su tamaño. Ver `.gitignore`.

## Uso

1. Exportar los GeoJSON del Operations Center a la carpeta `data/`
   (nombres tipo `interseccion2026.geojson`).
2. Regenerar los datos procesados:

   ```bash
   python limpiar_geojson.py
   ```

3. Abrir `index.html` en el navegador.
