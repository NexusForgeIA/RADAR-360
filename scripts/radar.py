"""Lógica compartida de RADAR 360: normaliza convocatorias de BDNS y las clasifica por tema.
Solo stdlib. El tema es una orientación por palabras clave, no una clasificación oficial."""
import re
import unicodedata

BDNS_FICHA = "https://www.infosubvenciones.es/bdnstrans/GE/es/convocatorias/{n}"

# Orden = prioridad: gana el primer tema cuyas palabras aparezcan en la descripción.
TEMAS = [
    ("Agro, pesca y animales", ["ganader", "agri", "agrar", "agro", "pesc", "acuicol", "animal", "felin", "colonas", "palomas",
                                "rural", "forestal", "regadi", "vino", "apicul"]),
    ("Vivienda y fachadas", ["vivienda", "fachada", "rehabilit", "inmueble", "vivenda", "accesibilidad"]),
    ("Deporte", ["deport", "futbol", "club", "esport", "atlet"]),
    ("Educación y becas", ["beca", "estudi", "escolar", "educa", "alumn", "doctor", "universit", "formacion", "ampa",
                           "investigador", "matricula", "curso 20"]),
    ("Social y salud", ["social", "salud", "sanit", "dependencia", "discapac", "enfermedad", "igualtat", "igualdad",
                        "cooperacion", "mayores", "jubilad", "inclusiv", "familia", "infancia", "farmac", "ela "]),
    ("Empresas y empleo", ["empresa", "autonom", "emprended", "comercio", "comercial", "empleo", "contratacion",
                           "desemplead", "empresarial", "industri", "exterior", "turism"]),
    ("Cultura y festejos", ["cultur", "festej", "fiesta", "concurso", "navide", "carnaval", "musica", "teatro",
                            "cartel", "patrimonio", "biblioteca", "artistic"]),
]
OTROS = "Otros"


def _plano(s):
    s = unicodedata.normalize("NFD", s or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", s)


def tema(descripcion):
    d = _plano(descripcion)
    for nombre, claves in TEMAS:
        if any(c in d for c in claves):
            return nombre
    return OTROS


# NUTS2 (4 primeros caracteres del código de región de BDNS) → comunidad autónoma.
CCAA = {"ES11": "Galicia", "ES12": "Asturias", "ES13": "Cantabria", "ES21": "País Vasco", "ES22": "Navarra",
        "ES23": "La Rioja", "ES24": "Aragón", "ES30": "Madrid", "ES41": "Castilla y León", "ES42": "Castilla-La Mancha",
        "ES43": "Extremadura", "ES51": "Cataluña", "ES52": "C. Valenciana", "ES53": "Illes Balears", "ES61": "Andalucía",
        "ES62": "Murcia", "ES63": "Ceuta", "ES64": "Melilla", "ES70": "Canarias"}


def territorio(regiones):
    """regiones: [{descripcion:'ES613 - Córdoba'}…] → {nacional, ccaa:[…], provincias:[…]}.
    Código de 5 caracteres = provincia (o isla en Canarias); 4 = comunidad; 'ES' = toda España; 'ES3' = Madrid;
    otros códigos de 3 caracteres (ES1…ES7) agrupan varias comunidades y no se asignan a ninguna."""
    ccaa, prov, nacional = [], [], False
    for r in regiones or []:
        d = (r.get("descripcion") if isinstance(r, dict) else str(r)) or ""
        cod, _, nombre = d.partition(" - ")
        cod, nombre = cod.strip(), nombre.strip()
        if cod == "ES":
            nacional = True
        elif cod == "ES3":
            ccaa.append("Madrid")
        elif len(cod) >= 4 and cod[:4] in CCAA:
            ccaa.append(CCAA[cod[:4]])
            if len(cod) >= 5 and nombre:
                prov.append(nombre)
    return {"nacional": nacional, "ccaa": sorted(set(ccaa)), "provincias": sorted(set(prov))}


def perfiles(beneficiarios):
    """Tipos de beneficiario de BDNS → perfiles de RADAR 360. Son cuatro categorías oficiales."""
    out = set()
    for b in beneficiarios or []:
        t = _plano(b if isinstance(b, str) else b.get("descripcion"))
        if "gran empresa" in t:
            out.add("empresa")
        elif "pyme" in t or ("desarrollan actividad" in t and "no desarrollan" not in t):
            out.add("negocio")           # pyme, autónomo y emprendedor
        elif "personas fisicas que no" in t:
            out.add("persona")
        elif "personas juridicas que no" in t:
            out.add("entidad")
    return sorted(out)


def _num(x):
    try:
        return round(float(x))
    except (TypeError, ValueError):
        return None


def enriquece(reg, d):
    """Añade a un registro los datos de la ficha oficial (JSON de /api/convocatorias?numConv=…)."""
    reg["presupuesto"] = _num(d.get("presupuestoTotal"))
    reg["inicio"] = (d.get("fechaInicioSolicitud") or "")[:10] or None
    reg["fin"] = (d.get("fechaFinSolicitud") or "")[:10] or None
    reg["perfiles"] = perfiles(d.get("tiposBeneficiarios"))
    reg["sectores"] = sorted({(s.get("descripcion") or "").strip() for s in d.get("sectores") or [] if s.get("descripcion")})
    reg["tipo"] = (d.get("tipoConvocatoria") or "").strip() or None
    reg.update(territorio(d.get("regiones")))
    reg["ficha"] = True
    return reg


def normaliza(c):
    """Una convocatoria cruda de BDNS → registro de RADAR 360."""
    n = str(c.get("numeroConvocatoria") or "").strip()
    desc = (c.get("descripcion") or c.get("descripcionLeng") or "").strip()
    return {
        "numero": n,
        "fecha": (c.get("fechaRecepcion") or "")[:10],
        "ambito": (c.get("nivel1") or "").strip().upper(),
        "organismo": (c.get("nivel3") or c.get("nivel2") or "").strip(),
        "descripcion": desc,
        "tema": tema(desc),
        "url": BDNS_FICHA.format(n=n),
    }
