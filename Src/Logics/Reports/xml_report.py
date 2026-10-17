import xml.etree.ElementTree as ET

from Src.Logics.Reports.table_report import Header, Row, TableReport


class XmlReport(TableReport):
    """XML-отчёт: элемент <row> на каждую строку таблицы."""

    def _format(self, title: str, header: Header, rows: list[Row]) -> str:
        """Оформляет таблицу в XML: <report name> → <row> → <field name>."""
        root = ET.Element("report", name=title)
        for row in rows:
            element = ET.SubElement(root, "row")
            for label, value in zip(header, row, strict=True):
                ET.SubElement(element, "field", name=label).text = str(value)
        ET.indent(root)
        return ET.tostring(root, encoding="unicode", xml_declaration=True)
