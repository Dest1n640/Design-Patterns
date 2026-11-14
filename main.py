import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse, Response

from Src.Core.exception import NotFoundException, ValidationException
from Src.Core.report_type import ReportType
from Src.Logics.report_factory import ReportFactory
from Src.Logics.serialize_factory import SerializeFactory
from Src.Logics.settings_manager import SettingsManager
from Src.Logics.storage_manager import StorageManager

# Запуск: читает settings.json и формирует данные хранилища.
settings_manager = SettingsManager()
settings_manager.read()
storage_manager = StorageManager()
storage_manager.start(settings_manager.settings)
report_factory = ReportFactory(settings_manager.settings)

app = FastAPI()


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
    try:
        entities = storage_manager.get_entities(entity_type)
    except NotFoundException as ex:
        raise HTTPException(404, ex.message) from ex
    return SerializeFactory().convert(entities)


@app.get(
    "/entities/{entity_type}/{entity_id}",
    summary="Получить объект выбранной коллекции по идентификатору",
    responses={404: {"description": "Коллекция или сущность не найдена."}},
)
def get_entity(entity_type: str, entity_id: str) -> dict:
    """Возвращает объект выбранной коллекции по значению его поля id."""
    try:
        entity = storage_manager.get_entity(entity_type, entity_id)
    except NotFoundException as ex:
        raise HTTPException(404, ex.message) from ex
    return SerializeFactory().convert(entity)


@app.get("/reports/{report_type}/{entity_type}/{code}")
def get_report(report_type: ReportType, entity_type: str, code: str) -> Response:
    """Отчёт в указанном формате по сущности и её коду."""
    return build_response(report_type, entity_type, code)


@app.get("/reports/{entity_type}/{code}")
def get_default_report(entity_type: str, code: str) -> Response:
    """Отчёт в формате из настроек (create_default) по сущности и её коду."""
    return build_response(None, entity_type, code)


def build_response(
    report_type: ReportType | None, entity_type: str, code: str
) -> Response:
    """Ищет сущность (nomenclature, measurement_unit, recipe) и отдаёт отчёт по ней.

    Без report_type формат берётся из настроек через create_default.
    """
    entities = {
        "nomenclature": storage_manager.nomenclature,
        "measurement_unit": storage_manager.measurement_units,
        "recipe": storage_manager.technological_maps,
    }.get(entity_type, [])
    entity = next((e for e in entities if e.id == code), None)
    if entity is None:
        raise HTTPException(
            404, f"Сущность '{entity_type}' с кодом '{code}' не найдена"
        )
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
        return Response(
            report.binary,
            media_type="application/octet-stream",
            headers={"Content-Disposition": f'attachment; filename="{file_name}"'},
        )
    return PlainTextResponse(report.text)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
