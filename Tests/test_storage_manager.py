"""Юнит-тесты для Src.Logics.storage_manager.StorageManager."""

import json
from unittest.mock import Mock

import pytest

from Src.Core.exception import NotFoundException, ValidationException
from Src.Core.validation import Validation
from Src.Logics.serialize_factory import SerializeFactory
from Src.Logics.settings_manager import SettingsManager
from Src.Logics.storage_manager import StorageManager
from Src.Models.ingredient_model import IngredientModel
from Src.Models.measurement_unit_model import MeasurementUnitModel
from Src.Models.nomenclature_group_model import NomenclatureGroupModel
from Src.Models.settings_model import SettingsModel
from Src.Models.technological_map_model import TechnologicalMapModel

COLLECTIONS = [
    "measurement_units",
    "nomenclature_groups",
    "nomenclature",
    "restaurants",
    "production_shops",
    "warehouses",
    "technological_maps",
]
ALL_COLLECTIONS = [
    *COLLECTIONS,
    "organizations",
    "premises",
    "dishes",
    "ingredients",
]


def _build_settings(first_start: bool = True) -> SettingsModel:
    """Строит настройки с заданным признаком первого запуска."""
    settings = SettingsModel()
    settings.first_start = first_start
    return settings


def _build_started_manager() -> StorageManager:
    """Возвращает хранилище, запущенное в режиме первого старта."""
    manager = StorageManager()
    manager.start(_build_settings())
    return manager


def _by_name(items: list) -> dict:
    """Возвращает словарь элементов коллекции по имени."""
    return {item.name: item for item in items}


def _ingredients(manager: StorageManager) -> list[IngredientModel]:
    """Возвращает ингредиенты-сырьё всех блюд технологических карт хранилища."""
    return [
        item
        for tmap in manager.technological_maps
        for dish in tmap.dishes
        for item in dish.ingredients
        if isinstance(item, IngredientModel)
    ]


def _same_objects(left: list, right: list) -> bool:
    """Проверяет, что списки состоят из одних и тех же объектов в том же порядке."""
    return len(left) == len(right) and all(
        a is b for a, b in zip(left, right, strict=True)
    )


def test_storage_manager__get_entity_types_empty_storage__all_collections():
    """Имена коллекций доступны даже в пустом хранилище."""
    # Подготовка
    manager = StorageManager()

    # Действия
    entity_types = manager.get_entity_types()

    # Проверки
    assert set(entity_types) == set(ALL_COLLECTIONS)


@pytest.mark.parametrize(
    "order", [("gram", "kilogram", "tonne"), ("tonne", "kilogram", "gram"), ("tonne",)]
)
def test_storage_manager__nested_registration__direct_references_counted_once(order):
    """Порядок корней и повторная регистрация сохраняют точные счётчики связей."""
    # Подготовка
    manager = StorageManager()
    gram = MeasurementUnitModel.create_gram()
    kilogram = MeasurementUnitModel.create_kilogram(gram)
    tonne = MeasurementUnitModel.create("тонна", 1000, kilogram)
    models = {"gram": gram, "kilogram": kilogram, "tonne": tonne}

    # Действия
    manager.commit([models[name] for name in order])
    first_counts = {
        model.id: manager.get_reference_count(model.id) for model in models.values()
    }
    manager.commit(manager.get_all_models())
    repeated_counts = {
        model.id: manager.get_reference_count(model.id) for model in models.values()
    }

    # Проверки
    assert len(manager.get_all_models()) == 3
    assert manager.get_entity("measurement_units", gram.id) is gram
    assert manager.get_entity("measurement_units", kilogram.id) is kilogram
    assert manager.get_entity("measurement_units", tonne.id) is tonne
    assert first_counts == repeated_counts == {gram.id: 1, kilogram.id: 1, tonne.id: 0}


def test_storage_manager__shared_nested_owner__outgoing_reference_counted_once():
    """Два владельца килограмма дают две ссылки на него и одну ссылку на грамм."""
    # Подготовка
    manager = StorageManager()
    kilogram = MeasurementUnitModel.create_kilogram()
    gram = kilogram.base_unit
    first = MeasurementUnitModel.create("Первая", 2, kilogram)
    second = MeasurementUnitModel.create("Вторая", 3, kilogram)

    # Действия
    manager.commit([first, second])

    # Проверки
    assert len(manager.measurement_units) == 4
    assert manager.get_reference_count(kilogram.id) == 2
    assert manager.get_reference_count(gram.id) == 1
    assert manager.get_reference_count(first.id) == 0
    assert manager.get_reference_count(second.id) == 0


@pytest.mark.parametrize("container_type", [list, dict])
def test_storage_manager__nested_collections__each_reference_counted(
    link_model_type, container_type
):
    """Каждое вхождение модели в списках и словарях учитывается отдельной ссылкой."""
    # Подготовка
    manager = StorageManager()
    gram = MeasurementUnitModel.create_gram()
    owner = link_model_type.create("Владелец")
    owner.links = (
        [gram, gram]
        if container_type is list
        else {"first": [gram], "second": {"unit": gram}}
    )

    # Действия
    manager.commit([owner])

    # Проверки
    assert len(manager.get_all_models()) == 2
    assert manager.get_reference_count(owner.id) == 0
    assert manager.get_reference_count(gram.id) == 2
    assert manager.get_entity("measurement_units", gram.id) is gram


def test_storage_manager__computed_reference__not_registered(
    link_model_type, monkeypatch
):
    """Вычисляемое свойство без сеттера не добавляет ссылку в индекс."""
    # Подготовка
    gram = MeasurementUnitModel.create_gram()

    monkeypatch.setattr(
        link_model_type,
        "computed_unit",
        property(Mock(return_value=gram)),
        raising=False,
    )
    manager = StorageManager()
    owner = link_model_type.create("Владелец")

    # Действия
    manager.commit([gram, owner])

    # Проверки
    assert owner.computed_unit is gram
    assert manager.get_reference_count(gram.id) == 0
    assert manager.get_reference_count(owner.id) == 0


@pytest.mark.parametrize("entry_point", ["read", "start"])
def test_storage_manager__nested_snapshot__reference_counts_restored(
    tmp_path, entry_point
):
    """Загрузка вложенного графа восстанавливает счётчики без дублирования корней."""
    # Подготовка
    manager = StorageManager()
    kilogram = MeasurementUnitModel.create_kilogram()
    gram = kilogram.base_unit
    file_name = tmp_path / "storage.json"
    source = {"measurement_units": SerializeFactory().convert([kilogram, gram])}
    file_name.write_text(json.dumps(source), encoding="utf-8")

    # Действия
    if entry_point == "read":
        manager.read(str(file_name))
    else:
        manager.start(SettingsModel(), str(file_name))
    manager.save(str(file_name))
    manager.read(str(file_name))
    loaded_kilogram = manager.get_entity("measurement_units", kilogram.id)
    loaded_gram = manager.get_entity("measurement_units", gram.id)

    # Проверки
    assert loaded_kilogram.base_unit is loaded_gram
    assert manager.get_reference_count(gram.id) == 1
    assert manager.get_reference_count(kilogram.id) == 0


def test_storage_manager__unknown_reference_count__not_found():
    """Запрос счётчика неизвестной модели сообщает об отсутствии сущности."""
    # Подготовка
    manager = StorageManager()

    # Действия
    with pytest.raises(NotFoundException):
        manager.get_reference_count("missing")

    # Проверки
    assert manager.get_all_models() == []


@pytest.mark.parametrize("invalid_graph", ["different_instance", "cycle"])
def test_storage_manager__invalid_nested_registration__indexes_kept(invalid_graph):
    """Конфликт вложенных экземпляров или цикл сохраняет прежние индексы."""
    # Подготовка
    manager = StorageManager()
    gram = MeasurementUnitModel.create_gram()
    kilogram = MeasurementUnitModel.create_kilogram(gram)
    manager.commit([kilogram])
    candidate = MeasurementUnitModel.create("Новая", 1, gram.clone())
    if invalid_graph == "cycle":
        candidate.base_unit = candidate

    # Действия
    with pytest.raises(ValidationException):
        manager.commit([gram, candidate])

    # Проверки
    assert len(manager.measurement_units) == 2
    assert manager.get_entity("measurement_units", kilogram.id) is kilogram
    assert manager.get_reference_count(gram.id) == 1
    assert manager.get_reference_count(kilogram.id) == 0


@pytest.mark.parametrize("invalid_batch", ["duplicate_id", "unsupported_model"])
def test_storage_manager__invalid_commit__file_and_models_kept(tmp_path, invalid_batch):
    """Ошибка набора моделей отклоняет сохранение целиком и сохраняет прежний файл."""
    # Подготовка
    manager = StorageManager()
    file_name = tmp_path / "storage.json"
    manager.start(_build_settings(False), str(file_name))
    original = NomenclatureGroupModel.create("Группа")
    manager.commit([original])
    duplicate = MeasurementUnitModel.create_gram()
    duplicate.id = original.id
    invalid_model = duplicate if invalid_batch == "duplicate_id" else SettingsModel()
    original_file = file_name.read_bytes()

    # Действия
    with pytest.raises(ValidationException):
        manager.commit([original, invalid_model])

    # Проверки
    assert file_name.read_bytes() == original_file
    assert manager.get_all_models() == [original]
    assert manager.get_entity("nomenclature_groups", original.id) is original


def test_storage_manager__new_enum_member__read_and_save_supported(
    register_entity_type, tmp_path
):
    """Одна запись перечисления подключает модель к чтению, поиску и сохранению."""

    # Подготовка
    class ExtraGroupModel(NomenclatureGroupModel):
        """Дополнительная доменная модель для проверки расширения реестра."""

        def __init__(self) -> None:
            """Создаёт группу без заполненных свойств."""
            super().__init__()
            self.__unit = None

        @property
        def unit(self) -> MeasurementUnitModel:
            """Возвращает единицу измерения группы."""
            return self.__unit

        @unit.setter
        def unit(self, value: MeasurementUnitModel) -> None:
            """Устанавливает единицу измерения группы."""
            self.__unit = Validation.validate_instance(
                value, MeasurementUnitModel, "unit", "Ожидается единица измерения"
            )

    register_entity_type("extra_groups", ExtraGroupModel)
    manager = StorageManager()
    unit = MeasurementUnitModel.create_gram()
    data = {
        "extra_groups": [
            {
                "type": "ExtraGroupModel",
                "id": "extra-group",
                "name": "Группа",
                "unit": SerializeFactory().convert(unit),
            }
        ]
    }
    file_name = tmp_path / "storage.json"
    file_name.write_text(json.dumps(data), encoding="utf-8")

    # Действия
    manager.read(str(file_name))
    entities = manager.get_entities("extra_groups")
    entity = manager.get_entity("extra_groups", "extra-group")
    manager.save(str(file_name))
    saved = json.loads(file_name.read_text(encoding="utf-8"))

    # Проверки
    assert "extra_groups" in manager.get_entity_types()
    assert type(entity) is ExtraGroupModel
    assert entity is entities[0]
    assert entity.unit is manager.get_entity("measurement_units", unit.id)
    assert saved["extra_groups"] == data["extra_groups"]


@pytest.mark.parametrize("collection", COLLECTIONS)
def test_storage_manager__get_entities__stored_objects_returned(collection):
    """Общий метод возвращает объекты любой коллекции хранилища."""
    # Подготовка
    manager = _build_started_manager()
    expected = getattr(manager, collection)

    # Действия
    entities = manager.get_entities(collection)

    # Проверки
    assert _same_objects(entities, expected)


@pytest.mark.parametrize("collection", ["missing", "settings", "_data", "save"])
def test_storage_manager__get_entities_invalid_collection__raises(collection):
    """Неизвестные имена, настройки, закрытые поля и методы недоступны."""
    # Подготовка
    manager = _build_started_manager()

    # Действия
    with pytest.raises(NotFoundException) as exc_info:
        manager.get_entities(collection)

    # Проверки
    assert collection in exc_info.value.message


@pytest.mark.parametrize("collection", COLLECTIONS)
def test_storage_manager__get_entity_existing_id__stored_object_returned(collection):
    """Поиск по идентификатору возвращает исходный объект любой коллекции."""
    # Подготовка
    manager = _build_started_manager()
    expected = getattr(manager, collection)[0]

    # Действия
    entity = manager.get_entity(collection, expected.id)

    # Проверки
    assert entity is expected


def test_storage_manager__get_entity_missing_id__raises():
    """Поиск отсутствующего идентификатора завершается ошибкой отсутствия сущности."""
    # Подготовка
    manager = _build_started_manager()

    # Действия
    with pytest.raises(NotFoundException) as exc_info:
        manager.get_entity("nomenclature_groups", "missing")

    # Проверки
    assert "missing" in exc_info.value.message


def test_storage_manager__renamed_entity__lookup_uses_id():
    """Изменение названия не влияет на поиск объекта по идентификатору."""
    # Подготовка
    manager = _build_started_manager()
    original = manager.nomenclature_groups[0]
    entity_id = original.id

    # Действия
    original.name = "Новое название"
    entity = manager.get_entity("nomenclature_groups", entity_id)

    # Проверки
    assert entity is original
    assert entity.name == "Новое название"


def test_storage_manager__duplicate_names__distinct_ids_preserved(tmp_path):
    """Объекты с одинаковыми названиями сохраняются и находятся по разным id."""
    # Подготовка
    manager = StorageManager()
    data = {
        "nomenclature_groups": [
            {"type": "NomenclatureGroupModel", "id": "first", "name": "Группа"},
            {"type": "NomenclatureGroupModel", "id": "second", "name": "Группа"},
        ]
    }
    file_name = tmp_path / "storage.json"
    file_name.write_text(json.dumps(data), encoding="utf-8")

    # Действия
    manager.read(str(file_name))
    first = manager.get_entity("nomenclature_groups", "first")
    second = manager.get_entity("nomenclature_groups", "second")
    manager.save(str(file_name))
    saved = json.loads(file_name.read_text(encoding="utf-8"))

    # Проверки
    assert first is not second
    assert first.name == second.name == "Группа"
    assert saved["nomenclature_groups"] == data["nomenclature_groups"]


def test_storage_manager__duplicate_id_across_collections__state_kept(tmp_path):
    """Одинаковые коды в разных коллекциях отклоняются до замены данных."""
    # Подготовка
    manager = _build_started_manager()
    original = manager.nomenclature_groups[0]
    data = {
        "nomenclature_groups": [
            {"type": "NomenclatureGroupModel", "id": "same", "name": "Группа"}
        ],
        "restaurants": [{"type": "RestaurantModel", "id": "same", "name": "Ресторан"}],
    }
    file_name = tmp_path / "storage.json"
    file_name.write_text(json.dumps(data), encoding="utf-8")

    # Действия
    with pytest.raises(ValidationException) as exc_info:
        manager.read(str(file_name))

    # Проверки
    assert exc_info.value.field == "id"
    assert manager.get_entity("nomenclature_groups", original.id) is original


def test_storage_manager__first_start__nested_models_have_collections():
    """Организация и вложенные модели доступны через общие методы хранилища."""
    # Подготовка
    settings_manager = SettingsManager()
    settings_manager.read()
    manager = StorageManager()

    # Действия
    manager.start(settings_manager.settings)
    sources = {
        "organizations": [settings_manager.settings.organization],
        "premises": [warehouse.premises for warehouse in manager.warehouses],
        "dishes": [dish for tmap in manager.technological_maps for dish in tmap.dishes],
        "ingredients": _ingredients(manager),
    }

    # Проверки
    assert manager.get_reference_count(settings_manager.settings.organization.id) == 1
    for collection, expected in sources.items():
        assert _same_objects(manager.get_entities(collection), expected)
        for entity in expected:
            assert manager.get_entity(collection, entity.id) is entity


def test_storage_manager__first_start_nested_dish__all_descendants_registered(
    monkeypatch, groups, units
):
    """Начальные данные регистрируют блюдо и ингредиенты на любой глубине вложения."""
    # Подготовка
    manager = StorageManager()
    model = TechnologicalMapModel.create_technological_map(groups, units)
    model.dishes = [model.dishes[1]]
    monkeypatch.setattr(
        StorageManager, "_create_default_data", Mock(return_value=[model])
    )

    # Действия
    manager.start(_build_settings())
    pizza = manager.technological_maps[0].dishes[0]
    dough = pizza.ingredients[0]

    # Проверки
    assert len(manager.get_entities("dishes")) == 2
    assert len(manager.get_entities("ingredients")) == 9
    assert manager.get_entity("dishes", dough.id) is dough
    assert manager.get_reference_count(pizza.id) == 1
    assert manager.get_reference_count(dough.id) == 1
    for ingredient in dough.ingredients:
        assert manager.get_entity("ingredients", ingredient.id) is ingredient
        assert manager.get_reference_count(ingredient.id) == 1


def test_storage_manager__settings_attached_after_read__organization_counted_once(
    tmp_path,
):
    """Подключение настроек после чтения учитывает организацию ровно один раз."""
    # Подготовка
    settings_manager = SettingsManager()
    settings_manager.read()
    settings = settings_manager.settings
    manager = StorageManager()
    file_name = tmp_path / "storage.json"
    file_name.write_text('{"organizations": []}', encoding="utf-8")
    manager.read(str(file_name))

    # Действия
    manager.start(settings)
    manager.start(settings)

    # Проверки
    assert manager.settings is settings
    assert manager.get_all_models() == [settings.organization]
    assert manager.get_reference_count(settings.organization.id) == 1


def test_storage_manager__settings_id_conflict__previous_indexes_kept(tmp_path):
    """Конфликт кода организации настроек с другой моделью сохраняет индексы."""
    # Подготовка
    settings_manager = SettingsManager()
    settings_manager.read()
    settings = settings_manager.settings
    settings.first_start = False
    organization = settings.organization
    manager = StorageManager()
    manager.start(settings)
    data = {
        "measurement_units": [
            {
                "type": "MeasurementUnitModel",
                "id": organization.id,
                "name": "грамм",
                "coefficient": 1,
            }
        ]
    }
    file_name = tmp_path / "conflicting.json"
    file_name.write_text(json.dumps(data), encoding="utf-8")

    # Действия
    with pytest.raises(ValidationException):
        manager.read(str(file_name))

    # Проверки
    assert manager.get_all_models() == [organization]
    assert manager.get_entity("organizations", organization.id) is organization
    assert manager.get_reference_count(organization.id) == 1
    assert settings.organization is organization


def test_storage_manager__saved_organization_id__reference_without_settings_counted(
    tmp_path, settings_data
):
    """Сохранённый выбор организации учитывается до подключения модели настроек."""
    # Подготовка
    manager = StorageManager()
    organization = settings_data["organization"] | {"id": "saved-organization"}
    data = {
        "organizations": [organization],
        "organization_id": organization["id"],
    }
    file_name = tmp_path / "storage.json"
    file_name.write_text(json.dumps(data), encoding="utf-8")

    # Действия
    manager.read(str(file_name))
    manager.save(str(file_name))
    manager.read(str(file_name))

    # Проверки
    assert manager.settings is None
    assert manager.get_reference_count(organization["id"]) == 1


def test_storage_manager__two_instances__same_object():
    """Повторное создание хранилища возвращает тот же экземпляр (singleton)."""
    # Подготовка
    first = StorageManager()

    # Действия
    second = StorageManager()

    # Проверки
    assert first is second


def test_storage_manager__start_via_one_instance__data_visible_in_another():
    """Данные, сформированные через один экземпляр, видны через другой."""
    # Подготовка
    manager = _build_started_manager()

    # Действия
    nomenclature = StorageManager().nomenclature

    # Проверки
    assert _same_objects(nomenclature, manager.nomenclature)


def test_storage_manager__constructor__not_loaded_and_empty():
    """До запуска хранилище не загружено, а все коллекции пусты."""
    # Подготовка
    # Дополнительная подготовка не требуется.

    # Действия
    manager = StorageManager()

    # Проверки
    assert not manager.is_loaded
    assert manager.settings is None
    assert all(getattr(manager, name) == [] for name in COLLECTIONS)


def test_storage_manager__start_first_start__is_loaded_and_settings_kept():
    """При первом старте данные формируются, а настройки сохраняются в хранилище."""
    # Подготовка
    settings = _build_settings(first_start=True)
    manager = StorageManager()

    # Действия
    manager.start(settings)

    # Проверки
    assert manager.is_loaded
    assert manager.settings is settings


def test_storage_manager__start_not_first_start__empty_storage_initialized():
    """При first_start=False создаётся сохранённое пустое хранилище."""
    # Подготовка
    manager = StorageManager()
    settings = _build_settings(first_start=False)

    # Действия
    manager.start(settings)

    # Проверки
    assert manager.is_loaded
    assert all(getattr(manager, name) == [] for name in COLLECTIONS)


def test_storage_manager__start_twice__data_not_recreated():
    """Повторный запуск не пересоздаёт уже сформированные объекты."""
    # Подготовка
    manager = _build_started_manager()
    nomenclature = manager.nomenclature
    settings = _build_settings()

    # Действия
    manager.start(settings)

    # Проверки
    assert _same_objects(manager.nomenclature, nomenclature)


def test_storage_manager__start_not_settings_model__raises():
    """Запуск с настройками не типа SettingsModel вызывает исключение валидации."""
    # Подготовка
    manager = StorageManager()

    # Действия
    with pytest.raises(ValidationException) as exc_info:
        manager.start("настройки")

    # Проверки
    assert isinstance(exc_info.value, ValidationException)


@pytest.mark.parametrize("collection", COLLECTIONS)
def test_storage_manager__collection_property__returns_copy(collection):
    """Изменение полученного списка не меняет коллекцию хранилища."""
    # Подготовка
    manager = _build_started_manager()

    # Действия
    getattr(manager, collection).clear()

    # Проверки
    assert getattr(manager, collection) != []


@pytest.mark.parametrize("collection", COLLECTIONS)
def test_storage_manager__first_start__collection_is_filled(collection):
    """При первом старте каждая коллекция хранилища заполнена."""
    # Подготовка
    manager = _build_started_manager()

    # Действия
    items = getattr(manager, collection)

    # Проверки
    assert items != []


@pytest.mark.parametrize(
    ("unit", "base_unit"), [("килограмм", "грамм"), ("литр", "миллилитр")]
)
def test_storage_manager__first_start__derived_unit_refers_to_base_unit(
    unit, base_unit
):
    """Кратная единица ссылается на тот же объект базовой единицы из хранилища."""
    # Подготовка
    manager = _build_started_manager()

    # Действия
    units = _by_name(manager.measurement_units)

    # Проверки
    assert units[unit].base_unit is units[base_unit]


def test_storage_manager__first_start__nomenclature_refers_to_stored_objects():
    """Группа и единица каждой номенклатуры — объекты из коллекций хранилища."""
    # Подготовка
    manager = _build_started_manager()

    # Действия
    nomenclature = manager.nomenclature

    # Проверки
    for position in nomenclature:
        assert any(position.group is group for group in manager.nomenclature_groups)
        assert any(
            position.measurement_unit is unit for unit in manager.measurement_units
        )


def test_storage_manager__first_start__warehouse_owners_are_stored_objects():
    """Владелец каждого склада — ресторан или цех из коллекций хранилища."""
    # Подготовка
    manager = _build_started_manager()
    owners = [*manager.restaurants, *manager.production_shops]

    # Действия
    warehouses = manager.warehouses

    # Проверки
    for warehouse in warehouses:
        assert any(warehouse.warehouse_owner is owner for owner in owners)


def test_storage_manager__first_start__all_ids_are_unique():
    """Каждый сформированный объект уникален: идентификаторы не повторяются."""
    # Подготовка
    manager = _build_started_manager()
    objects = [
        *manager.measurement_units,
        *manager.nomenclature_groups,
        *manager.nomenclature,
        *manager.restaurants,
        *manager.production_shops,
        *manager.warehouses,
        *(warehouse.premises for warehouse in manager.warehouses),
        *manager.technological_maps,
        *(dish for tmap in manager.technological_maps for dish in tmap.dishes),
        *_ingredients(manager),
    ]

    # Действия
    ids = [item.id for item in objects]

    # Проверки
    assert len(ids) == len(set(ids))


def test_storage_manager__first_start__ingredients_refer_to_stored_objects():
    """Группа и единица каждого ингредиента — объекты из коллекций хранилища."""
    # Подготовка
    manager = _build_started_manager()

    # Действия
    ingredients = _ingredients(manager)

    # Проверки
    for ingredient in ingredients:
        assert any(ingredient.group is group for group in manager.nomenclature_groups)
        assert any(
            ingredient.measurement_unit is unit for unit in manager.measurement_units
        )


def test_storage_manager__first_start__recipe_positions_exist():
    """Номенклатура содержит ингредиенты, тесто и блюдо рецепта пиццы Маргарита."""
    # Подготовка
    manager = _build_started_manager()

    # Действия
    names = _by_name(manager.nomenclature).keys()

    # Проверки
    assert {
        "Мука пшеничная",
        "Дрожжи сухие",
        "Соль",
        "Масло оливковое",
        "Сыр Моцарелла",
        "Томаты",
        "Базилик",
        "Тесто для пиццы",
        "Пицца Маргарита",
    } <= names


def test_storage_manager__first_start__technological_map_is_margherita():
    """Хранилище содержит технологическую карту «Пицца Маргарита» с тестом и пиццей."""
    # Подготовка
    manager = _build_started_manager()

    # Действия
    maps = _by_name(manager.technological_maps)

    # Проверки
    assert list(maps) == ["Пицца Маргарита"]
    assert [dish.name for dish in maps["Пицца Маргарита"].dishes] == [
        "Тесто для пиццы",
        "Пицца Маргарита",
    ]


def test_storage_manager__save__all_collections_in_json(tmp_path):
    """Выгрузка пишет в json все справочники, ссылки — вложенными словарями."""
    # Подготовка
    manager = _build_started_manager()
    file_name = tmp_path / "storage.json"

    # Действия
    manager.save(str(file_name))
    data = json.loads(file_name.read_text(encoding="utf-8"))

    # Проверки
    assert set(data) == set(ALL_COLLECTIONS)
    units = {unit["name"]: unit for unit in data["measurement_units"]}
    assert units["килограмм"]["base_unit"] == units["грамм"]


def test_storage_manager__read_empty_collections__loaded_and_empty(tmp_path):
    """Пустые коллекции загружаются без создания первичных данных."""
    # Подготовка
    manager = _build_started_manager()
    settings = manager.settings
    file_name = tmp_path / "storage.json"
    file_name.write_text(json.dumps(dict.fromkeys(COLLECTIONS, [])), encoding="utf-8")

    # Действия
    manager.read(str(file_name))

    # Проверки
    assert manager.is_loaded
    assert manager.settings is settings
    assert all(manager.get_entities(field) == [] for field in ALL_COLLECTIONS)


@pytest.mark.parametrize("data", [None, [], {}])
def test_storage_manager__read_invalid_root__state_kept(tmp_path, data):
    """Неверный корень JSON не заменяет уже сформированные справочники."""
    # Подготовка
    manager = _build_started_manager()
    originals = {field: getattr(manager, field) for field in COLLECTIONS}
    file_name = tmp_path / "storage.json"
    file_name.write_text(json.dumps(data), encoding="utf-8")

    # Действия
    with pytest.raises(ValidationException):
        manager.read(str(file_name))

    # Проверки
    assert manager.is_loaded
    for field, models in originals.items():
        assert _same_objects(getattr(manager, field), models)


@pytest.mark.parametrize(
    "collection",
    [
        None,
        {},
        [{"type": "MeasurementUnitModel", "name": "грамм", "coefficient": 1}],
        [{"type": "TechnologicalMapModel", "name": "Карта", "id": "same-id"}] * 2,
        [{"type": "UnknownModel"}],
    ],
)
def test_storage_manager__read_invalid_collection__state_kept(tmp_path, collection):
    """Ошибка в последней коллекции не приводит к частичному обновлению хранилища."""
    # Подготовка
    manager = _build_started_manager()
    originals = {field: getattr(manager, field) for field in COLLECTIONS}
    file_name = tmp_path / "storage.json"
    manager.save(str(file_name))
    data = json.loads(file_name.read_text(encoding="utf-8"))
    data["measurement_units"][0]["name"] = "Новое имя из файла"
    data["technological_maps"] = collection
    file_name.write_text(json.dumps(data), encoding="utf-8")

    # Действия
    with pytest.raises(ValidationException):
        manager.read(str(file_name))

    # Проверки
    assert manager.is_loaded
    for field, models in originals.items():
        assert _same_objects(getattr(manager, field), models)
