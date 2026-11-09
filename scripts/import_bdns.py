"""Descarga convocatorias de la API pública de BDNS (infosubvenciones.es) y escribe data/convocatorias.json.

Uso:
  python3 scripts/import_bdns.py                      # descarga de la API
  python3 scripts/import_bdns.py --from-file x.json   # normaliza un JSON ya descargado (lista de convocatorias)

NOTA: el endpoint y sus parámetros se confirmaron a mano desde un navegador (devuelve XML por defecto).
Revisar las condiciones de uso y los límites de BDNS antes de importar de forma masiva.
Si la descarga falla, NO se toca el fichero existente: la web sigue mostrando el último dato bueno.
"""
import argparse
import json
import os
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(__file__))
import radar  # noqa: E402

API = "https://www.infosubvenciones.es/bdnstrans/api/convocatorias/busqueda"
SALIDA = os.path.join(os.path.dirname(__file__), "..", "data", "convocatorias.json")
RETENCION_DIAS = 60     # la web solo guarda los últimos N días por fecha de recepción
POR_PAGINA = 100
MAX_PAGINAS = 10


def descarga(desde):
    out = []
    for p in range(MAX_PAGINAS):
        url = f"{API}?page={p}&pageSize={POR_PAGINA}&order=fechaRecepcion&direccion=desc&fechaDesde={desde}&vpd=GE"
        req = urllib.request.Request(url, headers={"User-Agent": "radar360/0.1 (+https://github.com/NexusForgeIA/RADAR-360)"})
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
        try:                                    # JSON si el servidor lo da…
            datos = json.loads(raw)
            filas = datos.get("content", datos) if isinstance(datos, dict) else datos
        except ValueError:                      # …y XML (formato por defecto) si no
            filas = []
            for c in ET.fromstring(raw).iter("content"):
                filas.append({e.tag: (e.text or None) for e in c})
        if not filas:
            break
        out += filas
        if len(filas) < POR_PAGINA:
            break
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-file")
    a = ap.parse_args()
    hoy = datetime.now(timezone.utc).date()
    limite = (hoy - timedelta(days=RETENCION_DIAS)).isoformat()
    if a.from_file:
        crudas = json.load(open(a.from_file, encoding="utf-8"))
    else:
        crudas = descarga((hoy - timedelta(days=14)).strftime("%d/%m/%Y"))
    nuevas = [radar.normaliza(c) for c in crudas if c.get("numeroConvocatoria")]
    if not nuevas:
        print("sin datos: se conserva el fichero actual")
        return 1
    try:
        previas = json.load(open(SALIDA, encoding="utf-8")).get("convocatorias", [])
    except (OSError, ValueError):
        previas = []
    por_num = {c["numero"]: c for c in previas}
    por_num.update({c["numero"]: c for c in nuevas})        # lo nuevo pisa a lo viejo
    todas = [c for c in por_num.values() if c["fecha"] >= limite]
    todas.sort(key=lambda c: (c["fecha"], c["numero"]), reverse=True)
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    json.dump({"actualizado": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ"), "fuente": "BDNS · infosubvenciones.es",
               "convocatorias": todas}, open(SALIDA, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{len(todas)} convocatorias guardadas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
