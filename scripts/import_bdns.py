"""Descarga convocatorias de la API pública de BDNS (infosubvenciones.es) y escribe data/convocatorias.json.

Uso:
  python3 scripts/import_bdns.py                      # descarga de la API
  python3 scripts/import_bdns.py --from-file x.json   # normaliza un JSON ya descargado (lista de convocatorias)

NOTA: endpoints y parámetros comprobados a mano desde un navegador; con Accept: application/json responden JSON.
Aviso legal de BDNS: reutilización comercial permitida citando la fuente y la fecha de actualización; pueden limitar el API ante abuso,
por eso se pide una ficha cada PAUSA segundos y con tope por ejecución.
Si la descarga falla, NO se toca el fichero existente: la web sigue mostrando el último dato bueno.
"""
import argparse
import json
import os
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(__file__))
import radar  # noqa: E402

UA = "radar360/0.1 (+https://github.com/NexusForgeIA/RADAR-360)"
API = "https://www.infosubvenciones.es/bdnstrans/api/convocatorias/busqueda"
SALIDA = os.path.join(os.path.dirname(__file__), "..", "data", "convocatorias.json")
RETENCION_DIAS = 14     # se conserva todo lo recibido en los últimos N días…
DETALLE = "https://www.infosubvenciones.es/bdnstrans/api/convocatorias?vpd=GE&numConv={n}"
MAX_FICHAS = 1200       # fichas que se piden por ejecución (cortesía con el API)
PAUSA = 0.2             # segundos entre peticiones
POR_PAGINA = 100
MAX_PAGINAS = 30


def ficha(n):
    req = urllib.request.Request(DETALLE.format(n=n), headers={"Accept": "application/json", "User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def completa(regs, hoy):
    """Pide la ficha oficial de las convocatorias que aún no la tienen (y refresca plazos que vencen pronto)."""
    pend = [r for r in regs if not r.get("ficha")][:MAX_FICHAS]
    hechas = 0
    for r in pend:
        try:
            radar.enriquece(r, ficha(r["numero"]))
            hechas += 1
        except Exception as e:                                  # una ficha rota no frena al resto
            print("ficha", r["numero"], "falló:", type(e).__name__)
        time.sleep(PAUSA)
    print(f"fichas completadas: {hechas}/{len(pend)}")


def descarga(desde):
    out = []
    for p in range(MAX_PAGINAS):
        url = f"{API}?page={p}&pageSize={POR_PAGINA}&order=fechaRecepcion&direccion=desc&fechaDesde={desde}&vpd=GE"
        req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": UA})
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
    for c in nuevas:                                        # lo nuevo pisa a lo viejo, salvo la ficha ya pedida
        v = por_num.get(c["numero"])
        por_num[c["numero"]] = {**c, **{k: v[k] for k in v if k not in c}} if v else c
    todas = [c for c in por_num.values() if c["fecha"] >= limite or (c.get("fin") or "") >= hoy.isoformat()]
    if not a.from_file:
        completa(todas, hoy)
    todas.sort(key=lambda c: (c["fecha"], c["numero"]), reverse=True)
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    json.dump({"actualizado": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ"), "fuente": "BDNS · infosubvenciones.es",
               "convocatorias": todas}, open(SALIDA, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{len(todas)} convocatorias guardadas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
