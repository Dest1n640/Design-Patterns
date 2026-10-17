import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse, Response

from Src.Core.exception import ValidationException
from Src.Core.report_type import ReportType
from Src.Logics.report_factory import ReportFactory
from Src.Logics.settings_manager import SettingsManager
from Src.Logics.storage_manager import StorageManager

# Запуск: читает settings.json и формирует данные хранилища.
settings_manager = SettingsManager()
settings_manager.load()
StorageManager().start(settings_manager.settings)
report_factory = ReportFactory(settings_manager.settings)

app = FastAPI()


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
    storage = StorageManager()
    entities = {
        "nomenclature": storage.nomenclature,
        "measurement_unit": storage.measurement_units,
        "recipe": storage.technological_maps,
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
