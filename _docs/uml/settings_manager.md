# UML: SettingsManager

Менеджеры лежат в `Src/Logics/`, общий базовый класс `AbstractManager` — в `Src/Core/`.
Порядок работы задаёт базовый `load()`: он читает json-файл в `_data` и вызывает `convert()`,
который реализует наследник. Признак `is_loaded` и имя файла меняются только после успешного
`convert()`, поэтому неудачная загрузка не затирает прежнее состояние.
Пунктирная стрелка — зависимость (создаёт, проверяет или бросает), закрашенный ромб — владение.

## SettingsManager

Singleton: `__new__` возвращает экземпляр, сохранённый в `_instance`, а `__init__` создаёт состояние
только один раз — все `SettingsManager()` в программе указывают на один объект с одними настройками.
Читает `settings.json` из корня проекта и собирает из раздела `company` и флага `first_start`
модель `SettingsModel`. Ошибки в данных бросают `ValidationException` — из `Validation` или из сеттеров
моделей; если файл не прочитан, `load()` бросает `ApplicationException`.

```mermaid
classDiagram
    direction TB

    class AbstractManager {
        <<abstract>>
        -_PROJECT_ROOT: Path$
        -_DEFAULT_FILE_NAME: str$
        -_file_name: str
        -_is_loaded: bool
        -_data: object
        +is_loaded: bool
        +load(file_name) None
        +convert()* bool
    }

    note for AbstractManager "Шаблонный метод: load() читает файл и вызывает convert(). Файл по умолчанию ищется от корня проекта"

    class SettingsManager {
        <<singleton>>
        -_instance: SettingsManager$
        -_DEFAULT_FILE_NAME: str$
        -_settings: SettingsModel
        +settings: SettingsModel
        +__new__() SettingsManager
        +convert() bool
    }

    note for SettingsManager "Файл по умолчанию settings.json. Модель присваивается только целиком, при ошибке прежние настройки не затираются"

    class SettingsModel {
        +organization: OrganizationModel | None
        +boss_name: str
        +accountant_name: str
        +first_start: bool
    }

    class OrganizationModel {
        +inn: str
        +bic: str
        +curr_account: str
        +legal_form: str
    }

    class AbstractModel {
        <<abstract>>
        +id: UUID
    }

    class NamedModel {
        +name: str
    }

    class Validation {
        +validate_instance(value, expected_type, field, message)$ object
        +validate_string(value, field)$ str
    }

    class ApplicationException
    class ValidationException

    AbstractManager <|-- SettingsManager
    SettingsManager *-- "1" SettingsModel : settings
    SettingsModel --> "0..1" OrganizationModel : organization
    AbstractModel <|-- SettingsModel
    AbstractModel <|-- NamedModel
    NamedModel <|-- OrganizationModel
    ApplicationException <|-- ValidationException
    SettingsManager ..> OrganizationModel : создаёт в convert()
    SettingsManager ..> Validation : проверяет разделы json
    AbstractManager ..> Validation : проверяет имя файла
    AbstractManager ..> ApplicationException : бросает, если файл не прочитан
    Validation ..> ValidationException : бросает
```
