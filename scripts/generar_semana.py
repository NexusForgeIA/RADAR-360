#!/usr/bin/env python3
"""Página /semana/: resumen automático con lo más relevante de la semana (ayudas con plazo próximo, licitaciones y adjudicaciones
más grandes). Se regenera en cada ejecución. Lo llama generar_seo.py."""
import json
from datetime import date, timedelta

from generar_seo import BASE, IMG, RAIZ, esc, fecha_es
from generar_organismos import cargar, eur, ganador, num
from mercado import reciente


def genera():
    c, l, a = cargar("convocatorias.json"), cargar("licitaciones.json"), cargar("adjudicaciones.json")
    if not c or not l:
        return []
    hoy = date.today().isoformat()
    en30 = (date.today() + timedelta(days=30)).isoformat()
    ayudas = sorted([x for x in c["convocatorias"] if (x.get("tipo") or "").lower().startswith("concurrencia") and x.get("presupuesto")
                     and hoy <= (x.get("fin") or "") <= en30], key=lambda x: -x["presupuesto"])[:10]
    abiertas = sorted([x for x in l["licitaciones"] if x.get("presupuesto") and (x.get("plazo") or "9999") >= hoy], key=lambda x: -x["presupuesto"])[:10]
    adj = []
    if a:
        todas = reciente(a["adjudicaciones"])
        if todas:
            ref = max(x["fecha"] for x in todas if x.get("fecha"))
            desde = (date.fromisoformat(ref) - timedelta(days=7)).isoformat()
            adj = sorted([x for x in todas if (x.get("fecha") or "") > desde and x.get("importe")], key=lambda x: -x["importe"])[:10]
    if not (ayudas or abiertas or adj):
        return []
    li_ay = "".join(f'<li><a href="{esc(x["url"])}" rel="noopener nofollow">{esc(x["descripcion"][:220])}</a><small>' + " · ".join(esc(y) for y in [
        x.get("organismo") or "", "presupuesto " + eur(x["presupuesto"]), "plazo hasta " + fecha_es(x["fin"])] if y) + "</small></li>" for x in ayudas)
    li_li = "".join(f'<li><a href="{esc(x["url"])}" rel="noopener nofollow">{esc(x["titulo"][:220])}</a><small>' + " · ".join(esc(y) for y in [
        x.get("organismo") or "", x.get("tipo") or "", "presupuesto " + eur(x["presupuesto"]), ("plazo hasta " + fecha_es(x["plazo"])) if x.get("plazo") else ""] if y) + "</small></li>" for x in abiertas)
    li_ad = "".join(f'<li><a href="{esc(x["url"])}" rel="noopener nofollow">{esc(x["titulo"][:220])}</a><small>' + " · ".join(esc(y) for y in [
        x.get("organismo") or "", eur(x["importe"]), f'{x["ofertas"]} ofertas' if x.get("ofertas") else "", "Adjudicado a " + ganador(x)] if y) + "</small></li>" for x in adj)
    act = (l.get("actualizado") or "")[:10] or hoy
    url = f"{BASE}/semana/"
    titulo = "Resumen de la semana: ayudas, licitaciones y adjudicaciones más grandes · RADAR 360"
    desc = "Las ayudas con plazo más próximo, las licitaciones abiertas más grandes y las mayores adjudicaciones de la semana en España. Datos oficiales, actualizados a diario."
    ld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": "Resumen de la semana", "description": desc, "url": url, "inLanguage": "es", "dateModified": act}
    def bloque(h, items, vacio):
        return f"<h2>{h}</h2>\n  " + (f'<ul class="seo-list">{items}</ul>' if items else f"<p>{vacio}</p>")
    html = f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(titulo)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="48x48" href="/assets/img/favicon-48.png">
<meta property="og:type" content="website">
<meta property="og:site_name" content="RADAR 360">
<meta property="og:locale" content="es_ES">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{esc(titulo)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{IMG}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{IMG}">
<link rel="stylesheet" href="/assets/style.css">
<link rel="manifest" href="/manifest.webmanifest">
<meta name="theme-color" content="#071024">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>
<body>
<header class="top"><div class="wrap bar">
  <a class="logo" href="/" aria-label="RADAR 360 · inicio"><img src="/assets/img/logo-nav.png" alt="RADAR 360" width="112" height="48"></a>
  <span class="tag"><a href="/licitaciones/" class="navlink">Licitaciones</a><a href="/mercado/" class="navlink">Mercado</a></span>
</div></header>
<main class="wrap seo">
  <p class="crumbs"><a href="/">RADAR 360</a> › Resumen de la semana</p>
  <h1>Resumen de la semana</h1>
  <p class="lead2">Lo más relevante de la contratación pública y las subvenciones en España, ordenado por importe. Se actualiza solo con los datos oficiales de la BDNS y de la Plataforma de Contratación.</p>
  <p class="upd2">Datos actualizados el {esc(fecha_es(act))}.</p>
  {bloque("Ayudas con plazo en los próximos 30 días (mayor presupuesto)", li_ay, "No hay ayudas de concurrencia con presupuesto informado y plazo próximo en nuestros datos.")}
  {bloque("Licitaciones abiertas más grandes", li_li, "No hay licitaciones abiertas con presupuesto informado.")}
  {bloque("Mayores adjudicaciones de los últimos 7 días", li_ad, "Aún no hay adjudicaciones recientes cargadas.")}
  <p><a class="cta" href="/">Buscar ayudas →</a> <a class="cta" href="/licitaciones/">Ver licitaciones →</a> <a class="cta" href="/mercado/">Estadísticas del mercado →</a></p>
  <h2>Cómo leer esta página</h2>
  <ul>
    <li>Son datos oficiales ordenados por importe; el importe no indica que la ayuda o el contrato encajen contigo. Comprueba plazo, requisitos y pliegos en la ficha oficial.</li>
    <li>Las ayudas excluyen concesiones directas y convenios con una entidad concreta. Las adjudicaciones solo nombran personas jurídicas. Los datos pueden contener errores de la fuente.</li>
  </ul>
</main>
<footer><div class="wrap"><a href="/aviso-legal/">Aviso legal</a> · <a href="/privacidad/">Privacidad</a> · <a href="/cookies/">Cookies</a><br>RADAR 360 · proyecto de <a href="https://whitemoon.es" rel="noopener">WhiteMoon</a>. Información orientativa de fuentes oficiales: más detalle en el <a href="/aviso-legal/">aviso legal</a>.</div></footer>
<script src="/assets/nav.js" defer></script>
</body>
</html>
'''
    d = RAIZ / "semana"
    d.mkdir(exist_ok=True)
    (d / "index.html").write_text(html, encoding="utf-8")
    return [url]
