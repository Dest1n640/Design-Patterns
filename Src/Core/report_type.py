from enum import Enum


class ReportType(Enum):
    """Тип отчёта; значение используется в адресе API."""

    TXT = "txt"
    BINARY = "binary"
    CSV = "csv"
    MARKDOWN = "markdown"
    XML = "xml"
    HTML = "html"
