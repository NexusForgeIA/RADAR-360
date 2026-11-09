#!/usr/bin/env python3
"""Genera páginas estáticas indexables (/ayudas/…) y sitemap.xml a partir de data/convocatorias.json.
Solo se crea una página si tiene al menos MIN resultados: así no hay páginas vacías ni casi idénticas."""
import html, json, re, shutil, sys, unicodedata
from collections import Counter
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
RAIZ = Path(__file__).resolve().parent.parent
BASE = "https://radar360pymes.onrender.com"
MIN = 5           # mínimo de convocatorias para publicar una página
MAX_LISTA = 60    # máximo de convocatorias listadas por página
IMG = BASE + "/assets/img/og-radar360.png"

PERFIL_TEMAS = {
    "negocio": ["Empresas y empleo", "Energía y medio ambiente", "Vivienda y fachadas", "Agro, pesca y animales"],
    "empresa": ["Empresas y empleo", "Energía y medio ambiente"],
    "persona": ["Educación y becas", "Social y salud", "Vivienda y fachadas", "Deporte"],
    "entidad": ["Cultura y festejos", "Deporte", "Social y salud", "Otros"],
}
PERFILES = {  # clave: (slug, título, quién)
    "negocio": ("autonomos-y-pymes", "Ayudas y subvenciones para autónomos y pymes", "autónomos, pymes y emprendedores"),
    "empresa": ("grandes-empresas", "Ayudas y subvenciones para grandes empresas", "grandes empresas"),
    "persona": ("personas", "Ayudas y subvenciones para personas y familias", "personas, familias y estudiantes"),
    "entidad": ("asociaciones", "Ayudas y subvenciones para asociaciones y entidades sin ánimo de lucro", "asociaciones y entidades sin ánimo de lucro"),
}


def slug(s):
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def esc(s):
    return html.escape(str(s or ""), quote=True)


def fecha_es(iso):
    return "/".join(reversed(iso[:10].split("-"))) if iso else ""


def perfil_de(c):
    if c.get("ficha"):
        return set(c.get("perfiles") or [])
    return {p for p, temas in PERFIL_TEMAS.items() if c.get("tema") in temas}


def ccaas_de(c):
    return set(c.get("ccaa") or [])


def tarjeta(c):
    meta = [esc(fecha_es(c.get("fecha"))), esc(c.get("organismo")), esc(c.get("tema"))]
    extra = ""
    if c.get("fin"):
        extra = f' · plazo hasta {esc(fecha_es(c["fin"]))}'
    if c.get("presupuesto"):
        extra += f' · presupuesto {c["presupuesto"]:,.0f} €'.replace(",", ".")
    return (f'<li><a href="{esc(c["url"])}" rel="noopener nofollow">{esc(c["descripcion"])}</a>'
            f'<small>{" · ".join(m for m in meta if m)}{extra}</small></li>')


def pagina(ruta, titulo, h1, desc, intro, lista, total, actualizado, enlaces, crumbs):
    url = f"{BASE}/ayudas/{ruta}" if ruta else f"{BASE}/ayudas/"
    org = Counter(c["organismo"] for c in lista if c.get("organismo")).most_common(5)
    temas = Counter(c["tema"] for c in lista if c.get("tema")).most_common(4)
    resumen = ""
    if org:
        resumen += "<p>Los organismos que más convocan en este listado: " + ", ".join(
            f"{esc(o)} ({n})" for o, n in org) + ".</p>"
    if temas and len(temas) > 1:
        resumen += "<p>Por tema (clasificación automática orientativa): " + ", ".join(
            f"{esc(t)} ({n})" for t, n in temas) + ".</p>"
    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "CollectionPage", "name": h1, "description": desc, "url": url, "inLanguage": "es",
         "dateModified": actualizado[:10]},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(crumbs)]}]}
    nav = "".join(f'<a href="{esc(h)}">{esc(t)}</a>' for t, h in enlaces)
    cr = " › ".join(f'<a href="{esc(u)}">{esc(n)}</a>' for n, u in crumbs[:-1]) + f" › {esc(crumbs[-1][0])}"
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
  <span class="tag"><a href="/panel/" class="navlink">Panel</a><i class="live"></i>Datos de BDNS · Gratis</span>
</div></header>
<main class="wrap seo">
  <p class="crumbs">{cr}</p>
  <h1>{esc(h1)}</h1>
  <p class="lead2">{intro}</p>
  <p class="upd2">Datos actualizados el {esc(fecha_es(actualizado))}. Origen: BDNS (Intervención General de la Administración del Estado).</p>
  <p><a class="cta" href="/">Buscar con mis filtros →</a></p>
  {resumen}
  <h2>{total} convocatorias recientes{f" (se muestran las {len(lista)} más recientes)" if total > len(lista) else ""}</h2>
  <ul class="seo-list">
{chr(10).join(tarjeta(c) for c in lista)}
  </ul>
  <h2>Más búsquedas</h2>
  <nav class="seo-nav">{nav}</nav>
  <h2>Cómo leer esta página</h2>
  <ul>
    <li>Cada enlace lleva a la ficha oficial de la convocatoria en la BDNS: allí están las bases, los requisitos y el plazo.</li>
    <li>El listado recoge las convocatorias publicadas en los últimos días; no es un histórico completo.</li>
    <li>El tema se asigna automáticamente por palabras clave del título y puede fallar. Aparecer aquí no significa que puedas optar a la ayuda ni que te la concedan.</li>
  </ul>
</main>
<footer><div class="wrap"><a href="/aviso-legal/">Aviso legal</a> · <a href="/privacidad/">Privacidad</a> · <a href="/cookies/">Cookies</a><br>RADAR 360 · proyecto de <a href="https://whitemoon.es" rel="noopener">WhiteMoon</a>. Información orientativa de fuentes oficiales: más detalle en el <a href="/aviso-legal/">aviso legal</a>.</div></footer>
<script src="/assets/nav.js" defer></script>
</body>
</html>
'''


def main():
    d = json.loads((RAIZ / "data" / "convocatorias.json").read_text(encoding="utf-8"))
    regs = d["convocatorias"]
    act = d.get("actualizado") or date.today().isoformat()
    regs = sorted(regs, key=lambda c: c.get("fecha") or "", reverse=True)

    grupos = []  # (ruta, h1, titulo, desc, intro, lista)
    for k, (sl, h1, quien) in PERFILES.items():
        lista = [c for c in regs if k in perfil_de(c)]
        grupos.append((f"{sl}/", h1, f"{h1} · RADAR 360",
                       f"Convocatorias recientes de ayudas y subvenciones para {quien} publicadas en la BDNS, con enlace a la ficha oficial.",
                       f"Convocatorias de ayudas y subvenciones recientes que, según la BDNS o por orientación automática, se dirigen a {quien}.", lista))
    for t in sorted({c["tema"] for c in regs if c.get("tema") and c["tema"] not in ("Otros", "Concesión directa y convenios")}):
        lista = [c for c in regs if c.get("tema") == t]
        grupos.append((f"{slug(t)}/", f"Ayudas y subvenciones: {t}", f"Ayudas y subvenciones de {t} · RADAR 360",
                       f"Convocatorias recientes de ayudas y subvenciones del tema «{t}» publicadas en la BDNS, con enlace oficial.",
                       f"Convocatorias recientes clasificadas en «{esc(t)}». La clasificación es automática por palabras clave.", lista))
    for cc in sorted({x for c in regs for x in ccaas_de(c)}):
        lista = [c for c in regs if cc in ccaas_de(c)]
        grupos.append((f"{slug(cc)}/", f"Ayudas y subvenciones en {cc}", f"Ayudas y subvenciones en {cc} · RADAR 360",
                       f"Convocatorias recientes de ayudas y subvenciones con ámbito en {cc} publicadas en la BDNS, con enlace oficial.",
                       f"Convocatorias recientes cuyo territorio oficial incluye {esc(cc)}.", lista))

    grupos = [g for g in grupos if len(g[5]) >= MIN]
    salida = RAIZ / "ayudas"
    if salida.exists():
        shutil.rmtree(salida)
    salida.mkdir()
    crumbs0 = [("RADAR 360", BASE + "/"), ("Ayudas", BASE + "/ayudas/")]
    enlaces_todos = [(g[1], f"/ayudas/{g[0]}") for g in grupos]
    for ruta, h1, titulo, desc, intro, lista in grupos:
        otros = [(t, h) for t, h in enlaces_todos if h != f"/ayudas/{ruta}"][:14]
        (salida / ruta).mkdir(parents=True)
        (salida / ruta / "index.html").write_text(
            pagina(ruta, titulo, h1, desc, intro, lista[:MAX_LISTA], len(lista), act,
                   [("Todas las ayudas", "/ayudas/")] + otros, crumbs0 + [(h1, f"{BASE}/ayudas/{ruta}")]),
            encoding="utf-8")

    # índice /ayudas/
    items = "".join(f'<li><a href="/ayudas/{g[0]}">{esc(g[1])}</a><small>{len(g[5])} convocatorias recientes</small></li>' for g in grupos)
    idx = pagina("", "Ayudas y subvenciones en España por perfil, tema y comunidad · RADAR 360",
                 "Ayudas y subvenciones en España", "Directorio de búsquedas de ayudas y subvenciones por perfil, tema y comunidad autónoma, con datos de la BDNS.",
                 "Elige tu perfil, un tema o tu comunidad para ver las convocatorias recientes publicadas en la BDNS.",
                 [], 0, act, [], crumbs0)
    idx = idx.replace('<h2>0 convocatorias recientes</h2>\n  <ul class="seo-list">\n\n  </ul>',
                      f'<h2>Búsquedas disponibles</h2>\n  <ul class="seo-list">{items}</ul>')
    idx = re.sub(r"\s*<h2>Más búsquedas</h2>\s*<nav class=\"seo-nav\"></nav>", "", idx)
    (salida / "index.html").write_text(idx, encoding="utf-8")

    urls = [f"{BASE}/", f"{BASE}/panel/", f"{BASE}/ayudas/", f"{BASE}/licitaciones/", f"{BASE}/mercado/", f"{BASE}/puedo-optar/", f"{BASE}/criba-go-no-go/", f"{BASE}/aviso-legal/", f"{BASE}/privacidad/", f"{BASE}/cookies/"] + [f"{BASE}/ayudas/{g[0]}" for g in grupos]
    try:  # páginas por organismo (necesitan data/mercado.json; sin él, solo se omiten)
        import generar_organismos
        urls += generar_organismos.genera()
        import generar_sectores
        urls += generar_sectores.genera()
    except ImportError as e:
        print("organismos omitidos:", e)
    mod = act[:10]
    (RAIZ / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{u}</loc><lastmod>{mod}</lastmod></url>\n" for u in urls) + "</urlset>\n", encoding="utf-8")
    print(f"{len(grupos)} páginas SEO + índice; sitemap con {len(urls)} URLs")


if __name__ == "__main__":
    sys.exit(main())
