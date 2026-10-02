# UML: StorageManager

Хранилище доменных моделей — singleton, по аналогии с `SettingsManager`: `__new__` возвращает экземпляр
из `_instance`, поэтому справочники одинаковы в любом месте программы. Наследуется от `AbstractManager`
и переопределяет `convert()`, а порядок «прочитать файл → преобразовать» задаёт базовый `load()`.
Пунктирная стрелка — зависимость (создаёт, проверяет или бросает), закрашенный ромб — владение,
пустой ромб — объект передан извне.

## StorageManager

Хранит справочники в шести коллекциях — словарях с ключом по имени: единицы измерения, группы
номенклатуры, номенклатура, склады, а также рестораны и производственные цеха как владельцы складов.
Повтор имени в данных — ошибка, поэтому каждый элемент уникален.

`start(settings)` получает настройки извне. При первом старте (`first_start = true`) он вызывает `load()`,
и `convert()` формирует первичные данные из `settings.json` — сейчас это 5 единиц измерения, 7 групп,
13 позиций номенклатуры, 10 ресторанов, 1 цех и 11 складов. При `first_start = false` коллекции
остаются пустыми, а повторный запуск после успешной загрузки ничего не делает.

`convert()` собирает данные по порядку: единицы → группы → номенклатура → рестораны → цех → склады.
Ссылки по имени (базовая единица, группа, единица измерения) и по коду ресторана разрешаются в тот же
объект, что лежит в коллекции, а не в копию. Ошибка в данных бросает `ValidationException`, а коллекции
заменяются только после обработки всех разделов — прежние данные при ошибке сохраняются.

```mermaid
classDiagram
    direction TB

    class AbstractManager {
        <<abstract>>
        +is_loaded: bool
        +load(file_name) None
        +convert()* bool
    }

    class StorageManager {
        <<singleton>>
        -_instance: StorageManager$
        -_DEFAULT_FILE_NAME: str$
        -_settings: SettingsModel | None
        -_measurement_units: dict~str, MeasurementUnitModel~
        -_nomenclature_groups: dict~str, NomenclatureGroupModel~
        -_nomenclature: dict~str, NomenclatureModel~
        -_restaurants: dict~str, RestaurantModel~
        -_production_shops: dict~str, ProductionShopModel~
        -_warehouses: dict~str, WarehouseModel~
        +settings: SettingsModel | None
        +measurement_units: list~MeasurementUnitModel~
        +nomenclature_groups: list~NomenclatureGroupModel~
        +nomenclature: list~NomenclatureModel~
        +restaurants: list~RestaurantModel~
        +production_shops: list~ProductionShopModel~
        +warehouses: list~WarehouseModel~
        +__new__() StorageManager
        +start(settings, file_name) None
        +convert() bool
        -_convert_measurement_units(items) dict
        -_convert_nomenclature_groups(items) dict
        -_convert_nomenclature(items, groups, units) dict
        -_convert_restaurants(items) tuple
        -_convert_warehouses(items, restaurants_by_code, production_shop) dict
    }

    note for StorageManager "Коллекции — словари с ключом по имени. Свойства возвращают копии списков. convert() заменяет коллекции только целиком"

    class SettingsModel {
        +first_start: bool
    }

    class MeasurementUnitModel {
        +coefficient: int | float
        +base_unit: MeasurementUnitModel | None
        +base_coefficient: int | float
    }

    class NomenclatureGroupModel

    class NomenclatureModel {
        +full_name: str
        +group: NomenclatureGroupModel
        +measurement_unit: MeasurementUnitModel
        +position_type: PositionType
    }

    class PositionType {
        <<enumeration>>
        RAW_MATERIAL
        GOODS
        SEMI_FINISHED
        DISH
    }

    class RestaurantModel
    class ProductionShopModel

    class WarehouseModel {
        +premises: PremisesModel
        +warehouse_owner: RestaurantModel | ProductionShopModel
    }

    note for WarehouseModel "Владелец — ресторан по restaurant_id или производственный цех для центрального склада"

    class PremisesModel {
        +address: str
        +square: int | float
    }

    class Validation {
        +validate_items(value, field)$ list
        +validate_unique(key, collection, field)$ str
        +validate_reference(key, collection, field)$ object
        +validate_enum(value, enum_type, field)$ Enum
    }

    class ValidationException

    AbstractManager <|-- StorageManager
    StorageManager o-- "0..1" SettingsModel : settings
    StorageManager *-- "*" MeasurementUnitModel : measurement_units
    StorageManager *-- "*" NomenclatureGroupModel : nomenclature_groups
    StorageManager *-- "*" NomenclatureModel : nomenclature
    StorageManager *-- "*" RestaurantModel : restaurants
    StorageManager *-- "*" ProductionShopModel : production_shops
    StorageManager *-- "*" WarehouseModel : warehouses
    MeasurementUnitModel --> "0..1" MeasurementUnitModel : base_unit
    NomenclatureModel --> "1" NomenclatureGroupModel : group
    NomenclatureModel --> "1" MeasurementUnitModel : measurement_unit
    NomenclatureModel --> "1" PositionType : position_type
    WarehouseModel *-- "1" PremisesModel : premises
    WarehouseModel --> "0..1" RestaurantModel : warehouse_owner
    WarehouseModel --> "0..1" ProductionShopModel : warehouse_owner
    StorageManager ..> PremisesModel : создаёт в convert()
    StorageManager ..> Validation : проверяет разделы, уникальность и ссылки
    Validation ..> ValidationException : бросает
```

Все модели справочников наследуются от `NamedModel` (свойство `name`) и `AbstractModel` (свойство `id`),
иерархия и полная `SettingsModel` — на [диаграмме SettingsManager](settings_manager.md).
