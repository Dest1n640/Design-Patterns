import xml.etree.ElementTree as ET

from Src.Dtos.table_dto import TableDto
from Src.Logics.Reports.table_report import TableReport


class XmlReport(TableReport):
    """XML-отчёт: элемент <row> на каждую строку таблицы."""

    def _format(self, table: TableDto) -> str:
        """Оформляет таблицу в XML: <report name> → <row> → <field name>."""
        root = ET.Element("report", name=table.title)
        for row in table.rows:
            element = ET.SubElement(root, "row")
            for field, value in zip(table.header, row, strict=True):
                ET.SubElement(element, "field", name=field).text = value
        ET.indent(root)
        return ET.tostring(root, encoding="unicode", xml_declaration=True)
