
"""
LIMPIAR GEOJSON — John Deere Ceres Tolvas
==========================================
Lee los archivos GeoJSON de la carpeta 'data' y genera un archivo
'campos.json' liviano con solo los datos necesarios para el dashboard.

Uso: python limpiar_geojson.py
"""

import json, os, glob

def classify(name):
    if not name: return 'OTROS'
    n = name.lower()
    if 'wheat' in n: return 'Trigo'
    if 'barley' in n: return 'Cebada'
    if 'oats' in n: return 'Avena'
    if 'soybeans' in n or 'soybean' in n: return 'Soja'
    if 'corn' in n: return 'Maiz'
    if 'canola' in n: return 'Canola'
    if 'pea_trapper' in n: return 'Arvejas'
    if 'sunflower' in n: return 'Girasol'
    return 'OTROS'

# Rendimiento máximo plausible por cultivo (t/ha).
# Valores superiores indican error en los datos fuente.
MAX_REND_HA = {
    'Soja':    15.0,
    'Maiz':    15.0,
    'Girasol': 15.0,
    'Trigo':   15.0,
    'Cebada':  15.0,
    'Avena':   15.0,
    'Canola':  15.0,
}
MIN_AREA_HA = 0.5   # lotes menores a esto son artefactos de medición

SEASON_MAP = {
    'interseccion2026.geojson': '2026',
    'interseccion2025F.geojson': '2025F',
    'interseccion2025.geojson': '2025',
}

carpeta = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
archivos = glob.glob(os.path.join(carpeta, '*.geojson'))

if not archivos:
    print(f"No se encontraron archivos .geojson en: {carpeta}")
    input("Presioná Enter para cerrar...")
else:
    print(f"Encontrados {len(archivos)} archivo(s):\n")
    all_fields = []

    for archivo in sorted(archivos):
        nombre = os.path.basename(archivo)
        label = SEASON_MAP.get(nombre)
        if not label:
            if '2026' in nombre: label = '2026'
            elif '2025F' in nombre or '2025f' in nombre: label = '2025F'
            elif '2025' in nombre: label = '2025'
            else: label = nombre.replace('.geojson', '')

        try:
            with open(archivo, encoding='utf-8') as f:
                gj = json.load(f)
            features = gj.get('features', [])
            size = os.path.getsize(archivo) / 1024
            for feat in features:
                p = feat.get('properties', {})
                partido = (p.get('PARTIDO') or p.get('partido') or 'DESCONOCIDO').upper()
                entry = {
                    'org':    p.get('Organization Name') or p.get('org') or '—',
                    'partido': partido,
                    'crop':   classify(p.get('Crop Name') or p.get('crop') or ''),
                    'area':   round(float(p.get('Area')          or p.get('area') or 0), 1),
                    'yt':     round(float(p.get('Yield (tons)')  or p.get('yt')   or 0), 1),
                    'ya':     round(float(p.get('Yield Average') or p.get('ya')   or 0), 2),
                    'mo':     round(float(p.get('Moisture Average') or p.get('mo') or 0), 1),
                    'file':   label,
                    'mvin':   p.get('Machine VIN')   or p.get('mvin') or '—',
                    'mmod':   p.get('Machine Model') or p.get('mmod') or '—',
                }

                # ── Filtro de outliers ──────────────────────────────────────
                if entry['area'] < MIN_AREA_HA:
                    print(f"    [FILTRO] Área mínima: {entry['org']} {entry['crop']} {entry['area']} ha")
                    continue
                if entry['area'] > 0:
                    rend = entry['yt'] / entry['area']
                    max_r = MAX_REND_HA.get(entry['crop'], 15.0)
                    if rend > max_r:
                        print(f"    [FILTRO] Rinde imposible: {entry['org']} {entry['crop']} {rend:.1f} t/ha ({entry['area']} ha) — max {max_r} t/ha")
                        continue
                # ────────────────────────────────────────────────────────────

                all_fields.append(entry)
            print(f"  v {nombre} [{label}]: {len(features)} lotes, {size:.0f}KB")
        except Exception as e:
            print(f"  x Error en {nombre}: {e}")

    output_path = os.path.join(carpeta, 'campos.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(all_fields, f, ensure_ascii=False, separators=(',', ':'))

    size_final = os.path.getsize(output_path) / 1024
    print(f"\n  v campos.json generado: {len(all_fields)} lotes totales, {size_final:.0f}KB")
    print("\nListo! Recarga el dashboard en el browser.")
    input("Presioná Enter para cerrar...")
