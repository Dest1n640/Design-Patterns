import xml.etree.ElementTree as ET

from Src.Logics.Reports.dish_report import DishReport, Row


class XmlReport(DishReport):
    """XML-отчёт по блюду: элемент на каждый ингредиент состава."""

    def _format(self, title: str, rows: list[Row]) -> str:
        """Оформляет состав в XML: <dish name> с вложенными <ingredient>."""
        root = ET.Element("dish", name=title)
        for code, name, brutto, netto in rows:
            ET.SubElement(
                root,
                "ingredient",
                id=code,
                name=name,
                brutto=str(brutto),
                netto=str(netto),
            )
        ET.indent(root)
        return ET.tostring(root, encoding="unicode", xml_declaration=True)
