from urllib.parse import quote

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, PlainTextResponse, Response
from pydantic import ValidationError
from starlette.convertors import StringConvertor, register_url_convertor

from Src.Core.exception import (
    ConflictException,
    NotFoundException,
    PersistenceException,
    ValidationException,
)
from Src.Core.report_type import ReportType
from Src.Dtos.measurement_unit_filter_dto import MeasurementUnitFilterDto
from Src.Dtos.nomenclature_filter_dto import NomenclatureFilterDto
from Src.Dtos.nomenclature_group_filter_dto import NomenclatureGroupFilterDto
from Src.Dtos.recipe_filter_dto import RecipeFilterDto
from Src.Logics.entity_request_adapter import EntityRequestAdapter
from Src.Logics.entity_service import EntityService
from Src.Logics.filter_prototype import FilterPrototype
from Src.Logics.report_factory import ReportFactory
from Src.Logics.serialize_factory import SerializeFactory
from Src.Logics.settings_manager import SettingsManager
from Src.Logics.storage_manager import StorageManager

settings_manager = SettingsManager()
settings_manager.read()
storage_manager = StorageManager()
storage_manager.start(settings_manager.settings)
report_factory = ReportFactory(settings_manager.settings)

app = FastAPI()

WRITE_RESPONSES = {
    404: {"description": "Коллекция или сущность не найдена."},
    409: {"description": "Конфликт идентификатора, вложенных данных или связей."},
    422: {"description": "Некорректное тело запроса или поля модели."},
    503: {"description": "Не удалось сохранить изменения в хранилище."},
}

FILTER_DTOS = {
    "nomenclature": NomenclatureFilterDto,
    "nomenclature_groups": NomenclatureGroupFilterDto,
    "measurement_units": MeasurementUnitFilterDto,
    "technological_maps": RecipeFilterDto,
}

REPORT_COLLECTIONS = {
    "nomenclature": "nomenclature",
    "measurement_unit": "measurement_units",
    "recipe": "technological_maps",
}


class ReportEntityConvertor(StringConvertor):
    """Распознаёт имена сущностей для маршрута отчёта без формата."""

    regex = "|".join(REPORT_COLLECTIONS)


register_url_convertor("report_entity", ReportEntityConvertor())


@app.exception_handler(NotFoundException)
@app.exception_handler(PersistenceException)
@app.exception_handler(ValidationException)
def handle_domain_exception(
    request: Request,
    exception: NotFoundException | ValidationException | PersistenceException,
) -> JSONResponse:
    """Преобразует ошибки доменной логики в ответы HTTP с описанием причины."""
    if isinstance(exception, NotFoundException):
        status_code = 404
    elif isinstance(exception, PersistenceException):
        status_code = 503
    elif isinstance(exception, ConflictException):
        status_code = 409
    else:
        status_code = 422
    content = {"detail": exception.message}
    if isinstance(exception, ValidationException):
        content["field"] = exception.field
    return JSONResponse(status_code=status_code, content=content)


@app.get("/report-formats", summary="Получить список форматов отчётов")
def get_report_formats() -> list[str]:
    """Возвращает список всех поддерживаемых форматов отчётов."""
    return [report_type.value for report_type in ReportType]


@app.get("/entities", summary="Получить список коллекций доменных сущностей")
def get_entity_types() -> list[str]:
    """Возвращает имена доступных коллекций доменных сущностей."""
    return storage_manager.get_entity_types()


@app.get(
    "/entities/{entity_type}",
    summary="Получить список объектов выбранной коллекции",
    responses={404: {"description": "Коллекция не найдена."}},
)
def get_entities(entity_type: str) -> list[dict]:
    """Возвращает все объекты коллекции, имя которой получено через GET /entities."""
    with storage_manager:
        entities = storage_manager.get_entities(entity_type)
        return SerializeFactory().convert(entities)


@app.get(
    "/entities/{entity_type}/{entity_id:path}",
    summary="Получить объект выбранной коллекции по идентификатору",
    responses={404: {"description": "Коллекция или сущность не найдена."}},
)
def get_entity(entity_type: str, entity_id: str) -> dict:
    """Возвращает объект выбранной коллекции по значению его поля id."""
    with storage_manager:
        entity = storage_manager.get_entity(entity_type, entity_id)
        return SerializeFactory().convert(entity)


@app.post(
    "/entities/{entity_type}",
    status_code=201,
    summary="Создать сущность вместе с новыми вложенными объектами",
    responses=WRITE_RESPONSES,
)
def create_entity(entity_type: str, data: dict) -> dict:
    """Создаёт сущность выбранной коллекции и возвращает её полное описание."""
    with storage_manager:
        model = EntityRequestAdapter.create(
            entity_type, data, storage_manager.find_model
        )
        entity = EntityService(storage_manager).create(model)
        return SerializeFactory().convert(entity)


@app.post(
    "/entities/{entity_type}/filter",
    summary="Отфильтровать объекты выбранной коллекции",
    responses={404: {"description": "Фильтрация коллекции недоступна."}},
)
def filter_entities(entity_type: str, data: dict) -> list[dict]:
    """Возвращает объекты коллекции, которые подходят под все условия запроса."""
    dto_type = FILTER_DTOS.get(entity_type)
    if dto_type is None:
        raise NotFoundException(f"Фильтрация коллекции '{entity_type}' недоступна")
    try:
        filter_dto = dto_type.model_validate(data)
    except ValidationError as ex:
        errors = [
            {**error, "loc": ("body", *error["loc"])}
            for error in ex.errors(include_context=False, include_url=False)
        ]
        raise RequestValidationError(errors, body=data) from ex

    with storage_manager:
        prototype = FilterPrototype(storage_manager.get_entities(entity_type))
        return SerializeFactory().convert(prototype.clone(filter_dto).data)


@app.patch(
    "/entities/{entity_type}/{entity_id:path}",
    summary="Частично изменить сущность",
    responses=WRITE_RESPONSES,
)
def update_entity(entity_type: str, entity_id: str, data: dict) -> dict:
    """Изменяет переданные поля, заменяя списки целиком и проверяя всю модель."""
    with storage_manager:
        original = storage_manager.get_entity(entity_type, entity_id)
        model = EntityRequestAdapter.update(original, data, storage_manager.find_model)
        entity = EntityService(storage_manager).update(entity_type, entity_id, model)
        return SerializeFactory().convert(entity)


@app.delete(
    "/entities/{entity_type}/{entity_id:path}",
    status_code=204,
    response_class=Response,
    summary="Удалить сущность без входящих ссылок",
    responses=WRITE_RESPONSES,
)
def delete_entity(entity_type: str, entity_id: str) -> Response:
    """Удаляет сущность, сохраняя связанные с ней вложенные объекты в коллекциях."""
    EntityService(storage_manager).delete(entity_type, entity_id)
    return Response(status_code=204)


@app.get("/reports/{entity_type:report_entity}/{code:path}")
def get_default_report(entity_type: str, code: str) -> Response:
    """Отчёт в формате из настроек (create_default) по сущности и её коду."""
    return build_response(None, entity_type, code)


@app.get("/reports/{report_type}/{entity_type}/{code:path}")
def get_report(report_type: ReportType, entity_type: str, code: str) -> Response:
    """Отчёт в указанном формате по сущности и её коду."""
    return build_response(report_type, entity_type, code)


app.add_api_route(
    "/reports/{entity_type}/{code}",
    get_default_report,
    methods=["GET"],
    name="get_report_for_unknown_entity",
    include_in_schema=False,
)


def build_response(
    report_type: ReportType | None, entity_type: str, code: str
) -> Response:
    """Строит отчёт по коду сущности в запрошенном формате или формате из настроек."""
    with storage_manager:
        try:
            entity = storage_manager.get_entity(REPORT_COLLECTIONS[entity_type], code)
        except (KeyError, NotFoundException) as ex:
            raise HTTPException(
                404, f"Сущность '{entity_type}' с кодом '{code}' не найдена"
            ) from ex
        if report_type is None:
            report_type = settings_manager.settings.response_format
            builder = report_factory.create_default()
        else:
            builder = report_factory.create(report_type)
        try:
            report = builder.build(entity)
        except ValidationException as ex:
            raise HTTPException(400, ex.message) from ex
        if report.binary:
            file_name = f"{entity_type}_{code}.{report_type.value}"
            encoded_name = quote(file_name, safe="")
            disposition = (
                f'attachment; filename="{file_name}"'
                if encoded_name == file_name
                else f"attachment; filename*=UTF-8''{encoded_name}"
            )
            return Response(
                report.binary,
                media_type="application/octet-stream",
                headers={"Content-Disposition": disposition},
            )
        return PlainTextResponse(report.text)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
