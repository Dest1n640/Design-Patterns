# UML: модели рецептов

Модели рецептов лежат в `Src/Models/` и описывают составную технологическую карту (п. 2.5 ТЗ):
карта состоит из блюд, блюдо — из ингредиентов и текста рецепта. Данные взяты из
[рецепта пиццы Маргарита](../recipes/pizza_margherita.md).
Пунктирная стрелка — зависимость (создаёт, проверяет или бросает), закрашенный ромб — владение,
пустой ромб — объекты переданы извне.

## Модели

`IngredientModel` — номенклатура с весом брутто и нетто, поэтому наследуется от `NomenclatureModel`.
`DishModel` хранит непустой список ингредиентов и рецепт приготовления и считает вес блюда:
`calculate_brutto()` и `calculate_netto()` складывают вес всех ингредиентов. `TechnologicalMapModel`
хранит блюда; карта без блюд создаётся пустой, `add_dish()` добавляет блюдо.
Свойства-списки возвращают копии, поэтому изменить состав можно только через сеттер или `add_dish()`.

Рецепт составной: полуфабрикат «Тесто для пиццы» — отдельное блюдо карты и одновременно ингредиент
пиццы с типом `SEMI_FINISHED`. Связь между ними — по наименованию.

```mermaid
classDiagram
    direction TB

    class NamedModel {
        +name: str
    }

    class NomenclatureModel {
        +full_name: str
        +group: NomenclatureGroupModel
        +measurement_unit: MeasurementUnitModel
        +position_type: PositionType
    }

    class IngredientModel {
        +brutto: int | float
        +netto: int | float
        +create_margherita_ingredients()$ dict~str, list~
    }

    note for IngredientModel "Вес брутто и нетто — положительные числа"

    class DishModel {
        -_INGREDIENTS_ERROR: str$
        +ingredients: list~IngredientModel~
        +recipe: str
        +calculate_netto() int | float
        +calculate_brutto() int | float
        +create_margherita_dishes()$ list~DishModel~
    }

    note for DishModel "Состав не может быть пустым. Вес = сумма веса ингредиентов"

    class TechnologicalMapModel {
        -_DISHES_ERROR: str$
        +dishes: list~DishModel~
        +add_dish(new_dish) list~DishModel~
        +create_technological_map()$ TechnologicalMapModel
    }

    class PositionType {
        <<enumeration>>
        RAW_MATERIAL
        GOODS
        SEMI_FINISHED
        DISH
    }

    class Validation {
        +validate_instance(value, expected_type, field, message)$ object
        +validate_string(value, field)$ str
        +validate_positive_number(value, field)$ int | float
    }

    class ValidationException

    NamedModel <|-- NomenclatureModel
    NomenclatureModel <|-- IngredientModel
    NamedModel <|-- DishModel
    NamedModel <|-- TechnologicalMapModel
    NomenclatureModel --> "1" PositionType : position_type
    TechnologicalMapModel o-- "*" DishModel : dishes
    DishModel o-- "1..*" IngredientModel : ingredients
    IngredientModel ..> Validation : проверяет brutto и netto
    DishModel ..> Validation : проверяет состав и рецепт
    TechnologicalMapModel ..> Validation : проверяет блюда
    DishModel ..> ValidationException : бросает при пустом составе
    Validation ..> ValidationException : бросает
```

Группа, единица измерения и базовая иерархия `AbstractModel` → `NamedModel` — на
[диаграмме StorageManager](storage_manager.md) и [диаграмме SettingsManager](settings_manager.md).

## Последовательность: создание технологической карты

Фабрики вызываются цепочкой сверху вниз: карта просит блюда, блюда — ингредиенты.
`StorageManager.convert()` вызывает `create_technological_map()` при первом старте.

```mermaid
sequenceDiagram
    autonumber
    actor Client as Клиентский код
    participant TM as TechnologicalMapModel
    participant Dish as DishModel
    participant Ingr as IngredientModel
    participant Unit as MeasurementUnitModel

    Client->>TM: create_technological_map()
    activate TM
    TM->>Dish: create_margherita_dishes()
    activate Dish
    Dish->>Ingr: create_margherita_ingredients()
    activate Ingr
    Ingr->>Unit: create_gram(), create_milliliter()
    Unit-->>Ingr: грамм, миллилитр
    Note over Ingr: Группы: Бакалея, Молочные продукты,<br/>Овощи, Полуфабрикаты
    Ingr-->>Dish: {«Тесто для пиццы»: 4, «Пицца Маргарита»: 6}
    deactivate Ingr
    Note over Dish: Шаги приготовления из pizza_margherita.md
    Dish-->>TM: [Тесто для пиццы, Пицца Маргарита]
    deactivate Dish
    TM->>TM: TechnologicalMapModel("Пицца Маргарита", dishes)
    TM-->>Client: карта «Пицца Маргарита»
    deactivate TM
```

## Последовательность: расчёт веса блюда

Вес считается при каждом вызове, поэтому изменение состава через сеттер `ingredients`
(добавление или исключение ингредиента) сразу меняет результат.

```mermaid
sequenceDiagram
    autonumber
    actor Client as Клиентский код
    participant Dish as DishModel
    participant Ingr as IngredientModel

    opt Изменение состава
        Client->>Dish: ingredients = [...]
        activate Dish
        Dish->>Dish: Validation: список, не пустой, только IngredientModel
        deactivate Dish
    end

    Client->>Dish: calculate_brutto()
    activate Dish
    loop Для каждого ингредиента
        Dish->>Ingr: brutto
        Ingr-->>Dish: вес брутто
    end
    Dish-->>Client: сумма брутто
    deactivate Dish

    Client->>Dish: calculate_netto()
    activate Dish
    loop Для каждого ингредиента
        Dish->>Ingr: netto
        Ingr-->>Dish: вес нетто
    end
    Dish-->>Client: сумма нетто
    deactivate Dish
```
