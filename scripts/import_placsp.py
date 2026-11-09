#!/usr/bin/env python3
"""Importa licitaciones abiertas de la Plataforma de Contratación del Sector Público (feed Atom de datos abiertos)
a data/licitaciones.json. Reutilización permitida con cita de la fuente. Sin dependencias externas.
Uso: python3 scripts/import_placsp.py [--from-file feed.atom]"""
import json, sys, time, urllib.request
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from radar import territorio  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "data" / "licitaciones.json"
SALIDA_ADJ = RAIZ / "data" / "adjudicaciones.json"
MAX_ADJ = 8000           # adjudicaciones que se conservan (las más recientes)
FEED = "https://contrataciondelestado.es/sindicacion/sindicacion_643/licitacionesPerfilesContratanteCompleto3.atom"
UA = "RADAR360-bot/1.0 (+https://radar360pymes.onrender.com; datos abiertos PLACSP)"
VENTANA_DIAS = 21      # cuánto se retrocede en el feed (cada página cubre ~2 días)
MAX_PAGINAS = 14
PAUSA = 1.0
TIPOS = {"1": "Suministros", "2": "Servicios", "3": "Obras", "21": "Gestión de servicios públicos",
         "22": "Concesión de servicios", "31": "Concesión de obras", "7": "Administrativo especial", "8": "Privado",
         "40": "Patrimonial", "50": "Otros"}


def _ln(el):
    return el.tag.rsplit("}", 1)[-1]


def _primero(nodo, nombre):
    for e in nodo.iter():
        if _ln(e) == nombre and (e.text or "").strip():
            return e.text.strip()
    return None


def _hijo(nodo, nombre):
    for e in nodo.iter():
        if _ln(e) == nombre:
            return e
    return None


def _num(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def parsea_entrada(e):
    """<entry> Atom → registro o None si no es una licitación utilizable."""
    cfs = _hijo(e, "ContractFolderStatus")
    if cfs is None:
        return None
    estado = _primero(cfs, "ContractFolderStatusCode")
    exp = _primero(cfs, "ContractFolderID")
    titulo = None
    proy = _hijo(cfs, "ProcurementProject")
    if proy is not None:
        titulo = _primero(proy, "Name")
    titulo = titulo or _primero(e, "title")
    if not exp or not titulo:
        return None
    # órgano de contratación
    org = None
    parte = _hijo(cfs, "LocatedContractingParty")
    if parte is not None:
        pn = _hijo(parte, "PartyName")
        org = _primero(pn, "Name") if pn is not None else None
    # presupuesto sin IVA si existe, si no el total
    presu = None
    if proy is not None:
        ba = _hijo(proy, "BudgetAmount")
        if ba is not None:
            presu = _num(_primero(ba, "TaxExclusiveAmount")) or _num(_primero(ba, "TotalAmount"))
    cpv = _primero(proy, "ItemClassificationCode") if proy is not None else None
    nuts = ciudad = None
    loc = _hijo(proy, "RealizedLocation") if proy is not None else None
    if loc is not None:
        nuts = _primero(loc, "CountrySubentityCode")
        ciudad = _primero(loc, "CountrySubentity")
    plazo = None
    tt = _hijo(cfs, "TenderSubmissionDeadlinePeriod")
    if tt is not None:
        plazo = _primero(tt, "EndDate")
    url = None
    for l in e:
        if _ln(l) == "link" and l.get("href"):
            url = l.get("href")
            break
    upd = _primero(e, "updated")
    adj = adjudicacion(cfs)
    reg = {
        "id": exp, "estado": estado, "titulo": " ".join(titulo.split()), "organismo": " ".join((org or "").split()),
        "tipo": TIPOS.get(_primero(proy, "TypeCode") if proy is not None else None),
        "presupuesto": presu, "cpv": cpv, "plazo": plazo, "actualizado": (upd or "")[:10], "url": url,
    }
    reg.update(territorio([{"descripcion": f"{nuts} - {ciudad or ''}"}] if nuts else []))
    if adj:
        reg["adj"] = adj
    return reg


def adjudicacion(cfs):
    """Resultado de la licitación (TenderResult): solo si hay adjudicatario. None si no lo hay (desierta, sin resolver…).
    Con varios lotes se suman importes y se toma el mínimo de ofertas recibidas."""
    lotes = []
    for tr in cfs.iter():
        if _ln(tr) != "TenderResult":
            continue
        gana = _hijo(tr, "WinningParty")
        nombre = None
        if gana is not None:
            pn = _hijo(gana, "PartyName")
            nombre = _primero(pn, "Name") if pn is not None else None
        if not nombre:
            continue
        ap = _hijo(tr, "AwardedTenderedProject")
        importe = None
        if ap is not None:
            lm = _hijo(ap, "LegalMonetaryTotal")
            if lm is not None:
                importe = _num(_primero(lm, "TaxExclusiveAmount")) or _num(_primero(lm, "PayableAmount"))
        ofertas = _num(_primero(tr, "ReceivedTenderQuantity"))
        lotes.append({"ganador": " ".join(nombre.split()), "importe": importe,
                      "ofertas": int(ofertas) if ofertas is not None else None, "fecha": (_primero(tr, "AwardDate") or "")[:10]})
    if not lotes:
        return None
    of = [l["ofertas"] for l in lotes if l["ofertas"] is not None]
    imp = [l["importe"] for l in lotes if l["importe"]]
    return {"ganador": lotes[0]["ganador"], "lotes": len(lotes), "importe": round(sum(imp), 2) if imp else None,
            "ofertas": min(of) if of else None, "fecha": max((l["fecha"] for l in lotes), default="")}


def lee(xml_bytes):
    """Atom → (lista de registros, url de la página siguiente, fecha más antigua de la página)."""
    raiz = ET.fromstring(xml_bytes)
    regs, antigua = [], None
    for e in raiz:
        if _ln(e) != "entry":
            continue
        u = (_primero(e, "updated") or "")[:10]
        if u and (antigua is None or u < antigua):
            antigua = u
        r = parsea_entrada(e)
        if r:
            regs.append(r)
    nxt = None
    for l in raiz:
        if _ln(l) == "link" and l.get("rel") == "next":
            nxt = l.get("href")
    return regs, nxt, antigua


def abierta(r, hoy):
    return r.get("estado") == "PUB" and (not r.get("plazo") or r["plazo"] >= hoy)


def descarga(hoy):
    url, vistas, minimo = FEED, {}, (date.fromisoformat(hoy) - timedelta(days=VENTANA_DIAS)).isoformat()
    for n in range(MAX_PAGINAS):
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=120) as r:
            regs, nxt, antigua = lee(r.read())
        for x in regs:  # el feed va de más nuevo a más viejo: la primera aparición es la versión vigente
            vistas.setdefault(x["id"], x)
        print(f"página {n + 1}: {len(regs)} registros (hasta {antigua})", flush=True)
        if not nxt or (antigua and antigua < minimo):
            break
        url = nxt
        time.sleep(PAUSA)
    return vistas


def guarda_adjudicaciones(vistas):
    """Acumula adjudicaciones (data/adjudicaciones.json) para las estadísticas de mercado. Se desduplica por expediente+organismo."""
    previas = {}
    if SALIDA_ADJ.exists():
        for r in json.loads(SALIDA_ADJ.read_text(encoding="utf-8")).get("adjudicaciones", []):
            previas[(r["id"], r["organismo"])] = r
    nuevas = 0
    for x in vistas.values():
        a = x.get("adj")
        if not a:
            continue
        k = (x["id"], x["organismo"])
        nuevas += k not in previas
        previas[k] = {"id": x["id"], "organismo": x["organismo"], "titulo": x["titulo"][:160], "tipo": x.get("tipo"),
                      "cpv": x.get("cpv"), "ccaa": x.get("ccaa") or [], "presupuesto": x.get("presupuesto"),
                      "importe": a["importe"], "ofertas": a["ofertas"], "ganador": a["ganador"], "lotes": a["lotes"],
                      "fecha": a["fecha"] or x.get("actualizado"), "url": x.get("url")}
    if not previas:
        print("sin adjudicaciones: no se escribe adjudicaciones.json")
        return
    todas = sorted(previas.values(), key=lambda r: (r["fecha"] or "", r["id"]), reverse=True)[:MAX_ADJ]
    SALIDA_ADJ.write_text(json.dumps({"actualizado": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
                                      "fuente": "Plataforma de Contratación del Sector Público (Ministerio de Hacienda)",
                                      "adjudicaciones": todas}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{len(todas)} adjudicaciones guardadas ({nuevas} nuevas)")


def main():
    hoy = date.today().isoformat()
    if "--from-file" in sys.argv:
        regs, _, _ = lee(Path(sys.argv[sys.argv.index("--from-file") + 1]).read_bytes())
        vistas = {r["id"]: r for r in regs}
    else:
        vistas = descarga(hoy)
    previas = {}
    if SALIDA.exists():
        previas = {r["id"]: r for r in json.loads(SALIDA.read_text(encoding="utf-8")).get("licitaciones", [])}
    guarda_adjudicaciones(vistas)
    for k, v in vistas.items():  # lo recién visto manda sobre lo antiguo; si ya no está publicada, sale de «abiertas»
        if v.get("estado") == "PUB":
            previas[k] = v
        else:
            previas.pop(k, None)
    abiertas = [r for r in previas.values() if abierta(r, hoy)]
    if not abiertas:
        print("sin licitaciones abiertas: no se toca el fichero")
        return 1
    abiertas.sort(key=lambda r: (r["plazo"] or "9999", r["id"]))
    SALIDA.write_text(json.dumps({
        "actualizado": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
        "fuente": "Plataforma de Contratación del Sector Público (Ministerio de Hacienda)",
        "licitaciones": [{k: v for k, v in r.items() if k != "adj"} for r in abiertas]}, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"{len(abiertas)} licitaciones abiertas guardadas")
    return 0


if __name__ == "__main__":
    sys.exit(main())
