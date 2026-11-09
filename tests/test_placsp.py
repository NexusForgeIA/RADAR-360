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

unittest.main() if __name__ == "__main__" else None
