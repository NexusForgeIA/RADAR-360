#!/usr/bin/env python3
"""Páginas estáticas por sector de contratación (/sectores/…), agrupando por división CPV (2 primeros dígitos).
Datos: licitaciones.json (abiertas) y adjudicaciones.json (últimos 90 días). Lo llama generar_seo.py."""
import json, shutil
from collections import Counter

from generar_seo import BASE, IMG, RAIZ, esc, fecha_es, slug
from generar_organismos import cargar, eur, ganador, num
from mercado import JURIDICA, indicadores, reciente

# División CPV → (nombre del sector, "licitaciones de …")
CPV = {
    "03": "Agricultura, ganadería y pesca", "09": "Combustibles y energía", "15": "Alimentación y bebidas", "18": "Ropa y calzado",
    "22": "Impresión y papelería", "24": "Productos químicos", "30": "Equipos informáticos y de oficina", "31": "Material eléctrico",
    "32": "Equipos de telecomunicaciones", "33": "Equipos médicos y material sanitario", "34": "Vehículos y equipos de transporte",
    "35": "Seguridad y defensa", "37": "Material deportivo y musical", "38": "Equipos de laboratorio y precisión", "39": "Mobiliario y equipamiento",
    "42": "Maquinaria industrial", "44": "Materiales de construcción", "45": "Obras de construcción", "48": "Software y sistemas de información",
    "50": "Mantenimiento y reparación", "55": "Hostelería y restauración", "60": "Transporte de viajeros y mercancías",
    "64": "Correos y telecomunicaciones", "65": "Agua, gas y electricidad (suministro)", "66": "Servicios financieros y seguros",
    "70": "Servicios inmobiliarios", "71": "Arquitectura e ingeniería", "72": "Servicios informáticos y desarrollo de software",
    "73": "Investigación y desarrollo", "75": "Servicios de administración pública", "77": "Servicios agrícolas y forestales",
    "79": "Servicios a empresas (consultoría, publicidad, jurídicos)", "80": "Educación y formación", "85": "Servicios sanitarios y sociales",
    "90": "Limpieza, residuos y medio ambiente", "92": "Servicios culturales, recreativos y deportivos", "98": "Otros servicios comunitarios y personales",
}
MIN_ABIERTAS, MIN_ADJ = 8, 15


def genera():
    a, l, m = cargar("adjudicaciones.json"), cargar("licitaciones.json"), cargar("mercado.json")
    salida = RAIZ / "sectores"
    if salida.exists():
        shutil.rmtree(salida)
    if not a or not l:
        return []
    adj = reciente(a["adjudicaciones"])
    act = (m or {}).get("actualizado") or l.get("actualizado") or ""
    org_slugs = {}
    if (RAIZ / "organismos").exists():
        for o in (m or {}).get("por_organismo", []):
            s = slug(o["organismo"])[:80].strip("-")
            if (RAIZ / "organismos" / s).exists():
                org_slugs[o["organismo"]] = s
    paginas = []
    for cod, nombre in CPV.items():
        ab = sorted([x for x in l["licitaciones"] if (x.get("cpv") or "").startswith(cod)], key=lambda r: r.get("plazo") or "9999")
        ad = sorted([x for x in adj if (x.get("cpv") or "").startswith(cod)], key=lambda r: (r.get("fecha") or "", r["id"]), reverse=True)
        if len(ab) < MIN_ABIERTAS and len(ad) < MIN_ADJ:
            continue
        paginas.append((cod, nombre, ab, ad))
    if not paginas:
        return []
    salida.mkdir()
    todos = [(nombre, f"{slug(nombre)}") for _, nombre, _, _ in paginas]
    urls = [f"{BASE}/sectores/"]
    for cod, nombre, ab, ad in paginas:
        s = slug(nombre)
        url = f"{BASE}/sectores/{s}/"
        ind = indicadores(ad)
        h1 = f"Licitaciones y adjudicaciones de {nombre.lower()}"
        titulo = f"Licitaciones de {nombre.lower()}: abiertas y adjudicadas · RADAR 360"
        desc = (f"{len(ab)} licitaciones abiertas de {nombre.lower()} y {ind['n']} adjudicaciones recientes: ofertas por contrato, baja media y organismos que más contratan. Datos oficiales.")
        resumen = f"Ahora mismo hay <strong>{len(ab)}</strong> licitaciones abiertas de {esc(nombre.lower())} (CPV {cod}) en la Plataforma de Contratación."
        if ind["n"]:
            resumen += (f" En los últimos 90 días se adjudicaron <strong>{ind['n']}</strong> contratos del sector"
                        + (f" por {esc(eur(ind['importe']))} (sin IVA)" if ind.get("importe") else "")
                        + f"; el <strong>{num(ind['pct_una_oferta'])} %</strong> recibió una sola oferta, con {num(ind['ofertas_media'])} ofertas de media"
                        + (f" y una baja media del {num(ind['baja_media'])} %" if ind.get("baja_media") is not None else "") + ".")
        li_ab = "".join(
            f'<li><a href="{esc(x["url"])}" rel="noopener nofollow">{esc(x["titulo"])}</a><small>' + " · ".join(esc(y) for y in [
                x.get("organismo") or "", ("presupuesto " + eur(x["presupuesto"])) if x.get("presupuesto") else "",
                ("plazo hasta " + fecha_es(x["plazo"])) if x.get("plazo") else "plazo: ver ficha"] if y) + "</small></li>" for x in ab[:20])
        li_ad = "".join(
            f'<li><a href="{esc(x["url"])}" rel="noopener nofollow">{esc(x["titulo"])}</a><small>' + " · ".join(esc(y) for y in [
                fecha_es(x.get("fecha")), x.get("organismo") or "", eur(x.get("importe")), f'{x["ofertas"]} ofertas' if x.get("ofertas") else "",
                "Adjudicado a " + ganador(x)] if y) + "</small></li>" for x in ad[:15])
        orgs = Counter(x["organismo"] for x in ad if x.get("organismo")).most_common(8)
        li_org = ", ".join((f'<a href="/organismos/{org_slugs[o]}/">{esc(o)}</a>' if o in org_slugs else esc(o)) + f" ({n})" for o, n in orgs)
        ab_bloque = (f'<h2>Licitaciones abiertas ({len(ab)})</h2>\n  <ul class="seo-list">{li_ab}</ul>' if ab else
                     "<h2>Licitaciones abiertas</h2>\n  <p>Ahora mismo no hay licitaciones abiertas de este sector en nuestros datos.</p>")
        nav = "".join(f'<a href="/sectores/{t}/">{esc(n)}</a>' for n, t in todos if t != s)[:6000]
        crumbs = [("RADAR 360", BASE + "/"), ("Sectores", BASE + "/sectores/"), (nombre, url)]
        ld = {"@context": "https://schema.org", "@graph": [
            {"@type": "CollectionPage", "name": h1, "description": desc, "url": url, "inLanguage": "es", "dateModified": act[:10]},
            {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(crumbs)]}]}
        (salida / s).mkdir()
        (salida / s / "index.html").write_text(f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(titulo)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="48x48" href="/assets/img/favicon-48.png">
<link rel="icon" type="image/png" sizes="96x96" href="/assets/img/favicon-96.png">
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
  <span class="tag"><a href="/licitaciones/" class="navlink">Licitaciones</a><a href="/mercado/" class="navlink">Mercado</a><i class="live"></i>Datos oficiales · Gratis</span>
</div></header>
<main class="wrap seo">
  <p class="crumbs"><a href="/">RADAR 360</a> › <a href="/sectores/">Sectores</a> › {esc(nombre)}</p>
  <h1>{esc(h1)}</h1>
  <p class="lead2">{resumen}</p>
  <p class="upd2">Datos actualizados el {esc(fecha_es(act))}. Origen: Plataforma de Contratación del Sector Público.</p>
  {ab_bloque}
  {("<h2>Últimas adjudicaciones</h2>" + chr(10) + '  <ul class="seo-list">' + li_ad + "</ul>") if li_ad else ""}
  {("<h2>Organismos que más contratan en este sector</h2>" + chr(10) + "  <p>" + li_org + ".</p>") if li_org else ""}
  <p><a class="cta" href="/licitaciones/">Filtrar todas las licitaciones →</a> <a class="cta" href="/mercado/">Estadísticas del mercado →</a></p>
  <h2>Otros sectores</h2>
  <nav class="seo-nav">{nav}</nav>
  <h2>Cómo leer esta página</h2>
  <ul>
    <li>El sector sale del código CPV principal que el órgano de contratación asigna al contrato (división de 2 dígitos); un contrato puede abarcar varios ámbitos.</li>
    <li>Datos oficiales agregados por RADAR 360 a partir del feed de datos abiertos de la Plataforma de Contratación; pueden contener errores de la fuente. El plazo, los pliegos y los requisitos solo valen en la ficha oficial.</li>
    <li>Una sola oferta es un indicador de competencia, no de irregularidad. Las adjudicaciones cubren los últimos 90 días y solo se nombran personas jurídicas.</li>
  </ul>
</main>
<footer><div class="wrap"><a href="/aviso-legal/">Aviso legal</a> · <a href="/privacidad/">Privacidad</a> · <a href="/cookies/">Cookies</a><br>RADAR 360 · proyecto de <a href="https://whitemoon.es" rel="noopener">WhiteMoon</a>. Información orientativa de fuentes oficiales: más detalle en el <a href="/aviso-legal/">aviso legal</a>.</div></footer>
<script src="/assets/nav.js" defer></script>
</body>
</html>
''', encoding="utf-8")
        urls.append(url)
    items = "".join(f'<li><a href="/sectores/{slug(n)}/">{esc(n)}</a><small>{len(ab)} abiertas · {len(ad)} adjudicaciones recientes</small></li>' for _, n, ab, ad in paginas)
    (salida / "index.html").write_text(f'''<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Licitaciones públicas por sector · RADAR 360</title>
<meta name="description" content="Licitaciones abiertas y adjudicaciones por sector: obras, informática, limpieza, sanidad, mantenimiento y más. Datos oficiales de la Plataforma de Contratación.">
<link rel="canonical" href="{BASE}/sectores/"><link rel="icon" href="/favicon.ico" sizes="any"><meta property="og:image" content="{IMG}">
<link rel="stylesheet" href="/assets/style.css"><link rel="manifest" href="/manifest.webmanifest"><meta name="theme-color" content="#071024">
</head><body>
<header class="top"><div class="wrap bar"><a class="logo" href="/" aria-label="RADAR 360 · inicio"><img src="/assets/img/logo-nav.png" alt="RADAR 360" width="112" height="48"></a>
<span class="tag"><a href="/licitaciones/" class="navlink">Licitaciones</a><a href="/mercado/" class="navlink">Mercado</a></span></div></header>
<main class="wrap seo"><p class="crumbs"><a href="/">RADAR 360</a> › Sectores</p>
<h1>Licitaciones públicas por sector</h1>
<p class="lead2">Elige tu sector para ver las licitaciones abiertas, las últimas adjudicaciones y los organismos que más contratan.</p>
<ul class="seo-list">{items}</ul></main>
<footer><div class="wrap"><a href="/aviso-legal/">Aviso legal</a> · <a href="/privacidad/">Privacidad</a> · <a href="/cookies/">Cookies</a></div></footer>
<script src="/assets/nav.js" defer></script></body></html>
''', encoding="utf-8")
    return urls
