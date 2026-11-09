import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import radar  # noqa: E402

# Cadenas reales observadas en la API de BDNS (09/11/2026).
class T(unittest.TestCase):
    def test_territorio_provincia(self):
        t = radar.territorio([{"descripcion": "ES613 - Córdoba"}])
        self.assertEqual((t["ccaa"], t["provincias"], t["nacional"]), (["Andalucía"], ["Córdoba"], False))

    def test_territorio_ccaa_y_nacional(self):
        self.assertEqual(radar.territorio([{"descripcion": "ES51 - CATALUÑA"}])["provincias"], [])
        self.assertEqual(radar.territorio([{"descripcion": "ES3 - COMUNIDAD DE MADRID"}])["ccaa"], ["Madrid"])
        self.assertEqual(radar.territorio([{"descripcion": "ES300 - Madrid"}])["ccaa"], ["Madrid"])
        self.assertTrue(radar.territorio([{"descripcion": "ES - ESPAÑA "}])["nacional"])
        self.assertEqual(radar.territorio([{"descripcion": "XXXX - TODO EL MUNDO"}]), {"nacional": False, "ccaa": [], "provincias": []})

    def test_territorio_isla_canarias(self):
        t = radar.territorio([{"descripcion": "ES705 - Gran Canaria"}])
        self.assertEqual((t["ccaa"], t["provincias"]), (["Canarias"], ["Gran Canaria"]))

    def test_perfiles(self):
        P = lambda *x: radar.perfiles([{"descripcion": d} for d in x])
        self.assertEqual(P("PYME Y PERSONAS FÍSICAS QUE DESARROLLAN ACTIVIDAD ECONÓMICA"), ["negocio"])
        self.assertEqual(P("PERSONAS FÍSICAS QUE NO DESARROLLAN ACTIVIDAD ECONÓMICA"), ["persona"])
        self.assertEqual(P("PERSONAS JURÍDICAS QUE NO DESARROLLAN ACTIVIDAD ECONÓMICA"), ["entidad"])
        self.assertEqual(P("GRAN EMPRESA", "PYME Y PERSONAS FÍSICAS QUE DESARROLLAN ACTIVIDAD ECONÓMICA"), ["empresa", "negocio"])

    def test_enriquece(self):
        r = radar.enriquece({"numero": "1"}, {"presupuestoTotal": 5.45e5, "fechaFinSolicitud": "2026-12-01",
            "tiposBeneficiarios": [{"descripcion": "GRAN EMPRESA"}], "regiones": [{"descripcion": "ES413 - León"}], "sectores": [{"descripcion": "X"}]})
        self.assertEqual((r["presupuesto"], r["fin"], r["inicio"], r["provincias"], r["perfiles"]), (545000, "2026-12-01", None, ["León"], ["empresa"]))

if __name__ == "__main__":
    unittest.main()
