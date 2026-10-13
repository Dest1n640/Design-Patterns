# UML: StorageManager

Хранилище доменных моделей — singleton, по аналогии с `SettingsManager`: `__new__` возвращает экземпляр
из `_instance`, поэтому справочники одинаковы в любом месте программы. Наследуется от `AbstractManager`
и переопределяет `convert()`, который формирует первичные данные фабричными методами доменных моделей.
Пунктирная стрелка — зависимость (создаёт, проверяет или бросает), закрашенный ромб — владение,
пустой ромб — объект передан извне.

## StorageManager

Хранит справочники в семи коллекциях — словарях с ключом по имени: единицы измерения, группы
номенклатуры, номенклатура, склады, рестораны и производственные цеха как владельцы складов,
а также технологические карты. Повтор имени в данных — ошибка, поэтому каждый элемент уникален.

`start(settings)` получает настройки извне. При первом старте (`first_start = true`) он вызывает
`convert()`, и тот формирует первичные данные: 5 единиц измерения, 5 групп, 9 позиций номенклатуры
для рецепта пиццы Маргарита, 2 ресторана, 1 цех, 3 склада и 1 технологическую карту.
При `first_start = false` коллекции остаются пустыми, а повторный запуск после формирования данных
ничего не делает.

`convert()` создаёт данные по порядку: единицы → группы → номенклатура → рестораны → цех → склады →
технологическая карта. Объекты создают фабричные методы `create_*` доменных моделей и возвращают
списки, а `_by_name()` превращает каждый список в словарь с ключом по имени. Фабрикам номенклатуры,
складов и технологической карты передаются уже созданные словари, поэтому ссылки (группа, единица
измерения, владелец склада, единицы и группы ингредиентов рецепта) ведут на тот же объект
из коллекции, а не на копию. Модели технологической карты — на [диаграмме рецептов](recipes.md).

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
        -_settings: SettingsModel | None
        -_measurement_units: dict~str, MeasurementUnitModel~
        -_nomenclature_groups: dict~str, NomenclatureGroupModel~
        -_nomenclature: dict~str, NomenclatureModel~
        -_restaurants: dict~str, RestaurantModel~
        -_production_shops: dict~str, ProductionShopModel~
        -_warehouses: dict~str, WarehouseModel~
        -_technological_maps: dict~str, TechnologicalMapModel~
        +settings: SettingsModel | None
        +measurement_units: list~MeasurementUnitModel~
        +nomenclature_groups: list~NomenclatureGroupModel~
        +nomenclature: list~NomenclatureModel~
        +restaurants: list~RestaurantModel~
        +production_shops: list~ProductionShopModel~
        +warehouses: list~WarehouseModel~
        +technological_maps: list~TechnologicalMapModel~
        +__new__() StorageManager
        +start(settings) None
        +convert() bool
        -_by_name(models)$ dict
    }

    note for StorageManager "Коллекции — словари с ключом по имени. Свойства возвращают копии списков. convert() вызывает фабричные методы моделей"

    class SettingsModel {
        +first_start: bool
    }

    class MeasurementUnitModel {
        +coefficient: int | float
        +base_unit: MeasurementUnitModel | None
        +base_coefficient: int | float
        +create_default_units()$ list
    }

    class NomenclatureGroupModel {
        +create_default_groups()$ list
    }

    class NomenclatureModel {
        +full_name: str
        +group: NomenclatureGroupModel
        +measurement_unit: MeasurementUnitModel
        +position_type: PositionType
        +create_margherita_nomenclature(groups, units)$ list
    }

    class PositionType {
        <<enumeration>>
        RAW_MATERIAL
        GOODS
        SEMI_FINISHED
        DISH
    }

    class RestaurantModel {
        +create_default_restaurants()$ list
    }

    class ProductionShopModel {
        +create_default_production_shops()$ list
    }

    class WarehouseModel {
        +premises: PremisesModel
        +warehouse_owner: RestaurantModel | ProductionShopModel
        +create_default_warehouses(restaurants, production_shops)$ list
    }

    note for WarehouseModel "Владелец — ресторан или производственный цех для центрального склада"

    class TechnologicalMapModel {
        +dishes: list~DishModel~
        +create_technological_map(groups, units)$ TechnologicalMapModel
    }

    note for TechnologicalMapModel "Подробно — на диаграмме рецептов (recipes.md)"

    class PremisesModel {
        +address: str
        +square: int | float
    }

    class Validation {
        +validate_instance(value, expected_type, field, message)$ object
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
    StorageManager *-- "*" TechnologicalMapModel : technological_maps
    MeasurementUnitModel --> "0..1" MeasurementUnitModel : base_unit
    NomenclatureModel --> "1" NomenclatureGroupModel : group
    NomenclatureModel --> "1" MeasurementUnitModel : measurement_unit
    NomenclatureModel --> "1" PositionType : position_type
    WarehouseModel *-- "1" PremisesModel : premises
    WarehouseModel --> "0..1" RestaurantModel : warehouse_owner
    WarehouseModel --> "0..1" ProductionShopModel : warehouse_owner
    WarehouseModel ..> PremisesModel : создаёт в create_default_warehouses()
    StorageManager ..> Validation : проверяет тип настроек в start()
    Validation ..> ValidationException : бросает
```

Все модели справочников наследуются от `NamedModel` (свойство `name`) и `AbstractModel` (свойство `id`),
иерархия и полная `SettingsModel` — на [диаграмме SettingsManager](settings_manager.md).

## Последовательность: запуск хранилища

Клиентский код сам загружает настройки через `SettingsManager` и передаёт готовую `SettingsModel`
в `start()` — хранилище не обращается к менеджеру настроек. При первом старте `convert()` вызывает
фабричные методы моделей по порядку и собирает из каждого списка словарь через `_by_name()`.

```mermaid
sequenceDiagram
    autonumber
    actor Client as Клиентский код
    participant SetM as SettingsManager
    participant SM as StorageManager
    participant Models as Доменные модели

    Client->>SetM: load()
    activate SetM
    SetM->>SetM: convert()
    SetM-->>Client: settings (SettingsModel)
    deactivate SetM

    Client->>SM: start(settings)
    activate SM
    SM->>SM: Validation.validate_instance(settings)

    alt Хранилище уже загружено (is_loaded == True)
        Note over SM: Повторный запуск ничего не делает
    else first_start == True
        SM->>SM: convert()
        SM->>Models: MeasurementUnitModel.create_default_units()
        Models-->>SM: 5 единиц измерения
        SM->>Models: NomenclatureGroupModel.create_default_groups()
        Models-->>SM: 5 групп
        SM->>Models: NomenclatureModel.create_margherita_nomenclature(groups, units)
        Models-->>SM: 9 позиций номенклатуры
        SM->>Models: RestaurantModel.create_default_restaurants()
        Models-->>SM: 2 ресторана
        SM->>Models: ProductionShopModel.create_default_production_shops()
        Models-->>SM: 1 цех
        SM->>Models: WarehouseModel.create_default_warehouses(restaurants, shops)
        Models-->>SM: 3 склада
        SM->>Models: TechnologicalMapModel.create_technological_map(groups, units)
        Models-->>SM: карта «Пицца Маргарита»
        Note over SM: Каждый список → _by_name() → словарь,<br/>is_loaded = True
    else first_start == False
        Note over SM: Коллекции остаются пустыми,<br/>is_loaded = False
    end

    SM-->>Client: None
    deactivate SM
```
