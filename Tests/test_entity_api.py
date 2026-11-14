"""Интеграционные тесты CRUD через HTTP-интерфейс приложения ASGI."""

import asyncio
import json
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from threading import Event

import pytest

from Src.Core.named_model import NamedModel
from Src.Core.validation import Validation
from Src.Logics.Convertors.basic_serialize import BasicSerialize
from Src.Logics.deserialize_factory import DeserializeFactory
from Src.Logics.model_registry import ENTITY_TYPES
from Src.Logics.settings_manager import SettingsManager
from Src.Logics.storage_manager import StorageManager
from Src.Models.settings_model import SettingsModel


def _request(app, method: str, path: str, data: object = None) -> tuple[int, object]:
    """Выполняет JSON-запрос через ASGI и возвращает статус и тело ответа."""
    messages = []
    body = b"" if data is None else json.dumps(data).encode()

    async def receive() -> dict:
        """Передаёт приложению тело запроса одним сообщением ASGI."""
        return {"type": "http.request", "body": body, "more_body": False}

    async def send(message: dict) -> None:
        """Собирает сообщения ответа приложения."""
        messages.append(message)

    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": method,
        "scheme": "http",
        "path": path,
        "raw_path": path.encode(),
        "query_string": b"",
        "root_path": "",
        "headers": [(b"content-type", b"application/json")],
        "server": ("testserver", 80),
        "client": ("127.0.0.1", 1234),
    }
    asyncio.run(app(scope, receive, send))
    status = next(
        item["status"] for item in messages if item["type"] == "http.response.start"
    )
    content = b"".join(
        item.get("body", b"")
        for item in messages
        if item["type"] == "http.response.body"
    )
    return status, json.loads(content) if content else None


@pytest.fixture
def api(monkeypatch):
    """Подключает пустое хранилище и возвращает функцию запросов к приложению."""
    import main

    StorageManager._instance = None
    monkeypatch.setattr(main, "storage_manager", StorageManager())
    return partial(_request, main.app)


@pytest.fixture
def entity_payloads() -> dict[str, dict]:
    """Возвращает корректные запросы создания всех доменных моделей."""
    group = {"type": "NomenclatureGroupModel", "name": "Группа"}
    unit = {"type": "MeasurementUnitModel", "name": "грамм", "coefficient": 1}
    position = {
        "name": "Продукт",
        "full_name": "Полное название продукта",
        "group": group,
        "measurement_unit": unit,
        "position_type": "raw_material",
    }
    ingredient = position | {"type": "IngredientModel", "brutto": 10, "netto": 8}
    dish = {
        "type": "DishModel",
        "name": "Блюдо",
        "ingredients": [ingredient],
        "recipe": "Приготовить",
    }
    premises = {
        "type": "PremisesModel",
        "name": "Помещение",
        "address": "Адрес",
        "square": 10,
    }
    return {
        "measurement_units": unit,
        "nomenclature_groups": group,
        "nomenclature": position,
        "restaurants": {"name": "Ресторан"},
        "production_shops": {"name": "Цех"},
        "warehouses": {
            "name": "Склад",
            "premises": premises,
            "warehouse_owner": {"type": "RestaurantModel", "name": "Владелец"},
        },
        "technological_maps": {"name": "Карта", "dishes": [dish]},
        "organizations": {
            "name": "Организация",
            "inn": "7701234567",
            "bic": "044525225",
            "curr_account": "40702810000000000001",
            "legal_form": "ООО",
        },
        "premises": premises,
        "dishes": dish,
        "ingredients": ingredient,
    }


@pytest.mark.parametrize("entity_type", list(ENTITY_TYPES))
def test_entity_api__all_model_types__crud_lifecycle(api, entity_payloads, entity_type):
    """Каждая зарегистрированная модель поддерживает полный цикл CRUD через HTTP."""
    # Подготовка
    path = f"/entities/{entity_type}"
    payload = entity_payloads[entity_type]

    # Действия
    created_status, created = api("POST", path, payload)
    entity_path = f"{path}/{created['id']}"
    read_status, stored = api("GET", entity_path)
    updated_status, updated = api("PATCH", entity_path, {"name": "Новое имя"})
    deleted_status, deleted = api("DELETE", entity_path)
    missing_status, _ = api("GET", entity_path)

    # Проверки
    assert created_status == 201
    assert read_status == 200
    assert stored == created
    assert updated_status == 200
    assert updated == created | {"name": "Новое имя"}
    assert deleted_status == 204
    assert deleted is None
    assert missing_status == 404


def test_entity_api__shared_reference__patch_updates_all_owners(api, entity_payloads):
    """Изменение связанной модели отражается у всех владельцев общей ссылки."""
    # Подготовка
    _, group = api("POST", "/entities/nomenclature_groups", {"name": "Группа"})
    _, unit = api(
        "POST", "/entities/measurement_units", {"name": "грамм", "coefficient": 1}
    )
    payload = entity_payloads["nomenclature"] | {
        "group": group,
        "measurement_unit": unit,
    }
    _, first = api("POST", "/entities/nomenclature", payload)
    _, second = api("POST", "/entities/nomenclature", payload)
    storage = StorageManager()
    original = storage.get_entity("nomenclature_groups", group["id"])

    # Действия
    status, _ = api(
        "PATCH",
        f"/entities/nomenclature_groups/{group['id']}",
        {"name": "Общая группа"},
    )
    _, first_loaded = api("GET", f"/entities/nomenclature/{first['id']}")
    _, second_loaded = api("GET", f"/entities/nomenclature/{second['id']}")

    # Проверки
    assert status == 200
    assert first_loaded["group"]["name"] == "Общая группа"
    assert second_loaded["group"]["name"] == "Общая группа"
    assert storage.get_entity("nomenclature", first["id"]).group is original
    assert storage.get_entity("nomenclature", second["id"]).group is original


def test_entity_api__conflicting_nested_object__request_rejected(api, entity_payloads):
    """Новый запрос не может изменить сохранённый объект через вложенное описание."""
    # Подготовка
    _, group = api("POST", "/entities/nomenclature_groups", {"name": "Группа"})
    payload = entity_payloads["nomenclature"] | {"group": group | {"name": "Конфликт"}}

    # Действия
    status, error = api("POST", "/entities/nomenclature", payload)
    _, groups = api("GET", "/entities/nomenclature_groups")
    _, positions = api("GET", "/entities/nomenclature")

    # Проверки
    assert status == 409
    assert error["field"] == "id"
    assert groups == [group]
    assert positions == []


def test_entity_api__invalid_nested_creation__no_partial_changes(api, entity_payloads):
    """Ошибка вложенной модели отклоняет создание всей совокупности объектов."""
    # Подготовка
    payload = entity_payloads["nomenclature"]
    payload["measurement_unit"]["coefficient"] = 0

    # Действия
    status, _ = api("POST", "/entities/nomenclature", payload)

    # Проверки
    assert status == 422
    assert StorageManager().nomenclature == []
    assert StorageManager().nomenclature_groups == []
    assert StorageManager().measurement_units == []


def test_entity_api__extra_creation_fields__ignored(api, entity_payloads):
    """Создание использует поля конструктора и игнорирует дополнительные данные."""
    # Подготовка
    payload = entity_payloads["nomenclature"] | {
        "unused": {"type": "RestaurantModel", "name": "Лишний объект"}
    }
    payload["measurement_unit"].update({"base_coefficient": 2, "unused": True})

    # Действия
    status, created = api("POST", "/entities/nomenclature", payload)

    # Проверки
    assert status == 201
    assert "unused" not in created
    assert "unused" not in created["measurement_unit"]
    assert created["measurement_unit"]["base_coefficient"] == 1
    assert StorageManager().restaurants == []


def test_entity_api__invalid_patch__original_and_nested_objects_kept(
    api, entity_payloads
):
    """Ошибка PATCH сохраняет исходное состояние и не добавляет вложенные объекты."""
    # Подготовка
    _, warehouse = api("POST", "/entities/warehouses", entity_payloads["warehouses"])
    path = f"/entities/warehouses/{warehouse['id']}"
    changes = {
        "name": "Новое имя",
        "premises": entity_payloads["premises"] | {"name": "Новое помещение"},
        "warehouse_owner": {"type": "RestaurantModel", "name": ""},
    }

    # Действия
    status, _ = api("PATCH", path, changes)
    _, stored = api("GET", path)
    _, premises = api("GET", "/entities/premises")

    # Проверки
    assert status == 422
    assert stored == warehouse
    assert premises == [warehouse["premises"]]


def test_entity_api__patch_lists__replace_links_and_keep_nested_models(
    api, entity_payloads
):
    """PATCH заменяет список целиком и сохраняет исключённые объекты в коллекциях."""
    # Подготовка
    _, recipe = api(
        "POST", "/entities/technological_maps", entity_payloads["technological_maps"]
    )
    dish = recipe["dishes"][0]
    dish_path = f"/entities/dishes/{dish['id']}"

    # Действия
    blocked_status, _ = api("DELETE", dish_path)
    status, updated = api(
        "PATCH", f"/entities/technological_maps/{recipe['id']}", {"dishes": []}
    )
    retained_status, retained = api("GET", dish_path)
    deleted_status, _ = api("DELETE", dish_path)
    ingredient_status, _ = api(
        "GET", f"/entities/ingredients/{dish['ingredients'][0]['id']}"
    )

    # Проверки
    assert blocked_status == 409
    assert status == 200
    assert updated["dishes"] == []
    assert retained_status == 200
    assert retained == dish
    assert deleted_status == 204
    assert ingredient_status == 200


@pytest.mark.parametrize("method", ["PATCH", "DELETE"])
def test_entity_api__incoming_reference__delete_and_id_change_blocked(api, method):
    """Входящая ссылка запрещает удаление сущности и смену её идентификатора."""
    # Подготовка
    _, gram = api(
        "POST", "/entities/measurement_units", {"name": "грамм", "coefficient": 1}
    )
    _, kilogram = api(
        "POST",
        "/entities/measurement_units",
        {"name": "килограмм", "coefficient": 1000, "base_unit": gram},
    )
    path = f"/entities/measurement_units/{gram['id']}"

    # Действия
    status, _ = api(method, path, {"id": "new-code"})
    _, stored = api("GET", path)
    _, owner = api("GET", f"/entities/measurement_units/{kilogram['id']}")

    # Проверки
    assert status == 409
    assert stored == gram
    assert owner == kilogram


@pytest.mark.parametrize("new_id", ["new-code", "section/new-code"])
def test_entity_api__unreferenced_id_change__new_code_available(api, new_id):
    """Сущность без входящих ссылок доступна по новому коду после PATCH."""
    # Подготовка
    _, group = api("POST", "/entities/nomenclature_groups", {"name": "Группа"})
    old_path = f"/entities/nomenclature_groups/{group['id']}"

    # Действия
    status, updated = api("PATCH", old_path, {"id": new_id})
    old_status, _ = api("GET", old_path)
    new_status, stored = api("GET", f"/entities/nomenclature_groups/{new_id}")

    # Проверки
    assert status == 200
    assert updated["id"] == new_id
    assert old_status == 404
    assert new_status == 200
    assert stored == updated


def test_entity_api__id_collision_on_patch__both_entities_kept(api):
    """Смена кода на занятый отклоняется даже при совпадающих данных моделей."""
    # Подготовка
    payload = {"name": "Группа"}
    _, first = api("POST", "/entities/nomenclature_groups", payload)
    _, second = api("POST", "/entities/nomenclature_groups", payload)

    # Действия
    status, _ = api(
        "PATCH", f"/entities/nomenclature_groups/{first['id']}", {"id": second["id"]}
    )
    _, stored = api("GET", "/entities/nomenclature_groups")

    # Проверки
    assert status == 409
    assert stored == [first, second]


def test_entity_api__cyclic_reference_on_patch__original_graph_kept(api):
    """PATCH отклоняет циклическую зависимость единиц измерения до её применения."""
    # Подготовка
    _, gram = api(
        "POST", "/entities/measurement_units", {"name": "грамм", "coefficient": 1}
    )
    _, kilogram = api(
        "POST",
        "/entities/measurement_units",
        {"name": "килограмм", "coefficient": 1000, "base_unit": gram},
    )
    path = f"/entities/measurement_units/{gram['id']}"

    # Действия
    status, _ = api("PATCH", path, {"base_unit": kilogram})
    _, stored = api("GET", path)

    # Проверки
    assert status == 409
    assert stored == gram


@pytest.mark.parametrize("changes", [{"unknown": 1}, {"base_coefficient": 1}])
def test_entity_api__invalid_patch_fields__validation_error(api, changes):
    """PATCH отклоняет неизвестные и вычисляемые поля без изменения объекта."""
    # Подготовка
    _, unit = api(
        "POST", "/entities/measurement_units", {"name": "грамм", "coefficient": 1}
    )
    path = f"/entities/measurement_units/{unit['id']}"

    # Действия
    status, _ = api("PATCH", path, changes)
    _, stored = api("GET", path)

    # Проверки
    assert status == 422
    assert stored == unit


@pytest.mark.parametrize("method", ["POST", "PATCH", "DELETE"])
def test_entity_api__unknown_collection__not_found(api, method):
    """Операции записи возвращают HTTP 404 для неизвестной коллекции."""
    # Подготовка
    path = "/entities/missing"
    if method != "POST":
        path += "/missing-id"

    # Действия
    status, _ = api(method, path, {"name": "Объект"})

    # Проверки
    assert status == 404


@pytest.mark.parametrize(
    "payload",
    [
        [],
        "text",
        None,
        {"name": ""},
        {"name": "Группа", "id": 42},
        {"name": "Группа", "type": "RestaurantModel"},
    ],
)
def test_entity_api__invalid_creation__validation_error(api, payload):
    """Некорректное тело запроса или поля модели отклоняются на границе HTTP."""
    # Подготовка
    # Данные предоставлены параметризацией.

    # Действия
    status, _ = api("POST", "/entities/nomenclature_groups", payload)

    # Проверки
    assert status == 422
    assert StorageManager().nomenclature_groups == []


def test_entity_api__cross_field_patch__whole_model_validated(api):
    """PATCH проверяет зависимость коэффициента от базовой единицы измерения."""
    # Подготовка
    _, gram = api(
        "POST", "/entities/measurement_units", {"name": "грамм", "coefficient": 1}
    )
    _, kilogram = api(
        "POST",
        "/entities/measurement_units",
        {"name": "килограмм", "coefficient": 1000, "base_unit": gram},
    )

    # Действия
    invalid_status, _ = api(
        "PATCH", f"/entities/measurement_units/{gram['id']}", {"coefficient": 2}
    )
    valid_status, updated = api(
        "PATCH", f"/entities/measurement_units/{kilogram['id']}", {"coefficient": 2000}
    )

    # Проверки
    assert invalid_status == 422
    assert valid_status == 200
    assert updated["coefficient"] == updated["base_coefficient"] == 2000


def test_entity_api__concurrent_same_id__one_creation_succeeds(api):
    """Параллельные запросы не создают две сущности с одинаковым кодом."""
    # Подготовка
    request = partial(
        api, "POST", "/entities/nomenclature_groups", {"id": "same", "name": "Группа"}
    )

    # Действия
    with ThreadPoolExecutor(max_workers=2) as executor:
        responses = list(executor.map(lambda _: request(), range(2)))

    # Проверки
    assert sorted(status for status, _ in responses) == [201, 409]
    assert len(StorageManager().nomenclature_groups) == 1


def test_entity_api__new_registered_model__crud_supported(api, monkeypatch):
    """Одна регистрация новой модели подключает существующие HTTP-методы CRUD."""

    # Подготовка
    import main

    class TagModel(NamedModel):
        """Дополнительная модель для проверки расширяемости CRUD."""

        def __init__(self, name: str) -> None:
            """Создаёт метку с выключенным признаком активности."""
            super().__init__(name)
            self.__enabled = False

        @property
        def enabled(self) -> bool:
            """Возвращает признак активности метки."""
            return self.__enabled

        @enabled.setter
        def enabled(self, new_enabled: bool) -> None:
            """Проверяет и устанавливает признак активности метки."""
            self.__enabled = Validation.validate_instance(
                new_enabled, bool, "enabled", "Ожидается логическое значение"
            )

    monkeypatch.setitem(ENTITY_TYPES, "tags", TagModel)
    StorageManager._instance = None
    monkeypatch.setattr(main, "storage_manager", StorageManager())

    # Действия
    created_status, created = api(
        "POST", "/entities/tags", {"name": "Метка", "enabled": True}
    )
    path = f"/entities/tags/{created['id']}"
    updated_status, updated = api(
        "PATCH", path, {"name": "Новая метка", "enabled": False}
    )
    deleted_status, _ = api("DELETE", path)

    # Проверки
    assert created_status == 201
    assert created["type"] == "TagModel"
    assert created["enabled"] is True
    assert updated_status == 200
    assert updated["name"] == "Новая метка"
    assert updated["enabled"] is False
    assert deleted_status == 204


def test_entity_api__active_organization__settings_reference_preserved(api):
    """PATCH обновляет организацию в настройках, а её удаление блокируется."""
    # Подготовка
    settings = SettingsManager()
    settings.read()
    storage = StorageManager()
    storage.start(settings.settings)
    organization = settings.settings.organization
    path = f"/entities/organizations/{organization.id}"

    # Действия
    updated_status, _ = api("PATCH", path, {"name": "Новое название"})
    deleted_status, _ = api("DELETE", path)

    # Проверки
    assert updated_status == 200
    assert settings.settings.organization is organization
    assert organization.name == "Новое название"
    assert deleted_status == 409
    assert storage.get_entity("organizations", organization.id) is organization


@pytest.mark.parametrize("collection_response", [False, True])
def test_entity_api__concurrent_get_and_patch__consistent_response(
    api, monkeypatch, collection_response
):
    """GET формирует целостный снимок до применения параллельного PATCH."""
    # Подготовка
    _, gram = api(
        "POST", "/entities/measurement_units", {"name": "грамм", "coefficient": 1}
    )
    _, unit = api(
        "POST",
        "/entities/measurement_units",
        {
            "name": "единица",
            "coefficient": 1000,
            "base_unit": gram,
        },
    )
    storage = StorageManager()
    original = storage.get_entity("measurement_units", unit["id"])
    captured = Event()
    resume = Event()
    writer_started = Event()
    writer_finished = Event()
    original_convert = BasicSerialize.convert
    path = "/entities/measurement_units"
    if not collection_response:
        path += f"/{unit['id']}"

    def paused_convert(self, source):
        """Останавливает сериализацию между чтением простых полей и ссылок."""
        result = original_convert(self, source)
        if source is original and not captured.is_set():
            captured.set()
            if not resume.wait(5):
                raise RuntimeError("Сериализация не получила сигнал продолжения")
        return result

    def update_unit():
        """Изменяет единицу измерения из параллельного потока."""
        writer_started.set()
        storage.update_entity(
            "measurement_units", unit["id"], {"coefficient": 1, "base_unit": None}
        )
        writer_finished.set()

    monkeypatch.setattr(BasicSerialize, "convert", paused_convert)

    # Действия
    with ThreadPoolExecutor(max_workers=2) as executor:
        reader = executor.submit(api, "GET", path)
        try:
            assert captured.wait(5)
            writer = executor.submit(update_unit)
            assert writer_started.wait(5)
            finished_during_read = writer_finished.wait(0.1)
        finally:
            resume.set()
        status, response = reader.result(timeout=5)
        writer.result(timeout=5)
    restored = DeserializeFactory().convert(response)

    # Проверки
    assert status == 200
    assert not finished_during_read
    if collection_response:
        assert response == [gram, unit]
        assert restored[1].coefficient == 1000
    else:
        assert response == unit
        assert restored.coefficient == 1000
    assert original.coefficient == 1
    assert original.base_unit is None


def test_entity_api__autosave_restart__created_entity_available(
    api, tmp_path, monkeypatch
):
    """Созданная через HTTP сущность доступна после восстановления приложения."""
    # Подготовка
    import main

    file_name = tmp_path / "storage.json"
    StorageManager().start(SettingsModel(), str(file_name))

    # Действия
    created_status, created = api(
        "POST", "/entities/nomenclature_groups", {"name": "Сохранённая"}
    )
    StorageManager._instance = None
    restored = StorageManager()
    settings = SettingsModel()
    settings.first_start = True
    restored.start(settings, str(file_name))
    monkeypatch.setattr(main, "storage_manager", restored)
    read_status, loaded = api("GET", f"/entities/nomenclature_groups/{created['id']}")

    # Проверки
    assert created_status == 201
    assert read_status == 200
    assert loaded == created


def test_entity_api__save_failure__service_error_and_retry(api, tmp_path, monkeypatch):
    """Ошибка сохранения возвращает HTTP 503, после восстановления запись доступна."""
    # Подготовка
    file_name = tmp_path / "storage.json"
    storage = StorageManager()
    storage.start(SettingsModel(), str(file_name))
    original_file = file_name.read_bytes()

    def fail_replace(source, target) -> None:
        """Имитирует отказ атомарной замены файла хранилища."""
        raise OSError("Запись недоступна")

    # Действия
    with monkeypatch.context() as patch:
        patch.setattr("Src.Logics.storage_manager.os.replace", fail_replace)
        failed_status, error = api(
            "POST", "/entities/nomenclature_groups", {"name": "Ошибка"}
        )
        failed_file = file_name.read_bytes()
        failed_models = storage.nomenclature_groups
    retry_status, created = api(
        "POST", "/entities/nomenclature_groups", {"name": "Сохранённая"}
    )
    saved = json.loads(file_name.read_text(encoding="utf-8"))

    # Проверки
    assert failed_status == 503
    assert "detail" in error
    assert failed_file == original_file
    assert failed_models == []
    assert retry_status == 201
    assert saved["nomenclature_groups"] == [created]
