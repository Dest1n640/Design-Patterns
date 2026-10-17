from enum import Enum


class ReportType(Enum):
    """Тип отчёта; значение используется в адресе API."""

    TXT = "txt"
    CSV = "csv"
    MARKDOWN = "markdown"
    XML = "xml"
    HTML = "html"
