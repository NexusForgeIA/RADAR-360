#!/usr/bin/env python3
"""Páginas estáticas por organismo contratante (/organismos/…) a partir de data/mercado.json, data/adjudicaciones.json
y data/licitaciones.json. Solo organismos con datos suficientes (los que ya recoge mercado.json). Lo llama generar_seo.py."""
import json, shutil
from pathlib import Path

from generar_seo import BASE, IMG, RAIZ, esc, fecha_es, slug
from mercado import JURIDICA, reciente

MAX_ADJ = 15
MAX_ABIERTAS = 15


def cargar(nombre):
    p = RAIZ / "data" / nombre
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def eur(x):
    return f"{x:,.0f} €".replace(",", ".") if x else ""


def num(x):
    return f"{x:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".") if x is not None else "—"


def ganador(a):
    return a["ganador"] if JURIDICA.search(a["ganador"]) else "persona física (no se lista)"


def pagina(o, slug_o, adj, abiertas, vecinos, actualizado):
    org = o["organismo"]
    url = f"{BASE}/organismos/{slug_o}/"
    h1 = f"Licitaciones y adjudicaciones de {org}"
    titulo = f"{org}: contratos adjudicados y licitaciones abiertas · RADAR 360"
    una = o["pct_una_oferta"]
    desc = (f"{org}: {o['n']} contratos adjudicados en los últimos 90 días, {num(una)} % con una sola oferta, "
            f"baja media {num(o['baja_media'])} %. Licitaciones abiertas y adjudicatarios, con datos oficiales.")
    resumen = (f"En los últimos 90 días, {esc(org)} adjudicó <strong>{o['n']}</strong> contratos"
               + (f" por un importe de {esc(eur(o['importe']))} (sin IVA)" if o.get("importe") else "")
               + f". El <strong>{num(una)} %</strong> recibió una sola oferta; la media es de {num(o['ofertas_media'])} ofertas por contrato"
               + (f" y la baja media sobre el presupuesto es del {num(o['baja_media'])} %" if o.get("baja_media") is not None else "") + ".")
    items_adj = "".join(
        f'<li><a href="{esc(a["url"])}" rel="noopener nofollow">{esc(a["titulo"])}</a><small>'
        + " · ".join(esc(x) for x in [fecha_es(a.get("fecha")), a.get("tipo") or "", eur(a.get("importe")),
                                       f'{a["ofertas"]} ofertas' if a.get("ofertas") else "", "Adjudicado a " + ganador(a)] if x) + "</small></li>"
        for a in adj[:MAX_ADJ])
    items_ab = "".join(
        f'<li><a href="{esc(l["url"])}" rel="noopener nofollow">{esc(l["titulo"])}</a><small>'
        + " · ".join(esc(x) for x in [l.get("tipo") or "", ("presupuesto " + eur(l["presupuesto"])) if l.get("presupuesto") else "",
                                       ("plazo hasta " + fecha_es(l["plazo"])) if l.get("plazo") else "plazo: ver ficha"] if x) + "</small></li>"
        for l in abiertas[:MAX_ABIERTAS])
    ab_bloque = (f'<h2>Licitaciones abiertas ({len(abiertas)})</h2>\n  <ul class="seo-list">{items_ab}</ul>' if abiertas else
                 "<h2>Licitaciones abiertas</h2>\n  <p>Ahora mismo no hay licitaciones abiertas de este organismo en nuestros datos.</p>")
    gan = {}
    for a in adj:
        if JURIDICA.search(a["ganador"]):
            gan[a["ganador"]] = gan.get(a["ganador"], 0) + 1
    top = sorted(gan.items(), key=lambda kv: (-kv[1], kv[0]))[:5]
    gan_bloque = ("<p>Adjudicatarios que más se repiten: " + ", ".join(f"{esc(n)} ({c})" for n, c in top if c >= 2) + ".</p>") if any(c >= 2 for _, c in top) else ""
    nav = "".join(f'<a href="/organismos/{s}/">{esc(n)}</a>' for n, s in vecinos)
    crumbs = [("RADAR 360", BASE + "/"), ("Organismos", BASE + "/organismos/"), (org, url)]
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "CollectionPage", "name": h1, "description": desc, "url": url, "inLanguage": "es", "dateModified": actualizado[:10]},
        {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(crumbs)]}]}
    return f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(titulo)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="{url}">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/img/favicon-32.png">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="48x48" href="/assets/img/favicon-48.png">
<link rel="icon" type="image/png" sizes="96x96" href="/assets/img/favicon-96.png">
<link rel="icon" type="image/png" sizes="192x192" href="/assets/img/favicon-192.png">
<meta property="og:type" content="website">
<meta property="og:site_name" content="RADAR 360">
<meta property="og:locale" content="es_ES">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{esc(titulo)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{IMG}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{IMG}">
<link rel="stylesheet" href="/assets/style.css">
<link rel="manifest" href="/manifest.webmanifest">
<meta name="theme-color" content="#071024">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="RADAR 360">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>
<body>
<header class="top"><div class="wrap bar">
  <a class="logo" href="/" aria-label="RADAR 360 · inicio"><img src="/assets/img/logo-nav.png" alt="RADAR 360" width="112" height="48"></a>
  <span class="tag"><a href="/licitaciones/" class="navlink">Licitaciones</a><a href="/mercado/" class="navlink">Mercado</a></span>
</div></header>
<main class="wrap seo">
  <p class="crumbs"><a href="/">RADAR 360</a> › <a href="/organismos/">Organismos</a> › {esc(org)}</p>
  <h1>{esc(h1)}</h1>
  <p class="lead2">{resumen}</p>
  <p class="upd2">Datos actualizados el {esc(fecha_es(actualizado))}. Origen: Plataforma de Contratación del Sector Público.</p>
  {ab_bloque}
  <h2>Últimas adjudicaciones</h2>
  <ul class="seo-list">{items_adj}</ul>
  {gan_bloque}
  <p><a class="cta" href="/mercado/">Ver estadísticas de todo el mercado →</a></p>
  <h2>Otros organismos</h2>
  <nav class="seo-nav">{nav}</nav>
  <h2>Cómo leer esta página</h2>
  <ul>
    <li>Son datos oficiales agregados por RADAR 360 a partir del feed de datos abiertos de la Plataforma de Contratación; pueden contener errores de la fuente. Contrasta siempre en la ficha oficial.</li>
    <li>Una sola oferta es un indicador de competencia, no de irregularidad. RADAR 360 no valora la legalidad ni la conveniencia de ninguna adjudicación.</li>
    <li>Solo se listan por nombre las personas jurídicas adjudicatarias. El cálculo cubre los últimos 90 días, no es un histórico completo.</li>
  </ul>
</main>
<footer><div class="wrap"><a href="/aviso-legal/">Aviso legal</a> · <a href="/privacidad/">Privacidad</a> · <a href="/cookies/">Cookies</a><br>RADAR 360 · proyecto de <a href="https://whitemoon.es" rel="noopener">WhiteMoon</a>. Información orientativa de fuentes oficiales: más detalle en el <a href="/aviso-legal/">aviso legal</a>.</div></footer>
<script src="/assets/nav.js" defer></script>
</body>
</html>
'''


def genera():
    """Devuelve la lista de URLs generadas (para el sitemap). Sin datos de mercado, no genera nada."""
    m, a, l = cargar("mercado.json"), cargar("adjudicaciones.json"), cargar("licitaciones.json")
    salida = RAIZ / "organismos"
    if salida.exists():
        shutil.rmtree(salida)
    if not m or not a or not m.get("por_organismo"):
        return []
    adj = sorted(reciente(a["adjudicaciones"]), key=lambda r: (r.get("fecha") or "", r["id"]), reverse=True)
    por_org, abiertas = {}, {}
    for r in adj:
        por_org.setdefault(r["organismo"], []).append(r)
    for r in (l or {}).get("licitaciones", []):
        abiertas.setdefault(r["organismo"], []).append(r)
    act = m.get("actualizado") or ""
    usados, orgs = set(), []
    for o in m["por_organismo"]:
        s = slug(o["organismo"])[:80].strip("-") or "organismo"
        while s in usados:
            s += "-2"
        usados.add(s)
        orgs.append((o, s))
    salida.mkdir()
    for o, s in orgs:
        mismos = [(x["organismo"], t) for x, t in orgs if x["ccaa"] == o["ccaa"] and x is not o][:10]
        vecinos = mismos or [(x["organismo"], t) for x, t in orgs if x is not o][:10]
        (salida / s).mkdir()
        (salida / s / "index.html").write_text(
            pagina(o, s, por_org.get(o["organismo"], []), sorted(abiertas.get(o["organismo"], []), key=lambda r: r.get("plazo") or "9999"), vecinos, act),
            encoding="utf-8")
    items = "".join(f'<li><a href="/organismos/{s}/">{esc(o["organismo"])}</a><small>{o["n"]} adjudicaciones · {num(o["pct_una_oferta"])} % con una sola oferta</small></li>' for o, s in orgs)
    idx = f'''<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Organismos contratantes: adjudicaciones y licitaciones · RADAR 360</title>
<meta name="description" content="Directorio de organismos públicos con sus contratos adjudicados, ofertas recibidas y licitaciones abiertas. Datos de la Plataforma de Contratación.">
<link rel="canonical" href="{BASE}/organismos/"><link rel="icon" type="image/png" sizes="32x32" href="/assets/img/favicon-32.png">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" type="image/png" sizes="48x48" href="/assets/img/favicon-48.png">
<link rel="icon" type="image/png" sizes="96x96" href="/assets/img/favicon-96.png">
<link rel="icon" type="image/png" sizes="192x192" href="/assets/img/favicon-192.png">
<meta property="og:image" content="{IMG}"><link rel="stylesheet" href="/assets/style.css"><link rel="manifest" href="/manifest.webmanifest"><meta name="theme-color" content="#071024">
</head><body>
<header class="top"><div class="wrap bar"><a class="logo" href="/" aria-label="RADAR 360 · inicio"><img src="/assets/img/logo-nav.png" alt="RADAR 360" width="112" height="48"></a>
<span class="tag"><a href="/licitaciones/" class="navlink">Licitaciones</a><a href="/mercado/" class="navlink">Mercado</a></span></div></header>
<main class="wrap seo"><p class="crumbs"><a href="/">RADAR 360</a> › Organismos</p>
<h1>Organismos contratantes</h1>
<p class="lead2">Organismos con al menos 5 adjudicaciones recientes en la Plataforma de Contratación del Sector Público. Entra en uno para ver sus licitaciones abiertas, las últimas adjudicaciones y cuánta competencia recibe.</p>
<ul class="seo-list">{items}</ul></main>
<footer><div class="wrap"><a href="/aviso-legal/">Aviso legal</a> · <a href="/privacidad/">Privacidad</a> · <a href="/cookies/">Cookies</a></div></footer>
<script src="/assets/nav.js" defer></script></body></html>
'''
    (salida / "index.html").write_text(idx, encoding="utf-8")
    return [f"{BASE}/organismos/"] + [f"{BASE}/organismos/{s}/" for _, s in orgs]
