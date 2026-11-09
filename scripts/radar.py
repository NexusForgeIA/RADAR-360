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
