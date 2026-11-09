"""Lógica compartida de RADAR 360: normaliza convocatorias de BDNS y las clasifica por tema.
Solo stdlib. El tema es una orientación por palabras clave, no una clasificación oficial."""
import re
import unicodedata

BDNS_FICHA = "https://www.infosubvenciones.es/bdnstrans/GE/es/convocatorias/{n}"

# Orden = prioridad: gana el primer tema cuyas palabras aparezcan en la descripción.
# «Concesión directa y convenios» va primero: son concesiones directas a una entidad concreta, no convocatorias abiertas.
NOMINATIVAS = "Concesión directa y convenios"
TEMAS = [
    (NOMINATIVAS, ["nominativ", "convenio", "subvencion directa", "subvencion excepcional", "cuota anual", "plan estrategico de subvenciones",
                   "resolucion de concesion"]),
    ("Agro, pesca y animales", ["ganader", "agri", "agrar", "agro", "pesc", "acuicol", "animal", "felin", "colonas", "palomas",
                                "rural", "forestal", "regadi", "vino", "apicul"]),
    ("Movilidad y transporte", ["taxi", "vtc", "vehiculo", "automovil", "turismo electrico", "moves", "achatarr", "punto de recarga",
                                "puntos de recarga", "autobus", "bicicleta", "ciclis", "patinete", "flota", "ferrocarril", "carsharing",
                                "motocicleta", "transportista", "transporte de mercancias", "transporte por carretera",
                                "transporte regular", "transporte de viajeros"]),
    ("Energía y medio ambiente", ["energ", "fotovolt", "autoconsumo", "renovable", "medioambient", "medio ambiente",
                                  "residuos", "climat", "sostenib", "eolic", "hidrogeno", "descarboniz"]),
    ("Vivienda y fachadas", ["vivienda", "fachada", "rehabilit", "inmueble", "vivenda", "accesibilidad"]),
    ("Deporte", ["deport", "futbol", "club", "esport", "atlet", "competicion"]),
    ("Educación y becas", ["beca", "estudi", "escolar", "educa", "alumn", "doctor", "universit", "formacion", "ampa",
                           "investigador", "matricula", "curso 20", "practicas profesionales"]),
    ("Social y salud", ["social", "salud", "sanit", "dependencia", "discapac", "enfermedad", "igualtat", "igualdad",
                        "cooperacion", "mayores", "jubilad", "inclusiv", "familia", "infancia", "farmac", "ela ", "voluntari",
                        "solidari", "juventud", "mujer"]),
    ("Empresas y empleo", ["empresa", "autonom", "emprended", "comercio", "comercial", "empleo", "contratacion",
                           "desemplead", "empresarial", "industri", "exterior", "turism", "bono consumo", "innovacion"]),
    ("Cultura y festejos", ["cultur", "festej", "fiesta", "concurso", "navide", "carnaval", "musica", "teatro",
                            "cartel", "patrimonio", "biblioteca", "artistic", "artes escenicas", "espectaculo", "premio"]),
]
OTROS = "Otros"

# Sectores oficiales de la ficha (texto en minúsculas sin tildes) → tema, solo cuando las palabras clave del título no deciden.
SECTORES = [
    ("artisticas, deportivas", "Cultura y festejos"),
    ("sanitarias y de servicios sociales", "Social y salud"), ("servicios sociales", "Social y salud"),
    ("educacion", "Educación y becas"), ("deportiv", "Deporte"),
    ("bibliotecas", "Cultura y festejos"), ("creacion artistica", "Cultura y festejos"), ("artisticas", "Cultura y festejos"),
    ("agricultura", "Agro, pesca y animales"), ("ganaderia", "Agro, pesca y animales"), ("pesca", "Agro, pesca y animales"),
    ("energia", "Energía y medio ambiente"), ("suministro de energia", "Energía y medio ambiente"),
    ("comercio", "Empresas y empleo"), ("hosteleria", "Empresas y empleo"), ("industria", "Empresas y empleo"),
    ("construccion", "Vivienda y fachadas"), ("actividades inmobiliarias", "Vivienda y fachadas"),
]

# Cláusulas con el nombre de un departamento u organismo («Departamento de Presidencia, Justicia, Cultura y Deporte»)
# que no dicen de qué trata la ayuda y confunden a las palabras clave.
_ORG = re.compile(r"\b(departamento|consejeria|concejalia|delegacion|vicepresidencia|instituto|direccion general|area) (de|del|de la|de los|de las) [^,.;:]{0,90}?(?= y la | y el | y las | y los |,|\.|;|:| en relacion| para |$)")


def _plano(s):
    s = unicodedata.normalize("NFD", s or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"\s+", " ", s)


def tema(descripcion, sectores=None, tipo=None):
    """tipo = tipo oficial de la convocatoria (ficha): «Concesión directa…» o «Concurrencia competitiva…»; manda sobre las palabras clave."""
    d = _ORG.sub(" ", _plano(descripcion))
    t = _plano(tipo)
    if t.startswith("concesion directa"):
        return NOMINATIVAS
    for nombre, claves in TEMAS:
        if nombre == NOMINATIVAS and t.startswith("concurrencia"):
            continue
        if any(c in d for c in claves):
            return nombre
    for sec in sectores or []:
        s = _plano(sec)
        for clave, nombre in SECTORES:
            if clave in s:
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
