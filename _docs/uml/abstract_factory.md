# UML: Абстрактная фабрика

Фабрика отчётов `ReportFactory` реализует контракт `AbstractFactory`: по типу отчёта (`ReportType`)
создаёт построитель — наследника `TableReport`. Фабрика хранит настройки, поэтому `create_default()`
создаёт построитель формата из `settings.response_format`. Клиентский код (`main.py`) знает только
`create()` / `create_default()` и `build()`, конкретный класс отчёта ему неизвестен.

Построитель собирает таблицу рефлексией (`Common.get_fields`) в `TableDto`, а оформление делегирует
наследнику через `_format()` (шаблонный метод). CSV и Markdown возвращают байты — они уходят клиенту
файлом, TXT, XML и HTML — текстом.

## Диаграмма последовательности: формирование отчёта

```mermaid
sequenceDiagram
    autonumber
    actor Client as Клиент (браузер)
    participant API as main.py (FastAPI)
    participant SM as StorageManager
    participant F as ReportFactory
    participant R as Отчёт (наследник TableReport)
    participant C as Common

    Client->>API: GET /reports/[report_type]/entity_type/code
    activate API
    API->>SM: коллекция по entity_type
    SM-->>API: список сущностей
    API->>API: поиск сущности по id == code

    alt Сущность не найдена
        API-->>Client: 404 Not Found
    else Сущность найдена
        alt Формат указан в адресе
            API->>F: create(report_type)
        else Формат не указан
            API->>F: create_default()
            F->>F: create(settings.response_format)
        end
        activate F
        F->>F: проверка ReportType, поиск класса в __mapping
        F-->>API: экземпляр отчёта (AbstractReport)
        deactivate F

        API->>R: build(entity)
        activate R
        R->>R: Validation.validate_instance(entity, NamedModel)
        R->>C: get_fields(entity)
        C-->>R: свойства сущности
        Note over R: строки — элементы первого непустого<br/>свойства-списка, иначе сама сущность
        R->>C: get_fields(item, is_common=True)
        C-->>R: колонки (свойства без списков)
        R->>R: _table() → TableDto(title, header, rows)
        R->>R: _format(table) — переопределён в наследнике
        R-->>API: ReportModel
        deactivate R

        alt report.binary (CSV, Markdown)
            API-->>Client: 200 application/octet-stream<br/>Content-Disposition: attachment
        else report.text (TXT, XML, HTML)
            API-->>Client: 200 text/plain
        end
    end
    deactivate API
```
