# UML: модели рецептов

Модели рецептов лежат в `Src/Models/` и описывают составную технологическую карту (п. 2.5 ТЗ):
карта состоит из блюд, блюдо — из ингредиентов и текста рецепта. Данные взяты из
[рецепта пиццы Маргарита](../recipes/pizza_margherita.md).
Пунктирная стрелка — зависимость (создаёт, проверяет или бросает), закрашенный ромб — владение,
пустой ромб — объекты переданы извне.

## Модели

`IngredientModel` — номенклатура с весом брутто и нетто, поэтому наследуется от `NomenclatureModel`.
`DishModel` хранит непустой состав и рецепт приготовления. В состав входят ингредиенты и вложенные
блюда-полуфабрикаты (шаблон «Компоновщик»), поэтому `calculate_brutto()` и `calculate_netto()`
рекурсивны: вес ингредиента берётся как есть, вес вложенного блюда считается тем же методом.
`TechnologicalMapModel` хранит блюда; карта без блюд создаётся пустой, `add_dish()` добавляет блюдо.
Свойства-списки возвращают копии, поэтому изменить состав можно только через сеттер или `add_dish()`.

Рецепт составной: полуфабрикат «Тесто для пиццы» — отдельное блюдо карты и одновременно элемент
состава пиццы, тот же объект. Вода в номенклатуре не учитывается, поэтому вес теста — 160 г, а пиццы —
160 + 291 = 451 г.

Фабрики не создают единицы измерения и группы сами: `StorageManager` передаёт по цепочке
карта → блюда → ингредиенты свои словари `groups` и `units`, поэтому у ингредиентов те же объекты
грамма, миллилитра и групп, что и в хранилище, без дублей.

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
        +create_margherita_ingredients(groups, units)$ dict~str, list~
    }

    note for IngredientModel "Вес брутто и нетто — положительные числа"

    class DishModel {
        -_INGREDIENTS_ERROR: str$
        +ingredients: list~IngredientModel | DishModel~
        +recipe: str
        +calculate_netto() int | float
        +calculate_brutto() int | float
        +create_margherita_dishes(groups, units)$ list~DishModel~
    }

    note for DishModel "Состав не может быть пустым. Вес = сумма веса состава, вложенные блюда — рекурсивно"

    class TechnologicalMapModel {
        -_DISHES_ERROR: str$
        +dishes: list~DishModel~
        +add_dish(new_dish) list~DishModel~
        +create_technological_map(groups, units)$ TechnologicalMapModel
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
    DishModel o-- "*" IngredientModel : ingredients
    DishModel o-- "*" DishModel : ingredients (полуфабрикаты)
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
`StorageManager.convert()` вызывает `create_technological_map(groups, units)` при первом старте
и передаёт свои словари групп и единиц измерения.

```mermaid
sequenceDiagram
    autonumber
    participant SM as StorageManager
    participant TM as TechnologicalMapModel
    participant Dish as DishModel
    participant Ingr as IngredientModel

    SM->>TM: create_technological_map(groups, units)
    activate TM
    TM->>Dish: create_margherita_dishes(groups, units)
    activate Dish
    Dish->>Ingr: create_margherita_ingredients(groups, units)
    activate Ingr
    Note over Ingr: Грамм, миллилитр и группы берутся<br/>из словарей хранилища, не создаются
    Ingr-->>Dish: {«Тесто для пиццы»: 4, «Пицца Маргарита»: 5}
    deactivate Ingr
    Note over Dish: Шаги приготовления из pizza_margherita.md
    Dish->>Dish: dough = DishModel(«Тесто для пиццы», 4 ингредиента)
    Dish->>Dish: pizza = DishModel(«Пицца Маргарита», [dough, 5 ингредиентов])
    Dish-->>TM: [Тесто для пиццы, Пицца Маргарита]
    deactivate Dish
    TM->>TM: TechnologicalMapModel("Пицца Маргарита", dishes)
    TM-->>SM: карта «Пицца Маргарита»
    deactivate TM
```

## Последовательность: расчёт веса блюда

Вес считается при каждом вызове, поэтому изменение состава через сеттер `ingredients`
(добавление или исключение ингредиента), в том числе у вложенного блюда, сразу меняет результат.
`calculate_brutto()` устроен так же, как `calculate_netto()`, только берёт `brutto`.

```mermaid
sequenceDiagram
    autonumber
    actor Client as Клиентский код
    participant Pizza as DishModel (пицца)
    participant Dough as DishModel (тесто)
    participant Ingr as IngredientModel

    opt Изменение состава
        Client->>Pizza: ingredients = [...]
        activate Pizza
        Pizza->>Pizza: Validation: список, не пустой, только IngredientModel или DishModel
        deactivate Pizza
    end

    Client->>Pizza: calculate_netto()
    activate Pizza
    loop Для каждого элемента состава
        alt Вложенное блюдо
            Pizza->>Dough: calculate_netto()
            activate Dough
            loop Для каждого ингредиента теста
                Dough->>Ingr: netto
                Ingr-->>Dough: вес нетто
            end
            Dough-->>Pizza: сумма нетто теста
            deactivate Dough
        else Ингредиент
            Pizza->>Ingr: netto
            Ingr-->>Pizza: вес нетто
        end
    end
    Pizza-->>Client: сумма нетто
    deactivate Pizza
```
