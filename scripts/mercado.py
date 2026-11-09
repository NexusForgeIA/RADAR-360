#!/usr/bin/env python3
"""Estadísticas de mercado a partir de data/adjudicaciones.json → data/mercado.json. Sin dependencias.
Solo indicadores objetivos (nº de adjudicaciones, ofertas recibidas, baja sobre presupuesto, importes)."""
import json, re, sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ENTRADA = RAIZ / "data" / "adjudicaciones.json"
SALIDA = RAIZ / "data" / "mercado.json"
MIN_ORG = 5   # adjudicaciones mínimas (con nº de ofertas informado) para listar un organismo
# Solo se rankean personas jurídicas: el nombre de una persona física no se agrega en ningún ranking.
JURIDICA = re.compile(r"\b(S\.?\s?L\.?(U\.?)?|S\.?\s?A\.?(U\.?)?|S\.?\s?COOP|UTE|U\.T\.E|S\.?L\.?L|S\.?C\.?P|FUNDACI[OÓ]N|ASOCIACI[OÓ]N|AGRUPACI[OÓ]N|SOCIEDAD|COOPERATIVA|CONSORCIO|CORPORACI[OÓ]N|EMPRESA)\b", re.I)


def _med(xs):
    return round(sum(xs) / len(xs), 2) if xs else None


def indicadores(rs):
    of = [r["ofertas"] for r in rs if r.get("ofertas")]
    bajas = [1 - r["importe"] / r["presupuesto"] for r in rs
             if r.get("importe") and r.get("presupuesto") and 0 < r["importe"] <= r["presupuesto"]]
    return {"n": len(rs), "importe": round(sum(r["importe"] or 0 for r in rs)),
            "con_ofertas": len(of), "una_oferta": sum(1 for o in of if o == 1),
            "pct_una_oferta": round(100 * sum(1 for o in of if o == 1) / len(of), 1) if of else None,
            "ofertas_media": _med(of), "baja_media": round(100 * _med(bajas), 1) if bajas else None}


def calcula(adj):
    out = {"global": indicadores(adj)}
    fechas = [r["fecha"] for r in adj if r.get("fecha")]
    out["periodo"] = {"desde": min(fechas) if fechas else None, "hasta": max(fechas) if fechas else None}
    for clave, f in (("por_tipo", lambda r: r.get("tipo") or "Otros"),):
        g = defaultdict(list)
        for r in adj:
            g[f(r)].append(r)
        out[clave] = {k: indicadores(v) for k, v in sorted(g.items(), key=lambda kv: -len(kv[1]))}
    g = defaultdict(list)
    for r in adj:
        for c in (r.get("ccaa") or []) [:1]:
            g[c].append(r)
    out["por_ccaa"] = {k: indicadores(v) for k, v in sorted(g.items(), key=lambda kv: -len(kv[1]))}
    g = defaultdict(list)
    for r in adj:
        if r.get("organismo"):
            g[r["organismo"]].append(r)
    orgs = []
    for nombre, rs in g.items():
        ind = indicadores(rs)
        if ind["con_ofertas"] < MIN_ORG:
            continue
        ganadores = Counter(r["ganador"] for r in rs if JURIDICA.search(r["ganador"]))
        top = ganadores.most_common(1)
        ind.update({"organismo": nombre, "ccaa": (rs[0].get("ccaa") or [None])[0],
                    "top_ganador": {"nombre": top[0][0], "n": top[0][1]} if top else None})
        orgs.append(ind)
    orgs.sort(key=lambda o: (-o["n"], o["organismo"]))
    out["por_organismo"] = orgs[:400]
    g = defaultdict(list)
    for r in adj:
        if JURIDICA.search(r["ganador"]):
            g[r["ganador"]].append(r)
    gan = [{"nombre": k, "n": len(v), "importe": round(sum(x["importe"] or 0 for x in v)),
            "organismos": len({x["organismo"] for x in v})} for k, v in g.items()]
    gan.sort(key=lambda a: (-a["importe"], -a["n"]))
    out["top_adjudicatarios"] = gan[:30]
    return out


def main():
    if not ENTRADA.exists():
        print("sin adjudicaciones.json: no se genera mercado.json")
        return 1
    adj = json.loads(ENTRADA.read_text(encoding="utf-8")).get("adjudicaciones", [])
    if not adj:
        return 1
    res = calcula(adj)
    res["actualizado"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    res["fuente"] = "Plataforma de Contratación del Sector Público (Ministerio de Hacienda)"
    SALIDA.write_text(json.dumps(res, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    g = res["global"]
    print(f"mercado.json: {g['n']} adjudicaciones, {len(res['por_organismo'])} organismos, una oferta {g['pct_una_oferta']}%")
    return 0


if __name__ == "__main__":
    sys.exit(main())
