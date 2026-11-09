import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import import_placsp as p

ATOM = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:cbc="urn:dgpe:names:draft:codice:schema:xsd:CommonBasicComponents-2" xmlns:cac="urn:dgpe:names:draft:codice:schema:xsd:CommonAggregateComponents-2" xmlns:cac-place-ext="urn:dgpe:names:draft:codice-place-ext:schema:xsd:CommonAggregateComponents-2" xmlns:cbc-place-ext="urn:dgpe:names:draft:codice-place-ext:schema:xsd:CommonBasicComponents-2">
<link rel="self" href="https://x/a"/><link rel="next" href="https://x/b"/>
<entry><id>1</id><title>Evento Nochevieja</title><link href="https://x/lic/1"/><updated>2026-11-08T20:02:19.875+01:00</updated>
<cac-place-ext:ContractFolderStatus><cbc:ContractFolderID>651/2026</cbc:ContractFolderID><cbc-place-ext:ContractFolderStatusCode>PUB</cbc-place-ext:ContractFolderStatusCode>
<cac-place-ext:LocatedContractingParty><cac:Party><cac:PartyName><cbc:Name>Ayuntamiento de Antigua</cbc:Name></cac:PartyName></cac:Party></cac-place-ext:LocatedContractingParty>
<cac:ProcurementProject><cbc:Name>Organización del evento Nochevieja al Sol 2026</cbc:Name><cbc:TypeCode>2</cbc:TypeCode>
<cac:BudgetAmount><cbc:TotalAmount>13500</cbc:TotalAmount><cbc:TaxExclusiveAmount>12616.82</cbc:TaxExclusiveAmount></cac:BudgetAmount>
<cac:RequiredCommodityClassification><cbc:ItemClassificationCode>79954000</cbc:ItemClassificationCode></cac:RequiredCommodityClassification>
<cac:RealizedLocation><cbc:CountrySubentity>Fuerteventura</cbc:CountrySubentity><cbc:CountrySubentityCode>ES704</cbc:CountrySubentityCode></cac:RealizedLocation></cac:ProcurementProject>
<cac:TenderingProcess><cac:TenderSubmissionDeadlinePeriod><cbc:EndDate>2026-11-20</cbc:EndDate><cbc:EndTime>23:59:00</cbc:EndTime></cac:TenderSubmissionDeadlinePeriod></cac:TenderingProcess>
</cac-place-ext:ContractFolderStatus></entry>
<entry><id>2</id><title>Adjudicada</title><link href="https://x/lic/2"/><updated>2026-11-06T10:00:00+01:00</updated>
<cac-place-ext:ContractFolderStatus><cbc:ContractFolderID>85/2026</cbc:ContractFolderID><cbc-place-ext:ContractFolderStatusCode>ADJ</cbc-place-ext:ContractFolderStatusCode>
<cac:ProcurementProject><cbc:Name>Obra</cbc:Name></cac:ProcurementProject></cac-place-ext:ContractFolderStatus></entry>
</feed>""".encode("utf-8")

class T(unittest.TestCase):
    def test_lee(self):
        regs, nxt, antigua = p.lee(ATOM)
        self.assertEqual(len(regs), 2)
        self.assertEqual(nxt, "https://x/b")
        self.assertEqual(antigua, "2026-11-06")
        r = regs[0]
        self.assertEqual((r["id"], r["estado"], r["tipo"], r["cpv"], r["plazo"]), ("651/2026", "PUB", "Servicios", "79954000", "2026-11-20"))
        self.assertEqual(r["presupuesto"], 12616.82)
        self.assertEqual(r["organismo"], "Ayuntamiento de Antigua")
        self.assertEqual(r["ccaa"], ["Canarias"])
        self.assertEqual(r["url"], "https://x/lic/1")

    def test_abierta(self):
        regs, _, _ = p.lee(ATOM)
        self.assertTrue(p.abierta(regs[0], "2026-11-09"))
        self.assertFalse(p.abierta(regs[0], "2026-11-21"))
        self.assertFalse(p.abierta(regs[1], "2026-11-09"))

ADJ = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:cbc="urn:dgpe:names:draft:codice:schema:xsd:CommonBasicComponents-2" xmlns:cac="urn:dgpe:names:draft:codice:schema:xsd:CommonAggregateComponents-2" xmlns:cac-place-ext="urn:dgpe:names:draft:codice-place-ext:schema:xsd:CommonAggregateComponents-2" xmlns:cbc-place-ext="urn:dgpe:names:draft:codice-place-ext:schema:xsd:CommonBasicComponents-2">
<entry><id>9</id><title>x</title><link href="https://x/lic/9"/><updated>2026-11-07T10:00:00+01:00</updated>
<cac-place-ext:ContractFolderStatus><cbc:ContractFolderID>10/2026</cbc:ContractFolderID><cbc-place-ext:ContractFolderStatusCode>ADJ</cbc-place-ext:ContractFolderStatusCode>
<cac-place-ext:LocatedContractingParty><cac:Party><cac:PartyName><cbc:Name>Ayuntamiento de Prueba</cbc:Name></cac:PartyName></cac:Party></cac-place-ext:LocatedContractingParty>
<cac:ProcurementProject><cbc:Name>Obra de acera</cbc:Name><cbc:TypeCode>3</cbc:TypeCode><cac:BudgetAmount><cbc:TaxExclusiveAmount>100000</cbc:TaxExclusiveAmount></cac:BudgetAmount></cac:ProcurementProject>
<cac:TenderResult><cbc:ResultCode>8</cbc:ResultCode><cbc:AwardDate>2026-11-05</cbc:AwardDate><cbc:ReceivedTenderQuantity>1</cbc:ReceivedTenderQuantity>
<cac:WinningParty><cac:PartyName><cbc:Name>Construcciones Ejemplo S.L.</cbc:Name></cac:PartyName></cac:WinningParty>
<cac:AwardedTenderedProject><cac:LegalMonetaryTotal><cbc:TaxExclusiveAmount>90000</cbc:TaxExclusiveAmount></cac:LegalMonetaryTotal></cac:AwardedTenderedProject></cac:TenderResult>
</cac-place-ext:ContractFolderStatus></entry>
<entry><id>8</id><title>y</title><updated>2026-11-07T10:00:00+01:00</updated>
<cac-place-ext:ContractFolderStatus><cbc:ContractFolderID>11/2026</cbc:ContractFolderID><cbc-place-ext:ContractFolderStatusCode>RES</cbc-place-ext:ContractFolderStatusCode>
<cac:ProcurementProject><cbc:Name>Desierta</cbc:Name></cac:ProcurementProject>
<cac:TenderResult><cbc:ResultCode>1</cbc:ResultCode></cac:TenderResult></cac-place-ext:ContractFolderStatus></entry>
</feed>""".encode("utf-8")


class Adj(unittest.TestCase):
    def test_adjudicacion(self):
        regs, _, _ = p.lee(ADJ)
        a = regs[0]["adj"]
        self.assertEqual((a["ganador"], a["importe"], a["ofertas"], a["fecha"]), ("Construcciones Ejemplo S.L.", 90000.0, 1, "2026-11-05"))
        self.assertNotIn("adj", regs[1])  # desierta: sin adjudicatario

    def test_mercado(self):
        import mercado
        regs, _, _ = p.lee(ADJ)
        a = regs[0]
        rows = [{"id": str(i), "organismo": "Ayuntamiento de Prueba", "tipo": "Obras", "ccaa": ["Madrid"], "presupuesto": 100000.0,
                 "importe": 90000.0, "ofertas": 1 if i < 3 else 4, "ganador": "Construcciones Ejemplo S.L." if i < 4 else "Juan Pérez García",
                 "fecha": "2026-11-05"} for i in range(5)]
        r = mercado.calcula(rows)
        self.assertEqual(r["global"]["pct_una_oferta"], 60.0)
        self.assertEqual(r["global"]["baja_media"], 10.0)
        self.assertEqual(r["por_organismo"][0]["top_ganador"], {"nombre": "Construcciones Ejemplo S.L.", "n": 4})
        rows.append({"id":"old","organismo":"Ayuntamiento de Prueba","tipo":"Obras","ccaa":["Madrid"],"presupuesto":1.0,"importe":1.0,"ofertas":1,"ganador":"Vieja S.L.","fecha":"2023-01-01"})
        self.assertEqual(mercado.calcula(rows)["global"]["n"], 5)  # la antigua queda fuera
        self.assertEqual([x["nombre"] for x in r["top_adjudicatarios"]], ["Construcciones Ejemplo S.L."])  # persona física fuera


unittest.main() if __name__ == "__main__" else None
